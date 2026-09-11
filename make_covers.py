# -*- coding: utf-8 -*-
import os, sys, json, math, random
import numpy as np
from PIL import Image, ImageDraw, ImageFont

sys.stdout.reconfigure(encoding="utf-8")

OUT = r"C:\AI\Antigravity\musica"
TAPAS = os.path.join(OUT, "Discos", "Tapas")
os.makedirs(TAPAS, exist_ok=True)

FONTS = r"C:\Windows\Fonts"
F_COND = os.path.join(FONTS, "AGENCYB.TTF")
F_COND_R = os.path.join(FONTS, "AGENCYR.TTF")
F_SERIF = os.path.join(FONTS, "BOOKOS.TTF")
F_SERIF_B = os.path.join(FONTS, "BOOKOSB.TTF")
F_BOD = os.path.join(FONTS, "BOD_BLAR.TTF")
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


def txt_w(dr, txt, font):
    bb = dr.textbbox((0, 0), txt, font=font)
    return bb[2] - bb[0]


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


def fit_font(text, maxw, base, kind=F_COND):
    sz = base
    td = tmp_d()
    while sz > 60:
        f = fload(kind, sz)
        if txt_w(td, text, f) <= maxw:
            return f
        sz -= 6
    return fload(kind, 60)


def fmt(seg):
    return "%d:%02d" % (int(seg // 60), int(seg % 60))


def v_gradient(stops):
    img = np.zeros((S, S, 3), float)
    ys = [st[0] * (S - 1) for st in stops]
    cols = [st[1] for st in stops]
    for i in range(3):
        img[:, :, i] = np.interp(np.arange(S), ys, [c[i] for c in cols])[:, None]
    return np.clip(img, 0, 255).astype(np.uint8)


def grain(img, seed, amt=7):
    r = np.random.default_rng(seed).normal(0, amt, img.shape[:2])[:, :, None]
    return np.clip(img.astype(float) + r, 0, 255).astype(np.uint8)


def ovl(base, layer):
    if layer is None:
        return base
    base = base.convert("RGBA")
    base.alpha_composite(layer)
    return base


def glow(center, r, color, amax, steps=54):
    layer = Image.new("RGBA", (S, S), (0, 0, 0, 0))
    d = ImageDraw.Draw(layer)
    cx, cy = center
    for i in range(steps, 0, -1):
        rr = int(r * i / steps)
        a = int(amax * (1 - i / steps) ** 0.5)
        if a <= 0:
            continue
        d.ellipse([cx - rr, cy - rr, cx + rr, cy + rr], outline=color + (a,), width=3)
    return layer


def text_mask(txt, font, ow=0):
    m = Image.new("L", (S, S), 0)
    mc = tmp_d()
    bb = mc.textbbox((0, 0), txt, font=font)
    ox = (S - (bb[2] - bb[0])) // 2
    oy = (S - (bb[3] - bb[1])) // 2 - bb[1]
    d = ImageDraw.Draw(m)
    d.text((ox, oy), txt, font=font, fill=255, stroke_width=ow, stroke_fill=255)
    return m, ox, oy


def gtext(img, center, txt, font, c1, c2, outline=None, ow=0, shadow=None, alpha=255):
    m, ox, oy = text_mask(txt, font, ow)
    g = np.zeros((S, S, 3), float)
    for i in range(3):
        g[:, :, i] = np.linspace(c1[i], c2[i], S)[:, None]
    grad = Image.fromarray(g.astype(np.uint8)).convert("RGBA")
    mm = m.point(lambda v: int(v * alpha / 255)) if alpha < 255 else m
    grad.putalpha(mm)
    if shadow:
        sh = ImageDraw.Draw(img)
        sh.text((ox + shadow[0], oy + shadow[1]), txt, font=font, fill=shadow[1],
                stroke_width=ow, stroke_fill=shadow[1])
    if outline:
        ring = m.copy()
        bm = Image.new("L", (S, S), 0)
        ImageDraw.Draw(bm).text((ox, oy), txt, font=font, fill=255)
        ring = ImageChops.subtract(ring, bm)
        ocol = Image.new("RGBA", (S, S), outline + (255,))
        ocol.putalpha(ring)
        img.alpha_composite(ocol)
    img.alpha_composite(grad)


try:
    from PIL import ImageChops
except Exception:
    ImageChops = None


# ---------------------------------------------------------------- FRONT 1 ---- MEDIANOCHE
def front_medianoche(d):
    img = Image.fromarray(grain(v_gradient([
        (0.0, (12, 14, 30)), (0.42, (74, 52, 92)), (0.72, (150, 96, 118)), (1.0, (214, 124, 128))]),
        31, 6)).convert("RGBA")
    img = ovl(img, glow((S * 0.5, 470), 300, (255, 238, 216), 52))
    dg = ImageDraw.Draw(img)
    dg.ellipse([S * 0.5 - 235, 235, S * 0.5 + 235, 705], outline=(255, 238, 216) + (36,), width=2)
    dg.ellipse([S * 0.5 - 250, 220, S * 0.5 + 250, 690], outline=(210, 168, 110) + (22,), width=1)
    rnd = random.Random(7)
    for _ in range(70):
        x, y = rnd.randint(40, S - 40), rnd.randint(60, 330)
        a = rnd.randint(20, 90)
        r = rnd.choice([2, 2, 3, 4])
        dg.ellipse([x, y, x + r, y + r], outline=(255, 250, 240) + (a,), width=1)
    dg.rectangle([46, 46, S - 46, S - 46], outline=(214, 178, 120), width=1)
    dg.rectangle([54, 54, S - 54, S - 54], outline=(214, 178, 120) + (0,), width=1)
    gold = (222, 184, 122)
    cream = (248, 240, 226)
    f_art = fload(F_SERIF, 36)
    draw_center(dg, (S / 2, 128), ARTISTA, f_art, cream + (205,), 7)
    f_t = fit_font("MEDIANOCHE", 1250, 238, F_BOD)
    gtext(img, (S / 2, 810), "MEDIANOCHE", f_t, (150, 116, 72), gold,
          outline=(34, 28, 56), ow=2, shadow=(3, 4, (0, 0, 0)))
    f_sub = fload(F_SERIF, 40)
    draw_center(dg, (S / 2, 830 + 96), d["subtitulo"].upper(), f_sub, cream + (235,), 5)
    dg.line([(S / 2 - 95, 810 + 74), (S / 2 + 95, 810 + 74)], fill=gold, width=1)
    f_sm = fload(F_NARR, 27)
    draw_center(dg, (S / 2, S - 110), "CANCIONES DE UNA CIUDAD", f_sm, gold + (215,), 6)
    draw_center(dg, (S / 2, S - 66), "COLECCION EN VINILO  -  33 1/3 RPM  -  ESTEREO", f_sm,
                cream + (155,), 3)
    return img


# ---------------------------------------------------------------- FRONT 2 ---- CIUDAD DE NEON (synthwave)
def front_ciudad(d):
    img = Image.fromarray(grain(v_gradient([(0.0, (10, 4, 42)), (0.62, (26, 8, 58))]), 32, 7)
                       ).convert("RGBA")
    h = int(S * 0.62)
    glowD = ImageDraw.Draw(img)
    img = ovl(img, glow((S * 0.5, h - 150), 380, (255, 140, 40), 70))
    gd = ImageDraw.Draw(img)
    cx, cy, rr = S * 0.5, h - 150, 238
    for i in range(0, rr, 20):
        gd.rectangle([cx - rr, cy - rr + i, cx + rr, cy - rr + i + 9], fill=(26, 8, 58))
    rnd = random.Random(9)
    x = -10
    while x < S + 40:
        bw = rnd.randint(40, 170)
        bh = rnd.randint(60, 260)
        gd.rectangle([x, h - bh, x + bw, h], fill=(8, 5, 26))
        x += bw + rnd.randint(2, 26)
    vp = (S * 0.5, h)
    for i in range(-9, 10):
        xh = S / 2 + i * 46
        gd.line([(xh, h), (S / 2 + (xh - S / 2) * 2.4, S)], fill=(255, 40, 150), width=2)
    for k in range(1, 17):
        t = k / 16
        y = h + (S - h) * t ** 1.5
        gd.line([(0, y), (S, y)], fill=(255, 40, 150), width=2)
    gd.line([(60, 60), (S - 60, 1480)], fill=(0, 255, 251), width=1)
    gd.line([(S - 60, 60), (60, 1480)], fill=(255, 40, 150), width=1)
    f_art = fload(F_COND_R, 40)
    draw_spaced(gd, (70, 66), ARTISTA, f_art, (240, 255, 255), 4)
    f_t = fit_font("CIUDAD DE NEON", 1340, 172)
    gtext(img, (S / 2, 300), "CIUDAD DE NEON", f_t, (0, 255, 251), (255, 45, 142),
          outline=(6, 2, 30), ow=3, shadow=(5, 6, (0, 0, 0)))
    f_sub = fload(F_COND_R, 40)
    draw_center(gd, (S / 2, 560), d["subtitulo"].upper(), f_sub, (255, 255, 255), 4)
    draw_center(gd, (S / 2, 620), "CANCIONES DE UNA CIUDAD", fload(F_NARR, 27),
                (0, 255, 251), 5)
    return img


# ---------------------------------------------------------------- FRONT 3 ---- OCHENTAS (arcade / MTV)
def blob(center, r, color, a):
    return glow(center, r, color, a, 60)


def front_ochentas(d):
    img = Image.fromarray(grain(v_gradient([(0.0, (16, 12, 40)), (1.0, (34, 16, 66))]), 33, 6)
                       ).convert("RGBA")
    img = ovl(img, blob((S * 0.16, S * 0.22), 540, (255, 40, 170), 44))
    img = ovl(img, blob((S * 0.86, S * 0.82), 560, (0, 229, 255), 40))
    img = ovl(img, blob((S * 0.5, S * 0.52), 330, (255, 214, 80), 40))
    gd = ImageDraw.Draw(img)
    for y in range(0, S, 5):
        gd.line([(0, y), (S, y)], fill=(0, 0, 0), width=1)
    for k in range(4):
        off = k * 14
        c = (0, 229, 255) if k % 2 else (255, 40, 170)
        pts = [(S * 0.5, 320 - off)]
        pw, ph = 210 + k * 34, 470 + k * 22
        pts += [(S * 0.5 + pw, 650 + k * 6), (S * 0.5, 900 + off + k * 8), (S * 0.5 - pw, 650 + k * 6)]
        gd.polygon(pts, outline=c + (60,), width=3)
    gd.line([(S * 0.5, 320), (S * 0.5 + 220, 650)], fill=(255, 255, 255), width=1)
    f_art = fload(F_COND_R, 38)
    draw_spaced(gd, (70, 62), ARTISTA, f_art, (255, 255, 255), 4)
    f_t = fit_font("OCHENTAS", 1320, 222)
    gtext(img, (S / 2, 540), "OCHENTAS", f_t, (255, 214, 80), (255, 45, 142),
          outline=(0, 229, 255), ow=3, shadow=(6, 8, (0, 0, 0)))
    f_sub = fload(F_COND_R, 42)
    draw_center(gd, (S / 2, 540 + 196), "★  %s  ★" % d["subtitulo"].upper(), f_sub,
                (255, 255, 255), 3)
    draw_center(gd, (S / 2, S - 96), "CANCIONES DE UNA CIUDAD", fload(F_NARR, 27),
                (0, 229, 255), 5)
    return img


# ---------------------------------------------------------------- FRONT 4 ---- LLAMAS (memphis)
def confetti(gd, rnd, n, colors, x0, x1, y0, y1):
    for _ in range(n):
        x, y = rnd.randint(x0, x1), rnd.randint(y0, y1)
        c = rnd.choice(colors)
        w = rnd.randint(7, 22)
        gd.ellipse([x, y, x + w, y + w], outline=c + (220,), width=3)


def squiggle(gd, rnd, n, color):
    for _ in range(n):
        x, y = rnd.randint(80, S - 160), rnd.randint(120, S - 200)
        w = rnd.randint(60, 150)
        gd.arc([x, y, x + w, y + w], rnd.randint(0, 180), rnd.randint(230, 360),
               fill=color + (180,), width=6)


def zigzag(gd, y, amp, width, color):
    pts = []
    x = 40
    step = 96
    while x < S - 20:
        dy = amp if (len(pts) % 2) == 0 else -amp
        pts.append((x, y + dy))
        x += step
    gd.line(pts, fill=color, width=width, joint="curve")


def front_llamas(d):
    img = Image.new("RGBA", (S, S), (6, 4, 10, 255))
    gd = ImageDraw.Draw(img)
    zig = (255, 60, 170), (0, 198, 200), (255, 212, 60)
    zigzag(gd, 150, 46, 26, zig[0])
    zigzag(gd, 240, 40, 16, zig[1])
    zigzag(gd, S - 150, 46, 26, zig[2])
    confetti(gd, random.Random(4), 90, zig, 60, S - 60, 300, S - 300)
    squiggle(gd, random.Random(5), 26, (255, 255, 255))
    flame = (255, 84, 40), (255, 168, 54), (255, 218, 96)
    for i, col in enumerate(flame):
        bx = 200 + i * 170
        gd.polygon([(bx, S + 60), (bx + 150, S + 60), (bx + 60, 880 + i * 130)],
                   outline=col, width=30)
    f_art = fload(F_COND_R, 42)
    draw_spaced(gd, (70, 64), ARTISTA, f_art, (255, 255, 255), 5)
    f_t = fit_font("LLAMAS", 1340, 300)
    gtext(img, (S / 2, 690), "LLAMAS", f_t, (255, 218, 96), (255, 70, 40),
          outline=(0, 0, 0), ow=4, shadow=(5, 7, (255, 60, 170)))
    gd.line([(S / 2 - 330, 690 + 120), (S / 2 + 330, 690 + 120)], fill=zig[2], width=6)
    f_sub = fload(F_COND_R, 44)
    draw_center(gd, (S / 2, 690 + 166), d["subtitulo"].upper(), f_sub, (255, 255, 255), 4)
    draw_center(gd, (S / 2, S - 86), "CANCIONES DE UNA CIUDAD", fload(F_NARR, 27),
                (255, 218, 96), 5)
    return img


# ---------------------------------------------------------------- FRONT 5 ---- EUFORIA (post-punk B&N)
def front_euforia(d):
    base = v_gradient([(0.0, (12, 14, 18)), (0.55, (60, 62, 66)), (1.0, (150, 150, 154))])
    m = np.zeros((S, S), float)
    xx = np.linspace(0, 1, S)[None, :]
    yy = np.linspace(0, 1, S)[:, None]
    m = np.clip(1 - (yy - xx) * 1.1, 0, 1)[:, :, None]
    base = base * (0.55 + 0.5 * m)
    img = Image.fromarray(grain(np.clip(base, 0, 255).astype(np.uint8), 34, 9)).convert("RGBA")
    gd = ImageDraw.Draw(img)
    gd.polygon([(S, 0), (S, 320), (980, 0)], fill=(0, 0, 0, 255))
    rnd = random.Random(6)
    bx = 120
    while bx < S - 120:
        bh = rnd.randint(90, 400)
        gd.rectangle([bx, 640 - bh, bx + 34, 640 + 260], fill=(0, 0, 0), width=0)
        bx += 40 + rnd.randint(4, 30)
    f_art = fload(F_COND_R, 40)
    draw_spaced(gd, (70, 66), ARTISTA, f_art, (255, 255, 255), 5)
    title = "EUFORIA"
    f_t = fit_font(title, 1340, 280)
    td = tmp_d()
    tw = sum(txt_w(td, c, f_t) + 6 for c in title) - 6
    cx = (S - tw) / 2
    y = 880
    for i, ch in enumerate(title):
        dy = rnd.choice([-14, 0, 10, 26])
        cw = txt_w(td, ch, f_t)
        gd.text((cx, y + dy), ch, font=f_t, fill=(14, 14, 16))
        gd.text((cx, y + dy - 4), ch, font=f_t, fill=(250, 250, 250))
        cx += cw + 6
    gd.rectangle([0, 0, S, 0], fill=(0, 0, 0))
    gd.line([(S * 0.5 - 240, 1010), (S * 0.5 + 240, 1010)], fill=(255, 60, 60), width=6)
    f_sub = fload(F_COND_R, 42)
    draw_center(gd, (S / 2, 1070), d["subtitulo"].upper(), f_sub, (245, 245, 245), 5)
    draw_center(gd, (S / 2, S - 92), "CANCIONES DE UNA CIUDAD", fload(F_NARR, 27),
                (220, 220, 220), 5)
    return img


FRONTS = {1: front_medianoche, 2: front_ciudad, 3: front_ochentas, 4: front_llamas,
          5: front_euforia}


# ---------------------------------------------------------------- BACK
BACK_STYLE = {1: "luna", 2: "sol", 3: "diamante", 4: "zigzag", 5: "barras"}
BACK_TINT = {1: (24, 22, 44), 2: (18, 8, 48), 3: (20, 14, 46), 4: (12, 8, 18), 5: (20, 20, 24)}


def back_mark(kind):
    layer = Image.new("RGBA", (S, S), (0, 0, 0, 0))
    gd = ImageDraw.Draw(layer)
    c = (255, 255, 255)
    if kind == "luna":
        gd.ellipse([S / 2 - 120, 110, S / 2 + 120, 350], outline=c + (28,), width=2)
    elif kind == "sol":
        for i in range(5):
            gd.rectangle([S / 2 - 130, 150 + i * 34, S / 2 + 130, 150 + i * 34 + 16],
                         outline=c + (26,), width=1)
    elif kind == "diamante":
        gd.polygon([(S / 2, 90), (S / 2 + 120, 220), (S / 2, 350), (S / 2 - 120, 220)],
                   outline=c + (26,), width=2)
    elif kind == "zigzag":
        pts = []
        for i in range(7):
            pts.append((S / 2 - 165 + i * 55, 230 if i % 2 == 0 else 130))
        gd.line(pts, fill=c + (26,), width=3)
    else:
        gd.line([(S / 2 - 150, 170), (S / 2 - 60, 280), (S / 2 + 40, 240)], fill=c + (30,), width=8)
    return layer


def draw_back(d, palette):
    tint = BACK_TINT[d["numero"]]
    img = Image.fromarray(grain(v_gradient([(0.0, tint), (1.0, (54, 50, 70))]), 40 + d["numero"], 5)
                       ).convert("RGBA")
    img = ovl(img, back_mark(BACK_STYLE[d["numero"]]))
    gd = ImageDraw.Draw(img)
    gold = (214, 178, 120)
    cream = (246, 238, 224)
    gd.rectangle([34, 34, S - 34, S - 34], outline=gold, width=1)
    gd.rectangle([42, 42, S - 42, S - 42], outline=cream + (90,), width=1)
    f_h = fload(F_SERIF, 44)
    draw_center(gd, (S / 2, 118), "CANCIONES DE UNA CIUDAD", f_h, gold, 6)
    draw_center(gd, (S / 2, 196), "UNA COLECCION EN VINILO", fload(F_NARR, 26),
                cream + (200,), 4)
    draw_center(gd, (S / 2, 268), "TRACKLIST", fload(F_NARR, 30), cream + (235,), 10)
    gd.line([(S / 2 - 110, 322), (S / 2 + 110, 322)], fill=gold, width=1)

    tr = d["tracklist"]
    half = math.ceil(len(tr) / 2)
    cols = [tr[:half], tr[half:]]
    f_t = fload(F_SERIF_B, 30)
    f_dur = fload(F_NARR, 26)
    f_lado = fload(F_COND_R, 36)
    for ci, col in enumerate(cols):
        xx = 118 if ci == 0 else 810
        draw_spaced(gd, (xx, 378), "LADO %s" % ("A" if ci == 0 else "B"), f_lado, gold, 4)
        y0 = 442
        for row in col:
            yy = y0 + (row["n"] - 1 - (0 if ci == 0 else half)) * 50
            gd.text((xx, yy), str(row["n"]).zfill(2), font=f_t, fill=gold)
            gd.text((xx + 62, yy), row["titulo"], font=f_t, fill=cream)
            dw = txt_w(gd, fmt(row["duracion"]), f_dur)
            gd.text((xx + 500 - dw, yy), fmt(row["duracion"]), font=f_dur, fill=gold)

    rows = max(len(cols[0]), len(cols[1]))
    yf = 442 + rows * 50 + 40
    f_cred = fload(F_NARR, 26)
    for i, txt in enumerate(
            ("MUSICA Y VOZ: %s      ARREGLOS: ESTUDIO CENTRAL" % ARTISTA,
             "COLECCION CANCIONES DE UNA CIUDAD",
             "(C) (P) 2026  EL DESVAN DEL VINILO  -  33 1/3 RPM  -  ESTEREO")):
        draw_center(gd, (S / 2, yf + i * 40), txt, f_cred, cream + (190,), 2)

    bx, by, bw, bh = S - 480, yf + 148, 300, 56
    rnd = random.Random(4400 + d["numero"])
    x = bx
    while x < bx + bw:
        w = rnd.randint(2, 5)
        if x + w <= bx + bw:
            gd.rectangle([x, by, x + w, by + bh], fill=cream)
        x += w + rnd.randint(3, 6)
    return img


for d in BOX:
    print(d["titulo"], "...", flush=True)
    front = FRONTS[d["numero"]](d)
    back = draw_back(d, BACK_TINT[d["numero"]])
    base = os.path.join(TAPAS, d["slug"])
    front.convert("RGB").save(base + "_front.jpg", quality=93)
    back.convert("RGB").save(base + "_back.jpg", quality=93)
    print("OK", base + "_front.jpg")

print("Tapas 80s generadas:", len(BOX) * 2)