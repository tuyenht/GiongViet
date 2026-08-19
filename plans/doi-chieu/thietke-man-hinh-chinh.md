# Bản kiểm kê trạng thái — "GiongDoc · Màn hình chính v2 (nghe theo dòng)"

Nguồn: `C:\Projects\DocCongDuc\design_handoff_giongdoc\designs-goc\GiongDoc - Màn hình chính v2 (nghe theo dòng).dc.html`
(kéo từ dự án thiết kế Claude Design, project `5c70b20f-0f8b-4da8-ad19-800b0fb6ae19`, ngày 17/8/2026 —
1.633 dòng / 129.909 byte, LF, không bị cắt).

Bản snapshot cũ trong `design_handoff_giongdoc/designs/` chỉ có 1.155 dòng — **đã lỗi thời**, đừng
dùng làm căn cứ nữa. Xem mục 12 để biết chỗ khác nhau.

Đọc bản kiểm kê này là đủ để dựng lại màn hình, không cần mở lại tệp thiết kế.

---

## 1. Bản mẫu là gì

Tệp `.dc.html` là **bản mẫu tương tác tự chạy được** (framework `DCLogic`, kèm `support.js`).
Phía trên khung cửa sổ giả có ba dải nút để đổi trạng thái. Mỗi trạng thái là **một yêu cầu xử lý
thật**, không phải hình trang trí.

Bản mẫu **ghi nhớ trạng thái vào `localStorage`** với khoá `giongviet.mockup.v1`
(hồ sơ, danh sách tệp, tên tự đặt, nội dung đã sửa, thẻ cảm xúc, hồ sơ đang chọn, `mNew`, `mAt`).
Menu **Trợ giúp → "Đặt lại bản mẫu về ban đầu"** xoá khoá này.

Mở tệp kèm `#banghep` trong URL → tự nhảy sang hồ sơ **"Danh sách, biểu mẫu"** và mở tệp ghép `M`.

---

## 2. Ba dải công tắc (nguyên văn nhãn tiếng Việt)

### 2.1 Dải 1 — trạng thái màn hình (prop `state`, mục "Trạng thái")

| Nhãn hiện ra | Giá trị | Ghi chú |
|---|---|---|
| `Sẵn sàng` | `san_sang` | **mặc định** |
| `Đang đọc` | `dang_doc` | |
| `Chưa có văn bản` | `rong` | |

Dòng chữ mô tả bên trái dải: `Phương án 2 · Văn bản theo đoạn`.
Nút đang chọn: nền `#0067c0`, chữ `#fff`. Nút không chọn: nền trong suốt, chữ `#5d5d5d`.

### 2.2 Dải 2 — giao diện (prop `theme`, mục "Trạng thái")

| Nhãn | Giá trị |
|---|---|
| `Sáng` | `sang` (**mặc định**) |
| `Tối` | `toi` |

Dải này nằm sát lề phải (`margin-left:auto`) cùng hàng với dải 1.

### 2.3 Dải 3 — tình huống (prop `tinhHuong`, mục "Trạng thái")

Hàng riêng bên dưới, nhãn nhóm bên trái: `Tình huống`. Nút bo tròn 14px.

| # | Nhãn | Giá trị |
|---|---|---|
| 1 | `Bình thường` | `binh_thuong` (**mặc định**) |
| 2 | `Đang tạo âm thanh` | `dang_tao` |
| 3 | `Mất kết nối` | `mat_ket_noi` |
| 4 | `Hết lượt` | `het_luot` |
| 5 | `Giọng đang tải` | `giong_dang_tai` |
| 6 | `Văn bản quá dài` | `van_ban_dai` |
| 7 | `Âm thanh cũ` | `am_thanh_cu` |
| 8 | `Đang xuất tệp` | `dang_xuat` |
| 9 | `Vừa xuất xong` | `vua_xuat_xong` |

### 2.4 Công tắc thứ tư — chỉ có trong bảng props, không có nút trên dải

`showEmotionChips` — boolean, mặc định `true`, mục **"Nội dung"**.
Khi `true`: tệp `A` có sẵn thẻ `[hắng giọng]` gắn ở **đoạn 11**. Khi `false`: không có thẻ nào sẵn.

### 2.5 Câu dẫn dưới ba dải (nguyên văn, có chữ in đậm)

> Bản mẫu bấm được như phần mềm thật. Mỗi **hồ sơ đọc** là một chỗ làm việc riêng: đổi hồ sơ thì tệp
> đang mở, nội dung ở giữa, giọng và các chỗ cần chú ý đều đổi theo. Đơn vị là **đoạn** — bấm
> **số đoạn** để nghe riêng đoạn đó, nghe hết đoạn thì dừng.

---

## 3. Cờ dẫn xuất — luật quyết định cái gì hiện, cái gì mất

Đọc kỹ mục này trước khi làm bất kỳ trạng thái nào.

```
isEmpty      = (state === 'rong')  hoặc hồ sơ hiện tại không có tệp nào
hasFile      = !isEmpty
isPlaying    = hasFile && state === 'dang_doc'
isPrep       = tinhHuong === 'dang_tao' && hasFile && !isPlaying
noEngine     = tinhHuong === 'mat_ket_noi'
noQuota      = tinhHuong === 'het_luot'
loadingVoice = tinhHuong === 'giong_dang_tai'
isExporting  = tinhHuong === 'dang_xuat'
blocked      = noEngine || noQuota || loadingVoice        ← chặn nghe/xuất
showBar      = (isPlaying || isPrep) && hasFile           ← dải phát ở đáy
hasBanner    = hasFile && tinhHuong có định nghĩa dải cảnh báo
toastOpen    = tinhHuong === 'vua_xuat_xong' && hasFile && chưa bấm đóng
```

Hệ quả quan trọng:
- **Khi `rong` thì KHÔNG có dải cảnh báo, KHÔNG có toast, KHÔNG có dải phát** — mọi tình huống bị
  vô hiệu hoá hết.
- `dang_tao` chỉ ra dải "đang tạo" khi **không** đang đọc; nếu vừa `dang_doc` vừa `dang_tao` thì
  dải phát hiện dạng "đang đọc".
- `blocked` làm mờ nút và **chặn thao tác thật**: `startPlay` không làm gì.

---

## 4. Bố cục cửa sổ — khung cố định 1440 × 900

Khung ngoài: nền `#e6e6e6`, cửa sổ giả `width:1440px; height:900px`, viền `1px rgba(0,0,0,.22)`,
bo 8px, `box-shadow: 0 16px 32px rgba(0,0,0,.22)`, `overflow:hidden`, xếp dọc (`flex-direction:column`).
Ba dải công tắc bên trên cũng rộng đúng `1440px`, canh giữa.

Font toàn màn hình: `'Segoe UI Variable Text','Segoe UI',Inter,system-ui,sans-serif`, cỡ gốc 14px.

Thứ tự **từ trên xuống** bên trong cửa sổ:

| # | Vùng | Chiều cao | Điều kiện |
|---|---|---|---|
| 1 | Thanh tiêu đề cửa sổ | 32px | luôn có |
| 2 | Thanh menu (6 menu) | 30px, `z-index:46` | luôn có |
| 3 | Thanh công cụ | 44px, `z-index:45` | luôn có |
| 4 | Khoảng đệm trống | **8px** | luôn có (chỗ này **trước đây là dải thẻ tệp**, đã bỏ) |
| 5 | Dải Tìm và thay thế | tự co | khi `findOpen` |
| 6 | Dải cảnh báo | tự co | khi `hasBanner` |
| 7 | Thân ba cột | `flex:1` | luôn có |
| 8 | Dải phát ở đáy | 46px | khi `showBar` |
| 9 | Thanh trạng thái | 28px | luôn có |

Lớp phủ (không chiếm chỗ):
- Màn che đóng menu: `position:absolute; inset:0; z-index:30` — khi `anyMenuOpen`.
- Hộp thoại Google Docs: `z-index:60`, nền che `rgba(0,0,0,.34)`, hộp `width:620px`.
- Toast: `z-index:55`, `right:12px; bottom:40px`, `width:360px`.

### 4.1 Thân ba cột (từ trái sang phải)

| Cột | Bề rộng | Điều kiện |
|---|---|---|
| Trái — **thanh ray hẹp** | `44px` (icon 34×34) | khi `railOpen` (đã thu gọn) |
| Trái — **bảng hồ sơ** | `240px` cố định | khi `panelOpen` (mặc định) |
| Giữa — **vùng văn bản** | `flex:1; min-width:0` | luôn có |
| Phải — **bảng điều khiển** | `300px` cố định | luôn có |

Hai bên trái loại trừ nhau: `railOpen = state.rail`, `panelOpen = !state.rail`.
Cột giữa: nền `var(--layer)`, viền `1px var(--stroke)`, bo 8px, `overflow:hidden`.

---

## 5. Từng vùng — chi tiết đầy đủ

### 5.1 Thanh tiêu đề (32px)

- Logo 16×16, bo 3px, nền `var(--acc)`, trong là SVG 4 vạch sóng màu `var(--acc-txt)`.
- Chữ tiêu đề 12.5px `var(--txt2)`: `{{ windowTitle }}` = **tên tệp đang mở + " — Giọng Việt"**.
  Ví dụ: `thongbao-quoc-khanh.txt — Giọng Việt`.
- Ba nút cửa sổ 46×32 sát phải, tooltip lần lượt: `Thu nhỏ` · `Phóng to` · `Đóng`.
  Nút Đóng khi trỏ vào: nền `var(--close)` (`#c42b1c`), chữ `#fff`.

### 5.2 Thanh menu (30px) — 6 menu, có gạch ngăn

Nhãn menu: `Tệp` · `Chỉnh sửa` · `Chèn` · `Giọng` · `Xem` · `Trợ giúp`.
Menu đang mở: nền `var(--sub-h)`. Dropdown: `top:30px`, `min-width:250px`, nền `var(--layer)`,
viền `var(--stroke2)`, bo 8px, `box-shadow: var(--shadow)`, `z-index:50`.
Toạ độ `left` theo menu: `6px · 49px · 140px · 191px · 250px · 293px`.

Mỗi mục: cao 32px, nhãn bên trái 14px, **phím tắt bên phải** 13px `var(--txt3)`.
Mục **có hành động thật** → chữ `var(--txt)`; mục **chưa nối gì** → chữ `var(--txt3)` (nhạt hơn).
Gạch ngăn: cao 1px, `var(--divider)`, `margin:5px 8px`.

**Tệp**
| Nhãn | Phím | Hành động |
|---|---|---|
| `Mở tệp…` | Ctrl+O | mở tệp phụ của hồ sơ (bảng `ALT`) |
| `Mở từ Google Docs…` | — | mở hộp thoại Google Docs (bước `signin` nếu chưa đăng nhập, `list` nếu đã) |
| `Dán văn bản` | Ctrl+V | mở tệp chính của hồ sơ (bảng `DEF`) |
| `Lưu` | Ctrl+S | chưa nối |
| `Xuất file âm thanh` | Ctrl+E | sang màn `GiongDoc - Xuất file âm thanh.dc.html` |
| `Đóng tệp` | Ctrl+W | chưa nối |
| — gạch ngăn — | | |
| `Ghép danh sách từ Google Sheet…` | — | sang màn `GiongDoc - Văn bản ghép.dc.html` |
| — gạch ngăn — | | |
| `Cài đặt…` | — | sang màn `GiongDoc - Cài đặt.dc.html` |
| `Thoát` | Alt+F4 | chưa nối |

**Chỉnh sửa**: `Hoàn tác` Ctrl+Z · `Làm lại` Ctrl+Y · —gạch— · `Cắt` Ctrl+X · `Sao chép` Ctrl+C ·
`Dán` Ctrl+V (mở tệp chính) · `Chọn tất cả` Ctrl+A · —gạch— · `Tìm và thay thế` Ctrl+H (mở dải tìm) ·
`Soát văn bản` Ctrl+K (sang màn Soát văn bản).

