# -*- coding: utf-8 -*-
"""Tai hien LOI L7 — "so nguoi moi nhom chi phoi nhip doc ma khong ai doi duoc".

RUI RO THAT SU o day KHONG phai "chuong trinh chay sai". Chuong trinh chay
dung y hen: cu N ten thi nghi dai mot lan. Rui ro la CAI NUM DIEU KHIEN BI
CAT MAT: gia tri N van nam trong cauhinh.ini, van duoc engine dung moi lan
dung playlist danh sach cong duc, nhung giao dien moi khong con cho nao bay
no ra. Nguoi dung 70 tuoi muon nghi dai thua hon hay thua hon thi khong co
nut nao bam — phai mo cauhinh.ini bang Notepad.

Bai nay chung minh HAI VE TACH ROI:
  VE 1 — "chi phoi nhip doc": chay that build_playlist_congduc voi cung mot
          danh sach 45 dong, chi doi so_nguoi_nhom, roi DEM cho nghi dai.
  VE 2 — "khong ai doi duoc": liet ke DAY DU khoa man Cai dat bay ra va DAY
          DU khoa ApiMoi.moi_dat_cai_dat chap nhan, cho thay khoa nay vang
          mat o ca hai.

KHONG chay tong hop tieng: chi dung o muc PLAYLIST (mot list dict), khong
cham vieneu, khong goi ffplay.
KHONG cham du lieu nguoi dung: chay tren tempfile, dat lai kho_cau_hinh.dat_goc
va engine.CONFIG_FILE sang thu muc tam, bat them khoa_du_lieu.khoa(), va do
van tay md5 sau tep du lieu that truoc/sau de tu chung minh.
"""
# --- dat goc du an tu vi tri tep nay (bai nam trong kiem/) ---
import os as _os, sys as _sys
from pathlib import Path as _Path
_os.environ.setdefault('GIONGVIET_GOC', str(_Path(__file__).resolve().parent.parent))
_sys.path.insert(0, _os.environ['GIONGVIET_GOC'])
# --- het shim ---
import ast
import hashlib
import io
import os
import re
import shutil
import sys
import tempfile
from pathlib import Path


# Goc du an. Tep nay nam ngoai kho (thu muc nhap), nen khong tinh duoc bang
# Path(__file__) nhu bo kiem trong kiem/. Tim NGUOC LEN tu thu muc lam viec
# thay vi viet cung "C:\..." — viet cung la may khac chay la vo.
def _tim_goc() -> Path:
    goi_y = os.environ.get("GIONGVIET_GOC")
    if goi_y and (Path(goi_y) / "DocCongDuc.py").exists():
        return Path(goi_y).resolve()
    p = Path.cwd().resolve()
    for ung_vien in [p, *p.parents]:
        if (ung_vien / "DocCongDuc.py").exists() and (ung_vien / "kho_cau_hinh.py").exists():
            return ung_vien
    raise SystemExit("Khong tim thay goc du an (can DocCongDuc.py + kho_cau_hinh.py)")


_GOC = _tim_goc()
sys.path.insert(0, str(_GOC))
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8",
                              line_buffering=True)

# --- Van tay du lieu nguoi dung TRUOC khi lam gi ------------------------------
TEP_CANH = ["cauhinh.ini", "noidung.ini", "congduc.txt", "tudien.ini",
            "hoso.json", "hoso-v2.json", "giaodien.json",
            "GiongViet/giongviet.db"]


def _van_tay() -> dict:
    ra = {}
    for t in TEP_CANH:
        p = _GOC / t
        ra[t] = hashlib.md5(p.read_bytes()).hexdigest() if p.is_file() else "(khong co)"
    return ra


VAN_TAY_TRUOC = _van_tay()

import DocCongDuc as engine          # noqa: E402
import kho_cau_hinh as kho           # noqa: E402
from giaodien import cai_dat, du_lieu, ho_so   # noqa: E402
from giaodien_moi import khoa_du_lieu          # noqa: E402

