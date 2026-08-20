# -*- coding: utf-8 -*-
"""L4 — Tài liệu đánh khoá bằng TÊN TỆP TRẦN.

Rủi ro thật sự cần chứng minh (không phải "code trông có vẻ sai"):
người dùng ở chùa hay chia danh sách theo tháng — Thang7\\congduc.txt,
Thang8\\congduc.txt. Nếu cầu nối Python trả về TÊN TRẦN (p.name) và giao diện
lấy chuỗi đó làm khoá cho kho tài liệu, kho đường dẫn, kho loại tệp và kho thẻ
cảm xúc, thì mở tệp thứ hai sẽ ĐÈ LÊN tệp thứ nhất: hai tab cùng tên, cùng nội
dung, và đường dẫn của tệp thứ nhất mất hẳn — mất luôn sau khi đóng chương
trình, vì phần đó được ghi xuống hoso-v2.json.

Bài này KHÔNG đọc thành tiếng: không nạp mô hình VieNeu, không gọi ffplay.
Phần dựng playlist (thứ dẫn tới tổng hợp tiếng) được giả lập.
Mọi tệp thử nằm trong thư mục tạm; không chạm một byte dữ liệu người dùng.

Chạy:  PYTHONIOENCODING=utf-8 py kiem/kiem_khoa_ten_tep.py
"""
# --- dat goc du an tu vi tri tep nay (bai nam trong kiem/) ---
import os as _os, sys as _sys
from pathlib import Path as _Path
_os.environ.setdefault('GIONGVIET_GOC', str(_Path(__file__).resolve().parent.parent))
_sys.path.insert(0, _os.environ['GIONGVIET_GOC'])
# --- het shim ---
import io
import os
import subprocess
import sys
import tempfile
from pathlib import Path

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8",
                              line_buffering=True)


def _tim_goc() -> Path:
    """Gốc dự án = thư mục có DocCongDuc.py. Dò từ nơi đang đứng đi lên,
    rồi từ chỗ đặt kịch bản đi lên. KHÔNG viết cứng đường dẫn."""
    mo = os.environ.get("GIONGVIET_GOC", "")
    ung_vien = ([Path(mo)] if mo else []) \
        + [Path.cwd()] + list(Path.cwd().parents) \
        + [Path(__file__).resolve().parent] + list(Path(__file__).resolve().parents)
    for d in ung_vien:
        if (d / "DocCongDuc.py").is_file() and (d / "giaodien_moi").is_dir():
            return d
    raise SystemExit("Không tìm ra gốc dự án (thư mục chứa DocCongDuc.py).")


_GOC = _tim_goc()
sys.path.insert(0, str(_GOC))

loi = 0


def ok(dk, nhan, them=""):
    global loi
    print(f"  {'ĐẠT ' if dk else 'LỆCH'} {nhan}{'  →  ' + str(them) if them else ''}")
    if not dk:
        loi += 1


def dong_nguon(tep: Path, so: int) -> str:
    return tep.read_text(encoding="utf-8").splitlines()[so - 1]


print(f"Gốc dự án: {_GOC}")
print(f"Python   : {sys.version.split()[0]}")

# Vân tay dữ liệu người dùng, lấy TRƯỚC khi nạp bất cứ mã ứng dụng nào.
DU_LIEU_NGUOI_DUNG = ("cauhinh.ini", "noidung.ini", "congduc.txt", "tudien.ini",
                      "hoso.json", "hoso-v2.json", "giaodien.json")


def _van_tay():
    import hashlib
    d = {}
    for ten in DU_LIEU_NGUOI_DUNG:
        t = _GOC / ten
        d[ten] = (hashlib.md5(t.read_bytes()).hexdigest() if t.is_file()
                  else "KHÔNG-CÓ-TỆP")
    return d


VAN_TAY_TRUOC = _van_tay()

# ---------------------------------------------------------------- A. Nguyên văn mã nguồn
print("\n--- A. Nguyên văn mã nguồn: trường 'ten' trả về gì ---")
CN = _GOC / "giaodien_moi" / "cau_noi_moi.py"
GD = _GOC / "ui-moi" / "giao-dien.js"
TT = _GOC / "ui-moi" / "trang-thai.js"

