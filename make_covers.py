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
    1: dict(stops=[(0, (5, 7, 18)), (0.38, (28, 20, 54)), (0.7, (88, 44, 96)),
                   (1.0, (132, 66, 108))],
            gold=(214, 176, 120), cream=(242, 234, 222), moon=(255, 240, 210),
            glow=(255, 214, 170)),
    2: dict(stops=[(0, (6, 3, 26)), (0.55, (24, 10, 58)), (1.0, (86, 22, 96))],
            cyan=(0, 255, 251), magenta=(255, 45, 142), sun=(255, 152, 60),
            glow=(255, 96, 180)),
    3: dict(stops=[(0, (20, 16, 44)), (0.6, (66, 34, 84)), (1.0, (128, 70, 112))],
            cream=(250, 240, 218), amber=(255, 204, 92), blue=(128, 194, 255),
            glow=(255, 170, 80)),
    4: dict(stops=[(0, (18, 3, 6)), (0.5, (92, 12, 20)), (1.0, (150, 36, 16))],
            gold=(255, 214, 96), crimson=(255, 84, 46), teal=(80, 216, 200),
            glow=(255, 150, 50)),
    5: dict(stops=[(0, (8, 10, 14)), (0.5, (44, 48, 56)), (1.0, (104, 108, 118))],
            wh=(250, 250, 248), red=(255, 84, 84), lime=(196, 255, 132),
            glow=(255, 120, 120)),
}


# ---- 1 MEDIANOCHE : nocturno con luna de nubes y bokeh ----
def front_medianoche(p):
    img = base_art(p, 101)
    img = ovl(img, glayer((S * 0.5, 470), 330, p["moon"], 34))
    lay = Image.new("RGBA", (S, S), (0, 0, 0, 0))
    d = ImageDraw.Draw(lay)
    d.ellipse([S * 0.5 - 260, 210, S * 0.5 + 260, 730], fill=(255, 244, 218, 60))
    d.ellipse([S * 0.5 - 238, 238, S * 0.5 + 238, 702], fill=(120, 80, 120, 0),
              outline=(255, 244, 218, 90), width=2)
    d.ellipse([S * 0.74, 120, S * 1.12, 460], outline=(214, 176, 120, 40), width=2)
    bl = lay.filter(ImageFilter.GaussianBlur(18))
    img = ovl(img, bl)
    rnd = random.Random(11)
    img = ovl(img, bokeh(img, rnd, (255, 214, 170), 44, 330, 900, 60, S - 60))
    img = grain_add(np.asarray(img.convert("RGB")), 12, 7)
    img = Image.fromarray(img).convert("RGBA")
    dr = ImageDraw.Draw(img)
    dr.rectangle([44, 44, S - 44, S - 44], outline=p["gold"], width=1)
    dr.rectangle([52, 52, S - 52, S - 52], outline=(214, 176, 120, 120), width=1)
    f_art = fload(F_SERIF, 34)
    draw_center(dr, (S / 2, 118), ARTISTA, f_art, p["cream"], 8)
    sculpt_title(img, "MEDIANOCHE", F_BOD, (150, 112, 66), (238, 204, 150),
                 (6, 6, 16), p["moon"], 2, 2)
    f_sub = fload(F_SERIF, 40)
    draw_center(dr, (S / 2, 862), p["sub"].upper(), f_sub, p["cream"], 6)
    dr.line([(S / 2 - 110, 806), (S / 2 + 110, 806)], fill=p["gold"], width=1)
    draw_center(dr, (S / 2, S - 108), "CANCIONES DE UNA CIUDAD", fload(F_NARR, 26),
                p["gold"], 7)
    draw_center(dr, (S / 2, S - 62), "COLECCION EN VINILO  -  33 1/3 RPM  -  ESTEREO",
                fload(F_NARR, 22), (242, 234, 222), 4)
    return img


