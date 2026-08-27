# Prompt chạy trong Claude Code — bản đầy đủ, tường bước

Copy **toàn bộ** phần dưới đường ngăn cách và dán vào Claude Code ở thư mục dự án. Không cần copy file gì vào dự án trước — Claude Code đọc bản thiết kế mới nhất qua MCP.

---

Dùng claude_design MCP (`https://api.anthropic.com/v1/design/mcp`, đăng nhập qua `/design-login`) để đọc dự án thiết kế này:

`https://claude.ai/design/p/5c70b20f-0f8b-4da8-ad19-800b0fb6ae19`

Cả dự án đọc được. Các file cần dùng, ở gốc dự án thiết kế:

- `GiongDoc - Màn hình chính v2 (nghe theo dòng).dc.html` — màn chính, là khung của mọi màn khác
- `GiongDoc - Soát văn bản.dc.html`
- `GiongDoc - Thư viện giọng.dc.html`
- `GiongDoc - Xuất file âm thanh.dc.html`
- `GiongDoc - Văn bản ghép.dc.html`
- `GiongDoc - Từ điển phát âm.dc.html`
- `GiongDoc - Cài đặt.dc.html`
- `design_handoff_giongdoc/README.md` — đặc tả chi tiết vòng trước
- `design_handoff_giongdoc/PROMPT.md`, `design_handoff_giongdoc/PROMPT-CAPNHAT.md` — hai vòng bàn giao trước, vẫn còn hiệu lực

Chỗ nào README khác với file `.dc.html` thì **file `.dc.html` là bản đúng**.

Việc lần này **không phải viết thêm tính năng mới**, mà là **đối chiếu chương trình đang chạy với bản thiết kế, báo cáo chênh lệch, rồi mới sửa**. Làm đúng 4 bước dưới đây, không nhảy bước.

## Bước 1 — Đọc và bấm thử bản mẫu trước khi sửa bất cứ dòng nào

Mở lần lượt 7 file `.dc.html` ở trên bằng trình duyệt và **bấm thử thật**, không đọc code rồi đoán.

Mỗi file có dải nút nhỏ phía trên khung cửa sổ (Sáng/Tối, *Tình huống*, *Mở từ*…). Đó là công tắc để xem các trạng thái — bấm hết từng cái. **Mỗi trạng thái là một yêu cầu xử lý thật**, không phải hình trang trí.

Ghi lại đường dẫn tương ứng trong code của từng màn để bước 2 chỉ được chỗ.

## Bước 2 — Viết `DOI-CHIEU.md`, chưa sửa code

Tạo `DOI-CHIEU.md` ở gốc dự án code. Một bảng, mỗi dòng một điểm lệch:

| Màn / khu vực | Thiết kế yêu cầu | Bản đang chạy | Loại | Mức | Khuyến nghị | Trạng thái |
|---|---|---|---|---|---|---|

- **Loại**: `thiếu` · `khác` · `lỗi` · `code làm tốt hơn thiết kế`
- **Mức**: `chặn` (người dùng tắc, không làm tiếp được) · `nặng` (làm được nhưng sai hoặc khó hiểu) · `nhẹ` (lệch hình thức: khoảng cách, cỡ chữ, màu, câu chữ)
- **Khuyến nghị**: nên theo bên nào, vì sao, kèm chi phí sửa (nhỏ / vừa / lớn)
- **Trạng thái**: để trống ở bước này

Mỗi dòng phải chỉ được: **file thiết kế + trạng thái nào** (ví dụ `Thư viện giọng · Tình huống: Hai người nói`) và **chỗ nào trong code** (đường dẫn tệp, tên hàm hoặc component). Không viết chung chung kiểu "giao diện chưa giống".

Cuối báo cáo, thêm ba mục:

1. **Cần tôi quyết** — chỗ thiết kế không nói rõ. Mỗi chỗ nêu 2–3 phương án và phương án bạn nghiêng về. Đừng tự chọn rồi làm luôn nếu nó đổi luồng người dùng.
2. **Code làm tốt hơn thiết kế** — phần bạn đã làm đầy đủ hơn bản mẫu (thêm trạng thái lỗi, thêm phím tắt, xử lý biên tốt hơn, dữ liệu thật thay dữ liệu mẫu). **Giữ lại**, mô tả rõ để tôi cập nhật thiết kế theo bạn. Đừng âm thầm bỏ đi, cũng đừng âm thầm giữ mà không báo.
3. **Mục menu còn xám** — danh sách chức năng chưa nối, để tôi biết còn nợ gì.

Xong `DOI-CHIEU.md` thì **dừng lại và báo tôi**. Không sửa code ở bước này.

## Bước 3 — Sửa theo thứ tự, chỉ sau khi tôi duyệt

