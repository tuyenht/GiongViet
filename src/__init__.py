# -*- coding: utf-8 -*-
"""Gói mã nguồn chính của ứng dụng Giọng Việt (src)."""
import sys
from . import core, app
from .core import kho_cau_hinh

# Đăng ký alias tương thích ngược vào sys.modules
sys.modules.setdefault("giaodien", core)
sys.modules.setdefault("giaodien_moi", app)
sys.modules.setdefault("kho_cau_hinh", kho_cau_hinh)
