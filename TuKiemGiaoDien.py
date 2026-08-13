# -*- coding: utf-8 -*-
"""Tự kiểm giao diện mới trên CỬA SỔ THẬT — tự bấm, tự đo, tự đóng.

Chủ dự án cho phép chiếm màn hình một lúc (2026-08-12). Cửa sổ mở nhỏ ở góc
trên trái, chạy hết kịch bản rồi tự thoát; có tiếng ra loa vài giây.

Kiểm đúng ba thứ mà bộ kiểm chạy chay KHÔNG với tới được:
  1. Ba nút thu nhỏ / phóng to / đóng có thật sự tác động lên cửa sổ không
     (đo bằng IsIconic và GetWindowRect của Windows, không phải bằng mắt).
  2. Nút loa có ra tiếng thật không (đếm tiến trình ffplay).
  3. Gói tin đẩy sang giao diện lúc đọc thật có đủ tu/den/trongSo không, và
     mỗi lúc có tối đa MỘT nguồn phát.

Chạy:  py TuKiemGiaoDien.py
Kết quả in ra màn hình và ghi vào thu_nghiem/tu-kiem-ket-qua.txt
"""

import ctypes
import io
import json
import os
import subprocess
import sys
import tempfile
import threading
import time
from ctypes import wintypes
from pathlib import Path

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8")

BASE_DIR = Path(__file__).resolve().parent
if str(BASE_DIR) not in sys.path:
    sys.path.insert(0, str(BASE_DIR))

import webview  # noqa: E402

# Cửa sổ nhỏ, nằm góc trên trái - chiếm ít chỗ nhất có thể.
VUNG = (40, 40, 1100, 720)

# Trần cứng cho cả phiên. Quá giờ là giết tiến trình, không để treo máy.
TRAN_GIAY = 420

TEP_KET_QUA = BASE_DIR / "thu_nghiem" / "tu-kiem-ket-qua.txt"

# Mốc bắt đầu, để cuối bài còn so xem có tệp dữ liệu nào bị chạm trong lúc chạy.
BAT_DAU = time.time()

# Thư mục tạm chứa dữ liệu của bài kiểm; main() đặt giá trị thật.
tam = None

VAN_BAN = [
    {"kieu": "head", "chu": "THÔNG BÁO NGHỈ LỄ"},
    {"kieu": "blank", "chu": ""},
    {"kieu": "body", "chu": "Kính gửi toàn thể cán bộ, nhân viên của công ty."},
    {"kieu": "body", "chu": "Nghỉ từ 31/8/2026 đến hết 2/9/2026, tổng đài 1900 6868."},
    {"kieu": "body", "chu": "Các phòng ban bố trí người trực và gửi danh sách "
                            "về phòng Hành chính trước 17h00 ngày 28 tháng 8."},
    {"kieu": "body", "chu": "Trước khi ra về, đề nghị mọi người tắt toàn bộ "
                            "thiết bị điện và khoá cửa phòng làm việc."},
    {"kieu": "body", "chu": "Trân trọng thông báo."},
]

dong = []
loi = 0


def ghi(s=""):
    print(s)
    dong.append(s)


def ok(dk, nhan, them=""):
    global loi
    ghi(f"  {'ĐẠT ' if dk else 'LỆCH'} {nhan}{'  →  ' + str(them) if them else ''}")
    if not dk:
        loi += 1


def dem_ffplay() -> int:
    try:
        r = subprocess.run(
            ["tasklist", "/FI", "IMAGENAME eq ffplay.exe", "/NH"],
            capture_output=True, text=True, timeout=10,
            creationflags=getattr(subprocess, "CREATE_NO_WINDOW", 0))
        return sum(1 for d in r.stdout.splitlines() if "ffplay.exe" in d.lower())
    except (OSError, subprocess.SubprocessError):
        return -1


def tim_cua_so():
    """HWND của cửa sổ Giọng Việt. pywebview không cho nên phải hỏi Windows."""
    return ctypes.windll.user32.FindWindowW(None, "Giọng Việt")


def khung(hwnd):
    r = wintypes.RECT()
    ctypes.windll.user32.GetWindowRect(hwnd, ctypes.byref(r))
    return r.right - r.left, r.bottom - r.top


def thu_nho(hwnd) -> bool:
    return bool(ctypes.windll.user32.IsIconic(hwnd))


def chay_js(api, ma: str, cho=0.35):
    """evaluate_js trả Promise khi chạm pywebview.api, nên nơi nào cần kết quả
    thì gán ra biến global rồi đọc lại - đã vấp lỗi này một lần."""
    try:
        kq = api._window.evaluate_js(ma)
    except Exception as e:            # noqa: BLE001 - kịch bản kiểm, cần biết hết
        ghi(f"       (evaluate_js lỗi: {type(e).__name__} {e})")
        return None
    time.sleep(cho)
    return kq


def duLieuGiong_cuaToi(api):
    """Số giọng riêng đang có trên máy — để bài kiểm nói rõ vì sao không có
    nút Xoá, thay vì lặng lẽ bỏ qua và tưởng là đã kiểm."""
    try:
        import DocCongDuc as engine
        return engine.doc_ds_giong_rieng()
    except Exception:                          # noqa: BLE001
        return []


