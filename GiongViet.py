# -*- coding: utf-8 -*-
"""GiongViet — chạy giao diện mới (ui-moi) với engine thật.

Điểm vào của Giọng Việt. Bản cũ đã ngừng dùng, nằm trong _luutru/ - phần
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

    pywebview bật DPI awareness cho tiến trình, sau đó
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

# Tối ưu hoá bộ nhớ Chromium WebView2: Giới hạn V8 JS heap 128MB, tắt cache shader đĩa dư thừa
if "WEBVIEW2_ADDITIONAL_BROWSER_ARGUMENTS" not in os.environ:
    os.environ["WEBVIEW2_ADDITIONAL_BROWSER_ARGUMENTS"] = (
        "--disable-gpu-shader-disk-cache --disable-component-update "
        "--js-flags=--max-old-space-size=128 --renderer-process-limit=1"
    )

import webview  # noqa: E402 — phải nằm sau vung_lam_viec()


def thu_muc_goc() -> Path:
    if getattr(sys, "frozen", False):
        return Path(sys.executable).resolve().parent
    return Path(__file__).resolve().parent


BASE_DIR = thu_muc_goc()
if str(BASE_DIR) not in sys.path:
    sys.path.insert(0, str(BASE_DIR))

import src  # noqa: F401 — Kích hoạt hệ sinh thái src và module mapping


def thu_muc_giao_dien() -> Path:
    ung_vien = [
        BASE_DIR / "src" / "web",
        BASE_DIR / "ui-moi",
    ]
    meipass = getattr(sys, "_MEIPASS", "")
    if meipass:
        ung_vien.insert(0, Path(meipass) / "web")
        ung_vien.insert(0, Path(meipass) / "ui-moi")
    for d in ung_vien:
        if (d / "index.html").exists():
            return d
    return ung_vien[0]


def bao_dam_ffmpeg():
    for ung_vien in [
        BASE_DIR / "bin" / "ffmpeg" / "bin",
        BASE_DIR / "ffmpeg" / "bin",
    ]:
        if (ung_vien / "ffplay.exe").exists() and (ung_vien / "ffmpeg.exe").exists():
            return
    bin_dir = BASE_DIR / "bin" / "ffmpeg" / "bin"

    import DocCongDuc as engine
    from giaodien import nhat_ky

    def bao(chu):
        # Bản --windowed không có stdout; ghi ra đâu cũng phải an toàn.
        try:
            print(chu)
            sys.stdout.flush()
        except (OSError, ValueError, AttributeError):
            pass

    bao("Lần đầu chạy: đang tải ffmpeg về, xin đợi vài phút...")
    try:
        engine.tai_ffmpeg_tu_dong(bin_dir, bao)
        bao("Đã tải xong ffmpeg.")
    except Exception as e:
        # Không chặn đường vào chương trình: người dùng vẫn mở được để soạn và
        # sửa văn bản, chỉ là chưa nghe được. Chặn ở đây thì họ không vào nổi.
        nhat_ky.ghi_loi("tải ffmpeg lần đầu", e)
        bao("Chưa tải được ffmpeg. Hãy chạy CaiDat.bat rồi mở lại.")


def main():
    bao_dam_ffmpeg()

    # Gom các tệp cấu hình rời vào giongviet.db, một lần duy nhất. Chạy TRƯỚC
    # khi dựng ApiMoi vì ApiMoi đọc cấu hình ngay lúc khởi tạo.
    #
    # Tệp cũ không bị xoá, chỉ dời sang sao-luu-cu/. Gom hỏng thì mọi đường đọc
    # tự lùi về tệp rời, chương trình vẫn chạy như chưa có gì.
    try:
        import kho_cau_hinh
        ket = kho_cau_hinh.nhap_tu_tep_cu()
        # Ghi lại mục nào gom mà chưa dọn được tệp cũ. Không ghi thì lần sau
        # nhìn thư mục vẫn bừa mà chẳng có manh mối nào.
        vuong = {k: v for k, v in ket.items() if v != "đã gom"}
        if vuong:
            from giaodien import nhat_ky
            nhat_ky.ghi(f"Gom cấu hình: {vuong}")
    except Exception as loi:                             # noqa: BLE001
        from giaodien import nhat_ky
        nhat_ky.ghi_loi("Gom cấu hình vào kho, dùng tệp rời như cũ", loi)

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

    # Ghi kho ra tệp text trong sao-luu-cu/ mỗi lần đóng chương trình.
    #
    # Gom cấu hình vào SQLite lấy mất một thứ đang dùng hằng ngày: mở cấu hình
    # bằng Notepad để dò lỗi. Bản sao lúc gom chỉ là ảnh chụp ngày đầu, không
    # theo kịp thiết lập người dùng đổi về sau. Ghi lại lúc thoát thì luôn có
    # bản đọc được, mà KHÔNG phải bày thêm nút nào cho người lớn tuổi.
    #
    # Sáu tệp cỡ vài KB nên tốn không đáng kể, và đặt sau _don_dep() để có
    # hỏng cũng không cản đường thoát.
    try:
        import kho_cau_hinh
        kho_cau_hinh.xuat_ra_tep(BASE_DIR / kho_cau_hinh.THU_MUC_SAO_LUU)
    except Exception:                                    # noqa: BLE001
        pass

    sys.stdout.flush()
    sys.stderr.flush()
    os._exit(0)


if __name__ == "__main__":
    main()
