# -*- coding: utf-8 -*-
import os, sys, json, re, shutil
from mutagen.mp3 import MP3

sys.stdout.reconfigure(encoding="utf-8")

SRC = r"C:\Discografia"
OUT = r"C:\AI\Antigravity\musica"
BOX = os.path.join(OUT, "Discos")

with open(os.path.join(OUT, "features.json"), encoding="utf-8") as fh:
    FEATS = json.load(fh)
ME = {f["archivo"]: f for f in FEATS}

DISCOS = [
    {"slug": "Disco_1_Medianoche", "numero": 1, "titulo": "Medianoche",
     "subtitulo": "Baladas que se escuchan a oscuras",
     "bpm_min": 0, "bpm_max": 99.5, "ambito": "menos de 100 BPM"},
    {"slug": "Disco_2_Ciudad_de_Neon", "numero": 2, "titulo": "Ciudad de Neon",
     "subtitulo": "Amores que brillan entre las luces",
     "bpm_min": 99.5, "bpm_max": 114.9, "ambito": "100-115 BPM"},
    {"slug": "Disco_3_Ochentas", "numero": 3, "titulo": "Ochentas",
     "subtitulo": "El destello de una decada",
     "bpm_min": 114.9, "bpm_max": 126.9, "ambito": "115-127 BPM"},
    {"slug": "Disco_4_Llamas", "numero": 4, "titulo": "Llamas",
     "subtitulo": "Cuando el corazon se enciende",
     "bpm_min": 126.9, "bpm_max": 149.9, "ambito": "127-150 BPM"},
    {"slug": "Disco_5_Euforia", "numero": 5, "titulo": "Euforia",
     "subtitulo": "Ritmos que levantan el animo",
     "bpm_min": 149.9, "bpm_max": 999, "ambito": "mas de 150 BPM"},
]

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

def file_title(fname):
    base = os.path.basename(fname)
    base = base[:-4] if base.lower().endswith(".mp3") else base
    t = re.sub(r"\([^)]*remix[^)]*\)", "", base, flags=re.IGNORECASE)
    t = re.sub(r"[_-]+", " ", t)
    t = re.sub(r"\s+", " ", t).strip()
    if t:
        t = t[0].upper() + t[1:]
    return t or base

def real_dur(rel):
    try:
        return MP3(os.path.join(SRC, rel)).info.length
    except Exception:
        return 0.0

def banda(bpm):
    for d in DISCOS:
        if d["bpm_min"] < bpm <= d["bpm_max"]:
            return d["slug"]
    return DISCOS[-1]["slug"]

groups = {d["slug"]: [] for d in DISCOS}
for rel in ME:
    groups[banda(ME[rel]["tempo_bpm"])].append(rel)

def sort_key(rel):
    return (ME[rel]["tempo_bpm"], -ME[rel]["energia_relativa"], display_title(rel))

for k in groups:
    groups[k].sort(key=sort_key)

estructura = []
for d in DISCOS:
    ddir = os.path.join(BOX, d["slug"])
    os.makedirs(ddir, exist_ok=True)
    tracklist = []
    for i, rel in enumerate(groups[d["slug"]], 1):
        name = "%02d - %s.mp3" % (i, file_title(rel))
        shutil.copy2(os.path.join(SRC, rel), os.path.join(ddir, name))
        dur = real_dur(rel)
        tracklist.append({"n": i, "archivo": rel, "nombre": name,
                          "titulo": display_title(rel), "bpm": ME[rel]["tempo_bpm"],
                          "duracion": dur, "tonalidad": ME[rel].get("key", "?")})
    d["tracklist"] = tracklist
    d["ruta"] = ddir
    estructura.append({"numero": d["numero"], "titulo": d["titulo"],
                       "slug": d["slug"], "ambito": d["ambito"],
                       "subtitulo": d["subtitulo"], "tracklist": tracklist})
    total = sum(t["duracion"] for t in tracklist)
    print("%s (%d temas, %dm)" % (d["titulo"], len(tracklist), int(total // 60)))
    for t in tracklist:
        print("   %02d %-42s %4.0f BPM" % (t["n"], t["titulo"], t["bpm"]))

for d in DISCOS:
    ddir = d["ruta"]
    ext = []
    for t in d["tracklist"]:
        ext.append("#EXTINF:%d,%s" % (int(t["duracion"]), t["titulo"]))
        ext.append(t["nombre"])
    with open(os.path.join(ddir, "playlist.m3u"), "w", encoding="utf-8-sig") as fh:
        fh.write("#EXTM3U\n" + "\n".join(ext) + "\n")

ext = ["#EXTM3U"]
for d in DISCOS:
    for t in d["tracklist"]:
        ext.append("#EXTINF:%d,%s" % (int(t["duracion"]), t["titulo"]))
        ext.append(os.path.join(d["slug"], t["nombre"]))
with open(os.path.join(BOX, "Coleccion_5_Discos.m3u"), "w", encoding="utf-8-sig") as fh:
    fh.write("\n".join(ext) + "\n")

with open(os.path.join(OUT, "box_set.json"), "w", encoding="utf-8") as fh:
    json.dump(estructura, fh, ensure_ascii=False, indent=1)

tot = sum(len(d["tracklist"]) for d in DISCOS)
print("TOTAL:", tot, "temas en 5 discos")