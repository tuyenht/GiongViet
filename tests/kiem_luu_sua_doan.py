# -*- coding: utf-8 -*-
"""L3 — "Go sua khong bao gio duoc ghi lai": tai hien bang ma chay that.

RUI RO THAT SU: nguoi dung mo mot tep, go sua vai cho cho de doc, roi dong
chuong trinh. Neu goi ho so ghi xuong dia KHONG mang theo chu cua doan, va
lan mo sau chuong trinh doc lai tep GOC tu duong dan da nho, thi moi chu ho
sua deu bien mat ma khong co mot loi canh bao nao.

Kich ban nay dung DUNG cai goi ma giao dien that su gui sang Python (chuoi
JSON chep nguyen van tu trinh duyet khi go sua that mot doan), roi:
  A. Ghi goi do xuong dia bang chinh giaodien_moi/ho_so_v2.luu, in nguyen
     van tep ket qua.
  B. Dien lai vong doi: mo tep -> go sua -> luu ho so -> "khoi dong lai" ->
     mo lai tep tu duong dan da nho, so chu truoc va sau.
  C. Xem Ctrl+S (moi_luu_van_ban -> luu_tep.luu) co cuu duoc khong.

AN TOAN: toan bo chay tren tempfile.mkdtemp. kho_cau_hinh.dat_goc() duoc keo
ve thu muc tam, ho_so_v2.TEP cung vay, nen khong mot byte nao cua du lieu
that bi cham toi. KHONG nap mo hinh, KHONG tong hop tieng.

TRANG THAI (soat lai 24/9/2026): bai van XANH, tuc la GOC RE con nguyen - goi ho
so ghi xuong dia KHONG mang theo chu cua doan, va mo lai tep tu duong dan da nho
thi ra ban goc tren dia.

NHUNG TAC HAI DA DUOC CHAN bang duong khac: co `chuaLuu` trong giao-dien.js (16
cho) danh dau moi duong sua, thanh trang thai in "Chua luu", va Dong tep / nut x
tren tab / nut dong cua so deu hoi truoc khi bo. Nguoi dung khong con mat chu ma
khong hay biet - do la phan nguy hiem cua L3, va no da het.

=> XANH o day KHONG con nghia la "dang mat bai". No nghia la ho so van chua mang
theo chu da go. Viec con lai lon hon: co nen cho hoso-v2.json om ca noi dung
khong (tep se phinh theo so tab va do dai bai) - chua ai quyet. Dung xep bai nay
vao "loi dang bao dong" khi doc bang ket qua.
"""
# --- dat goc du an tu vi tri tep nay (bai nam trong kiem/) ---
import os as _os, sys as _sys
from pathlib import Path as _Path
_os.environ.setdefault('GIONGVIET_GOC', str(_Path(__file__).resolve().parent.parent))
_sys.path.insert(0, _os.environ['GIONGVIET_GOC'])
# --- het shim ---
import hashlib
import io
import json
import os
import sys
import tempfile
from pathlib import Path

# Goc du an: do nguoc tu thu muc hien hanh, KHONG viet cung duong dan.
_GOC = None
for _p in [Path(os.environ.get("GIONGVIET_GOC", Path.cwd())), *Path.cwd().parents]:
    if (Path(_p) / "DocCongDuc.py").exists():
        _GOC = Path(_p).resolve()
        break
if _GOC is None:
    print("Khong tim thay goc du an (DocCongDuc.py). Chay tu trong thu muc du an.")
    sys.exit(2)
sys.path.insert(0, str(_GOC))
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8")

T = Path(tempfile.mkdtemp(prefix="gd-l3-"))

import kho_cau_hinh

import DocCongDuc as engine
from giaodien_moi import ho_so_v2 as H
from giaodien_moi import luu_tep
from giaodien_moi.cau_noi_moi import ApiMoi

# PHAI dat SAU khi import engine: DocCongDuc goi dat_goc(BASE_DIR) ngay luc nap
# module, dat truoc thi bi de len va kho lai tro vao thu muc du an that.
kho_cau_hinh.dat_goc(T)
H.TEP = T / "hoso-v2.json"

