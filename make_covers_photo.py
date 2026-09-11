# -*- coding: utf-8 -*-
import os, sys, json, math, time, urllib.request, urllib.parse
import numpy as np
from PIL import Image, ImageDraw, ImageFilter, ImageFont

sys.stdout.reconfigure(encoding="utf-8")

OUT = os.path.dirname(os.path.abspath(__file__))
TAPAS = os.path.join(OUT, "Discos", "Tapas")
SRC = os.path.join(TAPAS, "_src")
WEB = os.path.join(OUT, "web", "public", "covers")
S = 1500

FONTS = r"C:\Windows\Fonts"
F_BOD = os.path.join(FONTS, "BOD_BLAR.TTF")
F_SERIF = os.path.join(FONTS, "BOOKOS.TTF")
F_COND = os.path.join(FONTS, "AGENCYB.TTF")
F_COND_R = os.path.join(FONTS, "AGENCYR.TTF")
F_NARR = os.path.join(FONTS, "ARIALN.TTF")

THEMES = {
    "disco_1_medianoche": (["moon night forest silhouette",
                            "night fog trees moon", "moon mist landscape dark"],
                           ["moon", "nuit", "foret", "forest", "fog", "mist",
                            "night", "silhouette", "oscur", "nuit"]),
    "disco_2_ciudad": (["neon city street rain night lights",
                        "tokyo street night neon", "city skyline night lights traffic"],
                       ["neon", "tokyo", "rain", "street", "pud", "night",
                        "city", "sign", "yokohama", "street"]),
    "disco_3_ochentas": (["retro synthwave neon sunset",
                          "vaporwave sunset grid", "80s neon aesthetic purple sunset",
                          "synthwave horizon"],
                         ["synthwave", "vaporwave", "retro", "sunset", "neon",
                          "grid", "wave", "aesthetic", "scanline"]),
    "disco_4_llamas": (["purple lightning storm sky", "violet storm clouds dramatic",
                        "purple thunderstorm dramatic sky", "dark clouds sunset storm"],
                       ["purple", "storm", "lightning", "thunder", "violet",
                        "cloud", "dark", "sky", "skyline"]),
    "disco_5_euforia": (["concert confetti celebration colorful",
                         "carnival confetti festival fun", "joy celebration colorful crowd",
                         "party confetti colorful"],
                        ["confetti", "concer", "festival", "carnival", "celeb",
                         "party", "color", "crowd", "fun"]),
    "disco_6_directo": (["concert crowd stage lights silhouettes",
                         "live music crowd hands concert",
                         "rock concert stage light smoke"],
                        ["concer", "live", "stage", "crowd", "gig", "music",
                         "rock", "smoke", "live"]),
}

GOOD_LIC = {"cc0", "by", "by-sa", "pd"}


def fload(path, size):
    try:
        return ImageFont.truetype(path, int(size))
    except Exception:
        return ImageFont.truetype(os.path.join(FONTS, "arialbd.ttf"), int(size))


def tmp_d():
    return ImageDraw.Draw(Image.new("RGBA", (8, 8)))


def txt_w(td, txt, font):
    bb = td.textbbox((0, 0), txt, font=font)
    return bb[2] - bb[0]


def draw_spaced(dr, xy, txt, font, fill, ls=0, shadow=None):
    x, y = xy
    t = 0
    td = tmp_d()
    for ch in txt:
        dr.text((x + t, y), ch, font=font, fill=fill)
        bb = td.textbbox((0, 0), ch, font=font)
        t += bb[2] - bb[0] + ls
    return t


def draw_center(dr, xy, txt, font, fill, ls=0):
    td = tmp_d()
    w = sum((td.textbbox((0, 0), c, font=font)[2] - td.textbbox((0, 0), c, font=font)[0]
             + ls) for c in txt) - ls
    return draw_spaced(dr, (xy[0] - w / 2, xy[1]), txt, font, fill, ls)


