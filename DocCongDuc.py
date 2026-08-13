# -*- coding: utf-8 -*-
"""
CHƯƠNG TRÌNH ĐỌC TIẾNG VIỆT 4.0   (DocCongDuc.py)

Hai chế độ độc lập, MỖI CHẾ ĐỘ CÓ BỘ NÚT ĐỌC RIÊNG:
  📜 Danh sách công đức - đọc congduc.txt, có lời mở đầu / lời kết.
  📖 Đọc văn bản        - đọc mọi văn bản tiếng Việt: gõ, dán, mở file.

Mỗi chế độ giữ riêng vị trí đang đọc, tiến độ và trạng thái. Chuyển
qua lại giữa hai thẻ KHÔNG làm mất chỗ đang đọc dở.

Giọng đọc dùng VieNeu-TTS - chạy hoàn toàn tại máy (CPU, không cần
card đồ hoạ), không cần Internet sau khi cài đặt và tải mô hình lần
đầu (xem CaiDat.bat). Không còn dùng Edge TTS / Microsoft.
"""

import collections
import concurrent.futures
import configparser
import json
import os
import re
import shutil
import subprocess
import sys
import tempfile
import threading
import time
import tkinter as tk
from pathlib import Path
from tkinter import filedialog, font as tkfont, messagebox, ttk


APP_TITLE = "CHƯƠNG TRÌNH ĐỌC TIẾNG VIỆT"
APP_VERSION = "4.0"

# Bảng màu
MAU_NEN = "#f4f5f7"
MAU_CHINH = "#1f6b3b"      # nút đọc
MAU_TAM_DUNG = "#9a6b00"   # nút tạm dừng
MAU_DUNG = "#8a3030"       # nút dừng
MAU_MO = "#c9ccd2"         # nút bị khoá
MAU_SANG = "#ffe9a8"       # dòng đang đọc
MAU_PHU = "#5a6068"


def app_dir() -> Path:
    if getattr(sys, "frozen", False):
        return Path(sys.executable).resolve().parent
    return Path(__file__).resolve().parent


BASE_DIR = app_dir()
CONFIG_FILE = BASE_DIR / "cauhinh.ini"
NOIDUNG_FILE = BASE_DIR / "noidung.ini"
TUDIEN_FILE = BASE_DIR / "tudien.ini"
GIONG_RIENG_DIR = BASE_DIR / "giong_rieng"
GIONG_RIENG_FILE = GIONG_RIENG_DIR / "danhsach.json"

# Đặt NGAY LÚC NẠP MODULE, trước khi bất kỳ đoạn code nào có cơ hội
# "import vieneu" (dù trực tiếp hay để kiểm tra đã cài chưa) - để mô
# hình VieNeu-TTS tải về nằm gọn trong thư mục con "vieneu_models" cạnh
# chương trình, thay vì thư mục cache ẩn mặc định của Windows
# (C:\Users\...\.cache\huggingface). Đặt muộn hơn (vd trong hàm gọi lúc
# đọc) sẽ KHÔNG còn tác dụng nếu một chỗ khác đã lỡ import trước đó -
# huggingface_hub chốt đường dẫn cache ngay khi được import lần đầu.
# setdefault: không ghi đè nếu người dùng đã tự đặt HF_HOME từ trước.
os.environ.setdefault("HF_HOME", str(BASE_DIR / "vieneu_models"))

# Đo được 11/08/2026: dù mô hình đã nằm đủ trên đĩa, huggingface_hub vẫn
# hỏi máy chủ "có bản mới không" mỗi lần khởi tạo - nạp mô hình mất 33,8 s
# thay vì 9,7 s, và câu đầu tiên 5,1 s thay vì 3,3 s. Máy ở chùa mạng chập
# chờn còn lâu hơn nữa vì phải chờ hết thời gian gọi mạng mới chịu quay về
# đọc bản trên đĩa. Đã có đủ mô hình thì cắt hẳn đường mạng đó.
#
# Chỉ cắt khi CHẮC CHẮN đủ - máy mới cài chưa có mô hình vẫn phải tải được
# bình thường. Phải đặt trước khi huggingface_hub được import lần đầu, vì
# thư viện chốt cờ này ngay lúc import (giống HF_HOME ở trên).

# Ngưỡng cho TỪNG kho, không phải tổng hai kho cộng lại. Đo 11/08/2026:
# VieNeu 199 MB, MOSS 87 MB. Xét tổng thì một kho đủ bù cho kho kia đang
# thiếu - ví dụ VieNeu nguyên vẹn còn MOSS mới tải được một nửa vẫn vượt mốc
# tổng, thế là cắt mạng trong khi mô hình khuyết, đọc đến nơi mới lỗi.
# Lấy khoảng 90% dung lượng thật: loại được bản tải dở, vẫn còn biên nếu bản
# sau nhẹ bớt đôi chút.
# speaker_encoder.onnx (28 MB) chỉ được tải xuống lần đầu NHÂN BẢN GIỌNG, chứ
# không tải cùng lúc với mô hình đọc. Thiếu nó mà đã cắt mạng thì bấm "Nhân
# bản giọng" chỉ nhận về LocalEntryNotFoundError - đúng loại nút bấm vào không
# ra gì. Nên coi nó là phần bắt buộc: chưa có thì cứ để đường mạng mở, chịu
# chậm lúc mở máy, đổi lấy việc nhân bản giọng tải được tệp nó cần.
KHO_VIENEU_HF = "pnnbao-ump/VieNeu-TTS-v3-Turbo"
TEP_NHAN_BAN = "speaker_encoder.onnx"

KHO_MO_HINH = {
    "models--pnnbao-ump--VieNeu-TTS-v3-Turbo": {
        "toi_thieu": 210 * 1024 * 1024,
        "tep_bat_buoc": (TEP_NHAN_BAN, "denoiser.onnx"),
    },
    "models--OpenMOSS-Team--MOSS-Audio-Tokenizer-Nano-ONNX": {
        "toi_thieu": 78 * 1024 * 1024,
        "tep_bat_buoc": (),
    },
}

_da_du_mo_hinh = None


def mo_hinh_da_du_tren_dia() -> bool:
    """Cả hai kho mô hình đã tải xong và còn nguyên vẹn trên đĩa chưa.

    Nhớ kết quả lại: hàm được hỏi ở nhiều chỗ (lúc nạp module, lúc khởi tạo
    engine, lúc giao diện chọn chữ để hiển thị) mà mỗi lần lại quét lại cả
    thư mục mô hình."""
    global _da_du_mo_hinh
    if _da_du_mo_hinh is not None:
        return _da_du_mo_hinh

    hub = BASE_DIR / "vieneu_models" / "hub"
    _da_du_mo_hinh = True
    for ten_kho, yeu_cau in KHO_MO_HINH.items():
        thu_muc = hub / ten_kho / "snapshots"
        if not thu_muc.is_dir():
            _da_du_mo_hinh = False
            break

        tong = 0
        co_mat = set()
        for f in thu_muc.rglob("*"):
            if f.is_file():
                co_mat.add(f.name)
                try:
                    tong += f.stat().st_size
                except OSError:
                    tong = 0
                    break

        thieu_tep = [t for t in yeu_cau["tep_bat_buoc"] if t not in co_mat]
        if tong < yeu_cau["toi_thieu"] or thieu_tep:
            _da_du_mo_hinh = False
            break
    return _da_du_mo_hinh


if mo_hinh_da_du_tren_dia():
    os.environ.setdefault("HF_HUB_OFFLINE", "1")


# ---------------------------------------------------------------------------
# PHONG CÁCH ĐỌC - đúng 3 phong cách thật mà VieNeu-TTS hỗ trợ qua tham số
# style: "tu_nhien" | "tin_tuc" | "doc_truyen". Không có tham số tốc độ/cao
# độ riêng (không giống Edge TTS trước đây) - nghi_cau/nghi_doan là khoảng
# nghỉ do CHƯƠNG TRÌNH tự chèn giữa các câu/đoạn, không phải của VieNeu-TTS.
# ---------------------------------------------------------------------------

PHONG_CACH = {
    "Tự nhiên": {
        "style": "tu_nhien", "nghi_cau": 0.25, "nghi_doan": 0.70,
        "mo_ta": "Cân bằng, dùng cho hầu hết văn bản.",
    },
    "Tin tức - thông báo": {
        "style": "tin_tuc", "nghi_cau": 0.22, "nghi_doan": 0.60,
        "mo_ta": "Rõ ràng, dứt khoát. Hợp bản tin, thông báo, loa phát thanh.",
    },
    "Kể chuyện": {
        "style": "doc_truyen", "nghi_cau": 0.35, "nghi_doan": 0.90,
        "mo_ta": "Trầm, nhiều nhịp nghỉ. Hợp đọc công đức, sớ, kể chuyện.",
    },
}
PHONG_CACH_MAC_DINH = "Kể chuyện"




# ---------------------------------------------------------------------------
# NỘI DUNG MẶC ĐỊNH
# ---------------------------------------------------------------------------

MAU_CAU_MAC_DINH = "{ten}, phát tâm công đức số tiền {tien}."

LOI_DAU_MAC_DINH = """Nam mô A Di Đà Phật.

Nhà chùa xin thành kính thông báo và ghi nhận danh sách quý Phật tử, quý gia đình, quý cơ quan, đơn vị và quý mạnh thường quân đã phát tâm công đức xây dựng, tu bổ và hộ trì Tam Bảo.

Nhà chùa xin thành kính tri ân công đức của quý vị.

Sau đây là danh sách công đức."""

LOI_GIUA_MAC_DINH = (
    "Nhà chùa xin thành kính tri ân công đức và tấm lòng phát tâm "
    "của quý Phật tử."
)

LOI_CUOI_MAC_DINH = """Danh sách công đức đến đây xin được khép lại.

Nhà chùa xin thành kính tri ân công đức, tấm lòng hoan hỷ và sự phát tâm hộ trì Tam Bảo của quý Phật tử, quý gia đình, quý cơ quan, đơn vị và quý mạnh thường quân.

Nguyện đem công đức này hồi hướng cho quốc thái dân an, chúng sinh an lạc, gia đình bình an, mọi người mọi nhà được mạnh khỏe, hạnh phúc và sở cầu như nguyện.

Nam mô Công Đức Lâm Bồ Tát Ma Ha Tát."""

TUDIEN_MAC_DINH = {
    "MTTQ": "Mặt trận Tổ quốc", "UBMTTQ": "Ủy ban Mặt trận Tổ quốc",
    "UBND": "Ủy ban nhân dân", "HĐND": "Hội đồng nhân dân",
    "BCH": "Ban chấp hành", "BQL": "Ban quản lý", "HTX": "Hợp tác xã",
    "CLB": "Câu lạc bộ", "TNHH": "trách nhiệm hữu hạn", "MTV": "một thành viên",
    "CP": "cổ phần", "DNTN": "doanh nghiệp tư nhân",
    "THCS": "Trung học cơ sở", "THPT": "Trung học phổ thông",
    "GĐ": "Gia đình", "Cty": "Công ty", "TT": "Thị trấn", "TP": "Thành phố",
    "TX": "Thị xã", "NCT": "Người cao tuổi", "CCB": "Cựu chiến binh",
    "PN": "Phụ nữ", "TN": "Thanh niên", "VN": "Việt Nam", "Bt": "Bí thư",
    # Chữ ký cuối văn bản hành chính: "TM. Ban Giám đốc", "KT. Giám đốc".
    # Không có mục này thì máy đánh vần "tê em", chủ dự án bấm thử đã gặp.
    #
    # PHẢI có cả bản KÈM DẤU CHẤM. _ap_dung_tudien sắp khoá theo độ dài giảm
    # dần nên "TM." khớp trước "TM" và nuốt luôn dấu chấm; chỉ khai "TM" thì
    # ra "Thay mặt. Ban Giám đốc" - máy đọc thành hai câu, nghe như hụt hơi
    # giữa chừng.
    "TM.": "Thay mặt", "KT.": "Ký thay", "TL.": "Thừa lệnh",
    "TUQ.": "Thừa uỷ quyền", "TM": "Thay mặt", "KT": "Ký thay",
    "TL": "Thừa lệnh", "TUQ": "Thừa uỷ quyền",
    "PGS": "Phó giáo sư", "GS": "Giáo sư", "TS": "Tiến sĩ", "ThS": "Thạc sĩ",
    "BS": "Bác sĩ", "KS": "Kỹ sư", "NXB": "Nhà xuất bản",
    "TDTT": "Thể dục thể thao", "ATGT": "An toàn giao thông",
    "BHYT": "Bảo hiểm y tế", "BHXH": "Bảo hiểm xã hội",
    "CNTT": "Công nghệ thông tin", "QĐ": "Quyết định", "NĐ": "Nghị định",
    "TW": "Trung ương", "TPHCM": "Thành phố Hồ Chí Minh",
    "HCM": "Hồ Chí Minh", "HN": "Hà Nội",
}

CAUHINH_MAC_DINH = """[GiongDoc]
; ID giong VieNeu-TTS da chon (de trong = giong mac dinh cua mo hinh)
vieneu_voice_id=
; Phong cach: Tu nhien | Tin tuc - thong bao | Ke chuyen
phong_cach=Kể chuyện

[DocLienTuc]
; Chế độ DANH SÁCH CÔNG ĐỨC
nghi_giua_nguoi=1.3
nghi_giua_nhom=2.5
so_nguoi_moi_nhom=20
nghi_giua_doan=0.8
; 1 = doc nhan manh nhom cung nhieu nhat trong danh sach (to hon mot chut va
;     nghi lau hon sau cau do). Nguong tinh theo chinh danh sach dang doc.
nhan_manh_tien=0

[DocVanBan]
; Chế độ ĐỌC VĂN BẢN
nghi_giua_cau=0.25
nghi_giua_doan_vb=0.70
; Số ký tự tối đa mỗi lần gửi đi tổng hợp giọng (200-600 là hợp lý)
so_ky_tu_moi_doan=280
; 1 = đổi số lớn thành chữ (1.600.000 -> một triệu sáu trăm nghìn)
doc_so_bang_chu=0
; 1 = bỏ qua ký hiệu #, *, |, gạch đầu dòng
bo_ky_hieu_markdown=1

[HeThong]
file_cong_duc=congduc.txt
ffplay=ffmpeg\\bin\\ffplay.exe
"""


# ---------------------------------------------------------------------------
# FILE noidung.ini
# ---------------------------------------------------------------------------

KEY_RE = re.compile(r"^\s*(bat_dau|sau_moi|noi_dung)\s*=\s*(.*)$", re.IGNORECASE)
SECTION_RE = re.compile(r"^\s*\[([^\]]+)\]\s*$")


class NoiDung:
    """Đọc / ghi noidung.ini. Cho phép noi_dung nhiều dòng, có dòng trắng."""

    def __init__(self):
        self.dau_bat = True
        self.dau_text = LOI_DAU_MAC_DINH
        self.giua_bat = False
        self.giua_sau_moi = 30
        self.giua_text = LOI_GIUA_MAC_DINH
        self.cuoi_bat = True
        self.cuoi_text = LOI_CUOI_MAC_DINH
        self.mau_cau = MAU_CAU_MAC_DINH

    def load(self, path: Path):
        if not path.exists():
            return self
        try:
            raw = path.read_text(encoding="utf-8-sig", errors="replace")
        except OSError:
            return self

        sections, cur_sec, cur_key = {}, None, None
        for line in raw.splitlines():
            m_sec = SECTION_RE.match(line)
            if m_sec:
                cur_sec = m_sec.group(1).strip().lower()
                sections.setdefault(cur_sec, {})
                cur_key = None
                continue
            if cur_sec is None:
                continue
            if (line.lstrip().startswith(";") or line.lstrip().startswith("#")) \
                    and cur_key != "noi_dung":
                continue
            m_key = KEY_RE.match(line)
            if m_key:
                cur_key = m_key.group(1).lower()
                sections[cur_sec][cur_key] = m_key.group(2)
                continue
            if cur_key:
                sections[cur_sec][cur_key] += "\n" + line

        def get(sec, key, default=""):
            return sections.get(sec, {}).get(key, default)

        def to_bool(value, default=True):
            v = str(value).strip().lower()
            if v in ("1", "true", "co", "có", "yes", "bat", "bật"):
                return True
            if v in ("0", "false", "khong", "không", "no", "tat", "tắt"):
                return False
            return default

        def to_int(value, default):
            try:
                return max(1, int(str(value).strip()))
            except (TypeError, ValueError):
                return default

        if "daudanhsach" in sections:
            self.dau_bat = to_bool(get("daudanhsach", "bat_dau", "1"), True)
            self.dau_text = get("daudanhsach", "noi_dung", self.dau_text).strip("\n")
        if "giuadanhsach" in sections:
            self.giua_bat = to_bool(get("giuadanhsach", "bat_dau", "0"), False)
            self.giua_sau_moi = to_int(get("giuadanhsach", "sau_moi", "30"), 30)
            self.giua_text = get("giuadanhsach", "noi_dung", self.giua_text).strip("\n")
        if "cuoidanhsach" in sections:
            self.cuoi_bat = to_bool(get("cuoidanhsach", "bat_dau", "1"), True)
            self.cuoi_text = get("cuoidanhsach", "noi_dung", self.cuoi_text).strip("\n")
        if "maucau" in sections:
            mau = get("maucau", "noi_dung", "").strip()
            if "{ten}" in mau and "{tien}" in mau:
                self.mau_cau = mau
        return self

    def save(self, path: Path):
        path.write_text(
            "; ==========================================================\n"
            ";  NOI DUNG LOI DAN - CHE DO DANH SACH CONG DUC\n"
            ";  Sua bang Notepad roi luu lai (UTF-8), hoac sua trong\n"
            ";  chuong trinh: menu Cong cu > Sua loi dan.\n"
            ";  bat_dau=1 la BAT, bat_dau=0 la TAT.\n"
            "; ==========================================================\n\n"
            "[DauDanhSach]\n"
            f"bat_dau={1 if self.dau_bat else 0}\n"
            f"noi_dung={self.dau_text}\n\n"
            "[GiuaDanhSach]\n"
            f"bat_dau={1 if self.giua_bat else 0}\n"
            f"sau_moi={self.giua_sau_moi}\n"
            f"noi_dung={self.giua_text}\n\n"
            "[CuoiDanhSach]\n"
            f"bat_dau={1 if self.cuoi_bat else 0}\n"
            f"noi_dung={self.cuoi_text}\n\n"
            "[MauCau]\n"
            "; Bat buoc co {ten} va {tien}\n"
            f"noi_dung={self.mau_cau}\n",
            encoding="utf-8-sig")


# ---------------------------------------------------------------------------
# TỪ ĐIỂN CÁCH ĐỌC
# ---------------------------------------------------------------------------

def load_tudien(path: Path) -> dict:
    tudien = dict(TUDIEN_MAC_DINH)
    if not path.exists():
        return tudien
    cfg = configparser.ConfigParser(interpolation=None)
    cfg.optionxform = str
    try:
        cfg.read(path, encoding="utf-8-sig")
    except configparser.Error:
        return tudien
    if cfg.has_section("ThayThe"):
        for key, value in cfg.items("ThayThe"):
            key, value = key.strip(), value.strip()
            if not key:
                continue
            if value:
                tudien[key] = value
            else:
                # Giá trị rỗng = người dùng đã xoá mục này. Cần đánh dấu được
                # như vậy vì bảng mặc định luôn được trộn vào trước; không có
                # cách đánh dấu thì xoá xong lần sau mở lên nó lại hiện ra.
                # (Trước đây rỗng nghĩa là "thay bằng chuỗi rỗng", tức nuốt
                # luôn chữ đó khỏi lời đọc - gần như chắc chắn không ai muốn.)
                tudien.pop(key, None)
    return tudien


def luu_tudien(path: Path, tudien: dict):
    """Ghi từ điển cách đọc của người dùng.

    Mục mặc định nào bị xoá thì ghi lại với giá trị rỗng, để lần sau nạp lên
    biết đường bỏ qua thay vì trộn nó vào lần nữa.

    Ghi ra tệp tạm rồi mới thay thế: đây là dữ liệu người dùng gõ tay, mất
    điện giữa chừng mà tệp mới ghi được nửa chừng thì mất sạch.
    """
    dong = [
        "; ==========================================================",
        ";  TU DIEN CACH DOC  -  dung chung cho CA HAI che do",
        ";  Ben trai la chu trong van ban, ben phai la cach doc.",
        ";  Dong co gia tri rong = muc mac dinh da bi xoa di.",
        "; ==========================================================",
        "",
        "[ThayThe]",
    ]
    for key in sorted(tudien, key=str.lower):
        dong.append(f"{key}={tudien[key]}")
    for key in sorted(TUDIEN_MAC_DINH, key=str.lower):
        if key not in tudien:
            dong.append(f"{key}=")

    tam = path.with_suffix(path.suffix + ".tam")
    tam.write_text("\n".join(dong) + "\n", encoding="utf-8-sig")
    tam.replace(path)