def cho_den(dieu_kien, gioi_han, nhip=0.5):
    het = time.time() + gioi_han
    while time.time() < het:
        if dieu_kien():
            return True
        time.sleep(nhip)
    return False


def kich_ban(api):
    global loi
    time.sleep(2.0)          # để WebView2 dựng xong trang

    ghi("=== TỰ KIỂM GIAO DIỆN TRÊN CỬA SỔ THẬT ===")
    ghi(f"    {time.strftime('%Y-%m-%d %H:%M:%S')}")
    ghi()

    ghi("--- A. Trang có dựng lên được không ---")
    tieu_de = chay_js(api, "document.title")
    ok(tieu_de == "Giọng Việt", "trang đã nạp", tieu_de)
    so_nut = chay_js(api, "document.querySelectorAll('[data-cuaso]').length")
    ok(so_nut == 3, "có đủ 3 nút cửa sổ", so_nut)
    ok(chay_js(api, "typeof trangThaiChu") == "function",
       "hàm tô chữ có mặt")

    ghi("\n--- B. Ba nút cửa sổ có TÁC ĐỘNG THẬT không ---")
    hwnd = tim_cua_so()
    ok(bool(hwnd), "tìm được cửa sổ trong Windows", hwnd)
    if hwnd:
        rong0, cao0 = khung(hwnd)
        ghi(f"       cỡ ban đầu {rong0}x{cao0}")

        # Chờ theo ĐIỀU KIỆN, không ngủ một khoảng cố định: Windows thu cửa sổ
        # xong lúc nào là tuỳ máy, ngủ 1,2 giây có hôm vừa đủ có hôm hụt - đã
        # thấy bài kiểm lúc đạt lúc lệch trong khi mã không đổi dòng nào.
        chay_js(api, "document.querySelector('[data-cuaso=\"thu_nho\"]').click()", 0.2)
        ok(cho_den(lambda: thu_nho(hwnd), 5, 0.1),
           "bấm THU NHỎ thì cửa sổ thu xuống thanh tác vụ")

        ctypes.windll.user32.ShowWindow(hwnd, 9)   # SW_RESTORE, mở lại để kiểm tiếp
        ok(cho_den(lambda: not thu_nho(hwnd), 5, 0.1), "mở lại được")

        chay_js(api, "document.querySelector('[data-cuaso=\"phong_to\"]').click()", 1.2)
        rong1, cao1 = khung(hwnd)
        ok((rong1, cao1) != (rong0, cao0), "bấm PHÓNG TO thì cỡ cửa sổ đổi",
           f"{rong0}x{cao0} → {rong1}x{cao1}")

        chay_js(api, "document.querySelector('[data-cuaso=\"phong_to\"]').click()", 1.2)
        rong2, cao2 = khung(hwnd)
        ok((rong2, cao2) != (rong1, cao1), "bấm lần nữa thì thu về cỡ vừa",
           f"{rong1}x{cao1} → {rong2}x{cao2}")

    ghi("\n--- C. Chờ mô hình sẵn sàng ---")
    t0 = time.time()
    san = cho_den(lambda: api._bo_mo_hinh.san_sang, 300)
    ok(san, f"mô hình nạp xong sau {time.time() - t0:.0f} giây",
       "" if san else api._bo_mo_hinh.loi or "quá giờ")
    if not san:
        return

    ghi("\n--- D. Nút loa có ra tiếng THẬT không ---")
    ok(dem_ffplay() == 0, "trước khi bấm: 0 tiến trình ffplay", dem_ffplay())
    chay_js(api, "document.getElementById('ngheMau').click()", 0.6)
    dang = chay_js(api, "S.dangNgheThu")
    ok(bool(dang), "giao diện bật cờ đang nghe thử", dang)
    co_tieng = cho_den(lambda: dem_ffplay() > 0, 90)
    ok(co_tieng, "ffplay chạy → CÓ tiếng ra loa thật")
    ok(dem_ffplay() <= 1, "tối đa MỘT nguồn phát", dem_ffplay())

    chay_js(api, "dungNgheThu()", 1.5)
    het = cho_den(lambda: dem_ffplay() == 0, 20)
    ok(het, "bấm dừng thì tiếng tắt ngay", dem_ffplay())
    ok(not chay_js(api, "S.dangNgheThu"), "cờ hạ xuống")

    ghi("\n--- E. Đọc thật: gói tin có đủ số liệu để tô chữ không ---")
    goi = []
    goi_js_goc = api._goi_js

    def goi_js_thu(ma_lenh, *ts):
        # Chặn ở _goi_js chứ KHÔNG ở _day: ApiMoi._day mới là chỗ gắn thêm
        # doan/tu/den/trongSo, chặn trước nó thì chỉ bắt được gói thô của BoDoc
        # rồi tưởng nhầm là sản phẩm thiếu số liệu. Đã vấp đúng lỗi này.
        if ma_lenh == "window.gd.push" and ts and isinstance(ts[0], dict) \
                and "pos" in ts[0]:
            goi.append((time.time(), dict(ts[0])))
        return goi_js_goc(ma_lenh, *ts)

    api._goi_js = goi_js_thu

    # Nạp qua ĐÚNG đường người dùng đi (datTaiLieu), không gọi thẳng
    # api.moi_dat_doan: gọi thẳng thì Python có văn bản mà giao diện vẫn đang
    # hiện tài liệu khác, vùng đọc không có đoạn nào để tô và bài kiểm tưởng
    # nhầm là bộ tô chữ hỏng.
    chay_js(api, "datTaiLieu(" + json.dumps(
        {"ten": "tu-kiem.txt", "doan": VAN_BAN}, ensure_ascii=False) + ")", 1.5)
    ok(chay_js(api, "tenTepDangXem(S)") == "tu-kiem.txt",
       "văn bản đã vào vùng đọc", chay_js(api, "tenTepDangXem(S)"))
    chay_js(api, "dat(ngheToanBo(S)); batDauPhat();", 0.5)

    # Chờ theo GÓI TIN chứ đừng poll evaluate_js: hỏi trang 5 lần/giây là tranh
    # luồng giao diện với chính đường đẩy gói tin, trang không kịp xử lý và span
    # không bao giờ hiện ra. Gói tin đếm được ngay bên Python, không tốn gì.
    cho_den(lambda: len([g for g in goi if g[1].get("thoiLuong")]) >= 2, 240, 0.2)
    time.sleep(0.4)
    so_span = chay_js(api, "document.querySelectorAll('.doan__chu .tu').length")
    dang_doc = chay_js(api, "S.view")
    # Span bị gỡ ở quãng "đang tạo âm thanh" giữa hai mẩu (giao diện vẽ lại cả
    # màn), nên đếm span đúng khoảnh khắc là ăn may. toChuDoan/toChuTong thì
    # giữ nguyên qua các nhịp vẽ - hỏi chúng mới biết chắc bộ tô chữ đã chạy.
    to_doan = chay_js(api, "toChuDoan")
    to_tong = chay_js(api, "toChuTong")
    api.moi_dung()
    cho_den(lambda: dem_ffplay() == 0, 20)

    co_wav = [g for _, g in goi if g.get("thoiLuong")]
    ok(len(co_wav) >= 2, f"nhận được {len(co_wav)} gói tin kèm thời lượng WAV")
    ok(all("doan" in g for g in co_wav), "gói nào cũng biết số ĐOẠN")
    co_pv = [g for g in co_wav if "tu" in g and "den" in g]
    ok(len(co_pv) == len(co_wav), "gói nào cũng có phạm vi mẩu tu/den",
       f"{len(co_pv)}/{len(co_wav)}")
    ok(all(g["tu"] < g["den"] for g in co_pv), "tu luôn nhỏ hơn den")
    co_ts = [g for g in co_pv if g.get("trongSo")]
    ok(len(co_ts) >= 1, "có gói mang trọng số âm tiết", len(co_ts))
    if co_ts:
        g = co_ts[0]
        ghi(f"       ví dụ: đoạn {g['doan']} · {g['tu']:.3f}..{g['den']:.3f} · "
            f"{len(g['trongSo'])} chữ · WAV {g['thoiLuong']:.2f}s")

    ghi("\n--- F. Chữ có chạy thật trên màn hình không ---")
    ok(dang_doc == "dang_doc", "giao diện ở trạng thái đang đọc", dang_doc)
    ok((to_doan or 0) > 0 and (to_tong or 0) > 0,
       "bộ tô chữ đã chạy trên đoạn đang đọc",
       f"đoạn {to_doan} · {to_tong}s")
    ghi(f"       (span đếm được lúc soi: {so_span} — số này lên xuống theo nhịp vẽ)")

    ghi("\n--- G. Đổi tab rồi bấm Nghe: Python phải giữ ĐÚNG tài liệu đang hiện ---")
    # Đúng tình huống chủ dự án gặp: màn hình "phun thuốc", loa đọc "nghỉ lễ".
    chay_js(api, """
      TAI_LIEU['nghi-le.txt'] = { doan: [
        { kieu: 'head', chu: 'THÔNG BÁO NGHỈ LỄ QUỐC KHÁNH' },
        { kieu: 'body', chu: 'Nghỉ từ ngày mai đến hết tuần.' }],
        chuY: { tomTat: '', loai: [] } };
      TAI_LIEU['phun-thuoc.txt'] = { doan: [
        { kieu: 'head', chu: 'THÔNG BÁO PHUN THUỐC DIỆT MUỖI' },
        { kieu: 'body', chu: 'Kính mời bà con chú ý nghe thông báo.' },
        { kieu: 'body', chu: 'Sáng mai từ sáu giờ đến chín giờ.' }],
        chuY: { tomTat: '', loai: [] } };
      dat({ ...S,
            tabsByProfile: { ...S.tabsByProfile,
                             [S.profile]: ['nghi-le.txt', 'phun-thuoc.txt'] },
            activeByProfile: { ...S.activeByProfile, [S.profile]: 0 } });
      vanTayDaGui = '';
    """, 0.5)

    chay_js(api, "chuyenSang(doiTab(S, 1))", 0.2)
    cho_den(lambda: chay_js(api, "tenTepDangXem(S)", 0) == "phun-thuoc.txt", 15, 0.2)
    ok(chay_js(api, "tenTepDangXem(S)", 0) == "phun-thuoc.txt",
       "giao diện đang hiện tab phun-thuoc", chay_js(api, "tenTepDangXem(S)", 0))

    ghi(f"       JS thấy: tab={chay_js(api, 'tenTepDangXem(S)')!r} · "
        f"{chay_js(api, 'doanDangXem(S, TAI_LIEU).length')} đoạn · "
        f"vanTayDaGui={chay_js(api, 'vanTayDaGui')!r}")
    chay_js(api, "dat(ngheToanBo(S)); batDauPhat();", 0.2)
    # Chờ Python nhận xong tài liệu mới rồi mới soi - gửi đoạn đi qua cầu JS
    # nên nó không xong ngay trong cùng một nhịp.
    cho_den(lambda: len(api._doan) == 3, 20, 0.2)
    ghi(f"       sau khi phát: vanTayDaGui={chay_js(api, 'vanTayDaGui', 0)!r} · "
        f"Python giữ {len(api._doan)} đoạn")
    doc_that = " ".join(str(d.get("chu", "")) for d in api._doan)
    ok("PHUN THUỐC" in doc_that,
       "Python giữ đúng tài liệu ĐANG HIỆN", doc_that[:42])
    ok("NGHỈ LỄ" not in doc_that, "KHÔNG còn tài liệu của tab cũ")
    ok(len(api._doan) == 3, "đúng 3 đoạn của tab đang hiện", len(api._doan))
    api.moi_dung()
    cho_den(lambda: dem_ffplay() == 0, 20)

    ghi("\n--- G2. Màn Soát văn bản: nút phải MỞ ĐƯỢC màn thật ---")
    chay_js(api, "datTaiLieu(" + json.dumps(
        {"ten": "soat-thu.txt", "doan": [
            {"kieu": "head", "chu": "THÔNG BÁO NGHỈ LỄ 2/9"},
            {"kieu": "body", "chu": "Tổ XKLĐ khu TĐC họp lúc 17h00."},
            {"kieu": "body", "chu": "Gọi 1900 6868 nếu cần ☎."}]}, ensure_ascii=False)
        + ")", 1.2)
    chay_js(api, "LENH['Soát văn bản']()", 0.3)
    cho_den(lambda: chay_js(api, "S.man", 0) == "soat", 20, 0.3)
    ok(chay_js(api, "S.man") == "soat", "bấm Soát văn bản thì vào màn soát",
       chay_js(api, "S.man"))
    ok(chay_js(api, "!!duLieuSoat"), "có số liệu soát từ Python")
    ok((chay_js(api, "document.querySelectorAll('[data-soatdoan]').length") or 0) > 0,
       "bảng kết quả soát có hàng",
       chay_js(api, "document.querySelectorAll('[data-soatdoan]').length"))
    ok((chay_js(api, "document.querySelectorAll('[data-soattab]').length") or 0) == 2,
       "có đủ 2 tab")

    chay_js(api, "dat({ ...S, soatTab: 'chuanhoa' })", 0.5)
    ok(chay_js(api, "document.querySelectorAll('.soat__d3 mark').length") > 0,
       "tab 2 có tô chỗ máy đọc khác văn bản gốc",
       chay_js(api, "document.querySelectorAll('.soat__d3 mark').length"))

    # Quy tắc không tắt được thì KHÔNG được bày ra dạng nút - đúng KPI.
    ok(chay_js(api, "document.querySelectorAll('.soat__chip--tinh').length") == 2,
       "2 quy tắc không đổi được hiện dạng nhãn, không phải nút",
       chay_js(api, "document.querySelectorAll('.soat__chip--tinh').length"))
    ok((chay_js(api, "document.querySelectorAll('[data-quytac]').length") or 0) == 2,
       "2 quy tắc còn lại mới là nút bấm được")

    chay_js(api, "LENH['Đóng soát']()", 0.5)
    ok(chay_js(api, "S.man") == "chinh", "bấm Xong thì về màn chính")

    ghi("\n--- G3. Màn Thư viện giọng ---")
    chay_js(api, "LENH['Thư viện giọng']()", 0.3)
    cho_den(lambda: chay_js(api, "S.man", 0) == "giong", 30, 0.3)
    ok(chay_js(api, "S.man") == "giong", "bấm Thư viện giọng thì vào màn",
       chay_js(api, "S.man"))
    so_the = chay_js(api, "document.querySelectorAll('.the-giong:not(.the-giong--moi)').length") or 0
    ok(so_the >= 10, "hiện đủ thẻ giọng thật trên máy", so_the)
    ok((chay_js(api, "document.querySelectorAll('.the-giong.dung:not(.the-giong--moi)').length") or 0) == 1,
       "đúng MỘT thẻ mang nhãn Đang dùng")
    ok((chay_js(api, "document.querySelectorAll('[data-nghegiong]').length") or 0) == so_the,
       "thẻ nào cũng có nút Nghe thử")
    # Lọc và tìm phải lọc thật, không phải nút trang trí.
    chay_js(api, "dat({ ...S, giongLoc: 'cuatoi' })", 0.4)
    rieng = chay_js(api, "document.querySelectorAll('.the-giong:not(.the-giong--moi)').length") or 0
    ok(rieng < so_the, "lọc 'Giọng của tôi' cắt bớt danh sách", f"{so_the} → {rieng}")
    chay_js(api, "dat({ ...S, giongLoc: 'tatca', giongTim: 'khongcogiongnaoten' })", 0.4)
    ok((chay_js(api, "document.querySelectorAll('.the-giong:not(.the-giong--moi)').length") or 0) == 0,
       "tìm chữ không có thì ra danh sách rỗng")
    chay_js(api, "dat({ ...S, giongTim: '' })", 0.3)

    # Chọn giọng ở màn này phải đổi giọng của HỒ SƠ.
    ma_moi = chay_js(api, "(duLieuGiong.coSan.find(g => !g.dangDung) || {}).id")
    if ma_moi:
        chay_js(api, f"document.querySelector('[data-giong=\"{ma_moi}\"]').click()", 0.8)
        ok(chay_js(api, "hoSoDangDung(S).giong") == ma_moi,
           "bấm 'Dùng giọng này' thì hồ sơ đổi giọng thật", ma_moi)
        ok((chay_js(api, "document.querySelectorAll('.the-giong.dung:not(.the-giong--moi)').length") or 0) == 1,
           "nhãn Đang dùng dời sang đúng một thẻ mới")

    # Nhân bản / xoá giọng: KHÔNG chạy thật (mất vài phút, cần PyTorch và sẽ
    # đẻ tệp trong giong_rieng/). Chỉ kiểm nút có đường đi thật, và ba đường
    # tiến độ Python gọi ngược về có mặt — thiếu chúng thì bấm xong màn hình
    # đứng im, đúng lỗi đã vấp với ngheThuXong.
    ok((chay_js(api, "document.querySelectorAll('[data-nhanbangiong]').length") or 0) == 1,
       "có ô Nhân bản giọng mới")
    for ten_ham in ("tienDoGiong", "giongXong", "giongLoi"):
        ok(chay_js(api, f"typeof window.gd.{ten_ham}") == "function",
           f"window.gd.{ten_ham} có mặt để Python gọi ngược")
    ok(chay_js(api, "typeof nhanBanGiong") == "function"
       and chay_js(api, "typeof xoaGiongRieng") == "function",
       "hai hàm nhân bản và xoá đã nối")
    # Máy này chưa có giọng riêng nào nên không có nút Xoá — nói rõ thay vì
    # lặng lẽ bỏ qua.
    ghi(f"       (giọng riêng trên máy: {len(duLieuGiong_cuaToi(api))} — "
        f"nút Xoá chỉ hiện ở thẻ giọng riêng)")

    chay_js(api, "LENH['Đóng giọng']()", 0.5)
    ok(chay_js(api, "S.man") == "chinh", "bấm Xong thì về màn chính")
    ok(cho_den(lambda: dem_ffplay() == 0, 15), "không bỏ lại tiếng nào")

    ghi("\n--- G4. Màn Từ điển phát âm: sửa phải LƯU ĐƯỢC THẬT ---")
    import DocCongDuc as engine
    chay_js(api, "LENH['Từ điển phát âm']()", 0.3)
    cho_den(lambda: chay_js(api, "S.man", 0) == "tudien", 20, 0.3)
    ok(chay_js(api, "S.man") == "tudien", "vào được màn từ điển")
    so_muc = chay_js(api, "duLieuTuDien.tong") or 0
    ok(so_muc > 0, "đọc được từ điển thật", f"{so_muc} mục")

    tu_moi = "ZZTEST"
    truoc_mt = engine.TUDIEN_FILE.stat().st_mtime_ns \
        if engine.TUDIEN_FILE.exists() else 0
    chay_js(api, f"suaTuDien('them', '{tu_moi}', 'dê dê thử nghiệm')", 1.2)
    cho_den(lambda: (chay_js(api, "duLieuTuDien.tong", 0) or 0) > so_muc, 15, 0.3)
    ok((chay_js(api, "duLieuTuDien.tong") or 0) == so_muc + 1,
       "thêm một mục thì bảng dài thêm đúng một",
       chay_js(api, "duLieuTuDien.tong"))
    ok(engine.TUDIEN_FILE.exists()
       and engine.TUDIEN_FILE.stat().st_mtime_ns != truoc_mt,
       "GHI THẬT xuống tudien.ini (không còn mất khi đóng chương trình)")
    ok(tu_moi in engine.TUDIEN_FILE.read_text(encoding="utf-8", errors="replace"),
       "chữ vừa thêm có mặt trong tệp")

    chay_js(api, f"suaTuDien('xoa', '{tu_moi}')", 1.2)
    cho_den(lambda: (chay_js(api, "duLieuTuDien.tong", 0) or 0) == so_muc, 15, 0.3)
    ok((chay_js(api, "duLieuTuDien.tong") or 0) == so_muc,
       "xoá xong thì về đúng số mục ban đầu")

    chay_js(api, "LENH['Đóng từ điển']()", 0.4)
    ok(chay_js(api, "S.man") == "chinh", "bấm Xong thì về màn chính")

    ghi("\n--- G5. Màn Cài đặt ---")
    chay_js(api, "LENH['Cài đặt']()", 0.3)
    cho_den(lambda: chay_js(api, "S.man", 0) == "caidat", 20, 0.3)
    ok(chay_js(api, "S.man") == "caidat", "vào được màn cài đặt")
    ok((chay_js(api, "document.querySelectorAll('.caidat__nhom').length") or 0) >= 4,
       "có đủ các nhóm cài đặt",
       chay_js(api, "document.querySelectorAll('.caidat__nhom').length"))
    # Công tắc phải đổi cfg THẬT, không phải bật tắt cho vui.
    truoc = api._cfg.get("doc_so_bang_chu")
    chay_js(api, f"datCaiDat('doc_so_bang_chu', {str(not truoc).lower()})", 1.5)
    cho_den(lambda: api._cfg.get("doc_so_bang_chu") != truoc, 15, 0.3)
    ok(api._cfg.get("doc_so_bang_chu") != truoc,
       "bật/tắt công tắc thì cfg đổi thật", api._cfg.get("doc_so_bang_chu"))
    chay_js(api, f"datCaiDat('doc_so_bang_chu', {str(bool(truoc)).lower()})", 1.5)

    # Cỡ chữ do giao diện giữ, phải áp được vào biến CSS.
    chay_js(api, "dat({ ...S, zoom: 150 })", 0.4)
    ok(chay_js(api, "S.zoom") == 150, "đổi cỡ chữ vùng đọc", chay_js(api, "S.zoom"))
    chay_js(api, "dat({ ...S, zoom: 100 })", 0.3)
    chay_js(api, "LENH['Đóng cài đặt']()", 0.4)
    ok(chay_js(api, "S.man") == "chinh", "bấm Xong thì về màn chính")

    ghi("\n--- G6. Nút PHÓNG TO phải đo cửa sổ, không đoán ---")
    if hwnd:
        # Bản cũ giữ cờ _phong_to = True nên lần bấm ĐẦU lại thu nhỏ. Giờ đo
        # thật: kéo cửa sổ nhỏ lại rồi bấm thì phải TO RA, không phải nhỏ thêm.
        api._window.resize(900, 600)
        time.sleep(1.0)
        r0, c0 = khung(hwnd)
        chay_js(api, "document.querySelector('[data-cuaso=\"phong_to\"]').click()", 1.5)
        r1, c1 = khung(hwnd)
        ok(r1 > r0 and c1 > c0,
           "đang nhỏ mà bấm thì TO RA (không còn phụ thuộc cờ đoán trước)",
           f"{r0}x{c0} → {r1}x{c1}")
        chay_js(api, "document.querySelector('[data-cuaso=\"phong_to\"]').click()", 1.5)
        r2, c2 = khung(hwnd)
        ok(r2 < r1 and c2 < c1, "bấm lần nữa thì thu về cỡ vừa",
           f"{r1}x{c1} → {r2}x{c2}")

        # Nháy đúp thanh tiêu đề: thói quen Windows cả đời của người dùng.
        chay_js(api, """
          (function () {
            const t = document.querySelector('.tieude');
            t.dispatchEvent(new MouseEvent('dblclick', { bubbles: true }));
          })()""", 1.5)
        r3, c3 = khung(hwnd)
        ok(r3 > r2 and c3 > c2, "nháy đúp thanh tiêu đề thì phóng to",
           f"{r2}x{c2} → {r3}x{c3}")
        chay_js(api, """
          (function () {
            const t = document.querySelector('.tieude');
            t.dispatchEvent(new MouseEvent('dblclick', { bubbles: true }));
          })()""", 1.5)
        r4, c4 = khung(hwnd)
        ok(r4 < r3 and c4 < c3, "nháy đúp lần nữa thì thu về", f"{r3}x{c3} → {r4}x{c4}")

        # Nút giữa chỉ mang MỘT nghĩa tại một thời điểm.
        chay_js(api, "capNhatNutCuaSo()", 1.0)
        nhan_nho = chay_js(api, "document.querySelector('[data-cuaso=\"phong_to\"]').title")
        ok(nhan_nho == "Phóng to", "đang nhỏ thì nút ghi 'Phóng to'", nhan_nho)
        chay_js(api, "document.querySelector('[data-cuaso=\"phong_to\"]').click()", 1.6)
        nhan_kin = chay_js(api, "document.querySelector('[data-cuaso=\"phong_to\"]').title")
        ok(nhan_kin == "Thu về cỡ vừa", "đang kín thì nút đổi thành 'Thu về cỡ vừa'",
           nhan_kin)
        ok(chay_js(api, "!!document.querySelector('[data-cuaso=\"phong_to\"] use')"
                        " && document.querySelector('[data-cuaso=\"phong_to\"] use')"
                        ".getAttribute('href') === '#i-thuvua'"),
           "biểu tượng cũng đổi sang hai ô chồng nhau")

    ghi("\n--- G7. Kéo mép để đổi cỡ cửa sổ ---")
    so_vien = chay_js(api, "document.querySelectorAll('[data-vien]').length") or 0
    ok(so_vien == 8, "có đủ 8 dải kéo (4 cạnh + 4 góc)", so_vien)
    ok(chay_js(api, "getComputedStyle(document.querySelector('.vien--phai')).cursor")
       == "ew-resize", "mép phải đổi con trỏ thành mũi tên ngang")
    ok(chay_js(api, "getComputedStyle(document.querySelector('.vien--duoiphai')).cursor")
       == "nwse-resize", "góc dưới phải đổi con trỏ thành mũi tên chéo")
    # Dải mép không được nuốt cú bấm vào nút nằm sát mép.
    ok((chay_js(api, "document.elementFromPoint(200, 300) ?"
                     " document.elementFromPoint(200, 300).closest('[data-vien]') ? 1 : 0"
                     " : 0") or 0) == 0,
       "giữa màn hình KHÔNG dính dải kéo")

    ghi("\n--- G8. Đọc danh sách tên và số (chức năng gốc) ---")
    ds = tam / "danhsach-tu-kiem.txt"
    ds.write_text("DANH SÁCH ỦNG HỘ\nNguyễn Văn An\t500.000\n"
                  "Trần Thị Bình\t1.200.000\n", encoding="utf-8")
    chay_js(api, f"datTaiLieu(JSON.parse({json.dumps(json.dumps(None))}))", 0.1)
    kq = api.moi_doc_danh_sach(ds)
    ok(not kq.get("loi") and kq["loai"] == "congduc",
       "Python đọc được tệp danh sách", kq.get("loi") or kq["loai"])
    chay_js(api, "datTaiLieu(" + json.dumps(kq, ensure_ascii=False) + ")", 1.2)
    ok(chay_js(api, "tenTepDangXem(S)") == ds.name, "tab mở đúng tệp danh sách",
       chay_js(api, "tenTepDangXem(S)"))
    ok(chay_js(api, "loaiTepDangXem()") == "congduc",
       "giao diện nhớ đây là DANH SÁCH, không phải văn bản thường")
    ok((chay_js(api, "doanDangXem(S, TAI_LIEU).length") or 0) >= 3,
       "vùng đọc hiện các dòng của danh sách",
       chay_js(api, "doanDangXem(S, TAI_LIEU).length"))
    ok("500.000" in (chay_js(api, "doanDangXem(S, TAI_LIEU)"
                                  ".map(d => d.chu).join(' | ')") or ""),
       "hiện SỐ TIỀN như trong tệp, không phải chữ đọc")

    # Đổi sang tab khác rồi quay lại: Python phải dựng lại playlist DANH SÁCH,
    # không được đọc dòng hiển thị theo kiểu văn bản thường.
    chay_js(api, "vanTayDaGui = ''; guiDoanSangPython()", 1.5)
    cho_den(lambda: getattr(api, "_loai_tai_lieu", "") == "congduc", 20, 0.3)
    ok(api._loai_tai_lieu == "congduc",
       "quay lại tab danh sách thì Python dựng lại đúng kiểu",
       api._loai_tai_lieu)
    cau = next((s["text"] for s in api._playlist if s.get("loai") == "nguoi"), "")
    ok("nghìn" in cau.lower() or "trăm" in cau.lower(),
       "câu engine đọc dựng theo mẫu, số thành chữ", cau[:60])

    ghi("\n--- H. Nút ĐÓNG có làm tiến trình thoát sạch không ---")
    ghi("       (bấm nút đóng thật; phần còn lại kiểm sau khi cửa sổ tắt)")


