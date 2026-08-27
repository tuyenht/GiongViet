# Prompt cập nhật (dán vào Claude Code)

Dùng khi Claude Code **đã** làm việc với bộ handoff này trước đó. Copy toàn bộ khối dưới đây.
Nhớ copy lại thư mục `design_handoff_giongdoc/` mới nhất vào gốc dự án trước khi dán (README.md và 7 file trong `designs/` đều đã cập nhật).

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

## 7b. Cột trái: bỏ dải tab tệp

Tệp đang mở không còn nằm trên dải tab dưới thanh công cụ — chúng là danh sách con của hồ sơ trong cột trái. Chỉ hồ sơ đang chọn mở danh sách tệp và mục *Thêm tệp*; các hồ sơ khác thu về một dòng có tên tệp đang xem, số tệp và chấm đỏ khi hồ sơ đó có tệp mắc lỗi. Chi tiết ở mục *Danh sách tệp* và *Cột trái — Hồ sơ đọc* trong README. Nếu code đang dựng dải tab, gỡ nó đi.

## 8. Mở tài liệu từ Google Docs (mới)

Người dùng thường soạn thảo trên Google Docs rồi mới đọc, nên không bắt họ tải file về nữa. Chi tiết đầy đủ ở mục *Mở tài liệu từ Google Docs* trong README.

- Hai đường vào: menu **Tệp → Mở từ Google Docs…** và nút thứ ba ở trạng thái rỗng (*Dán văn bản* · *Chọn tệp từ máy…* · *Mở từ Google Docs…*).
- Một hộp thoại 620px, **ba bước trong cùng một hộp**: đăng nhập → chọn tài liệu → đang tải. Đã đăng nhập thì vào thẳng bước chọn tài liệu.
- Bước chọn tài liệu có **hai thẻ**: *Từ Drive* (ô tìm theo tên + danh sách tài liệu, nháy đúp mở nhanh) và *Dán link* (không cần đăng nhập, kiểm link phải là `docs.google.com/document`). Nút **Mở tài liệu** khoá khi chưa chọn được gì.
- Nói rõ quyền: Giọng Việt **chỉ xin quyền đọc**, không sửa không xoá gì trên Drive. Giữ nguyên câu này.
- Tài liệu tải xong mở ra **như một tệp văn bản thường** (một tab tệp trong hồ sơ đang dùng), sửa được tại chỗ như mọi tệp khác.
- Tệp đến từ Google Docs có **chip ở đầu vùng đọc**: *Google Docs · lấy lúc 14:02*. Bấm chip = lấy bản mới (icon xoay, chữ đổi thành *Đang lấy bản mới từ Google Docs…*, xong thì ghi lại giờ).
- Không dùng thứ tiếng Anh nào trong copy ngoài chính tên *Google Docs* / *Drive*.

## 9. Màn hình mới: Văn bản ghép

Màn thứ bảy, file `designs/GiongDoc - Văn bản ghép.dc.html`, đặc tả ở mục *Màn hình 7* trong README. Đây là phần làm mới hoàn toàn, làm sau khi sáu mục trên đã xong.

Vấn đề nó giải quyết: có loại văn bản mà phần lời là của người dùng nhưng phần danh sách nằm trong một bảng tính và đổi liên tục. Thay vì dán lại và sửa lại mỗi lần, người dùng khai một lần: phần **tĩnh** họ viết, phần **động** lấy từ bảng tính qua một **mẫu câu**.

**Đây là một hệ mẫu, không phải một màn cho danh sách công đức.** Công đức chỉ là một trong sáu mẫu sẵn. Từ vựng ở giao diện phải là từ vựng chung — cột, dòng, nhóm, cách đọc — đừng đưa “số tiền”, “đợt”, “công đức” vào tên trường hay tên hằng số trong code.

Tám điều không được bỏ:

1. **Thư viện mẫu ghép.** Một hồ sơ giữ nhiều mẫu; ô chọn mẫu ở đầu cột trái đổi mẫu, đổi tên, xoá, và *Tạo mẫu ghép mới…* mở hộp thoại sáu mẫu sẵn (công đức · quyên góp, ủng hộ · chi trả, bảng lương · khen thưởng, kết quả · lịch trực, phân công · thông báo tìm người, tạm trú). Mỗi mẫu sẵn mang theo cột gợi ý, mẫu câu và văn bản đầu/cuối — bảng đầy đủ trong README.
2. **Thiết lập là của từng mẫu, không phải của màn hình.** Đổi mẫu thì nguồn, khớp cột, luật lọc, bốn khối nội dung đều đổi theo. Sửa mẫu A không được chạm vào mẫu B.
3. **Khớp cột có hai trục độc lập.** *Dùng làm* (Dùng trong câu · Nhóm theo cột này · Lọc theo ngày · Bỏ qua) và *Cách đọc* (8 kiểu, xem README). Cột nào cũng chèn được vào mẫu câu trừ cột *Bỏ qua*; chỉ *Nhóm* và *Lọc ngày* là duy nhất, trùng thì báo đỏ ngay tại hàng và nói rõ cột nào được dùng. Biến sinh từ tiêu đề cột bỏ dấu, không phải danh sách vai cứng.
4. **Cách đọc phải thấy được ở cột xem trước.** Cùng một ô, đổi cách đọc thì bốn dòng mẫu ở cột phải đổi theo ngay: số tiền đọc thành chữ, số điện thoại đọc từng chữ số, điểm đọc “chín phẩy tám”, viết tắt đọc đầy. Dùng đúng bộ chuẩn hoá của màn *Soát văn bản*, đừng viết riêng một bộ khác.
5. **Cảnh báo tính lại theo thiết lập thật** (năm trường hợp trong README), lót ở đầu thẻ giữa, có nút *Mở Khớp cột*.
6. **Mất mạng không được làm dừng buổi đọc.** Không lấy được dữ liệu thì dùng bản đã tải lần trước và báo rõ là dữ liệu lúc nào — dải cảnh báo vàng + chấm `warn` ở thanh dưới, không phải hộp thoại chặn.

