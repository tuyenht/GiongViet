# -*- coding: utf-8 -*-
"""L6 - Kiem lai dong "Sua loi dan bang Notepad bi ghi de am tham".

BAO CAO CU noi: GiongViet.py:175 goi xuat_ra_tep(BASE_DIR/'sao-luu-cu') moi lan
thoat, ghi de moi tep trong do. Nen (a) trong sao-luu-cu/ LUON co mot noidung.ini
doc duoc va moi; (b) nguoi dung sua no bang Notepad thi lan doc sau van lay ban
trong kho; (c) lan dong chuong trinh ke tiep, ban ho vua go bi ghi de mat.

RUI RO THAT SU can lam ro - khong phai "ghi de" ma la NGUOI DUNG CO DUONG NAO
DE SUA LOI DAN KHONG. sao-luu-cu/ la DAU RA hay DAU VAO? Neu no chi la ban dump
chan doan, khong nam tren bat ky duong doc nao, thi "ghi de" no khong lam mat gi
CO TAC DUNG - va ket luan cu dang xep sai loai loi.

Bai nay do bon thu:
  A. Kho THAT tren may nay chua nhung gi -> tien de (a) dung hay sai.
  B. Chay that trong thu muc tam: gom -> xuat -> sua tay -> xuat lai.
  C. sao-luu-cu/ co nam tren duong DOC nao khong.
  D. Sau khi gom, nguoi dung con duong nao sua loi dan khong.

KHONG cham mot byte du lieu nguoi dung: kho that chi duoc CHEP ra thu muc tam
roi doc ban chep. Cuoi bai in lai van tay md5 de doi chieu.
KHONG nap mo hinh, KHONG tong hop tieng.
"""
# --- dat goc du an tu vi tri tep nay (bai nam trong kiem/) ---
import os as _os, sys as _sys
from pathlib import Path as _Path
_os.environ.setdefault('GIONGVIET_GOC', str(_Path(__file__).resolve().parent.parent))
_sys.path.insert(0, _os.environ['GIONGVIET_GOC'])
# --- het shim ---
import hashlib
import io
import os
import shutil
import sqlite3
import sys
import tempfile
from pathlib import Path

# Bai nay nay da nam trong kiem/ nen goc du an chinh la thu muc cha. Shim o dau
# tep da dat GIONGVIET_GOC theo __file__; duong lui cung tinh tu __file__ chu
# KHONG viet cung duong dan may nao - kho da len GitHub.
_GOC = Path(os.environ.get("GIONGVIET_GOC")
            or Path(__file__).resolve().parent.parent)
sys.path.insert(0, str(_GOC))
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8",
                              line_buffering=True)

BUNDLE = _GOC / "data" if (_GOC / "data" / "giongviet.db").exists() else (_GOC / "GiongViet" if (_GOC / "GiongViet" / "giongviet.db").exists() else _GOC)

loi = 0


def ok(dk, nhan, them=""):
    global loi
    print(f"  {'ĐẠT ' if dk else 'LỆCH'} {nhan}{'  →  ' + str(them) if them else ''}")
    if not dk:
        loi += 1


def md5(p: Path) -> str:
    return hashlib.md5(p.read_bytes()).hexdigest()[:12] if p.exists() else "(khong co)"


CANH = ["cauhinh.ini", "noidung.ini", "tudien.ini", "giaodien.json",
        "hoso.json", "hoso-v2.json", "congduc.txt", "giongviet.db"]
VAN_TAY_TRUOC = {t: md5(BUNDLE / t) for t in CANH}
VAN_TAY_TRUOC_GOC = {t: md5(_GOC / t) for t in CANH}

# ---------------------------------------------------------------------------
print("=== A. KHO THAT tren may nay chua nhung gi (doc ban CHEP, chi doc) ===")

