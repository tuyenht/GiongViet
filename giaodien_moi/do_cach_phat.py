# -*- coding: utf-8 -*-
"""So cac CACH PHAT am thanh, do xem cach nao ra tieng nhanh nhat.

Chu du an yeu cau: "do tre thap nhat co the, giong doc phat ra loa nhanh nhat
co the sau khi an nut play".

Hien tai moi mau dung MOT tien trinh ffplay moi. Do duoc 941 ms tu luc bo_doc
goi play() den luc loa ra tieng - va do la chi phi CO DINH moi lan, khong phu
thuoc do dai doan. Bai nay do xem chi phi ay nam o dau va cat bot duoc bao
nhieu.

CACH DO: ffplay chay voi -autoexit nen no thoat NGAY khi het audio. Vay
    tre = (thoi gian tien trinh song) - (do dai WAV)
la khoang loa con im truoc khi ra tieng. Voi winsound thi PlaySound chan den
het, do y het.

Phat WAV IM LANG nen bai nay khong on. Khong cham vao san pham, khong cham du
lieu nguoi dung - chi do.

Chay:  py giaodien_moi/do_cach_phat.py
"""
import io
import os
import statistics
import struct
import subprocess
import sys
import threading
import time
import wave

sys.path.insert(0, r"C:\Projects\DocCongDuc")
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8",
                              line_buffering=True)

import DocCongDuc as engine  # noqa: E402

DAI_GIAY = 2.0
TAN_SO = 24000          # VieNeu tra ve 24 kHz
SO_LAN = 5

FFPLAY = str(engine.load_config()["ffplay"])

CO_CHUNG = ["-hide_banner", "-loglevel", "error", "-nodisp", "-autoexit", "-vn"]

# Tung bo co, dat ten theo thu no cat bot.
CACH_FFPLAY = [
    ("hien tai (dang chay)", CO_CHUNG + ["-f", "wav", "-i", "pipe:0"]),
    ("+ probesize 32", CO_CHUNG + ["-probesize", "32", "-analyzeduration", "0",
                                   "-f", "wav", "-i", "pipe:0"]),
    ("+ nobuffer low_delay", CO_CHUNG + ["-fflags", "nobuffer", "-flags", "low_delay",
                                         "-f", "wav", "-i", "pipe:0"]),
    ("+ ca hai", CO_CHUNG + ["-probesize", "32", "-analyzeduration", "0",
                             "-fflags", "nobuffer", "-flags", "low_delay",
                             "-f", "wav", "-i", "pipe:0"]),
    ("raw PCM (khong doan dinh dang)",
     CO_CHUNG + ["-probesize", "32", "-analyzeduration", "0",
                 "-fflags", "nobuffer", "-flags", "low_delay",
                 "-f", "s16le", "-ar", str(TAN_SO), "-ac", "1", "-i", "pipe:0"]),
]


def wav_im_lang(giay=DAI_GIAY, rate=TAN_SO) -> bytes:
    buf = io.BytesIO()
    with wave.open(buf, "wb") as w:
        w.setnchannels(1)
        w.setsampwidth(2)
        w.setframerate(rate)
        w.writeframes(b"\x00\x00" * int(rate * giay))
    return buf.getvalue()


def pcm_im_lang(giay=DAI_GIAY, rate=TAN_SO) -> bytes:
    return b"\x00\x00" * int(rate * giay)


def _bom(proc, data):
    try:
        proc.stdin.write(data)
        proc.stdin.flush()
        proc.stdin.close()
    except OSError:
        pass


def do_ffplay(co, data) -> float:
    """Tra ve tre (giay): thoi gian song cua tien trinh tru do dai WAV."""
    si, cf = None, 0
    if os.name == "nt":
        si = subprocess.STARTUPINFO()
        si.dwFlags |= subprocess.STARTF_USESHOWWINDOW
        si.wShowWindow = 0
        cf = subprocess.CREATE_NO_WINDOW
    t0 = time.perf_counter()
    proc = subprocess.Popen([FFPLAY] + co, stdin=subprocess.PIPE,
                            stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL,
                            startupinfo=si, creationflags=cf)
    threading.Thread(target=_bom, args=(proc, data), daemon=True).start()
    proc.wait(timeout=60)
    return (time.perf_counter() - t0) - DAI_GIAY


def do_winsound(data) -> float:
    import winsound
    t0 = time.perf_counter()
    winsound.PlaySound(data, winsound.SND_MEMORY)   # SND_SYNC la mac dinh
    return (time.perf_counter() - t0) - DAI_GIAY