**Chèn**: `Thẻ cảm xúc` Alt+1…3 (mở dropdown thẻ) · `Khoảng lặng 1 giây` Alt+S · `Ngắt đoạn` Enter ·
—gạch— · `Thêm cách đọc cho từ đang chọn…` (sang màn Từ điển phát âm).

**Giọng**: `Đổi giọng đọc` Ctrl+G (mở dropdown giọng) · `Nghe mẫu giọng` Ctrl+M · —gạch— ·
`Thư viện giọng` · `Nhân bản giọng từ file…` (`…Thư viện giọng.dc.html?nhanban=1`) ·
`Thu âm để tạo giọng mới…` (`…?thuam=1`) · —gạch— · `Từ điển phát âm`.

**Xem**: `Thu gọn danh sách hồ sơ` Ctrl+B (bật/tắt thanh ray) · `Cỡ chữ lớn hơn` Ctrl+= ·
`Cỡ chữ nhỏ hơn` Ctrl+- · —gạch— · `Toàn màn hình` F11 · `Giao diện tối` (đảo giao diện).

**Trợ giúp**: `Hướng dẫn nhanh` F1 · `Danh sách phím tắt` Ctrl+/ · `Giới thiệu Giọng Việt` ·
—gạch— · `Kiểm tra bản cập nhật` · `Gửi phản hồi cho nhà phát triển` · —gạch— ·
`Đặt lại bản mẫu về ban đầu` (xoá `localStorage`, về mặc định).

### 5.3 Thanh công cụ (44px)

**Bên trái:**
1. `Dán văn bản` — tooltip `Dán văn bản từ clipboard (Ctrl+V)`.
2. `Mở file` — tooltip `Mở tệp văn bản (Ctrl+O)`.
3. Gạch dọc `1 × 22px`, màu `var(--stroke2)`, `margin: 0 10px`.
4. `Soát văn bản` (là thẻ `<a>` sang màn Soát văn bản) — tooltip
   `Xem các chỗ dễ đọc sai và văn bản sau chuẩn hoá (Ctrl+K)`.
5. `Thẻ cảm xúc` + mũi chỉ xuống — tooltip `Chèn thẻ cảm xúc vào đoạn đang chọn`.

Ba nút 4–5 và "Tìm và thay thế" dùng màu `{{ toolFg }}`: `var(--dis)` khi `rong`, còn lại `var(--txt)`.

**Bên phải (`margin-left:auto`):**
6. `Tìm và thay thế` — tooltip `Tìm một từ trong văn bản và thay bằng từ khác (Ctrl+H)`.
   Khi đang mở: nền `var(--sub-h)`.
7. **Chỉ khi `hasFile`:** gạch dọc `1 × 22px` `var(--stroke2)`, rồi:
   - `Nghe toàn bộ` (34px, nền `var(--ctl)`, viền `var(--stroke2)`, icon ▶) —
     tooltip `Nghe liền mạch toàn bộ văn bản từ đầu (Space)`.
     Chữ mờ `var(--dis)` khi `blocked`; bấm lúc đó **không có tác dụng**.
   - `Xuất file âm thanh` — **là thẻ `<a>`** sang `GiongDoc - Xuất file âm thanh.dc.html`,
     cao 34px, chữ đậm 600, tooltip `Mở hộp thoại xuất để chọn định dạng và nơi lưu (Ctrl+E)`.
     Bình thường: nền/viền `var(--acc)`, chữ `var(--acc-txt)`.
     Khi `blocked`: nền `var(--ctl)`, viền `var(--stroke2)`, chữ `var(--dis)`.

**Dropdown "Thẻ cảm xúc"** (`top:38px; left:0; width:260px; z-index:40`):
- Dòng đầu 12.5px `var(--txt3)`: `Chèn vào đoạn {{ selLabel }}` (số đoạn đang chọn).
- Ba mục, mỗi mục là một chip + phím tắt bên phải:
  `[cười]` — `Alt+1` · `[thở dài]` — `Alt+2` · `[hắng giọng]` — `Alt+3`.
  Chip: 13.5px/600, nền `var(--chip-bg)`, viền `var(--chip-bd)`, chữ `var(--chip-fg)`, bo 4px.
- Gạch ngăn, rồi mục cuối: `Gỡ thẻ khỏi đoạn này`.

### 5.4 Dải Tìm và thay thế (chỉ khi `findOpen`)

Hàng ngang trong khung `var(--layer)`, viền `var(--stroke2)`, bo 6px, `margin: 0 8px 8px`:
`Tìm` → ô 180px chứa **`17h00`** kèm con trỏ nháy (animation `caret 1.1s step-end infinite`,
viền dưới 2px `var(--acc)`) → `1/1` → gạch dọc → `Thay bằng` → ô 180px chứa **`17 giờ`** →
nút `Thay thế` → nút `Thay tất cả` → nút X sát phải (tooltip `Đóng`).

Hai ô nhập là **tĩnh trong bản mẫu** (nội dung viết cứng), chỉ nút X có hành động.

### 5.5 Dải cảnh báo (chỉ khi `hasFile` và tình huống có định nghĩa)

Khung `margin: 0 8px 8px`, `padding: 11px 13px`, bo 6px. Icon 18px bên trái, tiêu đề 14px/600
`var(--txt)`, nội dung 13.5px `var(--txt2)`, các nút sát phải.

Tông màu:
- **err** (`mat_ket_noi`, `het_luot`): nền `var(--err-bg)`, viền `var(--err-bd)`, icon `var(--err)`.
- **warn** (`giong_dang_tai`, `van_ban_dai`, `am_thanh_cu`): nền `var(--warn-bg)`,
  viền `var(--warn-bd)`, icon `var(--warn)`.

Nút phụ (`bnAlt`) là nút phẳng, không viền. Nút chính (`bnAction`) có nền `var(--ctl)` + viền
`var(--stroke2)`. Không có nút nào thì phần đó không hiện.

**Bảng 5 dải cảnh báo — nguyên văn:**

| Tình huống | Tiêu đề | Nội dung | Nút chính → làm gì | Nút phụ → làm gì |
|---|---|---|---|---|
| `mat_ket_noi` | `Không kết nối được máy chủ đọc` | `Văn bản của bạn vẫn được giữ nguyên. Kiểm tra lại mạng rồi thử lại.` | `Thử lại` → về `Bình thường` | (không) |
| `het_luot` | `Đã dùng hết dung lượng gói tháng này` | `Bạn đã đọc 100.000/100.000 ký tự. Gói làm mới sau 12 ngày, hoặc nâng gói để dùng tiếp ngay.` | `Nâng gói` → về `Bình thường` | `Xem chi tiết` → về `Bình thường` |
| `giong_dang_tai` | `Đang tải giọng ` + **tên giọng của hồ sơ** + ` về máy` | `Còn khoảng 1 phút nữa. Bạn vẫn soạn và sửa văn bản được, chưa nghe được.` | (không) | `Dùng giọng khác` → mở dropdown giọng |
| `van_ban_dai` | `Văn bản dài hơn giới hạn một lần xuất` | `12.400 ký tự, giới hạn 10.000. Khi xuất, phần mềm sẽ cắt thành 2 tệp, cắt ở ranh giới đoạn.` | `Xem chỗ cắt` → chọn **đoạn 9** và về `Bình thường` | (không) |
| `am_thanh_cu` | `Bạn vừa sửa văn bản, bản đã nghe là bản cũ` | `3 đoạn đã đổi: đoạn 4, 9 và 10. Nghe lại hoặc xuất lại để lấy bản mới.` | `Nghe lại 3 đoạn` → về `Bình thường` + chuyển `Đang đọc` từ **đoạn 4**, chế độ đọc liền | (không) |

`binh_thuong`, `dang_xuat`, `vua_xuat_xong` **không có dải cảnh báo**.

### 5.6 Cột trái — thanh ray hẹp (44px, khi đã thu gọn)

Từ trên xuống: nút hamburger 32×32 (tooltip `Mở rộng danh sách hồ sơ`) → các icon hồ sơ 34×34
(icon riêng từng hồ sơ, tooltip = `{{ p.title }}`; hồ sơ đang chọn: nền `var(--acc-soft)`,
màu `var(--acc)`) → đẩy xuống đáy: icon `Thư viện giọng`, icon `Cài đặt`.

**Lưu ý:** thanh ray hẹp **không có** lối vào `Văn bản ghép` — chỉ bảng 240px mới có.

### 5.7 Cột trái — bảng hồ sơ (240px, mặc định)

**Hàng đầu (38px):** hamburger 32×32 (tooltip `Thu gọn danh sách hồ sơ`) + tiêu đề `Hồ sơ đọc` (14px/600).

**Danh sách cuộn** (`flex:1; overflow-y:auto`, `gap:7px`, thanh cuộn mảnh — chỉ hiện màu
`var(--stroke2)` khi trỏ vào vùng này).

Mỗi **hàng hồ sơ**: `padding: 7px 6px 7px 11px`, bo 5px.
Hồ sơ đang chọn: nền `var(--layer)`, viền `var(--stroke)`, tên đậm 600.
Hồ sơ khác: nền trong suốt, viền trong suốt, hover `var(--sub-h)`, tên 400.
Tooltip mỗi hàng: `{tên} — {giọng} · {N} tệp · nháy đúp để đổi tên`.

Nội dung hàng:
- Dòng 1: **tên hồ sơ** (14px, cắt bằng `…` nếu dài).
- Dòng 2: **tên giọng** (12px `var(--txt3)`). Nếu là giọng tự nhân bản → có icon người 12px
  phía trước, tooltip `Giọng bạn tự nhân bản`.
- Dòng 3 — **chỉ khi hồ sơ đang thu** (không phải hồ sơ đang chọn): icon tệp 11px + **tên tệp đang
  mở của hồ sơ đó** (tooltip = chính tên tệp).
- Bên phải — **chỉ khi hồ sơ đang thu**: đốm đỏ 6px `var(--err)` nếu hồ sơ có tệp còn lỗi
  (tooltip `Hồ sơ này có tệp đang có lỗi nên sửa trước khi xuất`), rồi chữ `{{ N }} tệp`.
- Nút **X xoá hồ sơ** 20×20 — chỉ hiện khi còn nhiều hơn 1 hồ sơ, tooltip `Xoá hồ sơ này`,
  hover đổi màu `var(--err)`.

**Đổi tên hồ sơ:** nháy đúp vào hàng → ô nhập thay chỗ tên, viền `1px var(--acc)`, chữ 600/14px,
tự chọn hết chữ. `Enter` lưu (để trống thì giữ tên cũ), `Escape` bỏ, rời khỏi ô cũng lưu.

**Danh sách tệp lồng bên trong** — chỉ hiện với hồ sơ đang chọn:
- Mỗi tệp: cao 30px, `margin-left:9px`, viền trái 2px — `var(--acc)` nếu là tệp đang mở, trong suốt
  nếu không. Nền tệp đang mở `var(--ctl-h)`, icon `var(--acc)`, chữ 13px/600 `var(--txt)`;
  tệp khác chữ `var(--txt2)`/400, icon `var(--txt3)`. Tooltip `{tên tệp} · nháy đúp để đổi tên`.
- Nút X 18×18 cuối hàng, tooltip `Đóng tệp`.
- Nháy đúp → đổi tên tại chỗ (ô nhập 22px, viền `var(--acc)`, Enter lưu / Escape bỏ).
- Hàng cuối: `Thêm tệp` (icon dấu +, cao 28px, chữ 12.5px `var(--txt3)`) —
  tooltip `Mở thêm một tệp trong hồ sơ này`. Bấm → thêm một tệp trống và chuyển sang nó.
  Tệp trống được đặt tên tự động `Văn bản mới 1`, `Văn bản mới 2`, …

**Cuối danh sách cuộn:** `Tạo hồ sơ mới` (cao 34px, icon +, tooltip `Tạo hồ sơ đọc mới`).
Bấm → thêm hồ sơ tên `Hồ sơ mới {N+1}` với giọng `Giọng Ngọc Linh`, tốc độ/cao độ 0, âm lượng 100,
chọn luôn hồ sơ đó và **vào ngay chế độ đổi tên**.

