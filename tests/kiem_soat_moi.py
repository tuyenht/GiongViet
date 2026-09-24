# -*- coding: utf-8 -*-
"""Kiem man hinh 2 - Soat van ban.

Chay tren ApiMoi THAT, khong mo cua so, khong phat tieng, khong cham du lieu.
"""
import io
import sys
import tempfile
from pathlib import Path


# Goc du an, tinh tu chinh vi tri tep nay. KHONG viet cung duong dan:
# kho da len GitHub, ai tai ve cho khac la vo het bo kiem.
_GOC = str(Path(__file__).resolve().parent.parent)
sys.path.insert(0, _GOC)
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8",
                              line_buffering=True)

from giaodien import nhat_ky
nhat_ky.TEP_LOG = Path(tempfile.gettempdir()) / "gd-kiem-loi.log"

from giaodien import soat  # noqa: E402
from giaodien_moi import khoa_du_lieu, soat_moi  # noqa: E402
from giaodien_moi.cau_noi_moi import ApiMoi  # noqa: E402

loi = 0


def ok(dk, nhan, them=""):
    global loi
    print(f"  {'ĐẠT ' if dk else 'LỆCH'} {nhan}{'  →  ' + str(them) if them else ''}")
    if not dk:
        loi += 1


print("--- A. Tieu de viet hoa co dau KHONG duoc bao nham la viet tat ---")
# Da vap that: 'THÔNG BÁO NGHỈ LỄ QUỐC KHÁNH' de ra 3 canh bao gia TH·NG·KH,
# vi lookahead cu chi chan chu THUONG co dau, quen chu HOA co dau.
for cau in ["THÔNG BÁO NGHỈ LỄ QUỐC KHÁNH", "ĐỀ NGHỊ MỌI NGƯỜI",
            "KÍNH GỬI QUÝ VỊ", "CHƯƠNG TRÌNH VĂN NGHỆ"]:
    ok(not soat.VIET_TAT.findall(cau), f"{cau!r} -> khong canh bao",
       soat.VIET_TAT.findall(cau) or "sach")

# HAN CHE DA BIET, ghi ra day de nguoi sau khong tuong la bug moi: tu tieng
# Viet KHONG DAU viet hoa toan bo thi khong the phan biet voi viet tat. "DANH"
# trong "DANH SÁCH" van bi bao. Vo hai - may doc "DANH" dung roi, chi la mot
# canh bao thua; con neu siet chat hon thi se bo sot viet tat that.
ok(soat.VIET_TAT.findall("DANH SÁCH ỦNG HỘ") == ["DANH"],
   "han che da biet: tu khong dau viet hoa van bi bao (chap nhan)")

print("\n--- B. Viet tat THAT thi van phai bat duoc ---")
for cau, mong in [("UBND TP.HCM", {"UBND", "TP", "HCM"}),
                  ("công ty TNHH Phúc Lâm", {"TNHH"}),
                  ("Gọi số ĐT hoặc CMND", {"ĐT", "CMND"})]:
    thay = set(soat.VIET_TAT.findall(cau))
    ok(mong <= thay, f"{cau!r} bat duoc {sorted(mong)}", sorted(thay))

khoa_du_lieu.khoa()          # BAT BUOC: ApiMoi khong tu khoa nua
api = ApiMoi()
api._cfg["doc_so_bang_chu"] = True
# "XKLĐ" va "TĐC" cố ý chọn thứ CHƯA có trong từ điển người dùng - UBND, TP,
# HCM, TNHH đều đã có sẵn (43 mục), mà đã dạy rồi thì soát không báo nữa, và
# đó mới là hành vi đúng.
DOAN = [
    {"kieu": "head", "chu": "THÔNG BÁO NGHỈ LỄ 2/9"},
    {"kieu": "blank", "chu": ""},
    {"kieu": "body", "chu": "Kính gửi cán bộ UBND TP.HCM và tổ XKLĐ khu TĐC."},
    {"kieu": "body", "chu": "Nghỉ từ 31/8/2026, gọi 1900 6868 nếu cần ☎."},
]
api.moi_dat_doan(DOAN)
d = api.moi_soat()

print("\n--- C. Tab 1: cho can chu y ---")
cy = d["chuY"]
ok(not cy["trong"], "co van ban de soat")
loai = {v["loai"] for v in cy["vanDe"]}
ok("viettat" in loai, "bat duoc viet tat chua day", sorted(loai))
ok("kytu" in loai, "bat duoc ky tu la (dau dien thoai)")
ok(all("doan" in v for v in cy["vanDe"]), "moi muc deu biet no o DOAN nao")
ok(all(1 <= v["doan"] <= len(DOAN) for v in cy["vanDe"]),
   "so doan nam trong khoang hop le",
   sorted({v["doan"] for v in cy["vanDe"]}))
