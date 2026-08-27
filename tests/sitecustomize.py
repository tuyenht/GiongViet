# -*- coding: utf-8 -*-
"""Cầu nối tương thích ngược Import tự động (sitecustomize.py).

Tuân thủ chuẩn PEP 302 / PEP 451: Tự động chuyển hướng các import di sản:
- giaodien.*     -> src/core/*
- giaodien_moi.* -> src/app/*
- kiem.*         -> tests/*
Giữ cho thư mục gốc luôn sạch 100% mà không làm gián đoạn bất kỳ bài test nào.
"""
import importlib.abc
import importlib.util
import sys
from pathlib import Path

_FILE = Path(__file__).resolve()
_ROOT = _FILE.parent if _FILE.parent.name != "tests" else _FILE.parent.parent

class LegacyImportFinder(importlib.abc.MetaPathFinder):
    _MAP = {
        "giaodien": _ROOT / "src" / "core",
        "giaodien_moi": _ROOT / "src" / "app",
        "kiem": _ROOT / "tests",
    }
    _FILE_MAP = {
        "kho_cau_hinh": _ROOT / "src" / "core" / "kho_cau_hinh.py",
    }

    def find_spec(self, fullname, path, target=None):
        if fullname in self._FILE_MAP:
            target_file = self._FILE_MAP[fullname]
            if target_file.exists():
                return importlib.util.spec_from_file_location(fullname, str(target_file))
        parts = fullname.split(".")
        root_mod = parts[0]
        if root_mod in self._MAP:
            target_dir = self._MAP[root_mod]
            if len(parts) == 1:
                init_py = target_dir / "__init__.py"
                if init_py.exists():
                    return importlib.util.spec_from_file_location(
                        fullname, str(init_py), submodule_search_locations=[str(target_dir)]
                    )
                return importlib.util.spec_from_file_location(
                    fullname, None, submodule_search_locations=[str(target_dir)]
                )
            else:
                sub_name = parts[1]
                sub_path = target_dir / f"{sub_name}.py"
                if sub_path.exists():
                    return importlib.util.spec_from_file_location(fullname, str(sub_path))
        return None

if not any(isinstance(f, LegacyImportFinder) for f in sys.meta_path):
    sys.meta_path.insert(0, LegacyImportFinder())
