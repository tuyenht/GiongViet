# -*- coding: utf-8 -*-
"""Module Chuyển ngữ Khoa học & STEM Chuyên sâu (bo_chuyen_ngu_khoa_hoc.py)

Chuyển đổi công thức Toán học, Hóa học, Vật lý và Đơn vị kỹ thuật
thành câu đọc tiếng Việt tự nhiên, chuẩn mực sư phạm như thầy cô giảng bài.
"""

import re

# ---------------------------------------------------------------------------
# 1. ĐƠN VỊ ĐO LƯỜNG VẬT LÝ & KỸ THUẬT (Chỉ áp dụng khi đứng sau số lượng)
# ---------------------------------------------------------------------------

DON_VI_KEP = [
    (r"(\d+(?:[.,]\d+)?)\s*m/s²\b", r"\1 mét trên giây bình phương"),
    (r"(\d+(?:[.,]\d+)?)\s*m/s2\b", r"\1 mét trên giây bình phương"),
    (r"(\d+(?:[.,]\d+)?)\s*m/s\b", r"\1 mét trên giây"),
    (r"(\d+(?:[.,]\d+)?)\s*km/h\b", r"\1 ki lô mét trên giờ"),
    (r"(\d+(?:[.,]\d+)?)\s*kg/m³\b", r"\1 ki lô gam trên mét khối"),
    (r"(\d+(?:[.,]\d+)?)\s*kg/m3\b", r"\1 ki lô gam trên mét khối"),
    (r"(\d+(?:[.,]\d+)?)\s*g/cm³\b", r"\1 gam trên xăng ti mét khối"),
    (r"(\d+(?:[.,]\d+)?)\s*g/cm3\b", r"\1 gam trên xăng ti mét khối"),
    (r"(\d+(?:[.,]\d+)?)\s*kWh\b", r"\1 ki lô oát giờ"),
    (r"(\d+(?:[.,]\d+)?)\s*mol/l\b", r"\1 mol trên lít"),
]