def fit_font(text, maxw, base, kind=f"C:\\Windows\\Fonts\\BOD_BLAR.TTF"):
    sz = base
    td = tmp_d()
    while sz > 34:
        f = fload(kind, sz)
        bb = td.textbbox((0, 0), text, font=f)
        if bb[2] - bb[0] <= maxw:
            return f
        sz -= 5
    return fload(kind, 34)


def grain(arr, seed=7, amt=6):
    r = np.random.default_rng(seed).normal(0, amt, arr.shape[:-1])
    return np.clip(arr + r[:, :, None], 0, 255)


_last_call = 0.0


def _pace():
    global _last_call
    dt = time.time() - _last_call
    if dt < 6.0:
        time.sleep(6.0 - dt)
    _last_call = time.time()


def openverse(q, n=20, size="large", tries=4):
    params = {"q": q, "page_size": n, "license_type": "modification"}
    if size:
        params["size"] = size
    url = "https://api.openverse.org/v1/images/?" + urllib.parse.urlencode(params)
    for i in range(tries):
        _pace()
        req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
        try:
            with urllib.request.urlopen(req, timeout=45) as r:
                return json.loads(r.read().decode("utf-8")).get("results", [])
        except Exception as e:
            print("   API error:", e, "(reintento", i + 1, ")")
            time.sleep(8 * (i + 1))
    return []


