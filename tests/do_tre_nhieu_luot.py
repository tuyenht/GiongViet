# -*- coding: utf-8 -*-
"""Do do tre ra loa NHIEU LUOT, va xem cai tran co chan het so do that khong.

Chay:  py tests/do_tre_nhieu_luot.py          # 5 luot
       py tests/do_tre_nhieu_luot.py 3        # 3 luot

BAI NAY CO TIENG PHAT RA LOA. Khong chay duoc lúc may dang mo chuong trinh -
luat cua du an la MOT nguon phat tieng tai mot thoi diem.

VI SAO CAN NO, trong khi da co do_tre_phat.py:

  do_tre_phat.py do MOT luot va in ra tre tung mau. Tu do thay 9/9 mau nam
  trong 902-1610 ms, trong khi TRE_CAO_NHAT_MS = 800. Nhung mot luot khong du
  de chon lai mot hang so: chinh trong MOT giong, bon mau da dao dong 613 ms
  (997 -> 1610). CLAUDE.md §5: "nguong cung dat tren so do ngau nhien la bay".

  Va do_tre_phat.py KHONG nhin vao _tre_da_do, nen no khong tra loi duoc cau
  hoi that su quan trong: bo tu do co nhan duoc mau nao khong, hay tat ca bi
  loai? _cap_nhat_tre LOAI mau ngoai khoang 50..800 (`return`), khong kep ve
  800 - nen neu moi mau deu vuot tran thi _tre_ms khong bao gio roi 250, va
  chu chay truoc tieng o MOI mau chu khong chi mau dau.

CACH DO: nang tran len that cao NGAY TRONG bai nay de MOI mau duoc nhan, roi
xem phan bo thuc. Tu phan bo do moi biet tran nen dat o dau, va dem duoc bao
nhieu mau se bi tran 800 loai.

AN TOAN: bat khoa du lieu truoc khi dung ApiMoi, va day nhat ky loi sang thu
muc tam - GiongViet-loi.log la duong chan doan cua chu du an, khong tron rac
vao do.
"""
import io
import os
import statistics
import sys
import tempfile
import threading
import time
from pathlib import Path

GOC = Path(__file__).resolve().parent.parent
os.environ.setdefault("GIONGVIET_GOC", str(GOC))
sys.path.insert(0, str(GOC))
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8",
                              line_buffering=True)

from giaodien import nhat_ky as _nk                              # noqa: E402
_nk.TEP_LOG = Path(tempfile.gettempdir()) / "gd-kiem-loi.log"

from giaodien_moi import khoa_du_lieu                            # noqa: E402
from giaodien_moi.cau_noi_moi import ApiMoi                      # noqa: E402
import giaodien_moi.cau_noi_moi as cnm                           # noqa: E402

SO_LUOT = int(sys.argv[1]) if len(sys.argv) > 1 and sys.argv[1].isdigit() else 5

# PHAI ep so_ky_tu nho. Doan nao ngan hon so nay thi ra DUNG MOT mau, ma
# _cap_nhat_tre doi mot mau VA mau ke tiep (pos == moc[1] + 1) moi tinh duoc.
# Da vap: do bang doan mot mau roi thay "0 mau duoc nhan", suyt ket luan la
# tran chan mat - trong khi do chi la he qua cua setup sai.
# do_tre_phat.py:154 cung ep y vay.
SO_KY_TU_MOT_MAU = 60

DOAN = ("Kính gửi toàn thể cán bộ, nhân viên của công ty. "
        "Nghỉ lễ từ ngày 31/8/2026 đến hết ngày 2/9/2026. "
        "Mọi việc gấp xin gọi tổng đài 1900 6868. "
        "Các phòng ban gửi danh sách trực trước 17h00 ngày 28 tháng 8. "
        "Trân trọng thông báo.")

TRAN_GOC = cnm.TRE_CAO_NHAT_MS
SAN_GOC = cnm.TRE_THAP_NHAT_MS


def mot_luot(api, thu: int) -> list:
    """Phat that mot luot, tra ve moi gia tri tre ma _cap_nhat_tre TINH ra."""
    tinh_duoc = []
    tho = []                 # moi gia tri TINH RA, ke ca mau bi loai
    goc = api._cap_nhat_tre

    def bat(patch):
        # Tinh LAI dung cong thuc cua _cap_nhat_tre de thay gia tri THO truoc
        # khi no bi loc. Khong lam vay thi mau bi loai la vo hinh, va khong
        # phan biet duoc "bi SAN loai" / "bi TRAN loai" / "khong tinh ra so
        # nao ca" - ba cho do dan tói ba ket luan khac han.
        moc = api._moc_phat
        if not patch.get("thoiLuong") and moc \
                and int(patch.get("pos", 0)) == moc[1] + 1:
            tho.append(((time.time() - moc[0]) - moc[3] - moc[2]) * 1000)
        truoc = list(api._tre_da_do)
        goc(patch)
        if len(api._tre_da_do) > len(truoc) or api._tre_da_do[-1:] != truoc[-1:]:
            if api._tre_da_do:
                tinh_duoc.append(api._tre_da_do[-1])

    api._cap_nhat_tre = bat
    xong = threading.Event()
    goi_goc = api._goi_js

    def bat_js(ma, *ts):
        if ma == "window.gd.push" and ts and isinstance(ts[0], dict) \
                and ts[0].get("state") == "san_sang":
            xong.set()
        return goi_goc(ma, *ts)

    api._goi_js = bat_js
    try:
        api.moi_dat_doan([{"kieu": "body", "chu": DOAN}])
        so_mau = len(api._playlist)
        api._tre_da_do.clear()
        api.moi_nghe_toan_bo()
        if not xong.wait(timeout=420):
            print(f"  luot {thu}: QUA GIO, bo qua")
            api.moi_dung()
            return []
    finally:
        api._cap_nhat_tre = goc
        api._goi_js = goi_goc
        time.sleep(0.4)

    # So THO voi so DA NHAN bang dung sai so: hai ben la so thuc, so thang
    # bang thi mau da duoc nhan van bi ke vao "bi loai" - da in sai that.
    bi = [x for x in tho
          if not any(abs(x - y) < 1e-6 for y in tinh_duoc)]
    print(f"  luot {thu}: {so_mau} mau · tinh ra {len(tho)} so"
          f" · nhan {len(tinh_duoc)}"
          f"  [{'  '.join(f'{x:.0f}' for x in tinh_duoc)}]")
    if bi:
        print(f"           bi loai: {'  '.join(f'{x:.0f}' for x in bi)}"
              f"   (san {cnm.TRE_THAP_NHAT_MS}..tran {cnm.TRE_CAO_NHAT_MS})")
    if not tho:
        print("           KHONG tinh ra so nao: khong goi tin nao co"
              " thoiLuong, hoac pos khong lien tiep")
    return tinh_duoc


