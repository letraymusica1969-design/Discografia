# -*- coding: utf-8 -*-
import os, sys, json, subprocess
import numpy as np
import librosa
import imageio_ffmpeg

sys.stdout.reconfigure(encoding="utf-8")
sys.stderr.reconfigure(encoding="utf-8")

FFMPEG = os.path.dirname(imageio_ffmpeg.get_ffmpeg_exe())
os.environ["PATH"] = FFMPEG + os.pathsep + os.environ.get("PATH", "")

SRC = r"C:\Discografia"
OUT = r"C:\AI\Antigravity\musica"

KRUMP = np.array([6.35,2.23,3.48,2.33,4.38,4.09,2.52,5.19,2.39,3.66,2.29,2.88])
KRYMN = np.array([6.33,2.68,3.52,5.38,2.60,3.53,2.54,4.75,3.98,2.69,3.34,3.17])
PITCH = ["Do","Do#","Re","Re#","Mi","Fa","Fa#","Sol","Sol#","La","La#","Si"]
MAJOR_KEYS = ["Do","Sol","Re","La","Mi","Si","Fa#","Do#","Fa","Sib","Mib","Lab"]

def key_estimate(chroma):
    prof = np.sum(chroma, axis=1)
    prof = prof / (np.sum(prof) + 1e-8)
    best = (0, -np.inf, None)
    for i in range(12):
        for name, tmpl in (("mayor", KRUMP), ("menor", KRYMN)):
            corr = np.corrcoef(np.roll(tmpl, i), prof)[0, 1]
            if corr > best[1]:
                best = (i, corr, name)
    i, corr, mode = best
    buf = KRUMP if mode == "mayor" else KRYMN
    key = PITCH[int(np.argmax(np.roll(buf, i)))]
    rel = (int(np.argmax(np.roll(buf, i))) - i) % 12
    mode = "mayor" if rel == 0 else "menor"
    return key, mode

def analyze(path, dur=180):
    y, sr = librosa.load(path, sr=22050, mono=True, duration=dur)
    n = len(y)
    rms = librosa.feature.rms(y=y)[0]
    cent = librosa.feature.spectral_centroid(y=y, sr=sr)[0]
    zcr = librosa.feature.zero_crossing_rate(y)[0]
    onset_env = librosa.onset.onset_strength(y=y, sr=sr)
    tempo = librosa.feature.tempo(onset_envelope=onset_env, sr=sr)[0]
    chroma = librosa.feature.chroma_cqt(y=y, sr=sr)
    key, mode = key_estimate(chroma)
    dyn = librosa.feature.rms(y=y, frame_length=2048, hop_length=512)[0]
    loud = float(np.mean(dyn))
    return {
        "duracion": float(n / sr),
        "tempo_bpm": round(float(tempo), 1),
        "key": key,
        "modo": mode,
        "rms_medio": loud,
        "centroide_hz": float(np.mean(cent)),
        "tasa_cruce_cero": float(np.mean(zcr)),
        "energia_relativa": float(np.mean(rms)),
    }

files = []
for root, dirs, fs in os.walk(SRC):
    for f in fs:
        if f.lower().endswith(".mp3"):
            rel = os.path.relpath(os.path.join(root, f), SRC)
            files.append(rel)
files.sort()
results = []
for rel in files:
    src = os.path.join(SRC, rel)
    print(f"Analizando: {rel}", flush=True)
    try:
        feats = analyze(src)
    except Exception as e:
        print(f"  ERROR {rel}: {e}", flush=True)
        feats = {"error": str(e)}
    feats["archivo"] = rel.replace("\\", "/")
    results.append(feats)

os.makedirs(OUT, exist_ok=True)
with open(os.path.join(OUT, "features.json"), "w", encoding="utf-8") as fh:
    json.dump(results, fh, ensure_ascii=False, indent=1)

print("Listo: features.json")