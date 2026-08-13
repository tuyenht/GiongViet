# -*- coding: utf-8 -*-
"""Kiem hoso-v2.json. Chay hoan toan tren thu muc tam, khong dung tep that."""
import io
import json
import shutil
import sys
import tempfile
from pathlib import Path

sys.path.insert(0, r"C:\Projects\DocCongDuc")
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8")

from giaodien_moi import ho_so_v2 as H

T = Path(tempfile.gettempdir()) / "gd-kiem-hoso-v2"
if T.exists():
    shutil.rmtree(T)
T.mkdir(parents=True)
H.TEP = T / "hoso-v2.json"

loi = 0


def ok(dk, nhan, them=""):
    global loi
    print(f"  {'ĐẠT ' if dk else 'LỆCH'} {nhan}{'  →  ' + str(them) if them else ''}")
    if not dk:
        loi += 1


MAU = {
    "dangDung": 1, "theme": "toi",
    "the": {"a.txt": {"3": "[cười]"}},
    "duongDan": {"a.txt": r"C:\thu\a.txt"},
    "hoSo": [
        {"ma": "h1", "ten": "Bài viết", "giong": "g1",
         "chinh": {"tocDo": 0, "caoDo": 0, "amLuong": 100},
         "tep": ["a.txt"], "dangXem": 0},
        {"ma": "h2", "ten": "Sách nói", "giong": "g2",
         "chinh": {"tocDo": -10, "caoDo": 2, "amLuong": 90},
         "tep": ["b.txt", ""], "dangXem": 1},
    ],
}

print("--- A. Chua co tep thi doc ra None, khong phai loi ---")
ok(H.doc() is None, "chua luu lan nao -> None")

print("\n--- B. Luu roi doc lai y nguyen ---")
ok(H.luu(MAU) is True, "luu tra True")
ok(H.TEP.exists(), "tep hoso-v2.json co that")
d = H.doc()
ok(d is not None and len(d["hoSo"]) == 2, "doc lai 2 ho so")
ok(d["hoSo"][1]["ten"] == "Sách nói", "ten tieng Viet con dau", d["hoSo"][1]["ten"])
ok(d["hoSo"][1]["chinh"]["amLuong"] == 90, "thanh chinh giu nguyen")
ok(d["hoSo"][1]["tep"] == ["b.txt", ""], "danh sach tab giu nguyen", d["hoSo"][1]["tep"])
ok(d["dangDung"] == 1 and d["theme"] == "toi", "ho so dang dung + giao dien toi")
ok(d["the"]["a.txt"]["3"] == "[cười]", "the cam xuc con nguyen")
ok(d["duongDan"]["a.txt"] == r"C:\thu\a.txt", "duong dan tep con nguyen")

print("\n--- C. Ghi qua tep tam, khong bo lai rac ---")
H.luu(MAU)
rac = list(T.glob("*.tam"))
ok(not rac, "0 tep .tam", [x.name for x in rac])

print("\n--- D. Du lieu ban tu giao dien phai bi lam sach ---")
ban = {
    "dangDung": 99, "theme": "mau hong",
    "hoSo": [{"ma": None, "ten": "", "giong": 123, "chinh": {"tocDo": "nhanh"},
              "tep": [], "dangXem": 77}],
    "the": {"x.txt": {"khong-phai-so": "a", "5": "[ho]"}},
    "duongDan": {"x.txt": 42},
}
s = H.lam_sach(ban)
ok(s["dangDung"] == 0, "dangDung vuot so ho so -> ve 0", s["dangDung"])
ok(s["theme"] == "sang", "theme la khong hop le -> sang", s["theme"])
ok(s["hoSo"][0]["ten"] == "Hồ sơ", "ten rong -> ten mac dinh", s["hoSo"][0]["ten"])
ok(s["hoSo"][0]["tep"] == [""], "khong co tab -> mot tab chua dat ten")
ok(s["hoSo"][0]["dangXem"] == 0, "dangXem vuot so tab -> 0", s["hoSo"][0]["dangXem"])
ok(s["hoSo"][0]["chinh"]["tocDo"] == 0, "toc do khong phai so -> 0")
ok(s["the"]["x.txt"] == {"5": "[ho]"}, "the co khoa khong phai so bi bo", s["the"]["x.txt"])
ok(s["duongDan"] == {}, "duong dan khong phai chuoi bi bo", s["duongDan"])

print("\n--- E. Cat ve khoang cho phep ---")
s2 = H.lam_sach({"hoSo": [{"ma": "a", "ten": "T", "tep": ["x"],
                           "chinh": {"tocDo": 9999, "caoDo": -9999, "amLuong": 9999}}]})
c = s2["hoSo"][0]["chinh"]
# Bien SUA ngay 13/8: truoc do bang nay ghi tocDo toi 50 va amLuong toi 200,
# lech han voi thanh truot (TRUOT trong giao-dien.js: -50..100 va 0..100) va
# voi bo loc am_thanh_loc. Hau qua: keo Toc do het co sang phai thi ho so cat
# ve 50, nua thanh ben phai khong doi gi. Ba noi gio phai khop nhau.
ok(c["tocDo"] == 100 and c["caoDo"] == -12 and c["amLuong"] == 100,
   "ba thanh bi cat ve bien", c)

print("\n--- F. Tep hong thi coi nhu chua co, KHONG lam chuong trinh chet ---")
H.TEP.write_text("{ day khong phai json", encoding="utf-8")
ok(H.doc() is None, "json hong -> None")
H.TEP.write_text('{"hoSo": []}', encoding="utf-8")
ok(H.doc() is None, "khong co ho so nao -> None")
H.TEP.write_text('["mot", "mang"]', encoding="utf-8")
ok(H.doc() is None, "kieu du lieu sai -> None")

print("\n--- G. Khong luu ho so rong ---")
ok(H.luu({"hoSo": []}) is False, "khong ghi de tep cu bang du lieu rong")

print("\n--- H. Phien ban duoc ghi de sau nay doi dinh dang con biet duong ---")
H.luu(MAU)
raw = json.loads(H.TEP.read_text(encoding="utf-8"))
ok(raw["phienBan"] == H.PHIEN_BAN, "co so phien ban", raw["phienBan"])

print("\n--- I. Duong dan that phai la hoso-v2.json, KHONG phai hoso.json ---")
# H.TEP da bi tro sang thu muc tam o dau bai, nen doc lai tu ma nguon.
that = Path(r"C:\Projects\DocCongDuc\giaodien_moi\ho_so_v2.py").read_text(encoding="utf-8")
ok('"hoso-v2.json"' in that, "ma nguon tro toi hoso-v2.json")
ok('"hoso.json"' not in that, "ma nguon KHONG nhac toi hoso.json cua ban cu")

shutil.rmtree(T, ignore_errors=True)
print(f"\n{'XANH — khớp hết' if loi == 0 else f'ĐỎ — {loi} chỗ lệch'}")
sys.exit(1 if loi else 0)
