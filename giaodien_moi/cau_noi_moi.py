# -*- coding: utf-8 -*-
"""Cầu nối cho giao diện mới (ui-moi) — nối vào vòng đọc ĐÃ CÓ.

KHÔNG viết lại gì. `BoDoc` trong giaodien/bo_doc.py đã làm hết phần khó:
số phiên chống chồng tiếng, tổng hợp trước đoạn kế tiếp, và — quan trọng nhất
cho giao diện này — đẩy sang `thoiLuong` là số giây THẬT của khối WAV ngay sát
lúc phát, đúng thứ cần để tô chữ chạy theo tiếng.

Lớp này chỉ làm ba việc:
  1. Nhận danh sách ĐOẠN từ giao diện, dựng playlist cho BoDoc
  2. Dịch vị trí playlist ngược về SỐ ĐOẠN (một đoạn dài bị cắt thành nhiều
     mẩu, nên hai con số không trùng nhau)
  3. Chia chữ kèm mốc thời gian, giống hệt du_lieu._chia_tu

Kế thừa Api chứ không sửa giaodien/cau_noi.py: bản đang chạy phải nguyên vẹn.
"""

import re
import statistics
import threading
import time
from pathlib import Path

import webview

import DocCongDuc as engine

from giaodien import cai_dat, he_thong, nhat_ky, thu_vien_giong, tu_dien
from giaodien_moi import (am_thanh_loc, ho_so_v2, khoa_du_lieu, luu_tep,
                          so_dien_thoai, soat_moi, xuat_moi)
from giaodien.cau_noi import Api
from giaodien.du_lieu import _chia_tu

# Dòng ngắn, viết hoa gần hết, không kết thúc bằng dấu chấm -> coi là tiêu đề.
# Quy tắc thô nhưng đúng với thứ người dùng thật hay dán vào: thông báo, công
# văn, chương sách - tiêu đề của chúng đều viết hoa.
DAI_TOI_DA_TIEU_DE = 80

# Khoảng loa còn IM sau khi bộ đọc bảo "phát đi", trước lúc tiếng thật ra.
#
# Toàn bộ khoảng này là chi phí dựng một tiến trình ffplay mới cho từng mẩu:
# nạp exe, mở thiết bị âm thanh, đệm. Đo trên máy chủ dự án (giaodien_moi/
# do_tre_phat.py, 14 giọng): 12 giọng nằm gọn trong 621-855 ms, không phụ
# thuộc giọng cũng không phụ thuộc độ dài đoạn. Con số 240 ms trước đây chỉ là
# lúc TIẾN TRÌNH ffplay xuất hiện, chưa tính phần nó mở thiết bị và đệm - nên
# chữ vượt lên trước tiếng khoảng nửa giây ở mọi đoạn.
#
# Đây chỉ là giá trị cho mẩu ĐẦU TIÊN. Từ mẩu thứ hai trở đi dùng số đo thật
# của chính máy đang chạy, xem _cap_nhat_tre().
TRE_PHAT_MAC_DINH_MS = 700

# Trần và sàn cho số tự đo: máy kẹt CPU một nhịp là ra 2,9 giây, tin nó thì
# chữ đứng im gần ba giây.
TRE_THAP_NHAT_MS = 150
TRE_CAO_NHAT_MS = 1500

# Lấy trung vị của mấy lần gần nhất chứ không lấy trung bình: một lần kẹt CPU
# kéo trung bình lệch hẳn, còn trung vị thì không nhúc nhích.
SO_LAN_NHO_TRE = 5

# Đợi chừng này rồi mới tổng hợp trước mẩu đầu. Người dùng lướt qua mấy tab
# liền tay thì mỗi lần đổi là một lượt hẹn mới, lượt cũ bị huỷ - chỉ tab họ
# thật sự dừng lại mới được tổng hợp. Đủ ngắn để họ chưa kịp đọc xong màn hình.
CHO_NAP_TRUOC_GIAY = 1.2


def _la_tieu_de(dong: str) -> bool:
    d = dong.strip()
    if not d or len(d) > DAI_TOI_DA_TIEU_DE or d.endswith((".", "!", "?", ":")):
        return False
    chu = [c for c in d if c.isalpha()]
    if not chu:
        return False
    return sum(1 for c in chu if c.isupper()) / len(chu) >= 0.7


def van_ban_thanh_doan(text: str) -> list:
    """Văn bản thô -> mảng đoạn {kieu, chu} đúng hình dạng đặc tả.

    Mỗi dòng là một đoạn; dòng trống thành đoạn `blank`. Giữ dòng trống chứ
    không gộp: nó là nhịp nghỉ mắt của người đọc, và đặc tả có hẳn loại đoạn
    cho nó.
    """
    doan = []
    for dong in re.split(r"\r\n|\r|\n", text or ""):
        d = dong.rstrip()
        if not d.strip():
            doan.append({"kieu": "blank", "chu": ""})
        else:
            doan.append({"kieu": "head" if _la_tieu_de(d) else "body",
                         "chu": d.strip()})
    # Bỏ các dòng trống thừa ở cuối, đừng để cuộn xuống một khoảng rỗng dài.
    while doan and doan[-1]["kieu"] == "blank":
        doan.pop()
    return doan


