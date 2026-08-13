# -*- coding: utf-8 -*-
"""Đọc số điện thoại — tầng nhận dạng và tầng chuyển sang lời.

    Nhận dạng  ->  Phân loại  ->  Hoa văn  ->  Chia nhóm  ->  Ngắt nghỉ  ->  TTS
    (tệp này)      (tệp này)    sdt_mau     sdt_nhip      sdt_nhip      (tệp này)

HAI TẦNG ĐỘC LẬP, đúng mục 26 của đặc tả:

    PHONE VALIDATION        có phải số điện thoại không?
    PHONE PATTERN ANALYSIS  số hợp lệ đó nên đọc thế nào?

Số điện thoại bình thường vẫn phải đọc đúng dù chẳng có hoa văn nào. Hoa văn
chỉ tối ưu cách chia nhóm và ngắt nghỉ, TUYỆT ĐỐI không đổi chữ số.

Engine chuẩn hoá số theo kiểu SỐ LƯỢNG nên số điện thoại ra sai hoàn toàn
("1900 6868" -> "một nghìn chín trăm sáu nghìn tám trăm sáu mươi tám"). Module
này chạy TRƯỚC chuan_hoa_van_ban và thay số bằng chữ, nên engine sau đó không
còn số để hiểu sai. Cố ý không sửa DocCongDuc.py — engine là mã dùng chung.
"""

import re

from . import sdt_nhip

CHU_SO = {
    "0": "không", "1": "một", "2": "hai", "3": "ba", "4": "bốn",
    "5": "năm", "6": "sáu", "7": "bảy", "8": "tám", "9": "chín",
}

# --------------------------------------------------------------- nhận dạng

SO_IT_NHAT, SO_NHIEU_NHAT = 8, 12

# Đầu số phải là 0 / +84 / 1900 / 1800. Đây là thứ tách bạch số điện thoại khỏi
# TIỀN (1.600.000) và NĂM (2026) — hai thứ tuyệt đối không được đụng vào.
#
# Lookaround CHỈ chặn chữ số, không chặn dấu phẩy: số điện thoại trong câu rất
# hay có phẩy ngay sau ("gọi 028.2231.7777, gặp anh Nam").
#
# Lượng tử {3,18}: "1900 6868" sau đầu số chỉ còn " 6868" = 5 ký tự, mà phải
# chừa 1 ký tự cuối cho \d. Đặt {5,16} là hụt đúng số tổng đài.
MAU = re.compile(
    r"(?<!\d)"
    r"(?:\+84|0|1[89]00)"
    r"[\d.\-\s ]{3,18}"
    r"\d"
    r"(?!\d)"
)

DAU_NGAN = re.compile(r"[.\-\s ]+")


def phan_loai(so: str) -> str:
    """MOBILE | LANDLINE | HOTLINE. Chỉ để tầng ngắt nhịp tham khảo."""
    if so.startswith(("1900", "1800")):
        return "HOTLINE"
    if len(so) == 10 and so.startswith("0") and so[1] in "23":
        return "LANDLINE"
    return "MOBILE"


def la_so_dien_thoai(raw: str) -> bool:
    """Tầng VALIDATION, đứng riêng và không biết gì về hoa văn."""
    chi_so = re.sub(r"\D", "", raw or "")
    if not (SO_IT_NHAT <= len(chi_so) <= SO_NHIEU_NHAT):
        return False
    goc = (raw or "").strip()
    return goc.startswith(("0", "+84")) or chi_so.startswith(("1900", "1800"))


# --------------------------------------------------------------- phân tích

def phan_tich(raw: str) -> dict:
    """Một chuỗi số thô -> bản kế hoạch đọc đầy đủ (mục 23).

    Giữ riêng ba thứ: chuỗi gốc, chuỗi đã chuẩn hoá, và các nhóm để đọc.
    """
    goc = (raw or "").strip()
    lam_viec = "0" + goc[3:].lstrip(".-   ") if goc.startswith("+84") else goc

    chi_so = re.sub(r"\D", "", lam_viec)
    if not (SO_IT_NHAT <= len(chi_so) <= SO_NHIEU_NHAT):
        return {}

    # Nhóm theo dấu ngăn NGƯỜI VIẾT đặt — tín hiệu mạnh, nhưng không mù quáng
    # theo: tầng chấm điểm sẽ bỏ nếu nó tạo ra nhịp đọc kém (mục 6, 22).
    nhom_dau = [x for x in DAU_NGAN.split(lam_viec) if x.isdigit()]

    ke = sdt_nhip.lap_ke_hoach(chi_so, nhom_dau, phan_loai(chi_so))
    ke["original"] = goc
    return ke


# --------------------------------------------------------------- sang lời

# Nghỉ -> dấu câu. VieNeu nhận văn bản thuần, không có SSML, nên đây là toàn
# bộ những gì điều khiển được về nhịp: dấu phẩy nghỉ ngắn, dấu chấm nghỉ dài.
DAU_THEO_NGHI = {"NONE": " ", "SHORT": ", ", "MEDIUM": ". ", "LONG": ". "}


def _doc_nhom(nhom: str) -> str:
    chu = " ".join(CHU_SO[c] for c in nhom if c in CHU_SO)
    return chu[:1].upper() + chu[1:] if chu else ""


def sang_loi(ke: dict) -> str:
    """Metadata -> chữ cho VieNeu đọc.

    CHƯA làm được phần NHẤN. VieNeu nhận văn bản thuần: không có SSML, không
    có tham số nhấn từng cụm. Metadata vẫn mang đủ `emphasis` để khi nào đổi
    sang engine hỗ trợ SSML thì cắm vào ngay, còn ở đây chỉ dùng được nhịp
    nghỉ. Đừng bịa ra cách "nhấn" bằng cách viết hoa hay lặp chữ — mô hình sẽ
    đọc ra thứ khác hẳn.
    """
    phan = []
    for s in ke.get("segments", []):
        phan.append(_doc_nhom(s["text"]))
        phan.append(DAU_THEO_NGHI.get(s.get("pause_after", "SHORT"), ", "))
    return "".join(phan).strip().rstrip(",.").strip()


def doc_so(raw: str) -> str:
    """Chuỗi số thô -> chữ. Trả rỗng nếu không phải số điện thoại."""
    ke = phan_tich(raw)
    return sang_loi(ke) if ke else ""


def _thay(m):
    ra = doc_so(m.group(0))
    return ra if ra else m.group(0)


def chuan_hoa(text: str) -> str:
    """Thay mọi số điện thoại trong văn bản bằng cách đọc thành chữ."""
    return MAU.sub(_thay, text or "")
