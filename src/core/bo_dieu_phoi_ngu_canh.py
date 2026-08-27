# -*- coding: utf-8 -*-
"""Bộ Điều Phối Ngữ Cảnh Đa Miền (bo_dieu_phoi_ngu_canh.py)

Tự động nhận diện cú pháp đặc thù của từng thể loại văn bản trong đời sống
(Hành chính Pháp quy NĐ 30/2020/NĐ-CP / Đảng TW 66-QĐ/TW / Khoa học STEM / Tin tức)
để kích hoạt bộ chuyển ngữ thích hợp nhất mà không gây ép chuỗi mù quáng.
"""

import re
from . import bo_chuyen_ngu_khoa_hoc as stem


# ---------------------------------------------------------------------------
# 1. TỪ ĐIỂN LOẠI VĂN BẢN (Nghị định 30/2020/NĐ-CP Phụ lục I & VBQPPL & Đảng)
# ---------------------------------------------------------------------------
TEN_LOAI_VAN_BAN = {
    # Văn bản Quy phạm pháp luật & Hành chính thông thường (NĐ 30/2020/NĐ-CP)
    "NĐ": "Nghị định",
    "QĐ": "Quyết định",
    "NQ": "Nghị quyết",
    "TT": "Thông tư",
    "TTLT": "Thông tư liên tịch",
    "CT": "Chỉ thị",
    "KL": "Kết luận",
    "TB": "Thông báo",
    "BC": "Báo cáo",
    "KH": "Kế hoạch",
    "PA": "Phương án",
    "ĐA": "Đề án",
    "DA": "Dự án",
    "HD": "Hướng dẫn",     # HD (D không dấu) = Hướng dẫn
    "HĐ": "Hợp đồng",      # HĐ (Đ có dấu) = Hợp đồng (Theo Phụ lục I NĐ 30/2020/NĐ-CP)
    "BB": "Biên bản",
    "TTr": "Tờ trình",
    "CĐ": "Công điện",
    "CV": "Công văn",
    "CTr": "Chương trình",
    "QC": "Quy chuẩn",
    "QCh": "Quy chế",
    "L": "Luật",
    "PL": "Pháp lệnh",
    "SL": "Sắc lệnh",
    "SLu": "Sắc luật",
    "BK": "Bản kê",
    "BTL": "Bản trích lục",
    "BCĐ": "Báo cáo chuyên đề",
    "GCN": "Giấy chứng nhận",
    "GGT": "Giấy giới thiệu",
    "GNP": "Giấy nghỉ phép",
    "GĐĐ": "Giấy đi đường",
    "GB": "Giấy biên nhận",
    "PXL": "Phiếu xử lý",
    "PPH": "Phiếu phối hợp",
    "PGT": "Phiếu gửi",
    "PCH": "Phiếu chuyển",
    "TĐ": "Thư điện tử",
}

# ---------------------------------------------------------------------------
# 2. TỪ ĐIỂN CƠ QUAN BAN HÀNH & ĐƠN VỊ TRỰC THUỘC
# ---------------------------------------------------------------------------
TEN_CO_QUAN = {
    # Cơ quan cấp Trung ương / Chính phủ / Quốc hội / Tư pháp
    "CP": "Chính phủ",
    "TTg": "Thủ tướng Chính phủ",
    "QH": "Quốc hội",
    "UBTVQH": "Ủy ban Thường vụ Quốc hội",
    "CTN": "Chủ tịch nước",
    "TANDTC": "Tòa án nhân dân tối cao",
    "VKSNDTC": "Viện kiểm sát nhân dân tối cao",
    "KTNN": "Kiểm toán Nhà nước",
    "VPCP": "Văn phòng Chính phủ",
    "TTCP": "Thanh tra Chính phủ",
    "NHNN": "Ngân hàng Nhà nước",
    "UBDT": "Ủy ban Dân tộc",

    # Các Bộ & Cơ quan ngang Bộ
    "BQP": "Bộ Quốc phòng",
    "BCA": "Bộ Công an",
    "BNG": "Bộ Ngoại giao",
    "BTP": "Bộ Tư pháp",
    "BTC": "Bộ Tài chính",
    "BCT": "Bộ Công Thương",
    "BNNPTNT": "Bộ Nông nghiệp và Phát triển nông thôn",
    "BGTVT": "Bộ Giao thông vận tải",
    "BXD": "Bộ Xây dựng",
    "BTNMT": "Bộ Tài nguyên và Môi trường",
    "BTTTT": "Bộ Thông tin và Truyền thông",
    "BLĐTBXH": "Bộ Lao động Thương binh và Xã hội",
    "BVHTTDL": "Bộ Văn hóa Thể thao và Du lịch",
    "BKHCN": "Bộ Khoa học và Công nghệ",
    "BGDĐT": "Bộ Giáo dục và Đào tạo",
    "BYT": "Bộ Y tế",
    "BNV": "Bộ Nội vụ",
    "BKHĐT": "Bộ Kế hoạch và Đầu tư",

    # Chính quyền Địa phương
    "UBND": "Ủy ban nhân dân",
    "HĐND": "Hội đồng nhân dân",

    # Tổ chức Đảng (Quy định 66-QĐ/TW)
    "TW": "Trung ương",
    "TƯ": "Trung ương",
    "TU": "Tỉnh ủy",
    "BTCTW": "Ban Tổ chức Trung ương",
    "BTGTW": "Ban Tuyên giáo Trung ương",
    "UBKTTW": "Ủy ban Kiểm tra Trung ương",
    "BDNTW": "Ban Dân vận Trung ương",
    "BNCTW": "Ban Nội chính Trung ương",
    "BKTTW": "Ban Kinh tế Trung ương",
    "VPTW": "Văn phòng Trung ương Đảng",
}


