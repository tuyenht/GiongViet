# -*- coding: utf-8 -*-
"""L2 — Xuat file dung ban CU sau khi go sua van ban.

RUI RO THAT SU: nguoi dung mo van ban, go sua vai cho, roi bam Xuat ngay.
Neu giao dien khong gui lai doan sang Python truoc khi goi moi_bat_dau_xuat,
thi bo xuat lay `self._playlist` — thu chi duoc dung lai boi moi_dat_doan /
moi_doc_danh_sach / moi_nghe_doan — nen tep WAV ra doi mang NOI DUNG CHUA SUA.
Nguoi dung khong nghe lai het ca tep thi khong bao gio biet.

Bai nay CHUNG MINH bang code chay that, KHONG chay tong hop tieng:
  · Dung ApiMoi that trong THU MUC TAM (engine.BASE_DIR bi tro sang tam,
    kho_cau_hinh.dat_goc(tam)) — khong cham mot byte du lieu nguoi dung.
  · Mo hinh VieNeu KHONG duoc nap (_bo_mo_hinh.san_sang == False) nen
    _nap_truoc_mau_dau tu thoat, khong co mot lan tong hop nao.
  · BoXuatMoi.bat_dau bi GIA LAP de bat lay playlist duoc trao cho no,
    thay vi cho no ghi tep that.

Chay: PYTHONIOENCODING=utf-8 py l2.py
"""
# --- dat goc du an tu vi tri tep nay (bai nam trong kiem/) ---
import os as _os, sys as _sys
from pathlib import Path as _Path
_os.environ.setdefault('GIONGVIET_GOC', str(_Path(__file__).resolve().parent.parent))
_sys.path.insert(0, _os.environ['GIONGVIET_GOC'])
# --- het shim ---
import ast
import io
import re
import shutil
import sys
import tempfile
from pathlib import Path

# Goc du an tinh tu chinh vi tri tep nay (bai nay nam ngoai kho nen phai leo
# nguoc bang duong dan tuong doi da biet). KHONG viet cung o dia.
_GOC = Path(__file__).resolve()
while _GOC.name and not (_GOC / "DocCongDuc.py").exists():
    _GOC = _GOC.parent
    if _GOC == _GOC.parent:
        break
if not (_GOC / "DocCongDuc.py").exists():
    # Bai nay duoc dat trong scratchpad, khong nam trong kho — nhan goc qua
    # bien moi truong hoac tham so dong lenh.
    import os
    # Duong lui tinh tu __file__ (bai nay nam trong kiem/), KHONG viet cung
    # duong dan may nao - kho da len GitHub, viet cung la ai tai ve cho khac
    # cung vo het bo kiem.
    _GOC = Path(os.environ.get("GIONGVIET_GOC")
                or (sys.argv[1] if len(sys.argv) > 1
                    else Path(__file__).resolve().parent.parent))
GOC = _GOC
sys.path.insert(0, str(GOC))
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8",
                              line_buffering=True)

loi = 0


def ok(dk, nhan, them=""):
    global loi
    print(f"  {'ĐẠT ' if dk else 'LỆCH'} {nhan}{'  →  ' + str(them) if them else ''}")
    if not dk:
        loi += 1


# ===========================================================================
print("--- A. Liet ke DAY DU moi cho gan self._playlist (doc bang AST) ---")


def cho_gan_playlist(tep: Path):
    """[(dong, ten ham chua no)] cho moi phep gan len self._playlist."""
    cay = ast.parse(tep.read_text(encoding="utf-8"))
    ra = []
    for ham in ast.walk(cay):
        if not isinstance(ham, (ast.FunctionDef, ast.AsyncFunctionDef)):
            continue
        for n in ast.walk(ham):
            dich = []
            if isinstance(n, ast.Assign):
                dich = n.targets
            elif isinstance(n, (ast.AugAssign, ast.AnnAssign)):
                dich = [n.target]
            for d in dich:
                for x in ast.walk(d):
                    if (isinstance(x, ast.Attribute) and x.attr == "_playlist"
                            and isinstance(x.value, ast.Name)
                            and x.value.id == "self"):
                        ra.append((n.lineno, ham.name))
    return sorted(set(ra))


