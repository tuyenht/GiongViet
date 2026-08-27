# -*- coding: utf-8 -*-
"""Kiểm thử chuẩn hóa số văn bản pháp quy theo NĐ 30/2020/NĐ-CP & Đảng."""
import io
import sys
from pathlib import Path
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", line_buffering=True)
_GOC = str(Path(__file__).resolve().parent.parent)
sys.path.insert(0, _GOC)

from src.core.bo_dieu_phoi_ngu_canh import dieu_phoi_ngu_canh

tests = [
    # 1. Văn bản QPPL & Chính phủ
    ("Nghị định Số: 30/2020/NĐ-CP", "số 30 năm 2020 Nghị định Chính phủ"),
    ("Theo Nghị định 136/2020/NĐ-CP", "Theo Nghị định số 136 năm 2020 Nghị định Chính phủ"),
    ("Thông tư số 01/2021/TT-BGDĐT", "Thông tư số 1 năm 2021 Thông tư Bộ Giáo dục và Đào tạo"),
    ("Quyết định 15/2023/QĐ-UBND", "Quyết định số 15 năm 2023 Quyết định Ủy ban nhân dân"),
    
    # 2. Luật & Quốc hội
    ("Luật số 45/2019/QH14", "Luật số 45 năm 2019 Quốc hội khóa 14"),
    ("Nghị quyết 15/2024/QH15", "Nghị quyết số 15 năm 2024 Quốc hội khóa 15"),
    
    # 3. Văn bản Đảng (66-QĐ/TW)
    ("Quy định số 66-QĐ/TW", "Quy định số 66 Quyết định Trung ương"),
    ("Hướng dẫn 05-HD/BTCTW", "Hướng dẫn số 5 Hướng dẫn Ban Tổ chức Trung ương"),
    
    # 4. Hợp đồng (Đ có dấu) vs Hướng dẫn (D không dấu)
    ("Hợp đồng số 12-HĐ/2024", "Hợp đồng số 12 Hợp đồng năm 2024"),
]

loi = 0
for text, mong_doi in tests:
    kq = dieu_phoi_ngu_canh(text)
    dat = mong_doi in kq
    print(f"[{'PASS' if dat else 'FAIL'}] '{text}' -> '{kq}'")
    if not dat:
        loi += 1

if loi == 0:
    print("ALL_LEGAL_TESTS_PASSED_100%")
    sys.exit(0)
else:
    print(f"FAILED: {loi} tests")
    sys.exit(1)
