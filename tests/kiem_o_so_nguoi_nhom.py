# -*- coding: utf-8 -*-
"""Bai canh: o chinh "So nguoi moi nhom" phai CON va con NOI THAT.

LOAI_BAI = "canh"   -> xanh la tot. Doc chu thich nay truoc khi dung vao.

Day la nua sau cua L7. Bai kiem_so_nguoi_nhom.py chung minh cai LO: engine
dung so_nguoi_nhom de quyet dinh cho nghi dai, ho so van cat gia tri ay, ma
khong man hinh nao dat duoc. Bai NAY canh cho cai va: o chinh da co, va no
noi lien mach tu giao dien xuong toi engine.

BAY DA VAP THAT khi va lo nay, nen phep [G] o duoi la phep quan trong nhat:
lop cha Api DA CO san _dung_lai_playlist(giu_vi_tri=False) va muoi cho
trong cau_noi.py goi no. Dat trung ten trong ApiMoi la de mat, roi nam phuong
thuc ke thua (doi_phong_cach, dat_cai_dat, them_tu, sua_tu, xoa_tu) chet ngay
voi TypeError. Grep mot minh trong cau_noi_moi.py KHONG thay duoc - phai soi
ca lop cha.

Bai nay chi DOC: khong nap mo hinh, khong phat tieng, khong cham cau hinh
that (cfg la dict tu dung trong bo nho).
"""
LOAI_BAI = "canh"
# --- dat goc du an tu vi tri tep nay ---
import os as _os, sys as _sys
from pathlib import Path as _Path
_os.environ.setdefault('GIONGVIET_GOC', str(_Path(__file__).resolve().parent.parent))
_sys.path.insert(0, _os.environ['GIONGVIET_GOC'])
# --- het shim ---
import ast
import io
import re
import sys
from pathlib import Path

GOC = Path(_os.environ['GIONGVIET_GOC'])
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8",
                              line_buffering=True)

_lech = []


def ok(dieu, nhan, them=""):
    print(("  ĐẠT  " if dieu else "  LỆCH ") + nhan + (f"  →  {them}" if them != "" else ""))
    if not dieu:
        _lech.append(nhan)


def _muc_doc(che_do, cfg):
    from giaodien import cai_dat
    d = cai_dat.du_lieu(cfg, {}, che_do, "")
    return [m for n in d["nhom"] if n["ma"] == "doc" for m in n["muc"]]


CFG = {"so_nguoi_nhom": 7, "nhan_manh_tien": True, "doc_so_bang_chu": True,
       "bo_markdown": False, "data_file": ""}

print("=== A. Man Cai dat co o chinh so, dung pham vi ===")
_m = [m for m in _muc_doc("congduc", CFG) if m["khoa"] == "so_nguoi_nhom"]
ok(len(_m) == 1, "che do congduc CO muc so_nguoi_nhom")
if _m:
    m = _m[0]
    ok(m["kieu"] == "songuyen", "muc thuoc kieu so nguyen", m["kieu"])
    ok((m["nhoNhat"], m["lonNhat"]) == (1, 50), "pham vi 1..50",
       f'{m["nhoNhat"]}..{m["lonNhat"]}')
    ok(m["giaTri"] == 7, "hien dung gia tri dang co", m["giaTri"])
    ok(bool(m.get("nhan")) and bool(m.get("goiY")),
       "co nhan va loi goi y cho nguoi dung", m.get("nhan"))

print("\n=== B. Che do van ban KHONG duoc bay no ra ===")
# Bay ra o che do khong dung la mot dang nut gia: nguoi dung chinh no, khong
# co gi doi, vi van ban thuong khong chia nhom.
ok(not any(m["khoa"] == "so_nguoi_nhom" for m in _muc_doc("vanban", CFG)),
   "che do vanban KHONG co muc nay",
   [m["khoa"] for m in _muc_doc("vanban", CFG)])

print("\n=== C. Gia tri ban ra tu trinh duyet phai bi kep hai dau ===")
# so_nguoi_nhom = 0 thi DocCongDuc.py chay `stt % 0` -> ZeroDivisionError
# giua luc dang doc. Khong duoc tin gia tri tu trinh duyet.
for vao, mong in ((0, 1), (-5, 1), (999, 50), ("abc", 20), (None, 20)):
    r = [m for m in _muc_doc("congduc", {**CFG, "so_nguoi_nhom": vao})
         if m["khoa"] == "so_nguoi_nhom"]
    ok(bool(r) and r[0]["giaTri"] == mong, f"vao {vao!r} -> {mong}",
       r[0]["giaTri"] if r else "(mat muc)")

print("\n=== D. ApiMoi thuc su NHAN khoa so, khong chi nhan cong tac ===")
_nguon = (GOC / "src" / "app" / "cau_noi_moi.py").read_text(encoding="utf-8")
_cay = ast.parse(_nguon)
_ham = next((n for n in ast.walk(_cay) if isinstance(n, ast.FunctionDef)
             and n.name == "moi_dat_cai_dat"), None)
