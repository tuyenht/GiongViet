# Giọng Việt — Đặc tả giao diện

Ứng dụng desktop Windows chuyển văn bản tiếng Việt thành giọng nói, chạy mô hình cục bộ trên máy người dùng.

Đối tượng: người Việt không rành kỹ thuật — nhân viên văn phòng, người làm nội dung, cán bộ phường xã, người quản lý loa phát thanh, tình nguyện viên. Toàn bộ giao diện bằng tiếng Việt.

Bộ này gồm **7 màn hình**.

## Việc thật của người dùng

Người dùng **không nghe hết cả bài**. Họ dán văn bản vào, nghe thử vài chỗ nghi ngờ (số, ngày tháng, viết tắt, tên riêng), sửa, nghe lại đúng chỗ vừa sửa, rồi xuất file. Mọi quyết định dưới đây đi ra từ việc đó.

Ba điều bắt buộc giữ nguyên:

1. **Đơn vị nội dung là đoạn, không phải dòng.** Mỗi đoạn là một khối chữ tự xuống dòng theo chiều rộng thẻ, **không bao giờ cắt cụt bằng dấu ba chấm**.
2. **Không có thanh tua theo thời gian.** Người dùng tìm chỗ cần nghe bằng cách cuộn văn bản, không kéo thanh thời gian. Thanh dưới chỉ *báo* tiến trình, không kéo được.
3. **Sửa văn bản tại chỗ như Notepad.** Vùng đọc là nơi gõ được, không phải nơi chỉ đọc. **Nút ▶ ở lề phải từng đoạn = nghe riêng đoạn đó, nghe hết đoạn thì dừng.** Muốn nghe liền mạch cả bài thì bấm *Nghe toàn bộ*.

---

## Mô hình dữ liệu

### Hồ sơ đọc (profile)
Một hồ sơ = **một chỗ làm việc riêng** cho một loại nội dung. Hồ sơ giữ:
- tên
- giọng đọc
- tốc độ / cao độ / âm lượng
- **danh sách tệp đang mở** và tệp đang xem

Đổi hồ sơ ở cột trái thì **tất cả đổi theo**: danh sách tệp, nội dung ở giữa, giọng và các thanh điều chỉnh ở cột phải, danh sách *Cần chú ý*. Đây không phải preset giọng — đây là nơi làm việc.

Bốn hồ sơ mặc định:

| Hồ sơ | Giọng | Điều chỉnh | Tệp mở sẵn |
|---|---|---|---|
| Bài viết, văn bản | Giọng Ngọc Linh | mặc định | `thongbao-quoc-khanh.txt`, `bai-viet-nghe-lai.docx` |
| Thông báo ngắn | Giọng Xuân Vĩnh | Tốc độ +10% | `thongbao-phun-thuoc.txt` |
| Sách nói | Giọng bác Tuấn (giọng của tôi) | Tốc độ −10%, Âm lượng 90% | `chuong-01.docx` |
| Danh sách, biểu mẫu | Giọng Bình An | mặc định | `danh-sach-ung-ho.txt` |

*Tạo hồ sơ mới* thêm hồ sơ trống (một tab chưa đặt tên) và chuyển sang hồ sơ đó ngay.

### Tài liệu
Mỗi tài liệu có: tên tệp, mảng đoạn (`head` | `body`), và bộ *Cần chú ý* riêng. **Không có đoạn rỗng trong mảng** — khi nạp tệp, mọi dòng trống bị bỏ. Đoạn không có id riêng — số đoạn là vị trí trong mảng, tính từ 1.

Thời lượng ước tính: `số ký tự / 11` giây mỗi đoạn, cộng lại. Dưới 60 giây ghi `42 giây`, từ 60 giây trở lên ghi `1 phút 28 giây`.

---

## Design tokens

Hệ thiết kế: **WinUI 3 / Fluent (Windows 11)**. Đủ chế độ sáng và tối, đổi bằng thuộc tính `data-theme` trên gốc tài liệu.

### Màu — chế độ sáng
```
bg        #f3f3f3   nền cửa sổ, thanh công cụ, thanh menu
layer     #ffffff   thẻ, dropdown, vùng soạn thảo
layer2    #fafafa   nền chìm (thanh trạng thái, chân hộp thoại, ô trống)
stroke    rgba(0,0,0,.0578)   viền thẻ
stroke2   rgba(0,0,0,.16)     viền control
divider   #e5e5e5   đường ngăn
txt       #1a1a1a   chữ chính
txt2      #5d5d5d   chữ phụ, thân đoạn
txt3      #767676   nhãn, số đoạn
dis       #a3a3a3   vô hiệu, đoạn đã đọc xong
ctl       #fdfdfd   nền nút viền
ctl-h     #f6f6f6   nút viền khi rê chuột
sub-h     rgba(0,0,0,.037)    nút chìm khi rê chuột
sel       rgba(0,0,0,.055)    đoạn đang chọn
acc       #0067c0   accent
acc-h     #1a75c6   accent khi rê chuột
acc-txt   #ffffff   chữ trên accent
acc-soft  rgba(0,103,192,.09) nền accent nhạt
hl        rgba(0,103,192,.11) đoạn đang đọc
chip-bg   rgba(0,0,0,.055)  chip-bd rgba(0,0,0,.09)  chip-fg #4a4a4a
ok        #0f7b0f
err       #c42b1c   err-bg #fdf3f4   err-bd #eecfd2
warn      #9d5d00   warn-bg #fff9ec  warn-bd #f0e2c2
rail      #868686   thanh trượt, thanh cuộn
shadow    0 8px 16px rgba(0,0,0,.14)
```

### Màu — chế độ tối
```
bg #202020   layer #2b2b2b   layer2 #272727
stroke rgba(255,255,255,.07)   stroke2 rgba(255,255,255,.10)   divider #303030
txt #ffffff   txt2 rgba(255,255,255,.73)   txt3 rgba(255,255,255,.60)   dis rgba(255,255,255,.38)
ctl rgba(255,255,255,.06)   ctl-h rgba(255,255,255,.084)   sub-h rgba(255,255,255,.06)   sel rgba(255,255,255,.08)
acc #4cc2ff   acc-h #47b1e8   acc-txt #000000   acc-soft rgba(76,194,255,.12)   hl rgba(76,194,255,.13)
chip-bg rgba(255,255,255,.09)   chip-bd rgba(255,255,255,.14)   chip-fg rgba(255,255,255,.82)
ok #6ccb5f   err #ff99a4 / #442726 / #6b3a38   warn #fce100 / #3a3320 / #5c4f2a
rail #9a9a9a   shadow 0 8px 16px rgba(0,0,0,.36)
```

Nút đóng cửa sổ luôn `#c42b1c` ở cả hai chế độ.

### Chữ
Segoe UI Variable Text, dự phòng Segoe UI → Inter → system-ui.

| Vai trò | Cỡ | Đậm |
|---|---|---|
| Tiêu đề đoạn (`head`) | 20px | 700 |
| Thân đoạn (`body`) | 18px | 400 (600 khi đang đọc) |
| Chữ giao diện | 14px | 400 |
| Tên thẻ, nhãn nhấn | 14px | 600 |
| Nhãn nhóm (VIẾT HOA) | 12px | 600, giãn chữ .04em |
| Chữ phụ, gợi ý | 12.5–13.5px | 400 |
| Số đoạn, thanh trạng thái | 12–12.5px | 400 |

Mọi con số hiển thị dùng `font-variant-numeric: tabular-nums`. Chữ đoạn dùng `text-wrap: pretty`, dòng cao 1.55.

### Khoảng cách, bo góc, đổ bóng
- Bậc khoảng cách: 2 · 4 · 6 · 8 · 12 · 14 · 16 · 24px
- Bo góc: **4px** cho control (nút, ô nhập, chip, mục menu); **8px** cho thẻ, dropdown, hộp thoại; **6px** cho dải cảnh báo; **5px** cho mục hồ sơ, **0 4px 4px 0** cho mục tệp trong cột trái; **11–15px** cho chip bo tròn; tròn hoàn toàn cho chấm trạng thái
- Đổ bóng: chỉ dropdown (`shadow`), hộp thoại (`0 32px 64px rgba(0,0,0,.32)`), thông báo góc (`0 12px 28px rgba(0,0,0,.28)`). **Thẻ không có đổ bóng** — chỉ viền 1px.

### Chuyển động
Đổi màu nền 0.15–0.2s. Vòng xoay tải: 0.8s tuyến tính vô hạn. Chấm đang xử lý: nhấp nháy 1.2s ease-in-out. Con trỏ nháy: 1.1s step-end. Không có hiệu ứng nảy.

---

## Màn hình 1 — Màn hình chính

**File:** `designs/GiongDoc - Màn hình chính v2 (nghe theo dòng).dc.html`

Cửa sổ 1440×900. Xếp dọc: thanh tiêu đề 32px → thanh menu 30px → thanh công cụ 44px → *(thanh tìm kiếm)* → *(dải cảnh báo)* → vùng ba cột (co giãn) → *(thanh phát 46px)* → thanh trạng thái 28px.

### Thanh tiêu đề (32px)
Logo 16px bo 3px nền accent, tên tệp + `— Giọng Việt`. Bên phải ba nút cửa sổ 46×32px; nút đóng khi rê chuột nền `#c42b1c` chữ trắng.

### Thanh menu (30px)
`Tệp · Chỉnh sửa · Chèn · Giọng · Xem · Trợ giúp`. Bấm mở menu thả xuống rộng tối thiểu 250px, mỗi mục cao 32px, tên bên trái, phím tắt bên phải màu `txt3`. Bấm ra ngoài đóng menu.

