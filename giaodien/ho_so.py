# -*- coding: utf-8 -*-
"""Hồ sơ đọc — mỗi hồ sơ nhớ riêng giọng, phong cách và nhịp đọc.

Trước đây chương trình có đúng hai chế độ cố định dùng chung một giọng. Nay
người dùng tạo được nhiều hồ sơ: "Đọc sớ" giọng trầm nghỉ dài, "Thông báo
loa" giọng tin tức nghỉ ngắn, mỗi cái một bộ thiết lập.

CÁCH LƯU — cố tình chạm ít nhất có thể:
  cauhinh.ini  vẫn là thiết lập ĐANG DÙNG, y như cũ. Toàn bộ engine, bộ đọc,
               bộ xuất file không phải biết gì về hồ sơ.
  hoso.json    chỉ là thư viện các bộ thiết lập đã đặt tên.

Đổi hồ sơ = cất thiết lập hiện tại vào hồ sơ cũ, lấy thiết lập hồ sơ mới đổ
vào cauhinh.ini. Nhờ vậy nếu hoso.json có hỏng hay bị xoá thì chương trình
vẫn chạy đúng như trước khi có tính năng này.
"""

import json
import re
import unicodedata
import uuid

import DocCongDuc as engine

TEP = engine.BASE_DIR / "hoso.json"

# Khoá dùng chung cho mọi hồ sơ, và khoá riêng theo loại nội dung.
KHOA_CHUNG = ("vieneu_voice_id", "phong_cach")
KHOA_THEO_LOAI = {
    "congduc": ("nghi_nguoi", "nghi_nhom", "so_nguoi_nhom", "nghi_doan",
                "nhan_manh_tien"),
    "vanban": ("nghi_cau", "nghi_doan_vb", "so_ky_tu", "doc_so_bang_chu",
               "bo_markdown"),
}

# Lời dẫn đầu / giữa / cuối và mẫu câu nằm ở tệp riêng cho TỪNG hồ sơ danh
# sách. Trước đây chỉ có một tệp noidung.ini dùng chung, nên tạo hồ sơ "Danh
# sách khen thưởng" xong nó vẫn đọc "Nam mô A Di Đà Phật" ở đầu và "phát tâm
# công đức" ở mỗi dòng.
#
# Lưu TÊN TỆP chứ không lưu đường dẫn đầy đủ: chép cả thư mục chương trình
# sang máy khác thì vẫn tìm thấy.
TEP_NOI_DUNG_GOC = "noidung.ini"

# Hồ sơ mới bắt đầu bằng lời dẫn TRỐNG và mẫu câu trung tính. Cố tình không
# chép lời nhà chùa sang việc khác - danh sách khen thưởng mà đọc lời hồi
# hướng công đức thì còn tệ hơn là không có lời dẫn nào.
NOI_DUNG_TRUNG_TINH = """; ==========================================================
;  LOI DAN CHO HO SO: {ten}
;  Sua truc tiep file nay bang Notepad roi luu lai (UTF-8).
;  bat_dau=1 la BAT, bat_dau=0 la TAT (khong doc phan do).
; ==========================================================

[DauDanhSach]
bat_dau=0
noi_dung=

[GiuaDanhSach]
bat_dau=0
sau_moi=30
noi_dung=

[CuoiDanhSach]
bat_dau=0
noi_dung=

[MauCau]
; Bat buoc co {{ten}} va {{tien}}
noi_dung={{ten}}, {{tien}}.
"""


def _slug(ten: str) -> str:
    """Tên hồ sơ -> phần tên tệp: bỏ dấu, chỉ giữ chữ và số."""
    tach = unicodedata.normalize("NFD", (ten or "").lower())
    sach = "".join(c for c in tach if unicodedata.category(c) != "Mn")
    sach = sach.replace("đ", "d")
    sach = re.sub(r"[^a-z0-9]+", "-", sach).strip("-")
    return sach or "moi"


def tao_tep_noi_dung(ten_ho_so: str) -> str:
    """Tạo tệp lời dẫn cho một hồ sơ mới, trả về TÊN TỆP.

    Không ghi đè tệp đã có: người dùng đặt trùng tên hồ sơ thì thêm số vào
    đuôi chứ không xoá mất lời dẫn họ đã soạn ở hồ sơ cũ.
    """
    goc = f"noidung-{_slug(ten_ho_so)}"
    ten_tep = f"{goc}.ini"
    lan = 2
    while (engine.BASE_DIR / ten_tep).exists():
        ten_tep = f"{goc}-{lan}.ini"
        lan += 1
    (engine.BASE_DIR / ten_tep).write_text(
        NOI_DUNG_TRUNG_TINH.format(ten=ten_ho_so), encoding="utf-8-sig")
    return ten_tep


