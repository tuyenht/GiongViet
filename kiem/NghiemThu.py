# -*- coding: utf-8 -*-
"""Nghiem thu ban .exe — MAY do duoc gi thi may do, con lai moi huong dan tay.

Chay:  py kiem\\NghiemThu.py

Bai nay KHONG bam nut ho duoc: noi dung nam trong WebView2, tu ben ngoai
khong voi vao duoc. Nhung phan lon thu can biet thi van do duoc tu ben ngoai,
va do duoc thi khong phai tin vao cam giac:

  · Cua so hien ra chua, to bao nhieu            -> FindWindowW + GetWindowRect
  · Keo mep co an khong                          -> do kich thuoc truoc/sau
  · Ba thanh chinh co that su tac dong khong     -> DOC DONG LENH cua ffplay
                                                    dang chay, tim chuoi "-af"
  · Mot nguon phat tieng tai mot thoi diem       -> dem tien trinh ffplay
  · Xuat file co ra tep that khong               -> theo doi thu muc, do thoi
                                                    luong WAV bang module wave
  · Co ghi ban du lieu nguoi dung khong          -> so mtime + kich thuoc
  · Co loi nao khong                             -> doc nhat ky
  · Thoat co sach khong                          -> dem tien trinh con lai

Thu duy nhat may khong thay duoc anh: NGHE xem tieng co dung khong.
"""
import ctypes
import io
import subprocess
import sys
import time
import wave
from ctypes import wintypes
from pathlib import Path

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8",
                              line_buffering=True)

GOC = Path(__file__).resolve().parent.parent
THU_MUC = GOC / "GiongViet"
EXE = THU_MUC / "GiongViet.exe"
LOG = THU_MUC / "GiongViet-loi.log"
TEN_CUA_SO = "Giọng Việt"
THU_MUC_XUAT = Path.home() / "Documents" / "GiongViet"

DU_LIEU = ["congduc.txt", "cauhinh.ini", "noidung.ini", "tudien.ini",
           "hoso.json", "hoso-v2.json", "giaodien.json"]

dat = lech = 0


def ok(dk, nhan, them=""):
    global dat, lech
    print(f"    {'ĐẠT ' if dk else 'LỆCH'} {nhan}{'  →  ' + str(them) if them else ''}")
    if dk:
        dat += 1
    else:
        lech += 1


def cho(chu):
    """Dung lai cho nguoi dung lam mot viec roi bam Enter."""
    print(f"\n>>> {chu}")
    try:
        input("    (làm xong thì bấm Enter)")
    except EOFError:
        print("    (không có bàn phím — bỏ qua bước này)")


def hwnd():
    return ctypes.windll.user32.FindWindowW(None, TEN_CUA_SO)


def co_cua_so(h):
    r = wintypes.RECT()
    ctypes.windll.user32.GetWindowRect(h, ctypes.byref(r))
    return r.right - r.left, r.bottom - r.top


def dong_lenh(ten_exe):
    """Dong lenh day du cua cac tien trinh dang chay mang ten nay.

    Day la mau chot: no cho biet ffplay duoc goi VOI THAM SO GI. Thay "-af"
    trong do la bang chung ba thanh chinh that su tac dong den tieng - khong
    can nghe, khong can tin vao cam giac.
    """
    try:
        r = subprocess.run(
            ["powershell", "-NoProfile", "-Command",
             f"Get-CimInstance Win32_Process -Filter \"name='{ten_exe}'\""
             " | Select-Object -ExpandProperty CommandLine"],
            capture_output=True, text=True, timeout=20,
            creationflags=getattr(subprocess, "CREATE_NO_WINDOW", 0))
        return [d.strip() for d in r.stdout.splitlines() if d.strip()]
    except (OSError, subprocess.SubprocessError):
        return []


def dem(ten_exe):
    try:
        r = subprocess.run(["tasklist", "/FI", f"IMAGENAME eq {ten_exe}", "/NH"],
                           capture_output=True, text=True, timeout=10,
                           creationflags=getattr(subprocess, "CREATE_NO_WINDOW", 0))
        return sum(1 for d in r.stdout.splitlines() if ten_exe.lower() in d.lower())
    except (OSError, subprocess.SubprocessError):
        return -1


def moc_du_lieu():
    m = {}
    for t in DU_LIEU:
        p = GOC / t
        m[t] = (p.stat().st_mtime_ns, p.stat().st_size) if p.exists() else None
    return m


