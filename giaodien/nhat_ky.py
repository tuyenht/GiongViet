# -*- coding: utf-8 -*-
"""Ghi lỗi kèm traceback đầy đủ ra tệp GiongViet-loi.log.

Người dùng chương trình này phần lớn không rành máy tính, gặp lỗi thì chỉ
biết đọc lại câu thông báo ngắn trên màn hình - không đủ để lần ra nguyên
nhân. Bản đóng gói lại không có cửa sổ dòng lệnh nên traceback bay đi mất.

Tệp log nằm cạnh chương trình, người dùng chỉ cần gửi nó đi là đủ dữ kiện.
Không ghi nội dung văn bản đang đọc vào log - đó là chuyện riêng của họ.
"""

import sys
import time
import traceback
from pathlib import Path

import DocCongDuc as engine

TEP_LOG = engine.BASE_DIR / "GiongViet-loi.log"
GIOI_HAN_BYTE = 512 * 1024


def _cat_bot_neu_dai():
    try:
        if TEP_LOG.exists() and TEP_LOG.stat().st_size > GIOI_HAN_BYTE:
            TEP_LOG.unlink()
    except OSError:
        pass


def ghi_loi(boi_canh: str, loi: BaseException):
    """Ghi một sự cố. boi_canh: đang làm gì lúc lỗi, viết cho người đọc hiểu."""
    _cat_bot_neu_dai()
    try:
        with TEP_LOG.open("a", encoding="utf-8") as f:
            f.write("\n" + "=" * 72 + "\n")
            f.write(f"{time.strftime('%Y-%m-%d %H:%M:%S')}  |  {boi_canh}\n")
            f.write(f"đóng gói: {'có' if getattr(sys, 'frozen', False) else 'không'}"
                    f"  |  python {sys.version.split()[0]}\n")
            f.write(f"{type(loi).__name__}: {loi}\n\n")
            f.write("".join(traceback.format_exception(
                type(loi), loi, loi.__traceback__)))
    except OSError:
        pass


def ghi_chu(dong: str):
    """Ghi một dòng ghi chú (không phải lỗi) - dùng khi cần lần dấu vết."""
    _cat_bot_neu_dai()
    try:
        with TEP_LOG.open("a", encoding="utf-8") as f:
            f.write(f"{time.strftime('%H:%M:%S')}  {dong}\n")
    except OSError:
        pass


def duong_dan() -> str:
    return str(TEP_LOG)