MAP_LOAI_UPPER = {k.upper(): v for k, v in TEN_LOAI_VAN_BAN.items()}
MAP_CO_QUAN_UPPER = {k.upper(): v for k, v in TEN_CO_QUAN.items()}


PAT_QUOC_HIEU = re.compile(r"(?i)\bCộng\s+(?:hòa|hoà)\s+xã\s+hội\s+chủ\s+nghĩa\s+việt\s+nam\b")
PAT_TIEU_NGU = re.compile(r"(?i)\bĐộc\s+lập\s*[-–—,]\s*Tự\s+do\s*[-–—,]\s*Hạnh\s+phúc\b")
PAT_VBPQ_1 = re.compile(r"(?i)(?:\bsố\s*:\s*|\bsố\s+)?(\d+)/(\d{4})/([A-Za-zĐđ]+)-([A-Za-zĐđ\-_]+)")
PAT_VBPQ_1B = re.compile(r"(?i)(?:\bsố\s*:\s*|\bsố\s+)?(\d+)/([A-Za-zĐđ]{2,})-([A-Za-zĐđ\-_]+)")
PAT_VBPQ_2 = re.compile(r"(?i)(?:\bsố\s*:\s*|\bsố\s+)?(\d+)/(\d{4})/QH(\d+)")
PAT_VBPQ_3 = re.compile(r"(?i)(?:\bsố\s*:\s*|\bsố\s+)?(\d+)-([A-Za-zĐđ]+)/([A-Za-zĐđ\-_]+)")
PAT_VBPQ_4 = re.compile(r"(?i)(?:\bsố\s*:\s*|\bsố\s+)?(\d+)-([A-Za-zĐđ]+)/(\d{4})")

TU_VIET_TAT_DON_RAW = [
    (r"(?i)\bNĐ\s*[-/]\s*CP\b", "Nghị định Chính phủ"),
    (r"(?i)\bQĐ\s*[-/]\s*TTg\b", "Quyết định Thủ tướng Chính phủ"),
    (r"(?i)\bNQ\s*[-/]\s*CP\b", "Nghị quyết Chính phủ"),
    (r"(?i)\bTT\s*[-/]\s*BCA\b", "Thông tư Bộ Công an"),
    (r"(?i)\bTT\s*[-/]\s*BQP\b", "Thông tư Bộ Quốc phòng"),
    (r"(?i)\bTT\s*[-/]\s*BYT\b", "Thông tư Bộ Y tế"),
    (r"(?i)\bTT\s*[-/]\s*BGDĐT\b", "Thông tư Bộ Giáo dục và Đào tạo"),
    (r"(?i)\bTT\s*[-/]\s*BNV\b", "Thông tư Bộ Nội vụ"),
    (r"(?i)\bTT\s*[-/]\s*BTC\b", "Thông tư Bộ Tài chính"),
    (r"(?i)\bTT\s*[-/]\s*BTP\b", "Thông tư Bộ Tư pháp"),
    (r"(?i)\bTT\s*[-/]\s*BKHĐT\b", "Thông tư Bộ Kế hoạch và Đầu tư"),
    (r"(?i)\bTT\s*[-/]\s*BTTTT\b", "Thông tư Bộ Thông tin và Truyền thông"),
    (r"(?i)\bTT\s*[-/]\s*BLĐTBXH\b", "Thông tư Bộ Lao động Thương binh và Xã hội"),
    (r"(?i)\bVBQPPL\b", "Văn bản quy phạm pháp luật"),
    (r"(?i)\bUBND\b", "Ủy ban nhân dân"),
    (r"(?i)\bHĐND\b", "Hội đồng nhân dân"),
    (r"(?i)\bBCH\b", "Ban chấp hành"),
    (r"\bTƯ\b|\bTW\b|\bT\.Ư\b", "Trung ương"),
    (r"(?i)\bVPCP\b", "Văn phòng Chính phủ"),
    (r"(?i)\bTTg\b", "Thủ tướng Chính phủ"),
    (r"(?i)\bCTN\b", "Chủ tịch nước"),
    (r"(?i)\bTANDTC\b", "Tòa án nhân dân tối cao"),
    (r"(?i)\bVKSNDTC\b", "Viện kiểm sát nhân dân tối cao"),
    (r"(?i)\bKTNN\b", "Kiểm toán Nhà nước"),
    (r"(?i)\bTTCP\b", "Thanh tra Chính phủ"),
    (r"(?i)\bNHNN\b", "Ngân hàng Nhà nước"),
    (r"(?i)\bUBDT\b", "Ủy ban Dân tộc"),
]
TU_VIET_TAT_DON = [(re.compile(p), r) for p, r in TU_VIET_TAT_DON_RAW]


