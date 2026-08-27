# -*- coding: utf-8 -*-
"""L1 — Menu Tep hua nhan .csv nhung engine khong biet doc dau phay.

Rui ro that su: hop thoai mo tep loc san "*.csv" -> nguoi dung tin la chuong
trinh doc duoc tep Excel xuat ra. Nhung parse_data_file chi tach hai truong
bang TAB hoac bang KHOANG TRANG truoc con so; khong co nhanh nao cho dau phay
va cung khong he import module csv. Neu that vay thi moi dong "Ten,So tien"
roi vao nhanh kind='tieude' - ten VA so tien dinh lien nhau bi doc nguyen cuc
nhu mot cau tieu de, KHONG co canh bao nao bao cho nguoi dung biet.

Bai nay CHI goi parse_data_file / normalize_name (ham thuan van ban).
KHONG nap mo hinh VieNeu, KHONG sinh am thanh.
Chay tren tempfile, khong cham mot byte du lieu nguoi dung.
"""
# --- dat goc du an tu vi tri tep nay (bai nam trong kiem/) ---
import os as _os, sys as _sys
from pathlib import Path as _Path
_os.environ.setdefault('GIONGVIET_GOC', str(_Path(__file__).resolve().parent.parent))
_sys.path.insert(0, _os.environ['GIONGVIET_GOC'])
# --- het shim ---
import io
import os
import re
import shutil
import sys
import tempfile
from pathlib import Path

# Kich ban nay nam trong thu muc tam (ngoai kho) nen khong suy ra goc tu
# __file__ duoc. Lay tu bien moi truong, mac dinh la thu muc dang lam viec.
_GOC = os.environ.get("GIONGVIET_GOC") or os.getcwd()
if not (Path(_GOC) / "DocCongDuc.py").is_file():
    sys.exit(f"Khong thay DocCongDuc.py trong {_GOC} — dat GIONGVIET_GOC")
sys.path.insert(0, _GOC)
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8",
                              line_buffering=True)

GOC = Path(_GOC)

# Doi goc kho cau hinh sang thu muc tam TRUOC khi nap engine, dung nep cua
# kiem_kho_cau_hinh.py — engine khong duoc cham giongviet.db / *.ini that.
tam = Path(tempfile.mkdtemp())
from src.core import kho_cau_hinh as kho  # noqa: E402
kho.dat_goc(tam)

import DocCongDuc as engine                                         # noqa: E402

loi = 0


def ok(dk, nhan, them=""):
    global loi
    print(f"  {'ĐẠT ' if dk else 'LỆCH'} {nhan}{'  →  ' + str(them) if them else ''}")
    if not dk:
        loi += 1


def do_tep(ten, dong_list):
    """Ghi tep vao thu muc tam roi goi thang parse_data_file."""
    p = tam / ten
    p.write_text("\n".join(dong_list) + "\n", encoding="utf-8")
    return engine.parse_data_file(p)


def in_bang(records, canh_bao, nguon):
    print(f"    nguon: {nguon}")
    for r in records:
        print(f"      dong {r['line_no']}: kind={r['kind']!r:10} "
              f"name={r['name']!r}  amount={r['amount']!r}")
    print(f"      canh_bao = {canh_bao!r}   (so phan tu: {len(canh_bao)})")


# ---------------------------------------------------------------------------
print("--- A. Tep .csv dau PHAY, kieu Excel tieng Anh xuat ra ---")
DONG_PHAY = [
    "Họ và tên,Số tiền",              # 1 dong tieu de that
    "Nguyễn Văn An,500000",           # 2 phay KHONG khoang trang
    "Trần Thị Bình, 1.200.000",       # 3 phay CO khoang trang
    "Lê Văn Cường\t2.000.000",        # 4 dung TAB
]
rec_phay, cb_phay = do_tep("danhsach-phay.csv", DONG_PHAY)
in_bang(rec_phay, cb_phay, DONG_PHAY)

kind_phay = [r["kind"] for r in rec_phay]
ok(kind_phay[:3] == ["tieude", "tieude", "tieude"],
   "ba dong dau (tieu de + 2 dong phay) deu ra kind='tieude'", kind_phay)
ok(kind_phay[3] == "nguoi", "chi dong TAB ra kind='nguoi'", kind_phay[3])
ok(cb_phay == [],
   "canh_bao TRONG RONG - hong im lang, nguoi dung khong duoc bao gi", cb_phay)
so_nguoi_phay = sum(1 for r in rec_phay if r["kind"] == "nguoi")
ok(so_nguoi_phay == 1,
   f"3 dong du lieu that ma chi nhan ra {so_nguoi_phay} nguoi", so_nguoi_phay)

# ---------------------------------------------------------------------------
print("\n--- B. Tep .csv dau CHAM PHAY, kieu Excel tieng Viet xuat ra ---")
DONG_CP = [
    "Họ và tên;Số tiền",
    "Nguyễn Văn An;500000",           # cham phay KHONG khoang trang
    "Trần Thị Bình; 1.200.000",       # cham phay CO khoang trang
    "Lê Văn Cường\t2.000.000",        # TAB
]
rec_cp, cb_cp = do_tep("danhsach-champhay.csv", DONG_CP)
in_bang(rec_cp, cb_cp, DONG_CP)