DON_VI_DON = [
    # Điện & Từ
    (r"(\d+(?:[.,]\d+)?)\s*kV\b", r"\1 ki lô vôn"),
    (r"(\d+(?:[.,]\d+)?)\s*mV\b", r"\1 mi li vôn"),
    (r"(\d+(?:[.,]\d+)?)\s*V\b", r"\1 vôn"),
    (r"(\d+(?:[.,]\d+)?)\s*mA\b", r"\1 mi li am pe"),
    (r"(\d+(?:[.,]\d+)?)\s*µA\b", r"\1 mi crô am pe"),
    (r"(\d+(?:[.,]\d+)?)\s*uA\b", r"\1 mi crô am pe"),
    (r"(\d+(?:[.,]\d+)?)\s*A\b", r"\1 am pe"),
    (r"(\d+(?:[.,]\d+)?)\s*MW\b", r"\1 mê ga oát"),
    (r"(\d+(?:[.,]\d+)?)\s*kW\b", r"\1 ki lô oát"),
    (r"(\d+(?:[.,]\d+)?)\s*mW\b", r"\1 mi li oát"),
    (r"(\d+(?:[.,]\d+)?)\s*W\b", r"\1 oát"),
    (r"(\d+(?:[.,]\d+)?)\s*MΩ\b", r"\1 mê ga ôm"),
    (r"(\d+(?:[.,]\d+)?)\s*kΩ\b", r"\1 ki lô ôm"),
    (r"(\d+(?:[.,]\d+)?)\s*Ω\b", r"\1 ôm"),
    (r"(\d+(?:[.,]\d+)?)\s*µF\b", r"\1 mi crô pha ra"),
    (r"(\d+(?:[.,]\d+)?)\s*uF\b", r"\1 mi crô pha ra"),
    (r"(\d+(?:[.,]\d+)?)\s*nF\b", r"\1 na nô pha ra"),
    (r"(\d+(?:[.,]\d+)?)\s*pF\b", r"\1 pi cô pha ra"),
    (r"(\d+(?:[.,]\d+)?)\s*F\b", r"\1 pha ra"),
    (r"(\d+(?:[.,]\d+)?)\s*mH\b", r"\1 mi li hen ri"),
    (r"(\d+(?:[.,]\d+)?)\s*H\b(?!\d)", r"\1 hen ri"),
    (r"(\d+(?:[.,]\d+)?)\s*GHz\b", r"\1 ghi ga héc"),
    (r"(\d+(?:[.,]\d+)?)\s*MHz\b", r"\1 mê ga héc"),
    (r"(\d+(?:[.,]\d+)?)\s*kHz\b", r"\1 ki lô héc"),
    (r"(\d+(?:[.,]\d+)?)\s*Hz\b", r"\1 héc"),
    (r"(\d+(?:[.,]\d+)?)\s*dBm\b", r"\1 đề xi ben mi li oát"),
    (r"(\d+(?:[.,]\d+)?)\s*dB\b", r"\1 đề xi ben"),
    # Lực & Áp suất & Năng lượng
    (r"(\d+(?:[.,]\d+)?)\s*kN\b", r"\1 ki lô niu tơn"),
    (r"(\d+(?:[.,]\d+)?)\s*N\b", r"\1 niu tơn"),
    (r"(\d+(?:[.,]\d+)?)\s*kJ\b", r"\1 ki lô jun"),
    (r"(\d+(?:[.,]\d+)?)\s*J\b", r"\1 jun"),
    (r"(\d+(?:[.,]\d+)?)\s*kcal\b", r"\1 ki lô ca lo"),
    (r"(\d+(?:[.,]\d+)?)\s*cal\b", r"\1 ca lo"),
    (r"(\d+(?:[.,]\d+)?)\s*MPa\b", r"\1 mê ga pát xcan"),
    (r"(\d+(?:[.,]\d+)?)\s*kPa\b", r"\1 ki lô pát xcan"),
    (r"(\d+(?:[.,]\d+)?)\s*Pa\b", r"\1 pát xcan"),
    (r"(\d+(?:[.,]\d+)?)\s*bar\b", r"\1 ba"),
    (r"(\d+(?:[.,]\d+)?)\s*atm\b", r"\1 át mốt phe"),
    # Nhiệt độ & pH
    (r"(\d+(?:[.,]\d+)?)\s*°\s*C\b", r"\1 độ C"),
    (r"(\d+(?:[.,]\d+)?)\s*℃", r"\1 độ C"),
    (r"(\d+(?:[.,]\d+)?)\s*°\s*F\b", r"\1 độ F"),
    (r"(\d+(?:[.,]\d+)?)\s*K\b", r"\1 ken vin"),
    (r"(?i)\bpH\s*=\s*(\d+(?:[.,]\d+)?)", r"độ pH bằng \1"),
    (r"(?i)\bpH\s+(\d+(?:[.,]\d+)?)", r"độ pH \1"),
]


def chuyen_ngu_don_vi(text: str) -> str:
    """Chuyển đổi thứ nguyên và đơn vị đo lường vật lý."""
    s = text or ""
    for pat, repl in DON_VI_KEP:
        s = re.sub(pat, repl, s)
    for pat, repl in DON_VI_DON:
        s = re.sub(pat, repl, s)
    return s


# ---------------------------------------------------------------------------
# 2. TOÁN HỌC & GIẢI TÍCH (Mathematics)
# ---------------------------------------------------------------------------

