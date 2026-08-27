# -*- coding: utf-8 -*-
"""PhoneNumberProsodyEngine — chia nhóm và lên kế hoạch ngắt nghỉ.

Tách bạch hai khái niệm (mục 4 của đặc tả):
    GROUPING  quyết định  0987 | 654 | 321
    PROSODY   quyết định  nghỉ bao lâu ở đâu, nhấn chỗ nào

Không sinh SSML ở đây. Trả METADATA; tầng chuyển sang TTS mới lo cách thể
hiện, vì mỗi engine một kiểu.

Cách làm: sinh nhiều phương án chia nhóm, chấm điểm, chọn phương án cao nhất
(mục 19) — chứ không viết cứng một cách chia duy nhất.
"""

from . import sdt_mau

# Giới hạn cứng: không đọc liền quá 4 chữ số trong một nhịp (mục 3).
SO_CHU_SO_TOI_DA = 4

NGHI = ("NONE", "SHORT", "MEDIUM", "LONG")
NHAN = ("NORMAL", "MEDIUM", "STRONG")

# Cách chia quen thuộc theo độ dài. Cái đầu tiên là mặc định (mục 7).
CHIA_QUEN = {
    8:  [(4, 4)],
    9:  [(4, 3, 2), (3, 3, 3)],
    10: [(4, 3, 3), (3, 3, 4), (4, 4, 2), (3, 4, 3)],
    11: [(4, 3, 4), (4, 4, 3), (3, 4, 4)],
    12: [(4, 4, 4), (4, 3, 3, 2)],
}

# Hoa văn đủ mạnh để đáng bẻ ranh giới nhóm theo nó.
NHAN_THEO_MAU = {
    "QUINT_DIGIT": ("LONG", "STRONG"),
    "QUAD_DIGIT": ("MEDIUM", "STRONG"),
    "TRIPLE_DIGIT": ("MEDIUM", "MEDIUM"),
    "REPEATING_BLOCK": ("MEDIUM", "MEDIUM"),
    "DOUBLE_BLOCK": ("SHORT", "MEDIUM"),
}


def _cat(so: str, moc) -> list:
    ra, i = [], 0
    for m in moc:
        ra.append(so[i:i + m])
        i += m
    return [x for x in ra if x] if i == len(so) else []