def do_song_san(data_pcm) -> float:
    """Mot tien trinh ffplay SONG SAN, chi bom PCM vao khi can phat.

    Bo -autoexit de no dung cho. Do bang cach: bom xong thi doi dung DAI_GIAY
    roi tinh phan troi them - khong do duoc bang luc thoat nua, nen do bang
    thoi diem tien trinh bat dau doc het stdin. Con so nay chi de tham khao:
    no cho thay chi phi KHOI DONG bi cat di bao nhieu.
    """
    si, cf = None, 0
    if os.name == "nt":
        si = subprocess.STARTUPINFO()
        si.dwFlags |= subprocess.STARTF_USESHOWWINDOW
        si.wShowWindow = 0
        cf = subprocess.CREATE_NO_WINDOW
    proc = subprocess.Popen(
        [FFPLAY, "-hide_banner", "-loglevel", "error", "-nodisp", "-vn",
         "-probesize", "32", "-analyzeduration", "0",
         "-fflags", "nobuffer", "-flags", "low_delay",
         "-f", "s16le", "-ar", str(TAN_SO), "-ac", "1", "-i", "pipe:0"],
        stdin=subprocess.PIPE, stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL, startupinfo=si, creationflags=cf)
    time.sleep(1.5)                      # de no khoi dong xong han
    t0 = time.perf_counter()
    try:
        proc.stdin.write(data_pcm)
        proc.stdin.flush()
    except OSError:
        pass
    bom_xong = time.perf_counter() - t0
    time.sleep(DAI_GIAY + 0.5)
    try:
        proc.kill()
    except OSError:
        pass
    return bom_xong


def bang(nhan, ds):
    """Tre AM = tien trinh thoat TRUOC khi phat het -> no bo do, khong phai nhanh.

    Da vap that: '-fflags nobuffer -flags low_delay' cho ra -1261 ms va bai do
    xep no hang nhat, trong khi thuc te ffplay chet ngay va Python bao
    OSError khi ghi vao pipe da dong.
    """
    if min(ds) < -0.05:
        print(f"  {nhan:<34}  HONG — thoat som {min(ds) * -1000:.0f} ms, "
              f"khong phat het")
        return None
    tb = statistics.mean(ds)
    print(f"  {nhan:<34} {tb * 1000:6.0f} ms   "
          f"(thap {min(ds) * 1000:4.0f} · cao {max(ds) * 1000:4.0f})")
    return tb


def main():
    print(f"ffplay: {FFPLAY}")
    print(f"WAV im lang {DAI_GIAY}s · {TAN_SO} Hz · moi cach do {SO_LAN} lan\n")
    print("=" * 74)
    print("  TRE = tu luc goi phat den luc loa bat dau ra tieng")
    print("=" * 74)

    wav = wav_im_lang()
    pcm = pcm_im_lang()
    ket = []

    for nhan, co in CACH_FFPLAY:
        data = pcm if "s16le" in co else wav
        ds = []
        for _ in range(SO_LAN):
            try:
                ds.append(do_ffplay(co, data))
            except (OSError, subprocess.SubprocessError) as e:
                print(f"  {nhan:<34} loi: {e}")
                break
            time.sleep(0.25)
        if ds:
            tb = bang(nhan, ds)
            if tb is not None:
                ket.append((nhan, tb))

    if os.name == "nt":
        ds = []
        for _ in range(SO_LAN):
            try:
                ds.append(do_winsound(wav))
            except Exception as e:                      # noqa: BLE001
                print(f"  {'winsound (Windows API)':<34} loi: {e}")
                break
            time.sleep(0.25)
        if ds:
            tb = bang("winsound (Windows API)", ds)
            if tb is not None:
                ket.append(("winsound (Windows API)", tb))

    print()
    print("  Tien trinh ffplay SONG SAN — chi phi bom du lieu, da bo khoi dong:")
    try:
        ds = [do_song_san(pcm) for _ in range(3)]
        bang("ffplay song san (chi bom)", ds)
    except (OSError, subprocess.SubprocessError) as e:
        print(f"    loi: {e}")

    if ket:
        ket.sort(key=lambda x: x[1])
        goc = next((v for n, v in ket if n.startswith("hien tai")), None)
        print()
        print("=" * 74)
        print(f"  NHANH NHAT: {ket[0][0]} — {ket[0][1] * 1000:.0f} ms")
        if goc:
            print(f"  Hien tai  : {goc * 1000:.0f} ms  →  cat duoc "
                  f"{(goc - ket[0][1]) * 1000:.0f} ms")
        print("=" * 74)

    sys.stdout.flush()
    os._exit(0)


if __name__ == "__main__":
    main()
