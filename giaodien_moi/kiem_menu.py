# -*- coding: utf-8 -*-
"""Canh menu: KHONG duoc bay muc nao bam vao ma khong ra gi.

VI SAO CO TEP NAY: audit 13/8 dem duoc 15 muc menu chet. Ma xu ly la
`f ? f() : dat(dongHetMenu(S))` — khong tim thay lenh thi lang le dong menu,
khong bao loi, khong ghi log. Nguoi lon tuoi bam hai ba lan roi tuong may
hong. Day dung la thu KPI so 1 cua du an cam: "KHONG bay nut gia".

Suyt nua con go nham "The cam xuc": phep do dau tien tim chuoi phim tat
'Alt+1' nen bao no khong co phim tat, trong khi datThe() la chuc nang that va
Alt+1..3 van chay. Bai hoc: do bang TEN HAM duoc goi, dung do bang nhan chu.
"""
import io
import re
import sys
from pathlib import Path

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8")

G = Path(r"C:\Projects\DocCongDuc")
JS = (G / "ui-moi" / "giao-dien.js").read_text(encoding="utf-8")

loi = 0
def ok(dk, nhan, them=""):
    global loi
    print(f"  {'ĐẠT ' if dk else 'LỆCH'} {nhan}{'  →  ' + str(them) if them else ''}")
    if not dk:
        loi += 1


i = JS.find("const MENUS")
khoi_menu = JS[i: JS.find("];", i) + 2]
muc = re.findall(r"\['([^']+)',\s*'([^']*)'\]", khoi_menu)

j = JS.find("const LENH = {")
khoi_lenh = JS[j: JS.find("\n};", j)]
co_lenh = set(re.findall(r"^  '([^']+)'", khoi_lenh, re.M))

print("--- A. MOI muc menu phai co lenh that ---")
chet = [n for n, _ in muc if n not in co_lenh]
ok(not chet, f"{len(muc)} muc menu deu noi vao mot lenh", chet or "khong sot cai nao")

print("\n--- B. Khong lenh nao tro toi ham rong ---")
for ten, _ in muc:
    # Lay den dau muc KE TIEP chu khong cat mot dong: nhieu lenh la ham nhieu
    # dong, than nam o dong sau. Cat mot dong roi ket luan "rong" la bao lech
    # oan — da bao lech that mot lan voi 'Nghe mau giong'.
    m = re.search(r"^  '" + re.escape(ten) + r"':\s*(.*?)(?=\n  '|\Z)",
                  khoi_lenh, re.M | re.S)
    than = re.sub(r"\s+", " ", m.group(1) if m else "").strip()
    ok(than.replace(" ", "") not in ("", "()=>{}", "()=>{},"),
       f"'{ten}' co than lenh", than[:44])

print("\n--- C. Nhanh du phong van con, phong khi them muc moi ma quen ---")
ok("f ? f() : dat(dongHetMenu(S))" in JS,
   "bam muc la de -> van dong menu chu khong vo giao dien")

print("\n--- D. The cam xuc: giu lai vi no LA chuc nang that ---")
ok("datThe" in JS, "datThe con duoc goi")
ok("'Thẻ cảm xúc'" in khoi_lenh, "co lenh mo menu the")
ok("tags: true" in JS, "lenh ay BAT S.tags — truoc day khong noi nao bat len")
ok("S.tags ? veMenuThe()" in JS, "S.tags dung de ve menu the")

print("\n--- E. Sau muc da go thi phai go HAN, khong con nam trong menu ---")
for ten in ["Hoàn tác", "Làm lại", "Cắt", "Sao chép", "Khoảng lặng 1 giây",
            "Ngắt đoạn"]:
    ok(ten not in [n for n, _ in muc], f"'{ten}' khong con trong menu")

print("\n--- F. Ba muc Tro giup mo duoc hop thoai that ---")
for ten in ["Hướng dẫn nhanh", "Danh sách phím tắt", "Giới thiệu Giọng Việt"]:
    ok(ten in co_lenh, f"'{ten}' co lenh")
ok("function moHopTin" in JS, "co ham dung hop thong tin")
ok("veHopTin" in JS, "lop noi co ve hop thong tin")
ok("hopTin: null" in (G / "ui-moi" / "trang-thai.js").read_text(encoding="utf-8"),
   "trang thai co khoa hopTin")

print("\n--- G. Luu: phai di toi duong ghi tep that ---")
ok("'Lưu'" in khoi_lenh, "co lenh Luu")
ok("moi_luu_van_ban" in JS, "JS goi sang Python de ghi")
cn = (G / "giaodien_moi" / "cau_noi_moi.py").read_text(encoding="utf-8")
ok("def moi_luu_van_ban" in cn, "Python co cua nhan")
ok("luu_tep.luu(" in cn, "dung luu_tep — khong de ban goc cua nguoi dung")
ok("da_la_ban_cua_ta=bool(cu)" in cn,
   "lan luu sau ghi de dung ban cua minh, khong de them so moi")

print("\n" + ("XANH — khớp hết" if not loi else f"ĐỎ — {loi} chỗ lệch"))
sys.exit(1 if loi else 0)
