# -*- coding: utf-8 -*-
"""Canh viec DongGoi.bat cuu du lieu nguoi dung khi hoan doi thu muc.

VI SAO CO BAI NAY

Bo build khong xoa ban cu — no doi ten %DICH% thanh %DICH%_cu roi moi dua ban
moi ra, va co han mot vong cuu du lieu nguoi dung tu ban cu sang ban moi. Nhung
vong cuu ay chi bat BA kieu tep:

    for %%F in ("%CU%\\*.json" "%CU%\\*.ini" "%CU%\\*.txt")

Khong co *.db, va glob khong di vao thu muc con. Trong khi do:

  - Sau khi gom, MOI lenh ghi cau hinh di vao giongviet.db chu khong vao tep
    .ini roi nua (DocCongDuc.py:96-100 ghi_tep_cau_hinh -> kho_cau_hinh.ghi).
  - Nen tep .ini roi o goc du an dung yen tu luc gom, con thiet lap that da
    chay tiep trong kho.

Hau qua: build lai mot lan la thiet lap nguoi dung lang le lui ve moc cua cac
tep .ini roi; build lan hai thi %CU% bi rmdir /s /q xoa sach, mat han.

Chu du an da biet va CHON hoan viec va (19/8). Bai nay khong sua gi — no chi
lam cho rui ro ay KEU TO thay vi nam im: bat cu ai chay bo kiem truoc khi build
deu thay ngay.

BAI NAY DO: KHONG chay build, KHONG cham du lieu nguoi dung, chi DOC DongGoi.bat.
"""
import io
import os
import re
import sys
from pathlib import Path

_GOC = Path(os.environ.get("GIONGVIET_GOC")
            or Path(__file__).resolve().parent.parent)
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8",
                              line_buffering=True)

loi = 0


def ok(dk, nhan, them=""):
    global loi
    print(f"  {'ĐẠT ' if dk else 'LỆCH'} {nhan}{'  →  ' + str(them) if them else ''}")
    if not dk:
        loi += 1


BAT = _GOC / "DongGoi.bat"
print(f"Đọc: {BAT}")
if not BAT.is_file():
    sys.exit("Không thấy DongGoi.bat — bài kiểm này cần nó.")

nguon = BAT.read_text(encoding="utf-8", errors="replace")

# --- A. Vong cuu du lieu con do khong -----------------------------------------
print("\n--- A. Vòng cứu dữ liệu từ bản cũ vẫn còn ---")
mo = re.search(r'for\s+%%F\s+in\s+\(([^)]*%CU%[^)]*)\)', nguon, re.I)
ok(mo is not None, "vẫn còn vòng cứu dữ liệu từ %CU%")
danh_sach = mo.group(1) if mo else ""
if mo:
    print(f"      glob hiện tại: {danh_sach.strip()}")

# --- B. Cac kieu tep duoc cuu --------------------------------------------------
print("\n--- B. Glob cứu có bắt hết những thứ giữ thiết lập không ---")
for duoi in ("*.json", "*.ini", "*.txt"):
    ok(duoi in danh_sach, f"cứu {duoi}")

ok("*.db" in danh_sach,
   "cứu *.db  ← giongviet.db là NƠI THẬT chứa thiết lập sau khi gom",
   "CHƯA CÓ — build lại là thiết lập lùi về mốc các tệp .ini rời")

# --- C. Thu muc con -------------------------------------------------------------
print("\n--- C. Thư mục con có được cứu không ---")
cuu_thu_muc = bool(re.search(r'sao-luu-cu', nguon, re.I))
ok(cuu_thu_muc,
   "cứu thư mục sao-luu-cu/  ← ảnh chụp cấu hình đọc được bằng Notepad",
   "CHƯA CÓ — glob không đệ quy nên cả thư mục nằm lại %CU% rồi bị xoá")

# --- D. Ban cu co bi xoa o lan build sau khong ----------------------------------
print("\n--- D. Bản cũ bị xoá ở lần build kế tiếp ---")
ok(bool(re.search(r'rmdir\s+/s\s+/q\s+"%CU%"', nguon, re.I)),
   "có lệnh rmdir /s /q \"%CU%\" — nên thứ không được cứu sẽ mất sau LẦN BUILD THỨ HAI",
   "đây là lý do vá sớm rẻ hơn vá muộn")

# --- E. Nhac lai cach va -------------------------------------------------------
print("\n--- E. Cách vá (chưa làm — chủ dự án đã chọn hoãn 19/8) ---")
print("      1. Thêm \"%CU%\\*.db\" vào glob ở vòng cứu.")
print("      2. Chép cả thư mục: if exist \"%CU%\\sao-luu-cu\" xcopy /E /I /Y ...")
print("      Đây là ĐƯỜNG ĐÓNG GÓI — việc hội đồng, không tự sửa.")

print("\n" + "=" * 62)
if loi:
    print(f"ĐỎ — {loi} chỗ lệch.")
    print("KHÔNG chạy DongGoi.bat cho tới khi vá xong: build lại sẽ làm")
    print("thiết lập người dùng lùi về mốc cũ mà không báo một lời nào.")
else:
    print("XANH — bộ build cứu đủ dữ liệu người dùng.")
sys.exit(1 if loi else 0)