# Lop chan thu hai cua chinh du an: bit 9 cua ra ghi dia.
khoa_du_lieu.khoa()

TAM = Path(tempfile.mkdtemp(prefix="l7-"))
kho.dat_goc(TAM)                     # kho tro sang thu muc tam
engine.CONFIG_FILE = TAM / "cauhinh.ini"   # chi doi thuoc tinh luc chay

loi = 0


def ok(dk, nhan, them=""):
    global loi
    print(f"  {'ĐẠT ' if dk else 'LỆCH'} {nhan}{'  →  ' + str(them) if them else ''}")
    if not dk:
        loi += 1


def _dong(tep: str, tu: int, den: int) -> str:
    """Trich nguyen van dong tu..den (dem tu 1) cua mot tep trong kho."""
    d = (_GOC / tep).read_text(encoding="utf-8").splitlines()
    return "\n".join(f"    {i:>4} | {d[i - 1]}" for i in range(tu, den + 1))


# =============================================================================
print("=== A. TRICH NGUYEN VAN MA NGUON — doi chieu voi so dong bao cao neu ===")
# =============================================================================
print("\n  [1] DocCongDuc.py:1502-1504 — cho chen nghi dai")
print(_dong("DocCongDuc.py", 1502, 1504))
nguon_engine = (_GOC / "DocCongDuc.py").read_text(encoding="utf-8").splitlines()
ok('if cfg["so_nguoi_nhom"] and stt % cfg["so_nguoi_nhom"] == 0:'
   in nguon_engine[1502], "dong 1503 dung la cho quyet dinh nghi dai")
ok('nghi = cfg["nghi_nhom"]' in nguon_engine[1503], "dong 1504 gan nghi_nhom")

print("\n  [2] DocCongDuc.py:546 — cho nap gia tri, mac dinh 20")
print(_dong("DocCongDuc.py", 546, 546))
ok('so_nguoi_moi_nhom", 20' in nguon_engine[545], "dong 546 mac dinh dung la 20")

print("\n  [3] giaodien/du_lieu.py:126-134 — cho DUY NHAT bay khoa nay ra")
print(_dong("giaodien/du_lieu.py", 126, 134))
nguon_dl = (_GOC / "giaodien" / "du_lieu.py").read_text(encoding="utf-8").splitlines()
ok('"so_nguoi_nhom"' in nguon_dl[131], "dong 132 nam trong bang THANH_TRUOT")

print("\n  [4] giaodien/du_lieu.py:156 va :173 — hai cho doc bang THANH_TRUOT")
print(_dong("giaodien/du_lieu.py", 154, 156))
print(_dong("giaodien/du_lieu.py", 171, 173))

print("\n  [5] Ai goi thanh_truot / ep_gia_tri? (quet toan bo ma dang chay)")
nguoi_goi = []
for thu_muc in ("giaodien", "giaodien_moi", "ui-moi"):
    for p in sorted((_GOC / thu_muc).glob("*")):
        if p.suffix not in (".py", ".js", ".html"):
            continue
        t = p.read_text(encoding="utf-8", errors="replace")
        for ham in ("thanh_truot(", "ep_gia_tri(", "dat_thong_so"):
            for m in re.finditer(re.escape(ham), t):
                dong = t[:m.start()].count("\n") + 1
                nguoi_goi.append(f"{thu_muc}/{p.name}:{dong} → {ham}")
for g in nguoi_goi:
    print("      " + g)
ngoai_du_lieu = [g for g in nguoi_goi if "du_lieu.py" not in g]
ok(all("cau_noi.py" in g or "khoa_du_lieu.py" in g for g in ngoai_du_lieu),
   "ngoai chinh du_lieu.py, chi cau_noi.py (Api CU) va khoa_du_lieu.py nhac den",
   ngoai_du_lieu)
ok(not any(g.startswith("ui-moi/") for g in nguoi_goi),
   "KHONG mot tep nao trong ui-moi/ dong den thanh truot nay")