# Cắt theo NỘI DUNG, không theo số dòng. Trước đây mục này neo cứng vào
# cau_noi_moi.py 557/599 và giao-dien.js 947/948/958/960/962. Đo ngày 19/8: năm
# số của giao-dien.js đã trôi sang chỗ khác hẳn và in ra classList.toggle
# ('dang-doc') / cuonToiDoanHienTai — rác, chẳng dính gì tới khoá tên tệp — mà
# bài VẪN XANH vì chúng chỉ nằm trong print(). Neo cứng vào tệp đang sửa hằng
# ngày thì hỏng lặng lẽ như thế. Dự án đã vấp đúng họ này ở kiem_so_nguoi_nhom.py.
def cau_tra_ve(tep, ten_ham):
    """Câu return đầu tiên trong thân một hàm, tìm bằng tên hàm.

    Khớp tên hàm ĐẦY ĐỦ (`def ten(`) chứ không khớp tiền tố: có `moi_doc_tep`
    và `moi_doc_tep_v2` cạnh nhau thì khớp tiền tố bắt trúng hàm sai mà không
    ai biết.

    Và dừng ở CUỐI THÂN HÀM, không quét cứng 80 dòng. Quét tràn sang hàm kế
    tiếp là phép canh vẫn xanh nhờ câu return của một hàm khác — đúng lúc hàm
    thật đã bị sửa hỏng.
    """
    dong = tep.read_text(encoding="utf-8").splitlines()
    i = next((k for k, d in enumerate(dong)
              if d.strip().startswith(f"def {ten_ham}(")), -1)
    if i < 0:
        return f"KHÔNG TÌM THẤY def {ten_ham}"
    thut = len(dong[i]) - len(dong[i].lstrip())
    for d in dong[i + 1:]:
        con = d.strip()
        # Hết thân hàm: một dòng có nội dung, thụt bằng hoặc ít hơn dòng `def`.
        if con and (len(d) - len(d.lstrip())) <= thut:
            break
        if "return {" in d and '"ten"' in d:
            return d
    return f"KHÔNG THẤY câu return có 'ten' trong thân {ten_ham}"


def khoi_ham_js(tep, mo_dau, so_dong=30):
    """Thân một hàm JS, cắt bằng dòng mở đầu chứ không bằng số dòng."""
    dong = tep.read_text(encoding="utf-8").splitlines()
    i = next((k for k, d in enumerate(dong) if d.startswith(mo_dau)), -1)
    return dong[i:i + so_dong] if i >= 0 else []


ds_ham = cau_tra_ve(CN, "moi_doc_danh_sach")
tep_ham = cau_tra_ve(CN, "moi_doc_tep")
print(f"  cau_noi_moi.py moi_doc_danh_sach| {ds_ham.strip()}")
print(f"  cau_noi_moi.py moi_doc_tep      | {tep_ham.strip()}")
print(f"  cau_noi_moi.py moi_dan_van_ban  | {cau_tra_ve(CN, 'moi_dan_van_ban').strip()}")
for d in khoi_ham_js(GD, "function datTaiLieu"):
    if any(x in d for x in ("kq.ten", "TAI_LIEU[ten]", "chuaLuu.delete(ten)",
                            "[ten]: kq.duongDan", "[ten]: kq.loai")):
        print(f"  giao-dien.js datTaiLieu| {d.strip()}")
tt = TT.read_text(encoding="utf-8").splitlines()
print("  trang-thai.js| " + next(d.strip() for d in tt if d.startswith("const theCuaDoan")))

ok('"ten": p.name' in ds_ham,
   "moi_doc_danh_sach trả ten = p.name (tên trần)", ds_ham.strip())
ok('"ten": p.name' in tep_ham,
   "moi_doc_tep trả ten = p.name (tên trần)", tep_ham.strip())
ok('"duongDan": str(p)' in tep_ham,
   "đường dẫn ĐẦY ĐỦ vẫn có trong cùng gói tin, chỉ là không dùng làm khoá")
