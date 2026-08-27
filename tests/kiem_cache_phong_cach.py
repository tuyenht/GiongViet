# -*- coding: utf-8 -*-
"""Kiểm tra tính đúng đắn của kho âm thanh khi đổi phong cách đọc.

Lỗi P0: _khoa_kho() trước đây chỉ khoá theo (voice_id, amplification, text)
mà thiếu style/phong_cach. Khi người dùng đổi từ Kể chuyện sang Tin tức,
hệ thống lấy nhầm audio cũ từ kho thay vì tổng hợp mới.
"""
import io
import sys
import time
from pathlib import Path

_GOC = str(Path(__file__).resolve().parent.parent)
sys.path.insert(0, _GOC)
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8")

import DocCongDuc as engine

loi = 0
def ok(dk, nhan, them=""):
    global loi
    print(f"  {'ĐẠT ' if dk else 'LỆCH'} {nhan}{'  →  ' + str(them) if them else ''}")
    if not dk:
        loi += 1

print("--- Kiểm tra: Đổi phong cách đọc -> phải tổng hợp mới, không dùng nhầm kho cũ ---")
cfg = {"vieneu_voice_id": "giong-a", "phong_cach": "Kể chuyện"}
sp = engine.Speaker(cfg)
so_lan = 0
da_goi = []

def gia_synth(text, khuech_dai=1.0):
    global so_lan
    so_lan += 1
    style = engine.PHONG_CACH.get(cfg.get("phong_cach", ""), {}).get("style", "")
    da_goi.append((text, style, khuech_dai))
    return (f"AUDIO:{style}:{text}".encode("utf-8"), "wav")

sp._synth_blocking = gia_synth

# 1. Đọc lần đầu với phong cách 'Kể chuyện' (style: doc_truyen)
a1, _ = sp.get_audio("k1", "Chào buổi sáng.")
ok(so_lan == 1, "lần đầu tổng hợp Kể chuyện", so_lan)
ok(b"doc_truyen" in a1, "audio chứa style doc_truyen", a1)

# 2. Đổi phong cách sang 'Tin tức - thông báo' (style: tin_tuc)
cfg["phong_cach"] = "Tin tức - thông báo"

# 3. Đọc lại cùng câu -> PHẢI tổng hợp mới theo style tin_tuc
a2, _ = sp.get_audio("k2", "Chào buổi sáng.")
ok(so_lan == 2, "đổi phong cách -> phải tổng hợp lần 2", f"{so_lan} lần (nếu là 1 -> DÙNG NHẦM CACHE CŨ)")
ok(b"tin_tuc" in a2, "audio mới phải chứa style tin_tuc", a2)

# 4. Đổi lại phong cách 'Kể chuyện' -> PHẢI hit cache của Kể chuyện (không synth thêm)
cfg["phong_cach"] = "Kể chuyện"
a3, _ = sp.get_audio("k3", "Chào buổi sáng.")
ok(so_lan == 2, "đổi lại Kể chuyện -> hit cache cũ của Kể chuyện", f"{so_lan} lần")
ok(b"doc_truyen" in a3, "audio trả về đúng style doc_truyen", a3)

print("\n" + ("XANH — khớp hết" if not loi else f"ĐỎ — {loi} chỗ lệch (XÁC NHẬN LỖI CACHE STYLE)"))
sys.exit(1 if loi else 0)
