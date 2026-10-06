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

print("\n=== F2. Chuan giao dien (chu du an chot 6/10/2026) ===")
# Ban dau nut 34px va loi giai thich nam trong title. Ca hai deu khong dat:
# chuan doi vung bam >= 44px, va cam giau thu quan trong sau hover (man cam
# ung khong co hover). Cac phep nay canh cho viec do khong quay lai.
import re as _re
_khoi = _re.search(r"if \(m\.kieu === 'songuyen'\).*?\n  \}", _js_cd, _re.S)
_khoi = _khoi.group(0) if _khoi else ""
ok(bool(_khoi), "tim thay khoi ve o chinh so trong man-caidat.js")
ok("title=" not in _khoi,
   "KHONG dung title - title chi hien khi re chuot, man cam ung khong thay")
ok(_khoi.count("aria-label") == 2,
   "ca hai nut co aria-label cho bo doc man hinh", _khoi.count("aria-label"))
ok("aria-live" in _khoi,
   "con so co aria-live - doi gia tri thi bo doc man hinh doc len")
# Nhan chu ngay tren nut, khong chi mot dau - hay +
ok("B\u1edbt" in _khoi and "Th\u00eam" in _khoi,
   "nut co NHAN CHU, khong chi mot dau toan hoc")

_so_nut = _re.search(r"\.caidat__so-nut \{(.*?)\}", _css, _re.S)
_than = _so_nut.group(1) if _so_nut else ""
ok(bool(_so_nut), "co khoi CSS .caidat__so-nut")
_mw = _re.search(r"min-width:\s*(\d+)px", _than)
_mh = _re.search(r"min-height:\s*(\d+)px", _than)
ok(bool(_mw) and int(_mw.group(1)) >= 44,
   "vung bam rong >= 44px", (_mw.group(1) + "px") if _mw else "khong khai")
ok(bool(_mh) and int(_mh.group(1)) >= 44,
   "vung bam cao >= 44px", (_mh.group(1) + "px") if _mh else "khong khai")
_cu = _re.search(r"font-size:\s*(\d+)px", _than)
ok(bool(_cu) and int(_cu.group(1)) >= 16,
   "chu tren nut >= 16px", (_cu.group(1) + "px") if _cu else "khong khai")
ok("focus-visible" in _css and "outline" in _css,
   "co vien tieu diem thay duoc de di bang ban phim")

print("      CHUA KIEM duoc bang bai nay: mau sac, do tuong phan THAT, bo cuc")
print("      o be ngang dien thoai. Nhung thu do phai MO CUA SO moi thay.")


print("\n=== I. Nhanh khoa SO khong duoc nuot khoa SO THUC ===")
# Vap that: ban dau quet ca THANH_TRUOT roi int() moi thu, nen bon khoa thoi
# gian cung roi vao nhanh nay va bi CAT CUT - nghi_cau = 0,9 giay ghi xuong
# thanh 0. Duong chinh cac khoang nghi la dat_thong_so, khong phai ham nay.
# GOI HAM THAT cua ban chay. Ban truoc bai nay tu tinh lai _so bang logic
# rieng - tuc no kiem chinh no. Da thu dat nguoc loi vao ma bai VAN XANH,
# nen moi tach khoa_so_nguyen() ra muc module de goi duoc tu day.
from giaodien_moi import cau_noi_moi as _cnm
_so = _cnm.khoa_so_nguyen()
if _ham:
    _than_h = ast.get_source_segment(_nguon, _ham) or ""
    ok("khoa_so_nguyen()" in _than_h,
       "moi_dat_cai_dat lay danh sach khoa tu khoa_so_nguyen(), khong tu quet")
_thoi_gian = [k for k in ("nghi_nguoi", "nghi_nhom", "nghi_cau", "nghi_doan_vb")
              if k in _so]
ok(not _thoi_gian, "bon khoa thoi gian KHONG lot vao nhanh so nguyen",
   _thoi_gian or "khong cai nao")
ok(set(_so) == {"so_nguoi_nhom", "so_ky_tu"},
   "dung hai khoa so nguyen duoc nhan", sorted(_so))

print("\n=== J. Doi mot cong tac KHONG duoc bien danh sach thanh van ban ===")
# Vap that: nhanh boolean goi moi_dat_doan, ma ham do dat _loai_tai_lieu =
# "vanban" roi xoa _records. Dang mo danh sach cong duc ma gat mot cong tac la
# tai lieu AM THAM bien thanh van ban thuong - mat nhom, mat loi dan, va chinh
# hai muc cua cong duc bien khoi man hinh nguoi dung dang dung.
#
# Phep nay soi LOI GOI that bang AST chu khong tim chuoi: chu thich trong ham
# co nhac ten moi_dat_doan, tim bang chuoi la bao nham ngay - da bao nham that.
_goi_that = ([n.func.attr for n in ast.walk(_ham)
              if isinstance(n, ast.Call) and isinstance(n.func, ast.Attribute)]
             if _ham else [])
ok("moi_dat_doan" not in _goi_that,
   "moi_dat_cai_dat KHONG goi moi_dat_doan", sorted(set(_goi_that)))
ok("_dung_lai_playlist_moi" in _goi_that,
   "dung duong re nhanh theo loai tai lieu")

_mdd = next((n for n in ast.walk(_cay) if isinstance(n, ast.FunctionDef)
             and n.name == "moi_dat_doan"), None)
_than_mdd = (ast.get_source_segment(_nguon, _mdd) or "") if _mdd else ""
ok('self._loai_tai_lieu = "vanban"' in _than_mdd,
   "moi_dat_doan VAN dat loai = vanban (ly do khong duoc goi no o tren)")

print("\n=== H. Engine that su dung con so nay ===")
_eng = (GOC / "DocCongDuc.py").read_text(encoding="utf-8")
ok('cfg["so_nguoi_nhom"]' in _eng,
   "DocCongDuc.py van doc so_nguoi_nhom de quyet dinh cho nghi dai")
from giaodien import ho_so
ok("so_nguoi_nhom" in ho_so.KHOA_THEO_LOAI["congduc"],
   "ho so cat gia tri nay theo tung ho so")

print("\n" + ("ĐỎ — %d chỗ lệch" % len(_lech) if _lech else "XANH — khớp hết"))
sys.exit(1 if _lech else 0)
