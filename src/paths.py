# -*- coding: utf-8 -*-
"""Quản lý đường dẫn động tập trung toàn dự án (src/paths.py).

Tuân thủ Clean Architecture: Hỗ trợ cả 2 chế độ:
- Chế độ Source (Development / Testing)
- Chế độ Đóng gói Frozen (PyInstaller Executable Bundle)
"""
import sys
from pathlib import Path


def _tim_thu_muc_goc() -> Path:
    if getattr(sys, "frozen", False):
        return Path(sys.executable).resolve().parent
    return Path(__file__).resolve().parent.parent


ROOT_DIR = _tim_thu_muc_goc()
SRC_DIR = ROOT_DIR / "src"
CORE_DIR = SRC_DIR / "core"
APP_DIR = SRC_DIR / "app"
TESTS_DIR = ROOT_DIR / "tests"
DOCS_DIR = ROOT_DIR / "docs"
ARCHIVE_DIR = ROOT_DIR / "_archive"

# --- TẦNG DỮ LIỆU (Data Layer) ---
DATA_DIR = ROOT_DIR / "data"
CONFIG_DB = DATA_DIR / "giongviet.db" if (DATA_DIR / "giongviet.db").exists() else ROOT_DIR / "giongviet.db"
CUSTOM_VOICES_DIR = DATA_DIR / "giong_rieng" if (DATA_DIR / "giong_rieng").exists() else ROOT_DIR / "giong_rieng"

# --- TẦNG NHỊ PHÂN & MÔ HÌNH (Binaries & Models) ---
BIN_DIR = ROOT_DIR / "bin" / "ffmpeg" if (ROOT_DIR / "bin" / "ffmpeg").exists() else ROOT_DIR / "ffmpeg"
MODELS_DIR = ROOT_DIR / "models" / "vieneu" if (ROOT_DIR / "models" / "vieneu").exists() else ROOT_DIR / "vieneu_models"


def get_web_dir() -> Path:
    """Tìm thư mục giao diện Web, hỗ trợ cả Frozen bundle lẫn Source mode."""
    ung_vien = [
        SRC_DIR / "web",
        ROOT_DIR / "ui-moi",
    ]
    meipass = getattr(sys, "_MEIPASS", "")
    if meipass:
        ung_vien.insert(0, Path(meipass) / "web")
        ung_vien.insert(0, Path(meipass) / "ui-moi")
    for d in ung_vien:
        if (d / "index.html").exists():
            return d
    return ung_vien[0]


WEB_DIR = get_web_dir()
