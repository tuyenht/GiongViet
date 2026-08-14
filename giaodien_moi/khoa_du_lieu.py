# -*- coding: utf-8 -*-
"""Khoá mọi đường ghi vào dữ liệu người dùng — DÀNH CHO BỘ KIỂM.

DÙNG Ở ĐÂU (2026-08-13, chủ dự án chốt bỏ hẳn bản cũ):
  · BỘ KIỂM và BÀI ĐO   -> BẬT. Chạy thử không được để lại vết trên dữ liệu
                            thật của người dùng.
  · CHƯƠNG TRÌNH THẬT   -> KHÔNG bật. Người dùng bấm Lưu thì phải lưu được;
                            khoá lại là đẻ ra nút bấm không ăn thua, đúng thứ
                            KPI dự án cấm.

VÌ SAO CÓ TỆP NÀY — đã đo được rò rỉ thật, không phải đề phòng suông:
bấm chọn giọng ở giao diện mới gọi `doi_giong` của Api cũ, hàm đó gọi
`_ghi_cau_hinh()`, và cauhinh.ini + hoso.json bị ghi đè ngay lập tức. Hồi đó
bản cũ còn dùng hằng ngày nên đó là rò rỉ thật sự; giờ bản cũ bỏ rồi, nhưng
lá chắn vẫn đáng giữ cho bộ kiểm - nó đã bắt được 28 lượt ghi lén trong một
phép "bấm loạn" 18 phương thức.

CÁCH CHẶN — khoá ở CỬA RA, không vá từng nút bấm.
Api cũ có 19 phương thức công khai dẫn tới ghi tệp — doi_giong, doi_ho_so,
them_ho_so, xoa_ho_so, sua_ten_ho_so, mo_file, doi_phong_cach, dat_thong_so,
dat_cai_dat, doi_duong_dan_cai_dat, chon_thu_muc, bat_dau_xuat, luu_theme,
luu_zoom, them_tu, sua_tu, xoa_tu, nhan_ban_giong, xoa_giong — cộng thêm
`ho_so.doc()` chạy ngay trong __init__ và tự ghi lại hoso.json nếu tệp hỏng.
Override từng cái là chắc chắn sót, mà sót một cái thì mất dữ liệu thật của
người dùng. Nhưng cả 19 phương thức ấy chỉ đổ ra ĐÚNG 8 hàm ghi. Khoá 8 hàm
là khoá hết, kể cả phương thức thêm sau này — giaodien_moi/kiem_ro_ri_ghi.py
đọc mã nguồn để canh đúng điều đó.

Tiến trình bản mới (GiongViet.py) chạy riêng, nên khoá ở đây không ảnh
hưởng gì đến GiongDoc.py đang dùng hằng ngày.

KHÔNG khoá: tệp WAV do người dùng chủ động bấm Xuất (đó là thứ họ muốn có),
và GiongViet-loi.log (nhật ký lỗi, không phải dữ liệu của họ).
"""

import DocCongDuc as engine
import kho_cau_hinh

from giaodien import he_thong, ho_so

# Mỗi mục: (module, tên hàm, giá trị trả về thay thế, tệp nó vốn ghi vào).
# Giá trị trả về phải VÔ HẠI theo đúng nghĩa của từng hàm - trả None cho
# tao_tep_noi_dung sẽ làm hồ sơ mới trỏ vào tệp không tồn tại, nên nó trả về
# tên tệp lời dẫn gốc.
CUA_RA_GHI = [
    (engine, "save_config", None, "cauhinh.ini"),
    (engine, "luu_tudien", None, "tudien.ini"),
    (engine, "tao_giong_rieng", None, "giong_rieng/"),
    (engine, "xoa_giong_rieng", None, "giong_rieng/ (xoá tệp)"),
    (engine, "luu_ds_giong_rieng", None, "giong_rieng/danhsach.json"),
    (ho_so, "luu", None, "hoso.json"),
    (ho_so, "tao_tep_noi_dung", ho_so.TEP_NOI_DUNG_GOC, "noidung-*.ini (tệp mới)"),
    (he_thong, "luu_tuy_chon", None, "giaodien.json"),
    # Cấu hình nay gom vào giongviet.db. Không bịt cửa này thì bộ kiểm chạy
    # xong để lại một tệp kho ngay giữa thư mục dự án - đã xảy ra thật.
    # Trả False đúng nghĩa "ghi không thành", nơi gọi tự lùi về tệp rời.
    (kho_cau_hinh, "ghi", False, "giongviet.db"),
]

# Đếm số lần bị chặn theo tên hàm. Không phải để trang trí: khi giao diện mới
# lỡ gọi nhầm một hàm ghi, con số ở đây là bằng chứng chỉ đúng chỗ phải sửa,
# thay vì phải ngồi so mtime từng tệp.
da_chan = {}

_da_khoa = False


def _khoa_lai(ten_day_du: str, tra_ve, tep: str):
    def thay_the(*_a, **_k):
        da_chan[ten_day_du] = da_chan.get(ten_day_du, 0) + 1
        return tra_ve

    thay_the.__name__ = ten_day_du.split(".")[-1]
    thay_the.__doc__ = f"ĐÃ KHOÁ — lẽ ra ghi vào {tep}."
    thay_the.bi_khoa = True
    thay_the.tep = tep
    return thay_the


def khoa():
    """Khoá toàn bộ cửa ra. Gọi được nhiều lần, lần thứ hai trở đi không làm gì.

    Phải gọi TRƯỚC khi dựng Api: `ho_so.doc()` chạy ngay trong __init__ và nó
    tự ghi lại hoso.json nếu thấy tệp hỏng.
    """
    global _da_khoa
    if _da_khoa:
        return False
    for mo_dun, ten, tra_ve, tep in CUA_RA_GHI:
        setattr(mo_dun, ten, _khoa_lai(f"{mo_dun.__name__}.{ten}", tra_ve, tep))
    _da_khoa = True
    return True


def dang_khoa() -> bool:
    return _da_khoa


def con_ho() -> list:
    """Cửa ra nào chưa khoá. Rỗng là kín."""
    return [f"{m.__name__}.{t}" for m, t, _, _ in CUA_RA_GHI
            if not getattr(getattr(m, t, None), "bi_khoa", False)]
