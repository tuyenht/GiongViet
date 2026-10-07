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


def _muc_truot(khoa, nhan, nho, lon, don_vi, goi_y, gia_tri) -> dict:
    """Một mục chỉnh số, dựng từ MỘT dòng của du_lieu.THANH_TRUOT.

    Nhãn, phạm vi và đơn vị đều lấy từ bảng đó chứ không gõ lại ở đây: hai
    nơi cùng nhỉ một thứ thì có ngày màn Cài đặt cho kéo tới 50 trong khi
    engine chặn ở 30 mà không ai hay.

    CẬN LÀ SỐ NGUYÊN hay SỐ THỰC quyết định kiểu mục. so_nguoi_nhom và
    so_ky_tu đếm đơn vị rời nên đi từng 1; các khoảng nghỉ là giây nên đi
    từng 0,25 hay 0,5 — bước nhỏ hơn thì người dùng phải bấm hàng chục lần
    mới đi hết phạm vi, mà phần lớn họ lớn tuổi.
    """
    from . import du_lieu
    nguyen = isinstance(nho, int) and isinstance(lon, int)
    mac_dinh = nho if nguyen else float(nho)
    try:
        v = (int(float(gia_tri)) if nguyen else float(gia_tri))
    except (TypeError, ValueError):
        # Nhánh này KHÔNG xảy ra trong bản chạy: cfg luôn đến từ
        # engine.load_config(), mà hàm ấy ép từng khóa bằng get_float/get_int kèm
        # mặc định (DocCongDuc.py:657-663). Giữ để không vỡ nếu ai gọi trực
        # tiếp với dict tự dựng — và CỐ Ý không chép lại bảng mặc định của
        # engine sang đây: hai nơi cùng nhỉ một thứ là có ngày chúng lệch nhau.
        v = mac_dinh
    if v is None:
        v = mac_dinh
    v = max(nho, min(lon, v))
    if nguyen:
        # Buoc 1 la dung voi pham vi hep. Nhung so_ky_tu la 120..600: buoc 1 thi
        # 480 lan bam moi di het pham vi - o chinh do khong dung duoc. Da do khi
        # in dong goi y ra doc.
        #
        # KHONG chia pham vi cho mot so de "ra chung 24 lan bam": lam vay thi
        # so_nguoi_nhom (1..50) ra buoc 2, tuc chi dat duoc so CHAN, khong dat
        # noi 5 hay 15 nguoi moi nhom.
        buoc = 1 if (lon - nho) <= 60 else 20
    else:
        # Phạm vi hẹp thì bước nhỏ cho đủ tinh; phạm vi rộng thì bước lớn cho
        # đỡ phải bấm nhiều. 0..2 giây → 8 lần bấm; 0..8 giây → 16 lần.
        buoc = 0.25 if (lon - nho) <= 3 else 0.5
        # KHÔNG bắt v về lưới bước ở đây. Đã đo: cfg có nghi_nguoi = 1,3 giây
        # thì ô chỉnh hiện "1,5 giây" — nói sai con số người dùng đang có, và chỉ
        # mở màn Cài đặt ra xem cũng làm lệch thiết lập của họ. Hiển thị phải
        # là giá trị THẬT; việc bám lưới để nhúc − / + lo khi tính giá trị mới.
        v = round(v, 3)
    # BUOC NHAY phai hien ra MAT THUONG. Ban truoc chi dat no trong
    # aria-label, tuc chi bo doc man hinh thay - nguoi dung chinh cua chuong
    # trinh nay la nguoi lon tuoi mat thuong, ho khong biet mot lan bam doi bao
    # nhieu cho toi khi bam thu. KHONG nhoi len nut: "- Bot 0,5 giay" lam bon
    # nut dai, de xuong dong o man hep. Dong goi y da hien san, chi them mot cau.
    goi_y_du = goi_y
    if goi_y:
        buoc_chu = du_lieu._hien_thi_gia_tri(don_vi, buoc)
        goi_y_du = f"{goi_y}. M\u1ed7i l\u1ea7n b\u1ea5m \u0111\u1ed5i {buoc_chu}."
    return {"kieu": "songuyen" if nguyen else "sothuc",
            "khoa": khoa, "nhan": nhan, "goiY": goi_y_du,
            "giaTri": v, "nhoNhat": nho, "lonNhat": lon, "buoc": buoc,
            "donVi": don_vi,
            "hienThi": du_lieu._hien_thi_gia_tri(don_vi, v)}


def _muc_nhip_doc(cfg, loai_ho_so) -> list:
    """Mọi mục chỉnh nhịp đọc của loại hồ sơ đang mở.

    Duyệt THẮNG bảng THANH_TRUOT chứ không bày từng mục bằng tay. Bản trước
    bày tay đúng một mục (so_nguoi_nhom) và để sót năm mục còn lại — đo 6/10:
    engine dùng chúng thật mà người dùng không có đường nào đổi. Duyệt bảng
    thì thêm một dòng vào bảng là nó tự hiện ra, không còn chỗ để bỏ sót.
    """
    from . import du_lieu
    return [_muc_truot(k, nhan, nho, lon, don_vi, goi_y, cfg.get(k))
            for k, nhan, nho, lon, don_vi, goi_y
            in du_lieu.THANH_TRUOT.get(loai_ho_so or "vanban", [])]


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
                # Mọi mục nhịp đọc của loại hồ sơ này. Chúng chi phối nhịp đọc
                # THẬT (engine đọc chúng khi dựng playlist) nhưng trước giờ
                # không màn nào đặt được — hồ sơ vẫn cất, người dùng vẫn chịu.
                # Bài đo: tests/kiem_so_nguoi_nhom.py
                *_muc_nhip_doc(cfg, loai_ho_so),
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
    # Bỏ mục rỗng trước khi lọc theo loại hồ sơ,
    # không thì khi loai_ho_so rỗng nó lọt ra giao diện thành một dòng trống.
    for n in nhom:
        n["muc"] = [m for m in n["muc"] if m]

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
