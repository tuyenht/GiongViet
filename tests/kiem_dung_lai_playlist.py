# -*- coding: utf-8 -*-
"""Bai canh: CHAY THAT duong dung lai playlist cua ban moi.

LOAI_BAI = "canh"   -> xanh la tot.

VI SAO CO BAI NAY. ApiMoi._dung_lai_playlist_moi() la ma MOI, nam tren duong
nguoi dung di (doi mot thiet lap trong man Cai dat), va truoc bai nay no
CHUA TUNG CHAY MOT LAN NAO. Cac bai khac chi doc van ban ma nguon cua no.
Ma chua chay thi chua biet no co chay duoc khong.

Bai nay goi THAT phuong thuc do - khong mo phong lai - roi do ba thu:

  [A] Sau khi goi, tai lieu con la "congduc" va _records con nguyen hay khong.
      Day la phep bat viec quay ve goi moi_dat_doan, thu lam tai lieu AM THAM
      bien thanh van ban thuong. Da thu dat nguoc loi vao, bai do dung.

  [B] Doi so_nguoi_nhom tu 20 xuong 5 thi so cho nghi dai PHAI khac. Bai
      kiem_so_nguoi_nhom.py da chung minh dieu nay o muc ENGINE; bai nay
      chung minh con so di tron duong qua DUNG LOP ma giao dien goi toi.

  [C] So DOAN truoc va sau khi dung lai. Cai nay khong phai phep hinh thuc:
      datCaiDat trong giao-dien.js chi lam `duLieuCaiDat = kq; ve()` - no
      KHONG xin lai danh sach doan. Trinh duyet van giu danh sach doan tu
      luc mo tep. Neu dung lai lam so doan doi thi dong thu k tren man hinh
      khong con ung voi mau thu k ben Python nua.

AN TOAN: cau hinh ghi ra thu muc tam (tempfile.mkdtemp), KHONG cham cauhinh
that cua chu du an. Khong nap mo hinh VieNeu, khong goi ffplay: bo phat tieng
duoc thay bang mot vat ghi chep. Bo dem nap truoc bi chan - no hen mot Timer
150 ms roi tong hop tieng that, dung bai do la phat tieng giua luc kiem.
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

TAM = Path(tempfile.mkdtemp(prefix="kiem_dunglai_"))
# Keo engine ve thu muc tam TRUOC khi import no, de moi duong ghi deu roi vao
# day. Thieu buoc nay la bai tu ghi len cauhinh.ini that.
_os.environ["GIONGVIET_DATA"] = str(TAM)

import DocCongDuc as engine                                    # noqa: E402
from giaodien_moi.cau_noi_moi import ApiMoi                     # noqa: E402

engine.BASE_DIR = TAM
engine.CONFIG_FILE = TAM / "cauhinh.ini"

_lech = []


def ok(dieu, nhan, them=""):
    print(("  ĐẠT  " if dieu else "  LỆCH ") + nhan
          + (f"  →  {them}" if them != "" else ""))
    if not dieu:
        _lech.append(nhan)


# ---------------------------------------------------------------- vat ghi chep
class _LoaGia:
    """Thay bo phat tieng. Chi ghi lai minh da bi goi gi, khong phat gi ca."""

    def __init__(self):
        self.da_dung = 0
        self.playlist = None
        self.index = 0
        self.dang_doc = False
        self.co_giu_vi_tri = None

    def dung(self, giu_vi_tri=False):
        # GHI LAI co giu_vi_tri. Phai soi chinh cai co nay, khong phai soi
        # index sau cung: dong khoi phuc vi tri o cuoi ham tu lo index roi,
        # nen bo giu_vi_tri di ma phep van xanh - da thu dat nguoc loi va no
        # DO OAN. Cai co nay co viec rieng: bo phat that DAY "pos" len giao
        # dien ngay trong dung(), nen thieu no la giao dien nhan "doan 1"
        # trong khi nguoi ta dang o doan 121.
        self.da_dung += 1
        self.co_giu_vi_tri = giu_vi_tri
        if not giu_vi_tri:
            self.index = 0

    def dat_playlist(self, pl, cfg):
        self.playlist = list(pl)
        self.index = 0

    def cap_nhat_cfg(self, cfg):
        pass


class _Thu(ApiMoi):
    """Ke thua ApiMoi de _kieu_doan/_chu_doan (staticmethod) phan giai dung.

    KHONG goi ApiMoi.__init__: ham do nap mo hinh, dung hang chuc giay va
    doi co VieNeu tren dia. Bai nay chi can MOT phuong thuc, nen dung day
    du thuoc tinh ma phuong thuc ay cham toi - khong hon.
    """

    def __init__(self, cfg, records, noidung):
        self._cfg = cfg
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
        self.so_lan_nap_truoc = 0

    def _nap_truoc_mau_dau(self, vi_tri=None):
        # CHAN co y. Ban that hen mot threading.Timer 150 ms roi tong hop
        # tieng. Dung bai do la giua luc kiem may phat tieng that - va bai se
        # ket thuc truoc khi Timer kip chay, de lai mot luong mo hinh lo lung.
        self.so_lan_nap_truoc += 1


def _ghi_cau_hinh(n_nhom: int) -> dict:
    (TAM / "cauhinh.ini").write_text(
        "[GiongDoc]\n"
        "phong_cach = Tin tức - thông báo\n"
        "\n[DocLienTuc]\n"
        "nghi_giua_nguoi = 1.30\n"
        "nghi_giua_nhom = 2.50\n"
        f"so_nguoi_moi_nhom = {n_nhom}\n"
        "nghi_giua_doan = 0.80\n"
        "nhan_manh_tien = 0\n",
        encoding="utf-8-sig")
    return engine.load_config()


def _dem_nghi_dai(api) -> list:
    """STT cua nhung mau nguoi duoc nghi DAI (bang nghi_nhom) sau khi doc."""
    return [m["stt"] for m in api._playlist
            if m["loai"] == "nguoi"
            and abs(m["nghi"] - api._cfg["nghi_nhom"]) < 1e-9]


# ---------------------------------------------------------------- dung du lieu
DS = TAM / "danhsach.txt"
# Dau TAB, khong phai dau phay: parse_data_file lay tab lam ranh ten/so
# tien. Dung dau phay thi CA 45 dong bi doc thanh "tieude" - da do that,
# Counter({"tieude": 45}) - roi moi phep ve nhip doc deu ra 0, bai do oan
# cho ma that. Chinh bai kiem_so_nguoi_nhom.py cung ghi chu dung cho nay.
DS.write_text(
    "\n".join(f"Nguyễn Văn {i:02d}\t100.000"
              for i in range(1, 46)) + "\n",
    encoding="utf-8")
records, canh_bao = engine.parse_data_file(DS)
so_nguoi = len([r for r in records if r["kind"] == "nguoi"])

print("=== Du lieu thu ===")
ok(so_nguoi == 45, "doc duoc 45 dong nguoi",
   f"{len(records)} ban ghi, {len(canh_bao)} canh bao")

noidung = engine.NoiDung()

# =============================================================================
print("\n=== A. Goi THAT _dung_lai_playlist_moi - no co chay duoc khong ===")
cfg20 = _ghi_cau_hinh(20)
api = _Thu(cfg20, records, noidung)
try:
    api._dung_lai_playlist_moi()
    chay_duoc = True
    vi_sao = ""
except Exception as e:                      # noqa: BLE001 - can biet het
    chay_duoc, vi_sao = False, f"{type(e).__name__}: {e}"
ok(chay_duoc, "chay khong nem ngoai le", vi_sao or "sach")

if not chay_duoc:
    print("\nĐỎ — đường này không chạy được, các phép sau vô nghĩa")
    shutil.rmtree(TAM, ignore_errors=True)
    sys.exit(1)

ok(len(api._playlist) > 0, "dung ra playlist co mau", f"{len(api._playlist)} mẩu")
ok(api._bo_doc.playlist is not None,
   "co day playlist sang bo phat tieng", "da nhan")
ok(api._bo_doc.da_dung >= 1, "co DUNG bo phat truoc khi thay playlist",
   f"{api._bo_doc.da_dung} lan")

print("\n  Phep bat viec quay ve goi moi_dat_doan:")
# PHAI moi _doan len truoc khi goi. Ban truoc kiem tren mot doi tuong co
# _doan RONG: khi ay nhanh lui `elif self._doan:` cung khong chay, nen
# khong gi bi dung toi va phep van DAT du loi da nam san - DO OAN. Da thu
# dat nguoc loi vao va hai phep ay bao dat.
api2 = _Thu(_ghi_cau_hinh(20), records, noidung)
api2._doan = [{"kieu": "body", "chu": "dong moi san"}]
api2._dung_lai_playlist_moi()
ok(api2._loai_tai_lieu == "congduc",
   "tai lieu VAN la cong duc sau khi dung lai", api2._loai_tai_lieu)
ok(len(api2._records) == len(records),
   "_records con nguyen - khong bi xoa", f"{len(api2._records)} ban ghi")
ok(len(api2._doan) > 1,
   "danh sach doan duoc dung lai tu playlist, khong giu dong moi san",
   f"{len(api2._doan)} doan")

# =============================================================================
print("\n=== B. Con so di tron duong qua lop giao dien goi toi ===")
dai20 = _dem_nghi_dai(api)
doan20 = len(api._doan)
print(f"      20 nguoi/nhom: nghi dai tai STT {dai20} → {len(dai20)} lan "
      f"· {doan20} doan")

cfg5 = _ghi_cau_hinh(5)
api._cfg = cfg5
api._dung_lai_playlist_moi()
dai5 = _dem_nghi_dai(api)
doan5 = len(api._doan)
print(f"       5 nguoi/nhom: nghi dai tai STT {dai5} → {len(dai5)} lan "
      f"· {doan5} doan")

ok(len(dai5) > len(dai20),
   "nhom nho hon -> nghi dai nhieu lan hon",
   f"{len(dai20)} → {len(dai5)} lan")
ok(dai20 != dai5, "cho nghi dai dich chuyen that su")
ok(len(dai5) == so_nguoi // 5,
   f"nghi dai dung moi 5 nguoi mot lan ({so_nguoi}//5)", len(dai5))

# =============================================================================
print("\n=== B4. Khoang nghi (SO THUC) cung di tron duong ===")
# Phep [B] o tren do so_nguoi_nhom - khoa SO NGUYEN. Bon khoang nghi la so
# THUC va di qua mot NHANH KHAC trong moi_dat_cai_dat, nen phai do rieng.
# Khong do thi nhanh so thuc lai thanh ma chua ai chay - dung cai bay bai nay
# duoc viet ra de chan.
def _ghi_cau_hinh_nghi(nghi_nhom: float) -> dict:
    (TAM / "cauhinh.ini").write_text(
        "[GiongDoc]\n"
        "phong_cach = Tin t\u1ee9c - th\u00f4ng b\u00e1o\n"
        "\n[DocLienTuc]\n"
        "nghi_giua_nguoi = 1.30\n"
        f"nghi_giua_nhom = {nghi_nhom}\n"
        "so_nguoi_moi_nhom = 10\n"
        "nghi_giua_doan = 0.80\n"
        "nhan_manh_tien = 0\n",
        encoding="utf-8-sig")
    return engine.load_config()


api3 = _Thu(_ghi_cau_hinh_nghi(2.5), records, noidung)
api3._dung_lai_playlist_moi()
lang25 = sum(m["nghi"] for m in api3._playlist)
sau25 = len([m for m in api3._playlist if m["loai"] == "nguoi"
             and abs(m["nghi"] - 2.5) < 1e-9])

api3._cfg = _ghi_cau_hinh_nghi(6.0)
api3._dung_lai_playlist_moi()
lang60 = sum(m["nghi"] for m in api3._playlist)
sau60 = len([m for m in api3._playlist if m["loai"] == "nguoi"
             and abs(m["nghi"] - 6.0) < 1e-9])

print(f"      nghi_nhom 2,5 giay: tong lang {lang25:.2f}s · {sau25} mau nghi 2,5s")
print(f"      nghi_nhom 6,0 giay: tong lang {lang60:.2f}s · {sau60} mau nghi 6,0s")
ok(lang60 > lang25, "nghi lau hon -> tong khoang lang dai hon",
   f"{lang25:.2f}s → {lang60:.2f}s")
ok(sau25 > 0 and sau25 == sau60,
   "so cho nghi khong doi, chi do dai cho nghi doi", f"{sau25} = {sau60}")
ok(api3._cfg["nghi_nhom"] == 6.0,
   "cau hinh nap dung so THUC, khong bi cat cut thanh 6", api3._cfg["nghi_nhom"])


print("\n=== B5. nghi_doan (o chinh thu bay) cung di tron duong ===")
# O nay duoc them sau cung. Khi them, toi chi kiem no HIEN RA trong man Cai
# dat chu chua do no toi playlist - tuc no la "ma chua ai chay", dung cai bay
# ca bai nay viet ra de chan. Nen do that o day.
#
# Do TONG KHOANG LANG chu khong dem so mau: o 2,5 giay thi nghi_doan trung
# voi nghi_nhom (cung 2,50) nen phep dem mau se bat ca hai loai, doc ra so
# vo nghia.
def _ghi_cau_hinh_doan(nghi_doan: float) -> dict:
    (TAM / "cauhinh.ini").write_text(
        "[GiongDoc]\n"
        "phong_cach = Tin t\u1ee9c - th\u00f4ng b\u00e1o\n"
        "\n[DocLienTuc]\n"
        "nghi_giua_nguoi = 1.30\n"
        "nghi_giua_nhom = 2.50\n"
        "so_nguoi_moi_nhom = 10\n"
        f"nghi_giua_doan = {nghi_doan}\n"
        "nhan_manh_tien = 0\n",
        encoding="utf-8-sig")
    return engine.load_config()


# Loi dan PHAI bat, va phai co nhieu doan: nghi_doan chi chen GIUA hai doan
# cua loi dan. Loi dan tat thi doi no khong thay gi - va bai se do oan.
_nd = engine.NoiDung()
_nd.dau_bat, _nd.dau_text = True, "Doan mot.\n\nDoan hai.\n\nDoan ba."
_nd.cuoi_bat, _nd.cuoi_text = True, "Ket mot.\n\nKet hai."

api4 = _Thu(_ghi_cau_hinh_doan(0.8), records, _nd)
api4._dung_lai_playlist_moi()
lang08 = sum(m["nghi"] for m in api4._playlist)

api4._cfg = _ghi_cau_hinh_doan(2.5)
api4._dung_lai_playlist_moi()
lang25 = sum(m["nghi"] for m in api4._playlist)

print(f"      nghi_doan 0,8 giay: tong lang {lang08:.2f}s")
print(f"      nghi_doan 2,5 giay: tong lang {lang25:.2f}s")
ok(lang25 > lang08, "nghi giua doan lau hon -> tong khoang lang dai hon",
   f"{lang08:.2f}s → {lang25:.2f}s")
ok(api4._cfg["nghi_doan"] == 2.5,
   "cau hinh nap dung so THUC", api4._cfg["nghi_doan"])


print("\n=== B6. Dung lai playlist phai GIU CHO DANG DOC ===")
# Vap that, da do: nguoi dung o mau 121 tren 208, nhich mot thiet lap trong
# man Cai dat -> bi dua ve mau 1. bo_doc.dung() mac dinh dat index = 0, ma
# ban truoc goi dung() khong doi so. Voi nguoi lon tuoi dang do theo danh
# sach 200 ten o chua thi do la mat cho, phai tim lai tu dau.
#
# Lop cha Api._dung_lai_playlist(giu_vi_tri=True) da giai dung viec nay tu
# truoc; ban moi khong mang sang.
api5 = _Thu(_ghi_cau_hinh(20), records, noidung)
api5._dung_lai_playlist_moi()
_tong = len(api5._playlist)
_o = min(40, _tong - 1)
api5._bo_doc.index = _o
api5._bo_doc.dang_doc = True
api5._cfg = _ghi_cau_hinh(5)
api5._dung_lai_playlist_moi()
print(f"      o mau {_o + 1}/{_tong} -> sau khi nhich thiet lap: "
      f"mau {api5._bo_doc.index + 1}")
ok(api5._bo_doc.index == _o, "giu dung cho dang doc",
   f"{_o + 1} → {api5._bo_doc.index + 1}")

# Gan cuoi: so mau co the doi sau khi dung lai, nen phai KEP trong pham vi -
# khong kep thi index tro ra ngoai playlist.
api5._bo_doc.index = len(api5._playlist) - 1
_cuoi = api5._bo_doc.index
api5._cfg = _ghi_cau_hinh(20)
api5._dung_lai_playlist_moi()
ok(0 <= api5._bo_doc.index < len(api5._playlist),
   "cho dang doc luon nam trong pham vi playlist moi",
   f"{api5._bo_doc.index} / {len(api5._playlist)} mau")

# KHONG tu phat lai: man Cai dat chiem toan cua so, tieng noi len trong khi
# nguoi dung khong thay bo doc la lam ho giat minh.
ok(not hasattr(api5._bo_doc, "da_phat") or not api5._bo_doc.da_phat,
   "KHONG tu phat lai sau khi dung lai playlist")

ok(api5._bo_doc.co_giu_vi_tri is True,
   "co goi dung(giu_vi_tri=True) - thieu co nay la giao dien nhan sai cho",
   api5._bo_doc.co_giu_vi_tri)


print("\n=== C. So DOAN co doi khong - giao dien KHONG xin lai danh sach ===")
# datCaiDat trong giao-dien.js chi lam `duLieuCaiDat = kq; ve()`. Neu so doan
# doi thi dong thu k tren man hinh khong con ung voi mau thu k ben Python.
print(f"      truoc {doan20} doan · sau {doan5} doan")
ok(doan20 == doan5,
   "so doan GIU NGUYEN -> danh sach tren man hinh khong lech",
   f"{doan20} = {doan5}")
ok(len(api._doan_cua_mau) == len(api._playlist),
   "moi mau co dung mot so doan", f"{len(api._doan_cua_mau)}")

ok(api.so_lan_nap_truoc == 2,
   "bo dem nap truoc bi chan dung 2 lan (khong phat tieng giua luc kiem)",
   api.so_lan_nap_truoc)

# =============================================================================
print("\n=== D. Tu chung minh: khong cham cau hinh that ===")
THAT = Path(_os.environ['GIONGVIET_GOC'])
for ten in ("cauhinh.ini", "noidung.ini", "congduc.txt"):
    ok(not (THAT / ten).exists(), f"{ten} o goc du an khong bi tao ra")
ok(str(engine.CONFIG_FILE).startswith(str(TAM)),
   "engine.CONFIG_FILE tro vao thu muc tam", str(engine.CONFIG_FILE))

shutil.rmtree(TAM, ignore_errors=True)
print("\n" + ("ĐỎ — %d chỗ lệch" % len(_lech) if _lech else "XANH — khớp hết"))
sys.exit(1 if _lech else 0)
