# -*- coding: utf-8 -*-
"""Xuất playlist ra tệp âm thanh cho bản mới — WAV hoặc MP3, có SỐ PHIÊN.

VÌ SAO KHÔNG DÙNG THẲNG giaodien/xuat_file.py:

  · Ba kiểu tách của nó là (một tệp / mỗi 20 mục / mỗi dòng) — sinh ra cho
    danh sách công đức. Đặc tả màn hình 3 cần (một tệp / mỗi đoạn / cắt theo
    độ dài 10 phút). Khác hẳn nhau.
  · Nó chỉ ghi WAV. Hộp thoại bày sẵn MP3 320 và MP3 128 kbps — bày ra mà
    không làm được thì đúng là nút giả, thứ KPI dự án cấm.
  · Nó dừng bằng mỗi cờ threading.Event. Đó chính là họ bẫy đã vấp ở bo_doc
    và nghe_thu: tổng hợp một câu có thể mất tới 40 giây, cờ dừng không cắt
    nổi luồng đang đứng trong VieNeu, nên luồng cũ tỉnh dậy và ghi tiếp vào
    tệp mà người dùng tưởng đã huỷ xong từ lâu.

Không sửa xuat_file.py: chạm tối thiểu, và nó vẫn là đường xuất của Api cũ.

SỐ PHIÊN — mỗi lần bấm Bắt đầu xuất thì phiên tăng một. Luồng cũ tỉnh dậy,
thấy phiên trong tay không còn là phiên hiện hành thì tự im: không ghi tiếp,
không đẩy tiến độ, không báo xong. Cờ dừng chỉ là lớp thứ hai.

Nguồn VieNeu ra WAV 16 bit / 1 kênh / 48.000 Hz. Nên:
  · wav16  ghi thẳng, không cần ffmpeg — nhanh nhất, đúng nguyên bản.
  · wav24  và MP3 phải qua ffmpeg. Riêng wav24 chỉ là nới bit depth, KHÔNG
    làm tiếng hay hơn; giữ lựa chọn này vì đặc tả có, và tệp nó đẻ ra đúng là
    tệp 24 bit thật chứ không phải dán nhãn.
"""

import io
import os
import subprocess
import threading
import time
import wave
from pathlib import Path

import DocCongDuc as engine

from . import luu_tep
from giaodien import nhat_ky
from giaodien.du_lieu import KY_TU_MOI_GIAY

# Cắt theo độ dài: mỗi tệp tối đa chừng này giây audio.
GIAY_MOI_TEP = 600

# Đuôi của tệp đang ghi dở. Mang đuôi này thì Windows không coi là tệp âm
# thanh, người dùng mở ra cũng không nghe được nửa vời rồi tưởng phần mềm hỏng.
DUOI_DANG_XUAT = ".dangxuat"

# Ước tính: VieNeu ra 96.000 byte mỗi giây, và tổng hợp trên CPU chậm hơn
# thời lượng audio khoảng 4 lần. Hai con số này đo trên máy thật, chép lại từ
# giaodien/xuat_file.py để không phải nhập chéo module chỉ vì hai hằng số.
BYTE_MOI_GIAY = 96000
LAN_CHAM_HON_AUDIO = 4.0

# Cờ của Windows để subprocess không chớp cửa sổ đen lên giữa màn hình.
_KHONG_HIEN_CUA_SO = 0x08000000


def _khong_hien_cua_so():
    """STARTUPINFO giấu cửa sổ, giống hệt engine dựng trong Speaker.play."""
    if os.name != "nt":
        return None
    si = subprocess.STARTUPINFO()
    si.dwFlags |= subprocess.STARTF_USESHOWWINDOW
    si.wShowWindow = 0
    return si

DINH_DANG = {
    "wav16": {"duoi": ".wav", "ma": None},
    "wav24": {"duoi": ".wav", "ma": ["-c:a", "pcm_s24le"]},
    "mp3-320": {"duoi": ".mp3", "ma": ["-c:a", "libmp3lame", "-b:a", "320k"]},
    "mp3-128": {"duoi": ".mp3", "ma": ["-c:a", "libmp3lame", "-b:a", "128k"]},
}


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


