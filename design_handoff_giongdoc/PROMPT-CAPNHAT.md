# Prompt cập nhật (dán vào Claude Code)

Dùng khi Claude Code **đã** làm việc với bộ handoff này trước đó. Copy toàn bộ khối dưới đây.
Nhớ copy lại thư mục `design_handoff_giongdoc/` mới nhất vào gốc dự án trước khi dán (README.md và 6 file trong `designs/` đều đã cập nhật).

---

Bản thiết kế của dự án vừa được cập nhật. Đọc lại `design_handoff_giongdoc/README.md` (bản mới, đã thay đổi) và mở lại `design_handoff_giongdoc/designs/GiongDoc - Màn hình chính v2 (nghe theo dòng).dc.html` trong trình duyệt để bấm thử trước khi sửa code.

Đây là bản cập nhật, không phải bàn giao mới. Chỉ sửa những phần bên dưới, giữ nguyên phần còn lại đã làm đúng.

## 1. Tên ứng dụng: GiongDoc → Giọng Việt

- Mọi chỗ hiển thị cho người dùng dùng đúng cụm **Giọng Việt**: thanh tiêu đề mọi màn (`{tên tệp} — Giọng Việt`), menu Trợ giúp (*Giới thiệu Giọng Việt*), nhóm cài đặt *Về Giọng Việt*, đáy cột trái màn Cài đặt (`Giọng Việt 1.4.2`), thông báo sau khi xuất tệp.
- Đường dẫn và tên thư mục trên đĩa dùng dạng **không dấu `GiongViet`**: `Documents\GiongViet\Xuất`, `D:\GiongViet\Models`. Không dùng tên có dấu cho đường dẫn.
- Tên file thiết kế trong thư mục handoff vẫn còn tiền tố `GiongDoc` — đó chỉ là tên file, không phải tên sản phẩm. Nếu code có hằng số, namespace, tên window title kiểu `GiongDoc`, đổi sang `GiongViet` (code) / `Giọng Việt` (hiển thị).

## 2. Vùng đọc trở thành vùng soạn thảo như Notepad

Đây là thay đổi lớn nhất. Trước đây vùng đọc chỉ để đọc và chọn đoạn; giờ nó là nơi sửa văn bản trực tiếp.

- Bấm vào chữ → con trỏ nhập thật ở đúng vị trí bấm. Gõ, xoá, chọn khối, dán đều được. Dán chỉ nhận chữ trần, không nhận định dạng.
- `Enter` tách đoạn tại con trỏ: phần sau con trỏ thành đoạn mới, con trỏ nhảy vào đầu đoạn mới. Enter ở cuối đoạn tạo một đoạn rỗng mới và **giữ nó lại** để người dùng gõ.
- `Backspace` ở đầu đoạn → nối đoạn đó vào cuối đoạn trên, con trỏ đặt đúng chỗ nối. `Delete` ở cuối đoạn → kéo đoạn dưới lên.
- **Không bao giờ có đoạn rỗng.** Khi nạp tệp, mọi dòng trống bị bỏ. Đoạn bị xoá hết chữ sẽ tự mất khi con trỏ rời khỏi đoạn đó, số đoạn đánh lại liền mạch. Ngoại lệ duy nhất: đoạn đang giữ con trỏ (để Enter tạo đoạn mới còn dùng được).
- Chọn cả đoạn rồi `Delete`, hoặc chọn khối qua nhiều đoạn rồi xoá, phải cho kết quả đúng: chỉ những đoạn hết chữ bị xoá, các đoạn khác không đổi một ký tự.
- Số từ, số đoạn, ước tính thời lượng cập nhật ngay theo từng thao tác sửa.
- **Lưu ngay khi gõ**, không đợi rời khỏi ô. Đổi hồ sơ, đổi tab tệp, bấm ra ngoài vùng chữ đều không được làm mất chữ vừa gõ.
- Sửa đoạn đã nghe hoặc đã xuất → áp tình huống *Bạn vừa sửa văn bản, bản đã nghe là bản cũ*.

Ghi chú kỹ thuật (chúng tôi đã gặp và tự sửa trong bản mẫu, bạn nên tránh lặp lại): đừng để lớp render quản lý các nút chữ bên trong vùng soạn thảo, và đừng ghép chữ với đoạn theo chỉ số mảng — hãy gắn số đoạn lên từng ô rồi đọc lại toàn bộ theo số đó. Ghép theo vị trí sẽ lệch ngay sau lần xoá đầu tiên.

## 3. Nút nghe riêng đoạn chuyển sang lề phải

- Bỏ hành vi *bấm số đoạn để nghe*. Máng số bên trái giờ chỉ để đánh dấu vị trí, rộng 30px, cách chữ 12px.
- Mỗi đoạn có **nút ▶ 26×26px, bo 4px** ở lề phải, cách thanh cuộn 10px. Tooltip *Nghe riêng đoạn này, nghe hết đoạn thì dừng*.
- Nút chỉ hiện khi **rê chuột vào đúng đoạn đó**, hoặc khi đoạn đang đọc / đang tạo âm thanh (khi đó viền và chữ `acc`, nền `acc-soft`). Đổi độ mờ 0.12s. Không hiện đồng loạt mọi nút.
- Bỏ tam giác nhỏ ở máng số của đoạn đang đọc. Vòng xoay khi đang tạo âm thanh thì giữ.

