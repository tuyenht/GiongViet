# -*- coding: utf-8 -*-
"""Dat lai BAY thiet lap nhip doc ve gia tri da ghi lai.

Chay:  py tests/dat_lai_nhip_doc.py           # xem gia tri hien tai, KHONG ghi
       py tests/dat_lai_nhip_doc.py --ghi      # ghi that

VI SAO CO TEP NAY. Buoc bam thu bay o chinh trong man Cai dat GHI THAT xuong
cau hinh. Sau khi thu xong, chu du an can dat lai nhip doc cu - go tay bay o
la lau va de sai mot o.

GIA TRI GOC duoi day doc tu cau hinh that luc 7/10/2026, TRUOC khi bam thu.
Neu con so nao khac y chu du an thi sua ngay trong tep nay roi chay lai.

MAC DINH LA CHI XEM. Phai co --ghi moi that su ghi: day la du lieu nguoi dung,
va mot tep nam trong tests/ thi de bi chay bua.
"""
import io
import os
import sys
from pathlib import Path

GOC = Path(__file__).resolve().parent.parent
os.environ.setdefault("GIONGVIET_GOC", str(GOC))
sys.path.insert(0, str(GOC))
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8",
                              line_buffering=True)

import DocCongDuc as engine                                      # noqa: E402

# Doc tu cau hinh that luc 7/10/2026, truoc khi bam thu.
GOC_GIA_TRI = {
    "nghi_nguoi": 1.3,
    "nghi_nhom": 2.5,
    "so_nguoi_nhom": 20,
    "nghi_doan": 0.8,
    "nghi_cau": 0.25,
    "nghi_doan_vb": 0.7,
    "so_ky_tu": 280,
}

GHI = "--ghi" in sys.argv

cfg = engine.load_config()

print("  khoa            dang co      gia tri goc   trang thai")
print("  " + "-" * 58)
lech = []
for k, goc in GOC_GIA_TRI.items():
    nay = cfg.get(k)
    khop = abs(float(nay or 0) - float(goc)) < 1e-9
    print(f"  {k:<15} {str(nay):<12} {str(goc):<13} "
          f"{'khop' if khop else 'LECH -> se dat lai'}")
    if not khop:
        lech.append(k)

if not lech:
    print("\n  Khong co o nao lech. Khong phai dat lai gi.")
    sys.exit(0)

if not GHI:
    print(f"\n  {len(lech)} o dang lech. CHUA ghi gi ca.")
    print("  Muon dat lai that thi chay:  py tests/dat_lai_nhip_doc.py --ghi")
    sys.exit(0)

for k in lech:
    cfg[k] = GOC_GIA_TRI[k]
engine.save_config(cfg)

# Doc LAI tu dia de chac no ghi duoc that, khong chi doi trong bo nho.
lai = engine.load_config()
con_lech = [k for k, v in GOC_GIA_TRI.items()
            if abs(float(lai.get(k) or 0) - float(v)) >= 1e-9]
if con_lech:
    print(f"\n  CHUA XONG: {con_lech} van lech sau khi ghi.")
    sys.exit(1)
print(f"\n  Da dat lai {len(lech)} o, va doc lai tu dia thay dung.")