# ---- 2 CIUDAD DE NEON : grid + ola neon + sol ----
def front_ciudad(p):
    img = base_art(p, 202)
    img = ovl(img, glayer((S * 0.5, 330), 380, p["sun"], 44))
    lay = Image.new("RGBA", (S, S), (0, 0, 0, 0))
    d = ImageDraw.Draw(lay)
    cx, cy, rr = S * 0.5, 330, 250
    d.ellipse([cx - rr, cy - rr, cx + rr, cy + rr], fill=p["sun"] + (235,))
    for i in range(0, rr, 18):
        d.rectangle([cx - rr, cy - rr + i, cx + rr, cy - rr + i + 8], fill=(14, 6, 40))
    bl = lay.filter(ImageFilter.GaussianBlur(6))
    img = ovl(img, bl)
    rnd = random.Random(13)
    x = -20
    lay2 = Image.new("RGBA", (S, S), (0, 0, 0, 0))
    d2 = ImageDraw.Draw(lay2)
    h = int(S * 0.66)
    while x < S + 60:
        bw = rnd.randint(36, 150)
        bh = rnd.randint(40, 210)
        d2.rectangle([x, h - bh, x + bw, h], fill=(6, 2, 20))
        x += bw + rnd.randint(0, 30)
    img = ovl(img, lay2)
    gr = Image.new("RGBA", (S, S), (0, 0, 0, 0))
    g = ImageDraw.Draw(gr)
    for i in range(-8, 9):
        xh = S / 2 + i * 46
        g.line([(xh, h), (S / 2 + (xh - S / 2) * 3, S)], fill=p["magenta"], width=2)
    for k in range(1, 15):
        t = k / 15
        y = h + (S - h) * t ** 1.45
        g.line([(0, y), (S, y)], fill=p["magenta"], width=2)
    img = ovl(img, gr)
    wv = Image.new("RGBA", (S, S), (0, 0, 0, 0))
    w = ImageDraw.Draw(wv)
    pts = []
    xx = np.linspace(-40, S + 40, 120)
    yy = 1240 + 120 * np.sin(xx / 150) + 45 * np.sin(xx / 47 + 1.2)
    pts += [(float(xx[i]), float(yy[i])) for i in range(len(xx))]
    for r, wdt in ((12, 14), (0, 5)):
        w.line(pts, fill=(255, 255, 255, 255), width=wdt)
    wb = wv.filter(ImageFilter.GaussianBlur(8))
    img = ovl(img, wb)
    img = grain_add(np.asarray(img.convert("RGB")), 14, 6)
    img = Image.fromarray(img).convert("RGBA")
    dr = ImageDraw.Draw(img)
    draw_spaced(dr, (66, 64), ARTISTA, fload(F_COND_R, 38), p["cyan"], 5)
    sculpt_title(img, "CIUDAD DE NEON", F_COND, (40, 255, 252), (255, 64, 170),
                 (4, 0, 20), p["glow"], 2, 3)
    f_sub = fload(F_COND_R, 42)
    draw_center(dr, (S / 2, 470), p["sub"].upper(), f_sub, (255, 255, 255), 5)
    draw_center(dr, (S / 2, S - 96), "CANCIONES DE UNA CIUDAD", fload(F_NARR, 26),
                p["cyan"], 5)
    return img


# ---- 3 OCHENTAS : arco de medios tonos + titulo volumetrico ----
def front_ochentas(p):
    base = grad_img(p["stops"]).astype(float)
    n = perlin(303, 4, 96)
    base *= (0.6 + 0.55 * n[:, :, None])
    img = Image.fromarray(to_rgb(base)).convert("RGBA")
    img = ovl(img, glayer((S * 0.14, S * 0.3), 460, p["blue"], 30))
    img = ovl(img, glayer((S * 0.86, S * 0.72), 470, p["amber"], 34))
    arch = Image.new("RGBA", (S, S), (0, 0, 0, 0))
    d = ImageDraw.Draw(arch)
    for k, (rr, wdt, col) in enumerate(((260, 10, p["cream"]), (310, 3, p["amber"]),
                                        (360, 10, p["blue"]), (410, 3, p["cream"]),
                                        (470, 2, p["amber"]))):
        d.arc([S / 2 - rr, 150, S / 2 + rr, 150 + rr * 2], 180, 360, fill=col + (120,), width=wdt)
    bl = arch.filter(ImageFilter.GaussianBlur(8))
    img = ovl(img, bl)
    img = grain_add(np.asarray(img.convert("RGB")), 16, 9)
    img = Image.fromarray(img).convert("RGBA")
    dr = ImageDraw.Draw(img)
    draw_spaced(dr, (66, 64), ARTISTA, fload(F_COND_R, 40), p["cream"], 5)
    sculpt_title(img, "OCHENTAS", F_COND, (255, 224, 130), (236, 96, 130),
                 (10, 6, 26), p["glow"], 2, 2)
    f_sub = fload(F_COND_R, 44)
    draw_center(dr, (S / 2, 622), "★  %s  ★" % p["sub"].upper(), f_sub,
                p["cream"], 4)
    dr.line([(S / 2 - 150, 700), (S / 2 + 150, 700)], fill=p["cream"], width=1)
    draw_center(dr, (S / 2, S - 96), "CANCIONES DE UNA CIUDAD", fload(F_NARR, 26),
                p["blue"], 6)
    return img