loi = 0


def ok(dk, nhan, them=""):
    global loi
    print(f"  {'ĐẠT ' if dk else 'LỆCH'} {nhan}{'  →  ' + str(them) if them else ''}")
    if not dk:
        loi += 1


def md5(p: Path) -> str:
    return hashlib.md5(p.read_bytes()).hexdigest()


print(f"Goc du an : {_GOC}")
print(f"Thu muc tam: {T}")
print(f"Kho tro vao: {kho_cau_hinh.goc()}")

# ---------------------------------------------------------------------------
# A. Goi ma giao dien GUI SANG khi nguoi dung vua go sua mot doan.
#    Chuoi duoi day chep NGUYEN VAN tu JSON.stringify(phanCanLuu()) chay
#    trong trinh duyet, ngay sau khi go de len doan 1 va doan 2.
# ---------------------------------------------------------------------------
GOI_TU_GIAO_DIEN = json.loads(r"""
{"dangDung":0,"theme":"sang","zoom":100,
 "the":{"thongbao-quoc-khanh.txt":{"11":"[hắng giọng]"}},
 "duongDan":{},"loaiTep":{},
 "hoSo":[{"ma":"bai-viet","ten":"Bài viết, văn bản","giong":"ngoc-linh",
          "chinh":{"tocDo":0,"caoDo":0,"amLuong":100},
          "tep":["thongbao-quoc-khanh.txt","bai-viet-nghe-lai.docx"],"dangXem":0},
         {"ma":"thong-bao","ten":"Thông báo ngắn","giong":"xuan-vinh",
          "chinh":{"tocDo":10,"caoDo":0,"amLuong":100},
          "tep":["thongbao-phun-thuoc.txt"],"dangXem":0}]}
""")

print("\n--- A. Goi ho so ghi xuong dia co mang theo chu khong? ---")
ok(H.luu(GOI_TU_GIAO_DIEN) is True, "ho_so_v2.luu tra True")
noi_dung_tep = engine.doc_tep_cau_hinh(H.TEP)   # kho SQLite hoac tep roi
print(f"  Cho ghi that: {'kho ' + str(kho_cau_hinh.goc() / kho_cau_hinh.TEN_KHO) if (kho_cau_hinh.goc() / kho_cau_hinh.TEN_KHO).exists() else str(H.TEP)}")
print("  --- nguyen van hoso-v2.json ---")
for dong in noi_dung_tep.splitlines():
    print("  | " + dong)
print("  --- het ---")
ok("Nội dung cụ Tám vừa gõ" not in noi_dung_tep,
   "tep KHONG chua chu nguoi dung vua go")
ok(not any(k in noi_dung_tep for k in ("\"doan\"", "\"chu\"")),
   "tep KHONG co khoa doan/chu nao")
print(f"  (cac khoa cap 1: {sorted(json.loads(noi_dung_tep).keys())})")
print(f"  (cac khoa moi ho so: {sorted(json.loads(noi_dung_tep)['hoSo'][0].keys())})")

# ---------------------------------------------------------------------------
# B. Vong doi that: mo tep -> go sua -> luu ho so -> mo lai
# ---------------------------------------------------------------------------
print("\n--- B. Mo tep, go sua, dong chuong trinh, mo lai ---")
tep_goc = T / "thongbao.txt"
tep_goc.write_text(
    "THÔNG BÁO LỊCH NGHỈ LỄ\n"
    "Kính gửi toàn thể bà con trong xóm.\n"
    "Chùa nghỉ từ ngày 2 tháng 9.\n",
    encoding="utf-8")
md5_truoc = md5(tep_goc)

# Doc tep bang CHINH ham cua ung dung. moi_doc_tep khong dung `self` nen goi
# duoc voi mot self gia — khoi phai dung day dong co (khong nap mo hinh).
class _Gia:
    pass


