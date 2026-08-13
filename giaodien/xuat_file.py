# -*- coding: utf-8 -*-
"""Xuất playlist ra tệp WAV.

Ghép từng đoạn đã tổng hợp vào một tệp WAV bằng module wave của Python -
không nối thô bytes vì mỗi đoạn có phần đầu (header) riêng. Khoảng lặng
giữa các mục chèn bằng frame im lặng đúng định dạng của đoạn đầu tiên.
"""

import io
import threading
import time
import wave
from pathlib import Path

import DocCongDuc as engine

from . import du_lieu, nhat_ky

# Mỗi bao nhiêu mục thì cắt sang tệp mới ở kiểu tách "theo nhóm".
MUC_MOI_TEP = 20


def _mm_ss(giay: float) -> str:
    giay = max(0, int(giay))
    return f"{giay // 60:02d}:{giay % 60:02d}"


def _co_chu(so_byte: int) -> str:
    mb = so_byte / (1024 * 1024)
    if mb >= 1:
        return f"{mb:.1f} MB".replace(".", ",")
    return f"{so_byte / 1024:.0f} KB"


def _thoi_luong_chu(giay: float) -> str:
    phut, du = divmod(int(giay + 0.5), 60)
    return f"{phut} phút {du:02d} giây" if phut else f"{du} giây"


# VieNeu trả WAV 16 bit, 1 kênh, 48.000 Hz -> 96.000 byte mỗi giây (đo trên
# tệp thật, không đoán theo tài liệu).
BYTE_MOI_GIAY = 96000

# Tổng hợp giọng trên CPU chậm hơn thời lượng audio khoảng 4 lần (đo trên máy
# thật: 14,7 giây audio mất 78 giây, trong đó lần đầu còn tốn công nạp mô
# hình). Máy mạnh hơn sẽ nhanh hơn - đây chỉ là con số để người dùng biết nên
# chờ hay đi làm việc khác.
LAN_CHAM_HON_AUDIO = 4.0