**Khối chân bảng** (`margin-top:8px`, viền trên `1px var(--divider)`), ba lối đi, mỗi cái cao 36px:
| Nhãn | Đi tới | Tooltip |
|---|---|---|
| `Thư viện giọng` | `GiongDoc - Thư viện giọng.dc.html` | (không) |
| `Văn bản ghép` | `GiongDoc - Văn bản ghép.dc.html` | `Ghép phần tĩnh với danh sách từ Google Sheet` |
| `Cài đặt` | `GiongDoc - Cài đặt.dc.html` | (không) |

### 5.8 Cột giữa — hàng đầu vùng văn bản (38px)

Thứ tự từ trái sang phải, `gap:10px`, `padding: 0 16px`, viền dưới `1px var(--divider)`:

1. Icon tệp 14px `var(--txt3)`.
2. **`{{ curFileName }}`** — tên tệp đang mở, 14px/600, `max-width:340px`, cắt `…`.
3. Gạch dọc `1 × 16px` `var(--stroke2)`.
4. **`{{ docMeta }}`** — 13.5px `var(--txt2)`, chữ số đều cột:
   - khi `rong`: `Chưa có văn bản`
   - còn lại: `{số từ} từ · {số đoạn} đoạn · khoảng {thời lượng}`
     Thời lượng ước = tổng của `max(1, round(độ dài đoạn / 11))` giây; dưới 60 giây thì ghi
     `{N} giây`, từ 60 trở lên ghi `{M} phút {S} giây`.
5. **Chip Google Docs** — chỉ khi tệp đang mở là tệp Google Docs (`G`, `G2`, `G3`).
   Viên bo 11px, cao 22px, nền `var(--acc-soft)`, viền `var(--acc)`, chữ `var(--acc)` 12px,
   hover đảo thành nền `var(--acc)` chữ `var(--acc-txt)`. Có icon vòng làm mới.
   - Nhãn thường: `Google Docs · lấy lúc {HH:MM}` (mặc định `14:02`).
   - Đang lấy: `Đang lấy bản mới từ Google Docs…`, icon quay (`spin .8s linear infinite`).
   - Tooltip thường: `Tệp này lấy từ Google Docs lúc {HH:MM} — bấm để lấy bản mới nhất`.
   - Tooltip khi đang lấy: `Đang tải bản mới nhất từ Drive`.
   - Bấm → quay **1.400 ms** rồi cập nhật giờ thành giờ hệ thống hiện tại.
6. **Chip bản ghép** — chỉ khi tệp đang mở là tệp ghép (`M`). Cùng kích cỡ chip trên.
   - Nhãn thường: `Bản ghép · {248 + số dòng mới} dòng` và nếu có dòng mới thì thêm
     ` · +{số dòng mới} mới`.
   - Đang lấy: `Đang lấy dữ liệu mới…` + icon quay.
   - Màu khi **chưa** có dòng mới: nền `var(--acc-soft)`, viền `var(--acc)`, chữ `var(--acc)`.
     Khi **đã có** dòng mới: nền `var(--warn-bg)`, viền `var(--warn-bd)`, chữ `var(--warn)`.
   - Tooltip khi đang lấy:
     `Đang lấy danh sách mới — đoạn đang đọc và đoạn đã đọc không bị đổi`
   - Tooltip khi đã có dòng mới:
     `{N} dòng mới thuộc chỗ đã đọc qua nên được dồn xuống cuối danh sách · lấy lúc {HH:MM} · bấm để lấy dữ liệu mới` (giờ mặc định `15:12`)
   - Tooltip khi chưa có dòng mới:
     `Lấy lúc {HH:MM} · bản mẫu hiển thị mười dòng đầu · bấm để lấy dữ liệu mới` (giờ mặc định `14:58`)
   - Bấm → quay **1.300 ms**, rồi chèn thêm vào **trước khối đoạn kết** một câu dẫn
     `Sau đây là danh sách bổ sung.` (chỉ chèn nếu chưa có) và **3 dòng mới**:
     - `Ông Đỗ Văn Tám, phát tâm công đức số tiền một triệu đồng.`
     - `Gia đình chị Vũ Thanh Thuý, phát tâm công đức số tiền tám trăm nghìn đồng.`
     - `Phật tử Hoàng Văn Minh, phát tâm công đức số tiền hai trăm nghìn đồng.`
     Sau đó số dòng mới tăng 3, giờ lấy đặt thành `15:12`.
7. **Liên kết `Mẫu ghép ›`** — chỉ khi tệp ghép; 12.5px `var(--acc)`, sang màn
   `GiongDoc - Văn bản ghép.dc.html`, tooltip
   `Mở mẫu ghép để sửa mẫu câu, nguồn dữ liệu và cách đọc từng cột`.
8. **`{{ headerHint }}`** — 12.5px `var(--txt3)`, canh phải, chiếm hết chỗ còn lại, cắt `…`:
   - khi `rong`: chuỗi rỗng
   - tệp ghép: `Vạch xanh: từ bảng tính`
   - còn lại: `Bấm vào chữ để sửa như Notepad · nút ▶ bên phải để nghe riêng đoạn`

### 5.9 Cột giữa — trạng thái RỖNG (`isEmpty`)

Khung nét đứt `1.5px dashed var(--stroke2)`, bo 8px, `width:500px`, canh giữa, nền `var(--layer2)`,
`padding: 44px 32px`, chữ canh giữa:

- Icon clipboard 52px, `var(--txt3)`, `opacity:.75`.
- Tiêu đề 18px/600: **`Dán văn bản vào đây để bắt đầu`**
- Chú thích 14px `var(--txt2)`, hai dòng:
  `Nhấn Ctrl+V, hoặc kéo thả tệp .txt, .docx, .rtf vào cửa sổ này.`
  `Hồ sơ đang chọn: {tên hồ sơ} — {tên giọng}.` (tên hồ sơ in đậm)
- Ba nút cùng hàng:
  1. `Dán văn bản` — nền `var(--acc)`, chữ `var(--acc-txt)`, đậm 600 → mở tệp chính của hồ sơ.
  2. `Chọn tệp từ máy…` — nền `var(--ctl)`, viền `var(--stroke2)` → mở tệp phụ của hồ sơ.
  3. `Mở từ Google Docs…` — cùng kiểu nút 2, tooltip
     `Chọn một tài liệu Google Docs trên Drive` → mở hộp thoại Google Docs.

### 5.10 Cột giữa — danh sách đoạn (`hasFile`)

Vùng cuộn dọc, `padding: 8px 10px 8px 8px`. **Thanh cuộn trong suốt cho tới khi trỏ chuột vào
vùng văn bản** thì chuyển sang `var(--rail)`.

Mỗi đoạn có hai dạng:

**a) Đoạn trắng** (`k === 'blank'`): hàng cao tối thiểu 24px — số đoạn 34px canh phải
(12.5px `var(--txt3)`) + ô chữ sửa được rỗng, 16px.

**b) Đoạn có chữ:** hàng `padding: 7px 8px`, bo 6px, ba phần:

1. **Máng số đoạn** (30px, canh phải, `padding-right:12px`): số đoạn, chữ số đều cột.
   Khi đoạn này đang được tạo âm thanh (`isPrep` và trùng vị trí) → có **vòng xoay 11px**
   (`spin .8s linear infinite`) đứng trước số.
   Màu số: `var(--acc)` + đậm 700 khi là đoạn hiện tại; `var(--dis)` khi đã đọc qua;
   `var(--txt3)` các trường hợp khác.
2. **Chip thẻ cảm xúc** (nếu đoạn có thẻ): 12.5px/600, nền `var(--chip-bg)`, viền `var(--chip-bd)`,
   chữ `var(--chip-fg)`. Tooltip `Bấm để gỡ thẻ cảm xúc`. Hover → viền + chữ đổi `var(--err)`.
   Bấm → gỡ thẻ.
3. **Ô chữ sửa trực tiếp** (`contentEditable="plaintext-only"`, tắt soát chính tả):
   - Tiêu đề (`k === 'head'`): 20px, đậm 700, `letter-spacing:.01em`.
   - Thân bài: 18px, `letter-spacing:normal`, `line-height:1.55`.
   - Màu: đã đọc qua → `var(--dis)`; đoạn hiện tại → `var(--txt)` + đậm 600;
     tiêu đề → `var(--txt)`; còn lại → `var(--txt2)`.
4. **Nút nghe riêng đoạn** (máng 30px bên phải): ô vuông 26×26, bo 4px, icon ▶ 12px.
   Tooltip: `Nghe riêng đoạn này, nghe hết đoạn thì dừng`.
   **Chỉ hiện (`opacity:1`)** khi là đoạn hiện tại hoặc khi chuột đang trỏ vào đúng đoạn đó;
   ngoài ra `opacity:0` (chuyển mượt 0.12s).
   Đoạn hiện tại: viền `var(--acc)`, nền `var(--acc-soft)`, icon `var(--acc)`.
   Bấm → chuyển sang `Đang đọc`, chế độ **nghe riêng một đoạn**, đúng đoạn đó.

**Nền và vạch chỉ dấu của hàng đoạn:**
| Tình huống | Nền | Vạch trái (`box-shadow inset`) |
|---|---|---|
| Đoạn đang đọc / đang tạo | `var(--hl)` | `3px 0 0 var(--acc)` |
| Đoạn đang chọn (không đọc) | `var(--sel)` | `3px 0 0 var(--acc)` |
| Đoạn do bảng tính sinh ra | trong suốt | `2px 0 0 var(--acc)` (**vạch xanh mảnh hơn**) |
| Còn lại | trong suốt | không có |

Hover: đoạn đang đọc giữ `var(--hl)`, đoạn khác đổi `var(--sub-h)`.

**Đoạn động (từ bảng tính, `dyn`):**
- **`contentEditable = false`** — không sửa trực tiếp được.
- Khi đoạn động đang được chọn → hiện **khối gợi ý ngay dưới đoạn** (`margin: 2px 0 6px 50px`,
  nền `var(--acc-soft)`, bo 5px, 13px): icon chữ i + câu
  **`Đoạn này do bảng tính sinh ra, không sửa trực tiếp ở đây.`** + liên kết đậm
  **`Sửa mẫu câu ›`** sang `GiongDoc - Văn bản ghép.dc.html`.

**Phím khi đang sửa chữ trong đoạn:**
| Phím | Hành vi |
|---|---|
| `Enter` (không Shift) | Tách đoạn **ngay tại con trỏ**; nửa sau thành đoạn `body` mới; chọn và đặt con trỏ đầu đoạn mới |
| `Shift+Enter` | Không can thiệp |
| `Backspace` ở đầu đoạn, khi đoạn **có thẻ** | Gỡ thẻ cảm xúc (chưa nối đoạn) |
| `Backspace` ở đầu đoạn, không có thẻ, không phải đoạn đầu | Nối vào cuối đoạn trước; con trỏ đặt tại chỗ ghép |
| `Delete` ở cuối đoạn, không phải đoạn cuối | Nối đoạn sau vào; con trỏ giữ tại chỗ ghép |
| Rời khỏi ô (blur) | Xoá các đoạn rỗng, trừ đoạn đang giữ con trỏ; nếu xoá hết thì để lại 1 đoạn rỗng |

### 5.11 Cột phải (300px) — thẻ 1: hồ sơ, giọng, điều chỉnh

Khung `var(--layer)`, viền `var(--stroke)`, bo 8px. Ba tầng cách nhau bằng gạch `1px var(--divider)`.

**Tầng 1 — hồ sơ đang dùng:**
- Nhãn nhỏ in hoa 12px/600 `var(--txt3)`, `letter-spacing:.04em`: `HỒ SƠ ĐANG DÙNG`
  (viết trong nguồn là `Hồ sơ đang dùng`, hoa hoá bằng `text-transform:uppercase`).
- Bên dưới: tên hồ sơ 14px/600, cắt `…`.

