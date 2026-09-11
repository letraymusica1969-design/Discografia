# -*- coding: utf-8 -*-
import os, sys, json, re, subprocess
import imageio_ffmpeg

sys.stdout.reconfigure(encoding="utf-8")

FFMPEG = imageio_ffmpeg.get_ffmpeg_exe()
OUT = r"C:\AI\Antigravity\musica"
MASTER = os.path.join(OUT, "Master_Estudio")

LUFS_TARGET = -14.0
TP_TARGET = -1.6
LRA_TARGET = 11.0

PRE = (
    "afftdn=nr=12:nf=-55:tn=1,"
    "highpass=f=25,"
    "equalizer=f=80:t=q:w=1.0:g=0.5,"
    "equalizer=f=240:t=q:w=1.6:g=-1.5,"
    "equalizer=f=1200:t=q:w=1.5:g=0.6,"
    "equalizer=f=3400:t=q:w=1.2:g=1.3,"
    "equalizer=f=9500:t=q:w=1.8:g=1.1,"
    "acompressor=threshold=0.015:ratio=2.4:attack=8:release=200:makeup=1"
)

def run(cmd):
    p = subprocess.run(cmd, capture_output=True, text=True, encoding="utf-8", errors="replace")
    return p.returncode, p.stdout, p.stderr

def measure(src):
    af = f"{PRE},loudnorm=I={LUFS_TARGET}:TP={TP_TARGET}:LRA={LRA_TARGET}:print_format=json"
    code, _, err = run([
        FFMPEG, "-hide_banner", "-i", src, "-vn",
        "-af", af, "-f", "null", "-"
    ])
    if code != 0:
        raise RuntimeError(f"Medida fallida: {err[-500:]}")
    vals = {}
    for name in ("input_i", "input_tp", "input_lra", "input_thresh", "target_offset"):
        m = re.search(rf'"\s*{name}\s*"\s*:\s*"?([-0-9.]+)"?', err)
        if m:
            vals[name] = m.group(1)
    return vals

def apply_chain(src, dst, meas):
    af = (
        f"{PRE},loudnorm=I={LUFS_TARGET}:TP={TP_TARGET}:LRA={LRA_TARGET}"
        f":measured_I={meas['input_i']}:measured_TP={meas['input_tp']}"
        f":measured_LRA={meas['input_lra']}:measured_thresh={meas['input_thresh']}"
    )
    code, _, err = run([
        FFMPEG, "-y", "-hide_banner", "-i", src, "-vn",
        "-af", af, "-c:a", "flac", "-compression_level", "8", dst
    ])
    if code != 0:
        raise RuntimeError(f"Procesamiento fallido: {err[-500:]}")

def master_mp3(src, dst):
    meas = measure(src)
    apply_chain(src, dst, meas)

if __name__ == "__main__":
    src = sys.argv[1]
    dst = sys.argv[2]
    print(f"Master: {os.path.basename(src)}")
    meas = measure(src)
    print("  medidas:", {k: v for k, v in meas.items()})
    apply_chain(src, dst, meas)
    print("  OK ->", dst)