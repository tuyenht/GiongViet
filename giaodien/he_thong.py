# -*- coding: utf-8 -*-
"""Việc lặt vặt phía hệ điều hành: clipboard, mở thư mục, mở tệp bằng
chương trình mặc định, và ghi nhớ lựa chọn giao diện (chủ đề, cỡ chữ)."""

import ctypes
import json
import os
import subprocess
from pathlib import Path

import DocCongDuc as engine

TUY_CHON_FILE = engine.BASE_DIR / "giaodien.json"

MAC_DINH = {"theme": "light", "zoom": 100, "thu_muc_xuat": ""}


def doc_tuy_chon() -> dict:
    tuy_chon = dict(MAC_DINH)
    if TUY_CHON_FILE.exists():
        try:
            data = json.loads(TUY_CHON_FILE.read_text(encoding="utf-8"))
            if isinstance(data, dict):
                tuy_chon.update({k: v for k, v in data.items() if k in MAC_DINH})
        except (json.JSONDecodeError, OSError):
            pass
    return tuy_chon


def luu_tuy_chon(tuy_chon: dict):
    try:
        TUY_CHON_FILE.write_text(
            json.dumps(tuy_chon, ensure_ascii=False, indent=1), encoding="utf-8")
    except OSError:
        pass


def thu_muc_xuat_mac_dinh() -> Path:
    return Path.home() / "Documents" / "GiongViet" / "Xuất"


def doc_clipboard() -> str:
    """Đọc văn bản Unicode trong clipboard Windows. Trả về "" nếu không có."""
    if os.name != "nt":
        return ""
    CF_UNICODETEXT = 13
    u32, k32 = ctypes.windll.user32, ctypes.windll.kernel32
    u32.OpenClipboard.argtypes = [ctypes.c_void_p]
    u32.GetClipboardData.argtypes = [ctypes.c_uint]
    u32.GetClipboardData.restype = ctypes.c_void_p
    k32.GlobalLock.argtypes = [ctypes.c_void_p]
    k32.GlobalLock.restype = ctypes.c_void_p
    k32.GlobalUnlock.argtypes = [ctypes.c_void_p]

    if not u32.OpenClipboard(None):
        return ""
    try:
        handle = u32.GetClipboardData(CF_UNICODETEXT)
        if not handle:
            return ""
        con_tro = k32.GlobalLock(handle)
        if not con_tro:
            return ""
        try:
            return ctypes.c_wchar_p(con_tro).value or ""
        finally:
            k32.GlobalUnlock(handle)
    finally:
        u32.CloseClipboard()


def mo_thu_muc(duong_dan: str):
    """Mở File Explorer và chọn sẵn tệp vừa tạo."""
    p = Path(duong_dan)
    try:
        if p.is_file():
            subprocess.Popen(["explorer", "/select,", str(p)])
        else:
            os.startfile(str(p if p.exists() else p.parent))
    except OSError:
        pass


def mo_bang_chuong_trinh_mac_dinh(duong_dan: Path) -> str:
    """Mở tệp bằng chương trình mặc định (Notepad với .txt/.ini).
    Trả về "" nếu mở được, hoặc mô tả lỗi."""
    try:
        if not duong_dan.exists():
            return f"Không tìm thấy tệp:\n{duong_dan}"
        os.startfile(str(duong_dan))
        return ""
    except OSError as e:
        return str(e)


HUONG_DAN = """Ba bước để nghe:

1. Chọn chế độ đọc ở cột trái
   • Danh sách công đức — đọc tệp congduc.txt, có lời mở đầu và lời kết.
   • Đọc văn bản — đọc mọi văn bản: mở tệp hoặc dán từ clipboard.

2. Chọn giọng và phong cách ở cột phải
   Bấm "Nghe thử" để nghe trước vài giây.

3. Bấm nút tròn màu xanh ở dưới để phát
   Bấm thẳng vào một dòng bất kỳ để đọc từ chỗ đó.
   Muốn có tệp âm thanh, bấm "Xuất file âm thanh".

Phím tắt hay dùng:
   Space           Phát / tạm dừng
   Ctrl + ← / →    Câu trước / câu sau
   Ctrl + O        Mở tệp
   Ctrl + E        Xuất file âm thanh
   Ctrl + = / -    Phóng to / thu nhỏ chữ
   Ctrl + D        Bật tắt chế độ tối
   F1              Bảng hướng dẫn này

Chữ nhỏ quá thì bấm Ctrl và dấu = vài lần cho to lên."""


def ve_chuong_trinh() -> str:
    return (f"Giọng Việt — giao diện mới cho CHƯƠNG TRÌNH ĐỌC TIẾNG VIỆT "
            f"{engine.APP_VERSION}\n\n"
            "Giọng đọc dùng VieNeu-TTS, chạy hoàn toàn tại máy bằng CPU. "
            "Sau khi tải mô hình lần đầu, chương trình không cần Internet "
            "và không gửi văn bản của bạn đi đâu cả.\n\n"
            f"Thư mục chương trình:\n{engine.BASE_DIR}")
