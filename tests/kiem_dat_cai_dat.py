# -*- coding: utf-8 -*-
"""Bai canh: CHAY THAT ApiMoi.moi_dat_cai_dat - cua giao dien goi vao.

LOAI_BAI = "canh"   -> xanh la tot.

VI SAO CO BAI NAY. Bay o chinh trong man Cai dat deu di qua DUNG MOT phuong
thuc: moi_dat_cai_dat(khoa, gia_tri). Truoc bai nay, moi bai kiem quanh no
chi SOI MA NGUON bang ast - khong bai nao goi no. Toi da kiem tung bo phan
(khoa_so_nguyen, khoa_so_thuc, _dung_lai_playlist_moi, cai_dat.du_lieu) roi
tuong the la du; nhung chinh cai ham noi chung lai voi nhau thi chua ai chay.
Day la lan thu BA cung mot bay trong mot mach viec: ma chua chay thi chua
biet no co chay duoc khong.

AN TOAN: engine.save_config GHI THAT xuong dia, nen bai keo engine.BASE_DIR
va CONFIG_FILE ve tempfile.mkdtemp TRUOC khi goi. Khong nap mo hinh VieNeu,
khong goi ffplay. Co phep tu chung minh o muc cuoi.
"""
LOAI_BAI = "canh"
# --- dat goc du an tu vi tri tep nay ---
import os as _os, sys as _sys
from pathlib import Path as _Path
_os.environ.setdefault('GIONGVIET_GOC', str(_Path(__file__).resolve().parent.parent))
_sys.path.insert(0, _os.environ['GIONGVIET_GOC'])
# --- het shim ---
import io
import shutil
import sys
import tempfile
from pathlib import Path

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8",
                              line_buffering=True)

TAM = Path(tempfile.mkdtemp(prefix="kiem_datcaidat_"))
_os.environ["GIONGVIET_DATA"] = str(TAM)

import DocCongDuc as engine                                     # noqa: E402
from giaodien_moi.cau_noi_moi import ApiMoi                      # noqa: E402
from giaodien_moi import cau_noi_moi                             # noqa: E402

engine.BASE_DIR = TAM
engine.CONFIG_FILE = TAM / "cauhinh.ini"

_lech = []


def ok(dieu, nhan, them=""):
    print(("  ĐẠT  " if dieu else "  LỆCH ") + nhan
          + (f"  →  {them}" if them != "" else ""))
    if not dieu:
        _lech.append(nhan)


class _LoaGia:
    def __init__(self):
        self.da_dung = 0
        self.playlist = None
        self.index = 0
        self.dang_doc = False
        self.cfg_nhan = []
        self.co_giu_vi_tri = None

    def dung(self, giu_vi_tri=False):
        # PHAI nhan giu_vi_tri y nhu bo phat that. Ban truoc vat ghi chep nay
        # chi co dung(self), nen khi _dung_lai_playlist_moi doi sang goi
        # dung(giu_vi_tri=True) thi bai nay vo bang TypeError - va vo LANG LE:
        # khong mot dong stdout nao, bang ket qua chi ghi "(khong co dau ra)".
        # Cai cong truoc khi push bat duoc, con toi thi khong chay lai bai nay
        # sau khi sua ma nguon.
        self.da_dung += 1
        self.co_giu_vi_tri = giu_vi_tri
        if not giu_vi_tri:
            self.index = 0

    def dat_playlist(self, pl, cfg):
        self.playlist = list(pl)

    def cap_nhat_cfg(self, cfg):
        self.cfg_nhan.append(dict(cfg))


class _Thu(ApiMoi):
    """Ke thua de cac staticmethod cua ApiMoi phan giai dung.

    KHONG goi ApiMoi.__init__ - ham do nap mo hinh, dung hang chuc giay.
    """

    def __init__(self, cfg, records, noidung):
        self._cfg = cfg
        self._tuy_chon = {"theme": "light", "zoom": 100, "thu_muc_xuat": ""}
        self._records = records
        self._canh_bao = []
        self._noidung = noidung
        self._tudien = {}
        self._loai_tai_lieu = "congduc"
        self._bo_doc = _LoaGia()
        self._playlist = []
        self._doan = []
        self._doan_cua_mau = []
        self._trong_so_cache = {}
        self._moc_phat = None
        self._nghe_rieng = False

    def _nap_truoc_mau_dau(self, vi_tri=None):
        # Chan: ban that hen Timer 150 ms roi TONG HOP TIENG THAT.
        pass