**Tầng 2 — giọng đọc:**
- Nhãn in hoa: `GIỌNG ĐỌC` (nguồn: `Giọng đọc`).
- Hàng gồm: ô chọn giọng (cao 36px, `flex:1`, viền `var(--stroke2)`, nền `var(--ctl)`) —
  icon micro + **icon người 13px nếu là giọng tự nhân bản** (tooltip `Giọng bạn tự nhân bản`) +
  tên giọng + mũi chỉ xuống. Bên cạnh: nút loa 36×36, tooltip `Nghe mẫu giọng này (5 giây)`.
- Khi bấm nghe mẫu → hiện dòng có đốm nhấp nháy (`pulse 1.2s`):
  **`Đang phát mẫu {tên giọng}…`** — tự tắt sau **2.600 ms**.
- **Khi tình huống `Giọng đang tải`** (và không `rong`) → hiện khối tiến độ:
  hàng chữ 13px `Đang tải giọng về máy…` bên trái, `62%` bên phải; thanh 4px:
  nền `var(--rail)` `opacity:.45`, phần đã tải `62%` màu `var(--acc)`.
- **Dropdown chọn giọng** (`z-index:40`, phủ xuống dưới ô chọn, nền `var(--layer)`,
  viền `var(--stroke2)`, bo 8px, `box-shadow: var(--shadow)`):
  - Nhóm 1, nhãn in hoa `GIỌNG CÓ SẴN` (nguồn: `Giọng có sẵn`):
    | Tên | Chú thích |
    |---|---|
    | `Giọng Bình An` | `Nữ · Bắc` |
    | `Giọng Ngọc Linh` | `Nữ · Nam` |
    | `Giọng Xuân Vĩnh` | `Nam · Trung` |
  - Gạch ngăn.
  - Nhóm 2, nhãn in hoa `GIỌNG CỦA TÔI` (nguồn: `Giọng của tôi`):
    | Tên | Chú thích |
    |---|---|
    | `Giọng bác Tuấn` | `Nam · 62 tuổi` |
    | `Giọng của tôi (thử)` | `mẫu 30 giây` |
  - Mỗi hàng cao 34px: chỗ dấu ✓ 14px `var(--acc)` (chỉ giọng đang chọn có), tên, chú thích
    12px `var(--txt3)`, nút ▶ 24×24 nghe mẫu (tooltip `Nghe mẫu`).
    Giọng đang chọn: nền `var(--acc-soft)`.
  - Gạch ngăn, rồi mục cuối cao 36px, chữ `var(--acc)` đậm 600:
    **`Nhân bản giọng từ file…`** → `GiongDoc - Thư viện giọng.dc.html?nhanban=1`,
    tooltip `Tải lên 30 giây ghi âm để tạo giọng riêng`.

**Tầng 3 — điều chỉnh (gập/mở được):**
- Hàng tiêu đề bấm được: nhãn in hoa `ĐIỀU CHỈNH` (nguồn: `Điều chỉnh`) + mũi chỉ xuống;
  khi mở thì mũi quay `180deg`.
- **Khi gập** (mặc định): một dòng 13.5px `var(--txt2)` là `{{ tuneSummary }}`:
  - nếu cả ba thông số đều mặc định → **`Theo mặc định của hồ sơ`**
  - nếu có thông số lệch → ghép bằng ` · ` theo thứ tự
    `Tốc độ {±N%}` · `Cao độ {±N}` · `Âm lượng {N%}` (chỉ hiện phần lệch).
- **Khi mở:** ba thanh trượt, mỗi thanh gồm nhãn bên trái + giá trị đậm bên phải, rãnh 4px
  (`var(--rail)` mờ `.5`), phần đã chạy `var(--acc)`, núm 20×20 bo tròn có tâm 11px `var(--acc)`.
  Bấm vào bất cứ đâu trên rãnh là đặt giá trị theo vị trí bấm.

  | Nhãn | Khoảng | Tooltip |
  |---|---|---|
  | `Tốc độ` | −50% … +100% | `Từ -50% đến +100%` |
  | `Cao độ` | −12 … +12 | `Từ -12 đến +12 nửa cung` |
  | `Âm lượng` | 0% … 100% | `Từ 0% đến 100%` |

  Dưới cùng: `Đặt lại mặc định` (cao 30px) → tốc độ 0, cao độ 0, âm lượng 100.

### 5.12 Cột phải — thẻ 2: "Cần chú ý" (chỉ khi `hasFile`)

Khung `var(--layer)`, viền `var(--stroke)`, bo 8px, `padding: 12px 13px 13px`.
- Nhãn in hoa: `CẦN CHÚ Ý` (nguồn: `Cần chú ý`).
- Câu dẫn `{{ auditLead }}` — 13.5px `var(--txt2)`, thay đổi theo tệp (xem mục 7).
- Danh sách hàng, mỗi hàng cao 31px, bấm được:
  đốm 7px màu tông (`var(--err)` nếu là lỗi phải sửa, `var(--dis)` nếu chỉ là chú ý) +
  nhãn nhóm + **số đếm** trong viên bo (lỗi: chữ `var(--err)` nền `var(--err-bg)`;
  thường: chữ `var(--txt2)` nền `var(--chip-bg)`).
  Tooltip mỗi hàng = ví dụ cụ thể của nhóm đó. Bấm → nhảy chọn đúng đoạn tương ứng.
  Hàng trỏ tới đoạn đang chọn có nền `var(--sub-h)`.
- Nút `Soát văn bản` (cao 34px, nền `var(--ctl)`, viền `var(--stroke2)`) →
  `GiongDoc - Soát văn bản.dc.html`, tooltip `Mở màn hình soát văn bản`.
- Liên kết cuối `Từ điển phát âm` + mũi chỉ phải, chữ `var(--acc)` →
  `GiongDoc - Từ điển phát âm.dc.html`, tooltip `Ghi cách đọc riêng cho từ ngữ của bạn`.

### 5.13 Dải phát ở đáy (46px, chỉ khi `showBar`)

Viền trên `1px var(--divider)`, nền `var(--bg)`.

**a) Khi `Đang tạo âm thanh` (và không đang đọc):**
- Vòng xoay 18px (`spin .8s linear infinite`).
- Chữ đậm 14px: **`Đang tạo âm thanh cho đoạn {số đoạn}`**
- Chữ 13px `var(--txt2)`: **`Thường mất 5–10 giây cho mỗi đoạn`** (chú ý là gạch ngang dài `–`)
- Sát phải: nút `Huỷ` (cao 30px) → về `Bình thường`.

**b) Khi `Đang đọc`:**
- Nút tạm dừng 32×32, nền `var(--acc)`, icon hai vạch — tooltip `Tạm dừng (Space)` → về `Sẵn sàng`.
- Nút dừng 32×32, phẳng, icon ô vuông — tooltip `Dừng (Ctrl+.)` → về `Sẵn sàng`.
- Chữ đậm 14px `{{ playLabel }}`:
  - chế độ nghe riêng một đoạn: **`Đang nghe riêng đoạn {N}`**
  - chế độ đọc liền: **`Đang đọc đoạn {N}/{tổng}`**
- Chữ 13px `{{ timeLabel }}` dạng `mm:ss / mm:ss`:
  - nghe riêng: 40% thời lượng đoạn / thời lượng đoạn
  - đọc liền: (vị trí/tổng × tổng thời lượng) / tổng thời lượng
- Thanh tiến độ 150 × 3px, nền `var(--rail)` mờ `.45`, phần đã chạy `var(--acc)`:
  - nghe riêng: cố định `40%`
  - đọc liền: `round(vị trí / tổng × 100)%`
- Chữ 13px `var(--txt3)` `{{ playHint }}`:
  - nghe riêng: **`Nghe hết đoạn này sẽ dừng`**
  - đọc liền: **`Đang chuẩn bị đoạn tiếp theo…`**

### 5.14 Thanh trạng thái (28px)

Nền `var(--layer2)`, viền trên `1px var(--divider)`, chữ 12px `var(--txt2)`.

- **Bên trái** `{{ statusCaret }}`:
  - khi `rong`: `Chưa có văn bản`
  - còn lại: `Đoạn {N}, Cột 1` — `N` là đoạn đang đọc khi đang đọc, còn lại là đoạn đang chọn.
- **Bên phải**, hai phần cách nhau bằng gạch dọc `1 × 12px`:
  1. Đốm 7px + `{{ engineLabel }}`:
     | Tình huống | Nhãn | Màu đốm |
     |---|---|---|
     | `Đang xuất tệp` | `Đang xuất tệp âm thanh · 34%` | `var(--acc)` |
     | `Mất kết nối` | `VieNeu v3 Turbo · mất kết nối` | `var(--err)` |
     | `Hết lượt` | `VieNeu v3 Turbo · hết lượt tháng này` | `var(--warn)` |
     | `Giọng đang tải` | `Đang tải {tên giọng} · 62%` | `var(--warn)` |
     | `Đang tạo âm thanh` | `VieNeu v3 Turbo · đang tạo âm thanh` | `var(--acc)` |
     | còn lại | `VieNeu v3 Turbo · sẵn sàng` | `var(--ok)` |
  2. `{{ statusRight }}`:
     - khi `rong`: `Hồ sơ: {tên hồ sơ}`
     - còn lại: `Đã lưu 14:02 · Hồ sơ: {tên hồ sơ}`

---

## 6. Hai lớp phủ nhiều bước

### 6.1 Hộp thoại "Mở tài liệu Google Docs" (3 bước)

Nền che `rgba(0,0,0,.34)`, hộp `width:620px`, bo 8px, `box-shadow: 0 32px 64px rgba(0,0,0,.32)`.
Mở bằng: menu **Tệp → `Mở từ Google Docs…`**, hoặc nút `Mở từ Google Docs…` ở trạng thái rỗng.

**Đầu hộp** (viền dưới `1px var(--divider)`):
- Tiêu đề 18px/600: **`Mở tài liệu Google Docs`**
- Phụ đề 13px `var(--txt3)` `{{ gSub }}`:
  | Bước | Phụ đề |
  |---|---|
  | `signin` | `Cần đăng nhập Google một lần để đọc danh sách tài liệu` |
  | `list` | `Chọn một tài liệu, nội dung sẽ được mở ra như tệp văn bản thường` |
  | `loading` | `Đang lấy nội dung về máy` |
- Nút X 28×28 sát phải, tooltip `Đóng`.

**Bước 1 — `signin`** (chỉ khi chưa đăng nhập), canh giữa, `gap:14px`:
- Vòng tròn 46px nền `var(--acc-soft)`, icon tài liệu `var(--acc)`.
- Tiêu đề 15.5px/600: **`Đăng nhập Google để xem danh sách tài liệu`**
- Đoạn 13.5px `var(--txt2)`, rộng tối đa 420px (chữ **đọc** in đậm):
  > Đăng nhập một lần, lần sau mở luôn không cần làm lại. Giọng Việt chỉ xin quyền **đọc** tài liệu — không sửa, không xoá gì trên Drive của bạn.
- Nút chính cao 38px, nền `var(--acc)`: **`Đăng nhập bằng Google`** → sang bước `list`, thẻ `Từ Drive`.
- Liên kết chữ `var(--acc)`: **`Hoặc dán link tài liệu, không cần đăng nhập`** → sang bước `list`,
  thẻ `Dán link`.

**Bước 2 — `list`**, có **2 thẻ** (nút bo 4px trong khung `var(--ctl)`):
`Từ Drive` (mặc định) và `Dán link`. Thẻ đang chọn: nền `var(--acc)`, chữ `var(--acc-txt)`.
Nếu đã đăng nhập → sát phải hiện `chuaanlac.vp@gmail.com` + liên kết `Đổi tài khoản`
(bấm → quay lại bước `signin`, mất trạng thái đăng nhập).