# =============================================================================
print("\n=== B. VE 1 — chung minh so_nguoi_nhom CO chi phoi nhip doc that ===")
# =============================================================================
# 45 dong, moi dong mot nguoi. Dung dau tab cho parse_data_file khoi doan.
DS = TAM / "danhsach.txt"
DS.write_text("\n".join(f"Nguyễn Văn {i:02d}\t100.000" for i in range(1, 46)) + "\n",
              encoding="utf-8")
records, canh_bao = engine.parse_data_file(DS)
ok(len([r for r in records if r["kind"] == "nguoi"]) == 45,
   "doc duoc 45 dong nguoi", f"{len(records)} ban ghi, {len(canh_bao)} canh bao")


def _cfg_voi(n: int) -> dict:
    """Ghi cauhinh.ini TAM roi nap qua chinh engine.load_config()."""
    (TAM / "cauhinh.ini").write_text(
        "[GiongDoc]\n"
        "phong_cach = Tin tức - thông báo\n"
        "\n[DocLienTuc]\n"
        "nghi_giua_nguoi = 1.30\n"
        "nghi_giua_nhom = 2.50\n"
        f"so_nguoi_moi_nhom = {n}\n"
        "nghi_giua_doan = 0.80\n"
        "nhan_manh_tien = 0\n",
        encoding="utf-8-sig")
    return engine.load_config()


def _dem_nghi_dai(cfg: dict):
    nd = engine.NoiDung()
    pl = engine.build_playlist_congduc(records, nd, cfg, {}, doc_loi_dan=False)
    dai = [m["stt"] for m in pl if m["loai"] == "nguoi"
           and abs(m["nghi"] - cfg["nghi_nhom"]) < 1e-9]
    tong_lang = sum(m["nghi"] for m in pl)
    return pl, dai, tong_lang


print("\n  [B1] so_nguoi_moi_nhom = 20 (gia tri mac dinh)")
cfg20 = _cfg_voi(20)
ok(cfg20["so_nguoi_nhom"] == 20, "load_config nap dung 20", cfg20["so_nguoi_nhom"])
pl20, dai20, lang20 = _dem_nghi_dai(cfg20)
print(f"      playlist: {len(pl20)} mẩu · nghỉ dài tại STT {dai20} "
      f"→ {len(dai20)} lần · tổng lặng {lang20:.2f} giây")

print("\n  [B2] so_nguoi_moi_nhom = 5")
cfg5 = _cfg_voi(5)
ok(cfg5["so_nguoi_nhom"] == 5, "load_config nap dung 5", cfg5["so_nguoi_nhom"])
pl5, dai5, lang5 = _dem_nghi_dai(cfg5)
print(f"      playlist: {len(pl5)} mẩu · nghỉ dài tại STT {dai5} "
      f"→ {len(dai5)} lần · tổng lặng {lang5:.2f} giây")

print("\n  [B3] So sanh")
ok(len(dai20) == 2, "N=20 → dung 2 cho nghi dai (STT 20, 40)", dai20)
ok(len(dai5) == 9, "N=5  → dung 9 cho nghi dai", dai5)
ok(len(dai20) != len(dai5),
   "HAI KET QUA KHAC NHAU → khoa nay CO tac dung that len nhip doc",
   f"{len(dai20)} lần vs {len(dai5)} lần")
ok(abs(lang5 - lang20) > 1.0,
   "chenh lech tong thoi gian lang nghe thay ro",
   f"{lang20:.2f} s → {lang5:.2f} s, lech {lang5 - lang20:+.2f} s")
ok(len(pl20) == len(pl5) == 45, "so mau khong doi, CHI khoang nghi doi")

print("\n  [B4] Duong nay CO nam trong ban moi khong?")
nguon_moi = (_GOC / "giaodien_moi" / "cau_noi_moi.py").read_text(encoding="utf-8")
vi_tri = [nguon_moi[:m.start()].count("\n") + 1
          for m in re.finditer(r"build_playlist_congduc", nguon_moi)]