def _chuan_hoa_so_van_ban_phap_quy(text: str) -> str:
    """Đọc số ký hiệu văn bản quy phạm pháp luật & hành chính theo chuẩn Quốc gia."""
    s = text or ""

    # Quốc hiệu & Tiêu ngữ chuẩn Quốc gia (NĐ 30/2020/NĐ-CP)
    s = PAT_QUOC_HIEU.sub("Cộng hòa Xã hội Chủ nghĩa Việt Nam.", s)
    s = PAT_TIEU_NGU.sub("Độc lập - Tự do - Hạnh phúc.", s)

    # Dạng 1: [Số[:] ] 30/2020/NĐ-CP, 01/2021/TT-BGDĐT
    def _sub_vbpq(m):
        so, nam, loai, cq = m.group(1), m.group(2), m.group(3), m.group(4)
        loai_up = loai.upper().replace("-", "").replace("_", "")
        cq_up = cq.upper().replace("-", "").replace("_", "")
        ten_l = MAP_LOAI_UPPER.get(loai_up, loai)
        ten_c = MAP_CO_QUAN_UPPER.get(cq_up, cq)
        so_doc = str(int(so)) if so.isdigit() else so
        return f"số {so_doc} năm {nam} {ten_l} {ten_c}"

    s = PAT_VBPQ_1.sub(_sub_vbpq, s)

    # Dạng 1b: [Số[:] ] 12/BC-UBND, 15/QĐ-UBND, 24/TB-VPCP (không có năm)
    def _sub_vbpq_ko_nam(m):
        so, loai, cq = m.group(1), m.group(2), m.group(3)
        loai_up = loai.upper().replace("-", "").replace("_", "")
        cq_up = cq.upper().replace("-", "").replace("_", "")
        ten_l = MAP_LOAI_UPPER.get(loai_up, loai)
        ten_c = MAP_CO_QUAN_UPPER.get(cq_up, cq)
        so_doc = str(int(so)) if so.isdigit() else so
        return f"số {so_doc} {ten_l} {ten_c}"

    s = PAT_VBPQ_1B.sub(_sub_vbpq_ko_nam, s)

    # Dạng 2: [Số[:] ] 45/2019/QH14, 15/2024/QH15
    def _sub_qh(m):
        so, nam, khoa = m.group(1), m.group(2), m.group(3)
        so_doc = str(int(so)) if so.isdigit() else so
        return f"số {so_doc} năm {nam} Quốc hội khóa {khoa}"

    s = PAT_VBPQ_2.sub(_sub_qh, s)

    # Dạng 3: [Số[:] ] 66-QĐ/TW, 05-HD/BTCTW
    def _sub_dang(m):
        so, loai, cq = m.group(1), m.group(2), m.group(3)
        loai_up = loai.upper().replace("-", "").replace("_", "")
        cq_up = cq.upper().replace("-", "").replace("_", "")
        ten_l = MAP_LOAI_UPPER.get(loai_up, loai)
        ten_c = MAP_CO_QUAN_UPPER.get(cq_up, cq)
        so_doc = str(int(so)) if so.isdigit() else so
        return f"số {so_doc} {ten_l} {ten_c}"

    s = PAT_VBPQ_3.sub(_sub_dang, s)

    # Dạng 4: [Số[:] ] 12-HĐ/2024
    def _sub_hd_nam(m):
        so, loai, nam = m.group(1), m.group(2), m.group(3)
        loai_up = loai.upper().replace("-", "").replace("_", "")
        ten_l = MAP_LOAI_UPPER.get(loai_up, loai)
        so_doc = str(int(so)) if so.isdigit() else so
        return f"số {so_doc} {ten_l} năm {nam}"

    s = PAT_VBPQ_4.sub(_sub_hd_nam, s)

    # Các từ viết tắt cơ quan / chức danh độc lập
    for pat, repl in TU_VIET_TAT_DON:
        s = pat.sub(repl, s)

    return s


