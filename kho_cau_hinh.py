# -*- coding: utf-8 -*-
"""Gom các tệp cấu hình rời vào MỘT tệp SQLite.

Chủ dự án nhìn thư mục cài đặt thấy bảy tệp .ini/.json/.txt nằm lẫn với
GiongViet.exe và muốn gọn lại. Nay tất cả nằm trong `giongviet.db`.

CÁCH LÀM: kho khoá - giá trị, mỗi tệp cũ thành MỘT hàng, nội dung giữ nguyên
là chuỗi y như lúc còn nằm trong tệp. Nhờ vậy không phải viết lại một dòng
parser nào: configparser vẫn đọc chuỗi INI, json vẫn đọc chuỗi JSON. Chỗ duy
nhất đổi là lớp đọc/ghi.

VÌ SAO KHÔNG dựng bảng - cột cho từng thiết lập: mỗi tệp một lược đồ riêng,
dựng bảng riêng cho từng cái là viết lại toàn bộ phần đọc ghi của engine lẫn
hai tầng giao diện - đổi rất nhiều chỗ đang chạy tốt để lấy về đúng một thứ:
thư mục nhìn gọn hơn. Không đáng.

congduc.txt KHÔNG vào đây. Đó là văn bản người dùng tự soạn và tự mở bằng
Notepad, đường dẫn còn đổi được sang chỗ khác trong cấu hình - nhốt nó vào cơ
sở dữ liệu là lấy mất của họ một thứ đang dùng hằng ngày.

AN TOÀN: tệp cũ KHÔNG bị xoá. Lần đầu chạy, nội dung được chép vào kho rồi tệp
gốc dời sang thư mục `sao-luu-cu/`. Có trục trặc thì chép ngược lại là xong.
"""

import shutil
import sqlite3
import threading
from pathlib import Path

TEN_KHO = "giongviet.db"
THU_MUC_SAO_LUU = "sao-luu-cu"

# Đúng những tệp được gom. congduc.txt cố ý vắng mặt - xem docstring.
# noidung-*.ini (lời dẫn riêng của từng hồ sơ) gom theo mẫu ở _ten_can_gom().
TEP_GOM = ("cauhinh.ini", "tudien.ini", "noidung.ini",
           "hoso.json", "giaodien.json", "hoso-v2.json")

_goc: Path | None = None
_khoa = threading.Lock()


def dat_goc(thu_muc) -> None:
    """Engine gọi ngay sau khi tính BASE_DIR. Tách rời thế này để module kho
    không phải import ngược vào engine - hai bên import nhau là vòng."""
    global _goc
    _goc = Path(thu_muc)


def goc():
    """Thư mục kho đang trỏ tới, hoặc None. Engine hỏi qua đây chứ KHÔNG so
    với BASE_DIR của nó: bộ kiểm đổi BASE_DIR sang thư mục tạm mà kho vẫn ở
    chỗ cũ, so nhầm là bộ kiểm ghi thẳng vào kho thật - đã xảy ra."""
    return _goc


def _duong_kho() -> Path:
    if _goc is None:
        raise RuntimeError("Chưa gọi kho_cau_hinh.dat_goc()")
    return _goc / TEN_KHO


def _ket_noi() -> sqlite3.Connection:
    cn = sqlite3.connect(_duong_kho())
    cn.execute("CREATE TABLE IF NOT EXISTS tep ("
               "ten TEXT PRIMARY KEY, noi_dung TEXT NOT NULL)")
    return cn


def _ten_can_gom(ten: str) -> bool:
    return ten in TEP_GOM or (ten.startswith("noidung-") and ten.endswith(".ini"))


def doc(ten: str):
    """Nội dung tệp ảo, hoặc None nếu kho chưa có.

    Chưa có tệp kho thì về tay không NGAY, đừng gọi _ket_noi(): sqlite3.connect
    tự tạo tệp, nên chỉ đọc thôi cũng đẻ ra một giongviet.db rỗng. Bộ kiểm chạy
    xong để lại đúng một tệp như thế giữa thư mục dự án.
    """
    if _goc is None or not _duong_kho().exists():
        return None
    with _khoa:
        try:
            with _ket_noi() as cn:
                h = cn.execute("SELECT noi_dung FROM tep WHERE ten=?", (ten,)).fetchone()
            return h[0] if h else None
        except sqlite3.Error:
            return None


