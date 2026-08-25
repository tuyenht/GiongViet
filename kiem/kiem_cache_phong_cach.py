# -*- coding: utf-8 -*-
"""Canh loi cache tra lai WAV cua phong cach cu sau khi doi phong cach doc.

Bai nay KHONG nap mo hinh that: thay tong_hop_vieneu bang ham gia de chi kiem
hanh vi cache cua Speaker. Neu cung mot cau + cung giong nhung doi phong cach,
Speaker bat buoc phai tong hop lai thay vi lay WAV cua phong cach truoc.

Chay:
    py kiem\kiem_cache_phong_cach.py
"""

import sys
from pathlib import Path

_GOC = str(Path(__file__).resolve().parent.parent)
if _GOC not in sys.path:
    sys.path.insert(0, _GOC)

import DocCongDuc as engine  # noqa: E402


def main():
    goi = []
    tong_hop_goc = engine.tong_hop_vieneu

    def tong_hop_gia(text, voice_id, style, khuech_dai=1.0):
        goi.append((text, voice_id, style, khuech_dai))
        return f"{style}|{voice_id}|{text}".encode("utf-8")

    cfg = {
        "vieneu_voice_id": "kiem-cache-style",
        "phong_cach": "Kể chuyện",
    }
    speaker = engine.Speaker(cfg)
    engine.tong_hop_vieneu = tong_hop_gia
    try:
        audio_1, fmt_1 = speaker.get_audio(0, "Xin chào quý vị.")
        assert fmt_1 == "wav"
        assert audio_1.startswith(b"doc_truyen|")
        assert len(goi) == 1, "Lan dau phai tong hop dung mot lan"

        # Mo phong dung duong cap_nhat_cfg(): doi cfg va clear_cache().
        # clear_cache chi xoa hang prefetch, co y giu kho noi dung.
        cfg["phong_cach"] = "Tin tức - thông báo"
        speaker.cfg = cfg
        speaker.clear_cache()

        audio_2, fmt_2 = speaker.get_audio(0, "Xin chào quý vị.")
        assert fmt_2 == "wav"
        assert audio_2.startswith(b"tin_tuc|"), (
            "Doi phong cach nhung Speaker van tra WAV phong cach cu tu cache"
        )
        assert len(goi) == 2, (
            "Doi phong cach phai tong hop lai, khong duoc hit cache cu"
        )
    finally:
        engine.tong_hop_vieneu = tong_hop_goc
        speaker.shutdown()

    print("PASS: cache tach rieng theo phong cach doc")


if __name__ == "__main__":
    main()
