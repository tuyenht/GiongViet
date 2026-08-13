---
description: Chốt theo khuyến nghị hội đồng + thực thi, tự chứng minh xanh
argument-hint: [tùy chọn — để trống nếu tiếp nối hội đồng ở trên]
---
Chốt theo khuyến nghị hội đồng ở trên. Thực thi đạt CORE KPI dự án này: ổn định · dễ dùng cho người
lớn tuổi không rành máy tính · KHÔNG nút giả · bản `.exe` phải chạy được · một nguồn phát tiếng tại
một thời điểm · thoát sạch tiến trình · không đụng dữ liệu người dùng · chạm tối thiểu.

**Guardrail bắt buộc tự chạy — không đợi tôi nhắc:**

1. Cú pháp: `py -c "import glob,py_compile;[py_compile.compile(f,doraise=True) for f in ['GiongDoc.py']+glob.glob('giaodien/*.py')]"`
2. Đỏ → tự sửa và chạy lại đến khi xanh. DÁN output cuối cùng làm bằng chứng.
3. Đụng logic đọc/phát tiếng → chạy thử thật và ĐẾM tiến trình `ffplay`
   (`Get-Process ffplay`). Tối đa 1. Đo liên tục để bắt đỉnh, đừng lấy mẫu một lần.
4. Đụng dữ liệu/định dạng → chạy thử trên **bản sao** trong scratchpad, KHÔNG dùng file thật của tôi.

**Nếu đụng bất cứ thứ gì liên quan đóng gói** (`DongGoi.bat`, thư viện mới, file dữ liệu mới,
`__file__`, `sys.frozen`) thì CHƯA ĐƯỢC BÁO XONG cho tới khi:
- Build lại: `set GIONGDOC_TU_DONG=1 && DongGoi.bat` (~10 phút).
  ⚠ THIẾU biến đó là script dừng ở `pause` chờ bấm phím → treo vô hạn.
- Kiểm đủ 3 tệp mấu chốt trong bundle:
  `_internal\ui\index.html` · `_internal\sea_g2p\sea_g2p.bin` · `_internal\vieneu\assets\voices_v3_turbo.json`
- Bản `.exe` chạy thật và ĐỌC ĐƯỢC. Còn lỗi → đọc `GiongDoc-loi.log` (có traceback đầy đủ),
  KHÔNG đoán mò từng thư viện.

**Không tự chiếm màn hình của tôi.** Cần bấm thử giao diện → đưa tôi đường dẫn đầy đủ + nói rõ cần
bấm gì và cần nhìn cái gì, rồi chờ tôi báo lại. KHÔNG chụp toàn màn hình.

Báo cáo cuối phải nói rõ, không nhập nhèm:
- Cái gì đã chạy thật trên bản `.exe`
- Cái gì mới chạy từ source
- Cái gì chưa kiểm chứng được và vì sao

$ARGUMENTS
