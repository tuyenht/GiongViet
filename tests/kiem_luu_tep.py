# -*- coding: utf-8 -*-
"""Kiem duong luu Ctrl+S. Chay HOAN TOAN tren thu muc tam, khong dung tep that."""
import io, os, shutil, sys, tempfile, time
from pathlib import Path

# Goc du an, tinh tu chinh vi tri tep nay. KHONG viet cung duong dan:
# kho da len GitHub, ai tai ve cho khac la vo het bo kiem.
_GOC = str(Path(__file__).resolve().parent.parent)
sys.path.insert(0, _GOC)
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8")
from giaodien_moi import luu_tep as L

T = Path(tempfile.gettempdir()) / "gd-kiem-luu"
if T.exists():
    shutil.rmtree(T)
T.mkdir(parents=True)

loi = 0
def ok(dk, nhan, them=""):
    global loi
    print(f"  {'ĐẠT ' if dk else 'LỆCH'} {nhan}{'  →  ' + str(them) if them else ''}")
    if not dk: loi += 1

print("--- A. Chưa có tệp thì ghi thẳng ---")
p = L.luu(T / "thongbao.txt", "bản đầu")
ok(p.name == "thongbao.txt", "ghi đúng tên gốc", p.name)

print("\n--- B. Đã có tệp thì né sang bản mới, KHÔNG đụng bản gốc ---")
goc = T / "thongbao.txt"
noi_goc = goc.read_text(encoding="utf-8")
mt_goc = goc.stat().st_mtime_ns
time.sleep(0.01)
p1 = L.luu(goc, "bản đã sửa lần 1")
ok(p1.name == "thongbao (1).txt", "đẻ ra 'thongbao (1).txt'", p1.name)
ok(goc.read_text(encoding="utf-8") == noi_goc, "nội dung bản gốc còn nguyên", repr(goc.read_text(encoding='utf-8')))
ok(goc.stat().st_mtime_ns == mt_goc, "bản gốc không bị chạm cả mtime")

print("\n--- C. Đã có (1) thì ra (2) ---")
p2 = L.luu(goc, "bản đã sửa lần khác")
ok(p2.name == "thongbao (2).txt", "đẻ ra (2)", p2.name)

print("\n--- D. Các lần lưu SAU ghi đè chính bản của mình ---")
for i in range(3):
    L.luu(p1, f"sửa tiếp lần {i}", da_la_ban_cua_ta=True)
ds = sorted(x.name for x in T.glob("thongbao*"))
ok(ds == ["thongbao (1).txt", "thongbao (2).txt", "thongbao.txt"],
   "lưu 3 lần nữa KHÔNG đẻ thêm tệp", ds)
ok(p1.read_text(encoding="utf-8") == "sửa tiếp lần 2", "nội dung là bản mới nhất")

print("\n--- E. Không đẻ 'tên (1) (1)' ---")
p3 = L.luu(p1, "x")     # p1 = "thongbao (1).txt", chua danh dau la cua ta
ok(p3.name == "thongbao (3).txt", "từ 'thongbao (1)' ra 'thongbao (3)'", p3.name)

print("\n--- F. Không sót tệp tạm ---")
rac = list(T.glob("*.tam"))
ok(not rac, "0 tệp .tam", [x.name for x in rac])

print("\n--- G. Tên tiếng Việt có dấu và tên không phần mở rộng ---")
v = L.luu(T / "Thông báo nghỉ lễ.txt", "a"); L.luu(T / "Thông báo nghỉ lễ.txt", "b")
v2 = L.luu(T / "Thông báo nghỉ lễ.txt", "c")
ok(v2.name == "Thông báo nghỉ lễ (2).txt", "tên có dấu", v2.name)
k = L.luu(T / "khongduoi", "a"); k2 = L.luu(T / "khongduoi", "b")
ok(k2.name == "khongduoi (1)", "tên không phần mở rộng", k2.name)

print("\n--- H. Thư mục chưa có thì tự tạo ---")
sau = L.luu(T / "moi" / "sau" / "a.txt", "x")
ok(sau.exists(), "tạo được thư mục lồng nhau", str(sau.relative_to(T)))

print("\n--- I. Thư mục mặc định khi không biết tệp nằm đâu ---")
tm = L.thu_muc_mac_dinh()
ok(tm.name == "GiongViet" and tm.parent.name == "Documents", r"Documents\GiongViet", str(tm))
ok(not tm.exists() or tm.is_dir(), "không tạo bừa lúc chỉ hỏi đường dẫn")

print("\n--- J. Toàn bộ tệp sinh ra ---")
for x in sorted(T.rglob("*")):
    if x.is_file():
        print(f"     {x.relative_to(T)}  →  {x.read_text(encoding='utf-8')!r}")

shutil.rmtree(T)
print(f"\n{'XANH — khớp hết' if loi == 0 else f'ĐỎ — {loi} chỗ lệch'}")
sys.exit(1 if loi else 0)
