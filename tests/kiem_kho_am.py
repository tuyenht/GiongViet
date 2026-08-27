# -*- coding: utf-8 -*-
"""Kho am thanh theo NOI DUNG — nghe lai va xuat lai khong tong hop lai.

Truoc day Speaker._cache dung .pop() nen no chi la hang doi nap truoc: lay ra
la xoa. Hau qua do duoc khi bam thu: nghe lai mot doan vua nghe van phai cho,
va bam Xuat sau khi da nghe ca bai thi tong hop lai tu dau. Tong hop cham gap
~4 lan thoi luong tieng nen day la diem dau lon nhat cua chuong trinh.

Bai nay KHONG nap VieNeu that (se mat hang phut). Thay _synth_blocking bang
mot ham dem so lan goi — dung thu can do: TONG HOP BAO NHIEU LAN.
"""
import io
import sys
import time
from pathlib import Path

# Goc du an, tinh tu chinh vi tri tep nay. KHONG viet cung duong dan:
# kho da len GitHub, ai tai ve cho khac la vo het bo kiem.
_GOC = str(Path(__file__).resolve().parent.parent)
sys.path.insert(0, _GOC)
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8")

import DocCongDuc as engine

loi = 0
def ok(dk, nhan, them=""):
    global loi
    print(f"  {'ĐẠT ' if dk else 'LỆCH'} {nhan}{'  →  ' + str(them) if them else ''}")
    if not dk:
        loi += 1


def speaker_dem(voice="giong-a"):
    """Speaker that, nhung phan tong hop thay bang ham dem."""
    sp = engine.Speaker({"vieneu_voice_id": voice, "phong_cach": ""})
    sp.xoa_kho()
    sp.so_lan = 0

    def gia(text, khuech_dai=1.0):
        sp.so_lan += 1
        time.sleep(0.01)                       # gia lam cho tong hop ton thoi gian
        return (b"RIFF" + b"\0" * 4000, "wav")

    sp._synth_blocking = gia
    return sp


print("--- A. Cung noi dung -> chi tong hop MOT lan ---")
sp = speaker_dem()
sp.get_audio("v1", "Kính gửi toàn thể cán bộ.")
sp.get_audio("v2", "Kính gửi toàn thể cán bộ.")
sp.get_audio("v3", "Kính gửi toàn thể cán bộ.")
ok(sp.so_lan == 1, "goi 3 lan, tong hop 1 lan", f"{sp.so_lan} lan tong hop")

print("\n--- B. Noi dung KHAC thi van tong hop moi ---")
sp.get_audio("v4", "Một câu hoàn toàn khác.")
ok(sp.so_lan == 2, "cau moi -> tong hop them dung 1 lan", sp.so_lan)

print("\n--- C. Khuech dai khac -> khong dung nham ---")
sp.get_audio("v5", "Kính gửi toàn thể cán bộ.", 1.5)
ok(sp.so_lan == 3, "cung chu nhung khuech dai khac -> tong hop rieng", sp.so_lan)

print("\n--- D. Giong khac -> kho rieng, khong lan sang nhau ---")
sp2 = speaker_dem("giong-b")
sp2.get_audio("v1", "Kính gửi toàn thể cán bộ.")
ok(sp2.so_lan == 1, "giong khac phai tong hop lai", sp2.so_lan)

print("\n--- E. clear_cache GIU NGUYEN kho ---")
# Doi playlist thi hang doi nap truoc thanh vo nghia, nhung tieng da tong hop
# xong van dung — noi dung nao ra tieng nay. Xoa luon kho la vut di dung thu
# vua ton hang phut de co.
truoc = sp.so_lan
sp.clear_cache()
sp.get_audio("v9", "Kính gửi toàn thể cán bộ.")
ok(sp.so_lan == truoc, "sau clear_cache van lay duoc tu kho", f"{truoc} -> {sp.so_lan}")

print("\n--- F. xoa_kho thi moi that su quen ---")
sp.xoa_kho()
sp.get_audio("v10", "Kính gửi toàn thể cán bộ.")
ok(sp.so_lan == truoc + 1, "xoa_kho roi thi tong hop lai", sp.so_lan)

print("\n--- G. Nhanh hon that su, khong phai chi dem ---")
sp3 = speaker_dem()
t = time.perf_counter()
sp3.get_audio("a", "Câu dùng để đo thời gian.")
lan_dau = (time.perf_counter() - t) * 1000
t = time.perf_counter()
for i in range(20):
    sp3.get_audio(f"b{i}", "Câu dùng để đo thời gian.")
lan_sau = (time.perf_counter() - t) * 1000 / 20
ok(lan_sau < lan_dau / 2, "lay tu kho nhanh hon han lan dau",
   f"{lan_dau:.1f} ms -> {lan_sau:.3f} ms moi lan")

print("\n--- H. Kho day thi bo mau lau khong dung, khong phinh vo han ---")
sp4 = speaker_dem()
sp4.KHO_TOI_DA_BYTE = 12000          # ~3 mau, de day nhanh
for i in range(8):
    sp4.get_audio(f"k{i}", f"Câu số {i}.")
ok(sp4._kho_byte <= sp4.KHO_TOI_DA_BYTE, "khong vuot gioi han",
   f"{sp4._kho_byte} / {sp4.KHO_TOI_DA_BYTE} byte")
ok(len(sp4._kho) < 8, "da bo bot mau cu", f"{len(sp4._kho)} mau con lai")
# Mau moi nhat phai con, mau cu nhat phai bi bo.
ok(sp4._khoa_kho("Câu số 7.", 1.0) in sp4._kho, "mau moi nhat van con")
ok(sp4._khoa_kho("Câu số 0.", 1.0) not in sp4._kho, "mau cu nhat da bi bo")

print("\n--- I. Chuoi rong khong lam ban kho ---")
sp5 = speaker_dem()
sp5._synth_blocking = lambda t, k=1.0: (b"", "wav")
sp5.get_audio("x", "")
ok(not sp5._kho, "khong cat mau rong vao kho", len(sp5._kho))

print("\n" + ("XANH — khớp hết" if not loi else f"ĐỎ — {loi} chỗ lệch"))
sys.exit(1 if loi else 0)