| Menu | Mục |
|---|---|
| Tệp | Mở tệp… `Ctrl+O` · Mở từ Google Docs… · Dán văn bản `Ctrl+V` · Lưu `Ctrl+S` · Xuất file âm thanh `Ctrl+E` · Đóng tệp `Ctrl+W` |
| Chỉnh sửa | Hoàn tác `Ctrl+Z` · Làm lại `Ctrl+Y` · Cắt `Ctrl+X` · Sao chép `Ctrl+C` · Tìm và thay thế `Ctrl+H` |
| Chèn | Thẻ cảm xúc `Alt+1…3` · Khoảng lặng 1 giây `Alt+S` · Ngắt đoạn `Enter` |
| Giọng | Đổi giọng đọc `Ctrl+G` · Nghe mẫu giọng `Ctrl+M` · Thư viện giọng · Nhân bản giọng từ file… |
| Xem | Thu gọn danh sách hồ sơ `Ctrl+B` · Cỡ chữ lớn hơn `Ctrl+=` · Cỡ chữ nhỏ hơn `Ctrl+-` · Giao diện tối |
| Trợ giúp | Hướng dẫn nhanh `F1` · Danh sách phím tắt `Ctrl+/` · Giới thiệu Giọng Việt |

### Thanh công cụ (44px)
Trái sang phải, tất cả đều là nút chìm (không viền), cao 32px:

1. **Dán văn bản** — icon clipboard
2. **Mở file** — icon thư mục
3. đường ngăn dọc 1px cao 20px
4. **Soát văn bản** — icon dấu tích, mở màn hình 2
5. **Thẻ cảm xúc** — có chevron, mở menu chèn thẻ

Đẩy sang phải:

6. **Tìm và thay thế** — icon kính lúp, bật/tắt thanh tìm kiếm
7. đường ngăn dọc
8. **Nghe toàn bộ** — nút viền, cao 34px, icon tam giác
9. **Xuất file âm thanh** — nút accent đặc, cao 34px, chữ đậm 600

Cặp (8)(9) **chỉ hiện khi có văn bản**. Khi chưa có văn bản, các mục (4)(5)(6) chuyển màu `dis`.

Khi máy chủ mất kết nối, hết lượt, hoặc giọng đang tải: (8) chuyển màu `dis`, (9) chuyển sang dạng nút viền màu `dis`, bấm không có tác dụng.

Menu **Thẻ cảm xúc** rộng 260px: dòng đầu ghi *Chèn vào đoạn N* (N là đoạn đang chọn), rồi ba mục `[cười]` Alt+1 · `[thở dài]` Alt+2 · `[hắng giọng]` Alt+3, mỗi mục là một chip bên trái và phím tắt bên phải; cuối cùng là **Gỡ thẻ khỏi đoạn này**. Chọn một thẻ thì thẻ hiện ngay đầu đoạn đang chọn dưới dạng chip.

### Danh sách tệp (trong cột trái, không có dải tab)
Tệp đang mở **không nằm trên một dải tab riêng** mà là danh sách con của hồ sơ trong cột trái, thụt vào 9px và có vạch trái 2px. Mỗi tệp cao 30px: icon tài liệu 13px + tên 13px + dấu × đóng (18px, hiện chữ `txt3`, rê chuột thành `txt`). Tệp đang xem: nền `sel`, tên đậm 600, icon và vạch trái màu `acc`.

- Bấm một tệp để xem; **nháy đúp để đổi tên** (ô nhập tại chỗ, viền `acc`, `Enter` lưu, `Esc` bỏ).
- Cuối danh sách là **Thêm tệp** (cao 28px, chữ `txt3`, icon dấu cộng) — mở thêm một tệp trong hồ sơ đó.
- Đóng tệp cuối cùng thì còn lại một tệp rỗng tên *Văn bản mới 1*.
- Danh sách tệp thuộc về hồ sơ đang chọn; hồ sơ khác giữ danh sách riêng của nó.

### Thanh tìm và thay thế (ẩn/hiện)
Nằm ngay dưới thanh công cụ, nền `layer`, viền `stroke2`, bo 6px, cao khoảng 46px: nhãn *Tìm* + ô nhập 180px (viền dưới 2px accent, có con trỏ nháy) + `1/1` + đường ngăn + nhãn *Thay bằng* + ô nhập 180px + nút **Thay thế** + nút **Thay tất cả** + dấu × đóng ở góc phải.

### Dải cảnh báo (ẩn/hiện)
Xem mục *Trạng thái lỗi và chờ*.

### Cột trái — Hồ sơ đọc (240px)
Đầu cột: nút ba gạch 32px (thu gọn) + tiêu đề **Hồ sơ đọc** 14px/600.

Danh sách hồ sơ mở theo **hồ sơ đang chọn**: chỉ hồ sơ đang chọn hiện danh sách tệp của nó và mục *Thêm tệp*; các hồ sơ khác thu về một dòng. Bấm một hồ sơ là chọn và mở nó cùng lúc — không có nút thu gọn riêng, không có trạng thái đóng/mở phải nhớ.

- **Hồ sơ đang chọn** (nền `layer`, viền `stroke`, tên đậm 600, vạch dọc 3px `acc`): tên 14px + tên giọng 12px, rồi danh sách tệp thụt vào 9px với vạch trái 2px, mỗi tệp cao 30px (icon tài liệu + tên + dấu × đóng), cuối cùng là *Thêm tệp* cao 28px.
- **Hồ sơ thu gọn** (~69px): tên 14px + tên giọng 12px + dòng thứ ba là **tên tệp đang xem** (icon tài liệu 11px, 12px `txt3`, cắt bằng ellipsis); bên phải ghi số tệp (`3 tệp`), có chấm đỏ 6px phía trước nếu hồ sơ đó đang có tệp mắc lỗi phải sửa.

Nhờ vậy chiều cao cột trái không phụ thuộc số tệp của các hồ sơ khác: một hồ sơ mở 8 tệp cũng không đẩy hồ sơ nào ra khỏi khung.

Mỗi mục hồ sơ cao khoảng 52px khi chỉ có tên và giọng: icon 17px, tên 14px, dưới là tên giọng 12px màu `txt3` (cắt bằng ellipsis nếu dài). Mục đang chọn: nền `layer`, viền 1px `stroke`, tên đậm 600, và một vạch dọc 3×18px bo 2px màu `acc` ở `left:2px` căn giữa theo chiều dọc. Bấm để đổi hồ sơ.

Dưới danh sách: **Tạo hồ sơ mới** (nút chìm, icon dấu cộng).

Đáy cột, tách bằng đường 1px `divider`: **Thư viện giọng** và **Cài đặt**, mỗi mục cao 36px.

**Thu gọn:** bấm nút ba gạch, cột còn 44px, chỉ còn icon — nút ba gạch, bốn icon hồ sơ (icon đang chọn nền `acc-soft` màu `acc`), và hai icon dưới đáy. Mỗi icon có tooltip là tên đầy đủ. Bấm lại để mở ra.

### Cột giữa — Vùng đọc (co giãn)
Thẻ nền `layer`, viền `stroke`, bo 8px.

Đầu thẻ cao 38px: bên trái `215 từ · 15 đoạn · khoảng 1 phút 28 giây`; bên phải gợi ý *Bấm vào chữ để sửa như Notepad · nút ▶ bên phải để nghe riêng đoạn* (12.5px, `txt3`).

Thân là danh sách đoạn, đệm trong thẻ 8px bên trái và 16px bên phải. Mỗi đoạn là một hàng bo 6px, đệm 7×8px — nền khi chọn / đang đọc là một khối bo góc phủ cả số đoạn, chữ và nút ▶, không tràn ra sát viền thẻ. Mỗi đoạn gồm:
- **Máng số** rộng 30px, số căn phải, cách chữ 12px, 12.5px màu `txt3` — chỉ để đánh dấu vị trí, không còn là nút.
- **Chữ** tràn theo chiều rộng còn lại của hàng, 18px (tiêu đề 20px/700), dòng cao 1.55, `text-wrap: pretty`, **sửa được trực tiếp** (xem *Sửa văn bản tại chỗ* bên dưới).
- **Nút nghe riêng đoạn** 26×26px bo 4px, tam giác 12px, nằm ở lề phải, cách thanh cuộn 10px. **Chỉ hiện khi rê chuột đến đoạn đó** hoặc khi đoạn đang đọc / đang tạo âm thanh (khi đó viền và chữ `acc`, nền `acc-soft`); đổi độ mờ 0.12s. Rê chuột lên nút: viền `acc`, nền `acc-soft`. Tooltip *Nghe riêng đoạn này, nghe hết đoạn thì dừng*.
- Nếu đoạn có thẻ cảm xúc: chip 12.5px/600, nền `chip-bg`, viền `chip-bd`, bo 4px, đệm 4×8px, đặt trước khối chữ, cách chữ 9px, không xuống dòng, **nằm ngoài vùng gõ**. **Gỡ thẻ:** bấm vào chip (rê chuột đổi viền và chữ sang `err`, tooltip *Bấm để gỡ thẻ cảm xúc*), hoặc `Backspace` khi con trỏ ở đầu chữ của đoạn đó — lần `Backspace` này gỡ thẻ, **không nối đoạn lên trên**; bấm tiếp mới nối đoạn.
- **Không có đoạn rỗng.** Văn bản không bao giờ hiển thị dòng trống đánh số.

Trạng thái đoạn:

