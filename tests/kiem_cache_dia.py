# -*- coding: utf-8 -*-
import io
import sys
import time
from pathlib import Path

_GOC = str(Path(__file__).resolve().parent.parent)
sys.path.insert(0, _GOC)
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8")

import DocCongDuc as engine

def kiem():
    print("--- Kiểm tra: Kho âm thanh đĩa (Persistent Disk Cache SHA-256) ---")
    
    so_lan_tong_hop = 0
    def mock_synth(text, khuech_dai=1.0):
        nonlocal so_lan_tong_hop
        so_lan_tong_hop += 1
        return (f"AUDIO_REAL:{text}".encode("utf-8"), "wav")
    
    cfg = {"phong_cach": "Kể chuyện", "vieneu_voice_id": "hn_thao"}
    sp1 = engine.Speaker(cfg)
    sp1._synth_blocking = mock_synth
    
    text_test = f"Kính mừng Đức Phật Thích Ca Mâu Ni. {time.time_ns()}"
    
    # Lần 1: Chưa có trên RAM và Đĩa -> Phải tổng hợp
    a1, fmt1 = sp1.get_audio("k1", text_test, 1.0)
    assert so_lan_tong_hop == 1, f"Lần đầu phải tổng hợp, thực tế: {so_lan_tong_hop}"
    print(f"  ĐẠT  Lần đầu tổng hợp và lưu xuống đĩa  →  {so_lan_tong_hop} lần")
    
    # Kiểm tra file đã xuất hiện trên đĩa
    ma_bam = sp1._ma_bam_kho(text_test, 1.0)
    tep_cache = sp1._thu_muc_cache_dia() / f"{ma_bam}.wav"
    assert tep_cache.exists(), f"File cache trên đĩa phải tồn tại: {tep_cache}"
    print(f"  ĐẠT  File cache đĩa SHA-256 tồn tại: {tep_cache.name[:16]}...wav")
    
    # Khởi tạo một Speaker hoàn toàn mới (mô phỏng tắt bật lại app) -> RAM rỗng
    sp2 = engine.Speaker(cfg)
    sp2._synth_blocking = mock_synth
    assert len(sp2._kho) == 0, "RAM của instance mới phải rỗng"
    
    # Lần 2 trên Speaker mới -> Phải đọc từ đĩa (KHÔNG tăng số lần tổng hợp)
    t0 = time.perf_counter()
    a2, fmt2 = sp2.get_audio("k2", text_test, 1.0)
    t_doc_dia_ms = (time.perf_counter() - t0) * 1000
    
    assert so_lan_tong_hop == 1, f"Đọc lại từ đĩa không được tổng hợp lại! Thực tế: {so_lan_tong_hop}"
    assert a2 == a1, "Dữ liệu âm thanh đọc từ đĩa phải khớp tuyệt đối"
    print(f"  ĐẠT  Speaker mới nạp từ đĩa 0ms (thực tế {t_doc_dia_ms:.3f} ms), không cần tổng hợp lại")
    
    print("\nXANH — Kho đĩa SHA-256 đạt chuẩn 100%")

if __name__ == "__main__":
    kiem()