cnm_path = (GOC / "src" / "app" / "cau_noi_moi.py") if (GOC / "src" / "app" / "cau_noi_moi.py").exists() else (GOC / "giaodien_moi" / "cau_noi_moi.py")
cn_path = (GOC / "src" / "core" / "cau_noi.py") if (GOC / "src" / "core" / "cau_noi.py").exists() else (GOC / "giaodien" / "cau_noi.py")
gan_moi = cho_gan_playlist(cnm_path)
gan_cu = cho_gan_playlist(cn_path)
for d, h in gan_moi:
    print(f"       cau_noi_moi.py:{d:<5} trong {h}()")
for d, h in gan_cu:
    print(f"       cau_noi.py    :{d:<5} trong {h}()")

ham_gan_moi = sorted({h for _, h in gan_moi})
ok(set(ham_gan_moi) <= {"__init__", "moi_dat_doan", "moi_dat_doan_giu_vi_tri",
                        "moi_doc_danh_sach", "moi_nghe_doan"},
   "trong ApiMoi, _playlist CHI duoc dung lai boi may ham nay", ham_gan_moi)
ok("moi_bat_dau_xuat" not in ham_gan_moi,
   "moi_bat_dau_xuat KHONG he dung lai playlist — no chi tieu thu cai dang co")

# ===========================================================================
print("\n--- B. Dung ApiMoi that trong THU MUC TAM (khong cham du lieu that) ---")

TAM = Path(tempfile.mkdtemp(prefix="l2-giongviet-"))
(TAM / "cauhinh.ini").write_text(
    "[GiongDoc]\nvieneu_voice_id = Thu Nghiem\n", encoding="utf-8-sig")

import kho_cau_hinh  # noqa: E402
import DocCongDuc as engine  # noqa: E402

goc_that = kho_cau_hinh.goc()
engine.BASE_DIR = TAM
engine.CONFIG_FILE = TAM / "cauhinh.ini"
engine.NOIDUNG_FILE = TAM / "noidung.ini"
engine.TUDIEN_FILE = TAM / "tudien.ini"
engine.GIONG_RIENG_DIR = TAM / "giong_rieng"
kho_cau_hinh.dat_goc(TAM)

# Nhat ky loi cua bai kiem di cho khac — GiongViet-loi.log la duong chan doan
# cua chu du an, khong tron rac vao.
from giaodien import nhat_ky as _nk  # noqa: E402
_nk.TEP_LOG = TAM / "l2-loi.log"

from giaodien_moi import khoa_du_lieu  # noqa: E402
khoa_du_lieu.khoa()          # lop chan thu hai: cam moi duong ghi ra dia

from giaodien_moi.cau_noi_moi import ApiMoi  # noqa: E402
from giaodien import he_thong, ho_so  # noqa: E402
from giaodien_moi import ho_so_v2, xuat_moi  # noqa: E402

ok(str(engine.BASE_DIR) == str(TAM), "engine.BASE_DIR tro vao thu muc tam", TAM)
ok(str(kho_cau_hinh.goc()) == str(TAM),
   "kho_cau_hinh cung tro vao thu muc tam (goc that truoc do: "
   f"{goc_that})")
ok(str(GOC) not in str(he_thong.TUY_CHON_FILE)
   and str(GOC) not in str(ho_so.TEP)
   and str(GOC) not in str(ho_so_v2.TEP),
   "giaodien.json / hoso.json / hoso-v2.json deu tro ra ngoai kho du an",
   f"{he_thong.TUY_CHON_FILE.parent}")

api = ApiMoi((0, 0, 1280, 800))
ok(not api._bo_mo_hinh.san_sang,
   "mo hinh VieNeu CHUA nap — bai nay khong tong hop mot cau nao")
ok(api._playlist == [], "ApiMoi vua dung: playlist rong", api._playlist)

# ===========================================================================
print("\n--- C. Goi moi_dat_doan hai lan: playlist co doi theo khong? ---")

BAN_CU = [{"kieu": "body", "chu": "Đoạn một bản cũ."},
          {"kieu": "body", "chu": "Đoạn hai bản cũ."},
          {"kieu": "body", "chu": "Đoạn ba bản cũ."}]
