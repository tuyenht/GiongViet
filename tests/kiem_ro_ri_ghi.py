# -*- coding: utf-8 -*-
"""Quet ma nguon tim duong ro CHUA khoa. Khong chay ham nao, chi doc code.

Phep kiem chong hoi quy cho khoa_du_lieu.py. Neu mai nay ai them mot ham ghi
moi vao engine hay giaodien/ roi goi tu cau_noi.py ma quen khoa, bai nay phai
DO - thay vi doi den luc du lieu that cua nguoi dung bi ghi de moi biet.

Cach lam:
  1. Doc DocCongDuc.py va giaodien/*.py, danh dau ham nao CO GHI DIA. Ham goi
     mot ham co ghi cung tinh la co ghi (lan truyen den khi on dinh).
  2. Doc cau_noi.py, liet ke moi loi goi dang `mo_dun.ham(...)`.
  3. Loi goi nao tro toi mot ham co ghi ma khong nam trong CUA_RA_GHI -> DO.
"""
import ast
import io
import re
import sys
from pathlib import Path


# Goc du an, tinh tu chinh vi tri tep nay. KHONG viet cung duong dan:
# kho da len GitHub, ai tai ve cho khac la vo het bo kiem.
_GOC = str(Path(__file__).resolve().parent.parent)
sys.path.insert(0, _GOC)
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8")

from giaodien_moi import khoa_du_lieu

GOC = Path(_GOC)

# Dau hieu cham dia trong than mot ham.
#
# CO Y khong co "replace" va "rename": chuoi cung co .replace(), va ca engine
# dung no khap noi de chuan hoa van ban. De vao day thi gan nhu ham nao cung
# bi coi la ghi dia - bai kiem thanh vo dung. Doi ten tep di qua os.replace()
# va duoc bat rieng ben duoi.
GHI_TRUC_TIEP = {"write_text", "write_bytes", "unlink", "rmtree", "touch"}

# Loi goi ham dang day du duoc tinh la ghi dia.
GHI_THEO_TEN = {"json.dump", "os.replace", "os.rename", "os.remove",
                "shutil.copy", "shutil.copy2", "shutil.copyfile", "shutil.move",
                # Cấu hình nay vào giongviet.db qua hai cửa này chứ không còn
                # write_text thẳng ra tệp. Thiếu chúng ở đây thì ho_so.luu và
                # he_thong.luu_tuy_chon lọt lưới - quét mã không thấy dấu ghi
                # nào, trong khi chúng vẫn ghi thật.
                "engine.ghi_tep_cau_hinh", "ghi_tep_cau_hinh",
                "kho_cau_hinh.ghi", "kho.ghi"}

# Mien tru, co ly do ro rang cho tung cai:
MIEN_TRU = {
    # Nhat ky loi cua chuong trinh, khong phai du lieu nguoi dung. Chan no di
    # thi mat luon duong chan doan khi may nguoi dung tro chung.
    ("giaodien.nhat_ky", "ghi"),
    ("giaodien.nhat_ky", "ghi_loi"),
    ("giaodien.nhat_ky", "bat_loi_toan_cuc"),

    # lay_danh_sach_giong_day_du -> lay_danh_sach_giong_vieneu ->
    # dam_bao_vieneu_san_sang, va ham cuoi ghi giong_rieng/.voice_cache.json
    # (DocCongDuc.py, trong dam_bao_vieneu_san_sang).
    #
    # Mien tru chu KHONG khoa, vi ba le do:
    #   1. Do la CACHE DAN XUAT - vector dac trung tinh lai duoc tu chinh cac
    #      tep .wav mau. Xoa di chi mat thoi gian nap, khong mat du lieu nao.
    #   2. Khoa cua ra nay nghia la dam_bao_vieneu_san_sang tra ve gia - ma no
    #      tra ve doi tuong mo hinh TTS. Tra gia la vo ca duong doc.
    #   3. Duong nay chay khi NAP MO HINH, khong phai khi nguoi dung bam Luu.
    #
    # Cai can canh la bai kiem nao goi toi day phai tro GIONG_RIENG_DIR sang
    # thu muc tam truoc, dung de no ghi vao kho that.
    ("DocCongDuc", "lay_danh_sach_giong_day_du"),
    ("DocCongDuc", "lay_danh_sach_giong_vieneu"),
    ("DocCongDuc", "dam_bao_vieneu_san_sang"),
}

