# -*- coding: utf-8 -*-
"""Tái hiện L5 — nhân bản giọng xong không nạp lại danh sách giọng.

Rủi ro thật sự không phải "danh sách hiện thiếu một dòng". Nó là thế này:
người dùng lớn tuổi ngồi đợi mấy phút cho máy học giọng con cháu mình, máy báo
"Đã tạo xong", họ bấm "Dùng giọng này" — rồi ô Giọng đọc ở cột phải TRỐNG
KHÔNG. Không tên, không báo lỗi, không chỗ nào nói vì sao. Với người không rành
máy tính, màn hình trống nghĩa là "hỏng rồi", và họ mất luôn công vừa bỏ ra.

Bài này KHÔNG đọc code rồi suy luận. Nó nạp đúng 10 tệp JS mà index.html khai,
trong DOM giả (cùng cách kiem/kiem-giao-dien.mjs vẫn làm), rồi đi đúng đường
mà nút "Dùng giọng này" đi — giao-dien.js:1492 `dat(datGiong(S, ...))` — và
ĐỌC RA chuỗi mà cột phải in.

Không chạy tổng hợp tiếng, không nạp mô hình, không chạm dữ liệu người dùng:
chỉ ĐỌC mã nguồn và chạy JS trong node. Tệp tạm nằm ở %TEMP%.
"""
# --- dat goc du an tu vi tri tep nay (bai nam trong kiem/) ---
import os as _os, sys as _sys
from pathlib import Path as _Path
_os.environ.setdefault('GIONGVIET_GOC', str(_Path(__file__).resolve().parent.parent))
_sys.path.insert(0, _os.environ['GIONGVIET_GOC'])
# --- het shim ---
import io
import json
import os
import re
import subprocess
import sys
from pathlib import Path

# Kịch bản này nằm ở thư mục tạm, ngoài kho — nên gốc dự án tìm bằng cách đi
# ngược từ thư mục làm việc, KHÔNG viết cứng đường dẫn máy nào. Ai chạy ở máy
# khác, kho tải về chỗ khác, vẫn đúng.
def _tim_goc() -> Path:
    if len(sys.argv) > 1:
        return Path(sys.argv[1]).resolve()
    if os.environ.get("GIONGVIET_GOC"):
        return Path(os.environ["GIONGVIET_GOC"]).resolve()
    p = Path.cwd().resolve()
    for ung in [p, *p.parents]:
        if (ung / "GiongViet.py").is_file() and (ung / "ui-moi").is_dir():
            return ung
    raise SystemExit("Không tìm ra gốc dự án (cần GiongViet.py + ui-moi/)")


_GOC = _tim_goc()
_TOI = Path(__file__).resolve().parent
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8",
                              line_buffering=True)

loi = 0


def ok(dk, nhan, them=""):
    global loi
    print(f"  {'ĐẠT ' if dk else 'LỆCH'} {nhan}{'  →  ' + str(them) if them else ''}")
    if not dk:
        loi += 1


def doc(p: Path) -> str:
    return p.read_text(encoding="utf-8", errors="replace")


print(f"Gốc dự án: {_GOC}")
print(f"(chỉ ĐỌC; không ghi gì vào đó — tệp tạm ở {_TOI})\n")

UI = (_GOC / "src" / "web") if (_GOC / "src" / "web").exists() else (_GOC / "ui-moi")
TEP_UI = sorted(list(UI.glob("*.js")) + list(UI.glob("*.html")))

print("--- A. Giao diện có xử lý khoá 'thuVien' Python đẩy sang không? ---")
for tu_khoa, phan_biet_hoa in (("thuVien", True), ("thu_vien", True),
                               ("thuvien", False)):
    hit = []
    for p in TEP_UI:
        for i, dong in enumerate(doc(p).splitlines(), 1):
            so = dong if phan_biet_hoa else dong.lower()
            if tu_khoa in so:
                hit.append(f"{p.name}:{i}: {dong.strip()[:96]}")
    print(f"  · từ khoá {tu_khoa!r}: {len(hit)} chỗ")
    for h in hit:
        print(f"      {h}")