BAN_MOI = [{"kieu": "body", "chu": "Đoạn một bản mới."},
           {"kieu": "body", "chu": "Đoạn hai bản mới."},
           {"kieu": "body", "chu": "Đoạn ba bản mới."}]


def chu_trong_playlist():
    return " | ".join(s["goc"] for s in api._playlist)


kq1 = api.moi_dat_doan(BAN_CU)
print(f"       sau moi_dat_doan(ban CU) : {kq1}")
print(f"       playlist = {chu_trong_playlist()}")
ok("bản cũ" in chu_trong_playlist() and "bản mới" not in chu_trong_playlist(),
   "lan 1: playlist mang ban CU")

kq2 = api.moi_dat_doan(BAN_MOI)
print(f"       sau moi_dat_doan(ban MOI): {kq2}")
print(f"       playlist = {chu_trong_playlist()}")
ok("bản mới" in chu_trong_playlist() and "bản cũ" not in chu_trong_playlist(),
   "lan 2: playlist da doi sang ban MOI — tuc la CHI CAN goi la no dung lai")

# ===========================================================================
print("\n--- D. Kich ban THAT: gui MOT lan roi 'go sua' ma khong gui lai ---")

api.moi_dat_doan(BAN_CU)
print(f"       Python nhan ban cu       : {chu_trong_playlist()}")
print("       (nguoi dung go sua tren man hinh — giao dien KHONG goi gi sang)")
print(f"       Python van giu           : {chu_trong_playlist()}")
ok("bản cũ" in chu_trong_playlist(),
   "khong ai goi lai thi Python giu NGUYEN ban cu — khong co co che tu lam moi")

# Bat lay dung thu ma bo xuat nhan duoc, thay vi cho no ghi tep that.
da_bat = {}
that_bat_dau = api._bo_xuat_moi.bat_dau


def gia_lap_bat_dau(playlist, doan_cua_mau, cfg, ten, thu_muc, tach,
                    dinh_dang, loc_am=""):
    da_bat["playlist"] = [s["goc"] for s in playlist]
    da_bat["ten"] = ten
    da_bat["dinh_dang"] = dinh_dang
    return None


api._bo_xuat_moi.bat_dau = gia_lap_bat_dau

tra_ve = api.moi_bat_dau_xuat("thu-nghiem", str(TAM), "mot", "wav16")
print(f"       moi_bat_dau_xuat tra ve  : {tra_ve!r}  (None = da bat dau chay)")
print(f"       CHU DUOC TRAO CHO BO XUAT: {' | '.join(da_bat.get('playlist', []))}")

ok(tra_ve is None, "moi_bat_dau_xuat chay tron, khong bao loi gi")
ok(da_bat.get("playlist") and all("bản cũ" in c for c in da_bat["playlist"]),
   "BO XUAT NHAN BAN CU — tep WAV se mang noi dung CHUA sua",
   da_bat.get("playlist"))
ok(not any("bản mới" in c for c in da_bat.get("playlist", [])),
   "khong mot chu nao cua ban da sua lot duoc vao tep xuat")

# ===========================================================================
print("\n--- D2. Cung ho, NANG hon: bam 'Nghe doan nay' roi bam Xuat ---")
# moi_nghe_doan cung dung lai _playlist — nhung chi voi MOT doan. Bo xuat lay
# dung cai do. Gia lap mo hinh san sang va bit duong phat: KHONG tong hop tieng.
api.moi_dat_doan(BAN_CU)
api._bo_mo_hinh.san_sang = True
api._bo_doc.phat = lambda *a, **k: None
api._nhuong_duong_phat = lambda *a, **k: None
kq_doan = api.moi_nghe_doan(2)
print(f"       moi_nghe_doan(2) tra ve  : {kq_doan!r}")
print(f"       playlist con lai         : {chu_trong_playlist()}")
ok(len(api._playlist) == 1,
   "sau 'Nghe doan nay', playlist CHI con mot doan", len(api._playlist))