def chot(api):
    TEP_KET_QUA.parent.mkdir(parents=True, exist_ok=True)

    # Bài kiểm này chạy app thật nên phải tự chứng minh nó không để lại vết
    # trên dữ liệu của chủ dự án. Đã vấp: nó từng ghi đè hoso-v2.json.
    ghi("\n--- I. Bài kiểm KHÔNG được đụng dữ liệu thật ---")
    import DocCongDuc as engine
    from giaodien import he_thong, ho_so
    from giaodien import nhat_ky as nk
    from giaodien_moi import ho_so_v2
    for nhan, duong in [("hồ sơ bản mới", ho_so_v2.TEP), ("nhật ký", nk.TEP_LOG),
                        ("cấu hình", engine.CONFIG_FILE),
                        ("từ điển", engine.TUDIEN_FILE),
                        ("tuỳ chọn giao diện", he_thong.TUY_CHON_FILE),
                        ("hồ sơ bản cũ", ho_so.TEP)]:
        ok(Path(duong).parent != BASE_DIR,
           f"{nhan} trỏ ra ngoài thư mục chương trình", Path(duong).name)
    # Đo thẳng trên tệp thật: có tệp nào bị chạm trong lúc bài kiểm chạy không.
    cham = [t for t in ("cauhinh.ini", "tudien.ini", "hoso.json", "hoso-v2.json",
                        "giaodien.json", "congduc.txt", "noidung.ini")
            if (BASE_DIR / t).exists()
            and (BASE_DIR / t).stat().st_mtime >= BAT_DAU]
    ok(not cham, "KHÔNG tệp dữ liệu thật nào bị ghi trong lúc chạy", cham or "sạch")

    con = dem_ffplay()
    ghi(f"  {'ĐẠT ' if con == 0 else 'LỆCH'} không còn ffplay nào sót lại  →  {con}")
    tong = sum(1 for d in dong if d.strip().startswith(("ĐẠT", "LỆCH")))
    ghi()
    ghi(f"{'XANH — khớp hết' if loi == 0 else f'ĐỎ — {loi} chỗ lệch'}"
        f"  ({tong} phép kiểm)")
    TEP_KET_QUA.write_text("\n".join(dong), encoding="utf-8")
    print(f"\nĐã ghi: {TEP_KET_QUA}")


