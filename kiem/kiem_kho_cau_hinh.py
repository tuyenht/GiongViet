# -*- coding: utf-8 -*-
"""Kiem viec GOM cau hinh vao giongviet.db.

Day la cho DUY NHAT trong dot nay dung vao DU LIEU NGUOI DUNG, ma truoc bo kiem
nay khong co phep kiem nao canh no chay dung - chi co kiem_ro_ri_ghi canh chuyen
nguoc lai (bo kiem khong duoc ghi len kho that).

Rui ro that su o day khong phai "gom hong" ma la "gom nua voi": kho co du lieu
roi ma tep cu van nam nguyen, hoac te hon - tep cu bi don di khi kho CHUA co noi
dung. Ca hai deu tung xay ra trong luc lam.

Chay tren THU MUC TAM, khong cham mot byte nao cua nguoi dung.
"""
import io
import os
import shutil
import sys
import tempfile
from pathlib import Path

_GOC = str(Path(__file__).resolve().parent.parent)
sys.path.insert(0, _GOC)
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8",
                              line_buffering=True)

import kho_cau_hinh as kho  # noqa: E402

loi = 0


def ok(dk, nhan, them=""):
    global loi
    print(f"  {'ĐẠT ' if dk else 'LỆCH'} {nhan}{'  →  ' + str(them) if them else ''}")
    if not dk:
        loi += 1


def dung_thu_muc(tam: Path):
    """Dung mot thu muc giong that: sau tep cau hinh + congduc.txt."""
    (tam / "cauhinh.ini").write_text("[GiongDoc]\nvieneu_voice_id = Thử\n", encoding="utf-8-sig")
    (tam / "tudien.ini").write_text("[ThayThe]\nABC=a bờ cờ\n", encoding="utf-8-sig")
    (tam / "noidung.ini").write_text("[DauDanhSach]\nbat_dau=1\n", encoding="utf-8-sig")
    (tam / "hoso.json").write_text('{"dangDung":"a","dsHoSo":[]}', encoding="utf-8")
    (tam / "giaodien.json").write_text('{"theme":"sang"}', encoding="utf-8")
    (tam / "hoso-v2.json").write_text('{"phienBan":1,"hoSo":[]}', encoding="utf-8")
    (tam / "congduc.txt").write_text("Nguyễn Văn A - 500.000\n", encoding="utf-8")


print("--- A. Gom lan dau: 6 tep vao kho, tep cu doi sang sao-luu-cu ---")
tam = Path(tempfile.mkdtemp())
dung_thu_muc(tam)
kho.dat_goc(tam)

ok(kho.doc("cauhinh.ini") is None, "kho chua co gi truoc khi gom")
ok(not (tam / kho.TEN_KHO).exists(),
   "CHI DOC thi KHONG de ra tep kho - sqlite3.connect tu tao file, "
   "bo kiem tung de lai mot giongviet.db rong giua thu muc du an")

ket = kho.nhap_tu_tep_cu()
ok(len(ket) == 6, "gom dung 6 tep", sorted(ket))
con_lai = sorted(p.name for p in tam.glob("*") if p.is_file())
ok(con_lai == ["congduc.txt", kho.TEN_KHO], "thu muc chi con congduc.txt va kho", con_lai)
ok((tam / kho.THU_MUC_SAO_LUU).is_dir(), "co thu muc sao-luu-cu")
ok(len(list((tam / kho.THU_MUC_SAO_LUU).glob("*"))) == 6, "sao luu du 6 tep")

print("\n--- B. congduc.txt CO Y khong gom ---")
ok(kho.doc("congduc.txt") is None,
   "van ban nguoi dung tu soan van la tep roi, mo bang Notepad duoc")
ok((tam / "congduc.txt").exists(), "congduc.txt con nguyen tai cho")

print("\n--- C. Doc lai dung nguyen van, ke ca BOM ---")
ok(kho.doc("cauhinh.ini").startswith("[GiongDoc]"), "cauhinh.ini nguyen noi dung",
   repr(kho.doc("cauhinh.ini")[:22]))
ok("a bờ cờ" in kho.doc("tudien.ini"), "tudien.ini giu dung chu co dau")
ok(kho.doc("hoso-v2.json") == '{"phienBan":1,"hoSo":[]}', "json nguyen van")

print("\n--- D. Chay lai lan hai KHONG lam mat thiet lap moi ---")
kho.ghi("giaodien.json", '{"theme":"toi"}')
kho.nhap_tu_tep_cu()
ok(kho.doc("giaodien.json") == '{"theme":"toi"}',
   "gom lan hai khong de ban cu de len ban moi", kho.doc("giaodien.json"))

print("\n--- E. Don HUT lan dau thi lan sau van don duoc ---")
# Dung lai canh da gap that: kho co noi dung roi ma tep cu van nam nguyen.
(tam / "cauhinh.ini").write_text("[GiongDoc]\nbi ket lai\n", encoding="utf-8-sig")
ok((tam / "cauhinh.ini").exists(), "dung lai canh tep cu ket lai")
truoc = kho.doc("cauhinh.ini")
kho.nhap_tu_tep_cu()
ok(not (tam / "cauhinh.ini").exists(),
   "lan chay sau DON duoc tep ket lai - ban truoc gop viec gom voi viec don nen "
   "he kho da co la bo qua luon, tep ket vinh vien")
ok(kho.doc("cauhinh.ini") == truoc,
   "va KHONG lay noi dung tep ket lai de len kho", repr(kho.doc("cauhinh.ini")[:22]))

print("\n--- F. Duong lui: ghi nguoc ca kho ra tep ---")
ra = tam / "xuat-thu"
so = kho.xuat_ra_tep(ra)
ok(so == 6, "xuat ra dung 6 tep", so)
ok((ra / "cauhinh.ini").read_text(encoding="utf-8").startswith("[GiongDoc]"),
   "tep xuat ra doc lai duoc bang Notepad")

print("\n--- G. Duong dan NGOAI thu muc chuong trinh khong duoc dung vao kho ---")
import DocCongDuc as engine  # noqa: E402
ngoai = Path(tempfile.mkdtemp()) / "cauhinh.ini"
ngoai.write_text("[GiongDoc]\nngoai kho\n", encoding="utf-8")
ok(not engine._thuoc_kho(ngoai),
   "tep cung TEN nhung khac thu muc thi khong tinh la cua kho - thieu chan nay "
   "thi bo kiem ghi thang vao kho that, da xay ra")
ok(engine.doc_tep_cau_hinh(ngoai).strip().endswith("ngoai kho"),
   "van doc duoc tep roi o ngoai binh thuong")

shutil.rmtree(tam, ignore_errors=True)
shutil.rmtree(ngoai.parent, ignore_errors=True)

print(f"\n{'XANH — khớp hết' if loi == 0 else f'ĐỎ — {loi} chỗ lệch'}")
sys.exit(1 if loi else 0)