def _chia_deu(khuc: str) -> list:
    """Cắt một khúc dài thành các nhóm <= 4, chia ĐỀU nhất có thể.

    Cắt tham lam 4-4-… để lại nhóm một chữ số ở cuối: 88888 -> 8888 | 8.
    Nhóm một chữ số nghe cụt lủn và làm cả phương án bị chấm điểm thấp, nên
    hoa văn thua cách chia quen thuộc dù nó mạnh hơn. Chia đều thì 88888 ->
    888 | 88, nghe liền hơi hơn hẳn.
    """
    n = len(khuc)
    if n <= SO_CHU_SO_TOI_DA:
        return [khuc]
    so_nhom = -(-n // SO_CHU_SO_TOI_DA)          # làm tròn lên
    co_ban, du = divmod(n, so_nhom)
    ra, i = [], 0
    for k in range(so_nhom):
        lay = co_ban + (1 if k < du else 0)
        ra.append(khuc[i:i + lay])
        i += lay
    return ra


def _tu_mau(so: str, mau) -> list:
    """Chia nhóm bám theo ranh giới một hoa văn: trước / hoa văn / sau.

    Hoa văn dài hơn 4 chữ số vẫn phải cắt nhỏ để giữ giới hạn cứng, nhưng
    metadata sẽ ghi nó là một khối ngữ nghĩa (mục 12).
    """
    b, d = mau["bat_dau"], mau["dai"]
    nhom = []
    for khuc in (so[:b], so[b:b + d], so[b + d:]):
        if khuc:
            nhom.extend(_chia_deu(khuc))
    return nhom


def _ung_vien(so: str, nhom_dau: list, hoa_van: list) -> list:
    """Sinh các phương án chia nhóm."""
    ds = []
    if nhom_dau and all(len(x) <= SO_CHU_SO_TOI_DA for x in nhom_dau):
        ds.append(("SEPARATOR", nhom_dau))
    for moc in CHIA_QUEN.get(len(so), []):
        c = _cat(so, moc)
        if c:
            ds.append(("QUEN", c))
    for m in hoa_van[:3]:
        c = _tu_mau(so, m)
        if c:
            ds.append(("MAU", c))
    if not ds:                                   # độ dài lạ: 4 rồi 3 một nhóm
        moc, con = [4], len(so) - 4
        while con > 0:
            moc.append(3 if con > 3 else con)
            con -= moc[-1]
        ds.append(("QUEN", _cat(so, moc)))

    # bỏ trùng, giữ thứ tự
    thay, giu = set(), []
    for nguon, c in ds:
        k = "|".join(c)
        if k not in thay:
            thay.add(k)
            giu.append((nguon, c))
    return giu


def _cham_diem(nhom: list, nguon: str, hoa_van: list, co_dau_ngan: bool) -> float:
    """Chấm điểm một phương án chia nhóm (mục 19)."""
    if any(len(x) > SO_CHU_SO_TOI_DA for x in nhom):
        return -1e9                                  # giới hạn cứng, loại thẳng

    d = 0.0
    if nguon == "SEPARATOR" and co_dau_ngan:
        d += 6.0                                     # người viết đã chủ động ngăn
    if nguon == "QUEN":
        d += 3.0                                     # cách chia quen tai

    # Giữ trọn hoa văn trong MỘT nhóm thì cộng; cắt đôi hoa văn thì trừ.
    moc = []
    i = 0
    for x in nhom:
        moc.append((i, i + len(x)))
        i += len(x)
    for m in hoa_van[:4]:
        b, e = m["bat_dau"], m["bat_dau"] + m["dai"]
        tron = any(a <= b and e <= z for a, z in moc)
        if tron:
            d += 2.0 + m["dai"] * 0.4
        elif m["dai"] <= SO_CHU_SO_TOI_DA:
            d -= 1.5                                 # bẻ gãy hoa văn vừa nhóm

    d -= max(0, len(nhom) - 3) * 1.2                 # quá nhiều nhóm thì khó nhớ
    d -= sum(1 for x in nhom if len(x) == 1) * 2.0   # nhóm một chữ số nghe cụt
    return d


def _lap_ke_hoach(nhom: list, hoa_van: list) -> list:
    """Gắn nghỉ và nhấn cho từng nhóm.

    Mặc định nghỉ ngắn giữa các nhóm, không nhấn. Chỉ nhấn khi nhóm ĐÚNG BẰNG
    một hoa văn rõ ràng (mục 21) — không làm giọng đọc thành quảng cáo.
    """
    moc, i = [], 0
    for x in nhom:
        moc.append((i, i + len(x)))
        i += len(x)

    ke = []
    for k, (x, (b, e)) in enumerate(zip(nhom, moc)):
        cuoi = k == len(nhom) - 1
        nghi = "NONE" if cuoi else "SHORT"
        nhan = "NORMAL"
        khoi = False
        for m in hoa_van:
            if m["bat_dau"] == b and m["dai"] == len(x) and m["loai"] in NHAN_THEO_MAU:
                nghi_m, nhan_m = NHAN_THEO_MAU[m["loai"]]
                if not cuoi:
                    nghi = nghi_m
                nhan = nhan_m
                khoi = bool(m.get("nhom_ngu_nghia"))
                break
        ke.append({"text": x, "pause_after": nghi, "emphasis": nhan,
                   "semantic_group": khoi})
    return ke


def lap_ke_hoach(so: str, nhom_dau=None, loai="MOBILE") -> dict:
    """Vào: dãy chữ số đã chuẩn hoá + nhóm theo dấu ngăn người viết đặt.
    Ra: bản kế hoạch đọc dạng metadata (mục 23)."""
    so = "".join(c for c in (so or "") if c.isdigit())
    if not so:
        return {"normalized": "", "type": loai, "patterns": [], "segments": []}

    hoa_van = sdt_mau.phan_tich(so)
    co_dau = bool(nhom_dau) and len(nhom_dau) > 1

    tot_nhat, diem_nhat = None, None
    for nguon, c in _ung_vien(so, nhom_dau or [], hoa_van):
        d = _cham_diem(c, nguon, hoa_van, co_dau)
        if diem_nhat is None or d > diem_nhat:
            tot_nhat, diem_nhat = c, d

    return {
        "normalized": so,
        "type": loai,
        "patterns": hoa_van,
        "segments": _lap_ke_hoach(tot_nhat, hoa_van),
        "score": diem_nhat,
    }
