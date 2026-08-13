# -*- coding: utf-8 -*-
"""Soát văn bản trước khi đọc.

Chỉ báo những thứ ĐO ĐƯỢC từ chính nội dung, không đoán: số tiền không hiểu
được, chữ viết tắt chưa dạy máy đọc, ký tự máy sẽ đọc trẹo, tên trùng nhau.

Bản thiết kế gốc có nút "Sửa tất cả có thể". Cố tình không làm: hầu hết vấn
đề ở đây cần người quyết (viết tắt phải biết đọc thành gì, tên trùng phải
biết có đúng là hai người khác nhau không). Nút sửa hàng loạt mà chỉ sửa
được vài trường hợp vụn vặt thì hứa nhiều hơn làm.
"""

import re
from collections import Counter

import DocCongDuc as engine

# Chữ in hoa liền từ 2 ký tự trở lên - dấu hiệu của viết tắt. Máy đọc VieNeu
# gặp "UBND" mà không có trong từ điển thì đánh vần từng chữ cái.
#
# Lookahead phải chặn CẢ chữ hoa có dấu, không chỉ chữ thường. Khoảng "à-ỹ"
# (U+00E0..U+1EF9) không chứa À Á Â Ô Ơ Ư hoa (U+00C0..U+00DD), nên bản trước
# cắt "THÔNG" thành "TH" rồi báo là viết tắt chưa dạy. Đo được: một tiêu đề
# thường gặp như "THÔNG BÁO NGHỈ LỄ QUỐC KHÁNH" đẻ ra ba cảnh báo giả
# TH · NG · KH - mà tiêu đề viết hoa thì thông báo nào cũng có.
VIET_TAT = re.compile(r"(?<![0-9A-Za-zÀ-ỹĐđ])([A-ZĐ]{2,})(?![0-9A-Za-zÀ-ỹĐđ])")

# Ký tự chương trình biết đọc: chữ Việt, số, và các dấu câu thông thường.
# Ngoài bảng này (ký hiệu ✓, emoji, chữ Trung, mũi tên...) thì hoặc bị bỏ
# qua hoặc đọc trẹo, đằng nào cũng nên cho người dùng biết.
KY_TU_QUEN = re.compile(
    r"[0-9A-Za-zÀ-ỹĐđ\s.,;:!?\-–—/()\[\]{}'\"“”‘’…%+*&@#°²³]"
)

MUC_NANG = "nang"
MUC_NHE = "nhe"


def _ky_tu_la(chuoi: str) -> list:
    return sorted({c for c in (chuoi or "") if not KY_TU_QUEN.match(c)})


def _viet_tat_thieu(chuoi: str, tudien: dict) -> list:
    return [t for t in set(VIET_TAT.findall(chuoi or "")) if t not in tudien]


def _van_de(muc, loai, dong, tieu_de, chi_tiet, tu="") -> dict:
    return {"muc": muc, "loai": loai, "dong": dong,
            "tieuDe": tieu_de, "chiTiet": chi_tiet, "tu": tu}