def canh_gio():
    time.sleep(TRAN_GIAY)
    print(f"\n!! Quá {TRAN_GIAY} giây — thoát cưỡng bức")
    os._exit(3)


def doi_duong_du_lieu_sang_tam():
    """Trỏ MỌI đường ghi sang thư mục tạm TRƯỚC khi mở cửa sổ.

    Từ 2026-08-13 ApiMoi không tự khoá đường ghi nữa (người dùng bấm Lưu thì
    phải lưu được), nên bài kiểm phải tự lo: chép dữ liệu thật ra thư mục tạm
    rồi trỏ engine sang đó. Chạy thử vẫn đi đúng đường ghi thật - kiểm được cả
    chức năng lưu - mà không để lại vết nào trên tệp của chủ dự án.

    Bài này chạy app THẬT, mà giao diện tự lưu hồ sơ mỗi khi đổi tab - nên nó
    đã ghi đè hoso-v2.json của chủ dự án bằng hai tab bịa ra ở mục G. Đúng cái
    họ lỗi mà khoa_du_lieu.py đi bịt: ở đó rào kỹ 6 tệp của bản cũ rồi để hở
    đúng tệp của bản mới, vì đường lưu này đi qua JS chứ không qua Python.

    Nhật ký lỗi cũng trỏ đi: GiongViet-loi.log là đường chẩn đoán khi máy chủ dự
    án trở chứng, trộn rác của bài kiểm vào là làm hỏng đúng công cụ cần lúc
    khẩn cấp.
    """
    import shutil

    import DocCongDuc as engine
    from giaodien import he_thong, ho_so
    from giaodien import nhat_ky as nk
    from giaodien_moi import ho_so_v2

    tam = Path(tempfile.gettempdir()) / "gd-tu-kiem"
    if tam.exists():
        shutil.rmtree(tam, ignore_errors=True)
    tam.mkdir(parents=True, exist_ok=True)

    # Chép bản sao để chương trình vẫn có giọng, từ điển, nhịp đọc như thật.
    for ten in ("cauhinh.ini", "tudien.ini", "hoso.json", "noidung.ini",
                "congduc.txt", "giaodien.json"):
        goc = BASE_DIR / ten
        if goc.exists():
            shutil.copy2(goc, tam / ten)

    engine.CONFIG_FILE = tam / "cauhinh.ini"
    engine.TUDIEN_FILE = tam / "tudien.ini"
    engine.GIONG_RIENG_DIR = tam / "giong_rieng"
    engine.GIONG_RIENG_FILE = tam / "giong_rieng" / "danhsach.json"
    he_thong.TUY_CHON_FILE = tam / "giaodien.json"
    ho_so.TEP = tam / "hoso.json"
    ho_so_v2.TEP = tam / "hoso-v2.json"
    nk.TEP_LOG = tam / "GiongViet-loi.log"
    return tam


