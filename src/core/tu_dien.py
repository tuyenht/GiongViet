# -*- coding: utf-8 -*-
"""Dữ liệu cho màn hình Từ điển phát âm.

Từ điển là bảng phẳng: chữ trong văn bản -> cách đọc. Bản thiết kế gốc có
thêm cột "Phạm vi" (áp cho danh sách công đức hay cho văn bản), nhưng
tudien.ini không có chỗ chứa thông tin đó và engine áp chung cho cả hai chế
độ - dựng cột ấy là bày ra một ô chọn không đổi được gì.
"""

import unicodedata

import DocCongDuc as engine


def _la_mac_dinh(tu: str) -> bool:
    return tu in engine.TUDIEN_MAC_DINH


def _bo_dau(chu: str) -> str:
    """Bỏ dấu để tìm kiếm. Người lớn tuổi gõ không dấu là chuyện thường,
    bắt gõ đúng dấu mới ra kết quả thì coi như không có ô tìm."""
    tach = unicodedata.normalize("NFD", (chu or "").lower())
    return "".join(c for c in tach
                   if unicodedata.category(c) != "Mn").replace("đ", "d")


def du_lieu(tudien: dict, tim: str = "") -> dict:
    tu_khoa = _bo_dau((tim or "").strip())

    muc = []
    for tu in sorted(tudien, key=str.lower):
        doc = tudien[tu]
        if tu_khoa and tu_khoa not in _bo_dau(tu) and tu_khoa not in _bo_dau(doc):
            continue
        muc.append({
            "tu": tu,
            "doc": doc,
            "sanCo": _la_mac_dinh(tu),
            # Sửa khác gì so với bản gốc thì nói ra, để người dùng biết mục
            # nào mình đã đụng vào.
            "daSua": _la_mac_dinh(tu) and engine.TUDIEN_MAC_DINH[tu] != doc,
        })

    rieng = sum(1 for t in tudien if not _la_mac_dinh(t))
    da_xoa = sum(1 for t in engine.TUDIEN_MAC_DINH if t not in tudien)

    return {
        "muc": muc,
        "tim": tim or "",
        "tong": len(tudien),
        "rieng": rieng,
        "daXoa": da_xoa,
        "hienThi": len(muc),
    }
