# -*- coding: utf-8 -*-
"""Kiem the cam xuc di HET duong tu giao dien xuong mo hinh.

Chu du an bam thu bao "the cam xuc chua thay co tac dung" - dung, vi thieu hai
mat xich: giao dien khong gui the kem doan, va chuan_hoa_van_ban boc ngoac
vuong nen the chet truoc khi toi VieNeu.

Bo kiem nay canh CA DUONG DAY chu khong tung khuc: dung playlist that roi soi
chuoi `text` cuoi cung, va dua chinh chuoi ay qua phonemize cua VieNeu de xem
co ra token cam xuc khong. Tung khuc xanh ma duong day dut thi van vo hinh.

Khong mo cua so, khong phat tieng, khong cham du lieu nguoi dung.
"""
import io
import re
import sys
import tempfile
from pathlib import Path

_GOC = str(Path(__file__).resolve().parent.parent)
sys.path.insert(0, _GOC)
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8",
                              line_buffering=True)

from giaodien import nhat_ky  # noqa: E402
nhat_ky.TEP_LOG = Path(tempfile.gettempdir()) / "gd-kiem-the-loi.log"

import DocCongDuc as engine  # noqa: E402
from giaodien_moi import khoa_du_lieu  # noqa: E402
from giaodien_moi.cau_noi_moi import ApiMoi, THE_CAM_XUC  # noqa: E402

loi = 0


def ok(dk, nhan, them=""):
    global loi
    print(f"  {'ĐẠT ' if dk else 'LỆCH'} {nhan}{'  →  ' + str(them) if them else ''}")
    if not dk:
        loi += 1


print("--- A. Ba the phai khop dung thu VieNeu hieu ---")
try:
    from vieneu_utils.phonemize_text import phonemize_text_with_emotions as ph
    co_vieneu = True
except Exception as e:                                  # pragma: no cover
    co_vieneu = False
    print(f"  (bo qua phan phonemize: {e})")

ok(THE_CAM_XUC == ("[cười]", "[thở dài]", "[hắng giọng]"),
   "danh sach the dung ba chuoi VieNeu nhan", THE_CAM_XUC)

# Danh sach ben giao dien phai khop, khong thi bam the o man hinh ra mot dang
# ma Python loc bo mot dang.
js_path = (Path(_GOC) / "src" / "web" / "giao-dien.js") if (Path(_GOC) / "src" / "web" / "giao-dien.js").exists() else (Path(_GOC) / "ui-moi" / "giao-dien.js")
js = js_path.read_text(encoding="utf-8")
m = re.search(r"const THE_CAM_XUC = \[(.+?)\];", js, re.S)
the_js = tuple(re.findall(r"\['([^']+)'", m.group(1))) if m else ()
ok(the_js == THE_CAM_XUC, "danh sach ben giao dien khop ben Python", the_js)

if co_vieneu:
    for the, so in zip(THE_CAM_XUC, (1, 2, 3)):
        ra = ph(f"{the} Kính gửi quý vị.")
        ok(f"<|emotion_{so}|>" in ra, f"{the} -> <|emotion_{so}|>", ra[:44])
    ok("<|emotion_" not in ph("Không có thẻ gì cả."),
       "cau khong co the thi khong sinh token cam xuc")

print("\n--- B. Chuan hoa BOC ngoac vuong - ly do phai chen the SAU ---")
td = dict(engine.TUDIEN_MAC_DINH)
ra = engine.chuan_hoa_van_ban("[cười] Xin chào.", td, {})
ok("[cười]" not in ra,
   "chuan_hoa_van_ban van boc ngoac vuong nhu cu (khong sua engine)", ra)
ok("cười" in ra, "chu ben trong ngoac bi giu lai - chen the TRUOC la doc ra tieng")

print("\n--- C. Duong day that: playlist mang the o mau DAU cua dung doan ---")
khoa_du_lieu.khoa()
api = ApiMoi()
DOAN = [
    {"kieu": "head", "chu": "THÔNG BÁO"},
    {"kieu": "blank", "chu": ""},
    {"kieu": "body", "chu": "Kính gửi toàn thể cán bộ."},
    {"kieu": "body", "chu": "Chúc mọi người mạnh khoẻ.", "the": "[cười]"},
]
api.moi_dat_doan(DOAN)
pl, ban_do = api._playlist, api._doan_cua_mau

co_the = [i for i, s in enumerate(pl) if "[cười]" in s["text"]]
ok(len(co_the) == 1, "dung MOT mau mang the", f"{len(co_the)} mau")
if co_the:
    i = co_the[0]
    ok(ban_do[i] == 4, "the nam dung doan 4, khong lac sang doan khac", ban_do[i])
    ok(pl[i]["text"].startswith("[cười] "), "the dung dau chuoi doc", pl[i]["text"][:34])
    # Day la cho de vo nhat: `goc`/`tu`/`den` dem tren chuoi HIEN THI de to chu.
    ok("[cười]" not in pl[i]["goc"], "the KHONG lot vao `goc` - to chu khong lech")
    ok(pl[i]["den"] - pl[i]["tu"] == len(pl[i]["goc"]),
       "khoang to chu van dung bang do dai chuoi hien thi",
       f'{pl[i]["tu"]}..{pl[i]["den"]} / {len(pl[i]["goc"])}')

ok(all("[cười]" not in s["text"] for j, s in enumerate(pl) if ban_do[j] != 4),
   "doan khong dat the thi khong dinh the")

print("\n--- D. Chuoi doc ra tu playlist qua duoc phonemize ---")
if co_vieneu and co_the:
    ra = ph(pl[co_the[0]]["text"])
    ok("<|emotion_1|>" in ra, "chuoi playlist -> token cam xuc that", ra[:46])

print("\n--- E. The la bi loai, khong duoc doc thanh chu ---")
api.moi_dat_doan([{"kieu": "body", "chu": "Xin chào.", "the": "[nhảy múa]"}])
ok(all("nhảy múa" not in s["text"] for s in api._playlist),
   "the khong nam trong ba the VieNeu hieu thi bi bo han",
   api._playlist[0]["text"][:40] if api._playlist else "")

print(f"\n{'XANH — khớp hết' if loi == 0 else f'ĐỎ — {loi} chỗ lệch'}")
sys.exit(1 if loi else 0)