def noi_dung_tudien_mac_dinh() -> str:
    dong = [
        "; ==========================================================",
        ";  TU DIEN CACH DOC  -  dung chung cho CA HAI che do",
        ";  Ben trai la chu trong van ban, ben phai la cach doc.",
        ";  Vi du:  MTTQ=Mat tran To quoc",
        "; ==========================================================",
        "",
        "[ThayThe]",
    ]
    for key, value in TUDIEN_MAC_DINH.items():
        dong.append(f"{key}={value}")
    return "\n".join(dong) + "\n"


def save_tudien_mac_dinh(path: Path):
    path.write_text(noi_dung_tudien_mac_dinh(), encoding="utf-8-sig")


# ---------------------------------------------------------------------------
# CẤU HÌNH
# ---------------------------------------------------------------------------

def load_config():
    cfg = configparser.ConfigParser(interpolation=None)
    if CONFIG_FILE.exists():
        try:
            cfg.read(CONFIG_FILE, encoding="utf-8-sig")
        except configparser.Error:
            pass

    def get_float(section, key, default):
        try:
            return float(str(cfg.get(section, key, fallback=default)).replace(",", "."))
        except (ValueError, TypeError):
            return default

    def get_int(section, key, default):
        try:
            return int(float(cfg.get(section, key, fallback=default)))
        except (ValueError, TypeError):
            return default

    data_path = Path(cfg.get("HeThong", "file_cong_duc", fallback="congduc.txt"))
    if not data_path.is_absolute():
        data_path = BASE_DIR / data_path
    ffplay_path = Path(cfg.get("HeThong", "ffplay", fallback=r"ffmpeg\bin\ffplay.exe"))
    if not ffplay_path.is_absolute():
        ffplay_path = BASE_DIR / ffplay_path

    phong_cach = cfg.get("Giọng Việt", "phong_cach", fallback=PHONG_CACH_MAC_DINH)
    if phong_cach not in PHONG_CACH:
        phong_cach = PHONG_CACH_MAC_DINH

    return {
        "vieneu_voice_id": cfg.get("Giọng Việt", "vieneu_voice_id",
                                   fallback="").strip(),
        "phong_cach": phong_cach,
        "nghi_nguoi": max(0.0, get_float("DocLienTuc", "nghi_giua_nguoi", 1.3)),
        "nghi_nhom": max(0.0, get_float("DocLienTuc", "nghi_giua_nhom", 2.5)),
        "so_nguoi_nhom": max(1, get_int("DocLienTuc", "so_nguoi_moi_nhom", 20)),
        "nghi_doan": max(0.0, get_float("DocLienTuc", "nghi_giua_doan", 0.8)),
        "nhan_manh_tien": get_int("DocLienTuc", "nhan_manh_tien", 0) == 1,
        "nghi_cau": max(0.0, get_float("DocVanBan", "nghi_giua_cau", 0.25)),
        "nghi_doan_vb": max(0.0, get_float("DocVanBan", "nghi_giua_doan_vb", 0.70)),
        "so_ky_tu": min(900, max(80, get_int("DocVanBan", "so_ky_tu_moi_doan", 280))),
        "doc_so_bang_chu": get_int("DocVanBan", "doc_so_bang_chu", 0) == 1,
        "bo_markdown": get_int("DocVanBan", "bo_ky_hieu_markdown", 1) == 1,
        "data_file": data_path,
        "ffplay": ffplay_path,
    }


def save_config(cfg: dict):
    parser = configparser.ConfigParser(interpolation=None)
    parser["GiongDoc"] = {
        "vieneu_voice_id": cfg.get("vieneu_voice_id", ""),
        "phong_cach": cfg["phong_cach"],
    }
    parser["DocLienTuc"] = {
        "nghi_giua_nguoi": f'{cfg["nghi_nguoi"]:.2f}',
        "nghi_giua_nhom": f'{cfg["nghi_nhom"]:.2f}',
        "so_nguoi_moi_nhom": str(cfg["so_nguoi_nhom"]),
        "nghi_giua_doan": f'{cfg["nghi_doan"]:.2f}',
        "nhan_manh_tien": "1" if cfg.get("nhan_manh_tien") else "0",
    }
    parser["DocVanBan"] = {
        "nghi_giua_cau": f'{cfg["nghi_cau"]:.2f}',
        "nghi_giua_doan_vb": f'{cfg["nghi_doan_vb"]:.2f}',
        "so_ky_tu_moi_doan": str(cfg["so_ky_tu"]),
        "doc_so_bang_chu": "1" if cfg["doc_so_bang_chu"] else "0",
        "bo_ky_hieu_markdown": "1" if cfg["bo_markdown"] else "0",
    }

    def rel(p):
        try:
            return str(Path(p).relative_to(BASE_DIR))
        except ValueError:
            return str(p)

    parser["HeThong"] = {"file_cong_duc": rel(cfg["data_file"]),
                         "ffplay": rel(cfg["ffplay"])}
    with CONFIG_FILE.open("w", encoding="utf-8") as f:
        parser.write(f)


def ap_dung_phong_cach(cfg: dict, ten: str):
    """Áp dụng một phong cách dựng sẵn: đổi style VieNeu-TTS + khoảng nghỉ
    câu/đoạn do chương trình tự chèn. Nếu ten không hợp lệ, giữ nguyên."""
    pc = PHONG_CACH.get(ten)
    if pc:
        cfg["phong_cach"] = ten
        cfg["nghi_cau"] = pc["nghi_cau"]
        cfg["nghi_doan_vb"] = pc["nghi_doan"]
    return cfg


MAU_CONGDUC = """# FILE DANH SÁCH CÔNG ĐỨC
# Mỗi dòng gồm 2 cột, cách nhau bằng phím TAB:
#     Tên người hoặc đơn vị  <TAB>  Số tiền
#
# - Dòng bắt đầu bằng dấu # là ghi chú, chương trình không đọc.
# - Dòng không có số tiền được đọc như tiêu đề nhóm.
# - Không cần sửa "ông/bà", dấu gạch ngang hay 1000.000; chương trình tự đọc.
#
# Ví dụ (xoá dấu # ở đầu dòng để dùng thật):
# Gia đình ông/bà Líu - Điện\t200.000
# Bà Đỗ Thị Vang\t500.000
# Ủy ban MTTQ Việt Nam xã Ân Thi\t1000.000
"""


# ---------------------------------------------------------------------------
# TỰ ĐỘNG TẢI FFMPEG (ffplay.exe) KHI THIẾU
# ---------------------------------------------------------------------------
# Nguồn: BtbN/FFmpeg-Builds (https://github.com/BtbN/FFmpeg-Builds) - build
# tĩnh (static) cho Windows, cập nhật hàng ngày. URL "latest" là đường dẫn
# cố định, GitHub luôn trỏ nó tới bản build mới nhất nên không cần sửa URL
# này theo thời gian. Dùng bản "gpl" (không phải "-shared") vì đây là bản
# thực thi độc lập (standalone), không cần kèm theo các file .dll khác.

FFMPEG_DOWNLOAD_URL = (
    "https://github.com/BtbN/FFmpeg-Builds/releases/download/latest/"
    "ffmpeg-master-latest-win64-gpl.zip"
)


def tai_ffmpeg_tu_dong(bin_dir: Path, bao_tien_do=None) -> Path:
    """Tải ffplay.exe (kèm ffmpeg.exe, ffprobe.exe nếu có) từ bản FFmpeg
    build mới nhất trên GitHub, giải nén và chép vào bin_dir.

    bao_tien_do: hàm callback nhận 1 chuỗi mô tả tiến độ, gọi để cập nhật
    giao diện hoặc in ra console. Có thể để None.

    Trả về đường dẫn ffplay.exe sau khi tải xong. Ném ngoại lệ nếu lỗi
    (mất mạng, không tìm thấy ffplay.exe trong bản tải về...).
    """
    import tempfile
    import urllib.request
    import zipfile

    def bao(msg):
        if bao_tien_do:
            bao_tien_do(msg)

    bin_dir = Path(bin_dir)
    bin_dir.mkdir(parents=True, exist_ok=True)

    with tempfile.TemporaryDirectory(prefix="ffmpeg_giongdoc_") as tmp:
        tmp_path = Path(tmp)
        zip_path = tmp_path / "ffmpeg.zip"

        bao("Đang tải FFmpeg từ GitHub (khoảng 90–140 MB)...")
        req = urllib.request.Request(
            FFMPEG_DOWNLOAD_URL,
            headers={"User-Agent": "Mozilla/5.0 (DocCongDuc)"},
        )
        with urllib.request.urlopen(req, timeout=30) as resp:
            tong = int(resp.headers.get("Content-Length", 0) or 0)
            da_tai = 0
            with open(zip_path, "wb") as f:
                while True:
                    chunk = resp.read(256 * 1024)
                    if not chunk:
                        break
                    f.write(chunk)
                    da_tai += len(chunk)
                    if tong:
                        pct = da_tai * 100 // tong
                        bao(f"Đang tải... {pct}%  "
                            f"({da_tai // (1024*1024)} / {tong // (1024*1024)} MB)")
                    else:
                        bao(f"Đang tải... {da_tai // (1024*1024)} MB")

        bao("Đang giải nén...")
        extract_dir = tmp_path / "giai_nen"
        with zipfile.ZipFile(zip_path) as zf:
            zf.extractall(extract_dir)

        ffplay_src = next(extract_dir.rglob("ffplay.exe"), None)
        if ffplay_src is None:
            raise RuntimeError(
                "Không tìm thấy ffplay.exe trong bản tải về. Có thể "
                "BtbN/FFmpeg-Builds đã đổi cấu trúc file, hoặc bản tải "
                "về bị lỗi giữa chừng."
            )

        bao("Đang chép file vào ffmpeg\\bin...")
        dest = bin_dir / "ffplay.exe"
        shutil.copy2(ffplay_src, dest)

        # Chép luôn ffmpeg.exe / ffprobe.exe nếu có, phòng khi cần sau này.
        for ten in ("ffmpeg.exe", "ffprobe.exe"):
            nguon = ffplay_src.parent / ten
            if nguon.exists():
                shutil.copy2(nguon, bin_dir / ten)

        bao(f"Xong: {dest}")
        return dest


# ---------------------------------------------------------------------------
# VIENEU-TTS CHẠY TẠI MÁY (CPU, offline sau lần đầu)
# ---------------------------------------------------------------------------
# Nguồn giọng thứ hai bên cạnh Edge TTS. Dùng gói `vieneu` (pip install
# vieneu) - bản CPU mặc định chạy qua ONNX Runtime, KHÔNG cần PyTorch,
# KHÔNG cần card đồ hoạ. Giọng dựng sẵn (list_preset_voices) chạy được trên
# CPU; nhân bản giọng từ audio mẫu cần GPU nên KHÔNG hỗ trợ ở đây.
#
# Mô hình chỉ tải một lần từ Hugging Face (vài trăm MB) khi lần đầu chọn
# nguồn giọng này; các lần sau đọc offline hoàn toàn.

_vieneu_instance = None
_vieneu_lock = threading.Lock()


def tai_tep_nhan_ban_giong(bao_tien_do=None) -> bool:
    """Tải speaker_encoder.onnx về cùng kho mô hình.

    Tệp này (28 MB) chỉ được VieNeu lấy về đúng lúc nhân bản giọng lần đầu,
    không đi kèm khi tải mô hình đọc. Thiếu nó thì chương trình không dám cắt
    đường mạng lúc khởi động, nên máy nào cũng phải chờ máy chủ trả lời mỗi
    lần mở - đo được 33,8 giây thay vì 9,3 giây. Kéo về ngay lúc cài đặt là
    xong cả hai chuyện: mở nhanh, và nhân bản giọng chạy được khi không mạng.
    """
    def bao(msg):
        if bao_tien_do:
            bao_tien_do(msg)

    if mo_hinh_da_du_tren_dia():
        bao("Đã có sẵn phần nhân bản giọng.")
        return True
    try:
        from huggingface_hub import hf_hub_download
    except ImportError:
        # Không dùng ký tự lạ như "⚠" ở đây: hàm này in ra cửa sổ dòng lệnh
        # của CaiDat.bat, mà bảng mã cp1252 nuốt không nổi - đã vấp một lần.
        bao("[!] Thieu thu vien huggingface_hub, bo qua phan nhan ban giong.")
        return False
    try:
        hf_hub_download(KHO_VIENEU_HF, TEP_NHAN_BAN)
        return True
    except Exception as e:
        # Không phải lỗi chí mạng: đọc vẫn chạy, chỉ là nhân bản giọng sẽ cần
        # mạng vào lần đầu dùng, và khởi động còn chậm.
        bao(f"[!] Chua tai duoc phan nhan ban giong ({e}). Doc van dung "
            "binh thuong.")
        return False


def huong_dan_cai_vieneu() -> str:
    """VieNeu-TTS bị loại khỏi bản .exe đóng gói (để giữ file nhẹ, khởi
    động nhanh - xem DongGoi.bat). Trả về hướng dẫn đúng theo việc đang
    chạy bản .exe hay chạy trực tiếp bằng Python."""
    if getattr(sys, "frozen", False):
        return (
            "Bản chương trình đã đóng gói (.exe) KHÔNG kèm VieNeu-TTS - "
            "để giữ file nhẹ và khởi động nhanh cho mọi người.\n\n"
            "Muốn dùng VieNeu-TTS: chạy trực tiếp bằng Python thay vì "
            "file .exe:\n"
            "  1. Cài Python + chạy CaiDat.bat, chọn Y khi được hỏi cài "
            "VieNeu-TTS\n"
            "  2. Chạy: py DocCongDuc.py\n\n"
            "Hai thẻ chính vẫn đọc bình thường bằng Edge TTS trong bản .exe."
        )
    return "Chưa cài đặt VieNeu-TTS.\nChạy: pip install vieneu"


def vieneu_da_cai_dat() -> bool:
    try:
        import vieneu  # noqa: F401
        return True
    except ImportError:
        return False


def dam_bao_vieneu_san_sang(bao_tien_do=None):
    """Import và khởi tạo Vieneu() một lần duy nhất, dùng lại cho các lần
    sau (tránh nạp lại mô hình mỗi câu, rất chậm). An toàn khi gọi từ
    nhiều luồng.

    HF_HOME đã được đặt trỏ vào "vieneu_models" cạnh chương trình ngay
    lúc nạp module (xem đầu file) - nên mô hình tải về nằm gọn trong
    D:\\GiongDoc thay vì thư mục cache ẩn mặc định của Windows."""
    global _vieneu_instance

    def bao(msg):
        if bao_tien_do:
            bao_tien_do(msg)

    with _vieneu_lock:
        if _vieneu_instance is not None:
            return _vieneu_instance
        try:
            from vieneu import Vieneu
        except ImportError:
            raise RuntimeError(huong_dan_cai_vieneu())
        # Nói đúng việc đang làm: đã có mô hình trên đĩa thì chỉ là nạp, nói
        # "đang tải" khiến người dùng tưởng máy đang ngốn mạng của họ.
        if mo_hinh_da_du_tren_dia():
            bao("Đang mở bộ giọng đọc có sẵn trong máy…")
        else:
            bao("Lần đầu chạy: đang tải bộ giọng đọc về máy (vài trăm MB, "
                "mất vài phút tuỳ mạng). Những lần sau sẽ không cần tải nữa.")
        try:
            _vieneu_instance = Vieneu()
        except Exception as e:
            raise RuntimeError(f"Không khởi tạo được VieNeu-TTS: {e}")
        bao("Đã nạp xong mô hình VieNeu-TTS.")
        # Đăng ký lại MỌI giọng riêng đã tạo trước đó - không giả định
        # thư viện tự nhớ giữa các lần chạy chương trình, tự làm lại cho
        # chắc. Lỗi ở một giọng không làm hỏng cả quá trình khởi động.
        for g in doc_ds_giong_rieng():
            try:
                _vieneu_instance.add_voice(g["id"], g["file"])
            except Exception as e:
                bao(f"⚠ Không đăng ký lại được giọng riêng '{g['ten']}': {e}")
        return _vieneu_instance


# ---------------------------------------------------------------------------
# GIỌNG RIÊNG - tạo từ file mẫu do người dùng cung cấp (đã xin phép), lưu
# lại để chọn dùng nhiều lần như giọng dựng sẵn. Lưu ý về mặt kỹ thuật:
# tính năng add_voice của VieNeu-TTS bản mặc định (v3 Turbo) được tài
# liệu chính thức ghi là YÊU CẦU GPU THẬT - trên máy chỉ có CPU có thể
# THẤT BẠI. Có dấu hiệu bản cũ hơn (v2 Turbo, GGUF) hỗ trợ trên CPU
# nhưng chưa kiểm chứng được trên máy thật - hàm dưới đây thử với engine
# hiện có, báo lỗi rõ ràng nếu thất bại thay vì giả vờ chắc chắn.
# ---------------------------------------------------------------------------

def doc_ds_giong_rieng() -> list:
    """Đọc danh sách giọng riêng đã tạo:
    [{"id":.., "ten":.., "file":.., "ngay_tao":..}, ...]"""
    if not GIONG_RIENG_FILE.exists():
        return []
    try:
        data = json.loads(GIONG_RIENG_FILE.read_text(encoding="utf-8"))
        if isinstance(data, list):
            return [g for g in data if isinstance(g, dict) and "id" in g
                    and "ten" in g and "file" in g]
    except (json.JSONDecodeError, OSError):
        pass
    return []


def luu_ds_giong_rieng(ds: list):
    GIONG_RIENG_DIR.mkdir(parents=True, exist_ok=True)
    GIONG_RIENG_FILE.write_text(
        json.dumps(ds, ensure_ascii=False, indent=1), encoding="utf-8")


def _id_giong_rieng_moi(ds_hien_co: list) -> str:
    """ID nội bộ, ổn định, không trùng - tách biệt khỏi tên hiển thị để
    tránh lỗi ký tự đặc biệt/dấu tiếng Việt khi truyền cho thư viện."""
    so = 1
    ton_tai = {g["id"] for g in ds_hien_co}
    while f"rieng_{so:03d}" in ton_tai:
        so += 1
    return f"rieng_{so:03d}"