def tep_trong(thu_muc):
    if not thu_muc.exists():
        return {}
    return {p.name: p.stat().st_size for p in thu_muc.rglob("*") if p.is_file()}


# ═══════════════════════════════════════════════════════ A. TU DONG HOAN TOAN

print("=" * 62)
print("  NGHIEM THU BAN .EXE — Giọng Việt")
print("=" * 62)

print("\n--- A. Ban dong goi (tu dong) ---")
ok(EXE.exists(), "co GiongViet.exe",
   f"{EXE.stat().st_size / 1048576:.1f} MB" if EXE.exists() else "KHONG CO")
if not EXE.exists():
    print("\nChua co ban .exe. Chay truoc:  set GIONGDOC_TU_DONG=1 && DongGoi.bat")
    sys.exit(1)
for p, vi_sao in [
    ("_internal/ui-moi/index.html", "thieu thi cua so mo ra trang tron"),
    ("_internal/sea_g2p/sea_g2p.bin", "thieu thi 'os error 2' luc bam doc"),
    ("_internal/vieneu/assets/voices_v3_turbo.json", "thieu thi danh sach giong rong"),
    ("ffmpeg/bin/ffplay.exe", "thieu thi khong phat duoc tieng"),
    ("ffmpeg/bin/ffmpeg.exe", "thieu thi hong MP3, WAV 24 bit va ba thanh chinh"),
    ("vieneu_models", "thieu thi khong tong hop duoc"),
]:
    ok((THU_MUC / p).exists(), f"{p}", vi_sao if not (THU_MUC / p).exists() else "")

moc = moc_du_lieu()
truoc_ffplay = dem("ffplay.exe")
truoc_xuat = tep_trong(THU_MUC_XUAT)
LOG.unlink(missing_ok=True)

print("\n--- B. Mo chuong trinh (tu dong) ---")
tt = subprocess.Popen([str(EXE)], cwd=str(THU_MUC))
het = time.time() + 90
while time.time() < het and not hwnd():
    time.sleep(0.5)
h = hwnd()
ok(h != 0, "cua so hien ra trong 90 giay")
if not h:
    tt.kill()
    sys.exit(1)
r0, c0 = co_cua_so(h)
ok(r0 > 300 and c0 > 200, "cua so co kich thuoc that", f"{r0}x{c0}")
print("       (đợi 25 giây cho mô hình nạp xong...)")
time.sleep(25)
ok(tt.poll() is None, "van song sau khi nap mo hinh")

# ═══════════════════════════════════════════════ C. BAN TU DONG — anh bam, may do

print("\n" + "=" * 62)
print("  PHAN CAN ANH BAM. May se tu do sau moi buoc.")
print("=" * 62)

print("\n--- C1. Keo mep cua so ---")
cho("Kéo thử 4 cạnh và 4 góc cửa sổ cho nó ĐỔI KÍCH THƯỚC rõ rệt.")
h = hwnd()
if h:
    r1, c1 = co_cua_so(h)
    ok((r1, c1) != (r0, c0), "kich thuoc cua so DA DOI -> keo mep an",
       f"{r0}x{c0} → {r1}x{c1}")
else:
    ok(False, "khong tim thay cua so nua")

print("\n--- C2. Ba thanh chinh Toc do / Cao do / Am luong ---")
cho("Kéo thanh TỐC ĐỘ sang phải hết cỡ, rồi bấm Nghe toàn bộ.\n"
    "    Để tiếng chạy vài giây RỒI MỚI bấm Enter (đừng dừng).")
lenh = dong_lenh("ffplay.exe")
ok(len(lenh) >= 1, "co tien trinh ffplay dang phat", f"{len(lenh)} tien trinh")
ok(len(lenh) <= 1, "CHI MOT nguon phat tieng cung luc", f"{len(lenh)} tien trinh")
co_af = any("-af" in d for d in lenh)
ok(co_af, "lenh ffplay CO chua -af  ->  ba thanh chinh that su tac dong",
   next((d[d.find("-af"):d.find("-af") + 46] for d in lenh if "-af" in d), "khong thay"))
if not co_af and lenh:
    print("       (nếu anh chưa kéo thanh nào thì KHÔNG có -af là đúng)")

print("\n--- C3. Xuat file ---")
cho("Bấm Xuất file âm thanh → chọn MP3 128 kbps → Bắt đầu xuất.\n"
    "    Xem hộp có sang giai đoạn 2 (vòng xoay + phần trăm) không.\n"
    "    Đợi xuất XONG rồi bấm Enter.")
