# -*- coding: utf-8 -*-
"""Re-seleccion: reparte los 78 temas entre los 5 discos (Directo queda vacio)
buscando que cada disco tenga mix de lentas/medias/rapidas y cantidad similar.
Orden aleatorio dentro de cada disco. Mueve los archivos fisicos y reconstruye
box.json + box_set.json."""
import json, os, re, random, shutil, sys
sys.stdout.reconfigure(encoding="utf-8")
ROOT = os.path.dirname(os.path.abspath(__file__))
WEB_BOX = os.path.join(ROOT, "web", "data", "box.json")
BOX_SET = os.path.join(ROOT, "box_set.json")
SRC_ROOT = os.path.join(ROOT, "Discos")


def cls(bpm):
    if bpm is None:
        return "?"
    if bpm < 100:
        return "L"
    if bpm < 135:
        return "M"
    return "R"


NOM = {"L": "LENTA", "M": "MEDIA", "R": "RAPIDA", "?": "DESC"}


def main():
    with open(WEB_BOX, encoding="utf-8") as fh:
        box = json.load(fh)
    discos = [d for d in box if d["slug"] != "Disco_6_Directo"]
    directo = next(d for d in box if d["slug"] == "Disco_6_Directo")

    tracks = []
    for dis in discos:
        for t in dis["tracklist"]:
            tracks.append({
                "titulo": t["titulo"],
                "bpm": t.get("bpm"),
                "tonalidad": t.get("tonalidad"),
                "duracion": t.get("duracion"),
                "src_slug": dis["slug"],
                "src_name": t["nombre"],
            })

    print("ANALISIS TEMA POR TEMA")
    for t in sorted(tracks, key=lambda x: x["bpm"] or 0):
        print("  %-4s %6s %34s" % (cls(t["bpm"]), t["bpm"], t["titulo"][:34]))
    print("  total", len(tracks))

    disc_tracks = [[] for _ in discos]
    for c in "LMR":
        members = [t for t in tracks if cls(t["bpm"]) == c]
        random.shuffle(members)
        start = random.randrange(len(discos))
        for i, t in enumerate(members):
            disc_tracks[(start + i) % len(discos)].append(t)

    for i, lst in enumerate(disc_tracks):
        random.shuffle(lst)
        by_cls = {x: sum(1 for t in lst if cls(t["bpm"]) == x) for x in "LMR"}
        print("\n%s -> %d temas  (L%s M%s R%s)" % (discos[i]["slug"], len(lst),
                                                   by_cls["L"], by_cls["M"], by_cls["R"]))
        for n, t in enumerate(lst, 1):
            print("   %02d %-4s %6s %s" % (n, cls(t["bpm"]), t["bpm"], t["titulo"][:30]))

    for lst in disc_tracks:
        for n, t in enumerate(lst, 1):
            src = os.path.join(SRC_ROOT, t["src_slug"], t["src_name"])
            dst = os.path.join(SRC_ROOT, discos[disc_tracks.index(lst)]["slug"],
                               "%02d - %s.mp3" % (n, t["titulo"]))
            if os.path.abspath(src) != os.path.abspath(dst):
                os.makedirs(os.path.dirname(dst), exist_ok=True)
                os.rename(src, dst)

    for i, lst in enumerate(disc_tracks):
        slug = discos[i]["slug"]
        tl = []
        for n, t in enumerate(lst, 1):
            tl.append({
                "n": n,
                "archivo": "%s.mp3" % t["titulo"],
                "nombre": "%02d - %s.mp3" % (n, t["titulo"]),
                "titulo": t["titulo"],
                "bpm": t["bpm"],
                "tonalidad": t["tonalidad"],
                "duracion": t["duracion"],
                "audio": "/music/%s/%02d.mp3" % (slug, n),
            })
        discos[i]["tracklist"] = tl
    directo["tracklist"] = []

    with open(WEB_BOX, "w", encoding="utf-8") as fh:
        json.dump(box, fh, ensure_ascii=False, indent=1)
    with open(BOX_SET, encoding="utf-8") as fh:
        discos_set = json.load(fh)
    by_slug = {d["slug"]: d for d in discos_set}
    for dis in discos:
        if by_slug.get(dis["slug"]):
            by_slug[dis["slug"]]["tracklist"] = dis["tracklist"]
    if by_slug.get("Disco_6_Directo"):
        by_slug["Disco_6_Directo"]["tracklist"] = []
    with open(BOX_SET, "w", encoding="utf-8") as fh:
        json.dump(discos_set, fh, ensure_ascii=False, indent=1)
    print("\nTOTAL", sum(len(d["tracklist"]) for d in discos), "temas en 5 discos")


main()