def tao_giong_rieng(ten_hien_thi: str, duong_dan_mau, bao_tien_do=None) -> dict:
    """Tạo một giọng riêng mới từ file mẫu, đăng ký với VieNeu-TTS và lưu
    lại để dùng nhiều lần sau này. Trả về mục vừa tạo trong danh sách.
    Ném RuntimeError với thông báo rõ ràng nếu thất bại (kể cả trường hợp
    máy không đủ điều kiện phần cứng cho tính năng này)."""
    def bao(msg):
        if bao_tien_do:
            bao_tien_do(msg)

    ten_hien_thi = (ten_hien_thi or "").strip()
    if not ten_hien_thi:
        raise RuntimeError("Chưa đặt tên cho giọng riêng.")

    duong_dan_mau = Path(duong_dan_mau)
    if not duong_dan_mau.exists():
        raise RuntimeError(f"Không tìm thấy file mẫu:\n{duong_dan_mau}")

    ds = doc_ds_giong_rieng()
    if any(g["ten"] == ten_hien_thi for g in ds):
        raise RuntimeError(
            f'Đã có giọng riêng tên "{ten_hien_thi}". Chọn tên khác, '
            "hoặc xoá giọng cũ trước (menu Giọng đọc > Xoá giọng riêng).")

    ma = _id_giong_rieng_moi(ds)
    GIONG_RIENG_DIR.mkdir(parents=True, exist_ok=True)
    file_luu = GIONG_RIENG_DIR / f"{ma}{duong_dan_mau.suffix.lower() or '.wav'}"

    bao(f"Đang chép file mẫu vào {file_luu.name}...")
    try:
        shutil.copy2(duong_dan_mau, file_luu)
    except OSError as e:
        raise RuntimeError(f"Không chép được file mẫu: {e}")

    bao("Đang tạo giọng riêng (VieNeu-TTS xử lý mẫu giọng)...")
    tts = dam_bao_vieneu_san_sang(bao_tien_do)
    try:
        tts.add_voice(ma, str(file_luu))
    except Exception as e:
        try:
            file_luu.unlink()
        except OSError:
            pass
        loi_text = str(e)
        if "torch" in loi_text.lower():
            raise RuntimeError(
                "Không tạo được giọng riêng: thiếu thư viện PyTorch "
                "(torch) - tính năng nhân bản giọng của VieNeu-TTS cần "
                "thư viện này, KHÔNG được cài sẵn để giữ bản cài đặt "
                "chính nhẹ (đọc công đức bình thường không cần).\n\n"
                "PyTorch chạy được trên CPU bình thường, không bắt buộc "
                "phải có card đồ hoạ - chỉ là chưa cài. Thử cài rồi tạo "
                "lại giọng:\n\n"
                "py -m pip install torch --index-url "
                "https://download.pytorch.org/whl/cpu\n\n"
                f"Chi tiết lỗi gốc: {loi_text}")
        raise RuntimeError(
            "Không tạo được giọng riêng.\n\n"
            "Máy không có card đồ hoạ - có thể tính năng nhân bản giọng "
            "của VieNeu-TTS cần GPU thật cho đúng bước xử lý này. Bản cũ "
            "hơn (v2 Turbo, GGUF) có dấu hiệu hỗ trợ trên CPU nhưng chưa "
            f"kiểm chứng được.\n\nChi tiết lỗi: {loi_text}")

    muc_moi = {"id": ma, "ten": ten_hien_thi, "file": str(file_luu),
              "ngay_tao": time.strftime("%Y-%m-%d %H:%M")}
    ds.append(muc_moi)
    try:
        luu_ds_giong_rieng(ds)
    except OSError as e:
        raise RuntimeError(f"Tạo giọng thành công nhưng không lưu được "
                           f"danh sách: {e}")
    bao(f"Đã tạo xong giọng riêng: {ten_hien_thi}")
    return muc_moi


def xoa_giong_rieng(ma: str):
    """Xoá một giọng riêng khỏi danh sách và xoá file mẫu đã lưu."""
    ds = doc_ds_giong_rieng()
    muc = next((g for g in ds if g["id"] == ma), None)
    if muc is None:
        return
    ds = [g for g in ds if g["id"] != ma]
    luu_ds_giong_rieng(ds)
    try:
        Path(muc["file"]).unlink()
    except OSError:
        pass


def lay_danh_sach_giong_day_du(bao_tien_do=None):
    """Danh sách giọng đầy đủ cho giao diện: giọng riêng (đánh dấu rõ,
    xếp trước) + giọng dựng sẵn. Cùng định dạng {'id':.., 'ten':..}."""
    rieng = [{"id": g["id"], "ten": f'🎙️ {g["ten"]}  (giọng riêng)'}
             for g in doc_ds_giong_rieng()]
    dung_san = lay_danh_sach_giong_vieneu(bao_tien_do)
    return rieng + dung_san


def lay_danh_sach_giong_vieneu(bao_tien_do=None):
    """Trả về list các dict {'id':..., 'nhan':...} - dò thật từ thư viện,
    không đoán cứng, để luôn khớp mô hình hiện có."""
    tts = dam_bao_vieneu_san_sang(bao_tien_do)
    try:
        voices = tts.list_preset_voices()
    except Exception as e:
        raise RuntimeError(f"Không lấy được danh sách giọng: {e}")
    ket_qua = []
    for item in voices:
        if isinstance(item, (list, tuple)) and len(item) >= 2:
            nhan, vid = item[0], item[1]
        else:
            nhan = vid = str(item)
        ket_qua.append({"id": vid, "ten": nhan})
    return ket_qua


# ---------------------------------------------------------------------------
# NHẤN MẠNH SỐ TIỀN LỚN (tuỳ chọn, mặc định TẮT)
# ---------------------------------------------------------------------------
# VieNeu KHÔNG có tham số âm lượng, tốc độ hay cao độ - đã đo chữ ký infer():
# chỉ có voice/style/temperature/top_k. Nên "đọc to hơn" chỉ làm được bằng
# cách nhân biên độ sóng SAU khi tổng hợp, và "nhấn mạnh" thì mượn khoảng
# nghỉ dài hơn sau câu để câu đó đứng tách ra.
#
# Đo trên máy: đỉnh sóng một câu quanh 0,53 - còn khoảng 5,3 dB trước khi vỡ
# tiếng. Trần +3 dB đã chừa biên an toàn, nhưng câu nào to sẵn thì vẫn phải
# hạ tay xuống, nên còn một trần thứ hai tính theo đỉnh thật của từng câu.
DINH_AN_TOAN = 0.95
KHUECH_DAI_TOI_DA = 1.41          # +3 dB
HE_SO_NGHI_NHAN_MANH = 1.6        # nghỉ sau câu tiền lớn dài hơn bấy nhiêu lần

# Ngưỡng tính theo chính danh sách đang đọc, KHÔNG phải con số cố định: dữ
# liệu thật ở chùa nằm trong khoảng 200.000-500.000, đặt mốc cứng kiểu "trên
# một triệu" thì không ai được nhấn và tính năng thành vô dụng.
PHAN_VI_NHAN_MANH = 0.75
TOI_THIEU_DE_XEP_HANG = 4         # ít hơn thì không đủ cơ sở chia nhóm cao/thấp


def nguong_nhan_manh(records) -> int:
    """Số tiền từ mức này trở lên thì được đọc nhấn mạnh. 0 = không nhấn ai."""
    tien = []
    for r in records:
        if r.get("kind") != "nguoi":
            continue
        try:
            tien.append(parse_money(r["amount"]))
        except (ValueError, KeyError):
            continue
    if len(tien) < TOI_THIEU_DE_XEP_HANG:
        return 0
    tien.sort()
    return tien[min(len(tien) - 1, int(len(tien) * PHAN_VI_NHAN_MANH))]


def _khuech_dai(audio, he_so: float):
    """Nhân biên độ sóng, tự hạ hệ số xuống nếu câu này sắp vỡ tiếng.

    Giọng đọc ở chùa phát qua loa ngoài trời, tiếng rè vì vỡ biên nghe rõ hơn
    hẳn so với nghe bằng tai nghe - thà nhấn nhẹ hơn mong muốn còn hơn rè.
    """
    if he_so <= 1.0:
        return audio
    try:
        import numpy as np
    except ImportError:
        return audio
    try:
        dinh = float(np.max(np.abs(audio)))
    except (TypeError, ValueError):
        return audio
    if dinh <= 0:
        return audio
    thuc = min(he_so, KHUECH_DAI_TOI_DA, DINH_AN_TOAN / dinh)
    return audio * thuc if thuc > 1.0 else audio


def tong_hop_vieneu(text: str, voice_id: str, style: str = "",
                    bao_tien_do=None, khuech_dai: float = 1.0) -> bytes:
    """Tổng hợp một câu bằng VieNeu-TTS, trả về bytes định dạng WAV.

    style: "tu_nhien" | "tin_tuc" | "doc_truyen" (xem PHONG_CACH). Nếu
    bản vieneu đang cài không nhận tham số style (TypeError), tự động
    thử lại không kèm style thay vì báo lỗi - để không phụ thuộc cứng
    vào đúng một phiên bản API.
    """
    if not (text or "").strip():
        return b""
    tts = dam_bao_vieneu_san_sang(bao_tien_do)

    def goi(**kw):
        if voice_id:
            kw["voice"] = voice_id
        return tts.infer(text, **kw)

    try:
        try:
            audio = goi(style=style) if style else goi()
        except TypeError:
            # Bản vieneu đang cài không nhận tham số style - đọc bình
            # thường không kèm phong cách, còn hơn báo lỗi cho người dùng.
            audio = goi()
    except Exception as e:
        raise RuntimeError(f"VieNeu-TTS lỗi khi đọc câu: {e}")

    # Khuếch đại khi sóng còn là mảng số thực, trước lúc đóng thành WAV -
    # sửa ở đây thì cả đọc, nghe thử lẫn xuất file đều nhận cùng một tiếng,
    # không phải đi vá ba nơi rồi quên một nơi.
    audio = _khuech_dai(audio, khuech_dai)

    tmp_path = None
    try:
        with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as f:
            tmp_path = f.name
        tts.save(audio, tmp_path)
        return Path(tmp_path).read_bytes()
    finally:
        if tmp_path:
            try:
                Path(tmp_path).unlink()
            except OSError:
                pass


def tao_file_thieu():
    if not CONFIG_FILE.exists():
        CONFIG_FILE.write_text(CAUHINH_MAC_DINH, encoding="utf-8")
    if not NOIDUNG_FILE.exists():
        NoiDung().save(NOIDUNG_FILE)
    if not TUDIEN_FILE.exists():
        save_tudien_mac_dinh(TUDIEN_FILE)
    mac_dinh_dl = BASE_DIR / "congduc.txt"
    if not mac_dinh_dl.exists():
        try:
            mac_dinh_dl.write_text(MAU_CONGDUC, encoding="utf-8-sig")
        except OSError:
            pass


# ---------------------------------------------------------------------------
# SỐ / TIỀN ĐỌC BẰNG CHỮ
# ---------------------------------------------------------------------------

DIGITS = ["không", "một", "hai", "ba", "bốn", "năm", "sáu", "bảy", "tám", "chín"]


def read_three_digits(n: int, full: bool = False) -> str:
    tr, ch, dv = n // 100, (n // 10) % 10, n % 10
    parts = []
    if tr:
        parts += [DIGITS[tr], "trăm"]
    elif full and (ch or dv):
        parts += ["không", "trăm"]
    if ch:
        parts += ["mười"] if ch == 1 else [DIGITS[ch], "mươi"]
    elif dv and (tr or (full and dv)):
        parts.append("lẻ")
    if dv:
        if ch >= 2 and dv == 1:
            parts.append("mốt")
        elif ch >= 1 and dv == 5:
            parts.append("lăm")
        else:
            parts.append(DIGITS[dv])
    return " ".join(parts)


def number_to_vietnamese(n: int) -> str:
    if n == 0:
        return "không"
    if n < 0:
        return "âm " + number_to_vietnamese(-n)
    units = [(1_000_000_000, "tỷ"), (1_000_000, "triệu"), (1_000, "nghìn"), (1, "")]
    groups, remainder = [], n
    for value, label in units:
        if remainder >= value:
            q = remainder // value
            remainder %= value
            groups.append((q, label))
    result, first = [], True
    for q, label in groups:
        result.append(read_three_digits(q, full=(not first)))
        if label:
            result.append(label)
        first = False
    return " ".join(x for x in result if x).strip()


MONEY_SUFFIX = [(r"(?i)(triệu|tr|củ)\b", 1_000_000), (r"(?i)(nghìn|ngàn|k)\b", 1_000)]


def parse_money(text: str) -> int:
    raw = (text or "").strip()
    if not raw:
        raise ValueError("Số tiền trống")
    he_so = 1
    for pattern, factor in MONEY_SUFFIX:
        if re.search(pattern, raw):
            so_phan = re.sub(r"[^\d.,]", "", raw)
            if "." not in so_phan and "," not in so_phan:
                he_so = factor
            break
    digits = re.sub(r"[^\d]", "", raw)
    if not digits:
        raise ValueError(f"Số tiền không hợp lệ: {text}")
    return int(digits) * he_so


def format_money_for_reading(text: str) -> str:
    return number_to_vietnamese(parse_money(text)) + " đồng"


def format_money_for_display(text: str) -> str:
    try:
        return f"{parse_money(text):,}".replace(",", ".")
    except ValueError:
        return text


# ---------------------------------------------------------------------------
# CHUẨN HOÁ TÊN NGƯỜI
# ---------------------------------------------------------------------------

CHUC_DANH = {
    "bí", "trưởng", "phó", "chủ", "giám", "hiệu", "tổ", "đội", "chi", "ban",
    "cán", "cựu", "nguyên", "đại", "thủ", "kế", "hội", "đảng", "công", "nhân",
    "giáo", "thầy", "cô", "sư", "thượng", "thôn", "xã", "huyện", "tỉnh", "khu",
    "xóm", "làng", "phòng", "viện", "chánh", "phụ", "ủy", "uỷ", "bs", "ts",
}


def _ap_dung_tudien(text: str, tudien: dict) -> str:
    if not tudien:
        return text
    for key in sorted(tudien, key=len, reverse=True):
        if not key:
            continue
        pattern = r"(?<![0-9A-Za-zÀ-ỹ])" + re.escape(key) + r"(?![0-9A-Za-zÀ-ỹ])"
        text = re.sub(pattern, tudien[key].replace("\\", r"\\"), text)
    return text


def _xu_ly_dau_phay(text: str) -> str:
    if "," not in text:
        return text
    dau, sau = text.split(",", 1)
    dau, sau = dau.strip(), sau.strip()
    if not sau or not dau:
        return text.replace(",", ", ")
    tu_dau = sau.split()[0]
    if tu_dau[:1].islower() or tu_dau.lower().strip(".") in CHUC_DANH:
        return f"{dau}, {sau[:1].upper()}{sau[1:]}"
    if re.search(r"(?i)^(ông|bà|anh|chị|cô|chú|bác|cháu|em|thầy|sư)\b", sau):
        xung_ho = ""
    elif re.search(r"(?i)\bthị\b", sau):
        xung_ho = "bà "
    elif re.search(r"(?i)\bvăn\b", sau):
        xung_ho = "ông "
    else:
        xung_ho = ""
    return f"{dau} và {xung_ho}{sau}"


def normalize_name(raw: str, tudien: dict = None) -> str:
    name = (raw or "").strip()
    if not name:
        return ""
    name = _ap_dung_tudien(name, tudien or {})
    name = re.sub(r"(?i)\bông\s*/\s*bà\b", "ông bà", name)
    name = re.sub(r"(?i)\bbà\s*/\s*ông\b", "bà ông", name)
    name = re.sub(r"(?i)\banh\s*/\s*chị\b", "anh chị", name)
    name = re.sub(r"(?i)\bchị\s*/\s*anh\b", "chị anh", name)
    name = re.sub(r"(?i)\bô\s*/\s*b\b", "ông bà", name)
    name = name.replace("/", " ")
    name = re.sub(r"\s*[-–—]\s*", " ", name)
    name = re.sub(r"[()\[\]{}\"“”]", " ", name)
    name = name.replace("&", " và ")
    name = re.sub(r"\s*\+\s*", " và ", name)
    name = re.sub(r"\s+", " ", name).strip(" .;:")
    name = _xu_ly_dau_phay(name)
    return re.sub(r"\s+", " ", name).strip()


# ---------------------------------------------------------------------------
# CHUẨN HOÁ VĂN BẢN TIẾNG VIỆT
# ---------------------------------------------------------------------------

KY_HIEU_SOM = [
    (r"(?i)\bTP\s*\.\s*(?=[A-ZÀ-Ỹ])", "Thành phố "),
    (r"(?i)\bĐ\s*/\s*c\b", "Đồng chí"),
    (r"(?i)\bv\s*\.\s*v\s*\.?", " vân vân."),
    (r"(?i)\bTP\.?HCM\b", "Thành phố Hồ Chí Minh"),
    (r"(?<=[A-ZÀ-Ỹ])\.(?=[A-ZÀ-Ỹ])", " "),
]

KY_HIEU = [
    (r"(\d)\s*%", r"\1 phần trăm"),
    (r"(\d)\s*°\s*C", r"\1 độ C"),
    (r"(\d)\s*℃", r"\1 độ C"),
    (r"(\d)\s*m2\b", r"\1 mét vuông"),
    (r"(\d)\s*m²", r"\1 mét vuông"),
    (r"(\d)\s*km/h", r"\1 ki lô mét trên giờ"),
    (r"(\d)\s*km\b", r"\1 ki lô mét"),
    (r"(\d)\s*kg\b", r"\1 ki lô gam"),
    (r"(\d)\s*(đ|VNĐ|VND)\b", r"\1 đồng"),
    (r"(\d)\s*USD\b", r"\1 đô la Mỹ"),
    (r"(?i)\b([A-Za-zÀ-ỹ]+)\s*/\s*"
     r"(năm|tháng|tuần|ngày|giờ|người|lượt|khẩu|hộ|sào|ha)\b", r"\1 mỗi \2"),
    (r"\s*&\s*", " và "),
    (r"\s*→\s*", " đến "),
    (r"\s*->\s*", " đến "),
    (r"…", "."),
]


def _doi_ngay_thang(text: str) -> str:
    def full(m):
        return f"ngày {int(m.group(1))} tháng {int(m.group(2))} năm {m.group(3)}"

    def full_co_ngay(m):
        return f"{int(m.group(1))} tháng {int(m.group(2))} năm {m.group(3)}"

    def ngan(m):
        d, thang = int(m.group(1)), int(m.group(2))
        return f"ngày {d} tháng {thang}" if 1 <= d <= 31 and 1 <= thang <= 12 \
            else m.group(0)

    def ngan_co_ngay(m):
        d, thang = int(m.group(1)), int(m.group(2))
        return f"{d} tháng {thang}" if 1 <= d <= 31 and 1 <= thang <= 12 \
            else m.group(0)

    text = re.sub(r"(?i)(?<=ngày )(\d{1,2})/(\d{1,2})/(\d{4})\b", full_co_ngay, text)
    text = re.sub(r"(?i)(?<=ngày )(\d{1,2})/(\d{1,2})\b(?!/)", ngan_co_ngay, text)
    text = re.sub(r"\b(\d{1,2})/(\d{1,2})/(\d{4})\b", full, text)
    text = re.sub(r"\b(\d{1,2})/(\d{1,2})\b(?!/)", ngan, text)
    return text


def _doi_so_lon(text: str) -> str:
    def repl(m):
        raw = m.group(0)
        digits = re.sub(r"[^\d]", "", raw)
        if len(digits) < 4 or len(digits) > 13:
            return raw
        try:
            return number_to_vietnamese(int(digits))
        except ValueError:
            return raw

    return re.sub(r"\b\d{1,3}(?:[.,]\d{3})+\b|\b\d{4,13}\b", repl, text)


def chuan_hoa_van_ban(text: str, tudien: dict, cfg: dict) -> str:
    s = text or ""
    if cfg.get("bo_markdown", True):
        s = re.sub(r"^\s{0,3}#{1,6}\s*", "", s, flags=re.M)
        s = re.sub(r"^\s*[-*+•]\s+", "", s, flags=re.M)
        s = re.sub(r"^\s*>\s?", "", s, flags=re.M)
        s = re.sub(r"\*\*(.+?)\*\*", r"\1", s)
        s = re.sub(r"(?<!\w)[*_`]{1,3}(?=\S)|(?<=\S)[*_`]{1,3}(?!\w)", "", s)
        s = re.sub(r"^\s*[-=_]{3,}\s*$", "", s, flags=re.M)
        s = re.sub(r"\|", " ", s)

    for pattern, thay in KY_HIEU_SOM:
        s = re.sub(pattern, thay, s)
    s = _ap_dung_tudien(s, tudien or {})
    s = _doi_ngay_thang(s)
    for pattern, thay in KY_HIEU:
        s = re.sub(pattern, thay, s)
    if cfg.get("doc_so_bang_chu"):
        s = _doi_so_lon(s)

    s = re.sub(r"https?://\S+", " đường dẫn liên kết ", s)
    s = re.sub(r"[()\[\]{}\"“”]", " ", s)
    s = re.sub(r"\s*[-–—]\s+", ", ", s)
    s = re.sub(r"(?<=[A-Za-zÀ-ỹ0-9])\s*/\s*(?=[A-Za-zÀ-ỹ0-9])", " ", s)
    s = re.sub(r"\.{2,}", ".", s)
    s = re.sub(r"\s+", " ", s).strip()
    s = re.sub(r"\s+([,.;:!?])", r"\1", s)
    return s


VIET_TAT = ("tp.", "ts.", "ths.", "gs.", "pgs.", "bs.", "ks.", "vd.", "tr.",
            "st.", "mr.", "mrs.", "dr.", "no.", "vv.", "đ/c.")


