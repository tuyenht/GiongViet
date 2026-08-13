---
description: Senior reviewer soi thay đổi theo các họ lỗi dự án này đã vấp thật
argument-hint: [file / thay đổi / đề xuất cần review]
---
Với vai trò senior reviewer, soi thay đổi/đề xuất dưới đây. Dự án này đã vấp thật những họ lỗi sau —
tìm cụ thể, đừng review chung chung:

**Đóng gói (mắt xích cuối, hỏng là người dùng không chạy được)**
- Thư viện nạp file dữ liệu bằng `Path(__file__).parent / ...` → PyInstaller KHÔNG tự gói. Thiếu
  `--collect-data vieneu` → danh sách giọng RỖNG; thiếu `--collect-data sea_g2p` → `os error 2` đúng
  lúc bấm đọc (61 MB `sea_g2p.bin`).
- Import trong hàm / import động → cần `--hidden-import`.
- Kết luận "chạy được" mà chỉ chạy từ source → CHƯA CHỨNG MINH ĐƯỢC GÌ về bản `.exe`.
- `sys.frozen` đổi hành vi (đường dẫn, thông báo lỗi) — thông báo viết cho bản này có đúng với bản kia?

**Âm thanh — một nguồn phát tại một thời điểm**
- Mọi nơi gọi `Speaker.play` phải có SỐ PHIÊN (xem `bo_doc.py`, `nghe_thu.py`). Chỉ dùng cờ dừng là
  KHÔNG đủ: tổng hợp một câu mất tới 40 giây, `join(timeout)` bỏ cuộc rồi luồng cũ sống lại.
- Thêm nguồn phát thứ N mà không đi qua cơ chế chung → chồng tiếng (đã đo 4 tiến trình `ffplay`).

**Tiến trình & bộ nhớ**
- Đóng cửa sổ phải `os._exit(0)` — PyTorch/huggingface để lại luồng non-daemon (đã đo 66 luồng treo,
  ôm vài GB RAM).
- Thoát bằng Alt+F4 thì hàm `thoat()` KHÔNG chạy — `ffplay` vẫn đọc tiếp. Dọn dẹp phải đặt sau
  `webview.start()`.

**Giao diện**
- Sự kiện nổi lên `document` làm đóng ngay cái vừa mở (nút "Thư viện giọng", nút "…") → cần
  `stopPropagation`.
- Đóng dropdown khi cuộn mà quên loại trừ việc cuộn TRONG chính nó → không ai cuộn nổi.
- `position:absolute` trong thẻ có `overflow:auto` → bị cắt cụt giữa thân. Dùng `position:fixed` +
  tự tính toạ độ.
- Dựng lại toàn bộ DOM mỗi lần đổi trạng thái → giật với danh sách nghìn dòng. Đổi class thay vì
  `innerHTML`.
- Gọi sang Python theo từng nhịp chuột (kéo thanh trượt) → ghi đĩa liên tục + ngắt việc đang chạy.

**Chạy tự động / dòng lệnh**
- Script `.bat` có `pause` -> agent chạy sẽ treo vô hạn. Đặt `GIONGDOC_TU_DONG=1` trước khi gọi.
- PowerShell KHÔNG bung dấu sao cho lệnh ngoài: `python -m py_compile a.py giaodien/*.py` báo
  `[Errno 22]` và thoát mã 1 -> dễ tưởng nhầm code lỗi. Dùng `glob.glob` trong Python.
- `evaluate_js` gọi hàm `pywebview.api` trả về **Promise**; đọc đồng bộ chỉ nhận `{}`. Phải `.then()`
  gán vào biến global rồi mới đọc, không thì kết luận nhầm là cầu nối hỏng.
- Bản `--windowed` in tiếng Việt ra stdout bị `UnicodeEncodeError` (cp1252). Đừng dựa vào đường
  chẩn đoán dòng lệnh của bản đóng gói; ghi log ra tệp bằng UTF-8.

**Trung thực với người dùng**
- Bày nút/công tắc không nối vào chức năng thật.
- Vẽ dữ liệu bịa (sóng âm ngẫu nhiên, ước tính không có cơ sở đo).
- Thông báo lỗi viết cho lập trình viên (`pip install ...`) thay vì cho người lớn tuổi.
- Báo "đã xong" cho thứ mới chạy từ source, hoặc mới thử 2 đoạn rồi kết luận cho cả bài.

**Dữ liệu người dùng**
- Ghi đè `cauhinh.ini` / `congduc.txt` / `noidung.ini` / `tudien.ini` khi test. Test phải dùng bản sao.
- Xoá file mà không kiểm bản lưu có thật sự chứa thứ đó không.

**Giữ nguyên phần đang chạy được**
- Thay code đang chạy OK thay vì mở rộng bằng tham số · chạm quá rộng · thay đổi không có đường lùi.

Với mỗi quyết định có trade-off → hỏi "tại sao cách này thay vì phương án khác?".
Nêu rõ: vấn đề + mức độ nghiêm trọng + cách sửa. KHÔNG rubber-stamp.
Nếu tìm được 1 lỗi thuộc một họ ở trên → rà TOÀN BỘ các chỗ cùng họ, đừng vá lẻ.

$ARGUMENTS