def uoc_tinh(playlist: list, cfg: dict) -> list:
    """Ba lựa chọn tách tệp, kèm ước tính cho từng lựa chọn."""
    tong_ky_tu = sum(len(s.get("text", "")) for s in playlist)
    tong_nghi = sum(s.get("nghi", 0) for s in playlist)
    giay = tong_ky_tu / du_lieu.KY_TU_MOI_GIAY + tong_nghi
    so_byte = giay * BYTE_MOI_GIAY
    xu_ly = _thoi_luong_chu(giay * LAN_CHAM_HON_AUDIO)
    so_nhom = max(1, -(-len(playlist) // MUC_MOI_TEP))

    return [
        {"nhan": "Một tệp duy nhất", "goi_y": _co_chu(so_byte),
         "uoc_tinh": f"Ước tính: 1 tệp · {_co_chu(so_byte)} · "
                     f"khoảng {xu_ly} xử lý"},
        {"nhan": f"Mỗi {MUC_MOI_TEP} mục một tệp", "goi_y": f"{so_nhom} tệp",
         "uoc_tinh": f"Ước tính: {so_nhom} tệp · tổng {_co_chu(so_byte)} · "
                     f"khoảng {xu_ly} xử lý"},
        {"nhan": "Mỗi dòng một tệp", "goi_y": f"{len(playlist)} tệp",
         "uoc_tinh": f"Ước tính: {len(playlist)} tệp · tổng "
                     f"{_co_chu(so_byte)} · khoảng {xu_ly} xử lý"},
    ]


class BoXuat:
    def __init__(self, day_tien_do, bao_xong, bao_loi, bao_huy=None):
        self._tien_do = day_tien_do
        self._xong = bao_xong
        self._loi = bao_loi
        self._huy = bao_huy or (lambda: None)
        self._stop = threading.Event()
        self._worker = None

    @property
    def dang_chay(self) -> bool:
        return self._worker is not None and self._worker.is_alive()

    def huy(self):
        self._stop.set()

    def bat_dau(self, playlist, cfg, ten, thu_muc, kieu_tach):
        if self.dang_chay:
            return
        self._stop.clear()
        self._worker = threading.Thread(
            target=self._chay, args=(playlist, cfg, ten, thu_muc, kieu_tach),
            daemon=True)
        self._worker.start()

    # ------------------------------------------------------------ nội bộ

    def _nhom_theo_kieu(self, playlist, kieu_tach):
        if kieu_tach == 2:
            return [[s] for s in playlist]
        if kieu_tach == 1:
            return [playlist[i:i + MUC_MOI_TEP]
                    for i in range(0, len(playlist), MUC_MOI_TEP)]
        return [list(playlist)]

    def _chay(self, playlist, cfg, ten, thu_muc, kieu_tach):
        speaker = engine.Speaker(cfg)
        nhom = self._nhom_theo_kieu(playlist, kieu_tach)
        thu_muc = Path(thu_muc)
        bat_dau = time.time()
        tong_muc = len(playlist)
        da_lam = 0
        da_ghi = 0
        tong_giay = 0.0
        tep_dau = None

        try:
            thu_muc.mkdir(parents=True, exist_ok=True)
            for chi_so, cac_doan in enumerate(nhom, 1):
                if self._stop.is_set():
                    self._huy()
                    return

                duoi = "" if len(nhom) == 1 else f"-{chi_so:03d}"
                duong_dan = thu_muc / f"{ten}{duoi}.wav"
                if tep_dau is None:
                    tep_dau = duong_dan

                ghi = None
                try:
                    for seg in cac_doan:
                        if self._stop.is_set():
                            self._huy()
                            return
                        audio, _dd = speaker.get_audio(
                            id(seg), seg["text"], seg.get("khuech_dai", 1.0))
                        if audio:
                            with wave.open(io.BytesIO(audio), "rb") as doc:
                                if ghi is None:
                                    ghi = wave.open(str(duong_dan), "wb")
                                    ghi.setnchannels(doc.getnchannels())
                                    ghi.setsampwidth(doc.getsampwidth())
                                    ghi.setframerate(doc.getframerate())
                                ghi.writeframes(doc.readframes(doc.getnframes()))
                                tong_giay += doc.getnframes() / doc.getframerate()
                            self._chen_im_lang(ghi, seg.get("nghi", 0))
                            tong_giay += seg.get("nghi", 0)

                        da_lam += 1
                        self._bao_tien_do(da_lam, tong_muc, bat_dau)
                finally:
                    if ghi is not None:
                        ghi.close()
                if duong_dan.exists():
                    da_ghi += duong_dan.stat().st_size

            if tep_dau is None or not tep_dau.exists():
                self._loi("Không có nội dung nào được tổng hợp.")
                return

            self._xong({
                "ten": tep_dau.name if len(nhom) == 1 else f"{ten}-*.wav ({len(nhom)} tệp)",
                "thoi_luong": _thoi_luong_chu(tong_giay),
                "kich_thuoc": _co_chu(da_ghi),
                "xu_ly": _mm_ss(time.time() - bat_dau),
                "duong_dan": str(tep_dau),
            })
        except Exception as e:
            nhat_ky.ghi_loi(f"xuất file {ten}", e)
            self._loi(str(e))
        finally:
            speaker.shutdown()

    @staticmethod
    def _chen_im_lang(ghi, giay):
        if ghi is None or giay <= 0:
            return
        so_frame = int(ghi.getframerate() * giay)
        if so_frame > 0:
            ghi.writeframes(b"\0" * (so_frame * ghi.getsampwidth()
                                     * ghi.getnchannels()))

    def _bao_tien_do(self, da_lam, tong, bat_dau):
        troi_qua = time.time() - bat_dau
        phan_tram = int(da_lam / max(1, tong) * 100)
        con_lai = (troi_qua / da_lam) * (tong - da_lam) if da_lam else 0
        self._tien_do({
            "phan_tram": phan_tram,
            "mo_ta": f"Đang xử lý mục {da_lam}/{tong}",
            "troi_qua": _mm_ss(troi_qua),
            "con_lai": _mm_ss(con_lai) if da_lam else "—",
        })