Thứ tự mức: **chặn → nặng → nhẹ**. Trong mỗi mức, thứ tự màn: **Màn hình chính → Soát văn bản → Thư viện giọng → Xuất file âm thanh → Văn bản ghép → Từ điển phát âm → Cài đặt**. Màn chính là khung của mọi màn khác, sửa nó trước thì các màn sau đỡ phải sửa lại.

Sau mỗi nhóm: chạy thử được, mở lại đúng file thiết kế và bấm lại đúng trạng thái đó để so, cập nhật cột **Trạng thái** trong `DOI-CHIEU.md` (`xong` / `bỏ qua, lý do` / `chờ tôi quyết`), rồi báo tôi. Đừng chạy liền một mạch tới hết.

## Bước 4 — Những chỗ vừa đổi trong thiết kế, đối chiếu kỹ

### a. Menu trên cùng (màn chính và màn Soát văn bản)

Sáu menu, đúng thứ tự, đúng phím tắt:

- **Tệp**: Mở tệp… `Ctrl+O` · Mở từ Google Docs… · Dán văn bản `Ctrl+V` · Lưu `Ctrl+S` · Xuất file âm thanh `Ctrl+E` · Đóng tệp `Ctrl+W` — Ghép danh sách từ Google Sheet… — Cài đặt… · Thoát `Alt+F4`
- **Chỉnh sửa**: Hoàn tác `Ctrl+Z` · Làm lại `Ctrl+Y` — Cắt `Ctrl+X` · Sao chép `Ctrl+C` · **Dán `Ctrl+V`** · **Chọn tất cả `Ctrl+A`** — Tìm và thay thế `Ctrl+H` · Soát văn bản `Ctrl+K`
- **Chèn**: Thẻ cảm xúc `Alt+1…3` · Khoảng lặng 1 giây `Alt+S` · Ngắt đoạn `Enter` — **Thêm cách đọc cho từ đang chọn…** (mở Từ điển phát âm)
- **Giọng**: Đổi giọng đọc `Ctrl+G` · Nghe mẫu giọng `Ctrl+M` — Thư viện giọng · Nhân bản giọng từ file… · **Thu âm để tạo giọng mới…** — Từ điển phát âm
- **Xem**: Thu gọn danh sách hồ sơ `Ctrl+B` · Cỡ chữ lớn hơn `Ctrl+=` · Cỡ chữ nhỏ hơn `Ctrl+-` — **Toàn màn hình `F11`** · Giao diện tối
- **Trợ giúp**: Hướng dẫn nhanh `F1` · Danh sách phím tắt `Ctrl+/` · Giới thiệu Giọng Việt — **Kiểm tra bản cập nhật** · **Gửi phản hồi cho nhà phát triển**

Hai mục *Nhân bản giọng từ file…* và *Thu âm để tạo giọng mới…* phải **mở thẳng hộp nhân bản** ở đúng bước tương ứng (một cái vào bước chọn tệp, một cái vào bước thu âm), không chỉ mở Thư viện giọng rồi để người dùng tự tìm.

Trên màn **Soát văn bản**, menu *Xem* có thêm *Chỗ cần chú ý* / *Văn bản sau chuẩn hoá* để đổi bảng kết quả, và *Chỉnh sửa → Soát lại tệp này `Ctrl+K`*.

Bảng menu mở **thẳng cạnh trái của nhãn** — neo vào nhãn, đừng dùng bảng toạ độ cứng. Bấm ra ngoài thì đóng; bấm lại nhãn đang mở thì đóng.

Trong bản mẫu, mục chưa nối chức năng để **chữ xám** — đó là quy ước của bản mẫu, không phải yêu cầu cho sản phẩm. Trong bản chạy thật: **chức năng nào code đã có thì nối vào menu**, chỉ để xám những mục thật sự chưa làm. Không ẩn mục, không để bấm mà không có gì xảy ra.

### b. Nhân bản giọng — luồng đầy đủ, không có ngõ cụt

Hộp nhân bản gồm: **Nguồn → Kiểm tra → Xác nhận → Tạo giọng → Xong**. Đối chiếu từng trạng thái:

