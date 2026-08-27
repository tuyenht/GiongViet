# -*- coding: utf-8 -*-
"""Phep thu tich hop: dung ApiMoi THAT roi bam loan, do mtime 6 tep du lieu.

Day la phep kiem ma chu du an yeu cau: "chup mtime 6 tep du lieu truoc/sau mot
phien bam loan - phai KHONG doi". kiem_khoa_du_lieu.py chi kiem tung ham roi;
bai nay di qua dung con duong ma giao dien that di: ApiMoi -> Api -> engine.

AN TOAN HAI LOP:
  1. Sao luu 6 tep vao thu muc tam TRUOC khi cham vao gi.
  2. Tep nao doi thi KHOI PHUC ngay lap tuc roi moi bao DO.
Khong mo cua so: Api.__init__ chi dung doi tuong, mo hinh chi tai khi goi
bat_dau() - bai nay khong goi.
"""
import hashlib
import io
import shutil
import sys
import tempfile
from pathlib import Path

# Goc du an, tinh tu chinh vi tri tep nay. KHONG viet cung duong dan:
# kho da len GitHub, ai tai ve cho khac la vo het bo kiem.
_GOC = str(Path(__file__).resolve().parent.parent)
sys.path.insert(0, _GOC)
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8")

GOC = Path(_GOC)
TEP_DU_LIEU = ["cauhinh.ini", "hoso.json", "congduc.txt", "noidung.ini",
               "tudien.ini", "giaodien.json"]

SAO_LUU = Path(tempfile.gettempdir()) / "gd-bam-loan-sao-luu"
if SAO_LUU.exists():
    shutil.rmtree(SAO_LUU)
SAO_LUU.mkdir(parents=True)


def dau_van(p: Path):
    """(mtime, bam noi dung). Chi so mtime la du, nhung mot lan ghi de dung y
    noi dung cu trong cung mot giay thi mtime co the khong doi."""
    b = p.read_bytes()
    return p.stat().st_mtime_ns, hashlib.sha256(b).hexdigest()


truoc = {}
for t in TEP_DU_LIEU:
    p = GOC / t
    if p.exists():
        shutil.copy2(p, SAO_LUU / t)
        truoc[t] = dau_van(p)

loi = 0


def ok(dk, nhan, them=""):
    global loi
    print(f"  {'ĐẠT ' if dk else 'LỆCH'} {nhan}{'  →  ' + str(them) if them else ''}")
    if not dk:
        loi += 1


print(f"--- A. Sao luu {len(truoc)} tep du lieu truoc khi bat dau ---")
ok(len(truoc) >= 1 or (GOC / "giongviet.db").exists() or (GOC / "data" / "giongviet.db").exists(),
   "chup dau van du lieu nguoi dung (file roi hoac giongviet.db)", sorted(truoc))

print("\n--- B. Dung ApiMoi that (khong mo cua so, khong tai mo hinh) ---")
from src.app import khoa_du_lieu
from src.app.cau_noi_moi import ApiMoi

# Nhat ky loi cua bai do di cho khac - GiongViet-loi.log la duong chan doan cua
# chu du an, khong tron rac vao. Ra ca ho sau khi vap: 15 dong loi cua bai kiem
# tung nam trong log that.
import tempfile as _tf
from pathlib import Path as _P

from src.core import nhat_ky as _nk
_nk.TEP_LOG = _P(_tf.gettempdir()) / "gd-kiem-loi.log"

khoa_du_lieu.khoa()          # BAT BUOC: ApiMoi khong tu khoa nua
api = ApiMoi((0, 0, 1280, 800))
ok(khoa_du_lieu.dang_khoa(), "ApiMoi tu khoa duong ghi ngay trong __init__")
ok(khoa_du_lieu.con_ho() == [], "khong con cua ra nao ho", khoa_du_lieu.con_ho())

print("\n--- C. Bam loan: goi that cac ham von ghi de du lieu nguoi dung ---")
khoa_du_lieu.da_chan.clear()
giong_cu = api._cfg.get("vieneu_voice_id", "")
da_goi = []


