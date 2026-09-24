# -*- coding: utf-8 -*-
import asyncio
import io
import re
import tempfile
from pathlib import Path
from typing import Optional, Tuple
import edge_tts

# Danh sách đầy đủ toàn bộ giọng quốc tế chất lượng cao theo từng quốc gia (100% hợp lệ trên Edge TTS)
DS_GIONG_QUOC_TE_CHI_TIET = [
    # Tiếng Việt (Bản địa)
    {"id": "vi-VN-HoaiMyNeural", "ten": "Hoài My", "gioi": "Nữ", "ngon_ngu": "vi", "vung": "Miền Bắc"},
    {"id": "vi-VN-NamMinhNeural", "ten": "Nam Minh", "gioi": "Nam", "ngon_ngu": "vi", "vung": "Miền Bắc"},

    # Tiếng Trung (China, Hong Kong, Taiwan)
    {"id": "zh-CN-XiaoxiaoNeural", "ten": "Xiaoxiao", "gioi": "Nữ", "ngon_ngu": "zh", "vung": "Phổ thông"},
    {"id": "zh-CN-XiaoyiNeural", "ten": "Xiaoyi", "gioi": "Nữ", "ngon_ngu": "zh", "vung": "Phổ thông"},
    {"id": "zh-CN-liaoning-XiaobeiNeural", "ten": "Xiaobei", "gioi": "Nữ", "ngon_ngu": "zh", "vung": "Liêu Ninh"},
    {"id": "zh-CN-shaanxi-XiaoniNeural", "ten": "Xiaoni", "gioi": "Nữ", "ngon_ngu": "zh", "vung": "Thiểm Tây"},
    {"id": "zh-CN-YunjianNeural", "ten": "Yunjian", "gioi": "Nam", "ngon_ngu": "zh", "vung": "Phổ thông"},
    {"id": "zh-CN-YunxiNeural", "ten": "Yunxi", "gioi": "Nam", "ngon_ngu": "zh", "vung": "Phổ thông"},
    {"id": "zh-CN-YunxiaNeural", "ten": "Yunxia", "gioi": "Nam", "ngon_ngu": "zh", "vung": "Phổ thông"},
    {"id": "zh-CN-YunyangNeural", "ten": "Yunyang", "gioi": "Nam", "ngon_ngu": "zh", "vung": "Phổ thông"},
    {"id": "zh-HK-HiuGaaiNeural", "ten": "HiuGaai", "gioi": "Nữ", "ngon_ngu": "yue", "vung": "Quảng Đông (HK)"},
    {"id": "zh-HK-HiuMaanNeural", "ten": "HiuMaan", "gioi": "Nữ", "ngon_ngu": "yue", "vung": "Quảng Đông (HK)"},
    {"id": "zh-HK-WanLungNeural", "ten": "WanLung", "gioi": "Nam", "ngon_ngu": "yue", "vung": "Quảng Đông (HK)"},
    {"id": "zh-TW-HsiaoChenNeural", "ten": "HsiaoChen", "gioi": "Nữ", "ngon_ngu": "zh-tw", "vung": "Đài Loan"},
    {"id": "zh-TW-HsiaoYuNeural", "ten": "HsiaoYu", "gioi": "Nữ", "ngon_ngu": "zh-tw", "vung": "Đài Loan"},
    {"id": "zh-TW-YunJheNeural", "ten": "YunJhe", "gioi": "Nam", "ngon_ngu": "zh-tw", "vung": "Đài Loan"},

    # Tiếng Anh (Mỹ, Anh, Úc)
    {"id": "en-US-JennyNeural", "ten": "Jenny", "gioi": "Nữ", "ngon_ngu": "en", "vung": "Mỹ (US)"},
    {"id": "en-US-GuyNeural", "ten": "Guy", "gioi": "Nam", "ngon_ngu": "en", "vung": "Mỹ (US)"},
    {"id": "en-US-AriaNeural", "ten": "Aria", "gioi": "Nữ", "ngon_ngu": "en", "vung": "Mỹ (US)"},
    {"id": "en-US-ChristopherNeural", "ten": "Christopher", "gioi": "Nam", "ngon_ngu": "en", "vung": "Mỹ (US)"},
    {"id": "en-US-EricNeural", "ten": "Eric", "gioi": "Nam", "ngon_ngu": "en", "vung": "Mỹ (US)"},
    {"id": "en-US-MichelleNeural", "ten": "Michelle", "gioi": "Nữ", "ngon_ngu": "en", "vung": "Mỹ (US)"},
    {"id": "en-GB-SoniaNeural", "ten": "Sonia", "gioi": "Nữ", "ngon_ngu": "en-gb", "vung": "Anh (UK)"},
    {"id": "en-GB-RyanNeural", "ten": "Ryan", "gioi": "Nam", "ngon_ngu": "en-gb", "vung": "Anh (UK)"},
    {"id": "en-GB-LibbyNeural", "ten": "Libby", "gioi": "Nữ", "ngon_ngu": "en-gb", "vung": "Anh (UK)"},
    {"id": "en-AU-NatashaNeural", "ten": "Natasha", "gioi": "Nữ", "ngon_ngu": "en", "vung": "Úc (AU)"},
    {"id": "en-AU-WilliamMultilingualNeural", "ten": "William", "gioi": "Nam", "ngon_ngu": "en", "vung": "Úc (AU)"},

    # Tiếng Nhật
    {"id": "ja-JP-NanamiNeural", "ten": "Nanami", "gioi": "Nữ", "ngon_ngu": "ja", "vung": "Nhật Bản"},
    {"id": "ja-JP-KeitaNeural", "ten": "Keita", "gioi": "Nam", "ngon_ngu": "ja", "vung": "Nhật Bản"},

    # Tiếng Hàn
    {"id": "ko-KR-SunHiNeural", "ten": "Sun-Hi", "gioi": "Nữ", "ngon_ngu": "ko", "vung": "Hàn Quốc"},
    {"id": "ko-KR-InJoonNeural", "ten": "In-Joon", "gioi": "Nam", "ngon_ngu": "ko", "vung": "Hàn Quốc"},

    # Tiếng Pháp
    {"id": "fr-FR-DeniseNeural", "ten": "Denise", "gioi": "Nữ", "ngon_ngu": "fr", "vung": "Pháp"},
    {"id": "fr-FR-HenriNeural", "ten": "Henri", "gioi": "Nam", "ngon_ngu": "fr", "vung": "Pháp"},
    {"id": "fr-FR-EloiseNeural", "ten": "Eloise", "gioi": "Nữ", "ngon_ngu": "fr", "vung": "Pháp"},

    # Tiếng Đức
    {"id": "de-DE-KatjaNeural", "ten": "Katja", "gioi": "Nữ", "ngon_ngu": "de", "vung": "Đức"},
    {"id": "de-DE-ConradNeural", "ten": "Conrad", "gioi": "Nam", "ngon_ngu": "de", "vung": "Đức"},
    {"id": "de-DE-AmalaNeural", "ten": "Amala", "gioi": "Nữ", "ngon_ngu": "de", "vung": "Đức"},

    # Tiếng Tây Ban Nha
    {"id": "es-ES-ElviraNeural", "ten": "Elvira", "gioi": "Nữ", "ngon_ngu": "es", "vung": "Tây Ban Nha"},
    {"id": "es-ES-AlvaroNeural", "ten": "Alvaro", "gioi": "Nam", "ngon_ngu": "es", "vung": "Tây Ban Nha"},

    # Tiếng Ý
    {"id": "it-IT-ElsaNeural", "ten": "Elsa", "gioi": "Nữ", "ngon_ngu": "it", "vung": "Ý"},
    {"id": "it-IT-DiegoNeural", "ten": "Diego", "gioi": "Nam", "ngon_ngu": "it", "vung": "Ý"},
    {"id": "it-IT-IsabellaNeural", "ten": "Isabella", "gioi": "Nữ", "ngon_ngu": "it", "vung": "Ý"},

    # Tiếng Nga
    {"id": "ru-RU-SvetlanaNeural", "ten": "Svetlana", "gioi": "Nữ", "ngon_ngu": "ru", "vung": "Nga"},
    {"id": "ru-RU-DmitryNeural", "ten": "Dmitry", "gioi": "Nam", "ngon_ngu": "ru", "vung": "Nga"},

    # Tiếng Bồ Đào Nha
    {"id": "pt-BR-FranciscaNeural", "ten": "Francisca", "gioi": "Nữ", "ngon_ngu": "pt", "vung": "Brazil"},
    {"id": "pt-BR-AntonioNeural", "ten": "Antonio", "gioi": "Nam", "ngon_ngu": "pt", "vung": "Brazil"},

    # Đông Nam Á (ASEAN)
    {"id": "th-TH-PremwadeeNeural", "ten": "Premwadee", "gioi": "Nữ", "ngon_ngu": "th", "vung": "Thái Lan"},
    {"id": "th-TH-NiwatNeural", "ten": "Niwat", "gioi": "Nam", "ngon_ngu": "th", "vung": "Thái Lan"},
    {"id": "lo-LA-KeomanyNeural", "ten": "Keomany", "gioi": "Nữ", "ngon_ngu": "lo", "vung": "Lào"},
    {"id": "lo-LA-ChanthavongNeural", "ten": "Chanthavong", "gioi": "Nam", "ngon_ngu": "lo", "vung": "Lào"},
    {"id": "id-ID-GadisNeural", "ten": "Gadis", "gioi": "Nữ", "ngon_ngu": "id", "vung": "Indonesia"},
    {"id": "id-ID-ArdiNeural", "ten": "Ardi", "gioi": "Nam", "ngon_ngu": "id", "vung": "Indonesia"},
    {"id": "ms-MY-YasminNeural", "ten": "Yasmin", "gioi": "Nữ", "ngon_ngu": "ms", "vung": "Malaysia"},
    {"id": "ms-MY-OsmanNeural", "ten": "Osman", "gioi": "Nam", "ngon_ngu": "ms", "vung": "Malaysia"},
    {"id": "fil-PH-BlessicaNeural", "ten": "Blessica", "gioi": "Nữ", "ngon_ngu": "fil", "vung": "Philippines"},
    {"id": "fil-PH-AngeloNeural", "ten": "Angelo", "gioi": "Nam", "ngon_ngu": "fil", "vung": "Philippines"},
    {"id": "km-KH-SreymomNeural", "ten": "Sreymom", "gioi": "Nữ", "ngon_ngu": "km", "vung": "Campuchia"},
    {"id": "km-KH-PisethNeural", "ten": "Piseth", "gioi": "Nam", "ngon_ngu": "km", "vung": "Campuchia"},
    {"id": "my-MM-NilarNeural", "ten": "Nilar", "gioi": "Nữ", "ngon_ngu": "my", "vung": "Myanmar"},
    {"id": "my-MM-ThihaNeural", "ten": "Thiha", "gioi": "Nam", "ngon_ngu": "my", "vung": "Myanmar"},

    # Các nước khác
    {"id": "nl-NL-FennaNeural", "ten": "Fenna", "gioi": "Nữ", "ngon_ngu": "nl", "vung": "Hà Lan"},
    {"id": "nl-NL-MaartenNeural", "ten": "Maarten", "gioi": "Nam", "ngon_ngu": "nl", "vung": "Hà Lan"},
    {"id": "ar-SA-ZariyahNeural", "ten": "Zariyah", "gioi": "Nữ", "ngon_ngu": "ar", "vung": "Ả Rập"},
    {"id": "ar-SA-HamedNeural", "ten": "Hamed", "gioi": "Nam", "ngon_ngu": "ar", "vung": "Ả Rập"},
    {"id": "hi-IN-SwaraNeural", "ten": "Swara", "gioi": "Nữ", "ngon_ngu": "hi", "vung": "Ấn Độ"},
    {"id": "hi-IN-MadhurNeural", "ten": "Madhur", "gioi": "Nam", "ngon_ngu": "hi", "vung": "Ấn Độ"},
    {"id": "bn-BD-NabanitaNeural", "ten": "Nabanita", "gioi": "Nữ", "ngon_ngu": "bn", "vung": "Bangladesh"},
    {"id": "bn-BD-PradeepNeural", "ten": "Pradeep", "gioi": "Nam", "ngon_ngu": "bn", "vung": "Bangladesh"},
    {"id": "ur-PK-UzmaNeural", "ten": "Uzma", "gioi": "Nữ", "ngon_ngu": "ur", "vung": "Pakistan"},
    {"id": "ur-PK-AsadNeural", "ten": "Asad", "gioi": "Nam", "ngon_ngu": "ur", "vung": "Pakistan"},
    {"id": "ta-IN-PallaviNeural", "ten": "Pallavi", "gioi": "Nữ", "ngon_ngu": "ta", "vung": "Ấn Độ"},
    {"id": "ta-IN-ValluvarNeural", "ten": "Valluvar", "gioi": "Nam", "ngon_ngu": "ta", "vung": "Ấn Độ"},
    {"id": "mr-IN-AarohiNeural", "ten": "Aarohi", "gioi": "Nữ", "ngon_ngu": "mr", "vung": "Ấn Độ"},
    {"id": "mr-IN-ManoharNeural", "ten": "Manohar", "gioi": "Nam", "ngon_ngu": "mr", "vung": "Ấn Độ"},
    {"id": "tr-TR-EmelNeural", "ten": "Emel", "gioi": "Nữ", "ngon_ngu": "tr", "vung": "Thổ Nhĩ Kỳ"},
    {"id": "tr-TR-AhmetNeural", "ten": "Ahmet", "gioi": "Nam", "ngon_ngu": "tr", "vung": "Thổ Nhĩ Kỳ"},
]


