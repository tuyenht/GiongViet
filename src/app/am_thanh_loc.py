# -*- coding: utf-8 -*-
"""Dựng chuỗi bộ lọc ffmpeg cho Tốc độ · Cao độ · Âm lượng của hồ sơ đọc.

VieNeu-TTS không có tham số tốc độ và cao độ - đúng như ghi trong CLAUDE.md.
Nhưng ba thanh trượt trong đặc tả KHÔNG cần mô hình làm: ffmpeg đi kèm chương
trình làm được cả ba, và bản ffmpeg đang có đã biên dịch sẵn `rubberband`.

Đo ngày 2026-08-12 trên chính bản ffmpeg trong thư mục ffmpeg/bin:

    atempo=1.1      10,000 s -> 9,092 s   (lý thuyết 9,091)   144 ms
    atempo=0.5      10,000 s -> 19,980 s  (lý thuyết 20,000)  197 ms
    rubberband      đổi cao độ, độ dài giữ nguyên 10,000 s     252-315 ms
    volume=0.5      -18,1 dB -> -24,1 dB  (lý thuyết -6,02 dB)

Giá phải trả: khoảng 0,25 giây cho mỗi 10 giây tiếng. Tổng hợp một đoạn mất
5-10 giây, nên phần lọc chiếm vài phần trăm. Lúc PHÁT thì còn không mất gì:
ffplay nhận thẳng -af, không phải chạy thêm tiến trình nào.

Module này KHÔNG gọi ffmpeg. Nó chỉ dựng chuỗi chữ; nơi gọi cắm chuỗi đó vào
lệnh ffplay hoặc ffmpeg sẵn có.
"""

# Đặc tả: Tốc độ −50%…+100% · Cao độ −12…+12 nửa cung · Âm lượng 0…100%.
TOC_DO_MIN, TOC_DO_MAX = -50, 100
CAO_DO_MIN, CAO_DO_MAX = -12, 12
AM_LUONG_MIN, AM_LUONG_MAX = 0, 100

# atempo của ffmpeg nhận 0.5 trở lên, vừa khít khoảng của đặc tả nên không
# phải nối nhiều tầng atempo như cách người ta hay làm để vượt biên.
TEMPO_MIN, TEMPO_MAX = 0.5, 2.0

MAC_DINH = {"tocDo": 0, "caoDo": 0, "amLuong": 100}


def _ep(gt, thap, cao):
    return max(thap, min(cao, gt))


def he_so_tempo(toc_do_phan_tram: float) -> float:
    """−50% -> 0.5 · 0% -> 1.0 · +100% -> 2.0"""
    return _ep(1.0 + _ep(toc_do_phan_tram, TOC_DO_MIN, TOC_DO_MAX) / 100.0,
               TEMPO_MIN, TEMPO_MAX)


def he_so_pitch(nua_cung: float) -> float:
    """Nửa cung -> tỉ lệ tần số. Mỗi quãng tám là 12 nửa cung, nên 2^(n/12)."""
    return 2.0 ** (_ep(nua_cung, CAO_DO_MIN, CAO_DO_MAX) / 12.0)


def chuoi_loc(chinh: dict) -> str:
    """Trả chuỗi -af, hoặc chuỗi RỖNG nếu hồ sơ để mặc định.

    Trả rỗng khi không phải chỉnh gì là cố ý: không thêm bộ lọc thì tiếng đi
    thẳng từ mô hình ra loa, không qua một lần dựng lại sóng nào. Người dùng
    không chỉnh gì thì không phải chịu rủi ro nào.
    """
    toc = _ep(float(chinh.get("tocDo", 0)), TOC_DO_MIN, TOC_DO_MAX)
    cao = _ep(float(chinh.get("caoDo", 0)), CAO_DO_MIN, CAO_DO_MAX)
    am = _ep(float(chinh.get("amLuong", 100)), AM_LUONG_MIN, AM_LUONG_MAX)

    khong_gian = str(chinh.get("khongGian") or "").strip().lower()

    phan = []
    if cao:
        phan.append(f"rubberband=tempo={he_so_tempo(toc):.6g}"
                    f":pitch={he_so_pitch(cao):.6g}")
    elif toc:
        phan.append(f"atempo={he_so_tempo(toc):.6g}")

    if am != 100:
        phan.append(f"volume={am / 100.0:.6g}")

    if khong_gian == "podcast":
        phan.append("bass=g=4:f=110,treble=g=-2")
    elif khong_gian == "hoitruong":
        phan.append("aecho=0.8:0.9:1000:0.3")
    elif khong_gian == "loaphuong":
        phan.append("highpass=f=300,lowpass=f=3000,volume=1.2")
    elif khong_gian == "radio":
        phan.append("aecho=0.8:0.88:60:0.4")

    return ",".join(phan)


def them_vao_lenh(lenh: list, chinh: dict) -> list:
    """Chèn -af vào một lệnh ffplay/ffmpeg đã dựng sẵn. Không chỉnh gì thì
    trả nguyên lệnh cũ, không thêm tham số thừa."""
    loc = chuoi_loc(chinh)
    return lenh if not loc else list(lenh) + ["-af", loc]


def mo_ta(chinh: dict) -> str:
    """Dòng tóm tắt khi mục ĐIỀU CHỈNH đang đóng ở cột phải."""
    toc = int(chinh.get("tocDo", 0))
    cao = int(chinh.get("caoDo", 0))
    am = int(chinh.get("amLuong", 100))
    kg = str(chinh.get("khongGian") or "").strip().lower()
    
    p = []
    if toc:
        p.append(f"Tốc độ {'+' if toc > 0 else '−'}{abs(toc)}%")
    if cao:
        p.append(f"Cao độ {'+' if cao > 0 else '−'}{abs(cao)}")
    if am != 100:
        p.append(f"Âm lượng {am}%")
    if kg == "podcast":
        p.append("Studio/Podcast")
    elif kg == "hoitruong":
        p.append("Hội trường")
    elif kg == "loaphuong":
        p.append("Loa phường")
    elif kg == "radio":
        p.append("Radio FM")
        
    return " · ".join(p) if p else "Theo mặc định của hồ sơ"
