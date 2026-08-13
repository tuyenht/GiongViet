# -*- coding: utf-8 -*-
"""GiongViet — chạy giao diện mới (ui-moi) với engine thật.

Bản song song, cố ý KHÔNG đụng GiongDoc.py: chương trình anh đang dùng hằng
ngày phải chạy y nguyên trong lúc bản mới còn dở. Khi nào bản mới qua đủ
nghiệm thu thì mới đổi tên thư mục và gộp lại làm một.

Chạy:  py GiongViet.py
"""

import ctypes
import os
import sys
from ctypes import wintypes
from pathlib import Path

SPI_GETWORKAREA = 0x0030


def vung_lam_viec():
    """Lấy vùng màn hình dùng được TRƯỚC khi import webview.

    Lý do y hệt GiongDoc.py: pywebview bật DPI awareness cho tiến trình, sau đó
    Windows trả pixel vật lý còn cỡ cửa sổ lại tính bằng pixel logic. Lấy sai
    một nhịp là cửa sổ tràn ra ngoài màn hình, mất luôn thanh phát ở dưới cùng.
    """
    mac_dinh = (0, 0, 1280, 800)
    if os.name != "nt":
        return mac_dinh
    r = wintypes.RECT()
    try:
        if not ctypes.windll.user32.SystemParametersInfoW(
                SPI_GETWORKAREA, 0, ctypes.byref(r), 0):
            return mac_dinh
    except (AttributeError, OSError):
        return mac_dinh
    rong, cao = r.right - r.left, r.bottom - r.top
    if rong < 640 or cao < 480:
        return mac_dinh
    return r.left, r.top, rong, cao


VUNG_LAM_VIEC = vung_lam_viec()

import webview  # noqa: E402 — phải nằm sau vung_lam_viec()


def thu_muc_goc() -> Path:
    if getattr(sys, "frozen", False):
        return Path(sys.executable).resolve().parent
    return Path(__file__).resolve().parent


BASE_DIR = thu_muc_goc()
if str(BASE_DIR) not in sys.path:
    sys.path.insert(0, str(BASE_DIR))


def thu_muc_giao_dien() -> Path:
    ung_vien = [BASE_DIR / "ui-moi"]
    meipass = getattr(sys, "_MEIPASS", "")
    if meipass:
        ung_vien.insert(0, Path(meipass) / "ui-moi")
    for d in ung_vien:
        if (d / "index.html").exists():
            return d
    return ung_vien[-1]


def main():
    from giaodien_moi.cau_noi_moi import ApiMoi

    api = ApiMoi(VUNG_LAM_VIEC)
    nen = "#202020" if api._tuy_chon.get("theme") == "dark" else "#F3F3F3"
    x, y, rong, cao = VUNG_LAM_VIEC

    api._window = webview.create_window(
        "Giọng Việt",
        str(thu_muc_giao_dien() / "index.html"),
        js_api=api,
        x=x, y=y, width=rong, height=cao,
        # Cỡ nhỏ nhất, tính từ chính bố cục chứ không đoán: cột trái 240 + cột
        # phải 300 là cố định, vùng đọc cần chừng 480 nữa mới đọc thoải mái.
        # Chiều cao: thanh tiêu đề, menu, công cụ, dải tab, thanh phát và dòng
        # trạng thái ăn khoảng 240 px, chừa 440 cho vùng đọc là vừa mắt.
        min_size=(1024, 680),
        frameless=True,
        easy_drag=False,          # chỉ kéo được ở thanh tiêu đề
        # Bật chọn chữ: phép thử mốc 0 đã chứng minh gõ tiếng Việt chạy đúng và
        # kéo cửa sổ vẫn được (cửa sổ dịch 84px, không bôi đen chữ).
        text_select=True,
        background_color=nen,
    )

    webview.start(debug=os.environ.get("GIONGDOC_DEBUG") == "1")

    # --- Cửa sổ đã đóng. Hai việc bắt buộc làm bằng tay, y như GiongDoc.py ---
    # 1) Dừng ffplay: đóng bằng Alt+F4 thì thoat() không chạy, tiếng vẫn phát nốt.
    # 2) os._exit: PyTorch và huggingface để lại luồng nền không phải daemon,
    #    không có dòng này thì cửa sổ đóng rồi mà tiến trình vẫn sống, ôm vài GB.
    api._don_dep()
    sys.stdout.flush()
    sys.stderr.flush()
    os._exit(0)


if __name__ == "__main__":
    main()