nguon_ui = "\n".join(doc(p) for p in TEP_UI)
ok('"thuVien"' not in nguon_ui and "'thuVien'" not in nguon_ui
   and ".thuVien" not in nguon_ui and "thuVien:" not in nguon_ui,
   "KHÔNG chỗ nào trong ui-moi/ đọc khoá thuVien")

# Mấy chỗ vừa in ra là tên HÀM API (moi_thu_vien_giong) và một dòng nằm giữa
# khối chú thích đầu man-giong.js — không phải chỗ đọc khoá đẩy về. Nói rõ ra
# để không ai nhìn con số 4 rồi tưởng "có xử lý".
dinh = [l.strip() for l in nguon_ui.splitlines()
        if "thu_vien" in l or "thuVien" in l]
ok(all("moi_thu_vien_giong" in d or "thu_vien_giong.py" in d for d in dinh),
   "cả 4 chỗ đều là tên hàm API hoặc nhắc tên tệp Python trong chú thích",
   len(dinh))

print("\n--- B. Mọi lời gọi datGiongThat trong ui-moi/ ---")
goi = []
for p in TEP_UI:
    for i, dong in enumerate(doc(p).splitlines(), 1):
        if "datGiongThat" not in dong:
            continue
        loai = "ĐỊNH NGHĨA" if re.search(r"function\s+datGiongThat", dong) \
            else ("chú thích" if dong.lstrip().startswith(("//", "*", "/*"))
                  else "LỜI GỌI")
        goi.append((loai, f"{p.name}:{i}", dong.strip()[:96]))
for loai, vt, dong in goi:
    print(f"  {loai:<10} {vt:<20} {dong}")
so_goi = [g for g in goi if g[0] == "LỜI GỌI"]
ok(len(so_goi) == 2, f"đúng {len(so_goi)} lời gọi thật",
   ", ".join(g[1] for g in so_goi))

print("\n--- C. Phía Python có thật sự đẩy khoá 'thuVien' không? ---")
cn = (_GOC / "src" / "core" / "cau_noi.py") if (_GOC / "src" / "core" / "cau_noi.py").exists() else (_GOC / "giaodien" / "cau_noi.py")
dong_cn = doc(cn).splitlines()
for i, d in enumerate(dong_cn, 1):
    if "thuVien" in d:
        print(f"  cau_noi.py:{i}: {d.strip()}")
ok(any("_day(" in d and '"thuVien"' in d for d in dong_cn),
   "cau_noi.py CÓ _day({'thuVien': ...}) — đẩy thật, không phải suy đoán")
ok(any('self._goi_js("window.gd.push", patch)' in d for d in dong_cn),
   "_day đẩy qua window.gd.push")

# Bên nhận của window.gd.push là hàm trong datNguoiNhan(...) ở giao-dien.js.
gd = doc(UI / "giao-dien.js").replace("\r\n", "\n")
than = gd[gd.index("datNguoiNhan((goi) => {"):]
than = than[:than.index("\n});")]
khoa_xu_ly = sorted(set(re.findall(r"goi\.([A-Za-z_]\w*)", than)))
print(f"  bên nhận push xử lý các khoá: {khoa_xu_ly}")
ok("thuVien" not in khoa_xu_ly and "voices" not in khoa_xu_ly,
   "bên nhận KHÔNG đụng tới thuVien lẫn voices → gói tin rơi vào hư không")

print("\n--- D. Hệ quả: chạy giao diện THẬT trong DOM giả, đọc chuỗi in ra ---")
kq = subprocess.run(["node", str(_TOI / "soi_nap_lai_giong.mjs"), str(UI)],
                    capture_output=True, text=True, encoding="utf-8", timeout=180)