**Thẻ `Từ Drive`:**
- Ô tìm cao 34px, icon kính lúp, ô nhập gợi ý (placeholder) **`Tìm theo tên tài liệu…`**
- Danh sách tài liệu, vùng cuộn `max-height:290px`. Mỗi hàng: icon tài liệu 17px, tên 14px,
  dòng phụ 12.5px `var(--txt3)`, dấu ✓ 16px `var(--acc)` khi được chọn.
  Hàng được chọn: nền `var(--acc-soft)`, viền `var(--acc)`, tên đậm 600, icon `var(--acc)`.
  Tooltip: `{tên} — nháy đúp để mở luôn`. **Bấm 1 lần** = chọn; **nháy đúp** = mở ngay.
  | Tên tài liệu | Dòng phụ |
  |---|---|
  | `Thư cảm ơn cuối năm` | `Bạn sửa lần cuối · 14:02 hôm nay` |
  | `Thông báo lễ tổng kết năm học 2026` | `Cô Hạnh sửa lần cuối · hôm qua` |
  | `Danh sách khen thưởng học kỳ hai` | `Thầy Dũng sửa lần cuối · 9/8/2026` |
- Lọc theo tên, không phân biệt hoa thường. **Không khớp gì** → khối rỗng canh giữa:
  `Không có tài liệu nào khớp “{từ đã gõ}”.` / xuống dòng /
  `Thử tên khác, hoặc dán link tài liệu ở thẻ bên cạnh.`

**Thẻ `Dán link`:**
- Nhãn 13px: `Link tài liệu Google Docs`
- Ô nhập cao 36px, viền dưới 2px `var(--acc)`, gợi ý **`https://docs.google.com/document/d/…`**
- Khối ghi chú nền `var(--ctl)`, viền `var(--stroke2)`, bo 6px, 13.5px (phần trong ngoặc kép in đậm):
  > Tài liệu phải bật **“Bất kỳ ai có đường liên kết đều xem được”**. Cách này không cần đăng nhập — tiện khi mượn máy hoặc dùng máy chung.

**Bước 3 — `loading`**, canh giữa:
- Vòng xoay 34px (`spin .8s linear infinite`).
- Chữ 15px/600: **`Đang tải {tên tài liệu}…`** (thẻ Dán link thì tên là `tài liệu từ link`).
- Chữ 13.5px: **`Tải xong sẽ mở ra như một tệp văn bản thường.`**
- Chạy **1.200 ms** rồi đóng hộp, đặt giờ lấy = giờ hệ thống hiện tại và mở tệp ra.

**Chân hộp** (nền `var(--layer2)`, viền trên `1px var(--divider)`):
- Chữ 12.5px `var(--txt3)` `{{ gFoot }}`:
  | Trạng thái | Chữ chân hộp |
  |---|---|
  | `loading` | `Bấm Huỷ nếu bạn không muốn mở tài liệu này nữa` |
  | `list` + thẻ `Từ Drive`, có kết quả | `{N} tài liệu · nháy đúp để mở nhanh` |
  | `list` + thẻ `Từ Drive`, không kết quả | `Không có tài liệu nào khớp` |
  | `list` + thẻ `Dán link` | `Không cần đăng nhập nếu tài liệu đã bật chia sẻ công khai` |
  | `signin` | `Giọng Việt chỉ đọc, không sửa gì trên Drive của bạn` |
- Nút `Huỷ` (nền `var(--layer)`, viền `var(--stroke2)`) → đóng hộp, hủy cả bộ đếm đang chạy.
- Nút `Mở tài liệu` — **chỉ hiện ở bước `list`**.

**Điều kiện đi tiếp / bị chặn của nút `Mở tài liệu`:**
- Thẻ `Từ Drive`: đi tiếp được khi danh sách lọc **còn ít nhất 1 tài liệu**.
- Thẻ `Dán link`: đi tiếp được khi link **khớp mẫu `docs.google.com/document`**.
- Khi **chưa đủ điều kiện**: nút có nền + viền `var(--stroke2)`, chữ `var(--txt3)` (dáng bị làm mờ)
  và **bấm không có tác dụng**.
- Khi đủ: nền + viền `var(--acc)`, chữ `var(--acc-txt)`, đậm 600.

### 6.2 Toast "Vừa xuất xong"

Chỉ hiện khi tình huống là `Vừa xuất xong`, **có tệp**, và người dùng chưa bấm đóng.
Vị trí `right:12px; bottom:40px`, `width:360px`, nền `var(--layer)`, viền `var(--stroke2)`,
bo 8px, `box-shadow: 0 12px 28px rgba(0,0,0,.28)`, `padding:14px`, `z-index:55`.

- Hàng đầu: logo 16×16 `var(--acc)` + chữ 12px `var(--txt3)` **`Giọng Việt`** + nút X 24×24 sát phải.
- Tiêu đề 15px/600: **`Đã xuất xong tệp âm thanh`**
- Nội dung 14px `var(--txt2)`, hai dòng:
  - dòng 1 `{{ toastLine }}` = `{tên tệp không đuôi}{đuôi} · {thời lượng} · {dung lượng}`
    Mặc định định dạng là `WAV 24 bit` → đuôi `.wav` → dung lượng **`11,6 MB`**
    (nếu là MP3 thì **`2,8 MB`**).
  - dòng 2: **`Lưu tại: Tài liệu\GiongViet\Xuất`**
- Hai nút chia đôi hàng, cao 34px: `Mở thư mục` (chưa nối) và `Đóng` (đóng toast).

Bấm bất kỳ nút trên dải công tắc `Tình huống` hay dải trạng thái sẽ **bật lại** toast
(cờ "đã đóng" bị xoá).

---

## 7. Dữ liệu mẫu — hồ sơ, tệp, nội dung, "cần chú ý"

Bảng này quyết định cái gì hiện ở cột giữa và cột phải, nên phải ghi lại đủ.

### 7.1 Bốn hồ sơ mặc định

| # | Tên hồ sơ | Giọng | Tốc độ | Cao độ | Âm lượng | Icon | Tệp mở sẵn |
|---|---|---|---|---|---|---|---|
| 0 | `Bài viết, văn bản` | `Giọng Ngọc Linh` | 0 | 0 | 100 | tài liệu | `A`, `E` |
| 1 | `Thông báo ngắn` | `Giọng Xuân Vĩnh` | +10 | 0 | 100 | chuông | `C` |
| 2 | `Sách nói` | `Giọng bác Tuấn` | −10 | 0 | 90 | sách | `B` |
| 3 | `Danh sách, biểu mẫu` | `Giọng Bình An` | 0 | 0 | 100 | danh sách | `D`, `M` |

Nút `Dán văn bản` mở tệp chính theo hồ sơ: `A` · `C` · `B` · `D`.
Nút `Mở file` mở tệp phụ theo hồ sơ: `E` · `C` · `B` · `D`.
(Nếu tệp đó đã mở ở chỗ khác trong cùng hồ sơ thì chỉ nhảy sang chứ không mở thêm.)

### 7.2 Chín tệp mẫu

| Mã | Tên tệp | Loại | Câu dẫn "Cần chú ý" |
|---|---|---|---|
| `A` | `thongbao-quoc-khanh.txt` | thường | `9 chỗ cần chú ý, trong đó 2 lỗi nên sửa trước khi xuất.` |
| `B` | `chuong-01.docx` | thường | `5 chỗ cần chú ý, trong đó 1 lỗi nên sửa trước khi xuất.` |
| `C` | `thongbao-phun-thuoc.txt` | thường | `4 chỗ cần chú ý, trong đó 1 lỗi nên sửa trước khi xuất.` |
| `D` | `danh-sach-ung-ho.txt` | thường | `11 chỗ cần chú ý, trong đó 1 lỗi nên sửa trước khi xuất.` |
| `E` | `bai-viet-nghe-lai.docx` | thường | `3 chỗ cần chú ý, không có lỗi bắt buộc sửa.` |
| `G` | `Thư cảm ơn cuối năm` | **Google Docs** | `3 chỗ cần chú ý, không có lỗi nào phải sửa.` |
| `G2` | `Thông báo lễ tổng kết năm học 2026` | **Google Docs** | `4 chỗ cần chú ý, trong đó 1 lỗi nên sửa trước khi xuất.` |
| `G3` | `Danh sách khen thưởng học kỳ hai` | **Google Docs** | `5 chỗ cần chú ý, trong đó 1 lỗi nên sửa trước khi xuất.` |
| `M` | `Danh sách công đức` | **bản ghép**, 248 dòng | `4 chỗ cần chú ý, không có lỗi bắt buộc sửa.` |

### 7.3 Các hàng "Cần chú ý" theo tệp

Định dạng: `nhãn` — số đếm — nhảy tới đoạn — có phải lỗi phải sửa — tooltip (nguyên văn).

**`A`**
- `Lỗi phải sửa` — 2 — đoạn 1 — **lỗi** — `“2/9” đọc thành “hai phần chín” · “17h00” đọc thành “mười bảy hắt không không”`
- `Từ viết tắt` — 4 — đoạn 2 — `TNHH · UBND · TP.HCM · TM.`
- `Đoạn dài, ký tự lạ` — 2 — đoạn 4 — `Đoạn 4 dài 168 ký tự · ký tự “—” bị bỏ qua`
- `Tên riêng, số điện thoại` — 1 — đoạn 10 — `Nguyễn Văn Tuyến · 1900 6868`

**`B`**
- `Lỗi phải sửa` — 1 — đoạn 4 — **lỗi** — `“4h30” đọc thành “bốn hắt ba mươi”`
- `Số cần đọc rõ` — 2 — đoạn 4 — `“68 tuổi” · “hồi 15”`
- `Ký tự lạ` — 1 — đoạn 1 — `Ký tự “—” trong tên chương bị bỏ qua`
- `Tên riêng` — 1 — đoạn 6 — `ông Tư · thằng Hai`

**`C`**
- `Lỗi phải sửa` — 1 — đoạn 4 — **lỗi** — `“6h00” đọc thành “sáu hắt không không”`
- `Từ viết tắt` — 1 — đoạn 1 — `UBND`
- `Ngày tháng` — 1 — đoạn 3 — `“15/8” nên viết “ngày 15 tháng 8”`
- `Số điện thoại` — 1 — đoạn 6 — `0283 8123 456 sẽ đọc từng chữ số`

**`D`**
- `Lỗi phải sửa` — 1 — đoạn 2 — **lỗi** — `“12.500.000” đọc thành “mười hai chấm năm trăm nghìn”`
- `Số tiền đọc dài` — 5 — đoạn 3 — `Mỗi dòng một số tiền, nên đọc theo nhóm nghìn`
- `Ký tự lạ` — 5 — đoạn 3 — `Dấu “—” giữa tên và số tiền bị bỏ qua`

**`E`**
- `Câu dài` — 2 — đoạn 4 — `Đoạn 4 và đoạn 6 dài hơn 25 từ`
- `Số cần đọc rõ` — 1 — đoạn 4 — `“25 từ” đọc là “hai mươi lăm từ”`

**`G`**
- `Ngày tháng` — 1 — đoạn 5 — `“22/8/2026” nên viết “ngày 22 tháng 8”`
- `Số cần đọc rõ` — 2 — đoạn 4 — `“12 quạt trần” · “340 bộ sách”`

**`G2`**
- `Lỗi phải sửa` — 1 — đoạn 3 — **lỗi** — `“7h30” đọc thành “bảy hắt ba mươi”`
- `Ngày tháng` — 1 — đoạn 3 — `“22/8” nên viết “ngày 22 tháng 8”`
- `Từ viết tắt` — 2 — đoạn 5 — `GVCN · BGH`

**`G3`**
- `Lỗi phải sửa` — 1 — đoạn 2 — **lỗi** — `“9,8” đọc thành “chín tám”`
- `Tên riêng` — 3 — đoạn 3 — `Nguyễn Bảo Châu · Trần Gia Hân · Lê Đức Duy`
- `Số cần đọc rõ` — 1 — đoạn 2 — `“5A1” đọc là “năm A một”`

**`M`**
- `Tên riêng` — 2 — đoạn 6 — `Nguyễn Văn Tuyến · Trần Thị Kim Loan`
- `Số tiền đọc dài` — 1 — đoạn 7 — `Số tiền đã được đọc thành chữ theo Cách đọc của cột`
- `Đoạn dài` — 1 — đoạn 2 — `Đoạn 2 dài 165 ký tự`