sau_xuat = tep_trong(THU_MUC_XUAT)
moi = {k: v for k, v in sau_xuat.items() if k not in truoc_xuat}
ok(bool(moi), "co tep MOI trong thu muc xuat", list(moi)[:3] or "khong co tep nao")
for ten, co in list(moi.items())[:3]:
    ok(co > 1000, f"  {ten} co noi dung", f"{co:,} byte")
    if ten.lower().endswith(".mp3"):
        dau = (THU_MUC_XUAT / ten).read_bytes()[:3]
        ok(dau in (b"ID3", b"\xff\xfb", b"\xff\xf3"), f"  {ten} dung dinh dang MP3")
    if ten.lower().endswith(".wav"):
        try:
            with wave.open(str(THU_MUC_XUAT / ten), "rb") as w:
                ok(w.getnframes() > 0, f"  {ten} la WAV hop le",
                   f"{w.getnframes() / w.getframerate():.1f} giay")
        except Exception as e:
            ok(False, f"  {ten} KHONG doc duoc bang module wave", e)
ok(not list(THU_MUC_XUAT.glob("*.dangxuat")) if THU_MUC_XUAT.exists() else True,
   "khong bo lai tep .dangxuat nao")

print("\n--- C4. Huy giua chung ---")
cho("Xuất lần nữa, nhưng BẤM HUỶ XUẤT khi phần trăm đang chạy.")
if THU_MUC_XUAT.exists():
    ok(not list(THU_MUC_XUAT.glob("*.dangxuat")),
       "huy xong khong bo lai tep do dang",
       [p.name for p in THU_MUC_XUAT.glob("*.dangxuat")] or "sach")

print("\n--- C5. Menu ---")
cho("Mở cả 5 menu. Bấm thử: Lưu · Cỡ chữ lớn hơn · Thẻ cảm xúc ·\n"
    "    Hướng dẫn nhanh. Xem có mục nào bấm vào KHÔNG RA GÌ không.")
print("       (bước này chỉ mắt anh thấy được — máy ghi nhận qua nhật ký lỗi ở phần D)")

print("\n--- C6. Bon man phu ---")
cho("Mở Soát văn bản · Thư viện giọng · Từ điển phát âm · Cài đặt,\n"
    "    rồi quay lại màn hình chính.")

# ═══════════════════════════════════════════════════════ D. TU DONG — ket luan

print("\n" + "=" * 62)
print("  D. May tu ket luan")
print("=" * 62)

print("\n--- D1. Nhat ky loi ---")
if LOG.exists():
    noi = LOG.read_text(encoding="utf-8", errors="replace")
    print(noi[-1500:])
    ok(False, "CO loi ghi vao nhat ky", f"{LOG.stat().st_size} byte")
else:
    ok(True, "KHONG co loi nao duoc ghi ra")

print("\n--- D2. Du lieu nguoi dung con nguyen khong ---")
sau = moc_du_lieu()
doi = [t for t in DU_LIEU if moc.get(t) != sau.get(t)]
# cauhinh/hoso/giaodien.json doi la BINH THUONG neu anh co chinh thiet lap
nang = [t for t in doi if t in ("congduc.txt", "noidung.ini")]
ok(not nang, "tep du lieu GOC khong bi dung toi", nang or "nguyen ven")
if doi:
    print(f"       (có đổi: {', '.join(doi)} — bình thường nếu anh vừa chỉnh thiết lập)")

print("\n--- D3. Thoat co sach khong ---")
cho("ĐÓNG cửa sổ chương trình (bấm nút X).")
time.sleep(3)
ok(dem("GiongViet.exe") == 0, "khong con tien trinh GiongViet.exe",
   dem("GiongViet.exe"))
ok(dem("ffplay.exe") <= truoc_ffplay, "khong bo lai ffplay nao",
   f"{dem('ffplay.exe')} (truoc khi chay: {truoc_ffplay})")
if tt.poll() is None:
    tt.kill()
    ok(False, "phai giet bang tay — khong tu thoat")

print("\n" + "=" * 62)
print(f"  KET QUA: {dat} dat · {lech} lech")
print("=" * 62)
print("\nMay KHONG kiem duoc (chi tai anh):")
print("  · Tieng doc co dung va de nghe khong")
print("  · Chu chay co khop voi tieng khong")
print("  · Keo Toc do len thi tieng co NHANH HON that khong")
sys.exit(1 if lech else 0)