| Trạng thái | Nền | Chữ | Máng số |
|---|---|---|---|
| Bình thường | trong suốt | `txt2` | `txt3` |
| Đang chọn (bấm vào) | `sel` + vạch trong 3px `acc` bên trái | như cũ, con trỏ gõ thật ở đúng chỗ bấm | như cũ |
| Đang đọc | `hl` + vạch trong 3px `acc` bên trái | `txt`, đậm 600 | `acc`, đậm 700 (không có tam giác) |
| Đã đọc xong (chỉ khi nghe liền mạch) | trong suốt | `dis` | `dis` |
| Đang tạo âm thanh | `hl` | `txt` | vòng xoay 11px trước số |

Rê chuột lên đoạn: nền `sub-h`, nút ▶ của đoạn đó hiện ra.

Vùng đọc **cuộn thật** (`overflow-y: auto`), thanh cuộn mảnh (`scrollbar-width: thin`) màu `rail`, **chỉ hiện khi chuột ở trong vùng đọc** — chuột ra khỏi vùng thì `scrollbar-color` chuyển sang trong suốt, đồng thời ẩn nút ▶.

### Sửa văn bản tại chỗ
Vùng đọc làm việc như Notepad, không có chế độ *xem* / *sửa* riêng:
- Bấm vào chữ → con trỏ nháy đúng vị trí bấm; gõ, xoá, chọn khối, dán đều được. Dán chỉ nhận chữ trần, không nhận định dạng.
- `Enter` tách đoạn tại con trỏ; phần sau con trỏ thành đoạn mới, con trỏ ở đầu đoạn mới.
- `Backspace` ở đầu đoạn → nối đoạn đó vào cuối đoạn trên, con trỏ ở chỗ nối. `Delete` ở cuối đoạn → kéo đoạn dưới lên.
- **Đoạn bỏ trống tự xoá** khi rời khỏi đoạn đó, số đoạn đánh lại liền mạch. Không có ngoại lệ nào — cả dòng trống sẵn có trong tệp gốc cũng bị bỏ khi nạp.
- Số từ, số đoạn, thứ tự và ước tính thời lượng cập nhật theo từng thao tác sửa.
- Sửa đoạn đã nghe/đã xuất → áp tình huống *Âm thanh cũ sau khi sửa văn bản*.

**Trạng thái rỗng:** khung nét đứt 1.5px `stroke2`, rộng 500px, bo 8px, nền `layer2`, đệm 44×32px, canh giữa. Bên trong: icon clipboard 52px mờ .75 → tiêu đề 18px/600 *Dán văn bản vào đây để bắt đầu* → hai dòng 14px *Nhấn Ctrl+V, hoặc kéo thả tệp .txt, .docx, .rtf vào cửa sổ này.* / *Hồ sơ đang chọn: **{tên hồ sơ}** — {tên giọng}.* → ba nút: **Dán văn bản** (accent), **Chọn tệp từ máy…** (viền) và **Mở từ Google Docs…** (viền).

### Mở tài liệu từ Google Docs

Hai đường vào: menu *Tệp → Mở từ Google Docs…* và nút thứ ba ở trạng thái rỗng. Hộp thoại rộng 620px, bo 8px, phủ lên màn chính (màn nền `rgba(0,0,0,.34)`).

Đầu hộp: tiêu đề 18px/600 **Mở tài liệu Google Docs** + dòng phụ đổi theo bước + dấu × 28px. Ba bước dùng chung một hộp:

**Bước 1 — đăng nhập** (chỉ khi chưa đăng nhập). Icon tài liệu trong vòng tròn 46px nền `acc-soft` → *Đăng nhập Google để xem danh sách tài liệu* (15.5px/600) → đoạn giải thích: đăng nhập một lần, và Giọng Việt chỉ xin quyền **đọc**, không sửa không xoá gì trên Drive → nút accent **Đăng nhập bằng Google** → liên kết *Hoặc dán link tài liệu, không cần đăng nhập* (nhảy thẳng sang thẻ *Dán link*). Dòng phụ đầu hộp: *Cần đăng nhập Google một lần để đọc danh sách tài liệu*.

**Bước 2 — chọn tài liệu.** Hai thẻ **Từ Drive** / **Dán link** (thẻ đang chọn nền `acc`, chữ `acc-txt`). Khi đã đăng nhập, bên phải hàng thẻ hiện email `chuaanlac.vp@gmail.com` + liên kết *Đổi tài khoản* (quay về bước đăng nhập).

- *Từ Drive*: ô tìm 34px (icon kính lúp + *Tìm theo tên tài liệu…*), rồi danh sách cao tối đa 290px, cuộn được. Mỗi dòng: icon tài liệu 17px + tên 14px + dòng phụ 12.5px *ai sửa lần cuối · khi nào*; dòng đang chọn nền `acc-soft`, viền `acc`, tên đậm 600, dấu tích `acc` bên phải. Bấm để chọn, nháy đúp để mở luôn. Không khớp thì hiện *Không có tài liệu nào khớp “{từ khoá}”. / Thử tên khác, hoặc dán link tài liệu ở thẻ bên cạnh.*
- *Dán link*: nhãn *Link tài liệu Google Docs* + ô nhập viền dưới 2px `acc`, gợi ý `https://docs.google.com/document/d/…`; dưới là ô chú thích nền `ctl`: tài liệu phải bật **“Bất kỳ ai có đường liên kết đều xem được”**, cách này không cần đăng nhập — tiện khi mượn máy hoặc dùng máy chung. Nút **Mở tài liệu** chỉ bật khi link có dạng `docs.google.com/document`.

**Bước 3 — đang tải.** Vòng xoay 34px + *Đang tải {tên tài liệu}…* (15px/600) + *Tải xong sẽ mở ra như một tệp văn bản thường.* Xong thì tài liệu mở thành một tab tệp mới trong hồ sơ đang dùng.

Chân hộp nền `layer2`: chú thích 12.5px bên trái đổi theo bước (`{số} tài liệu · nháy đúp để mở nhanh` / *Không có tài liệu nào khớp* / *Bấm Huỷ nếu bạn không muốn mở tài liệu này nữa*), rồi **Huỷ** (viền) và **Mở tài liệu** (accent; chuyển màu `dis` khi chưa chọn được gì).

Ba tài liệu mẫu trên Drive: *Thư cảm ơn cuối năm* — Bạn sửa lần cuối · 14:02 hôm nay · *Thông báo lễ tổng kết năm học 2026* — Cô Hạnh sửa lần cuối · hôm qua · *Danh sách khen thưởng học kỳ hai* — Thầy Dũng sửa lần cuối · 9/8/2026.

**Tệp mở từ Google Docs** có thêm một chip ở đầu vùng đọc, ngay sau dòng thống kê: bo tròn 22px, nền `acc-soft`, viền `acc`, icon vòng lặp + *Google Docs · lấy lúc 14:02*. Tooltip *Tệp này lấy từ Google Docs lúc 14:02 — bấm để lấy bản mới nhất*. Bấm chip: icon xoay, chữ đổi thành *Đang lấy bản mới từ Google Docs…*, xong thì ghi lại giờ lấy mới. Tệp mở từ máy không có chip này.

### Tab bản ghép

Bấm **Mở bản ghép để nghe** ở màn *Văn bản ghép* thì bản ghép mở thành **một tệp trong hồ sơ đang dùng** (thêm vào danh sách tệp ở cột trái), tên tệp là tên mẫu (`Danh sách công đức`), nội dung là các đoạn đã ghép sẵn và đánh số liên tục: đầu danh sách → tên nhóm → từng dòng → câu xen giữa → cuối. Nghe riêng từng đoạn, nghe toàn bộ, xuất file đều như tệp thường. Khác tệp thường ba điểm:

- **Chip ở đầu vùng đọc**, cùng kiểu chip Google Docs: *Bản ghép · 248 dòng · lấy lúc 14:58*, bấm để lấy dữ liệu mới (icon xoay, chữ đổi thành *Đang lấy dữ liệu mới từ bảng tính…*). Cạnh chip là liên kết **Mở mẫu ghép ›** về màn 7.
- **Đoạn tĩnh sửa được tại chỗ** như mọi tệp khác, và sửa ở đây ghi thẳng vào mẫu.
- **Đoạn động không sửa tại chỗ**: có vạch dọc 2px `acc` ở lề trái, không nhận con trỏ gõ. Bấm vào đoạn thì ngay dưới đoạn hiện một dải `acc-soft`: *Đoạn này do bảng tính sinh ra, không sửa trực tiếp ở đây.* + liên kết **Sửa mẫu câu ›**. Gợi ý ở đầu vùng đọc đổi thành *Đoạn có vạch xanh lấy từ bảng tính · phần bạn viết sửa như Notepad · nút ▶ để nghe riêng đoạn*.

**Bảng tính cập nhật giữa lúc đang đọc.** Nguyên tắc: **không bao giờ đổi đoạn đang đọc hoặc đã đọc; chỉ nối thêm vào phần chưa đọc.** App tự kiểm tra 5 phút một lần, so bản mới với bản đang đọc theo khoá dòng rồi xử theo bốn trường hợp:

| Trường hợp | Xử lý |
|---|---|
| Dòng mới nằm sau chỗ đang đọc | chèn im lặng vào đúng vị trí của nó — đọc tới là đọc đủ, không hỏi gì |
| Dòng mới thuộc chỗ đã đọc qua | dồn vào **đợt bổ sung ở cuối danh sách**, trước câu xen giữa và câu kết, có câu dẫn *Sau đây là danh sách bổ sung.*; chip vàng báo `3 dòng mới, đã thêm vào cuối` |
| Dòng đã sửa | chưa đọc thì cập nhật im lặng; đã đọc rồi thì giữ nguyên buổi đọc và báo qua tình huống *Bạn vừa sửa văn bản, bản đã nghe là bản cũ* + nút *Đọc lại 2 dòng* |
| Dòng bị xoá | chưa đọc thì bỏ khỏi phần còn lại; đang đọc dòng đó thì đọc hết dòng rồi mới bỏ, không cắt giữa câu |

