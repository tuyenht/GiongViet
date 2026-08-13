# -*- coding: utf-8 -*-
"""Kiem ban DONG GOI (.exe) co that su chay duoc khong.

KPI cua du an: "ban .exe phai chay duoc, khong chi ban source". Ca phien lam
viec truoc do deu chay tu source; bai nay la mat xich con thieu.

Chay tu source KHONG chung minh .exe chay duoc - du an nay da mat 4 vong vi
bo qua dieu do. Nhung thu chi lo ra o ban dong goi:
  · thieu --add-data ui-moi   -> cua so mo ra TRANG TRON
  · thieu --collect-data      -> danh sach giong RONG / "os error 2" luc bam doc
  · thieu hidden-import       -> ImportError ngay khi khoi dong

Bai nay KHONG bam nut duoc (khong voi tay vao trong .exe). No kiem nhung thu
do duoc tu ben ngoai: tien trinh song, cua so hien ra, nhat ky loi, va thoat
co sach khong.

Chay:  py KiemBanExe.py
"""
import ctypes
import io
import subprocess
import sys
import time
from ctypes import wintypes
from pathlib import Path

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8",
                              line_buffering=True)

GOC = Path(__file__).resolve().parent
THU_MUC = GOC / "GiongViet"
EXE = THU_MUC / "GiongViet.exe"
LOG = THU_MUC / "GiongViet-loi.log"

# Mo hinh nap mat khoang 40 giay; cho rong tay roi moi ket luan.
CHO_CUA_SO = 90
CHO_ON_DINH = 25

loi = 0


def ok(dk, nhan, them=""):
    global loi
    print(f"  {'ĐẠT ' if dk else 'LỆCH'} {nhan}{'  →  ' + str(them) if them else ''}")
    if not dk:
        loi += 1


def tim_cua_so():
    return ctypes.windll.user32.FindWindowW(None, "Giọng Việt")


def khung(hwnd):
    r = wintypes.RECT()
    ctypes.windll.user32.GetWindowRect(hwnd, ctypes.byref(r))
    return r.right - r.left, r.bottom - r.top


def dem(ten_exe):
    try:
        r = subprocess.run(["tasklist", "/FI", f"IMAGENAME eq {ten_exe}", "/NH"],
                           capture_output=True, text=True, timeout=10,
                           creationflags=getattr(subprocess, "CREATE_NO_WINDOW", 0))
        return sum(1 for d in r.stdout.splitlines() if ten_exe.lower() in d.lower())
    except (OSError, subprocess.SubprocessError):
        return -1


def cho_den(dk, gioi_han, nhip=0.5):
    het = time.time() + gioi_han
    while time.time() < het:
        if dk():
            return True
        time.sleep(nhip)
    return False


print("=== KIEM BAN DONG GOI (.exe) ===")
print(f"    {time.strftime('%Y-%m-%d %H:%M:%S')}")
print()

print("--- A. Ban dong goi co day du khong ---")
ok(EXE.exists(), "co GiongViet.exe", f"{EXE.stat().st_size / 1048576:.1f} MB"
   if EXE.exists() else "")
for p, vi_sao in [
    ("_internal/ui-moi/index.html", "thieu thi cua so mo ra trang tron"),
    ("_internal/sea_g2p/sea_g2p.bin", "thieu thi 'os error 2' luc bam doc"),
    ("_internal/vieneu/assets/voices_v3_turbo.json", "thieu thi danh sach giong rong"),
]:
    ok((THU_MUC / p).exists(), f"{p}  ({vi_sao})")
# ffmpeg.exe: thieu no thi ba muc MP3 320 / MP3 128 / WAV 24 bit trong hop
# thoai xuat thanh nut bam khong ra gi. ffplay.exe co khong dam bao ffmpeg.exe
# cung co - hai tep khac nhau trong cung mot thu muc.
for p in ("ffmpeg/bin/ffplay.exe", "ffmpeg/bin/ffmpeg.exe", "vieneu_models"):
    ok((THU_MUC / p).exists(), f"{p} (noi qua junction)")

if loi:
    print("\nBan dong goi thieu tep - dung lai, khong chay thu.")
    sys.exit(1)

# Nhat ky cu de lai se lam sai ket luan "co loi moi khong".
LOG.unlink(missing_ok=True)
truoc_ffplay = dem("ffplay.exe")

print("\n--- B. Chay .exe that ---")
tien_trinh = subprocess.Popen([str(EXE)], cwd=str(THU_MUC))
try:
    ok(cho_den(lambda: tim_cua_so() != 0, CHO_CUA_SO),
       f"cua so hien ra trong vong {CHO_CUA_SO} giay")
    hwnd = tim_cua_so()
    if hwnd:
        r, c = khung(hwnd)
        ok(r > 300 and c > 200, "cua so co kich thuoc that", f"{r}x{c}")

        # Cua so mo len PHAI lap kin vung lam viec. Do bang pixel VAT LY o ca
        # hai ve cho cung don vi - lan truoc so nham logic voi vat ly nen khong
        # thay cua so chi chiem 80% be ngang.
        wa = wintypes.RECT()
        ctypes.windll.user32.SystemParametersInfoW(0x0030, 0, ctypes.byref(wa), 0)
        wr, wc = wa.right - wa.left, wa.bottom - wa.top
        print(f"       vung lam viec (vat ly): {wr}x{wc}")
        ok(r >= wr - 40 and c >= wc - 40,
           "mo len la lap kin vung lam viec", f"{r}x{c} / {wr}x{wc}")

    ok(tien_trinh.poll() is None, "tien trinh con song sau khi dung cua so")

    print(f"       (de yen {CHO_ON_DINH} giay cho mo hinh nap...)")
    time.sleep(CHO_ON_DINH)
    ok(tien_trinh.poll() is None, "van song, khong tu chet giua chung")
    ok(tim_cua_so() != 0, "cua so van con do")

    print("\n--- C. Nhat ky loi ---")
    if LOG.exists():
        noi_dung = LOG.read_text(encoding="utf-8", errors="replace")
        print(noi_dung[-1200:])
        ok(False, "CO loi ghi vao nhat ky", f"{LOG.stat().st_size} byte")
    else:
        ok(True, "KHONG co loi nao duoc ghi ra")
finally:
    print("\n--- D. Thoat co sach khong ---")
    if tien_trinh.poll() is None:
        # WM_CLOSE truoc, y het nguoi dung bam nut dong; het han moi giet.
        hwnd = tim_cua_so()
        if hwnd:
            ctypes.windll.user32.PostMessageW(hwnd, 0x0010, 0, 0)
        try:
            tien_trinh.wait(timeout=25)
        except subprocess.TimeoutExpired:
            tien_trinh.kill()
            ok(False, "KHONG tu thoat sau khi dong cua so - phai giet")
    ok(cho_den(lambda: dem("GiongViet.exe") == 0, 20),
       "khong con tien trinh GiongViet.exe")
    ok(cho_den(lambda: dem("ffplay.exe") <= truoc_ffplay, 20),
       "khong bo lai ffplay nao", dem("ffplay.exe"))

print(f"\n{'XANH — khớp hết' if loi == 0 else f'ĐỎ — {loi} chỗ lệch'}")
sys.exit(1 if loi else 0)
