# -*- coding: utf-8 -*-
"""Cai cong truoc khi day vao .git/hooks/. Chay: py tests/hooks/cai_cong.py

VI SAO PHAI CO BUOC CAI: .git/hooks/ KHONG nam trong kho, nen tep hook khong
di theo git clone duoc. Giu ban goc trong tests/hooks/ roi chep sang - ai tai
kho ve cung chay mot lenh nay la co cong.

Chay lai nhieu lan khong sao: no chep de ban cu.
"""
import shutil
import stat
import sys
from pathlib import Path

GOC = Path(__file__).resolve().parent.parent.parent
NGUON = GOC / "tests" / "hooks" / "pre-push"
DICH = GOC / ".git" / "hooks" / "pre-push"


def main():
    if not NGUON.is_file():
        print(f"[LOI] Khong thay ban goc: {NGUON}")
        return 1
    if not (GOC / ".git").is_dir():
        print(f"[LOI] {GOC} khong phai kho git.")
        return 1

    DICH.parent.mkdir(parents=True, exist_ok=True)
    da_co = DICH.is_file()
    shutil.copyfile(NGUON, DICH)

    # Git Bash tren Windows van doi bit thuc thi. Thieu no thi hook bi bo qua
    # LANG LE - khong bao loi, chi la khong bao gio chay, ma minh lai tuong
    # dang duoc canh.
    try:
        DICH.chmod(DICH.stat().st_mode | stat.S_IXUSR | stat.S_IXGRP | stat.S_IXOTH)
    except OSError as e:
        print(f"[nhac] Khong dat duoc bit thuc thi: {e}")

    print(f"{'Da thay' if da_co else 'Da cai'} cong: {DICH}")
    print()
    print("Tu gio moi lan `git push` se chay bo kiem truoc.")
    print("Bai nao do CO CHU Y thi khai trong DO_CO_CHU_Y o dau")
    print("tests/chay_tat_ca.py, kem LY DO - khong co ly do thi danh sach ay")
    print("phinh dan cho toi khi cai cong nay vo nghia.")
    print()
    print("Thu ngay:  py tests/chay_tat_ca.py --cong")
    print("Bo qua mot lan:  git push --no-verify")
    return 0


if __name__ == "__main__":
    sys.exit(main())
