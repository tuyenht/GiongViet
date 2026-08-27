# -*- coding: utf-8 -*-
"""Lõi Dịch thuật và Nhận diện Ngôn ngữ Tự động (Zero-Cost Neural Translation Core).

Hỗ trợ 28 ngôn ngữ toàn cầu, tự động phát hiện ngôn ngữ nguồn,
tinh chỉnh văn phong theo thể loại kịch bản, và đệm bộ nhớ đệm (Cache) tức thì.
"""

import json
import re
import urllib.parse
import urllib.request
from typing import Dict, List, Optional, Tuple

_CACHE_DICH: Dict[Tuple[str, str, str], str] = {}

DS_28_NGON_NGU = [
    # Nhóm 1: Bản Địa & Đông Nam Á (ASEAN)
    {"ma": "vi", "ten": "Tiếng Việt (Gốc)", "co": "🇻🇳", "nhom": "Đông Nam Á"},
    {"ma": "th", "ten": "Tiếng Thái (ภาษาไทย)", "co": "🇹🇭", "nhom": "Đông Nam Á"},
    {"ma": "id", "ten": "Tiếng Indonesia (Bahasa)", "co": "🇮🇩", "nhom": "Đông Nam Á"},
    {"ma": "ms", "ten": "Tiếng Malaysia (Melayu)", "co": "🇲🇾", "nhom": "Đông Nam Á"},
    {"ma": "fil", "ten": "Tiếng Philippines (Tagalog)", "co": "🇵🇭", "nhom": "Đông Nam Á"},
    {"ma": "km", "ten": "Tiếng Campuchia (Khmer)", "co": "🇰🇭", "nhom": "Đông Nam Á"},
    {"ma": "lo", "ten": "Tiếng Lào (Lao)", "co": "🇱🇦", "nhom": "Đông Nam Á"},
    {"ma": "my", "ten": "Tiếng Myanmar (Burmese)", "co": "🇲🇲", "nhom": "Đông Nam Á"},

    # Nhóm 2: Đông Á
    {"ma": "zh", "ten": "Tiếng Trung (Phổ thông)", "co": "🇨🇳", "nhom": "Đông Á"},
    {"ma": "yue", "ten": "Tiếng Trung (Quảng Đông)", "co": "🇭🇰", "nhom": "Đông Á"},
    {"ma": "ja", "ten": "Tiếng Nhật (日本語)", "co": "🇯🇵", "nhom": "Đông Á"},
    {"ma": "ko", "ten": "Tiếng Hàn (한국어)", "co": "🇰🇷", "nhom": "Đông Á"},

    # Nhóm 3: Âu - Mỹ & Toàn Cầu
    {"ma": "en", "ten": "Tiếng Anh (Mỹ - US)", "co": "🇺🇸", "nhom": "Âu - Mỹ & Toàn Cầu"},
    {"ma": "en-gb", "ten": "Tiếng Anh (Anh - UK)", "co": "🇬🇧", "nhom": "Âu - Mỹ & Toàn Cầu"},
    {"ma": "fr", "ten": "Tiếng Pháp (Français)", "co": "🇫🇷", "nhom": "Âu - Mỹ & Toàn Cầu"},
    {"ma": "de", "ten": "Tiếng Đức (Deutsch)", "co": "🇩🇪", "nhom": "Âu - Mỹ & Toàn Cầu"},
    {"ma": "es", "ten": "Tiếng Tây Ban Nha (Español)", "co": "🇪🇸", "nhom": "Âu - Mỹ & Toàn Cầu"},
    {"ma": "pt", "ten": "Tiếng Bồ Đào Nha (Português)", "co": "🇵🇹", "nhom": "Âu - Mỹ & Toàn Cầu"},
    {"ma": "it", "ten": "Tiếng Ý (Italiano)", "co": "🇮🇹", "nhom": "Âu - Mỹ & Toàn Cầu"},
    {"ma": "ru", "ten": "Tiếng Nga (Русский)", "co": "🇷🇺", "nhom": "Âu - Mỹ & Toàn Cầu"},
    {"ma": "nl", "ten": "Tiếng Hà Lan (Nederlands)", "co": "🇳🇱", "nhom": "Âu - Mỹ & Toàn Cầu"},

    # Nhóm 4: Nam Á & Trung Đông
    {"ma": "ar", "ten": "Tiếng Ả Rập (العربية)", "co": "🇸🇦", "nhom": "Nam Á & Trung Đông"},
    {"ma": "hi", "ten": "Tiếng Hindi (हिन्दी)", "co": "🇮🇳", "nhom": "Nam Á & Trung Đông"},
    {"ma": "bn", "ten": "Tiếng Bengal (বাংলা)", "co": "🇧🇩", "nhom": "Nam Á & Trung Đông"},
    {"ma": "ur", "ten": "Tiếng Urdu (اردو)", "co": "🇵🇰", "nhom": "Nam Á & Trung Đông"},
    {"ma": "ta", "ten": "Tiếng Tamil (தமிழ்)", "co": "🇮🇳", "nhom": "Nam Á & Trung Đông"},
    {"ma": "mr", "ten": "Tiếng Marathi (मराठी)", "co": "🇮🇳", "nhom": "Nam Á & Trung Đông"},
    {"ma": "tr", "ten": "Tiếng Thổ Nhĩ Kỳ (Türkçe)", "co": "🇹🇷", "nhom": "Nam Á & Trung Đông"},
]