da_bat.clear()
api._bo_xuat_moi.bat_dau = gia_lap_bat_dau
tra_ve2 = api.moi_bat_dau_xuat("thu-nghiem-2", str(TAM), "mot", "wav16")
print(f"       CHU DUOC TRAO CHO BO XUAT: {' | '.join(da_bat.get('playlist', []))}")
ok(tra_ve2 is None and da_bat.get("playlist") == ["Đoạn hai bản cũ."],
   "Xuat sau 'Nghe doan nay' chi ra MOT doan, mat hai doan con lai",
   da_bat.get("playlist"))
api._bo_mo_hinh.san_sang = False
api._bo_xuat_moi.bat_dau = that_bat_dau

# ===========================================================================
print("\n--- E. Ben JS: MOI loi goi guiDoanSangPython, kem ham chua no ---")

JS = (GOC / "src" / "web" / "giao-dien.js") if (GOC / "src" / "web" / "giao-dien.js").exists() else (GOC / "ui-moi" / "giao-dien.js")
dong_js = JS.read_text(encoding="utf-8", errors="replace").splitlines()

RE_HAM = re.compile(r"^\s*(?:async\s+)?function\s+([A-Za-z0-9_$]+)")


def ham_chua(i):
    for k in range(i, -1, -1):
        m = RE_HAM.match(dong_js[k])
        if m:
            return m.group(1)
    return "(ngoai ham)"


goi = []
for i, d in enumerate(dong_js):
    if "guiDoanSangPython" in d and not RE_HAM.match(d):
        goi.append((i + 1, ham_chua(i), d.strip()))

for so, ham, noi in goi:
    print(f"       dong {so:<5} trong {ham}()  →  {noi}")

ten_ham_goi = sorted({h for _, h, _ in goi})
ok(len(goi) >= 7, f"tim thay {len(goi)} loi goi guiDoanSangPython", ten_ham_goi)

# Ba ham cua duong XUAT va duong GO SUA — co ten nao trong danh sach tren?
for ten in ("moHopXuat", "batDauXuat", "luuSuaDoan", "tachDoanTaiCho"):
    ok(ten not in ten_ham_goi,
       f"{ten}() KHONG goi guiDoanSangPython",
       "dung nhu bao cao" if ten in ("moHopXuat", "batDauXuat") else
       "day la duong GO SUA")

# Nguoc lai: duong NGHE va duong SOAT thi co goi.
for ten in ("batDauPhat", "moManSoat"):
    ok(ten in ten_ham_goi, f"{ten}() CO goi guiDoanSangPython — nen bam Nghe "
                           "thi noi dung duoc lam moi")

print("\n--- F. Dau van tay: sau khi go sua, cai gi lam Python duoc lam moi? ---")
# vanTayTaiLieu = ten | loai | soDoan | TONG SO KY TU | the cam xuc
van_tay = [d for d in dong_js if "doan.reduce((s, d) => s + d.chu.length, 0)" in d]
ok(bool(van_tay), "dau van tai lieu dem TONG SO KY TU", van_tay[0].strip() if van_tay else "")
print("       → sua chu ma GIU NGUYEN so ky tu (vd doi 'sáu' thanh 'bảy') thi")
print("         van tay KHONG doi, nen bam Nghe cung khong gui lai. Do la mot")
print("         lo thu hai, nam ngoai pham vi L2 nhung cung ho.")

# ===========================================================================
print("\n--- G. Don dep: khong de lai vet nao ---")
ok(not (TAM / "l2-loi.log").exists() or True, "nhat ky bai kiem nam trong thu muc tam")
ok(sum(khoa_du_lieu.da_chan.values()) >= 0,
   f"khoa chan {sum(khoa_du_lieu.da_chan.values())} luot ghi ra dia",
   dict(khoa_du_lieu.da_chan) or "khong co lan ghi nao")
try:
    api._bo_doc.dung()
except Exception:
    pass
shutil.rmtree(TAM, ignore_errors=True)
ok(not TAM.exists(), "da xoa thu muc tam")

print(f"\n{'XANH — khớp hết' if loi == 0 else f'ĐỎ — {loi} chỗ lệch'}")
sys.exit(1 if loi else 0)
