# Bản kiểm kê trạng thái — màn "Cài đặt"

Nguồn: `C:\Projects\DocCongDuc\design_handoff_giongdoc2\designs-goc\GiongDoc - Cài đặt.dc.html`
(kéo từ dự án thiết kế `5c70b20f-0f8b-4da8-ad19-800b0fb6ae19`, ngày 17/8/2026)

> Ghi chú đường dẫn: lúc bắt đầu việc, thư mục tên là `design_handoff_giongdoc`.
> Trong khi đang làm, nó bị đổi tên thành `design_handoff_giongdoc2` (có tiến
> trình khác cùng lúc nén ra `GiongDoc desktop mockup chính.zip`). Tệp vẫn còn
> nguyên, md5 không đổi (`523e5e23d1ed89cc2f3b89a310fc363b`).
> Bản snapshot cũ để đối chiếu: `design_handoff_giongdoc2\designs\GiongDoc - Cài đặt.dc.html`
> (md5 `9f999ce2fed8214dac7d27178a4d6cb8`).

Đây là bản mẫu tương tác tự chạy được (`.dc.html`) — HTML tĩnh cộng một khối
`<script type="text/x-dc">` chứa lớp `Component extends DCLogic`. Toàn bộ dữ liệu
hiển thị nằm trong hàm `sections()`; hàm `renderVals()` sinh ra các biến mà HTML
tham chiếu qua `{{ ... }}`.

---

## 0. Tóm tắt điểm khác so với bản snapshot cũ (14/8/2026)

Bản mới **khác** bản snapshot cũ ở đúng 3 chỗ (4 dòng). Cả 3 đều là thay đổi
thiết kế thật, không phải sai lệch do ghi lại:

| # | Chỗ | Bản cũ | Bản mới |
|---|-----|--------|---------|
| 1 | Nút mũi tên lùi ở đầu thanh bên trái (30×30) | `<div>` trơ, `cursor:default` | `<a href="GiongDoc - Màn hình chính v2 (nghe theo dòng).dc.html">`, thêm `flex:none`, `text-decoration:none`, bỏ `cursor:default` |
| 2 | Nút chính **"Đóng"** ở chân bảng phải | `<div>` trơ, `cursor:default` | `<a href="GiongDoc - Màn hình chính v2 (nghe theo dòng).dc.html">`, thêm `text-decoration:none` (vẫn giữ `cursor:default`) |
| 3 | Phím tắt của **"Soát văn bản"** | `Ctrl + Shift + K` | `Ctrl + K` |

Ý nghĩa cho phần cài đặt: hai đường quay về màn hình chính (mũi tên lùi + nút
"Đóng") giờ là **liên kết điều hướng thật**, không còn là hình trang trí. Phím
tắt soát văn bản đổi từ ba phím xuống hai phím.

---

## 1. Dải nút phía trên khung cửa sổ — danh sách công tắc ĐẦY ĐỦ

Dải nút này nằm **ngoài** khung cửa sổ 1440×900, là hàng điều khiển của bản mẫu
(không phải giao diện chương trình).

Bố cục hàng: `width:1440px`, canh giữa, `margin:0 auto 14px`, `display:flex`,
`align-items:center`, `gap:14px`.

- Bên trái: nhãn chữ **"Cài đặt"** — `font-size:12px`, `letter-spacing:.05em`,
  `text-transform:uppercase`, `color:#5d5d5d`, `font-weight:600`.
- Bên phải (`margin-left:auto`): một nhóm nút dạng viên thuốc — `background:#fdfdfd`,
  `border:1px solid rgba(0,0,0,.09)`, `border-radius:6px`, `padding:3px`, `gap:3px`.

### Công tắc duy nhất: Chủ đề sáng/tối

| Giá trị (id nội bộ) | Nhãn nguyên văn trên nút |
|---|---|
| `sang` | **"Sáng"** |
| `toi` | **"Tối"** |

Kiểu nút: `border:0`, `cursor:pointer`, `font:600 13px 'Segoe UI Variable Text','Segoe UI',Inter,sans-serif`,
`padding:7px 12px`, `border-radius:4px`.

- Đang chọn: `background:#0067c0`, `color:#fff`.
- Không chọn: `background:transparent`, `color:#5d5d5d`.

Bấm nút gọi `this.setState({ theme: id })`. Sau đó `applyTheme()` đặt
`document.documentElement.setAttribute('data-theme', theme === 'toi' ? 'dark' : 'light')`.
Hàm này được gọi cả trong `componentDidMount()` và `componentDidUpdate()`.

Khai báo prop (trong `data-props` của thẻ `<script>`):

```
theme: { editor: "enum", options: ["sang","toi"], default: "sang",
         tsType: "'sang'|'toi'", section: "Trạng thái" }
```

Thứ tự ưu tiên đọc chủ đề: `this.state.theme || this.props.theme || 'sang'`.