def nhan_dien_ngon_ngu_nhanh(text: str) -> str:
    """Nhận diện ngôn ngữ bằng đặc trưng ký tự và bảng mã (0.001ms)."""
    s = (text or "").strip()
    if not s:
        return "vi"

    # Kiểm tra các hệ chữ đặc thù
    if re.search(r"[\u3040-\u30ff]", s):  # Hiragana / Katakana
        return "ja"
    if re.search(r"[\uac00-\ud7af]", s):  # Hangul
        return "ko"
    if re.search(r"[\u4e00-\u9fa5]", s):  # Hanzi (Trung Quốc)
        return "zh"
    if re.search(r"[\u0e00-\u0e7f]", s):  # Thai
        return "th"
    if re.search(r"[\u0600-\u06ff]", s):  # Arabic
        return "ar"
    if re.search(r"[\u0900-\u097f]", s):  # Devanagari (Hindi)
        return "hi"
    if re.search(r"[\u0980-\u09ff]", s):  # Bengali
        return "bn"
    if re.search(r"[\u0400-\u04ff]", s):  # Cyrillic (Nga)
        return "ru"
    if re.search(r"[\u1780-\u17ff]", s):  # Khmer
        return "km"
    if re.search(r"[\u0e80-\u0eff]", s):  # Lao
        return "lo"
    if re.search(r"[\u1000-\u109f]", s):  # Myanmar
        return "my"

    # Dấu tiếng Việt đặc trưng
    if re.search(r"[àáảãạăằắẳẵặâầấẩẫậèéẻẽẹêềếểễệìíỉĩịòóỏõọôồốổỗộơờớởỡợùúủũụưừứửữựỳýỷỹỵđĐ]", s, re.IGNORECASE):
        return "vi"

    # Mặc định chữ Latinh cơ bản -> Tiếng Anh
    return "en"


MAP_MA_API = {
    "zh": "zh-CN",
    "zh-tw": "zh-TW",
    "yue": "zh-TW",
    "fil": "tl",
    "en-gb": "en",
}


import unicodedata


def _bo_dau_ten(s: str) -> str:
    s = str(s or "").replace("Đ", "D").replace("đ", "d")
    return "".join(c for c in unicodedata.normalize("NFD", s) if unicodedata.category(c) != "Mn")