ok(cy["nang"] + cy["nhe"] == len(cy["vanDe"]), "dem loi + canh bao khop tong")
tu = {v["tu"] for v in cy["vanDe"] if v["loai"] == "viettat"}
ok({"XKLĐ", "TĐC"} <= tu, "bat dung chu CHUA day", sorted(tu))
ok(not ({"UBND", "TP", "HCM"} & tu),
   "chu DA co trong tu dien thi KHONG bao nua", sorted(tu))

print("\n--- D. Tab 2: van ban sau chuan hoa ---")
ch = d["chuanHoa"]
ok(len(ch["dong"]) == 3, "bo qua doan RONG, con 3 doan co chu", len(ch["dong"]))
ok(all(x["doan"] != 2 for x in ch["dong"]), "doan 2 (blank) khong co mat")
ok(ch["soDoi"] >= 2, f"{ch['soDoi']} doan se doc khac van ban goc")
d1 = next(x for x in ch["dong"] if x["doan"] == 1)
ok("tháng 9" in d1["doc"], "'2/9' doc thanh ngay thang", d1["doc"])
d3 = next(x for x in ch["dong"] if x["doan"] == 3)
ok("Ủy ban nhân dân" in d3["doc"], "'UBND' doc thanh chu (tu dien)", d3["doc"][:50])

print("\n--- E. Chuoi doc phai la CHINH chuoi engine se doc ---")
# Khong duoc chuan hoa lai lan nua: lech mot chut la man soat noi doi.
gom = {}
for i, seg in enumerate(api._playlist):
    n = api._doan_cua_mau[i]
    gom.setdefault(n, []).append(seg["text"].strip())
for x in ch["dong"]:
    mong = " ".join(t for t in gom.get(x["doan"], []) if t)
    ok(x["doc"] == mong, f"doan {x['doan']} khop nguyen van playlist")

print("\n--- F. Quy tac: chi bay nut cho thu BAT TAT DUOC THAT ---")
q = {x["ma"]: x for x in d["quyTac"]}
ok(len(d["quyTac"]) == 4, "du 4 nhom quy tac", len(d["quyTac"]))
ok(q["so"]["doiDuoc"] and q["so"]["khoa"] == "doc_so_bang_chu",
   "'So thanh chu' co cong tac that")
ok(not q["ngay"]["doiDuoc"], "'Ngay thang' KHONG bay nut (engine luon bat)")
ok(not q["daucau"]["doiDuoc"], "'Bo dau cau lap' KHONG bay nut")
ok(q["so"]["so"] > 0, f"dem duoc {q['so']['so']} cho co chu so")

print("\n--- G. Tat quy tac thi chuoi doc phai doi that ---")
truoc = next(x for x in ch["dong"] if x["doan"] == 4)["doc"]
d2 = api.moi_dat_quy_tac("doc_so_bang_chu", False)
sau = next(x for x in d2["chuanHoa"]["dong"] if x["doan"] == 4)["doc"]
ok(truoc != sau, "tat 'So thanh chu' -> engine doc khac han")
ok("hai nghìn" not in sau, "khong con doc so thanh chu nua", sau[:56])
ok(api._cfg["doc_so_bang_chu"] is False, "cfg trong bo nho da doi")
api.moi_dat_quy_tac("doc_so_bang_chu", True)

print("\n--- H. Khoa la thi bo qua, khong ghi bua vao cau hinh ---")
ok(api.moi_dat_quy_tac("khoa_khong_co_that", True) is None, "tra None")
ok("khoa_khong_co_that" not in api._cfg, "khong them khoa la vao cfg")

print("\n--- I. Van ban rong thi noi ro la CHUA soat, khong noi 'khong sao' ---")
api.moi_dat_doan([])
trong = api.moi_soat()
ok(trong["chuY"]["trong"] is True, "co co 'trong'")
ok(not trong["chuY"]["vanDe"], "khong bia ra van de nao")
ok(not trong["chuanHoa"]["dong"], "tab 2 cung rong")

api._huy_hen_nap_truoc()
api._don_dep()
print(f"\n{'XANH — khớp hết' if loi == 0 else f'ĐỎ — {loi} chỗ lệch'}")
sys.exit(1 if loi else 0)