### KHÔNG có các công tắc khác

Bản thiết kế này **không có** công tắc "Tình huống: …", "Mở từ: …", hay
"Bước: …". Dải nút chỉ có Sáng/Tối. Hai chiều trạng thái còn lại nằm **trong**
khung cửa sổ, đổi bằng cách bấm trực tiếp vào giao diện:

| Trạng thái trong khung | Cách đổi | Giá trị |
|---|---|---|
| `state.nav` | bấm một mục ở thanh bên trái | 0…5 (6 nhóm cài đặt) |
| `state.toggles` | bấm vào từng công tắc bật/tắt trong danh sách | khoá dạng `"{nav}:{chỉ số dòng}"` → `true`/`false` |

`state` khởi tạo: `{ theme: null, nav: 0, toggles: {} }` — tức mở ra là **chủ đề
Sáng, nhóm "Chung"**, mọi công tắc lấy giá trị mặc định khai trong `sections()`.

---

## 2. Cấu trúc bố cục

### 2.1 Trang ngoài

`min-height:100vh`, `padding:20px 24px 40px`, `background:#e6e6e6`,
`font-family:'Segoe UI Variable Text','Segoe UI',Inter,system-ui,sans-serif`,
`font-size:14px`, `color:#1a1a1a`. `body{margin:0;background:#e6e6e6}`.

### 2.2 Khung cửa sổ

**Bề rộng cố định 1440px, cao cố định 900px**, canh giữa (`margin:0 auto`).
`background:var(--bg)`, `border:1px solid rgba(0,0,0,.22)`, `border-radius:8px`,
`box-shadow:0 16px 32px rgba(0,0,0,.22)`, `overflow:hidden`, xếp dọc
(`display:flex;flex-direction:column`), `color:var(--txt)`.

Từ trên xuống, khung có 2 tầng:

1. **Thanh tiêu đề** — cao 32px, `flex:none`.
2. **Thân** — `flex:1`, `padding:0 8px 8px`, xếp ngang.

### 2.3 Thanh tiêu đề (cao 32px, `padding-left:12px`, `background:var(--bg)`)

Từ trái sang phải:

1. Ô biểu tượng ứng dụng 16×16, `border-radius:3px`, `background:var(--acc)`;
   bên trong là SVG 10×10 hình 4 vạch đứng cao thấp khác nhau (dạng thanh âm):
   `M4 9v6 M9 5v14 M14 8v8 M19 11v2`, `stroke:var(--acc-txt)`, `stroke-width:2.6`,
   `stroke-linecap:round`.
2. Chữ tiêu đề **"Cài đặt — Giọng Việt"** — `font-size:12.5px`, `color:var(--txt2)`.
   (Dấu gạch dài là em dash `—`.)
3. Chip liên kết **"Màn hình chính"** — cao 22px, `padding:0 10px 0 7px`,
   `border-radius:11px`, `background:var(--sub-h)`, `color:var(--txt2)`,
   `font-size:12px`, `text-decoration:none`, `white-space:nowrap`, `gap:5px`.
   Bên trong có mũi tên chevron trái 11×11 (`M14 6l-6 6 6 6`) rồi đến chữ.
   - `title` (tooltip): **"Quay lại màn hình chính"**
   - `href`: `GiongDoc%20-%20M%C3%A0n%20h%C3%ACnh%20ch%C3%ADnh%20v2%20%28nghe%20theo%20d%C3%B2ng%29.dc.html`
     (= `GiongDoc - Màn hình chính v2 (nghe theo dòng).dc.html`)
   - hover: `color:var(--txt)`
4. `margin-left:auto` rồi 3 nút cửa sổ, mỗi nút **46×32**, `cursor:default`:
   - Thu nhỏ: SVG 10×10 một vạch ngang `M1 6h10`, `stroke-width:1`. Hover `background:var(--sub-h)`.
   - Phóng to: SVG 10×10 hình vuông `rect x=1.5 y=1.5 w=9 h=9 rx=1`, `fill:none`, `stroke-width:1`. Hover `background:var(--sub-h)`.
   - Đóng: SVG 10×10 dấu X `M1.5 1.5l9 9 M10.5 1.5l-9 9`, `stroke-width:1.1`.
     Hover **`background:#c42b1c; color:#fff`** (đỏ Windows).

   Ba nút này **không có** `title`/tooltip và **không nối** vào chức năng nào.

### 2.4 Thanh bên trái (bề rộng cố định 240px, `flex:none`, `padding-right:8px`)

Từ trên xuống:

1. **Hàng đầu** — cao 44px, `padding:0 10px`, `gap:9px`:
   - Nút mũi tên lùi 30×30, `border-radius:4px`, `color:var(--txt)`,
     `text-decoration:none`, `flex:none`. Bên trong SVG 16×16 chevron trái
     `M15 5l-7 7 7 7`, `stroke-width:1.7`, `fill:none`.
     - `title` (tooltip): **"Quay lại màn hình chính"**
     - `href`: cùng đích với chip ở thanh tiêu đề — `GiongDoc - Màn hình chính v2 (nghe theo dòng).dc.html`
     - hover: `background:var(--sub-h)`
     - **Đây là chỗ thay đổi #1** — bản cũ là `<div>` trơ.
   - Chữ **"Cài đặt"** — `font-size:16px`, `font-weight:600`, `color:var(--txt)`.
2. **Danh sách nhóm** (`margin-top:4px`, `gap:2px`) — 6 mục, sinh từ `sections()`.
   Mỗi mục cao 38px, `padding:0 12px 0 13px`, `border-radius:5px`, `gap:11px`,
   `cursor:default`, `position:relative`.
   - Thanh chỉ dấu bên trái: `position:absolute; left:2px; top:50%; margin-top:-9px;`
     `width:3px; height:18px; border-radius:2px`.
   - Nhãn: `font-size:14px`, `color:var(--txt)`.

   | | Đang chọn | Không chọn |
   |---|---|---|
   | `background` | `var(--layer)` | `transparent` |
   | `border` | `1px solid var(--stroke)` | `1px solid transparent` |
   | thanh chỉ dấu | `var(--acc)` | `transparent` |
   | `font-weight` nhãn | `600` | `400` |

   Hover (mọi mục): `background:var(--sub-h)`. Bấm gọi `setState({ nav: i })`.
   `hint-placeholder-count="6"`.
3. **Chân thanh bên** (`margin-top:auto`, `padding-top:8px`,
   `border-top:1px solid var(--divider)`, `padding-left:4px`, `font-size:13px`,
   `color:var(--txt3)`, `line-height:1.5`), hai dòng cách nhau bằng `<br>`:
   - **"Giọng Việt 1.4.2"**
   - **"Bản quyền đã kích hoạt"**

### 2.5 Bảng nội dung bên phải (`flex:1`)

`background:var(--layer)`, `border:1px solid var(--stroke)`, `border-radius:8px`,
`overflow:hidden`, xếp dọc 3 tầng: đầu bảng 56px → vùng danh sách `flex:1` →
chân bảng 52px.

**Đầu bảng** — cao 56px, `padding:0 20px`, `gap:12px`,
`border-bottom:1px solid var(--divider)`:
- Tiêu đề nhóm `{{ sectionTitle }}` — `font-size:18px`, `font-weight:600`, `color:var(--txt)`.
- Câu phụ `{{ sectionHint }}` — `font-size:13px`, `color:var(--txt3)`.
- `margin-left:auto` → hộp tìm kiếm: bề rộng cố định **260px**, cao 32px,
  `padding:0 11px`, `border:1px solid var(--stroke2)`, `border-radius:4px`,
  `background:var(--ctl)`, `gap:9px`. Bên trong: kính lúp 15×15
  (`circle cx=11 cy=11 r=6` + `M15.5 15.5L20 20`, `stroke:var(--txt3)`,
  `stroke-width:1.6`) rồi chữ mờ **"Tìm cài đặt"** (`font-size:14px`, `color:var(--txt3)`).
  Đây là chữ tĩnh, **không phải `<input>`** — chưa nối chức năng tìm.

**Vùng danh sách** — `flex:1`, `min-height:0`, `overflow:hidden`,
`padding:16px 20px`, xếp dọc, `gap:10px`. `hint-placeholder-count="7"`
(nhưng nhóm nhiều nhất chỉ có 6 dòng).

Mỗi dòng cài đặt: `flex:none`, `min-height:60px`, `padding:12px 16px`,
`background:var(--layer2)`, `border:1px solid var(--stroke)`,
`border-radius:6px`, `gap:14px`, canh giữa theo chiều dọc. Từ trái sang phải:

1. **Cột dấu tròn** — bề rộng 22px, canh giữa, `color:var(--txt2)`.
   Hiện khi `r.iconDot` đúng (`renderVals()` luôn đặt `iconDot: true`, nên **mọi
   dòng đều có dấu tròn**). Dấu: 8×8, `border-radius:4px`,
   `background:var(--acc-soft)`, `border:2px solid var(--acc)` — vòng tròn rỗng
   viền xanh nhấn.
2. **Cột chữ** (`flex:1`, `min-width:0`):
   - Nhãn: `font-size:14px`, `font-weight:600`, `color:var(--txt)`.
   - Câu gợi ý: `font-size:13px`, `color:var(--txt3)`, `margin-top:2px`.
     Có dòng để **rỗng** (chuỗi `''`) — khi đó không có chữ gợi ý.
3. **Cột điều khiển** — 1 trong 4 dạng, xem mục 4.