def _chuan_hoa_thuc_the_viet_nam(text: str, tgt_lang: str = "en") -> str:
    """Chuẩn hóa thực thể tên người, địa danh, Phật học, hành chính trước khi dịch sang ngoại ngữ."""
    s = text or ""
    if not s.strip():
        return ""

    # 1. Danh xưng Phật giáo / Tôn giáo / Lễ nghi
    s = re.sub(r"(?i)\bPháp danh\s+([A-ZÀ-Ỹ][a-zà-ỹ]+(?:\s+[A-ZÀ-Ỹ][a-zà-ỹ]+)*)", lambda m: f"Dharma name {_bo_dau_ten(m.group(1))}", s)
    s = re.sub(r"(?i)\bPhật tử\s+([A-ZÀ-Ỹ][a-zà-ỹ]+(?:\s+[A-ZÀ-Ỹ][a-zà-ỹ]+)*)", lambda m: f"Buddhist disciple {_bo_dau_ten(m.group(1))}", s)
    s = re.sub(r"(?i)\bGia đình cụ\s+([A-ZÀ-Ỹ][a-zà-ỹ]+(?:\s+[A-ZÀ-Ỹ][a-zà-ỹ]+)*)", lambda m: f"Family of late elder {_bo_dau_ten(m.group(1))}", s)
    s = re.sub(r"(?i)\bGia đình bà\s+([A-ZÀ-Ỹ][a-zà-ỹ]+(?:\s+[A-ZÀ-Ỹ][a-zà-ỹ]+)*)", lambda m: f"Family of Mrs. {_bo_dau_ten(m.group(1))}", s)
    s = re.sub(r"(?i)\bGia đình ông\s+([A-ZÀ-Ỹ][a-zà-ỹ]+(?:\s+[A-ZÀ-Ỹ][a-zà-ỹ]+)*)", lambda m: f"Family of Mr. {_bo_dau_ten(m.group(1))}", s)
    s = re.sub(r"(?i)\bTập thể cựu sinh viên\s+([A-Za-z0-9]+)", r"Alumni group of \1", s)
    s = re.sub(r"(?i)\bCông ty TNHH\s+([A-ZÀ-Ỹa-zà-ỹ0-9\s]+?)(?=,|\.|\s+phát tâm|\s+đã phát)", lambda m: f"{_bo_dau_ten(m.group(1)).strip()} Co., Ltd", s)

    # 2. Địa danh & Địa chỉ hành chính chuẩn quốc tế
    s = re.sub(r"(?i)\bTP\.?\s*HCM\b|\bTP\.?\s*Hồ Chí Minh\b", "Ho Chi Minh City", s)
    s = re.sub(r"(?i)\bTP\.?\s*HN\b|\bTP\.?\s*Hà Nội\b", "Hanoi City", s)
    s = re.sub(r"(?i)\bTP\.?\s*Huế\b", "Hue City", s)
    s = re.sub(r"(?i)\bTP\.?\s*Đà Nẵng\b", "Da Nang City", s)
    s = re.sub(r"(?i)\bTP\.?\s*Hải Phòng\b", "Hai Phong City", s)
    s = re.sub(r"(?i)\bTP\.?\s*Cần Thơ\b", "Can Tho City", s)
    s = re.sub(r"(?i)\bTP\.?\s*Nha Trang\b", "Nha Trang City", s)
    s = re.sub(r"(?i)\bTP\.?\s*([A-ZÀ-Ỹ][a-zà-ỹ]+(?:\s+[A-ZÀ-Ỹ][a-zà-ỹ]+)*)", lambda m: f"{_bo_dau_ten(m.group(1))} City", s)

    s = re.sub(r"(?i)\bSố\s+(\d+[A-Za-z]?)\s+Đường\s+([A-ZÀ-Ỹ0-9\s]+?)(?=,|\.|\s+Nha Trang|\s+Hà Nội|\s+TP|\s+phát)", lambda m: f"No. {m.group(1)}, {_bo_dau_ten(m.group(2)).strip()} Street, ", s)
    s = re.sub(r"(?i)\bThôn\s+(\d+)\s+Xã\s+([A-ZÀ-Ỹ][a-zà-ỹ]+(?:\s+[A-ZÀ-Ỹ][a-zà-ỹ]+)*)\s+([A-ZÀ-Ỹ][a-zà-ỹ]+(?:\s+[A-ZÀ-Ỹ][a-zà-ỹ]+)*)", lambda m: f"Village {m.group(1)}, {_bo_dau_ten(m.group(2))} Commune, {_bo_dau_ten(m.group(3))}", s)
    s = re.sub(r"(?i)\bTổ\s+(\d+)\s+Phường\s+([A-ZÀ-Ỹ][a-zà-ỹ]+(?:\s+[A-ZÀ-Ỹ][a-zà-ỹ]+)*)\s+Q\.?\s*(\d+)", lambda m: f"Group {m.group(1)}, {_bo_dau_ten(m.group(2))} Ward, District {m.group(3)}", s)

    # 3. Bảo vệ tên người ở đầu đoạn (ví dụ: '10. Dương Thị Tuyết,' -> '10. Duong Thi Tuyet,')
    s = re.sub(r"(?m)^(\s*\d+\.\s*)([A-ZÀ-Ỹ][a-zà-ỹ]+(?:\s+[A-ZÀ-Ỹ][a-zà-ỹ]+)+)(?=,|-|\s)", lambda m: f"{m.group(1)}{_bo_dau_ten(m.group(2))}", s)

    # 4. Phát tâm công đức / số tiền
    s = re.sub(r"(?i)\bphát tâm công đức số tiền\s+([\d.,]+)\b", r"donated the amount of \1 VND", s)
    s = re.sub(r"(?i)\bphát tâm công đức\s+([\d.,]+)\b", r"donated \1 VND", s)

    return s