Hai chốt kèm theo: bấm *Nghe toàn bộ* thì **lấy dữ liệu một lần trước khi đọc**; bấm *Xuất file âm thanh* thì **chốt dữ liệu tại thời điểm bấm** — bảng tính đổi giữa lúc xuất không làm hỏng tệp, xuất xong mới báo *Có 3 dòng mới sau khi bắt đầu xuất*.

Bản mẫu dựng tab này trong hồ sơ *Danh sách, biểu mẫu* với mười dòng đầu của 248 dòng; bấm chip là thêm đợt bổ sung ba dòng vào cuối để xem đúng hành vi trên.

### Cột phải (300px)

**Thẻ trên — hồ sơ và giọng.** Ba phần ngăn bằng đường 1px:

1. Nhãn `HỒ SƠ ĐANG DÙNG` + tên hồ sơ 14px/600.
2. Nhãn `GIỌNG ĐỌC` + ô chọn giọng cao 36px (icon micro + tên giọng + chevron) và nút loa 36×36px bên cạnh (nghe mẫu 5 giây). Bấm nút loa hiện dòng *Đang phát mẫu {tên giọng}…* kèm chấm nhấp nháy, tự tắt sau khoảng 2,5 giây.
   Ô chọn giọng mở dropdown: nhóm `GIỌNG CÓ SẴN` (Giọng Bình An · Nữ · Bắc / Giọng Ngọc Linh · Nữ · Nam / Giọng Xuân Vĩnh · Nam · Trung), nhóm `GIỌNG CỦA TÔI` (Giọng bác Tuấn · Nam · 62 tuổi / Giọng của tôi (thử) · mẫu 30 giây), cuối cùng **Nhân bản giọng từ file…** màu accent. Mỗi dòng có ô tích bên trái khi đang chọn và nút tam giác nghe mẫu bên phải. **Chọn giọng là ghi vào hồ sơ đang dùng.**
3. Nhãn `ĐIỀU CHỈNH` có chevron thu gọn. Khi đóng: một dòng tóm tắt, ví dụ *Tốc độ −10% · Âm lượng 90%*, hoặc *Theo mặc định của hồ sơ*. Khi mở: ba thanh trượt **Tốc độ** (−50% … +100%), **Cao độ** (−12 … +12 nửa cung), **Âm lượng** (0 … 100%), rồi **Đặt lại mặc định**. Thanh trượt: rãnh 4px `rail` mờ .5, phần đã chọn `acc`, núm 20px tròn nền `layer` viền `stroke2` chấm trong 11px `acc`. **Kéo thanh là ghi vào hồ sơ đang dùng.**

**Thẻ dưới — Cần chú ý** (chỉ hiện khi có văn bản). Nhãn `CẦN CHÚ Ý` → một câu tóm tắt, ví dụ *9 chỗ cần chú ý, trong đó 2 lỗi nên sửa trước khi xuất.* → danh sách loại lỗi, mỗi dòng cao 31px: chấm 7px (đỏ `err` cho lỗi bắt buộc, `dis` cho cảnh báo) + tên loại + số đếm dạng nhãn bo 4px (nền `err-bg` chữ `err`, hoặc nền `chip-bg` chữ `txt2`). Mỗi dòng có tooltip liệt kê chỗ cụ thể, bấm vào thì chọn đoạn tương ứng ở giữa. Dưới cùng: nút viền **Soát văn bản** (mở màn hình 2) và liên kết **Từ điển phát âm ›** (mở màn hình 5).

### Thanh phát (46px, chỉ khi đang phát hoặc đang tạo)
- **Đang tạo âm thanh:** vòng xoay 18px + *Đang tạo âm thanh cho đoạn N* (14px/600) + *Thường mất 5–10 giây cho mỗi đoạn* + nút **Huỷ** ở góc phải.
- **Đang phát:** nút tạm dừng 32px nền accent + nút dừng 32px chìm → *Đang đọc đoạn 4/16* hoặc *Đang nghe riêng đoạn 4* → đồng hồ `00:35 / 02:12` → thanh tiến trình rộng 150px cao 3px (**không kéo được**) → *Đang chuẩn bị đoạn tiếp theo…* hoặc *Nghe hết đoạn này sẽ dừng*.

### Thanh trạng thái (28px)
Trái: `Đoạn 13, Cột 1` (số đoạn đang chọn, hoặc đang đọc khi đang phát). Phải: chấm trạng thái + nhãn máy đọc, đường ngăn, `Đã lưu 14:02 · Hồ sơ: {tên hồ sơ}`.

| Tình huống | Chấm | Nhãn |
|---|---|---|
| Bình thường | `ok` | VieNeu v3 Turbo · sẵn sàng |
| Đang tạo âm thanh | `acc` | VieNeu v3 Turbo · đang tạo âm thanh |
| Đang xuất | `acc` | Đang xuất tệp âm thanh · 34% |
| Mất kết nối | `err` | VieNeu v3 Turbo · mất kết nối |
| Hết lượt | `warn` | VieNeu v3 Turbo · hết lượt tháng này |
| Giọng đang tải | `warn` | Đang tải {tên giọng} · 62% |

**Không hiển thị** mã hoá tệp, kiểu xuống dòng, hay mức phóng to — người dùng không cần và không hiểu.

### Hộp thoại xuất file
Bấm **Xuất file âm thanh** mở hộp thoại phủ lên màn hình (màn nền tối `rgba(0,0,0,.34)`), rộng 600px, bo 8px.

Đầu: tiêu đề 20px/600 **Xuất file âm thanh** + dòng phụ `{tên tệp} · {số} đoạn · {tên giọng}`.

Thân: **Tên tệp** (ô nhập, viền dưới 2px accent, phần đuôi `.wav` màu `txt3`) và **Định dạng** (WAV 24 bit / WAV 16 bit / MP3 320 kbps / MP3 128 kbps) trên cùng một hàng · **Lưu vào** (đường dẫn + nút *Chọn…*) · **Tách tệp** (ba lựa chọn tròn: *Một tệp duy nhất* / *Mỗi đoạn một tệp — {số} tệp* / *Cắt theo độ dài — mỗi 10 phút một tệp*).

Chân, nền `layer2`: ước tính `Ước tính 1 phút 28 giây · khoảng 11,6 MB` bên trái; **Huỷ** (viền) và **Bắt đầu xuất** (accent) bên phải.

Bấm *Bắt đầu xuất*: hộp thoại đóng, thanh trạng thái chuyển sang *Đang xuất… 34%*, khoảng 2 giây sau hiện thông báo góc dưới phải rộng 360px: **Đã xuất xong tệp âm thanh** + `{tên tệp} · {thời lượng} · {dung lượng}` + `Lưu tại: Tài liệu\GiongDoc\Xuất` + hai nút **Mở thư mục** / **Đóng**.

### Trạng thái lỗi và chờ
Dải cảnh báo nằm giữa thanh công cụ và vùng ba cột, cách hai bên 8px, bo 6px, viền 1px: icon 18px + tiêu đề 14px/600 + dòng giải thích 13.5px + nút hành động bên phải. Lỗi dùng bộ `err`, cảnh báo dùng bộ `warn`.

| Tình huống | Tiêu đề | Nội dung | Nút | Ảnh hưởng khác |
|---|---|---|---|---|
| Mất kết nối máy chủ | Không kết nối được máy chủ đọc | Văn bản của bạn vẫn được giữ nguyên. Kiểm tra lại mạng rồi thử lại. | Thử lại | khoá Nghe và Xuất |
| Hết lượt | Đã dùng hết dung lượng gói tháng này | Bạn đã đọc 100.000/100.000 ký tự. Gói làm mới sau 12 ngày, hoặc nâng gói để dùng tiếp ngay. | Xem chi tiết · Nâng gói | khoá Nghe và Xuất |
| Giọng đang tải | Đang tải giọng {tên} về máy | Còn khoảng 1 phút nữa. Bạn vẫn soạn và sửa văn bản được, chưa nghe được. | Dùng giọng khác | khoá Nghe và Xuất; thẻ giọng hiện thanh tiến trình 62% |
| Văn bản quá dài | Văn bản dài hơn giới hạn một lần xuất | 12.400 ký tự, giới hạn 10.000. Khi xuất, phần mềm sẽ cắt thành 2 tệp, cắt ở ranh giới đoạn. | Xem chỗ cắt | vẫn xuất được |
| Âm thanh cũ | Bạn vừa sửa văn bản, bản đã nghe là bản cũ | 3 đoạn đã đổi: đoạn 4, 9 và 10. Nghe lại hoặc xuất lại để lấy bản mới. | Nghe lại 3 đoạn | vẫn xuất được |
| Đang tạo âm thanh | *(không có dải cảnh báo)* | | | vòng xoay ở máng số đoạn đang chờ + thanh phát dạng chờ |

Nguyên tắc viết lỗi: nói điều đã xảy ra, trấn an là dữ liệu còn nguyên, rồi nói việc cần làm. Không mã lỗi, không thuật ngữ.

---

## Màn hình 2 — Soát văn bản

**File:** `designs/GiongDoc - Soát văn bản.dc.html`
**Mục đích:** tìm những chỗ máy sẽ đọc sai và sửa trước khi xuất.

Là một chế độ phủ lên cửa sổ chính: **cột trái (hồ sơ đọc kèm danh sách tệp) và cột phải (thẻ hồ sơ — giọng — điều chỉnh và thẻ Cần chú ý) của màn chính vẫn hiện nguyên nội dung**, chỉ mờ đi (opacity .55) và không bấm được (`pointer-events:none`); phần giữa là nội dung của màn này. Hai cột đó giữ ngữ cảnh — người dùng biết mình đang soát tệp nào, trong hồ sơ nào, bằng giọng nào.

