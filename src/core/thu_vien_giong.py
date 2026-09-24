# -*- coding: utf-8 -*-
"""Dữ liệu cho màn hình Thư viện giọng.

Sóng âm trên thẻ giọng riêng được đọc THẬT từ file mẫu người dùng đã thu,
không phải hình trang trí sinh ngẫu nhiên - nhìn vào là biết mẫu thu có to
rõ hay bị rè, bị im tiếng.

Giọng dựng sẵn của VieNeu nằm trong mô hình, không có file mẫu riêng nên
không vẽ sóng - thà để trống còn hơn vẽ một hình bịa ra.
"""

import array
import shutil
import wave
from pathlib import Path

import DocCongDuc as engine

SO_COT_SONG = 32
GIAY_DOC_TOI_DA = 30


def _co_chu(so_byte: int) -> str:
    gb = so_byte / (1024 ** 3)
    if gb >= 1:
        return f"{gb:.1f} GB".replace(".", ",")
    mb = so_byte / (1024 ** 2)
    if mb >= 1:
        return f"{mb:.0f} MB"
    return f"{so_byte / 1024:.0f} KB"


_SONG_AM_CACHE = {}


def song_am(duong_dan) -> list:
    """Biên độ từng khúc của file mẫu, quy về thang 0..1 để giao diện vẽ cột (kèm cache mtime trong RAM)."""
    if not duong_dan:
        return []
    p = Path(duong_dan)
    if not p.exists():
        return []
    try:
        mtime = p.stat().st_mtime
        cache_item = _SONG_AM_CACHE.get(str(p))
        if cache_item and cache_item[0] == mtime:
            return list(cache_item[1])
    except OSError:
        pass

    try:
        with wave.open(str(p), "rb") as w:
            if w.getsampwidth() != 2 or not w.getnframes():
                return []
            kenh = w.getnchannels()
            khung = w.readframes(min(w.getnframes(),
                                     w.getframerate() * GIAY_DOC_TOI_DA))
    except (wave.Error, OSError, EOFError):
        return []

    mau = array.array("h")
    mau.frombytes(khung[:len(khung) - len(khung) % 2])
    if kenh > 1:
        mau = mau[::kenh]
    if not len(mau):
        return []

    buoc = max(1, len(mau) // SO_COT_SONG)
    cot = []
    for i in range(0, buoc * SO_COT_SONG, buoc):
        khoi = mau[i:i + buoc]
        cot.append(max(abs(min(khoi)), abs(max(khoi))) if khoi else 0)
    dinh = max(cot) or 1
    res = [round(c / dinh, 3) for c in cot]
    try:
        _SONG_AM_CACHE[str(p)] = (p.stat().st_mtime, res)
    except OSError:
        pass
    return res


def _kich_thuoc(duong_dan) -> int:
    p = Path(duong_dan)
    try:
        if p.is_file():
            return p.stat().st_size
        if p.is_dir():
            return sum(f.stat().st_size for f in p.rglob("*") if f.is_file())
    except OSError:
        pass
    return 0


def _cho_trong() -> str:
    try:
        return _co_chu(shutil.disk_usage(engine.BASE_DIR).free)
    except OSError:
        return "—"


def du_lieu(voices: list, dang_dung: str) -> dict:
    """voices: danh sách đã qua du_lieu.danh_sach_giong (có ten, mo_ta, rieng)."""
    from src.core import danh_muc_giong
    goc_rieng = {g["id"]: g for g in engine.doc_ds_giong_rieng()}
    cua_toi, co_san = [], []
    da_co = set()

    for v in voices:
        vid = v.get("id")
        if vid in da_co:
            continue
        da_co.add(vid)

        info = danh_muc_giong.tra_cuu_thong_tin_giong(vid)

        the = {
            "id": vid,
            "ten": v["ten"],
            "moTa": info["dac_trung"],
            "phongCach": info["phong_cach"],
            "khuyenDung": info["khuyen_dung"],
            "vung": info["vung"],
            "gioi": info["gioi"],
            "dangDung": vid == dang_dung or str(dang_dung).startswith(str(vid)),
            "rieng": v["rieng"],
            "song": [],
            "phu": f"{info['vung']} · {info['phong_cach']} · Khuyên dùng: {info['khuyen_dung']}",
        }
        if v["rieng"]:
            g = goc_rieng.get(vid, {})
            # Đọc cờ THẬT người dùng đã đặt, đừng gán cứng True/"all": gán cứng
            # là mọi giọng nhân bản đều bị dán nhãn "đa ngữ" dù người dùng vừa
            # tắt nó đi, và con số đếm ở màn Thư viện giọng phồng theo.
            the["daNgonNgu"] = bool(g.get("da_ngon_ngu", False))
            the["ngonNgu"] = str(g.get("ngon_ngu", "vi"))
            tep = g.get("file", "")
            the["song"] = song_am(tep)
            # Chốt `if tep` phải giữ: Path("") ra WindowsPath('.'), is_dir() đúng,
            # rồi _kich_thuoc rglob đệ quy CẢ thư mục làm việc và in ra như thể
            # đó là cỡ mẫu thu.
            co_size = _co_chu(_kich_thuoc(tep)) if tep else "chưa có"
            the["phu"] = f"Mẫu thu {co_size} · {info['phong_cach']} · Khuyên dùng: {info['khuyen_dung']}"
            cua_toi.append(the)
        else:
            the["daNgonNgu"] = bool(v.get("da_ngon_ngu", False))
            the["ngonNgu"] = str(v.get("ngon_ngu", "vi"))
            # KHÔNG vẽ sóng cho giọng dựng sẵn. Docstring đầu tệp đã chốt: giọng
            # dựng sẵn nằm trong mô hình, không có tệp mẫu nên không có sóng
            # thật để đọc - thà để trống còn hơn vẽ một hình bịa ra. Bản trước
            # sinh sóng bằng math.sin() từ mã băm tên giọng, nhìn y như sóng
            # thật nên người dùng tưởng đó là dạng sóng của giọng đó.
            co_san.append(the)

    # Mô hình nay nằm ở models/vieneu; "vieneu_models" là bố cục cũ. Dò cả hai
    # đúng cách engine vẫn dò (DocCongDuc.py), chứ gõ cứng một đường là màn hình
    # báo "chiếm chưa có" trong khi đĩa đang giữ hơn 300 MB.
    mo_hinh = _kich_thuoc(engine.MODELS_DIR)
    mau_rieng = _kich_thuoc(engine.GIONG_RIENG_DIR)
    return {
        "cuaToi": cua_toi,
        "coSan": co_san,
        "boNho": (f"Mô hình giọng chiếm {_co_chu(mo_hinh)}"
                  + (f", mẫu giọng riêng {_co_chu(mau_rieng)}" if mau_rieng else "")
                  + f". Ổ đĩa còn trống {_cho_trong()}."),
    }