KY_HIEU_TOAN_HOC = [
    # Ký hiệu so sánh & quan hệ
    (r"\s*≠\s*", " khác "),
    (r"\s*<=\s*", " nhỏ hơn hoặc bằng "),
    (r"\s*≤\s*", " nhỏ hơn hoặc bằng "),
    (r"\s*>=\s*", " lớn hơn hoặc bằng "),
    (r"\s*≥\s*", " lớn hơn hoặc bằng "),
    (r"\s*≈\s*", " xấp xỉ "),
    (r"\s*±\s*", " cộng trừ "),
    (r"\s*∈\s*", " thuộc "),
    (r"\s*∉\s*", " không thuộc "),
    (r"\s*⊂\s*", " tập con của "),
    (r"\s*∪\s*", " hợp "),
    (r"\s*∩\s*", " giao "),
    (r"\s*∅\s*", " tập rỗng "),
    (r"\s*=>\s*", " suy ra "),
    (r"\s*<=>\s*", " tương đương "),
    # Ký tự Hy Lạp toán học
    (r"\bDelta\b|\bΔ\b", "đen-ta"),
    (r"\balpha\b|\bα\b", "an-pha"),
    (r"\bbeta\b|\bβ\b", "bê-ta"),
    (r"\bgamma\b|\bγ\b", "ga-ma"),
    (r"\blambda\b|\bλ\b", "lam-đa"),
    (r"\bomega\b|\bω\b|\bΩ\b(?!\s*\d)", "ô-mê-ga"),
    (r"\bpi\b|\bπ\b", "pi"),
    (r"\btheta\b|\bθ\b", "thê-ta"),
    (r"\bsigma\b|\bσ\b|\b∑\b", "tổng xích-ma"),
    (r"\b∫\b", "tích phân"),
]


def chuyen_ngu_toan_hoc(text: str) -> str:
    """Chuyển đổi ký hiệu toán học thành lời đọc tự nhiên."""
    s = text or ""

    # Hàm số: f(x) -> f của x, g(t) -> g của t, P(x) -> P của x
    s = re.sub(r"\b([fghPQyF])\(([a-z0-9]+)\)", r"\1 của \2", s)

    # Lượng giác: sin(x) -> sin x, cos(x) -> cốt x, tan(x) -> tang x, cot(x) -> cô tang x
    s = re.sub(r"(?i)\bsin\^2\(([a-zA-Z0-9]+)\)", r"sin bình phương \1", s)
    s = re.sub(r"(?i)\bcos\^2\(([a-zA-Z0-9]+)\)", r"cốt bình phương \1", s)
    s = re.sub(r"(?i)\bsin\(([a-zA-Z0-9]+)\)", r"sin \1", s)
    s = re.sub(r"(?i)\bcos\(([a-zA-Z0-9]+)\)", r"cốt \1", s)
    s = re.sub(r"(?i)\btan\(([a-zA-Z0-9]+)\)", r"tang \1", s)
    s = re.sub(r"(?i)\bcot\(([a-zA-Z0-9]+)\)", r"cô tang \1", s)

    # Logarit: log_2(x) -> lô-ga cơ số 2 của x, ln(x) -> len x
    s = re.sub(r"(?i)\blog_(\d+)\(([a-zA-Z0-9]+)\)", r"lô ga cơ số \1 của \2", s)
    s = re.sub(r"(?i)\blog\(([a-zA-Z0-9]+)\)", r"lô ga của \1", s)
    s = re.sub(r"(?i)\bln\(([a-zA-Z0-9]+)\)", r"len \1", s)

    # Giới hạn: lim khi x tiến tới a
    def _repl_lim(m):
        var = m.group(1) or m.group(3) or "x"
        val = m.group(2) or m.group(4) or "0"
        return f"lim khi {var} tiến tới {val}"

    pat_lim = re.compile(
        r"(?i)\blim\s*(?:_\{?\s*([a-zA-Z0-9]+)\s*(?:->|→|tiến tới)\s*([a-zA-Z0-9\-+∞]+)\s*\}?|\(\s*([a-zA-Z0-9]+)\s*(?:->|→|tiến tới)\s*([a-zA-Z0-9\-+∞]+)\s*\))"
    )
    s = pat_lim.sub(_repl_lim, s)

    # Căn thức: √x -> căn bậc hai của x
    s = re.sub(r"√\((.+?)\)", r"căn bậc hai của \1", s)
    s = re.sub(r"√([a-zA-Z0-9]+)", r"căn bậc hai của \1", s)

    # Ký hiệu so sánh & quan hệ
    for pat, repl in KY_HIEU_TOAN_HOC:
        s = re.sub(pat, repl, s)

    return s