**Chân bảng** — cao 52px, `padding:0 20px`, `gap:10px`,
`border-top:1px solid var(--divider)`, `background:var(--layer2)`:
- Bên trái: câu **"Thay đổi được lưu ngay."** — `font-size:13px`, `color:var(--txt3)`.
- `margin-left:auto` → 2 nút, `gap:8px`:
  - **"Đặt lại mặc định"** — nút mờ (ghost): cao 34px, `padding:0 14px`,
    `border-radius:4px`, `font-size:14px`, `color:var(--txt2)`, `cursor:default`,
    không viền không nền. Hover `background:var(--sub-h)`. **Chưa nối chức năng.**
  - **"Đóng"** — nút chính: cao 34px, `padding:0 16px`, `border-radius:4px`,
    `background:var(--acc)`, `color:var(--acc-txt)`, `font-size:14px`,
    `font-weight:600`, `cursor:default`, `text-decoration:none`.
    Hover `background:var(--acc-h)`.
    `href` → `GiongDoc - Màn hình chính v2 (nghe theo dòng).dc.html`.
    **Đây là chỗ thay đổi #2** — bản cũ là `<div>` trơ.

---

## 3. Sáu nhóm cài đặt — nội dung ĐẦY ĐỦ, nguyên văn

Nguồn: hàm `sections()`. Định dạng mỗi nhóm: `[tiêu đề, câu phụ, [các dòng]]`.
Định dạng mỗi dòng: `[dạng, nhãn, câu gợi ý, giá trị…]`.

### Nhóm 1 (nav=0, MẶC ĐỊNH) — "Chung"
Câu phụ: **"Ngôn ngữ, khởi động, giao diện"**

| # | Dạng | Nhãn | Câu gợi ý | Giá trị / mặc định |
|---|---|---|---|---|
| 0 | select | "Ngôn ngữ giao diện" | "Áp dụng cho toàn bộ ứng dụng" | "Tiếng Việt" |
| 1 | select | "Chủ đề" | "Theo hệ thống, sáng hoặc tối" | "Theo hệ thống Windows" |
| 2 | toggle | "Mở tệp gần nhất khi khởi động" | "Tự mở lại tệp bạn đang làm việc" | **BẬT** |
| 3 | toggle | "Thu nhỏ xuống khay hệ thống" | "Giữ ứng dụng chạy nền khi đóng cửa sổ" | **TẮT** |
| 4 | select | "Cỡ chữ vùng soạn thảo" | "Ảnh hưởng đến vùng soạn thảo, không đổi giao diện" | "18 px (mặc định)" |
| 5 | toggle | "Tự động soát văn bản khi mở tệp" | "Báo lỗi số tiền, tên riêng, ký tự lạ" | **BẬT** |

### Nhóm 2 (nav=1) — "Giọng & mô hình"
Câu phụ: **"Mô hình đọc, tăng tốc phần cứng"**

| # | Dạng | Nhãn | Câu gợi ý | Giá trị / mặc định |
|---|---|---|---|---|
| 0 | select | "Mô hình mặc định" | "Dùng khi tạo hồ sơ mới" | "VieNeu v3 Turbo" |
| 1 | toggle | "Tải mô hình sẵn khi mở ứng dụng" | "Mất thêm ~40 giây khi khởi động, bù lại phát nhanh" | **BẬT** |
| 2 | toggle | "Tăng tốc bằng GPU (NVIDIA)" | "Phát hiện: RTX 3060 · nhanh hơn khoảng 3 lần" | **BẬT** |
| 3 | select | "Số luồng CPU" | "Nhiều luồng xử lý nhanh hơn nhưng máy nóng hơn" | "8 luồng" |
| 4 | path | "Nơi lưu mô hình" | "Mỗi mô hình chiếm 0,6–3,2 GB" | `D:\GiongViet\Models` |
| 5 | toggle | "Giải phóng mô hình khi rảnh 10 phút" | "Trả lại RAM cho các ứng dụng khác" | **TẮT** |

### Nhóm 3 (nav=2) — "Xuất file"
Câu phụ: **"Định dạng, nơi lưu, đặt tên"**

| # | Dạng | Nhãn | Câu gợi ý | Giá trị / mặc định |
|---|---|---|---|---|
| 0 | select | "Định dạng mặc định" | "Dùng cho mọi lần xuất" | "WAV 24 bit · 24.000 Hz" |
| 1 | path | "Thư mục xuất mặc định" | "Có thể đổi ở từng lần xuất" | `Documents\GiongViet\Xuất` |
| 2 | select | "Quy tắc đặt tên" | "Tránh ghi đè tệp cũ" | "{tên tệp}-{ngày}" |
| 3 | toggle | "Mở thư mục sau khi xuất" | *(rỗng)* | **BẬT** |
| 4 | toggle | "Thông báo khay hệ thống khi xuất xong" | *(rỗng)* | **BẬT** |
| 5 | select | "Khoảng lặng giữa các mục" | "Áp dụng cho văn bản dạng danh sách" | "0,5 giây" |