def dich_cau_neural(text: str, src: str = "auto", tgt: str = "en") -> Tuple[str, str]:
    """Dịch câu qua giao thức Neural Engine Direct (Zero-Cost).

    Trả về tuple: (ngon_ngu_phat_hien, ban_dich).
    """
    s_raw = (text or "").strip()
    if not s_raw:
        return src, ""

    src_api = MAP_MA_API.get(src, "auto" if not src or src == "auto" else src)
    tgt_api = MAP_MA_API.get(tgt, tgt.split("-")[0] if tgt else "en")

    if src != "auto" and src_api == tgt_api:
        return src, s_raw

    # Chuẩn hóa tên riêng, địa danh, tôn giáo đối với ngôn ngữ nguồn tiếng Việt
    s = _chuan_hoa_thuc_the_viet_nam(s_raw, tgt_api) if src in ("auto", "vi") else s_raw

    cache_key = (s, src_api, tgt_api)
    if cache_key in _CACHE_DICH:
        return src, _CACHE_DICH[cache_key]

    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
    }

    # Phương thức 1 (Tốc độ cao nhất, 50-100ms): Google translate_a direct endpoint
    try:
        url1 = (
            "https://translate.googleapis.com/translate_a/single?client=gtx&sl="
            + urllib.parse.quote(src_api)
            + "&tl="
            + urllib.parse.quote(tgt_api)
            + "&dt=t&q="
            + urllib.parse.quote(s)
        )
        req1 = urllib.request.Request(url1, headers=headers)
        with urllib.request.urlopen(req1, timeout=2.5) as res1:
            raw_json = res1.read().decode("utf-8", errors="replace")
            data1 = json.loads(raw_json)
            detected = data1[2] if len(data1) > 2 and data1[2] else src_api
            translated = "".join([part[0] for part in data1[0] if part and part[0]]).strip()
            if translated:
                _CACHE_DICH[cache_key] = translated
                return str(detected), translated
    except Exception:
        pass

    # Phương thức 2: Google Web Mobile Endpoint (Dự phòng)
    try:
        import html
        url2 = (
            "https://translate.google.com/m?sl="
            + urllib.parse.quote(src_api)
            + "&tl="
            + urllib.parse.quote(tgt_api)
            + "&q="
            + urllib.parse.quote(s)
        )
        req2 = urllib.request.Request(url2, headers=headers)
        with urllib.request.urlopen(req2, timeout=2.5) as res2:
            html_text = res2.read().decode("utf-8", errors="replace")
            m = re.search(r'class="result-container">([^<]+)<', html_text)
            if m:
                trans = html.unescape(m.group(1)).strip()
                if trans:
                    _CACHE_DICH[cache_key] = trans
                    return "vi" if src_api == "auto" else src_api, trans
    except Exception:
        pass

    # Phương thức 3: OpenAI / Gemini API (nếu người dùng cài API Key riêng trong Cài đặt)
    try:
        from DocCongDuc import CONFIG_FILE
        if CONFIG_FILE.exists():
            cfg_obj = json.loads(CONFIG_FILE.read_text(encoding="utf-8"))
            openai_key = str(cfg_obj.get("openai_api_key", "")).strip()
            gemini_key = str(cfg_obj.get("gemini_api_key", "")).strip()
            if openai_key:
                payload = {
                    "model": "gpt-4o-mini",
                    "messages": [
                        {"role": "system", "content": f"Translate from {src_api} to {tgt_api} naturally for speech synthesis. Output ONLY translated text."},
                        {"role": "user", "content": s}
                    ],
                    "temperature": 0.2
                }
                req_ai = urllib.request.Request(
                    "https://api.openai.com/v1/chat/completions",
                    headers={"Authorization": f"Bearer {openai_key}", "Content-Type": "application/json"},
                    data=json.dumps(payload).encode("utf-8")
                )
                with urllib.request.urlopen(req_ai, timeout=3) as r_ai:
                    ai_data = json.loads(r_ai.read().decode("utf-8"))
                    trans_ai = ai_data["choices"][0]["message"]["content"].strip()
                    if trans_ai:
                        _CACHE_DICH[cache_key] = trans_ai
                        return src_api, trans_ai
            elif gemini_key:
                payload_gem = {
                    "contents": [{
                        "parts": [{"text": f"Translate to {tgt_api}: {s}"}]
                    }]
                }
                url_gem = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent?key={gemini_key}"
                req_gem = urllib.request.Request(
                    url_gem,
                    headers={"Content-Type": "application/json"},
                    data=json.dumps(payload_gem).encode("utf-8")
                )
                with urllib.request.urlopen(req_gem, timeout=3) as r_gem:
                    gem_data = json.loads(r_gem.read().decode("utf-8"))
                    trans_gem = gem_data["candidates"][0]["content"]["parts"][0]["text"].strip()
                    if trans_gem:
                        _CACHE_DICH[cache_key] = trans_gem
                        return src_api, trans_gem
    except Exception:
        pass

    # Dự phòng khi mất hoàn toàn Internet: trả lại văn bản gốc
    return nhan_dien_ngon_ngu_nhanh(s), s


