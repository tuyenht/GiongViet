---
description: Hội đồng đề xuất bước tiếp theo nên làm gì
argument-hint: [bối cảnh thêm — tùy chọn]
---
Hội đồng chuyên gia cao cấp phù hợp: đề xuất bước tiếp theo nên xử lý thế nào.

Quy trình: xác minh thực địa → tranh biện → 1 khuyến nghị duy nhất + priority matrix. Propose-first,
chờ tôi chốt rồi mới làm.

**Xác minh thực địa trước (dự án này KHÔNG dùng git):**
- `ls -la` thư mục gốc — xem mtime `GiongDoc.exe` so với các file nguồn vừa sửa
- `py -c "import glob,py_compile;[py_compile.compile(f,doraise=True) for f in ['GiongDoc.py']+glob.glob('giaodien/*.py')]"`
- Bundle còn đủ 3 tệp mấu chốt không: `_internal\ui\index.html` · `_internal\sea_g2p\sea_g2p.bin` ·
  `_internal\vieneu\assets\voices_v3_turbo.json`
- `GiongDoc-loi.log` có gì mới không
- Trích `file:line` cho mọi khẳng định về code

**Xếp thứ tự ưu tiên theo nguyên tắc: chứng minh giả định rủi ro nhất trước.** Dự án này đã học bài
học đó — dựng 2 màn hình xong mới phát hiện đường đóng gói chưa ai kiểm, may mà không vỡ.

Cân nhắc khi xếp ưu tiên:
- Việc nào mà nếu SAI sẽ làm vô hiệu công sức đã bỏ ra? → làm trước.
- Việc nào đang CHẶN mọi việc khác? → làm trước.
- Đường lỗi và lần chạy đầu quan trọng hơn tính năng thứ N — người dùng đích không rành máy tính,
  gặp lỗi là bỏ luôn.
- Thêm tính năng lên một nền chưa kiểm chứng = nợ chồng nợ.

Nêu rõ việc bị loại khỏi ưu tiên + lý do (1 câu mỗi việc).

$ARGUMENTS