### Nhóm 4 (nav=3) — "Phím tắt"
Câu phụ: **"Xem và đổi phím tắt"**

| # | Dạng | Nhãn | Câu gợi ý | Giá trị / mặc định |
|---|---|---|---|---|
| 0 | select | "Phát / tạm dừng" | *(rỗng)* | "Space" |
| 1 | select | "Câu trước / câu sau" | *(rỗng)* | "Ctrl + ← / →" |
| 2 | select | "Xuất file âm thanh" | *(rỗng)* | "Ctrl + E" |
| 3 | select | "Soát văn bản" | *(rỗng)* | **"Ctrl + K"** ← đổi từ "Ctrl + Shift + K" |
| 4 | select | "Chèn thẻ cảm xúc" | *(rỗng)* | "Alt + 1…3" |
| 5 | toggle | "Cho phép phím tắt khi cửa sổ chạy nền" | "Điều khiển phát mà không cần mở cửa sổ" | **TẮT** |

### Nhóm 5 (nav=4) — "Bộ nhớ"
Câu phụ: **"Dung lượng mô hình và bộ đệm"**

| # | Dạng | Nhãn | Câu gợi ý | Giá trị / mặc định |
|---|---|---|---|---|
| 0 | meter | "Mô hình giọng đã tải" | "3 mô hình · 6,4 GB" | đã dùng "6,4 GB đã dùng", còn "còn 128 GB", thanh đầy **5%** |
| 1 | path | "Bộ đệm audio tạm" | "Xoá được an toàn" | "1,2 GB" |
| 2 | toggle | "Tự xoá bộ đệm khi đóng ứng dụng" | *(rỗng)* | **TẮT** |
| 3 | select | "Giới hạn RAM cho mô hình" | "Đặt thấp nếu máy hay bị đầy bộ nhớ" | "4 GB" |
| 4 | toggle | "Cảnh báo khi RAM trống dưới 2 GB" | "Tránh lỗi không tải được mô hình" | **BẬT** |

Nhóm này chỉ có **5 dòng** (các nhóm 1–4 có 6 dòng).

### Nhóm 6 (nav=5) — "Về Giọng Việt"
Câu phụ: **"Phiên bản, cập nhật, giấy phép"**

| # | Dạng | Nhãn | Câu gợi ý | Giá trị / mặc định |
|---|---|---|---|---|
| 0 | select | "Kênh cập nhật" | "Ổn định hoặc thử nghiệm" | "Ổn định" |
| 1 | toggle | "Tự kiểm tra cập nhật" | *(rỗng)* | **BẬT** |
| 2 | path | "Giấy phép" | "Kích hoạt cho 1 máy" | "GD-2026-XXXX-4821" |
| 3 | toggle | "Gửi báo cáo lỗi ẩn danh" | "Không gửi nội dung văn bản của bạn" | **TẮT** |

Nhóm này chỉ có **4 dòng**.

Lưu ý dòng `path` **"Giấy phép"** và **"Bộ đệm audio tạm"**: dùng dạng `path`
nên vẫn hiện nút **"Đổi…"** bên phải, dù về nghĩa "đổi giấy phép" / "đổi bộ đệm"
không phải chọn thư mục. Đây là điểm cần cân nhắc khi làm thật (nút "Đổi…" ở
dòng bộ đệm nên là "Xoá…", ở dòng giấy phép nên là "Nhập mã…").

---

## 4. Bốn dạng điều khiển — trạng thái đổi những gì

### 4.1 `toggle` — công tắc bật/tắt (CÓ tương tác thật)

Viên thuốc **44×22**, `flex:none`, `border-radius:11px`, `padding:0 3px`,
`display:flex; align-items:center`, `cursor:default`.
Núm bên trong: **14×14**, `border-radius:7px`.

| | BẬT (`on = true`) | TẮT (`on = false`) |
|---|---|---|
| `background` đường ray | `var(--acc)` | `transparent` |
| `border` (1px solid) | `var(--acc)` | `var(--stroke2)` |
| màu núm | `var(--acc-txt)` | `var(--txt2)` |
| `justify-content` | `flex-end` (núm sang phải) | `flex-start` (núm sang trái) |

Bấm vào → lật giá trị: sao `state.toggles`, đặt `t[key] = !on`, `setState`.
Khoá `key = "{nav}:{chỉ số dòng}"` — nghĩa là trạng thái đã lật **được giữ lại
khi đổi nhóm rồi quay lại**, và khi đổi chủ đề Sáng/Tối. Giá trị đọc theo:
`state.toggles[key] === undefined ? mặc_định_trong_sections : state.toggles[key]`.

### 4.2 `select` — hộp chọn (KHÔNG tương tác — chỉ hiện giá trị)