## 4. Định dạng hàng đoạn

- Mỗi đoạn là một hàng **bo 6px, đệm 7×8px**; vùng đọc đệm trong 8px bên trái, 10px bên phải.
- Nền khi chọn (`sel`) hoặc đang đọc (`hl`) là một khối bo góc phủ trọn máng số, chữ và nút ▶ — không tràn sát viền thẻ.
- Đoạn đang chọn có **vạch dọc 3px màu `acc`** ở lề trái, nằm trong khối bo góc, cùng nền `sel`. Đoạn đang đọc cũng vạch 3px `acc` nhưng nền `hl`, chữ đậm 600, số màu `acc`.
- Chữ tràn theo chiều rộng còn lại của hàng (bỏ giới hạn 700px và đệm phải 24px của bản cũ).
- Gợi ý ở đầu vùng đọc đổi thành *Bấm vào chữ để sửa như Notepad · nút ▶ bên phải để nghe riêng đoạn*.

## 5. Thanh cuộn thật, tự ẩn

- Vùng đọc phải **cuộn được thật** (chuột, bánh xe, bàn phím). Bản cũ vẽ thanh cuộn giả nên không cuộn được — bỏ hẳn.
- Thanh cuộn mảnh, màu `rail`, **chỉ hiện khi chuột ở trong vùng đọc**; chuột ra khỏi vùng thì ẩn đi (cùng lúc ẩn các nút ▶).

## 6. Gỡ thẻ cảm xúc

- Thẻ cảm xúc nằm **ngoài** vùng chữ (không gõ vào được), đặt trước khối chữ, cách chữ 9px.
- **Bấm vào thẻ để gỡ**: rê chuột thì viền và chữ chuyển sang `err`, tooltip *Bấm để gỡ thẻ cảm xúc*.
- `Backspace` khi con trỏ ở đầu chữ của đoạn có thẻ thì **gỡ thẻ trước, đoạn giữ nguyên**; nhấn tiếp lần nữa mới nối đoạn lên trên.
- Menu *Thẻ cảm xúc → Gỡ thẻ khỏi đoạn này* giữ nguyên.

## 7. Dữ liệu mẫu

- Vì bỏ dòng trống, tài liệu mẫu `thongbao-quoc-khanh.txt` còn **15 đoạn** (bản cũ 16), dòng thống kê là `215 từ · 15 đoạn · khoảng 1 phút 28 giây`. Tài liệu `danh-sach-ung-ho.txt` cũng bỏ dòng trống tương tự.
- Các mục *Cần chú ý* tham chiếu số đoạn — kiểm lại cho khớp với mảng đoạn sau khi bỏ dòng trống. Bảng dữ liệu mẫu đầy đủ nằm trong README.

## Cách làm

1. Đối chiếu 6 mục trên với code hiện tại, báo tôi mục nào đã đúng / sai / chưa có, kèm file và vị trí. **Dừng chờ tôi duyệt** trước khi sửa.
2. Sửa theo thứ tự: đổi tên (mục 1) → lớp soạn thảo (mục 2) → nút ▶ và định dạng hàng (mục 3, 4) → thanh cuộn (mục 5) → thẻ cảm xúc (mục 6).
3. Mọi con số không ghi ở đây thì lấy trực tiếp từ README hoặc từ file bản mẫu, đừng tự đoán.

## Nghiệm thu

- [ ] Không còn chữ `GiongDoc` nào hiển thị cho người dùng; đường dẫn dùng `GiongViet`
- [ ] Bấm vào chữ gõ được ngay; `Enter` / `Backspace` / `Delete` tách và nối đoạn đúng
- [ ] Chọn cả đoạn rồi Delete: mất đúng đoạn đó, các đoạn khác không đổi một ký tự
- [ ] Không có đoạn rỗng nào tồn tại sau khi rời khỏi đoạn
- [ ] Gõ chữ rồi đổi hồ sơ / đổi tab rồi quay lại: chữ vẫn còn
- [ ] Con trỏ không nhảy về đầu đoạn khi đang gõ giữa câu
- [ ] Nút ▶ chỉ hiện ở đoạn đang trỏ chuột, cách thanh cuộn một khoảng
- [ ] Vùng đọc cuộn thật; thanh cuộn chỉ hiện khi chuột ở trong vùng
- [ ] Bấm vào thẻ cảm xúc gỡ được thẻ mà đoạn không bị nối lên trên
- [ ] Đoạn đang chọn có vạch xanh và nền bo góc, không tràn sát viền thẻ
- [ ] Tài liệu mẫu đầu tiên hiển thị `215 từ · 15 đoạn`, không còn dòng trống đánh số
