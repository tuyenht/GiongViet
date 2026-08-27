# -*- coding: utf-8 -*-
"""Phát thử một giọng.

Tách riêng vì nghe thử và vòng đọc chính là hai nguồn phát âm thanh độc lập.
Để chúng tự do chạy song song thì nhiều giọng cùng nói một lúc - đo thật trên
máy: bấm "Nghe thử" ba lần trong lúc đang đọc là có 4 tiến trình ffplay cùng
chạy. Ở đây mỗi lần nghe thử được cấp một SỐ PHIÊN; bấm lần mới thì lần cũ bị
vô hiệu và tắt tiếng ngay, y như cách bo_doc.py giữ cho chỉ một luồng đọc sống.
"""

import threading

import DocCongDuc as engine

from . import nhat_ky

# Mỗi phong cách một câu riêng: nghe thử là để chọn giọng cho ĐÚNG VIỆC, đọc
# chung một câu cho cả ba thì không nghe ra khác biệt giữa chúng. Nội dung để
# trung tính, dùng được ở mọi nơi chứ không gắn riêng ngữ cảnh nào.
CAU_MAU_THEO_PHONG_CACH = {
    "tu_nhien": "Xin chào, đây là giọng đọc bạn vừa chọn. Giọng này đọc "
                "thong thả, rõ ràng và dễ nghe.",
    "tin_tuc": "Kính chào quý vị. Sau đây là bản tin tổng hợp trong ngày, "
               "kính mời quý vị cùng theo dõi.",
    "doc_truyen": "Ngày xửa ngày xưa, bên một dòng sông nhỏ, có hai ông bà "
                  "sống với nhau đã mấy chục năm trời.",
}
CAU_MAU_CHUNG = "Xin chào, đây là giọng đọc bạn vừa chọn."

CAU_MAU_QUOC_TE = {
    "vi": "Xin chào, đây là giọng đọc bạn vừa chọn.",
    "en": "Hello! This is a preview of the voice you selected.",
    "th": "สวัสดีครับ นี่คือเสียงตัวอย่างที่คุณเลือก",
    "ja": "こんにちは、こちらは選択された音声のプレビューです。",
    "ko": "안녕하세요, 선택하신 음성의 미리듣기입니다.",
    "zh": "您好，这是您选择的语音试听。",
    "yue": "你好，呢個係你選擇嘅語音試聽。",
    "fr": "Bonjour, ceci est un aperçu de la voix sélectionnée.",
    "de": "Hallo, dies ist eine Hörprobe der ausgewählten Stimme.",
    "es": "Hola, esta es una vista previa de la voz seleccionada.",
    "ru": "Здравствуйте, это образец выбранного вами голоса.",
    "it": "Ciao, questa è un'anteprima della voce selezionata.",
    "pt": "Olá, esta é uma prévia da voz selecionada.",
    "id": "Halo, ini adalah contoh suara yang Anda pilih.",
    "lo": "ສະບາຍດີ, ນີ້ແມ່ນສຽງຕົວຢ່າງທີ່ທ່ານເລືອກ.",
    "km": "សួស្តី នេះគឺជាគំរូសំឡេងដែលអ្នកបានជ្រើសរើស។",
    "my": "မင်္ဂလာပါ၊ ဤသည်မှာ သင်ရွေးချယ်ထားသော အသံနမူနာဖြစ်ပါသည်။",
    "ar": "مرحبًا، هذا نموذج للصوت الذي قمت باختياره.",
    "hi": "नमस्ते, यह आपके द्वारा चुनी गई आवाज़ का नमूना है।",
}


def cau_nghe_thu(cfg: dict, ma_giong: str = "") -> str:
    """Câu đọc thử hợp với phong cách hoặc ngôn ngữ bản xứ của giọng đang chọn."""
    g_id = str(ma_giong or cfg.get("vieneu_voice_id", "")).lower()
    
    # 1. Nếu là giọng quốc tế Microsoft (vd: th-TH, ja-JP, en-US...) -> Đọc câu bản xứ của tiếng đó
    for code, mau in CAU_MAU_QUOC_TE.items():
        if g_id.startswith(f"{code}-") or f"-{code}-" in g_id:
            return mau

    # 2. Nếu là giọng Việt Nam -> Dùng câu theo phong cách
    ten = cfg.get("phong_cach", "")
    style = engine.PHONG_CACH.get(ten, {}).get("style", "")
    return CAU_MAU_THEO_PHONG_CACH.get(style, CAU_MAU_CHUNG)


class BoNgheThu:
    def __init__(self, bao_xong, bao_loi):
        self._xong = bao_xong
        self._loi = bao_loi
        self._phien = 0
        self._speaker = None

    def phat(self, cfg: dict, ma_giong: str = "", cau: str = "", loc: str = ""):
        """`cau` rỗng thì đọc câu mẫu hợp phong cách, như cũ.

        Truyền câu vào để nghe thử MỘT NỘI DUNG CỤ THỂ - màn Từ điển phát âm
        cần nghe đúng cách đọc vừa gõ trước khi lưu, chứ nghe câu mẫu thì
        chẳng biết mình gõ đúng chưa.

        `loc` là chuỗi -af theo ba thanh chỉnh của hồ sơ. Nghe thử phải nghe
        đúng thứ sẽ phát ra lúc đọc thật, không thì chỉnh xong nghe thử thấy y
        như cũ, người dùng tưởng thanh trượt hỏng.
        """
        self.dung()
        self._phien += 1
        threading.Thread(target=self._chay,
                         args=(dict(cfg), ma_giong, self._phien, str(cau or ""),
                               str(loc or "")),
                         daemon=True).start()

    def dung(self):
        """Vô hiệu hoá lần nghe thử đang chạy và tắt tiếng ngay."""
        self._phien += 1
        speaker = self._speaker
        if speaker is not None:
            speaker.stop()

    def tat(self):
        self.dung()
        speaker = self._speaker
        if speaker is not None:
            speaker.shutdown()

    def _chay(self, cfg, ma_giong, phien, cau="", loc=""):
        if ma_giong:
            cfg["vieneu_voice_id"] = ma_giong
        speaker = engine.Speaker(cfg)
        self._speaker = speaker
        try:
            noi_dung = cau.strip() or cau_nghe_thu(cfg, ma_giong)
            # Khoá cache đổi theo nội dung: dùng chung một khoá thì nghe thử
            # câu thứ hai lại phát ra câu thứ nhất đã tổng hợp trước đó.
            audio, dinh_dang = speaker.get_audio(f"nghe_thu:{hash(noi_dung)}",
                                                 noi_dung)
            # Tổng hợp xong mới quay lại đây, lúc này người dùng có thể đã bấm
            # nghe thử giọng khác - phát nữa là chồng tiếng.
            if phien != self._phien:
                return
            speaker.play(audio, threading.Event(), dinh_dang, loc)
        except Exception as e:
            nhat_ky.ghi_loi(f"nghe thử giọng {ma_giong or '(mặc định)'}", e)
            if phien == self._phien:
                self._loi(str(e))
        finally:
            speaker.shutdown()
            if self._speaker is speaker:
                self._speaker = None
            engine.giai_phong_bo_nho_he_thong()
            if phien == self._phien:
                self._xong(ma_giong)