GIONG_BAN_XU_28 = {}
for g in DS_GIONG_QUOC_TE_CHI_TIET:
    nn = g["ngon_ngu"]
    if nn not in GIONG_BAN_XU_28:
        GIONG_BAN_XU_28[nn] = {}
    if g["gioi"] == "Nữ" and "nu" not in GIONG_BAN_XU_28[nn]:
        GIONG_BAN_XU_28[nn]["nu"] = g["id"]
    elif g["gioi"] == "Nam" and "nam" not in GIONG_BAN_XU_28[nn]:
        GIONG_BAN_XU_28[nn]["nam"] = g["id"]

for nn, d in GIONG_BAN_XU_28.items():
    if "nu" not in d and "nam" in d:
        d["nu"] = d["nam"]
    elif "nam" not in d and "nu" in d:
        d["nam"] = d["nu"]


def doan_gioi_tinh(voice_hint: str) -> str:
    """Nhận diện giới tính Nam/Nữ của giọng đọc đang chọn để đồng bộ sang giọng bản xứ quốc tế."""
    import unicodedata
    s = str(voice_hint or "").lower().strip()
    s_khong_dau = "".join(c for c in unicodedata.normalize("NFD", s) if unicodedata.category(c) != "Mn").replace("đ", "d").replace("_", " ").replace("-", " ")

    # 1. Tra cứu trực tiếp danh sách giọng riêng (cloned voices)
    try:
        from DocCongDuc import doc_ds_giong_rieng
        for g in doc_ds_giong_rieng():
            g_id = str(g.get("id", "")).lower()
            g_ten = str(g.get("ten", "")).lower()
            g_ten_kd = "".join(c for c in unicodedata.normalize("NFD", g_ten) if unicodedata.category(c) != "Mn").replace("đ", "d")
            if s in (g_id, g_ten) or s_khong_dau in (g_id, g_ten_kd) or g_id in s:
                if any(k in g_ten_kd for k in ["ngan", "nam", "ong", "bac", "anh", "chu", "tuan", "vinh", "son", "tuyen", "duc", "binh", "triet", "tri", "adam", "long", "hung", "khoa", "bach"]):
                    return "nam"
                if any(k in g_ten_kd for k in ["nu", "ba", "co", "chi", "linh", "trang", "anh", "doan", "dung", "tran", "duyen", "thanh", "huyen", "ly", "thao", "huong"]):
                    return "nu"
                return "nam"
    except Exception:
        pass

    # 2. Danh sách từ khoá nhận diện giọng NAM chuẩn
    tu_khoa_nam = [
        "minh duc", "pham tuyen", "quang son", "anh khoa", "thanh binh", "duc hung",
        "van long", "xuan vinh", "thai son", "bac tuan", "minh triet", "duc tri",
        "viet bach", "ngan", "tuan", "vinh", "son", "tuyen", "duc", "binh",
        "triet", "tri", "adam", "khoa", "hung", "long", "bach",
        "nam", "male", "guy", "boy", "ong ", "anh ", "bac ", "chu "
    ]
    for k in tu_khoa_nam:
        if k in s_khong_dau or k in s:
            return "nam"

    # 3. Danh sách từ khoá nhận diện giọng NỮ
    tu_khoa_nu = [
        "ngoc linh", "truc ly", "doan trang", "mai anh", "thuc doan", "thuy dung",
        "ngoc tran", "my duyen", "quynh anh", "kim thanh", "ngoc huyen", "phuong thao",
        "linh", "ly", "trang", "doan", "dung", "tran", "duyen", "huyen", "thao",
        "nu", "female", "woman", "girl", "chi ", "co ", "ba ", "me "
    ]
    for k in tu_khoa_nu:
        if k in s_khong_dau or k in s:
            return "nu"

    if s in ("1", "3", "5", "7", "nam", "rieng_001") or s_khong_dau in ("1", "3", "5", "7", "nam", "rieng_001"):
        return "nam"
    return "nam"


