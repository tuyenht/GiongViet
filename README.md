# Giọng Việt

Chương trình đọc văn bản tiếng Việt thành tiếng nói, chạy hoàn toàn trên máy.
Dùng ở chùa. **Người dùng cuối phần lớn lớn tuổi, không rành máy tính** — mọi
quyết định thiết kế lấy đó làm gốc.

Tiếng nói do mô hình **VieNeu-TTS** tạo ra ngay trên máy, không gửi văn bản đi
đâu cả.

---

## Làm được gì

| | |
|---|---|
| Đọc văn bản | `.txt`, `.docx`, hoặc dán thẳng từ clipboard |
| Hồ sơ đọc | Mỗi hồ sơ nhớ riêng giọng, tốc độ, cao độ, âm lượng và các tệp đang mở |
| Chỉnh tiếng | Tốc độ −50…+100% · Cao độ ±12 nửa cung · Âm lượng 0…100% |
| Thẻ cảm xúc | Gắn `[cười]` · `[thở dài]` · `[hắng giọng]` cho từng đoạn |
| Soát văn bản | Chỉ ra chỗ máy dễ đọc sai trước khi xuất |
| Từ điển phát âm | Dạy máy đọc đúng tên riêng, từ viết tắt |
| Thư viện giọng | Chọn giọng theo vùng miền và giới tính; nhân bản giọng từ tệp mẫu |
| Xuất tệp | WAV 16/24 bit · MP3 320/128 kbps · một tệp, mỗi đoạn một tệp, hoặc cắt theo 10 phút |
| Danh sách công đức | Đọc danh sách tên kèm số tiền theo mẫu câu có sẵn |

---

## Chạy

```bat
py GiongViet.py
```

Lần đầu cần cài phụ thuộc và tải mô hình:

```bat
CaiDat.bat
```

Mô hình VieNeu (~330 MB) và ffmpeg (~200 MB) **không nằm trong kho** — chúng
vượt giới hạn 100 MB một tệp của GitHub. `CaiDat.bat` lo phần tải.

## Đóng gói

```bat
set GIONGDOC_TU_DONG=1 && DongGoi.bat
```

Ra `GiongViet\GiongViet.exe` (dạng một thư mục). Bản đóng gói **phải** có đủ ba
tệp mấu chốt, thiếu cái nào cũng hỏng theo một kiểu riêng:

| Tệp | Thiếu thì |
|---|---|
| `_internal\ui-moi\index.html` | cửa sổ mở ra trang trắng |
| `_internal\sea_g2p\sea_g2p.bin` | `os error 2` ngay lúc bấm đọc |
| `_internal\vieneu\assets\voices_v3_turbo.json` | danh sách giọng rỗng |

---

## Cấu trúc

```
GiongViet.py           điểm vào — cửa sổ pywebview + WebView2, không khung
DocCongDuc.py          ENGINE: VieNeu-TTS, chuẩn hoá tiền/tên/số, giọng riêng

giaodien/              THƯ VIỆN DÙNG CHUNG (không phải bản cũ — cả 15 tệp đều đang dùng)
  cau_noi.py             lớp Api, cầu JS ↔ Python
  bo_doc.py              vòng đọc playlist        │ có SỐ PHIÊN
  nghe_thu.py            phát thử một giọng       │ có SỐ PHIÊN
  xuat_file.py           ghép WAV (đường xuất của bản cũ)
  du_lieu.py · ho_so.py · soat.py · tu_dien.py · cai_dat.py
  mo_hinh.py · ds_giong.py · thu_vien_giong.py · he_thong.py · nhat_ky.py

giaodien_moi/          TẦNG ỨNG DỤNG
  cau_noi_moi.py         ApiMoi — kế thừa Api, thêm cửa cho giao diện mới
  xuat_moi.py            bộ xuất WAV/MP3          │ có SỐ PHIÊN
  am_thanh_loc.py        dựng chuỗi -af cho ba thanh chỉnh
  ho_so_v2.py · soat_moi.py · luu_tep.py · so_dien_thoai.py · khoa_du_lieu.py
  kiem_*.py              18 bộ kiểm, 757 phép kiểm

ui-moi/                GIAO DIỆN
  index.html · app.css · man-hinh-chinh.css
  giao-dien.js           lớp vẽ và bắt sự kiện
  trang-thai.js          mô hình trạng thái thuần, không DOM
  cau-noi.js             cầu JS ↔ Python (window.gd)
  hop-thoai.js           hộp thoại và thông báo góc
  man-soat.js · man-giong.js · man-tudien.js · man-caidat.js
  kiem-*.mjs             bộ kiểm giao diện

design_handoff_giongdoc/   đặc tả và bản mẫu thiết kế (bản gốc, không sửa)
plans/                     nhật ký các phiên làm việc
_luutru/                   bản cũ đã ngừng dùng, giữ để đối chiếu
```

---

## Bộ kiểm

```bat
py giaodien_moi\kiem_xuat_moi.py        rem   và 13 bộ .py khác
node ui-moi\kiem-giao-dien.mjs          rem   và 3 bộ .mjs khác
py KiemBanExe.py                        rem   kiểm chính bản .exe
```

**757 phép kiểm / 18 bộ.** Bộ kiểm chạy hoàn toàn trên `%TEMP%`, không đụng dữ
liệu hay nhật ký thật.

Ba nguyên tắc rút ra từ những lần vấp thật, nay được chính bộ kiểm canh:

- **Chạy được từ source KHÔNG chứng minh `.exe` chạy được.** Thiếu
  `--collect-data` là danh sách giọng rỗng; thiếu `--add-data ui-moi` là trang
  trắng. Chỉ lộ ra ở bản đóng gói.
- **Mọi nguồn phát tiếng phải có SỐ PHIÊN.** Cờ dừng không đủ: tổng hợp một câu
  có thể mất tới 40 giây, luồng cũ tỉnh dậy sau đó vẫn phát chồng lên.
- **Không bày nút giả.** Mọi nút phải nối vào chức năng có thật, nếu không thì
  gỡ khỏi giao diện.

---

## Dữ liệu người dùng

Không nằm trong kho, và không được đưa lên: `congduc.txt` (tên và số tiền người
thật), `cauhinh.ini`, `noidung.ini`, `tudien.ini`, `hoso*.json`, `giaodien.json`,
`giong_rieng/`, `*-loi.log`.

---

## Giấy phép

Chưa chọn. Kho đang để riêng tư.