class ApiMoi(Api):
    def __init__(self, vung_lam_viec=(0, 0, 1280, 800)):
        # CỐ Ý KHÔNG khoá đường ghi ở đây nữa (2026-08-13).
        #
        # Khoá dựng ra hồi bản cũ còn chạy hằng ngày, để bản mới đang dở dang
        # không ghi đè dữ liệu của nó. Chủ dự án đã bỏ hẳn bản cũ, mà giữ khoá
        # thì Từ điển phát âm, Thư viện giọng và Cài đặt đều thành nút bấm
        # không ăn thua - người dùng thêm một từ, dùng được trong phiên, đóng
        # chương trình là mất sạch. Đó mới là thứ tệ hơn.
        #
        # Bộ kiểm và bài đo vẫn tự bật khoa_du_lieu.khoa() trước khi dựng
        # ApiMoi, nên chạy thử vẫn không để lại vết nào.
        super().__init__(vung_lam_viec)
        # Số đoạn tương ứng với từng mẩu trong playlist. Một đoạn dài bị
        # tach_chunk cắt làm nhiều mẩu nên map này KHÔNG phải ánh xạ 1-1.
        self._doan_cua_mau = []
        self._doan = []
        self._nghe_rieng = False
        # "vanban" hay "congduc". Danh sách công đức dựng playlist theo đường
        # khác hẳn (mẫu câu, lời dẫn, nhóm nghỉ), nên phải nhớ tab đang mở
        # thuộc loại nào.
        self._loai_tai_lieu = "vanban"
        # Trọng số đọc theo số đoạn. Chuẩn hoá từng chữ là phần chậm nhất trên
        # đường đẩy tin, mà một đoạn thì bị hỏi lại mỗi mẩu một lần.
        self._trong_so_cache = {}
        # Tự đo độ trễ ra loa: (thời điểm, số mẩu, thời lượng WAV, nghỉ)
        self._moc_phat = None
        self._tre_da_do = []
        self._tre_ms = TRE_PHAT_MAC_DINH_MS
        # Hẹn giờ nạp trước mẩu đầu. Đổi tab lần nữa thì lượt hẹn cũ bị huỷ.
        self._hen_nap_truoc = None
        # Ba thanh chỉnh của hồ sơ, và chuỗi -af dựng từ chúng.
        self._chinh_am = {}
        self._loc_am = ""
        # Tệp nào đã có bản lưu của mình: {tên đang mở: đường dẫn đã ghi}.
        self._da_luu = {}
        # Bộ xuất riêng của bản mới. Bốn đường báo ngược dùng lại của lớp cha
        # (window.gd.tienDoXuat / xuatXong / xuatLoi / xuatHuy) - giao thức ấy
        # đã chạy được ở bản cũ, không viết lại.
        self._bo_xuat_moi = xuat_moi.BoXuatMoi(
            self._tien_do_xuat, self._xuat_xong, self._xuat_loi, self._xuat_huy)

    # ------------------------------------------------------------ nạp nội dung

    def moi_dat_doan(self, doan):
        """Giao diện gửi sang mảng đoạn: [{kieu, chu}, ...], đếm từ 1.

        Đoạn rỗng bị bỏ khỏi playlist nhưng vẫn giữ số thứ tự của nó — người
        dùng bấm số đoạn nào thì phải đọc đúng đoạn đó.
        """
        # Dừng hẳn TRƯỚC khi thay playlist. Đổi playlist dưới chân vòng đọc thì
        # nó vẫn đang phát mẩu của tài liệu cũ, mà giao diện đã đếm theo tài
        # liệu mới - loa một đằng màn hình một nẻo. Đã xảy ra thật.
        self._bo_doc.dung()
        self._doan = list(doan or [])
        self._loai_tai_lieu = "vanban"
        self._records, self._canh_bao = [], []
        self._trong_so_cache.clear()
        self._moc_phat = None
        self._playlist, self._doan_cua_mau = self._dung_playlist(range(1, len(self._doan) + 1))
        self._bo_doc.dat_playlist(self._playlist, self._cfg)
        self._nghe_rieng = False
        self._nap_truoc_mau_dau()
        return {"soMau": len(self._playlist), "soDoan": len(self._doan)}

    def _nap_truoc_mau_dau(self):
        """Hẹn tổng hợp sẵn mẩu đầu, để bấm Nghe là có tiếng ngay.

        Đo được: từ lúc bấm Nghe đến lúc có tiếng mất 5,9 giây với một câu ngắn
        và 9,8 giây với một đoạn vừa - gần như toàn bộ là VieNeu dựng WAV, còn
        ffplay chỉ chiếm 0,6-0,9 giây. Người dùng ngồi nhìn màn hình im lìm gần
        chục giây, tưởng máy treo. Khoảng ấy tiêu được ngay lúc họ còn đang đọc
        lướt văn bản vừa mở.

        CHỐT DUY NHẤT: CHỜ MỘT NHỊP rồi mới làm. Lướt qua năm tab là năm lượt
        tổng hợp, mà Speaker chỉ có MỘT worker nên chúng xếp hàng nối đuôi. Đo
        thật lúc chưa có chốt này: bấm Nghe phải chờ 106 giây vì đứng sau cả
        hàng; có chốt rồi còn 11 giây.

        CỐ Ý KHÔNG huỷ lượt đã gửi vào pool. Muốn huỷ thì phải nắm cái future,
        mà Speaker chỉ cất nó trong `_cache` - thuộc tính riêng của một lớp
        thuộc engine dùng chung. Đã thử và trả giá: 15 lỗi AttributeError trong
        GiongViet-loi.log, cộng một phép kiểm xanh giả vì vật giả trong bài kiểm
        không có `_cache` nên biến luôn bằng None và phép so sánh thành vô
        nghĩa. Đổi lại chỉ được ~1% lợi ích - xấu nhất là một lượt tổng hợp
        thừa chạy nốt trong nền.
        """
        self._huy_hen_nap_truoc()
        if not self._playlist or not self._bo_mo_hinh.san_sang:
            return
        self._hen_nap_truoc = threading.Timer(CHO_NAP_TRUOC_GIAY,
                                              self._chay_nap_truoc)
        self._hen_nap_truoc.daemon = True
        self._hen_nap_truoc.start()

    def _huy_hen_nap_truoc(self):
        """Bỏ lượt nạp trước còn đang hẹn mà chưa tới giờ."""
        hen = self._hen_nap_truoc
        if hen is not None:
            hen.cancel()
            self._hen_nap_truoc = None

    def _chay_nap_truoc(self):
        speaker = self._bo_doc.speaker
        if speaker is None or not self._playlist or not self._bo_mo_hinh.san_sang:
            return
        seg = self._playlist[0]
        try:
            speaker.prefetch(0, seg["text"], seg.get("khuech_dai", 1.0))
        except Exception as e:                      # noqa: BLE001
            # Nạp trước chỉ là tiện thêm; hỏng thì người dùng chờ như cũ chứ
            # không được phép làm sập cả vòng đọc.
            nhat_ky.ghi_loi("nạp trước mẩu đầu", e)

    def _dung_playlist(self, so_doan_can):
        """Dựng playlist từ các số đoạn cho trước. Trả (playlist, map số đoạn).

        Mỗi mẩu mang theo PHẠM VI KÝ TỰ của nó trong đoạn gốc (`tu`, `den`).
        Giao diện cần con số này để tô chữ: một đoạn dài bị cắt làm ba mẩu, mỗi
        mẩu có thời lượng WAV riêng, mà tỉ lệ ký tự của mẩu thì gần như không
        bao giờ trùng tỉ lệ thời lượng của nó. Không có phạm vi thì giao diện
        chỉ còn cách chia đều cả đoạn theo ký tự - và đó chính là chỗ chữ chạy
        lệch khỏi tiếng.
        """
        playlist, ban_do = [], []
        for n in so_doan_can:
            d = self._doan[n - 1] if 0 < n <= len(self._doan) else None
            if not d or not str(d.get("chu", "")).strip():
                continue
            goc = str(d["chu"])
            # Cắt trên chính chuỗi HIỂN THỊ, không phải chuỗi đã chuẩn hoá:
            # start/end của tach_chunk phải đếm được trên đúng chữ mà người
            # dùng nhìn thấy, không thì tô lệch đúng bằng phần chuẩn hoá đã
            # thêm bớt.
            for c in engine.tach_chunk(goc, self._cfg["so_ky_tu"]):
                # Số điện thoại đọc TRƯỚC khi engine chuẩn hoá: engine đọc số
                # theo kiểu số lượng nên "1900 6868" ra "một nghìn chín trăm
                # sáu nghìn…". Thay sẵn bằng chữ thì engine không hiểu sai nữa.
                doc = engine.chuan_hoa_van_ban(
                    so_dien_thoai.chuan_hoa(c["raw"]), self._tudien, self._cfg)
                if not doc.strip():
                    continue
                playlist.append({
                    "loai": "cau", "text": doc, "goc": c["raw"], "rec": None,
                    "tu": c["start"], "den": c["end"],
                    "nghi": self._cfg["nghi_doan_vb"] if c["cuoi_doan"]
                            else self._cfg["nghi_cau"],
                })
                ban_do.append(n)
        for i, seg in enumerate(playlist, 1):
            seg["stt"], seg["tong"] = i, len(playlist)
        return playlist, ban_do

    # ------------------------------------------------------------ điều khiển đọc

    def moi_nghe_toan_bo(self):
        if not self._bo_mo_hinh.san_sang:
            return {"loi": "Mô hình chưa sẵn sàng"}
        if self._nghe_rieng:
            # Đang ở playlist một đoạn, phải dựng lại playlist đầy đủ.
            self.moi_dat_doan(self._doan)
        # Bỏ lượt nạp trước còn đang HẸN để nó khỏi tranh CPU với vòng đọc.
        # Cái đã gửi vào pool thì cứ để chạy nốt - vòng đọc sắp lấy đúng nó ra
        # dùng, huỷ đi là bắt dựng lại từ đầu.
        self._huy_hen_nap_truoc()
        self._nhuong_duong_phat()
        self._bo_doc.index = 0
        self._bo_doc.phat()
        return None

    def moi_nghe_doan(self, so_doan):
        """Nghe riêng một đoạn: playlist chỉ có đoạn đó nên hết là tự dừng.

        Cách này KHÔNG đụng vào bo_doc.py. Bo_doc vốn đọc hết playlist rồi
        dừng - cho nó playlist một đoạn là ra đúng hành vi "nghe hết đoạn thì
        dừng" mà đặc tả yêu cầu.
        """
        if not self._bo_mo_hinh.san_sang:
            return {"loi": "Mô hình chưa sẵn sàng"}
        n = int(so_doan)
        playlist, ban_do = self._dung_playlist([n])
        if not playlist:
            return {"loi": "Đoạn này không có chữ để đọc"}
        # Bỏ lượt nạp trước còn đang HẸN để nó khỏi tranh CPU với vòng đọc.
        # Cái đã gửi vào pool thì cứ để chạy nốt - vòng đọc sắp lấy đúng nó ra
        # dùng, huỷ đi là bắt dựng lại từ đầu.
        self._huy_hen_nap_truoc()
        self._nhuong_duong_phat()
        self._bo_doc.dat_playlist(playlist, self._cfg)
        self._playlist, self._doan_cua_mau = playlist, ban_do
        self._nghe_rieng = True
        self._bo_doc.phat()
        return None

    def moi_tam_dung(self):
        self._bo_doc.tam_dung()
        return None

    def moi_doc_tiep(self):
        if not self._bo_mo_hinh.san_sang:
            return None
        # Bỏ lượt nạp trước còn đang HẸN để nó khỏi tranh CPU với vòng đọc.
        # Cái đã gửi vào pool thì cứ để chạy nốt - vòng đọc sắp lấy đúng nó ra
        # dùng, huỷ đi là bắt dựng lại từ đầu.
        self._huy_hen_nap_truoc()
        self._nhuong_duong_phat()
        self._bo_doc.phat()
        return None

    def moi_dung(self):
        self._bo_doc.dung()
        return None

    def doi_giong(self, ma):
        """Đổi giọng xong thì nạp trước lại: cap_nhat_cfg vừa xoá sạch cache,
        không nạp lại là lần bấm Nghe kế tiếp phải chờ tổng hợp từ đầu."""
        kq = super().doi_giong(ma)
        self._nap_truoc_mau_dau()
        return kq

    def _day_mo_hinh(self, patch: dict):
        """Mô hình vừa sẵn sàng thì nạp trước ngay.

        Lúc mở chương trình, giao diện gửi văn bản sang trước khi mô hình kịp
        bật, nên _nap_truoc_mau_dau lần đó không làm gì được. Đây là nhịp thứ
        hai để bắt lại.
        """
        super()._day_mo_hinh(patch)
        if (patch or {}).get("model", {}).get("trangThai") == "san_sang":
            self._nap_truoc_mau_dau()

    def cua_so(self, hanh_dong):
        """Nút phóng to phải ĐO cửa sổ, đừng đoán.

        Bản cũ giữ một cờ `_phong_to` khởi tạo bằng True, nên lần bấm ĐẦU TIÊN
        lại là thu nhỏ - người dùng bấm nút hình vuông mong to ra thì thấy nó
        nhỏ đi. Tệ hơn: kéo cửa sổ bằng chuột xong thì cờ sai hẳn và nút đảo
        chiều lung tung.

        Đo bằng GetWindowRect của Windows: đang lấp gần kín vùng làm việc thì
        thu về cỡ vừa, còn lại thì phóng cho kín. Kéo tay kiểu gì nút cũng làm
        đúng cái người dùng đang nhìn thấy.

        Vẫn KHÔNG dùng maximize(): với cửa sổ không khung nó phủ luôn lên thanh
        tác vụ, che mất đồng hồ và nút Start.
        """
        if self._window is None or hanh_dong != "phong_to":
            return super().cua_so(hanh_dong)

        x, y, rong, cao = self._vung
        hien = self._do_cua_so()
        # Ngưỡng 24 px: cửa sổ vừa phóng có thể lệch vài pixel vì viền/DPI.
        dang_kin = hien is not None and hien[0] >= rong - 24 and hien[1] >= cao - 24

        if dang_kin:
            rong2, cao2 = min(1280, rong - 80), min(800, cao - 80)
            self._window.resize(rong2, cao2)
            self._window.move(x + (rong - rong2) // 2, y + (cao - cao2) // 2)
        else:
            self._window.resize(rong, cao)
            self._window.move(x, y)
        self._phong_to = not dang_kin
        return None

    # Tiêu đề cửa sổ, đúng chuỗi truyền cho webview.create_window trong
    # GiongViet.py. Để một chỗ duy nhất: hai hàm dưới đây đều dò cửa sổ theo
    # tên, đổi tên ở một nơi mà quên nơi kia là nút phóng to và kéo mép cùng
    # chết lặng, không báo lỗi gì.
    TEN_CUA_SO = "Giọng Việt"

    @classmethod
    def _tim_hwnd(cls):
        import ctypes
        return ctypes.windll.user32.FindWindowW(None, cls.TEN_CUA_SO)

    @classmethod
    def _do_cua_so(cls):
        """(rộng, cao) cửa sổ tính bằng PIXEL LOGIC, hoặc None nếu không hỏi được.

        PHẢI quy đổi DPI. GetWindowRect trả pixel VẬT LÝ, còn window.resize()
        nhận pixel LOGIC - đúng cái bẫy đã ghi trong CLAUDE.md. Máy chủ dự án
        chạy 125%, nên cửa sổ 1020x640 logic hiện ra 1275x800 vật lý; so thẳng
        hai con số ấy với nhau là lúc nào cũng thấy "đang kín" và nút phóng to
        đứng im. Đo được: bấm lần hai không nhúc nhích.
        """
        try:
            import ctypes
            from ctypes import wintypes
            hwnd = cls._tim_hwnd()
            if not hwnd:
                return None
            r = wintypes.RECT()
            ctypes.windll.user32.GetWindowRect(hwnd, ctypes.byref(r))
            ty_le = 1.0
            try:
                dpi = ctypes.windll.user32.GetDpiForWindow(hwnd)
                if dpi:
                    ty_le = dpi / 96.0
            except (OSError, AttributeError):
                pass          # Windows cũ không có hàm này; coi như 100%
            return (round((r.right - r.left) / ty_le),
                    round((r.bottom - r.top) / ty_le))
        except (OSError, AttributeError, ImportError):
            return None

    def _don_dep(self):
        # Hẹn giờ là luồng riêng: không huỷ thì đóng cửa sổ xong nó vẫn nổ và
        # gọi vào một Speaker đã tắt.
        self._huy_hen_nap_truoc()
        super()._don_dep()

    def moi_nghe_cau(self, cau):
        """Nghe thử một nội dung cụ thể bằng giọng đang dùng.

        Màn Từ điển phát âm cần nghe đúng cách đọc vừa gõ trước khi lưu. Vẫn
        đi qua BoNgheThu sẵn có nên không đẻ thêm nguồn phát tiếng nào.
        """
        if not self._bo_mo_hinh.san_sang or not str(cau or "").strip():
            return None
        self._bo_doc.tam_dung()
        self._bo_nghe_thu.phat(self._cfg, self._cfg.get("vieneu_voice_id", ""),
                               str(cau), self._loc_am)
        return None

    def moi_dat_chinh_am(self, chinh):
        """Ba thanh Tốc độ · Cao độ · Âm lượng của hồ sơ đang dùng.

        Giao diện giữ ba con số ấy trong hoso-v2.json và gọi sang đây mỗi khi
        chúng đổi, cùng một lần lúc mở chương trình. Trước đây KHÔNG có đường
        này: kéo thanh thì con số được ghi xuống hồ sơ tử tế, mà tiếng phát ra
        không đổi một li - đúng nghĩa nút giả.

        Đổi ngay giữa lúc đang đọc cũng không sao: mẩu đang phát nghe hết bằng
        bộ lọc cũ, mẩu kế đã theo bộ mới. Dừng phát để áp cho đúng từ đầu thì
        người dùng mất chỗ đang nghe, đắt hơn nhiều so với một mẩu lệch.
        """
        self._chinh_am = dict(chinh or {})
        self._loc_am = am_thanh_loc.chuoi_loc(self._chinh_am)
        self._bo_doc.loc_am = self._loc_am
        return {"loc": self._loc_am, "moTa": am_thanh_loc.mo_ta(self._chinh_am)}

    def moi_dung_nghe_thu(self):
        """Tắt tiếng nghe thử giữa chừng.

        Api cũ không có cửa nào làm việc này: bản cũ chỉ dừng nghe thử khi
        người dùng bấm nghe thử giọng khác. Giao diện mới có nút bấm-lần-nữa-
        để-dừng nên cần đúng một lời gọi. KHÔNG phải nguồn phát mới - vẫn là
        BoNgheThu đã có, chỉ gọi hàm dung() sẵn có của nó.
        """
        self._bo_nghe_thu.dung()
        return None

    # ------------------------------------------------------------ khởi động

    def moi_khoi_dong(self):
        """Giao diện gọi ngay khi mở cửa sổ. BẮT BUỘC — thiếu là câm tiếng.

        Api.khoi_dong() của bản cũ làm ba việc: nạp giọng nhanh, dựng lại
        playlist theo chế độ cũ, bật mô hình. Ở đây bỏ việc giữa: playlist của
        giao diện mới đến từ moi_dat_doan chứ không từ tệp congduc/vanban, nên
        dựng lại theo chế độ cũ vừa thừa vừa đọc nhầm tệp danh sách công đức.
        """
        self._nap_giong_nhanh()
        self._bo_mo_hinh.bat_dau()
        return self.moi_danh_sach_giong()

    # ------------------------------------------------------------ nạp văn bản

    def moi_dan_van_ban(self):
        """Ctrl+V — lấy văn bản từ clipboard, trả về mảng đoạn."""
        text = he_thong.doc_clipboard()
        if not (text or "").strip():
            return {"loi": "Clipboard đang trống. Hãy bôi đen văn bản ở nơi khác, "
                           "bấm Ctrl+C, rồi quay lại bấm Dán văn bản."}
        return {"ten": "Văn bản đã dán", "duongDan": "",
                "doan": van_ban_thanh_doan(text)}

    def moi_mo_tep(self):
        """Mở hộp thoại chọn tệp, đọc .txt / .md / .csv / .docx."""
        chon = self._window.create_file_dialog(
            webview.OPEN_DIALOG,
            file_types=("Tệp văn bản (*.txt;*.md;*.csv;*.docx)", "Tất cả tệp (*.*)"))
        if not chon:
            return None
        return self.moi_doc_tep(chon[0])

    # ------------------------------------------------------------ danh sách công đức

    def moi_mo_danh_sach(self):
        """Mở tệp danh sách tên và số tiền — chức năng gốc của chương trình.

        Khác hẳn mở văn bản thường: mỗi dòng là một người, engine dựng câu từ
        mẫu trong lời dẫn ("{ten}, {tien}."), chèn lời mở đầu / lời giữa / lời
        kết, và cứ mấy người thì nghỉ dài một nhịp. Toàn bộ phần khó đó đã nằm
        trong engine.build_playlist_congduc, ở đây chỉ nối vào.
        """
        chon = self._window.create_file_dialog(
            webview.OPEN_DIALOG,
            file_types=("Tệp danh sách (*.txt;*.csv)", "Tất cả tệp (*.*)"))
        if not chon:
            return None
        return self.moi_doc_danh_sach(chon[0])

    def moi_doc_danh_sach(self, duong_dan):
        """Đọc một tệp danh sách. Tách riêng để kéo thả tệp cũng dùng lại được."""
        p = Path(duong_dan)
        try:
            records, canh_bao = engine.parse_data_file(p)
        except FileNotFoundError:
            return {"loi": f"Không tìm thấy tệp:\n{p}"}
        except OSError as e:
            return {"loi": f"Không mở được tệp: {e}"}
        if not records:
            return {"loi": "Tệp này không có dòng nào đọc được. Mỗi dòng cần "
                           "một tên, có thể kèm số tiền."}

        self._records, self._canh_bao = records, canh_bao
        self._loai_tai_lieu = "congduc"
        self._nap_noi_dung()          # lời dẫn đi theo hồ sơ đang mở
        self._trong_so_cache.clear()
        self._moc_phat = None

        self._playlist = engine.build_playlist_congduc(
            records, self._noidung, self._cfg, self._tudien)
        self._doan_cua_mau = list(range(1, len(self._playlist) + 1))
        self._doan = [{"kieu": self._kieu_doan(s), "chu": self._chu_doan(s)}
                      for s in self._playlist]
        self._bo_doc.dat_playlist(self._playlist, self._cfg)
        self._nghe_rieng = False
        self._nap_truoc_mau_dau()

        so_nguoi = sum(1 for r in records if r.get("kind") == "nguoi")
        return {"ten": p.name, "duongDan": str(p), "loai": "congduc",
                "doan": self._doan, "soNguoi": so_nguoi,
                "canhBao": list(canh_bao or [])}

    @staticmethod
    def _kieu_doan(seg) -> str:
        """Lời dẫn và tiêu đề hiện đậm như tiêu đề; tên người là dòng thường."""
        return "head" if seg.get("loai") in ("tieude", "mo_dau", "giua", "ket") \
            else "body"

    @staticmethod
    def _chu_doan(seg) -> str:
        """Chữ hiện lên màn hình cho một mẩu của danh sách.

        Với dòng người thì hiện TÊN VÀ SỐ TIỀN như trong tệp, không hiện câu
        engine đã dựng - người dùng đang dò theo danh sách của họ, thấy
        "Nguyễn Văn A, năm trăm nghìn đồng." thay vì "Nguyễn Văn A — 500.000"
        là mất dấu ngay.
        """
        rec = seg.get("rec")
        if rec and seg.get("loai") == "nguoi":
            tien = engine.format_money_for_display(rec.get("amount", ""))
            ten = str(rec.get("name", "")).strip()
            return f"{ten} — {tien}" if tien else ten
        if rec:
            return str(rec.get("name", "")).strip()
        return str(seg.get("text", "")).strip()

    def moi_doc_tep(self, duong_dan):
        """Đọc một tệp thành mảng đoạn. Tách riêng khỏi moi_mo_tep để kéo thả
        tệp vào cửa sổ cũng dùng lại được."""
        p = Path(duong_dan)
        try:
            if p.suffix.lower() == ".docx":
                import docx
                text = "\n".join(x.text for x in docx.Document(p).paragraphs)
            else:
                text = p.read_text(encoding="utf-8-sig", errors="replace")
        except ImportError:
            return {"loi": "Chưa đọc được tệp .docx trên máy này."}
        except OSError as e:
            return {"loi": f"Không mở được tệp: {e}"}
        return {"ten": p.name, "duongDan": str(p), "doan": van_ban_thanh_doan(text)}

    # ------------------------------------------------------------ dữ liệu cho giao diện

    def moi_danh_sach_giong(self):
        """Giọng THẬT trên máy, đổi sang hình dạng giao diện mới cần.

        Bản mock có sẵn tên đẹp (Ngọc Linh, Bình An…) nhưng đó là giọng tưởng
        tượng. Máy này cài giọng nào thì đọc bằng giọng đó.
        """
        ds = []
        for v in self._voices:
            ten = v["ten"]
            mo_ta = v.get("mo_ta", "")

            # du_lieu._tach_nhan_giong đã gói giới tính vào ngoặc sau tên
            # ("Phạm Tuyên (Nam)") và để vùng miền + phong cách ở mô tả
            # ("Miền Bắc · Phong cách tin tức"). Tách lại thành trường riêng để
            # giao diện xếp nhóm và sắp thứ tự được.
            m = re.search(r"\(([^)]+)\)\s*$", ten)
            gioi = m.group(1).strip() if m else ""
            ten_goc = re.sub(r"\s*\([^)]+\)\s*$", "", ten).strip()

            phan = [p.strip() for p in mo_ta.split("·") if p.strip()]
            vung = phan[0] if phan else ""
            tinh = " · ".join(phan[1:]) if len(phan) > 1 else ""

            ds.append({
                "ma": v["id"],
                "ten": ten_goc or ten,          # tên trơ, không kèm ngoặc
                "gioi": gioi,                   # Nam | Nữ
                "vung": vung,                   # Miền Bắc | Miền Trung | Miền Nam
                "tinh": tinh,                   # Phong cách tin tức…
                "rieng": bool(v.get("rieng")),
                # Dòng phụ dựng sẵn, giao diện chỉ việc in ra.
                "ngan": " · ".join(x for x in (gioi, vung, tinh) if x)
                        or ("Giọng của tôi" if v.get("rieng") else ""),
            })
        return {"giong": ds, "dangDung": self._cfg.get("vieneu_voice_id", "")}

    def moi_goi_y_xuat(self, ten_tep=""):
        """Gợi ý cho hộp thoại xuất, dựa trên playlist đang có."""
        goi = self.goi_y_xuat_file()
        if ten_tep:
            goi["ten"] = Path(ten_tep).stem or goi["ten"]
        goi["mo_ta"] = (f"{ten_tep or 'Văn bản'} · {len(self._doan)} đoạn · "
                        f"{self._cfg.get('vieneu_voice_id', '')}")
        # Ghi đè phần ước tính của lớp cha: ba kiểu tách của nó là của danh
        # sách công đức (một tệp / mỗi 20 mục / mỗi dòng), không phải ba kiểu
        # trong đặc tả màn hình 3.
        goi["tach"] = xuat_moi.uoc_tinh(self._playlist, self._so_doan_co_tieng())
        return goi

    def _so_doan_co_tieng(self) -> int:
        """Số đoạn thật sự ra tiếng — đúng bằng số tệp khi chọn 'mỗi đoạn'.

        Đếm theo _doan_cua_mau chứ không theo len(self._doan): đoạn rỗng đã bị
        loại khỏi playlist, đếm cả chúng là hứa nhiều tệp hơn số tệp sẽ đẻ ra.
        """
        return len(set(self._doan_cua_mau)) or 1

    def moi_bat_dau_xuat(self, ten, thu_muc, tach, dinh_dang):
        """Xuất thật. Trả về lỗi dạng chữ, hoặc None nếu đã bắt đầu chạy.

        Dừng vòng đọc trước khi chạy: Speaker chỉ có MỘT worker, để hai bên
        cùng xếp hàng thì cả hai cùng chậm gấp đôi, mà người dùng đang nhìn
        thanh tiến trình xuất nên tưởng máy treo.
        """
        if not self._playlist:
            return "Chưa có nội dung nào để xuất."
        if self._bo_xuat_moi.dang_chay:
            return "Đang xuất một tệp khác, xin đợi hoặc bấm Huỷ."
        if dinh_dang not in xuat_moi.DINH_DANG:
            return "Không hiểu định dạng được chọn."
        # Có chỉnh âm thì WAV 16 bit cũng phải qua ffmpeg, nên đừng chỉ nhìn
        # định dạng mà kết luận là không cần.
        can_ffmpeg = bool(xuat_moi.DINH_DANG[dinh_dang]["ma"]) or bool(self._loc_am)
        if can_ffmpeg and not xuat_moi.duong_ffmpeg(self._cfg).exists():
            # Thà nói thẳng còn hơn để người dùng nhìn thanh tiến trình chạy
            # hết rồi mới báo hỏng.
            return ("Máy thiếu ffmpeg nên chưa xuất được. Hãy chọn WAV 16 bit "
                    "và đưa ba thanh chỉnh về mặc định.") if self._loc_am else \
                   "Máy thiếu ffmpeg nên chỉ xuất được WAV 16 bit."

        self._nhuong_duong_phat()
        self._bo_doc.dung(giu_vi_tri=True)
        self._tuy_chon["thu_muc_xuat"] = thu_muc
        he_thong.luu_tuy_chon(self._tuy_chon)
        self._bo_xuat_moi.bat_dau(
            self._playlist, self._doan_cua_mau, self._cfg,
            str(ten), str(thu_muc), str(tach), str(dinh_dang), self._loc_am)
        return None

    def moi_huy_xuat(self):
        self._bo_xuat_moi.huy()
        return None

    def moi_luu_van_ban(self, ten_tep, noi_dung):
        """Ctrl+S — ghi văn bản ra đĩa, KHÔNG đè bản gốc của người dùng.

        Lần lưu đầu của mỗi tệp đẻ ra một bản đánh số kiểu Explorer
        ("thongbao (1).txt"); các lần sau ghi đè chính bản ấy, không thì soạn
        một buổi là thư mục đầy "(1) (2) (3)". luu_tep.py lo phần đó, đây chỉ
        cần nhớ tệp nào đã là bản của mình.

        Chỗ lưu: LUÔN là Tài liệu\\GiongViet, không phải cạnh tệp gốc. Lý do là
        bên Python không biết tệp gốc nằm đâu: WebView2 không cho biết đường
        dẫn thật của tệp kéo thả vào (đo ở phép thử mốc 0), và văn bản dán từ
        clipboard thì vốn chẳng có đường dẫn nào. Giao diện có giữ S.duongDanTep
        cho vài trường hợp mở tệp, nhưng nó không được gửi sang đây - muốn lưu
        cạnh tệp gốc thì phải gửi kèm, và đó là việc của lượt sau.
        """
        ten = str(ten_tep or "vanban.txt").strip() or "vanban.txt"
        if not Path(ten).suffix:
            ten += ".txt"
        # Đã lưu tệp này rồi thì ghi đè ĐÚNG bản mình đẻ ra lần trước, chứ
        # không phải tên gốc: truyền tên gốc vào là mỗi lần Ctrl+S lại né sang
        # một số mới, đúng cái luu_tep.py cố tránh.
        cu = self._da_luu.get(ten)
        dich = Path(cu) if cu else (luu_tep.thu_muc_mac_dinh() / Path(ten).name)
        try:
            that = luu_tep.luu(dich, str(noi_dung or ""), da_la_ban_cua_ta=bool(cu))
        except OSError as e:
            nhat_ky.ghi_loi(f"lưu văn bản {ten}", e)
            return None
        self._da_luu[ten] = str(that)
        return {"ten": that.name, "duongDan": str(that)}

    def moi_chia_tu(self, so_doan):
        """Chữ kèm mốc [b, e] của một đoạn, để tô chạy theo tiếng.

        Dùng chung _chia_tu với bản cũ nên hai giao diện tô giống hệt nhau.
        """
        n = int(so_doan)
        if not (0 < n <= len(self._doan)):
            return []
        return _chia_tu(str(self._doan[n - 1].get("chu", "")))

    def moi_trang_thai_dau(self):
        """Thông tin giao diện cần ngay lúc mở: giọng và tình trạng mô hình."""
        return {
            "giong": self._voices,
            "giongDangDung": self._cfg.get("vieneu_voice_id", ""),
            "moHinhSanSang": bool(self._bo_mo_hinh.san_sang),
            "moHinhLoi": self._bo_mo_hinh.loi or "",
        }

    # ------------------------------------------------------------ cài đặt

    # Mã vùng biên của Windows. Gửi đúng mã là hệ điều hành tự lo phần kéo:
    # bám con trỏ, vẽ khung xem trước, tôn trọng min_size, snap ra mép màn
    # hình. Tự tính bằng JS thì mất hết những thứ đó và kéo lúc nào cũng giật.
    VIEN = {"trai": 10, "phai": 11, "tren": 12, "trentrai": 13, "trenphai": 14,
            "duoi": 15, "duoitrai": 16, "duoiphai": 17}

    def moi_keo_vien(self, ma):
        """Bắt đầu kéo đổi cỡ cửa sổ từ một mép hoặc góc.

        Cửa sổ dựng frameless nên không có viền sẵn để kéo. Giao diện tự vẽ
        tám dải mỏng ở mép; chạm vào dải nào thì gọi sang đây, rồi chuyển tiếp
        cho Windows đúng như khi người dùng kéo viền của một cửa sổ bình thường.

        PHẢI GẮN LUỒNG TRƯỚC — chỗ này đã hỏng suốt và không ai thấy.

        Đo được (2026-08-13): pywebview chạy mỗi lời gọi js_api trên một luồng
        riêng — luồng 35884, trong khi luồng UI của cửa sổ là 26696. Mà
        ReleaseCapture() theo tài liệu Win32 chỉ giải phóng chuột CỦA LUỒNG
        GỌI NÓ. Gọi từ luồng js_api thì nó không đụng được vào con chuột mà
        WebView2 đang giữ ở luồng UI, nên WM_NCLBUTTONDOWN có gửi sang cũng vô
        ích: vòng kéo của Windows không nhận được chuyển động chuột nào.

        AttachThreadInput ghép hai luồng dùng chung trạng thái bàn phím/chuột,
        lúc ấy ReleaseCapture mới với tới. Chủ dự án đã kéo thử hai cách cạnh
        nhau: cách cũ không nhúc nhích, cách này kéo được cả bốn mép và bốn góc.

        SendMessageW chứ không PostMessageW: phải vào vòng kéo NGAY trong lúc
        hai luồng còn đang gắn nhau. Nó chặn đến khi người dùng buông chuột —
        không sao, vì mỗi lời gọi js_api có luồng riêng.
        """
        vung = self.VIEN.get(str(ma or ""))
        if vung is None or self._window is None:
            return None
        try:
            import ctypes
            u = ctypes.windll.user32
            hwnd = self._tim_hwnd()
            if not hwnd:
                return None
            tid_ui = u.GetWindowThreadProcessId(hwnd, None)
            tid_js = ctypes.windll.kernel32.GetCurrentThreadId()
            u.AttachThreadInput(tid_js, tid_ui, True)
            try:
                u.ReleaseCapture()
                u.SendMessageW(hwnd, 0x00A1, vung, 0)   # WM_NCLBUTTONDOWN
            finally:
                # Gỡ trong finally: bỏ sót một lần là luồng js_api ấy chết đi
                # mà trạng thái input hai luồng vẫn còn dính vào nhau.
                u.AttachThreadInput(tid_js, tid_ui, False)
        except (OSError, AttributeError, ImportError):
            return None
        return None

    def moi_cua_so_kin(self):
        """Cửa sổ đang lấp kín vùng làm việc chưa — để nút đổi icon cho đúng."""
        hien = self._do_cua_so()
        if hien is None:
            return False
        _x, _y, rong, cao = self._vung
        return hien[0] >= rong - 24 and hien[1] >= cao - 24

    def moi_cai_dat(self):
        """Màn hình 6.

        Truyền loại "vanban" chứ không để rỗng: cai_dat.du_lieu sẽ lọc bỏ
        `nhan_manh_tien` - thiết lập ấy chỉ có nghĩa với danh sách công đức,
        mà bản mới chưa có chế độ đó. Bày ra là một công tắc bấm không đổi gì.
        """
        return cai_dat.du_lieu(self._cfg, self._tuy_chon, "vanban", "")

    def moi_dat_cai_dat(self, khoa, gia_tri):
        """Đổi một thiết lập rồi trả bảng đã cập nhật.

        Chỉ nhận các khoá thuộc CÁCH ĐỌC. Màu nền và cỡ chữ do giao diện tự
        giữ trong hoso-v2.json - gửi sang đây nữa là hai nơi cùng nhớ một thứ,
        và có ngày chúng lệch nhau.
        """
        cho_phep = {"doc_so_bang_chu", "bo_markdown"}
        if khoa not in cho_phep:
            return None
        moi = bool(gia_tri)
        if moi == bool(self._cfg.get(khoa)):
            return self.moi_cai_dat()
        self._cfg[khoa] = moi
        engine.save_config(self._cfg)
        self._bo_doc.cap_nhat_cfg(self._cfg)
        if self._doan:
            self.moi_dat_doan(self._doan)      # cách đọc đổi -> dựng lại
        return self.moi_cai_dat()

    def moi_chon_thu_muc_xuat(self):
        """Mở hộp thoại chọn thư mục xuất mặc định."""
        chon = self._window.create_file_dialog(webview.FOLDER_DIALOG)
        if not chon:
            return None
        self._tuy_chon["thu_muc_xuat"] = str(chon[0])
        he_thong.luu_tuy_chon(self._tuy_chon)
        return self.moi_cai_dat()

    # ------------------------------------------------------------ từ điển phát âm

    def moi_tu_dien(self, tim=""):
        """Màn hình 5. Api cũ đã có sẵn tu_dien.du_lieu, dùng lại nguyên."""
        return tu_dien.du_lieu(self._tudien, str(tim or ""))

    def moi_sua_tu_dien(self, viec, tu, doc="", tu_cu=""):
        """Thêm / sửa / xoá một mục, rồi trả về bảng đã cập nhật.

        Gộp ba việc vào một cửa vì cả ba đều kết thúc giống hệt nhau: ghi
        tudien.ini, dựng lại playlist (cách đọc vừa đổi phải nghe thấy ngay),
        rồi trả bảng mới. Tách ba đường là ba chỗ phải nhớ làm đủ ba bước.
        """
        viec = str(viec or "")
        tu = str(tu or "").strip()
        doc = str(doc or "").strip()

        if viec == "xoa":
            if tu not in self._tudien:
                return None
            kq = self.xoa_tu(tu)
        elif viec == "sua":
            if not tu or not doc:
                return None
            kq = self.sua_tu(str(tu_cu or "").strip() or tu, tu, doc)
        elif viec == "them":
            if not tu or not doc:
                return None
            if tu in self._tudien:
                # Thêm chữ đã có thì coi như sửa - đỡ bắt người dùng tự nhớ
                # mình đã dạy máy chữ này chưa.
                kq = self.sua_tu(tu, tu, doc)
            else:
                kq = self.them_tu(tu, doc)
        else:
            return None

        if kq is None:
            return None
        # Cách đọc đổi thì chuỗi engine đọc cũng đổi - dựng lại để màn Soát và
        # lần bấm Nghe kế tiếp không còn dùng bản cũ.
        if self._doan:
            self.moi_dat_doan(self._doan)
        return self.moi_tu_dien()

    # ------------------------------------------------------------ thư viện giọng

    def moi_thu_vien_giong(self, dang_dung=""):
        """Số liệu cho màn hình 4.

        `dang_dung` do giao diện gửi sang chứ không lấy từ cfg: ở bản mới mỗi
        HỒ SƠ giữ giọng riêng của nó, còn cfg chỉ là giọng của lần phát gần
        nhất. Lấy nhầm cfg là thẻ "Đang dùng" sáng ở giọng khác với giọng cột
        phải đang ghi.
        """
        if not self._voices:
            self._nap_giong_nhanh()
        return thu_vien_giong.du_lieu(self._voices,
                                      str(dang_dung or ""))

    # ------------------------------------------------------------ soát văn bản

    def moi_soat(self):
        """Số liệu cho màn hình 2. Soát lại mỗi lần mở - văn bản có thể vừa
        được sửa bằng Tìm-thay-thế."""
        return soat_moi.du_lieu(self._doan, self._playlist, self._doan_cua_mau,
                                self._tudien, self._cfg)

    def moi_dat_quy_tac(self, khoa, bat):
        """Bật/tắt một quy tắc chuẩn hoá.

        Chỉ nhận đúng các khoá mà soat_moi khai là đổi được - giao diện gửi
        khoá lạ thì bỏ qua chứ không ghi bừa vào cấu hình.
        """
        cho_phep = {q["congTac"] for q in soat_moi.QUY_TAC if q["congTac"]}
        if khoa not in cho_phep:
            return None
        self._cfg[khoa] = bool(bat)
        # Đổi cách chuẩn hoá là chuỗi engine đọc cũng khác - dựng lại playlist
        # rồi trả số liệu mới, không thì tab 2 vẫn hiện bản cũ.
        self.moi_dat_doan(self._doan)
        return self.moi_soat()

    # ------------------------------------------------------------ hồ sơ bản mới

    def moi_doc_ho_so(self):
        """Hồ sơ đã lưu lần trước, hoặc None nếu máy này chưa từng lưu.

        None KHÔNG phải lỗi: lần chạy đầu tiên thì giao diện dựng bốn hồ sơ
        mẫu như trước.
        """
        return ho_so_v2.doc()

    def moi_luu_ho_so(self, du_lieu):
        """Ghi hồ sơ, tab, ba thanh điều chỉnh và thẻ cảm xúc xuống đĩa.

        Đi thẳng vào hoso-v2.json. Không dùng lại đường của Api cũ: đường đó
        ghi đè hoso.json và cauhinh.ini của bản anh đang dùng hằng ngày, và
        toàn bộ đường đó đã bị khoá lại - xem giaodien_moi/khoa_du_lieu.py.
        """
        return ho_so_v2.luu(du_lieu)

    # ------------------------------------------------------------ dịch vị trí

    def _day(self, patch: dict):
        """Chặn giữa đường đẩy trạng thái, dịch vị trí playlist -> SỐ ĐOẠN.

        BoDoc đếm theo mẩu trong playlist. Giao diện đếm theo đoạn. Một đoạn
        dài bị cắt làm ba mẩu thì BoDoc báo pos 5, 6, 7 mà giao diện vẫn phải
        sáng đúng một đoạn. Dịch ở đây, một chỗ duy nhất.

        Gửi kèm `tu`/`den`: phần chữ mà MẨU NÀY đọc, tính theo tỉ lệ trong
        đoạn. Giao diện tô đúng khúc đó với đúng thời lượng WAV của nó, thay vì
        chia đều cả đoạn.
        """
        if isinstance(patch, dict) and "pos" in patch:
            patch = dict(patch)
            i = int(patch["pos"]) - 1
            if 0 <= i < len(self._doan_cua_mau):
                n = self._doan_cua_mau[i]
                patch["doan"] = n
                patch.update(self._pham_vi_mau(i, n))
            patch["ngheRieng"] = self._nghe_rieng
            self._cap_nhat_tre(patch)
            if patch.get("thoiLuong"):
                patch["treMs"] = self._tre_ms
        super()._day(patch)

    def _cap_nhat_tre(self, patch: dict):
        """Tự đo khoảng loa còn im, bằng chính nhịp đi của vòng đọc.

        bo_doc đẩy gói kèm thoiLuong NGAY TRƯỚC khi gọi speaker.play, mà play
        thì chặn đến lúc phát xong, rồi mới nghỉ và đẩy gói của mẩu kế. Nên:

            phát thật = t(mẩu kế) - t(mẩu này) - nghỉ
            trễ       = phát thật - thoiLuong

        ffplay chạy với -autoexit nên nó thoát ngay khi hết audio; vì thế toàn
        bộ phần dôi ra nằm ở ĐẦU, lúc loa còn im. Đó đúng là khoảng chữ phải
        đứng đợi.

        Đo bằng chính máy đang chạy nên tự hợp với máy yếu, máy mạnh, và với
        cả lúc máy đang bận việc khác.
        """
        pos = int(patch.get("pos", 0))
        if patch.get("thoiLuong"):
            self._moc_phat = (time.time(), pos, float(patch["thoiLuong"]),
                              self._nghi_cua_mau(pos))
            return
        moc = self._moc_phat
        if not moc or pos != moc[1] + 1:
            return
        self._moc_phat = None
        tre = ((time.time() - moc[0]) - moc[3] - moc[2]) * 1000
        if not TRE_THAP_NHAT_MS <= tre <= TRE_CAO_NHAT_MS:
            return
        self._tre_da_do.append(tre)
        del self._tre_da_do[:-SO_LAN_NHO_TRE]
        self._tre_ms = int(statistics.median(self._tre_da_do))

    def _nghi_cua_mau(self, pos: int) -> float:
        seg = self._playlist[pos - 1] if 0 < pos <= len(self._playlist) else {}
        try:
            return float(seg.get("nghi", 0) or 0)
        except (TypeError, ValueError):
            return 0.0

    def _pham_vi_mau(self, i: int, so_doan: int) -> dict:
        """Tỉ lệ [tu, den] của mẩu thứ i trong đoạn số `so_doan`, khoảng 0..1.

        Trả rỗng khi không tính được - giao diện hiểu là "tô cả đoạn", đúng
        như hành vi cũ, chứ không tô sai chỗ.
        """
        seg = self._playlist[i] if 0 <= i < len(self._playlist) else None
        d = self._doan[so_doan - 1] if 0 < so_doan <= len(self._doan) else None
        if not seg or not d or "tu" not in seg:
            return {}
        chu = str(d.get("chu", ""))
        if not chu:
            return {}

        trong_so = self._trong_so_doc(so_doan, chu)
        if trong_so:
            # PHẢI đo bằng cùng thước với `trongSo`. Giao diện đặt mốc từng chữ
            # theo trọng số âm tiết, nên phạm vi mẩu cũng phải tính theo âm
            # tiết. Trộn hai thước - phạm vi theo ký tự, mốc chữ theo âm tiết -
            # là chữ nhảy sai chỗ đúng bằng khoảng chênh giữa hai thước; đo
            # được 1,07 giây ngay ở chữ đầu mẩu.
            mau = self._mau_cua_doan(so_doan)
            truoc = 0
            for s in mau:
                if s is seg:
                    break
                truoc += len(str(s.get("goc", "")).split())
            rong = len(str(seg.get("goc", "")).split())
            tong = sum(trong_so)
            if tong > 0 and truoc + rong <= len(trong_so):
                tu = sum(trong_so[:truoc]) / tong
                den = sum(trong_so[:truoc + rong]) / tong
                return {"tu": round(max(0.0, min(1.0, tu)), 6),
                        "den": round(max(tu, min(1.0, den)), 6),
                        "trongSo": trong_so}

        # Không có trọng số thì cả hai bên cùng dùng thước ký tự.
        dai = len(chu)
        tu = max(0.0, min(1.0, seg["tu"] / dai))
        den = max(tu, min(1.0, seg["den"] / dai))
        return {"tu": round(tu, 6), "den": round(den, 6)}

    def _trong_so_doc(self, so_doan: int, chu: str) -> list:
        """Mỗi chữ hiển thị đọc ra bao nhiêu ÂM TIẾT - trọng số để tô.

        Chia đều theo ký tự hiển thị là sai gốc: "31/8/2026" chỉ 9 ký tự mà
        đọc thành "ngày ba mươi mốt tháng tám năm hai nghìn không trăm hai mươi
        sáu". Chữ ấy phải được tô lâu hơn hẳn chữ bên cạnh.

        Đếm ÂM TIẾT chứ không đếm ký tự: tiếng Việt đọc từng âm tiết một, nên
        số âm tiết bám sát thời gian đọc hơn nhiều.
        """
        cu = self._trong_so_cache.get(so_doan)
        if cu is not None:
            return cu
        ra = []
        for seg in self._mau_cua_doan(so_doan):
            ra.extend(self._am_tiet_tung_chu(str(seg.get("goc", ""))))
        # Số phần tử phải khớp số chữ của đoạn, không thì giao diện bỏ qua và
        # quay về chia đều. Thà chia đều còn hơn gán nhầm trọng số chữ này cho
        # chữ kia - lệch kiểu đó nhìn còn khó chịu hơn.
        if len(ra) != len(chu.split()):
            ra = []
        self._trong_so_cache[so_doan] = ra
        return ra

    def _mau_cua_doan(self, so_doan: int) -> list:
        return [s for j, s in enumerate(self._playlist)
                if j < len(self._doan_cua_mau) and self._doan_cua_mau[j] == so_doan]

    def _am_tiet_tung_chu(self, mau: str) -> list:
        """Âm tiết của từng chữ trong một mẩu, đo bằng cách chuẩn hoá TIỀN TỐ.

        Không chuẩn hoá từng chữ rời: ngữ cảnh đổi hẳn cách đọc. Đo thật trên
        "tổng đài 1900 6868." - cả câu engine đọc "Một chín không không, Sáu
        tám sáu tám" (8 âm tiết, đúng kiểu số điện thoại), tách rời từng chữ
        thì ra "một nghìn chín trăm" + "sáu nghìn tám trăm sáu mươi tám" (11
        âm tiết, sai hẳn). Chuẩn hoá dồn từ đầu mẩu rồi lấy phần chênh giữa hai
        bước liên tiếp thì ngữ cảnh còn nguyên.

        Mẩu tối đa vài chục chữ nên số lần chuẩn hoá vẫn nhỏ, và kết quả được
        nhớ lại theo đoạn.
        """
        tu = mau.split()
        if not self._can_dem_ky(mau):
            # Đường nhanh: tiếng Việt mỗi chữ đúng một âm tiết. Mẩu không có số
            # và không đụng từ điển thì chuẩn hoá chẳng đổi gì, khỏi phải hỏi
            # engine. Đo được: đoạn 624 chữ tốn 973 ms nếu hỏi engine từng bước,
            # mà đó là thời gian nằm chắn ngay trên đường đẩy gói tin.
            return [1] * len(tu)

        ra, truoc = [], 0
        for k in range(1, len(tu) + 1):
            doc = engine.chuan_hoa_van_ban(
                so_dien_thoai.chuan_hoa(" ".join(tu[:k])), self._tudien, self._cfg)
            n = len(doc.split())
            # Thêm một chữ có khi làm engine đọc lại phần trước theo kiểu khác
            # (bốn số rời thành số điện thoại) và tổng âm tiết TỤT xuống. Ép
            # không giảm, không thì mốc tô chạy giật lùi.
            ra.append(max(1, n - truoc))
            truoc = max(truoc, n)
        return ra

    def _can_dem_ky(self, mau: str) -> bool:
        """Mẩu này có gì đọc ra dài hơn chính nó không?

        Chỉ hai thứ làm chữ nở ra: CHỮ SỐ ("2/9" thành "ngày hai tháng chín")
        và mục trong từ điển người dùng ("TP.HCM" thành "Thành phố Hồ Chí
        Minh"). Không có cả hai thì mỗi chữ đúng một âm tiết.
        """
        if any(c.isdigit() for c in mau):
            return True
        if not self._tudien:
            return False
        thap = mau.lower()
        return any(k.lower() in thap for k in self._tudien)