print(f"      giaodien_moi/cau_noi_moi.py gọi build_playlist_congduc tại dòng {vi_tri}")
ok(bool(vi_tri),
   "ban MOI van dung dung ham nay khi mo tep danh sach → khong phai code chet",
   vi_tri)


# =============================================================================
print("\n=== C. VE 2 — chung minh khong cua nao cho nguoi dung doi ===")
# =============================================================================
tuy_chon = {"theme": "light", "zoom": 100, "thu_muc_xuat": ""}


def _khoa_man_cai_dat(loai: str):
    d = cai_dat.du_lieu(cfg20, tuy_chon, loai, "")
    ra = []
    for n in d["nhom"]:
        for m in n["muc"]:
            ra.append((n["ma"], m["kieu"], m.get("khoa") or f'(chỉ xem: {m["nhan"]})'))
    return ra


for loai in ("", "congduc", "vanban"):
    nhan = loai or "(khong loc theo ho so)"
    print(f"\n  [C1] Man Cai dat bay ra — loai ho so = {nhan}")
    muc = _khoa_man_cai_dat(loai)
    for nhom, kieu, k in muc:
        print(f"      · nhóm {nhom:<6} {kieu:<9} {k}")
    khoa_that = {k for _, _, k in muc if not k.startswith("(")}
    ok("so_nguoi_nhom" not in khoa_that,
       f"so_nguoi_nhom KHONG co trong man Cai dat ({nhan})", sorted(khoa_that))

print("\n  [C2] ApiMoi thuc su goi cai_dat.du_lieu voi loai nao?")
m = re.search(r"def moi_cai_dat\(self\):(.*?)\n    def ", nguon_moi, re.S)
print("      " + m.group(1).strip().splitlines()[-1].strip())
ok('cai_dat.du_lieu(self._cfg, self._tuy_chon, "vanban", "")' in nguon_moi,
   'ApiMoi.moi_cai_dat truyen "vanban" → man Cai dat cua ban moi loc theo vanban')

print("\n  [C3] Khoa ApiMoi.moi_dat_cai_dat CHAP NHAN (doc thang tu ma nguon)")
cay = ast.parse(nguon_moi)
chap_nhan = None
for n in ast.walk(cay):
    if isinstance(n, ast.FunctionDef) and n.name == "moi_dat_cai_dat":
        print(f"      giaodien_moi/cau_noi_moi.py:{n.lineno}  def moi_dat_cai_dat(...)")
        for c in ast.walk(n):
            if isinstance(c, ast.Assign) and getattr(c.targets[0], "id", "") == "cho_phep":
                chap_nhan = {e.value for e in c.value.elts}
                print(f"      dòng {c.lineno}: cho_phep = {sorted(chap_nhan)}")
ok(chap_nhan == {"doc_so_bang_chu", "bo_markdown"},
   "chi dung HAI khoa duoc chap nhan", sorted(chap_nhan or []))
ok("so_nguoi_nhom" not in (chap_nhan or set()),
   "so_nguoi_nhom KHONG nam trong danh sach chap nhan cua ApiMoi")

print("\n  [C4] Giao dien web co cho nao nhac den khoa nay khong?")
tim = []
for p in sorted((_GOC / "ui-moi").glob("*")):
    if p.suffix not in (".js", ".html", ".css"):
        continue
    t = p.read_text(encoding="utf-8", errors="replace")
    for tu in ("so_nguoi", "soNguoiNhom", "nhóm", "thong_so"):
        if tu in t:
            tim.append(f"{p.name}: “{tu}”")
print("      " + ("; ".join(tim) if tim else "khong tim thay chuoi nao"))
ok(not any("so_nguoi" in x or "soNguoiNhom" in x or "thong_so" in x for x in tim),
   "khong tep giao dien nao co o nhap / thanh truot cho khoa nay", tim)