# moi_dan_van_ban trước đây chỉ được IN ra chứ không có phép canh nào — đúng cái
# bệnh mà bài này sinh ra để chữa. Nó là đường DÁN CHỮ, việc Hướng dẫn nhanh bảo
# làm đầu tiên, và là ca nặng nhất vì bản dán không có tệp nào trên đĩa để mở lại.
dan_ham = cau_tra_ve(CN, "moi_dan_van_ban")
ok('"ten": "Văn bản đã dán"' in dan_ham,
   "moi_dan_van_ban trả tên CỐ ĐỊNH — dán hai lần là hai bản cùng một khoá",
   dan_ham.strip())
ok('"duongDan": ""' in dan_ham,
   "và KHÔNG có đường dẫn, nên khoá theo đường dẫn không cứu được ca dán")
# Năm dòng print bên trên chỉ có ích khi chúng trỏ đúng vào datTaiLieu. Canh
# luôn điều đó, không thì lần sau lại in rác mà không ai biết.
ok(any("TAI_LIEU[ten]" in d for d in khoi_ham_js(GD, "function datTaiLieu")),
   "datTaiLieu vẫn là chỗ ghi TAI_LIEU theo tên trần")
# Tìm theo NỘI DUNG, không theo số dòng: thêm bớt vài dòng ở đầu tệp là lát cắt
# theo số dòng trỏ sai chỗ, rồi phép kiểm đỏ lên vì lý do chẳng liên quan gì.
ok(any("kq.ten" in d for d in GD.read_text(encoding="utf-8").splitlines()),
   "giao-dien.js lấy khoá từ kq.ten")

# ---------------------------------------------------------------- B. Gọi thật hàm đọc tệp
print("\n--- B. Gọi THẬT ApiMoi.moi_doc_tep trên hai tệp trùng tên ---")
tam = Path(tempfile.mkdtemp(prefix="l4_"))
(tam / "Thang7").mkdir()
(tam / "Thang8").mkdir()
p7 = tam / "Thang7" / "congduc.txt"
p8 = tam / "Thang8" / "congduc.txt"
p7.write_text("THANG BAY - Nguyen Van A - 500.000\n", encoding="utf-8")
p8.write_text("THANG TAM - Tran Thi B - 200.000\n", encoding="utf-8")
print(f"  thư mục tạm: {tam}")
print(f"  tệp 1: {p7}")
print(f"  tệp 2: {p8}")

import giaodien_moi.cau_noi_moi as cnm  # noqa: E402
import DocCongDuc as engine             # noqa: E402

# moi_doc_tep không dùng tới self -> gọi thẳng hàm của lớp, khỏi dựng ApiMoi
# (dựng ApiMoi là nạp mô hình + đọc cấu hình thật).
kq7 = cnm.ApiMoi.moi_doc_tep(None, str(p7))
kq8 = cnm.ApiMoi.moi_doc_tep(None, str(p8))
print(f"  kq7 = {{'ten': {kq7['ten']!r}, 'duongDan': {kq7['duongDan']!r}, "
      f"'chu': {kq7['doan'][0]['chu']!r}}}")
print(f"  kq8 = {{'ten': {kq8['ten']!r}, 'duongDan': {kq8['duongDan']!r}, "
      f"'chu': {kq8['doan'][0]['chu']!r}}}")

ok(kq7["ten"] == kq8["ten"] == "congduc.txt",
   "hai tệp khác thư mục, khác nội dung -> CÙNG một trường 'ten'",
   f"{kq7['ten']!r} == {kq8['ten']!r}")
ok(kq7["duongDan"] != kq8["duongDan"],
   "đường dẫn thì vẫn khác nhau (nên khoá theo nó là sửa được)")
ok(kq7["doan"][0]["chu"] != kq8["doan"][0]["chu"],
   "nội dung hai tệp thật sự khác nhau")

