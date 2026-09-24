# -*- coding: utf-8 -*-
"""Nạp mô hình VieNeu-TTS ở luồng nền để cửa sổ hiện lên ngay.

Lần đầu chạy, engine có thể phải tải mô hình về (vài GB) - nếu chờ xong
mới vẽ giao diện thì người dùng tưởng máy treo.
"""

import sys
import threading

import DocCongDuc as engine

from . import nhat_ky


class BoNapMoHinh:
    def __init__(self, day_trang_thai):
        """day_trang_thai(dict) — hàm đẩy trạng thái sang giao diện."""
        self._day = day_trang_thai
        self.san_sang = False
        self.loi = ""

    def bat_dau(self):
        threading.Thread(target=self._chay, daemon=True).start()

    def trang_thai_ban_dau(self) -> dict:
        return {"trangThai": "kiem_tra", "tieuDe": "Đang kiểm tra mô hình…",
                "ghiChu": "", "phanTram": 0}

    @staticmethod
    def _huong_dan_cai() -> str:
        """KHÔNG dùng engine.huong_dan_cai_vieneu(): hàm đó viết cho bản
        DocCongDuc.exe cũ - bản ấy cố ý không kèm VieNeu và bảo người dùng
        "chạy py DocCongDuc.py", lại còn nhắc Edge TTS vốn đã bị gỡ khỏi
        chương trình. GiongDoc.exe thì có kèm sẵn bộ giọng, nên nếu thiếu là
        bản đóng gói hỏng chứ không phải người dùng làm sai.
        """
        if getattr(sys, "frozen", False):
            return ("Bản chương trình này lẽ ra đã kèm sẵn bộ giọng đọc AI "
                    "nhưng không tìm thấy.\n\n"
                    "Nghĩa là bản đóng gói bị thiếu tệp - không phải do máy "
                    "của bạn. Hãy báo lại cho người đã cài chương trình để họ "
                    "đóng gói lại.")
        return ("Máy chưa cài bộ giọng đọc AI.\n\n"
                "Cách cài: mở thư mục chương trình, bấm đúp vào tệp "
                "CaiDat.bat rồi làm theo hướng dẫn trên màn hình. Cài xong "
                "mở lại chương trình này.")

    def _bao(self, tieu_de, ghi_chu="", trang_thai="dang_tai", phan_tram=0):
        self._day({"model": {"trangThai": trang_thai, "tieuDe": tieu_de,
                             "ghiChu": ghi_chu, "phanTram": phan_tram}})

    def _chay(self):
        if not engine.vieneu_da_cai_dat():
            self.loi = self._huong_dan_cai()
            self._bao("Chưa có bộ giọng đọc AI",
                      "Xem hướng dẫn trong khung báo lỗi ở giữa màn hình.",
                      "loi")
            self._day({
                "state": "loi",
                "loi": {
                    "tieu_de": "Chưa có bộ giọng đọc AI",
                    "chi_tiet": self.loi,
                    "nut": [{"nhan": "Kiểm tra lại", "act": "thuLaiMoHinh"}],
                },
            })
            return

        # Bộ giọng đã nằm trên đĩa thì đây chỉ là mở tệp lên, không đụng mạng.
        # Nói "đang tải" làm người dùng tưởng máy đang tải mấy trăm MB.
        dang_tai_that = not engine.mo_hinh_da_du_tren_dia()
        if dang_tai_that:
            tieu_de = "Đang tải bộ giọng đọc về máy…"
            ghi_chu = "Chỉ lần đầu mới cần tải. Các lần sau mở là dùng ngay."
        else:
            tieu_de = "Đang mở bộ giọng đọc…"
            ghi_chu = "Bộ giọng có sẵn trong máy, không cần Internet."

        self._bao(tieu_de, ghi_chu)
        try:
            tts = engine.dam_bao_vieneu_san_sang(
                lambda msg: self._bao(tieu_de, str(msg)))
            self.san_sang = True
            self.loi = ""
            self._bao("Giọng Việt · Sẵn sàng",
                      "Động cơ giọng đọc chạy ngay trên máy, không cần Internet.",
                      "san_sang")


            # Khởi động nóng ONNX execution graph và active voice trong luồng nền để câu đầu tiên phát tức thì
            def _warmup():
                try:
                    cfg = engine.load_config()
                    active_voice = str(cfg.get("vieneu_voice_id", "") or "")
                    if active_voice and hasattr(tts, "_preset_voices") and active_voice in tts._preset_voices:
                        try:
                            tts.infer("Xin chào.", voice=active_voice, apply_watermark=False)
                        except Exception:
                            tts.infer("Xin chào.", apply_watermark=False)
                    else:
                        tts.infer("Xin chào.", apply_watermark=False)
                except Exception:
                    pass
                try:
                    engine.giai_phong_bo_nho_he_thong()
                except Exception:
                    pass

            threading.Thread(target=_warmup, daemon=True).start()
        except Exception as e:
            nhat_ky.ghi_loi("nạp mô hình VieNeu-TTS", e)
            self.loi = str(e)
            self._bao("Mô hình chưa tải được", self.loi[:200], "loi")
            self._day({
                "state": "loi",
                "loi": {
                    "tieu_de": "Không tải được mô hình giọng đọc",
                    "chi_tiet": self.loi,
                    "nut": [{"nhan": "Thử lại", "act": "thuLaiMoHinh"}],
                },
            })
            return
