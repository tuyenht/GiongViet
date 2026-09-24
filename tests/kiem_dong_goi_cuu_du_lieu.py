# -*- coding: utf-8 -*-
"""BAI CANH (xanh = tot): DongGoi.bat phai cuu du lieu nguoi dung TRUOC khi xoa.

VI SAO CO BAI NAY

Buoc 4 cua DongGoi.bat go junction bang mot vong:

    for %%L in (ffmpeg vieneu_models giong_rieng bin models data) do (
        if exist "%DICH%\\%%L" rmdir /s /q "%DICH%\\%%L" 2>nul
    )

`data` nam trong danh sach do, va giongviet.db - NOI THAT SU giu thiet lap sau
khi gom - nam ngay trong `data`. Da do bang thuc nghiem (07/09/2026):

  · rmdir /s /q tren thu muc chua junction XOA tep thuong ben trong
    -> giongviet.db bien mat.
  · rmdir /s /q KHONG di theo junction
    -> data\\giong_rieng chi mat cai junction, mau giong o thu muc goc con nguyen.

Nen hau qua dung muc la: MAT THIET LAP, khong mat giong rieng.

Ban truoc con co mot vong cuu o cuoi tep di tim %CU%\\data\\giongviet.db - nhung
data da bi xoa tu truoc khi doi ten sang %CU%, nen khong con gi de cuu.

BAI NAY CANH BA DIEU, theo dung thu tu chung phai xay ra:
  A. Co khoi CUU chay TRUOC vong go junction.
  B. Khoi cuu bat het cac duoi tep giu thiet lap (.db .txt .json .ini).
  C. Co khoi TRA LAI, va no chay TRUOC doan chep tu %ROOT% - de ban cua
     nguoi dung thang ban cua thu muc du an.

Bai chi DOC DongGoi.bat. Khong chay build, khong cham mot byte du lieu nguoi dung.
"""
import io
import re
import sys
from pathlib import Path

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")

GOC = Path(__file__).resolve().parent.parent
BAT = GOC / "DongGoi.bat"

loi = 0


def ok(dieu_kien, nhan, them=""):
    global loi
    print(f"  {'ĐẠT ' if dieu_kien else 'LỆCH'} {nhan}" + (f"  →  {them}" if them else ""))
    if not dieu_kien:
        loi += 1


print(f"Đọc: {BAT}")
nguon = BAT.read_text(encoding="utf-8", errors="replace")


def dong_cua(mau):
    m = re.search(mau, nguon, re.I)
    return nguon[:m.start()].count("\n") + 1 if m else None


d_cuu = dong_cua(r'if exist "%DICH%\\data"\s*\(\s*\r?\n\s*if not exist "%CUU%" mkdir')
d_go = dong_cua(r'for %%L in \(ffmpeg')
d_tra = dong_cua(r'if exist "%CUU%"\s*\(\s*\r?\n\s*for %%F in \("%CUU%')
d_chep_root = dong_cua(r'if exist "%ROOT%data\\giongviet\.db"')

print("\n--- A. Khối CỨU phải chạy TRƯỚC vòng gỡ junction ---")
ok(d_cuu is not None, "có khối cứu dữ liệu từ %DICH%\\data",
   f"dòng {d_cuu}" if d_cuu else "KHÔNG CÓ — build là mất thiết lập người dùng")
ok(d_go is not None, "vẫn còn vòng gỡ junction", f"dòng {d_go}" if d_go else "")
if d_cuu and d_go:
    ok(d_cuu < d_go, "cứu TRƯỚC rồi mới xoá",
       f"cứu ở dòng {d_cuu}, xoá ở dòng {d_go}")

print("\n--- B. Khối cứu bắt đủ các đuôi tệp giữ thiết lập ---")
m = re.search(r'for %%F in \(([^)]*%DICH%\\data[^)]*)\)', nguon, re.I)
ds_cuu = m.group(1) if m else ""
if ds_cuu:
    print(f"      glob cứu: {ds_cuu.strip()}")
for duoi, vi_sao in (("*.db", "giongviet.db — nơi thật chứa thiết lập sau khi gom"),
                     ("*.txt", "congduc.txt — danh sách của người dùng"),
                     ("*.json", "hồ sơ, giao diện"),
                     ("*.ini", "cấu hình bản trước khi gom")):
    ok(duoi in ds_cuu, f"cứu {duoi}", vi_sao if duoi not in ds_cuu else "")

print("\n--- C. Khối TRẢ LẠI phải chạy TRƯỚC đoạn chép từ %ROOT% ---")
ok(d_tra is not None, "có khối trả lại dữ liệu đã cứu",
   f"dòng {d_tra}" if d_tra else "cứu rồi mà không trả thì cũng như không")
if d_tra and d_chep_root:
    ok(d_tra < d_chep_root,
       "trả lại TRƯỚC khi chép bản của thư mục dự án",
       f"trả ở dòng {d_tra}, chép ở dòng {d_chep_root} — các lệnh chép đều có "
       '"if not exist" nên bản người dùng thắng')

print("\n--- D. Thư mục cứu không bị xoá ngay trong cùng lượt build ---")
ok(not re.search(r'rmdir /s /q "%CUU%"[^\r\n]*\r?\n[^\r\n]*echo\s+BUILD', nguon, re.I),
   "giữ %CUU% lại sau khi build xong — còn đường lui nếu bản mới hỏng")

print()
if loi:
    print(f"ĐỎ — {loi} chỗ lệch. KHÔNG chạy DongGoi.bat cho tới khi vá xong:")
    print("build lại sẽ xoá thiết lập người dùng mà không báo một lời nào.")
else:
    print("XANH — DongGoi.bat cứu dữ liệu người dùng đúng thứ tự.")
sys.exit(1 if loi else 0)