1. **Nguồn**: hai lựa chọn — *Tải tệp âm thanh lên* và *Thu âm trực tiếp*. Cả hai đều phải bấm được. Kèm khối điều kiện tệp (định dạng, độ dài từ 30 giây, một người nói, quyền dùng giọng).
2. **Thu âm trực tiếp**: đoạn mẫu để đọc, đồng hồ chạy, cột mức tín hiệu chạy theo tiếng, nút *Bắt đầu thu / Dừng thu / Thu lại*, dòng nhắc đổi theo thời lượng, và **chỉ cho sang bước sau khi bản thu đủ 30 giây** (nút mờ kèm tooltip nói lý do). Ghi rõ micro đang dùng và bản thu chỉ nằm trên máy.
3. **Kiểm tra**: tên tệp hoặc bản thu, sóng âm, vùng chọn, danh sách kết luận tự động (một người nói / độ ồn / tiếng vọng). Ba trường hợp phải khác nhau: **đạt** (cảnh báo nhẹ vẫn đi tiếp được), **bản ghi quá ngắn** và **có hai người nói** — hai cái sau chặn, hiện khối lỗi kèm nút sửa, nút tiếp bị mờ.
4. **Xác nhận**: ô tên giọng, **tích cam kết quyền dùng giọng** (chưa tích thì không tạo được), câu nói rõ giọng chỉ nằm trên máy.
5. **Tạo giọng**: vòng xoay, bước hiện tại, thời gian còn lại, và **đóng hộp thì việc chạy tiếp ở nền** — có tiến độ ở thanh trạng thái, xong thì báo. Đây là chỗ dễ làm sai nhất: đừng huỷ việc khi người dùng đóng hộp.
6. **Xong**: tên giọng, thông tin mẫu, sóng âm, nghe thử câu mẫu, nút dùng ngay cho hồ sơ đang chọn.
7. **Tạo giọng lỗi**: nói rõ dừng ở bước nào, đoạn nào có vấn đề, *không mất lượt nhân bản*, có *Tạo lại* và *Quay lại chọn đoạn khác*. Không hiện mã lỗi kỹ thuật.
8. **Hết lượt nhân bản**: bấm *Nhân bản giọng mới* ra hộp riêng — số lượt của gói, danh sách giọng đang có kèm nút *Xoá* từng giọng, hai lựa chọn *Để sau* / *Xem gói cao hơn*.

Ngoài hộp nhân bản, thẻ giọng phải xử lý đủ: **Nghe thử có trạng thái đang phát** (đổi nhãn, có nút dừng) · **Đổi tên giọng** (hộp nhập thật, chỉ đổi tên hiển thị) · **Thêm mẫu để giọng giống hơn** (chạy lại luồng 3 bước, không hỏi lại tên) · **Xuất bản sao ra tệp** · **Xoá giọng của tôi** và **Gỡ giọng có sẵn khỏi máy** — hai cái sau **phải có hộp xác nhận**, nói rõ hậu quả và hồ sơ đang dùng sẽ chuyển về giọng nào. Cột trái hiện hạn mức đã nhân bản và dung lượng còn lại.

Sau mỗi việc, thông báo góc phải phải nói đúng việc vừa xong (đặt mặc định, đổi tên, xoá, gỡ, tạo xong, cập nhật xong) — không dùng chung một câu cho mọi việc.

### c. Mượt tay khi dùng

- Mở/đóng menu, mở hộp, đổi tab: không nháy, không nhảy bố cục, không phải đợi.
- Việc dài (tạo giọng, tải mô hình, xuất tệp) **chạy ở nền**, có tiến độ, hộp thoại không khoá cả cửa sổ.
- Nút không dùng được thì làm mờ **kèm tooltip nói lý do**.
- Trạng thái đang chạy (thu âm, đang phát, đang tải, đang tạo) phải có dấu hiệu động và có cách dừng.
- Mọi danh sách đều có trạng thái rỗng bằng câu tiếng Việt tự nhiên, kèm chỉ dẫn việc cần làm.

## Ràng buộc

- **Sửa tối thiểu, không refactor.** Đây là việc chỉnh cho khớp thiết kế, không phải dịp dọn kiến trúc. Không đổi cấu trúc dữ liệu, không đổi thư viện, không đổi cách tổ chức thư mục, không đổi phần tích hợp máy đọc hoặc giấy phép. Nếu bạn cho rằng phải đổi mới làm được, ghi vào mục *Cần tôi quyết* thay vì tự làm.
- Các vòng bàn giao trước vẫn còn hiệu lực: tên sản phẩm *Giọng Việt*, vùng chữ soạn thảo được như Notepad, nút ▶ nghe riêng đoạn ở lề phải, thanh cuộn thật tự ẩn, gỡ thẻ cảm xúc bằng cách bấm vào thẻ. Bản chạy còn lệch những chỗ đó thì đưa luôn vào báo cáo lần này.
- Không đổi tên biến CSS trong thiết kế; lấy màu, khoảng cách, bo góc, cỡ chữ từ đúng các biến đó (bộ sáng và bộ tối).
- Tiếng Việt có dấu cho mọi chữ hiển thị; đường dẫn trên đĩa dùng `GiongViet` không dấu.
- Không thêm biểu tượng cảm xúc, không thêm màu gradient, không đổi kiểu chữ.
- Dữ liệu mẫu trong bản thiết kế chỉ để minh hoạ trạng thái — không copy vào sản phẩm, nhưng **giữ đúng các trạng thái** mà dữ liệu đó minh hoạ.

Bắt đầu từ bước 1 và bước 2. Không sửa code cho tới khi tôi xem xong `DOI-CHIEU.md`.
