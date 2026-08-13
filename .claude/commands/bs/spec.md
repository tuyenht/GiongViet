---
description: Spec-first — nói lại hiểu + edge case + giả định trước khi code
argument-hint: [mô tả việc cần làm]
---
Trước khi viết BẤT KỲ code nào cho yêu cầu dưới đây:
1. Nói lại bằng lời của bạn vấn đề tôi đang hỏi.
2. Liệt kê edge case bạn nhìn thấy — đặc biệt: bản `.exe` (thiếu file dữ liệu) · chồng tiếng ·
   treo tiến trình · dữ liệu người dùng bị ghi đè · người dùng lớn tuổi hiểu nhầm.
3. Nêu các giả định ngầm bạn đang dùng — nhất là giả định "chạy được từ source nghĩa là chạy được
   khi đóng gói" (giả định này đã SAI nhiều lần ở dự án này).
4. Phân loại độ phức tạp:
   • ĐƠN GIẢN → làm thẳng, báo cáo sau.
   • PHỨC TẠP / HỘI ĐỒNG → tự lên plan (TodoWrite) rồi chạy hội đồng, propose-first, DỪNG chờ tôi.

Việc thuộc HỘI ĐỒNG ở dự án này:
- Đụng `DocCongDuc.py` (engine dùng chung: VieNeu-TTS, chuẩn hoá tiền/tên, giọng riêng).
- Đụng đường đóng gói (`DongGoi.bat`, cờ `--collect-data`, `--hidden-import`).
- Đụng dữ liệu người dùng (`congduc.txt`, `cauhinh.ini`, `noidung.ini`, `tudien.ini`, `giong_rieng/`).
- Thêm nguồn phát âm thanh thứ N (hiện có: `bo_doc`, `nghe_thu`, `xuat_file`).
- Lật một quyết định đã chốt.

Ràng buộc xuyên suốt (CORE KPI dự án này):
ổn định · dễ dùng cho người lớn tuổi không rành máy tính · KHÔNG bày nút giả (mọi nút phải nối vào
chức năng có thật) · bản `.exe` phải chạy được, không chỉ bản source · một nguồn phát tiếng tại một
thời điểm · đóng cửa sổ là tiến trình phải thoát sạch · không đụng dữ liệu người dùng ·
giữ nguyên phần đang chạy được, chạm tối thiểu.

KHÔNG viết code cho tới khi tôi xác nhận.

Yêu cầu: $ARGUMENTS
