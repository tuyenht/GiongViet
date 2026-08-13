# -*- coding: utf-8 -*-
"""Canh ba thanh Toc do / Cao do / Am luong CO THAT SU doi tieng.

VI SAO CO TEP NAY: am_thanh_loc.py viet xong tu 12/8, do so lieu that, 20 phep
kiem xanh — nhung KHONG AI GOI no. Ca thang troi ba thanh truot ay chi ghi con
so xuong hoso-v2.json roi thoi; keo het co sang phai tieng van y nguyen. Bo
kiem cua rieng am_thanh_loc xanh khong cuu duoc gi, vi no chi kiem ham dung
chuoi -af cho dung, khong kiem co ai dung chuoi ay khong.

Nen bai nay di theo CA DUONG DAY: giao dien -> ApiMoi -> bo_doc/nghe_thu ->
lenh ffplay, va xuat file. Phan cuoi xuat mot tep that bang ffmpeg that roi
DO THOI LUONG: keo toc do len thi tep phai NGAN LAI. Do la bang chung khong
cai xoa duoc.
"""
import io
import re
import subprocess
import sys
import shutil
import tempfile
import wave
from pathlib import Path


# Goc du an, tinh tu chinh vi tri tep nay. KHONG viet cung duong dan:
# kho da len GitHub, ai tai ve cho khac la vo het bo kiem.
_GOC = str(Path(__file__).resolve().parent.parent)
sys.path.insert(0, _GOC)
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8")

from giaodien_moi import am_thanh_loc as A

G = Path(_GOC)
loi = 0
def ok(dk, nhan, them=""):
    global loi
    print(f"  {'ĐẠT ' if dk else 'LỆCH'} {nhan}{'  →  ' + str(them) if them else ''}")
    if not dk:
        loi += 1


MAC_DINH = {"tocDo": 0, "caoDo": 0, "amLuong": 100}

print("--- A. Khong chinh gi thi KHONG chen bo loc nao ---")
ok(A.chuoi_loc(MAC_DINH) == "", "ho so mac dinh -> chuoi rong",
   repr(A.chuoi_loc(MAC_DINH)))
ok(A.chuoi_loc({}) == "", "thieu khoa -> van rong")
lenh_goc = ["ffplay", "-i", "pipe:0"]
ok(A.them_vao_lenh(lenh_goc, MAC_DINH) == lenh_goc,
   "lenh ffplay giu nguyen tung chu — ban cu khong doi hanh vi")

print("\n--- B. Chinh roi thi co bo loc that ---")
nhanh = A.chuoi_loc({**MAC_DINH, "tocDo": 50})
ok("atempo" in nhanh, "keo Toc do -> co atempo", nhanh)
cao = A.chuoi_loc({**MAC_DINH, "caoDo": 50})
ok("rubberband" in cao or "pitch" in cao, "keo Cao do -> co doi cao do", cao)
# Thang am luong la 0..100 (chi giam, khong khuech dai). Lay 200 la bi ep ve
# 100 = mac dinh -> khong sinh bo loc nao, va phep kiem bao lech oan.
nho = A.chuoi_loc({**MAC_DINH, "amLuong": 60})
ok("volume" in nho, "keo Am luong -> co volume", nho)
ok(A.chuoi_loc({**MAC_DINH, "amLuong": 200}) == "",
   "amLuong vuot bien bi ep ve mac dinh, khong sinh bo loc thua")

print("\n--- C. Engine: Speaker.play PHAI nhan bo loc va chen -af ---")
e = (G / "DocCongDuc.py").read_text(encoding="utf-8")
than = e[e.find("def play(self, audio"):]
than = than[:than.find("\n    def ", 10)]
chu_ky = than[:than.find('"""')]

def bo_docstring(s):
    """Cat docstring ra truoc khi soi THU TU cac lenh.

    Docstring cua play() nhac "-af" ngay o cau giai thich, tuc la truoc cho
    dat no that. Doc ca van xuoi vao thi phep kiem bao lech trong khi code
    dung - da bao lech that mot lan, y het cai bay o kiem_cua_so.py.
    """
    d = s.find('"""')
    c = s.find('"""', d + 3)
    return s[:d] + s[c + 3:] if 0 <= d < c else s

than_ma = bo_docstring(than)
ok("loc: str" in chu_ky, "play() co tham so loc")
ok('loc: str = ""' in chu_ky, "mac dinh RONG — moi noi goi cu khong doi")
ok(re.search(r'if loc:\s*\n\s*lenh \+= \["-af", loc\]', than_ma) is not None,
   "chen -af vao lenh khi co bo loc")
ok(than_ma.find("-af") > than_ma.find("pipe:0"),
   "-af dat sau -i, dung thu tu ffplay doi")

print("\n--- D. Duong day: ba noi phat tieng deu phai nhan bo loc ---")
bd = (G / "giaodien" / "bo_doc.py").read_text(encoding="utf-8")
ok("self.loc_am" in bd, "bo_doc giu loc_am")
ok(re.search(r"speaker\.play\([^)]*self\.loc_am", bd) is not None,
   "bo_doc TRUYEN loc_am vao play — day la cho tung bi bo quen")