# ---- 4 LLAMAS : campo de fuego flow (perlin de calor) ----
def front_llamas(p):
    arr = grad_img(p["stops"]).astype(float)
    n = perlin(404, 5, 64)
    t = np.linspace(0, 1, S)[:, None]
    wavy = n * 0.6 + 0.28 * np.sin(np.linspace(0, 6, S)[None, :] * 4 + t * 2)
    cap = 1 - np.clip((1 + (np.linspace(0, 1, S)[None, :] - 0.62) * 8), 0, 1)
    val = np.clip(wavy * 2.2 - (1 - cap) * 1.6, 0, 1)
    arr = arr * (0.55 + 1.2 * val[:, :, None])
    arr = to_rgb(arr)
    img = Image.fromarray(arr).convert("RGBA")
    img = ovl(img, glayer((S * 0.3, 1050), 420, p["gold"], 34))
    img = ovl(img, glayer((S * 0.68, 560), 340, p["crimson"], 30))
    img = grain_add(np.asarray(img.convert("RGB")), 18, 8)
    img = Image.fromarray(img).convert("RGBA")
    dr = ImageDraw.Draw(img)
    dr.rectangle([44, 44, S - 44, S - 44], outline=p["teal"], width=1)
    draw_spaced(dr, (66, 64), ARTISTA, fload(F_COND_R, 42), p["gold"], 5)
    sculpt_title(img, "LLAMAS", F_COND, (255, 240, 150), (255, 70, 30),
                 (30, 4, 6), p["glow"], 2, 2)
    f_sub = fload(F_COND_R, 46)
    draw_center(dr, (S / 2, 668), p["sub"].upper(), f_sub, p["cream"] if False else
                (255, 240, 220), 5)
    dr.line([(S / 2 - 160, 724), (S / 2 + 160, 724)], fill=p["gold"], width=6)
    draw_center(dr, (S / 2, S - 96), "CANCIONES DE UNA CIUDAD", fload(F_NARR, 26),
                p["gold"], 6)
    return img


# ---- 5 EUFORIA : estallido radial + anillo ----
def front_euforia(p):
    base = grad_img(p["stops"]).astype(float)
    n = perlin(505, 4, 96)
    base *= (0.7 + 0.5 * n[:, :, None])
    base = to_rgb(base)
    img = Image.fromarray(base).convert("RGBA")
    cx, cy = S * 0.5, S * 0.42
    lay = Image.new("RGBA", (S, S), (0, 0, 0, 0))
    d = ImageDraw.Draw(lay)
    rnd = random.Random(21)
    for i in range(220):
        ang = rnd.uniform(0, math.pi * 2)
        rr = rnd.uniform(120, 680)
        wd = rnd.choice([2, 2, 4, 7])
        i2 = rnd.uniform(0, 1)
        col = tuple(int(p["wh"][k] * (0.3 + 0.7 * i2)) for k in range(3))
        a = int(20 + 120 * (1 - rr / 690))
        x0 = cx + rr * math.cos(ang)
        y0 = cy + rr * math.sin(ang) * 0.9
        x1 = cx + (rr + 40 + 40 * i2) * math.cos(ang)
        y1 = cy + (rr + 40 + 40 * i2) * math.sin(ang) * 0.9
        d.line([(x0, y0), (x1, y1)], fill=col + (a,), width=wd)
    d.ellipse([cx - 210, cy - 210, cx + 210, cy + 210], outline=p["wh"] + (60,), width=2)
    d.ellipse([cx - 240, cy - 240, cx + 240, cy + 240], outline=p["red"] + (70,), width=3)
    bl = lay.filter(ImageFilter.GaussianBlur(4))
    img = ovl(img, bl)
    img = grain_add(np.asarray(img.convert("RGB")), 23, 10)
    img = Image.fromarray(img).convert("RGBA")
    dr = ImageDraw.Draw(img)
    dr.line([(S * 0.5 - 250, 150), (S * 0.5 + 250, 150)], fill=p["red"], width=1)
    draw_spaced(dr, (66, 64), ARTISTA, fload(F_COND_R, 40), p["wh"], 5)
    sculpt_title(img, "EUFORIA", F_COND, (250, 250, 248), (196, 210, 220),
                 (10, 10, 14), p["glow"], 2, 2)
    f_sub = fload(F_COND_R, 44)
    draw_center(dr, (S / 2, 760), p["sub"].upper(), f_sub, p["wh"], 5)
    draw_center(dr, (S / 2, S - 96), "CANCIONES DE UNA CIUDAD", fload(F_NARR, 26),
                p["lime"], 6)
    return img


FRONTS = {1: front_medianoche, 2: front_ciudad, 3: front_ochentas, 4: front_llamas,
          5: front_euforia}


def np_random_halftone(seed):
    return None


# ---------------- DORSO ----------------
BACK_TINT = {1: (10, 12, 26), 2: (12, 8, 30), 3: (18, 12, 30), 4: (22, 8, 10), 5: (16, 18, 22)}


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
    draw_center(dr, (S / 2, 188), "UNA COLECCION EN VINILO", fload(F_NARR, 26),
                (244, 236, 222), 4)
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