### 7.4 Nội dung tệp ghép `M` — 15 đoạn, ba khối

Đây là tệp minh hoạ **dữ liệu sống**: phần tĩnh + phần động từ bảng tính + phần kết tĩnh.

**Khối tĩnh đầu (đoạn 1–4, sửa được):**
1. `Nam mô A Di Đà Phật.`
2. `Nhà chùa xin thành kính thông báo và ghi nhận danh sách quý Phật tử, quý gia đình, quý cơ quan, đơn vị và quý mạnh thường quân đã phát tâm công đức xây dựng, tu bổ và hộ trì Tam Bảo.`
3. `Nhà chùa xin thành kính tri ân công đức của quý vị.`
4. `Sau đây là danh sách công đức.`

**Khối động (đoạn 5–11, `dyn` — có vạch xanh mảnh, KHÔNG sửa được):**
5. `Đợt cúng dường Rằm tháng Bảy.`
6. `Gia đình Phật tử Nguyễn Văn Tuyến, phát tâm công đức số tiền năm triệu đồng.`
7. `Bà Trần Thị Kim Loan, phát tâm công đức số tiền hai triệu năm trăm nghìn đồng.`
8. `Công ty trách nhiệm hữu hạn Bảo Sơn, phát tâm công đức số tiền hai mươi triệu đồng.`
9. `Phật tử Lê Minh Hoà, phát tâm công đức số tiền năm trăm nghìn đồng.`
10. `Gia đình bà Nguyễn Thị Bích Ngọc, phát tâm công đức số tiền một triệu hai trăm nghìn đồng.`
11. `Bà Phạm Thị Hoa, phát tâm công đức số tiền ba trăm nghìn đồng.`

**Khối kết tĩnh (đoạn 12–15, đánh dấu `tail`):**
12. `Danh sách công đức đến đây xin được khép lại.`
13. `Nhà chùa xin thành kính tri ân công đức, tấm lòng hoan hỷ và sự phát tâm hộ trì Tam Bảo của quý Phật tử, quý gia đình, quý cơ quan, đơn vị và quý mạnh thường quân.`
14. `Nguyện đem công đức này hồi hướng cho quốc thái dân an, chúng sinh an lạc, gia đình bình an, mọi người mọi nhà được mạnh khỏe, hạnh phúc và sở cầu như nguyện.`
15. `Nam mô Công Đức Lâm Bồ Tát Ma Ha Tát.`

Khi bấm chip lấy dữ liệu mới → dòng dẫn `Sau đây là danh sách bổ sung.` + 3 dòng mới được chèn
**ngay trước đoạn 12** (trước khối `tail`), tức là **dồn xuống cuối phần động** — không xen vào
giữa những dòng đã đọc qua.

### 7.5 Nội dung các tệp mẫu khác (dòng đầu là tiêu đề `head`, 20px/700)

**`A` — `thongbao-quoc-khanh.txt`** (16 đoạn, có 1 đoạn trắng ở vị trí 13):
1. `THÔNG BÁO LỊCH NGHỈ LỄ QUỐC KHÁNH 2/9`
2. `Kính gửi toàn thể cán bộ, nhân viên Công ty TNHH Bảo Sơn.`
3. `Căn cứ Bộ luật Lao động 2019 và thông báo của UBND TP.HCM, Ban Giám đốc thông báo lịch nghỉ lễ Quốc khánh năm 2026 như sau.`
4. `Thời gian nghỉ tính từ thứ Hai ngày 31/8/2026 đến hết thứ Tư ngày 2/9/2026, tổng cộng 3 ngày làm việc. Công ty làm việc trở lại bình thường từ sáng thứ Năm ngày 3/9.`
5. `Các bộ phận trực tiếp sản xuất bố trí người trực theo lịch đã gửi qua email ngày 12/8. Danh sách trực cụ thể như sau.`
6. `Phòng Kinh doanh — anh Trần Minh Đức`
7. `Phòng Kỹ thuật — anh Lê Hoàng Nam`
8. `Phòng Kho vận — chị Phạm Thu Hà`
9. `Nhân viên có nhu cầu nghỉ thêm vui lòng đăng ký với Phòng Nhân sự trước 17h00 ngày 25/8/2026 để bộ phận sắp xếp nhân lực thay thế.`
10. `Trong thời gian nghỉ lễ, mọi sự cố khẩn cấp xin liên hệ số hotline 1900 6868, máy lẻ 2.`
11. `Kính chúc toàn thể anh chị em cùng gia đình một kỳ nghỉ lễ vui vẻ và an toàn.` — **đoạn có thẻ `[hắng giọng]` sẵn** khi `showEmotionChips = true`
12. `Trân trọng thông báo.`
13. *(đoạn trắng)*
14. `TM. BAN GIÁM ĐỐC`
15. `Giám đốc điều hành`
16. `Nguyễn Văn Tuyến`

**`B` — `chuong-01.docx`** (9 đoạn): `Chương 1 — Bến sông buổi sớm` /
`Sương còn đọng trên mặt nước khi ông Tư đẩy chiếc thuyền nhỏ rời bờ.` /
`Bến sông giờ này chỉ có dăm người, phần lớn là dân chài đã quen mặt nhau mấy chục năm.` /
`Ông Tư năm nay 68 tuổi, theo sông từ hồi 15. Mỗi sáng ông rời nhà lúc 4h30, về lúc gần trưa.` /
`Con nước tháng 8 lên chậm. Ông thả lưới ở khúc quanh trước miếu Bà, chỗ nước xoáy nhẹ, cá hay tụ về.` /
`Thằng Hai, con trai út, đã bỏ sông lên thành phố làm công nhân được ba năm.` /
`Nó gọi về mỗi tháng một lần, lần nào cũng bảo ba nghỉ đi, con gửi tiền về.` /
`Ông ừ, rồi sáng hôm sau vẫn ra bến.` /
`Sông không giữ ai, nhưng ai đã quen sông thì khó mà rời.`

**`C` — `thongbao-phun-thuoc.txt`** (6 đoạn): `THÔNG BÁO CỦA UBND PHƯỜNG` /
`Kính thưa toàn thể bà con nhân dân trong phường.` /
`Ngày mai, thứ Bảy 15/8, phường tổ chức phun thuốc diệt muỗi phòng dịch sốt xuất huyết.` /
`Thời gian từ 6h00 đến 10h30, bắt đầu từ tổ 1 đến tổ 7.` /
`Đề nghị bà con đóng cửa sổ, che đậy thức ăn và không để trẻ nhỏ ra ngoài trong lúc phun thuốc.` /
`Mọi thắc mắc xin liên hệ cán bộ y tế phường, số 0283 8123 456.`

**`D` — `danh-sach-ung-ho.txt`** (9 đoạn, đoạn 8 là đoạn trắng):
`DANH SÁCH ỦNG HỘ QUỸ KHUYẾN HỌC THÁNG 8` / `Tổng cộng 6 lượt ủng hộ, số tiền 12.500.000 đồng.` /
`Ông Nguyễn Văn Ba — 5.000.000 đồng` / `Bà Trần Thị Lan — 3.000.000 đồng` /
`Anh Lê Minh Quân — 2.000.000 đồng` / `Chị Phạm Thu Hà — 1.500.000 đồng` /
`Gia đình ông bà Đỗ Văn Tám — 1.000.000 đồng` / *(đoạn trắng)* /
`Ban Khuyến học xin trân trọng cảm ơn quý vị.`

**`E` — `bai-viet-nghe-lai.docx`** (7 đoạn): `Vì sao nên nghe lại bài viết trước khi đăng` /
`Mắt quen với chữ của chính mình nên rất dễ đọc lướt qua lỗi.` /
`Khi nghe, tai bắt buộc phải đi theo đúng thứ tự chữ, không nhảy cóc được.` /
`Một câu dài quá 25 từ sẽ lộ ra ngay, vì người nghe hụt hơi trước khi câu kết thúc.` /
`Lặp từ, thừa liên từ, sai chính tả tên riêng cũng dễ nhận ra hơn khi nghe.` /
`Cách làm gọn nhất: nghe từng đoạn, dừng lại sửa, rồi nghe lại đúng đoạn vừa sửa.` /
`Không cần nghe hết cả bài trong một lần.`

**`G` — `Thư cảm ơn cuối năm`** (6 đoạn): `THƯ CẢM ƠN CUỐI NĂM` /
`Kính gửi quý vị phụ huynh và các em học sinh Trường Tiểu học An Lạc.` /
`Một năm học nữa đã đi qua. Nhà trường xin gửi lời cảm ơn chân thành đến quý vị phụ huynh đã đồng hành cùng thầy cô trong suốt năm học vừa rồi.` /
`Nhờ sự chung tay của quý vị, nhà trường đã hoàn thành việc sửa lại khu nhà vệ sinh, lắp thêm 12 quạt trần cho các lớp tầng ba và mua mới 340 bộ sách cho thư viện.` /
`Lễ tổng kết năm học sẽ diễn ra vào 8h00 thứ Bảy ngày 22/8/2026 tại sân trường. Kính mời quý vị phụ huynh đến dự.` /
`Trân trọng cảm ơn.`

**`G2` — `Thông báo lễ tổng kết năm học 2026`** (6 đoạn):
`THÔNG BÁO LỄ TỔNG KẾT NĂM HỌC 2026` /
`Kính gửi quý vị phụ huynh và các em học sinh toàn trường.` /
`Lễ tổng kết năm học 2025 – 2026 sẽ diễn ra vào 7h30 thứ Bảy ngày 22/8/2026 tại sân trường.` /
`Học sinh có mặt trước 7h15, mặc đồng phục đầy đủ và tập trung theo lớp dưới sự hướng dẫn của GVCN.` /
`Phụ huynh có con được khen thưởng vui lòng đến sớm 15 phút để BGH sắp chỗ ngồi ở khu vực phía trước.` /
`Nếu trời mưa, buổi lễ chuyển vào hội trường tầng hai. Nhà trường sẽ nhắn tin thông báo trước 6h30 sáng cùng ngày.`

**`G3` — `Danh sách khen thưởng học kỳ hai`** (5 đoạn):
`DANH SÁCH KHEN THƯỞNG HỌC KỲ HAI` /
`Khối 5 có 3 em đạt danh hiệu Học sinh xuất sắc, điểm trung bình từ 9,8 trở lên.` /
`Em Nguyễn Bảo Châu, lớp 5A1. Em Trần Gia Hân, lớp 5A2. Em Lê Đức Duy, lớp 5A4.` /
`Nhà trường xin chúc mừng các em và gia đình.` /
`Phần thưởng được trao trong lễ tổng kết năm học.`

---

## 8. Toàn bộ chuỗi tiếng Việt hiện ra màn hình

### 8.1 Ngoài khung cửa sổ (khu điều khiển bản mẫu)
`Phương án 2 · Văn bản theo đoạn` · `Sẵn sàng` · `Đang đọc` · `Chưa có văn bản` · `Sáng` · `Tối` ·
`Tình huống` · `Bình thường` · `Đang tạo âm thanh` · `Mất kết nối` · `Hết lượt` · `Giọng đang tải` ·
`Văn bản quá dài` · `Âm thanh cũ` · `Đang xuất tệp` · `Vừa xuất xong` ·
`Bản mẫu bấm được như phần mềm thật. Mỗi hồ sơ đọc là một chỗ làm việc riêng: đổi hồ sơ thì tệp đang mở, nội dung ở giữa, giọng và các chỗ cần chú ý đều đổi theo. Đơn vị là đoạn — bấm số đoạn để nghe riêng đoạn đó, nghe hết đoạn thì dừng.`

