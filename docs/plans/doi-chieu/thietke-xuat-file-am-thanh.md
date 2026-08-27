# Bản kiểm kê trạng thái — Màn "Xuất file âm thanh"

Nguồn: `design_handoff_giongdoc2/designs-goc/GiongDoc - Xuất file âm thanh.dc.html`
(kéo từ dự án thiết kế `5c70b20f-0f8b-4da8-ad19-800b0fb6ae19`, ở gốc dự án thiết kế, ngày 17/8/2026)

> Thư mục ban đầu tên `design_handoff_giongdoc`, bị một tiến trình khác đổi thành
> `design_handoff_giongdoc2` lúc 17:19 ngày 17/8/2026 trong khi việc này đang chạy.
> Nội dung tệp không đổi (`md5 = f71f452cf5429d05335e9d14c54069e8`, 22.811 byte).

So với snapshot cũ `designs/GiongDoc - Xuất file âm thanh.dc.html`: **KHÁC** — 3 chỗ, đều là
thay đổi thiết kế thật (xem mục 10).

Mục tiêu tài liệu này: đọc xong là biết chính xác phải dựng gì, **không cần mở lại tệp thiết kế**.

---

## 1. Dải nút điều khiển phía trên khung cửa sổ

Dải nút nằm NGOÀI khung cửa sổ mô phỏng (bản mẫu tương tác, không phải phần của ứng dụng).
Rộng 1440px, canh giữa, `margin-bottom:14px`, `display:flex; gap:14px; flex-wrap:wrap`.

Bản thiết kế này **không dùng tiền tố nhãn** kiểu "Tình huống: …" / "Mở từ: …" / "Bước: …".
Chỉ có một nhãn chương ở đầu dòng rồi hai nhóm nút viên thuốc.

| Thứ tự | Thành phần | Giá trị |
|---|---|---|
| 1 | Nhãn chương (chữ, không bấm được) | `"Hộp thoại xuất file"` |
| 2 | Nhóm công tắc **Trạng thái** (bên trái) | `"Cấu hình"` · `"Đang xuất"` · `"Hoàn tất"` |
| 3 | Nhóm công tắc **Bộ màu** (đẩy sát phải, `margin-left:auto`) | `"Sáng"` · `"Tối"` |

Mã nội bộ và mặc định (khai báo trong `data-props`, đều thuộc section `"Trạng thái"`):

| Công tắc | Mã trị | Mặc định |
|---|---|---|
| `state` | `cau_hinh` \| `dang_xuat` \| `hoan_tat` | `cau_hinh` |
| `theme` | `sang` \| `toi` | `sang` |

Định dạng nhãn chương: `font-size:12px; letter-spacing:.05em; text-transform:uppercase;
color:#5d5d5d; font-weight:600`.

Định dạng hộp chứa nút: `display:flex; gap:3px; padding:3px; background:#fdfdfd;
border:1px solid rgba(0,0,0,.09); border-radius:6px`.

Định dạng từng nút: `border:0; cursor:pointer; font:600 13px 'Segoe UI Variable Text','Segoe UI',
Inter,sans-serif; padding:7px 12px; border-radius:4px`.
- Đang chọn: `background:#0067c0; color:#fff`
- Không chọn: `background:transparent; color:#5d5d5d`

Đổi bộ màu thực hiện bằng `document.documentElement.setAttribute('data-theme', theme==='toi' ? 'dark' : 'light')`,
gọi ở cả `componentDidMount` và `componentDidUpdate`.

### Trạng thái nội bộ (KHÔNG có trên dải nút, đổi bằng cách bấm trong hộp thoại)

| Biến | Miền giá trị | Mặc định |
|---|---|---|
| `split` | 0 · 1 · 2 (nhóm nút tròn "Tách tệp") | `0` |
| `gap` | 0 → 20 (thanh trượt khoảng lặng, bước 1 ≙ 0,1 giây) | `5` (⇒ "0,5 giây") |
| `checks` | mảng 3 phần tử bật/tắt | `[true, false, true]` |

---

## 2. Bố cục tổng thể

