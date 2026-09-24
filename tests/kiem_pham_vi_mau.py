# -*- coding: utf-8 -*-
"""Kiem du lieu de to chu: pham vi mau + trong so doc.

Chay tren ApiMoi THAT voi playlist THAT, nhung KHONG phat tieng - khong chiem
loa cua chu du an. Khong dung tep du lieu nao (khoa_du_lieu chan het).

Day la nua Python cua bai do ui-moi/do-lech-chu-tieng.mjs: bai kia do cong
thuc to chu, bai nay kiem con so dau vao cua cong thuc do co dung khong.
"""
import io
import sys
import tempfile
from pathlib import Path

# Goc du an, tinh tu chinh vi tri tep nay. KHONG viet cung duong dan:
# kho da len GitHub, ai tai ve cho khac la vo het bo kiem.
_GOC = str(Path(__file__).resolve().parent.parent)
sys.path.insert(0, _GOC)
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8")

from giaodien import nhat_ky
from giaodien_moi import khoa_du_lieu
from giaodien_moi.cau_noi_moi import ApiMoi

# Nhat ky loi cua bai kiem di cho khac. GiongViet-loi.log la duong chan doan khi
# may chu du an tro chung; tron rac cua bai kiem vao la hong dung cong cu can
# den luc khan cap. Da vap: 15 dong loi cua bai kiem nam trong log that.
nhat_ky.TEP_LOG = Path(tempfile.gettempdir()) / "gd-kiem-loi.log"

loi = 0


def ok(dk, nhan, them=""):
    global loi
    print(f"  {'ĐẠT ' if dk else 'LỆCH'} {nhan}{'  →  ' + str(them) if them else ''}")
    if not dk:
        loi += 1


khoa_du_lieu.khoa()          # BAT BUOC: ApiMoi khong tu khoa nua
api = ApiMoi()
ok(khoa_du_lieu.dang_khoa(), "bai kiem tu bat khoa ghi du lieu")

DOAN_DAI = ("Kính gửi toàn thể cán bộ, nhân viên của công ty. "
            "Nghỉ từ 31/8/2026 đến hết 2/9/2026, tổng đài 1900 6868. "
            "Trân trọng thông báo.")
DOAN = [
    {"kieu": "head", "chu": "THÔNG BÁO NGHỈ LỄ"},
    {"kieu": "blank", "chu": ""},
    {"kieu": "body", "chu": DOAN_DAI},
    {"kieu": "body", "chu": "Một dòng ngắn."},
]

print("\n--- A. Dung playlist: doan dai phai bi cat thanh nhieu mau ---")
# Ha nguong cat trong BO NHO (khong ghi dia - khoa_du_lieu chan) de doan mau
# 126 ky tu bi cat that. De nguyen 280 thi ca doan gon trong mot mau va bai
# kiem khong cham vao duoc cho can kiem.
api._cfg["so_ky_tu"] = 60
kq = api.moi_dat_doan(DOAN)
ok(kq["soDoan"] == 4, "dung 4 doan", kq["soDoan"])
ok(kq["soMau"] >= 5, f"cat ra {kq['soMau']} mau (doan rong khong vao playlist)")
mau3 = api._mau_cua_doan(3)
ok(len(mau3) >= 3, f"doan 3 rieng no da co {len(mau3)} mau")

print("\n--- B. Moi mau mang theo vi tri ky tu trong doan goc ---")
ok(all("tu" in s and "den" in s for s in api._playlist), "mau nao cung co tu/den")
ok(all(s["tu"] < s["den"] for s in api._playlist), "tu luon nho hon den")
lien_tuc = all(mau3[i]["den"] <= mau3[i + 1]["tu"] + 1 for i in range(len(mau3) - 1))
ok(lien_tuc, "cac mau noi tiep nhau, khong chong len nhau")
ok(mau3[0]["tu"] == 0, "mau dau bat dau tu ky tu 0", mau3[0]["tu"])
ok(mau3[-1]["den"] <= len(DOAN_DAI), "mau cuoi khong vuot qua doan",
   f'{mau3[-1]["den"]} / {len(DOAN_DAI)}')

