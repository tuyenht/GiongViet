# -*- coding: utf-8 -*-
"""Hồ sơ của giao diện mới — lưu ở hoso-v2.json, KHÔNG đụng hoso.json.

Quyết định của chủ dự án (2026-08-12): bản mới có tệp hồ sơ riêng. Bản cũ vẫn
đọc ghi hoso.json của nó như chưa có gì xảy ra, nên hai bản chạy song song mà
không giẫm lên nhau. Xem thêm giaodien_moi/khoa_du_lieu.py.

Hình dạng khác hoso.json vì mô hình dữ liệu khác hẳn: bản mới mỗi hồ sơ mang
theo DANH SÁCH TỆP ĐANG MỞ (tab) và ba thanh điều chỉnh, thứ bản cũ không có.

Không tin dữ liệu từ giao diện: mọi giá trị đều bị ép kiểu và cắt về khoảng
cho phép trước khi ghi. Tệp này người dùng không bao giờ mở tay, nhưng một
JSON hỏng làm chương trình mở lên trắng trơn thì họ không tự chữa được.
"""

import json

import DocCongDuc as engine

from giaodien_moi import luu_tep

TEP = engine.BASE_DIR / "hoso-v2.json"

PHIEN_BAN = 1

# Chặn tệp phình vô hạn nếu giao diện có lỗi vòng lặp. Con số rộng gấp nhiều
# lần nhu cầu thật (4 hồ sơ, mỗi hồ sơ vài tệp) nên người dùng không bao giờ
# chạm tới.
TOI_DA_HO_SO = 50
TOI_DA_TAB = 50
TOI_DA_THE = 2000

# PHẢI khớp ba nơi: thanh trượt trong ui-moi/giao-dien.js (TRUOT), bộ lọc
# giaodien_moi/am_thanh_loc.py, và bảng này. Trước đây lệch nhau và không ai
# thấy: giao diện cho kéo Tốc độ tới +100 mà bảng này cắt về +50, nên nửa
# thanh bên phải kéo xong không đổi gì. Âm lượng thì ngược lại - bảng cho tới
# 200 trong khi bộ lọc chỉ giảm chứ không khuếch đại (đẩy quá đỉnh là rè).
GIOI_HAN_CHINH = {"tocDo": (-50, 100), "caoDo": (-12, 12), "amLuong": (0, 100)}
MAC_DINH_CHINH = {"tocDo": 0, "caoDo": 0, "amLuong": 100}


def _so_nguyen(gt, thap, cao, mac_dinh):
    try:
        return max(thap, min(cao, int(gt)))
    except (TypeError, ValueError):
        return mac_dinh


def _chu(gt, dai_toi_da=200) -> str:
    return str(gt or "")[:dai_toi_da]


def _lam_sach_chinh(chinh) -> dict:
    chinh = chinh if isinstance(chinh, dict) else {}
    res = {k: _so_nguyen(chinh.get(k), t, c, MAC_DINH_CHINH[k])
           for k, (t, c) in GIOI_HAN_CHINH.items()}
    kg = str(chinh.get("khongGian") or "").strip().lower()
    if kg in ("podcast", "hoitruong", "loaphuong", "radio"):
        res["khongGian"] = kg
    return res


def _lam_sach_ho_so(h) -> dict:
    h = h if isinstance(h, dict) else {}
    tep = [_chu(t, 400) for t in (h.get("tep") or [])[:TOI_DA_TAB]
           if isinstance(t, str)]
    if not tep:
        # Hồ sơ luôn có ít nhất một tab; rỗng nghĩa là tab "Chưa đặt tên".
        tep = [""]

    g_theo_nn = {}
    if isinstance(h.get("giongTheoNgonNgu"), dict):
        for k_nn, v_g in h["giongTheoNgonNgu"].items():
            if isinstance(k_nn, str) and isinstance(v_g, str):
                g_theo_nn[_chu(k_nn, 30)] = _chu(v_g, 120)

    return {
        "ma": _chu(h.get("ma"), 64) or "hs",
        "ten": _chu(h.get("ten"), 120) or "Hồ sơ",
        "giong": _chu(h.get("giong"), 120),
        "ngonNgu": _chu(h.get("ngonNgu"), 30) or "vi",
        "ngonNguNguon": _chu(h.get("ngonNguNguon"), 30) or "auto",
        "phongCach": _chu(h.get("phongCach"), 60) or "Tự nhiên",
        "giongTheoNgonNgu": g_theo_nn,
        "chinh": _lam_sach_chinh(h.get("chinh")),
        "tep": tep,
        "dangXem": _so_nguyen(h.get("dangXem"), 0, len(tep) - 1, 0),
    }