### Trang ngoài
`min-height:100vh; padding:20px 24px 40px; background:#e6e6e6;
font-family:'Segoe UI Variable Text','Segoe UI',Inter,system-ui,sans-serif;
font-size:14px; color:#1a1a1a`.

### Khung cửa sổ (bề rộng CỐ ĐỊNH)
`position:relative; width:1440px; height:900px; margin:0 auto; background:var(--bg);
border:1px solid rgba(0,0,0,.22); border-radius:8px; box-shadow:0 16px 32px rgba(0,0,0,.22);
overflow:hidden; display:flex; flex-direction:column; color:var(--txt)`.

Từ trên xuống, 4 tầng:

**(a) Thanh tiêu đề — cao 32px**, `padding-left:12px`, `background:var(--bg)`.
Nhóm trái, `gap:9px`:
- Biểu tượng ứng dụng 16×16, `border-radius:3px`, `background:var(--acc)`; bên trong SVG 10×10
  hình 4 vạch cân bằng âm (`path d="M4 9v6M9 5v14M14 8v8M19 11v2"`, `stroke:var(--acc-txt)`,
  `stroke-width:2.6`, `stroke-linecap:round`).
- Chữ tiêu đề `"thongbao-quoc-khanh.txt — Giọng Việt"`, 12.5px, `color:var(--txt2)`.
- Nút viên thuốc quay lại: cao 22px, `padding:0 10px 0 7px`, `border-radius:11px`,
  `background:var(--sub-h)`, `color:var(--txt2)`, 12px, `text-decoration:none`, `white-space:nowrap`;
  hover đổi `color:var(--txt)`; **tooltip (`title`) = `"Quay lại màn hình chính"`**;
  nhãn `"Màn hình chính"`, kèm mũi chevron trái SVG 11×11 (`path d="M14 6l-6 6 6 6"`).
  Đích: `GiongDoc - Màn hình chính v2 (nghe theo dòng).dc.html`.

Nhóm phải (`margin-left:auto`) — 3 nút cửa sổ, mỗi nút 46×32, `color:var(--txt3)`:
thu nhỏ (một gạch `M1 6h10`), phóng to (ô vuông `rect rx=1`), đóng (chữ X `M1.5 1.5l9 9M10.5 1.5l-9 9`).

**(b) Thân — `flex:1; min-height:0; display:flex; padding:8px 8px 0`, và `opacity:.5`**
(cố tình làm mờ vì hộp thoại đang che). Ba cột:
- Cột trái **rộng 240px** cố định, `padding-right:8px`, `gap:6px`: khối cao 34px
  (`background:var(--layer)`, viền `var(--stroke)`, bo 5px) → khối cao 52px cùng kiểu →
  hai khối cao 52px `background:var(--sub-h)`, bo 5px, không viền.
- Cột giữa `flex:1`: thẻ `background:var(--layer)`, viền `var(--stroke)`, bo 8px,
  `padding:14px 16px`, `gap:14px`; trong đó **14 dòng bóng** cao 10px, bo 3px,
  `background:var(--sub-h)`, bề rộng lần lượt: `62%, 48%, 8%, 54%, 72%, 30%, 30%, 30%, 30%, 30%,
  30%, 30%, 30%, 30%`.
- Cột phải **rộng 320px** cố định, `padding-left:8px`: một thẻ cao 320px
  (`background:var(--layer)`, viền `var(--stroke)`, bo 8px).

**(c) Thanh dưới — cao 72px**, `border-top:1px solid var(--divider)`, `background:var(--bg)`, `opacity:.5`.

**(d) Lớp che phủ** — `position:absolute; inset:0; background:var(--scrim);
display:flex; align-items:center; justify-content:center`.
Bên trong chỉ hiện **đúng một** trong ba hộp thoại, theo `state`.

---

## 3. Trạng thái "Cấu hình" (`state = cau_hinh`, cờ `isConfig`)

Hộp thoại **rộng 600px** (rộng hơn hai hộp còn lại): `background:var(--layer)`,
`border:1px solid var(--stroke2)`, `border-radius:8px`,
`box-shadow:0 32px 64px rgba(0,0,0,.32)`, `overflow:hidden`.

