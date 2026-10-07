# -*- coding: utf-8 -*-
"""In bang man Cai dat ra JSON, de bai kiem JS dung bang THAT.

Chay:  py tests/_bang_caidat.py congduc
       py tests/_bang_caidat.py vanban

VI SAO CAN TEP NAY. Bai kiem JS can mot bang cai dat de bam nut len. Go tay
mot bang gia thi no se lech khoi bang Python that - doi ten mot truong ben
Python la bai JS van xanh trong khi san pham da hong. Nen lay bang THAT.

Tep bat dau bang dau gach duoi: chay_tat_ca.py chi chay *.py nhung tep nay
khong phai bai kiem, no chi in du lieu. Dat ten _bang_... cho de nhan ra.
"""
import io
import json
import os
import sys
from pathlib import Path

GOC = Path(__file__).resolve().parent.parent
os.environ.setdefault("GIONGVIET_GOC", str(GOC))
sys.path.insert(0, str(GOC))
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8")

from giaodien import cai_dat                                     # noqa: E402

CHE_DO = sys.argv[1] if len(sys.argv) > 1 else "congduc"

# Cau hinh TU DUNG trong bo nho - khong doc cauhinh.ini that cua chu du an.
CFG = {
    "nghi_nguoi": 1.3, "nghi_nhom": 2.5, "so_nguoi_nhom": 20, "nghi_doan": 0.8,
    "nghi_cau": 0.25, "nghi_doan_vb": 0.7, "so_ky_tu": 260,
    "nhan_manh_tien": True, "doc_so_bang_chu": True, "bo_markdown": False,
    "data_file": "",
}
TUY_CHON = {"theme": "light", "zoom": 100, "thu_muc_xuat": ""}

print(json.dumps(cai_dat.du_lieu(CFG, TUY_CHON, CHE_DO, ""),
                 ensure_ascii=False, default=str))