def soat_cong_duc(records, canh_bao, tudien) -> list:
    van_de = []

    for c in canh_bao or []:
        # parse_data_file trả cảnh báo dạng câu chữ chứ không kèm số dòng
        # riêng; moi số ra để còn xếp đúng thứ tự và nhảy tới được. Không moi
        # được thì để 0, vẫn hiện bình thường ở đầu danh sách.
        khop = re.match(r"^Dòng\s+(\d+)", str(c))
        van_de.append(_van_de(
            MUC_NANG, "tien", int(khop.group(1)) if khop else 0,
            "Không hiểu số tiền", str(c)))

    dem_ten = Counter(r["name"].strip().lower()
                      for r in records if r.get("kind") == "nguoi")

    da_bao_trung = set()
    for r in records:
        dong = r.get("line_no", 0)
        ten = r.get("name", "")

        if r.get("kind") == "nguoi":
            khoa = ten.strip().lower()
            if dem_ten[khoa] > 1 and khoa not in da_bao_trung:
                da_bao_trung.add(khoa)
                van_de.append(_van_de(
                    MUC_NHE, "trung", dong, "Tên xuất hiện nhiều lần",
                    f"“{ten}” có {dem_ten[khoa]} dòng. Nếu đúng là hai người "
                    "khác nhau thì bỏ qua, còn nếu gõ nhầm thì sửa lại."))

        for t in _viet_tat_thieu(ten, tudien):
            van_de.append(_van_de(
                MUC_NANG, "viettat", dong, f"Chưa dạy máy đọc “{t}”",
                f"Máy sẽ đánh vần từng chữ cái. Thêm “{t}” vào từ điển phát "
                "âm để đọc cho đúng.", t))

        la = _ky_tu_la(ten)
        if la:
            van_de.append(_van_de(
                MUC_NHE, "kytu", dong, "Có ký tự máy không đọc được",
                f"Dòng này chứa {' '.join(la)} — máy sẽ bỏ qua hoặc đọc trẹo."))

    return van_de


def soat_van_ban(van_ban: str, tudien: dict) -> list:
    van_de = []
    for so, dong in enumerate((van_ban or "").splitlines(), 1):
        for t in _viet_tat_thieu(dong, tudien):
            van_de.append(_van_de(
                MUC_NANG, "viettat", so, f"Chưa dạy máy đọc “{t}”",
                f"Máy sẽ đánh vần từng chữ cái. Thêm “{t}” vào từ điển phát "
                "âm để đọc cho đúng.", t))
        la = _ky_tu_la(dong)
        if la:
            van_de.append(_van_de(
                MUC_NHE, "kytu", so, "Có ký tự máy không đọc được",
                f"Dòng này chứa {' '.join(la)} — máy sẽ bỏ qua hoặc đọc trẹo."))
    return van_de


def gop_trung(van_de: list) -> list:
    """Gộp các dòng cùng một chữ viết tắt lại - danh sách nghìn tên mà mỗi
    dòng một mục thì không ai đọc nổi."""
    theo_tu = {}
    ket_qua = []
    for v in van_de:
        if v["loai"] != "viettat":
            ket_qua.append(v)
            continue
        cu = theo_tu.get(v["tu"])
        if cu is None:
            v = dict(v, soDong=1)
            theo_tu[v["tu"]] = v
            ket_qua.append(v)
        else:
            cu["soDong"] += 1
    for v in theo_tu.values():
        if v["soDong"] > 1:
            v["chiTiet"] = (f"Xuất hiện ở {v['soDong']} dòng. " + v["chiTiet"])
    return ket_qua


def du_lieu(che_do, records, canh_bao, van_ban, tudien) -> dict:
    if che_do == "congduc":
        van_de = soat_cong_duc(records or [], canh_bao, tudien or {})
        so_dong = sum(1 for r in (records or []) if r.get("kind") == "nguoi")
        mo_ta = f"{so_dong} người trong danh sách"
        co_noi_dung = bool(records)
    else:
        van_de = soat_van_ban(van_ban or "", tudien or {})
        so_dong = len((van_ban or "").splitlines())
        mo_ta = f"{so_dong} dòng văn bản"
        co_noi_dung = bool((van_ban or "").strip())

    # Chưa mở tệp nào mà báo "không thấy vấn đề gì" thì nghe như đã soát xong
    # và mọi thứ ổn - trong khi thật ra chưa soát cái gì cả.
    if not co_noi_dung:
        return {"vanDe": [], "nang": 0, "nhe": 0, "moTa": "", "trong": True}

    van_de = gop_trung(van_de)
    van_de.sort(key=lambda v: (v["muc"] != MUC_NANG, v["dong"]))

    return {
        "vanDe": van_de,
        "nang": sum(1 for v in van_de if v["muc"] == MUC_NANG),
        "nhe": sum(1 for v in van_de if v["muc"] == MUC_NHE),
        "moTa": mo_ta,
        "trong": False,
    }