### 3.1 Phần đầu — `padding:22px 24px 4px`
- Tiêu đề: `"Xuất file âm thanh"` — 20px, weight 600, `color:var(--txt)`.
- Phụ đề: `"thongbao-quoc-khanh.txt · 15 đoạn · giọng Ngọc Linh"` — 14px, `color:var(--txt2)`,
  `margin-top:4px`.

### 3.2 Phần thân — `padding:16px 24px 20px; display:flex; flex-direction:column; gap:16px`

**Hàng 1 — Tên tệp + Định dạng** (`display:flex; gap:12px`)

| Ô | Bề rộng | Nhãn | Nội dung |
|---|---|---|---|
| Tên tệp | `flex:1` | `"Tên tệp"` | `"thongbao-quoc-khanh"` + phần `".wav"` tô `var(--txt3)` |
| Định dạng | **150px** | `"Định dạng"` | `"WAV 24 bit"` + mũi chevron xuống |

- Nhãn: 14px, `color:var(--txt2)`, `margin-bottom:6px`.
- Ô tên tệp: cao 36px, `padding:0 10px`, `border:1px solid var(--stroke2)` nhưng
  **`border-bottom-width:2px; border-bottom-color:var(--acc)`** — tức đang ở trạng thái được
  tiêu điểm (gạch chân màu nhấn kiểu WinUI). `border-radius:4px`, `background:var(--ctl)`, 14px.
- Ô định dạng: cao 36px, `padding:0 8px 0 10px`, viền `var(--stroke2)`, bo 4px,
  `background:var(--ctl)`; chữ `flex:1`; chevron SVG 13×13 (`path d="M6 9.5l6 6 6-6"`,
  `stroke:var(--txt2)`, `stroke-width:1.8`).

**Hàng 2 — Lưu vào**
- Nhãn `"Lưu vào"` 14px `var(--txt2)`, `margin-bottom:6px`.
- Hàng `display:flex; gap:8px`:
  - Ô đường dẫn `flex:1`, cao 36px, `padding:0 10px`, viền `var(--stroke2)`, bo 4px,
    `background:var(--ctl)`, `white-space:nowrap; overflow:hidden; text-overflow:ellipsis`;
    nội dung `"C:\Users\Tuan\Documents\GiongViet\Xuất"`.
  - Nút `"Chọn…"` cao 36px, `padding:0 14px`, viền `var(--stroke2)`, bo 4px,
    `background:var(--ctl)`, hover `background:var(--ctl-h)`.

**Hàng 3 — Tách tệp** (nhóm nút tròn, chọn một)
- Nhãn `"Tách tệp"` 14px `var(--txt2)`, `margin-bottom:7px`.
- Danh sách dọc `gap:2px`; mỗi dòng cao 34px, `padding:0 8px`, bo 4px,
  hover `background:var(--sub-h)`.
- Nút tròn: vòng 18×18, bo 9px, `border:1.5px solid` — đang chọn `var(--acc)`, không chọn
  `var(--stroke2)`; điểm giữa 8×8 bo 4px — đang chọn `var(--acc)`, không chọn `transparent`.
- Nhãn 14px `var(--txt)`; chú thích 13px `var(--txt3)`.

| # | Nhãn (nguyên văn) | Chú thích (nguyên văn) | Mặc định |
|---|---|---|---|
| 0 | `"Một tệp duy nhất"` | `"11,6 MB"` | **đang chọn** |
| 1 | `"Mỗi đoạn một tệp"` | `"16 tệp"` | |
| 2 | `"Cắt theo độ dài"` | `"mỗi 10 phút một tệp"` | |

**Hàng 4 — Thanh trượt khoảng lặng**
- Dòng đầu `display:flex; justify-content:space-between`, 14px `var(--txt2)`, `margin-bottom:4px`:
  - trái: `"Khoảng lặng giữa các đoạn"`
  - phải: giá trị, `font-weight:600`, `color:var(--txt)`, `font-variant-numeric:tabular-nums`
- Công thức nhãn giá trị: `(gap/10).toFixed(1)` rồi thay `"."` bằng `","`, cộng `" giây"`.
  Miền `gap` 0→20 ⇒ nhãn từ `"0,0 giây"` đến `"2,0 giây"`, bước 0,1 giây.
  **Mặc định `gap=5` ⇒ `"0,5 giây"`.**