tam_soi = Path(tempfile.mkdtemp(prefix="l6-soi-"))
ban_sao_db = tam_soi / "ban-sao.db"
shutil.copy2(BUNDLE / "giongviet.db", ban_sao_db)
cn = sqlite3.connect(ban_sao_db)
ban_ghi = list(cn.execute("SELECT ten, length(noi_dung) FROM tep ORDER BY ten"))
cn.close()
print(f"  giongviet.db that: {(BUNDLE / 'giongviet.db').stat().st_size} byte")
for ten, dai in ban_ghi:
    print(f"    ban ghi: {ten:16s} {dai} ky tu")

ten_trong_kho = [t for t, _ in ban_ghi]
ok(len(ban_ghi) == 3, "kho that CHI co 3 ban ghi", ten_trong_kho)
ok("noidung.ini" not in ten_trong_kho,
   "kho that KHONG co noidung.ini -> xuat_ra_tep khong the de ra noidung.ini")

thuc_te = sorted(p.name for p in (BUNDLE / "sao-luu-cu").glob("*"))
print(f"  sao-luu-cu/ that: {thuc_te}")
ok(thuc_te == sorted(ten_trong_kho),
   "sao-luu-cu/ that khop DUNG danh sach ban ghi trong kho, khong hon khong kem")
ok("noidung.ini" not in thuc_te,
   "TIEN DE (a) CUA BAO CAO CU SAI: sao-luu-cu/ KHONG co noidung.ini")

con_o_goc = sorted(p.name for p in BUNDLE.glob("*.ini")) + \
            sorted(p.name for p in BUNDLE.glob("*.json"))
print(f"  goc thu muc cai dat van con: {con_o_goc}")
ok("noidung.ini" in con_o_goc,
   "noidung.ini van nam NGUYEN o goc thu muc cai dat, chua bi gom lan nao")

# ---------------------------------------------------------------------------
print("\n=== B. Vi sao chi ra ba tep: xuat_ra_tep lap theo danh_sach() cua kho ===")
from src.core import kho_cau_hinh as kho  # noqa: E402
import DocCongDuc as engine  # noqa: E402

# engine.import da goi dat_goc(BASE_DIR that). Keo ngay ve thu muc tam.
print(f"  kho.goc() ngay sau khi import engine: {kho.goc()}")
tam = Path(tempfile.mkdtemp(prefix="l6-chay-"))
kho.dat_goc(tam)
ok(kho.goc() == tam, "da keo kho ve thu muc tam", tam)
print(f"  TEP_GOM khai bao trong ma nguon: {kho.TEP_GOM}")
ok("noidung.ini" in kho.TEP_GOM,
   "noidung.ini CO trong danh sach duoc gom -> may khac se gom no that")

# ---------------------------------------------------------------------------
print("\n=== C. Dung lai NGUYEN TRANG thu muc cai dat trong thu muc tam ===")
print("     (chep db that + 7 tep that sang tam, roi mo phong LAN KHOI DONG KE TIEP)")
for t in CANH:
    if (BUNDLE / t).exists():
        shutil.copy2(BUNDLE / t, tam / t)
print(f"  truoc khi gom, goc tam co: {sorted(p.name for p in tam.glob('*'))}")
print(f"  truoc khi gom, kho co:     {kho.danh_sach()}")

ket = kho.nhap_tu_tep_cu()
print(f"  ket qua nhap_tu_tep_cu(): {ket}")
sau_goc = sorted(p.name for p in tam.glob("*") if p.is_file())
sau_luu = sorted(p.name for p in (tam / kho.THU_MUC_SAO_LUU).glob("*") if p.is_file())
print(f"  sau khi gom, goc tam con:  {sau_goc}")
print(f"  sau khi gom, sao luu:      {sau_luu}")
print(f"  sau khi gom, kho co:       {kho.danh_sach()}")

ok(not (tam / "noidung.ini").exists(),
   "LAN KHOI DONG KE TIEP: noidung.ini BIEN MAT khoi goc thu muc cai dat")
ok("noidung.ini" in sau_luu, f"noidung.ini bi DOI sang {kho.THU_MUC_SAO_LUU}/")
ok("noidung.ini" in kho.danh_sach(), "va noi dung no nam trong kho")
ok("congduc.txt" in sau_goc, "congduc.txt co y KHONG gom, van nam tai cho")

