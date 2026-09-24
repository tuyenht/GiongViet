# -*- coding: utf-8 -*-
"""BAI CANH (xanh = tot): bo chuan hoa dia danh KHONG duoc doi ten nguoi.

VI SAO CO BAI NAY

Ca dung goc cua chuong trinh la doc DANH SACH CONG DUC o chua - day ten nguoi
that. Ma ten dem viet tat mot chu cai ("Le Q. Anh", "Co giao P. Huong") la dang
pho bien nhat trong danh sach ay.

Bo chuan hoa dia danh (bo_dieu_phoi_ngu_canh.py) co cac quy tac doi viet tat
hanh chinh: "Q." -> "Quan", "P." -> "Phuong", "H." -> "Huyen". Chung khong tu
phan biet duoc dia danh voi ten dem, nen tung doi that (do ngay 08/09/2026,
4/9 dong hong):

    "Co giao P. Huong ung ho 500.000"  ->  "Co giao PHUONG Huong ..."
    "Ba H. Lan phat tam 200.000"       ->  "Ba HUYEN Lan ..."
    "Le Q. Anh cung duong"             ->  "Le QUAN Anh ..."
    "Ba Le Thi Q 12 cong duc"          ->  "Ba Le Thi QUAN 12 ..."

May doc to ten nguoi sai giua buoi le, va khong co cong tac nao tat duoc.

Ban va: _la_ten_nguoi() xet cum chu NGAY TRUOC vi tri doi - co danh xung
(ong/ba/co/thay/phat tu...) hay ho nguoi Viet (Nguyen/Tran/Le...) thi giu
nguyen. Cum tinh tu dau ngat gan nhat, nen dia chi that trong cung mot cau
van doi binh thuong: "Nha ba Nguyen Thi Hoa, P. 5, Q. 3".

Bai chi goi ham thuan van ban. KHONG nap mo hinh, KHONG sinh am thanh,
KHONG cham mot byte du lieu nguoi dung.
"""
import io
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")

from src.core.bo_dieu_phoi_ngu_canh import dieu_phoi_ngu_canh

loi = 0


def ok(dieu_kien, nhan, them=""):
    global loi
    print(f"  {'ĐẠT ' if dieu_kien else 'LỆCH'} {nhan}" + (f"  →  {them}" if them else ""))
    if not dieu_kien:
        loi += 1


print("--- A. Tên người viết tắt phải GIỮ NGUYÊN ---")
TEN_NGUOI = [
    "Cô giáo P. Hương ủng hộ 500.000",
    "Bà H. Lan phát tâm 200.000",
    "Lê Q. Anh cúng dường 1.000.000",
    "Bà Lê Thị Q 12 công đức 300.000",
    "Ông Nguyễn P. Thảo 700.000",
    "Gia đình bà H. Nga 1.500.000",
    "Phật tử Trần Q. Dũng 250.000",
    "Cụ P. Tâm 100.000",
    "Đạo hữu Vũ H. Sơn 400.000",
]
for s in TEN_NGUOI:
    ra = dieu_phoi_ngu_canh(s)
    ok(ra == s, f"giữ nguyên: {s[:44]}", "" if ra == s else f"BỊ ĐỔI THÀNH: {ra}")

print("\n--- B. Địa chỉ thật vẫn phải ĐƯỢC CHUYỂN ---")
DIA_CHI = [
    ("Số 5, P. 12, Q. Tân Bình", ("Phường 12", "Quận Tân Bình")),
    ("Nhà bà Nguyễn Thị Hoa, P. 5, Q. 3", ("Phường 5", "Quận 3")),
    ("Xã Tân Túc, H. Bình Chánh", ("Huyện Bình Chánh",)),
    ("Địa chỉ: Q1, TP.HCM", ("Quận 1", "Thành phố Hồ Chí Minh")),
]
for s, mong_doi in DIA_CHI:
    ra = dieu_phoi_ngu_canh(s)
    thieu = [m for m in mong_doi if m not in ra]
    ok(not thieu, f"chuyển đúng: {s[:44]}", "" if not thieu else f"thiếu {thieu} → {ra}")

print("\n--- C. Viết tắt nhiều chữ không nhập nhằng với tên, phải chuyển ---")
for s, mong in (("TP.HCM", "Thành phố Hồ Chí Minh"),
                ("TX. Dĩ An", "Thị xã"),
                ("TT. Củ Chi", "Thị trấn")):
    ra = dieu_phoi_ngu_canh(s)
    ok(mong in ra, f"{s} → {mong}", ra)

print("\n--- C2. QUA ĐƯỜNG ĐỌC THẬT (chuan_hoa_van_ban), không chỉ hàm con ---")
# Có HAI bảng quy tắc địa danh làm cùng một việc: PAT_DIA_CHI ở module này và
# KY_HIEU_SOM trong DocCongDuc.py. Vá một bên xong mà bên kia còn nguyên thì
# tên người vẫn bị đổi trên đường đọc thật — đã xảy ra đúng như vậy.
import DocCongDuc as _engine
_cfg = {"doc_tien": True, "doc_so": True}
for chu, mong in (("Cô giáo P. Hương", "Cô giáo P. Hương"),
                  ("Bà H. Lan", "Bà H. Lan"),
                  ("Lê Q. Anh", "Lê Q. Anh"),
                  ("Số 5, P. 12, Q. Tân Bình", "Số 5, Phường 12, Quận Tân Bình"),
                  ("Xã Tân Túc, H. Bình Chánh", "Xã Tân Túc, Huyện Bình Chánh")):
    ra = _engine.chuan_hoa_van_ban(chu, {}, _cfg).rstrip(".")
    ok(ra == mong.rstrip("."), f"đường thật: {chu[:40]}",
       "" if ra == mong.rstrip(".") else f"RA “{ra}”")

print("\n--- D. Tên viết HOA TOÀN BỘ (bảng Excel hay xuất kiểu này) ---")
# Bản trước hạ cả cụm thành "Nguyễn văn an." — sai chính tả tên người ngay trên
# màn hình soát văn bản, lại thừa một dấu chấm.
import DocCongDuc as engine
for chu, mong in (("NGUYỄN VĂN AN", "Nguyễn Văn An"),
                  ("TRẦN THỊ BÍCH", "Trần Thị Bích"),
                  ("LÊ HOÀNG LONG", "Lê Hoàng Long"),
                  ("BÀ PHẠM THỊ DUNG", "Bà Phạm Thị Dung")):
    ra = engine._chuan_hoa_hoa_chu(chu)
    ok(ra == mong, f"{chu} → {mong}", "" if ra == mong else f"RA “{ra}”")

print("\n--- E. Tiêu đề toàn hoa vẫn hạ chữ như cũ (không phải tên người) ---")
for chu, mong in (("THÔNG BÁO LỊCH NGHỈ LỄ", "Thông báo: lịch nghỉ lễ."),
                  ("QUYẾT ĐỊNH VỀ VIỆC BỔ NHIỆM", "Quyết định: về việc bổ nhiệm.")):
    ra = engine._chuan_hoa_hoa_chu(chu)
    ok(ra == mong, f"{chu[:30]} vẫn hạ chữ", "" if ra == mong else f"RA “{ra}”")

print()
if loi:
    print(f"ĐỎ — {loi} chỗ lệch. Bộ chuẩn hoá đang đọc sai tên người trong")
    print("danh sách công đức, hoặc đã ngừng chuẩn hoá địa chỉ thật.")
else:
    print("XANH — tên người giữ nguyên, địa chỉ vẫn chuẩn hoá đúng.")
sys.exit(1 if loi else 0)