ok(_ham is not None, "co ApiMoi.moi_dat_cai_dat")
if _ham:
    than = ast.get_source_segment(_nguon, _ham) or ""
    ok("THANH_TRUOT" in than,
       "pham vi kep lay tu du_lieu.THANH_TRUOT, khong go cung lai trong ham")
    ok("save_config" in than, "co ghi xuong cau hinh")
    ok("_dung_lai_playlist_moi" in than,
       "co dung lai playlist - cho nghi duoc chen luc DUNG, khong phai luc phat")

print("\n=== E. Man Cai dat phai theo loai tai lieu dang mo ===")
_mcd = next((n for n in ast.walk(_cay) if isinstance(n, ast.FunctionDef)
             and n.name == "moi_cai_dat"), None)
_than_mcd = ast.get_source_segment(_nguon, _mcd) or "" if _mcd else ""
ok("_loai_tai_lieu" in _than_mcd,
   "moi_cai_dat truyen loai tai lieu dang mo")
# "vanban" VAN duoc phep xuat hien - no la duong lui khi chua mo tep nao.
# Thu phai chan la dang GO CUNG: truyen thang "vanban" ma khong ngo toi
# _loai_tai_lieu. Soi dung loi goi cai_dat.du_lieu chu khong soi ca ham.
_goi = re.search(r"cai_dat\.du_lieu\((.*?)\)", _than_mcd, re.S)
_tham_so = _goi.group(1) if _goi else ""
ok(bool(_goi), "tim thay loi goi cai_dat.du_lieu trong moi_cai_dat")
ok("_loai_tai_lieu" in _tham_so,
   "loai ho so truyen vao la BIEN, khong phai chuoi go cung",
   " ".join(_tham_so.split()))

print("\n=== F. Giao dien web co ve va co noi tay bam ===")
_js_cd = (GOC / "src" / "web" / "man-caidat.js").read_text(encoding="utf-8")
_js_gd = (GOC / "src" / "web" / "giao-dien.js").read_text(encoding="utf-8")
ok("songuyen" in _js_cd, "man-caidat.js co ve kieu songuyen")
ok("data-cdso" in _js_cd, "o chinh co gan data-cdso de bat tay bam")
ok("data-cdso" in _js_gd and "datCaiDat" in _js_gd,
   "giao-dien.js co bat data-cdso va goi datCaiDat")
_css = (GOC / "src" / "web" / "man-giong.css").read_text(encoding="utf-8")
ok(".caidat__so" in _css, "co CSS cho o chinh so")

print("\n=== G. Ten rieng, KHONG de mat phuong thuc cua lop cha ===")
# Phep quan trong nhat cua bai nay. Xem docstring dau tep.
_cha = (GOC / "src" / "core" / "cau_noi.py").read_text(encoding="utf-8")
_ten_cha = {n.name for n in ast.walk(ast.parse(_cha))
            if isinstance(n, ast.FunctionDef)}
_ten_con = {n.name for n in ast.walk(_cay) if isinstance(n, ast.FunctionDef)}
_de = sorted(_ten_cha & _ten_con)

# ApiMoi co quyen GHI DE co y - nhung moi lan de phai la co y, nen liet ke ra
# de nguoi doc thay. Cai bat buoc: ten rieng cua bai nay khong duoc trung.
ok("_dung_lai_playlist" not in _ten_con,
   "ApiMoi KHONG dat trung ten _dung_lai_playlist cua lop cha")
ok("_dung_lai_playlist_moi" in _ten_con,
   "duong dung lai playlist cua ban moi mang ten rieng")

_goi_cha = len(re.findall(r"self\._dung_lai_playlist\(", _cha))
print(f"      lop cha tu goi _dung_lai_playlist {_goi_cha} lan - de mat la "
      f"{_goi_cha} cho cung hong")
ok(_goi_cha > 0, "lop cha that su van dung phuong thuc do", _goi_cha)
print(f"      ApiMoi ghi de co y {len(_de)} ten: {_de}")

print("\n=== H. Engine that su dung con so nay ===")
_eng = (GOC / "DocCongDuc.py").read_text(encoding="utf-8")
ok('cfg["so_nguoi_nhom"]' in _eng,
   "DocCongDuc.py van doc so_nguoi_nhom de quyet dinh cho nghi dai")
from giaodien import ho_so
ok("so_nguoi_nhom" in ho_so.KHOA_THEO_LOAI["congduc"],
   "ho so cat gia tri nay theo tung ho so")

print("\n" + ("ĐỎ — %d chỗ lệch" % len(_lech) if _lech else "XANH — khớp hết"))
sys.exit(1 if _lech else 0)