def _lam_sach_the(the) -> dict:
    """Thẻ cảm xúc: { 'ten-tep.txt': { '11': '[hắng giọng]' } }.

    Khoá số đoạn đi qua JSON thành chuỗi. Giữ nguyên chuỗi ở đây, phía giao
    diện tra bằng số nên JavaScript tự ép về chuỗi khi tra khoá đối tượng.
    """
    if not isinstance(the, dict):
        return {}
    ra, dem = {}, 0
    for tep, cua_tep in the.items():
        if not isinstance(cua_tep, dict) or dem >= TOI_DA_THE:
            continue
        muc = {}
        for so, nhan in cua_tep.items():
            if dem >= TOI_DA_THE:
                break
            if str(so).lstrip("-").isdigit() and nhan:
                muc[str(so)] = _chu(nhan, 60)
                dem += 1
        if muc:
            ra[_chu(tep, 400)] = muc
    return ra


def _lam_sach_duong_dan(duong_dan) -> dict:
    """{ 'ten-tep.txt': 'C:\\...\\ten-tep.txt' } — để mở lại tệp ở lần chạy sau.

    Tab chỉ nhớ TÊN tệp, mà tên thì không mở lại được. Văn bản dán từ clipboard
    không có đường dẫn nên không có mặt ở đây; lần sau mở lên tab đó thành
    trống, đúng như bản chất của nó.
    """
    if not isinstance(duong_dan, dict):
        return {}
    return {_chu(t, 400): _chu(p, 400)
            for t, p in list(duong_dan.items())[:TOI_DA_HO_SO * TOI_DA_TAB]
            if isinstance(p, str) and p.strip()}


def lam_sach(du_lieu) -> dict:
    """Dữ liệu từ giao diện -> hình dạng chuẩn để ghi. Luôn trả về dict hợp lệ."""
    d = du_lieu if isinstance(du_lieu, dict) else {}
    ds = [_lam_sach_ho_so(h) for h in (d.get("hoSo") or [])[:TOI_DA_HO_SO]]
    return {
        "phienBan": PHIEN_BAN,
        "dangDung": _so_nguyen(d.get("dangDung"), 0, max(0, len(ds) - 1), 0),
        "hoSo": ds,
        "theme": "toi" if d.get("theme") == "toi" else "sang",
        # Cỡ chữ vùng đọc. Cắt về khoảng màn Cài đặt cho chọn, không thì một
        # giá trị lạ trong tệp làm chữ nhỏ tí hoặc to tràn màn hình.
        "zoom": _so_nguyen(d.get("zoom"), 70, 200, 100),
        "the": _lam_sach_the(d.get("the")),
        "duongDan": _lam_sach_duong_dan(d.get("duongDan")),
        "loaiTep": _lam_sach_loai_tep(d.get("loaiTep")),
    }


def _lam_sach_loai_tep(loai) -> dict:
    """{ 'danhsach.txt': 'congduc' } — tab nào là danh sách tên và số.

    Không nhớ thì lần mở sau nó đọc danh sách theo kiểu văn bản thường: đọc
    nguyên cả dòng "Nguyễn Văn A — 500.000" thay vì dựng câu theo mẫu.
    """
    if not isinstance(loai, dict):
        return {}
    return {_chu(t, 400): ("congduc" if v == "congduc" else "vanban")
            for t, v in list(loai.items())[:TOI_DA_HO_SO * TOI_DA_TAB]
            if isinstance(v, str)}


def doc():
    """Trả về dict đã làm sạch, hoặc None nếu chưa có tệp / tệp hỏng.

    None nghĩa là "dùng hồ sơ mặc định", không phải lỗi: lần chạy đầu tiên
    trên máy nào cũng rơi vào nhánh này.
    """
    noi_dung = engine.doc_tep_cau_hinh(TEP)
    if not noi_dung:
        return None
    try:
        d = json.loads(noi_dung)
    except (json.JSONDecodeError, OSError, UnicodeDecodeError):
        return None
    if not isinstance(d, dict) or not d.get("hoSo"):
        return None
    return lam_sach(d)


def luu(du_lieu) -> bool:
    """Ghi qua tệp tạm rồi đổi tên đè lên, y như giaodien_moi/luu_tep.py.

    Trả False thay vì ném lỗi: mất một lần lưu thiết lập không đáng để chương
    trình hiện hộp thoại đỏ giữa lúc người ta đang đọc.
    """
    sach = lam_sach(du_lieu)
    if not sach["hoSo"]:
        return False
    try:
        # Kho SQLite ghi trong một giao dịch nên đã an toàn sẵn; ghi_tep_cau_hinh
        # chỉ lùi về luu_tep.ghi_an_toan khi kho hỏng.
        engine.ghi_tep_cau_hinh(TEP, json.dumps(sach, ensure_ascii=False, indent=1))
    except OSError:
        return False
    return True
