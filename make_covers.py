# -*- coding: utf-8 -*-
import os, sys, json, math, random
import numpy as np
from PIL import Image, ImageDraw, ImageFont, ImageFilter

sys.stdout.reconfigure(encoding="utf-8")

OUT = r"C:\AI\Antigravity\musica"
TAPAS = os.path.join(OUT, "Discos", "Tapas")
os.makedirs(TAPAS, exist_ok=True)
FONTS = r"C:\Windows\Fonts"
F_BOD = os.path.join(FONTS, "BOD_BLAR.TTF")
F_SERIF = os.path.join(FONTS, "BOOKOS.TTF")
F_SERIF_B = os.path.join(FONTS, "BOOKOSB.TTF")
F_COND = os.path.join(FONTS, "AGENCYB.TTF")
F_COND_R = os.path.join(FONTS, "AGENCYR.TTF")
F_NARR = os.path.join(FONTS, "ARIALN.TTF")
F_MONO = os.path.join(FONTS, "consolab.ttf")
S = 1500
ARTISTA = "SANDRO SAAVEDRA"

with open(os.path.join(OUT, "box_set.json"), encoding="utf-8") as fh:
    BOX = json.load(fh)


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


def fmt(seg):
    return "%d:%02d" % (int(seg // 60), int(seg % 60))


# ---------------- ruido fractal (perlin) ----------------
def perlin(seed, octaves=5, base=64):
    rng = np.random.default_rng(seed)
    acc = np.zeros((S, S), float)
    p = 1.0
    gl = np.linspace(0, 1, S)
    for o in range(octaves):
        n = max(2, base // (2 ** o))
        grid = rng.random((n + 2, n + 2))
        q = gl * n
        hi, fi = np.floor(q).astype(int), q - np.floor(q)
        gy = hi[:, None]
        gx = hi[None, :]
        fy = fi[:, None]
        fx = fi[None, :]
        uy = fy * fy * (3 - 2 * fy)
        ux = fx * fx * (3 - 2 * fx)
        yy = gy + 1
        xx = gx + 1
        v00 = grid[gy, gx]
        v10 = grid[gy, xx]
        v01 = grid[yy, gx]
        v11 = grid[yy, xx]
        a = v00 * (1 - ux) + v10 * ux
        b = v01 * (1 - ux) + v11 * ux
        acc += p * (a * (1 - uy) + b * uy)
        p *= 0.5
    acc -= acc.min()
    return acc / (acc.max() + 1e-9)


print("importado", flush=True)


def to_rgb(arr):
    return np.clip(arr, 0, 255).astype(np.uint8)


def grad_img(stops):
    arr = np.zeros((S, S, 3), float)
    ys = [s[0] * (S - 1) for s in stops]
    cols = [s[1] for s in stops]
    for i in range(3):
        arr[:, :, i] = np.interp(np.arange(S), ys, [c[i] for c in cols])[:, None]
    return to_rgb(arr)


def grain_add(arr, seed=1, amt=8):
    r = np.random.default_rng(seed).normal(0, amt, arr.shape[:-1])
    return to_rgb(arr + r[:, :, None])


def bloom(base, layer, rad=46):
    g = layer.filter(ImageFilter.GaussianBlur(rad)).convert("RGB")
    a = np.asarray(base).astype(float)
    b = np.asarray(g).astype(float)
    m = 1 - (1 - a / 255.0) * (1 - b / 255.0)
    return Image.fromarray(to_rgb(m)).convert("RGBA")


def ovl(base, layer):
    base = base.convert("RGBA")
    if layer is not None:
        base.alpha_composite(layer)
    return base


def glayer(center, r, color, amax, steps=50):
    lay = Image.new("RGBA", (S, S), (0, 0, 0, 0))
    d = ImageDraw.Draw(lay)
    cx, cy = center
    for i in range(steps, 0, -1):
        rr = int(r * i / steps)
        a = int(amax * (1 - i / steps) ** 0.6)
        if a > 0:
            d.ellipse([cx - rr, cy - rr, cx + rr, cy + rr], outline=color + (a,), width=4)
    return lay


def bokeh(img, rnd, color, n, y0, y1, x0, x1):
    lay = Image.new("RGBA", (S, S), (0, 0, 0, 0))
    d = ImageDraw.Draw(lay)
    for _ in range(n):
        r = rnd.randint(14, 90)
        x, y = rnd.randint(x0, x1), rnd.randint(y0, y1)
        a = rnd.randint(14, 60)
        d.ellipse([x - r, y - r // 2, x + r, y + r // 2], outline=color + (a,), width=8)
    lay = lay.filter(ImageFilter.GaussianBlur(10))
    return lay


def smooth_dots(rx, ry, rx0, ry0, amp, cy, seed=3, bright=170, dark=40):
    arr = np.full((ry, rx), dark, float)
    rng = np.random.default_rng(seed)
    field = perlin(seed + 9, 4, 64) * amp
    rg = np.arange(rx)
    for yy in range(0, ry, 3):
        for xx in range(0, rx, 3):
            fv = (yy < cy) - field[yy, xx] + amp
            arr[yy, xx] = bright if fv > 0 else dark
    return to_rgb(arr)


def halftone(mat, period=3, bg=40, fg=190, hue=(255, 255, 255)):
    h, w = mat.shape
    d = max(1, min(h, w) // 1)
    down = Image.fromarray(mat).resize((w // 2, h // 2), Image.LANCZOS).resize(
        (w, h), Image.LANCZOS)
    return to_rgb(down)


# ---------------- texto ----------------
def text_sil(txt, font, ow=0):
    m = Image.new("L", (S, S), 0)
    bb = tmp_d().textbbox((0, 0), txt, font=font)
    ox = (S - (bb[2] - bb[0])) // 2
    oy = (S - (bb[3] - bb[1])) // 2 - bb[1]
    d = ImageDraw.Draw(m)
    d.text((ox, oy), txt, font=font, fill=255, stroke_width=ow, stroke_fill=255)
    return m, ox, oy


def shear_mask(m, k):
    sh = int(k * S)
    im = Image.fromarray(np.asarray(m)).transform(
        (S + sh, S), Image.AFFINE, (1, k, -sh / 2, 0, 1, 0))
    return im.resize((S, S), Image.LANCZOS)


def draw_spaced(dr, xy, txt, font, fill, ls=0):
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
    w = sum((td.textbbox((0, 0), c, font=font)[2] - td.textbbox((0, 0), c, font=font)[0] + ls)
            for c in txt) - ls
    return draw_spaced(dr, (xy[0] - w / 2, xy[1]), txt, font, fill, ls)


def fit_font(text, maxw, base, kind=F_BOD):
    sz = base
    td = tmp_d()
    while sz > 40:
        f = fload(kind, sz)
        if txt_w(td, text, f) <= maxw:
            return f
        sz -= 5
    return fload(kind, 40)


def sculpt_title(img, txt, kind, c1, c2, ocolor, glow_col, emboss=2, ow=2):
    size = fit_font(txt, 1330, 250, kind)
    m, ox, oy = text_sil(txt, size, ow)
    if glow_col:
        gl = Image.new("RGBA", (S, S), glow_col + (255,))
        gm = m.point(lambda v: min(255, v + 60)) if False else m
        gl.putalpha(Image.fromarray(np.asarray(m).copy()))
        bl = gl.filter(ImageFilter.GaussianBlur(14))
        img.alpha_composite(bl)
    emb = Image.new("RGBA", (S, S), (0, 0, 0, 0))
    ed = ImageDraw.Draw(emb)
    if emboss:
        for (dx, dy, col) in ((0, emboss, (0, 0, 0)), (2, 1, (130, 120, 90)),
                              (0, 0, (255, 255, 255))):
            bb = tmp_d().textbbox((0, 0), txt, font=size)
            ed.text((ox + dx, oy + dy), txt, font=size, fill=col + (255,))
    msk = Image.fromarray(np.asarray(m))
    for dx, dy, coli in ((0, emboss, (0, 0, 0)),):
        pass
    base_l = m.point(lambda v: v) if len(m.getbands()) == 1 else m
    alpha = np.asarray(m) / 255.0
    g = np.zeros((S, S, 4), float)
    # gradiente metalico vertical + diagonal
    yy = np.linspace(0, 1, S)[:, None]
    xx = np.linspace(0, 1, S)[None, :]
    t = np.clip((0.45 * yy + 0.18 * xx) * 1.6, 0, 1)
    for i in range(3):
        g[:, :, i] = c1[i] + (c2[i] - c1[i]) * t
    g[:, :, 3] = alpha * 255
    img.alpha_composite(Image.fromarray(g.astype(np.uint8)))
    sheen = np.zeros((S, S), float)
    yyv = np.linspace(0, 1, S)
    amp = alpha * np.clip(2.4 * (0.52 - yyv[:, None]), 0, 0.5)
    sheen = np.clip(amp, 0, 180)
    lay = Image.new("RGBA", (S, S), (255, 255, 255, 0))
    lay.putalpha(Image.fromarray(sheen.astype(np.uint8)))
    img.alpha_composite(lay)
    tmp = Image.new("L", (S, S), 0)
    ImageDraw.Draw(tmp).text((ox, oy), txt, font=size)
    mask2 = np.asarray(tmp)
    ring = np.asarray(m) - mask2
    rr = ring * 0
    rr = np.clip(np.asarray(m) - mask2, 0, 255)
    if rr.max() > 0 and ocolor:
        oc = Image.new("RGBA", (S, S), ocolor + (255,))
        oc.putalpha(Image.fromarray(rr))
        img.alpha_composite(oc)


# ---------------- FRONT por disco ----------------
def base_art(pal, seed):
    arr = grad_img(pal["stops"]).astype(float)
    n = perlin(seed + 301, 5, 64)
    arr = arr * (0.72 + 0.45 * n[:, :, None])
    arr = to_rgb(arr)
    return Image.fromarray(arr).convert("RGBA")


PAL = {
    1: dict(stops=[(0, (4, 7, 20)), (0.45, (26, 38, 74)), (1.0, (70, 96, 150))],
            gold=(202, 178, 120), cream=(238, 232, 220), moon=(236, 244, 255),
            glow=(190, 220, 255)),
    2: dict(stops=[(0, (8, 2, 30)), (0.5, (30, 10, 64)), (1.0, (110, 38, 118))],
            cyan=(0, 244, 255), magenta=(255, 64, 170), sun=(255, 160, 70),
            cream=(250, 242, 230), glow=(140, 90, 255)),
    3: dict(stops=[(0, (24, 18, 40)), (0.5, (60, 30, 80)), (1.0, (140, 70, 120))],
            cream=(250, 240, 220), amber=(255, 190, 60), blue=(80, 170, 255),
            pink=(255, 110, 170), teal=(50, 190, 180), red=(235, 65, 70),
            dark=(24, 18, 40), glow=(255, 214, 90)),
    4: dict(stops=[(0, (16, 8, 38)), (0.5, (74, 22, 112)), (1.0, (180, 68, 118))],
            storm=(220, 120, 240), head=(255, 235, 214), gold=(255, 210, 110),
            red=(255, 80, 60), glow=(255, 150, 220)),
    5: dict(stops=[(0, (222, 236, 252)), (0.6, (170, 204, 240)), (1.0, (104, 156, 224))],
            ink=(20, 30, 80), red=(232, 60, 70), sun=(255, 236, 160),
            cream=(250, 248, 240), glow=(255, 214, 90)),
    6: dict(stops=[(0, (10, 10, 10)), (0.5, (40, 34, 32)), (1.0, (92, 76, 66))],
            wh=(244, 242, 238), red=(230, 60, 50), gold=(205, 170, 110),
            acid=(255, 214, 64), glow=(255, 214, 64)),
}


# ---- 1 MEDIANOCHE : noche pictorica al modo Disintegration ----
def front_medianoche(p):
    arr = grad_img(p["stops"]).astype(float)
    n = perlin(101, 5, 64)
    arr *= (0.55 + 0.5 * n[:, :, None])
    img = Image.fromarray(to_rgb(arr)).convert("RGBA")

    nsm = perlin(102, 5, 96)
    swirl = Image.fromarray((nsm * 255).astype(np.uint8)).convert("L")
    swirl = swirl.filter(ImageFilter.GaussianBlur(4))
    slay = Image.new("RGBA", (S, S), (86, 108, 160, 0))
    slay.putalpha(swirl.point(lambda v: int(v * 0.4)))
    img = ovl(img, slay)

    img = ovl(img, glayer((S * 0.5, 640), 340, p["glow"], 60))
    moon = Image.new("RGBA", (S, S), (0, 0, 0, 0))
    md = ImageDraw.Draw(moon)
    md.ellipse([S * 0.5 - 250, 390, S * 0.5 + 250, 890], fill=p["moon"] + (238,))
    mph = (perlin(103, 6, 40) > 0.7).astype(np.uint8) * 255
    mph = Image.fromarray(mph).convert("L").filter(ImageFilter.GaussianBlur(2))
    mar = Image.new("RGBA", (S, S), (128, 138, 156, 150))
    mar.putalpha(mph)
    moon.alpha_composite(mar)
    img = ovl(img, moon.filter(ImageFilter.GaussianBlur(2)))

    for i, (y0, s, a) in enumerate(((380, 40, 6), (560, 90, 5), (720, 60, 3), (810, 30, 4))):
        cl = Image.new("RGBA", (S, S), (0, 0, 0, 0))
        cd2 = ImageDraw.Draw(cl)
        xx0 = 160 + i * 110
        for j in range(120):
            rx = xx0 + j * 24 + int(s * math.sin(j / 4 + i))
            ry = y0 + int(18 * math.sin(j / 3 + i * 2))
            r = 46 + int(24 * math.sin(j / 5 + i))
            cd2.ellipse([rx - r, ry - r // 2, rx + r, ry + r // 2],
                        fill=(230, 234, 244, a))
        img = ovl(img, cl.filter(ImageFilter.GaussianBlur(12)))

    gd = ImageDraw.Draw(img)
    gd.polygon([(0, 1202), (S, 1202), (S, 1162), (0, 1132)], fill=(14, 20, 44, 255))
    gd.rectangle([0, 1236, S, S], fill=(5, 8, 20, 255))
    fx = S * 0.5
    gd.ellipse([fx - 15, 1106 - 30, fx + 15, 1106], fill=(6, 10, 22))
    gd.polygon([(fx - 10, 1132), (fx + 10, 1132), (fx + 8, 1236), (fx - 8, 1236)],
               fill=(6, 10, 22))
    gd.rectangle([44, 44, S - 44, S - 44], outline=p["gold"], width=1)
    gd.rectangle([52, 52, S - 52, S - 52], outline=p["cream"] + (120,), width=1)

    draw_center(gd, (S / 2, 108), ARTISTA, fload(F_SERIF, 32), p["cream"], 10)
    sculpt_title(img, "MEDIANOCHE", F_BOD, (196, 172, 120), (244, 228, 196),
                 (4, 6, 16), p["glow"], 2, 2)
    f_sub = fload(F_SERIF, 38)
    draw_center(gd, (S / 2, 976), p["sub"].upper(), f_sub, p["cream"], 5)
    draw_center(gd, (S / 2, S - 92), "CANCIONES DE UNA CIUDAD", fload(F_NARR, 24),
                p["gold"], 6)
    draw_center(gd, (S / 2, S - 52), "VINILO  -  33 1/3 RPM  -  ESTEREO",
                fload(F_NARR, 20), p["cream"], 4)
    return img


# ---- 2 CIUDAD DE NEON : sol de scanlines + skyline + rejilla (Kraftwerk) ----
def front_ciudad(p):
    arr = grad_img(p["stops"]).astype(float)
    n = perlin(202, 5, 64)
    arr *= (0.58 + 0.55 * n[:, :, None])
    img = Image.fromarray(to_rgb(arr)).convert("RGBA")

    lay = Image.new("RGBA", (S, S), (0, 0, 0, 0))
    d = ImageDraw.Draw(lay)
    cx, cy = S * 0.5, 300
    for rr in (320, 355, 395, 445):
        d.ellipse([cx - rr, cy - rr, cx + rr, cy + rr], outline=p["sun"] + (70,), width=4)
    d.ellipse([cx - 220, cy - 220, cx + 220, cy + 220], fill=p["sun"] + (210,))
    for i in range(0, 446, 14):
        d.rectangle([cx - 220, cy - 220 + i, cx + 220, cy - 220 + i + 9], fill=(18, 6, 48))
    img = ovl(img, lay.filter(ImageFilter.GaussianBlur(2)))

    h = 640
    sky = Image.new("RGBA", (S, S), (0, 0, 0, 0))
    sd = ImageDraw.Draw(sky)
    rnd = random.Random(23)
    x = -20
    while x < S + 40:
        bw = rnd.randint(48, 160)
        bh = rnd.randint(70, 330)
        sd.rectangle([x, h - bh, x + bw, h], fill=(6, 2, 20, 255))
        for _ in range(rnd.randint(1, 3)):
            wx = x + rnd.randint(10, max(12, bw - 12))
            wy = h - rnd.randint(10, max(12, bh - 20))
            sd.rectangle([wx - 4, wy, wx + 4, wy + 11], fill=p["cyan"] + (230,))
        x += bw + rnd.randint(4, 30)
    img = ovl(img, sky)

    gr = Image.new("RGBA", (S, S), (0, 0, 0, 0))
    gd = ImageDraw.Draw(gr)
    for i in range(-9, 10):
        xh = S / 2 + i * 52
        gd.line([(xh, h), (S / 2 + (xh - S / 2) * 2.6, S)], fill=p["magenta"] + (215,), width=2)
    for k in range(1, 17):
        t = k / 17
        y = h + (S - h) * t ** 1.45
        gd.line([(0, y), (S, y)], fill=p["magenta"] + (200,), width=2)
    img = ovl(img, gr)

    img = grain_add(np.asarray(img.convert("RGB")), 14, 7)
    img = Image.fromarray(img).convert("RGBA")
    dr = ImageDraw.Draw(img)
    draw_spaced(dr, (66, 62), ARTISTA, fload(F_COND_R, 40), p["cyan"], 6)
    f_title = fit_font("CIUDAD DE NEON", 1280, 200, F_COND)
    draw_spaced(dr, (84, S - 312), "CIUDAD DE NEON", f_title, p["magenta"], 4)
    draw_spaced(dr, (76, S - 320), "CIUDAD DE NEON", f_title, p["cyan"], 4)
    f_sub = fload(F_COND_R, 40)
    draw_spaced(dr, (84, S - 210), p["sub"].upper(), f_sub, p["sun"], 4)
    draw_center(dr, (S / 2, S - 92), "CANCIONES DE UNA CIUDAD", fload(F_NARR, 26),
                p["cyan"], 5)
    return img


# ---- 3 OCHENTAS : collage airbrush de poster ochentero (De La Soul) ----
def front_ochentas(p):
    img = Image.fromarray(grad_img([(0, (248, 240, 226)), (1, (226, 214, 194))])).convert("RGBA")
    rnd = random.Random(31)
    for cx, cy, r, col in ((S * 0.22, S * 0.30, 250, p["blue"]),
                           (S * 0.80, S * 0.66, 300, p["pink"]),
                           (S * 0.52, S * 0.20, 210, p["amber"]),
                           (S * 0.34, S * 0.76, 235, p["teal"]),
                           (S * 0.72, S * 0.28, 170, p["red"])):
        img = ovl(img, glayer((int(cx), int(cy)), int(r), col, 34))

    pan = Image.new("RGBA", (S, S), (0, 0, 0, 0))
    pd = ImageDraw.Draw(pan)
    pd.rectangle([S * 0.07, S * 0.32, S * 0.40, S * 0.58], outline=p["dark"] + (230,), width=14)
    pd.rectangle([S * 0.62, S * 0.40, S * 0.91, S * 0.63], outline=p["red"] + (230,), width=12)
    pd.line([(S * 0.07, S * 0.45), (S * 0.40, S * 0.45)], fill=p["dark"] + (200,), width=4)
    pd.line([(S * 0.62, S * 0.52), (S * 0.91, S * 0.52)], fill=p["dark"] + (200,), width=4)
    img = ovl(img, pan)

    ch = Image.new("RGBA", (S, S), (0, 0, 0, 0))
    cd = ImageDraw.Draw(ch)
    for i in range(0, 260, 90):
        for j, xx in enumerate(range(-90, S, 90)):
            if (i // 90 + j) % 2 == 0:
                cd.rectangle([xx, 1240 + i, xx + 90, 1330 + i], fill=p["teal"] + (130,))
    img = ovl(img, ch)

    st = Image.new("RGBA", (S, S), (0, 0, 0, 0))
    sd = ImageDraw.Draw(st)
    for _ in range(34):
        x = rnd.randint(20, S - 20)
        y = rnd.randint(20, S - 20)
        r = rnd.randint(3, 7)
        col = rnd.choice([p["dark"], p["red"], p["blue"], p["teal"]])
        sd.polygon([(x, y - r), (x + r // 2, y - r // 2), (x + r, y),
                    (x + r // 2, y + r // 2), (x, y + r), (x - r // 2, y + r // 2),
                    (x - r, y), (x - r // 2, y - r // 2)], fill=col + (190,))
    img = ovl(img, st)

    img = grain_add(np.asarray(img.convert("RGB")), 16, 10)
    img = Image.fromarray(img).convert("RGBA")
    dr = ImageDraw.Draw(img)
    draw_spaced(dr, (66, 62), ARTISTA, fload(F_COND_R, 40), p["dark"], 6)
    sculpt_title(img, "OCHENTAS", F_COND, (160, 190, 255), (255, 96, 170),
                 (30, 20, 50), p["glow"], 2, 3)
    f_sub = fload(F_COND_R, 40)
    draw_center(dr, (S / 2, 976), "★  %s  ★" % p["sub"].upper(), f_sub, p["dark"], 4)
    draw_center(dr, (S / 2, S - 88), "CANCIONES DE UNA CIUDAD", fload(F_NARR, 26),
                p["red"], 5)
    return img


# ---- 4 LLAMAS : storm purple rain a lo Prince, moto contraluz ----
def front_llamas(p):
    arr = grad_img(p["stops"]).astype(float)
    n = perlin(404, 5, 64)
    arr *= (0.6 + 0.5 * n[:, :, None])
    img = Image.fromarray(to_rgb(arr)).convert("RGBA")
    img = ovl(img, glayer((S * 0.5, 560), 430, p["glow"], 46))

    rain = Image.new("RGBA", (S, S), (0, 0, 0, 0))
    rd = ImageDraw.Draw(rain)
    rnd = random.Random(41)
    for _ in range(95):
        x0 = rnd.randint(0, S)
        y0 = rnd.randint(-50, S - 200)
        ln = rnd.randint(70, 280)
        wd = rnd.choice([2, 3, 5])
        col = rnd.choice([p["head"], p["gold"], p["storm"]])
        a = rnd.randint(90, 230)
        rd.line([(x0, y0), (x0 + int(ln * 0.26), y0 + ln)], fill=col + (a,), width=wd)
    img = ovl(img, rain.filter(ImageFilter.GaussianBlur(1)))

    sil = Image.new("RGBA", (S, S), (0, 0, 0, 0))
    sd = ImageDraw.Draw(sil)
    sd.ellipse([S * 0.5 - 190, 1090, S * 0.5 - 90, 1200], fill=(10, 6, 20, 255))
    sd.ellipse([S * 0.5 + 70, 1090, S * 0.5 + 170, 1200], fill=(10, 6, 20, 255))
    sd.rectangle([S * 0.5 - 174, 1130, S * 0.5 + 154, 1168], fill=(12, 8, 22, 255))
    sd.line([(S * 0.5 - 40, 1130), (S * 0.5 - 120, 1040)], fill=(12, 8, 22, 255), width=14)
    sd.line([(S * 0.5 + 40, 1130), (S * 0.5 + 120, 1040)], fill=(12, 8, 22, 255), width=14)
    sd.ellipse([S * 0.5 + 52, 1000, S * 0.5 + 130, 1085], fill=(10, 6, 18, 255))
    sd.polygon([(S * 0.5 + 60, 1085), (S * 0.5 + 30, 1160), (S * 0.5 + 130, 1160),
                (S * 0.5 + 118, 1085)], fill=(10, 6, 18, 255))
    img = ovl(img, sil.filter(ImageFilter.GaussianBlur(2)))

    em = Image.new("RGBA", (S, S), (0, 0, 0, 0))
    ed = ImageDraw.Draw(em)
    r2 = random.Random(42)
    for _ in range(80):
        x = r2.randint(0, S)
        y = r2.randint(560, S)
        r = r2.randint(2, 6)
        ed.ellipse([x - r, y - r, x + r, y + r],
                   fill=r2.choice([(255, 200, 90), (255, 130, 60), (255, 236, 170)])
                   + (r2.randint(120, 230),))
    img = ovl(img, em)

    img = grain_add(np.asarray(img.convert("RGB")), 18, 9)
    img = Image.fromarray(img).convert("RGBA")
    dr = ImageDraw.Draw(img)
    dr.rectangle([44, 44, S - 44, S - 44], outline=p["head"], width=1)
    draw_spaced(dr, (66, 62), ARTISTA, fload(F_COND_R, 40), p["head"], 6)
    sculpt_title(img, "LLAMAS", F_BOD, (255, 214, 120), (255, 150, 120),
                 (40, 10, 40), p["glow"], 2, 2)
    f_sub = fload(F_COND_R, 40)
    draw_center(dr, (S / 2, 968), p["sub"].upper(), f_sub, p["head"], 5)
    draw_center(dr, (S / 2, S - 88), "CANCIONES DE UNA CIUDAD", fload(F_NARR, 26),
                p["gold"], 5)
    return img


# ---- 5 EUFORIA : sol ingenuo dibujado a mano (Daydream Nation) ----
def front_euforia(p):
    img = Image.fromarray(grad_img(p["stops"])).convert("RGBA")

    sun = Image.new("RGBA", (S, S), (0, 0, 0, 0))
    sd = ImageDraw.Draw(sun)
    cx, cy, rr = S * 0.5, S * 0.46, 300
    sd.ellipse([cx - rr, cy - rr, cx + rr, cy + rr], fill=p["sun"] + (255,))
    sd.ellipse([cx - rr, cy - rr, cx + rr, cy + rr], outline=p["ink"] + (255,), width=14)
    sd.ellipse([cx - 360, cy - 360, cx + 360, cy + 360], outline=p["red"] + (230,), width=10)
    rnd = random.Random(51)
    for _ in range(70):
        ang = rnd.uniform(0, math.pi * 2)
        r0 = rnd.uniform(rr + 26, 560)
        r1 = rnd.uniform(rr + 40, 730)
        x0 = cx + r0 * math.cos(ang)
        y0 = cy + r0 * math.sin(ang)
        x1 = cx + r1 * math.cos(ang) * 0.9
        y1 = cy + r1 * math.sin(ang) * 0.9
        sd.line([(x0, y0), (x1, y1)], fill=p["ink"] + (rnd.randint(120, 220),),
                width=rnd.choice([2, 3, 6]))
    img = ovl(img, sun)

    sc = Image.new("RGBA", (S, S), (0, 0, 0, 0))
    cd = ImageDraw.Draw(sc)
    r2 = random.Random(52)
    for _ in range(130):
        x0 = r2.randint(60, S - 60)
        y0 = r2.randint(60, S - 60)
        x1 = x0 + r2.randint(-190, 190)
        y1 = y0 + r2.randint(-190, 190)
        cd.line([(x0, y0), (x1, y1)], fill=p["ink"] + (r2.randint(50, 130),),
                width=r2.choice([2, 3, 4]))
    img = ovl(img, sc)

    img = grain_add(np.asarray(img.convert("RGB")), 21, 9)
    img = Image.fromarray(img).convert("RGBA")
    dr = ImageDraw.Draw(img)
    draw_spaced(dr, (66, 62), ARTISTA, fload(F_COND_R, 40), p["ink"], 6)
    sculpt_title(img, "EUFORIA", F_COND, (255, 240, 190), (255, 120, 110),
                 (20, 30, 80), p["red"], 2, 2)
    f_sub = fload(F_COND_R, 40)
    draw_center(dr, (S / 2, 986), p["sub"].upper(), f_sub, p["ink"], 3)
    dr.line([(S / 2 - 190, 1036), (S / 2 + 190, 1036)], fill=p["red"], width=4)
    draw_center(dr, (S / 2, S - 84), "CANCIONES DE UNA CIUDAD", fload(F_NARR, 26),
                p["ink"], 5)
    return img


# ---- 6 DIRECTO : bootleg rock en vivo (Appetite for Destruction) ----
def front_directo(p):
    arr = grad_img(p["stops"]).astype(float)
    n = perlin(606, 4, 96)
    arr *= (0.62 + 0.5 * n[:, :, None])
    img = Image.fromarray(to_rgb(arr)).convert("RGBA")

    cone = Image.new("RGBA", (S, S), (0, 0, 0, 0))
    cd = ImageDraw.Draw(cone)
    cd.polygon([(S * 0.5, -200), (S * 0.16, S), (S * 0.84, S)], fill=p["wh"] + (46,))
    cd.ellipse([S * 0.44, 30, S * 0.56, 220], fill=p["wh"] + (210,))
    img = ovl(img, cone.filter(ImageFilter.GaussianBlur(120)))
    img = ovl(img, glayer((S * 0.5, 60), 300, p["wh"], 60))

    rnd = random.Random(61)
    rom = Image.new("RGBA", (S, S), (0, 0, 0, 0))
    rd = ImageDraw.Draw(rom)
    yb = S - 260
    for i in range(52):
        x = rnd.randint(-40, S + 40)
        y = yb + rnd.randint(0, 160)
        r = rnd.randint(22, 34)
        rd.ellipse([x - r, y - r, x + r, y + r], fill=(8, 7, 6, 240))
        if rnd.random() < 0.32:
            rd.line([(x, y - r),
                     (x + rnd.randint(-40, 40), y - r - rnd.randint(30, 90))],
                    fill=(10, 9, 8, 240), width=rnd.randint(4, 8))
    rom = rom.filter(ImageFilter.GaussianBlur(2))
    img = ovl(img, rom)

    mic = Image.new("RGBA", (S, S), (0, 0, 0, 0))
    md = ImageDraw.Draw(mic)
    for k, xx in enumerate((S * 0.5 - 430, S * 0.5 + 40)):
        md.line([(xx, 500), (xx + 90, 250)], fill=(6, 5, 5, 240), width=22)
        md.ellipse([xx + 64, 214, xx + 120, 270], fill=(6, 5, 5, 240))
    img = ovl(img, mic)

    img = grain_add(np.asarray(img.convert("RGB")), 24, 42)
    img = Image.fromarray(img).convert("RGBA")
    dr = ImageDraw.Draw(img)

    stamp = Image.new("RGBA", (S, S), (0, 0, 0, 0))
    sd = ImageDraw.Draw(stamp)
    sd.rectangle([150, 150, 470, 246], outline=p["red"] + (255,), width=9)
    sd.rectangle([164, 164, 456, 232], outline=p["red"] + (255,), width=2)
    sd.text((192, 164), "EN VIVO", font=fload(F_COND, 56), fill=p["red"])
    img.alpha_composite(stamp.rotate(6, resample=Image.BICUBIC))

    dr.ellipse([S - 216, 80, S - 158, 138], fill=p["red"])
    draw_spaced(dr, (S - 162, 94), "REC", fload(F_COND, 36), p["red"], 6)
    draw_spaced(dr, (66, 62), ARTISTA, fload(F_COND_R, 40), p["wh"], 8)

    f_t = fit_font("DIRECTO", 1180, 250, F_BOD)
    m, ox, oy = text_sil("DIRECTO", f_t, 3)
    for dx, dy, col in ((-6, 5, (0, 0, 0)), (0, 0, p["wh"])):
        lay2 = Image.new("RGBA", (S, S), (0, 0, 0, 0))
        ImageDraw.Draw(lay2).text((ox + dx, oy + dy), "DIRECTO", font=f_t,
                                  fill=col + (255,))
        if col == (0, 0, 0):
            lay2 = lay2.filter(ImageFilter.GaussianBlur(1))
        img.alpha_composite(lay2)

    f_sub = fload(F_COND_R, 38)
    draw_center(dr, (S / 2, 994), p["sub"].upper(), f_sub, p["acid"], 4)
    dr.line([(S * 0.5 - 160, 1046), (S * 0.5 + 160, 1046)], fill=p["red"], width=5)
    draw_center(dr, (S / 2, S - 84), "EL DESVAN DEL VINILO  -  (C) 2026",
                fload(F_NARR, 24), p["red"], 3)
    return img


FRONTS = {1: front_medianoche, 2: front_ciudad, 3: front_ochentas, 4: front_llamas,
          5: front_euforia, 6: front_directo}


def np_random_halftone(seed):
    return None


# ---------------- DORSO ----------------
BACK_TINT = {1: (10, 12, 26), 2: (12, 8, 30), 3: (18, 12, 30), 4: (22, 8, 10), 5: (16, 18, 22),
             6: (14, 10, 8)}


def draw_back(d, pal):
    tint = BACK_TINT[d["numero"]]
    arr = grad_img([(0, tint), (1, (58, 52, 74))]).astype(float)
    n = perlin(600 + d["numero"], 4, 96)
    arr *= (0.82 + 0.3 * n[:, :, None])
    img = Image.fromarray(to_rgb(arr)).convert("RGBA")
    img = grain_add(np.asarray(img.convert("RGB")), 30 + d["numero"], 5)
    img = Image.fromarray(img).convert("RGBA")
    dr = ImageDraw.Draw(img)
    gold = (214, 176, 120)
    cream = (244, 236, 222)
    dr.rectangle([34, 34, S - 34, S - 34], outline=gold, width=1)
    dr.rectangle([42, 42, S - 42, S - 42], outline=(244, 236, 222, 90), width=1)
    draw_center(dr, (S / 2, 108), "CANCIONES DE UNA CIUDAD", fload(F_SERIF, 46), gold, 6)
    leyenda = "GRABADO EN VIVO - UNA SOLA TOMA" if d["numero"] == 6 else "UNA COLECCION EN VINILO"
    draw_center(dr, (S / 2, 188), leyenda, fload(F_NARR, 26), (244, 236, 222), 4)
    draw_center(dr, (S / 2, 262), "TRACKLIST", fload(F_NARR, 30), (244, 236, 222), 10)
    dr.line([(S / 2 - 110, 316), (S / 2 + 110, 316)], fill=gold, width=1)

    tr = d["tracklist"]
    half = math.ceil(len(tr) / 2)
    cols = [tr[:half], tr[half:]]
    f_serif = fload(F_SERIF, 30)
    f_dur = fload(F_NARR, 26)
    for ci, col in enumerate(cols):
        xx = 118 if ci == 0 else 810
        draw_spaced(dr, (xx, 378), "LADO %s" % ("A" if ci == 0 else "B"),
                    fload(F_COND_R, 34), gold, 4)
        for row in col:
            yy = 442 + (row["n"] - 1 - (0 if ci == 0 else half)) * 50
            dr.text((xx, yy), str(row["n"]).zfill(2), font=f_serif, fill=gold)
            dr.text((xx + 60, yy), row["titulo"], font=f_serif, fill=cream)
            dw = txt_w(dr, fmt(row["duracion"]), f_dur)
            dr.text((xx + 500 - dw, yy), fmt(row["duracion"]), font=f_dur, fill=gold)

    rowsmax = max(len(cols[0]), len(cols[1]))
    yf = 442 + rowsmax * 50 + 56
    bx, by, bw, bh = 118, yf, 230, 44
    rnd = random.Random(4400 + d["numero"])
    x = bx
    while x < bx + bw:
        w = rnd.randint(2, 5)
        if x + w <= bx + bw:
            dr.rectangle([x, by, x + w, by + bh], fill=cream)
        x += w + rnd.randint(3, 6)
    draw_spaced(dr, (118, by + bh + 8), "ESTEREO", fload(F_MONO, 20), gold, 2)

    f_cred = fload(F_NARR, 24)
    xr = S - 118
    lines = ["SANDRO SAAVEDRA",
             "MUSICA, LETRA Y VOCES",
             "ARREGLOS: ESTUDIO CENTRAL",
             "PRODUCCION: EL DESVAN DEL VINILO",
             "(C) (P) 2026  -  33 1/3 RPM  -  ESTEREO"]
    yy = yf - 6
    f_h = fload(F_SERIF_B, 34)
    w = txt_w(dr, lines[0], f_h)
    dr.text((xr - w, yy), lines[0], font=f_h, fill=gold)
    yy += 44
    for ln in lines[1:]:
        w = txt_w(dr, ln, f_cred)
        dr.text((xr - w, yy), ln, font=f_cred, fill=(244, 236, 222))
        yy += 28
    dr.line([(xr - 420, yf + 6), (xr, yf + 6)], fill=gold, width=3)
    return img


def main():
    for d in BOX:
        p = PAL[d["numero"]]
        p["sub"] = d["subtitulo"]
        print(d["titulo"], "...", flush=True)
        front = FRONTS[d["numero"]](p)
        back = draw_back(d, p)
        base = os.path.join(TAPAS, d["slug"])
        front.convert("RGB").save(base + "_front.jpg", quality=93)
        back.convert("RGB").save(base + "_back.jpg", quality=93)
        print("OK", base + "_front.jpg")


main()