def main():
    from giaodien_moi.cau_noi_moi import ApiMoi

    global tam
    tam = doi_duong_du_lieu_sang_tam()
    ghi(f"(hồ sơ và nhật ký của bài kiểm để ở {tam})")

    api = ApiMoi(VUNG)
    x, y, rong, cao = VUNG
    api._window = webview.create_window(
        "Giọng Việt", str(BASE_DIR / "ui-moi" / "index.html"),
        js_api=api, x=x, y=y, width=rong, height=cao,
        min_size=(980, 620), frameless=True, easy_drag=False,
        text_select=True, background_color="#F3F3F3")

    threading.Thread(target=canh_gio, daemon=True).start()

    def bat_dau():
        try:
            kich_ban(api)
        except Exception as e:                 # noqa: BLE001
            import traceback
            ghi(f"\n!! Kịch bản vỡ: {type(e).__name__} {e}")
            ghi(traceback.format_exc())
        finally:
            try:
                api._window.evaluate_js(
                    "document.querySelector('[data-cuaso=\"dong\"]').click()")
            except Exception:                  # noqa: BLE001
                api._window.destroy()

    threading.Thread(target=bat_dau, daemon=True).start()
    webview.start(debug=False)

    api._don_dep()
    time.sleep(1.0)
    chot(api)
    sys.stdout.flush()
    sys.stderr.flush()
    os._exit(1 if loi else 0)


if __name__ == "__main__":
    main()
