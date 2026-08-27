# -*- coding: utf-8 -*-
"""Kiem khoa ghi du lieu nguoi dung.

AN TOAN: moi hang duong dan bi tro sang thu muc tam TRUOC khi goi bat cu ham
ghi nao, nen ke ca khi khoa hong thi tep that van khong bi cham. Cuoi bai con
so lai mtime cua 6 tep du lieu that de chung minh dieu do.

Phep kiem quan trong nhat la muc A: goi ham ghi KHI CHUA KHOA va bat no phai
tao ra tep. Thieu buoc nay thi ca bai kiem se xanh gia - mot ham ghi hong san
cung "khong ghi gi".
"""
import io
import json
import shutil
import sys
import tempfile
from pathlib import Path

# Goc du an, tinh tu chinh vi tri tep nay. KHONG viet cung duong dan:
# kho da len GitHub, ai tai ve cho khac la vo het bo kiem.
_GOC = str(Path(__file__).resolve().parent.parent)
sys.path.insert(0, _GOC)
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8")

import DocCongDuc as engine

from giaodien import he_thong, ho_so
from giaodien_moi import khoa_du_lieu

# 6 tep du lieu that. Chup mtime dau bai, so lai cuoi bai.
TEP_THAT = ["cauhinh.ini", "hoso.json", "congduc.txt", "noidung.ini",
            "tudien.ini", "giaodien.json"]
GOC = Path(_GOC)
truoc = {t: (GOC / t).stat().st_mtime_ns for t in TEP_THAT if (GOC / t).exists()}

T = Path(tempfile.gettempdir()) / "gd-kiem-khoa"
if T.exists():
    shutil.rmtree(T)
T.mkdir(parents=True)

# Tro TAT CA duong ghi sang thu muc tam. Lam truoc khi goi bat cu thu gi.
engine.CONFIG_FILE = T / "cauhinh.ini"
engine.BASE_DIR = T
engine.GIONG_RIENG_DIR = T / "giong_rieng"
engine.GIONG_RIENG_FILE = T / "giong_rieng" / "danhsach.json"
ho_so.TEP = T / "hoso.json"
he_thong.TUY_CHON_FILE = T / "giaodien.json"
TUDIEN_TAM = T / "tudien.ini"

loi = 0


def ok(dk, nhan, them=""):
    global loi
    print(f"  {'ĐẠT ' if dk else 'LỆCH'} {nhan}{'  →  ' + str(them) if them else ''}")
    if not dk:
        loi += 1


CFG_MAU = {
    "vieneu_voice_id": "Giong Thu", "phong_cach": "Tin tức - thông báo",
    "nghi_nguoi": 3.3, "nghi_nhom": 0.95, "so_nguoi_nhom": 20, "nghi_doan": 0.5,
    "nhan_manh_tien": False, "nghi_cau": 0.3, "nghi_doan_vb": 0.6,
    "so_ky_tu": 280, "doc_so_bang_chu": True, "bo_markdown": True,
    "data_file": T / "congduc.txt", "ffplay": T / "ffplay.exe",
}
KHO_MAU = {"dangDung": "aaa", "dsHoSo": [
    {"ma": "aaa", "ten": "Thử", "loai": "vanban"}]}


def goi_het_cac_ham_ghi():
    """Goi 8 cua ra ghi. Tra ve danh sach tep xuat hien sau do."""
    engine.save_config(dict(CFG_MAU))
    engine.luu_tudien(TUDIEN_TAM, {"abc": "a bờ cờ"})
    engine.luu_ds_giong_rieng([{"id": "r1", "ten": "x", "file": "y"}])
    ho_so.luu(dict(KHO_MAU))
    ho_so.tao_tep_noi_dung("Danh sách thử")
    he_thong.luu_tuy_chon({"theme": "dark", "zoom": 150})
    return sorted(str(p.relative_to(T)) for p in T.rglob("*") if p.is_file())


print("--- A. CHUA khoa: cac ham ghi PHAI tao ra tep (phep kiem tu chung minh) ---")
sinh_ra = goi_het_cac_ham_ghi()
ok(len(sinh_ra) >= 6, f"chua khoa thi ghi that, {len(sinh_ra)} tep hien ra", sinh_ra)
ok((T / "cauhinh.ini").exists(), "save_config co ghi cauhinh.ini")
ok((T / "hoso.json").exists(), "ho_so.luu co ghi hoso.json")
ok((T / "giaodien.json").exists(), "luu_tuy_chon co ghi giaodien.json")
ok(TUDIEN_TAM.exists(), "luu_tudien co ghi tudien.ini")
ok(any(x.startswith("noidung-") for x in sinh_ra), "tao_tep_noi_dung co de tep moi")
ok((T / "giong_rieng" / "danhsach.json").exists(), "luu_ds_giong_rieng co ghi")