Thanh công cụ riêng cao 42px có **hai tab**:

1. **Chỗ cần chú ý** — danh sách lỗi
2. **Văn bản sau chuẩn hoá** — so sánh gốc với cách máy đọc

Tab đang chọn: nền `acc-soft`, chữ và viền `acc`. Bên phải thanh: *Lần soát cuối: 14:03 · tự động soát khi mở tệp* (tab 1) hoặc *11 chỗ sẽ được đọc khác văn bản gốc · 15 đoạn* (tab 2).

### Tab 1 — Chỗ cần chú ý
Trên: vùng văn bản, mỗi đoạn có gạch chân lượn sóng dưới chỗ có vấn đề (đỏ `err` cho lỗi, vàng `warn` cho cảnh báo, `text-underline-offset: 5px`, `text-decoration-skip-ink: none`) và nhãn loại lỗi ở lề phải.

Dưới: bảng **Kết quả soát** cao 302px. Đầu bảng: tiêu đề + ba chip lọc *Tất cả (9)* / *Lỗi (2)* / *Cảnh báo (7)*, mỗi chip có chấm màu; bên phải hai nút **Sửa tất cả có thể (5)** và **Bỏ qua tất cả**. Hàng tiêu đề cột 32px chữ hoa 12px: Đoạn (64px) · Loại (150px) · Nội dung cảnh báo (co giãn) · Đề xuất (300px) · Hành động (150px). Mỗi hàng cao 38px, ngăn bằng `divider`, hàng thuộc đoạn đang chọn nền `acc-soft`. Cột hành động có nút viền (Sửa / Nghe / Tách / Đổi / Thêm) và chữ **Bỏ qua**.

### Tab 2 — Văn bản sau chuẩn hoá
Đầu: nhãn `QUY TẮC ĐANG BẬT` + bốn chip bật/tắt — *Số thành chữ 48* · *Viết tắt, ký hiệu 6* · *Ngày tháng 3* · *Bỏ dấu câu lặp 0*. Chip bật: nền `acc-soft`, viền và chữ `acc`, dấu tích. Chip tắt: viền `stroke2`, chữ `txt3`, dấu ×.

Thân: bảng hai cột **VĂN BẢN GỐC** / **MÁY SẼ ĐỌC THÀNH**, ngăn bằng đường dọc 1px, số đoạn ở cột 52px bên trái. Cột phải: phần bị đổi được tô nền `mark` (sáng `rgba(0,103,192,.14)`, tối `rgba(76,194,255,.2)`), bo 3px, đậm 600. Đoạn không đổi thì cột phải để chữ màu `txt3`.

Ví dụ chuẩn hoá phải giữ nguyên:
- `2/9` → **hai phần chín**
- `TNHH` → **trách nhiệm hữu hạn**
- `UBND TP.HCM` → **Uỷ ban nhân dân Thành phố Hồ Chí Minh**
- `31/8/2026` → **ba mươi mốt tháng tám năm hai nghìn không trăm hai mươi sáu**
- `17h00` → **mười bảy hắt không không**
- `1900 6868` → **một chín không không sáu tám sáu tám**
- `TM. BAN GIÁM ĐỐC` → **Tê mờ** ban giám đốc

Chân: chú thích *Chuẩn hoá chỉ ảnh hưởng đến âm thanh, văn bản gốc của bạn không thay đổi.* và hai nút **Nghe thử đoạn đang chọn** · **Thêm vào từ điển phát âm**.

---

## Khung chung của các màn phụ

Các màn 4, 5, 6 và 7 dùng chung một khung: thanh tiêu đề 32px (logo + tên màn + `— Giọng Việt` + nút **‹ Màn hình chính** dạng chip bo tròn 22px nền `sub-h`, rồi ba nút cửa sổ bên phải) → vùng nội dung chia hai cột: **cột trái 240px** là danh sách nhóm/bộ lọc, **cột phải** là một thẻ nền `layer` viền `stroke` bo 8px chiếm hết chỗ còn lại.

Mục đang chọn ở cột trái: nền `layer`, viền 1px `stroke`, chữ đậm 600, vạch dọc 3×18px màu `acc` ở `left:2px`. Đầu cột trái có mũi tên quay lại 30px + tên màn 16px/600. Đáy cột trái là một dòng thông tin phụ 13px màu `txt3`.

Kích thước nào không ghi trong tài liệu này thì lấy đúng theo bản mẫu HTML.

---

## Màn hình 3 — Xuất file âm thanh

**File:** `designs/GiongDoc - Xuất file âm thanh.dc.html`

Hộp thoại 600px phủ lên màn chính (màn nền mờ), **ba giai đoạn trong cùng một hộp**. Màn hình chính chỉ dựng giai đoạn 1; ba giai đoạn đầy đủ nằm ở màn này.

**Giai đoạn 1 — thiết lập.** Như mô tả ở màn hình 1: Tên tệp + Định dạng · Lưu vào · Tách tệp · Khoảng lặng giữa các đoạn (thanh trượt). Ba lựa chọn tách tệp: *Một tệp duy nhất — 11,6 MB* · *Mỗi đoạn một tệp — 16 tệp* · *Cắt theo độ dài — mỗi 10 phút một tệp*. Dòng ước tính đổi theo lựa chọn:
- `Ước tính: 1 tệp · 11,6 MB · khoảng 27 giây xử lý`
- `Ước tính: 16 tệp · tổng 11,9 MB · khoảng 34 giây xử lý`
- `Ước tính: 1 tệp · 11,6 MB · chưa tới 10 phút nên không cắt`

**Giai đoạn 2 — đang xuất.** Vòng xoay 16px + tiêu đề 20px/600 *Đang xuất thongbao-quoc-khanh.wav* → thanh tiến trình cao 5px bo 3px → ba dòng số liệu căn hai bên: *Đã trôi qua* `00:38` · *Còn lại (ước tính)* · *Đã ghi* `16,2 MB`. Bên dưới là danh sách đoạn đang xử lý dạng vạch mờ. Nút **Huỷ** ở chân hộp.

**Giai đoạn 3 — xong.** Tiêu đề thành công → thẻ tóm tắt nền `layer2` viền `stroke` bo 6px: tên tệp đậm 600, rồi ba dòng căn hai bên *Thời lượng* `1 phút 28 giây` · *Kích thước* `11,6 MB` · *Thời gian xử lý* `00:27` → đường dẫn đầy đủ 13px màu `txt3` (`word-break: break-all`). Chân hộp: **Mở thư mục** · **Xuất tiếp bản khác** · **Đóng**.

---

## Màn hình 4 — Thư viện giọng

**File:** `designs/GiongDoc - Thư viện giọng.dc.html`
**Mục đích:** xem, nghe thử, chọn và quản lý mọi giọng có trên máy; nhân bản giọng mới.

**Cột trái** — bộ lọc, mỗi mục cao 38px, có số đếm bên phải: *Tất cả giọng 8* · *Giọng có sẵn 6* · *Giọng của tôi 2* · *Đang tải về —*. Đáy cột: *Đã dùng 6,4 GB cho mô hình giọng. / Còn trống 128 GB.*

**Đầu thẻ phải (56px):** ô tìm kiếm 300px (*Tìm theo tên, vùng miền…*) · bộ lọc *Giới tính: Tất cả* · bộ lọc *Vùng: Tất cả* · đẩy sang phải là nút accent **Nhân bản giọng mới** (icon dấu cộng).

**Thân:** hai nhóm, mỗi nhóm có nhãn viết hoa 12px — `GIỌNG CỦA TÔI` rồi `GIỌNG CÓ SẴN`. Thẻ giọng rộng **270px**, nền `layer2`, viền `stroke` (viền `acc` nếu đang dùng), bo 8px, đệm 13px:

- Hàng đầu: vòng tròn 34px chứa icon micro (giọng của tôi: nền `acc-soft` màu `acc`; giọng có sẵn: nền `chip-bg` màu `txt2`) + tên giọng 15px/600 + nhãn **Đang dùng** (chip bo 9px nền `acc` chữ `acc-txt` 11.5px/600) nếu đang dùng.
- Dòng phụ 13px `txt3`: giới tính · vùng miền · tính chất · dung lượng. Ví dụ *Nữ · miền Nam · nhẹ nhàng · 620 MB*; giọng nhân bản ghi thêm ngày tạo: *Nam · 62 tuổi · nhân bản 12/6/2026 · 480 MB*.
- Dải sóng âm: 26 vạch, cao 6–28px, bo 1px, khoảng cách 2px, cao tổng 30px. Giọng đang dùng dùng màu đậm, giọng khác dùng `rail`.
- Hàng nút: **Nghe thử** (nút viền, icon tam giác) · **Dùng giọng này** (nút accent; nếu đang dùng thì đổi thành *Đang dùng*, nền trong suốt, chữ `txt3`, không bấm được) · nút ba chấm 32px (tuỳ chọn: đổi tên, xoá, xem chi tiết).

Cuối nhóm *Giọng của tôi* là ô nét đứt 270px cùng chiều cao thẻ: icon dấu cộng 26px + *Nhân bản giọng mới* + *Cần 30 giây thu âm*.

**Chân thẻ (44px), nền `layer2`:** `8 giọng · 2 giọng của tôi` | `Giọng đang dùng cho hồ sơ "Bài viết, văn bản": **Giọng Ngọc Linh**`.

