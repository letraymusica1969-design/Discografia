# -*- coding: utf-8 -*-
import os, sys, json, re, shutil
from mutagen.mp3 import MP3

sys.stdout.reconfigure(encoding="utf-8")
sys.stderr.reconfigure(encoding="utf-8")

SRC = r"C:\Discografia"
OUT = r"C:\AI\Antigravity\musica"

with open(os.path.join(OUT, "features.json"), encoding="utf-8") as fh:
    feats = json.load(fh)

ME = {f["archivo"]: f for f in feats}

STYLES = [
    {"key": "A1", "dir": "A1_Baladas_y_Desamor", "nombre": "Acto I · Baladas y desamor",
     "rango": "< 100 BPM", "desc": "Canciones lentas, íntimas y emotivas. Son el corazón del álbum."},
    {"key": "A2", "dir": "A2_Pop_Midtempo", "nombre": "Acto II · Pop midtempo",
     "rango": "100–129 BPM", "desc": "Románticas de ritmo medio, brillantes y acompañadas."},
    {"key": "A3", "dir": "A3_Ritmos_Vivos", "nombre": "Acto III · Ritmos vivos",
     "rango": "≥ 130 BPM", "desc": "Enérgicas y bailables; la efervescencia del cierre."},
]

def mis_estilo(f):
    bpm = ME[f]["tempo_bpm"]
    if bpm < 100:
        return "A1"
    if bpm < 130:
        return "A2"
    return "A3"

def clean_title(fname):
    base = fname[:-4] if fname.lower().endswith(".mp3") else fname
    t = re.sub(r"\([^)]*remix[^)]*\)", "", base, flags=re.IGNORECASE)
    t = re.sub(r"\s+", " ", t).replace("(2)", "(2)").strip()
    t = re.sub(r"\s*-\s*$", "", t).strip()
    if not t:
        t = base
    t = t[0].upper() + t[1:] if t else t
    return t

def duracion(fname):
    try:
        return MP3(os.path.join(SRC, fname)).info.length
    except Exception:
        return 0.0