print("\n--- C. Vi tri phai dem tren chu HIEN THI, khong phai chu da chuan hoa ---")
# Neu con dem tren chuoi da chuan hoa so dien thoai thi den se vot qua do dai
# that cua doan - do chinh la loi cu.
ok(all(s["den"] <= len(DOAN_DAI) for s in mau3),
   "khong mau nao tro ra ngoai doan goc")
lay = DOAN_DAI[mau3[1]["tu"]:mau3[1]["den"]].strip()
ok(lay.startswith("Nghỉ"), "cat dung chu o mau 2", repr(lay[:24]))

print("\n--- D. Trong so doc: chu co so phai nang hon han chu thuong ---")
ts = api._trong_so_doc(3, DOAN_DAI)
tu_hien = DOAN_DAI.split()
ok(len(ts) == len(tu_hien), f"du trong so cho {len(tu_hien)} chu", len(ts))
i_ngay = tu_hien.index("31/8/2026")
i_thuong = tu_hien.index("Kính")
ok(ts[i_ngay] > ts[i_thuong] * 5,
   "'31/8/2026' nang hon 'Kính' nhieu lan",
   f"{ts[i_ngay]} am tiet vs {ts[i_thuong]}")
ok(all(x >= 1 for x in ts), "khong chu nao trong so 0")

print("\n--- E. So dien thoai giu duoc ngu canh (khong tach thanh so luong) ---")
# "1900 6868" doc kieu so dien thoai la 8 am tiet; doc kieu so luong la 11.
i1900 = tu_hien.index("1900")
tong_sdt = ts[i1900] + ts[i1900 + 1]
ok(tong_sdt <= 9, f"'1900 6868' ra {tong_sdt} am tiet (kieu so dien thoai)")

print("\n--- F. Pham vi mau va trong so dung CUNG mot thuoc ---")
# Day la loi da vap: pham vi tinh theo ky tu con moc tung chu tinh theo am
# tiet, tron hai thuoc la chu nhay sai cho (do duoc 1,07 giay).
i_mau = api._playlist.index(mau3[1])
pv = api._pham_vi_mau(i_mau, 3)
ok("tu" in pv and "den" in pv, "co pham vi", pv.get("tu"))
ok("trongSo" in pv and len(pv["trongSo"]) == len(tu_hien), "co trong so kem theo")
truoc = len(mau3[0]["goc"].split())
rong = len(mau3[1]["goc"].split())
tong = sum(ts)
mong_doi = sum(ts[:truoc]) / tong
ok(abs(pv["tu"] - mong_doi) < 1e-5,
   "tu = ti le AM TIET cua cac chu dung truoc",
   f'{pv["tu"]:.4f} vs {mong_doi:.4f}')
mong_doi_den = sum(ts[:truoc + rong]) / tong
ok(abs(pv["den"] - mong_doi_den) < 1e-5, "den cung thuoc do",
   f'{pv["den"]:.4f} vs {mong_doi_den:.4f}')

print("\n--- G. Cac mau phu kin doan, khong ho khong chong ---")
pvs = [api._pham_vi_mau(api._playlist.index(s), 3) for s in mau3]
ok(abs(pvs[0]["tu"]) < 1e-6, "mau dau bat dau tu 0", pvs[0]["tu"])
ok(abs(pvs[-1]["den"] - 1.0) < 1e-6, "mau cuoi ket thuc o 1", pvs[-1]["den"])
noi = all(abs(pvs[i]["den"] - pvs[i + 1]["tu"]) < 1e-6 for i in range(len(pvs) - 1))
ok(noi, "mau sau bat dau dung cho mau truoc ket thuc")

