# -*- coding: utf-8 -*-
"""Vòng đọc: chạy qua playlist, tổng hợp giọng và phát từng đoạn.

Giữ nguyên cách làm của DocApp._worker trong DocCongDuc.py (tổng hợp trước
đoạn kế tiếp để phát liền mạch), chỉ đổi phần báo trạng thái từ Tkinter sang
đẩy sang giao diện web.

Mỗi lần bắt đầu đọc được cấp một SỐ PHIÊN. Luồng đọc kiểm tra số phiên ở mọi
điểm dừng chân; số phiên đổi nghĩa là "có người khác thế chỗ rồi, thoát đi".
Chỉ dùng cờ dừng thôi thì không đủ: tổng hợp một câu có thể mất 40 giây, luồng
cũ còn đang kẹt trong đó thì join() đã hết hạn chờ, rồi phat() xoá cờ dừng làm
luồng cũ sống lại và chạy song song với luồng mới - hậu quả là hai tiến trình
ffplay cùng đọc chồng lên nhau.
"""

import io
import re
import threading
import time
import wave

import DocCongDuc as engine

from . import nhat_ky

# Thời gian chờ luồng đọc tự thoát. Không chờ lâu hơn vì luồng có thể đang kẹt
# giữa chừng tổng hợp một câu dài; số phiên đã đủ giữ cho nó vô hại.
CHO_DUNG_GIAY = 2.0


def _thoi_luong_wav(audio, text: str = "") -> float:
    """Số giây của khối WAV vừa tổng hợp. Nếu là streaming, ước tính từ độ dài ký tự và đặc trưng ngôn ngữ."""
    if not audio:
        return 0.0
    if not isinstance(audio, (bytes, bytearray)):
        s = (text or "").strip()
        if not s:
            return 0.5
        # Tiếng Nhật / Trung / Hàn / Thái / Lào: mật độ ký tự cao (1 ký tự ~ 1 âm tiết)
        if re.search(r"[\u3040-\u30ff\u4e00-\u9fa5\uac00-\ud7af\u0e00-\u0e7f\u0e80-\u0eff]", s):
            return max(0.8, len(s) / 4.8)
        return max(0.5, len(s) / 13.5)
    try:
        with wave.open(io.BytesIO(audio), "rb") as w:
            frames = w.getnframes()
            rate = float(w.getframerate() or 1)
            sampwidth = w.getsampwidth() or 2
            nchannels = w.getnchannels() or 1
            if frames > 10000000 or frames <= 0:
                raw_pcm_len = max(0, len(audio) - 44)
                return raw_pcm_len / (rate * sampwidth * nchannels)
            return frames / rate
    except (wave.Error, EOFError, OSError):
        return max(0.5, len(text) / 13.5) if text else 0.0


def _dam_bao_da_dich(seg: dict, cfg: dict) -> str:
    """Bảo đảm 100% đoạn đọc đã được dịch sang ngôn ngữ đích trước khi gửi sang TTS."""
    if not seg:
        return ""
    lang_tgt = str(cfg.get("ngonNgu") or "vi").strip().lower()
    if lang_tgt and lang_tgt != "vi":
        text_goc = seg.get("text_goc") or seg.get("text", "")
        # Nếu chưa dịch hoặc text vẫn trùng văn bản tiếng Việt gốc
        if not seg.get("_da_dich") or seg.get("text") == text_goc:
            try:
                from src.core import dich_thuat
                trans = dich_thuat.dich_van_ban(text_goc, src=cfg.get("ngonNguNguon", "auto"), tgt=lang_tgt)
                if trans:
                    seg["text"] = trans
                    seg["_da_dich"] = True
            except Exception:
                pass
    return seg.get("text", "")