def tach_chunk(text: str, max_len: int = 280):
    """Cắt văn bản thành từng mẩu để đọc, kèm vị trí ký tự để tô sáng."""
    chunks = []
    if not (text or "").strip():
        return chunks

    for m in re.finditer(r"[^\n]+(?:\n(?!\s*\n)[^\n]+)*", text):
        d_start, doan = m.start(), m.group()

        cau_spans, bat_dau, i = [], 0, 0
        while i < len(doan):
            if doan[i] in ".!?…":
                j = i + 1
                while j < len(doan) and doan[j] in ".!?…":
                    j += 1
                sau = doan[j:j + 1]
                truoc = doan[max(0, i - 6):i + 1].lower().strip()
                la_viet_tat = any(truoc.endswith(v) for v in VIET_TAT)
                la_so = doan[i - 1:i].isdigit() and sau.isdigit()
                if not la_viet_tat and not la_so and (sau == "" or sau.isspace()):
                    cau_spans.append((bat_dau, j))
                    bat_dau = j
                    while bat_dau < len(doan) and doan[bat_dau].isspace():
                        bat_dau += 1
                    i = bat_dau
                    continue
                i = j
                continue
            i += 1
        if bat_dau < len(doan):
            cau_spans.append((bat_dau, len(doan)))

        cum = []
        for c_start, c_end in cau_spans:
            if c_end - c_start <= max_len:
                cum.append((c_start, c_end))
                continue
            pos = c_start
            while pos < c_end:
                het = min(pos + max_len, c_end)
                if het < c_end:
                    cat = doan.rfind(",", pos + int(max_len * 0.4), het)
                    if cat == -1:
                        cat = doan.rfind(" ", pos + int(max_len * 0.4), het)
                    if cat != -1:
                        het = cat + 1
                cum.append((pos, het))
                pos = het
                while pos < c_end and doan[pos].isspace():
                    pos += 1

        gop = []
        for c_start, c_end in cum:
            if gop and (c_end - gop[-1][0]) <= max_len:
                gop[-1] = (gop[-1][0], c_end)
            else:
                gop.append((c_start, c_end))

        for k, (c_start, c_end) in enumerate(gop):
            raw = doan[c_start:c_end].strip()
            if raw:
                chunks.append({"start": d_start + c_start, "end": d_start + c_end,
                               "raw": raw, "cuoi_doan": (k == len(gop) - 1)})
    return chunks


# ---------------------------------------------------------------------------
# ĐỌC FILE DANH SÁCH CÔNG ĐỨC
# ---------------------------------------------------------------------------

def parse_data_file(path: Path):
    if not path.exists():
        raise FileNotFoundError(f"Không tìm thấy file:\n{path}")

    records, canh_bao = [], []
    with path.open("r", encoding="utf-8-sig", errors="replace") as f:
        for line_no, raw in enumerate(f, 1):
            line = raw.strip()
            if not line or line.startswith("#") or line.startswith(";"):
                continue

            name, amount = line, ""
            if "\t" in line:
                name, amount = line.split("\t", 1)
            else:
                m = re.match(r"^(.*?)\s{2,}([\d.,\s]+(?:đ|đồng|k|tr)?)\s*$", line)
                if m:
                    name, amount = m.group(1), m.group(2)
                else:
                    m2 = re.match(r"^(.*?[^\d.,])\s+([\d][\d.,]*\s*(?:đ|đồng|k|tr)?)$",
                                  line)
                    if m2:
                        name, amount = m2.group(1), m2.group(2)

            name, amount = name.strip(), amount.strip()
            if not name:
                continue
            if not amount:
                records.append({"kind": "tieude", "name": name, "amount": "",
                                "line_no": line_no})
                continue
            try:
                parse_money(amount)
            except ValueError:
                canh_bao.append(f"Dòng {line_no}: không hiểu số tiền “{amount}”.")
                records.append({"kind": "tieude", "name": line, "amount": "",
                                "line_no": line_no})
                continue
            records.append({"kind": "nguoi", "name": name, "amount": amount,
                            "line_no": line_no})
    return records, canh_bao


def tach_doan(text: str):
    doan = [d.strip() for d in re.split(r"\n\s*\n", text or "") if d.strip()]
    return [re.sub(r"\s*\n\s*", " ", d) for d in doan]


def build_playlist_congduc(records, noidung: NoiDung, cfg: dict, tudien: dict,
                           doc_loi_dan=True):
    playlist = []
    tong_nguoi = sum(1 for r in records if r["kind"] == "nguoi")
    stt = 0
    nguong = nguong_nhan_manh(records) if cfg.get("nhan_manh_tien") else 0

    if doc_loi_dan and noidung.dau_bat:
        for doan in tach_doan(noidung.dau_text):
            playlist.append({"loai": "mo_dau", "text": doan,
                             "nghi": cfg["nghi_doan"], "rec": None,
                             "stt": 0, "tong": tong_nguoi})
        if playlist:
            playlist[-1]["nghi"] = cfg["nghi_nhom"]

    for rec in records:
        if rec["kind"] == "tieude":
            playlist.append({"loai": "tieude",
                             "text": normalize_name(rec["name"], tudien) + ".",
                             "nghi": cfg["nghi_nhom"], "rec": rec,
                             "stt": stt, "tong": tong_nguoi})
            continue

        stt += 1
        ten = normalize_name(rec["name"], tudien)
        tien = format_money_for_reading(rec["amount"])
        try:
            cau = noidung.mau_cau.format(ten=ten, tien=tien)
        except (KeyError, IndexError, ValueError):
            cau = MAU_CAU_MAC_DINH.format(ten=ten, tien=tien)

        nghi = cfg["nghi_nguoi"]
        if cfg["so_nguoi_nhom"] and stt % cfg["so_nguoi_nhom"] == 0:
            nghi = cfg["nghi_nhom"]

        # Nhấn mạnh: đọc to hơn một chút và để lặng lâu hơn sau câu đó, cho
        # tên vừa đọc còn đọng lại thay vì bị tên kế tiếp đè lên ngay.
        khuech_dai = 1.0
        nhan_manh = False
        if nguong:
            try:
                nhan_manh = parse_money(rec["amount"]) >= nguong
            except ValueError:
                nhan_manh = False
        if nhan_manh:
            khuech_dai = KHUECH_DAI_TOI_DA
            nghi = nghi * HE_SO_NGHI_NHAN_MANH

        playlist.append({"loai": "nguoi", "text": cau, "nghi": nghi, "rec": rec,
                         "stt": stt, "tong": tong_nguoi,
                         "khuech_dai": khuech_dai, "nhan_manh": nhan_manh})

        if (doc_loi_dan and noidung.giua_bat and noidung.giua_sau_moi
                and stt % noidung.giua_sau_moi == 0 and stt != tong_nguoi):
            for doan in tach_doan(noidung.giua_text):
                playlist.append({"loai": "giua", "text": doan,
                                 "nghi": cfg["nghi_doan"], "rec": None,
                                 "stt": stt, "tong": tong_nguoi})
            playlist[-1]["nghi"] = cfg["nghi_nhom"]

    if doc_loi_dan and noidung.cuoi_bat:
        for doan in tach_doan(noidung.cuoi_text):
            playlist.append({"loai": "ket", "text": doan, "nghi": cfg["nghi_doan"],
                             "rec": None, "stt": stt, "tong": tong_nguoi})
    return playlist


def build_playlist_vanban(text: str, cfg: dict, tudien: dict):
    playlist = []
    for c in tach_chunk(text, cfg["so_ky_tu"]):
        doc = chuan_hoa_van_ban(c["raw"], tudien, cfg)
        if not doc.strip():
            continue
        playlist.append({
            "loai": "cau", "text": doc,
            "nghi": cfg["nghi_doan_vb"] if c["cuoi_doan"] else cfg["nghi_cau"],
            "rec": None, "start": c["start"], "end": c["end"], "goc": c["raw"],
        })
    # đánh số liên tục sau khi đã bỏ các mẩu rỗng
    tong = len(playlist)
    for i, seg in enumerate(playlist, 1):
        seg["stt"], seg["tong"] = i, tong
    return playlist


def uoc_luong_thoi_gian(playlist, cfg) -> str:
    """Ước lượng thời gian đọc, để người dùng biết bài dài bao nhiêu."""
    if not playlist:
        return "—"
    ky_tu = sum(len(s["text"]) for s in playlist)
    nghi = sum(s["nghi"] for s in playlist)
    giay = ky_tu / 14.0 + nghi
    phut, du = divmod(int(giay + 0.5), 60)
    return f"{phut} phút {du:02d} giây" if phut else f"{du} giây"


# ---------------------------------------------------------------------------
# BỘ ĐỌC
# ---------------------------------------------------------------------------

class Speaker:
    """Phát giọng đọc bằng VieNeu-TTS (chạy tại máy, CPU). Mỗi lần tổng
    hợp trả về (bytes, dinh_dang) - dinh_dang luôn là 'wav'."""

    # Chốt chặn cuối cho luật "một nguồn phát tiếng tại một thời điểm". Mọi
    # tiếng động của chương trình đều chui qua play(), nên giữ luật ngay tại
    # đây thì không nguồn nào lọt - kể cả nguồn viết thêm sau này quên đi dừng
    # nguồn đang chạy. Trước đó luật nằm rải rác ở từng nơi gọi, mỗi nơi phải
    # tự nhớ, và đã quên thật: bấm Nghe thử rồi bấm Phát ngay trong lúc câu
    # nghe thử còn đang tổng hợp là hai giọng nói chồng lên nhau.
    #
    # KHÔNG thay thế SỐ PHIÊN trong bo_doc/nghe_thu: số phiên chặn ở tầng
    # playlist, chốt này chặn ở tầng tiến trình ffplay. Cần cả hai.
    _khoa_loa = threading.Lock()
    _dang_giu_loa = None

    def _gianh_loa(self):
        """Chiếm loa, trả về nguồn đang giữ trước đó (nếu có ai khác)."""
        with Speaker._khoa_loa:
            cu = Speaker._dang_giu_loa
            Speaker._dang_giu_loa = self
        return cu if cu is not self else None

    def _con_giu_loa(self) -> bool:
        with Speaker._khoa_loa:
            return Speaker._dang_giu_loa is self

    def _nha_loa(self):
        with Speaker._khoa_loa:
            if Speaker._dang_giu_loa is self:
                Speaker._dang_giu_loa = None

    def __init__(self, cfg):
        self.cfg = cfg
        self.player = None
        self._lock = threading.Lock()
        self._pool = concurrent.futures.ThreadPoolExecutor(max_workers=1)
        # Hàng đợi NẠP TRƯỚC: {khoá vị trí -> Future}. Lấy ra là xoá.
        self._cache = {}
        # KHO theo nội dung: {(giọng, khuếch đại, chữ) -> (bytes, định dạng)}.
        # Giữ lại để nghe lại và xuất lại không phải tổng hợp lần nữa.
        # OrderedDict để bỏ được mẩu lâu không đụng tới nhất khi đầy.
        self._kho = collections.OrderedDict()
        self._kho_byte = 0
        self._khoa_kho_lock = threading.Lock()

    def _synth_blocking(self, text: str, khuech_dai: float = 1.0):
        if not (text or "").strip():
            return b"", "wav"
        style = PHONG_CACH.get(self.cfg.get("phong_cach", ""), {}).get("style", "")
        audio = tong_hop_vieneu(text, self.cfg.get("vieneu_voice_id", ""), style,
                                khuech_dai=khuech_dai)
        return audio, "wav"

    def prefetch(self, key, text, khuech_dai: float = 1.0):
        if key in self._cache or not text:
            return
        self._cache[key] = self._pool.submit(self._synth_blocking, text, khuech_dai)

    # Kho âm thanh đã tổng hợp, tra theo NỘI DUNG. Xem giải thích ở get_audio.
    # 250 MB ≈ 43 phút tiếng — thừa sức chứa vài chục tài liệu thường gặp, mà
    # vẫn nhỏ so với RAM máy phổ thông.
    KHO_TOI_DA_BYTE = 250 * 1024 * 1024

    def _khoa_kho(self, text: str, khuech_dai: float):
        return (self.cfg.get("vieneu_voice_id", ""), round(khuech_dai, 3), text)

    def get_audio(self, key, text, khuech_dai: float = 1.0):
        """Trả về (bytes, dinh_dang).

        BA TẦNG, tra từ rẻ tới đắt:

          1. KHO theo nội dung — cùng một câu, cùng giọng, cùng khuếch đại thì
             lấy lại bản cũ, mất vài mili giây.
          2. Hàng đợi nạp trước (_cache) — mẩu đã hẹn tổng hợp sẵn.
          3. Tổng hợp thật — chậm nhất, khoảng 4 lần thời lượng tiếng.

        Vì sao cần tầng 1: trước đây `_cache.pop()` LẤY RA RỒI XOÁ, nên nó chỉ
        là hàng đợi nạp trước chứ không phải kho. Nghe lại một đoạn vừa nghe,
        hay bấm Xuất sau khi đã nghe cả bài, đều tổng hợp lại từ đầu - chủ dự
        án bấm thử và nhận xét "đoạn dài quay quay lâu mới đọc" cùng "thời
        gian xuất lâu". Cả hai là một gốc.

        Kho tra theo NỘI DUNG chứ không theo số thứ tự đoạn: sửa một dòng giữa
        bài thì các đoạn còn lại vẫn dùng lại được, chỉ dòng vừa sửa phải tổng
        hợp mới. Đây cũng là thứ khiến nguồn động sau này dùng được - dữ liệu
        đổi vài dòng thì chỉ đọc lại vài dòng.
        """
        kho_key = self._khoa_kho(text, khuech_dai)
        with self._khoa_kho_lock:
            san = self._kho.get(kho_key)
            if san is not None:
                self._kho.move_to_end(kho_key)
                return san

        fut = self._cache.pop(key, None)
        kq = None
        if fut is not None:
            try:
                kq = fut.result()
            except Exception:
                kq = None
        if kq is None:
            kq = self._synth_blocking(text, khuech_dai)

        audio = kq[0] if isinstance(kq, tuple) else None
        if audio:
            with self._khoa_kho_lock:
                self._kho[kho_key] = kq
                self._kho_byte += len(audio)
                # Đầy thì bỏ mẩu lâu không đụng tới nhất.
                while self._kho_byte > self.KHO_TOI_DA_BYTE and len(self._kho) > 1:
                    _, cu = self._kho.popitem(last=False)
                    self._kho_byte -= len(cu[0]) if cu and cu[0] else 0
        return kq

    def clear_cache(self):
        """Xoá HÀNG ĐỢI nạp trước, GIỮ NGUYÊN kho theo nội dung.

        Đổi playlist thì mấy lượt nạp trước đã hẹn thành vô nghĩa, nhưng tiếng
        đã tổng hợp xong thì vẫn đúng - nội dung nào ra tiếng nấy. Xoá luôn kho
        là vứt đi đúng thứ vừa tốn hàng phút để có.
        """
        self._cache.clear()

    def xoa_kho(self):
        """Dọn sạch kho âm thanh. Chỉ dùng khi đổi giọng hoặc cần lấy lại RAM."""
        with self._khoa_kho_lock:
            self._kho.clear()
            self._kho_byte = 0

    def play(self, audio: bytes, stop_event: threading.Event,
             dinh_dang: str = "wav", loc: str = "") -> bool:
        """`loc` là chuỗi -af của ffplay, để hồ sơ chỉnh Tốc độ/Cao độ/Âm lượng.

        Mặc định RỖNG và khi rỗng thì lệnh dựng ra giống hệt bản trước từng
        chữ - bản cũ và mọi nơi gọi cũ không đổi hành vi một li nào. VieNeu
        không có ba tham số ấy, nhưng ffplay đi kèm chương trình làm được:
        xem giaodien_moi/am_thanh_loc.py, có số đo thật.
        """
        if not audio:
            return True

        # Giành loa trước khi kêu. Ai đang giữ thì bị tắt tiếng ngay.
        nguon_cu = self._gianh_loa()
        if nguon_cu is not None:
            nguon_cu.stop()

        startupinfo, creationflags = None, 0
        if os.name == "nt":
            startupinfo = subprocess.STARTUPINFO()
            startupinfo.dwFlags |= subprocess.STARTF_USESHOWWINDOW
            startupinfo.wShowWindow = 0
            creationflags = subprocess.CREATE_NO_WINDOW

        ff_fmt = "wav" if dinh_dang == "wav" else "mp3"  # dự phòng, luôn là wav
        lenh = [str(self.cfg["ffplay"]), "-hide_banner", "-loglevel", "error",
                "-nodisp", "-autoexit", "-vn", "-f", ff_fmt, "-i", "pipe:0"]
        if loc:
            lenh += ["-af", loc]
        proc = subprocess.Popen(
            lenh,
            stdin=subprocess.PIPE, stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
            startupinfo=startupinfo, creationflags=creationflags)
        with self._lock:
            self.player = proc

        # Dựng tiến trình ffplay mất vài chục mili giây; trong khoảng đó nguồn
        # khác có thể đã giành mất loa, mà lúc nó gọi stop() thì self.player
        # còn None nên chẳng giết được gì - tiến trình vừa sinh sẽ kêu chồng
        # lên. Kiểm lại quyền một lần nữa rồi mới cho phát.
        if not self._con_giu_loa():
            self.stop()
            return False

        threading.Thread(target=self._feed, args=(proc, audio), daemon=True).start()
        try:
            while proc.poll() is None:
                if stop_event.is_set():
                    self.stop()
                    self._nha_loa()   # tự dừng thì trả loa lại, đừng ôm khư khư
                    return False
                time.sleep(0.05)
        finally:
            with self._lock:
                if self.player is proc:
                    self.player = None

        # Trả về theo "tôi còn giữ loa không", KHÔNG theo cờ dừng. Bị nguồn
        # khác giành thì ffplay của mình bị giết mà cờ dừng của mình vẫn sạch;
        # cứ nhìn cờ dừng thì vòng đọc tưởng câu này phát xong êm đẹp rồi
        # chuyển sang câu kế - chồng tiếng trở lại đúng thứ vừa đi vá.
        con_quyen = self._con_giu_loa()
        self._nha_loa()
        return con_quyen and not stop_event.is_set()

    @staticmethod
    def _feed(proc, audio):
        try:
            proc.stdin.write(audio)
            proc.stdin.flush()
        except (BrokenPipeError, OSError, ValueError):
            pass
        finally:
            try:
                proc.stdin.close()
            except Exception:
                pass

    def stop(self):
        with self._lock:
            proc, self.player = self.player, None
        if proc:
            try:
                proc.kill()
            except Exception:
                pass

    def shutdown(self):
        self.stop()
        # Nhả cả loa: nếu luồng phát thoát bằng ngoại lệ thì nó không kịp nhả,
        # để treo tham chiếu ở đó thì nguồn sau vẫn giành được nhưng object này
        # không bao giờ được thu hồi.
        self._nha_loa()
        self.clear_cache()
        try:
            self._pool.shutdown(wait=False)
        except Exception:
            pass


# ---------------------------------------------------------------------------
# TIỆN ÍCH GIAO DIỆN
# ---------------------------------------------------------------------------

def nut_lon(parent, text, command, mau):
    """Nút hành động chính - dùng tk.Button để tô được màu trên mọi Windows."""
    return tk.Button(parent, text=text, command=command, bg=mau, fg="white",
                     activebackground=mau, activeforeground="white",
                     font=("Segoe UI", 11, "bold"), relief="flat", bd=0,
                     padx=10, pady=9, cursor="hand2",
                     disabledforeground="#eeeeee")


def dat_trang_thai_nut(btn, bat, mau):
    btn.configure(state=("normal" if bat else "disabled"),
                  bg=(mau if bat else MAU_MO),
                  activebackground=(mau if bat else MAU_MO),
                  cursor=("hand2" if bat else ""))


