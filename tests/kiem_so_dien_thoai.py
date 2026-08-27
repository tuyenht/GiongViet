# -*- coding: utf-8 -*-
"""Kiểm cách đọc số điện thoại — theo mục 25 của đặc tả.

Bốn nửa quan trọng ngang nhau:
  1. Nhận diện hoa văn đúng loại (tam hoa, tứ quý, ngũ quý, tiến, gánh…)
  2. Chia nhóm đúng, và KHÔNG nhóm nào quá 4 chữ số
  3. Đọc ra chữ đúng, không đọc thành số lượng
  4. Những thứ KHÔNG phải số điện thoại phải giữ nguyên si

Nửa thứ tư mới là chỗ dễ hỏng: bắt quá tay thì tiền, ngày tháng, năm, số điều
khoản đều bị đọc thành dãy chữ số — nghe rất vô nghĩa.

Chạy:  py giaodien_moi/kiem_so_dien_thoai.py
"""

import io
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8")

from giaodien_moi import so_dien_thoai as sdt
from giaodien_moi import sdt_mau, sdt_nhip

loi = 0


def ok(dk, nhan, them=""):
    global loi
    print(f"  {'ĐẠT ' if dk else 'LỆCH'} {nhan}{'  →  ' + str(them) if them else ''}")
    if not dk:
        loi += 1


def nhom(raw):
    return [s["text"] for s in sdt.phan_tich(raw).get("segments", [])]


def loai_mau(raw):
    return [m["loai"] for m in sdt.phan_tich(raw).get("patterns", [])]


print("--- A. Giới hạn cứng: không nhóm nào quá 4 chữ số ---")
for s in ["0987654321", "0988888123", "0988888832", "0987123456", "0987123123",
          "19006868", "028.2231.7777", "0987.888.888", "+84973356368"]:
    g = nhom(s)
    ok(g and all(len(x) <= sdt_nhip.SO_CHU_SO_TOI_DA for x in g),
       f"{s:16s} → {' | '.join(g)}")

print("\n--- B. Số di động thường: mặc định 4 + 3 + 3 (mục 7) ---")
ok(nhom("0987654321") == ["0987", "654", "321"], "0987654321", " | ".join(nhom("0987654321")))
ok(nhom("0912345678") == ["0912", "345", "678"], "0912345678", " | ".join(nhom("0912345678")))

print("\n--- C. Có dấu ngăn thì ưu tiên giữ (mục 6, 22) ---")
for s, mong in [("0987-654-321", ["0987", "654", "321"]),
                ("0987.654.321", ["0987", "654", "321"]),
                ("0987 654 321", ["0987", "654", "321"]),
                ("028.2231.7777", ["028", "2231", "7777"]),
                ("0962.04.6262", ["0962", "04", "6262"])]:
    ok(nhom(s) == mong, s, " | ".join(nhom(s)))

print("\n--- D. Tam hoa / tứ quý / ngũ quý (mục 10, 11, 12) ---")
ok("TRIPLE_DIGIT" in loai_mau("0987888321"), "0987888321 → có TRIPLE_DIGIT", loai_mau("0987888321")[:2])
# Đếm cho kỹ: 0988881321 có ĐÚNG BỐN số 8, 0988888321 có NĂM.
ok("QUAD_DIGIT" in loai_mau("0988881321"), "0988881321 → có QUAD_DIGIT", loai_mau("0988881321")[:2])
ok("QUINT_DIGIT" in loai_mau("0988888321"), "0988888321 → có QUINT_DIGIT", loai_mau("0988888321")[:2])
# Cụ thể thắng tổng quát (mục 18): 8888 không được gọi là REPEATED_DIGIT
ok(loai_mau("0988881321")[0] == "QUAD_DIGIT",
   "hoa văn mạnh nhất của 0988881321 là QUAD_DIGIT", loai_mau("0988881321")[0])

print("\n--- E. Tứ quý phải nằm TRỌN một nhóm (mục 11) ---")
g = nhom("0988881321")
ok("8888" in g, "0988881321 giữ trọn 8888", " | ".join(g))
g = nhom("0988888321")
ok(all(len(x) <= 4 for x in g) and "".join(g) == "0988888321",
   "0988888321 (ngũ quý) cắt được mà không mất chữ số nào", " | ".join(g))
g = nhom("0987888321")
ok("888" in g, "0987888321 giữ trọn 888", " | ".join(g))

print("\n--- F. Số tiến, khối lặp, số gánh (mục 13, 14, 15) ---")
ok("SEQUENTIAL_ASCENDING" in loai_mau("0987123456"), "0987123456 → số tiến")
ok("SEQUENTIAL_DESCENDING" in loai_mau("0987654321"), "0987654321 → số lùi")
ok(any(t in loai_mau("0987123123") for t in ("REPEATING_BLOCK", "DOUBLE_BLOCK")),
   "0987123123 → khối lặp", loai_mau("0987123123")[:2])
ok(any(t in sdt_mau.phan_tich("1221") for t in []) or
   any(m["loai"] in ("MIRROR", "PALINDROME") for m in sdt_mau.phan_tich("1221")),
   "1221 → số gánh")

