# -*- coding: utf-8 -*-
import json, sys
sys.stdout.reconfigure(encoding="utf-8")
d = json.load(open("web/data/box.json", encoding="utf-8"))
rows = []
for dis in d:
    for t in dis["tracklist"]:
        rows.append((t["titulo"], t.get("bpm"), t.get("tonalidad"), dis["slug"]))
rows.sort(key=lambda r: (r[1] is None, r[1] or 0))
for tit, bpm, ton, slug in rows:
    print("%6s %5s  %-34s %s" % (str(bpm), str(ton or "-"), tit[:34], slug))
print("total", len(rows))