class SuaFileDialog(tk.Toplevel):
    """Cửa sổ sửa nhanh một file .ini bằng chữ (dùng cho tudien.ini)."""

    def __init__(self, master, path: Path, tieu_de, mac_dinh_fn, on_saved):
        super().__init__(master)
        self.title(tieu_de)
        self.geometry("760x600")
        self.transient(master)
        self.path = path
        self.mac_dinh_fn = mac_dinh_fn
        self.on_saved = on_saved

        ttk.Label(self, text=str(path), foreground=MAU_PHU).pack(
            anchor="w", padx=12, pady=(10, 4))
        khung = ttk.Frame(self)
        khung.pack(fill="both", expand=True, padx=12)
        self.box = tk.Text(khung, wrap="none", font=("Consolas", 11), undo=True)
        self.box.pack(side="left", fill="both", expand=True)
        sb = ttk.Scrollbar(khung, command=self.box.yview)
        sb.pack(side="right", fill="y")
        self.box.configure(yscrollcommand=sb.set)
        try:
            self.box.insert("1.0", path.read_text(encoding="utf-8-sig"))
        except OSError:
            self.box.insert("1.0", mac_dinh_fn())

        bar = ttk.Frame(self, padding=12)
        bar.pack(fill="x")
        ttk.Button(bar, text="💾 Lưu và đóng", command=self.luu).pack(side="right",
                                                                     padx=4)
        ttk.Button(bar, text="Đóng", command=self.destroy).pack(side="right", padx=4)
        ttk.Button(bar, text="↺ Khôi phục mặc định",
                   command=self.mac_dinh).pack(side="left", padx=4)
        self.grab_set()

    def mac_dinh(self):
        if messagebox.askyesno("Khôi phục", "Đưa file về nội dung mặc định?",
                               parent=self):
            self.box.delete("1.0", "end")
            self.box.insert("1.0", self.mac_dinh_fn())

    def luu(self):
        try:
            self.path.write_text(self.box.get("1.0", "end-1c"), encoding="utf-8-sig")
        except OSError as e:
            messagebox.showerror("Lỗi", f"Không lưu được:\n{e}", parent=self)
            return
        self.on_saved()
        self.destroy()


class NoiDungDialog(tk.Toplevel):
    def __init__(self, master, noidung: NoiDung, on_saved):
        super().__init__(master)
        self.title("Sửa lời dẫn - noidung.ini")
        self.geometry("820x600")
        self.minsize(700, 520)
        self.transient(master)
        self.noidung = noidung
        self.on_saved = on_saved

        nb = ttk.Notebook(self)
        nb.pack(fill="both", expand=True, padx=12, pady=12)

        self.dau_bat = tk.BooleanVar(value=noidung.dau_bat)
        self.cuoi_bat = tk.BooleanVar(value=noidung.cuoi_bat)
        self.giua_bat = tk.BooleanVar(value=noidung.giua_bat)
        self.giua_sau_moi = tk.IntVar(value=noidung.giua_sau_moi)

        self.txt_dau = self._tab(nb, "1. Lời mở đầu", self.dau_bat,
                                 "Đọc lời mở đầu", noidung.dau_text)
        self.txt_giua = self._tab(nb, "2. Lời giữa danh sách", self.giua_bat,
                                  "Đọc lời tri ân xen giữa", noidung.giua_text, True)
        self.txt_cuoi = self._tab(nb, "3. Lời kết", self.cuoi_bat,
                                  "Đọc lời kết", noidung.cuoi_text)

        frame = ttk.Frame(nb, padding=14)
        nb.add(frame, text="4. Mẫu câu đọc")
        ttk.Label(frame, wraplength=700,
                  text="Mẫu câu đọc cho từng người. Bắt buộc có {ten} và {tien}."
                  ).pack(anchor="w", pady=(0, 8))
        self.mau_cau = tk.StringVar(value=noidung.mau_cau)
        ttk.Entry(frame, textvariable=self.mau_cau, font=("Segoe UI", 11)).pack(fill="x")
        ttk.Label(frame, justify="left", foreground=MAU_PHU, text=(
            "\nVí dụ:\n"
            "   {ten}, phát tâm công đức số tiền {tien}.\n"
            "   Xin ghi nhận công đức của {ten}, số tiền {tien}.")
                  ).pack(anchor="w", pady=10)

        bar = ttk.Frame(self, padding=(12, 0, 12, 12))
        bar.pack(fill="x")
        ttk.Button(bar, text="💾 Lưu và đóng", command=self.save_close).pack(
            side="right", padx=4)
        ttk.Button(bar, text="Lưu", command=self.save).pack(side="right", padx=4)
        ttk.Button(bar, text="Đóng", command=self.destroy).pack(side="right", padx=4)
        ttk.Button(bar, text="↺ Khôi phục mặc định",
                   command=self.restore_default).pack(side="left", padx=4)
        self.grab_set()

    def _tab(self, nb, title, var_bat, label_bat, text, sau_moi=False):
        frame = ttk.Frame(nb, padding=14)
        nb.add(frame, text=title)
        top = ttk.Frame(frame)
        top.pack(fill="x", pady=(0, 8))
        ttk.Checkbutton(top, text=label_bat, variable=var_bat).pack(side="left")
        if sau_moi:
            ttk.Label(top, text="   Cứ sau mỗi").pack(side="left")
            ttk.Spinbox(top, from_=5, to=500, increment=5, width=6,
                        textvariable=self.giua_sau_moi).pack(side="left", padx=6)
            ttk.Label(top, text="người").pack(side="left")
        box = tk.Text(frame, wrap="word", font=("Segoe UI", 11), undo=True, height=16)
        box.pack(fill="both", expand=True)
        box.insert("1.0", text)
        return box

    def _collect(self):
        self.noidung.dau_bat = self.dau_bat.get()
        self.noidung.dau_text = self.txt_dau.get("1.0", "end").strip()
        self.noidung.giua_bat = self.giua_bat.get()
        try:
            self.noidung.giua_sau_moi = max(1, int(self.giua_sau_moi.get()))
        except (tk.TclError, ValueError):
            self.noidung.giua_sau_moi = 30
        self.noidung.giua_text = self.txt_giua.get("1.0", "end").strip()
        self.noidung.cuoi_bat = self.cuoi_bat.get()
        self.noidung.cuoi_text = self.txt_cuoi.get("1.0", "end").strip()
        mau = self.mau_cau.get().strip()
        if "{ten}" in mau and "{tien}" in mau:
            self.noidung.mau_cau = mau
        else:
            messagebox.showwarning("Mẫu câu chưa đúng",
                                   "Mẫu câu phải có cả {ten} và {tien}.\n"
                                   "Chương trình giữ lại mẫu câu cũ.", parent=self)

    def save(self):
        self._collect()
        try:
            self.noidung.save(NOIDUNG_FILE)
        except OSError as e:
            messagebox.showerror("Lỗi", f"Không lưu được noidung.ini:\n{e}", parent=self)
            return False
        self.on_saved()
        return True

    def save_close(self):
        if self.save():
            self.destroy()

    def restore_default(self):
        if not messagebox.askyesno("Khôi phục", "Khôi phục toàn bộ lời dẫn về mặc định?",
                                   parent=self):
            return
        for box, mac_dinh in ((self.txt_dau, LOI_DAU_MAC_DINH),
                              (self.txt_giua, LOI_GIUA_MAC_DINH),
                              (self.txt_cuoi, LOI_CUOI_MAC_DINH)):
            box.delete("1.0", "end")
            box.insert("1.0", mac_dinh)
        self.mau_cau.set(MAU_CAU_MAC_DINH)
        self.dau_bat.set(True)
        self.cuoi_bat.set(True)
        self.giua_bat.set(False)
        self.giua_sau_moi.set(30)


class TaiGiongVieNeuDialog(tk.Toplevel):
    """Tải danh sách giọng dựng sẵn của VieNeu-TTS (chạy tại máy). Lần đầu
    có thể kèm tải mô hình từ Hugging Face (vài trăm MB), các lần sau chỉ
    đọc từ bộ nhớ đã nạp, rất nhanh."""

    def __init__(self, master, app, khi_xong):
        super().__init__(master)
        self.title("Tải giọng VieNeu-TTS")
        self.geometry("480x200")
        self.resizable(False, False)
        self.transient(master)
        self.app = app
        self.khi_xong = khi_xong
        self._da_goi_ket_qua = False

        ttk.Label(
            self, text="Chuẩn bị VieNeu-TTS (chạy tại máy, CPU)",
            font=("Segoe UI", 10, "bold")
        ).pack(padx=16, pady=(16, 4), anchor="w")
        self.trangthai = tk.StringVar(value=(
            "Lần đầu có thể tải mô hình từ Hugging Face (vài trăm MB, "
            "cần Internet một lần). Các lần sau đọc offline hoàn toàn."))
        ttk.Label(self, textvariable=self.trangthai, wraplength=440,
                  justify="left").pack(padx=16, fill="x")
        self.pb = ttk.Progressbar(self, mode="indeterminate")
        self.pb.pack(padx=16, pady=14, fill="x")
        self.pb.start(12)

        bar = ttk.Frame(self, padding=(16, 0, 16, 16))
        bar.pack(fill="x", side="bottom")
        ttk.Button(bar, text="Huỷ", command=self._huy).pack(side="right", padx=4)

        self.protocol("WM_DELETE_WINDOW", self._huy)
        self.grab_set()
        threading.Thread(target=self._chay, daemon=True).start()

    def _chay(self):
        try:
            ds = lay_danh_sach_giong_day_du(bao_tien_do=self._bao)
            self._ket_qua(ds, None)
        except Exception as e:
            self._ket_qua(None, str(e))

    def _bao(self, msg):
        try:
            self.after(0, self.trangthai.set, msg)
        except (RuntimeError, tk.TclError):
            pass

    def _ket_qua(self, ds, loi):
        def cap_nhat():
            if self._da_goi_ket_qua:
                return
            self._da_goi_ket_qua = True
            self.pb.stop()
            if loi:
                messagebox.showerror(
                    "Không tải được giọng VieNeu-TTS",
                    f"{loi}\n\n(Nếu đã cài đặt đầy đủ, có thể do mất "
                    "Internet lúc tải mô hình lần đầu.)",
                    parent=self.app.root)
                self.destroy()
                self.khi_xong(False)
                return
            self.app.vieneu_giong = ds
            self.destroy()
            self.khi_xong(True)
        try:
            self.after(0, cap_nhat)
        except (RuntimeError, tk.TclError):
            pass

    def _huy(self):
        # Không huỷ được luồng nạp mô hình đang chạy nền (thư viện không
        # hỗ trợ huỷ giữa chừng) - chỉ đóng cửa sổ và không đổi nguồn giọng.
        if not self._da_goi_ket_qua:
            self._da_goi_ket_qua = True
            self.destroy()
            self.khi_xong(False)


class TaoGiongRiengDialog(tk.Toplevel):
    """Tạo giọng riêng mới từ file mẫu do người dùng cung cấp. Giọng tạo
    xong được lưu lại (giong_rieng\\), dùng chọn lại được nhiều lần như
    giọng dựng sẵn, luôn đánh dấu 🎙️ ... (giọng riêng) để phân biệt."""

    def __init__(self, master, app, khi_xong):
        super().__init__(master)
        self.title("Tạo giọng riêng từ file mẫu")
        self.geometry("520x360")
        self.resizable(False, False)
        self.transient(master)
        self.app = app
        self.khi_xong = khi_xong
        self._duong_dan_mau = None
        self._dang_chay = False

        canh_bao = (
            "⚠ Chỉ dùng giọng của chính anh, hoặc của người khác khi đã "
            "được họ đồng ý.\n"
            "⚠ Máy không có card đồ hoạ: tính năng này có thể không chạy "
            "được (VieNeu-TTS bản mặc định yêu cầu GPU cho việc nhân bản "
            "giọng) - chương trình sẽ báo lỗi rõ nếu vậy, không giả vờ "
            "chắc chắn thành công."
        )
        tk.Label(self, text=canh_bao, wraplength=480, justify="left",
                 bg="#fff3cd", fg="#664d03", padx=10, pady=8).pack(
            fill="x", padx=12, pady=(12, 10))

        khung_file = ttk.Frame(self)
        khung_file.pack(fill="x", padx=12)
        ttk.Label(khung_file, text="File mẫu giọng nói (3-5 giây, .wav/.mp3, "
                                   "rõ tiếng, ít tạp âm):").pack(anchor="w")
        hang_file = ttk.Frame(khung_file)
        hang_file.pack(fill="x", pady=(4, 10))
        self.nhan_file = ttk.Label(hang_file, text="(chưa chọn file)",
                                   foreground=MAU_PHU)
        self.nhan_file.pack(side="left", fill="x", expand=True)
        ttk.Button(hang_file, text="📂 Chọn file…",
                   command=self._chon_file).pack(side="right")

        ttk.Label(self, text="Tên đặt cho giọng này (vd: Giọng của tôi, "
                             "Giọng bác Tuấn):").pack(anchor="w", padx=12)
        self.ten_var = tk.StringVar()
        ttk.Entry(self, textvariable=self.ten_var).pack(
            fill="x", padx=12, pady=(4, 12))

        self.trangthai = tk.StringVar(value="Sẵn sàng.")
        ttk.Label(self, textvariable=self.trangthai, wraplength=480,
                  justify="left").pack(fill="x", padx=12)
        self.pb = ttk.Progressbar(self, mode="indeterminate")
        self.pb.pack(fill="x", padx=12, pady=(8, 0))

        bar = ttk.Frame(self, padding=12)
        bar.pack(fill="x", side="bottom")
        self.btn_tao = ttk.Button(bar, text="🎙️ Tạo giọng", command=self._tao)
        self.btn_tao.pack(side="right", padx=4)
        ttk.Button(bar, text="Đóng", command=self.destroy).pack(side="right", padx=4)
        self.grab_set()

    def _chon_file(self):
        path = filedialog.askopenfilename(
            title="Chọn file mẫu giọng nói", parent=self,
            filetypes=[("Âm thanh", "*.wav *.mp3 *.flac *.m4a"),
                      ("Tất cả file", "*.*")])
        if not path:
            return
        self._duong_dan_mau = Path(path)
        self.nhan_file.configure(text=self._duong_dan_mau.name,
                                 foreground="black")

    def _tao(self):
        if self._dang_chay:
            return
        ten = self.ten_var.get().strip()
        if not ten:
            self.trangthai.set("⚠ Chưa đặt tên cho giọng.")
            return
        if not self._duong_dan_mau:
            self.trangthai.set("⚠ Chưa chọn file mẫu.")
            return

        self._dang_chay = True
        self.btn_tao.configure(state="disabled")
        self.pb.start(12)
        duong_dan = self._duong_dan_mau

        def chay():
            try:
                muc = tao_giong_rieng(ten, duong_dan, bao_tien_do=self._bao)
                self._ket_qua(muc, None)
            except Exception as e:
                self._ket_qua(None, str(e))

        threading.Thread(target=chay, daemon=True).start()

    def _bao(self, msg):
        try:
            self.after(0, self.trangthai.set, msg)
        except (RuntimeError, tk.TclError):
            pass

    def _ket_qua(self, muc, loi):
        def cap_nhat():
            self._dang_chay = False
            self.pb.stop()
            self.btn_tao.configure(state="normal")
            if loi:
                self.trangthai.set("⚠ Không tạo được giọng.")
                messagebox.showerror("Không tạo được giọng riêng", loi,
                                     parent=self)
                return
            self.trangthai.set(f"✅ Đã tạo xong: {muc['ten']}")
            self.khi_xong(muc)
            self.after(1200, self.destroy)
        try:
            self.after(0, cap_nhat)
        except (RuntimeError, tk.TclError):
            pass


class QuanLyGiongRiengDialog(tk.Toplevel):
    """Xem và xoá các giọng riêng đã tạo."""

    def __init__(self, master, app, khi_doi):
        super().__init__(master)
        self.title("Quản lý giọng riêng")
        self.geometry("460x360")
        self.transient(master)
        self.app = app
        self.khi_doi = khi_doi

        ttk.Label(self, text="Các giọng riêng đã tạo",
                  font=("Segoe UI", 10, "bold")).pack(
            anchor="w", padx=12, pady=(12, 6))

        khung = ttk.Frame(self)
        khung.pack(fill="both", expand=True, padx=12)
        self.ds_box = tk.Listbox(khung, font=("Segoe UI", 10))
        self.ds_box.pack(side="left", fill="both", expand=True)
        sb = ttk.Scrollbar(khung, command=self.ds_box.yview)
        sb.pack(side="right", fill="y")
        self.ds_box.configure(yscrollcommand=sb.set)

        self._nap_lai()

        bar = ttk.Frame(self, padding=12)
        bar.pack(fill="x", side="bottom")
        ttk.Button(bar, text="🗑️ Xoá giọng đã chọn",
                   command=self._xoa).pack(side="right", padx=4)
        ttk.Button(bar, text="Đóng", command=self.destroy).pack(side="right", padx=4)
        self.grab_set()

    def _nap_lai(self):
        self._ds = doc_ds_giong_rieng()
        self.ds_box.delete(0, "end")
        if not self._ds:
            self.ds_box.insert("end", "(chưa có giọng riêng nào)")
            return
        for g in self._ds:
            self.ds_box.insert("end", f'{g["ten"]}   -   tạo ngày {g["ngay_tao"]}')

    def _xoa(self):
        sel = self.ds_box.curselection()
        if not sel or not self._ds or sel[0] >= len(self._ds):
            return
        muc = self._ds[sel[0]]
        if not messagebox.askyesno(
                "Xoá giọng riêng",
                f'Xoá hẳn giọng "{muc["ten"]}"? Không thể hoàn tác.',
                parent=self):
            return
        xoa_giong_rieng(muc["id"])
        self._nap_lai()
        self.khi_doi()


class TaiFFmpegDialog(tk.Toplevel):
    """Cửa sổ tải ffplay.exe tự động từ GitHub khi chương trình thiếu nó."""

    def __init__(self, master, bin_dir: Path, on_done=None):
        super().__init__(master)
        self.title("Tải FFmpeg")
        self.geometry("480x200")
        self.resizable(False, False)
        self.transient(master)
        self.bin_dir = bin_dir
        self.on_done = on_done
        self._dang_tai = False

        ttk.Label(self, text="Chương trình cần ffplay.exe để phát âm thanh.",
                  font=("Segoe UI", 10, "bold")).pack(
            padx=16, pady=(16, 4), anchor="w")

        self.trangthai = tk.StringVar(value=(
            "Bấm Tải ngay để tự động tải bản FFmpeg mới nhất từ GitHub "
            "(BtbN/FFmpeg-Builds). Không cần cài đặt thủ công, không cần "
            "vào trang web nào cả."
        ))
        ttk.Label(self, textvariable=self.trangthai, wraplength=440,
                  justify="left").pack(padx=16, fill="x")

        self.pb = ttk.Progressbar(self, mode="indeterminate")
        self.pb.pack(padx=16, pady=14, fill="x")

        bar = ttk.Frame(self, padding=(16, 0, 16, 16))
        bar.pack(fill="x")
        self.btn_tai = ttk.Button(bar, text="⬇ Tải ngay", command=self.bat_dau)
        self.btn_tai.pack(side="right", padx=4)
        ttk.Button(bar, text="Đóng", command=self.destroy).pack(side="right", padx=4)
        self.grab_set()

    def bat_dau(self):
        if self._dang_tai:
            return
        self._dang_tai = True
        self.btn_tai.configure(state="disabled")
        self.pb.start(12)

        def chay():
            try:
                dest = tai_ffmpeg_tu_dong(self.bin_dir, self._bao)
                self._ket_qua(dest, None)
            except Exception as e:
                self._ket_qua(None, str(e))

        threading.Thread(target=chay, daemon=True).start()

    def _bao(self, msg):
        try:
            self.after(0, self.trangthai.set, msg)
        except (RuntimeError, tk.TclError):
            pass

    def _ket_qua(self, dest, loi):
        def cap_nhat():
            self._dang_tai = False
            self.pb.stop()
            self.btn_tai.configure(state="normal")
            if loi:
                self.trangthai.set(f"⚠ Tải thất bại: {loi}")
                return
            self.trangthai.set(f"✅ Đã tải xong: {dest}")
            if self.on_done:
                self.on_done()
            self.after(1200, self.destroy)
        try:
            self.after(0, cap_nhat)
        except (RuntimeError, tk.TclError):
            pass