def main():
    khoa_du_lieu.khoa()
    print(f"khoa du lieu: {'BAT' if khoa_du_lieu.dang_khoa() else 'TAT'}")
    print(f"hang so that: san {SAN_GOC} ms · TRAN {TRAN_GOC} ms · "
          f"mac dinh {cnm.TRE_PHAT_MAC_DINH_MS} ms")
    print()

    # NANG TRAN trong bai nay de MOI mau duoc nhan -> thay phan bo THUC.
    # Khong doi hang so trong ma nguon; chi doi trong bo nho cua lan chay nay.
    cnm.TRE_CAO_NHAT_MS = 100000
    cnm.TRE_THAP_NHAT_MS = 0
    print(f"da nang tran trong BO NHO len {cnm.TRE_CAO_NHAT_MS} ms de khong mau")
    print("nao bi loai -> doc duoc phan bo that. Ma nguon KHONG bi sua.")
    print(f"\nChay {SO_LUOT} luot, SE CO TIENG PHAT RA LOA...\n")

    api = ApiMoi()
    api._cfg["so_ky_tu"] = SO_KY_TU_MOT_MAU
    api._bo_doc.cap_nhat_cfg(api._cfg)

    # PHAI cho mo hinh. ApiMoi() KHONG nap dong bo - phat ngay sau khi dung
    # xong thi khong tong hop duoc gi, khong goi tin nao co thoiLuong, nen
    # _cap_nhat_tre khong bao gio co moc de tinh. Da do: chi 3 luot goi, deu
    # thoat o nhanh "khong co moc", roi bai bao "0 so do" - va suyt ket luan
    # sai rang cai TRAN chan mat so do.
    print("Cho mo hinh nap...")
    het = time.time() + 300
    api._bo_mo_hinh.bat_dau()
    while not api._bo_mo_hinh.san_sang and time.time() < het:
        time.sleep(0.5)
    if not api._bo_mo_hinh.san_sang:
        print("!! Mo hinh khong san sang:", api._bo_mo_hinh.loi)
        return 2
    api._nap_giong()
    print(f"mo hinh san sang · _tre_ms luc khoi tao: {api._tre_ms} ms\n")

    tat_ca = []
    for i in range(1, SO_LUOT + 1):
        tat_ca += mot_luot(api, i)

    api.moi_dung()
    cnm.TRE_CAO_NHAT_MS = TRAN_GOC
    cnm.TRE_THAP_NHAT_MS = SAN_GOC

    print()
    print("=" * 74)
    if not tat_ca:
        print("  KHONG do duoc mau nao. Khong ket luan gi.")
        api._don_dep()
        return 1

    tat_ca.sort()
    bi_loai = [x for x in tat_ca if not SAN_GOC <= x <= TRAN_GOC]
    print(f"  Tong {len(tat_ca)} so do qua {SO_LUOT} luot")
    print(f"  thap nhat {min(tat_ca):.0f} · trung vi "
          f"{statistics.median(tat_ca):.0f} · cao nhat {max(tat_ca):.0f} ms")
    if len(tat_ca) > 1:
        print(f"  do lech chuan {statistics.stdev(tat_ca):.0f} ms")
    print()
    print(f"  VOI TRAN THAT ({SAN_GOC}..{TRAN_GOC} ms):")
    print(f"    bi loai : {len(bi_loai)}/{len(tat_ca)} mau")
    print(f"    con lai : {len(tat_ca) - len(bi_loai)} mau")
    if len(bi_loai) == len(tat_ca):
        print("    -> KHONG mau nao song sot. _tre_da_do rong mai, _tre_ms")
        print(f"       giu nguyen {cnm.TRE_PHAT_MAC_DINH_MS} ms, va chu chay")
        print(f"       truoc tieng ~{statistics.median(tat_ca) - cnm.TRE_PHAT_MAC_DINH_MS:.0f} ms o MOI mau.")
    print()
    print("  DOC CON SO NAY THE NAO: tran chi de gat mau RAC (luc may ket CPU),")
    print("  khong phai de gat so do binh thuong. Dat tran tren muc cao nhat do")
    print("  duoc, con lai de trung vi 5 mau loc - chinh no da chong mau lac.")
    print("=" * 74)
    api._don_dep()
    return 0


if __name__ == "__main__":
    sys.exit(main())
