# -*- coding: utf-8 -*-
"""Kiểm toán toàn diện: Tệp giọng riêng, Lõi Tone Color Transfer, UI và Speaker Pipeline."""

import io
import json
import sys
from pathlib import Path

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8")
_GOC = str(Path(__file__).resolve().parent.parent)
sys.path.insert(0, _GOC)

import DocCongDuc as engine
from src.core.ds_giong import doc_nhanh
from src.core.thu_vien_giong import du_lieu
from src.core.chuyen_mau_giong import BoChuyenMauGiong

loi = 0
def ok(dk, nhan, them=""):
    global loi
    print(f"  {'ĐẠT ' if dk else 'LỆCH'} {nhan}{'  →  ' + str(them) if them else ''}")
    if not dk:
        loi += 1

print("--- 1. Kiểm toán Tệp và Dữ liệu Kho Giọng Riêng ---")
ds_file = Path("data/giong_rieng/danhsach.json")
ok(ds_file.exists(), "tệp danhsach.json tồn tại trên đĩa")
ds = json.loads(ds_file.read_text(encoding="utf-8")) if ds_file.exists() else []
ok(len(ds) == 5, f"đủ 5 giọng mẫu mặc định", f"{len(ds)}/5 giọng")

for g in ds:
    fpath = Path(g["file"])
    ok(fpath.exists(), f"{g['id']} file mẫu tồn tại", f"{fpath.name} ({fpath.stat().st_size:,} bytes)")
    ok(g.get("da_ngon_ngu") is True, f"{g['id']} cờ da_ngon_ngu đã bật")

print("\n--- 2. Kiểm toán Lõi Trích xuất Âm sắc (Timbre Feature Extraction) ---")
for g in ds:
    timbre = BoChuyenMauGiong.trich_xuat_van_giong(g["file"])
    ok(timbre is not None and len(timbre) > 100, f"trích xuất âm sắc thành công cho {g['ten'][:20]}...", f"{len(timbre)} bins")

print("\n--- 3. Kiểm toán Nạp Nhanh Danh Sách UI & Thư Viện Giọng ---")
quick_list = doc_nhanh()
rieng_in_quick = [x for x in quick_list if str(x["id"]).startswith("rieng_")]
ok(len(rieng_in_quick) == 5, "5 giọng riêng đứng đầu danh sách nhanh doc_nhanh()", f"{len(rieng_in_quick)} giọng")
for r in rieng_in_quick:
    ok(r.get("da_ngon_ngu") is True, f"{r['id']} nhãn đa ngữ trên UI", r["ten"])

print("\n--- 4. Kiểm toán Khóa Cache Phân Lập Đa Ngôn Ngữ trong Speaker ---")
speaker = engine.Speaker({"giong": "rieng_001", "ngonNgu": "zh"})
kho_key = speaker._khoa_kho("你好世界", 1.0)
ok(kho_key[1] == "zh" and kho_key[2] == "rieng_001", "khóa cache phân lập chính xác (ngôn ngữ zh, giọng rieng_001)", str(kho_key))

print(f"\n{('XANH — khớp hết (0 Gap)' if loi == 0 else f'ĐỎ — {loi} chỗ lệch')}")
sys.exit(loi)