# ---------------------------------------------------------------------------
# 3. HÓA HỌC (Chemistry)
# ---------------------------------------------------------------------------

PAT_HOA_HOC = re.compile(
    r"(?:[0-9]*[A-Z][a-zA-Z0-9()]*\s*[\+]\s*)+[0-9]*[A-Z][a-zA-Z0-9()]*\s*(?:→|->|⇄|<=>)\s*[0-9A-Za-z \+\-()→\->⇄<=>]+"
)


def _chuan_hoa_pt_hoa_hoc(m: re.Match) -> str:
    """Biến đổi phương trình hóa học thành câu đọc tự nhiên."""
    raw = m.group(0)
    parts = re.split(r"\s*(?:→|->|⇄|<=>)\s*", raw, maxsplit=1)
    if len(parts) == 2:
        trai, phai = parts
        trai = re.sub(r"\s*\+\s*", " tác dụng với ", trai)
        phai = re.sub(r"\s*\+\s*", " và ", phai)
        mui_ten = " phản ứng thuận nghịch tạo thành " if ("⇄" in raw or "<=>" in raw) else " tạo thành "
        return f"{trai}{mui_ten}{phai}"
    return raw


def chuyen_ngu_hoa_hoc(text: str) -> str:
    """Chuyển đổi phương trình và công thức hóa học phức chất."""
    s = text or ""

    # 1. Nhận diện và chuyển ngữ phương trình hóa học trước
    s = PAT_HOA_HOC.sub(_chuan_hoa_pt_hoa_hoc, s)

    # 2. Xử lý nhóm nguyên tố trong ngoặc: Ca(OH)2 -> Ca OH 2 lần, Fe2(SO4)3 -> Fe2 SO4 3 lần
    s = re.sub(r"\b([A-Z][a-zA-Z0-9]*)\(([A-Z][a-zA-Z0-9]+)\)(\d+)\b", r"\1 \2 \3 lần", s)

    # 3. Muối ngậm nước: CuSO4.5H2O -> CuSO4 ngậm 5 H2O
    s = re.sub(r"\b([A-Z][a-z0-9]+)\.(\d+)H2O\b", r"\1 ngậm \2 H2O", s)

    # 4. Trạng thái chất trong ngoặc đơn
    s = re.sub(r"\s*\(r\)\b", " thể rắn", s)
    s = re.sub(r"\s*\(l\)\b", " thể lỏng", s)
    s = re.sub(r"\s*\((?:k|g)\)\b", " thể khí", s)
    s = re.sub(r"\s*\((?:dd|aq)\)\b", " dung dịch", s)

    return s


# ---------------------------------------------------------------------------
# Fast-path check: chỉ quét nếu có số, ký tự đặc thù hoặc công thức STEM
_STEM_CHARS = set("0123456789%°℃℉²³Ωµ±≠≤≥≈√∫∑→⇄<=>+*/^[]_")

def chuyen_ngu_stem_toan_dien(text: str) -> str:
    """Bộ chuyển ngữ khoa học tổng hợp: Đơn vị -> Hóa học -> Toán học (có Fast-Path)."""
    if not text:
        return ""
    # Fast-path: nếu câu không chứa chữ số hoặc ký hiệu khoa học thì bỏ qua toàn bộ regex STEM
    if not any(c in _STEM_CHARS for c in text):
        return text
    s = text
    s = chuyen_ngu_don_vi(s)
    s = chuyen_ngu_hoa_hoc(s)
    s = chuyen_ngu_toan_hoc(s)
    return s