### 8.2 Thanh menu và các mục
`Tệp` · `Chỉnh sửa` · `Chèn` · `Giọng` · `Xem` · `Trợ giúp` ·
`Mở tệp…` · `Mở từ Google Docs…` · `Dán văn bản` · `Lưu` · `Xuất file âm thanh` · `Đóng tệp` ·
`Ghép danh sách từ Google Sheet…` · `Cài đặt…` · `Thoát` ·
`Hoàn tác` · `Làm lại` · `Cắt` · `Sao chép` · `Dán` · `Chọn tất cả` · `Tìm và thay thế` ·
`Soát văn bản` · `Thẻ cảm xúc` · `Khoảng lặng 1 giây` · `Ngắt đoạn` ·
`Thêm cách đọc cho từ đang chọn…` · `Đổi giọng đọc` · `Nghe mẫu giọng` · `Thư viện giọng` ·
`Nhân bản giọng từ file…` · `Thu âm để tạo giọng mới…` · `Từ điển phát âm` ·
`Thu gọn danh sách hồ sơ` · `Cỡ chữ lớn hơn` · `Cỡ chữ nhỏ hơn` · `Toàn màn hình` · `Giao diện tối` ·
`Hướng dẫn nhanh` · `Danh sách phím tắt` · `Giới thiệu Giọng Việt` · `Kiểm tra bản cập nhật` ·
`Gửi phản hồi cho nhà phát triển` · `Đặt lại bản mẫu về ban đầu`

### 8.3 Thanh công cụ và dải tìm
`Dán văn bản` · `Mở file` · `Soát văn bản` · `Thẻ cảm xúc` · `Tìm và thay thế` · `Nghe toàn bộ` ·
`Xuất file âm thanh` · `Chèn vào đoạn {N}` · `[cười]` · `[thở dài]` · `[hắng giọng]` ·
`Gỡ thẻ khỏi đoạn này` · `Tìm` · `Thay bằng` · `Thay thế` · `Thay tất cả` · `17h00` · `17 giờ` · `1/1`

### 8.4 Cột trái
`Hồ sơ đọc` · `Thêm tệp` · `Tạo hồ sơ mới` · `Thư viện giọng` · `Văn bản ghép` · `Cài đặt` ·
`Bài viết, văn bản` · `Thông báo ngắn` · `Sách nói` · `Danh sách, biểu mẫu` ·
`Hồ sơ mới {N}` · `Văn bản mới {N}` · `{N} tệp`

### 8.5 Cột giữa
`Chưa có văn bản` · `{N} từ · {M} đoạn · khoảng {thời lượng}` · `{N} giây` · `{M} phút {S} giây` ·
`Google Docs · lấy lúc {HH:MM}` · `Đang lấy bản mới từ Google Docs…` ·
`Bản ghép · {N} dòng` · `· +{N} mới` · `Đang lấy dữ liệu mới…` · `Mẫu ghép ›` ·
`Vạch xanh: từ bảng tính` ·
`Bấm vào chữ để sửa như Notepad · nút ▶ bên phải để nghe riêng đoạn` ·
`Dán văn bản vào đây để bắt đầu` ·
`Nhấn Ctrl+V, hoặc kéo thả tệp .txt, .docx, .rtf vào cửa sổ này.` ·
`Hồ sơ đang chọn: {tên} — {giọng}.` · `Dán văn bản` · `Chọn tệp từ máy…` · `Mở từ Google Docs…` ·
`Đoạn này do bảng tính sinh ra, không sửa trực tiếp ở đây.` · `Sửa mẫu câu ›`

### 8.6 Cột phải
`Hồ sơ đang dùng` · `Giọng đọc` · `Đang phát mẫu {tên giọng}…` · `Đang tải giọng về máy…` · `62%` ·
`Giọng có sẵn` · `Giọng Bình An` · `Nữ · Bắc` · `Giọng Ngọc Linh` · `Nữ · Nam` ·
`Giọng Xuân Vĩnh` · `Nam · Trung` · `Giọng của tôi` · `Giọng bác Tuấn` · `Nam · 62 tuổi` ·
`Giọng của tôi (thử)` · `mẫu 30 giây` · `Nhân bản giọng từ file…` ·
`Điều chỉnh` · `Theo mặc định của hồ sơ` · `Tốc độ` · `Cao độ` · `Âm lượng` · `Đặt lại mặc định` ·
`Cần chú ý` · `Soát văn bản` · `Từ điển phát âm` ·
(+ các nhãn hàng và câu dẫn ở mục 7.2 / 7.3)

### 8.7 Dải phát và thanh trạng thái
`Đang tạo âm thanh cho đoạn {N}` · `Thường mất 5–10 giây cho mỗi đoạn` · `Huỷ` ·
`Đang nghe riêng đoạn {N}` · `Đang đọc đoạn {N}/{M}` · `Nghe hết đoạn này sẽ dừng` ·
`Đang chuẩn bị đoạn tiếp theo…` · `Đoạn {N}, Cột 1` ·
`Đang xuất tệp âm thanh · 34%` · `VieNeu v3 Turbo · mất kết nối` ·
`VieNeu v3 Turbo · hết lượt tháng này` · `Đang tải {tên giọng} · 62%` ·
`VieNeu v3 Turbo · đang tạo âm thanh` · `VieNeu v3 Turbo · sẵn sàng` ·
`Hồ sơ: {tên}` · `Đã lưu 14:02 · Hồ sơ: {tên}`

### 8.8 Hộp thoại Google Docs
`Mở tài liệu Google Docs` · `Cần đăng nhập Google một lần để đọc danh sách tài liệu` ·
`Chọn một tài liệu, nội dung sẽ được mở ra như tệp văn bản thường` · `Đang lấy nội dung về máy` ·
`Đăng nhập Google để xem danh sách tài liệu` ·
`Đăng nhập một lần, lần sau mở luôn không cần làm lại. Giọng Việt chỉ xin quyền đọc tài liệu — không sửa, không xoá gì trên Drive của bạn.` ·
`Đăng nhập bằng Google` · `Hoặc dán link tài liệu, không cần đăng nhập` ·
`Từ Drive` · `Dán link` · `chuaanlac.vp@gmail.com` · `Đổi tài khoản` ·
`Tìm theo tên tài liệu…` ·
`Thư cảm ơn cuối năm` · `Bạn sửa lần cuối · 14:02 hôm nay` ·
`Thông báo lễ tổng kết năm học 2026` · `Cô Hạnh sửa lần cuối · hôm qua` ·
`Danh sách khen thưởng học kỳ hai` · `Thầy Dũng sửa lần cuối · 9/8/2026` ·
`Không có tài liệu nào khớp “{từ khoá}”.` · `Thử tên khác, hoặc dán link tài liệu ở thẻ bên cạnh.` ·
`Link tài liệu Google Docs` · `https://docs.google.com/document/d/…` ·
`Tài liệu phải bật “Bất kỳ ai có đường liên kết đều xem được”. Cách này không cần đăng nhập — tiện khi mượn máy hoặc dùng máy chung.` ·
`Đang tải {tên}…` · `Tải xong sẽ mở ra như một tệp văn bản thường.` ·
`Bấm Huỷ nếu bạn không muốn mở tài liệu này nữa` · `{N} tài liệu · nháy đúp để mở nhanh` ·
`Không có tài liệu nào khớp` ·
`Không cần đăng nhập nếu tài liệu đã bật chia sẻ công khai` ·
`Giọng Việt chỉ đọc, không sửa gì trên Drive của bạn` · `Huỷ` · `Mở tài liệu` ·
`tài liệu từ link`

### 8.9 Toast
`Giọng Việt` · `Đã xuất xong tệp âm thanh` · `Lưu tại: Tài liệu\GiongViet\Xuất` ·
`Mở thư mục` · `Đóng` · `11,6 MB` · `2,8 MB`

### 8.10 Toàn bộ tooltip (thuộc tính `title`)
`Thu nhỏ` · `Phóng to` · `Đóng` ·
`Dán văn bản từ clipboard (Ctrl+V)` · `Mở tệp văn bản (Ctrl+O)` ·
`Xem các chỗ dễ đọc sai và văn bản sau chuẩn hoá (Ctrl+K)` ·
`Chèn thẻ cảm xúc vào đoạn đang chọn` ·
`Tìm một từ trong văn bản và thay bằng từ khác (Ctrl+H)` ·
`Nghe liền mạch toàn bộ văn bản từ đầu (Space)` ·
`Mở hộp thoại xuất để chọn định dạng và nơi lưu (Ctrl+E)` ·
`Mở rộng danh sách hồ sơ` · `Thu gọn danh sách hồ sơ` · `Thư viện giọng` · `Cài đặt` ·
`Giọng bạn tự nhân bản` · `Hồ sơ này có tệp đang có lỗi nên sửa trước khi xuất` ·
`Xoá hồ sơ này` · `Đóng tệp` · `Mở thêm một tệp trong hồ sơ này` · `Tạo hồ sơ đọc mới` ·
`Ghép phần tĩnh với danh sách từ Google Sheet` ·
`{tên hồ sơ} — {giọng} · {N} tệp · nháy đúp để đổi tên` · `{tên tệp} · nháy đúp để đổi tên` ·
`Mở mẫu ghép để sửa mẫu câu, nguồn dữ liệu và cách đọc từng cột` ·
`Chọn một tài liệu Google Docs trên Drive` ·
`Bấm để gỡ thẻ cảm xúc` · `Nghe riêng đoạn này, nghe hết đoạn thì dừng` ·
`Nghe mẫu giọng này (5 giây)` · `Nghe mẫu` ·
`Tải lên 30 giây ghi âm để tạo giọng riêng` ·
`Từ -50% đến +100%` · `Từ -12 đến +12 nửa cung` · `Từ 0% đến 100%` ·
`Mở màn hình soát văn bản` · `Ghi cách đọc riêng cho từ ngữ của bạn` ·
`Tạm dừng (Space)` · `Dừng (Ctrl+.)` ·
`{tên tài liệu} — nháy đúp để mở luôn` ·
(+ các tooltip động của chip Google Docs / chip bản ghép ở mục 5.8,
và tooltip hàng "Cần chú ý" ở mục 7.3)

---

## 9. Biến CSS — giá trị bộ Sáng và bộ Tối

Bộ Sáng khai báo ở `:root`. Bộ Tối khai báo ở `:root[data-theme='dark']`.
Mã đặt `data-theme = 'dark'` khi giao diện là `toi`, ngược lại `'light'`.

| Biến | Sáng | Tối |
|---|---|---|
| `--bg` | `#f3f3f3` | `#202020` |
| `--layer` | `#ffffff` | `#2b2b2b` |
| `--layer2` | `#fafafa` | `#272727` |
| `--stroke` | `rgba(0,0,0,.0578)` | `rgba(255,255,255,.07)` |
| `--stroke2` | `rgba(0,0,0,.16)` | `rgba(255,255,255,.10)` |
| `--divider` | `#e5e5e5` | `#303030` |
| `--txt` | `#1a1a1a` | `#ffffff` |
| `--txt2` | `#5d5d5d` | `rgba(255,255,255,.73)` |
| `--txt3` | `#767676` | `rgba(255,255,255,.60)` |
| `--dis` | `#a3a3a3` | `rgba(255,255,255,.38)` |
| `--ctl` | `#fdfdfd` | `rgba(255,255,255,.06)` |
| `--ctl-h` | `#f6f6f6` | `rgba(255,255,255,.084)` |
| `--sub-h` | `rgba(0,0,0,.037)` | `rgba(255,255,255,.06)` |
| `--sel` | `rgba(0,0,0,.055)` | `rgba(255,255,255,.08)` |
| `--acc` | `#0067c0` | `#4cc2ff` |
| `--acc-h` | `#1a75c6` | `#47b1e8` |
| `--acc-txt` | `#ffffff` | `#000000` |
| `--acc-soft` | `rgba(0,103,192,.09)` | `rgba(76,194,255,.12)` |
| `--hl` | `rgba(0,103,192,.11)` | `rgba(76,194,255,.13)` |
| `--chip-bg` | `rgba(0,0,0,.055)` | `rgba(255,255,255,.09)` |
| `--chip-fg` | `#4a4a4a` | `rgba(255,255,255,.82)` |
| `--chip-bd` | `rgba(0,0,0,.09)` | `rgba(255,255,255,.14)` |
| `--ok` | `#0f7b0f` | `#6ccb5f` |
| `--err` | `#c42b1c` | `#ff99a4` |
| `--err-bg` | `#fdf3f4` | `#442726` |
| `--err-bd` | `#eecfd2` | `#6b3a38` |
| `--warn` | `#9d5d00` | `#fce100` |
| `--warn-bg` | `#fff9ec` | `#3a3320` |
| `--warn-bd` | `#f0e2c2` | `#5c4f2a` |
| `--rail` | `#868686` | `#9a9a9a` |
| `--close` | `#c42b1c` | `#c42b1c` (**giống nhau**) |
| `--shadow` | `0 8px 16px rgba(0,0,0,.14)` | `0 8px 16px rgba(0,0,0,.36)` |

