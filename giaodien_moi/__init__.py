# -*- coding: utf-8 -*-
import sys, pathlib
_app_path = pathlib.Path(__file__).resolve().parent.parent / 'src' / 'app'
__path__ = [str(_app_path)]
import src.app
sys.modules['giaodien_moi'] = src.app