print("\n--- H. Doan mot mau thi phu tron 0..1 ---")
i4 = api._playlist.index(api._mau_cua_doan(4)[0])
pv4 = api._pham_vi_mau(i4, 4)
ok(abs(pv4["tu"]) < 1e-6 and abs(pv4["den"] - 1.0) < 1e-6,
   "doan ngan: tu 0 den 1", f'{pv4["tu"]}..{pv4["den"]}')

print("\n--- I. Nho lai ket qua, khong tinh lai moi lan day tin ---")
api._trong_so_cache.clear()
api._trong_so_doc(3, DOAN_DAI)
ok(3 in api._trong_so_cache, "co nho lai theo so doan")
ok(api._trong_so_doc(3, DOAN_DAI) is api._trong_so_cache[3], "lan sau tra dung ban da nho")
# Nap van ban KHAC roi hoi lai doan 3: phai ra trong so cua van ban moi.
# (Khong kiem cache rong: dat_playlist day trang thai ngay, nen cache duoc nap
# lai trong cung mot nhip - dieu do dung, mien la du lieu la cua van ban moi.)
cu = list(api._trong_so_doc(3, DOAN_DAI))
api.moi_dat_doan([{"kieu": "body", "chu": "Một."},
                  {"kieu": "body", "chu": "Hai."},
                  {"kieu": "body", "chu": "Ba bốn năm sáu bảy."}])
moi = api._trong_so_doc(3, "Ba bốn năm sáu bảy.")
ok(moi != cu and len(moi) == 5, "nap van ban moi thi trong so tinh lai", moi)

print("\n--- K. Tu do do tre ra loa ---")
import time as _t
from giaodien_moi import cau_noi_moi as C

api.moi_dat_doan(DOAN)
ok(api._tre_ms == C.TRE_PHAT_MAC_DINH_MS,
   f"chua do lan nao thi dung mac dinh {C.TRE_PHAT_MAC_DINH_MS} ms", api._tre_ms)


def gia_lap_mot_mau(pos, wav, that):
    """Gia lap dung nhip bo_doc: day goi kem thoiLuong, cho `that` giay
    (= phat that), roi day goi cua mau ke tiep."""
    api._day({"pos": pos, "state": "dang_doc", "thoiLuong": wav})
    _t.sleep(that)
    api._day({"pos": pos + 1, "state": "dang_doc"})


# Phat that 1,50s cho WAV 1,00s va nghi 0 -> tre 500 ms.
for s in api._playlist:
    s["nghi"] = 0
gia_lap_mot_mau(1, 1.0, 1.5)
ok(450 <= api._tre_ms <= 560, "do ra khoang 500 ms", api._tre_ms)

# Mot lan ket CPU 4 giay: qua tran, phai bi bo qua.
gia_lap_mot_mau(1, 1.0, 5.0)
ok(450 <= api._tre_ms <= 560, "lan ket CPU bi bo, khong keo con so len",
   api._tre_ms)

# Vai lan quanh 300 ms -> trung vi keo ve phia do.
for _ in range(4):
    gia_lap_mot_mau(1, 0.5, 0.8)
ok(280 <= api._tre_ms <= 520, "lay trung vi may lan gan nhat", api._tre_ms)

# Goi tin gui sang giao dien phai KEM con so vua do.
bat = []
goc = api._goi_js
api._goi_js = lambda ma, *ts: (bat.append(ts[0]) if ma == "window.gd.push"
                               and ts and isinstance(ts[0], dict) else None)
api._day({"pos": 1, "state": "dang_doc", "thoiLuong": 1.0})
api._goi_js = goc
ok(bat and bat[0].get("treMs") == api._tre_ms,
   "goi tin mang theo treMs", bat[0].get("treMs") if bat else None)

print("\n--- L. Nap truoc mau dau ---")