**Ba màu viết cứng ngoài hệ biến** (chỉ dùng ở khu điều khiển bản mẫu bên ngoài cửa sổ,
không đổi theo giao diện): nền trang `#e6e6e6`, nút đang chọn `#0067c0` / chữ `#fff`,
chữ nút không chọn `#5d5d5d`, viền nút `rgba(0,0,0,.09)`, nền nút `#fdfdfd`.

**Ba animation khai báo:**
- `pulse` — `0%,100% { opacity:.3 } 50% { opacity:1 }` — dùng cho đốm "đang phát mẫu".
- `caret` — `50% { opacity:0 }` — dùng cho con trỏ nháy trong ô Tìm.
- `spin` — `to { transform: rotate(360deg) }` — dùng cho mọi vòng xoay (đoạn đang tạo âm thanh,
  dải phát, hộp thoại Google Docs, chip làm mới).

---

## 10. Phím tắt nêu trong thiết kế

| Phím | Việc |
|---|---|
| `Ctrl+O` | Mở tệp… |
| `Ctrl+V` | Dán văn bản |
| `Ctrl+S` | Lưu |
| `Ctrl+E` | Xuất file âm thanh |
| `Ctrl+W` | Đóng tệp |
| `Alt+F4` | Thoát |
| `Ctrl+Z` | Hoàn tác |
| `Ctrl+Y` | Làm lại |
| `Ctrl+X` | Cắt |
| `Ctrl+C` | Sao chép |
| `Ctrl+A` | Chọn tất cả |
| `Ctrl+H` | Tìm và thay thế |
| `Ctrl+K` | Soát văn bản |
| `Alt+1` / `Alt+2` / `Alt+3` | Chèn thẻ `[cười]` / `[thở dài]` / `[hắng giọng]` |
| `Alt+S` | Khoảng lặng 1 giây |
| `Enter` | Ngắt đoạn (tách đoạn tại con trỏ) |
| `Ctrl+G` | Đổi giọng đọc |
| `Ctrl+M` | Nghe mẫu giọng |
| `Ctrl+B` | Thu gọn / mở lại danh sách hồ sơ |
| `Ctrl+=` | Cỡ chữ lớn hơn |
| `Ctrl+-` | Cỡ chữ nhỏ hơn |
| `F11` | Toàn màn hình |
| `F1` | Hướng dẫn nhanh |
| `Ctrl+/` | Danh sách phím tắt |
| `Space` | Nghe toàn bộ / Tạm dừng (chỉ ghi trong tooltip) |
| `Ctrl+.` | Dừng (chỉ ghi trong tooltip) |
| `Escape` | Bỏ việc đổi tên hồ sơ / tệp |
| `Backspace` / `Delete` | Nối đoạn (xem mục 5.10) |

---

## 11. Mốc thời gian trong bản mẫu (phải giữ khi làm thật)

| Việc | Thời gian |
|---|---|
| Nghe mẫu giọng | tự tắt sau **2.600 ms** |
| Tải tài liệu Google Docs trong hộp thoại | **1.200 ms** rồi mở ra |
| Làm mới tệp Google Docs bằng chip | **1.400 ms** |
| Lấy dữ liệu mới cho bản ghép | **1.300 ms** |
| Câu ghi trong dải "đang tạo âm thanh" | `Thường mất 5–10 giây cho mỗi đoạn` |
| Tiến độ tải giọng (viết cứng) | `62%` |
| Tiến độ xuất tệp (viết cứng) | `34%` |
| Giờ "đã lưu" (viết cứng) | `14:02` |

---

## 12. Bản mới khác bản snapshot cũ ở đâu

Bản kéo hôm nay **khác thật** bản trong `design_handoff_giongdoc/designs/` (1.633 vs 1.155 dòng,
md5 `d5529180…` vs `17ae3e69…`). Đây là **thay đổi thiết kế**, không phải sai lệch do ghi lại.

**Bỏ đi:**
1. **Dải thẻ tệp ngang (36px) dưới thanh công cụ đã bị xoá hẳn** — cùng với nó là nút
   `Tệp mới (Ctrl+T)`. Chỗ đó nay là khoảng đệm trống 8px. Danh sách tệp chuyển thành **cây lồng
   trong bảng hồ sơ bên trái**.
2. **Hộp thoại "Xuất file âm thanh" tự làm trong màn này đã bị xoá**, thay bằng **liên kết sang màn
   `GiongDoc - Xuất file âm thanh.dc.html`**. Kéo theo mất các nhãn `Tên tệp`, `Định dạng`, `Lưu vào`,
   `Chọn…`, `Tách tệp`, `Một tệp duy nhất`, `Mỗi đoạn một tệp`, `Cắt theo độ dài`, `Bắt đầu xuất`,
   và đường dẫn mẫu `C:\Users\Tuan\Documents\GiongViet\Xuất`.

**Thêm mới:**
3. **Hai tình huống mới**: `Đang xuất tệp` (`dang_xuat`) và `Vừa xuất xong` (`vua_xuat_xong`)
   — nâng dải Tình huống từ **7 lên 9** nút.
4. **Toàn bộ luồng Google Docs**: hộp thoại 3 bước (`signin` / `list` / `loading`), 2 thẻ
   `Từ Drive` / `Dán link`, 3 tài liệu mẫu (`G`, `G2`, `G3`) với nội dung + danh sách "Cần chú ý"
   riêng, chip `Google Docs · lấy lúc HH:MM` trên hàng đầu, nút `Mở từ Google Docs…` ở trạng thái
   rỗng và trong menu Tệp.
5. **Toàn bộ luồng bản ghép (dữ liệu sống)**: tệp `M` = `Danh sách công đức` (248 dòng, 15 đoạn mẫu,
   khối tĩnh + khối động + khối kết), khái niệm **đoạn động** (`dyn`: không sửa được, vạch xanh
   2px, khối gợi ý `Đoạn này do bảng tính sinh ra, không sửa trực tiếp ở đây.` + `Sửa mẫu câu ›`),
   chip `Bản ghép · N dòng · +N mới` biết đổi màu cảnh báo, lối vào `Văn bản ghép` ở chân bảng hồ sơ,
   mục menu `Ghép danh sách từ Google Sheet…`, và cơ chế **dồn dòng mới xuống cuối phần động**.
   Mở kèm `#banghep` là nhảy thẳng vào tệp này.
6. **Hàng đầu vùng văn bản được thiết kế lại**: thêm icon tệp + **tên tệp đang mở** + gạch phân cách
   (trước đây chỉ có `docMeta` và `headerHint`).
7. **Bảng hồ sơ bên trái thành cây hai cấp**, có: đổi tên tại chỗ (hồ sơ và tệp, nháy đúp),
   xoá hồ sơ, `Thêm tệp`, đếm `N tệp`, đốm đỏ cảnh báo hồ sơ có lỗi, dòng tên tệp đang mở, icon
   giọng tự nhân bản, và vùng danh sách cuộn được.
8. **Menu có nội dung thật**: thêm gạch ngăn, thêm mục (`Mở từ Google Docs…`, `Chọn tất cả`,
   `Soát văn bản`, `Thêm cách đọc cho từ đang chọn…`, `Thu âm để tạo giọng mới…`, `Từ điển phát âm`,
   `Toàn màn hình`, `Kiểm tra bản cập nhật`, `Gửi phản hồi cho nhà phát triển`,
   `Đặt lại bản mẫu về ban đầu`, `Cài đặt…`, `Thoát`) và **phần lớn mục nay bấm được thật**;
   mục chưa nối thì chữ nhạt `var(--txt3)`.
9. **Lưu trạng thái vào `localStorage`** (`giongviet.mockup.v1`) + mục menu đặt lại.
10. **Icon "giọng tự nhân bản"** trong ô chọn giọng ở cột phải và trong bảng hồ sơ.

**Sửa nhỏ:**
11. Tên giọng hồ sơ "Sách nói" đổi từ `Giọng bác Tuấn (giọng của tôi)` thành **`Giọng bác Tuấn`**
    (phần "của tôi" giờ thể hiện bằng icon).
12. Gạch dọc trên thanh công cụ dày lên: `1×20px var(--divider)` → **`1×22px var(--stroke2)`**,
    lề `8px` → **`10px`**.
13. Liên kết `Nhân bản giọng từ file…` thêm tham số `?nhanban=1`.
14. Hồ sơ "Danh sách, biểu mẫu" mở sẵn **2 tệp** (`D`, `M`) thay vì 1 (`D`).

---

## 13. Chỗ cần chú ý khi đem thiết kế này vào phần mềm thật

1. **Bản mẫu có ba thanh trượt `Tốc độ` và `Cao độ`** — nhưng theo kim chỉ nam dự án,
   **VieNeu không có tham số tốc độ và cao độ**; thứ chỉnh được chỉ là các khoảng nghỉ.
   Phải chốt lại với chủ dự án trước khi làm, đừng bày nút giả.
2. **Nút chưa nối chức năng trong bản mẫu** (chữ nhạt trong menu): `Lưu`, `Đóng tệp`, `Thoát`,
   `Hoàn tác`, `Làm lại`, `Cắt`, `Sao chép`, `Chọn tất cả`, `Nghe mẫu giọng`, `Cỡ chữ lớn/nhỏ hơn`,
   `Toàn màn hình`, `Hướng dẫn nhanh`, `Danh sách phím tắt`, `Giới thiệu Giọng Việt`,
   `Kiểm tra bản cập nhật`, `Gửi phản hồi cho nhà phát triển`, `Khoảng lặng 1 giây`,
   nút `Thay thế` / `Thay tất cả` trong dải tìm, nút `Mở thư mục` trong toast.
   Bản thật phải nối hết hoặc bỏ hẳn.
3. **Mục menu `Giao diện tối` trong bản mẫu bị lỗi logic**: nó đặt giao diện thành `'dark'`/`'light'`,
   trong khi mã chỉ nhận `'sang'`/`'toi'`, nên bấm vào là quay về nền sáng. Bản thật phải đảo đúng
   giữa `sang` và `toi`.
4. **Mã còn sót phần chết** sau khi bỏ dải thẻ tệp và hộp thoại xuất: `fileTabs`, `newTab`,
   `splitOpts`, `scrollTop`, `scrollH`, `railOpacity`, `ghepNew` được tính nhưng không dùng để
   vẽ gì. Đừng tưởng đó là yêu cầu chưa làm.
5. **Con số trong câu dẫn "Cần chú ý" khớp đúng tổng các hàng ở cả 9 tệp** — đã cộng kiểm:
   `A` 2+4+2+1=9 · `B` 1+2+1+1=5 · `C` 1+1+1+1=4 · `D` 1+5+5=11 · `E` 2+1=3 · `G` 1+2=3 ·
   `G2` 1+1+2=4 · `G3` 1+3+1=5 · `M` 2+1+1=4. Bản thật phải **tự tính** con số này từ kết quả soát,
   không viết cứng.
6. **Chip bản ghép nói `248 dòng` nhưng nội dung mẫu chỉ có 7 dòng động** (tooltip tự nhận
   `bản mẫu hiển thị mười dòng đầu`). Số 248 là số dòng của nguồn dữ liệu, không phải số đoạn hiển thị.
7. **Địa chỉ email `chuaanlac.vp@gmail.com` trong hộp thoại là dữ liệu mẫu viết cứng** — bản thật
   phải lấy từ phiên đăng nhập.
