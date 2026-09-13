# -*- coding: utf-8 -*-
"""Escaneo integral de todos los temas disco por disco:
- verifica archivo por archivo (duracion real con ffprobe),
- detecta cambios de arreglo (mismo nombre, duracion diferente),
- calcula BPM faltante,
- agrega temas nuevos y respeta los que ya estaban,
- deja marcados los que hay que re-encodear."""
import json, os, re, subprocess, sys, unicodedata, importlib.util

sys.stdout.reconfigure(encoding="utf-8")
ROOT = os.path.dirname(os.path.abspath(__file__))
FFMPEG = r"C:\Users\AI01_\AppData\Local\Temp\opencode\ffmpeg\bin\ffmpeg.exe"
FFPROBE = r"C:\Users\AI01_\AppData\Local\Temp\opencode\ffmpeg\bin\ffprobe.exe"
WEB_BOX = os.path.join(ROOT, "web", "data", "box.json")
BOX_SET = os.path.join(ROOT, "box_set.json")
SRC_ROOT = os.path.join(ROOT, "Discos")
MUSIC_OUT = os.path.join(ROOT, "web", "public", "music")
EQ = "equalizer=f=3000:t=q:w=1.2:g=2.5,equalizer=f=9000:t=q:w=1:g=2"


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
        return round(60.0 / (lag * hop_s), 1)
    except Exception:
        return None


def parse(name):
    m = re.match(r"^(\d+)\s*-\s*(.+)\.mp3$", name)
    return (int(m.group(1)), m.group(2)) if m else None


def transcode(src, dest):
    os.makedirs(os.path.dirname(dest), exist_ok=True)
    subprocess.run(
        [FFMPEG, "-y", "-hide_banner", "-loglevel", "error",
         "-i", src, "-af", EQ, "-c:a", "libmp3lame", "-abr", "1", "-b:a", "160k",
         "-id3v2_version", "3", "-map_metadata", "-1", dest],
        check=True)


def main():
    with open(WEB_BOX, encoding="utf-8") as fh:
        discos = json.load(fh)
    total = 0
    for dis in discos:
        folder = os.path.join(SRC_ROOT, dis["slug"])
        if not os.path.isdir(folder):
            continue
        have = {}
        for name in sorted(os.listdir(folder)):
            if name.lower().endswith(".mp3"):
                p = parse(name)
                if p:
                    have[p[1]] = name
        print("=" * 8, dis["slug"], "=" * 8)
        for t in dis["tracklist"]:
            n = t["n"]
            path = os.path.join(folder, t["nombre"])
            state = "OK"
            if not os.path.isfile(path):
                state = "FALTA ARCHIVO"
                print(f"  {n:02d} {t['titulo']:35s} {state}")
                continue
            dur = duration(path)
            if dur is None:
                print(f"  {n:02d} {t['titulo']:35s} ERROR ffprobe")
                continue
            old = t.get("duracion") or 0
            delta = abs(dur - old)
            if delta > 0.3:
                state = f"DURO {old}->{dur}" if old else "DURACION NUEVA"
                t["duracion"] = dur
            if not t.get("bpm"):
                t["bpm"] = bpm_estimate(path)
                state += f" BPM {t['bpm']}"
            dest = os.path.join(MUSIC_OUT, dis["slug"], f"{n:02d}.mp3")
            if delta > 1.5 or not os.path.isfile(dest):
                if os.path.isfile(dest):
                    os.remove(dest)
                transcode(path, dest)
                state += " REENCOD"
            print(f"  {n:02d} {t['titulo']:35s} {state}")
            total += 1
        nuevos = []
        for title, name in have.items():
            if not any(t.get("titulo") == title for t in dis["tracklist"]):
                nuevos.append(name)
        for name in nuevos:
            num, title = parse(name)
            path = os.path.join(folder, name)
            dur = duration(path)
            bpm = bpm_estimate(path)
            t = {
                "n": num,
                "archivo": f"{title}.mp3",
                "nombre": name,
                "titulo": title,
                "bpm": bpm,
                "tonalidad": None,
                "duracion": dur,
                "audio": f"/music/{dis['slug']}/{num:02d}.mp3",
            }
            dis["tracklist"].append(t)
            transcode(path, os.path.join(MUSIC_OUT, dis["slug"], f"{num:02d}.mp3"))
            print(f"  + NUEVO {num:02d} {title} ({dur}s BPM {bpm})")
            total += 1
        dis["tracklist"].sort(key=lambda x: x["n"])

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
    print("TOTAL", total, "temas")


main()