# ---------------------------------------------------------------------------
print("\n=== D. Sau khi gom, nguoi dung con duong nao sua loi dan? ===")
from src.core import he_thong  # noqa: E402

# Chan os.startfile: bai kiem TUYET DOI khong duoc mo Notepad tren man hinh
# nguoi dung. Ghi lai loi goi thay vi thuc thi.
da_mo = []
os.startfile = lambda p: da_mo.append(p)          # noqa: E731

thong_bao = he_thong.mo_bang_chuong_trinh_mac_dinh(tam / "noidung.ini")
print(f"  he_thong.mo_bang_chuong_trinh_mac_dinh(goc/noidung.ini) -> {thong_bao!r}")
ok(thong_bao.startswith("Không tìm thấy tệp"),
   "nut 'Sua loi dan' (cau_noi.sua_file) tro vao tep roi o GOC -> nay bao LOI")
ok(not da_mo, "khong mo Notepad nao cua nguoi dung", da_mo or "sach")

# Nguoi dung tu tao lai tep roi o goc roi go noi dung moi (Notepad luu file moi)
(tam / "noidung.ini").write_text(
    "[DauDanhSach]\nbat_dau=1\nnoi_dung=BAN NGUOI DUNG VUA GO O GOC\n",
    encoding="utf-8")
doc_duoc = engine.doc_tep_cau_hinh(tam / "noidung.ini")
print(f"  engine.doc_tep_cau_hinh(goc/noidung.ini) tra ve 60 ky tu dau: "
      f"{doc_duoc[:60]!r}")
ok("BAN NGUOI DUNG VUA GO O GOC" not in doc_duoc,
   "go lai tep roi o GOC cung VO ICH: kho co muc ay nen doc_tep_cau_hinh "
   "lay ban trong kho, bo qua tep roi")
nd = engine.NoiDung().load(tam / "noidung.ini")
ok("BAN NGUOI DUNG VUA GO O GOC" not in nd.dau_text,
   "NoiDung.load cung khong thay chu vua go", repr(nd.dau_text[:40]))
(tam / "noidung.ini").unlink()

# ---------------------------------------------------------------------------
print("\n=== E. Ghi de trong sao-luu-cu: co that khong? ===")
so_lan_1 = kho.xuat_ra_tep(tam / "sao-luu-cu")
print(f"  xuat_ra_tep lan 1 (mo phong lan thoat thu nhat): ghi {so_lan_1} tep")

tep_sua = tam / "sao-luu-cu" / "noidung.ini"
NGUOI_DUNG_GO = ("[DauDanhSach]\nbat_dau=1\n"
                 "noi_dung=Nam Mo A Di Da Phat - BAN NGUOI DUNG SUA BANG NOTEPAD\n")
tep_sua.write_text(NGUOI_DUNG_GO, encoding="utf-8")
truoc = tep_sua.read_text(encoding="utf-8")
print(f"  nguoi dung sua tay sao-luu-cu/noidung.ini -> {len(truoc)} ky tu, "
      f"dong 3: {truoc.splitlines()[2][:55]!r}")

doc_lai = engine.doc_tep_cau_hinh(tam / "noidung.ini")
ok("BAN NGUOI DUNG SUA BANG NOTEPAD" not in doc_lai,
   "(b) DUNG: sua trong sao-luu-cu KHONG vao duoc chuong trinh, doc van ra ban kho")

so_lan_2 = kho.xuat_ra_tep(tam / "sao-luu-cu")
sau = tep_sua.read_text(encoding="utf-8")
print(f"  xuat_ra_tep lan 2 (mo phong lan thoat ke tiep): ghi {so_lan_2} tep")
print(f"  sao-luu-cu/noidung.ini sau lan 2 -> {len(sau)} ky tu, "
      f"60 ky tu dau: {sau[:60]!r}")
ok(sau != truoc, "(c) DUNG: ban nguoi dung vua go BI GHI DE, khong hoi mot cau")
ok("BAN NGUOI DUNG SUA BANG NOTEPAD" not in sau, "chu vua go bien mat hoan toan")