Sáu giọng có sẵn: Bình An (Nữ · miền Bắc · trầm ấm · 620 MB) · Ngọc Linh (Nữ · miền Nam · nhẹ nhàng · 620 MB) · Xuân Vĩnh (Nam · miền Trung · rõ ràng · 640 MB) · Minh Quân (Nam · miền Bắc · dứt khoát · 610 MB) · Hải Yến (Nữ · miền Bắc · truyền cảm · 630 MB) · Thiện Tâm (Nam · miền Nam · chậm, phù hợp kinh sách · 660 MB).

---

## Màn hình 5 — Từ điển phát âm

**File:** `designs/GiongDoc - Từ điển phát âm.dc.html`
**Mục đích:** ghi cách đọc riêng cho tên riêng, viết tắt ngành, từ địa phương — để không phải sửa đi sửa lại trong từng văn bản.

**Cột trái** — phạm vi, có số đếm: *Tất cả 34* · *Mọi hồ sơ 12* · *Bài viết, văn bản 16* · *Sách nói 4* · *Thông báo ngắn 2*.

**Đầu thẻ phải:** ô tìm kiếm 280px (*Tìm từ hoặc cách đọc…*) · đẩy sang phải: **Nhập từ tệp CSV** (nút viền) và **Thêm từ** (nút accent, icon dấu cộng).

**Khung thêm từ** (hiện khi bấm *Thêm từ*), nền `acc-soft`, đệm 14×16px, các ô căn đáy: *Từ trong văn bản* (230px, viền dưới 2px `acc`) · *Đọc thành* (co giãn, placeholder *ví dụ: …*) · *Phạm vi* (170px, mặc định **Hồ sơ hiện tại**) · nút **Nghe thử** (viền) · **Lưu** (accent) · **Huỷ** (chìm).

**Bảng.** Hàng tiêu đề 34px nền `layer2`, chữ hoa 12px: Từ trong văn bản (250px) · Đọc thành (co giãn) · Phạm vi (170px) · Lần dùng (120px) · Hành động (130px, căn phải). Mỗi hàng cao 42px, ngăn bằng `divider`, từ gốc 15px màu `txt`, cách đọc màu `txt2`. Cột phạm vi dùng chip nhỏ. Cột hành động: **Sửa** và **Xoá**.

Ví dụ nội dung giữ nguyên: `Bùi Thị Thanh Tâm` → *Bùi Thị Thanh Tâm (đọc chậm, rõ dấu)* · 6 lần; `Phúc Lâm` → *Phúc Lâm (không đọc là Phúc Lam)* · 18 lần.

---

## Màn hình 6 — Cài đặt

**File:** `designs/GiongDoc - Cài đặt.dc.html`

**Cột trái** — sáu nhóm, mỗi nhóm có tên và một dòng mô tả:

| Nhóm | Mô tả |
|---|---|
| Chung | Ngôn ngữ, khởi động, giao diện |
| Giọng & mô hình | Mô hình đọc, tăng tốc phần cứng |
| Xuất file | Định dạng, nơi lưu, đặt tên |
| Phím tắt | Xem và đổi phím tắt |
| Bộ nhớ | Dung lượng mô hình và bộ đệm |
| Về Giọng Việt | Phiên bản, cập nhật, giấy phép |

Đáy cột trái: `Giọng Việt 1.4.2` / `Bản quyền đã kích hoạt`.

**Cột phải** — danh sách thiết lập của nhóm đang chọn. Mỗi dòng có tên 14px, dòng giải thích 13px màu `txt3` bên dưới (bỏ trống nếu không cần), và điều khiển ở bên phải. Bốn kiểu điều khiển:

- `toggle` — công tắc bật/tắt
- `select` — ô chọn có chevron, hiện giá trị hiện tại
- `path` — đường dẫn + nút *Chọn…* (hoặc *Xoá* cho bộ đệm)
- `meter` — thanh dung lượng kèm hai nhãn hai bên, ví dụ *6,4 GB đã dùng* / *còn 128 GB*

Nội dung mẫu giữ nguyên, ví dụ: *Ngôn ngữ giao diện — Áp dụng cho toàn bộ ứng dụng — Tiếng Việt* · *Tăng tốc bằng GPU (NVIDIA) — Phát hiện: RTX 3060 · nhanh hơn khoảng 3 lần* · *Tải mô hình sẵn khi mở ứng dụng — Mất thêm ~40 giây khi khởi động, bù lại phát nhanh* · *Giải phóng mô hình khi rảnh 10 phút — Trả lại RAM cho các ứng dụng khác* · *Cảnh báo khi RAM trống dưới 2 GB — Tránh lỗi không tải được mô hình*.

---

## Màn hình 7 — Văn bản ghép

**File:** `designs/GiongDoc - Văn bản ghép.dc.html`
**Mục đích:** đọc một danh sách dài mà chỉ phải viết một lần. Người dùng viết phần **tĩnh** (câu mở đầu, câu xen giữa, câu kết), khai một **mẫu câu** cho mỗi dòng, và phần **động** lấy từ bảng tính — bảng thêm dòng thì bản đọc tự có dòng mới, không phải gõ lại.

Một **mẫu ghép** giữ đủ: nguồn dữ liệu, cách khớp cột, luật lọc và nhóm, bốn khối nội dung. Mẫu ghép thuộc hồ sơ **Danh sách, biểu mẫu**; một hồ sơ giữ **nhiều mẫu ghép**. Bản mẫu có sẵn hai mẫu: *Danh sách công đức* (248 dòng) và *Quỹ khuyến học tháng 8* (96 dòng).

Màn này **không dành riêng cho một loại danh sách nào**. Từ vựng ở giao diện là từ vựng chung (cột, dòng, nhóm, cách đọc); nội dung riêng của từng loại nằm trong mẫu sẵn.

Dùng khung chung của các màn phụ, thêm cột thứ ba và một thanh dưới: thanh tiêu đề 32px → *(dải cảnh báo dữ liệu cũ)* → vùng ba cột (cột trái 240px · thẻ giữa co giãn · cột phải 392px, đệm ngoài 8px) → thanh dưới 46px.

### Thư viện mẫu ghép
Đầu cột trái không còn là tiêu đề tĩnh mà là **ô chọn mẫu**: mũi tên quay lại 30px + tên mẫu 15px/600 + chevron. Bấm mở menu 268px, bo 8px, có đổ bóng:

- nhãn `MẪU GHÉP TRONG HỒ SƠ NÀY` rồi danh sách mẫu, mỗi mục cao 38px: tên 14px + dòng phụ 12px `{số} dòng · {loại mẫu}`; mẫu đang mở nền `acc-soft`, tên đậm 600, dấu tích `acc` bên phải
- đường ngăn, rồi **Tạo mẫu ghép mới…** (chữ `acc`, icon dấu cộng) · **Đổi tên mẫu này** · **Xoá mẫu này** (chỉ hiện khi hồ sơ có từ hai mẫu)

*Đổi tên* biến tiêu đề thành ô nhập viền dưới 2px `acc`, tự chọn hết chữ; `Enter` lưu, `Esc` bỏ, bấm ra ngoài cũng lưu.

**Hộp thoại tạo mẫu mới** rộng 660px: tiêu đề 20px/600 **Tạo mẫu ghép mới** + dòng phụ *Chọn loại danh sách gần giống của bạn. Tên cột, mẫu câu và câu chữ đều sửa lại được sau.* Thân là lưới hai cột, mỗi thẻ nền `layer2` viền `stroke` bo 6px (rê chuột: viền `acc`, nền `acc-soft`): tên 14.5px/600 + mô tả 13px + dòng cột gợi ý 12.5px `txt3`. Bấm một thẻ là tạo mẫu và mở ngay ở mục *Nguồn dữ liệu*; tên trùng thì thêm ` (2)`. Chân hộp: chú thích *Mẫu mới được thêm vào hồ sơ Danh sách, biểu mẫu — các mẫu đang có không đổi.* + **Huỷ**.

Sáu mẫu sẵn:

| Mẫu | Dùng cho | Cột gợi ý | Dòng mẫu |
|---|---|---|---|
| Danh sách công đức | sổ công đức của chùa, đền, nhà thờ | Tên · Số tiền · Ngày · Đợt · Pháp danh | 248 |
| Quyên góp, ủng hộ | quỹ khuyến học, ủng hộ bão lụt, quỹ lớp | Người ủng hộ · Số tiền · Ngày · Tổ dân phố · Hiện vật | 96 |
| Chi trả, bảng lương | chi trả lương, trợ cấp, tiền hỗ trợ | Họ và tên · Số tiền nhận · Ngày chi trả · Bộ phận · Số quyết định | 64 |
| Khen thưởng, kết quả | học sinh đạt danh hiệu, kết quả thi, trúng tuyển | Họ và tên · Lớp · Điểm trung bình · Danh hiệu · Ngày xét | 132 |
| Lịch trực, phân công | lịch trực cơ quan, phân công theo ngày | Ngày trực · Người trực · Bộ phận · Ca · Điện thoại | 42 |
| Thông báo tìm người, tạm trú | loa phát thanh phường: tìm người, nhắn tin, tạm trú | Họ và tên · Năm sinh · Địa chỉ · Loại thông báo · Số liên hệ | 18 |

Mỗi mẫu sẵn mang theo: tên bảng tính, sáu cột kèm *Dùng làm* + *Cách đọc* đoán trước, mẫu câu, văn bản đầu / xen giữa / cuối, câu đọc tên nhóm, và bốn dòng dữ liệu mẫu để dựng cột xem trước.

### Dải cảnh báo dữ liệu cũ (ẩn/hiện)
Bộ `warn`, nằm ngay dưới thanh tiêu đề: **Chưa lấy được danh sách mới, đang dùng bản đã tải lúc 14:03 hôm nay** + *{số} dòng của bản cũ vẫn đọc và xuất được bình thường. Nếu bảng tính vừa thêm dòng, hãy thử lấy lại trước khi đọc.* + nút chìm **Vẫn dùng bản cũ** và nút viền **Thử lấy lại**. Không lấy được dữ liệu **không bao giờ** làm dừng buổi đọc.