def pick_and_dl(key, spec):
    dest = os.path.join(SRC, key + ".jpg")
    if os.path.exists(dest) and os.path.getsize(dest) > 60000:
        print("   ya existe", os.path.basename(dest))
        return dest
    queries, kws = spec
    res = []
    for q in queries:
        res = openverse(q)
        if len(res) < 4:
            res2 = openverse(q, size=None)
            res = res if len(res) >= len(res2) else res2
        if res:
            break
    if not res:
        raise SystemExit("   no hay resultados para " + key)
    cands = [x for x in res if x.get("license") in GOOD_LIC] or res
    big = [x for x in cands
           if min(x.get("width", 0) or 0, x.get("height", 0) or 0) >= 1100] or cands
    big.sort(key=lambda x: (x.get("width", 0) or 0) * (x.get("height", 0) or 0),
             reverse=True)
    matched = [x for x in big if any(k in (x.get("title") or "").lower()
                                     for k in kws)]
    ordered = (matched + [x for x in big if x not in matched])[:4]
    for attempt, c in enumerate(ordered):
        try:
            req = urllib.request.Request(c["url"], headers={"User-Agent": "Mozilla/5.0"})
            with urllib.request.urlopen(req, timeout=90) as r:
                data = r.read()
            if len(data) < 60000:
                continue
            with open(dest, "wb") as f:
                f.write(data)
            print("   elegida:", (c.get("title") or "")[:44], "|",
                  c.get("license"), "|", c.get("width"), "x", c.get("height"),
                  "|", len(data) // 1024, "KB")
            return dest
        except Exception as e:
            print("   fallo", c.get("url", "")[:60], e)
    raise SystemExit("   ningun candidato sirvio para " + key)


def load_src(path):
    im = Image.open(path).convert("RGB")
    w, h = im.size
    m = min(w, h)
    left = (w - m) // 2
    top = int((h - m) * 0.35)
    im = im.crop((left, top, left + m, top + m)).resize((S, S), Image.LANCZOS)
    return im


def soul(im, tint, contrast=1.15, vign=0.62, velo=0.35, lift_top=0.06,
         dark_bottom=0.30, grain_amt=5, seed=7):
    arr = np.asarray(im).astype(float)
    arr = (arr - 128) * contrast + 128
    lum = np.clip(arr[..., 0] * 0.3 + arr[..., 1] * 0.59 + arr[..., 2] * 0.11,
                  0, 255)
    w = np.clip((1 - lum / 255.0) ** 1.6, 0, 1) * 0.5
    arr = arr * (1 - w[..., None]) + np.array(tint)[None, None, :] * w[..., None]

    yy = np.linspace(0, 1, S)[:, None]
    xx = np.linspace(0, 1, S)[None, :]
    soft = np.asarray(im.filter(ImageFilter.GaussianBlur(52))).astype(float)
    d = np.sqrt((xx - 0.5) ** 2 + (yy - 0.5) ** 2) * 1.45
    wv = np.clip((d - 0.32) / 0.5, 0, 1) * velo
    arr = arr * (1 - wv[..., None]) + soft * wv[..., None]

    v = 1 - vign * np.clip((d - 0.35) / 0.62, 0, 1) ** 1.5
    arr *= v[..., None]
    arr += np.clip((yy - 0.15) * lift_top * 255, 0, 40)[..., None]
    arr *= (1 - dark_bottom * yy[..., None])
    arr = grain(arr, seed, grain_amt)
    return Image.fromarray(np.clip(arr, 0, 255).astype(np.uint8)).convert("RGBA")


def make_text_mask(txt, font, shift, stroke=0):
    m = Image.new("L", (S, S), 0)
    d = ImageDraw.Draw(m)
    bb = tmp_d().textbbox((0, 0), txt, font=font)
    ox = int((S - (bb[2] - bb[0])) / 2)
    oy = int(shift + (S - (bb[3] - bb[1])) / 2 - bb[1])
    d.text((ox, oy), txt, font=font, fill=255, stroke_width=stroke, stroke_fill=255)
    return m


def spaced_mask(txt, font, spacing, x, y):
    m = Image.new("L", (S, S), 0)
    d = ImageDraw.Draw(m)
    td = tmp_d()
    t = 0
    for ch in txt:
        d.text((x + t, y), ch, font=font, fill=255)
        bb = td.textbbox((0, 0), ch, font=font)
        t += bb[2] - bb[0] + spacing
    return m


def gold_artist(img, txt, font, spacing, metal, glow, seed=77):
    rng = np.random.default_rng(seed)
    x, y0p = 66, 70
    m = spaced_mask(txt, font, spacing, x, y0p)
    ys, xs = np.nonzero(np.asarray(m))
    if len(ys) == 0:
        return None
    by0, by1, bx0, bx1 = ys.min(), ys.max(), xs.min(), xs.max()
    deep, hi = metal

    gl = Image.new("RGBA", (S, S), glow + (255,))
    gl.putalpha(Image.fromarray((np.asarray(m) * 0.30).astype(np.uint8)))
    img.alpha_composite(gl.filter(ImageFilter.GaussianBlur(12)))

    sh = Image.new("RGBA", (S, S), (0, 0, 0, 185))
    sh.putalpha(Image.fromarray(np.asarray(m).copy()))
    shl = Image.new("RGBA", (S, S), (0, 0, 0, 0))
    shl.alpha_composite(sh, (0, 4))
    img.alpha_composite(shl.filter(ImageFilter.GaussianBlur(3)))

    yy2 = np.broadcast_to(np.arange(S)[:, None], (S, S)).astype(float)
    xx2 = np.broadcast_to(np.arange(S)[None, :], (S, S)).astype(float)
    ny = np.clip((yy2 - by0) / max(by1 - by0, 1), 0, 1)
    nx = np.clip((xx2 - bx0) / max(bx1 - bx0, 1), 0, 1)
    t = np.clip(0.42 * ny + 0.28 * nx, 0, 1)

    base = (np.maximum(deep, np.minimum(hi, t[..., None] * (np.array(hi) - np.array(deep))
                 + np.array(deep))))
    spec = np.exp(-((t - 0.74) / 0.16) ** 2)[..., None] * 130
    g = np.clip(base + spec + 20, 0, 255).astype(np.uint8)
    lay = Image.fromarray(g).convert("RGBA")
    lay.putalpha(Image.fromarray(np.asarray(m)))
    img.alpha_composite(lay)

    for sy, sx in ((by0 - 34, bx1 + 16), (by1 + 30, bx1 + 42), (by0 - 56, bx0 - 6)):
        r = int(rng.integers(5, 9))
        sp = Image.new("RGBA", (S, S), (0, 0, 0, 0))
        dd = ImageDraw.Draw(sp)
        col = tuple(min(c + 30, 255) for c in hi)
        dd.line([(sx - r, sy), (sx + r, sy)], fill=col + (210,), width=2)
        dd.line([(sx, sy - r), (sx, sy + r)], fill=col + (210,), width=2)
        img.alpha_composite(sp.filter(ImageFilter.GaussianBlur(1)))
    return bx1, by1
    m = Image.new("L", (S, S), 0)
    d = ImageDraw.Draw(m)
    bb = tmp_d().textbbox((0, 0), txt, font=font)
    ox = int((S - (bb[2] - bb[0])) / 2)
    oy = int(shift + (S - (bb[3] - bb[1])) / 2 - bb[1])
    d.text((ox, oy), txt, font=font, fill=255, stroke_width=stroke, stroke_fill=255)
    return m


def photo_title(img, txt, kind, c1, c2, shift=-90, glow=None, angle=0, outline=3):
    f = fit_font(txt, 1320, 250, kind)
    m = make_text_mask(txt, f, shift, outline)
    if glow:
        gl = Image.new("RGBA", (S, S), glow + (255,))
        gl.putalpha(Image.fromarray((np.asarray(m) * 0.85).astype(np.uint8)))
        img.alpha_composite(gl.filter(ImageFilter.GaussianBlur(24)))
    sh = Image.new("RGBA", (S, S), (0, 0, 0, 210))
    sh.putalpha(Image.fromarray(np.asarray(m).copy()))
    shl = Image.new("RGBA", (S, S), (0, 0, 0, 0))
    shl.alpha_composite(sh, (0, 7))
    img.alpha_composite(shl.filter(ImageFilter.GaussianBlur(5)))

    yy = np.linspace(0, 1, S)[:, None]
    xx = np.linspace(0, 1, S)[None, :]
    t = np.clip(0.42 * yy + 0.28 * xx, 0, 1)
    g = np.zeros((S, S, 3), np.uint8)
    for i in range(3):
        g[:, :, i] = (c1[i] + (c2[i] - c1[i]) * t).astype(np.uint8)
    lay = Image.fromarray(g).convert("RGBA")
    lay.putalpha(m)
    if angle:
        lay = lay.rotate(angle, resample=Image.BICUBIC, expand=False)
    img.alpha_composite(lay)


def small_line(img, txt, font, color, y, ls=6, shadow=True):
    dr = ImageDraw.Draw(img)
    if shadow:
        draw_center(dr, (S / 2 + 1, y + 2), txt, font, (0, 0, 40, 160), ls)
    draw_center(dr, (S / 2, y), txt, font, color, ls)


DISCS = {
    1: dict(key="disco_1_medianoche", title="MEDIANOCHE", kind=F_BOD,
            c1=(240, 233, 218), c2=(196, 174, 128), glow=(150, 180, 255),
            tint=(16, 26, 56), contrast=1.12, vign=0.72, velo=0.4,
            grain=6, seed=101, artist=(238, 232, 218), sub=(238, 232, 218),
            seal=(205, 184, 132),
            metal=((118, 84, 30), (255, 240, 198)),
            artist_glow=(150, 180, 255)),
    2: dict(key="disco_2_ciudad", title="CIUDAD DE NEON", kind=F_COND,
            c1=(40, 240, 255), c2=(255, 60, 170), glow=(120, 90, 255),
            tint=(55, 12, 96), contrast=1.18, vign=0.66, velo=0.34,
            grain=6, seed=102, artist=(0, 244, 255), sub=(250, 244, 230),
            seal=(255, 120, 210),
            metal=((44, 74, 138), (255, 255, 255)),
            artist_glow=(120, 90, 255)),
    3: dict(key="disco_3_ochentas", title="OCHENTAS", kind=F_COND,
            c1=(255, 244, 200), c2=(255, 130, 80), glow=(255, 214, 90),
            tint=(150, 80, 30), contrast=1.1, vign=0.5, velo=0.28,
            grain=6, seed=103, artist=(40, 30, 90), sub=(50, 34, 90),
            seal=(235, 65, 70),
            metal=((152, 70, 18), (255, 250, 210)),
            artist_glow=(255, 214, 90)),
    4: dict(key="disco_4_llamas", title="LLAMAS", kind=F_BOD,
            c1=(255, 226, 150), c2=(255, 140, 110), glow=(255, 160, 220),
            tint=(74, 12, 110), contrast=1.16, vign=0.6, velo=0.32,
            grain=6, seed=104, artist=(255, 232, 210), sub=(255, 232, 210),
            seal=(255, 210, 110),
            metal=((136, 58, 16), (255, 246, 200)),
            artist_glow=(255, 160, 220)),
    5: dict(key="disco_5_euforia", title="EUFORIA", kind=F_COND,
            c1=(255, 255, 244), c2=(255, 150, 110), glow=(255, 90, 70),
            tint=(205, 92, 34), contrast=1.08, vign=0.46, velo=0.24,
            grain=5, seed=105, artist=(255, 255, 255), sub=(255, 255, 244),
            seal=(255, 84, 84),
            metal=((152, 60, 16), (255, 252, 215)),
            artist_glow=(255, 90, 70)),
    6: dict(key="disco_6_directo", title="DIRECTO", kind=F_BOD,
            c1=(250, 248, 244), c2=(205, 180, 170), glow=None,
            tint=(26, 24, 24), contrast=1.2, vign=0.82, velo=0.5,
            grain=14, seed=106, artist=(244, 242, 238), sub=(255, 214, 64),
            seal=(230, 60, 50),
            metal=((60, 56, 54), (255, 255, 255)),
            artist_glow=(240, 150, 100)),
}


def slug_of(num):
    return {1: "Disco_1_Medianoche", 2: "Disco_2_Ciudad_de_Neon",
            3: "Disco_3_Ochentas", 4: "Disco_4_Llamas",
            5: "Disco_5_Euforia", 6: "Disco_6_Directo"}[num]


def build(num, CONFIG, subtitulo):
    os.makedirs(SRC, exist_ok=True)
    src = pick_and_dl(CONFIG["key"], THEMES[CONFIG["key"]])
    base = load_src(src)
    img = soul(base, CONFIG["tint"], CONFIG["contrast"], CONFIG["vign"],
               CONFIG["velo"], grain_amt=CONFIG["grain"], seed=CONFIG["seed"])

    dr = ImageDraw.Draw(img)
    dr.rectangle([26, 26, S - 26, S - 26], outline=(255, 255, 255, 60), width=1)
    dr.rectangle([34, 34, S - 34, S - 34], outline=CONFIG["seal"] + (140,), width=1)

    f_art = fload(F_COND_R, 40)
    gold_artist(img, "SANDRO SAAVEDRA", f_art, spacing=10,
                metal=CONFIG["metal"], glow=CONFIG["artist_glow"])
    draw_spaced(dr, (68, 148), "CANCIONES DE UNA CIUDAD", fload(F_COND_R, 23),
                CONFIG["seal"], 7, shadow=(0, 0, 0))

    photo_title(img, CONFIG["title"], CONFIG["kind"], CONFIG["c1"], CONFIG["c2"],
                shift=-70, glow=CONFIG["glow"], angle=-2 if num == 6 else 0)

    f_sub = fload(F_COND_R, 38)
    small_line(img, subtitulo.upper(), f_sub, CONFIG["sub"], 1040)

    f_seal = fload(F_NARR, 22)
    small_line(img, "VINILO  33 1/3 RPM  -  ESTEREO", f_seal, CONFIG["seal"], 1396)
    return img


def main():
    import json as _json
    with open(os.path.join(OUT, "box_set.json"), encoding="utf-8") as fh:
        box = _json.load(fh)
    only = sys.argv[1] if len(sys.argv) > 1 else None
    for d in box:
        num = d["numero"]
        if only and int(only) != num:
            continue
        cfg = DISCS[num]
        print("portada", num, d["titulo"], "...")
        img = build(num, cfg, d["subtitulo"])
        path = os.path.join(TAPAS, slug_of(num) + "_front.jpg")
        img.convert("RGB").save(path, quality=93)
        sh = os.path.join(WEB, slug_of(num) + "_front.jpg")
        img.convert("RGB").save(sh, quality=93)
        print("OK", path)


main()