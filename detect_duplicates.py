# -*- coding: utf-8 -*-
import os, sys, json, itertools
import numpy as np
import librosa
import imageio_ffmpeg

sys.stdout.reconfigure(encoding="utf-8")

FFDIR = os.path.dirname(imageio_ffmpeg.get_ffmpeg_exe())
os.environ["PATH"] = FFDIR + os.pathsep + os.environ.get("PATH", "")

OUT = r"C:\AI\Antigravity\musica"
SRC = r"C:\Discografia"

with open(os.path.join(OUT, "features.json"), encoding="utf-8") as fh:
    feats = json.load(fh)

def fingerprint(rel):
    y, sr = librosa.load(os.path.join(SRC, rel), sr=22050, mono=True, duration=180)
    chroma = librosa.feature.chroma_cqt(y=y, sr=sr).mean(axis=1)
    mel = librosa.feature.melspectrogram(y=y, sr=sr, n_mels=16).mean(axis=1)
    mel = mel / (mel.max() + 1e-9)
    return np.concatenate([chroma, mel])

db = {}
for f in feats:
    if "error" in f:
        continue
    try:
        db[f["archivo"]] = fingerprint(f["archivo"])
        print(f"FP: {f['archivo']}", flush=True)
    except Exception as e:
        print(f"FP ERROR {f['archivo']}: {e}", flush=True)

keys = sorted(db)
pairs = []
for a, b in itertools.combinations(keys, 2):
    ca = np.corrcoef(db[a], db[b])[0, 1]
    if ca >= 0.85:
        da = feats[[i for i, f in enumerate(feats) if f["archivo"] == a][0]].get("error") is None
        durA = None
        durB = None
        for f in feats:
            if f["archivo"] == a:
                durA = f.get("duracion")
            if f["archivo"] == b:
                durB = f.get("duracion")
        pairs.append((round(ca, 3), a, b, durA, durB))

pairs.sort(reverse=True)
print("\n=== SIMILARIDADES (corr >= 0.85) ===")
for ca, a, b, da, db_ in pairs:
    flag = " <-- IDENTICAS" if da and db_ and abs(da - db_) < 20 else ""
    print(f"{ca}  {a}  |  {b}  (dur {da:.0f}s vs {db_:.0f}s){flag}")

with open(os.path.join(OUT, "duplicados.json"), "w", encoding="utf-8") as fh:
    json.dump([{"corr": p[0], "a": p[1], "b": p[2]} for p in pairs], fh, ensure_ascii=False, indent=1)