### Cột trái — các phần của bản ghép
Bảy mục, mỗi mục cao tối thiểu 38px: chấm 7px + tên 14px + dòng phụ 12px `txt3`. Chấm `ok` = phần này đang được đọc, chấm rỗng viền `stroke2` = đang tắt, chấm `warn` = mục có chỗ cần xem lại. Mục đang chọn: nền `layer`, viền `stroke`, tên đậm 600, vạch dọc 3×18px `acc` ở `left:2px`.

| Mục | Dòng phụ |
|---|---|
| Nguồn dữ liệu | tên cách lấy đang chọn |
| Khớp cột | `5 cột đang dùng` (thêm ` · cần xem lại` khi có vấn đề) |
| Lọc & nhóm | `bỏ dòng thiếu · gộp trùng · nhóm theo cột`, hoặc *không lọc* |
| Đầu danh sách | `Đang bật · 4 đoạn` / *Đang tắt* |
| Mẫu câu mỗi dòng | `Luôn đọc · 248 dòng` |
| Câu xen giữa | `Sau mỗi 30 dòng` / *Đang tắt* |
| Cuối danh sách | `Đang bật · 4 đoạn` / *Đang tắt* |

Đáy cột, tách bằng `divider`: *Mẫu này thuộc hồ sơ **Danh sách, biểu mẫu**. Các hồ sơ khác không bị ảnh hưởng.* và nút chìm **Trả mẫu về ban đầu** (xoá mọi thay đổi của mọi mẫu).

### Thẻ giữa
Đầu thẻ 52px: tên mục 17px/600 + một dòng giải thích 13px `txt3` (*Nơi lấy danh sách và lúc nào lấy lại* · *Phần mềm tự đoán, bạn sửa lại nếu đoán sai* · *Dòng nào được đọc, đọc theo thứ tự nào* · *Phần động — mỗi dòng bảng tính thành một câu* · *Phần tĩnh — bạn viết một lần, dùng cho mọi lần đọc*). Ba mục tĩnh (Đầu danh sách, Câu xen giữa, Cuối danh sách) có thêm công tắc bên phải: *Đang đọc phần này* / *Đang bỏ qua phần này*.

Đầu thân thẻ, khi có chỗ cần xem lại, là một dải `warn` liệt kê từng vấn đề, kèm nút **Mở Khớp cột** nếu đang không ở mục đó. Năm vấn đề được phát hiện, tính lại theo thiết lập thật:
- mẫu câu đang trống — *các dòng trong bảng tính sẽ không được đọc*
- mẫu câu dùng một biến mà không cột nào cấp dữ liệu, hoặc cột đó đang đặt *Bỏ qua*
- hai cột cùng đặt *Nhóm theo cột này* hoặc cùng đặt *Lọc theo ngày* — nói rõ cột nào được dùng, cột nào bị bỏ
- bật đọc tên nhóm nhưng chưa có cột *Nhóm theo cột này*
- chưa có cột *Lọc theo ngày* nên bộ lọc khoảng ngày bị bỏ qua

**Nguồn dữ liệu.** Ba lựa chọn tròn: *Dán link chia sẻ công khai* (bảng tính phải bật “Bất kỳ ai có đường liên kết đều xem được”) · *Đăng nhập Google* (dùng được cả bảng riêng tư) · *File trên máy* (.xlsx hoặc .csv, không cần mạng). Lựa chọn đang dùng: nền `acc-soft`, viền `acc`, nhãn **Đang dùng**. Dưới đó là ô nhập nguồn (viền dưới 2px `acc`) + nút **Kiểm tra kết nối**, rồi hai ô chọn **Bảng trong tệp** (danh sách theo mẫu) và **Dòng tiêu đề** (Dòng 1 · Dòng 2 · Dòng 3 · Không có dòng tiêu đề).

Nhãn `LẤY DỮ LIỆU MỚI` rồi ba hàng: *Bấm nút để lấy dữ liệu mới* — **Luôn bật** · *Tự kiểm tra định kỳ* — công tắc, `5 phút một lần`, chỉ kiểm tra, không tự đổi giữa lúc đang đọc · *Khi không lấy được* — **Đã chọn**: dùng bản đã tải lần trước và báo rõ dữ liệu ngày nào.

**Khớp cột.** Dải `acc-soft` giải thích: phần mềm đọc dòng tiêu đề và tự đoán cách dùng từng cột; cột nào cũng chèn được vào mẫu câu, trừ cột đặt *Bỏ qua*; **Cách đọc** quyết định máy đọc ô đó thành gì.

Bảng: Cột (38px) · Cột trong sheet (co giãn, hai dòng: tiêu đề 14px/600 + `Ví dụ: …` 12.5px) · Dùng làm (158px) · Cách đọc (168px) · Chèn được (104px). Hai trục độc lập:

- **Dùng làm** — `Dùng trong câu` · `Nhóm theo cột này` · `Lọc theo ngày` · `Bỏ qua`. Mỗi mẫu chỉ dùng được **một** cột nhóm và **một** cột lọc ngày; cột thứ hai cùng vai thì hàng đó nền `warn-bg`, ô chọn viền và chữ `err`, mất chip biến. Cột đặt *Bỏ qua* để nền trong suốt, chữ `txt3`.
- **Cách đọc** — `Nguyên văn` · `Số tiền` · `Ngày tháng` · `Số thứ tự` · `Đọc từng chữ số` · `Tên riêng (đọc chậm)` · `Điểm, số thập phân` · `Viết tắt đọc đầy`. Đây là thứ quyết định cột xem trước: `2.500.000` → “hai triệu năm trăm nghìn đồng”, `0912 345 678` → “không chín một hai ba bốn năm sáu bảy tám”, `9,8` → “chín phẩy tám”, `1958` → “một nghìn chín trăm năm mươi tám”, `QĐ 142/2026` → “quyết định một trăm bốn mươi hai năm hai nghìn không trăm hai mươi sáu”.

Biến sinh từ tiêu đề cột, bỏ dấu và bỏ khoảng trắng: `Số tiền` → `{sotien}`, `Pháp danh` → `{phapdanh}`, `Họ và tên` → `{hovaten}`. Chú thích cuối bảng: *Cột đặt “Bỏ qua” vẫn nằm trong sheet, chỉ là không đọc tới. Mỗi mẫu chỉ có một cột nhóm và một cột lọc ngày.*

Sáu cột của mẫu *Danh sách công đức*: A *Tên* — Dùng trong câu / Tên riêng · B *Số tiền* — Dùng trong câu / Số tiền · C *Ngày* — Lọc theo ngày / Ngày tháng · D *Đợt* — Nhóm theo cột này / Nguyên văn · E *Pháp danh* — Dùng trong câu / Tên riêng · F *Ghi chú* — Bỏ qua.

**Lọc & nhóm.** Ba công tắc kèm ảnh hưởng thật: *Bỏ dòng thiếu dữ liệu* — `4 dòng bị bỏ` · *Gộp dòng trùng* — `2 dòng gộp lại`, mở ra thêm một dòng **So trùng theo cột** (ô chọn chữ cột) và câu *Hai dòng có cùng {tên cột} được coi là một*; mẫu có cột đọc kiểu *Số tiền* thì ghi thêm “số tiền được cộng gộp” · *Giữ đúng thứ tự trong sheet* — `Theo bảng tính`, tắt thì `Số lớn trước`.

Rồi nhãn `KHOẢNG NGÀY` với hai ô ngày 170px (**Từ ngày** / **Đến ngày**) và chú thích *Lấy theo cột {tên cột}. Bỏ trống hai ô này thì đọc toàn bộ danh sách.* — chưa có cột lọc ngày thì chú thích đổi thành *Chưa có cột nào đặt “Lọc theo ngày”, nên bộ lọc này chưa có tác dụng.*

Cuối là nhãn `NHÓM THEO CỘT` với công tắc *Đọc tên nhóm trước mỗi nhóm* — `{số} nhóm`, chú thích ghi cột nhóm và câu sẽ đọc, ví dụ “Đợt cúng dường Rằm tháng Bảy.”

**Bốn mục nội dung** dùng chung một ô soạn: nhãn bên trái, số đếm bên phải (`4 đoạn · 612 ký tự`; mẫu câu đếm ký tự), ô nhập nhiều dòng viền dưới 2px `acc`, chữ 15px dòng cao 1.65, cao tối thiểu 260px (mẫu câu 120px), kéo cao được. Mục tĩnh có chú thích *Cách dòng một lần là ngắt đoạn — phần mềm sẽ nghỉ một nhịp ở đó.*

*Câu xen giữa* có thêm một hàng trên ô soạn: **Đọc câu này sau mỗi** [10 · 20 · 30 · 40 · 50 · 100] **dòng**, bên phải là `Sẽ đọc 8 lần trong 248 dòng`.

*Mẫu câu mỗi dòng* có thêm nhãn `CHÈN DỮ LIỆU TỪ SHEET` và một hàng chip bo 15px: tên biến (chữ đơn cách, đậm 600) + tiêu đề cột; tooltip ghi cột nguồn và cách đọc. Chip đã dùng trong mẫu: nền `acc-soft`, viền và chữ `acc`. Bấm chip chèn biến **vào đúng vị trí con trỏ**. Dưới cùng là chú thích về cách đọc, dẫn sang **Cách đọc** ở mục Khớp cột và **Từ điển phát âm** (màn 5).

