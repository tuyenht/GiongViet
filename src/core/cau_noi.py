# -*- coding: utf-8 -*-
"""Lớp Api — mọi thứ giao diện web gọi sang Python đều đi qua đây.

Không có logic đọc nào nằm ở file này; nó chỉ điều phối giữa engine
(DocCongDuc.py), bộ đọc, bộ xuất file và cửa sổ WebView.
"""

import json
import threading
from pathlib import Path

import webview

# Tương thích pywebview 5+ (khử cảnh báo deprecation OPEN_DIALOG / FOLDER_DIALOG)
DIALOG_OPEN = getattr(webview.FileDialog, "OPEN", getattr(webview, "OPEN_DIALOG", 10)) if hasattr(webview, "FileDialog") else getattr(webview, "OPEN_DIALOG", 10)
DIALOG_FOLDER = getattr(webview.FileDialog, "FOLDER", getattr(webview, "FOLDER_DIALOG", 20)) if hasattr(webview, "FileDialog") else getattr(webview, "FOLDER_DIALOG", 20)
DIALOG_SAVE = getattr(webview.FileDialog, "SAVE", getattr(webview, "SAVE_DIALOG", 30)) if hasattr(webview, "FileDialog") else getattr(webview, "SAVE_DIALOG", 30)

import DocCongDuc as engine

from . import (cai_dat, ds_giong, du_lieu, he_thong, ho_so, nhat_ky, soat,
               thu_vien_giong, tu_dien, xuat_file)
from .bo_doc import BoDoc
from .mo_hinh import BoNapMoHinh
from .nghe_thu import BoNgheThu
from .xuat_file import BoXuat

CHE_DO = [
    {"ma": "congduc", "ten": "Danh sách tên và số"},
    {"ma": "vanban", "ten": "Đọc văn bản"},
]