def tong_hop_da_ngu_native(text: str, lang: str = "en", voice_hint: str = "",
                           khuech_dai: float = 1.0, ref_audio_path: str = None) -> bytes:
    s = (text or "").strip()
    if not s:
        return b""

    # Nếu đã truyền đích danh ID giọng Microsoft (vd: vi-VN-HoaiMyNeural, th-TH-NiwatNeural...)
    if voice_hint and ("Neural" in voice_hint or ("-" in voice_hint and len(voice_hint) > 8)):
        voice = voice_hint
    else:
        lang_code = lang.lower().split("-")[0] if "-" not in lang else lang.lower()
        gioi = doan_gioi_tinh(voice_hint)
        lang_voices = GIONG_BAN_XU_28.get(lang.lower(), GIONG_BAN_XU_28.get(lang_code, {"nu": "en-US-JennyNeural", "nam": "en-US-GuyNeural"}))
        if isinstance(lang_voices, dict):
            voice = lang_voices.get(gioi, lang_voices.get("nu"))
        else:
            voice = lang_voices

    pitch_arg, rate_arg = "+0Hz", "+0%"

    async def _chay_edge():
        communicate = edge_tts.Communicate(s, voice, pitch=pitch_arg, rate=rate_arg)
        buffer = bytearray()
        async for chunk in communicate.stream():
            if chunk["type"] == "audio":
                buffer.extend(chunk["data"])
        return bytes(buffer)

    raw_audio = b""
    try:
        raw_audio = asyncio.run(_chay_edge())
    except Exception:
        try:
            loop = asyncio.new_event_loop()
            raw_audio = loop.run_until_complete(_chay_edge())
            loop.close()
        except Exception:
            raw_audio = b""

    return _mp3_sang_wav(raw_audio)