- Rãnh: hộp cao 20px; đường ray phủ hết bề rộng, cao 4px, bo 2px, `background:var(--rail)`,
  `opacity:.5`; phần đã tô cao 4px bo 2px `background:var(--acc)`, bề rộng `= gapPct`.
- Núm: 20×20, bo 10px, `background:var(--layer)`, `border:1px solid var(--stroke2)`,
  `box-shadow:0 1px 3px rgba(0,0,0,.18)`, `margin-left:-10px`, `left = gapPct`;
  điểm giữa núm 11×11 bo 6px `background:var(--acc)`.
- `gapPct = Math.round(gap/20*100) + '%'` ⇒ mặc định **25%**.
- Bấm bất kỳ đâu trên rãnh: lấy `rect` của rãnh, `f = clamp((clientX - rect.left)/rect.width, 0, 1)`,
  đặt `gap = Math.round(f*20)`. (Không có kéo thả, chỉ một cú bấm.)

**Hàng 5 — Ba ô đánh dấu** (`gap:2px`; mỗi dòng cao 34px, `padding:0 8px`, bo 4px,
hover `background:var(--sub-h)`)
- Ô vuông 18×18, bo 3px, `border:1.5px solid` — bật `var(--acc)`, tắt `var(--stroke2)`;
  `background` — bật `var(--acc)`, tắt `transparent`; màu dấu tích `var(--acc-txt)`.
- Dấu tích **chỉ vẽ khi đang bật**: SVG 12×12, `path d="M5 12.5l4.5 4.5L19 7"`, `stroke-width:3`.
- Nhãn 14px `color:var(--txt)`.

| # | Nhãn (nguyên văn) | Mặc định |
|---|---|---|
| 0 | `"Đọc số tiền thành chữ (500.000 → năm trăm nghìn)"` | **BẬT** |
| 1 | `"Đọc thẻ cảm xúc thành âm thanh"` | tắt |
| 2 | `"Chèn 1 giây im lặng ở đầu tệp"` | **BẬT** |

**Hàng 6 — Băng thông báo ước tính**
- `display:flex; align-items:center; gap:9px; padding:11px 12px;
  background:var(--acc-soft); border-radius:4px`.
- Biểu tượng chữ "i" trong vòng tròn, SVG 16×16, `fill:currentColor`, màu `var(--acc)`
  (`path d="M12 2a10 10 0 100 20 10 10 0 000-20zm1 15h-2v-6h2zm0-8h-2V7h2z"`).
- Chữ 14px `color:var(--txt)`, **đổi theo `split`**:

| `split` | Chuỗi ước tính (nguyên văn) |
|---|---|
| 0 | `"Ước tính: 1 tệp · 11,6 MB · khoảng 27 giây xử lý"` |
| 1 | `"Ước tính: 16 tệp · tổng 11,9 MB · khoảng 34 giây xử lý"` |
| 2 | `"Ước tính: 1 tệp · 11,6 MB · chưa tới 10 phút nên không cắt"` |

### 3.3 Chân hộp thoại
`display:flex; gap:8px; padding:16px 24px; background:var(--layer2);
border-top:1px solid var(--divider)`.

| Nút | Kiểu | Hành động |
|---|---|---|
| `"Bắt đầu xuất"` | chính: `flex:1`, cao 38px, bo 4px, `background:var(--acc)`, `color:var(--acc-txt)`, 15px/600, hover `var(--acc-h)` | `start()` ⇒ `view = 'dang_xuat'` |
| `"Huỷ"` | phụ: `flex:1`, cao 38px, bo 4px, `background:var(--ctl)`, `border:1px solid var(--stroke2)`, `color:var(--txt)`, 15px, hover `var(--ctl-h)` | **là liên kết `<a>`** trở về `GiongDoc - Màn hình chính v2 (nghe theo dòng).dc.html` |

Không có nút nào bị làm mờ / vô hiệu ở trạng thái này. Không có ràng buộc kiểm tra (validate)
nào chặn nút "Bắt đầu xuất" trong bản thiết kế.

---