Bề rộng cố định **210px**, cao 34px, `padding:0 8px 0 11px`,
`border:1px solid var(--stroke2)`, `border-radius:4px`, `background:var(--ctl)`,
`gap:8px`, `cursor:default`. Hover `background:var(--ctl-h)`.
- Chữ giá trị: `flex:1`, `font-size:14px`, `color:var(--txt)`,
  `white-space:nowrap; overflow:hidden; text-overflow:ellipsis` (cắt bằng dấu ba chấm).
- Mũi tên xuống 13×13 (`M6 9.5l6 6 6-6`), `stroke:var(--txt2)`, `stroke-width:1.8`.

**Không có `onClick`, không có danh sách bung ra.** Bản thiết kế chỉ tả hình
dáng hộp chọn ở trạng thái đóng — phần danh sách bung ra phải tự thiết kế khi làm thật.

### 4.3 `path` — đường dẫn + nút "Đổi…" (KHÔNG tương tác)

Nhóm ngang `flex:none`, `gap:8px`:
- Chữ đường dẫn: `font-size:13px`, `color:var(--txt2)`, **`max-width:260px`**,
  `white-space:nowrap; overflow:hidden; text-overflow:ellipsis`.
- Nút **"Đổi…"** (dấu ba chấm là ký tự `…`, không phải ba dấu chấm rời):
  cao 32px, `padding:0 13px`, `border-radius:4px`, `background:var(--ctl)`,
  `border:1px solid var(--stroke2)`, `font-size:14px`, `color:var(--txt)`,
  `cursor:default`. Hover `background:var(--ctl-h)`. Không có `onClick`.

### 4.4 `meter` — thanh dung lượng (KHÔNG tương tác)

Khối bề rộng cố định **280px**, `flex:none`:
- Đường ray: cao 6px, `border-radius:3px`, `background:var(--rail)`,
  `opacity:.9`, `overflow:hidden`.
- Phần đã dùng: cao 6px, `border-radius:3px`, `background:var(--acc)`,
  `width` = giá trị `pct` (ở dòng duy nhất dùng meter là **`5%`**).
- Dưới thanh (`margin-top:6px`, `font-size:12.5px`, `color:var(--txt3)`,
  `font-variant-numeric:tabular-nums`, `justify-content:space-between`):
  chữ bên trái = đã dùng (**"6,4 GB đã dùng"**), chữ bên phải = còn trống
  (**"còn 128 GB"**).

Cảnh báo số liệu: câu gợi ý nói "3 mô hình · 6,4 GB", chữ dưới thanh nói
"6,4 GB đã dùng" và "còn 128 GB" — tổng ~134 GB, mà thanh chỉ đầy `5%`
(5% của 134 GB ≈ 6,7 GB, khớp xấp xỉ). Khi làm thật phải tính `pct` từ số liệu
thật, đừng viết cứng `5%`.

---

## 5. Toàn bộ chuỗi tiếng Việt hiện ra màn hình

Ghi nguyên văn, kể cả dấu và khoảng trắng. Sắp theo vị trí.

**Ngoài khung cửa sổ (dải nút bản mẫu):**
- "Cài đặt" (nhãn in hoa của dải nút)
- "Sáng"
- "Tối"

**Thanh tiêu đề:**
- "Cài đặt — Giọng Việt"
- "Màn hình chính"
- "Quay lại màn hình chính" *(tooltip của chip)*

**Thanh bên trái:**
- "Quay lại màn hình chính" *(tooltip của nút mũi tên lùi)*
- "Cài đặt"
- "Chung" · "Giọng & mô hình" · "Xuất file" · "Phím tắt" · "Bộ nhớ" · "Về Giọng Việt"
- "Giọng Việt 1.4.2"
- "Bản quyền đã kích hoạt"

**Đầu bảng phải (đổi theo nhóm đang chọn):**
- Tiêu đề: "Chung" / "Giọng & mô hình" / "Xuất file" / "Phím tắt" / "Bộ nhớ" / "Về Giọng Việt"
- Câu phụ: "Ngôn ngữ, khởi động, giao diện" / "Mô hình đọc, tăng tốc phần cứng" /
  "Định dạng, nơi lưu, đặt tên" / "Xem và đổi phím tắt" /
  "Dung lượng mô hình và bộ đệm" / "Phiên bản, cập nhật, giấy phép"
- "Tìm cài đặt" *(chữ mờ trong hộp tìm)*

**Trong danh sách:** mọi nhãn, câu gợi ý và giá trị đã liệt kê đủ ở mục 3.
Nút lặp lại ở các dòng `path`: "Đổi…"

**Chân bảng phải:**
- "Thay đổi được lưu ngay."
- "Đặt lại mặc định"
- "Đóng"

**Không có** câu trạng thái rỗng, câu lỗi, hay câu đang tải nào trong bản thiết
kế này. Nếu làm thật cần các câu đó (ví dụ chưa dò được GPU, không đọc được
thư mục mô hình) thì phải soạn thêm — thiết kế chưa nói.

---

## 6. Biến CSS — giá trị bộ sáng và bộ tối