# Cua ra da khoa, dang "mo_dun.ham".
DA_KHOA = ({f"{m.__name__}.{t}" for m, t, _, _ in khoa_du_lieu.CUA_RA_GHI}
           | {f"{m.__name__.replace('src.core.', 'giaodien.')}.{t}"
              for m, t, _, _ in khoa_du_lieu.CUA_RA_GHI}
           | {f"{m.__name__.replace('src.app.', 'giaodien_moi.')}.{t}"
              for m, t, _, _ in khoa_du_lieu.CUA_RA_GHI})

loi = 0


def ok(dk, nhan, them=""):
    global loi
    print(f"  {'ĐẠT ' if dk else 'LỆCH'} {nhan}{'  →  ' + str(them) if them else ''}")
    if not dk:
        loi += 1


def _ten_ham_goi(node):
    """Ten ham cua mot loi goi: 'ho_so.luu', 'open', 'json.dump'..."""
    f = node.func
    if isinstance(f, ast.Name):
        return f.id
    if isinstance(f, ast.Attribute):
        if isinstance(f.value, ast.Name):
            return f"{f.value.id}.{f.attr}"
        return f.attr
    return ""


def _mo_de_ghi(n) -> bool:
    """open(p, "w") / CONFIG_FILE.open("w") / open(p, mode="a")...

    Phai bat ca dang phuong thuc: engine.save_config ghi bang
    `with CONFIG_FILE.open("w") as f`, khong dung open() dung san.
    """
    for a in list(n.args[:2]) + [k.value for k in n.keywords if k.arg == "mode"]:
        if isinstance(a, ast.Constant) and isinstance(a.value, str) \
                and any(c in a.value for c in "wax"):
            return True
    return False


def _co_ghi_truc_tiep(than) -> bool:
    for n in ast.walk(than):
        if isinstance(n, ast.Attribute) and n.attr in GHI_TRUC_TIEP:
            return True
        if isinstance(n, ast.Call):
            ten = _ten_ham_goi(n)
            if (ten == "open" or ten.endswith(".open")) and _mo_de_ghi(n):
                return True
            if ten in GHI_THEO_TEN:
                return True
    return False


def quet_mo_dun(duong_dan: Path, ten_mo_dun: str) -> set:
    """Tap ten ham cap module CO GHI trong mot tep."""
    cay = ast.parse(duong_dan.read_text(encoding="utf-8"))
    ham = {n.name: n for n in cay.body
           if isinstance(n, (ast.FunctionDef, ast.AsyncFunctionDef))}
    co_ghi = {t for t, n in ham.items() if _co_ghi_truc_tiep(n)}

    # Lan truyen: ham goi mot ham co ghi thi cung co ghi.
    #
    # TRU ham da nam trong CUA_RA_GHI - do la diem chan. `ho_so.doc()` co goi
    # `ho_so.luu()` that (khi tep hong thi no dung lai tu dau), nhung `luu` da
    # bi khoa nen `doc` khong con duong nao cham dia nua. Khong tru thi ca chuoi
    # ham doc-du-lieu deu bi bao la ro ri.
    chan = {t for t in co_ghi if f"{ten_mo_dun}.{t}" in DA_KHOA}
    doi = True
    while doi:
        doi = False
        for ten, n in ham.items():
            if ten in co_ghi:
                continue
            for goi in ast.walk(n):
                goi_ten = _ten_ham_goi(goi) if isinstance(goi, ast.Call) else ""
                if goi_ten in co_ghi and goi_ten not in chan:
                    co_ghi.add(ten)
                    doi = True
                    break
    return {t for t in co_ghi if (ten_mo_dun, t) not in MIEN_TRU}


print("--- A. Ham co ghi dia trong engine va giaodien/ ---")
G_GD = (GOC / "src" / "core") if (GOC / "src" / "core").exists() else (GOC / "giaodien")
ban_do = {}          # 'ten_alias_trong_cau_noi' -> (ten_mo_dun, set ham co ghi)
ban_do["engine"] = ("DocCongDuc", quet_mo_dun(GOC / "DocCongDuc.py", "DocCongDuc"))
for p in sorted(G_GD.glob("*.py")):
    if p.stem in ("__init__", "cau_noi"):
        continue
    ban_do[p.stem] = (f"giaodien.{p.stem}",
                      quet_mo_dun(p, f"giaodien.{p.stem}"))