def khoa_cua(loai: str) -> tuple:
    return KHOA_CHUNG + KHOA_THEO_LOAI.get(loai, ())


def ma_moi() -> str:
    return uuid.uuid4().hex[:12]


def _trich(cfg: dict, loai: str) -> dict:
    """Rút các thiết lập thuộc về một hồ sơ ra khỏi cấu hình đang chạy."""
    return {k: cfg[k] for k in khoa_cua(loai) if k in cfg}


def mac_dinh_tu_cau_hinh(cfg: dict) -> list:
    """Lần đầu chạy: dựng hai hồ sơ từ đúng thiết lập người dùng đang có.

    Không đặt bừa giá trị mẫu - người dùng đã chỉnh nhịp đọc quen tay rồi,
    mở lên thấy khác đi là hoang mang.
    """
    return [
        # Hồ sơ danh sách đầu tiên trỏ thẳng vào noidung.ini đang có, để lời
        # dẫn người dùng đã soạn từ trước dùng tiếp được ngay.
        dict(ma=ma_moi(), ten="Danh sách tên và số", loai="congduc",
             noidung_file=TEP_NOI_DUNG_GOC, **_trich(cfg, "congduc")),
        dict(ma=ma_moi(), ten="Đọc văn bản", loai="vanban",
             **_trich(cfg, "vanban")),
    ]


def tep_noi_dung_cua(h: dict) -> str:
    """Tên tệp lời dẫn của một hồ sơ. Hồ sơ cũ chưa có khoá này thì dùng
    noidung.ini như trước."""
    return (h or {}).get("noidung_file") or TEP_NOI_DUNG_GOC


def doc(cfg: dict) -> dict:
    """Trả {"dangDung": ma, "dsHoSo": [...]}. Tệp hỏng thì dựng lại từ đầu
    chứ không để chương trình chết vì một tệp phụ."""
    # Hồ sơ nay nằm trong giongviet.db; doc_tep_cau_hinh tự lùi về tệp rời khi
    # kho chưa có mục ấy, nên bản đang chạy của người dùng không hụt gì.
    _noi_dung = engine.doc_tep_cau_hinh(TEP)
    if _noi_dung:
        try:
            data = json.loads(_noi_dung)
            ds = [h for h in data.get("dsHoSo", [])
                  if isinstance(h, dict) and h.get("ma") and h.get("ten")
                  and h.get("loai") in KHOA_THEO_LOAI]
            if ds:
                dang = data.get("dangDung")
                if dang not in {h["ma"] for h in ds}:
                    dang = ds[0]["ma"]
                return {"dangDung": dang, "dsHoSo": ds}
        except (json.JSONDecodeError, OSError, TypeError):
            pass

    ds = mac_dinh_tu_cau_hinh(cfg)
    kho = {"dangDung": ds[0]["ma"], "dsHoSo": ds}
    luu(kho)
    return kho


def luu(kho: dict):
    engine.ghi_tep_cau_hinh(TEP, json.dumps(kho, ensure_ascii=False, indent=1))


def tim(kho: dict, ma: str):
    return next((h for h in kho["dsHoSo"] if h["ma"] == ma), None)


def cat_thiet_lap(kho: dict, cfg: dict):
    """Cất thiết lập đang dùng vào hồ sơ đang mở, trước khi chuyển đi nơi khác."""
    h = tim(kho, kho["dangDung"])
    if h:
        h.update(_trich(cfg, h["loai"]))


def do_vao_cau_hinh(h: dict, cfg: dict):
    """Đổ thiết lập của một hồ sơ vào cấu hình đang chạy."""
    for k in khoa_cua(h["loai"]):
        if k in h:
            cfg[k] = h[k]


def du_lieu(kho: dict) -> list:
    """Danh sách cho giao diện, kèm tên giọng đọc để nhìn là biết ngay."""
    return [{"ma": h["ma"], "ten": h["ten"], "loai": h["loai"],
             "giong": h.get("vieneu_voice_id", "") or "Giọng mặc định",
             "dangDung": h["ma"] == kho["dangDung"]}
            for h in kho["dsHoSo"]]
