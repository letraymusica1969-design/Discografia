# -*- coding: utf-8 -*-
"""Reordena los temas de cada disco de forma aleatoria, renumera los archivos
fisicos (NN - Title.mp3) y reconstruye box.json + box_set.json."""
import json, os, re, random, subprocess

sys = __import__("sys")
sys.stdout.reconfigure(encoding="utf-8")
ROOT = os.path.dirname(os.path.abspath(__file__))
FFPROBE = r"C:\Users\AI01_\AppData\Local\Temp\opencode\ffmpeg\bin\ffprobe.exe"
WEB_BOX = os.path.join(ROOT, "web", "data", "box.json")
BOX_SET = os.path.join(ROOT, "box_set.json")
SRC_ROOT = os.path.join(ROOT, "Discos")


def parse(name):
    m = re.match(r"^(\d+)\s*-\s*(.+)\.mp3$", name)
    if not m:
        return None
    return m.group(2)


def duration(path):
    out = subprocess.run(
        [FFPROBE, "-v", "error", "-show_entries", "format=duration",
         "-of", "default=noprint_wrappers=1:nokey=1", path],
        capture_output=True, text=True)
    try:
        return round(float(out.stdout.strip()), 3)
    except Exception:
        return None


def main():
    with open(WEB_BOX, encoding="utf-8") as fh:
        discos = json.load(fh)

    old = {}
    for dis in discos:
        for t in dis["tracklist"]:
            if t.get("titulo") and t["titulo"] not in old:
                old[t["titulo"]] = t

    for dis in discos:
        folder = os.path.join(SRC_ROOT, dis["slug"])
        if not os.path.isdir(folder):
            dis["tracklist"] = []
            continue
        items = []
        for name in os.listdir(folder):
            if not name.lower().endswith(".mp3"):
                continue
            title = parse(name)
            if title is None:
                print("SIN PREFIJO", dis["slug"], repr(name))
                continue
            items.append((name, title))
        random.shuffle(items)

        temps = []
        for i, (oldname, title) in enumerate(items, 1):
            tf = os.path.join(folder, f".tmp_{i}_{oldname}")
            os.rename(os.path.join(folder, oldname), tf)
            temps.append((tf, f"{i:02d} - {title}.mp3"))
        for tf, final in temps:
            os.rename(tf, os.path.join(folder, final))

        tl = []
        for i, (oldname, title) in enumerate(items, 1):
            path = os.path.join(folder, f"{i:02d} - {title}.mp3")
            meta = old.get(title) or {}
            dur = duration(path)
            tl.append({
                "n": i,
                "archivo": f"{title}.mp3",
                "nombre": f"{i:02d} - {title}.mp3",
                "titulo": title,
                "bpm": meta.get("bpm"),
                "tonalidad": meta.get("tonalidad"),
                "duracion": dur,
                "audio": f"/music/{dis['slug']}/{i:02d}.mp3",
            })
        dis["tracklist"] = tl
        print(dis["slug"], len(tl), "temas ->", ", ".join(f"{i:02d} {title}" for i, (_, title) in enumerate(items, 1)))

    with open(WEB_BOX, "w", encoding="utf-8") as fh:
        json.dump(discos, fh, ensure_ascii=False, indent=1)

    with open(BOX_SET, encoding="utf-8") as fh:
        discos_set = json.load(fh)
    by_slug = {d["slug"]: d for d in discos_set}
    cambios = 0
    for dis in discos:
        ds = by_slug.get(dis["slug"])
        if ds is not None and ds["tracklist"] != dis["tracklist"]:
            ds["tracklist"] = dis["tracklist"]
            cambios += 1
    with open(BOX_SET, "w", encoding="utf-8") as fh:
        json.dump(discos_set, fh, ensure_ascii=False, indent=1)

    total = sum(len(d["tracklist"]) for d in discos)
    print(f"TOTAL {total} temas")


main()