tong = sum(len(v[1]) for v in ban_do.values())
ok(tong > 0, f"tim thay {tong} ham co ghi dia")
ok("save_config" in ban_do["engine"][1], "engine.save_config bi nhan dien la ghi")
ok("luu" in ban_do["ho_so"][1], "ho_so.luu bi nhan dien la ghi")
ok("tao_giong_rieng" in ban_do["engine"][1],
   "lan truyen dung: tao_giong_rieng ghi qua luu_ds_giong_rieng")
ok("luu_tuy_chon" in ban_do["he_thong"][1], "he_thong.luu_tuy_chon bi nhan dien")

print("\n--- B. Loi goi ham ghi trong cau_noi.py phai nam trong CUA_RA_GHI ---")
cn_path = (GOC / "src" / "core" / "cau_noi.py") if (GOC / "src" / "core" / "cau_noi.py").exists() else (GOC / "giaodien" / "cau_noi.py")
cay = ast.parse(cn_path.read_text(encoding="utf-8"))
ro = []
dung = set()
for n in ast.walk(cay):
    if not isinstance(n, ast.Call):
        continue
    ten = _ten_ham_goi(n)
    if "." not in ten:
        continue
    alias, ham = ten.split(".", 1)
    muc = ban_do.get(alias)
    if not muc or ham not in muc[1]:
        continue
    day_du = f"{muc[0]}.{ham}"
    if day_du in DA_KHOA:
        dung.add(day_du)
    else:
        ro.append(f"{day_du} (dong {n.lineno})")

ok(not ro, "khong con duong ghi nao ho trong cau_noi.py", ro or "kin")
ok(len(dung) >= 3, f"co {len(dung)} cua ra da khoa dang duoc goi that",
   sorted(dung))

print("\n--- B2. Loi goi ham ghi trong cau_noi_moi.py phai nam trong CUA_RA_GHI ---")
# Phan B chi soi cau_noi.py - lop Api CU. Nhung lop dang chay that trong
# GiongViet.py la ApiMoi (src/app/cau_noi_moi.py), va no co cua ra ghi RIENG:
# ho_so_v2.luu ghi hoso-v2.json, luu_tep.luu ghi van ban nguoi dung.
#
# Thieu phan nay thi luoi canh chi soi lop cu: ai them mot ham ghi moi roi goi
# tu ApiMoi ma quen khoa, khong phep nao do len. Ba cua ra hien co deu CO CHU Y
# khong khoa - xem MIEN_TRU_MOI ngay duoi - nen phan nay canh cho TUONG LAI.
G_APP = (GOC / "src" / "app") if (GOC / "src" / "app").exists() else (GOC / "giaodien_moi")
ban_do_moi = dict(ban_do)
for p_app in sorted(G_APP.glob("*.py")):
    if p_app.stem in ("__init__", "cau_noi_moi", "khoa_du_lieu"):
        continue
    ban_do_moi[p_app.stem] = (f"giaodien_moi.{p_app.stem}",
                              quet_mo_dun(p_app, f"giaodien_moi.{p_app.stem}"))

# Ba cua ra duoi day CO Y khong khoa. Khong phai bo sot - da co hai bai kiem
# doc lap khang dinh dieu nguoc lai:
#   tests/kiem_khoa_du_lieu.py  muc G  "van luu duoc hoso-v2.json khi da khoa"
#   tests/kiem_bam_loan.py      muc F  "moi_luu_ho_so ghi duoc khi da khoa"
#
# Ly do: tang MOI chan bang cach DOI DICH GHI, khong bang cach khoa ham.
# Bai kiem tro ho_so_v2.TEP (va duong luu van ban) sang thu muc tam roi moi
# chay; khoa ham lai thi chinh hai bai tren do ngay.
#
# Ranh gioi phai giu: bai kiem nao dung ba ham nay MA QUEN doi dich ghi thi
# no cham vao du lieu that. Canh chuyen do KHONG phai viec cua tep nay ma la
# cua tung bai: lay van tay (mtime + noi dung) sau tep du lieu that truoc khi
# chay roi so lai sau khi chay - xem tests/kiem_bam_loan.py muc D.
MIEN_TRU_MOI = {
    "giaodien_moi.ho_so_v2.luu",
    "giaodien_moi.luu_tep.luu",
    "DocCongDuc.ghi_tep_cau_hinh",
}

