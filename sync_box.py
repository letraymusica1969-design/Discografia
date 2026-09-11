# -*- coding: utf-8 -*-
import os, sys, json, re, shutil, subprocess, unicodedata
from mutagen.mp3 import MP3

sys.stdout.reconfigure(encoding="utf-8")

OUT = os.path.dirname(os.path.abspath(__file__))
BOX_FILE = os.path.join(OUT, "box_set.json")
BOX_DIR = os.path.join(OUT, "Discos")
TAPAS = os.path.join(BOX_DIR, "Tapas")
DESC = os.path.join(BOX_DIR, "_Descartados")
NUEVOS = os.path.join(BOX_DIR, "_Nuevos")
WEB_COVERS = os.path.join(OUT, "web", "public", "covers")
WEB_DATA = os.path.join(OUT, "web", "data", "box.json")
SRC_ROOTS = [r"C:\Discografia", r"C:\Discografia\Pendientes"]


def norm(s):
    s = s or ""
    s = re.sub(r"^.*[\\/]", "", s)
    s = re.sub(r"\.mp3$", "", s, flags=re.I)
    s = re.sub(r"^\s*\d+\s*[-._]\s*", "", s)
    s = s.lower()
    s = unicodedata.normalize("NFD", s)
    s = "".join(c for c in s if unicodedata.category(c) != "Mn")
    s = re.sub(r"\((\d)\)", r"v\1", s)
    s = re.sub(r"\W+", "", s)
    return s


def file_title(fname):
    base = os.path.basename(fname)
    base = base[:-4] if base.lower().endswith(".mp3") else base
    t = re.sub(r"\([^)]*remix[^)]*\)", "", base, flags=re.IGNORECASE)
    t = re.sub(r"[_-]+", " ", t)
    t = re.sub(r"\s+", " ", t).strip()
    if t:
        t = t[0].upper() + t[1:]
    return t or base


def display_title(fname):
    base = os.path.basename(fname)
    base = base[:-4] if base.lower().endswith(".mp3") else base
    had = re.search(r"\((\d)\)", base)
    t = re.sub(r"\(\d\)", "", base)
    t = re.sub(r"\([^)]*remix[^)]*\)", "", t, flags=re.IGNORECASE)
    t = re.sub(r"[_-]+", " ", t)
    t = re.sub(r"\s+", " ", t).strip()
    if had:
        t = t + " (version " + had.group(1) + ")"
    if t:
        t = t[0].upper() + t[1:]
    return t or base


def build_pool():
    exact = {}
    normed = {}
    for root in SRC_ROOTS:
        if os.path.isdir(root):
            for base in os.listdir(root):
                if base.lower().endswith(".mp3"):
                    exact.setdefault(base.lower(), os.path.join(root, base))
                    normed.setdefault(norm(base), os.path.join(root, base))
    if os.path.isdir(NUEVOS):
        for base in os.listdir(NUEVOS):
            if base.lower().endswith(".mp3"):
                exact.setdefault(base.lower(), os.path.join(NUEVOS, base))
                normed.setdefault(norm(base), os.path.join(NUEVOS, base))
    for slug in os.listdir(BOX_DIR):
        d = os.path.join(BOX_DIR, slug)
        if os.path.isdir(d) and not slug.startswith("_"):
            for base in os.listdir(d):
                if base.lower().endswith(".mp3"):
                    exact.setdefault(base.lower(), os.path.join(d, base))
                    normed.setdefault(norm(base), os.path.join(d, base))
    return exact, normed


def load_feats():
    fp = os.path.join(OUT, "features.json")
    if not os.path.isfile(fp):
        return {}
    with open(fp, encoding="utf-8") as fh:
        data = json.load(fh)
    return {norm(f.get("archivo", "")): f for f in data}


def dur_of(path):
    try:
        return MP3(path).info.length
    except Exception:
        return 0.0


def write_m3u(d, ddir):
    lines = ["#EXTM3U"]
    for t in d["tracklist"]:
        lines.append("#EXTINF:%d,%s" % (int(t["duracion"]), t["titulo"]))
        lines.append(t["nombre"])
    with open(os.path.join(ddir, "playlist.m3u"), "w", encoding="utf-8-sig") as fh:
        fh.write("\n".join(lines) + "\n")