def _cau_hinh_goc() -> dict:
    (TAM / "cauhinh.ini").write_text(
        "[GiongDoc]\n"
        "phong_cach = Tin tức - thông báo\n"
        "\n[DocLienTuc]\n"
        "nghi_giua_nguoi = 1.30\n"
        "nghi_giua_nhom = 2.50\n"
        "so_nguoi_moi_nhom = 20\n"
        "nghi_giua_doan = 0.80\n"
        "nhan_manh_tien = 0\n",
        encoding="utf-8-sig")
    return engine.load_config()


DS = TAM / "danhsach.txt"
DS.write_text(
    "\n".join(f"Nguyễn Văn {i:02d}\t100.000" for i in range(1, 31)) + "\n",
    encoding="utf-8")
records, _cb = engine.parse_data_file(DS)
noidung = engine.NoiDung()

api = _Thu(_cau_hinh_goc(), records, noidung)
api._dung_lai_playlist_moi()      # co playlist ban dau de so sanh

# =============================================================================
print("=== A. Goi THAT moi_dat_cai_dat voi khoa SO NGUYEN ===")
try:
    kq = api.moi_dat_cai_dat("so_nguoi_nhom", 5)
    chay, vi_sao = True, ""
except Exception as e:                      # noqa: BLE001
    kq, chay, vi_sao = None, False, f"{type(e).__name__}: {e}"
ok(chay, "chay khong nem ngoai le", vi_sao or "sach")
if not chay:
    print("\nĐỎ — cửa giao diện gọi vào không chạy được")
    shutil.rmtree(TAM, ignore_errors=True)
    sys.exit(1)

ok(kq is not None, "tra ve bang cai dat, khong tra None (None = giao dien bao "
                   "'Chua doi duoc thiet lap nay')")
ok(isinstance(kq, dict) and "nhom" in kq, "bang tra ve dung dang man Cai dat")
ok(api._cfg["so_nguoi_nhom"] == 5, "cau hinh TRONG BO NHO da doi",
   api._cfg["so_nguoi_nhom"])
ok((TAM / "cauhinh.ini").read_text(encoding="utf-8-sig").find("= 5") > 0
   or "so_nguoi_moi_nhom = 5" in (TAM / "cauhinh.ini").read_text(encoding="utf-8-sig"),
   "da GHI XUONG DIA, khong chi doi trong bo nho")
ok(api._bo_doc.cfg_nhan and api._bo_doc.cfg_nhan[-1]["so_nguoi_nhom"] == 5,
   "bo phat tieng duoc bao cau hinh moi")

_dai = [m["stt"] for m in api._playlist if m["loai"] == "nguoi"
        and abs(m["nghi"] - api._cfg["nghi_nhom"]) < 1e-9]
ok(len(_dai) == 6, "playlist da dung lai theo so moi (30 nguoi / 5 = 6 cho nghi)",
   f"{len(_dai)} cho: {_dai}")

# =============================================================================
print("\n=== B. Goi THAT voi khoa SO THUC - nhanh khac han ===")
_truoc = sum(m["nghi"] for m in api._playlist)
kq2 = api.moi_dat_cai_dat("nghi_nhom", 6.0)
ok(kq2 is not None, "nhan khoa so thuc, khong tra None")
ok(api._cfg["nghi_nhom"] == 6.0, "gia tri so THUC khong bi cat cut thanh 6",
   api._cfg["nghi_nhom"])
_sau = sum(m["nghi"] for m in api._playlist)
ok(_sau > _truoc, "playlist dung lai: tong khoang lang dai hon",
   f"{_truoc:.2f}s → {_sau:.2f}s")

# =============================================================================
print("\n=== C. Kep hai dau NGAY TRONG ham, khong tin trinh duyet ===")
for khoa, vao, mong in (("so_nguoi_nhom", 0, 1), ("so_nguoi_nhom", 9999, 50),
                        ("nghi_nhom", -5, 0.0), ("nghi_nhom", 99, 8.0)):
    api.moi_dat_cai_dat(khoa, vao)
    ok(api._cfg[khoa] == mong, f"{khoa} = {vao} -> kep ve {mong}",
       api._cfg[khoa])

