# -*- coding: utf-8 -*-
"""Reordena los temas de cada disco de forma aleatoria, renumera los archivos
fisicos (NN - Title.mp3) y reconstruye box.json + box_set.json recuperando
bpm/tonalidad/titulo del metadata original (git 04d574c)."""
import json, os, re, random, subprocess, unicodedata, importlib.util

ROOT = os.path.dirname(os.path.abspath(__file__))
FFMPEG = r"C:\Users\AI01_\AppData\Local\Temp\opencode\ffmpeg\bin\ffmpeg.exe"
FFPROBE = r"C:\Users\AI01_\AppData\Local\Temp\opencode\ffmpeg\bin\ffprobe.exe"
WEB_BOX = os.path.join(ROOT, "web", "data", "box.json")
BOX_SET = os.path.join(ROOT, "box_set.json")
SRC_ROOT = os.path.join(ROOT, "Discos")
OLD_SHA = "04d574c"


def norm(s):
    s = (s or "")
    s = unicodedata.normalize("NFKD", s).encode("ascii", "ignore").decode()
    s = s.lower()
    s = re.sub(r"\((\d+)\)", r"version \1", s)
    s = re.sub(r"[\s\-_]+", " ", s).strip()
    return s


def title_of(fname):
    if not fname:
        return ""
    return re.sub(r"^\d+\s*-\s*", "", fname).rsplit(".", 1)[0]


def duration(path):
    out = subprocess.run(
        [FFPROBE, "-v", "error", "-show_entries", "format=duration",
         "-of", "default=noprint_wrappers=1:nokey=1", path],
        capture_output=True, text=True)
    try:
        return round(float(out.stdout.strip()), 3)
    except Exception:
        return None


def bpm_estimate(path):
    if importlib.util.find_spec("numpy") is None:
        return None
    import numpy as np
    try:
        raw = subprocess.run(
            [FFMPEG, "-v", "error", "-t", "180", "-i", path,
             "-ac", "1", "-ar", "22050", "-f", "s16le", "-"],
            capture_output=True).stdout
        x = np.frombuffer(raw, dtype=np.int16).astype(np.float32) / 32768.0
        if len(x) < 22050 * 8:
            return None
        hop = 512
        n = len(x) // hop
        rms = np.sqrt(np.mean(x[:n * hop].reshape(n, hop) ** 2, axis=1))
        env = np.diff(rms)
        env[env < 0] = 0
        env -= env.mean()
        env[env < 0] = 0
        env /= (env.max() + 1e-9)
        hop_s = hop / 22050.0
        lo = int(round(60 / 180.0 / hop_s))
        hi = int(round(60 / 60.0 / hop_s))
        ac = np.array([np.dot(env[: -lag], env[lag:]) for lag in range(lo, hi + 1)])
        lag = lo + int(np.argmax(ac))
        bpm = 60.0 / (lag * hop_s)
        return round(bpm, 1)
    except Exception:
        return None


def load_old_metadata():
    out = subprocess.run(["git", "show", f"{OLD_SHA}:web/data/box.json"],
                         capture_output=True, cwd=ROOT)
    if out.returncode != 0:
        print("no pude leer metadata original:", out.stderr.decode("utf-8", "replace")[:200])
        return {}
    idx = {}
    for dis in json.loads(out.stdout.decode("utf-8")):
        for t in dis["tracklist"]:
            keys = {norm(t.get("titulo")), norm(title_of(t.get("nombre"))), norm(title_of(t.get("archivo")))}
            for k in keys:
                if k and k not in idx:
                    idx[k] = t
    return idx


def main():
    with open(WEB_BOX, encoding="utf-8") as fh:
        discos = json.load(fh)
    idx = load_old_metadata()
    sin_meta = []

    for dis in discos:
        folder = os.path.join(SRC_ROOT, dis["slug"])
        if not os.path.isdir(folder):
            dis["tracklist"] = []
            continue
        items = []
        for name in os.listdir(folder):
            if not name.lower().endswith(".mp3"):
                continue
            m = re.match(r"^(\d+)\s*-\s*(.+)\.mp3$", name)
            if not m:
                print("SIN PREFIJO", dis["slug"], repr(name))
                continue
            items.append((name, m.group(2)))
        random.shuffle(items)

        temps = []
        for i, (oldname, _) in enumerate(items, 1):
            tf = os.path.join(folder, f".tmp_{i:02d}_{oldname}")
            os.rename(os.path.join(folder, oldname), tf)
            temps.append((tf, oldname))

        tl = []
        orden = []
        for i, (tf, oldname) in enumerate(temps, 1):
            title = re.match(r"^(\d+)\s*-\s*(.+)\.mp3$", oldname).group(2)
            meta = idx.get(norm(title)) or {}
            titulo_cur = meta.get("titulo") or title
            final = os.path.join(folder, f"{i:02d} - {titulo_cur}.mp3")
            os.rename(tf, final)
            path = final
            dur = duration(path)
            bpm = meta.get("bpm")
            tol = meta.get("tonalidad")
            if not meta:
                bpm = bpm_estimate(path)
                sin_meta.append((dis["slug"], i, title, bpm))
            tl.append({
                "n": i,
                "archivo": f"{titulo_cur}.mp3",
                "nombre": f"{i:02d} - {titulo_cur}.mp3",
                "titulo": titulo_cur,
                "bpm": bpm,
                "tonalidad": tol,
                "duracion": dur,
                "audio": f"/music/{dis['slug']}/{i:02d}.mp3",
            })
            orden.append(f"{i:02d} {titulo_cur}")
        dis["tracklist"] = tl
        print(dis["slug"], len(tl), "temas ->", ", ".join(orden))

    with open(WEB_BOX, "w", encoding="utf-8") as fh:
        json.dump(discos, fh, ensure_ascii=False, indent=1)

    with open(BOX_SET, encoding="utf-8") as fh:
        discos_set = json.load(fh)
    by_slug = {d["slug"]: d for d in discos_set}
    for dis in discos:
        ds = by_slug.get(dis["slug"])
        if ds is not None and ds["tracklist"] != dis["tracklist"]:
            ds["tracklist"] = dis["tracklist"]
    with open(BOX_SET, "w", encoding="utf-8") as fh:
        json.dump(discos_set, fh, ensure_ascii=False, indent=1)

    total = sum(len(d["tracklist"]) for d in discos)
    print(f"TOTAL {total} temas")
    for s, i, t, b in sin_meta:
        print(f"SIN METADATA {s} {i:02d} '{t}' -> bpm estimado: {b}")


main()