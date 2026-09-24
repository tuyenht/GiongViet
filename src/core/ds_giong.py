# -*- coding: utf-8 -*-
"""Đọc danh sách giọng NGAY, không đợi nạp mô hình.

engine.lay_danh_sach_giong_day_du() phải dựng Vieneu() trước vì
list_preset_voices() là hàm của đối tượng - mà dựng Vieneu() nghĩa là nạp cả
mô hình thần kinh vào RAM, mất 25-40 giây. Người dùng ngồi nhìn ô giọng ghi
"Đang tải danh sách giọng…" suốt từng ấy thời gian, tưởng chương trình treo.

Thực ra danh sách chỉ nằm trong assets/voices_v3_turbo.json, đọc mất vài mili
giây. Còn giọng riêng thì nằm trong giong_rieng/danhsach.json. Module này đọc
thẳng hai tệp đó để hiện danh sách tức thì; mô hình vẫn nạp song song ở luồng
nền cho việc phát tiếng.

Trả về ĐÚNG định dạng của engine.lay_danh_sach_giong_day_du() -
[{"id":.., "ten":..}] - để phần còn lại không phải đổi gì.
"""

import json
from pathlib import Path

import DocCongDuc as engine


def _tep_preset() -> Path:
    """assets/voices_v3_turbo.json nằm cạnh gói vieneu. Không import vieneu ở
    mức module: import nó là kéo theo torch, chậm y như cũ."""
    import importlib.util
    dac_ta = importlib.util.find_spec("vieneu")
    if not dac_ta or not dac_ta.submodule_search_locations:
        return Path()
    goc = Path(list(dac_ta.submodule_search_locations)[0])
    return goc / "assets" / "voices_v3_turbo.json"


def doc_preset() -> list:
    tep = _tep_preset()
    if not tep or not tep.exists():
        return []
    try:
        data = json.loads(tep.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError, UnicodeDecodeError):
        return []
    presets = data.get("presets")
    if not isinstance(presets, dict):
        return []
    ket_qua = []
    for ten, muc in presets.items():
        mo_ta = (muc or {}).get("description") or ""
        ket_qua.append({"id": ten, "ten": f"{ten} — {mo_ta}" if mo_ta else ten})
    return ket_qua


def doc_nhanh() -> list:
    """Giọng riêng trước, giọng dựng sẵn sau, kèm toàn bộ giọng quốc tế - đúng thứ tự của
    engine.lay_danh_sach_giong_day_du()."""
    rieng = [{"id": g["id"], "ten": f'🎙️ {g["ten"]}  (giọng riêng · 28+ ngôn ngữ, cần mạng)', "da_ngon_ngu": True, "ngon_ngu": "all"}
             for g in engine.doc_ds_giong_rieng()]
    ma_rieng = {g["id"] for g in rieng}
    preset = [v for v in doc_preset() if v["id"] not in ma_rieng]
    for v in preset:
        v["da_ngon_ngu"] = False
        v["ngon_ngu"] = "vi"

    quoc_te = []
    try:
        from src.core.da_ngon_ngu_tts import DS_GIONG_QUOC_TE_CHI_TIET
        TEN_QUOC_GIA = {
            "vi": "Tiếng Việt", "th": "Tiếng Thái", "lo": "Tiếng Lào", "id": "Tiếng Indonesia",
            "ms": "Tiếng Malaysia", "fil": "Tiếng Philippines", "km": "Tiếng Khmer", "my": "Tiếng Myanmar",
            "zh": "Tiếng Trung", "zh-tw": "Tiếng Trung", "yue": "Tiếng Trung",
            "ja": "Tiếng Nhật", "ko": "Tiếng Hàn", "en": "Tiếng Anh", "en-gb": "Tiếng Anh",
            "fr": "Tiếng Pháp", "de": "Tiếng Đức", "es": "Tiếng Tây Ban Nha", "pt": "Tiếng Bồ Đào Nha",
            "it": "Tiếng Ý", "ru": "Tiếng Nga", "nl": "Tiếng Hà Lan", "ar": "Tiếng Ả Rập",
            "hi": "Tiếng Hindi", "bn": "Tiếng Bengal", "ur": "Tiếng Urdu", "ta": "Tiếng Tamil",
            "mr": "Tiếng Marathi", "tr": "Tiếng Thổ Nhĩ Kỳ"
        }
        for g in DS_GIONG_QUOC_TE_CHI_TIET:
            ma_nn = g["ngon_ngu"]
            ten_nn = TEN_QUOC_GIA.get(ma_nn, ma_nn.upper())
            vung_str = f" ({g['vung']})" if g.get("vung") else ""
            quoc_te.append({
                "id": g["id"],
                "ten": f"{g['ten']} — {g['gioi']} · {ten_nn}{vung_str} · Chuẩn bản xứ",
                "da_ngon_ngu": False,
                "ngon_ngu": ma_nn
            })
    except Exception:
        pass

    return rieng + preset + quoc_te
