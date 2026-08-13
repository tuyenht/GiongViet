# -*- coding: utf-8 -*-
"""Do do lech giua CHU CHAY va TIENG DOC — bang so, tren tung giong.

VI SAO DO DUOC MA KHONG CAN TAI
  bo_doc.py:198  day goi tin kem thoiLuong (so giay WAV that) NGAY TRUOC khi phat
  bo_doc.py:200  speaker.play(...) CHAN cho den khi phat xong
  bo_doc.py:206  roi moi nghi seg["nghi"] giay
  bo_doc.py:153  vong sau day goi "dang_doc" cua mau ke tiep

Nen:  phat_that = t(goi mau sau) - t(goi mau nay) - nghi
      tre       = phat_that - thoiLuong

`tre` chinh la khoang tu luc giao dien bat dau cho chu chay den luc loa het
tieng: ffplay khoi dong, dem, roi thoat. Chu chay theo thoiLuong nen no ve dich
som hon tieng dung bang `tre`. Do duoc con so nay tren TUNG GIONG thi biet
TRE_PHAT_MS nen dat bao nhieu, va biet no co on dinh giua cac giong khong.

KHONG mo cua so - chi can engine va loa. Co tieng ra loa suot bai chay.

Chay:  py giaodien_moi/do_tre_phat.py           (5 giong, doan dai)
       py giaodien_moi/do_tre_phat.py tatca     (tat ca giong)
"""
import io
import os
import statistics
import sys
import threading
import time
from pathlib import Path

# Goc du an, tinh tu chinh vi tri tep nay. KHONG viet cung duong dan:
# kho da len GitHub, ai tai ve cho khac la vo het bo kiem.
_GOC = str(Path(__file__).resolve().parent.parent)
sys.path.insert(0, _GOC)
# line_buffering BAT BUOC: ket thuc bang os._exit (PyTorch de lai luong nen
# khong phai daemon), ma os._exit khong xa dem - khong bat thi mat sach output.
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

# Doan dai that: nhieu cau, co so, co ngay thang, co so dien thoai - dung thu
# nguoi dung dan vao that. Cat nho de moi cau thanh mot mau rieng.
DOAN_DAI = (
    "Kính gửi toàn thể cán bộ, nhân viên của công ty. "
    "Nghỉ lễ từ ngày 31/8/2026 đến hết ngày 2/9/2026. "
    "Mọi việc gấp xin gọi tổng đài 1900 6868. "
    "Các phòng ban gửi danh sách trực trước 17h00 ngày 28 tháng 8. "
    "Trân trọng thông báo."
)
# PHAI du dai de tach_chunk cat ra it nhat 3 mau: mau CUOI khong co mau sau
# nen khong do duoc, doan mot mau la ca bai giong do khong cho ra so nao.
DOAN_NGAN = ("Kính gửi quý vị. Sau đây là bản tin tổng hợp trong ngày. "
             "Mời quý vị cùng theo dõi phần tin trong nước. "
             "Xin cảm ơn quý vị đã lắng nghe.")

SO_KY_TU_MOT_MAU = 60      # ep cat nho de co nhieu mau ma do

TRAN_GIAY = 1500


def canh_gio():
    time.sleep(TRAN_GIAY)
    print(f"\n!! Qua {TRAN_GIAY} giay - thoat cuong buc")
    os._exit(3)


def do_mot_giong(api, ma_giong: str, van_ban: str, nhan: str):
    """Phat that mot doan bang mot giong, tra ve danh sach do tre tung mau."""
    api._cfg["vieneu_voice_id"] = ma_giong
    api._bo_doc.cap_nhat_cfg(api._cfg)

    moc = []            # (thoi diem, patch)
    goi_js_goc = api._goi_js

    def bat(ma_lenh, *ts):
        if ma_lenh == "window.gd.push" and ts and isinstance(ts[0], dict) \
                and "pos" in ts[0]:
            moc.append((time.time(), dict(ts[0])))
        return goi_js_goc(ma_lenh, *ts)

    api._goi_js = bat
    try:
        api.moi_dat_doan([{"kieu": "body", "chu": van_ban}])
        so_mau = len(api._playlist)
        xong = threading.Event()

        # Vong doc bao "san_sang" khi het bai.
        goi_js_bat = api._goi_js

        def bat2(ma_lenh, *ts):
            if ma_lenh == "window.gd.push" and ts and isinstance(ts[0], dict) \
                    and ts[0].get("state") == "san_sang":
                xong.set()
            return goi_js_bat(ma_lenh, *ts)

        api._goi_js = bat2
        api.moi_nghe_toan_bo()
        if not xong.wait(timeout=600):
            print(f"     ! {nhan}: qua gio, bo qua")
            api.moi_dung()
            return []
    finally:
        api._goi_js = goi_js_goc
        api.moi_dung()
        time.sleep(0.4)

    # Ghep lai: voi moi mau, tim goi CO thoiLuong va goi ke tiep cua mau sau.
    co_wav = [(t, g) for t, g in moc if g.get("thoiLuong")]
    ra = []
    for i, (t, g) in enumerate(co_wav):
        # Moc bat dau cua mau ke tiep = goi dau tien co pos lon hon, bat ky loai
        sau = next((tt for tt, gg in moc
                    if tt > t and gg.get("pos", 0) == g.get("pos", 0) + 1), None)
        if sau is None:
            continue
        seg = api._playlist[g["pos"] - 1] if g["pos"] - 1 < len(api._playlist) else {}
        nghi = float(seg.get("nghi", 0) or 0)
        phat_that = sau - t - nghi
        ra.append({"mau": g["pos"], "wav": g["thoiLuong"],
                   "that": phat_that, "tre": phat_that - g["thoiLuong"]})
    return ra