kho_gia = {}
kho_gia[kq7["ten"]] = kq7["doan"]
kho_gia[kq8["ten"]] = kq8["doan"]
print(f"  kho_gia[ten] sau hai lần gán: {len(kho_gia)} mục, "
      f"nội dung còn lại = {kho_gia['congduc.txt'][0]['chu']!r}")
ok(len(kho_gia) == 1 and "THANG TAM" in kho_gia["congduc.txt"][0]["chu"],
   "đánh khoá bằng 'ten' -> tệp sau đè tệp trước")

# ---------------------------------------------------------------- C. Đường danh sách công đức
print("\n--- C. Đường DANH SÁCH công đức (moi_doc_danh_sach) ---")
try:
    class BoDocGia:
        def dat_playlist(self, *a, **k):
            pass

    class ApiGia(cnm.ApiMoi):
        """Chỉ thay phần dẫn tới TỔNG HỢP TIẾNG bằng đồ giả. Thân hàm
        moi_doc_danh_sach vẫn là mã thật của sản phẩm."""

        def __init__(self):
            self._records, self._canh_bao = None, None
            self._loai_tai_lieu = None
            self._noidung, self._cfg, self._tudien = None, {}, {}
            self._trong_so_cache = {}
            self._moc_phat = None
            self._playlist, self._doan, self._doan_cua_mau = [], [], []
            self._bo_doc = BoDocGia()
            self._nghe_rieng = False

        def _nap_noi_dung(self):
            pass

        def _nap_truoc_mau_dau(self):
            pass

    goc_build = engine.build_playlist_congduc
    engine.build_playlist_congduc = lambda records, *a, **k: [
        {"loai": "nguoi", "rec": r} for r in records]
    try:
        a = ApiGia()
        d7 = a.moi_doc_danh_sach(str(p7))
        d8 = a.moi_doc_danh_sach(str(p8))
    finally:
        engine.build_playlist_congduc = goc_build

    print(f"  d7 = {{'ten': {d7['ten']!r}, 'duongDan': {d7['duongDan']!r}, "
          f"'loai': {d7['loai']!r}, 'doan[0].chu': {d7['doan'][0]['chu']!r}}}")
    print(f"  d8 = {{'ten': {d8['ten']!r}, 'duongDan': {d8['duongDan']!r}, "
          f"'loai': {d8['loai']!r}, 'doan[0].chu': {d8['doan'][0]['chu']!r}}}")
    ok(d7["ten"] == d8["ten"] == "congduc.txt",
       "đường danh sách cũng trả CÙNG một 'ten'",
       f"{d7['ten']!r} == {d8['ten']!r}")
except Exception as e:                                   # noqa: BLE001
    ok(False, f"không gọi được moi_doc_danh_sach: {type(e).__name__}: {e}")

# ---------------------------------------------------------------- D. Giao diện thật trong DOM giả
print("\n--- D. Chạy ĐÚNG giao-dien.js của sản phẩm (DOM giả, không mở trình duyệt) ---")
mjs = Path(__file__).resolve().parent / "soi_khoa_ten_tep.mjs"
r = subprocess.run(["node", str(mjs), str(_GOC / "ui-moi"), str(p7), str(p8)],
                   capture_output=True, text=True, encoding="utf-8")
print(r.stdout.rstrip())
if r.stderr.strip():
    print("  [node stderr]\n" + r.stderr.rstrip())
ok(r.returncode == 0, "phần JS chạy hết và mọi phép đều ĐẠT",
   f"mã thoát node = {r.returncode}")

# ---------------------------------------------------------------- E. Sạch tay
print("\n--- E. Không chạm dữ liệu người dùng (md5 trước/sau) ---")
VAN_TAY_SAU = _van_tay()
for ten in DU_LIEU_NGUOI_DUNG:
    ok(VAN_TAY_TRUOC[ten] == VAN_TAY_SAU[ten], f"{ten} nguyên vẹn",
       VAN_TAY_SAU[ten])

print(f"\n{'=' * 62}\nKết: {'KHÔNG có phép nào lệch' if loi == 0 else str(loi) + ' phép LỆCH'}")
sys.exit(1 if loi else 0)