print("\n  Gia tri vo nghia thi TU CHOI, khong ghi bua:")
_giu = dict(api._cfg)
for khoa, vao in (("so_nguoi_nhom", "abc"), ("nghi_nhom", None),
                  ("nghi_nhom", "x")):
    r = api.moi_dat_cai_dat(khoa, vao)
    ok(r is None, f"{khoa} = {vao!r} -> tra None (giao dien bao cho nguoi dung)")
    ok(api._cfg[khoa] == _giu[khoa], f"  va KHONG ghi gi len {khoa}",
       api._cfg[khoa])

# =============================================================================
print("\n=== D. Khoa la thi tu choi han ===")
for khoa in ("theme", "zoom", "khoa_khong_ton_tai", "vieneu_voice_id"):
    ok(api.moi_dat_cai_dat(khoa, 1) is None,
       f"khoa {khoa!r} bi tu choi - man Cai dat tu giu theme/zoom")

# =============================================================================
print("\n=== E. Dat lai DUNG gia tri dang co thi khong dung lai playlist ===")
# Dung lai playlist la DUNG bo phat tieng. Lam viec do khi gia tri khong doi
# la cat ngang nguoi ta dang nghe ma khong duoc gi.
api.moi_dat_cai_dat("nghi_nhom", 4.0)
_dung_truoc = api._bo_doc.da_dung
api.moi_dat_cai_dat("nghi_nhom", 4.0)
ok(api._bo_doc.da_dung == _dung_truoc,
   "dat lai cung gia tri -> KHONG dung bo phat tieng lan nua",
   f"{_dung_truoc} → {api._bo_doc.da_dung}")

# So thuc phai so co SAI SO: 0.1+0.2 != 0.3 trong dau may.
api.moi_dat_cai_dat("nghi_cau", 0.3)
_d2 = api._bo_doc.da_dung
api.moi_dat_cai_dat("nghi_cau", 0.1 + 0.2)
ok(api._bo_doc.da_dung == _d2,
   "0.1+0.2 duoc coi la BANG 0.3 -> khong dung lai vo co",
   f"{_d2} → {api._bo_doc.da_dung}")

# =============================================================================
print("\n=== F. Bay o chinh deu di qua duoc cua nay ===")
from giaodien import cai_dat                                     # noqa: E402
_tat_ca = {}
for _che in ("congduc", "vanban"):
    for m in [x for n in cai_dat.du_lieu(api._cfg, api._tuy_chon, _che, "")["nhom"]
              if n["ma"] == "doc" for x in n["muc"]]:
        if m["kieu"] in ("songuyen", "sothuc"):
            _tat_ca[m["khoa"]] = m
ok(len(_tat_ca) == 7, "co du bay o chinh", sorted(_tat_ca))
for _k, _m in sorted(_tat_ca.items()):
    _giua = (_m["nhoNhat"] + _m["lonNhat"]) / 2
    if _m["kieu"] == "songuyen":
        _giua = int(_giua)
    _r = api.moi_dat_cai_dat(_k, _giua)
    ok(_r is not None and abs(float(api._cfg[_k]) - float(_giua)) < 1e-9,
       f"  {_k} = {_giua} di qua duoc", api._cfg.get(_k))

# =============================================================================
print("\n=== G. Tu chung minh: khong cham cau hinh that ===")
THAT = Path(_os.environ['GIONGVIET_GOC'])
for ten in ("cauhinh.ini", "noidung.ini", "congduc.txt", "giongviet.db"):
    ok(not (THAT / ten).exists(), f"{ten} o goc du an khong bi tao ra")
ok(str(engine.CONFIG_FILE).startswith(str(TAM)),
   "engine.CONFIG_FILE tro vao thu muc tam")

shutil.rmtree(TAM, ignore_errors=True)
print("\n" + ("ĐỎ — %d chỗ lệch" % len(_lech) if _lech else "XANH — khớp hết"))
sys.exit(1 if _lech else 0)