nt = (G / "giaodien" / "nghe_thu.py").read_text(encoding="utf-8")
ok(re.search(r"def phat\([^)]*loc", nt) is not None, "nghe_thu.phat nhan loc")
# KHONG dung [^)]* o day: doi so co ngoac long (threading.Event()), lop ky tu
# ay dung ngay o dau ngoac dong dau tien va bao lech oan. Dung .*? + DOTALL.
ok(re.search(r"speaker\.play\(.*?loc\)", nt, re.S) is not None,
   "nghe_thu truyen loc xuong play")
cn = (G / "giaodien_moi" / "cau_noi_moi.py").read_text(encoding="utf-8")
ok("def moi_dat_chinh_am" in cn, "ApiMoi co cua nhan ba thanh tu giao dien")
ok("self._bo_doc.loc_am = self._loc_am" in cn, "ApiMoi day bo loc xuong bo_doc")
ok(re.search(r"_bo_nghe_thu\.phat\(.*?self\._loc_am", cn, re.S) is not None,
   "nghe thu dung dung bo loc dang chinh")
ok("am_thanh_loc" in cn, "cau_noi_moi CO import am_thanh_loc")

print("\n--- E. Giao dien phai goi sang, khong thi ba thanh van chet ---")
js = (G / "ui-moi" / "giao-dien.js").read_text(encoding="utf-8")
ok("moi_dat_chinh_am" in js, "JS co goi moi_dat_chinh_am")
ok("guiChinhAm()" in js.replace("function guiChinhAm()", ""),
   "guiChinhAm CO duoc goi, khong chi dinh nghia")
ok(re.search(r"const dat = .*guiChinhAm\(\)", js) is not None,
   "gan vao dat() nen moi duong doi ho so/keo thanh deu bao duoc")

print("\n--- F. Xuat file cung phai ap bo loc ---")
xm = (G / "giaodien_moi" / "xuat_moi.py").read_text(encoding="utf-8")
ok(re.search(r"def bat_dau\(.*?loc", xm, re.S) is not None, "bat_dau nhan loc")
ok('["-af", loc]' in xm, "co chen -af khi xuat")
ok(re.search(r"self\._bo_xuat_moi\.bat_dau\(.*?self\._loc_am", cn, re.S) is not None,
   "ApiMoi truyen bo loc sang bo xuat")

print("\n--- G. DO THAT: keo toc do len thi tep xuat NGAN LAI ---")
ff = G / "ffmpeg" / "bin" / "ffmpeg.exe"
if not ff.exists():
    print("  BO QUA — khong co ffmpeg")
else:
    T = Path(tempfile.gettempdir()) / "gd-kiem-chinh-am"
    if T.exists():
        shutil.rmtree(T)
    T.mkdir(parents=True)
    goc = T / "goc.wav"
    with wave.open(str(goc), "wb") as w:
        w.setnchannels(1); w.setsampwidth(2); w.setframerate(48000)
        w.writeframes(b"\0\0" * 48000 * 4)          # 4,000 giay

    def do_dai(p):
        with wave.open(str(p), "rb") as r:
            return r.getnframes() / r.getframerate()

    ok(abs(do_dai(goc) - 4.0) < 0.01, "tep goc dung 4 giay", do_dai(goc))
    for nhan, chinh, mong in [("Toc do +50", {**MAC_DINH, "tocDo": 50}, "ngan hon"),
                              ("Toc do -50", {**MAC_DINH, "tocDo": -50}, "dai hon")]:
        loc = A.chuoi_loc(chinh)
        ra = T / (nhan.replace(" ", "_").replace("+", "p") + ".wav")
        subprocess.run([str(ff), "-y", "-loglevel", "error", "-i", str(goc),
                        "-af", loc, str(ra)], check=True,
                       creationflags=0x08000000)
        d = do_dai(ra)
        dung = d < 3.9 if mong == "ngan hon" else d > 4.1
        ok(dung, f"{nhan} -> tep {mong} that su", f"{d:.3f}s (goc 4,000s)")

    # Am luong CHI GIAM, khong khuech dai (0-100) - day quá đỉnh la re, nhat
    # la loa ngoai troi o chua. Nen lay 50%, khong lay 200%.
    loc_nho = A.chuoi_loc({**MAC_DINH, "amLuong": 50})
    ok(loc_nho != "", "amLuong 50% co sinh bo loc", repr(loc_nho))
    ra = T / "nho.wav"
    subprocess.run([str(ff), "-y", "-loglevel", "error", "-i", str(goc),
                    "-af", loc_nho, str(ra)], check=True, creationflags=0x08000000)
    ok(abs(do_dai(ra) - 4.0) < 0.05,
       "Am luong doi thi do dai GIU NGUYEN", f"{do_dai(ra):.3f}s")
    ok(A.chuoi_loc({**MAC_DINH, "amLuong": 100}) == "",
       "am luong 100% = mac dinh -> khong chen bo loc thua")
    shutil.rmtree(T, ignore_errors=True)

print("\n" + ("XANH — khớp hết" if not loi else f"ĐỎ — {loi} chỗ lệch"))
sys.exit(1 if loi else 0)