# ---------------------------------------------------------------------------
print("\n=== F. sao-luu-cu/ co nam tren duong DOC nao khong? ===")
ok(not engine._thuoc_kho(tam / "sao-luu-cu" / "noidung.ini"),
   "tep trong sao-luu-cu/ KHONG duoc tinh la cua kho (khac thu muc)")
rieng = engine.doc_tep_cau_hinh(tam / "sao-luu-cu" / "noidung.ini")
ok("BAN NGUOI DUNG SUA BANG NOTEPAD" not in rieng,
   "sau khi bi ghi de, doc thang tep do cung chi ra lai noi dung kho")
nguon_gv = (_GOC / "GiongViet.py").read_text(encoding="utf-8")
ok(nguon_gv.count("xuat_ra_tep") == 1,
   "trong GiongViet.py, sao-luu-cu chi xuat hien o duong GHI (luc thoat), "
   "khong co mot loi DOC nao")
so_doc = sum(1 for p in list(_GOC.glob("*.py")) + list((_GOC / "src" / "core").glob("*.py"))
             + list((_GOC / "src" / "app").glob("*.py"))
             if "THU_MUC_SAO_LUU" in p.read_text(encoding="utf-8")
             or "sao-luu-cu" in p.read_text(encoding="utf-8"))
print(f"  so tep .py nhac den sao-luu-cu: {so_doc}")
ok(so_doc <= 2, "chi kho_cau_hinh.py (dinh nghia + ghi) va GiongViet.py (ghi) "
                "nhac den no", so_doc)

# ---------------------------------------------------------------------------
print("\n=== G. Ban sao AN TOAN goc bi bao mon: mat BOM va mat anh chup goc ===")
tam3 = Path(tempfile.mkdtemp(prefix="l6-bom-"))
(tam3 / "cauhinh.ini").write_text("[GiongDoc]\nvieneu_voice_id = A\n",
                                  encoding="utf-8-sig")
goc_bytes = (tam3 / "cauhinh.ini").read_bytes()
kho.dat_goc(tam3)
kho.nhap_tu_tep_cu()
sau_doi = (tam3 / kho.THU_MUC_SAO_LUU / "cauhinh.ini").read_bytes()
BOM = b"\xef\xbb\xbf"
ok(sau_doi == goc_bytes, "vua doi xong, ban sao con y nguyen tung byte (co BOM)",
   "co BOM" if sau_doi[:3] == BOM else "MAT BOM")
kho.ghi("cauhinh.ini", "[GiongDoc]\nvieneu_voice_id = B\n")   # nguoi dung doi giong
kho.xuat_ra_tep(tam3 / kho.THU_MUC_SAO_LUU)
sau_xuat = (tam3 / kho.THU_MUC_SAO_LUU / "cauhinh.ini").read_bytes()
print(f"  truoc: {goc_bytes!r}")
print(f"  sau  : {sau_xuat!r}")
ok(sau_xuat != goc_bytes,
   "sau mot lan thoat, ban sao KHONG con la anh chup goc nua ma la guong cua kho")
ok(sau_xuat[:3] != BOM,
   "va mat luon BOM utf-8-sig ma ban goc co (xuat_ra_tep ghi utf-8 tran)")

# ---------------------------------------------------------------------------
print("\n=== H. Van tay du lieu nguoi dung: truoc va sau khi chay bai nay ===")
for t in CANH:
    sau_ = md5(BUNDLE / t)
    ok(sau_ == VAN_TAY_TRUOC[t], f"GiongViet/{t}", f"{VAN_TAY_TRUOC[t]} -> {sau_}")
for t in CANH:
    sau_ = md5(_GOC / t)
    ok(sau_ == VAN_TAY_TRUOC_GOC[t], f"goc/{t}", f"{VAN_TAY_TRUOC_GOC[t]} -> {sau_}")

for d in (tam, tam_soi, tam3):
    shutil.rmtree(d, ignore_errors=True)

print(f"\n{'XANH — khớp hết' if loi == 0 else f'ĐỎ — {loi} chỗ lệch'}")
sys.exit(1 if loi else 0)
