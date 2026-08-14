# Prompt để dán vào Claude Code

Giải nén / copy thư mục `design_handoff_giongdoc/` vào gốc dự án, rồi copy toàn bộ khối dưới đây dán vào Claude Code.

Thư mục đã đủ để chạy độc lập: 6 file thiết kế, `support.js`, và thư mục `_ds/` chứa font. Mở file màn hình chính bằng trình duyệt là xem và bấm được ngay, không cần cài gì.

---

Tôi cần bạn áp **đầy đủ** bản thiết kế mới nhất của **Giọng Việt** vào dự án này. Giọng Việt là ứng dụng desktop Windows chuyển văn bản tiếng Việt thành giọng nói, chạy mô hình cục bộ trên máy người dùng. Người dùng là người Việt không rành kỹ thuật.

**Tên ứng dụng chính thức là “Giọng Việt”.** Mọi chỗ hiển thị cho người dùng dùng đúng cụm này (thanh tiêu đề, menu Trợ giúp, màn Cài đặt, thông báo). Tên thư mục và đường dẫn trên đĩa dùng dạng không dấu `GiongViet` (ví dụ `Documents\GiongViet\Xuất`). Tên file thiết kế trong thư mục bàn giao vẫn còn tiền tố `GiongDoc` — đó chỉ là tên file, không phải tên sản phẩm.

Dự án này **có thể đã được dựng một phần từ bản thiết kế cũ**. Thiết kế đã thay đổi khá nhiều từ lần bàn giao trước, và một số phần của bản cũ cũng chưa được làm xong. Vì vậy việc đầu tiên không phải là viết code, mà là đối chiếu.

Lưu ý: thư mục dự án có thể vẫn mang tên cũ (`DocCongDuc`) và code cũ có thể xoay quanh nội dung "danh sách công đức". Đó là **di sản của bản đầu**, không phải phạm vi sản phẩm. Giọng Việt đọc mọi loại văn bản tiếng Việt — thông báo, bài viết, sách nói, danh sách và biểu mẫu. Đừng lấy tên thư mục làm căn cứ cho nội dung hay cách đặt tên trong code mới.

## Tài liệu

- `design_handoff_giongdoc/README.md` — đặc tả đầy đủ: mô hình dữ liệu, token màu, cỡ chữ, từng màn hình, từng trạng thái, từng hành vi bấm. Đây là nguồn đúng duy nhất.
- `design_handoff_giongdoc/designs/` — 6 file HTML bản mẫu. **Mở `GiongDoc - Màn hình chính v2 (nghe theo dòng).dc.html` trong trình duyệt và bấm thử trước khi code.** Bản mẫu chạy thật: đổi hồ sơ, mở menu, chuyển tab tệp, chọn đoạn, chèn thẻ, tìm và thay thế, xuất file, đi lại giữa các màn hình.
- Bản mẫu là **thiết kế, không phải code sản phẩm**. Đừng copy HTML sang dự án. Dựng lại bằng framework và thư viện sẵn có của dự án.

## Bước 1 — Đối chiếu trước, code sau

Khảo sát dự án và lập cho tôi một bảng đối chiếu: mỗi mục trong đặc tả thì hiện trạng là *đã đúng* / *đã có nhưng sai* / *chưa có*. Nêu rõ file và vị trí. **Dừng lại chờ tôi duyệt** trước khi sửa bất cứ thứ gì.