7. **Nút “Mở bản ghép để nghe” mở bản ghép thành một tab tệp ở màn chính**, không mở cửa sổ riêng — mục *Tab bản ghép* trong README. Đoạn tĩnh sửa tại chỗ và ghi vào mẫu; đoạn động có vạch xanh, không sửa trực tiếp, bấm vào thì dẫn sang mẫu câu.
8. **Bảng tính cập nhật giữa lúc đang đọc không được làm mất dòng nào.** Không đổi đoạn đang đọc hay đã đọc; dòng mới sau chỗ đang đọc thì chèn im lặng, dòng mới thuộc chỗ đã đọc thì dồn vào đợt bổ sung ở cuối kèm câu dẫn; dòng đã sửa hoặc bị xoá xử theo bảng bốn trường hợp trong README. *Nghe toàn bộ* lấy dữ liệu một lần trước khi đọc; *Xuất file* chốt dữ liệu tại thời điểm bấm.

Mẫu ghép thuộc hồ sơ **Danh sách, biểu mẫu** đã có ở màn chính — không thêm hồ sơ mới, không đổi tên hồ sơ.

## Cách làm

1. Đối chiếu 6 mục trên với code hiện tại, báo tôi mục nào đã đúng / sai / chưa có, kèm file và vị trí. **Dừng chờ tôi duyệt** trước khi sửa.
2. Sửa theo thứ tự: đổi tên (mục 1) → lớp soạn thảo (mục 2) → nút ▶ và định dạng hàng (mục 3, 4) → thanh cuộn (mục 5) → thẻ cảm xúc (mục 6) → Google Docs (mục 8) → màn Văn bản ghép (mục 9).
3. Mọi con số không ghi ở đây thì lấy trực tiếp từ README hoặc từ file bản mẫu, đừng tự đoán.

## Nghiệm thu

- [ ] Không còn chữ `GiongDoc` nào hiển thị cho người dùng; đường dẫn dùng `GiongViet`
- [ ] Bấm vào chữ gõ được ngay; `Enter` / `Backspace` / `Delete` tách và nối đoạn đúng
- [ ] Chọn cả đoạn rồi Delete: mất đúng đoạn đó, các đoạn khác không đổi một ký tự
- [ ] Không có đoạn rỗng nào tồn tại sau khi rời khỏi đoạn
- [ ] Gõ chữ rồi đổi hồ sơ / đổi tệp rồi quay lại: chữ vẫn còn
- [ ] Cột trái: chỉ hồ sơ đang chọn mở danh sách tệp; hồ sơ khác thu một dòng có tên tệp đang xem và số tệp
- [ ] Con trỏ không nhảy về đầu đoạn khi đang gõ giữa câu
- [ ] Nút ▶ chỉ hiện ở đoạn đang trỏ chuột, cách thanh cuộn một khoảng
- [ ] Vùng đọc cuộn thật; thanh cuộn chỉ hiện khi chuột ở trong vùng
- [ ] Bấm vào thẻ cảm xúc gỡ được thẻ mà đoạn không bị nối lên trên
- [ ] Đoạn đang chọn có vạch xanh và nền bo góc, không tràn sát viền thẻ
- [ ] Tài liệu mẫu đầu tiên hiển thị `215 từ · 15 đoạn`, không còn dòng trống đánh số
- [ ] *Tệp → Mở từ Google Docs…* mở đủ ba bước trong một hộp; thẻ *Dán link* mở được mà không cần đăng nhập
- [ ] Tệp mở từ Google Docs có chip *Google Docs · lấy lúc hh:mm*, bấm lấy được bản mới
- [ ] Màn Văn bản ghép: đổi vai cột, bật/tắt phần tĩnh, sửa mẫu câu — cột *Bản ghép hoàn chỉnh* và số đoạn ở thanh dưới đổi theo ngay
- [ ] Trùng vai cột hoặc biến không có cột → hiện đúng cảnh báo, không đợi đến lúc đọc mới báo
- [ ] Không lấy được dữ liệu → vẫn đọc được bằng bản cũ, có dải cảnh báo ghi rõ giờ tải