def tong_hop_da_ngu_stream(text: str, lang: str = "en", voice_hint: str = "",
                           khuech_dai: float = 1.0, ref_audio_path: str = None):
    """Generator sinh PCM 16-bit 48kHz mono trực tiếp từ Microsoft Neural TTS theo thời gian thực (Streaming).
    100% trong trẻo, tự nhiên chuẩn bản xứ, không can thiệp méo tiếng.
    """
    s = (text or "").strip()
    if not s:
        return

    import os, subprocess, threading
    ff_bin = _tim_ffmpeg()
    creationflags = subprocess.CREATE_NO_WINDOW if os.name == "nt" else 0

    if voice_hint and ("Neural" in voice_hint or ("-" in voice_hint and len(voice_hint) > 8)):
        voice = voice_hint
    else:
        lang_code = lang.lower().split("-")[0] if "-" not in lang else lang.lower()
        gioi = doan_gioi_tinh(voice_hint)
        lang_voices = GIONG_BAN_XU_28.get(lang.lower(), GIONG_BAN_XU_28.get(lang_code, {"nu": "en-US-JennyNeural", "nam": "en-US-GuyNeural"}))
        if isinstance(lang_voices, dict):
            voice = lang_voices.get(gioi, lang_voices.get("nu"))
        else:
            voice = lang_voices

    pitch_arg, rate_arg = "+0Hz", "+0%"

    proc = subprocess.Popen(
        [ff_bin, "-hide_banner", "-loglevel", "error", "-f", "mp3", "-i", "pipe:0", "-f", "s16le", "-ar", "48000", "-ac", "1", "pipe:1"],
        stdin=subprocess.PIPE,
        stdout=subprocess.PIPE,
        stderr=subprocess.DEVNULL,
        creationflags=creationflags
    )

    stdin = getattr(proc, "stdin", None)

    def _feed():
        async def _run():
            try:
                comm = edge_tts.Communicate(s, voice, pitch=pitch_arg, rate=rate_arg)
                async for chunk in comm.stream():
                    if chunk["type"] == "audio":
                        if stdin and not stdin.closed:
                            try:
                                stdin.write(chunk["data"])
                                stdin.flush()
                            except (BrokenPipeError, OSError, ValueError):
                                break
            except Exception:
                pass
            finally:
                try:
                    if stdin and not stdin.closed:
                        stdin.close()
                except (BrokenPipeError, OSError, ValueError):
                    pass
        try:
            asyncio.run(_run())
        except Exception:
            try:
                loop = asyncio.new_event_loop()
                loop.run_until_complete(_run())
                loop.close()
            except Exception:
                pass

    threading.Thread(target=_feed, daemon=True).start()

    try:
        while True:
            data = proc.stdout.read(4096 * 2)
            if not data:
                break
            yield data
    finally:
        try:
            if proc.stdin and not proc.stdin.closed:
                try:
                    proc.stdin.close()
                except Exception:
                    pass
        except Exception:
            pass
        try:
            if proc.stdout and not proc.stdout.closed:
                try:
                    proc.stdout.close()
                except Exception:
                    pass
        except Exception:
            pass
        try:
            proc.wait(timeout=0.2)
        except Exception:
            try:
                proc.kill()
            except Exception:
                pass