print("\n--- B. Con ho truoc khi khoa ---")
ho = khoa_du_lieu.con_ho()
ok(len(ho) == 9, "9 cua ra deu dang mo", len(ho))
ok(not khoa_du_lieu.dang_khoa(), "chua khoa")

print("\n--- C. Khoa lai ---")
ok(khoa_du_lieu.khoa() is True, "lan dau khoa tra True")
ok(khoa_du_lieu.khoa() is False, "goi lai lan hai khong lam gi")
ok(khoa_du_lieu.dang_khoa(), "dang_khoa() = True")
ok(khoa_du_lieu.con_ho() == [], "khong con cua ra nao ho", khoa_du_lieu.con_ho())

print("\n--- D. SAU khoa: goi lai y het, KHONG mot byte nao ra dia ---")
for p in T.rglob("*"):
    if p.is_file():
        p.unlink()
shutil.rmtree(T / "giong_rieng", ignore_errors=True)
khoa_du_lieu.da_chan.clear()
con_lai = goi_het_cac_ham_ghi()
ok(con_lai == [], "0 tep duoc tao ra", con_lai)
ok(sum(khoa_du_lieu.da_chan.values()) == 6, "dem du 6 lan bi chan",
   dict(khoa_du_lieu.da_chan))

print("\n--- E. Gia tri tra ve phai vo hai ---")
ok(ho_so.tao_tep_noi_dung("bat ky") == ho_so.TEP_NOI_DUNG_GOC,
   "tao_tep_noi_dung tra ve noidung.ini chu khong phai None",
   ho_so.tao_tep_noi_dung("x"))
ok(engine.save_config(dict(CFG_MAU)) is None, "save_config tra None")

print("\n--- F. Cac ham trung gian cua Api van nam duoi cua da khoa ---")
# Doc thang ma nguon: moi phuong thuc cong khai co goi mot trong 8 cua ra
# (truc tiep hay qua _ghi_cau_hinh / _luu_kho_ho_so / _luu_tu_dien) deu phai
# nam duoi mot cua da khoa. Day la phep kiem chong "them ham ghi moi ma quen".
nguon_path = (GOC / "src" / "core" / "cau_noi.py") if (GOC / "src" / "core" / "cau_noi.py").exists() else (GOC / "giaodien" / "cau_noi.py")
nguon = nguon_path.read_text(encoding="utf-8")
CUA = [t for _, t, _, _ in khoa_du_lieu.CUA_RA_GHI]
ok(all(f".{t}(" in nguon or f"{t}(" in nguon
       for t in ["save_config", "luu_tudien", "luu_tuy_chon"]),
   "cac cua ra chinh deu thay trong cau_noi.py")
ok("_ghi_cau_hinh" in nguon and "_luu_kho_ho_so" in nguon,
   "hai ham trung gian con nguyen ten")
so_lan_ghi_cau_hinh = nguon.count("self._ghi_cau_hinh()")
ok(so_lan_ghi_cau_hinh >= 10,
   f"_ghi_cau_hinh duoc goi {so_lan_ghi_cau_hinh} cho - tat ca deu bi khoa chan")

print("\n--- G. hoso-v2 KHONG di qua duong bi khoa ---")
from giaodien_moi import ho_so_v2
ho_so_v2.TEP = T / "hoso-v2.json"
ok(ho_so_v2.luu({"hoSo": [{"ma": "a", "ten": "T", "giong": "g", "tep": ["x.txt"]}]}),
   "van luu duoc hoso-v2.json khi da khoa")
ok((T / "hoso-v2.json").exists(), "tep hoso-v2.json co that")
d = json.loads((T / "hoso-v2.json").read_text(encoding="utf-8"))
ok(d["hoSo"][0]["ten"] == "T", "doc lai dung noi dung", d["hoSo"][0]["ten"])

print("\n--- H. 6 tep du lieu THAT khong bi cham suot ca bai kiem ---")
for t, mt in truoc.items():
    ok((GOC / t).stat().st_mtime_ns == mt, f"{t} nguyen mtime")

shutil.rmtree(T, ignore_errors=True)
print(f"\n{'XANH — khớp hết' if loi == 0 else f'ĐỎ — {loi} chỗ lệch'}")
sys.exit(1 if loi else 0)
