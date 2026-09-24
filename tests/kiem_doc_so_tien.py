# -*- coding: utf-8 -*-
"""BAI CANH (xanh = tot): doc dung SO TIEN trong danh sach cong duc.

VI SAO CO BAI NAY

Nghiep vu goc cua chuong trinh la doc danh sach cong duc: moi dong mot nguoi,
kem so tien. Doc sai so tien la sai vao dung cai nguoi ta quan tam nhat.

Do ngay 08/09/2026, parse_money sai 10/12 ca:

    "1,5 trieu"  ->  15            (muoi lam dong, dung ra 1.500.000)
    "2,5tr"      ->  25
    "0,5 trieu"  ->  5
    "1 ty"       ->  1             (don vi "ty" chua tung duoc ho tro)

Nguyen nhan: ban cu bo he so ngay khi phan so co bat ky dau cham hay phay nao,
roi xoa het dau de lay chu so - "1,5" thanh "15".

Ham nay nam tren BA duong quan trong:
  · format_money_for_reading  -> chu doc ra loa
  · cong tong tien            (DocCongDuc.py, cau_noi.py)
  · nguong nhan manh so tien lon

Ban va phan biet dau PHAN CACH NGHIN ("2.000.000", nhom du 3 chu so) voi dau
THAP PHAN ("1,5", sau dau 1-2 chu so).

Bai chi goi ham thuan van ban. KHONG nap mo hinh, KHONG sinh am thanh,
KHONG cham mot byte du lieu nguoi dung.
"""
import io
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")

import DocCongDuc as engine

loi = 0


def ok(dieu_kien, nhan, them=""):
    global loi
    print(f"  {'ĐẠT ' if dieu_kien else 'LỆCH'} {nhan}" + (f"  →  {them}" if them else ""))
    if not dieu_kien:
        loi += 1


print("--- A. Số tiền có phần thập phân + đơn vị ---")
THAP_PHAN = [
    ("1,5 triệu", 1_500_000), ("2,5 triệu", 2_500_000), ("1.5 triệu", 1_500_000),
    ("0,5 triệu", 500_000), ("1,2tr", 1_200_000), ("2,5tr", 2_500_000),
    ("1,5 tr", 1_500_000), ("100,5 nghìn", 100_500), ("3,5 củ", 3_500_000),
]
for chu, mong in THAP_PHAN:
    ra = engine.parse_money(chu)
    ok(ra == mong, f"{chu:<14} = {mong:,}", "" if ra == mong else f"RA {ra:,}")

print("\n--- B. Số nguyên + đơn vị (gồm 'tỷ' — trước đây không có) ---")
NGUYEN = [
    ("2 triệu", 2_000_000), ("500 nghìn", 500_000), ("500k", 500_000),
    ("2tr", 2_000_000), ("1 tỷ", 1_000_000_000), ("2,5 tỷ", 2_500_000_000),
    ("3 tỉ", 3_000_000_000),
]
for chu, mong in NGUYEN:
    ra = engine.parse_money(chu)
    ok(ra == mong, f"{chu:<14} = {mong:,}", "" if ra == mong else f"RA {ra:,}")

print("\n--- C. Dấu phân cách nghìn vẫn phải giữ nguyên nghĩa cũ ---")
NGHIN = [
    ("2.000.000", 2_000_000), ("500.000 đồng", 500_000), ("1.500.000đ", 1_500_000),
    ("800000", 800_000), ("10.000.000 VNĐ", 10_000_000), ("2.500.000 VND", 2_500_000),
]
for chu, mong in NGHIN:
    ra = engine.parse_money(chu)
    ok(ra == mong, f"{chu:<16} = {mong:,}", "" if ra == mong else f"RA {ra:,}")

print("\n--- D. Chuỗi đọc ra loa ---")
DOC = [
    ("1,5 triệu", "một triệu năm trăm nghìn đồng"),
    ("1 tỷ", "một tỷ đồng"),
    ("2.000.000", "hai triệu đồng"),
    ("500k", "năm trăm nghìn đồng"),
]
for chu, mong in DOC:
    ra = engine.format_money_for_reading(chu)
    ok(ra == mong, f"{chu:<12} đọc là “{mong}”", "" if ra == mong else f"RA “{ra}”")

print("\n--- E. Đầu vào hỏng phải báo lỗi, không trả số bừa ---")
for chu in ("", "   ", "abc", "đồng"):
    try:
        ra = engine.parse_money(chu)
        ok(False, f"{chu!r} phải ném ValueError", f"lại trả {ra}")
    except ValueError:
        ok(True, f"{chu!r} ném ValueError đúng")

print()
if loi:
    print(f"ĐỎ — {loi} chỗ lệch. Chương trình đang đọc sai số tiền công đức.")
else:
    print("XANH — số tiền đọc đúng ở mọi dạng ghi thường gặp.")
sys.exit(1 if loi else 0)
