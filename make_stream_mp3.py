# -*- coding: utf-8 -*-
import json, os, re, subprocess, sys

sys.stdout.reconfigure(encoding="utf-8")
ROOT = os.path.dirname(os.path.abspath(__file__))
FFMPEG = r"C:\Users\AI01_\AppData\Local\Temp\opencode\ffmpeg\bin\ffmpeg.exe"
BITRATE = "160k"
EQ = "equalizer=f=3000:t=q:w=1.2:g=2.5,equalizer=f=9000:t=q:w=1:g=2"

WEB_BOX = os.path.join(ROOT, "web", "data", "box.json")
SRC_ROOT = os.path.join(ROOT, "Discos")
MUSIC_OUT = os.path.join(ROOT, "web", "public", "music")


def disco_mp3s(folder):
    d = os.path.join(SRC_ROOT, folder)
    if not os.path.isdir(d):
        return {}
    out = {}
    for name in sorted(os.listdir(d)):
        if not name.lower().endswith(".mp3"):
            continue
        m = re.match(r"^(\d+)\s*-\s*(.+)\.mp3$", name)
        if m:
            out[int(m.group(1))] = os.path.join(d, name)
    return out


def transcode(src, dest):
    os.makedirs(os.path.dirname(dest), exist_ok=True)
    subprocess.run(
        [FFMPEG, "-y", "-hide_banner", "-loglevel", "error",
         "-i", src, "-af", EQ, "-c:a", "libmp3lame", "-abr", "1", "-b:a", BITRATE,
         "-id3v2_version", "3", "-map_metadata", "-1", dest],
        check=True)


def main():
    with open(WEB_BOX, encoding="utf-8") as fh:
        discos = json.load(fh)

    made = skipped = 0
    for d in discos:
        slug = d["slug"]
        folder = d["slug"]
        files = disco_mp3s(folder)
        for t in d["tracklist"]:
            n = t["n"]
            path = files.get(n)
            if not path:
                print("FALTA", slug, n, t["titulo"])
                continue
            dest = os.path.join(MUSIC_OUT, slug, f"{n:02d}.mp3")
            if not os.path.exists(dest):
                transcode(path, dest)
                made += 1
            else:
                skipped += 1
            t["audio"] = f"/music/{slug}/{n:02d}.mp3"
        print("disco", slug, "ok")

    with open(WEB_BOX, "w", encoding="utf-8") as fh:
        json.dump(discos, fh, ensure_ascii=False, indent=1)

    with open(os.path.join(ROOT, "box_set.json"), encoding="utf-8") as fh:
        discos_root = json.load(fh)
    by_slug = {d["slug"]: d for d in discos_root}
    for d in discos:
        dr = by_slug.get(d["slug"])
        if dr is None:
            print("box_set sin disco", d["slug"])
            continue
        audios = {t["n"]: t.get("audio") for t in d["tracklist"]}
        for tr in dr["tracklist"]:
            tr["audio"] = audios.get(tr["n"])
    with open(os.path.join(ROOT, "box_set.json"), "w", encoding="utf-8") as fh:
        json.dump(discos_root, fh, ensure_ascii=False, indent=1)

    total = sum(os.path.getsize(os.path.join(dp, f))
                for dp, _, fs in os.walk(MUSIC_OUT) for f in fs)
    print(f"generados={made} yaExistian={skipped} total={total/1024/1024:.1f}MB")


main()