def main():
    dry = "--dry" in sys.argv
    purge = "--purge" in sys.argv
    covers = "--no-covers" not in sys.argv

    with open(BOX_FILE, encoding="utf-8") as fh:
        box = json.load(fh)

    pool_exact, pool_norm = build_pool()
    feats = load_feats()
    missing = []
    used = {}

    for d in box:
        slug = d["slug"]
        ddir = os.path.join(BOX_DIR, slug)
        os.makedirs(ddir, exist_ok=True)
        used[slug] = set()
        keep = []
        for i, t in enumerate(d.get("tracklist", []), 1):
            t["n"] = i
            ref = t.get("archivo", "") or t.get("titulo", "") or ""
            src = pool_exact.get(os.path.basename(ref).lower())
            if not src:
                src = pool_norm.get(norm(ref))
            if not src:
                missing.append((slug, i, t.get("titulo") or t.get("archivo") or "?"))
                keep.append(t)
                continue
            fbase = file_title(src)
            nombre = "%02d - %s.mp3" % (i, fbase)
            t["archivo"] = os.path.basename(src)
            t["nombre"] = nombre
            if not t.get("titulo"):
                t["titulo"] = display_title(src)
            t["duracion"] = round(dur_of(src), 3)
            f = feats.get(norm(t["archivo"]))
            if f:
                t["bpm"] = f["tempo_bpm"]
                t["tonalidad"] = f.get("key", "?")
            elif "bpm" not in t:
                t["bpm"] = 0
                t["tonalidad"] = "?"
            target = os.path.join(ddir, nombre)
            used[slug].add(nombre)
            if os.path.normcase(os.path.abspath(src)) != os.path.normcase(os.path.abspath(target)):
                print("   copiar: %s  ->  %s" % (os.path.basename(src), nombre))
                if not dry:
                    shutil.copy2(src, target)
            keep.append(t)
        d["tracklist"] = keep

    for d in box:
        slug = d["slug"]
        ddir = os.path.join(BOX_DIR, slug)
        for base in os.listdir(ddir):
            if not base.lower().endswith(".mp3") or base in used.get(slug, set()):
                continue
            if purge:
                print("   borrar: %s" % base)
                if not dry:
                    os.remove(os.path.join(ddir, base))
            else:
                dest = os.path.join(DESC, slug)
                print("   quitar: %s  ->  _Descartados/%s" % (base, slug))
                if not dry:
                    os.makedirs(dest, exist_ok=True)
                    shutil.move(os.path.join(ddir, base), os.path.join(dest, base))

    if not dry:
        for d in box:
            write_m3u(d, os.path.join(BOX_DIR, d["slug"]))
        ext = ["#EXTM3U"]
        for d in box:
            for t in d["tracklist"]:
                ext.append("#EXTINF:%d,%s" % (int(t["duracion"]), t["titulo"]))
                ext.append(os.path.join(d["slug"], t["nombre"]))
        with open(os.path.join(BOX_DIR, "Coleccion_5_Discos.m3u"), "w",
                  encoding="utf-8-sig") as fh:
            fh.write("\n".join(ext) + "\n")

    tot = sum(len(d["tracklist"]) for d in box)
    print("TOTAL: %d temas en %d discos" % (tot, len(box)))
    if missing:
        print("SIN AUDIO (falta subir/indicar el archivo):")
        for slug, n, tit in missing:
            print("   [%s] #%d %s" % (slug, n, tit))

    if dry:
        print("(modo dry: no se escribio nada)")
        return

    with open(BOX_FILE, "w", encoding="utf-8") as fh:
        json.dump(box, fh, ensure_ascii=False, indent=1)
    shutil.copy2(BOX_FILE, WEB_DATA)
    os.makedirs(WEB_COVERS, exist_ok=True)
    print("box_set.json -> web/data/box.json")

    if covers:
        subprocess.run([sys.executable, "make_covers.py"], cwd=OUT, check=True)
        for base in os.listdir(TAPAS):
            if base.lower().endswith(".jpg"):
                shutil.copy2(os.path.join(TAPAS, base), os.path.join(WEB_COVERS, base))
        print("tapas -> web/public/covers")


main()