kq_mo = ApiMoi.moi_doc_tep(_Gia(), str(tep_goc))
doan = kq_mo["doan"]
print(f"  Mo tep: {kq_mo['ten']}, {len(doan)} doan")
print(f"  Doan 1 luc moi mo : {doan[0]['chu']!r}")

# Nguoi dung go sua — day la thu chuDangGo() lam: chep vao TAI_LIEU trong RAM.
doan[0] = dict(doan[0], chu="THÔNG BÁO NGHỈ LỄ — CỤ TÁM SỬA CHO CHỮ TO DỄ ĐỌC")
print(f"  Doan 1 sau khi go  : {doan[0]['chu']!r}")

# Giao dien goi henLuuHoSo() -> moi_luu_ho_so(phanCanLuu()). Goi do co dung
# hinh dang o phan A: co duongDan, khong co doan.
goi_khi_dong = {
    "dangDung": 0, "theme": "sang", "zoom": 100, "the": {},
    "duongDan": {"thongbao.txt": str(tep_goc)},
    "loaiTep": {"thongbao.txt": "vanban"},
    "hoSo": [{"ma": "bai-viet", "ten": "Bài viết, văn bản", "giong": "ngoc-linh",
              "chinh": {"tocDo": 0, "caoDo": 0, "amLuong": 100},
              "tep": ["thongbao.txt"], "dangXem": 0}],
}
ok(H.luu(goi_khi_dong) is True, "luu ho so luc dong chuong trinh")
ok("CỤ TÁM SỬA" not in engine.doc_tep_cau_hinh(H.TEP),
   "chu vua go KHONG nam trong hoso-v2.json")

# --- khoi dong lai ---
ho_so_doc_lai = H.doc()
duong_nho = ho_so_doc_lai["duongDan"]["thongbao.txt"]
print(f"  Lan chay sau, duong dan nho lai: {duong_nho}")
kq_mo_lai = ApiMoi.moi_doc_tep(_Gia(), duong_nho)   # moLaiTepDangXem lam viec nay
doan_mo_lai = kq_mo_lai["doan"]
print(f"  Doan 1 khi mo lai  : {doan_mo_lai[0]['chu']!r}")

ok(doan_mo_lai[0]["chu"] != doan[0]["chu"], "chu da go KHONG con nua")
ok(doan_mo_lai[0]["chu"] == "THÔNG BÁO LỊCH NGHỈ LỄ",
   "man hinh quay ve dung ban goc", doan_mo_lai[0]["chu"])
ok(md5(tep_goc) == md5_truoc, "tep tren dia khong he bi ghi", md5_truoc[:12])

# ---------------------------------------------------------------------------
# C. Ctrl+S co cuu duoc khong?
# ---------------------------------------------------------------------------
print("\n--- C. Ctrl+S (moi_luu_van_ban -> luu_tep.luu) ---")
noi_dung_da_sua = "\n".join(d["chu"] for d in doan)
ban_moi = luu_tep.luu(T / "thongbao.txt", noi_dung_da_sua, da_la_ban_cua_ta=False)
print(f"  Ctrl+S ghi ra      : {ban_moi}")
ok(ban_moi != tep_goc, "Ctrl+S de ra tep MOI, khong de len ban goc")
ok("CỤ TÁM SỬA" in ban_moi.read_text(encoding="utf-8"),
   "ban moi CO chu da go")
ok(ho_so_doc_lai["duongDan"]["thongbao.txt"] == str(tep_goc),
   "nhung duong dan trong ho so van tro vao ban GOC",
   ho_so_doc_lai["duongDan"]["thongbao.txt"])
kq_sau_ctrl_s = ApiMoi.moi_doc_tep(_Gia(), ho_so_doc_lai["duongDan"]["thongbao.txt"])
print(f"  Mo lai theo ho so  : {kq_sau_ctrl_s['doan'][0]['chu']!r}")
ok("CỤ TÁM SỬA" not in kq_sau_ctrl_s["doan"][0]["chu"],
   "du da Ctrl+S, mo lai van ra ban goc")

print(f"\nTONG: {loi} lech")
sys.exit(1 if loi else 0)
