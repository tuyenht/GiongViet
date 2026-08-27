# -*- coding: utf-8 -*-
"""Kiem che do doc DANH SACH TEN VA SO — chuc nang goc cua chuong trinh.

Chay tren ApiMoi that, khong phat tieng, khong cham du lieu that (dung tep
danh sach TAM chu khong dung congduc.txt cua chu du an).
"""
import io
import sys
import tempfile
from pathlib import Path

# Goc du an, tinh tu chinh vi tri tep nay. KHONG viet cung duong dan:
# kho da len GitHub, ai tai ve cho khac la vo het bo kiem.
_GOC = str(Path(__file__).resolve().parent.parent)
sys.path.insert(0, _GOC)
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8",
                              line_buffering=True)

from giaodien import nhat_ky
nhat_ky.TEP_LOG = Path(tempfile.gettempdir()) / "gd-kiem-loi.log"

from giaodien_moi import khoa_du_lieu  # noqa: E402
from giaodien_moi.cau_noi_moi import ApiMoi  # noqa: E402

loi = 0


def ok(dk, nhan, them=""):
    global loi
    print(f"  {'ĐẠT ' if dk else 'LỆCH'} {nhan}{'  →  ' + str(them) if them else ''}")
    if not dk:
        loi += 1


T = Path(tempfile.gettempdir()) / "gd-kiem-danhsach"
T.mkdir(parents=True, exist_ok=True)
TEP = T / "danhsach-thu.txt"
TEP.write_text(
    "DANH SÁCH ỦNG HỘ ĐỢT MỘT\n"
    "Nguyễn Văn An\t500.000\n"
    "Trần Thị Bình\t1.200.000\n"
    "Lê Văn Cường\t200000\n"
    "DANH SÁCH ĐỢT HAI\n"
    "Phạm Thị Dung\t50.000\n",
    encoding="utf-8")

khoa_du_lieu.khoa()
api = ApiMoi()

print("--- A. Mo duoc tep danh sach ---")
kq = api.moi_doc_danh_sach(TEP)
ok(not kq.get("loi"), "khong loi", kq.get("loi", ""))
ok(kq["loai"] == "congduc", "bao dung loai tai lieu", kq["loai"])
ok(kq["soNguoi"] == 4, "dem dung 4 nguoi (khong tinh 2 dong tieu de)",
   kq["soNguoi"])

print("\n--- B. Chu HIEN THI la ten + so tien nhu trong tep ---")
doan = kq["doan"]
nguoi = [d for d in doan if d["kieu"] == "body"]
ok(len(nguoi) == 4, "4 dong nguoi", len(nguoi))
ok("Nguyễn Văn An" in nguoi[0]["chu"], "co ten", nguoi[0]["chu"])
ok("500.000" in nguoi[0]["chu"],
   "co so tien dang NHIN THAY, khong phai chu doc", nguoi[0]["chu"])
ok("năm trăm nghìn" not in nguoi[0]["chu"].lower(),
   "KHONG hien cau engine doc - nguoi dung dang do theo danh sach cua ho")

print("\n--- C. Cau engine DOC thi lai dung mau cau, doc so thanh chu ---")
mau_nguoi = [s for s in api._playlist if s.get("loai") == "nguoi"]
ok(len(mau_nguoi) == 4, "4 mau nguoi trong playlist", len(mau_nguoi))
doc1 = mau_nguoi[0]["text"].lower()
ok("nghìn" in doc1 or "trăm" in doc1, "so tien doc thanh chu", mau_nguoi[0]["text"])

print("\n--- D. Loi dan cua ho so duoc chen vao ---")
loai_mau = [s.get("loai") for s in api._playlist]
ok("tieude" in loai_mau, "dong tieu de trong tep thanh mau rieng", set(loai_mau))
ok(len(api._playlist) > 4, "playlist nhieu hon so nguoi (co loi dan/tieu de)",
   len(api._playlist))

print("\n--- E. Moi mau ung voi dung MOT doan hien thi ---")
ok(len(api._doan) == len(api._playlist), "so doan = so mau",
   f"{len(api._doan)} / {len(api._playlist)}")
ok(api._doan_cua_mau == list(range(1, len(api._playlist) + 1)),
   "anh xa mau -> doan la mot doi mot")

print("\n--- F. Nap van ban thuong thi tro lai che do cu ---")
api.moi_dat_doan([{"kieu": "body", "chu": "Một câu văn bản thường."}])
ok(api._loai_tai_lieu == "vanban", "loai tai lieu tro ve vanban",
   api._loai_tai_lieu)
ok(not api._records, "quen danh sach cu di")

print("\n--- G. Tep hong / rong thi bao ro, khong lam vo gi ---")
rong = T / "rong.txt"
rong.write_text("", encoding="utf-8")
ok("loi" in api.moi_doc_danh_sach(rong), "tep rong -> bao loi")
ok("loi" in api.moi_doc_danh_sach(T / "khong-co-that.txt"),
   "tep khong ton tai -> bao loi")

print("\n--- H. So tien may khong hieu thi canh bao chu khong bo qua ---")
la = T / "la.txt"
la.write_text("Nguyễn Văn X\tmột ít\nTrần Thị Y\t300.000\n", encoding="utf-8")
kq2 = api.moi_doc_danh_sach(la)
ok(not kq2.get("loi"), "van mo duoc")
ok(len(kq2["canhBao"]) >= 1, "co canh bao ve dong khong hieu so tien",
   kq2["canhBao"][:1])

api._huy_hen_nap_truoc()
api._don_dep()
import shutil

shutil.rmtree(T, ignore_errors=True)
print(f"\n{'XANH — khớp hết' if loi == 0 else f'ĐỎ — {loi} chỗ lệch'}")
sys.exit(1 if loi else 0)