class CaiDatDialog(tk.Toplevel):
    def __init__(self, master, cfg, on_saved):
        super().__init__(master)
        self.title("Cài đặt chi tiết")
        self.geometry("520x480")
        self.resizable(False, False)
        self.transient(master)
        self.cfg = cfg
        self.on_saved = on_saved

        frame = ttk.Frame(self, padding=18)
        frame.pack(fill="both", expand=True)

        self.nghi_nguoi = tk.StringVar(value=f'{cfg["nghi_nguoi"]:.2f}')
        self.nghi_nhom = tk.StringVar(value=f'{cfg["nghi_nhom"]:.2f}')
        self.so_nguoi = tk.StringVar(value=str(cfg["so_nguoi_nhom"]))
        self.nghi_doan = tk.StringVar(value=f'{cfg["nghi_doan"]:.2f}')
        self.nghi_cau = tk.StringVar(value=f'{cfg["nghi_cau"]:.2f}')
        self.nghi_doan_vb = tk.StringVar(value=f'{cfg["nghi_doan_vb"]:.2f}')
        self.so_ky_tu = tk.StringVar(value=str(cfg["so_ky_tu"]))
        self.doc_so = tk.BooleanVar(value=cfg["doc_so_bang_chu"])
        self.bo_md = tk.BooleanVar(value=cfg["bo_markdown"])

        r = 0

        def tieu_de(text):
            nonlocal r
            ttk.Label(frame, text=text, font=("Segoe UI", 10, "bold")).grid(
                row=r, column=0, columnspan=2, sticky="w", pady=(10, 6))
            r += 1

        def dong(label, var, values=None):
            nonlocal r
            ttk.Label(frame, text=label).grid(row=r, column=0, sticky="w", pady=5)
            if values:
                ttk.Combobox(frame, textvariable=var, values=values, width=20).grid(
                    row=r, column=1, sticky="ew")
            else:
                ttk.Entry(frame, textvariable=var, width=22).grid(
                    row=r, column=1, sticky="ew")
            r += 1

        tieu_de("CHẾ ĐỘ DANH SÁCH CÔNG ĐỨC")
        dong("Nghỉ giữa từng người (giây)", self.nghi_nguoi)
        dong("Nghỉ giữa từng nhóm (giây)", self.nghi_nhom)
        dong("Số người mỗi nhóm", self.so_nguoi)
        dong("Nghỉ giữa các đoạn lời dẫn (giây)", self.nghi_doan)

        tieu_de("CHẾ ĐỘ ĐỌC VĂN BẢN")
        dong("Nghỉ giữa câu (giây)", self.nghi_cau)
        dong("Nghỉ giữa đoạn (giây)", self.nghi_doan_vb)
        dong("Số ký tự mỗi lần đọc (200-600)", self.so_ky_tu)
        ttk.Checkbutton(frame, text="Đọc số lớn thành chữ (1.600.000 → một triệu…)",
                        variable=self.doc_so).grid(row=r, column=0, columnspan=2,
                                                   sticky="w", pady=3)
        r += 1
        ttk.Checkbutton(frame, text="Bỏ qua ký hiệu #, *, |, gạch đầu dòng",
                        variable=self.bo_md).grid(row=r, column=0, columnspan=2,
                                                  sticky="w", pady=3)
        r += 1

        frame.columnconfigure(1, weight=1)
        bar = ttk.Frame(frame)
        bar.grid(row=r, column=0, columnspan=2, sticky="e", pady=(18, 0))
        ttk.Button(bar, text="💾 Lưu", command=self.save).pack(side="right", padx=4)
        ttk.Button(bar, text="Đóng", command=self.destroy).pack(side="right", padx=4)
        self.grab_set()

    def save(self):
        def f(var, default):
            try:
                return max(0.0, float(str(var.get()).replace(",", ".")))
            except ValueError:
                return default

        self.cfg["nghi_nguoi"] = f(self.nghi_nguoi, 1.3)
        self.cfg["nghi_nhom"] = f(self.nghi_nhom, 2.5)
        self.cfg["nghi_doan"] = f(self.nghi_doan, 0.8)
        self.cfg["nghi_cau"] = f(self.nghi_cau, 0.25)
        self.cfg["nghi_doan_vb"] = f(self.nghi_doan_vb, 0.7)
        self.cfg["doc_so_bang_chu"] = bool(self.doc_so.get())
        self.cfg["bo_markdown"] = bool(self.bo_md.get())
        try:
            self.cfg["so_nguoi_nhom"] = max(1, int(float(self.so_nguoi.get())))
        except ValueError:
            self.cfg["so_nguoi_nhom"] = 20
        try:
            self.cfg["so_ky_tu"] = min(900, max(80, int(float(self.so_ky_tu.get()))))
        except ValueError:
            self.cfg["so_ky_tu"] = 280

        try:
            save_config(self.cfg)
        except OSError as e:
            messagebox.showerror("Lỗi", f"Không lưu được cauhinh.ini:\n{e}", parent=self)
            return
        self.on_saved()
        self.destroy()


# ---------------------------------------------------------------------------
# PHIÊN ĐỌC - mỗi thẻ giữ vị trí riêng
# ---------------------------------------------------------------------------

class Phien:
    def __init__(self, ma):
        self.ma = ma              # "cd" hoặc "vb"
        self.playlist = []
        self.index = 0
        self.mode = "lien_tuc"    # "lien_tuc" hoặc "don_le"


# ---------------------------------------------------------------------------
# CHƯƠNG TRÌNH CHÍNH
# ---------------------------------------------------------------------------

