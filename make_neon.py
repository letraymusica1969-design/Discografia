# -*- coding: utf-8 -*-
import os, sys
import numpy as np
from PIL import Image, ImageDraw, ImageFont, ImageFilter

sys.stdout.reconfigure(encoding="utf-8")
OUT = os.path.dirname(os.path.abspath(__file__))
SIGN = os.path.join(OUT, "web", "public", "sign")
os.makedirs(SIGN, exist_ok=True)

FONT = r"C:\Windows\Fonts\ARLRDBD.TTF"
FINAL = 620
GAS_MID = (255, 178, 60)


def letter_blob(ch):
    font = ImageFont.truetype(FONT, round(FINAL * 0.9))
    bb = font.getbbox(ch)
    W = bb[2] - bb[0]
    H = bb[3] - bb[1]
    pad = 90
    img = Image.new("L", (W + pad * 2, H + pad * 2), 0)
    d = ImageDraw.Draw(img)
    d.text((pad - bb[0], pad - bb[1]), ch, font=font, fill=255)
    a = np.asarray(img.filter(ImageFilter.GaussianBlur(1.4)), dtype=float)
    return np.clip((a - 16) * (255.0 / 216.0), 0, 255).astype(np.float64)


def build_letter(ch, dead=False):
    blob = letter_blob(ch)
    blob = np.asarray(Image.fromarray(blob.astype(np.uint8)).resize(
        (FINAL, FINAL), Image.LANCZOS), dtype=np.float64)
    a_u8 = ((blob > 120) * 255).astype(np.uint8)
    a = np.clip(blob / 255.0, 0, 1)
    Hc = Wc = FINAL
    yy = np.linspace(0, 1, Hc)[:, None]

    core = (np.asarray(Image.fromarray(a_u8).filter(ImageFilter.MinFilter(41))) > 0)
    rim_arr = np.clip(a_u8.astype(float) - np.asarray(
        Image.fromarray(a_u8).filter(ImageFilter.MinFilter(13))).astype(float), 0, 255)

    if dead:
        halo_alpha = 15
        hot = 0.0
        c_top, c_mid, c_bot = (84, 26, 8), (48, 15, 4), (18, 6, 2)
        w_top, w_mid, w_bot = (58, 18, 6), (36, 11, 3), (13, 4, 2)
    else:
        halo_alpha = 66
        hot = 1.0
        c_top, c_mid, c_bot = (255, 244, 206), (255, 198, 88), (255, 142, 26)
        w_top, w_mid, w_bot = (230, 110, 18), (198, 70, 8), (140, 44, 4)

    t = np.clip(yy, 0, 1)

    def ramp(TOP, MID, BOT, t):
        out = np.zeros((len(t), 3))
        for i in range(3):
            out[:, i] = np.where(t[:, 0] < 0.4,
                                 TOP[i] + (MID[i] - TOP[i]) * (t[:, 0] / 0.4),
                                 MID[i] + (BOT[i] - MID[i]) * ((t[:, 0] - 0.4) / 0.6))
        return out

    core_col = ramp(c_top, c_mid, c_bot, t)
    wall_col = ramp(w_top, w_mid, w_bot, t)
    hot_bump = np.exp(-((yy - 0.26) / 0.12) ** 2) * 100 * hot
    core_col[:, 0] = np.clip(core_col[:, 0] + hot_bump[:, 0], 0, 255)

    col = np.empty((Hc, Wc, 3))
    col[:] = wall_col[:, None, :]
    col[core] = core_col[np.nonzero(core)[0]]
    col[rim_arr > 0] *= 0.74

    ske = (np.asarray(Image.fromarray(a_u8).filter(ImageFilter.MinFilter(19))) > 0)
    ske_u8 = (ske * 255).astype(np.uint8)
    low = Image.fromarray(ske_u8).transform((Wc, Hc), Image.AFFINE,
                                            (1, 0, 0, 0, 1, 5), resample=Image.NEAREST)
    shadow_band = (a_u8 > 0) & (np.asarray(low) > 0)
    col[shadow_band] *= 0.48
    hi = Image.fromarray(ske_u8).transform((Wc, Hc), Image.AFFINE,
                                           (1, 0, 0, 0, 1, -4), resample=Image.NEAREST)
    hi_band = (a_u8 > 0) & (np.asarray(hi) > 0)
    col[hi_band] = np.clip(col[hi_band] * 1.2, 0, 255)

    halo = a[..., None] * (np.array(GAS_MID)[None, None, :]) * (halo_alpha / 255.0)
    halo = Image.fromarray(np.clip(halo, 0, 255).astype(np.uint8)).convert("RGBA")
    halo.putalpha(Image.fromarray((a * halo_alpha).astype(np.uint8)))
    halo = halo.filter(ImageFilter.GaussianBlur(7))

    tube_img = Image.fromarray(np.clip(col, 0, 255).astype(np.uint8)).convert("RGBA")
    tube_img.putalpha(Image.fromarray((a * 255).astype(np.uint8)))

    top_w = np.clip(1 - yy * 1.3, 0.15, 1)
    hl = rim_arr * top_w * (0.95 if not dead else 0.25)
    ring_img = Image.new("RGBA", (Wc, Hc), (0, 0, 0, 0))
    ring_img.putalpha(Image.fromarray(hl.astype(np.uint8)))
    ring_col = Image.new("RGBA", (Wc, Hc), (255, 253, 238, 255))
    ring_img = Image.composite(ring_col, ring_img, ring_img.split()[3])

    out = Image.new("RGBA", (Wc, Hc), (0, 0, 0, 0))
    out.alpha_composite(halo)
    out.alpha_composite(tube_img)
    out.alpha_composite(ring_img)

    alpha_arr = np.asarray(out)[..., 3]
    ys, xs = np.nonzero(alpha_arr > 6)
    if len(ys):
        pad = 14
        box = (max(xs.min() - pad, 0), max(ys.min() - pad, 0),
               min(xs.max() + pad + 1, Wc), min(ys.max() + pad + 1, Hc))
        out = out.crop(box)
    return out


def main():
    only = sys.argv[1] if len(sys.argv) > 1 else None
    chars = set("SANDRO") | set("SAAVEDRA")
    for ch in sorted(chars):
        for dead in (False, True):
            if only and only != ch + ("_burn" if dead else ""):
                continue
            name = f"let_{ch}" + ("_burn" if dead else "") + ".png"
            img = build_letter(ch, dead)
            if img is None:
                print("SKIP", name)
                continue
            img.save(os.path.join(SIGN, name))
            print("OK", name)


main()