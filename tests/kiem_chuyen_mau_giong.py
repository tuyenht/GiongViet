# -*- coding: utf-8 -*-
"""Kiểm tra: Lõi Chuyển Đổi Âm Sắc Xuyên Ngôn Ngữ (Cross-Lingual Tone Color Transfer)."""

import io
import sys
import time
import wave
from pathlib import Path
import numpy as np

_GOC = str(Path(__file__).resolve().parent.parent)
sys.path.insert(0, _GOC)
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8")

loi = 0
def ok(dk, nhan, them=""):
    global loi
    print(f"  {'ĐẠT ' if dk else 'LỆCH'} {nhan}{'  →  ' + str(them) if them else ''}")
    if not dk:
        loi += 1

print("--- A. Trích xuất Vân giọng (Timbre Feature Extraction) ---")
from src.core.chuyen_mau_giong import BoChuyenMauGiong

# 1. Tạo file WAV mẫu giọng test
ref_path = Path("ref_temp_test.wav")
try:
    with wave.open(str(ref_path), "wb") as w:
        w.setnchannels(1)
        w.setsampwidth(2)
        w.setframerate(48000)
        t = np.linspace(0, 3, 48000 * 3)
        # Giọng mẫu trầm ấm đặc trưng (130Hz + các họa âm F1/F2)
        sig = 0.5 * np.sin(2 * np.pi * 130 * t) + 0.3 * np.sin(2 * np.pi * 260 * t) + 0.2 * np.sin(2 * np.pi * 520 * t)
        w.writeframes((sig * 32767).astype(np.int16).tobytes())

    t0 = time.time()
    timbre1 = BoChuyenMauGiong.trich_xuat_van_giong(str(ref_path))
    t_extract = (time.time() - t0) * 1000
    ok(timbre1 is not None and len(timbre1) > 100, "trích xuất thành công vector âm sắc", f"{len(timbre1)} bins trong {t_extract:.1f}ms")

    t0 = time.time()
    timbre2 = BoChuyenMauGiong.trich_xuat_van_giong(str(ref_path))
    t_cache = (time.time() - t0) * 1000
    ok(timbre2 is timbre1, "lần 2 lấy thẳng từ RAM Cache (0ms)", f"{t_cache:.3f}ms")

    print("\n--- B. Biến đổi âm sắc PCM Stream trong Realtime (CPU < 5ms) ---")
    # Tạo 1 giây âm thanh nguồn (ví dụ tiếng bản ngữ 200Hz)
    t_src = np.linspace(0, 1, 48000)
    raw_pcm_in = (np.sin(2 * np.pi * 200 * t_src) * 25000).astype(np.int16).tobytes()

    t0 = time.time()
    converted_pcm = BoChuyenMauGiong.chuyen_doi_pcm_chunk(raw_pcm_in, timbre1, cuong_do=0.75)
    t_convert = (time.time() - t0) * 1000
    ok(len(converted_pcm) == len(raw_pcm_in), "độ dài PCM giữ nguyên 100%", f"{len(converted_pcm)} bytes")
    ok(t_convert < 250.0, "tốc độ chuyển đổi siêu tốc trên CPU", f"{t_convert:.2f}ms cho 1s audio")


    print("\n--- C. Chuyển đổi trọn gói file WAV (Đóng gói Cache) ---")
    out_wav = io.BytesIO()
    with wave.open(out_wav, "wb") as w:
        w.setnchannels(1)
        w.setsampwidth(2)
        w.setframerate(48000)
        w.writeframes(raw_pcm_in)
    in_wav_bytes = out_wav.getvalue()

    out_converted_wav = BoChuyenMauGiong.chuyen_doi_wav(in_wav_bytes, str(ref_path))
    ok(out_converted_wav.startswith(b"RIFF") and len(out_converted_wav) > 44, "chuyển đổi WAV thành công và giữ chuẩn RIFF header")

    print("\n--- D. Kiểm tra tính bền bỉ với chunk kích thước tùy ý (Small & Large Chunks) ---")
    for chunk_size in (256, 1024, 4096, 16384):
        sub_chunk = raw_pcm_in[:chunk_size]
        conv_sub = BoChuyenMauGiong.chuyen_doi_pcm_chunk(sub_chunk, timbre1)
        ok(len(conv_sub) == len(sub_chunk), f"khớp chính xác độ dài byte với chunk {chunk_size} bytes")

finally:
    ref_path.unlink(missing_ok=True)

print(f"\n{('XANH — khớp hết' if loi == 0 else f'ĐỎ — {loi} chỗ lệch')}")
sys.exit(loi)