class DocApp:
    def __init__(self, root):
        self.root = root
        self.root.title(f"{APP_TITLE}  -  v{APP_VERSION}")
        # 700px cao vừa với màn hình laptop phổ biến 1366x768 (trừ taskbar
        # và title bar). Bố cục hai thẻ ghim nút ở đáy nên vẫn luôn hiện
        # đủ nút dù kéo cửa sổ thấp hơn nữa, tới tận minsize.
        self.root.geometry("1080x700")
        self.root.minsize(860, 560)
        self.root.configure(bg=MAU_NEN)
        self.root.protocol("WM_DELETE_WINDOW", self.quit_app)

        tao_file_thieu()
        self.cfg = load_config()
        self.noidung = NoiDung().load(NOIDUNG_FILE)
        self.tudien = load_tudien(TUDIEN_FILE)
        self.vieneu_giong = []    # danh sách giọng VieNeu-TTS, tải khi cần

        self.records = []
        self.phien = {"cd": Phien("cd"), "vb": Phien("vb")}
        self.phien_chay = None
        self.stop_event = threading.Event()
        self.worker = None
        self.speaker = Speaker(self.cfg)
        self.vb_chu_ky = None      # dấu vân tay nội dung đã dựng playlist
        self.vb_goi_y = True       # đang hiện dòng gợi ý trong ô soạn thảo

        self.var = {
            "cd_file": tk.StringVar(value=str(self.cfg["data_file"])),
            "cd_tomtat": tk.StringVar(value=""),
            "cd_ten": tk.StringVar(value="—"),
            "cd_tien": tk.StringVar(value=""),
            "cd_cau": tk.StringVar(value=""),
            "cd_tiendo": tk.StringVar(value="0 / 0"),
            "cd_trangthai": tk.StringVar(value="Sẵn sàng."),
            "vb_tomtat": tk.StringVar(value=""),
            "vb_tiendo": tk.StringVar(value="0 / 0"),
            "vb_trangthai": tk.StringVar(value="Chưa có nội dung."),
            "giong": tk.StringVar(),
            "phong_cach": tk.StringVar(value=self.cfg["phong_cach"]),
            "pc_mo_ta": tk.StringVar(value=""),
        }

        self.build_menu()
        self.build_ui()
        self.gan_phim_tat()
        self.reload_data(show_errors=True)
        self.cap_nhat_nut()
        self._nap_ngam_giong_vieneu_khoi_dong()

    # ================= MENU =================
    def build_menu(self):
        menubar = tk.Menu(self.root)

        m_tep = tk.Menu(menubar, tearoff=0)
        m_tep.add_command(label="Mở file danh sách công đức…",
                          command=self.open_data_file)
        m_tep.add_command(label="Mở file văn bản (.txt)…", command=self.vb_mo_file)
        m_tep.add_separator()
        m_tep.add_command(label="Lưu giọng đọc văn bản ra WAV…", command=self.vb_luu_mp3)
        m_tep.add_separator()
        m_tep.add_command(label="Thoát", command=self.quit_app)
        menubar.add_cascade(label="Tệp", menu=m_tep)

        m_cc = tk.Menu(menubar, tearoff=0)
        m_cc.add_command(label="Sửa lời dẫn (lời mở đầu / giữa / kết)…",
                         command=self.sua_noi_dung)
        m_cc.add_command(label="Sửa từ điển cách đọc…", command=self.sua_tudien)
        m_cc.add_separator()
        m_cc.add_command(label="Xem trước lời đọc của thẻ hiện tại",
                         command=self.xem_truoc)
        m_cc.add_command(label="Cài đặt chi tiết…", command=self.cai_dat)
        m_cc.add_separator()
        m_cc.add_command(label="Tải / cập nhật FFmpeg (ffplay.exe)…",
                         command=self.hoi_tai_ffmpeg)
        menubar.add_cascade(label="Công cụ", menu=m_cc)

        m_giong = tk.Menu(menubar, tearoff=0)
        m_giong.add_command(label="Nghe thử giọng hiện tại", command=self.nghe_thu)
        m_giong.add_command(
            label="🔄 Tải / làm mới danh sách giọng VieNeu-TTS…",
            command=self.tai_lai_giong_vieneu)
        m_giong.add_separator()
        m_giong.add_command(
            label="🎙️ Tạo giọng riêng từ file mẫu…",
            command=self.tao_giong_rieng)
        m_giong.add_command(
            label="🗑️ Quản lý / xoá giọng riêng…",
            command=self.quan_ly_giong_rieng)
        menubar.add_cascade(label="Giọng đọc", menu=m_giong)

        m_tg = tk.Menu(menubar, tearoff=0)
        m_tg.add_command(label="Hướng dẫn nhanh", command=self.huong_dan)
        m_tg.add_command(label="Giới thiệu", command=self.gioi_thieu)
        menubar.add_cascade(label="Trợ giúp", menu=m_tg)

        self.root.configure(menu=menubar)

    def gan_phim_tat(self):
        self.root.bind("<F5>", lambda e: self.phim_doc())
        self.root.bind("<F6>", lambda e: self.tam_dung(self.phien_hien_tai()))
        self.root.bind("<F7>", lambda e: self.dung(self.phien_hien_tai()))
        self.root.bind("<Escape>", lambda e: self.dung(self.phien_hien_tai()))

    def phim_doc(self):
        if self.nb.index(self.nb.select()) == 0:
            self.cd_doc()
        else:
            self.vb_doc()

    def phien_hien_tai(self):
        return self.phien["cd" if self.nb.index(self.nb.select()) == 0 else "vb"]

    # ================= GIAO DIỆN =================
    def build_ui(self):
        style = ttk.Style()
        for theme in ("vista", "clam", "default"):
            try:
                style.theme_use(theme)
                break
            except tk.TclError:
                continue
        style.configure("TFrame", background=MAU_NEN)
        style.configure("TLabel", background=MAU_NEN)
        style.configure("TLabelframe", background=MAU_NEN)
        style.configure("TLabelframe.Label", background=MAU_NEN)
        style.configure("TCheckbutton", background=MAU_NEN)
        style.configure("Phu.TLabel", foreground=MAU_PHU, font=("Segoe UI", 9))
        style.configure("Nho.TButton", font=("Segoe UI", 9), padding=5)
        style.configure("TNotebook.Tab", font=("Segoe UI", 11, "bold"), padding=(18, 8))

        outer = ttk.Frame(self.root, padding=(14, 10, 14, 12))
        outer.pack(fill="both", expand=True)

        ttk.Label(outer, text=APP_TITLE, font=("Segoe UI", 17, "bold"),
                  anchor="center").pack(fill="x")

        self.build_thanh_giong(outer)

        self.nb = ttk.Notebook(outer)
        self.nb.pack(fill="both", expand=True, pady=(10, 0))
        self.tab_cd = ttk.Frame(self.nb, padding=12)
        self.tab_vb = ttk.Frame(self.nb, padding=12)
        self.nb.add(self.tab_cd, text="📜  Danh sách công đức")
        self.nb.add(self.tab_vb, text="📖  Đọc văn bản")

        self.build_tab_congduc(self.tab_cd)
        self.build_tab_vanban(self.tab_vb)

        self.foot = tk.StringVar()
        ttk.Label(outer, textvariable=self.foot, anchor="center",
                  style="Phu.TLabel").pack(fill="x", pady=(8, 0))
        self.update_foot()

    def build_thanh_giong(self, parent):
        hang1 = ttk.Frame(parent, padding=(0, 8, 0, 0))
        hang1.pack(fill="x")

        ttk.Label(hang1, text="Giọng").pack(side="left")
        self.cbo_giong = ttk.Combobox(hang1, textvariable=self.var["giong"],
                                      state="readonly", width=44)
        self.cbo_giong.pack(side="left", padx=(6, 16))
        self.cbo_giong.bind("<<ComboboxSelected>>", self.on_doi_giong)
        self.cap_nhat_combo_giong()

        ttk.Label(hang1, text="Phong cách").pack(side="left")
        self.cbo_phong_cach = ttk.Combobox(
            hang1, textvariable=self.var["phong_cach"], state="readonly",
            width=20, values=list(PHONG_CACH.keys()))
        self.cbo_phong_cach.pack(side="left", padx=(6, 16))
        self.cbo_phong_cach.bind("<<ComboboxSelected>>", self.on_doi_phong_cach)

        ttk.Button(hang1, text="🔈 Nghe thử", style="Nho.TButton",
                   command=self.nghe_thu).pack(side="left")

        ttk.Label(parent, textvariable=self.var["pc_mo_ta"],
                  style="Phu.TLabel").pack(fill="x", pady=(4, 0))
        self.cap_nhat_mo_ta_pc()

    def cap_nhat_combo_giong(self):
        """Nạp danh sách giọng VieNeu-TTS thật vào ô Giọng."""
        if not self.vieneu_giong:
            cho = "(đang tải danh sách giọng...)"
            self.cbo_giong["values"] = [cho]
            self.var["giong"].set(cho)
            return
        ten_list = [g["ten"] for g in self.vieneu_giong]
        hien = next((g["ten"] for g in self.vieneu_giong
                    if g["id"] == self.cfg.get("vieneu_voice_id")), None)
        if hien is None:
            hien = ten_list[0]
            self.cfg["vieneu_voice_id"] = self.vieneu_giong[0]["id"]
        self.cbo_giong["values"] = ten_list
        self.var["giong"].set(hien)

    # ---------- khung điều khiển dùng chung cho 2 thẻ ----------
    def build_dieu_khien(self, parent, ma, phu_nut):
        """Tạo hàng nút ĐỌC / TẠM DỪNG / DỪNG riêng cho một thẻ.

        LUÔN ghim ở ĐÁY và được gọi TRƯỚC khi khung nội dung chính (bảng
        hoặc ô soạn thảo) được pack — nhờ vậy hàng nút luôn có chỗ và
        luôn nhìn thấy được, kể cả trên màn hình thấp (ví dụ laptop
        1366x768). Khung nội dung chính pack sau, fill=both, expand=True,
        tự co giãn theo phần còn lại và có thanh cuộn riêng.
        """
        khung = ttk.Frame(parent)
        khung.pack(side="bottom", fill="x", pady=(10, 0))

        chinh = ttk.Frame(khung)
        chinh.pack(fill="x")

        btn_doc = nut_lon(chinh, "▶  ĐỌC LIÊN TỤC",
                          self.cd_doc if ma == "cd" else self.vb_doc, MAU_CHINH)
        btn_doc.pack(side="left", fill="x", expand=True, padx=(0, 6))
        btn_tam = nut_lon(chinh, "⏸  TẠM DỪNG",
                          lambda: self.tam_dung(self.phien[ma]), MAU_TAM_DUNG)
        btn_tam.pack(side="left", fill="x", expand=True, padx=6)
        btn_dung = nut_lon(chinh, "⏹  DỪNG",
                           lambda: self.dung(self.phien[ma]), MAU_DUNG)
        btn_dung.pack(side="left", fill="x", expand=True, padx=(6, 0))

        setattr(self, f"btn_doc_{ma}", btn_doc)
        setattr(self, f"btn_tam_{ma}", btn_tam)
        setattr(self, f"btn_dung_{ma}", btn_dung)

        phu = ttk.Frame(khung)
        phu.pack(fill="x", pady=(8, 0))
        for text, cmd in phu_nut:
            ttk.Button(phu, text=text, style="Nho.TButton", command=cmd).pack(
                side="left", padx=(0, 6))

        ttk.Label(phu, text="F5 đọc · F6 tạm dừng · F7 dừng",
                  style="Phu.TLabel").pack(side="right")
        return khung

    # ---------- thẻ công đức ----------
    def build_tab_congduc(self, parent):
        top = ttk.Frame(parent)
        top.pack(side="top", fill="x")
        ttk.Label(top, textvariable=self.var["cd_file"],
                  style="Phu.TLabel").pack(side="left")
        ttk.Label(top, textvariable=self.var["cd_tomtat"],
                  font=("Segoe UI", 10, "bold")).pack(side="right")

        # Hàng nút dựng TRƯỚC và luôn ghim đáy (side="bottom" bên trong
        # build_dieu_khien) để chắc chắn luôn có chỗ, không bị bảng danh
        # sách chiếm hết chỗ trên màn hình thấp.
        self.build_dieu_khien(parent, "cd", [
            ("⏭ Đọc một người rồi dừng", self.cd_doc_mot_nguoi),
            ("↩ Về đầu danh sách", self.cd_ve_dau),
            ("🔄 Nạp lại danh sách", lambda: self.reload_data(True)),
            ("📂 Mở file khác", self.open_data_file),
            ("✏️ Sửa lời dẫn", self.sua_noi_dung),
        ])

        body = ttk.Frame(parent)
        body.pack(side="top", fill="both", expand=True, pady=8)
        body.columnconfigure(0, weight=3)
        body.columnconfigure(1, weight=4)
        body.rowconfigure(0, weight=1)

        left = ttk.Frame(body)
        left.grid(row=0, column=0, sticky="nsew", padx=(0, 12))
        left.rowconfigure(0, weight=1)
        left.columnconfigure(0, weight=1)

        self.tree = ttk.Treeview(left, columns=("stt", "ten", "tien"),
                                 show="headings", selectmode="browse")
        for c, t, w, a, s in (("stt", "STT", 46, "center", False),
                              ("ten", "Tên người / đơn vị", 250, "w", True),
                              ("tien", "Số tiền", 110, "e", False)):
            self.tree.heading(c, text=t)
            self.tree.column(c, width=w, anchor=a, stretch=s)
        self.tree.grid(row=0, column=0, sticky="nsew")
        self.tree.tag_configure("dangdoc", background=MAU_SANG)
        self.tree.tag_configure("tieude", foreground="#7a5c00")
        self.tree.bind("<Double-1>", self.on_tree_double)
        sb = ttk.Scrollbar(left, orient="vertical", command=self.tree.yview)
        self.tree.configure(yscrollcommand=sb.set)
        sb.grid(row=0, column=1, sticky="ns")
        ttk.Label(left, text="Nháy đúp một dòng để bắt đầu đọc từ dòng đó.",
                  style="Phu.TLabel").grid(row=1, column=0, sticky="w", pady=(4, 0))

        right = ttk.Frame(body)
        right.grid(row=0, column=1, sticky="nsew")
        the = tk.Frame(right, bg="white", highlightbackground="#dcdfe4",
                       highlightthickness=1)
        the.pack(fill="both", expand=True)
        tk.Label(the, text="ĐANG ĐỌC", bg="white", fg=MAU_PHU,
                 font=("Segoe UI", 9, "bold")).pack(anchor="w", padx=16, pady=(12, 0))
        tk.Label(the, textvariable=self.var["cd_ten"], bg="white",
                 font=("Segoe UI", 19, "bold"), wraplength=420,
                 justify="center").pack(fill="x", padx=16, pady=(8, 2))
        tk.Label(the, textvariable=self.var["cd_tien"], bg="white", fg="#a8410a",
                 font=("Segoe UI", 15)).pack(fill="x", padx=16)
        tk.Frame(the, bg="#e6e8ec", height=1).pack(fill="x", padx=16, pady=12)
        tk.Label(the, text="Câu sẽ đọc", bg="white", fg=MAU_PHU,
                 font=("Segoe UI", 9, "bold")).pack(anchor="w", padx=16)
        tk.Label(the, textvariable=self.var["cd_cau"], bg="white", fg="#2b5d2b",
                 wraplength=420, justify="left").pack(fill="x", padx=16, pady=(2, 12))
        tk.Label(the, textvariable=self.var["cd_tiendo"], bg="white",
                 font=("Segoe UI", 22, "bold")).pack(pady=(0, 4))

        self.pb_cd = ttk.Progressbar(right, mode="determinate")
        self.pb_cd.pack(fill="x", pady=(8, 4))
        ttk.Label(right, textvariable=self.var["cd_trangthai"],
                  font=("Segoe UI", 10)).pack(anchor="w")

    # ---------- thẻ văn bản ----------
    def build_tab_vanban(self, parent):
        top = ttk.Frame(parent)
        top.pack(side="top", fill="x")
        ttk.Label(top, text="Gõ, dán (Ctrl+V) hoặc mở file .txt rồi bấm ĐỌC LIÊN TỤC.",
                  style="Phu.TLabel").pack(side="left")
        ttk.Label(top, textvariable=self.var["vb_tomtat"],
                  font=("Segoe UI", 10, "bold")).pack(side="right")

        # Hàng nút dựng TRƯỚC, ghim đáy — luôn hiện dù màn hình thấp.
        self.build_dieu_khien(parent, "vb", [
            ("🖱 Đọc từ vị trí con trỏ", self.vb_doc_tu_con_tro),
            ("📂 Mở file .txt", self.vb_mo_file),
            ("📋 Dán", self.vb_dan),
            ("🧹 Xoá nội dung", self.vb_xoa),
            ("💾 Lưu WAV", self.vb_luu_mp3),
        ])

        # Hàng tiến độ cũng ghim đáy, ngay trên hàng nút — luôn hiện.
        hang = ttk.Frame(parent)
        hang.pack(side="bottom", fill="x")
        ttk.Label(hang, textvariable=self.var["vb_tiendo"],
                  font=("Segoe UI", 13, "bold")).pack(side="left")
        ttk.Label(hang, textvariable=self.var["vb_trangthai"],
                  font=("Segoe UI", 10)).pack(side="left", padx=14)
        self.pb_vb = ttk.Progressbar(parent, mode="determinate")
        self.pb_vb.pack(side="bottom", fill="x", pady=(4, 4))

        # Khung soạn thảo lấy phần còn lại — co giãn, có thanh cuộn riêng
        # nên không bao giờ đẩy các thành phần khác ra ngoài màn hình.
        khung = tk.Frame(parent, bg="white", highlightbackground="#dcdfe4",
                         highlightthickness=1)
        khung.pack(side="top", fill="both", expand=True, pady=8)
        self.vb_text = tk.Text(khung, wrap="word", font=("Segoe UI", 12), undo=True,
                               padx=14, pady=12, relief="flat", bg="white",
                               insertbackground="#333", height=6)
        self.vb_text.pack(side="left", fill="both", expand=True)
        sb = ttk.Scrollbar(khung, command=self.vb_text.yview)
        sb.pack(side="right", fill="y")
        self.vb_text.configure(yscrollcommand=sb.set)
        self.vb_text.tag_configure("dangdoc", background=MAU_SANG)
        self.vb_text.tag_configure("goiy", foreground="#9aa0a6")
        self.vb_dat_goi_y()
        self.vb_text.bind("<Key>", self.vb_xoa_goi_y)
        self.vb_text.bind("<Button-1>", self.vb_xoa_goi_y)
        self.vb_text.bind("<<Paste>>", lambda e: self.root.after(50, self.vb_cap_nhat))
        self.vb_text.bind("<KeyRelease>", lambda e: self.vb_hen_cap_nhat())

    def update_foot(self):
        ten_giong = next(
            (g["ten"] for g in self.vieneu_giong
             if g["id"] == self.cfg.get("vieneu_voice_id")),
            self.cfg.get("vieneu_voice_id") or "(chưa chọn)")
        self.foot.set(
            f'Giọng {ten_giong}  ·  VieNeu-TTS chạy tại máy - '
            "offline sau lần tải mô hình đầu tiên")

    def cap_nhat_mo_ta_pc(self):
        pc = PHONG_CACH.get(self.cfg["phong_cach"], {})
        self.var["pc_mo_ta"].set(
            f'{pc.get("mo_ta", "")}   (nghỉ giữa câu {self.cfg["nghi_cau"]:.2f}s, '
            f'giữa đoạn {self.cfg["nghi_doan_vb"]:.2f}s)')

    # ================= GIỌNG =================
    def _nap_ngam_giong_vieneu_khoi_dong(self):
        """Âm thầm tải danh sách giọng VieNeu-TTS ở nền ngay khi khởi
        động - để ô Giọng hiện đúng tên thay vì "(đang tải danh sách...)"
        mãi. Đọc vẫn hoạt động bình thường trong lúc chờ (voice_id đã lưu
        vẫn dùng được), không hiện popup, không chặn giao diện, im lặng
        bỏ qua nếu lỗi (menu Giọng đọc > Tải / làm mới danh sách giọng
        VieNeu-TTS vẫn dùng được thủ công)."""
        if self.vieneu_giong:
            return

        def chay():
            try:
                ds = lay_danh_sach_giong_day_du()
            except Exception:
                self._bao_loi_tai_ngam_vieneu()
                return  # im lặng - không hiện popup lúc khởi động

            def cap_nhat():
                self.vieneu_giong = ds
                self.cap_nhat_combo_giong()
                self.update_foot()
            try:
                self.root.after(0, cap_nhat)
            except (RuntimeError, tk.TclError):
                pass

        threading.Thread(target=chay, daemon=True).start()

    def _bao_loi_tai_ngam_vieneu(self):
        """Tải ngầm lúc khởi động thất bại - đổi placeholder từ "đang tải"
        sang trạng thái rõ ràng, tránh kẹt mãi trông như đang chạy."""
        def cap_nhat():
            if (not self.vieneu_giong
                    and self.var["giong"].get() == "(đang tải danh sách giọng...)"):
                cho = "(chưa tải được - xem menu Giọng đọc)"
                self.cbo_giong["values"] = [cho]
                self.var["giong"].set(cho)
        try:
            self.root.after(0, cap_nhat)
        except (RuntimeError, tk.TclError):
            pass

    def tai_lai_giong_vieneu(self):
        def khi_xong(thanh_cong):
            if thanh_cong:
                self.cap_nhat_combo_giong()
                self.update_foot()
            tb = ("Đã tải danh sách giọng VieNeu-TTS." if thanh_cong
                 else "Không tải được danh sách giọng VieNeu-TTS.")
            self.var["cd_trangthai"].set(tb)
            self.var["vb_trangthai"].set(tb)

        TaiGiongVieNeuDialog(self.root, self, khi_xong)

    def tao_giong_rieng(self):
        def khi_xong(muc):
            # Nạp lại danh sách đầy đủ (đã gồm giọng mới) rồi CHỌN LUÔN
            # giọng vừa tạo, để người dùng nghe thử ngay không phải tự
            # tìm trong danh sách.
            try:
                self.vieneu_giong = lay_danh_sach_giong_day_du()
            except Exception:
                pass
            self.cfg["vieneu_voice_id"] = muc["id"]
            self.cap_nhat_combo_giong()
            self.update_foot()
            tb = f'Đã tạo giọng riêng "{muc["ten"]}" và chọn để dùng.'
            self.var["cd_trangthai"].set(tb)
            self.var["vb_trangthai"].set(tb)
            try:
                save_config(self.cfg)
            except OSError:
                pass

        TaoGiongRiengDialog(self.root, self, khi_xong)

    def quan_ly_giong_rieng(self):
        def khi_doi():
            # Giọng đang dùng có thể vừa bị xoá - nạp lại danh sách và để
            # cap_nhat_combo_giong tự chọn giọng khác nếu vậy.
            try:
                self.vieneu_giong = lay_danh_sach_giong_day_du()
            except Exception:
                pass
            self.cap_nhat_combo_giong()
            self.update_foot()
            self.ap_dung_cau_hinh()

        QuanLyGiongRiengDialog(self.root, self, khi_doi)

    def on_doi_giong(self, _e=None):
        ten = self.var["giong"].get()
        for g in self.vieneu_giong:
            if g["ten"] == ten:
                self.cfg["vieneu_voice_id"] = g["id"]
                break
        self.ap_dung_cau_hinh("Đã đổi giọng đọc.")

    def on_doi_phong_cach(self, _e=None):
        ap_dung_phong_cach(self.cfg, self.var["phong_cach"].get())
        self.ap_dung_cau_hinh(f'Phong cách: {self.cfg["phong_cach"]}.')

    def ap_dung_cau_hinh(self, thong_bao=""):
        """Đổi giọng/phong cách: giữ nguyên vị trí đang đọc, chỉ dựng lại
        lời."""
        dang_chay = self.phien_chay
        self.dung_tat_ca(silent=True)
        self.speaker.cfg = self.cfg
        self.speaker.clear_cache()
        try:
            save_config(self.cfg)
        except OSError:
            pass
        self.dung_playlist("cd", giu_vi_tri=True)
        self.dung_playlist("vb", giu_vi_tri=True)
        self.update_foot()
        self.cap_nhat_mo_ta_pc()
        self.cap_nhat_nut()
        if thong_bao:
            them = "  Bấm ĐỌC để đọc tiếp." if dang_chay else ""
            self.var["cd_trangthai"].set(thong_bao + them)
            self.var["vb_trangthai"].set(thong_bao + them)

    def nghe_thu(self):
        if not self.kiem_tra_moi_truong(can_noi_dung=False):
            return
        self.dung_tat_ca(silent=True)
        mau = ("Nam mô A Di Đà Phật. Đây là giọng đọc thử của chương trình. "
               "Hôm nay ngày mùng 2 tháng 8, quý vị nghe rõ chứ ạ?")
        self.var["cd_trangthai"].set("🔈 Đang nghe thử...")
        self.var["vb_trangthai"].set("🔈 Đang nghe thử...")
        self.stop_event.clear()
        ev = self.stop_event

        def chay():
            try:
                audio, dinh_dang = self.speaker._synth_blocking(mau)
                self.speaker.play(audio, ev, dinh_dang)
                self._ui(self.var["cd_trangthai"].set, "Nghe thử xong.")
                self._ui(self.var["vb_trangthai"].set, "Nghe thử xong.")
            except Exception as e:
                self._ui(self._loi_doc, None, str(e))

        threading.Thread(target=chay, daemon=True).start()

    # ================= DỮ LIỆU CÔNG ĐỨC =================
    def reload_data(self, show_errors=False):
        self.dung_tat_ca(silent=True)
        try:
            self.records, canh_bao = parse_data_file(self.cfg["data_file"])
        except FileNotFoundError:
            self.records, canh_bao = [], []
            self.fill_tree()
            self.phien["cd"].playlist = []
            self.phien["cd"].index = 0
            self.var["cd_tomtat"].set("")
            self.var["cd_trangthai"].set(
                "Chưa có file danh sách. Dùng 📂 Mở file khác, "
                "hoặc chuyển sang thẻ 📖 Đọc văn bản.")
            self.cap_nhat_nut()
            return
        except Exception as e:
            self.records, canh_bao = [], []
            self.fill_tree()
            self.phien["cd"].playlist = []
            self.phien["cd"].index = 0
            self.var["cd_trangthai"].set("Lỗi đọc danh sách.")
            self.var["cd_tomtat"].set("")
            if show_errors:
                messagebox.showerror("Lỗi", str(e), parent=self.root)
            self.cap_nhat_nut()
            return

        self.fill_tree()
        self.dung_playlist("cd")
        self.hien_thi_cd(0)
        tong = sum(1 for r in self.records if r["kind"] == "nguoi")
        tong_tien = 0
        for r in self.records:
            if r["kind"] == "nguoi":
                try:
                    tong_tien += parse_money(r["amount"])
                except ValueError:
                    pass
        self.var["cd_tomtat"].set(
            f'{tong} người · tổng {tong_tien:,} đồng · '
            f'~{uoc_luong_thoi_gian(self.phien["cd"].playlist, self.cfg)}'
            .replace(",", "."))
        self.var["cd_trangthai"].set(
            "Sẵn sàng. Bấm ĐỌC LIÊN TỤC để bắt đầu." if tong else
            "File danh sách chưa có ai. Mở congduc.txt và thêm dòng "
            "“Tên  <TAB>  Số tiền”.")
        self.cap_nhat_nut()

        if canh_bao and show_errors:
            messagebox.showwarning(
                "Có dòng chưa chuẩn",
                "Chương trình vẫn chạy được, nhưng nên kiểm tra lại:\n\n"
                + "\n".join(canh_bao[:15]) + ("\n..." if len(canh_bao) > 15 else ""),
                parent=self.root)

    def fill_tree(self):
        self.tree.delete(*self.tree.get_children())
        stt = 0
        for i, rec in enumerate(self.records):
            if rec["kind"] == "nguoi":
                stt += 1
                self.tree.insert("", "end", iid=str(i),
                                 values=(stt, rec["name"],
                                         format_money_for_display(rec["amount"])))
            else:
                self.tree.insert("", "end", iid=str(i),
                                 values=("", rec["name"], ""), tags=("tieude",))

    def dung_playlist(self, ma, giu_vi_tri=False, doc_loi_dan=True):
        """Dựng lại playlist cho một thẻ."""
        phien = self.phien[ma]
        cu = phien.index
        if ma == "cd":
            phien.playlist = build_playlist_congduc(
                self.records, self.noidung, self.cfg, self.tudien, doc_loi_dan)
            self.pb_cd["maximum"] = max(1, len(phien.playlist))
        else:
            text = self.vb_lay_text()
            phien.playlist = build_playlist_vanban(text, self.cfg, self.tudien)
            self.vb_chu_ky = (hash(text), self.cfg["so_ky_tu"],
                              self.cfg["doc_so_bang_chu"], self.cfg["bo_markdown"])
            self.pb_vb["maximum"] = max(1, len(phien.playlist))
            self.var["vb_tomtat"].set(
                f'{len(text.split())} từ · {len(phien.playlist)} đoạn · '
                f'~{uoc_luong_thoi_gian(phien.playlist, self.cfg)}'
                if text.strip() else "")
        phien.index = min(cu, max(0, len(phien.playlist) - 1)) if giu_vi_tri else 0

    # ================= HIỂN THỊ =================
    def hien_thi(self, phien, idx):
        if phien.ma == "cd":
            self.hien_thi_cd(idx)
        else:
            self.hien_thi_vb(idx)

    def hien_thi_cd(self, idx):
        pl = self.phien["cd"].playlist
        if not pl:
            self.var["cd_ten"].set("Chưa có dữ liệu")
            self.var["cd_tien"].set("")
            self.var["cd_cau"].set("")
            self.var["cd_tiendo"].set("0 / 0")
            self.pb_cd["value"] = 0
            return

        idx = max(0, min(idx, len(pl) - 1))
        seg = pl[idx]
        nhan = {"mo_dau": "【 LỜI MỞ ĐẦU 】", "giua": "【 LỜI TRI ÂN 】",
                "ket": "【 LỜI KẾT 】", "tieude": "【 TIÊU ĐỀ NHÓM 】"}
        if seg["loai"] == "nguoi":
            self.var["cd_ten"].set(seg["rec"]["name"])
            self.var["cd_tien"].set(
                format_money_for_display(seg["rec"]["amount"]) + " đồng")
        else:
            self.var["cd_ten"].set(nhan.get(seg["loai"], ""))
            self.var["cd_tien"].set("")
        self.var["cd_cau"].set(seg["text"])
        self.var["cd_tiendo"].set(f'{seg["stt"]} / {seg["tong"]}')
        self.pb_cd["value"] = idx + 1

        if seg["rec"] is not None:
            try:
                row = str(self.records.index(seg["rec"]))
                for iid in self.tree.get_children():
                    tags = list(self.tree.item(iid, "tags"))
                    if "dangdoc" in tags:
                        tags.remove("dangdoc")
                        self.tree.item(iid, tags=tags)
                self.tree.item(row, tags=list(self.tree.item(row, "tags")) + ["dangdoc"])
                self.tree.see(row)
            except (ValueError, tk.TclError):
                pass

    def hien_thi_vb(self, idx):
        pl = self.phien["vb"].playlist
        if not pl:
            self.var["vb_tiendo"].set("0 / 0")
            self.pb_vb["value"] = 0
            return
        idx = max(0, min(idx, len(pl) - 1))
        seg = pl[idx]
        self.var["vb_tiendo"].set(f'{seg["stt"]} / {seg["tong"]}')
        self.pb_vb["value"] = idx + 1
        try:
            self.vb_text.tag_remove("dangdoc", "1.0", "end")
            a, b = f'1.0 + {seg["start"]} chars', f'1.0 + {seg["end"]} chars'
            self.vb_text.tag_add("dangdoc", a, b)
            self.vb_text.see(a)
        except tk.TclError:
            pass

    def cap_nhat_nut(self):
        for ma in ("cd", "vb"):
            phien = self.phien[ma]
            dang_chay = self.phien_chay is phien
            co_noi_dung = bool(phien.playlist)
            btn_doc = getattr(self, f"btn_doc_{ma}", None)
            if btn_doc is None:
                continue
            if not co_noi_dung or phien.index <= 0:
                nhan = "▶  ĐỌC LIÊN TỤC"
            elif phien.index >= len(phien.playlist):
                nhan = "🔁  ĐỌC LẠI TỪ ĐẦU"
            else:
                nhan = f"▶  ĐỌC TIẾP  ({phien.index + 1}/{len(phien.playlist)})"
            btn_doc.configure(text=("🔊  ĐANG ĐỌC…" if dang_chay else nhan))
            dat_trang_thai_nut(btn_doc, co_noi_dung and not dang_chay, MAU_CHINH)
            dat_trang_thai_nut(getattr(self, f"btn_tam_{ma}"), dang_chay, MAU_TAM_DUNG)
            dat_trang_thai_nut(getattr(self, f"btn_dung_{ma}"),
                               dang_chay or phien.index > 0, MAU_DUNG)

    # ================= THẺ CÔNG ĐỨC =================
    def on_tree_double(self, _e):
        sel = self.tree.selection()
        if not sel:
            return
        rec = self.records[int(sel[0])]
        for i, seg in enumerate(self.phien["cd"].playlist):
            if seg["rec"] is rec:
                self.dung_tat_ca(silent=True)
                self.phien["cd"].index = i
                self.hien_thi_cd(i)
                self.var["cd_trangthai"].set(
                    f'Đã chọn dòng {seg["stt"]}. Bấm ĐỌC để đọc từ đây.')
                self.cap_nhat_nut()
                break

    def cd_ve_dau(self):
        self.dung_tat_ca(silent=True)
        self.dung_playlist("cd")
        self.hien_thi_cd(0)
        self.var["cd_trangthai"].set("Đã về đầu danh sách.")
        self.cap_nhat_nut()

    def cd_doc(self):
        phien = self.phien["cd"]
        if self.phien_chay is phien:
            return
        if not phien.playlist:
            self.dung_playlist("cd")
        if phien.index >= len(phien.playlist):
            phien.index = 0
        if not self.kiem_tra_moi_truong(phien):
            return
        phien.mode = "lien_tuc"
        self.bat_dau(phien)

    def cd_doc_mot_nguoi(self):
        phien = self.phien["cd"]
        self.dung_tat_ca(silent=True)
        if not phien.playlist:
            self.dung_playlist("cd")
        if not phien.playlist:
            return
        for i in range(phien.index, len(phien.playlist)):
            if phien.playlist[i]["loai"] == "nguoi" and i >= phien.index:
                phien.index = i
                break
        else:
            self.var["cd_trangthai"].set("Đã hết danh sách.")
            return
        self.hien_thi_cd(phien.index)
        if not self.kiem_tra_moi_truong(phien):
            return
        phien.mode = "don_le"
        self.bat_dau(phien)

    # ================= THẺ VĂN BẢN =================
    GOI_Y = ("Dán hoặc gõ nội dung tiếng Việt cần đọc vào đây.\n\n"
             "Chương trình tự tách câu và tự đọc ngày tháng, phần trăm, "
             "đơn vị đo, chữ viết tắt cho tự nhiên.")

    def vb_dat_goi_y(self):
        self.vb_text.delete("1.0", "end")
        self.vb_text.insert("1.0", self.GOI_Y, "goiy")
        self.vb_goi_y = True

    def vb_xoa_goi_y(self, _e=None):
        if self.vb_goi_y:
            self.vb_text.delete("1.0", "end")
            self.vb_goi_y = False

    def vb_lay_text(self) -> str:
        if self.vb_goi_y:
            return ""
        return self.vb_text.get("1.0", "end-1c")

    def vb_hen_cap_nhat(self):
        """Gõ xong 400ms mới tính lại, tránh tính liên tục khi đang gõ."""
        if getattr(self, "_vb_job", None):
            try:
                self.root.after_cancel(self._vb_job)
            except tk.TclError:
                pass
        self._vb_job = self.root.after(400, self.vb_cap_nhat)

    def vb_cap_nhat(self):
        if self.phien_chay is self.phien["vb"]:
            return
        if not self.vb_can_dung_lai():
            self.cap_nhat_nut()
            return
        self.dung_playlist("vb")
        self.hien_thi_vb(0)
        so = len(self.phien["vb"].playlist)
        self.var["vb_trangthai"].set(
            f"Sẵn sàng đọc {so} đoạn." if so else "Chưa có nội dung.")
        self.cap_nhat_nut()

    def vb_can_dung_lai(self) -> bool:
        text = self.vb_lay_text()
        chu_ky = (hash(text), self.cfg["so_ky_tu"], self.cfg["doc_so_bang_chu"],
                  self.cfg["bo_markdown"])
        return chu_ky != self.vb_chu_ky

    def vb_doc(self):
        phien = self.phien["vb"]
        if self.phien_chay is phien:
            return
        doi = False
        if self.vb_can_dung_lai():
            doi = bool(phien.playlist) and phien.index > 0
            self.dung_playlist("vb")
        if phien.index >= len(phien.playlist):
            phien.index = 0
        if not self.kiem_tra_moi_truong(phien):
            return
        phien.mode = "lien_tuc"
        self.bat_dau(phien)
        if doi:
            self.var["vb_trangthai"].set(
                "🔊 Nội dung đã thay đổi nên đọc lại từ đầu...")

    def vb_doc_tu_con_tro(self):
        phien = self.phien["vb"]
        self.dung_tat_ca(silent=True)
        if self.vb_can_dung_lai():
            self.dung_playlist("vb")
        if not phien.playlist:
            self.var["vb_trangthai"].set("Chưa có nội dung.")
            return
        try:
            vi_tri = len(self.vb_text.get("1.0", "insert"))
        except tk.TclError:
            vi_tri = 0
        phien.index = next((i for i, s in enumerate(phien.playlist)
                            if s["end"] > vi_tri), 0)
        self.hien_thi_vb(phien.index)
        if not self.kiem_tra_moi_truong(phien):
            return
        phien.mode = "lien_tuc"
        self.bat_dau(phien)

    def vb_mo_file(self):
        path = filedialog.askopenfilename(
            title="Mở file văn bản",
            filetypes=[("File văn bản", "*.txt *.md *.csv *.log"),
                       ("Tất cả file", "*.*")])
        if not path:
            return
        try:
            noi_dung = Path(path).read_text(encoding="utf-8-sig", errors="replace")
        except OSError as e:
            messagebox.showerror("Lỗi", f"Không đọc được file:\n{e}", parent=self.root)
            return
        self.dung_tat_ca(silent=True)
        self.vb_goi_y = False
        self.vb_text.delete("1.0", "end")
        self.vb_text.insert("1.0", noi_dung)
        self.dung_playlist("vb")
        self.hien_thi_vb(0)
        self.var["vb_trangthai"].set(
            f"Đã mở {Path(path).name} · {len(self.phien['vb'].playlist)} đoạn.")
        self.nb.select(self.tab_vb)
        self.cap_nhat_nut()

    def vb_dan(self):
        try:
            noi_dung = self.root.clipboard_get()
        except tk.TclError:
            messagebox.showinfo("Clipboard", "Clipboard đang trống.", parent=self.root)
            return
        self.vb_xoa_goi_y()
        self.vb_text.insert("insert", noi_dung)
        self.vb_cap_nhat()

    def vb_xoa(self):
        self.dung_tat_ca(silent=True)
        self.vb_dat_goi_y()
        self.phien["vb"].playlist = []
        self.phien["vb"].index = 0
        self.vb_chu_ky = None
        self.var["vb_tiendo"].set("0 / 0")
        self.var["vb_tomtat"].set("")
        self.pb_vb["value"] = 0
        self.var["vb_trangthai"].set("Đã xoá nội dung.")
        self.cap_nhat_nut()

    def vb_luu_mp3(self):
        if self.vb_can_dung_lai():
            self.dung_playlist("vb")
        segs = list(self.phien["vb"].playlist)
        if not segs:
            messagebox.showinfo("Lưu WAV", "Chưa có nội dung để đọc.", parent=self.root)
            return
        if not vieneu_da_cai_dat():
            messagebox.showerror("Thiếu thư viện", huong_dan_cai_vieneu(),
                                 parent=self.root)
            return
        path = filedialog.asksaveasfilename(
            title="Lưu giọng đọc ra file WAV", defaultextension=".wav",
            initialfile="giongdoc.wav", filetypes=[("WAV", "*.wav")])
        if not path:
            return
        self.var["vb_trangthai"].set("Đang tạo file WAV, xin đợi...")

        def chay():
            import wave
            ghi = None
            try:
                for i, seg in enumerate(segs, 1):
                    audio, _dinh_dang = self.speaker._synth_blocking(seg["text"])
                    if not audio:
                        continue
                    with tempfile.NamedTemporaryFile(suffix=".wav",
                                                     delete=False) as f:
                        tmp_path = f.name
                    try:
                        Path(tmp_path).write_bytes(audio)
                        with wave.open(tmp_path, "rb") as doc:
                            if ghi is None:
                                ghi = wave.open(path, "wb")
                                ghi.setnchannels(doc.getnchannels())
                                ghi.setsampwidth(doc.getsampwidth())
                                ghi.setframerate(doc.getframerate())
                            ghi.writeframes(doc.readframes(doc.getnframes()))
                    finally:
                        try:
                            Path(tmp_path).unlink()
                        except OSError:
                            pass
                    self._ui(self.var["vb_trangthai"].set,
                             f"Đang tạo WAV: {i}/{len(segs)} đoạn...")
                if ghi is not None:
                    ghi.close()
                self._ui(self.var["vb_trangthai"].set, f"✅ Đã lưu: {path}")
                self._ui(lambda: messagebox.showinfo(
                    "Xong", f"Đã lưu file WAV:\n{path}", parent=self.root))
            except Exception as e:
                if ghi is not None:
                    try:
                        ghi.close()
                    except Exception:
                        pass
                self._ui(self._loi_doc, None, str(e))

        threading.Thread(target=chay, daemon=True).start()

    # ================= ĐIỀU KHIỂN ĐỌC =================
    def kiem_tra_moi_truong(self, phien=None, can_noi_dung=True) -> bool:
        if not vieneu_da_cai_dat():
            messagebox.showerror("Thiếu thư viện", huong_dan_cai_vieneu(),
                                 parent=self.root)
            return False
        if not self.cfg["ffplay"].exists():
            self.hoi_tai_ffmpeg()
            return False
        if can_noi_dung and phien is not None and not phien.playlist:
            messagebox.showwarning("Chưa có nội dung",
                                   "Thẻ này chưa có nội dung để đọc.",
                                   parent=self.root)
            return False
        return True

    def hoi_tai_ffmpeg(self):
        def sau_khi_tai():
            tb = "Đã có FFmpeg. Bấm ĐỌC LIÊN TỤC để bắt đầu."
            self.var["cd_trangthai"].set(tb)
            self.var["vb_trangthai"].set(tb)

        TaiFFmpegDialog(self.root, self.cfg["ffplay"].parent, sau_khi_tai)

    def bat_dau(self, phien):
        # Chỉ đọc một thẻ tại một thời điểm: dừng thẻ kia nếu đang đọc.
        khac = self.phien_chay
        self.dung_tat_ca(silent=True)
        if khac is not None and khac is not phien:
            self.var[f"{khac.ma}_trangthai"].set(
                "⏸ Đã dừng để nhường thẻ kia. Bấm ĐỌC TIẾP khi cần.")
        self.stop_event.clear()
        self.phien_chay = phien
        self.speaker.cfg = self.cfg
        self.var[f"{phien.ma}_trangthai"].set("🔊 Đang đọc...")
        self.cap_nhat_nut()
        self.worker = threading.Thread(target=self._worker, args=(phien,), daemon=True)
        self.worker.start()

    def tam_dung(self, phien):
        if self.phien_chay is not phien:
            return
        self.stop_event.set()
        self.speaker.stop()
        self.var[f"{phien.ma}_trangthai"].set(
            "⏸ Tạm dừng. Bấm ĐỌC TIẾP để đọc tiếp đúng chỗ đang dở.")

    def dung(self, phien):
        dang = self.phien_chay is phien
        if dang:
            self.dung_tat_ca(silent=True)
        phien.index = 0
        if phien.ma == "cd":
            self.hien_thi_cd(0)
            self.var["cd_trangthai"].set("⏹ Đã dừng, quay về đầu.")
        else:
            self.hien_thi_vb(0)
            self.var["vb_trangthai"].set("⏹ Đã dừng, quay về đầu.")
        self.cap_nhat_nut()

    def dung_tat_ca(self, silent=False):
        """Dừng mọi thứ đang phát, giữ nguyên vị trí của các thẻ."""
        self.stop_event.set()
        self.speaker.stop()
        if self.worker and self.worker.is_alive():
            self.worker.join(timeout=2.0)
        self.speaker.clear_cache()
        self.phien_chay = None
        if not silent:
            self.var["cd_trangthai"].set("⏹ Đã dừng.")
            self.var["vb_trangthai"].set("⏹ Đã dừng.")
        self.cap_nhat_nut()

    # ================= LUỒNG ĐỌC =================
    def _ui(self, func, *args):
        try:
            self.root.after(0, func, *args)
        except (RuntimeError, tk.TclError):
            pass

    def _worker(self, phien):
        try:
            while phien.index < len(phien.playlist):
                if self.stop_event.is_set():
                    break
                idx = phien.index
                seg = phien.playlist[idx]
                self._ui(self.hien_thi, phien, idx)

                if phien.mode == "lien_tuc" and idx + 1 < len(phien.playlist):
                    self.speaker.prefetch((phien.ma, idx + 1),
                                          phien.playlist[idx + 1]["text"])
                try:
                    audio, dinh_dang = self.speaker.get_audio(
                        (phien.ma, idx), seg["text"])
                    if self.stop_event.is_set():
                        break
                    xong = self.speaker.play(audio, self.stop_event, dinh_dang)
                except Exception as e:
                    self._ui(self._loi_doc, phien, str(e))
                    return
                if not xong:
                    break

                phien.index = idx + 1
                if phien.mode == "don_le":
                    self._ui(self._xong_don_le, phien)
                    return

                het = time.time() + seg["nghi"]
                while time.time() < het:
                    if self.stop_event.is_set():
                        break
                    time.sleep(0.05)

            if not self.stop_event.is_set():
                self._ui(self._doc_xong, phien)
        finally:
            if self.phien_chay is phien:
                self.phien_chay = None
            self._ui(self.cap_nhat_nut)

    def _xong_don_le(self, phien):
        self.phien_chay = None
        self.var[f"{phien.ma}_trangthai"].set("Đã đọc xong một người.")
        self.cap_nhat_nut()

    def _doc_xong(self, phien):
        self.phien_chay = None
        if phien.ma == "vb":
            self.pb_vb["value"] = self.pb_vb["maximum"]
            self.var["vb_trangthai"].set("✅ Đã đọc xong toàn bộ văn bản.")
        else:
            tong = sum(1 for r in self.records if r["kind"] == "nguoi")
            self.var["cd_tiendo"].set(f"{tong} / {tong}")
            self.pb_cd["value"] = self.pb_cd["maximum"]
            self.var["cd_ten"].set("🙏 ĐÃ ĐỌC XONG DANH SÁCH")
            self.var["cd_tien"].set("")
            self.var["cd_cau"].set("Thành kính tri ân công đức quý vị.")
            self.var["cd_trangthai"].set("✅ Hoàn tất toàn bộ danh sách.")
        phien.index = len(phien.playlist)
        self.cap_nhat_nut()

    def _loi_doc(self, phien, err):
        self.phien_chay = None
        tb = "⚠ Không đọc được. Kiểm tra Internet rồi bấm ĐỌC TIẾP."
        if phien is not None:
            self.var[f"{phien.ma}_trangthai"].set(tb)
        else:
            self.var["cd_trangthai"].set(tb)
            self.var["vb_trangthai"].set(tb)
        self.cap_nhat_nut()
        messagebox.showerror(
            "Lỗi giọng đọc",
            "Không tạo được giọng đọc bằng Edge TTS.\n\n"
            "Edge TTS cần kết nối Internet. Kiểm tra mạng rồi bấm ĐỌC TIẾP "
            "để đọc tiếp đúng chỗ đang dở.\n\n"
            f"Chi tiết: {err}", parent=self.root)

    # ================= CỬA SỔ PHỤ =================
    def sua_noi_dung(self):
        def on_saved():
            self.noidung = NoiDung().load(NOIDUNG_FILE)
            self.dung_tat_ca(silent=True)
            self.dung_playlist("cd")
            self.hien_thi_cd(0)
            self.var["cd_trangthai"].set("Đã cập nhật lời dẫn.")
            self.cap_nhat_nut()

        NoiDungDialog(self.root, NoiDung().load(NOIDUNG_FILE), on_saved)

    def sua_tudien(self):
        def on_saved():
            self.tudien = load_tudien(TUDIEN_FILE)
            self.dung_tat_ca(silent=True)
            self.dung_playlist("cd", giu_vi_tri=True)
            self.dung_playlist("vb", giu_vi_tri=True)
            self.var["cd_trangthai"].set("Đã cập nhật từ điển cách đọc.")
            self.var["vb_trangthai"].set("Đã cập nhật từ điển cách đọc.")
            self.cap_nhat_nut()

        SuaFileDialog(self.root, TUDIEN_FILE, "Từ điển cách đọc - tudien.ini",
                      noi_dung_tudien_mac_dinh, on_saved)

    def cai_dat(self):
        def on_saved():
            self.cfg = load_config()
            self.var["phong_cach"].set(self.cfg["phong_cach"])
            self.ap_dung_cau_hinh("Đã lưu cài đặt.")

        CaiDatDialog(self.root, dict(self.cfg), on_saved)

    def xem_truoc(self):
        ma = "cd" if self.nb.index(self.nb.select()) == 0 else "vb"
        if ma == "vb" and self.vb_can_dung_lai():
            self.dung_playlist("vb")
        elif ma == "cd" and not self.phien["cd"].playlist:
            self.dung_playlist("cd")
        playlist = self.phien[ma].playlist
        if not playlist:
            messagebox.showinfo("Xem trước", "Thẻ này chưa có nội dung.",
                                parent=self.root)
            return

        dong = []
        for seg in playlist:
            dau = {"mo_dau": "[MỞ ĐẦU] ", "giua": "[GIỮA] ", "ket": "[KẾT] ",
                   "tieude": "[NHÓM] "}.get(seg["loai"], "")
            stt = f'{seg["stt"]:>4}. ' if seg["loai"] in ("nguoi", "cau") else "      "
            dong.append(stt + dau + seg["text"])

        win = tk.Toplevel(self.root)
        win.title("Xem trước toàn bộ lời đọc")
        win.geometry("860x640")
        box = tk.Text(win, wrap="word", font=("Segoe UI", 11))
        box.pack(fill="both", expand=True, side="left", padx=(10, 0), pady=10)
        sb = ttk.Scrollbar(win, command=box.yview)
        sb.pack(fill="y", side="right", padx=(0, 10), pady=10)
        box.configure(yscrollcommand=sb.set)
        box.insert("1.0", "\n\n".join(dong))
        box.configure(state="disabled")

    def open_data_file(self):
        path = filedialog.askopenfilename(
            title="Chọn file công đức", initialdir=str(BASE_DIR),
            filetypes=[("Text file", "*.txt"), ("Tất cả file", "*.*")])
        if not path:
            return
        self.cfg["data_file"] = Path(path)
        self.var["cd_file"].set(path)
        try:
            save_config(self.cfg)
        except OSError:
            pass
        self.nb.select(self.tab_cd)
        self.reload_data(show_errors=True)

    def huong_dan(self):
        messagebox.showinfo(
            "Hướng dẫn nhanh",
            "THẺ 📜 DANH SÁCH CÔNG ĐỨC\n"
            "  • Bấm ▶ ĐỌC LIÊN TỤC là đọc hết danh sách.\n"
            "  • Nháy đúp một dòng để bắt đầu từ dòng đó.\n"
            "  • Lời mở đầu / kết sửa ở Công cụ > Sửa lời dẫn.\n\n"
            "THẺ 📖 ĐỌC VĂN BẢN\n"
            "  • Gõ, dán Ctrl+V hoặc mở file .txt rồi bấm ▶ ĐỌC LIÊN TỤC.\n"
            "  • Câu đang đọc được tô sáng vàng.\n"
            "  • Muốn đọc từ giữa bài: nháy chuột vào chỗ đó rồi bấm "
            "“Đọc từ vị trí con trỏ”.\n\n"
            "CHUNG\n"
            "  • ⏸ TẠM DỪNG rồi ▶ ĐỌC TIẾP: tiếp đúng chỗ đang dở.\n"
            "  • ⏹ DỪNG: dừng và quay về đầu.\n"
            "  • Mỗi thẻ giữ vị trí riêng, chuyển thẻ không mất chỗ đang đọc.\n"
            "  • Phím tắt: F5 đọc · F6 tạm dừng · F7 dừng.\n"
            "  • Đọc sai chữ nào: Công cụ > Sửa từ điển cách đọc.",
            parent=self.root)

    def gioi_thieu(self):
        messagebox.showinfo(
            "Giới thiệu",
            f"{APP_TITLE}  v{APP_VERSION}\n\n"
            "Đọc tiếng Việt bằng Microsoft Edge TTS, phát qua ffplay.\n"
            "Cần Internet khi đọc.\n\n"
            f"Thư mục chương trình:\n{BASE_DIR}", parent=self.root)

    def quit_app(self):
        self.dung_tat_ca(silent=True)
        self.speaker.shutdown()
        self.root.destroy()