def duong_ffmpeg(cfg: dict) -> Path:
    """ffmpeg.exe nằm cạnh ffplay.exe mà engine đã dò sẵn trong cfg.

    Dò lại từ đầu là đẻ thêm một chỗ nữa phải nhớ sửa khi đổi cách đóng gói —
    và bản đóng gói trỏ ffmpeg\\bin bằng junction, không phải thư mục thật.
    """
    return Path(cfg["ffplay"]).parent / "ffmpeg.exe"


def uoc_tinh(playlist: list, so_doan: int) -> dict:
    """Ba dòng ước tính của giai đoạn 1, mỗi kiểu tách một dòng."""
    tong_ky_tu = sum(len(s.get("text", "")) for s in playlist)
    tong_nghi = sum(s.get("nghi", 0) for s in playlist)
    giay = tong_ky_tu / KY_TU_MOI_GIAY + tong_nghi
    co = _co_chu(giay * BYTE_MOI_GIAY)
    xu_ly = _thoi_luong_chu(giay * LAN_CHAM_HON_AUDIO)
    so_tep_dai = max(1, -(-int(giay) // GIAY_MOI_TEP))

    return {
        "mot": f"Ước tính: 1 tệp · {co} · khoảng {xu_ly} xử lý",
        "moi-doan": f"Ước tính: {so_doan} tệp · tổng {co} · khoảng {xu_ly} xử lý",
        "do-dai": (f"Ước tính: 1 tệp · {co} · chưa tới 10 phút nên không cắt"
                   if so_tep_dai == 1 else
                   f"Ước tính: {so_tep_dai} tệp · tổng {co} · khoảng {xu_ly} xử lý"),
        "goiY": {"mot": co, "moi-doan": f"{so_doan} tệp",
                 "do-dai": "mỗi 10 phút một tệp"},
    }


class BoXuatMoi:
    def __init__(self, day_tien_do, bao_xong, bao_loi, bao_huy):
        self._tien_do = day_tien_do
        self._xong = bao_xong
        self._loi = bao_loi
        self._huy = bao_huy
        self._stop = threading.Event()
        self._worker = None
        self._phien = 0
        # Phiên nào bị người dùng bấm Huỷ. Phải nhớ riêng: phiên bị một lượt
        # xuất MỚI đè lên thì im lặng rút, còn phiên bị bấm Huỷ thì phải báo
        # về cho giao diện đóng hộp, không thì hộp đứng im như treo máy.
        self._phien_huy = None
        self._khoa = threading.Lock()

    @property
    def dang_chay(self) -> bool:
        return self._worker is not None and self._worker.is_alive()

    def huy(self):
        with self._khoa:
            self._phien_huy = self._phien
            self._phien += 1
        self._stop.set()

    def bat_dau(self, playlist, doan_cua_mau, cfg, ten, thu_muc, tach, dinh_dang,
                loc=""):
        """Mở phiên mới rồi chạy nền. Phiên cũ có sống lại cũng thành vô hiệu.

        `loc` là chuỗi -af của ba thanh chỉnh. Tệp xuất ra PHẢI nghe giống hệt
        thứ người dùng vừa nghe thử, không thì họ chỉnh cả buổi rồi mở tệp ra
        thấy khác hẳn.
        """
        with self._khoa:
            self._phien += 1
            phien = self._phien
            # Lượt xuất mới xoá dấu huỷ cũ: luồng của lượt trước có tỉnh dậy
            # muộn cũng không được đóng mất hộp của lượt này.
            self._phien_huy = None
        self._stop.clear()
        self._worker = threading.Thread(
            target=self._chay, daemon=True,
            args=(phien, playlist, doan_cua_mau, cfg, ten, thu_muc, tach,
                  dinh_dang, str(loc or "")))
        self._worker.start()

    # ------------------------------------------------------------ nội bộ

    def _con_hieu_luc(self, phien: int) -> bool:
        with self._khoa:
            return phien == self._phien and not self._stop.is_set()

    def _nhom(self, playlist, doan_cua_mau, tach):
        """Chia playlist thành các nhóm, mỗi nhóm ra một tệp."""
        if tach == "moi-doan":
            nhom, dang = [], None
            for i, seg in enumerate(playlist):
                so = doan_cua_mau[i] if i < len(doan_cua_mau) else None
                if so != dang or not nhom:
                    nhom.append([])
                    dang = so
                nhom[-1].append(seg)
            return nhom
        if tach == "do-dai":
            nhom, don, tich = [], [], 0.0
            for seg in playlist:
                don.append(seg)
                tich += len(seg.get("text", "")) / KY_TU_MOI_GIAY \
                    + seg.get("nghi", 0)
                if tich >= GIAY_MOI_TEP:
                    nhom.append(don)
                    don, tich = [], 0.0
            if don:
                nhom.append(don)
            return nhom or [[]]
        return [list(playlist)]

    def _chay(self, phien, playlist, doan_cua_mau, cfg, ten, thu_muc, tach,
              dinh_dang, loc=""):
        dd = dict(DINH_DANG.get(dinh_dang, DINH_DANG["wav16"]))
        if loc:
            # Có chỉnh âm thì kể cả WAV 16 bit cũng phải đi qua ffmpeg, vì bộ
            # lọc nằm ở đó. Không chỉnh gì thì WAV 16 vẫn ghi thẳng như cũ.
            dd["ma"] = list(dd["ma"] or []) + ["-af", loc]
        nhom = self._nhom(playlist, doan_cua_mau, tach)
        speaker = engine.Speaker(cfg)
        bat_dau = time.time()
        tong_muc = len(playlist)
        da_lam = da_ghi = 0
        tong_giay = 0.0
        tep_dau = None

        try:
            Path(thu_muc).mkdir(parents=True, exist_ok=True)
            # Dọn rác của lần trước bị đóng ngang. Chỉ đụng tệp mang đuôi
            # .dangxuat - đó là thứ chương trình này đẻ ra, không phải tệp của
            # người dùng.
            self._don_tep_do(Path(thu_muc).glob("*" + DUOI_DANG_XUAT))
            for chi_so, cac_doan in enumerate(nhom, 1):
                if not self._con_hieu_luc(phien):
                    return self._bao_huy(phien)

                duoi_so = "" if len(nhom) == 1 else f"-{chi_so:03d}"
                # Lọc tên TRƯỚC khi ghép đường dẫn: "Công đức T8/2026" mà để
                # nguyên thì lệnh ghi ném [Errno 22] và người dùng nhận một câu
                # tiếng Anh kèm đường dẫn, không hiểu mình đã làm sai gì.
                ten_an_toan = luu_tep.ten_tep_an_toan(ten)
                dich = luu_tep.duong_dan_moi(
                    Path(thu_muc) / f"{ten_an_toan}{duoi_so}{dd['duoi']}")
                # Tệp tạm cũng phải né tệp sẵn có: người dùng hoàn toàn có thể
                # đang giữ một "thongbao.goc.wav" của riêng họ trong thư mục ấy.
                tam = dich if not dd["ma"] else luu_tep.duong_dan_moi(
                    dich.with_name(dich.stem + ".goc.wav"))

                giay_nhom, da_lam = self._ghi_mot_tep(
                    phien, speaker, cac_doan, tam, da_lam, tong_muc, bat_dau,
                    da_ghi)
                if giay_nhom is None:
                    # Huỷ giữa chừng để lại một tệp cụt nửa chừng. Với người
                    # dùng đích - người lớn tuổi - một tệp nằm đó trông y như
                    # bản xuất thành công; họ mở ra nghe được nửa bài rồi tưởng
                    # phần mềm hỏng. Dọn đi.
                    self._don_tep_do([tam, dich])
                    return self._bao_huy(phien)
                tong_giay += giay_nhom

                # Chốt trước khi gọi ffmpeg: nó là tiến trình ngoài, đã chạy
                # rồi thì cờ huỷ không với tới, người dùng phải ngồi đợi hết.
                if not self._con_hieu_luc(phien):
                    self._don_tep_do([tam, dich])
                    return self._bao_huy(phien)

                if dd["ma"] and not self._chuyen_ma(cfg, tam, dich, dd["ma"]):
                    # Chuyển mã hỏng thì GIỮ LẠI bản WAV: nó vừa ngốn hàng phút
                    # tổng hợp, vứt đi là bắt người dùng chờ lại từ đầu. Có tệp
                    # nghe được còn hơn không có gì.
                    if tam.exists():
                        # Bỏ đuôi ".goc" đi: người dùng chọn MP3 mà nhận về
                        # "thongbao.goc.wav" thì tưởng phần mềm để quên tệp rác.
                        that = luu_tep.duong_dan_moi(
                            tam.with_name(tam.name.replace(".goc.wav", ".wav")))
                        try:
                            tam.rename(that)
                        except OSError:
                            that = tam
                        tep_dau = tep_dau or that
                        da_ghi += that.stat().st_size
                    continue
                if tep_dau is None and dich.exists():
                    tep_dau = dich
                if dich.exists():
                    da_ghi += dich.stat().st_size

            if not self._con_hieu_luc(phien):
                return self._bao_huy(phien)
            if tep_dau is None:
                self._loi("Không có nội dung nào được tổng hợp.")
                return

            self._xong({
                "ten": tep_dau.name if len(nhom) == 1
                       else f"{ten}-*{dd['duoi']} ({len(nhom)} tệp)",
                "thoiLuong": _thoi_luong_chu(tong_giay),
                "kichThuoc": _co_chu(da_ghi),
                "xuLy": _mm_ss(time.time() - bat_dau),
                "duongDan": str(tep_dau),
                "thuMuc": str(tep_dau.parent),
            })
        except Exception as e:
            nhat_ky.ghi_loi(f"xuất file {ten}", e)
            if self._con_hieu_luc(phien):
                self._loi(str(e))
        finally:
            speaker.shutdown()

    def _ghi_mot_tep(self, phien, speaker, cac_doan, dich, da_lam, tong,
                     bat_dau, byte_truoc):
        """Ghép các mẩu vào một tệp WAV. Trả (số giây, đã làm) hoặc (None, _).

        GHI VÀO TỆP ".dangxuat" RỒI MỚI ĐỔI TÊN khi xong.

        Bấm Huỷ thì đã dọn được, nhưng ĐÓNG CỬA SỔ giữa lúc xuất thì không:
        worker là luồng daemon, GiongViet gọi os._exit(0) là nó chết ngang,
        không kịp dọn gì, mà lúc ấy tệp còn đang mở nên bên ngoài cũng không
        xoá được. Cách duy nhất chắc ăn là đừng để nó mang tên thật từ đầu -
        thứ còn lại trên đĩa là "thongbao.wav.dangxuat", không phải tệp WAV,
        người dùng không thể nhầm nó với bản xuất thành công.
        """
        dang = dich.with_name(dich.name + DUOI_DANG_XUAT)
        ghi = None
        giay = 0.0
        byte_tep = 0
        try:
            from src.core.bo_doc import _dam_bao_da_dich
            cfg_spk = speaker.cfg if speaker else {}

            # Prefetch gối đầu các mẩu đầu tiên
            for s in cac_doan[:3]:
                _dam_bao_da_dich(s, cfg_spk)
                speaker.prefetch(id(s), s["text"], s.get("khuech_dai", 1.0))

            for idx_s, seg in enumerate(cac_doan):
                if not self._con_hieu_luc(phien):
                    return None, da_lam
                # Đẩy mẩu tiếp theo vào hàng đợi tổng hợp ngầm
                if idx_s + 3 < len(cac_doan):
                    tiep = cac_doan[idx_s + 3]
                    _dam_bao_da_dich(tiep, cfg_spk)
                    speaker.prefetch(id(tiep), tiep["text"], tiep.get("khuech_dai", 1.0))

                _dam_bao_da_dich(seg, cfg_spk)
                audio, _dd = speaker.get_audio(
                    id(seg), seg["text"], seg.get("khuech_dai", 1.0))
                # Kiểm lại NGAY SAU get_audio: mẩu vừa rồi có thể đã ngốn 40
                # giây, người dùng bấm Huỷ từ đời nào. Không có chốt này thì
                # tệp vẫn phình thêm sau khi họ tưởng đã dừng.
                if not self._con_hieu_luc(phien):
                    return None, da_lam
                if audio:
                    with wave.open(io.BytesIO(audio), "rb") as doc:
                        if ghi is None:
                            ghi = wave.open(str(dang), "wb")
                            ghi.setnchannels(doc.getnchannels())
                            ghi.setsampwidth(doc.getsampwidth())
                            ghi.setframerate(doc.getframerate())
                        ghi.writeframes(doc.readframes(doc.getnframes()))
                        giay += doc.getnframes() / doc.getframerate()
                    byte_tep += len(audio)
                    self._chen_im_lang(ghi, seg.get("nghi", 0))
                    giay += seg.get("nghi", 0)
                da_lam += 1
                self._bao_tien_do(phien, da_lam, tong, bat_dau,
                                  byte_truoc + byte_tep)
        finally:
            if ghi is not None:
                ghi.close()
            # Huỷ hoặc lỗi -> tệp dở không được phép ở lại dưới BẤT KỲ tên nào.
            if not self._con_hieu_luc(phien):
                self._don_tep_do([dang])
        if not self._con_hieu_luc(phien):
            return None, da_lam
        if dang.exists():
            # Đổi tên trên cùng ổ đĩa là thao tác nguyên tử: hoặc có tệp hoàn
            # chỉnh mang tên thật, hoặc không có gì cả. Không có trạng thái ở
            # giữa để người dùng nhìn nhầm.
            os.replace(dang, dich)
        return giay, da_lam

    def _chuyen_ma(self, cfg: dict, tam: Path, dich: Path, ma: list) -> bool:
        """WAV gốc -> định dạng người dùng chọn. Trả True nếu ra được tệp đích.

        Chỉ xoá bản WAV khi ĐÃ CHẮC có tệp đích thay thế. Xoá trong finally như
        lần đầu viết là hỏng ffmpeg một cái mất luôn cả buổi tổng hợp.
        """
        if not tam.exists():
            return False
        # CHUYỂN HƯỚNG ĐỦ BA ĐƯỜNG + startupinfo, y hệt engine làm ở
        # DocCongDuc.py Speaker.play. Bản .exe dựng bằng --windowed không có
        # console, nên tiến trình con thừa kế handle chuẩn không hợp lệ; chạy
        # từ source có console thì không bao giờ lộ ra. Đây đúng cái bẫy số một
        # của dự án - "chạy được từ source KHÔNG chứng minh .exe chạy được" -
        # nên bám theo cách engine đã chạy được nhiều tháng, đừng tự nghĩ kiểu
        # gọn hơn.
        try:
            subprocess.run(
                [str(duong_ffmpeg(cfg)), "-y", "-loglevel", "error",
                 "-i", str(tam), *ma, str(dich)],
                check=True,
                stdin=subprocess.DEVNULL, stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL,
                startupinfo=_khong_hien_cua_so(),
                creationflags=_KHONG_HIEN_CUA_SO)
        except (OSError, subprocess.SubprocessError) as e:
            nhat_ky.ghi_loi(f"chuyển mã {dich.name}", e)
            return False
        if not (dich.exists() and dich.stat().st_size > 0):
            return False
        try:
            tam.unlink()
        except OSError:
            pass          # còn lại tệp WAV thừa thì phiền, mất tệp đích mới tệ
        return True

    @staticmethod
    def _don_tep_do(cac_tep):
        for p in cac_tep:
            try:
                if p and Path(p).exists():
                    Path(p).unlink()
            except OSError:
                pass

    @staticmethod
    def _chen_im_lang(ghi, giay):
        if ghi is None or giay <= 0:
            return
        so_frame = int(ghi.getframerate() * giay)
        if so_frame > 0:
            ghi.writeframes(b"\0" * (so_frame * ghi.getsampwidth()
                                     * ghi.getnchannels()))

    def _bao_huy(self, phien):
        # Chỉ phiên ĐÚNG BỊ BẤM HUỶ mới được báo, và chỉ một lần. Phiên bị
        # lượt xuất mới đè lên thì rút im lặng — báo huỷ lúc ấy là đóng mất
        # hộp thoại của lượt người dùng vừa mở.
        with self._khoa:
            dung_phien = phien == self._phien_huy
            if dung_phien:
                self._phien_huy = None
        if dung_phien:
            self._huy()

    def _bao_tien_do(self, phien, da_lam, tong, bat_dau, da_ghi):
        if not self._con_hieu_luc(phien):
            return
        troi_qua = time.time() - bat_dau
        con_lai = (troi_qua / da_lam) * (tong - da_lam) if da_lam else 0
        self._tien_do({
            "phanTram": int(da_lam / max(1, tong) * 100),
            "moTa": f"Đang xử lý mục {da_lam}/{tong}",
            "troiQua": _mm_ss(troi_qua),
            "conLai": _mm_ss(con_lai) if da_lam else "—",
            "daGhi": _co_chu(da_ghi),
        })