Nếu dự án chưa có framework, đề xuất cho tôi chọn (WinUI 3 C#/XAML, hoặc Electron/Tauri + React) rồi mới đi tiếp.

## Bước 2 — Danh sách thay đổi so với bản bàn giao trước

Đây là những chỗ chắc chắn khác bản cũ. Kiểm từng dòng:

**Cấu trúc**
1. Còn **6 màn hình**, không phải 7. Màn *Xem trước chuẩn hoá* đã bị gộp vào màn *Soát văn bản* thành **tab thứ hai** trong cùng một màn. Nếu dự án đang có màn riêng, gỡ nó đi.
2. **Hồ sơ đọc là một chỗ làm việc riêng, không phải preset giọng.** Mỗi hồ sơ giữ giọng, tốc độ/cao độ/âm lượng, **và danh sách tệp đang mở của riêng nó**. Bấm đổi hồ sơ ở cột trái thì dải tab tệp, nội dung ở giữa, giọng, thanh điều chỉnh và danh sách *Cần chú ý* đều đổi theo. Xem bảng bốn hồ sơ mặc định trong README.
3. Hồ sơ thứ tư đổi tên: *Danh sách công đức* → **Danh sách, biểu mẫu**.
4. Mọi màn phụ có nút **‹ Màn hình chính** ở thanh tiêu đề.

**Thanh công cụ**
5. Bỏ hẳn nút **…** (thêm lệnh) — không có lệnh nào bị ẩn nên nó vô nghĩa.
6. Nút kính lúp giờ có nhãn chữ: **Tìm và thay thế**. Bấm mở thanh tìm kiếm nằm dưới dải tab.
7. Mục *Xem trước chuẩn hoá* đổi thành **Soát văn bản** (icon dấu tích), mở màn hình 2.
8. *Dán văn bản* là nút chìm như các nút khác, **không** phải nút viền. Toàn bộ nhóm bên trái cùng một mức nhấn mạnh.
9. **Nghe toàn bộ** và **Xuất file âm thanh** **ẩn hẳn** khi chưa có văn bản — không phải hiện mờ. Khi có văn bản nhưng máy đọc lỗi (mất kết nối / hết lượt / giọng đang tải) thì hiện nhưng khoá.
10. Phím tắt dán thống nhất là `Ctrl+V` ở mọi chỗ (bản cũ có chỗ ghi `Ctrl+Shift+V`).

**Vùng đọc**
11. **Bỏ cột thời lượng từng đoạn** và nhãn `THỜI LƯỢNG` ở đầu vùng đọc. Thời lượng tổng đã có ở dòng thống kê, thời gian chạy đã có ở thanh phát.
12. Đầu vùng đọc: bên trái là thống kê `215 từ · 16 đoạn · khoảng 1 phút 28 giây`, bên phải là gợi ý *Bấm vào chữ để sửa như Notepad · nút ▶ bên phải để nghe riêng đoạn*. **Không lặp lại tên tệp** ở đây (đã có ở thanh tiêu đề và ở tab).
13. Chữ tràn theo chiều rộng thẻ: lề trái 34px (máng số), lề phải 30px (chỗ nút ▶). Bản cũ giới hạn 640–700px và đệm 54px hai bên — bỏ.
14. **Nút ▶ ở lề phải từng đoạn = nghe riêng đoạn đó, hết đoạn thì dừng** (bản cũ bấm vào số đoạn — nay số đoạn chỉ để đánh dấu vị trí). Bấm *Nghe toàn bộ* mới nghe liền mạch. Thanh phát ghi *Đang nghe riêng đoạn 4* / *Nghe hết đoạn này sẽ dừng* ở chế độ nghe riêng, và *Đang đọc đoạn 4/16* / *Đang chuẩn bị đoạn tiếp theo…* ở chế độ liền mạch. Đồng hồ ở chế độ nghe riêng đếm theo độ dài đoạn đó, không phải cả bài.
15. Ở chế độ nghe riêng, các đoạn phía trên **không** bị làm mờ (chỉ chế độ liền mạch mới mờ các đoạn đã đọc xong).
16. **Vùng đọc sửa được tại chỗ như Notepad** — phần này mới hoàn toàn, xem mục *Sửa văn bản tại chỗ* trong README. Bấm vào chữ → con trỏ gõ thật ở đúng vị trí bấm (không phải con trỏ giả đầu đoạn như bản cũ), gõ/xoá/chọn khối/dán đều được; `Enter` tách đoạn, `Backspace` đầu đoạn nối lên trên, `Delete` cuối đoạn kéo đoạn dưới lên; **đoạn bỏ trống tự xoá**; số từ / số đoạn / thời lượng cập nhật theo. Rê chuột lên cả đoạn thì sáng lên và hiện nút ▶ của đoạn đó.

**Hiện / ẩn theo chuột**
27. Nút ▶ của mỗi đoạn **chỉ hiện khi chuột ở trên đoạn đó** (hoặc đoạn đang đọc / đang tạo âm thanh). Không hiện hàng loạt 16 nút cùng lúc.
28. Thanh cuộn của vùng đọc **chỉ hiện khi chuột ở trong vùng đọc**, chuột ra khỏi thì mờ dần về 0 (0.15s).
29. Bỏ tam giác nhỏ ở máng số của đoạn đang đọc — nền `hl` và vạch `acc` đã đủ để biết đoạn nào đang đọc. Vòng xoay khi đang tạo âm thanh thì giữ.

**Cột phải**
17. Thêm phần đầu thẻ: nhãn `HỒ SƠ ĐANG DÙNG` + tên hồ sơ. Giọng và thanh điều chỉnh bên dưới thuộc về hồ sơ đó — bỏ dòng chú thích cũ nằm trong mục thu gọn.
18. Bỏ khoảng trống lớn giữa thẻ giọng và thẻ *Cần chú ý* — hai thẻ xếp liền từ trên xuống.
19. *Cần chú ý*: mỗi dòng có chấm màu (đỏ cho lỗi bắt buộc, xám cho cảnh báo) và số đếm dạng nhãn bo góc. Bấm một dòng thì chọn đoạn tương ứng ở giữa. **Mỗi tài liệu có bộ Cần chú ý riêng** — xem README.
20. Chọn giọng và kéo thanh điều chỉnh là **ghi vào hồ sơ đang dùng**, không phải state toàn cục.

**Thanh trạng thái**
21. Bỏ `UTF-8 · CRLF` và mức phóng to `100%` — ngôn ngữ của trình soạn code, người dùng không cần.
22. Chấm và nhãn máy đọc đổi màu theo tình huống (bảng trong README).

**Luồng xuất**
23. Bấm *Xuất file âm thanh* **mở hộp thoại thiết lập** (tên tệp, định dạng, nơi lưu, tách tệp) rồi mới chạy. Bản cũ nhảy thẳng tới thông báo "đã xuất xong" — sai.
24. Sau khi bấm *Bắt đầu xuất*: hộp thoại đóng → thanh trạng thái chạy *Đang xuất… 34%* → khoảng 2 giây sau hiện thông báo góc dưới phải.

**Trạng thái lỗi và chờ — phần này hoàn toàn mới**
25. Dựng đủ **bảy tình huống** trong mục *Trạng thái lỗi và chờ* của README: mất kết nối máy chủ, hết lượt/hết dung lượng gói, giọng đang tải, văn bản quá dài phải cắt, âm thanh cũ sau khi sửa văn bản, đang tạo âm thanh, và bình thường. Mỗi tình huống có dải cảnh báo riêng, nút hành động riêng, và ảnh hưởng riêng tới nút Nghe/Xuất, thẻ giọng, thanh trạng thái.

**Các chỗ bấm phải chạy thật**
26. Menu trên cùng (6 menu, có phím tắt) · dải tab tệp (chuyển, đóng, thêm) · nút ba gạch thu gọn cột trái thành dải icon 44px · *Tạo hồ sơ mới* · menu thẻ cảm xúc chèn thẻ vào **đoạn đang chọn** và gỡ được · nút loa nghe mẫu giọng · các nút trong dải cảnh báo · các lựa chọn trong hộp thoại xuất. Danh sách đầy đủ nằm trong README, mục từng màn hình.

## Bước 3 — Thứ tự làm

1. Lớp token màu (đủ sáng + tối) + kiểu chữ + control cơ bản: nút chìm, nút viền, nút accent, ô chọn, slider, chip, dropdown, hộp thoại, dải cảnh báo, thông báo góc, công tắc bật/tắt.
2. Mô hình dữ liệu: hồ sơ, tài liệu, tab theo hồ sơ, trạng thái ứng dụng (bảng cuối README).
3. **Khung chung của các màn phụ** (mục cùng tên trong README): thanh tiêu đề có nút *‹ Màn hình chính*, cột trái 240px, thẻ nội dung bên phải. Dựng một lần rồi dùng lại cho màn 4, 5, 6.
4. Màn hình chính, đủ ba trạng thái vùng đọc và bảy tình huống. Làm xong màn này rồi mới sang màn khác.
5. Màn Soát văn bản (2 tab) → Xuất file âm thanh (3 giai đoạn) → Thư viện giọng → Từ điển phát âm → Cài đặt.
6. Nối các màn với nhau và kiểm nút *‹ Màn hình chính*.

**Trước khi dựng mỗi màn:** mở file bản mẫu của màn đó trong trình duyệt, bấm thử hết các chỗ bấm được, và đọc lại đúng mục của màn đó trong README. Mọi con số không ghi trong README thì lấy trực tiếp từ bản mẫu — đừng tự đoán.

Sau mỗi bước, dừng lại báo tôi biết đã xong gì.

## Bốn quyết định bắt buộc giữ nguyên, đừng "cải tiến"

- Đơn vị nội dung là **đoạn**, không phải dòng. Chữ tự xuống dòng, **không bao giờ cắt cụt bằng dấu ba chấm**. Vùng đọc là nơi sửa được, không phải nơi chỉ đọc.
- **Không có thanh tua theo thời gian.** Thanh dưới chỉ báo tiến trình, không kéo được. Người dùng tìm chỗ cần nghe bằng cách cuộn và bấm nút ▶ của đoạn.
- **Nghe toàn bộ** và **Xuất file âm thanh** là một cặp ở góc phải thanh công cụ, chỉ hiện khi có văn bản, và chỉ *Xuất* là nút accent.
- **Hồ sơ đọc là chỗ làm việc riêng**, không phải preset giọng.

## Yêu cầu chất lượng

Mức hi-fi: màu, cỡ chữ, khoảng cách, bán kính bo trong README là giá trị cuối cùng, dựng đúng từng pixel. Hệ thiết kế là WinUI 3 / Fluent (Windows 11), accent `#0067c0` (sáng) và `#4cc2ff` (tối). Cỡ chữ giao diện nhỏ nhất là 12px; chữ trong vùng đọc 18px, tiêu đề đoạn 20px.

Chưa cần nối vào mô hình TTS thật — mock dữ liệu theo đúng nội dung mẫu trong README (5 tài liệu, 4 hồ sơ, 5 giọng) để tôi xem được giao diện chạy.

Copy tiếng Việt trong README là bản cuối, **giữ nguyên từng chữ**, kể cả nội dung lỗi và các câu gợi ý.

## Nghiệm thu

Xong thì tự kiểm bằng danh sách này và báo lại từng dòng đạt hay chưa:

- [ ] Đổi hồ sơ ở cột trái → tab tệp, nội dung giữa, giọng, thanh điều chỉnh, Cần chú ý đều đổi
- [ ] Bấm nút ▶ của một đoạn → nghe riêng đoạn đó, thanh phát ghi đúng, hết đoạn thì dừng
- [ ] Nút ▶ và thanh cuộn chỉ hiện theo chuột đúng như mục 27–28
- [ ] Sửa chữ trực tiếp trong vùng đọc: gõ, `Enter` tách đoạn, `Backspace`/`Delete` nối đoạn, đoạn bỏ trống tự xoá, số từ và số đoạn cập nhật
- [ ] Bấm *Nghe toàn bộ* → đọc liền mạch, các đoạn đã đọc mờ dần
- [ ] Chưa có văn bản → cặp Nghe/Xuất ẩn, các công cụ phụ thuộc văn bản chuyển màu mờ
- [ ] Xuất → hộp thoại → thanh trạng thái chạy → thông báo góc
- [ ] Bảy tình huống lỗi/chờ hiện đúng dải cảnh báo và khoá đúng nút
- [ ] 6 menu trên cùng mở được, đủ phím tắt
- [ ] Tab tệp chuyển / đóng / thêm được, mỗi hồ sơ nhớ tab riêng
- [ ] Nút ba gạch thu gọn cột trái thành dải icon và mở lại được
- [ ] Chèn và gỡ thẻ cảm xúc vào đúng đoạn đang chọn
- [ ] Soát văn bản có 2 tab, tab 2 là bảng so sánh gốc / máy sẽ đọc thành
- [ ] Xuất file âm thanh có đủ ba giai đoạn trong cùng một hộp thoại
- [ ] Thư viện giọng: 8 thẻ giọng chia hai nhóm, có dải sóng âm, nhãn *Đang dùng*, ô nét đứt nhân bản giọng mới
- [ ] Từ điển phát âm: bảng 5 cột + khung *Thêm từ* mở ra đóng được
- [ ] Cài đặt: 6 nhóm, đủ bốn kiểu điều khiển toggle / select / path / meter
- [ ] Mọi màn phụ quay lại được màn chính
- [ ] Chế độ tối đúng token, không chỗ nào còn màu sáng lọt vào
