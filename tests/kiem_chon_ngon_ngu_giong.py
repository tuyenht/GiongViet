# -*- coding: utf-8 -*-
import io, sys
from pathlib import Path
_GOC = str(Path(__file__).resolve().parent.parent)
sys.path.insert(0, _GOC)
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
from src.app import ho_so_v2 as H
from src.core import nghe_thu
loi = 0
def ok(dk, nhan, them=''):
    global loi
    print(('  DAT ' if dk else '  LECH ') + str(nhan) + ((' -> ' + str(them)) if them else ''))
    if not dk: loi += 1
print('--- A. ho_so_v2 giongTheoNgonNgu ---')
hs = {'hoSo': [{'ma': 'h1', 'ten': 'H1', 'giong': 'ngan', 'ngonNgu': 'en-gb', 'giongTheoNgonNgu': {'vi': 'ngan', 'en-gb': 'en-GB-RyanNeural', 'zh': 'zh-CN-YunxiNeural'}}]}
s = H.lam_sach(hs)
ok(s['hoSo'][0]['giongTheoNgonNgu']['en-gb'] == 'en-GB-RyanNeural', 'giu en-gb')
ok(s['hoSo'][0]['giongTheoNgonNgu']['zh'] == 'zh-CN-YunxiNeural', 'giu zh')
print('\n--- B. cau mau quoc te ---')
txt_en = nghe_thu.cau_nghe_thu({'ngonNgu': 'en-gb'}, 'en-GB-RyanNeural')
ok('preview' in txt_en.lower() or 'hello' in txt_en.lower(), 'cau mau en', txt_en)
txt_zh = nghe_thu.cau_nghe_thu({'ngonNgu': 'zh'}, 'zh-CN-YunxiNeural')
ok(len(txt_zh) > 5, 'cau mau zh', txt_zh)
txt_de = nghe_thu.cau_nghe_thu({'ngonNgu': 'de'}, 'de-DE-KatjaNeural')
ok('hallo' in txt_de.lower() or 'probe' in txt_de.lower(), 'cau mau de', txt_de)
print('\nXANH - khop het' if loi == 0 else f'\nDO - {loi} cho lech')
sys.exit(1 if loi else 0)
