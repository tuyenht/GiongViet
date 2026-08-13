# -*- coding: utf-8 -*-
"""Canh duong keo mep va do cua so. Chi doc ma nguon, khong mo cua so nao.

VI SAO CO TEP NAY — da hong that va khong ai thay:

Keo mep viet xong tu phien truoc, ghi la DA LAM, nhung chua bao gio keo duoc.
Ma trong khong co gi sai; cai sai nam o cho khong nhin ra bang mat: pywebview
chay js_api tren luong RIENG (do duoc: 35884, luong UI la 26696), ma
ReleaseCapture() chi giai phong chuot cua chinh luong goi no.

Khong the tu dong keo chuot de kiem, nen bai nay canh nhung dieu kien da
chung minh la CAN: co gan luong, co go luong, dung SendMessage, va hai danh
sach mep hai ben JS/Python phai khop nhau.
"""
import io
import re
import sys
from pathlib import Path


sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8")

# Goc du an, tinh tu chinh vi tri tep nay. KHONG viet cung duong dan:
# kho da len GitHub, ai tai ve cho khac la vo het bo kiem.
_GOC = str(Path(__file__).resolve().parent.parent)
G = Path(_GOC)
PY = (G / "giaodien_moi" / "cau_noi_moi.py").read_text(encoding="utf-8")
JS = (G / "ui-moi" / "giao-dien.js").read_text(encoding="utf-8")
CSS = (G / "ui-moi" / "man-hinh-chinh.css").read_text(encoding="utf-8")
CHINH = (G / "GiongViet.py").read_text(encoding="utf-8")

loi = 0
def ok(dk, nhan, them=""):
    global loi
    print(f"  {'ĐẠT ' if dk else 'LỆCH'} {nhan}{'  →  ' + str(them) if them else ''}")
    if not dk:
        loi += 1


than_keo = PY[PY.find("def moi_keo_vien"):]
than_keo = than_keo[:than_keo.find("\n    def ", 10)]

# BO DOCSTRING ra truoc khi soi thu tu cac lenh. Docstring cua ham nay giai
# thich vi sao ReleaseCapture mot minh la vo ich, nen no NHAC hai ten ham theo
# thu tu nguoc voi thu tu ma code goi. Doc ca van xuoi vao thi phep kiem bao
# lech trong khi code dung — chinh no da bao lech that mot lan.
_dau = than_keo.find('"""')
_cuoi = than_keo.find('"""', _dau + 3)
docstring = than_keo[_dau:_cuoi + 3] if _dau >= 0 < _cuoi else ""
than_keo = than_keo.replace(docstring, "") if docstring else than_keo

print("--- A. Ten cua so: mot nguon duy nhat, khop voi create_window ---")
m = re.search(r'TEN_CUA_SO\s*=\s*"([^"]+)"', PY)
ok(bool(m), "co hang TEN_CUA_SO")
ten = m.group(1) if m else ""
m2 = re.search(r'create_window\(\s*\n?\s*"([^"]+)"', CHINH)
ok(bool(m2), "doc duoc ten trong GiongViet.create_window")
ok(bool(m2) and ten == m2.group(1),
   "hai noi dat CUNG mot ten", f"{ten!r} vs {m2.group(1)!r}" if m2 else ten)
ok(PY.count("FindWindowW") == 1,
   "chi MOT cho go FindWindowW (trong _tim_hwnd)", PY.count("FindWindowW"))
ok('FindWindowW(None, "' + ten + '")' not in PY,
   "khong con cho nao viet cung ten cua so vao giua ma")

print("\n--- B. Keo mep PHAI gan luong truoc, khong thi ReleaseCapture vo hieu ---")
ok("AttachThreadInput" in than_keo, "co goi AttachThreadInput")
ok(than_keo.count("AttachThreadInput(") == 2,
   "gan roi PHAI go — dung hai lan", than_keo.count("AttachThreadInput("))
ok(re.search(r"AttachThreadInput\([^)]*True\)", than_keo) is not None, "co lan gan (True)")
ok(re.search(r"AttachThreadInput\([^)]*False\)", than_keo) is not None, "co lan go (False)")
sau_finally = than_keo.split("finally:")[-1] if "finally:" in than_keo else ""
ok(re.search(r"AttachThreadInput\([^)]*False\)", sau_finally) is not None,
   "lan go nam trong finally — luong chet giua chung van khong dinh input")
ok('"""' not in than_keo, "phep kiem nay dang soi CODE, da bo docstring")
ok("ReleaseCapture" in than_keo, "van goi ReleaseCapture")
i_gan = than_keo.find("AttachThreadInput")
i_tha = than_keo.find("ReleaseCapture")
ok(0 < i_gan < i_tha, "gan luong TRUOC khi tha chuot, khong nguoc lai")

print("\n--- C. SendMessage chu khong Post: phai vao vong keo luc con gan ---")
ok("SendMessageW(" in than_keo, "dung SendMessageW")
ok("PostMessageW(" not in than_keo,
   "KHONG con PostMessageW — no tra ve ngay, go luong xong la vong keo mat chuot")
ok("0x00A1" in than_keo, "gui dung WM_NCLBUTTONDOWN (0x00A1)")

print("\n--- D. Bang tam huong: dung ma hit-test cua Windows ---")
CHUAN = {"trai": 10, "phai": 11, "tren": 12, "trentrai": 13,
         "trenphai": 14, "duoi": 15, "duoitrai": 16, "duoiphai": 17}
bang = dict(re.findall(r'"(\w+)":\s*(\d+)', PY[PY.find("VIEN = {"):PY.find("}", PY.find("VIEN = {"))]))
bang = {k: int(v) for k, v in bang.items()}
ok(bang == CHUAN, "tam huong dung ma HTLEFT..HTBOTTOMRIGHT", bang)

print("\n--- E. Hai ben JS va Python phai khop tung ten mep ---")
mjs = re.search(r"VIEN_KEO\s*=\s*\[(.*?)\]", JS, re.S)
ds_js = set(re.findall(r"'(\w+)'", mjs.group(1))) if mjs else set()
ok(ds_js == set(CHUAN), "JS liet ke dung tam mep ay", sorted(ds_js))
ok("veVienKeo()" in JS.replace("const veVienKeo", ""),
   "veVienKeo() co duoc GOI, khong chi dinh nghia")
ok("data-vien" in JS and "mousedown" in JS, "bat o mousedown, khong phai click")
ok("moi_keo_vien" in JS, "co goi sang Python")

print("\n--- F. CSS: du tam dai va phai noi len tren cung ---")
for v in CHUAN:
    ok(f".vien--{v}" in CSS, f"co lop .vien--{v}")
ok(re.search(r"\.vien\s*\{[^}]*position:\s*fixed", CSS) is not None,
   "dai mep dung position:fixed")
m3 = re.search(r"\.vien\s*\{[^}]*z-index:\s*(\d+)", CSS)
ok(bool(m3) and int(m3.group(1)) >= 100,
   "z-index du cao de khong bi thu khac phu len", m3.group(1) if m3 else "khong co")

print("\n" + ("XANH — khớp hết" if not loi else f"ĐỎ — {loi} chỗ lệch"))
sys.exit(1 if loi else 0)
