# Mốc 0 — kết quả phép thử 5 giả định

Đo ngày 2026-08-12. **Toàn bộ chạy trên bản đóng gói `ThuNghiem.exe`**, không phải từ source.
Máy: Windows 11 26200 · Python 3.14.2 · pywebview 6.2.1 · PyInstaller 6.19.0.

| # | Giả định | Kết quả | Bằng chứng |
|---|---|---|---|
| 1 | Gõ tiếng Việt Telex/VNI trong WebView2 | **ĐẠT** | Khớp từng ký tự 25/25: `Nguyễn Thị Tuyết ườ ẫ ỹ đ` |
| 2 | `text_select=True` mà vẫn kéo được cửa sổ | **ĐẠT** | Cửa sổ dịch 84px, không bôi đen chữ |
| 3 | Hoàn tác / Làm lại trong `contenteditable` | **HỎNG** | `Ctrl+Z` 9→9 ký tự · `Ctrl+Y` 29→29 ký tự — không đổi gì |
| 4 | Kéo thả tệp vào cửa sổ không khung | **ĐẠT có điều kiện** | Nhận được tệp và nội dung (230 ký tự), **không có đường dẫn thật** |
| 5 | `python-docx` đóng gói được | **ĐẠT** | 4 đoạn · giữ dấu · giữ đoạn rỗng · build 49 giây, 45 MB |

Kèm theo: `.exe` khởi động exit code 0, **thoát sạch 0 tiến trình sót**, ghi tệp tạm rồi
`os.replace()` sống sót qua mô phỏng mất điện giữa chừng.

---

## Bốn sự thật mới về môi trường, đo được chứ không suy

### M1. Bộ gõ tiếng Việt KHÔNG dùng sự kiện ghép chữ
`soGhep = 0` — Unikey không phát `compositionstart`/`compositionend`, nó bơm thẳng phím và
phím xoá vào ô. Hệ quả: **đừng dựa vào sự kiện ghép chữ để nhận biết người dùng đang gõ tiếng
Việt.** Bộ hoàn tác tự viết phải gom theo thời gian nghỉ tay, không gom theo ranh giới ghép chữ.

### M2. WebView2 không cho hoàn tác trong `contenteditable`
Đo được: bấm `Ctrl+Z` và `Ctrl+Y` thì độ dài chữ không đổi.
**Chưa tách bạch được** nguyên nhân là (a) WebView2 không nối lệnh sửa, hay (b) chữ do Unikey
bơm vào không vào được ngăn xếp hoàn tác. Không cần tách: cả hai đường đều dẫn tới cùng một
việc — **tự viết bộ hoàn tác**.

### M3. Kéo thả tệp không bao giờ cho biết tệp nằm ở đâu
`File.path` rỗng, và pywebview 6.2.1 **không có sự kiện thả tệp ở tầng native** — danh sách
sự kiện đầy đủ của `Window`: `closed · closing · loaded · before_load · before_show ·
initialized · shown · minimized · maximized · restored · resized · moved · request_sent ·
response_received`. Không có `file_drop`.

Hệ quả: tệp kéo thả vào và văn bản dán từ clipboard đều **không có thư mục gốc**. Lưu lần đầu
phải rơi vào `Tài liệu\GiongDoc\` (`luu_tep.thu_muc_mac_dinh()`). Chỉ tệp mở bằng hộp thoại
*Mở tệp…* mới biết đường dẫn thật.

### M4. `python-docx` không cần khai báo tay khi đóng gói
PyInstaller có sẵn `hook-docx.py` và `hook-lxml.py`. Không phải thêm `--hidden-import`.
`.docx` **giữ nguyên đoạn rỗng** → ánh xạ thẳng sang loại đoạn `blank` của đặc tả.

---

## Quyết định đã chốt

**Ctrl+S ghi thành tệp mới nếu tệp cũ đã có, đánh số tăng dần** *(chủ dự án, 2026-08-12)*.
Cài ở `giaodien_moi/luu_tep.py`, 15 phép kiểm xanh, chạy trên bản sao trong thư mục tạm.

- Kiểu đánh số theo File Explorer: `thongbao.txt` → `thongbao (1).txt` → `thongbao (2).txt`
- **Chỉ lần lưu ĐẦU mới đẻ tệp mới.** Các lần sau ghi đè chính bản vừa tạo, nếu không soạn
  một buổi là thư mục đầy `(1) (2) (3)…`
- Không đẻ `tên (1) (1)` — cắt phần số cũ trước khi đánh số lại
- Bản gốc của người dùng không bị chạm, kể cả `mtime`
- Ghi qua tệp tạm rồi `os.replace()`, lỗi thì dọn tệp tạm trước khi ném lên

---

## Việc phải làm thêm, phát sinh từ kết quả

| Việc | Vì sao | Ước |
|---|---|---|
| **Tự viết bộ hoàn tác / làm lại** | M2 | Ngăn xếp trạng thái vùng đọc, gom theo thời gian nghỉ tay (M1). Phải xong trước khi mở cho sửa văn bản |
| **Đường lưu cho tệp không rõ nguồn** | M3 | Tệp kéo thả và văn bản dán lưu vào `Tài liệu\GiongDoc\` |
| Sửa copy trạng thái rỗng | M3 | Câu *"kéo thả tệp .txt, .docx, .rtf vào cửa sổ này"* vẫn đúng — kéo thả chạy được. Chỉ `.rtf` là chưa đọc được |

---

## Chưa kiểm chứng được

- **`.rtf`** — chưa thử, chưa có thư viện. 0/5 tài liệu mẫu dùng định dạng này nên để sau.
- **Nguyên nhân chính xác của M2** — xem M2, không cần tách bạch để đi tiếp.
- **Hoàn tác khi văn bản dài** — phép thử chỉ gõ 29 ký tự. Ngăn xếp hoàn tác trên tài liệu
  vài nghìn từ ăn bao nhiêu RAM thì phải đo lúc dựng thật.
