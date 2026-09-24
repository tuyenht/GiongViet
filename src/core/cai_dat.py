# -*- coding: utf-8 -*-
"""Dữ liệu cho màn hình Cài đặt.

Chỉ bày ra những thiết lập engine LÀM ĐƯỢC THẬT. Bản thiết kế gốc vẽ 36 mục
(ngôn ngữ giao diện, tăng tốc GPU, giới hạn RAM, kênh cập nhật, mã giấy
phép...) nhưng chương trình này chạy ONNX trên CPU, chỉ có tiếng Việt và
không có hệ thống bản quyền nào - dựng đủ 36 mục là bày ra hơn hai chục cái
công tắc bấm vào không xảy ra gì.

Hai thiết lập đáng giá nhất ở đây là doc_so_bang_chu và bo_ky_hieu_markdown:
engine vẫn dùng chúng, nhưng trước giờ muốn đổi thì phải mở cauhinh.ini bằng
Notepad.
"""

from pathlib import Path

import DocCongDuc as engine

# Phím tắt chỉ để XEM. Đổi được phím tắt là một tính năng khác hẳn, chưa có -
# bày ô cho bấm vào rồi không đổi được thì thà in ra cho đọc.
PHIM_TAT = [
    ("Phát / tạm dừng", "Space"),
    ("Câu trước / câu sau", "Ctrl + ← / →"),
    ("Dừng hẳn", "Ctrl + ."),
    ("Phóng to / thu nhỏ chữ", "Ctrl + + / −"),
    ("Cỡ chữ gốc", "Ctrl + 0"),
    ("Nạp lại tệp", "F5"),
    ("Hướng dẫn", "F1"),
]

CO_CHU = [(70, "Nhỏ"), (85, "Hơi nhỏ"), (100, "Vừa"),
          (120, "Hơi lớn"), (150, "Lớn"), (200, "Rất lớn")]


def _co_chu_byte(so_byte: int) -> str:
    if so_byte >= 1024 ** 3:
        return f"{so_byte / 1024 ** 3:.1f} GB".replace(".", ",")
    if so_byte >= 1024 ** 2:
        return f"{so_byte / 1024 ** 2:.0f} MB"
    if so_byte > 0:
        return f"{so_byte / 1024:.0f} KB"
    return "chưa có"


def _dung_luong(duong_dan) -> int:
    p = Path(duong_dan)
    try:
        if p.is_dir():
            return sum(f.stat().st_size for f in p.rglob("*") if f.is_file())
    except OSError:
        pass
    return 0


def _cong_tac(khoa, nhan, goi_y, bat) -> dict:
    return {"kieu": "congtac", "khoa": khoa, "nhan": nhan,
            "goiY": goi_y, "bat": bool(bat)}


def _chu(nhan, goi_y, gia_tri) -> dict:
    return {"kieu": "chu", "nhan": nhan, "goiY": goi_y, "giaTri": gia_tri}


def _duong_dan(khoa, nhan, goi_y, gia_tri) -> dict:
    return {"kieu": "duongdan", "khoa": khoa, "nhan": nhan,
            "goiY": goi_y, "giaTri": gia_tri}