kind_cp = [r["kind"] for r in rec_cp]
ok(kind_cp[1] == "tieude",
   "';' khong khoang trang -> tieude (mat ca ten lan tien)", kind_cp[1])
ok(kind_cp[2] == "nguoi",
   "'; ' CO khoang trang -> lai lot vao nhanh nguoi", kind_cp[2])
ten_cp = rec_cp[2]["name"] if kind_cp[2] == "nguoi" else ""
ok(ten_cp.endswith(";"),
   "va ten con DINH nguyen dau ';' o cuoi", repr(ten_cp))

# ---------------------------------------------------------------------------
print("\n--- C. Doi chung: dung tep .txt hai khoang trang thi dung het ---")
DONG_TXT = [
    "DANH SÁCH CÔNG ĐỨC",
    "Nguyễn Văn An   500000",
    "Trần Thị Bình   1.200.000",
    "Lê Văn Cường\t2.000.000",
]
rec_txt, cb_txt = do_tep("danhsach-chuan.txt", DONG_TXT)
in_bang(rec_txt, cb_txt, DONG_TXT)
kind_txt = [r["kind"] for r in rec_txt]
ok(kind_txt == ["tieude", "nguoi", "nguoi", "nguoi"],
   "dinh dang chuan: 1 tieu de + 3 nguoi", kind_txt)

# ---------------------------------------------------------------------------
print("\n--- D. Cau se DOC RA LOA voi tep .csv dau phay ---")
# normalize_name la ham thuan van ban, khong nap mo hinh. Day dung la chuoi
# engine dua vao build_playlist_congduc (DocCongDuc.py:1487-1489: text =
# normalize_name(rec["name"]) + ".").
for r in rec_phay:
    if r["kind"] == "tieude":
        print(f"      se doc: {engine.normalize_name(r['name'], {}) + '.'!r}")
ok(any("500000" in engine.normalize_name(r["name"], {})
       or "500.000" in engine.normalize_name(r["name"], {})
       for r in rec_phay if r["kind"] == "tieude"),
   "so tien bi keo nguyen cuc vao cau tieu de, khong duoc doc thanh tien")

# ---------------------------------------------------------------------------
print("\n--- E. Toan bo ma ung dung co 'import csv' khong ---")
tep_quet = [GOC / "DocCongDuc.py"] + sorted((GOC / "src" / "core").glob("*.py")) \
           + sorted((GOC / "src" / "app").glob("*.py"))
co_csv = []
for p in tep_quet:
    nguon = p.read_text(encoding="utf-8", errors="replace")
    if re.search(r"^\s*import\s+csv\b|^\s*from\s+csv\s+import", nguon, re.M):
        co_csv.append(p.name)
print(f"    quet {len(tep_quet)} tep: DocCongDuc.py + src/core/ + src/app/")
ok(not co_csv, "khong tep nao import csv", co_csv or "khong co")

print("\n--- F. Hop thoai co that su hua .csv khong ---")
nguon_cn = (GOC / "src" / "app" / "cau_noi_moi.py").read_text(encoding="utf-8")
for i, d in enumerate(nguon_cn.splitlines(), 1):
    if "csv" in d and "file_types" in d:
        print(f"      cau_noi_moi.py:{i}: {d.strip()}")
ok('Tệp danh sách (*.txt;*.csv)' in nguon_cn,
   "menu 'Mo danh sach ten va so' loc san *.csv")

# ---------------------------------------------------------------------------
print("\n--- G. Ba nhanh tach truong trong parse_data_file ---")
nguon_e = (GOC / "DocCongDuc.py").read_text(encoding="utf-8")
than = nguon_e.split("def parse_data_file(")[1].split("\ndef ")[0]
print("      cac nhanh tach truong tim thay:")
for d in than.splitlines():
    if "split(" in d or "re.match(" in d or "m2 = " in d or d.strip().startswith('r"^'):
        print(f"        {d.strip()}")
ok('"\\t" in line' in than, "nhanh 1: TAB")
ok(r"\s{2,}" in than, "nhanh 2: it nhat HAI khoang trang")
ok(r"\s+(" in than or r")\s+(" in than, "nhanh 3: it nhat MOT khoang trang")
# CHI xet cac cau lenh TACH TRUONG. Khong duoc quet ca than ham: dong
# `line.startswith(";")` la dau hieu DONG CHU THICH, khong phai dau phan cach,
# quet tho se bao nham la "co ho tro cham phay".
dong_tach = [d.strip() for d in than.splitlines()
             if "split(" in d or "re.match(" in d or d.strip().startswith('r"^')]
tach_theo_phay = [d for d in dong_tach
                  if 'split(","' in d or "split(';'" in d or 'split(";"' in d
                  or "[,;]" in d or "[;,]" in d]
ok(not tach_theo_phay,
   "khong cau lenh tach truong nao dung dau phay / cham phay lam dau phan cach",
   tach_theo_phay or "khong co")
ok(all(("\\t" in d) or ("\\s{2,}" in d) or ("\\s+(" in d) or ("re.match" not in d
       and "split(" not in d) for d in dong_tach),
   "moi nhanh tach truong deu doi TAB hoac KHOANG TRANG")

shutil.rmtree(tam, ignore_errors=True)

print(f"\n{'XANH — khớp hết' if loi == 0 else f'ĐỎ — {loi} chỗ lệch'}")
sys.exit(1 if loi else 0)