print("\n--- G. Ngắt nghỉ: chỉ nhấn khi có hoa văn rõ (mục 21) ---")
seg = sdt.phan_tich("0987654321")["segments"]
ok(all(s["emphasis"] == "NORMAL" for s in seg), "số thường → không nhấn chỗ nào")
seg = {s["text"]: s for s in sdt.phan_tich("0988881321")["segments"]}
ok(seg.get("8888", {}).get("emphasis") == "STRONG", "tứ quý → nhấn STRONG",
   seg.get("8888", {}).get("emphasis"))
seg = {s["text"]: s for s in sdt.phan_tich("0987888321")["segments"]}
ok(seg.get("888", {}).get("emphasis") == "MEDIUM", "tam hoa → nhấn MEDIUM",
   seg.get("888", {}).get("emphasis"))
ok(sdt.phan_tich("0987654321")["segments"][-1]["pause_after"] == "NONE",
   "nhóm cuối không nghỉ thêm")

print("\n--- H. Đọc thành chữ, KHÔNG đọc thành số lượng (mục 24) ---")
for goc, mong in [
    ("028.2231.7777", "Không hai tám, Hai hai ba một, Bảy bảy bảy bảy"),
    ("0962.04.6262", "Không chín sáu hai, Không bốn, Sáu hai sáu hai"),
    ("0973 356 368", "Không chín bảy ba, Ba năm sáu, Ba sáu tám"),
    ("19006868", "Một chín không không, Sáu tám sáu tám"),
    ("19006860", "Một chín không không, Sáu tám sáu không"),
]:
    ra = sdt.doc_so(goc)
    ok(ra == mong, goc, ra if ra != mong else "")
ok("tám tám tám tám" in sdt.doc_so("0988881321").lower(),
   "8888 đọc là tám tám tám tám", sdt.doc_so("0988881321"))
ok("trăm" not in sdt.doc_so("0987654321"), "không có chữ 'trăm' nào")

print("\n--- I. Trong câu, kèm dấu câu ---")
for cau, phai_co in [
    ("Liên hệ tổng đài 1900 6868 để được hỗ trợ.", "Một chín không không"),
    ("Gọi 028.2231.7777, gặp anh Nam.", "Không hai tám"),
    ("Số của tôi: 0973 356 368.", "Không chín bảy ba"),
    ("Hotline 1900 6868!", "Sáu tám sáu tám"),
    ("(0912 345 678)", "Không chín một hai"),
    ("Số quốc tế +84 973 356 368 cũng đọc được.", "Không chín bảy ba"),
]:
    ra = sdt.chuan_hoa(cau)
    ok(phai_co in ra, cau, ra if phai_co not in ra else "")

print("\n--- J. TUYỆT ĐỐI không được đụng vào (mục 25, regression) ---")
for s in [
    "Số tiền ủng hộ 1.600.000 đồng", "Tổng cộng 25.000.000 đồng",
    "Nghỉ từ ngày 31/8/2026 đến 2/9/2026", "Năm 2026 và năm 1975",
    "Lúc 17h00 ngày 28 tháng 8", "Điều 45, khoản 2, điểm a",
    "Bạn đã đọc 100.000/100.000 ký tự", "Gói làm mới sau 12 ngày",
    "Tổ 7, khu phố 3", "Giá 2,5 triệu đồng",
    "Phòng 0912 không phải số", "Mã số thuế 0301234567890123",
    "Dãy 123456789 không phải số điện thoại",
    "Dãy 1234567890 không phải số điện thoại",
    "Dãy 1234567 không phải số điện thoại",
]:
    ra = sdt.chuan_hoa(s)
    ok(ra == s, s, "" if ra == s else "BỊ ĐỔI → " + ra)

print("\n--- K. Tầng nhận dạng đứng độc lập với tầng hoa văn (mục 26) ---")
ok(sdt.la_so_dien_thoai("0987654321"), "số thường vẫn hợp lệ dù không hoa văn")
ok(sdt.la_so_dien_thoai("0988888888"), "số nhiều hoa văn cũng hợp lệ")
ok(not sdt.la_so_dien_thoai("1234567890"), "dãy không đúng đầu số thì không phải")
ok(sdt.phan_loai("19006868") == "HOTLINE", "phân loại tổng đài", sdt.phan_loai("19006868"))
ok(sdt.phan_loai("0282231777") == "LANDLINE", "phân loại cố định", sdt.phan_loai("0282231777"))
ok(sdt.phan_loai("0987654321") == "MOBILE", "phân loại di động")

print("\n--- L. Không làm hỏng văn bản không có số ---")
for s in ["Kính gửi toàn thể cán bộ, nhân viên.", "", "   ", "THÔNG BÁO NGHỈ LỄ"]:
    ok(sdt.chuan_hoa(s) == s, repr(s))

print(f"\n{'XANH — khớp hết' if loi == 0 else f'ĐỎ — {loi} chỗ lệch'}")
sys.exit(1 if loi else 0)
