# -*- coding: utf-8 -*-
"""Ghi văn bản đã sửa ra đĩa — KHÔNG BAO GIỜ ghi đè tệp gốc của người dùng.

Quyết định của chủ dự án (2026-08-12): Ctrl+S ghi thành TỆP MỚI nếu tệp cũ đã
có, đánh số tăng dần. Người dùng đích là người lớn tuổi không rành máy tính;
mất bản gốc vì bấm nhầm Ctrl+S là thứ không sửa lại được.

Cách đặt số theo đúng kiểu File Explorer của Windows - `tên (1).txt`,
`tên (2).txt` - vì đó là thứ người dùng đã nhìn thấy cả đời mỗi khi chép tệp.

MỘT LẦN duy nhất đẻ ra tệp mới: lần lưu đầu tiên. Sau đó tệp mới ấy trở thành
tệp của phiên làm việc, các lần lưu sau ghi đè lên chính nó. Nếu lần nào cũng
đẻ tệp mới thì soạn một buổi sáng là thư mục đầy "(1) (2) (3)…" - phiền không
kém gì mất bản gốc.
"""

import os
import re
from pathlib import Path

# Ghi tệp tạm rồi đổi tên đè lên đích. Đổi tên trên cùng ổ đĩa là thao tác
# nguyên tử, nên mất điện giữa chừng thì tệp đích còn nguyên bản cũ chứ không
# cụt nửa chừng. Đo được ở phép thử mốc 0.
DUOI_TAM = ".tam"

# Chặn vòng lặp vô hạn nếu thư mục có sẵn hàng nghìn bản đánh số.
SO_TOI_DA = 999


def _tach_so(ten_goc: str) -> str:
    """Bỏ phần " (n)" ở cuối tên nếu có, để không đẻ ra "tên (1) (1)"."""
    return re.sub(r"\s\(\d+\)$", "", ten_goc)


def duong_dan_moi(dich: Path) -> Path:
    """Đường dẫn trống đầu tiên: dich, rồi "dich (1)", "dich (2)"…

    Trả về chính `dich` nếu chưa có tệp nào ở đó.
    """
    dich = Path(dich)
    if not dich.exists():
        return dich
    goc = _tach_so(dich.stem)
    for n in range(1, SO_TOI_DA + 1):
        ung_vien = dich.with_name(f"{goc} ({n}){dich.suffix}")
        if not ung_vien.exists():
            return ung_vien
    raise OSError(f"Thư mục đã có quá {SO_TOI_DA} bản của {goc}{dich.suffix}")


def ghi_an_toan(dich: Path, noi_dung: str) -> Path:
    """Ghi đè `dich`, qua tệp tạm. Chỉ dùng cho tệp DO CHƯƠNG TRÌNH tạo ra."""
    dich = Path(dich)
    tam = dich.with_name(dich.name + DUOI_TAM)
    try:
        tam.write_text(noi_dung, encoding="utf-8")
        os.replace(tam, dich)
    except OSError:
        # Dọn tệp tạm rồi mới ném lỗi lên, đừng để lại rác cho người dùng thấy.
        if tam.exists():
            try:
                tam.unlink()
            except OSError:
                pass
        raise
    return dich


def luu(dich: Path, noi_dung: str, da_la_ban_cua_ta: bool = False) -> Path:
    """Lưu văn bản, trả về đường dẫn ĐÃ ghi thật.

    da_la_ban_cua_ta = False (lần lưu đầu): tệp gốc còn có thì né sang bản mới.
    da_la_ban_cua_ta = True  (các lần sau): ghi đè chính bản mình vừa tạo.

    Người gọi phải nhớ đường dẫn trả về và từ lần sau truyền True, nếu không
    mỗi lần Ctrl+S lại đẻ thêm một tệp.
    """
    dich = Path(dich)
    thuc = dich if da_la_ban_cua_ta else duong_dan_moi(dich)
    thuc.parent.mkdir(parents=True, exist_ok=True)
    return ghi_an_toan(thuc, noi_dung)


def thu_muc_mac_dinh() -> Path:
    """Chỗ lưu khi không biết tệp nằm đâu.

    Cần đến vì WebView2 không cho biết đường dẫn thật của tệp kéo thả vào
    (đo ở phép thử mốc 0: pywebview 6.2.1 không có sự kiện thả tệp ở tầng
    native, JS chỉ nhận được nội dung). Văn bản dán từ clipboard cũng vậy.
    """
    return Path.home() / "Documents" / "GiongViet"