Bộ sáng đặt trên `:root`. Bộ tối đặt trên `:root[data-theme='dark']`
(thuộc tính này do `applyTheme()` gắn vào `<html>`).

| Biến | Sáng | Tối | Dùng ở đâu |
|---|---|---|---|
| `--bg` | `#f3f3f3` | `#202020` | nền khung cửa sổ, nền thanh tiêu đề |
| `--layer` | `#ffffff` | `#2b2b2b` | nền bảng phải, nền mục nav đang chọn |
| `--layer2` | `#fafafa` | `#272727` | nền từng dòng cài đặt, nền chân bảng |
| `--stroke` | `rgba(0,0,0,.0578)` | `rgba(255,255,255,.07)` | viền bảng phải, viền dòng cài đặt, viền nav đang chọn |
| `--stroke2` | `rgba(0,0,0,.16)` | `rgba(255,255,255,.10)` | viền hộp tìm, hộp chọn, nút "Đổi…", viền công tắc TẮT |
| `--divider` | `#e5e5e5` | `#303030` | vạch chia đầu bảng / chân bảng / chân thanh bên |
| `--txt` | `#1a1a1a` | `#ffffff` | chữ chính, nhãn dòng, giá trị hộp chọn |
| `--txt2` | `#5d5d5d` | `rgba(255,255,255,.73)` | tiêu đề cửa sổ, chip, đường dẫn, núm công tắc TẮT, nút "Đặt lại mặc định" |
| `--txt3` | `#767676` | `rgba(255,255,255,.60)` | câu gợi ý, chữ mờ hộp tìm, chân thanh bên, nhãn thanh dung lượng |
| `--dis` | `#a3a3a3` | `rgba(255,255,255,.38)` | *(khai báo nhưng KHÔNG dùng trong tệp này — dành cho trạng thái bị làm mờ)* |
| `--ctl` | `#fdfdfd` | `rgba(255,255,255,.06)` | nền hộp tìm, hộp chọn, nút "Đổi…" |
| `--ctl-h` | `#f6f6f6` | `rgba(255,255,255,.084)` | nền các thứ trên khi trỏ chuột vào |
| `--sub-h` | `rgba(0,0,0,.037)` | `rgba(255,255,255,.06)` | nền chip "Màn hình chính"; nền hover của nav, nút lùi, nút cửa sổ, "Đặt lại mặc định" |
| `--acc` | `#0067c0` | `#4cc2ff` | màu nhấn: biểu tượng app, thanh chỉ dấu nav, công tắc BẬT, thanh dung lượng đã dùng, nút "Đóng", viền dấu tròn |
| `--acc-h` | `#1a75c6` | `#47b1e8` | nút "Đóng" khi trỏ chuột vào |
| `--acc-txt` | `#ffffff` | `#000000` | chữ trên nền nhấn: chữ "Đóng", núm công tắc BẬT, vạch trong biểu tượng app |
| `--acc-soft` | `rgba(0,103,192,.09)` | `rgba(76,194,255,.12)` | nền dấu tròn đầu mỗi dòng |
| `--chip-bg` | `rgba(0,0,0,.055)` | `rgba(255,255,255,.09)` | *(khai báo nhưng KHÔNG dùng trong tệp này)* |
| `--chip-bd` | `rgba(0,0,0,.09)` | `rgba(255,255,255,.14)` | *(khai báo nhưng KHÔNG dùng)* |
| `--chip-fg` | `#4a4a4a` | `rgba(255,255,255,.82)` | *(khai báo nhưng KHÔNG dùng)* |
| `--ok` | `#0f7b0f` | `#6ccb5f` | *(khai báo nhưng KHÔNG dùng — màu "xong/tốt")* |
| `--warn` | `#9d5d00` | `#f7b84b` | *(khai báo nhưng KHÔNG dùng — màu cảnh báo)* |
| `--rail` | `#868686` | `#9a9a9a` | đường ray thanh dung lượng |
| `--shadow` | `0 8px 16px rgba(0,0,0,.14)` | `0 8px 16px rgba(0,0,0,.36)` | *(khai báo nhưng KHÔNG dùng — khung cửa sổ tự viết bóng riêng `0 16px 32px rgba(0,0,0,.22)`)* |

Ngoài biến, có 3 màu **viết cứng** không theo biến:
- nền trang ngoài và `body`: `#e6e6e6`
- dải nút bản mẫu: `#fdfdfd`, viền `rgba(0,0,0,.09)`, nút đang chọn `#0067c0` chữ `#fff`, nút không chọn chữ `#5d5d5d`
- nút Đóng cửa sổ khi hover: `#c42b1c` chữ `#fff`
- viền khung cửa sổ `rgba(0,0,0,.22)`, bóng `0 16px 32px rgba(0,0,0,.22)`