## 4. Trạng thái "Đang xuất" (`state = dang_xuat`, cờ `isRunning`)

Hộp thoại **rộng 520px**, vỏ ngoài y như hộp Cấu hình (layer / stroke2 / bo 8px /
shadow `0 32px 64px rgba(0,0,0,.32)`).

### 4.1 Phần thân — `padding:22px 24px 20px`
- Hàng đầu `display:flex; align-items:center; gap:11px`:
  - **Vòng xoay**: 16×16, bo 8px, `border:2px solid var(--stroke2)` với
    `border-top-color:var(--acc)`, `animation:spin .8s linear infinite`
    (`@keyframes spin{to{transform:rotate(360deg)}}`).
  - Tiêu đề `"Đang xuất thongbao-quoc-khanh.wav"` — 20px, weight 600, `var(--txt)`.
- **Thanh tiến độ** (`margin-top:18px`): ray cao 5px, bo 3px, `background:var(--rail)`,
  `opacity:.9`, `overflow:hidden`; phần đã chạy cao 5px, bo 3px, `background:var(--acc)`,
  **`width:38%` (viết cứng trong thiết kế)**.
- Hàng dưới thanh (`margin-top:9px`, `space-between`, 14px `var(--txt2)`, tabular-nums):
  trái `"Đang xử lý đoạn 6/16"` — phải `"38%"`.
- Ba dòng số liệu (`margin-top:18px`, `gap:9px`, mỗi dòng `space-between`;
  nhãn `var(--txt2)`, giá trị `var(--txt)` + tabular-nums):

| Nhãn (nguyên văn) | Giá trị (nguyên văn) |
|---|---|
| `"Đã trôi qua"` | `"00:38"` |
| `"Còn lại (ước tính)"` | `"01:02"` |
| `"Đã ghi"` | `"16,2 MB"` |

- Dòng nhắc (`margin-top:16px`, 13px `var(--txt3)`):
  `"Có thể tiếp tục soạn thảo trong lúc xuất. Không tắt máy."`

### 4.2 Chân hộp thoại
Cùng kiểu chân của hộp Cấu hình. **Hai nút, cả hai đều là nút phụ** (không có nút chính):

| Nút | Hành động trong thiết kế |
|---|---|
| `"Chạy nền"` | `finish()` ⇒ `view = 'hoan_tat'` |
| `"Huỷ xuất"` | **KHÔNG gắn hành động** (chỉ có hover đổi nền) |

---

## 5. Trạng thái "Hoàn tất" (`state = hoan_tat`, cờ `isDone`)

Hộp thoại **rộng 520px**, vỏ ngoài như trên.

### 5.1 Phần thân — `padding:22px 24px 20px`
- Hàng đầu `gap:11px`:
  - Huy hiệu thành công 22×22, bo 11px, `background:var(--ok)`, dấu tích trắng
    (`color:#fff`, SVG 14×14, `path d="M5 12.5l4.5 4.5L19 7"`, `stroke-width:3`).
  - Tiêu đề `"Đã xuất xong"` — 20px, weight 600, `var(--txt)`.
- **Thẻ kết quả** (`margin-top:16px`): `border:1px solid var(--stroke)`, bo 6px,
  `background:var(--layer2)`, `padding:13px`.
  - Tên tệp `"thongbao-quoc-khanh.wav"` — 14px, weight 600, `var(--txt)`.
  - Ba dòng (`margin-top:6px`, `gap:5px`, `space-between`, 14px; nhãn `var(--txt2)`,
    giá trị `var(--txt)` + tabular-nums):

| Nhãn (nguyên văn) | Giá trị (nguyên văn) |
|---|---|
| `"Thời lượng"` | `"1 phút 28 giây"` |
| `"Kích thước"` | `"11,6 MB"` |
| `"Thời gian xử lý"` | `"00:27"` |

- Đường dẫn đầy đủ (`margin-top:12px`, 13px `var(--txt3)`, `word-break:break-all`):
  `"C:\Users\Tuan\Documents\GiongViet\Xuất\thongbao-quoc-khanh.wav"`

### 5.2 Chân hộp thoại

