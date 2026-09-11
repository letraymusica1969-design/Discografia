# -*- coding: utf-8 -*-
import os, sys, json, itertools
import numpy as np
import librosa
import imageio_ffmpeg
from mutagen.mp3 import MP3

sys.stdout.reconfigure(encoding="utf-8")

FFDIR = os.path.dirname(imageio_ffmpeg.get_ffmpeg_exe())
os.environ["PATH"] = FFDIR + os.pathsep + os.environ.get("PATH", "")

OUT = r"C:\AI\Antigravity\musica"
SRC = r"C:\Discografia"

with open(os.path.join(OUT, "features.json"), encoding="utf-8") as fh:
    feats = json.load(fh)

def real_dur(rel):
    try:
        return MP3(os.path.join(SRC, rel)).info.length
    except Exception:
        return None

def signature(rel):
    y, sr = librosa.load(os.path.join(SRC, rel), sr=22050, mono=True, duration=300)
    tempo, beats = librosa.beat.beat_track(y=y, sr=sr, units="time")
    chroma = librosa.feature.chroma_cqt(y=y, sr=sr)
    times = librosa.times_like(chroma, sr=sr)
    if len(beats) < 8:
        n = 16
        idx = np.linspace(0, len(chroma.T) - 1, n).astype(int)
        frames = np.array_split(chroma.T, n)
    else:
        frames = []
        edges = list(beats)
        edges.append(times[-1])
        for i in range(len(edges) - 1):
            a, b = edges[i], edges[i + 1]
            sel = (times >= a) & (times < b)
            if sel.sum() > 0:
                frames.append(chroma[:, sel].mean(axis=1))
        if len(frames) < 8:
            n = 16
            frames = np.array_split(chroma.T, n)
    sig = np.concatenate([f for f in frames])[: 12 * 16]
    mfcc = librosa.feature.mfcc(y=y, sr=sr, n_mfcc=13)
    mmean = mfcc.mean(axis=1)
    mstd = mfcc.std(axis=1)
    return np.concatenate([sig, mmean, mstd])

db = {}
meta = {}
for f in feats:
    rel = f["archivo"]
    if "error" in f:
        continue
    meta[rel] = f
    db[rel] = real_dur(rel)

print("Firmas (beat-synced chroma)...")
sigs = {}
for rel in db:
    try:
        sigs[rel] = signature(rel)
    except Exception as e:
        print(f"  ERROR {rel}: {e}", flush=True)

keys = sorted(sigs)
pairs = []
for a, b in itertools.combinations(keys, 2):
    fa, fb = meta[a], meta[b]
    if abs(fa["tempo_bpm"] - fb["tempo_bpm"]) > 4:
        continue
    if db[a] is None or db[b] is None or abs(db[a] - db[b]) > 45:
        continue
    va, vb = sigs[a], sigs[b]
    if len(va) != len(vb):
        continue
    if np.linalg.norm(va) == 0 or np.linalg.norm(vb) == 0:
        continue
    c = float(np.corrcoef(va, vb)[0, 1])
    if c >= 0.92:
        pairs.append((round(c, 4), a, b, round(db[a]), round(db[b])))

pairs.sort(reverse=True)
print("\n=== POSIBLES DUPLICADOS (corr >= 0.92) ===")
for c, a, b, da, db_ in pairs:
    print(f"{c:.3f}  {a}  |  {b}  ({da}s vs {db_}s)")

with open(os.path.join(OUT, "duplicados.json"), "w", encoding="utf-8") as fh:
    json.dump([{"corr": p[0], "a": p[1], "b": p[2], "dur_a": p[3], "dur_b": p[4]} for p in pairs],
              fh, ensure_ascii=False, indent=1)