Nghĩa là **dải nút bản mẫu và nền trang không đổi màu theo chủ đề** — chỉ phần
trong khung cửa sổ đổi. Điều này đúng vì dải nút là công cụ của bản mẫu.

Có sẵn quy tắc chung cho liên kết: `a{color:var(--acc)} a:hover{color:var(--acc-h)}`
— nhưng cả 3 liên kết trong tệp đều tự đặt `color` riêng nên quy tắc này bị ghi đè.

Phông: `<link rel="stylesheet" href="_ds/bssaas-adminkit-design-system-60ba9c0b-5497-49a2-b7c1-ba0772d8cf30/fonts/inter.css">`
nhưng ngăn xếp phông thật là `'Segoe UI Variable Text','Segoe UI',Inter,system-ui,sans-serif`
— tức **Segoe UI trước, Inter chỉ là dự phòng**.

---

## 7. Phím tắt nêu trong thiết kế

Toàn bộ nằm ở nhóm "Phím tắt" (dạng `select`, chỉ hiện chứ chưa đổi được):

| Việc | Phím |
|---|---|
| Phát / tạm dừng | `Space` |
| Câu trước / câu sau | `Ctrl + ←` / `Ctrl + →` (ghi gộp: "Ctrl + ← / →") |
| Xuất file âm thanh | `Ctrl + E` |
| Soát văn bản | `Ctrl + K` **(bản cũ: `Ctrl + Shift + K`)** |
| Chèn thẻ cảm xúc | `Alt + 1…3` |

Cộng thêm một công tắc liên quan: "Cho phép phím tắt khi cửa sổ chạy nền" —
mặc định **TẮT**, câu gợi ý "Điều khiển phát mà không cần mở cửa sổ".

**Bản thiết kế màn Cài đặt không tự nghe phím tắt nào** — không có `keydown`,
không có `Esc để đóng`. Nếu muốn `Esc` đóng cửa sổ Cài đặt thì phải tự thêm,
thiết kế chưa nói.

---

## 8. Hộp thoại / nhiều bước

**Không có.** Tệp này không có hộp thoại, không có luồng nhiều bước, không có
điều kiện chặn/cho đi tiếp. Mọi thứ nằm trên một trang, đổi nội dung theo `nav`.

Những chỗ **đáng lẽ phải mở hộp thoại nhưng thiết kế chưa vẽ**:
- nút "Đổi…" ở 4 dòng `path` (chọn thư mục mô hình, thư mục xuất, bộ đệm, giấy phép)
- mọi hộp `select` (12 hộp) — chưa có danh sách bung ra
- "Đặt lại mặc định" — thường cần một câu hỏi xác nhận
- hộp "Tìm cài đặt" — chưa có kết quả tìm, chưa có trạng thái "không tìm thấy"

---

## 9. Việc cần làm khi dựng thật — chốt lại

1. Dải nút Sáng/Tối là **công cụ của bản mẫu**, KHÔNG dựng vào chương trình.
   Chủ đề thật lấy từ dòng cài đặt "Chủ đề" trong nhóm "Chung".
2. Hai đường quay về màn hình chính (mũi tên lùi ở thanh bên + nút "Đóng" ở chân
   bảng) phải nối chức năng thật — bản thiết kế mới đã đổi chúng thành liên kết,
   đúng KPI "không bày nút giả".
3. Chip "Màn hình chính" ở thanh tiêu đề là **đường thứ ba** về cùng đích. Cân
   nhắc có cần cả ba hay không — với người lớn tuổi, ba đường về cùng một chỗ
   dễ gây rối; nhưng nếu giữ thì cả ba đều phải chạy.
4. Ba nút cửa sổ (thu nhỏ / phóng to / đóng) chưa có tooltip — nên thêm.
5. Hộp "Tìm cài đặt" là chữ tĩnh, **chưa phải `<input>`**. Nếu chưa làm chức
   năng tìm thì đừng bày hộp này ra (KPI "không bày nút giả").
6. Câu "Thay đổi được lưu ngay." là một cam kết — nghĩa là **không có nút Lưu**,
   mọi thay đổi phải ghi xuống `cauhinh.ini` ngay khi người dùng đổi.
7. Nhóm nav 1–4 có 6 dòng, nhóm 5 có 5 dòng, nhóm 6 có 4 dòng. Vùng danh sách
   `overflow:hidden` (không `auto`) — nếu thật có nhiều dòng hơn 6 thì phải đổi
   sang cuộn được, thiết kế chưa tính chỗ đó.
8. Số liệu trong bản mẫu là số minh hoạ ("RTX 3060", "6,4 GB", "còn 128 GB",
   "GD-2026-XXXX-4821", "Giọng Việt 1.4.2") — phải lấy từ máy thật, không viết cứng.
9. Dòng `path` "Bộ đệm audio tạm" và "Giấy phép" dùng nút "Đổi…" chưa đúng nghĩa
   — nên đổi nhãn nút cho từng dòng.
