# -*- coding: utf-8 -*-
import sys, pathlib
_core_path = pathlib.Path(__file__).resolve().parent.parent / 'src' / 'core'
__path__ = [str(_core_path)]
import src.core
sys.modules['giaodien'] = src.core

