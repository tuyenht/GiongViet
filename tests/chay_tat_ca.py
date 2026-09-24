# -*- coding: utf-8 -*-
"""Chay ca bo kiem va DOC GIUM ket qua cho dung.

VI SAO CAN TEP NAY - da tra gia that, hai lan trong mot phien:

  1. `NghiemThu.py` tim duong dan CU ("ffmpeg/bin/ffplay.exe") sau khi cay thu
     muc doi. No bao "ban .exe thieu ffplay" va viec do bi xep muc "rat cao".
     Bundle khong thieu gi ca - DongGoi.bat noi junction dung ten MOI.

  2. Bon bai L1/L2/L5/L6 dang DO. Do voi chung nghia la LOI DA DUOC VA. Nhung
     nhin bang liet ke "do = hong" thi ca bon bi xep vao "loi dang bao dong",
     va suyt co mot dot di chua bon cai loi khong con ton tai.

Bo kiem nay co HAI LOAI bai, doc nguoc la di chua loi khong co that:

  · BAI CANH         -> XANH la tot. Da so bai thuoc loai nay.
  · BAI TAI HIEN LOI -> XANH nghia la LOI CON NGUYEN, DO nghia la DA VA XONG.
                        Nhan ra chung bang ma "L1".."L7" o dau docstring.

Ma L chi la SUY DOAN. Bai nao da duoc dao menh de thanh bai canh hoi quy thi
khai bao mot dong  LOAI_BAI = "canh"  o dau tep, bang ket qua se doc dong do
thay vi suy tu ma L. Tep nay khong tu doan bua - doan sai con te hon khong doan.

CHAY:
    py tests/chay_tat_ca.py            # bo qua cac bai mo cua so / phat tieng
    py tests/chay_tat_ca.py --tat-ca   # chay ca chung (se chiem man hinh)
"""
import io
import os
import re
import subprocess
import sys
import time
from pathlib import Path

GOC = Path(__file__).resolve().parent.parent
THU_MUC = GOC / "tests"
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8")

# Cac bai MO CUA SO THAT hoac PHAT TIENG THAT. CLAUDE.md cam chiem foreground
# cua chu du an khi ho dang lam viec, nen mac dinh bo qua.
#
# Rieng NghiemThu.py con la bai BAN THU CONG: no dung lai cho NGUOI bam nut
# (vi du "bam Huy Xuat khi phan tram dang chay") roi dem nguoc. Chay tu dong
# thi no dem het gio roi bo qua muc do - khong phai hong, nhung cung khong
# chung minh duoc gi. Muon dung no thi phai ngoi truoc may.
CHIEM_MAN_HINH = {
    "KiemBanExe.py", "NghiemThu.py", "TuKiemGiaoDien.py", "chay_thu_tieng.py",
    "do_cach_phat.py", "do_tre_phat.py", "do_phan_ra_tre.py",
}

HET_GIO = 300  # giay cho moi bai

_MA_L = re.compile(r"(?:T[aá]i hi[eệ]n(?: LOI| L[OÔ]I)?\s*)?(L\d)\b", re.I)
_KHAI_BAO = re.compile(r"^LOAI_BAI\s*=\s*['\"](\w+)['\"]", re.M)


def doc_nhan(tep):
    """Tra ve (ma_loi, dong dau docstring, loai khai bao) cua mot bai kiem."""
    try:
        dau = tep.read_text(encoding="utf-8", errors="replace")[:1400]
    except OSError:
        return None, "", None
    m = re.search(r'"""(.*?)(?:\n|""")', dau, re.S)
    dong1 = m.group(1).strip() if m else ""
    ma = _MA_L.match(dong1)
    kb = _KHAI_BAO.search(dau)
    return (ma.group(1).upper() if ma else None), dong1, (kb.group(1) if kb else None)


def chay(tep):
    lenh = ["node", str(tep)] if tep.suffix == ".mjs" else [sys.executable, str(tep)]
    t0 = time.perf_counter()
    try:
        r = subprocess.run(lenh, cwd=str(GOC), capture_output=True, timeout=HET_GIO,
                           env={**os.environ, "PYTHONIOENCODING": "utf-8"})
        ra = (r.stdout or b"").decode("utf-8", "replace").rstrip().split("\n")
        cuoi = next((d.strip() for d in reversed(ra) if d.strip()), "(khong co dau ra)")
        return r.returncode, cuoi[:52], time.perf_counter() - t0
    except subprocess.TimeoutExpired:
        return None, "QUA {}s - chua do duoc".format(HET_GIO), time.perf_counter() - t0


def main():
    tat_ca = "--tat-ca" in sys.argv
    bai = sorted(
        [p for p in THU_MUC.glob("*.py")
         if p.name not in ("chay_tat_ca.py", "sitecustomize.py")]
        + list(THU_MUC.glob("*.mjs")),
        key=lambda p: p.name.lower())

    co_ma, thuong, bo_qua = [], [], []
    for p in bai:
        if not tat_ca and p.name in CHIEM_MAN_HINH:
            bo_qua.append(p.name)
            continue
        ma, dong1, loai = doc_nhan(p)
        rc, cuoi, _ = chay(p)
        muc = (p.name, ma, dong1, rc, cuoi, loai)
        (co_ma if (ma and loai != "canh") else thuong).append(muc)
        dau = "?" if rc is None else ("xanh" if rc == 0 else "do")
        print("  [{:>4}] {:<32} {}".format(dau, p.name, cuoi))

    print("\n" + "=" * 78)
    print("BAI CO MA LOI — DOC NGUOC LA DI CHUA LOI KHONG CO THAT")
    print("  Voi nhung bai nay: XANH = loi con nguyen · DO = loi da duoc va.")
    print("=" * 78)
    for ten, ma, dong1, rc, _cuoi, _loai in sorted(co_ma, key=lambda x: x[1]):
        if rc is None:
            dau, y = "?", "chua do duoc"
        elif rc == 0:
            dau, y = "XANH", "theo quy uoc: loi CON nguyen"
        else:
            dau, y = "DO", "theo quy uoc: loi da duoc VA"
        print("  {}  {:<30} {:<5}  {}".format(ma, ten, dau, y))
        print("        {}".format(dong1[:86]))
    print("\n  Quy uoc tren SUY RA tu ma L o docstring, chua phai su that da kiem")
    print("  chung tung bai. Bai nao da dao menh de thanh bai canh hoi quy thi")
    print('  them mot dong  LOAI_BAI = "canh"  o dau tep, bang nay se doc dong do.')

    hong = [x for x in thuong if x[3] not in (0, None)]
    cho = [x for x in thuong if x[3] is None]
    xanh = len(thuong) - len(hong) - len(cho)
    print("\n" + "=" * 78)
    print("BAI CANH (xanh la tot): {}/{} xanh".format(xanh, len(thuong)))
    for ten, _ma, _d, _rc, cuoi, _l in hong:
        print("  DO   {:<32} {}".format(ten, cuoi))
    for ten, _ma, _d, _rc, cuoi, _l in cho:
        print("  ?    {:<32} {}".format(ten, cuoi))
    if bo_qua:
        print("\nBo qua {} bai mo cua so / phat tieng (them --tat-ca de chay):"
              .format(len(bo_qua)))
        print("  " + ", ".join(sorted(bo_qua)))
    return 1 if hong else 0


if __name__ == "__main__":
    sys.exit(main())
