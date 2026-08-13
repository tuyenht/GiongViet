# -*- coding: utf-8 -*-
"""Phan ra tung khuc thoi gian tu luc bam Nghe den luc loa ra tieng.

Chu du an muon "nhanh nhat co the". Muon cat cho nao thi phai biet cho nao dang
an bao nhieu - bai nay do tung khuc, tren van ban that.

CAC KHUC:
  1. moi_dat_doan      dung playlist: chuan hoa, tach_chunk
  2. trong so doc      chuan hoa tien to de biet moi chu doc ra may am tiet
                       (O(n^2) - chinh la thu can soi ky nhat)
  3. tong hop mau dau  VieNeu dung WAV
  4. tre ra loa        ffplay khoi dong + mo thiet bi + dem
  5. giua hai mau      nghi + tong hop mau sau (neu nap truoc chua kip)

Khong mo cua so. Co tieng ra loa.

Chay:  py giaodien_moi/do_phan_ra_tre.py
"""
import io
import os
import statistics
import sys
import threading
import time

sys.path.insert(0, r"C:\Projects\DocCongDuc")
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8",
                              line_buffering=True)

from giaodien_moi import khoa_du_lieu  # noqa: E402
from giaodien_moi.cau_noi_moi import ApiMoi  # noqa: E402

# Nhat ky loi cua bai do di cho khac - GiongViet-loi.log la duong chan doan cua
# chu du an, khong tron rac vao. Ra ca ho sau khi vap: 15 dong loi cua bai kiem
# tung nam trong log that.
import tempfile as _tf
from pathlib import Path as _P
from giaodien import nhat_ky as _nk
_nk.TEP_LOG = _P(_tf.gettempdir()) / "gd-kiem-loi.log"

NGAN = "Kính mời bà con nhân dân trong khu phố chú ý nghe thông báo."

VUA = ("Kính gửi toàn thể cán bộ, nhân viên của công ty. "
       "Nghỉ lễ từ ngày 31/8/2026 đến hết ngày 2/9/2026. "
       "Mọi việc gấp xin gọi tổng đài 1900 6868. "
       "Trân trọng thông báo.")

# Doan that dai: 40 cau. Day la cho O(n^2) lo mat neu no co van de.
DAI = " ".join([
    "Kính gửi toàn thể cán bộ, nhân viên của công ty trong toàn hệ thống.",
    "Căn cứ thông báo của Uỷ ban nhân dân thành phố về lịch nghỉ lễ năm nay.",
    "Ban Giám đốc thông báo tới các phòng ban lịch nghỉ cụ thể như sau đây.",
    "Thời gian nghỉ tính từ ngày 31/8/2026 cho đến hết ngày 2/9/2026.",
    "Toàn thể cán bộ trở lại làm việc bình thường vào sáng thứ Năm ngày 3 tháng 9.",
] * 8)

TRAN_GIAY = 900


def canh_gio():
    time.sleep(TRAN_GIAY)
    print(f"\n!! Qua {TRAN_GIAY} giay - thoat cuong buc")
    os._exit(3)


def do_dung_playlist(api, van_ban, lan=3):
    ds = []
    for _ in range(lan):
        api._trong_so_cache.clear()
        t = time.perf_counter()
        api.moi_dat_doan([{"kieu": "body", "chu": van_ban}])
        ds.append(time.perf_counter() - t)
    return statistics.median(ds), len(api._playlist)


def do_trong_so(api, van_ban, lan=3):
    ds = []
    for _ in range(lan):
        api._trong_so_cache.clear()
        t = time.perf_counter()
        api._trong_so_doc(1, van_ban)
        ds.append(time.perf_counter() - t)
    return statistics.median(ds)