def main():
    # Chế độ dòng lệnh: dùng cho CaiDat.bat / DongGoi.bat để tự động tải
    # ffplay.exe TRƯỚC khi đóng gói, không cần mở giao diện.
    #     py DocCongDuc.py --tai-ffmpeg
    if len(sys.argv) > 1 and sys.argv[1] == "--tai-ffmpeg":
        bin_dir = BASE_DIR / "ffmpeg" / "bin"
        if (bin_dir / "ffplay.exe").exists():
            print(f"Đã có sẵn: {bin_dir / 'ffplay.exe'}")
            return
        try:
            dest = tai_ffmpeg_tu_dong(bin_dir, print)
            print(f"Tải xong: {dest}")
        except Exception as e:
            print(f"[LỖI] {e}")
            sys.exit(1)
        return

    # Chế độ dòng lệnh: "làm nóng" VieNeu-TTS NGAY LÚC CÀI ĐẶT - tải mô
    # hình + danh sách giọng + thử tổng hợp một câu ngắn, để lúc mở
    # chương trình thật là dùng được ngay, không cần tải gì thêm.
    #     py DocCongDuc.py --tai-vieneu
    if len(sys.argv) > 1 and sys.argv[1] == "--tai-vieneu":
        try:
            print("Bước 1/4: Nạp mô hình VieNeu-TTS...")
            dam_bao_vieneu_san_sang(print)
            print("Bước 2/4: Lấy danh sách giọng dựng sẵn...")
            ds = lay_danh_sach_giong_vieneu()
            print(f"  Có {len(ds)} giọng: "
                  + ", ".join(g["ten"].split(" — ")[0] for g in ds[:8])
                  + (", ..." if len(ds) > 8 else ""))
            print("Bước 3/4: Thử tổng hợp một câu ngắn để xác nhận hoạt động...")
            audio = tong_hop_vieneu("Xin chào, VieNeu-TTS đã sẵn sàng.",
                                    ds[0]["id"] if ds else "")
            print(f"  Tổng hợp thành công, {len(audio):,} bytes âm thanh.")
            print("Bước 4/4: Tải phần dành cho nhân bản giọng...")
            if tai_tep_nhan_ban_giong(lambda m: print(f"  {m}")):
                print("  Xong - máy này sẽ mở nhanh và nhân bản được khi "
                      "không có mạng.")
            print(f"Xong. Mô hình đã lưu tại: {BASE_DIR / 'vieneu_models'}")
        except Exception as e:
            print(f"[LỖI] {e}")
            sys.exit(1)
        return

    root = tk.Tk()
    try:
        root.tk.call("tk", "scaling", 1.15)
    except tk.TclError:
        pass
    try:
        mac_dinh = tkfont.nametofont("TkDefaultFont")
        mac_dinh.configure(family="Segoe UI", size=10)
    except tk.TclError:
        pass
    DocApp(root)
    root.mainloop()


if __name__ == "__main__":
    main()