def in_bang(nhan, ds):
    if not ds:
        print(f"  {nhan:<26} (khong do duoc mau nao)")
        return None
    tre = [d["tre"] for d in ds]
    tb = statistics.mean(tre)
    print(f"  {nhan:<26} {len(ds)} mau · WAV {sum(d['wav'] for d in ds):5.1f}s"
          f" · tre tb {tb * 1000:6.0f} ms"
          f" · thap {min(tre) * 1000:5.0f} · cao {max(tre) * 1000:5.0f}")
    return tb


def main():
    threading.Thread(target=canh_gio, daemon=True).start()
    tat_ca = len(sys.argv) > 1 and sys.argv[1] == "tatca"

    khoa_du_lieu.khoa()          # BAT BUOC: ApiMoi khong tu khoa nua
    api = ApiMoi()
    print(f"khoa du lieu: {'BAT' if khoa_du_lieu.dang_khoa() else 'CHUA'}")
    api._cfg["so_ky_tu"] = SO_KY_TU_MOT_MAU

    print("Cho mo hinh...")
    het = time.time() + 300
    api._bo_mo_hinh.bat_dau()
    while not api._bo_mo_hinh.san_sang and time.time() < het:
        time.sleep(0.5)
    if not api._bo_mo_hinh.san_sang:
        print("!! Mo hinh khong san sang:", api._bo_mo_hinh.loi)
        os._exit(2)

    api._nap_giong()
    giong = list(api._voices)
    print(f"Co {len(giong)} giong tren may\n")
    if not tat_ca:
        giong = giong[:5]

    print("=" * 78)
    print("PHAN 1 — DOAN DAI, mot giong. Xem tre co on dinh qua nhieu mau khong.")
    print("=" * 78)
    dai = do_mot_giong(api, giong[0]["id"], DOAN_DAI, giong[0]["ten"])
    in_bang(f"{giong[0]['ten']} (doan dai)", dai)
    for d in dai:
        print(f"       mau {d['mau']}: WAV {d['wav']:5.2f}s · phat that "
              f"{d['that']:5.2f}s · tre {d['tre'] * 1000:5.0f} ms")

    print()
    print("=" * 78)
    print(f"PHAN 2 — {len(giong)} GIONG, cung mot doan. Tre co giong nhau khong?")
    print("=" * 78)
    tb_giong = []
    for g in giong:
        ds = do_mot_giong(api, g["id"], DOAN_NGAN, g["ten"])
        tb = in_bang(g["ten"], ds)
        if tb is not None:
            tb_giong.append((g["ten"], tb))

    print()
    print("=" * 78)
    if tb_giong:
        so = [t for _, t in tb_giong]
        print(f"  Tre trung binh tren {len(so)} giong : {statistics.mean(so) * 1000:.0f} ms")
        print(f"  Thap nhat / cao nhat            : {min(so) * 1000:.0f} / {max(so) * 1000:.0f} ms")
        if len(so) > 1:
            print(f"  Do lech chuan                   : {statistics.pstdev(so) * 1000:.0f} ms")
        print()
        print("  DOC CON SO NAY THE NAO:")
        print("   · TRE_PHAT_MS nen dat gan muc trung binh -> chu doi dung bang")
        print("     luc loa im truoc khi ra tieng.")
        print("   · Neu do lech chuan NHO thi mot con so dung cho moi giong.")
        print("     Neu LON thi phai do rieng tung giong, khong the dung chung.")
    api._don_dep()
    time.sleep(0.5)
    os._exit(0)


if __name__ == "__main__":
    main()