class SpeakerGia:
    def __init__(self):
        self.da_goi = []
        self.cfg = {}

    def prefetch(self, key, text, khuech_dai=1.0):
        self.da_goi.append((key, text))

    def clear_cache(self):
        pass

    def stop(self):
        pass

    def shutdown(self):
        pass

    # Bai nay chi kiem duong NAP TRUOC, khong chay vong doc. Hai ham duoi day
    # co mat de vat gia du giong that; cham vao chung nghia la duong code da di
    # cho khac han y dinh - bao dong ngay chu dung im lang tra bay.
    def get_audio(self, key, text, khuech_dai=1.0):
        raise AssertionError("bai kiem nap truoc KHONG duoc goi get_audio")

    def play(self, audio, stop_event, dinh_dang="wav"):
        raise AssertionError("bai kiem nap truoc KHONG duoc phat tieng")


import time as _time
from giaodien_moi import cau_noi_moi as _C

api.moi_dat_doan(DOAN)
gia = SpeakerGia()

# VAT GIA PHAI TU CHUNG MINH NO DU GIONG THAT.
#
# Day la bai hoc phai tra gia: phep kiem cu dung SpeakerGia thieu thuoc tinh
# `_cache`, code san pham dam vao do, loi bi nuot boi try/except, va phep kiem
# so None voi None nen luon XANH ma chang kiem gi. Bo kiem xanh nhung cho duoc
# kiem thi khong duoc kiem - te hon la de no do.
#
# Chot lai: doi chieu voi lop Speaker THAT, moi thu code san pham co the goi
# deu phai co mat.
import DocCongDuc as _engine
_that = _engine.Speaker({"ffplay": "x"})
_thieu = [t for t in ("prefetch", "get_audio", "play", "stop", "shutdown",
                      "clear_cache", "cfg")
          if hasattr(_that, t) and not hasattr(gia, t)]
ok(not _thieu, "SpeakerGia co du moi thu ma Speaker that co", _thieu or "du")

api._bo_doc.speaker = gia
_C.CHO_NAP_TRUOC_GIAY = 0.15        # rut ngan cho bai kiem chay nhanh
# Doc so mau nap truoc TU MA NGUON, dung neo cung. Bai nay tung neo cung so 1;
# khi ma doi sang nap 2 mau mot luot thi ca BON phep duoi bao lech, trong khi
# khong co gi hong - y nghia that cua bai la "khong nap trung LUOT", khong
# phai "nap dung mot mau".
_SO_MAU = getattr(_C, "SO_MAU_NAP_TRUOC", 2)


def cho_nap():
    _time.sleep(_C.CHO_NAP_TRUOC_GIAY + 0.25)


