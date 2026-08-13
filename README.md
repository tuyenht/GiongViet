# Giọng Việt

Chương trình đọc văn bản tiếng Việt thành tiếng nói, **chạy hoàn toàn trên máy**.
Tiếng nói do mô hình VieNeu-TTS tạo ra tại chỗ — văn bản không gửi đi đâu cả.

Điều làm nên Giọng Việt không phải là đọc được một tệp `.txt`, mà là **đọc được
dữ liệu sống**: nội dung ghép từ phần cố định và phần thay đổi theo thời gian,
đọc lại lúc nào cũng ra bản mới nhất mà không phải soạn lại từ đầu.

Người dùng cuối phần lớn **lớn tuổi, không rành máy tính**. Mọi quyết định
thiết kế lấy đó làm gốc: không bày nút không dùng được, không thuật ngữ, không
bắt ai đi tìm tệp trên mạng.

---

## Hai loại nguồn

| Nguồn | Là gì | Trạng thái |
|---|---|---|
| **Tĩnh** | Tệp `.txt` / `.docx` trên máy, hoặc chữ dán thẳng vào | ✅ đang chạy |
| **Động** | Nội dung lấy từ URL — bảng tính / tài liệu trên Google Drive; nguồn đổi thì lần đọc sau tự lấy bản mới | 🔜 đang làm |
| **Trộn** | Một bài đọc ghép cả hai: khung cố định + dữ liệu lấy về theo thời điểm | 🔜 đang làm |

**Format là thứ mở rộng được.** Chương trình không gắn cứng vào một loại nội
dung nào — nó nhận một *khuôn đọc* rồi áp lên dữ liệu. Danh sách công đức đọc ở
chùa chỉ là **một khuôn mẫu có sẵn**, không phải mục đích của chương trình.
Cùng cơ chế ấy dùng được cho danh sách học viên, bảng phân công, thông báo theo
ca, lịch trực, kết quả cập nhật hằng ngày — bất cứ thứ gì có phần khung lặp lại
và phần dữ liệu thay đổi.

---

## Làm được gì

**Đọc**
- Mở `.txt`, `.docx`, hoặc dán thẳng từ clipboard
- Nghe cả bài, nghe riêng từng đoạn, hoặc bấm vào đoạn nào nghe đoạn đó
- Chữ chạy theo tiếng, đúng nhịp — tự đo độ trễ thật của máy đang chạy
- Chuẩn hoá sẵn tiền, số, ngày tháng, số điện thoại, tên riêng

**Chỉnh tiếng**
- Tốc độ −50…+100% · Cao độ ±12 nửa cung · Âm lượng 0…100%
- Thẻ cảm xúc `[cười]` · `[thở dài]` · `[hắng giọng]` cho từng đoạn
- Mỗi **hồ sơ đọc** nhớ riêng giọng và ba thanh chỉnh, cùng các tệp đang mở

**Giọng**
- Thư viện giọng theo vùng miền và giới tính
- Nhân bản giọng riêng từ một tệp mẫu
- Từ điển phát âm: dạy máy đọc đúng tên riêng và từ viết tắt

**Soát và xuất**
- Soát văn bản: chỉ ra chỗ máy dễ đọc sai **trước khi** xuất
- Xuất WAV 16/24 bit · MP3 320/128 kbps
- Tách một tệp · mỗi đoạn một tệp · hoặc cắt theo mỗi 10 phút
- Xuất chạy nền được, huỷ giữa chừng không để lại tệp dở

---

## Cài và chạy

```bat
CaiDat.bat        rem  lần đầu: cài thư viện, tải ffmpeg và mô hình giọng
py GiongViet.py
```

**Không cần tải gì bằng tay.** ffmpeg (~200 MB) và mô hình VieNeu (~330 MB)
không nằm trong kho vì vượt giới hạn 100 MB một tệp của GitHub — chương trình
**tự tải chúng** ở lần chạy đầu, và `DongGoi.bat` cũng tự tải trước khi đóng gói
nếu thấy thiếu.

### Đóng gói

```bat
set GIONGDOC_TU_DONG=1 && DongGoi.bat
```

Ra `GiongViet\GiongViet.exe` dạng một thư mục. Bản đóng gói phải có đủ ba tệp
mấu chốt — thiếu cái nào hỏng theo một kiểu riêng, nên `DongGoi.bat` kiểm từng cái:

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

giaodien/              THƯ VIỆN DÙNG CHUNG — cả 15 tệp đều đang được gọi
  cau_noi.py             lớp Api, cầu JS ↔ Python
  bo_doc.py              vòng đọc playlist        │ có SỐ PHIÊN
  nghe_thu.py            phát thử một giọng       │ có SỐ PHIÊN
  du_lieu.py · ho_so.py · soat.py · tu_dien.py · cai_dat.py · mo_hinh.py
  ds_giong.py · thu_vien_giong.py · he_thong.py · nhat_ky.py · xuat_file.py

giaodien_moi/          TẦNG ỨNG DỤNG
  cau_noi_moi.py         ApiMoi — kế thừa Api, thêm cửa cho giao diện
  xuat_moi.py            bộ xuất WAV/MP3          │ có SỐ PHIÊN
  am_thanh_loc.py        dựng chuỗi lọc cho ba thanh chỉnh
  ho_so_v2.py · soat_moi.py · luu_tep.py · so_dien_thoai.py
  kiem_*.py              14 bộ kiểm

ui-moi/                GIAO DIỆN — index.html · app.css · giao-dien.js
  trang-thai.js          mô hình trạng thái thuần, không DOM
  cau-noi.js             cầu JS ↔ Python
  man-soat.js · man-giong.js · man-tudien.js · man-caidat.js · hop-thoai.js
  kiem-*.mjs             4 bộ kiểm giao diện

design_handoff_giongdoc/   đặc tả và bản mẫu thiết kế (bản gốc, không sửa)
plans/                     nhật ký các phiên làm việc
_luutru/                   bản cũ đã ngừng dùng, giữ để đối chiếu
```

---

## Bộ kiểm

**757 phép kiểm / 18 bộ.** Chạy hoàn toàn trên `%TEMP%`, không đụng dữ liệu hay
nhật ký thật.

```bat
py giaodien_moi\kiem_xuat_moi.py       rem  và 13 bộ .py khác
node ui-moi\kiem-giao-dien.mjs         rem  và 3 bộ .mjs khác
py KiemBanExe.py                       rem  kiểm chính bản .exe
```

Ba nguyên tắc rút từ những lần vấp thật, nay chính bộ kiểm canh:

- **Chạy được từ source KHÔNG chứng minh `.exe` chạy được.** Thiếu
  `--collect-data` là danh sách giọng rỗng; thiếu `--add-data` là trang trắng.
  Chỉ lộ ra ở bản đóng gói.
- **Mọi nguồn phát tiếng phải có SỐ PHIÊN.** Cờ dừng không đủ: tổng hợp một câu
  có thể mất tới 40 giây, luồng cũ tỉnh dậy sau đó vẫn phát chồng lên.
- **Không bày nút giả.** Nút nào chưa nối được vào chức năng thật thì gỡ khỏi
  giao diện, không để đó cho người dùng bấm vào rồi tưởng máy hỏng.

---

## Dữ liệu người dùng

Không nằm trong kho và không bao giờ được commit: `congduc.txt`, `cauhinh.ini`,
`noidung.ini`, `tudien.ini`, `hoso*.json`, `giaodien.json`, `giong_rieng/`,
`*-loi.log`.

## Giấy phép

Chưa chọn. Kho đang để riêng tư.