class Api:
    def __init__(self, vung_lam_viec=(0, 0, 1280, 800)):
        self._window = None
        self._vung = vung_lam_viec
        self._cfg = engine.load_config()
        self._tuy_chon = he_thong.doc_tuy_chon()
        self._noidung = engine.NoiDung()
        self._tudien = engine.load_tudien(engine.TUDIEN_FILE)

        # Hồ sơ đọc: cauhinh.ini vẫn giữ thiết lập đang dùng, hoso.json chỉ là
        # thư viện các bộ thiết lập đã đặt tên. Nạp hồ sơ đang mở vào cfg ngay
        # từ đây để mọi phần bên dưới không cần biết gì về hồ sơ.
        self._kho_ho_so = ho_so.doc(self._cfg)
        _hs = ho_so.tim(self._kho_ho_so, self._kho_ho_so["dangDung"])
        self._che_do = _hs["loai"] if _hs else "congduc"
        # Đồng bộ theo chiều cauhinh.ini -> hồ sơ, KHÔNG phải chiều ngược lại:
        # cauhinh.ini là thứ được ghi sau cùng, hoso.json chỉ là bản sao có
        # đặt tên. Đổ ngược vào là có ngày nuốt mất thay đổi của lần chạy
        # trước, ví dụ khi lần đó thoát bằng Alt+F4.
        if _hs:
            ho_so.cat_thiet_lap(self._kho_ho_so, self._cfg)
        self._nap_noi_dung()
        self._van_ban = ""
        self._playlist = []
        self._lines = []
        self._doc_name = ""
        self._doc_path = ""
        self._canh_bao = []
        self._records = []
        self._voices = []
        self._banner_text = ""
        self._loi = None
        self._dang_nhan_ban = False
        # Cửa sổ mở sẵn đã lấp kín vùng làm việc, nên lần bấm nút giữa đầu
        # tiên là thu về cỡ nhỏ.
        self._phong_to = True

        self._bo_doc = BoDoc(self._day)
        self._bo_nghe_thu = BoNgheThu(
            lambda ma: self._goi_js("window.gd.ngheThuXong", ma or ""),
            lambda msg: self._goi_js("window.gd.baoLoi",
                                     "Không nghe thử được", msg))
        self._bo_xuat = BoXuat(self._tien_do_xuat, self._xuat_xong,
                               self._xuat_loi, self._xuat_huy)
        self._bo_mo_hinh = BoNapMoHinh(self._day_mo_hinh)

    # ================================================== cầu nối sang giao diện

    def _goi_js(self, ma_lenh: str, *tham_so):
        if self._window is None:
            return
        tham_so_js = ", ".join(json.dumps(t, ensure_ascii=False) for t in tham_so)
        try:
            self._window.evaluate_js(f"{ma_lenh}({tham_so_js})")
        except Exception:
            pass

    def _day(self, patch: dict):
        self._goi_js("window.gd.push", patch)

    def _day_mo_hinh(self, patch: dict):
        self._day(patch)
        mo_hinh = patch.get("model") or {}
        if mo_hinh.get("trangThai") == "san_sang":
            # Nạp lại kể cả khi đã có danh sách đọc nhanh: lúc này mô hình đã
            # sẵn sàng nên gọi rất nhanh, và nó là nguồn chuẩn nhất.
            threading.Thread(target=self._nap_giong, daemon=True).start()

    def _nap_giong_nhanh(self):
        """Hiện danh sách giọng NGAY lúc mở chương trình.

        Không đợi mô hình: xem ds_giong.py. Trước đây người dùng phải nhìn
        dòng "Đang tải danh sách giọng…" suốt 25-40 giây."""
        try:
            ds = ds_giong.doc_nhanh()
        except Exception as e:
            nhat_ky.ghi_loi("đọc nhanh danh sách giọng", e)
            return
        if not ds:
            return
        self._voices = du_lieu.danh_sach_giong(ds)
        if not self._cfg.get("vieneu_voice_id"):
            self._cfg["vieneu_voice_id"] = self._voices[0]["id"]

    def _nap_giong(self):
        try:
            self._voices = du_lieu.danh_sach_giong(
                engine.lay_danh_sach_giong_day_du())
        except Exception as e:
            nhat_ky.ghi_loi("lấy danh sách giọng từ mô hình", e)
            self._day({"model": {"trangThai": "loi",
                                 "tieuDe": "Không lấy được danh sách giọng",
                                 "ghiChu": str(e)[:180], "phanTram": 0}})
            return
        if not self._cfg.get("vieneu_voice_id") and self._voices:
            self._cfg["vieneu_voice_id"] = self._voices[0]["id"]
        # Kèm luôn dữ liệu thư viện: danh sách giọng nạp xong sau khi cửa sổ
        # đã hiện, người dùng có thể đang đứng sẵn ở màn hình Thư viện giọng và
        # nhìn vào một trang trống.
        self._day({"voices": self._voices,
                   "voiceId": self._cfg.get("vieneu_voice_id", ""),
                   "thuVien": self._du_lieu_thu_vien()})

    # ================================================== trạng thái

    def _mo_ta_nguong_nhan_manh(self) -> str:
        """Nói thẳng ra ai sẽ được nhấn mạnh, đừng bắt người dùng đoán.

        Ngưỡng tính theo chính danh sách đang mở nên mỗi tệp một khác; không
        nói rõ thì người dùng bật lên rồi ngồi nghe xem có gì đổi không.
        """
        if self._che_do != "congduc" or not self._records:
            return ""
        nguong = engine.nguong_nhan_manh(self._records)
        if not nguong:
            return "Danh sách quá ít người nên chưa chia được nhóm."
        so = 0
        for r in self._records:
            if r.get("kind") != "nguoi":
                continue
            try:
                if engine.parse_money(r["amount"]) >= nguong:
                    so += 1
            except ValueError:
                continue
        return (f"Sẽ nhấn {so} người cúng từ "
                f"{engine.format_money_for_display(str(nguong))} đồng trở lên.")

    def _tom_tat_soat(self) -> dict:
        d = self._du_lieu_soat()
        return {"nang": d.get("nang", 0), "nhe": d.get("nhe", 0),
                "trong": bool(d.get("trong"))}

    def _toan_bo(self) -> dict:
        return {
            "theme": self._tuy_chon["theme"],
            "zoom": self._tuy_chon["zoom"],
            "mode": self._che_do,
            "hoSo": ho_so.du_lieu(self._kho_ho_so),
            "hoSoDangDung": self._kho_ho_so["dangDung"],
            "loaiHoSo": [dict(m) for m in CHE_DO],
            "state": self._trang_thai(),
            "lines": self._lines,
            "pos": self._bo_doc.index + 1 if self._lines else 0,
            "docName": self._doc_name or "Chưa mở tệp",
            "docMeta": self._mo_ta_tep(),
            "docPath": self._doc_path,
            "tongThoiLuong": engine.uoc_luong_thoi_gian(self._playlist, self._cfg)
                             if self._playlist else "",
            "voices": self._voices,
            "voiceId": self._cfg.get("vieneu_voice_id", ""),
            "styles": du_lieu.phong_cach(),
            "style": self._cfg.get("phong_cach", engine.PHONG_CACH_MAC_DINH),
            "sliders": du_lieu.thanh_truot(self._cfg, self._che_do),
            "nhanManhTien": bool(self._cfg.get("nhan_manh_tien")),
            "nguongNhanManh": self._mo_ta_nguong_nhan_manh(),
            # Tóm tắt soát ngay ở cột phải: đo được 11 ms cho danh sách 2000
            # dòng nên gọi mỗi lần cũng không sao, mà người dùng thấy ngay có
            # chỗ nào cần xem lại trước khi bấm đọc.
            "canhBao": self._tom_tat_soat(),
            "banner": self._banner_text,
            "loi": self._loi,
        }

    def _trang_thai(self) -> str:
        if self._loi:
            return "loi"
        if self._bo_doc.dang_doc:
            return "dang_doc"
        return "san_sang" if self._lines else "trong"

    def _mo_ta_tep(self) -> str:
        if not self._playlist:
            return ""
        phan = [f"{len(self._lines)} dòng"]
        if self._che_do == "congduc":
            so_nguoi = sum(1 for s in self._playlist if s.get("loai") == "nguoi")
            phan.insert(0, f"{so_nguoi} người")
        else:
            phan.insert(0, f"{len(self._van_ban.split())} từ")
        phan.append(f"khoảng {engine.uoc_luong_thoi_gian(self._playlist, self._cfg)}")
        return " · ".join(phan)

    # ================================================== dựng playlist

    def _dung_lai_playlist(self, giu_vi_tri=False):
        # Đổi nhịp đọc hay phong cách thì phải dựng lại playlist vì khoảng nghỉ
        # nằm sẵn trong từng đoạn. Nhưng đang nghe dở mà bị tắt ngang thì rất
        # khó chịu, nên nhớ lại và đọc tiếp ngay sau khi dựng xong.
        doc_tiep = giu_vi_tri and self._bo_doc.dang_doc
        vi_tri = self._bo_doc.index if giu_vi_tri else 0
        self._loi = None
        try:
            if self._che_do == "congduc":
                # Giữ lại records: giao diện cần nó để nói rõ ngưỡng nhấn mạnh
                # là bao nhiêu và bao nhiêu người rơi vào nhóm đó.
                self._records, self._canh_bao = engine.parse_data_file(
                    self._cfg["data_file"])
                self._playlist = engine.build_playlist_congduc(
                    self._records, self._noidung, self._cfg, self._tudien)
                self._doc_name = Path(self._cfg["data_file"]).name
                self._doc_path = str(self._cfg["data_file"])
            else:
                self._playlist = engine.build_playlist_vanban(
                    self._van_ban, self._cfg, self._tudien)
        except FileNotFoundError as e:
            self._playlist, self._canh_bao, self._records = [], [], []
            self._loi = {"tieu_de": "Không mở được tệp danh sách",
                        "chi_tiet": str(e),
                        "nut": [{"nhan": "Chọn tệp khác…", "act": "moFile"}]}
        except Exception as e:
            self._playlist, self._canh_bao, self._records = [], [], []
            self._loi = {"tieu_de": "Không đọc được nội dung",
                        "chi_tiet": str(e), "nut": []}

        self._lines = du_lieu.dong_hien_thi(self._playlist, self._che_do,
                                            self._tudien)
        self._bo_doc.dat_playlist(self._playlist, self._cfg)
        self._bo_doc.index = min(vi_tri, max(0, len(self._playlist) - 1))
        self._banner_text = self._banner()
        if doc_tiep and self._playlist:
            self._bo_doc.phat()

    def _banner(self) -> str:
        if not self._playlist or self._loi:
            return ""
        if self._canh_bao:
            return (f"Có {len(self._canh_bao)} dòng máy chưa hiểu số tiền, "
                    f"sẽ đọc nguyên văn. Ví dụ: {self._canh_bao[0]}")
        return ("Đã sẵn sàng. Bấm <strong>nút tròn xanh</strong> để nghe, "
                "hoặc bấm thẳng vào một dòng để đọc từ chỗ đó.")

    # ================================================== khởi động

    def khoi_dong(self):
        self._nap_giong_nhanh()
        self._dung_lai_playlist()
        self._bo_mo_hinh.bat_dau()
        return self._toan_bo()

    # ================================================== tệp và chế độ

    def _tep_noi_dung(self) -> Path:
        hs = ho_so.tim(self._kho_ho_so, self._kho_ho_so["dangDung"])
        return engine.BASE_DIR / ho_so.tep_noi_dung_cua(hs)

    def _nap_noi_dung(self):
        """Lời dẫn đi theo hồ sơ, không dùng chung nữa.

        Trước đây chỉ có một noidung.ini cho tất cả, nên tạo hồ sơ "Danh sách
        khen thưởng" xong nó vẫn đọc lời mở đầu của nhà chùa và mỗi dòng vẫn
        là "phát tâm công đức".
        """
        self._noidung = engine.NoiDung().load(self._tep_noi_dung())

    def _luu_kho_ho_so(self):
        """Cất thiết lập đang dùng vào hồ sơ đang mở rồi ghi ra đĩa."""
        ho_so.cat_thiet_lap(self._kho_ho_so, self._cfg)
        ho_so.luu(self._kho_ho_so)

    def _ghi_cau_hinh(self):
        """Cửa duy nhất để ghi cấu hình: vừa lưu cauhinh.ini, vừa cất vào hồ
        sơ đang mở.

        Nếu tách hai việc này ra thì sẽ có ngày quên một cái: chỉnh nhịp đọc,
        đóng chương trình, mở lại, chuyển hồ sơ qua rồi quay về - thiết lập cũ
        hiện lên vì hoso.json chưa hề biết gì về lần chỉnh đó.
        """
        engine.save_config(self._cfg)
        self._luu_kho_ho_so()

    def _vao_che_do(self, loai):
        self._bo_doc.dung()
        self._che_do = loai
        self._nap_noi_dung()          # lời dẫn đi theo hồ sơ vừa chuyển sang
        if loai == "vanban" and not self._van_ban:
            self._playlist, self._lines = [], []
            self._doc_name, self._doc_path = "", ""
            self._banner_text = ""
        else:
            self._dung_lai_playlist()

    def doi_ho_so(self, ma):
        """Chuyển sang hồ sơ khác: cất thiết lập hiện tại lại, lấy thiết lập
        của hồ sơ mới đổ vào cấu hình đang chạy."""
        hs = ho_so.tim(self._kho_ho_so, ma)
        if hs is None or ma == self._kho_ho_so["dangDung"]:
            return None
        self._luu_kho_ho_so()
        self._kho_ho_so["dangDung"] = ma
        ho_so.do_vao_cau_hinh(hs, self._cfg)
        self._ghi_cau_hinh()
        ho_so.luu(self._kho_ho_so)
        self._vao_che_do(hs["loai"])
        return self._toan_bo()

    def them_ho_so(self, ten, loai):
        ten = (ten or "").strip()
        if not ten or loai not in ho_so.KHOA_THEO_LOAI:
            return None
        self._luu_kho_ho_so()
        # Hồ sơ mới thừa hưởng thiết lập đang dùng cho đúng loại đó - người
        # dùng thường tạo hồ sơ mới để chỉnh đi một chút, không phải để bắt
        # đầu lại từ số không.
        moi = dict(ma=ho_so.ma_moi(), ten=ten, loai=loai)
        for k in ho_so.khoa_cua(loai):
            if k in self._cfg:
                moi[k] = self._cfg[k]
        if loai == "congduc":
            # Tệp lời dẫn RIÊNG, nội dung trung tính. Không chép lời của hồ sơ
            # đang dùng sang: danh sách khen thưởng mà mở đầu bằng lời hồi
            # hướng công đức thì còn tệ hơn là không có lời dẫn nào.
            moi["noidung_file"] = ho_so.tao_tep_noi_dung(ten)
        self._kho_ho_so["dsHoSo"].append(moi)
        self._kho_ho_so["dangDung"] = moi["ma"]
        ho_so.do_vao_cau_hinh(moi, self._cfg)
        self._ghi_cau_hinh()
        ho_so.luu(self._kho_ho_so)
        self._vao_che_do(loai)
        return self._toan_bo()

    def sua_ten_ho_so(self, ma, ten):
        ten = (ten or "").strip()
        hs = ho_so.tim(self._kho_ho_so, ma)
        if hs is None or not ten:
            return None
        hs["ten"] = ten
        ho_so.luu(self._kho_ho_so)
        return self._toan_bo()

    def xoa_ho_so(self, ma):
        ds = self._kho_ho_so["dsHoSo"]
        # Xoá hết thì không còn gì để đọc - luôn phải chừa lại một hồ sơ.
        if len(ds) <= 1 or ho_so.tim(self._kho_ho_so, ma) is None:
            return None
        dang_xoa_cai_dang_dung = ma == self._kho_ho_so["dangDung"]
        self._kho_ho_so["dsHoSo"] = [h for h in ds if h["ma"] != ma]
        if dang_xoa_cai_dang_dung:
            con = self._kho_ho_so["dsHoSo"][0]
            self._kho_ho_so["dangDung"] = con["ma"]
            ho_so.do_vao_cau_hinh(con, self._cfg)
            self._ghi_cau_hinh()
            ho_so.luu(self._kho_ho_so)
            self._vao_che_do(con["loai"])
        else:
            ho_so.luu(self._kho_ho_so)
        return self._toan_bo()

    def mo_file(self):
        chon = self._window.create_file_dialog(
            DIALOG_OPEN,
            file_types=("Tệp văn bản (*.txt;*.md;*.csv)", "Tất cả tệp (*.*)"))
        if not chon:
            return None
        duong_dan = Path(chon[0])
        if self._che_do == "congduc":
            # Chế độ công đức đọc thẳng từ tệp, không cần nạp nội dung ở đây -
            # parse_data_file trong _dung_lai_playlist sẽ tự đọc và tự báo lỗi.
            self._cfg["data_file"] = duong_dan
            self._ghi_cau_hinh()
        else:
            try:
                self._van_ban = duong_dan.read_text(encoding="utf-8-sig",
                                                    errors="replace")
            except OSError as e:
                self._loi = {"tieu_de": "Không đọc được tệp",
                             "chi_tiet": str(e), "nut": []}
                return self._toan_bo()
            self._doc_name = duong_dan.name
            self._doc_path = str(duong_dan)
        self._dung_lai_playlist()
        return self._toan_bo()

    def dan_van_ban(self):
        text = he_thong.doc_clipboard()
        if not text.strip():
            self._goi_js(
                "window.gd.baoTin", "Clipboard đang trống",
                "Hãy bôi đen văn bản ở nơi khác, bấm Ctrl+C, rồi quay lại "
                "bấm Dán văn bản.")
            return None
        self._che_do = "vanban"
        self._van_ban = text
        self._doc_name = "Văn bản đã dán"
        self._doc_path = ""
        self._dung_lai_playlist()
        return self._toan_bo()

    def nap_lai(self):
        # Nạp lại CẢ lời dẫn và từ điển, không chỉ tệp danh sách. Hộp thoại
        # "Đã mở tệp để sửa" bảo người dùng sửa xong thì bấm F5 để chương
        # trình đọc nội dung mới - mà trước đây F5 chỉ đọc lại tệp danh sách,
        # nên sửa lời dẫn hay từ điển xong bấm F5 chẳng thấy gì đổi.
        self._nap_noi_dung()
        self._tudien = engine.load_tudien(engine.TUDIEN_FILE)
        self._dung_lai_playlist()
        return self._toan_bo()

    # ================================================== giọng và thông số

    def doi_giong(self, ma):
        self._cfg["vieneu_voice_id"] = ma
        self._ghi_cau_hinh()
        self._bo_doc.cap_nhat_cfg(self._cfg)
        return {"voiceId": ma}

    def doi_phong_cach(self, ten):
        engine.ap_dung_phong_cach(self._cfg, ten)
        self._ghi_cau_hinh()
        self._dung_lai_playlist(giu_vi_tri=True)
        return self._toan_bo()

    def dat_thong_so(self, khoa, gia_tri):
        moi = du_lieu.ep_gia_tri(khoa, gia_tri, self._che_do)
        if moi is None or moi == self._cfg.get(khoa):
            return None
        self._cfg[khoa] = moi
        self._ghi_cau_hinh()
        self._dung_lai_playlist(giu_vi_tri=True)
        return self._toan_bo()

    def tai_lai_giong(self):
        self._voices = []
        threading.Thread(target=self._nap_giong, daemon=True).start()
        return None

    def nghe_thu(self):
        return self._nghe_thu(self._cfg.get("vieneu_voice_id", ""))

    def nghe_thu_giong(self, ma):
        """Nghe thử một giọng bất kỳ trong thư viện mà KHÔNG đổi giọng đang
        dùng - nghe xong thấy không hợp thì mọi thứ vẫn nguyên như cũ."""
        return self._nghe_thu(ma)

    def _nghe_thu(self, ma):
        if not self._bo_mo_hinh.san_sang:
            return {"loi": "Mô hình giọng đọc đang khởi động, vui lòng chờ vài giây rồi thử lại."}
        # Đang đọc dở mà nghe thử thì hai giọng nói chồng lên nhau. Tạm dừng
        # bài đọc trước; người dùng bấm Phát là đọc tiếp đúng chỗ đang dở.
        self._bo_doc.tam_dung()
        self._bo_nghe_thu.phat(self._cfg, ma)
        return None

    # ================================================== điều khiển đọc

    def _nhuong_duong_phat(self):
        """Dọn đường trước khi cho một nguồn khác phát tiếng.

        Chiều "nghe thử làm tạm dừng bộ đọc" đã có sẵn, nhưng chiều ngược lại
        thì không: bấm Nghe thử rồi bấm Phát ngay trong lúc câu nghe thử còn
        đang tổng hợp (mất vài giây) thì đến lúc nó tổng hợp xong, hai giọng
        nói chồng lên nhau. Cờ dừng của riêng bộ đọc không với tới được nguồn
        nghe thử - phải gọi thẳng sang nó.

        Speaker.play() còn một chốt nữa chặn đúng chuyện này, nhưng ĐỪNG bỏ
        hàm này đi vì thấy trùng: chốt kia chỉ chặn lúc sắp kêu, tức là để câu
        nghe thử tổng hợp xong xuôi rồi mới vứt đi - phí mấy giây CPU đúng lúc
        máy đang bận đọc. Ở đây huỷ sớm, chốt kia là lưới cuối.
        """
        self._bo_nghe_thu.dung()

    def phat(self):
        if not self._bo_mo_hinh.san_sang:
            return None
        self._nhuong_duong_phat()
        self._banner_text = ""
        self._bo_doc.phat()
        return {"banner": ""}

    def tam_dung(self):
        self._bo_doc.tam_dung()
        return None

    def dung(self):
        self._bo_doc.dung()
        return None

    def cau_truoc(self):
        self._bo_doc.buoc(-1)
        return None

    def cau_sau(self):
        self._bo_doc.buoc(1)
        return None

    def nhay_toi(self, dong):
        self._bo_doc.nhay_toi(int(dong))
        return None

    # ================================================== xem trước chuẩn hoá

    def xem_truoc_chuan_hoa(self):
        dong, so_doi = [], 0
        for i, seg in enumerate(self._playlist, 1):
            rec = seg.get("rec")
            if self._che_do == "congduc" and rec:
                goc = rec.get("name", "")
                if rec.get("amount"):
                    goc += "\t" + rec["amount"]
            else:
                goc = (seg.get("goc") or seg.get("text") or "")
            doc = seg.get("text", "")
            khac = " ".join(goc.split()) != " ".join(doc.split())
            so_doi += 1 if khac else 0
            dong.append({"no": i, "goc": goc.strip(), "doc": doc.strip(),
                         "doi": khac})
        return {"dong": dong,
                "tom_tat": f"{so_doi} chỗ sẽ được đọc khác văn bản gốc · "
                           f"{len(dong)} dòng"}

    # ================================================== xuất file

    def goi_y_xuat_file(self):
        thu_muc = self._tuy_chon.get("thu_muc_xuat") \
            or str(he_thong.thu_muc_xuat_mac_dinh())
        ten = Path(self._doc_name).stem or "giongdoc"
        giong = next((v["ten"] for v in self._voices
                      if v["id"] == self._cfg.get("vieneu_voice_id")), "giọng mặc định")
        return {
            "ten": ten,
            "thu_muc": thu_muc,
            "mo_ta": f"{self._doc_name or 'Văn bản'} · {len(self._lines)} dòng · {giong}",
            "tach": xuat_file.uoc_tinh(self._playlist, self._cfg),
        }

    def chon_thu_muc(self):
        chon = self._window.create_file_dialog(DIALOG_FOLDER)
        if not chon:
            return None
        self._tuy_chon["thu_muc_xuat"] = str(chon[0])
        he_thong.luu_tuy_chon(self._tuy_chon)
        return self._tuy_chon["thu_muc_xuat"]

    def bat_dau_xuat(self, ten, thu_muc, kieu_tach):
        if not self._playlist:
            return None
        self._nhuong_duong_phat()
        self._bo_doc.dung(giu_vi_tri=True)
        self._tuy_chon["thu_muc_xuat"] = thu_muc
        he_thong.luu_tuy_chon(self._tuy_chon)
        self._bo_xuat.bat_dau(self._playlist, self._cfg, ten, thu_muc, int(kieu_tach))
        return None

    def huy_xuat(self):
        self._bo_xuat.huy()
        return None

    def _tien_do_xuat(self, d):
        self._goi_js("window.gd.tienDoXuat", d)

    def _xuat_xong(self, kq):
        self._goi_js("window.gd.xuatXong", kq)

    def _xuat_loi(self, msg):
        self._goi_js("window.gd.xuatLoi", msg)

    def _xuat_huy(self):
        # Người dùng chủ động huỷ thì không phải lỗi, không doạ họ bằng hộp
        # thoại "Không xuất được tệp".
        self._goi_js("window.gd.xuatHuy")

    def mo_thu_muc(self, duong_dan):
        he_thong.mo_thu_muc(duong_dan)
        return None

    # ================================================== hệ thống

    def sua_file(self, loai):
        # Lời dẫn mở đúng tệp của HỒ SƠ ĐANG DÙNG, không phải noidung.ini cố
        # định - mỗi hồ sơ danh sách nay có lời dẫn riêng.
        bang = {"danh_sach": self._cfg["data_file"],
                "noi_dung": self._tep_noi_dung(),
                "tu_dien": engine.TUDIEN_FILE}
        duong_dan = bang.get(loai)
        if duong_dan is None:
            return None
        loi = he_thong.mo_bang_chuong_trinh_mac_dinh(Path(duong_dan))
        if loi:
            self._goi_js("window.gd.baoLoi", "Không mở được tệp", loi)
        else:
            self._goi_js(
                "window.gd.baoTin", "Đã mở tệp để sửa",
                "Sửa xong nhớ bấm Ctrl+S để lưu, rồi quay lại đây bấm F5 "
                "(hoặc menu Tệp ▸ Nạp lại) để chương trình đọc nội dung mới.")
        return None

    def luu_theme(self, theme):
        self._tuy_chon["theme"] = theme
        he_thong.luu_tuy_chon(self._tuy_chon)
        return None

    def luu_zoom(self, zoom):
        self._tuy_chon["zoom"] = int(zoom)
        he_thong.luu_tuy_chon(self._tuy_chon)
        return None

    def cua_so(self, hanh_dong):
        if self._window is None:
            return None
        x, y, rong, cao = self._vung
        if hanh_dong == "thu_nho":
            self._window.minimize()
        elif hanh_dong == "phong_to":
            # Không dùng maximize() của WinForms: với cửa sổ không khung nó phủ
            # luôn lên thanh tác vụ. Tự đặt đúng vùng làm việc thay vì vậy.
            if self._phong_to:
                rong2, cao2 = min(1280, rong - 80), min(800, cao - 80)
                self._window.resize(rong2, cao2)
                self._window.move(x + (rong - rong2) // 2, y + (cao - cao2) // 2)
            else:
                self._window.resize(rong, cao)
                self._window.move(x, y)
            self._phong_to = not self._phong_to
        return None

    def _don_dep(self):
        """Dừng mọi việc đang chạy nền. Gọi cả khi người dùng đóng cửa sổ
        bằng Alt+F4 - lúc đó thoat() không hề chạy."""
        for dung in (self._bo_doc.tat, self._bo_nghe_thu.tat, self._bo_xuat.huy):
            try:
                dung()
            except Exception:
                pass
        engine.giai_phong_bo_nho_he_thong()

    def thoat(self):
        self._don_dep()
        if self._window is not None:
            self._window.destroy()
        return None

    def huong_dan(self):
        self._goi_js("window.gd.baoTin", "Hướng dẫn nhanh", he_thong.HUONG_DAN)
        return None

    def ve_chuong_trinh(self):
        self._goi_js("window.gd.baoTin", "Về Giọng Việt",
                     he_thong.ve_chuong_trinh())
        return None

    # ================================================== soát văn bản

    def _du_lieu_soat(self) -> dict:
        return soat.du_lieu(self._che_do, self._records, self._canh_bao,
                            self._van_ban, self._tudien)

    def mo_soat(self):
        return {"man": "soat", "soat": self._du_lieu_soat()}

    def soat_lai(self):
        return {"soat": self._du_lieu_soat()}

    def nhay_toi_dong_tep(self, so_dong):
        """Nhảy tới một dòng theo SỐ DÒNG TRONG TỆP, không phải vị trí trong
        playlist. Hai con số này lệch nhau: playlist còn chèn lời mở đầu, lời
        giữa và lời kết, nên dòng 1 của tệp có thể nằm ở vị trí thứ 5. Dùng
        thẳng số dòng tệp là nhảy trượt sang người khác.
        """
        try:
            can = int(so_dong)
        except (TypeError, ValueError):
            return None
        for vi_tri, doan in enumerate(self._playlist, 1):
            rec = doan.get("rec")
            if rec and rec.get("line_no") == can:
                return self.nhay_toi(vi_tri)
        return None

    # ================================================== từ điển phát âm

    def _du_lieu_tu_dien(self, tim="") -> dict:
        return tu_dien.du_lieu(self._tudien, tim)

    def mo_tu_dien(self):
        return {"man": "tudien", "tuDien": self._du_lieu_tu_dien()}

    def tim_tu_dien(self, tim):
        return {"tuDien": self._du_lieu_tu_dien(tim)}

    def _luu_tu_dien(self, tim=""):
        """Ghi ra đĩa rồi dựng lại playlist - cách đọc vừa đổi phải nghe thấy
        ngay chứ không đợi mở lại chương trình."""
        engine.luu_tudien(engine.TUDIEN_FILE, self._tudien)
        self._dung_lai_playlist(giu_vi_tri=True)
        return dict(self._toan_bo(), tuDien=self._du_lieu_tu_dien(tim))

    def them_tu(self, tu, doc, tim=""):
        tu, doc = (tu or "").strip(), (doc or "").strip()
        if not tu or not doc:
            return None
        self._tudien[tu] = doc
        return self._luu_tu_dien(tim)

    def sua_tu(self, tu_cu, tu, doc, tim=""):
        tu_cu = (tu_cu or "").strip()
        tu, doc = (tu or "").strip(), (doc or "").strip()
        if not tu or not doc:
            return None
        # Đổi cả chữ bên trái thì phải bỏ mục cũ đi, không thì thành hai mục.
        if tu_cu and tu_cu != tu:
            self._tudien.pop(tu_cu, None)
        self._tudien[tu] = doc
        return self._luu_tu_dien(tim)

    def xoa_tu(self, tu, tim=""):
        if (tu or "").strip() not in self._tudien:
            return None
        self._tudien.pop(tu.strip(), None)
        return self._luu_tu_dien(tim)

    def _du_lieu_cai_dat(self) -> dict:
        hs = ho_so.tim(self._kho_ho_so, self._kho_ho_so["dangDung"])
        return cai_dat.du_lieu(self._cfg, self._tuy_chon,
                               hs["loai"] if hs else "",
                               hs["ten"] if hs else "")

    def mo_cai_dat(self):
        return {"man": "caidat", "caiDat": self._du_lieu_cai_dat()}

    # Ba loại thiết lập đi ba đường khác nhau: cauhinh.ini (ảnh hưởng lời đọc,
    # phải dựng lại playlist), giaodien.json (chỉ là hình thức), và đường dẫn
    # tệp (phải mở hộp thoại chọn). Gộp vào một cửa cho giao diện đỡ phải nhớ.
    CONG_TAC_CAU_HINH = ("doc_so_bang_chu", "bo_markdown", "nhan_manh_tien")

    def dat_cai_dat(self, khoa, gia_tri):
        if khoa in self.CONG_TAC_CAU_HINH:
            moi = bool(gia_tri)
            if moi == bool(self._cfg.get(khoa)):
                return None
            self._cfg[khoa] = moi
            self._ghi_cau_hinh()
            self._dung_lai_playlist(giu_vi_tri=True)
            return dict(self._toan_bo(), caiDat=self._du_lieu_cai_dat())

        if khoa == "theme":
            self._tuy_chon["theme"] = "dark" if gia_tri == "dark" else "light"
            he_thong.luu_tuy_chon(self._tuy_chon)
            return dict(self._toan_bo(), caiDat=self._du_lieu_cai_dat())

        if khoa == "zoom":
            try:
                self._tuy_chon["zoom"] = max(70, min(200, int(gia_tri)))
            except (TypeError, ValueError):
                return None
            he_thong.luu_tuy_chon(self._tuy_chon)
            return dict(self._toan_bo(), caiDat=self._du_lieu_cai_dat())

        return None

    def doi_duong_dan_cai_dat(self, khoa):
        """Mở hộp thoại chọn tệp/thư mục cho một mục trong Cài đặt."""
        if khoa == "data_file":
            chon = self._window.create_file_dialog(
                DIALOG_OPEN,
                file_types=("Tệp văn bản (*.txt;*.md;*.csv)", "Tất cả tệp (*.*)"))
            if not chon:
                return None
            self._cfg["data_file"] = Path(chon[0])
            self._ghi_cau_hinh()
            self._dung_lai_playlist()
            return dict(self._toan_bo(), caiDat=self._du_lieu_cai_dat())

        if khoa == "thu_muc_xuat":
            chon = self._window.create_file_dialog(DIALOG_FOLDER)
            if not chon:
                return None
            self._tuy_chon["thu_muc_xuat"] = str(chon[0])
            he_thong.luu_tuy_chon(self._tuy_chon)
            return {"caiDat": self._du_lieu_cai_dat()}

        return None

    # ================================================== thư viện giọng

    def _du_lieu_thu_vien(self) -> dict:
        return thu_vien_giong.du_lieu(self._voices,
                                      self._cfg.get("vieneu_voice_id", ""))

    def mo_thu_vien_giong(self):
        return {"man": "giong", "thuVien": self._du_lieu_thu_vien()}

    def dong_man_hinh(self):
        return {"man": "chinh"}

    def tao_giong_rieng(self):
        return self.mo_thu_vien_giong()

    def quan_ly_giong_rieng(self):
        return self.mo_thu_vien_giong()

    def chon_file_mau(self):
        chon = self._window.create_file_dialog(
            DIALOG_OPEN,
            file_types=("Tệp âm thanh (*.wav;*.mp3;*.m4a;*.flac)",
                        "Tất cả tệp (*.*)"))
        return str(chon[0]) if chon else None

    def nhan_ban_giong(self, ten, duong_dan):
        if self._dang_nhan_ban:
            return None
        self._dang_nhan_ban = True
        threading.Thread(target=self._nhan_ban_nen,
                         args=(ten, duong_dan), daemon=True).start()
        return None

    def _nhan_ban_nen(self, ten, duong_dan):
        try:
            engine.tao_giong_rieng(
                ten, duong_dan,
                lambda m: self._goi_js("window.gd.tienDoGiong", str(m)))
        except Exception as e:
            # Engine viết sẵn thông báo dài, dễ hiểu (thiếu PyTorch, máy không
            # đủ điều kiện...) - đưa nguyên văn cho người dùng đọc.
            self._goi_js("window.gd.giongLoi", str(e))
            return
        finally:
            self._dang_nhan_ban = False
        self._nap_giong()
        self._day({"thuVien": self._du_lieu_thu_vien()})
        self._goi_js("window.gd.giongXong", ten)

    def xoa_giong(self, ma):
        engine.xoa_giong_rieng(ma)
        if self._cfg.get("vieneu_voice_id") == ma:
            # Đang dùng chính giọng vừa xoá thì chuyển về giọng đầu danh sách,
            # không thì lần phát tới sẽ lỗi vì trỏ vào giọng không còn nữa.
            self._cfg["vieneu_voice_id"] = ""
            self._ghi_cau_hinh()
        self._nap_giong()
        return {"thuVien": self._du_lieu_thu_vien()}

    def bo_qua_loi(self):
        """Người dùng bấm dấu X trên khung báo lỗi."""
        self._loi = None
        return {"loi": None, "state": self._trang_thai()}

    def xu_ly_loi(self, act):
        if act == "thuLaiMoHinh":
            self._loi = None
            self._bo_mo_hinh.bat_dau()
        elif act == "docTiep":
            self._loi = None
            self._bo_doc.phat()
        # Xoá khung lỗi ở giao diện: bo_doc.phat() chỉ đẩy state và pos, không
        # đụng tới trường loi nên khung đỏ sẽ nằm lại nếu không dọn ở đây.
        return {"loi": None}