that = api._bo_mo_hinh.san_sang
try:
    api._bo_mo_hinh.san_sang = False
    api._nap_truoc_mau_dau()
    cho_nap()
    ok(not gia.da_goi, "mo hinh chua san sang -> khong nap truoc", gia.da_goi)

    api._bo_mo_hinh.san_sang = True
    api._nap_truoc_mau_dau()
    ok(not gia.da_goi, "HEN truoc, chua lam ngay")
    cho_nap()
    ok(len(gia.da_goi) == _SO_MAU, f"het hen thi nap dung MOT luot ({_SO_MAU} mau)",
       len(gia.da_goi))
    ok(gia.da_goi and gia.da_goi[0][0] == 0, "nap dung mau so 0 (mau se phat dau)")
    ok(gia.da_goi and gia.da_goi[0][1] == api._playlist[0]["text"],
       "nap dung noi dung cua mau dau")

    # LUOT QUA NAM TAB: chi tab dung lai moi duoc tong hop. Day la cho da vap -
    # khong co chot nay thi hang doi dai ra va bam Nghe phai cho 106 giay.
    gia.da_goi.clear()
    for _ in range(5):
        api._nap_truoc_mau_dau()
    cho_nap()
    ok(len(gia.da_goi) == _SO_MAU, "doi tab 5 lan lien tay -> chi MOT luot tong hop",
       len(gia.da_goi))

    # Doi giong xong phai nap lai: cap_nhat_cfg vua xoa sach cache.
    gia.da_goi.clear()
    api.doi_giong(api._cfg.get("vieneu_voice_id", "") or "thu")
    cho_nap()
    ok(len(gia.da_goi) == _SO_MAU, "doi giong -> nap truoc lai", len(gia.da_goi))

    # Mo hinh bao san sang giua chung cung phai bat lai nhip nay.
    gia.da_goi.clear()
    api._day_mo_hinh({"model": {"trangThai": "san_sang"}})
    cho_nap()
    ok(len(gia.da_goi) == _SO_MAU, "mo hinh san sang -> nap truoc", len(gia.da_goi))

    gia.da_goi.clear()
    api._day_mo_hinh({"model": {"trangThai": "dang_tai"}})
    cho_nap()
    ok(not gia.da_goi, "dang tai thi chua nap")

    # Sap phat thi bo luot con dang HEN.
    gia.da_goi.clear()
    api._nap_truoc_mau_dau()
    api._huy_hen_nap_truoc()
    cho_nap()
    ok(not gia.da_goi, "bam Nghe thi huy luot con dang hen")

    # KHONG con bam vao ruot Speaker nua. Phep kiem cu o day so None voi None
    # nen luon dat ma chang chung minh gi - vat gia khong co `_cache` nen bien
    # theo doi khong bao gio duoc gan. Gio doi thanh kiem dieu do bang chung.
    ok(not hasattr(api, "_viec_nap_truoc"),
       "KHONG con giu future cua Speaker (bo phu thuoc thuoc tinh rieng)")
    # Cam LOI GOI, khong cam nhac ten: phan giai thich vi sao bo no van duoc
    # phep noi den `_cache`, va nen noi - de nguoi sau khong dam vao lan nua.
    _nguon_path = (Path(_GOC) / "src" / "app" / "cau_noi_moi.py") if (Path(_GOC) / "src" / "app" / "cau_noi_moi.py").exists() else (Path(_GOC) / "giaodien_moi" / "cau_noi_moi.py")
    _nguon = _nguon_path.read_text(encoding="utf-8")
    ok("speaker._cache" not in _nguon and "._cache.get" not in _nguon,
       "ma nguon khong con GOI vao speaker._cache")
finally:
    api._bo_mo_hinh.san_sang = that
    _C.CHO_NAP_TRUOC_GIAY = 1.2
    api._huy_hen_nap_truoc()

print("\n--- M. Duong nhanh cho trong so: chu thuong = mot am tiet ---")
_cau = "Kính gửi toàn thể cán bộ nhân viên"
ok(api._am_tiet_tung_chu(_cau) == [1] * len(_cau.split()),
   f"mau khong co so -> moi chu mot am tiet ({len(_cau.split())} chu)",
   api._am_tiet_tung_chu(_cau))
ok(api._can_dem_ky("Nghi tu 31/8/2026"), "mau co chu so -> phai dem ky")
ok(not api._can_dem_ky("Kính gửi quý vị"), "mau thuong -> khong can dem ky")
import time as _tt

_b = _tt.perf_counter()
api._am_tiet_tung_chu(" ".join(["Kính gửi toàn thể cán bộ nhân viên"] * 40))
_nhanh = (_tt.perf_counter() - _b) * 1000
ok(_nhanh < 50, f"240 chu khong so: {_nhanh:.0f} ms (duong nhanh)")

print("\n--- J. Doan rong / so doan sai khong lam vo gi ---")
ok(api._pham_vi_mau(999, 3) == {}, "chi so mau ngoai bang -> rong")
ok(api._pham_vi_mau(0, 999) == {}, "so doan ngoai bang -> rong")
api.moi_dat_doan([])
ok(api._playlist == [], "khong con mau nao")

api._don_dep()
print(f"\n{'XANH — khớp hết' if loi == 0 else f'ĐỎ — {loi} chỗ lệch'}")
sys.exit(1 if loi else 0)