# ---------------------------------------------------------------------------
# 3. BỘ TỪ ĐIỂN TIN TỨC, TÀI CHÍNH & CÔNG NGHỆ
# ---------------------------------------------------------------------------
PAT_TIN_TUC = [
    (re.compile(r"\bVN-Index\b"), "Vê En In đêch"),
    (re.compile(r"\bHNX-Index\b"), "Hát En Ích In đêch"),
    (re.compile(r"\bGDP\b"), "Gờ Đê Phê"),
    (re.compile(r"\bFDI\b"), "Ép Đê I"),
    (re.compile(r"\bVPS\b"), "Vê Pê Ép"),
    (re.compile(r"\bChatGPT\b"), "Chát Gờ Pê Tê"),
    (re.compile(r"\bWHO\b"), "Tổ chức Y tế Thế giới"),
    (re.compile(r"\bWTO\b"), "Tổ chức Thương mại Thế giới"),
]


def _chuan_hoa_tin_tuc(text: str) -> str:
    s = text or ""
    for pat, repl in PAT_TIN_TUC:
        s = pat.sub(repl, s)
    return s


PAT_DIA_CHI = [
    # Quý tài chính: Q1/2026, Q2 2026
    (re.compile(r"(?i)\bQ([1-4])\s*/\s*(\d{4})\b"), r"Quý \1 năm \2"),
    (re.compile(r"(?i)\bQ([1-4])\s+(\d{4})\b"), r"Quý \1 năm \2"),
    # Thành phố viết tắt
    (re.compile(r"(?i)\bTP\.?HCM\b"), "Thành phố Hồ Chí Minh"),
    (re.compile(r"(?i)\bTP\.?HN\b"), "Thành phố Hà Nội"),
    (re.compile(r"(?i)\bTP\s*\.\s*(?=[A-ZÀ-Ỹ])"), "Thành phố "),
    # Quận viết tắt: Q1 -> Q12 hoặc Q.1 -> Q.12
    (re.compile(r"(?i)\bQ\s*\.?\s*([1-9]|1[0-2])\b"), r"Quận \1"),
    (re.compile(r"(?i)\bQ\s*\.\s*(?=[A-ZÀ-Ỹ])"), "Quận "),
    # Phường viết tắt: P1 -> P30 hoặc P.1 -> P.30
    (re.compile(r"(?i)\bP\s*\.?\s*([1-9]|[12]\d|30)\b"), r"Phường \1"),
    (re.compile(r"(?i)\bP\s*\.\s*(?=[A-ZÀ-Ỹ])"), "Phường "),
    # Thị xã, Thị trấn, Huyện:
    (re.compile(r"(?i)\bTX\s*\.\s*(?=[A-ZÀ-Ỹ])"), "Thị xã "),
    (re.compile(r"(?i)\bTT\s*\.\s*(?=[A-ZÀ-Ỹ])"), "Thị trấn "),
    (re.compile(r"(?i)\bH\s*\.\s*(?=[A-ZÀ-Ỹ])"), "Huyện "),
]


def _chuan_hoa_dia_chi(text: str) -> str:
    """Chuẩn hóa viết tắt địa danh hành chính (Quận, Phường, Thị xã, Tỉnh/Thành phố)."""
    s = text or ""
    for pat, repl in PAT_DIA_CHI:
        s = pat.sub(repl, s)
    return s


# ---------------------------------------------------------------------------
# 4. BỘ ĐIỀU PHỐI TỔNG HỢP THEO NGỮ CẢNH (Universal Semantic Router)
# ---------------------------------------------------------------------------
def dieu_phoi_ngu_canh(text: str, cfg: dict = None) -> str:
    """Điều phối và áp dụng bộ chuẩn hóa ngữ cảnh thích hợp nhất cho văn bản."""
    if not text:
        return ""
    cfg = cfg or {}
    s = text

    # 1. Chuyển ngữ Hành chính & Pháp quy (NĐ 30/2020/NĐ-CP & Đảng)
    s = _chuan_hoa_so_van_ban_phap_quy(s)

    # 2. Chuyển ngữ Địa chỉ & Địa danh hành chính
    s = _chuan_hoa_dia_chi(s)

    # 3. Chuyển ngữ Tin tức & Công nghệ
    s = _chuan_hoa_tin_tuc(s)

    # 4. Chuyển ngữ Khoa học & STEM Chuyên sâu (Toán, Lý, Hóa, Đơn vị SI)
    s = stem.chuyen_ngu_stem_toan_dien(s)

    return s