| Nút | Kiểu | Hành động trong thiết kế |
|---|---|---|
| `"Mở thư mục"` | **chính** (`background:var(--acc)`, `color:var(--acc-txt)`, 15px/600, hover `var(--acc-h)`) | KHÔNG gắn hành động |
| `"Đóng"` | phụ (`var(--ctl)` + viền `var(--stroke2)`, 15px, hover `var(--ctl-h)`) | **là liên kết `<a>`** trở về `GiongDoc - Màn hình chính v2 (nghe theo dòng).dc.html` |

---

## 6. Toàn bộ chuỗi tiếng Việt hiện ra màn hình

### Dải nút bản mẫu (ngoài ứng dụng)
`"Hộp thoại xuất file"` · `"Cấu hình"` · `"Đang xuất"` · `"Hoàn tất"` · `"Sáng"` · `"Tối"`

### Thanh tiêu đề cửa sổ
`"thongbao-quoc-khanh.txt — Giọng Việt"` · `"Màn hình chính"` ·
tooltip `"Quay lại màn hình chính"`

### Hộp thoại Cấu hình
`"Xuất file âm thanh"` ·
`"thongbao-quoc-khanh.txt · 15 đoạn · giọng Ngọc Linh"` ·
`"Tên tệp"` · `"thongbao-quoc-khanh"` · `".wav"` ·
`"Định dạng"` · `"WAV 24 bit"` ·
`"Lưu vào"` · `"C:\Users\Tuan\Documents\GiongViet\Xuất"` · `"Chọn…"` ·
`"Tách tệp"` ·
`"Một tệp duy nhất"` · `"11,6 MB"` ·
`"Mỗi đoạn một tệp"` · `"16 tệp"` ·
`"Cắt theo độ dài"` · `"mỗi 10 phút một tệp"` ·
`"Khoảng lặng giữa các đoạn"` · `"0,5 giây"` (mẫu; dạng `"X,Y giây"`) ·
`"Đọc số tiền thành chữ (500.000 → năm trăm nghìn)"` ·
`"Đọc thẻ cảm xúc thành âm thanh"` ·
`"Chèn 1 giây im lặng ở đầu tệp"` ·
`"Ước tính: 1 tệp · 11,6 MB · khoảng 27 giây xử lý"` ·
`"Ước tính: 16 tệp · tổng 11,9 MB · khoảng 34 giây xử lý"` ·
`"Ước tính: 1 tệp · 11,6 MB · chưa tới 10 phút nên không cắt"` ·
`"Bắt đầu xuất"` · `"Huỷ"`

### Hộp thoại Đang xuất
`"Đang xuất thongbao-quoc-khanh.wav"` ·
`"Đang xử lý đoạn 6/16"` · `"38%"` ·
`"Đã trôi qua"` · `"00:38"` ·
`"Còn lại (ước tính)"` · `"01:02"` ·
`"Đã ghi"` · `"16,2 MB"` ·
`"Có thể tiếp tục soạn thảo trong lúc xuất. Không tắt máy."` ·
`"Chạy nền"` · `"Huỷ xuất"`

### Hộp thoại Hoàn tất
`"Đã xuất xong"` · `"thongbao-quoc-khanh.wav"` ·
`"Thời lượng"` · `"1 phút 28 giây"` ·
`"Kích thước"` · `"11,6 MB"` ·
`"Thời gian xử lý"` · `"00:27"` ·
`"C:\Users\Tuan\Documents\GiongViet\Xuất\thongbao-quoc-khanh.wav"` ·
`"Mở thư mục"` · `"Đóng"`

### Không có trong thiết kế
Bản thiết kế này **không có** câu trạng thái rỗng (empty state), **không có** câu lỗi
(error state), **không có** tooltip nào khác ngoài `"Quay lại màn hình chính"`.

---

## 7. Biến CSS — giá trị hai bộ màu

Khai báo trên `:root` (bộ Sáng) và `:root[data-theme='dark']` (bộ Tối).
Nền `body` cứng `#e6e6e6` ở cả hai bộ (nền bàn làm việc của bản mẫu, không đổi theo chủ đề).