class BoDoc:
    def __init__(self, day_trang_thai):
        self._day = day_trang_thai
        self.playlist = []
        self.index = 0
        # Chuỗi -af của ffplay cho ba thanh Tốc độ / Cao độ / Âm lượng. Rỗng
        # là tiếng đi thẳng từ mô hình ra loa, không qua lần dựng lại sóng nào
        # - đúng hành vi cũ. Giao diện mới đặt qua ApiMoi.moi_dat_chinh_am.
        self.loc_am = ""
        self.speaker = None
        self._stop = threading.Event()
        self._worker = None
        self._phien = 0

    # ------------------------------------------------------------ vòng đời

    def dat_playlist(self, playlist: list, cfg: dict):
        self.dung(giu_vi_tri=False)
        self.playlist = playlist
        self.index = 0
        if self.speaker is None:
            self.speaker = engine.Speaker(cfg)
        else:
            self.speaker.cfg = cfg
            self.speaker.clear_cache()

    def cap_nhat_cfg(self, cfg: dict):
        if self.speaker is not None:
            self.speaker.cfg = cfg
            self.speaker.clear_cache()

    @property
    def dang_doc(self) -> bool:
        return self._worker is not None and self._worker.is_alive()

    # ------------------------------------------------------------ điều khiển

    def phat(self):
        if self.dang_doc or not self.playlist:
            return
        if self.index >= len(self.playlist):
            self.index = 0
        self._stop.clear()
        self._phien += 1

        # Nạp trước song song 2 đoạn kế tiếp ngay khi bấm Phát để khử 100% độ trễ đoạn đầu
        if self.speaker:
            for delta in (1, 2):
                p_idx = self.index + delta
                if p_idx < len(self.playlist):
                    ke = self.playlist[p_idx]
                    _dam_bao_da_dich(ke, self.speaker.cfg if self.speaker else {})
                    self.speaker.prefetch(p_idx, ke["text"], ke.get("khuech_dai", 1.0))

        self._worker = threading.Thread(target=self._chay, args=(self._phien,),
                                        daemon=True)
        self._worker.start()
        self._day({"state": "dang_doc", "pos": self.index + 1, "doan": self.index + 1})

    def tam_dung(self):
        self._huy_phien()
        self._cho_dung()
        self._day({"state": "tam_dung", "pos": self.index + 1, "doan": self.index + 1})

    def dung(self, giu_vi_tri=False):
        self._huy_phien()
        self._cho_dung()
        if not giu_vi_tri:
            self.index = 0
        if self.speaker:
            self.speaker.clear_cache()
            self.speaker.stop()
        engine.giai_phong_bo_nho_he_thong()
        self._day({"state": "san_sang" if self.playlist else "trong",
                   "pos": self.index + 1 if self.playlist else 0})

    def nhay_toi(self, dong: int):
        """dong đếm từ 1. Đang đọc thì đọc tiếp ngay từ chỗ mới."""
        if not self.playlist:
            return
        moi = max(0, min(len(self.playlist) - 1, int(dong) - 1))
        dang = self.dang_doc
        if dang:
            self._huy_phien()
            self._cho_dung()
            if self.speaker:
                self.speaker.clear_cache()
        self.index = moi
        if dang:
            self.phat()
        else:
            self._day({"pos": self.index + 1})

    def buoc(self, huong: int):
        self.nhay_toi(self.index + 1 + huong)

    def tat(self):
        self._huy_phien()
        if self.speaker:
            self.speaker.shutdown()

    # ------------------------------------------------------------ nội bộ

    def _huy_phien(self):
        """Vô hiệu hoá luồng đọc hiện tại và bảo nó dừng ngay."""
        self._phien += 1
        self._stop.set()
        if self.speaker:
            self.speaker.stop()

    def _cho_dung(self):
        worker, self._worker = self._worker, None
        if worker is not None and worker.is_alive():
            worker.join(timeout=CHO_DUNG_GIAY)

    def _het_han(self, phien: int) -> bool:
        return phien != self._phien or self._stop.is_set()

    def _chay(self, phien: int):
        try:
            while self.index < len(self.playlist):
                if self._het_han(phien):
                    return
                idx = self.index
                seg = self.playlist[idx]
                _dam_bao_da_dich(seg, self.speaker.cfg if self.speaker else {})

                # 1. Báo UI chuẩn bị âm thanh cho đoạn này (chưa có thoiLuong -> UI chờ, không chạy chữ trước tiếng)
                self._day({
                    "pos": idx + 1,
                    "doan": idx + 1,
                    "state": "dang_doc",
                    "cauDoc": seg.get("text", ""),
                    "cauGoc": seg.get("text_goc", "")
                })

                try:
                    audio, dinh_dang = self.speaker.get_audio(
                        idx, seg["text"], seg.get("khuech_dai", 1.0), stream=False)
                except Exception as e:


                    nhat_ky.ghi_loi(f"đọc đoạn {idx + 1}/{len(self.playlist)}", e)
                    if self._het_han(phien):
                        return
                    self._day({
                        "state": "loi",
                        "loi": {"tieu_de": "Không đọc được đoạn này",
                                "chi_tiet": str(e),
                                "nut": [{"nhan": "Đọc tiếp", "act": "docTiep"}]},
                    })
                    return

                # Nạp trước 2 đoạn kế tiếp (Double-Buffer Lookahead chống trễ hoàn toàn)
                for delta in (1, 2):
                    next_idx = idx + delta
                    if next_idx < len(self.playlist):
                        ke = self.playlist[next_idx]
                        _dam_bao_da_dich(ke, self.speaker.cfg if self.speaker else {})
                        self.speaker.prefetch(next_idx, ke["text"],
                                              ke.get("khuech_dai", 1.0))


                # Tổng hợp xong mới quay lại đây - lúc này phiên có thể đã bị
                # thay, tuyệt đối không được phát nữa.
                if self._het_han(phien):
                    return

                # Báo thời lượng thật của đoạn audio để giao diện tô màu chạy
                # theo từng chữ. Phải gửi ngay sát lúc phát, gửi sớm hơn thì
                # chữ chạy trước tiếng.
                tl_goc = _thoi_luong_wav(audio, seg.get("text", ""))
                he_so_toc = 1.0
                if "atempo=" in self.loc_am:
                    m = re.search(r"atempo=([\d.]+)", self.loc_am)
                    if m: he_so_toc = float(m.group(1))
                elif "tempo=" in self.loc_am:
                    m = re.search(r"tempo=([\d.]+)", self.loc_am)
                    if m: he_so_toc = float(m.group(1))
                
                self._day({
                    "pos": idx + 1,
                    "doan": idx + 1,
                    "state": "dang_doc",
                    "thoiLuong": tl_goc / he_so_toc,
                    "cauDoc": seg.get("text", ""),
                    "cauGoc": seg.get("text_goc", "")
                })
                if not self.speaker.play(audio, self._stop, dinh_dang, self.loc_am,
                                         text_goc=seg.get("text", ""),
                                         khuech_dai=seg.get("khuech_dai", 1.0)):
                    # play() trả False vì HAI lẽ khác nhau:
                    #   · chính ta vừa bị bảo dừng -> dung()/tam_dung() đã đẩy
                    #     trạng thái rồi, đẩy nữa là ghi đè mất
                    #   · bị nguồn khác GIÀNH LOA -> chưa ai đẩy gì cả
                    # Vế thứ hai là chỗ hở: vòng đọc thoát im lặng, khối finally
                    # dưới cũng không đẩy, nên tiếng tắt ngấm mà màn hình vẫn
                    # báo đang đọc. Đúng họ lỗi sổ đối chiếu đã ghi ở màn Cài đặt.
                    if not self._het_han(phien):
                        self._day({"state": "tam_dung", "pos": self.index + 1,
                                   "doan": self.index + 1})
                    return
                if self._het_han(phien):
                    return

                self.index = idx + 1
                het = time.time() + seg.get("nghi", 0)
                while time.time() < het and not self._het_han(phien):
                    time.sleep(0.05)

            if not self._het_han(phien):
                self.index = 0
                self._day({"state": "san_sang", "pos": 1,
                           "banner": "Đã đọc xong toàn bộ. Bấm "
                                     "<strong>Phát</strong> để nghe lại từ đầu."})
                engine.giai_phong_bo_nho_he_thong()
        finally:
            if phien == self._phien:
                self._worker = None
                engine.giai_phong_bo_nho_he_thong()