if kq.returncode != 0:
    print(kq.stdout[-2000:])
    print(kq.stderr[-2000:])
    raise SystemExit("KHÔNG chạy được node — không kết luận được phần hệ quả")
d = json.loads(kq.stdout.strip().splitlines()[-1])


def hien(x):
    return "(RỖNG)" if x == "" else ("(không có thẻ)" if x is None else repr(x))


t, s = d["truoc"], d["sau"]
print(f"  TRƯỚC khi bấm 'Dùng giọng này'"
      f"\n     hồ sơ đang trỏ giọng : {t['maHoSo']!r}"
      f"\n     ô Giọng đọc cột phải : {hien(t['oGiong'])}"
      f"\n     tooltip ô giọng      : {hien(t['tieuDe'])}"
      f"\n     dòng giọng cột trái  : {hien(t['cotTrai'])}"
      f"\n     GIONG có {t['soGiong']} giọng")
print(f"  SAU khi bấm 'Dùng giọng này' (giọng vừa nhân bản)"
      f"\n     hồ sơ đang trỏ giọng : {s['maHoSo']!r}"
      f"\n     GIONG.find(...)      : {s['timThay']}"
      f"\n     ô Giọng đọc cột phải : {hien(s['oGiong'])}"
      f"\n     tooltip ô giọng      : {hien(s['tieuDe'])}"
      f"\n     dòng giọng cột trái  : {hien(s['cotTrai'])}")

ok(t["oGiong"], "trước đó ô giọng có tên hẳn hoi", hien(t["oGiong"]))
ok(s["timThay"] == "undefined", "giọng mới KHÔNG có trong GIONG", s["timThay"])
ok(s["oGiong"] == "", "ô Giọng đọc cột phải in ra chuỗi RỖNG", hien(s["oGiong"]))
ok(s["tieuDe"] == "", "tooltip cũng rỗng — rê chuột vào cũng không biết giọng gì")
ok(s["cotTrai"] == "", "dòng giọng dưới tên hồ sơ ở cột trái cũng rỗng")

p1, p2 = d["sauPush"], d["sauGiongXong"]
print(f"\n  Đẩy đúng gói Python gửi ( {{voices, voiceId, thuVien}} rồi {{thuVien}} )"
      f"\n     GIONG: {t['soGiong']} → {p1['soGiong']} giọng · "
      f"dropdown {p1['soDropdown']} mục · tìm giọng mới: {p1['timThay']}")
print(f"  Rồi Python gọi window.gd.giongXong('Giọng bác Tuấn mới')"
      f"\n     GIONG: {p2['soGiong']} giọng · tìm giọng mới: {p2['timThay']}"
      f"\n     ô Giọng đọc cột phải : {hien(p2['oGiong'])}")

ok(p1["soGiong"] == t["soGiong"] and p1["timThay"] == "undefined",
   "gói đẩy về KHÔNG làm danh sách giọng nhúc nhích")
ok(p2["soGiong"] == t["soGiong"] and p2["timThay"] == "undefined",
   "giongXong xong danh sách vẫn thiếu giọng mới")
ok(p2["oGiong"] == "", "ô giọng vẫn rỗng sau khi Python báo xong")

dc = d["doiChung"]
print(f"\n  ĐỐI CHỨNG — gọi tay datGiongThat({{giong: [...]}}) đúng một câu:"
      f"\n     GIONG: {dc['soGiong']} giọng · tên tìm được: {dc['timThay']}"
      f"\n     ô Giọng đọc cột phải : {hien(dc['oGiong'])}")
ok(dc["oGiong"] == "Giọng bác Tuấn mới",
   "gọi datGiongThat là ô giọng có tên ngay → hàm không hỏng, chỉ là KHÔNG AI GỌI",
   hien(dc["oGiong"]))

print(f"\n{'XANH — tái hiện đúng như mô tả' if loi == 0 else f'ĐỎ — {loi} chỗ lệch'}")
sys.exit(1 if loi else 0)
