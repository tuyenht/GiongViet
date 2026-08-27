# -*- coding: utf-8 -*-
"""Chạy thử ĐƯỜNG TIẾNG của giao diện mới, không cần mở cửa sổ.

Lái thẳng ApiMoi bằng Python: nạp mô hình, dựng playlist, phát thật. Người
ngồi trước máy sẽ NGHE THẤY tiếng — đó là bằng chứng.

Song song, đếm tiến trình ffplay liên tục để kiểm luật xương sống của dự án:
MỘT NGUỒN PHÁT TIẾNG TẠI MỘT THỜI ĐIỂM. Lấy mẫu một lần là không đủ, phải đo
liên tục mới bắt được đỉnh.

Không ghi vào tệp dữ liệu nào của người dùng.
Chạy:  py giaodien_moi/chay_thu_tieng.py
"""

import io
import subprocess
import sys
import threading
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", write_through=True)

from giaodien_moi.cau_noi_moi import ApiMoi

DOAN = [
    {"kieu": "head", "chu": "Thông báo nghỉ lễ Quốc khánh."},
    {"kieu": "blank", "chu": ""},
    {"kieu": "body", "chu": "Kính gửi toàn thể cán bộ, nhân viên Công ty TNHH Phúc Lâm."},
    {"kieu": "body", "chu": "Nghỉ từ ngày 31/8/2026 đến hết ngày 2/9/2026."},
]

CHO_MO_HINH_GIAY = 600


def dem_ffplay() -> int:
    try:
        r = subprocess.run(["tasklist", "/FI", "IMAGENAME eq ffplay.exe", "/NH"],
                           capture_output=True, text=True, timeout=10)
        return sum(1 for d in r.stdout.splitlines() if "ffplay" in d.lower())
    except (OSError, subprocess.SubprocessError):
        return -1


class Canh:
    """Đếm ffplay trong luồng riêng, giữ lại đỉnh."""

    def __init__(self):
        self.dinh = 0
        self.mau = 0
        self._chay = True
        threading.Thread(target=self._vong, daemon=True).start()

    def _vong(self):
        while self._chay:
            n = dem_ffplay()
            if n >= 0:
                self.mau += 1
                self.dinh = max(self.dinh, n)
            time.sleep(0.25)

    def dung(self):
        self._chay = False


def main():
    goi = []
    canh = Canh()

    api = ApiMoi((0, 0, 1280, 800))

    # Chặn ở _goi_js chứ KHÔNG phải _day: cau_noi.py:66 làm BoDoc(self._day),
    # tức BoDoc giữ hàm đã gắn từ lúc khởi tạo. Thay api._day sau đó thì BoDoc
    # vẫn gọi hàm cũ, và mọi gói tin của vòng đọc lọt hết ra ngoài lưới.
    api._goi_js = lambda ma, *ts: goi.append(dict(ts[0]) if ts and isinstance(ts[0], dict) else {})

    print("1. Nạp mô hình VieNeu (lần đầu có thể mất 40 giây hoặc hơn)…")
    api._bo_mo_hinh.bat_dau()
    het = time.time() + CHO_MO_HINH_GIAY
    while not api._bo_mo_hinh.san_sang and time.time() < het:
        if api._bo_mo_hinh.loi:
            print("   HỎNG:", api._bo_mo_hinh.loi)
            return 1
        time.sleep(1)
    if not api._bo_mo_hinh.san_sang:
        print(f"   HỎNG: quá {CHO_MO_HINH_GIAY} giây mà mô hình chưa sẵn sàng")
        return 1
    print(f"   Mô hình sẵn sàng · giọng đang dùng: {api._cfg.get('vieneu_voice_id')!r}")

    print("\n2. Gửi đoạn sang, dựng playlist…")
    print("  ", api.moi_dat_doan(DOAN))

    print("\n3. NGHE TOÀN BỘ — từ đây trở đi phải có tiếng ra loa")
    t0 = time.time()
    api.moi_nghe_toan_bo()
    time.sleep(12)

    print("\n4. Đang phát dở thì bấm NGHE RIÊNG đoạn 4 — thử chống chồng tiếng")
    api.moi_nghe_doan(4)
    time.sleep(8)

    print("\n5. Bấm loạn: nghe toàn bộ / nghe riêng / tạm dừng liên tiếp")
    for i in range(4):
        api.moi_nghe_toan_bo(); time.sleep(0.6)
        api.moi_nghe_doan(3);   time.sleep(0.6)
        api.moi_tam_dung();     time.sleep(0.4)
    api.moi_dung()
    time.sleep(2)

    canh.dung()
    print(f"\n=== KẾT QUẢ sau {time.time() - t0:.0f} giây ===")
    print(f"  Tiến trình ffplay ĐỈNH ĐIỂM : {canh.dinh}   (luật: tối đa 1)")
    print(f"  Số lần lấy mẫu              : {canh.mau}")
    print(f"  Gói tin Python đẩy sang JS  : {len(goi)}")

    doan_da_bao = [g["doan"] for g in goi if "doan" in g]
    print(f"  Số đoạn đã báo sang giao diện: {doan_da_bao}")
    co_thoi_luong = [g for g in goi if g.get("thoiLuong")]
    print(f"  Gói có thoiLuong thật (để tô chữ): {len(co_thoi_luong)}")
    if co_thoi_luong:
        print(f"     ví dụ: đoạn {co_thoi_luong[0].get('doan')} · "
              f"{co_thoi_luong[0]['thoiLuong']:.2f} giây")

    api._don_dep()
    time.sleep(1)
    con = dem_ffplay()
    print(f"  ffplay còn sót sau khi dọn  : {con}   (phải là 0)")

    dat = canh.dinh <= 1 and con == 0
    print(f"\n{'XANH — một nguồn phát, thoát sạch' if dat else 'ĐỎ — xem số liệu bên trên'}")
    return 0 if dat else 1


if __name__ == "__main__":
    sys.exit(main())
