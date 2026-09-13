# -*- coding: utf-8 -*-
"""Genera el pack USB para el sistema multimedia VW MIB:
- 79 temas por disco (misma versión que la web), renombrados NN - Title.mp3
- tags ID3v2.3 (titulo, artista San Cougar, album, track/total, disco, año, género)
- portada incrustada (600x600) + folder.jpg por disco
- playlists .m3u por disco + una completa
"""
import json, os, shutil, subprocess, sys
sys.stdout.reconfigure(encoding="utf-8")

ROOT = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(ROOT, "Para_el_auto")
FF = r"C:\Users\AI01_\AppData\Local\Temp\opencode\ffmpeg\bin\ffmpeg.exe"
ARTISTA = "San Cougar"
GEN = "Pop"
TOTAL = 79


def main():
    if os.path.isdir(OUT):
        shutil.rmtree(OUT)
    box = json.load(open(os.path.join(ROOT, "web", "data", "box.json"), encoding="utf-8"))
    discos = [d for d in box if d["slug"] != "Disco_6_Directo"]
    n_disc = len(discos)

    completa = []
    n_audio = 0
    for d in discos:
        carpeta = os.path.join(OUT, "Vol%02d - %s" % (d["numero"], d["titulo"]))
        os.makedirs(carpeta, exist_ok=True)
        cover_src = os.path.join(ROOT, "web", "public", "covers", d["slug"] + "_front.jpg")
        lista = []
        for t in d["tracklist"]:
            src = os.path.join(ROOT, "web", "public", "music", d["slug"], "%02d.mp3" % t["n"])
            dst = os.path.join(carpeta, t["nombre"])
            cmd = [FF, "-y", "-loglevel", "error", "-i", src, "-i", cover_src,
                   "-map", "0:a", "-map", "1", "-map_metadata", "-1",
                   "-c:a", "copy", "-c:v", "mjpeg", "-q:v", "4", "-vf", "scale=600:-1",
                   "-id3v2_version", "3", "-disposition:v:0", "attached_pic",
                   "-metadata", "title=%s" % t["titulo"],
                   "-metadata", "artist=%s" % ARTISTA,
                   "-metadata", "album_artist=%s" % ARTISTA,
                   "-metadata", "album=%s" % d["titulo"],
                   "-metadata", "date=2026",
                   "-metadata", "track=%d/%d" % (t["n"], len(d["tracklist"])),
                   "-metadata", "disc=%d/%d" % (d["numero"], n_disc),
                   "-metadata", "genre=%s" % GEN,
                   "-metadata:s:v", "title=Album cover",
                   "-metadata:s:v", "comment=Cover (front)",
                   dst]
            subprocess.run(cmd, check=True)
            lista.append(d["titulo"] + "/" + t["nombre"])
            completa.append("Vol%02d - %s/%s" % (d["numero"], d["titulo"], t["nombre"]))
            n_audio += 1
        shutil.copy2(cover_src, os.path.join(carpeta, "folder.jpg"))
        with open(os.path.join(carpeta, d["titulo"] + ".m3u"), "w", encoding="utf-8") as fh:
            fh.write("\n".join(t.split("/", 1)[1] for t in lista))
    with open(os.path.join(OUT, "Box_Set_Canciones_de_una_ciudad.m3u"), "w", encoding="utf-8") as fh:
        fh.write("\n".join(completa))

    instrucciones = [
        "BAND SONORA PARA EL AUTO - CANCIONES DE UNA CIUDAD",
        "Artista: San Cougar  |  79 temas en 5 discos  |  2026",
        "",
        "COMO INSTALAR (SISTEMAS VW MIB / MIB2 / MIB3):",
        "1) Copia TODO el contenido de esta carpeta a la raiz de una memoria",
        "   USB (o tarjeta SD) formateada en FAT32 o exFAT.",
        "2) Sin carpetas anidadas ni archivos de mas en la raiz.",
        "3) Conectala al puerto USB del auto y elegí la fuente de medios USB.",
        "4) Elegí por disco (Medianoche, Ciudad de Neon, Ochentas, Llamas,",
        "   Euforia) o la playlist completa Box_Set_Canciones_de_una_ciudad.m3u",
        "",
        "DATOS:",
        "  - Formato MP3 (160 kbps avg) + portadas incrustadas y folder.jpg.",
        "  - Tags ID3v2.3: titulo, artista, album, numero de pista y de disco,",
        "    anio 2026. Lo lee el MIB de forma nativa, sin internet.",
        "  - El orden por disco es: mezcla equilibrada de temas lentos y",
        "    rapidos, el mismo del sitio web.",
    ]
    with open(os.path.join(OUT, "INSTALAR.txt"), "w", encoding="utf-8") as fh:
        fh.write("\n".join(instrucciones))

    mb = sum(os.path.getsize(os.path.join(dp, f))
             for dp, _, fs in os.walk(OUT) for f in fs) / 1024 / 1024
    print("temas:", n_audio, "| carpetas:", 1 + n_disc, "| total: %.1f MB" % mb)


main()