print("\n  [C5] Ba thanh truot ban moi thuc su bay ra (ui-moi/giao-dien.js:365-369)")
print(_dong("ui-moi/giao-dien.js", 365, 369))
_js = (_GOC / "ui-moi" / "giao-dien.js").read_text(encoding="utf-8").splitlines()
# Cắt khối TRUOT theo NỘI DUNG chứ không theo số dòng: thêm bớt vài dòng ở chỗ
# khác trong tệp là lát cắt cứng trỏ nhầm, rồi phép kiểm đỏ lên vô cớ.
_i = next((k for k, d in enumerate(_js) if d.startswith("const TRUOT")), -1)
_khoi = _js[_i:_i + 8] if _i >= 0 else []
_ba = [x for x in ("tocDo", "caoDo", "amLuong") if any(x in d for d in _khoi)]
ok(_ba == ["tocDo", "caoDo", "amLuong"],
   "bang TRUOT cua ban moi chi co ba muc, khong co so_nguoi_nhom", _ba)

print("\n  [C6] Khoa nay VAN duoc cat vao ho so — nen doi ho so la doi ngam")
print(f"      giaodien/ho_so.py KHOA_THEO_LOAI['congduc'] = {ho_so.KHOA_THEO_LOAI['congduc']}")
ok("so_nguoi_nhom" in ho_so.KHOA_THEO_LOAI["congduc"],
   "ho so CO nho gia tri nay, nhung khong co man hinh nao dat no")

print("\n  [C7] Thanh truot cu VAN dung — chi la khong ai goi den")
bang = du_lieu.thanh_truot(cfg20, "congduc")
for b in bang:
    print(f"      · {b['khoa']:<14} {b['nhan']:<22} {b['hien_thi']:<12} "
          f"[{b['min']}..{b['max']}]")
ok(any(b["khoa"] == "so_nguoi_nhom" for b in bang),
   "du_lieu.thanh_truot(che_do='congduc') van tra ve muc nay — ma chet, khong ai goi")


# =============================================================================
print("\n=== D. GIA TRI THAT trong cau hinh nguoi dung (CHI DOC) ===")
# =============================================================================
that = _GOC / "cauhinh.ini"
if that.is_file():
    noi_dung = that.read_text(encoding="utf-8-sig")
    m = re.search(r"^\s*so_nguoi_moi_nhom\s*=\s*(\S+)", noi_dung, re.M)
    gt = m.group(1) if m else "(khong co dong nay)"
    print(f"      {that.name}: so_nguoi_moi_nhom = {gt}")
    ok(True, "doc duoc gia tri that", gt)
    ok(gt == "20",
       "gia tri that DUNG BANG mac dinh 20 → chua ai tung dat khac roi bi ket",
       gt)
else:
    ok(False, "khong thay cauhinh.ini that")

hs = _GOC / "hoso.json"
if hs.is_file():
    import json
    d = json.loads(hs.read_text(encoding="utf-8"))
    for h in d.get("dsHoSo", []):
        if "so_nguoi_nhom" in h:
            print(f"      hoso.json · hồ sơ “{h['ten']}” : "
                  f"so_nguoi_nhom = {h['so_nguoi_nhom']}")
    ok(all(h.get("so_nguoi_nhom", 20) == 20 for h in d.get("dsHoSo", [])),
       "khong ho so nao dang giu mot gia tri khac 20")


# =============================================================================
print("\n=== E. TU CHUNG MINH: khong cham du lieu nguoi dung ===")
# =============================================================================
VAN_TAY_SAU = _van_tay()
for t in TEP_CANH:
    ok(VAN_TAY_TRUOC[t] == VAN_TAY_SAU[t], f"{t} nguyen ven",
       VAN_TAY_SAU[t][:12])
ok(not (_GOC / "giongviet.db").exists(),
   "khong de lai giongviet.db rong giua thu muc du an")
print(f"      khoa_du_lieu chan duoc: {khoa_du_lieu.da_chan or 'khong lan nao'}")

shutil.rmtree(TAM, ignore_errors=True)
print(f"\n{'XANH — khớp hết' if loi == 0 else f'ĐỎ — {loi} chỗ lệch'}")
sys.exit(1 if loi else 0)