_FFMPEG_BIN = None


def _tim_ffmpeg() -> str:
    global _FFMPEG_BIN
    if _FFMPEG_BIN:
        return _FFMPEG_BIN
    import shutil
    import DocCongDuc as engine
    candidates = [
        engine.BASE_DIR / "bin" / "ffmpeg" / "bin" / "ffmpeg.exe",
        engine.BASE_DIR / "bin" / "ffmpeg" / "ffmpeg.exe",
        engine.BASE_DIR / "ffmpeg" / "bin" / "ffmpeg.exe",
        engine.BASE_DIR / "GiongViet" / "bin" / "ffmpeg" / "bin" / "ffmpeg.exe",
    ]
    for c in candidates:
        if c.exists():
            _FFMPEG_BIN = str(c)
            return _FFMPEG_BIN
    sys_ff = shutil.which("ffmpeg")
    _FFMPEG_BIN = sys_ff if sys_ff else "ffmpeg"
    return _FFMPEG_BIN


def _mp3_sang_wav(mp3_bytes: bytes) -> bytes:
    if not mp3_bytes:
        return b""
    try:
        import os, subprocess
        ff_bin = _tim_ffmpeg()
        creationflags = subprocess.CREATE_NO_WINDOW if os.name == "nt" else 0
        proc = subprocess.Popen(
            [ff_bin, "-hide_banner", "-loglevel", "error", "-i", "pipe:0", "-f", "wav", "-ar", "48000", "-ac", "1", "pipe:1"],
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            creationflags=creationflags
        )
        wav_out, _ = proc.communicate(input=mp3_bytes, timeout=8)
        return wav_out if (wav_out and wav_out.startswith(b"RIFF")) else mp3_bytes
    except Exception:
        return mp3_bytes