| Biến | Sáng | Tối | Dùng ở đâu |
|---|---|---|---|
| `--bg` | `#f3f3f3` | `#202020` | nền khung cửa sổ, thanh tiêu đề, thanh dưới |
| `--layer` | `#ffffff` | `#2b2b2b` | thân hộp thoại, thẻ, núm trượt |
| `--layer2` | `#fafafa` | `#272727` | chân hộp thoại, thẻ kết quả |
| `--stroke` | `rgba(0,0,0,.0578)` | `rgba(255,255,255,.07)` | viền thẻ nhẹ |
| `--stroke2` | `rgba(0,0,0,.16)` | `rgba(255,255,255,.10)` | viền ô nhập, viền hộp thoại, viền nút phụ |
| `--divider` | `#e5e5e5` | `#303030` | vạch phân cách trên chân hộp thoại / thanh dưới |
| `--txt` | `#1a1a1a` | `#ffffff` | chữ chính |
| `--txt2` | `#5d5d5d` | `rgba(255,255,255,.73)` | nhãn, chữ phụ |
| `--txt3` | `#767676` | `rgba(255,255,255,.60)` | chú thích, đuôi `.wav`, đường dẫn, nút cửa sổ |
| `--dis` | `#a3a3a3` | `rgba(255,255,255,.38)` | (khai báo nhưng **không dùng** trong tệp này) |
| `--ctl` | `#fdfdfd` | `rgba(255,255,255,.06)` | nền ô nhập và nút phụ |
| `--ctl-h` | `#f6f6f6` | `rgba(255,255,255,.084)` | nền nút phụ khi hover |
| `--sub-h` | `rgba(0,0,0,.037)` | `rgba(255,255,255,.06)` | nền hover dòng chọn, khối bóng, viên thuốc tiêu đề |
| `--acc` | `#0067c0` | `#4cc2ff` | màu nhấn: nút chính, gạch chân tiêu điểm, thanh tiến độ, dấu tích |
| `--acc-h` | `#1a75c6` | `#47b1e8` | nút chính khi hover |
| `--acc-txt` | `#ffffff` | `#000000` | chữ/hình trên nền nhấn |
| `--acc-soft` | `rgba(0,103,192,.09)` | `rgba(76,194,255,.12)` | nền băng thông báo ước tính |
| `--chip-bg` | `rgba(0,0,0,.055)` | `rgba(255,255,255,.09)` | (khai báo, **không dùng** ở tệp này) |
| `--chip-bd` | `rgba(0,0,0,.09)` | `rgba(255,255,255,.14)` | (khai báo, **không dùng**) |
| `--chip-fg` | `#4a4a4a` | `rgba(255,255,255,.82)` | (khai báo, **không dùng**) |
| `--ok` | `#0f7b0f` | `#6ccb5f` | huy hiệu thành công ở trạng thái Hoàn tất |
| `--err` | `#c42b1c` | `#ff99a4` | (khai báo, **không dùng**) |
| `--rail` | `#868686` | `#9a9a9a` | ray thanh trượt, ray thanh tiến độ |
| `--close` | `#c42b1c` | `#c42b1c` | (khai báo, **không dùng**) |
| `--shadow` | `0 8px 16px rgba(0,0,0,.14)` | `0 8px 16px rgba(0,0,0,.36)` | (khai báo, **không dùng**) |
| `--scrim` | `rgba(0,0,0,.32)` | `rgba(0,0,0,.45)` | lớp che phủ sau hộp thoại |

Ngoài ra: liên kết `a` dùng `color:var(--acc)`, hover `var(--acc-h)`;
hoạt ảnh `@keyframes spin{to{transform:rotate(360deg)}}`.
Phông chữ nạp từ `_ds/bssaas-adminkit-design-system-60ba9c0b-5497-49a2-b7c1-ba0772d8cf30/fonts/inter.css`.

---

## 8. Phím tắt

**Tệp thiết kế này KHÔNG nêu phím tắt nào** (không có `keydown`, không có chú thích phím
trong giao diện).

Đối chiếu chéo — bản thiết kế màn hình chính
(`designs/GiongDoc - Màn hình chính v2 (nghe theo dòng).dc.html`) có ghi trong trình đơn:
`"Xuất file âm thanh"` ↔ `Ctrl+E`, `"Đóng tệp"` ↔ `Ctrl+W`. Tức **Ctrl+E là phím mở hộp thoại
này**, nhưng nó thuộc thiết kế màn hình chính, không thuộc tệp đang kiểm kê.