def do_tu_luc_bam(api, van_ban, cho_truoc=0.0):
    """Do tung moc tu luc goi phat den luc mau dau ra tieng.

    `cho_truoc` gia lap nguoi dung mo van ban roi doc luot mot lat moi bam
    Nghe. Trong quang do _nap_truoc_mau_dau da tong hop san mau dau, nen day
    la cach do dung loi ich cua viec nap truoc.
    """
    moc = {}
    goi_js_goc = api._goi_js
    xong = threading.Event()

    def bat(ma_lenh, *ts):
        if ma_lenh == "window.gd.push" and ts and isinstance(ts[0], dict):
            g = ts[0]
            if g.get("pos") == 1 and "thoiLuong" not in g and "bat_dau" not in moc:
                moc["bat_dau"] = time.perf_counter()
            if g.get("pos") == 1 and g.get("thoiLuong") and "co_wav" not in moc:
                moc["co_wav"] = time.perf_counter()
                moc["wav"] = g["thoiLuong"]
            if g.get("pos") == 2 and "mau2" not in moc:
                moc["mau2"] = time.perf_counter()
                xong.set()
        return goi_js_goc(ma_lenh, *ts)

    api._trong_so_cache.clear()
    api.moi_dat_doan([{"kieu": "body", "chu": van_ban}])
    if cho_truoc:
        time.sleep(cho_truoc)
    api._goi_js = bat
    try:
        t0 = time.perf_counter()
        api.moi_nghe_toan_bo()
        xong.wait(timeout=300)
    finally:
        api._goi_js = goi_js_goc
        api.moi_dung()
        time.sleep(0.5)
    if "co_wav" not in moc:
        return None
    nghi = float(api._playlist[0].get("nghi", 0) or 0)
    tong_hop = moc["co_wav"] - moc.get("bat_dau", t0)
    tre_loa = (moc["mau2"] - moc["co_wav"] - nghi - moc["wav"]
               if "mau2" in moc else float("nan"))
    return {"vao_vong": moc.get("bat_dau", t0) - t0,
            "tong_hop": tong_hop, "wav": moc["wav"], "tre_loa": tre_loa}


def main():
    threading.Thread(target=canh_gio, daemon=True).start()
    khoa_du_lieu.khoa()          # BAT BUOC: ApiMoi khong tu khoa nua
    api = ApiMoi()
    print(f"khoa du lieu: {'BAT' if khoa_du_lieu.dang_khoa() else 'CHUA'}")
    api._bo_mo_hinh.bat_dau()
    het = time.time() + 300
    while not api._bo_mo_hinh.san_sang and time.time() < het:
        time.sleep(0.5)
    if not api._bo_mo_hinh.san_sang:
        print("!! Mo hinh khong san sang:", api._bo_mo_hinh.loi)
        os._exit(2)
    api._nap_giong()

    print("\n" + "=" * 76)
    print("  PHAN 1 — Chi phi DUNG PLAYLIST va TINH TRONG SO (khong phat tieng)")
    print("=" * 76)
    print(f"  {'van ban':<12} {'chu':>5} {'mau':>4} {'dung playlist':>15} "
          f"{'trong so':>12}")
    for nhan, vb in (("ngan", NGAN), ("vua", VUA), ("dai", DAI)):
        t_pl, so_mau = do_dung_playlist(api, vb)
        t_ts = do_trong_so(api, vb)
        print(f"  {nhan:<12} {len(vb.split()):>5} {so_mau:>4} "
              f"{t_pl * 1000:>12.0f} ms {t_ts * 1000:>9.0f} ms")

    print("\n" + "=" * 76)
    print("  PHAN 3 — Loi ich cua NAP TRUOC mau dau")
    print("  (mo van ban xong, doc luot mot lat roi moi bam Nghe)")
    print("=" * 76)
    for cho in (0.0, 4.0, 12.0):
        kq = do_tu_luc_bam(api, VUA, cho_truoc=cho)
        if not kq:
            print(f"  cho {cho:4.0f}s truoc khi bam : khong do duoc")
            continue
        tong = kq["vao_vong"] + kq["tong_hop"]
        print(f"  doc luot {cho:4.0f} giay roi bam  →  cho them "
              f"{tong * 1000:6.0f} ms moi co tieng")

    print("\n" + "=" * 76)
    print("  PHAN 4 — LUOT QUA NHIEU TAB roi bam Nghe")
    print("  (day la cho da vap: hang doi tong hop dai ra, bam Nghe cho 106 giay)")
    print("=" * 76)
    for _ in range(5):
        api.moi_dat_doan([{"kieu": "body", "chu": NGAN}])
        time.sleep(0.3)          # luot nhanh hon thoi gian hen
    kq = do_tu_luc_bam(api, VUA, cho_truoc=0.0)
    if kq:
        tong = kq["vao_vong"] + kq["tong_hop"]
        print(f"  luot 5 tab roi bam ngay  →  cho them {tong * 1000:6.0f} ms")
        print("  (truoc khi co chot huy/hen: 106844 ms)")

    api._don_dep()
    sys.stdout.flush()
    os._exit(0)


if __name__ == "__main__":
    main()