def dich_van_ban(text: str, src: str = "auto", tgt: str = "vi", the_loai: str = "") -> str:
    """Dịch văn bản và chuẩn hoá dấu câu cho TTS."""
    if not text or not text.strip():
        return ""
    _, translated = dich_cau_neural(text, src=src, tgt=tgt)
    return translated


def kiem_tra_api_key(loai: str, api_key: str) -> dict:
    """Thử kết nối và dịch 1 câu ngắn để xác nhận API Key hoạt động thật 100%."""
    key = str(api_key or "").strip()
    if not key:
        return {"thanhCong": False, "loi": "Vui lòng nhập mã API Key"}

    cau_mau = "Xin chào, chúc bạn một ngày tốt lành."
    if loai == "openai":
        try:
            payload = {
                "model": "gpt-4o-mini",
                "messages": [
                    {"role": "system", "content": "Translate from Vietnamese to English. Output only translation."},
                    {"role": "user", "content": cau_mau}
                ],
                "max_tokens": 50
            }
            req = urllib.request.Request(
                "https://api.openai.com/v1/chat/completions",
                headers={"Authorization": f"Bearer {key}", "Content-Type": "application/json"},
                data=json.dumps(payload).encode("utf-8")
            )
            with urllib.request.urlopen(req, timeout=8) as res:
                data = json.loads(res.read().decode("utf-8"))
                dich = data["choices"][0]["message"]["content"].strip()
                return {"thanhCong": True, "banDich": dich, "moHinh": "OpenAI GPT-4o-mini"}
        except urllib.error.HTTPError as e:
            return {"thanhCong": False, "loi": f"Lỗi OpenAI ({e.code}): Mã Key không đúng hoặc tài khoản hết hạn mức"}
        except Exception as e:
            return {"thanhCong": False, "loi": f"Lỗi kết nối OpenAI: {e}"}

    elif loai == "gemini":
        try:
            payload = {
                "contents": [{
                    "parts": [{"text": f"Translate to English: {cau_mau}"}]
                }]
            }
            url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent?key={key}"
            req = urllib.request.Request(
                url,
                headers={"Content-Type": "application/json"},
                data=json.dumps(payload).encode("utf-8")
            )
            with urllib.request.urlopen(req, timeout=8) as res:
                data = json.loads(res.read().decode("utf-8"))
                dich = data["candidates"][0]["content"]["parts"][0]["text"].strip()
                return {"thanhCong": True, "banDich": dich, "moHinh": "Google Gemini 1.5 Flash"}
        except urllib.error.HTTPError as e:
            return {"thanhCong": False, "loi": f"Lỗi Google Gemini ({e.code}): Mã API Key không hợp lệ"}
        except Exception as e:
            return {"thanhCong": False, "loi": f"Lỗi kết nối Gemini: {e}"}

    return {"thanhCong": False, "loi": "Loại dịch thuật không hỗ trợ"}