def du_lieu(cfg: dict, tuy_chon: dict, loai_ho_so: str = "",
            ten_ho_so: str = "") -> dict:
    # engine đã dò sẵn (models/vieneu, lùi về vieneu_models nếu là bố cục cũ).
    # Gõ cứng một đường là màn Cài đặt báo "Chiếm chưa có" kèm lời cảnh báo
    # "xoá là phải tải lại vài trăm MB" trỏ vào một thư mục rỗng.
    thu_muc_mo_hinh = engine.MODELS_DIR
    co_chu = int(tuy_chon.get("zoom", 100))

    nhom = [
        {
            "ma": "chung",
            "nhan": "Chung",
            "moTa": "Màu nền và cỡ chữ",
            "muc": [
                {"kieu": "chon", "khoa": "theme", "nhan": "Màu nền",
                 "goiY": "Nền sáng dễ đọc ban ngày, nền tối đỡ chói buổi tối.",
                 "giaTri": tuy_chon.get("theme", "light"),
                 "chon": [{"ma": "light", "nhan": "Sáng"},
                          {"ma": "dark", "nhan": "Tối"}]},
                {"kieu": "chon", "khoa": "zoom", "nhan": "Cỡ chữ vùng văn bản",
                 "goiY": "Chỉ đổi cỡ chữ của danh sách và văn bản đang đọc.",
                 "giaTri": str(co_chu),
                 "chon": [{"ma": str(v), "nhan": f"{n} · {v}%"}
                          for v, n in CO_CHU]},
            ],
        },
        {
            "ma": "doc",
            "nhan": "Cách đọc",
            "moTa": (f"Áp riêng cho hồ sơ “{ten_ho_so}”" if ten_ho_so
                     else "Những thứ ảnh hưởng đến lời đọc"),
            "muc": [
                _cong_tac("doc_so_bang_chu", "Đọc số thành chữ",
                          "1.600.000 đọc là “một triệu sáu trăm nghìn” thay vì "
                          "đọc từng chữ số.",
                          cfg.get("doc_so_bang_chu")),
                _cong_tac("bo_markdown", "Bỏ ký hiệu lạ khi đọc",
                          "Văn bản chép từ web hay lẫn dấu #, *, gạch đầu dòng "
                          "— bật lên thì không đọc chúng.",
                          cfg.get("bo_markdown")),
                _cong_tac("nhan_manh_tien", "Nhấn mạnh dòng có số lớn",
                          "Nhóm có số lớn nhất trong danh sách được đọc to hơn "
                          "một chút và nghỉ lâu hơn sau đó.",
                          cfg.get("nhan_manh_tien")),
            ],
        },
        {
            "ma": "tep",
            "nhan": "Tệp",
            "moTa": "Nơi lấy danh sách và nơi lưu tệp xuất ra",
            "muc": [
                _duong_dan("data_file", "Tệp danh sách",
                           "Tệp mở sẵn mỗi lần khởi động chương trình.",
                           str(cfg.get("data_file", ""))),
                _duong_dan("thu_muc_xuat", "Thư mục xuất mặc định",
                           "Chỗ gợi ý sẵn khi bấm Xuất file âm thanh; mỗi lần "
                           "xuất vẫn đổi được.",
                           tuy_chon.get("thu_muc_xuat", "")
                           or "Chưa chọn — sẽ hỏi khi xuất"),
            ],
        },
        {
            "ma": "may",
            "nhan": "Máy và phiên bản",
            "moTa": "Thông tin để xem, không đổi được",
            "muc": [
                _chu("Bộ giọng đọc lưu tại",
                     f"Chiếm {_co_chu_byte(_dung_luong(thu_muc_mo_hinh))}. "
                     "Xoá thư mục này là lần sau phải tải lại vài trăm MB.",
                     str(thu_muc_mo_hinh)),
                _chu("Chạy trên", "Bộ giọng đọc AI chạy trực tiếp tại máy, "
                     "không gửi nội dung của bạn đi đâu.",
                     "CPU · không cần Internet"),
                _chu("Phiên bản", "", f"Giọng Việt {engine.APP_VERSION}"),
            ],
        },
    ]

    # Mỗi thiết lập ở nhóm "Cách đọc" thuộc về MỘT loại hồ sơ. Bày mục của
    # loại khác ra là bẫy: người dùng tắt nó khi đang ở hồ sơ công đức, thay
    # đổi không có chỗ cất, chuyển sang hồ sơ văn bản thì nó bật lại - tưởng
    # chương trình không nghe lời. Đo được thật, nên chỉ hiện đúng mục hợp
    # với hồ sơ đang mở.
    if loai_ho_so:
        from . import ho_so
        cho_phep = set(ho_so.khoa_cua(loai_ho_so))
        for n in nhom:
            if n["ma"] == "doc":
                n["muc"] = [m for m in n["muc"] if m.get("khoa") in cho_phep]

    import json as py_json
    from pathlib import Path
    cau_hinh_dict = dict(cfg or {})
    for k, v in cau_hinh_dict.items():
        if isinstance(v, Path):
            cau_hinh_dict[k] = str(v)
            
    noi_dung = engine.doc_tep_cau_hinh(engine.CONFIG_FILE)
    if noi_dung:
        try:
            import configparser
            c = configparser.ConfigParser(interpolation=None)
            c.read_string(noi_dung)
            for sec in c.sections():
                for k, v in c.items(sec):
                    cau_hinh_dict[k] = v
        except Exception:
            pass

    return {
        "nhom": [n for n in nhom if n["muc"]],
        "phimTat": [{"nhan": n, "phim": p} for n, p in PHIM_TAT],
        "cauHinh": cau_hinh_dict,
    }