def bam(ten, *ts):
    try:
        getattr(api, ten)(*ts)
        da_goi.append(ten)
    except Exception as e:                      # noqa: BLE001 - bai kiem, can biet het
        print(f"       (bo qua {ten}: {type(e).__name__} {e})")


bam("doi_giong", "Thái Sơn")
bam("doi_giong", "Một Giọng Không Có Thật")
bam("doi_phong_cach", "Kể chuyện - tâm tình")
bam("dat_thong_so", "nghi_cau", 0.9)
bam("dat_thong_so", "so_ky_tu", 120)
bam("luu_theme", "dark")
bam("luu_zoom", 170)
bam("dat_cai_dat", "doc_so_bang_chu", False)
bam("dat_cai_dat", "bo_markdown", False)
bam("dat_cai_dat", "theme", "dark")
bam("dat_cai_dat", "zoom", 190)
bam("them_ho_so", "Ho so thu nghiem", "congduc")
bam("sua_ten_ho_so", api._kho_ho_so["dangDung"], "Doi ten thu")
bam("them_tu", "abc", "a bờ cờ")
bam("sua_tu", "abc", "abc", "a bê xê")
bam("xoa_tu", "abc")
bam("doi_ho_so", api._kho_ho_so["dsHoSo"][0]["ma"])
bam("xoa_ho_so", api._kho_ho_so["dsHoSo"][-1]["ma"])
ok(len(da_goi) >= 15, f"goi duoc {len(da_goi)} phuong thuc ghi", da_goi)
ok(api._cfg.get("vieneu_voice_id") != giong_cu,
   "cfg TRONG BO NHO van doi (chuc nang giu nguyen)",
   f"{giong_cu} -> {api._cfg.get('vieneu_voice_id')}")
ok(sum(khoa_du_lieu.da_chan.values()) > 0,
   f"khoa chan {sum(khoa_du_lieu.da_chan.values())} luot ghi",
   dict(khoa_du_lieu.da_chan))

print("\n--- D. 6 tep du lieu nguoi dung: mtime va noi dung KHONG doi ---")
hong = []
for t, dv in truoc.items():
    p = GOC / t
    nay = dau_van(p)
    con_nguyen = nay == dv
    if not con_nguyen:
        hong.append(t)
    ok(con_nguyen, f"{t} nguyen ven",
       "" if con_nguyen else f"mtime {dv[0]} -> {nay[0]}")

if hong:
    print(f"\n  !! KHOI PHUC {len(hong)} tep tu ban sao luu ngay lap tuc")
    for t in hong:
        shutil.copy2(SAO_LUU / t, GOC / t)
        print(f"     da tra lai {t}")

print("\n--- E. Khong de lai tep la trong thu muc chuong trinh ---")
la = [p.name for p in GOC.glob("noidung-*.ini")]
ok(not la, "khong de ra noidung-*.ini nao", la or "sach")
tam = [p.name for p in GOC.glob("*.tam")]
ok(not tam, "khong bo lai tep .tam", tam or "sach")

print("\n--- F. hoso-v2.json van ghi duoc binh thuong ---")
from src.app import ho_so_v2
tam_v2 = Path(tempfile.gettempdir()) / "gd-bam-loan-v2.json"
that_v2 = ho_so_v2.TEP
ho_so_v2.TEP = tam_v2
try:
    ok(api.moi_luu_ho_so({"hoSo": [{"ma": "a", "ten": "T", "giong": "g",
                                    "tep": ["x.txt"]}]}) is True,
       "moi_luu_ho_so ghi duoc khi da khoa")
    d = api.moi_doc_ho_so()
    ok(d and d["hoSo"][0]["ten"] == "T", "moi_doc_ho_so doc lai dung")
finally:
    ho_so_v2.TEP = that_v2
    tam_v2.unlink(missing_ok=True)

print(f"       (hoso-v2.json that: "
      f"{'da co' if (GOC / 'hoso-v2.json').exists() else 'chua tao lan nao'})")

api._don_dep()
shutil.rmtree(SAO_LUU, ignore_errors=True)
print(f"\n{'XANH — khớp hết' if loi == 0 else f'ĐỎ — {loi} chỗ lệch'}")
sys.exit(1 if loi else 0)