def fmt_duracion(seg):
    m, s = int(seg // 60), int(seg % 60)
    return f"{m}:{s:02d}"

def dinamica(rms):
    if rms < 0.10:
        return "suave"
    if rms < 0.125:
        return "media"
    return "alta"

groups = {s["key"]: [] for s in STYLES}
for fname in sorted(ME):
    groups[mis_estilo(fname)].append(fname)

def song_key(fname):
    f = ME[fname]
    return (f["tempo_bpm"], -f["energia_relativa"], clean_title(fname))

for k in groups:
    groups[k].sort(key=song_key)

# crear carpetas y copiar archivos
for s in STYLES:
    d = os.path.join(OUT, s["dir"])
    os.makedirs(d, exist_ok=True)
    for i, fname in enumerate(groups[s["key"]], 1):
        name = f"{i:02d} - {clean_title(fname)}.mp3"
        shutil.copy2(os.path.join(SRC, fname), os.path.join(d, name))

# playlists
def escribir_m3u(path, entries):
    with open(path, "w", encoding="utf-8-sig") as fh:
        fh.write("#EXTM3U\n")
        for e in entries:
            fh.write(e + "\n")

for s in STYLES:
    d = os.path.join(OUT, s["dir"])
    entries = []
    for i, f in enumerate(groups[s["key"]], 1):
        entries.append(f"#EXTINF:{int(duracion(f))},{clean_title(f)}")
        entries.append(f"{i:02d} - {clean_title(f)}.mp3")
    escribir_m3u(os.path.join(d, f"{s['key']}_playlist.m3u"), entries)

# playlist del album completo (obras en orden + bonus)
album_entries = []
line_num = 1
for s in STYLES:
    for fname in groups[s["key"]]:
        rel = os.path.join(s["dir"], f"{line_num:02d} - {clean_title(fname)}.mp3")
        album_entries.append(f"#EXTINF:{int(duracion(fname))},{clean_title(fname)}")
        album_entries.append(rel)
        line_num += 1
if "Ochentas (2).mp3" in ME and ME["Ochentas (2).mp3"]:
    pass
escribir_m3u(os.path.join(OUT, "ALBUM_Completo.m3u"), album_entries)

# ---- informe ----
total_dur = sum(duracion(f) for pf in groups.values() for f in pf)
lineas = []
lineas.append("# Luciano Saavedra — «Canciones de una ciudad»\n")
lineas.append("Compilación curada a partir de los 31 temas de `C:\\Discografia`, organizada")
lineas.append("por estilo musical (tempo y energía medidos por análisis de audio) como un")
lineas.append("álbum en tres actos.\n")
lineas.append(f"- **Temas:** 31   **Duración total:** {fmt_duracion(total_dur)}")
lineas.append("- **Análisis:** tempo (BPM), tonalidad, energía y brillo calculados con `librosa`.\n")

for s in STYLES:
    lineas.append(f"\n## {s['nombre']}  ·  {s['rango']}\n")
    lineas.append(f"_{s['desc']}_\n")
    lineas.append("| # | Título | Tonalidad | BPM | Duración | Dinámica |")
    lineas.append("|---|--------|-----------|-----|----------|----------|")
    for i, fname in enumerate(groups[s["key"]], 1):
        f = ME[fname]
        titulo = clean_title(fname)
        tono = f"{f['key'].replace('#','♯')} {f['modo']}"
        lineas.append(f"| {i:02d} | {titulo} | {tono} | {f['tempo_bpm']:.0f} | "
                      f"{fmt_duracion(duracion(fname))} | {dinamica(f['energia_relativa'])} |")

bonus = "Ochentas (2).mp3"
lineas.append(f"\n## Bonus track\n")
f = ME[bonus]
lineas.append(f"- **Ochentas (versión alternativa)** · {f['key'].replace('#','♯')} {f['modo']} · "
              f"{f['tempo_bpm']:.0f} BPM · {fmt_duracion(duracion(bonus))} — misma canción que el tema 18, "
              f"con mezcla/duración distinta. Incluida como variante.\n")

lineas.append("\n## Notas técnicas\n")
lineas.append("- Línea del álbum: el álbum progresa de lo íntimo (Acto I) hacia lo luminoso (Acto II)")
lineas.append("  y termina en efervescencia (Acto III), un arco pensado para escucharse de corrido.")
lineas.append("  La playlist `ALBUM_Completo.m3u` lo reproduce en este orden.\n")
lineas.append("- **Susurros Nocturnos** es la única a 320 kbps (estereo, 44,1 kHz); si se va a")
lineas.append("  remasterizar o subir, es la mejor fuente.\n")
lineas.append("- Metadatos originales con título sucio (ej. *Buenos Momentos (Remix)(Remix)(Remix)(Remix)*):")
lineas.append("  los archivos copiados quedaron renombrados en limpio, pero las etiquetas ID3 interiores")
lineas.append("  no se modificaron. ¿Quieres que las limpie también?\n")
lineas.append("\n**Estructura en disco:**\n")
for s in STYLES:
    lineas.append(f"- `{s['dir']}/` — {s['rango']} ({len(groups[s['key']])} temas + playlist)")
lineas.append("- `ALBUM_Completo.m3u` — playlist maestra\n")

with open(os.path.join(OUT, "INFORME.md"), "w", encoding="utf-8") as fh:
    fh.write("\n".join(lineas))

# resumen STDOUT
print("=== RESUMEN DEL ÁLBUM ===")
for s in STYLES:
    print(f"\n{s['nombre']} ({len(groups[s['key']])} temas)")
    for i, fname in enumerate(groups[s["key"]], 1):
        f = ME[fname]
        print(f"  {i:02d} {clean_title(fname)} — {f['tempo_bpm']:.0f} BPM")
print("\nEstructura generada en:", OUT)