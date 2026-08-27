# -*- coding: utf-8 -*-
"""PhoneNumberPatternAnalyzer — tìm hoa văn trong dãy số đã chuẩn hoá.

Tầng NÀY KHÔNG quyết định số có phải điện thoại hay không, và cũng không
quyết định đọc thế nào. Nó chỉ trả về: trong dãy này có những hoa văn gì, nằm
ở đâu, dài bao nhiêu, mạnh cỡ nào.

Hai tầng phải độc lập (mục 26 của đặc tả):
    PHONE VALIDATION      -> có phải số điện thoại không?
    PHONE PATTERN ANALYSIS -> số hợp lệ đó nên đọc thế nào?
Một số điện thoại bình thường vẫn phải đọc đúng dù không có hoa văn nào.

Các tên tam hoa / tứ quý / phong thuỷ ở đây là HEURISTIC PHỤC VỤ CÁCH ĐỌC,
không phải khẳng định số đẹp hay xấu.
"""

# Ưu tiên: hoa văn cụ thể hơn thắng hoa văn tổng quát (mục 18).
UU_TIEN = [
    "QUINT_DIGIT", "QUAD_DIGIT", "TRIPLE_DIGIT",
    "REPEATING_BLOCK", "DOUBLE_BLOCK",
    "PALINDROME", "MIRROR", "SYMMETRIC",
    "SEQUENTIAL_ASCENDING", "SEQUENTIAL_DESCENDING",
    "DOUBLE_DIGIT", "REPEATED_DIGIT",
]
DIEM_UU_TIEN = {t: len(UU_TIEN) - i for i, t in enumerate(UU_TIEN)}

DAI_THEO_LAP = {2: "DOUBLE_DIGIT", 3: "TRIPLE_DIGIT",
                4: "QUAD_DIGIT", 5: "QUINT_DIGIT"}

DAI_IT_NHAT_TIEN = 4        # 1234 mới coi là số tiến
DAI_IT_NHAT_GANH = 4        # 1221 mới coi là số gánh


def _lap_lien_tiep(so: str) -> list:
    """Chuỗi cùng một chữ số lặp liên tiếp: 888, 8888, 88888…"""
    ra, i = [], 0
    while i < len(so):
        j = i
        while j + 1 < len(so) and so[j + 1] == so[i]:
            j += 1
        dai = j - i + 1
        if dai >= 2:
            loai = DAI_THEO_LAP.get(dai, "REPEATED_DIGIT")
            ra.append({"loai": loai, "gia_tri": so[i:j + 1],
                       "bat_dau": i, "dai": dai, "chu_so": so[i],
                       "nhom_ngu_nghia": dai > 4})
        i = j + 1
    return ra


def _day_tien(so: str) -> list:
    """Chuỗi tăng hoặc giảm đều 1 đơn vị: 1234, 987654…"""
    ra, i = [], 0
    while i < len(so):
        for buoc, loai in ((1, "SEQUENTIAL_ASCENDING"), (-1, "SEQUENTIAL_DESCENDING")):
            j = i
            while j + 1 < len(so) and int(so[j + 1]) - int(so[j]) == buoc:
                j += 1
            dai = j - i + 1
            if dai >= DAI_IT_NHAT_TIEN:
                ra.append({"loai": loai, "gia_tri": so[i:j + 1],
                           "bat_dau": i, "dai": dai, "nhom_ngu_nghia": True})
                i = j
                break
        i += 1
    return ra


def _khoi_lap(so: str) -> list:
    """Khối lặp lại: 123123, 121212, 686868…"""
    ra = []
    n = len(so)
    for dai_khoi in (2, 3, 4):
        i = 0
        while i + dai_khoi * 2 <= n:
            khoi = so[i:i + dai_khoi]
            lan = 1
            while so[i + lan * dai_khoi:i + (lan + 1) * dai_khoi] == khoi:
                lan += 1
            if lan >= 2 and len(set(khoi)) > 1:      # 888888 để _lap_lien_tiep lo
                ra.append({
                    "loai": "DOUBLE_BLOCK" if lan == 2 else "REPEATING_BLOCK",
                    "gia_tri": khoi * lan, "bat_dau": i,
                    "dai": dai_khoi * lan, "khoi": khoi, "so_lan": lan,
                    "nhom_ngu_nghia": True,
                })
                i += dai_khoi * lan
            else:
                i += 1
    return ra


def _doi_xung(so: str) -> list:
    """Số gánh / đối xứng: 1221, 3443, 12321…"""
    ra = []
    n = len(so)
    for i in range(n):
        for j in range(i + DAI_IT_NHAT_GANH, n + 1):
            khuc = so[i:j]
            if khuc == khuc[::-1] and len(set(khuc)) > 1:
                loai = "PALINDROME" if len(khuc) % 2 else "MIRROR"
                ra.append({"loai": loai, "gia_tri": khuc, "bat_dau": i,
                           "dai": len(khuc), "nhom_ngu_nghia": True})
    # Giữ khúc dài nhất tại mỗi vị trí bắt đầu, bỏ các khúc con của nó.
    ra.sort(key=lambda x: (-x["dai"], x["bat_dau"]))
    giu, da_phu = [], set()
    for m in ra:
        vung = set(range(m["bat_dau"], m["bat_dau"] + m["dai"]))
        if vung & da_phu:
            continue
        giu.append(m)
        da_phu |= vung
    return giu


def phan_tich(so: str) -> list:
    """Trả danh sách hoa văn, đã xếp theo độ mạnh giảm dần.

    `diem` = ưu tiên loại × độ dài, để tầng ngắt nhịp cân nhắc khi có nhiều
    hoa văn chồng lấn nhau.
    """
    so = "".join(c for c in (so or "") if c.isdigit())
    if not so:
        return []

    ds = _lap_lien_tiep(so) + _day_tien(so) + _khoi_lap(so) + _doi_xung(so)
    # DOUBLE_DIGIT quá phổ biến, tự nó không đáng để đổi cách chia nhóm.
    ds = [m for m in ds if m["loai"] != "DOUBLE_DIGIT" or m["dai"] > 2]

    for m in ds:
        m.setdefault("nhom_ngu_nghia", False)
        m["diem"] = DIEM_UU_TIEN.get(m["loai"], 0) * m["dai"]
    ds.sort(key=lambda x: (-x["diem"], x["bat_dau"]))
    return ds