### Cột phải — Bản ghép hoàn chỉnh (392px)
Đầu thẻ 44px: **Bản ghép hoàn chỉnh** + `4 khối · 259 đoạn` (mặc định của mẫu công đức; bật *Câu xen giữa* thành `5 khối · 267 đoạn`). Thân cuộn, mỗi khối là một hộp bo 5px với vạch trái 3px: khối lấy từ bảng tính dùng viền và vạch `acc`, nền `acc-soft`; khối tĩnh dùng viền `stroke`, vạch `stroke2`, nền `layer2`. Đầu khối là nhãn 11.5px viết hoa (*Đầu danh sách · tĩnh* · *Tên nhóm · từ Google Sheet* · *Danh sách · từ Google Sheet* — nguồn là tệp trên máy thì ghi *từ tệp trên máy* · *Câu xen giữa · tĩnh* · *Cuối danh sách · tĩnh*) + số đếm bên phải (`4 đoạn`, `248 dòng`, `lặp 8 lần`, `nhóm 1/3`).

Khối danh sách hiện bốn dòng đầu đã đánh số và **đã áp Cách đọc của từng cột** — đây là chỗ người dùng thấy trước máy sẽ đọc thành gì. Biến không có cột cấp dữ liệu hiện thành `(chưa có cột ten)`. Chân thẻ nền `layer2`: *Khối viền xanh là phần lấy từ bảng tính, sẽ tự đổi theo dữ liệu. Khối viền xám là phần bạn viết, không đổi.*

### Thanh dưới (46px)
Chấm trạng thái + nhãn: *Dữ liệu cũ — lấy lúc 14:03 hôm nay · 248 dòng* (chấm `warn`) hoặc *Đã cập nhật 14:58 hôm nay · 248 dòng · tự kiểm tra 5 phút một lần* (chấm `ok`). Rồi nút viền **Lấy dữ liệu mới**. Đẩy sang phải: `259 đoạn · khoảng 39 phút` (ước tính 9 giây mỗi đoạn) và nút accent **Mở bản ghép để nghe** — mở bản ghép thành một tab tệp ở màn hình chính (xem *Tab bản ghép* ở màn hình 1).

### Trạng thái của màn này
Trạng thái chia hai tầng: danh sách mẫu, và thiết lập **riêng của từng mẫu**.

| Tên | Mặc định | Ý nghĩa |
|---|---|---|
| `maus` | 2 mẫu sẵn | danh sách mẫu ghép của hồ sơ (id, mẫu gốc, tên) |
| `mau` | 0 | mẫu đang mở |
| `nav` | 0 | mục đang chọn ở cột trái |
| `docs[id].src` / `.srcVal` | theo mẫu | cách lấy dữ liệu và đường dẫn của từng cách |
| `docs[id].sheet` / `.headRow` | theo mẫu / `Dòng 1` | bảng trong tệp và dòng tiêu đề |
| `docs[id].auto` | true | tự kiểm tra định kỳ |
| `docs[id].roles` | theo mẫu | `{Dùng làm, Cách đọc}` của từng cột |
| `docs[id].rule` / `.dupCol` | cả ba bật / cột đầu | bỏ dòng thiếu, gộp trùng (theo cột nào), giữ thứ tự |
| `docs[id].group` | true | đọc tên nhóm trước mỗi nhóm |
| `docs[id].on` | `dau` bật, `giua` tắt, `cuoi` bật | ba phần tĩnh có được đọc hay không |
| `docs[id].text` | bốn khối của mẫu | nội dung đầu, mẫu câu, câu xen giữa, cuối |
| `docs[id].sauMoi` | `30` | đọc câu xen giữa sau mỗi bao nhiêu dòng |
| `docs[id].dFrom` / `.dTo` | 1/7/2026 – 15/8/2026 | khoảng ngày |
| `stale` | true | đang dùng bản dữ liệu cũ |

Mọi thay đổi được lưu ngay trên máy (khoá `giongviet.ghep.v2`), mở lại vẫn còn; **Trả mẫu về ban đầu** xoá hết.

---

## Trạng thái ứng dụng

| Tên | Kiểu | Mặc định | Ý nghĩa |
|---|---|---|---|
| `profile` | số | 0 | hồ sơ đang chọn |
| `profiles` | mảng | 4 hồ sơ | tên, giọng, tốc độ, cao độ, âm lượng |
| `tabsByProfile` | map | theo bảng hồ sơ | danh sách tệp mở của từng hồ sơ (hiện trong cột trái) |
| `activeByProfile` | map | 0 | tệp đang xem của từng hồ sơ |
| `view` | `san_sang` \| `dang_doc` \| `rong` | `san_sang` | trạng thái vùng đọc |
| `situation` | 7 giá trị | `binh_thuong` | tình huống lỗi / chờ |
| `pos` | số | 1 | đoạn đang đọc |
| `sel` | số | 1 | đoạn đang chọn (con trỏ) |
| `mode` | `all` \| `one` | `all` | nghe liền mạch hay nghe riêng một đoạn |
| `rail` | boolean | false | cột trái thu gọn |
| `menu` | số | −1 | menu trên cùng đang mở |
| `find` | boolean | false | thanh tìm và thay thế |
| `tags` / `voiceOpen` / `tune` | boolean | false | các menu và mục thu gọn |
| `chips` | map | `{A: {11: '[hắng giọng]'}}` | thẻ cảm xúc theo đoạn |
| `exportOpen` / `exporting` / `toast` | boolean | false | ba bước của luồng xuất |
| `theme` | `sang` \| `toi` | `sang` | chế độ màu |
| `gStep` | `signin` \| `list` \| `loading` \| — | — | bước của hộp thoại Google Docs |
| `gSigned` | boolean | false | đã đăng nhập Google |
| `gTab` | số | 0 | 0 = từ Drive, 1 = dán link |
| `gSel` / `gQuery` / `gLink` | số / chữ / chữ | 0 / rỗng / rỗng | tài liệu đang chọn, từ khoá tìm, link đã dán |
| `gPull` / `gAt` | boolean / giờ | false / `14:02` | đang lấy bản mới từ Google Docs, giờ lấy gần nhất |

Chuyển trạng thái:
- bấm nút ▶ của một đoạn → `view = 'dang_doc'`, `mode = 'one'`, `pos = sel = N`; hết đoạn thì `view = 'san_sang'`
- sửa chữ trong một đoạn → cập nhật mảng đoạn của tài liệu đang xem; `Enter`/`Backspace`/`Delete` tách và nối đoạn; đoạn bỏ trống bị gỡ khỏi mảng khi rời khỏi đoạn
- **Nghe toàn bộ** → `view = 'dang_doc'`, `mode = 'all'`, `pos = 1`
- tạm dừng → `view = 'san_sang'` (giữ `pos`); dừng → `view = 'san_sang'`
- đổi hồ sơ hoặc đổi tệp → `view = 'san_sang'`, `pos = sel = 1`
- **Xuất** → `exportOpen` → `exporting` (≈2 giây) → `toast`
- mở một menu → đóng các menu còn lại; bấm ra ngoài → đóng tất cả

## Phím tắt

`Ctrl+V` dán · `Ctrl+O` mở tệp · `Ctrl+S` lưu · `Ctrl+T` tệp mới · `Ctrl+W` đóng tệp · `Ctrl+H` tìm và thay thế · `Ctrl+K` soát văn bản · `Ctrl+E` xuất · `Ctrl+B` thu gọn cột trái · `Ctrl+G` đổi giọng · `Ctrl+M` nghe mẫu giọng · `Space` phát/dừng · `Ctrl+.` dừng hẳn · `Alt+1…3` chèn thẻ cảm xúc · `F1` hướng dẫn · `Ctrl+/` phím tắt

## Bản đồ file

| File | Màn hình |
|---|---|
| `GiongDoc - Màn hình chính v2 (nghe theo dòng).dc.html` | Màn hình chính — **bắt đầu từ đây** |
| `GiongDoc - Soát văn bản.dc.html` | Soát văn bản (2 tab) |
| `GiongDoc - Xuất file âm thanh.dc.html` | Xuất file âm thanh |
| `GiongDoc - Thư viện giọng.dc.html` | Thư viện giọng |
| `GiongDoc - Từ điển phát âm.dc.html` | Từ điển phát âm |
| `GiongDoc - Cài đặt.dc.html` | Cài đặt |
| `GiongDoc - Văn bản ghép.dc.html` | Văn bản ghép — thư viện mẫu ghép từ bảng tính |

Các file liên kết với nhau bằng đường dẫn tương đối — mở file màn hình chính trong trình duyệt là bấm đi lại được giữa các màn. Mọi màn phụ có nút **‹ Màn hình chính** ở thanh tiêu đề.

Màn hình chính có bảng điều khiển bản mẫu phía trên cửa sổ (trạng thái, tình huống, sáng/tối) — đó là công cụ để xem thiết kế, **không phải một phần của sản phẩm**.

---

## Ba điều trông có vẻ thiếu nhưng là cố ý

**1. Đơn vị là đoạn, không phải dòng.** Bản đầu dựng vùng đọc theo dạng bảng mỗi dòng cao cố định và cắt cụt bằng dấu ba chấm. Người dùng không đọc được nội dung nên không biết chỗ nào cần nghe. Đoạn tự xuống dòng giải quyết việc đó.

**2. Không có thanh tua.** Người dùng dò từng chỗ nghi ngờ, không nghe tuyến tính. Thanh tua chỉ tạo cảm giác đây là trình phát nhạc và khiến người ta kéo qua kéo lại vô ích.

**3. Không có mã hoá tệp, kiểu xuống dòng, mức phóng to ở thanh trạng thái.** Đó là ngôn ngữ của trình soạn code. Người dùng của Giọng Việt không cần.