---

## 9. Luồng nhiều bước — điều kiện đi tiếp / bị chặn

Ba trạng thái là ba bước tuần tự của một luồng:

```
cau_hinh ──"Bắt đầu xuất"──► dang_xuat ──"Chạy nền"──► hoan_tat
   │                                                        │
   └──"Huỷ" (liên kết)──► Màn hình chính ◄──"Đóng" (liên kết)┘
```

| Bước | Vào bằng | Đi tiếp bằng | Điều kiện chặn |
|---|---|---|---|
| 1. `cau_hinh` | mặc định, hoặc nút `"Cấu hình"` trên dải nút | `"Bắt đầu xuất"` | **Không có** — thiết kế không đặt bất kỳ kiểm tra (tên tệp rỗng, thư mục không tồn tại…) nào chặn nút này |
| 2. `dang_xuat` | `"Bắt đầu xuất"`, hoặc nút `"Đang xuất"` | `"Chạy nền"` | **Không có** |
| 3. `hoan_tat` | `"Chạy nền"`, hoặc nút `"Hoàn tất"` | `"Đóng"` → về màn hình chính | — |

Ba nút trên dải nút cho phép nhảy trực tiếp tới bất kỳ bước nào (đây là cơ chế của bản mẫu,
không phải luồng thật của ứng dụng).

**Nút chưa gắn hành động trong thiết kế** (cần quyết định khi làm thật, vì KPI của dự án
là "KHÔNG bày nút giả"):
- `"Chọn…"` (chọn thư mục lưu)
- ô `"Định dạng"` (không có danh sách bung ra trong thiết kế; chỉ hiển thị `"WAV 24 bit"` + chevron)
- `"Huỷ xuất"` ở bước Đang xuất
- `"Mở thư mục"` ở bước Hoàn tất
- ba nút cửa sổ (thu nhỏ / phóng to / đóng)
- hàm `reset()` vẫn còn trong mã (đưa về `cau_hinh`) nhưng **không nút nào gọi nó nữa**
  (trước đây nút `"Đóng"` gọi hàm này)

---

## 10. Khác biệt so với snapshot cũ

`md5` bản mới `f71f452cf5429d05335e9d14c54069e8` (22.811 byte) ≠
`md5` snapshot cũ `3f10e4ec677eba8cd907fd06940285b5` (22.597 byte).
Cả hai đều 291 dòng, kết thúc LF — `diff` đúng **3 hunk / 6 dòng**, không có sai lệch nào
kiểu thiếu ký tự hay lệch xuống dòng. Cả ba đều là **thay đổi thiết kế thật**:

| # | Chỗ | Snapshot cũ | Bản mới |
|---|---|---|---|
| 1 | Phụ đề hộp Cấu hình | `"… · 16 đoạn · giọng Ngọc Linh"` | `"… · 15 đoạn · giọng Ngọc Linh"` |
| 2 | Nút `"Huỷ"` (chân hộp Cấu hình) | `<div>` trơ, không hành động | `<a href>` trở về màn hình chính |
| 3 | Nút `"Đóng"` (chân hộp Hoàn tất) | `<div onClick="{{ reset }}">` → về `cau_hinh` | `<a href>` trở về màn hình chính |

**Điểm cần lưu ý — số đoạn không nhất quán trong chính bản mới:** phụ đề đã sửa thành
`"15 đoạn"`, nhưng những chỗ khác vẫn giữ số 16:
- chú thích tuỳ chọn tách tệp: `"16 tệp"`
- chuỗi ước tính khi `split=1`: `"Ước tính: 16 tệp · …"`
- tiến độ bước Đang xuất: `"Đang xử lý đoạn 6/16"`

Khi dựng thật, các con số này phải suy ra từ dữ liệu chứ không viết cứng, nên mâu thuẫn
này không chặn việc triển khai — nhưng nó cho thấy `"15 đoạn"` có thể chỉ là chỉnh lẻ chưa
rà hết, đừng coi 15 là con số chuẩn.
