# -*- coding: utf-8 -*-
"""Kiem am_thanh_loc bang cach CHAY THAT qua ffmpeg roi do ket qua."""
import io, subprocess, sys, tempfile
from pathlib import Path
sys.path.insert(0, r"C:\Projects\DocCongDuc")
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8")
from giaodien_moi import am_thanh_loc as A

FF = Path(r"C:\Projects\DocCongDuc\ffmpeg\bin\ffmpeg.exe")
FP = Path(r"C:\Projects\DocCongDuc\ffmpeg\bin\ffprobe.exe")
T = Path(tempfile.gettempdir()) / "gd-loc"; T.mkdir(exist_ok=True)
GOC = T / "goc.wav"

# 48 kHz dung bang tan so mau that cua VieNeu v3 Turbo
subprocess.run([str(FF), "-hide_banner", "-loglevel", "error", "-y", "-f", "lavfi",
                "-i", "sine=frequency=200:duration=10:sample_rate=48000,tremolo=f=6:d=0.8",
                str(GOC)], check=True)

def do(p):
    d = float(subprocess.run([str(FP), "-v", "error", "-show_entries", "format=duration",
                              "-of", "csv=p=0", str(p)], capture_output=True, text=True).stdout)
    r = subprocess.run([str(FF), "-hide_banner", "-i", str(p), "-af", "volumedetect",
                        "-f", "null", "-"], capture_output=True, text=True).stderr
    v = [l for l in r.splitlines() if "max_volume" in l]
    return d, (v[0].split("max_volume:")[1].strip() if v else "?")

d0, v0 = do(GOC)
print(f"gốc: {d0:.3f} giây · {v0}\n")

loi = 0
def ok(dk, nhan, them=""):
    global loi
    print(f"  {'ĐẠT ' if dk else 'LỆCH'} {nhan}{'  →  ' + str(them) if them else ''}")
    if not dk: loi += 1

print("--- A. Mặc định thì KHÔNG thêm bộ lọc nào ---")
ok(A.chuoi_loc(A.MAC_DINH) == "", "mặc định → chuỗi rỗng", repr(A.chuoi_loc(A.MAC_DINH)))
lenh = ["ffplay", "-i", "pipe:0"]
ok(A.them_vao_lenh(lenh, A.MAC_DINH) == lenh, "lệnh giữ nguyên, không thêm -af")

print("\n--- B. Chạy thật từng cấu hình rồi đo ---")
BO = [
  ({"tocDo": 0,   "caoDo": 0,  "amLuong": 100}, 10.00, "mặc định"),
  ({"tocDo": 10,  "caoDo": 0,  "amLuong": 100},  9.09, "Tốc độ +10% (hồ sơ Thông báo ngắn)"),
  ({"tocDo": -10, "caoDo": 0,  "amLuong": 90},  11.11, "Tốc độ −10% + Âm lượng 90% (Sách nói)"),
  ({"tocDo": -50, "caoDo": 0,  "amLuong": 100}, 20.00, "Tốc độ hết cỡ chậm"),
  ({"tocDo": 100, "caoDo": 0,  "amLuong": 100},  5.00, "Tốc độ hết cỡ nhanh"),
  ({"tocDo": 0,   "caoDo": 2,  "amLuong": 100}, 10.00, "Cao độ +2 (độ dài PHẢI giữ nguyên)"),
  ({"tocDo": 0,   "caoDo": -12,"amLuong": 100}, 10.00, "Cao độ hết cỡ trầm"),
  ({"tocDo": 0,   "caoDo": 12, "amLuong": 100}, 10.00, "Cao độ hết cỡ cao"),
  ({"tocDo": 20,  "caoDo": -3, "amLuong": 50},   8.33, "cả ba cùng lúc"),
]
for chinh, mong, nhan in BO:
    s = A.chuoi_loc(chinh)
    ra = T / f"r{abs(hash(str(chinh)))%10000}.wav"
    cmd = A.them_vao_lenh([str(FF), "-hide_banner", "-loglevel", "error", "-y",
                           "-i", str(GOC)], chinh) + [str(ra)]
    subprocess.run(cmd, check=True)
    d, v = do(ra)
    ok(abs(d - mong) < 0.06, f"{nhan}", f"{d:.3f} giây (mong {mong:.2f}) · {v} · -af \"{s}\"")

print("\n--- C. Âm lượng đúng decibel lý thuyết ---")
import math
for am in (90, 50, 25):
    ra = T / f"v{am}.wav"
    subprocess.run(A.them_vao_lenh([str(FF), "-hide_banner", "-loglevel", "error", "-y",
                                    "-i", str(GOC)], {"tocDo":0,"caoDo":0,"amLuong":am})
                   + [str(ra)], check=True)
    d, v = do(ra)
    thuc = float(v.replace(" dB","")) - float(v0.replace(" dB",""))
    ly = 20 * math.log10(am/100)
    ok(abs(thuc - ly) < 0.15, f"Âm lượng {am}%", f"{thuc:+.2f} dB (lý thuyết {ly:+.2f})")

print("\n--- D. Ép biên, không cho vượt khoảng của đặc tả ---")
ok(A.he_so_tempo(999) == 2.0, "tốc độ vượt trần bị ép về 2.0", A.he_so_tempo(999))
ok(A.he_so_tempo(-999) == 0.5, "tốc độ dưới sàn bị ép về 0.5", A.he_so_tempo(-999))
ok(abs(A.he_so_pitch(99) - 2.0) < 1e-9, "cao độ vượt trần ép về +12 nửa cung")
ok(A.chuoi_loc({"tocDo":0,"caoDo":0,"amLuong":500}) == "", "âm lượng >100% bị ép về 100 (không khuếch đại)")

print("\n--- E. Dòng tóm tắt ở cột phải ---")
ok(A.mo_ta({"tocDo":-10,"caoDo":0,"amLuong":90}) == "Tốc độ −10% · Âm lượng 90%",
   "hồ sơ Sách nói", A.mo_ta({"tocDo":-10,"caoDo":0,"amLuong":90}))
ok(A.mo_ta(A.MAC_DINH) == "Theo mặc định của hồ sơ", "mặc định")

print(f"\n{'XANH — khớp hết' if loi == 0 else f'ĐỎ — {loi} chỗ lệch'}")
sys.exit(1 if loi else 0)
