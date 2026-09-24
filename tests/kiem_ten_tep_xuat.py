# -*- coding: utf-8 -*-
"""BAI CANH (xanh = tot): ten tep nguoi dung go phai xuat duoc.

VI SAO CO BAI NAY

Nguoi dung go ten ban ghi la "Cong duc T8/2026" - do la cach nguoi ta viet
thang, hoan toan tu nhien. Windows cam 9 ky tu trong ten tep, va dau "/" la
mot trong so do.

Do ngay 08/09/2026, 4/9 ten thu nghiem KHONG tao duoc tep:

    "Cong duc T8/2026"      -> FileNotFoundError
    "Ban ghi *nhap*"        -> OSError [Errno 22]
    'Ten co "ngoac kep"'    -> OSError [Errno 22]
    "a?b"                   -> OSError [Errno 22]

Loi CO duoc bat, nhung cau bao hien ra cho nguoi lon tuoi la:
    [Errno 22] Invalid argument: 'C:\\Users\\...\\Ban ghi *nhap*.wav'
Ho khong the doan ra la minh vua go mot ky tu Windows khong nhan.

Ban va loc ten TRUOC khi ghep duong dan: ky tu cam thanh gach ngang, ten rong
thanh ten mac dinh, ten thiet bi (CON, PRN, NUL...) them gach duoi. Tep van ra,
ten van doc duoc.

Bai chay tren thu muc tam. KHONG cham mot byte du lieu nguoi dung,
KHONG nap mo hinh, KHONG sinh am thanh.
"""
import io
import sys
import shutil
import tempfile
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")

from src.app import luu_tep

loi = 0


def ok(dieu_kien, nhan, them=""):
    global loi
    print(f"  {'ĐẠT ' if dieu_kien else 'LỆCH'} {nhan}" + (f"  →  {them}" if them else ""))
    if not dieu_kien:
        loi += 1


tam = Path(tempfile.mkdtemp(prefix="kiem_ten_tep_"))
try:
    print("--- A. Mọi tên người dùng có thể gõ đều phải tạo được tệp ---")
    TEN = [
        "Công đức tháng 8", "Công đức T8/2026", "Danh sách: chùa A",
        "Bản ghi *nháp*", 'Tên có "ngoặc kép"', "a?b", "CON", "PRN", "NUL",
        "  ", "", "Tên<lớn>hơn|nhỏ", "kết thúc bằng dấu chấm.", "x" * 200,
        "back\\slash",
    ]
    for t in TEN:
        an = luu_tep.ten_tep_an_toan(t)
        p = luu_tep.duong_dan_moi(tam / f"{an}.wav")
        try:
            p.write_bytes(b"RIFF")
            ok(True, f"{t[:30]!r} → {p.name[:44]}")
        except Exception as ex:
            ok(False, f"{t[:30]!r}", f"{type(ex).__name__}: {str(ex)[:50]}")

    print("\n--- B. Tên vẫn phải đọc được, không bị băm nát ---")
    ok(luu_tep.ten_tep_an_toan("Công đức T8/2026") == "Công đức T8-2026",
       "dấu / thành gạch ngang, giữ nguyên chữ",
       luu_tep.ten_tep_an_toan("Công đức T8/2026"))
    ok(luu_tep.ten_tep_an_toan("Công đức tháng 8") == "Công đức tháng 8",
       "tên vốn hợp lệ thì KHÔNG đụng vào")
    ok(luu_tep.ten_tep_an_toan("") == "Ban ghi", "tên rỗng có tên mặc định")
    ok(luu_tep.ten_tep_an_toan("CON").upper() != "CON", "tên thiết bị được đổi")

    print("\n--- C. KHÔNG BAO GIỜ ghi đè tệp sẵn có ---")
    goc = tam / "trung.wav"
    goc.write_bytes(b"BAN GOC CUA NGUOI DUNG")
    ten_ra = []
    for _ in range(3):
        p = luu_tep.duong_dan_moi(tam / "trung.wav")
        p.write_bytes(b"BAN MOI")
        ten_ra.append(p.name)
    ok(goc.read_bytes() == b"BAN GOC CUA NGUOI DUNG",
       "tệp gốc còn nguyên từng byte")
    ok(len(set(ten_ra)) == 3, "mỗi lần ra một tên khác", ", ".join(ten_ra))
finally:
    shutil.rmtree(tam, ignore_errors=True)

print()
if loi:
    print(f"ĐỎ — {loi} chỗ lệch. Người dùng gõ tên bình thường mà không xuất được tệp.")
else:
    print("XANH — mọi tên gõ vào đều xuất được, và không tệp nào bị ghi đè.")
sys.exit(1 if loi else 0)