cnm_path = G_APP / "cau_noi_moi.py"
ok(cnm_path.exists(), "tim thay cau_noi_moi.py de soi", cnm_path.name)
ro_moi = []
if cnm_path.exists():
    for n in ast.walk(ast.parse(cnm_path.read_text(encoding="utf-8"))):
        if not isinstance(n, ast.Call):
            continue
        ten = _ten_ham_goi(n)
        if "." not in ten:
            continue
        alias, ham = ten.split(".", 1)
        muc = ban_do_moi.get(alias)
        if not muc or ham not in muc[1]:
            continue
        day_du = f"{muc[0]}.{ham}"
        if day_du not in DA_KHOA and day_du not in MIEN_TRU_MOI:
            ro_moi.append(f"{day_du} (dong {n.lineno})")

ok(not ro_moi, "khong con duong ghi nao ho trong cau_noi_moi.py", ro_moi or "kin")


print("\n--- C. Moi muc trong CUA_RA_GHI deu con ton tai that ---")
for m, t, _, tep in khoa_du_lieu.CUA_RA_GHI:
    ok(hasattr(m, t), f"{m.__name__}.{t} van ton tai  ({tep})")

TEP_DU_LIEU = ("cauhinh.ini", "hoso.json", "noidung.ini", "tudien.ini",
               "giaodien.json", "congduc.txt")

print("\n--- D. Cac module khac cua ban moi khong tu ghi vao du lieu cu ---")
G_GM = (GOC / "src" / "app") if (GOC / "src" / "app").exists() else (GOC / "giaodien_moi")
G_KIEM = (GOC / "tests") if (GOC / "tests").exists() else (GOC / "kiem")
for p in sorted(list(G_GM.glob("*.py")) + list(G_KIEM.glob("*.py"))):
    ten = p.stem.lower()
    if "kiem" in ten or "nghiemthu" in ten or p.stem == "khoa_du_lieu" or p.stem == "sitecustomize":
        continue
    nguon = p.read_text(encoding="utf-8")
    xau = [t for t in TEP_DU_LIEU if f'"{t}"' in nguon or f"'{t}'" in nguon]
    ok(not xau, f"{p.name} khong nhac ten tep du lieu cu", xau or "sach")

print("\n--- E. Bo kiem va bai do khong duoc ghi vao NHAT KY that ---")
for p in sorted(G_KIEM.glob("*.py")):
    nguon = p.read_text(encoding="utf-8")
    # Goi thang nhat_ky.ghi_loi la ghi vao log that. Bit mieng no thi khong sao.
    goi_that = re.search(r"^\s*nhat_ky\.ghi_loi\(", nguon, re.M) is not None
    bit = "ghi_loi = lambda" in nguon
    ok(not goi_that or bit,
       f"{p.name} khong lam ban nhat ky that",
       "co bit mieng" if bit else "sach")

print("\n--- F. Khong tep nao trong kiem/ viet cung duong dan may nay ---")
# Kho da len GitHub. Viet cung "C:\\Projects\\..." la ai tai ve cho khac cung
# vo het bo kiem, ma vo theo kieu im lang: FileNotFoundError giua chung.
# Ghep chuoi de chinh tep nay khong tu bao lech: viet thang "C:\\Projects" vao
# day thi dong kiem tro thanh cai ma no dang di tim.
_O_DIA = "C" + ":"
# Dung G_KIEM (dong 207) chu khong viet cung "kiem": thu muc da doi ten thanh
# tests/, nen vong nay tung chay tren tap RONG va muc F luon bao dat ma khong
# kiem gi ca - dung cai loi ma chinh no sinh ra de canh.
_ds_quet = sorted(list(G_KIEM.glob("*.py")) + list(G_KIEM.glob("*.mjs")))
ok(len(_ds_quet) > 0, f"quet duoc tep trong {G_KIEM.name}/", f"{len(_ds_quet)} tep")
for p in _ds_quet:
    nguon = p.read_text(encoding="utf-8", errors="replace")
    ok(_O_DIA + "\\Projects" not in nguon and _O_DIA + "/Projects" not in nguon,
       f"{p.name} khong viet cung duong dan")

print(f"\n{'XANH — khớp hết' if loi == 0 else f'ĐỎ — {loi} chỗ lệch'}")
sys.exit(1 if loi else 0)
