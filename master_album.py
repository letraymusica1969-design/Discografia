# -*- coding: utf-8 -*-
import os, sys, json, re
import master_track as mt

sys.stdout.reconfigure(encoding="utf-8")

OUT = mt.OUT
MASTER = mt.MASTER
SRC = r"C:\Discografia"

with open(os.path.join(OUT, "features.json"), encoding="utf-8") as fh:
    feats = json.load(fh)
ME = {f["archivo"]: f for f in feats}

STYLES = {
    "A1": ("A1_Baladas_y_Desamor", "< 100 BPM"),
    "A2": ("A2_Pop_Midtempo", "100–129 BPM"),
    "A3": ("A3_Ritmos_Vivos", "≥ 130 BPM"),
}

def estilo(f):
    bpm = ME[f]["tempo_bpm"]
    return "A1" if bpm < 100 else ("A2" if bpm < 130 else "A3")

def clean_title(fname):
    base = fname[:-4] if fname.lower().endswith(".mp3") else fname
    t = re.sub(r"\([^)]*remix[^)]*\)", "", base, flags=re.IGNORECASE)
    t = re.sub(r"\s+", " ", t).strip()
    if not t:
        t = base
    return t[0].upper() + t[1:] if t else t

groups = {k: [] for k in STYLES}
for fname in sorted(ME):
    groups[estilo(fname)].append(fname)

def song_key(fname):
    f = ME[fname]
    return (f["tempo_bpm"], -f["energia_relativa"], clean_title(fname))

for k in groups:
    groups[k].sort(key=song_key)

def process_act(act):
    d = os.path.join(MASTER, STYLES[act][0])
    os.makedirs(d, exist_ok=True)
    done, skipped, failed = 0, 0, 0
    for i, fname in enumerate(groups[act], 1):
        name = f"{i:02d} - {clean_title(fname)}.flac"
        dst = os.path.join(d, name)
        if os.path.exists(dst):
            print(f"  [skip] {name}")
            skipped += 1
            continue
        src = os.path.join(SRC, fname)
        try:
            print(f"  [{i:02d}] {fname}", flush=True)
            meas = mt.measure(src)
            mt.apply_chain(src, dst, meas)
            done += 1
        except Exception as e:
            failed += 1
            print(f"  !! ERROR {fname}: {e}", flush=True)
    print(f"Acto {act}: {done} ok, {skipped} previos, {failed} fallidos")

if __name__ == "__main__":
    for act in sys.argv[1:]:
        process_act(act)