def ghi(ten: str, noi_dung: str) -> bool:
    if _goc is None:
        return False
    with _khoa:
        try:
            with _ket_noi() as cn:
                cn.execute("INSERT INTO tep(ten, noi_dung) VALUES(?,?) "
                           "ON CONFLICT(ten) DO UPDATE SET noi_dung=excluded.noi_dung",
                           (ten, str(noi_dung)))
            return True
        except sqlite3.Error:
            return False


def co(ten: str) -> bool:
    return doc(ten) is not None


def danh_sach() -> list:
    if _goc is None:
        return []
    with _khoa:
        try:
            with _ket_noi() as cn:
                return [h[0] for h in cn.execute("SELECT ten FROM tep ORDER BY ten")]
        except sqlite3.Error:
            return []


def nhap_tu_tep_cu() -> dict:
    """Chép tệp cũ vào kho rồi dời chúng sang sao-luu-cu/.

    Chỉ chép tệp nào kho CHƯA có: chạy lại lần hai không đè mất thiết lập mới.
    Dời chứ không xoá - có trục trặc thì chép ngược lại là xong.
    """
    if _goc is None:
        return {}
    ket = {}
    luu = _goc / THU_MUC_SAO_LUU
    for tep in sorted(_goc.glob("*")):
        if not tep.is_file() or not _ten_can_gom(tep.name):
            continue

        # TÁCH hai việc: gom vào kho, và dọn tệp cũ. Bản trước gộp làm một, hễ
        # kho đã có mục ấy là `continue` ngay - nên lần đầu gom được mà dời hụt
        # (Explorer hay phần mềm diệt virus đang giữ tệp) thì từ đó về sau
        # KHÔNG BAO GIỜ dọn nữa, tệp kẹt lại vĩnh viễn. Chủ dự án gặp đúng thế:
        # có giongviet.db mà sáu tệp cũ vẫn nằm nguyên.
        if not co(tep.name):
            try:
                # utf-8-sig: cauhinh.ini và tudien.ini vốn ghi kèm BOM.
                noi_dung = tep.read_text(encoding="utf-8-sig")
            except (OSError, UnicodeDecodeError) as loi:
                ket[tep.name] = f"không đọc được: {loi}"
                continue
            if not ghi(tep.name, noi_dung):
                ket[tep.name] = "ghi vào kho không xong"
                continue

        # Tới đây kho CHẮC CHẮN đã có nội dung, nên dọn tệp cũ là an toàn.
        # Thử lại mỗi lần khởi động cho tới khi dọn được.
        try:
            luu.mkdir(exist_ok=True)
            dich = luu / tep.name
            if dich.exists():
                dich.unlink()          # lần trước dời dở, ghi đè bản sao cũ
            shutil.move(str(tep), str(dich))
            ket[tep.name] = "đã gom"
        except OSError as loi:
            # KHÔNG nuốt im lặng nữa: nuốt là lần sau không ai biết vì sao thư
            # mục vẫn bừa. Kho đã có nội dung nên chương trình vẫn chạy đúng.
            ket[tep.name] = f"đã gom, chưa dọn được tệp cũ: {loi}"
    return ket


def xuat_ra_tep(thu_muc=None) -> int:
    """Ghi ngược mọi thứ trong kho ra tệp rời, để chẩn đoán hoặc quay về.

    Mất đường này là mất luôn khả năng mở cấu hình bằng Notepad - thứ đang
    dùng để dò lỗi. Có nó thì đổi sang SQLite không phải cửa một chiều.
    """
    if _goc is None:
        return 0
    ra = Path(thu_muc) if thu_muc else _goc
    ra.mkdir(parents=True, exist_ok=True)
    dem = 0
    for ten in danh_sach():
        noi_dung = doc(ten)
        if noi_dung is None:
            continue
        try:
            (ra / ten).write_text(noi_dung, encoding="utf-8")
            dem += 1
        except OSError:
            pass
    return dem
