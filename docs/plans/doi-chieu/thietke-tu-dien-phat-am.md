# Bản kiểm kê trạng thái — màn "Từ điển phát âm"

Nguồn: `design_handoff_giongdoc/designs-goc/GiongDoc - Từ điển phát âm.dc.html`
(kéo về từ dự án thiết kế ngày 2026-08-17, projectId `5c70b20f-0f8b-4da8-ad19-800b0fb6ae19`, file ở gốc dự án).

Đọc bản kiểm kê này là đủ để dựng lại màn hình, **không cần mở lại file thiết kế**.

---

## 0. Tóm lại màn này là gì

Một cửa sổ ứng dụng giả lập (1440 × 900) chứa bảng từ điển phát âm: mỗi dòng là một
cặp *"từ trong văn bản" → "đọc thành"*, kèm phạm vi áp dụng và số lần đã dùng.
Bên trái là cột lọc theo phạm vi. Bên trên bảng là thanh công cụ (tìm, nhập CSV,
thêm từ). Khi bấm "Thêm từ" thì một dải form nhập chèn thêm vào giữa thanh công cụ
và tiêu đề bảng.

Không có hộp thoại nổi (modal), không có nhiều bước (wizard). Xem mục 8.

---

## 1. Dải nút phía trên khung cửa sổ — DANH SÁCH ĐẦY ĐỦ

File này **chỉ có MỘT công tắc** trong dải nút phía trên khung cửa sổ:

| Công tắc | Các giá trị (nguyên văn nhãn) | Mặc định |
|---|---|---|
| Bộ màu | `Sáng` · `Tối` | `Sáng` |

Không có công tắc "Tình huống: …", "Mở từ: …", "Bước: …" trong màn này.

Khai báo prop tương ứng trong `data-dc-script`:

```
theme : editor "enum", options ["sang","toi"], default "sang",
        tsType 'sang'|'toi', section "Trạng thái"
```

Quy tắc lấy giá trị hiệu lực: `state.theme || props.theme || 'sang'`.
Áp dụng bằng `document.documentElement.setAttribute('data-theme', theme === 'toi' ? 'dark' : 'light')`,
chạy cả ở `componentDidMount` và `componentDidUpdate`.

### Ba trạng thái tương tác khác (nằm TRONG thân mockup, không ở dải nút trên)

| Trạng thái | Giá trị | Mặc định | Cách đổi |
|---|---|---|---|
| `scope` — phạm vi đang lọc ở cột trái | 0…4 (5 mục, xem mục 4) | `0` = "Tất cả" | bấm một mục trong danh sách cột trái |
| `addOpen` — mở/đóng dải form thêm từ | `true` / `false` | `false` | bấm "Thêm từ" hoặc "Huỷ" (cùng một hàm `toggleAdd`, đảo giá trị) |
| `sel` — dòng đang được chọn trong bảng | tên từ (chuỗi) | `'Bùi Thị Thanh Tâm'` | thiết kế **chưa nối** hành vi bấm chọn dòng; chỉ dùng để tô nền dòng |

**Liên kết sâu:** khi `componentDidMount`, nếu `location.hash === '#them'` thì tự
đặt `addOpen = true`. Nghĩa là URL `…Từ điển phát âm.dc.html#them` mở màn hình
với dải form thêm từ đã bung sẵn. Đây là hợp đồng để màn hình khác (màn hình
chính, màn soát văn bản) nhảy trực tiếp vào việc "thêm một từ mới".

---

## 2. Sự khác nhau giữa bộ Sáng và bộ Tối

Đổi bộ màu **chỉ đổi giá trị các biến CSS**, không ẩn/hiện khối nào, không đổi
chữ nào, không đổi bố cục. Xem bảng biến ở mục 6.

Lưu ý quan trọng: **phần bên ngoài khung cửa sổ KHÔNG theo bộ màu** — nó ghi cứng
màu sáng ở cả hai bộ:

- nền trang: `#e6e6e6` (ghi cứng ở cả `body{background}` và div ngoài cùng)
- nhãn "TỪ ĐIỂN PHÁT ÂM" phía trên trái: `#5d5d5d`
- hộp chứa hai nút Sáng/Tối: nền `#fdfdfd`, viền `1px solid rgba(0,0,0,.09)`
- nút bộ màu đang chọn: nền `#0067c0`, chữ `#fff`; nút không chọn: nền `transparent`, chữ `#5d5d5d`

Toàn bộ phần *bên trong* khung cửa sổ dùng biến `var(--…)` nên đổi theo bộ màu.

---

## 3. Trạng thái `addOpen` — mô tả chính xác

Dùng thẻ điều kiện `sc-if value="{{ addOpen }}"`, tức là khi `addOpen = false`
thì khối form **không tồn tại trong DOM** (không phải chỉ ẩn) → tiêu đề bảng và
danh sách dòng **dịch lên**, chiều cao vùng bảng tăng thêm đúng phần form đó.

### `addOpen = false` (mặc định)
- Không có dải form.
- Thứ tự dọc trong khung phải: thanh công cụ (56px) → tiêu đề bảng (34px) → danh sách dòng (co giãn) → thanh trạng thái (44px).
- Nút "Thêm từ" vẫn ở dạng nút chính (nền `var(--acc)`), không bị làm mờ.

### `addOpen = true`
- Chèn dải form ngay dưới thanh công cụ, trên tiêu đề bảng.
- Dải form: `padding:14px 16px`, nền `var(--acc-soft)` (nền xanh nhạt để phân biệt),
  viền dưới `1px solid var(--divider)`, `display:flex`, `align-items:flex-end`, `gap:10px`.
- Bên trong theo thứ tự trái → phải:
  1. **Ô "Từ trong văn bản"** — rộng 230px. Nhãn 13px `var(--txt2)`, cách ô 5px.
     Ô cao 34px, `padding:0 10px`, viền `1px solid var(--stroke2)`, **viền dưới
     `2px solid var(--acc)`** (dấu hiệu ô đang có con trỏ), bo 4px, nền `var(--layer)`,
     chữ 14px `var(--txt)`. Giá trị đang có: `"Bùi Thị Thanh Tâm"`.
  2. **Ô "Đọc thành"** — chiếm hết phần còn lại (`flex:1`). Cùng kiểu ô nhưng
     **không** có viền dưới nhấn, chữ màu `var(--txt3)` vì đang là chữ gợi ý:
     `"ví dụ: Bùi Thị Thanh Tâm (giữ dấu, đọc chậm)"`.
  3. **Hộp chọn "Phạm vi"** — rộng 170px, cao 34px, `padding:0 8px 0 10px`,
     viền `1px solid var(--stroke2)`, nền `var(--layer)`. Giá trị hiển thị:
     `"Hồ sơ hiện tại"`, kèm mũi nhọn xuống 12×12 (`M6 9.5l6 6 6-6`) màu `var(--txt2)`.
  4. **Nút "Nghe thử"** — cao 34px, `padding:0 13px`, bo 4px, nền `var(--layer)`,
     viền `1px solid var(--stroke2)`, chữ 14px `var(--txt)`; **hover** nền `var(--ctl-h)`.
     Biểu tượng tam giác phát 13×13 đặc (`M8 5l11 7-11 7z`), đứng trước chữ, `gap:8px`.
  5. **Nút "Lưu"** — cao 34px, `padding:0 16px`, bo 4px, nền `var(--acc)`,
     chữ `var(--acc-txt)` 14px đậm 600; **hover** nền `var(--acc-h)`.
  6. **Nút "Huỷ"** — cao 34px, `padding:0 12px`, bo 4px, không viền không nền,
     chữ 14px `var(--txt2)`; **hover** nền `var(--sub-h)`. `onClick = toggleAdd`.

- Trong thiết kế, **"Lưu" và "Nghe thử" chưa nối vào hàm nào** (không có `onClick`).
  Chỉ "Thêm từ" và "Huỷ" cùng gọi `toggleAdd`. Khi dựng thật phải nối đủ cả hai.
- Không có thông báo lỗi, không có trạng thái "đang lưu", không có ô nào bị làm mờ
  trong thiết kế này. Nếu cần thì phải bổ sung, thiết kế chưa quy định.

---

## 4. Trạng thái `scope` — cột lọc bên trái

Năm mục, nguyên văn nhãn và số đếm:

| # | Nhãn | Số |
|---|---|---|
| 0 | `Tất cả` | `34` |
| 1 | `Mọi hồ sơ` | `12` |
| 2 | `Bài viết, văn bản` | `16` |
| 3 | `Sách nói` | `4` |
| 4 | `Thông báo ngắn` | `2` |

Mặc định chọn mục 0 (`Tất cả`).

Mục **đang chọn**: nền `var(--layer)`, viền `1px solid var(--stroke)`,
vạch chỉ báo bên trái màu `var(--acc)`, nhãn đậm `600`.
Mục **không chọn**: nền `transparent`, viền `transparent`, vạch chỉ báo `transparent`,
nhãn thường `400`.
**Hover** (cả hai): nền `var(--sub-h)`.

Kích thước mỗi mục: cao 38px, `padding:0 12px 0 13px`, bo 5px, `cursor:default`,
khoảng cách giữa các mục 2px. Vạch chỉ báo: `position:absolute; left:2px;
top:50%; margin-top:-9px; width:3px; height:18px; border-radius:2px`.
Nhãn 14px `var(--txt)`; số 13px `var(--txt3)`, `font-variant-numeric:tabular-nums`.

**Cảnh báo triển khai:** trong thiết kế, đổi `scope` **KHÔNG lọc bảng** — danh sách
14 dòng là cố định, không phụ thuộc `scope`. Đây là chỗ thiết kế bỏ ngỏ; khi dựng
thật thì bấm mục nào phải lọc ra đúng những dòng có phạm vi đó, và số đếm ở cột
trái phải khớp với số dòng lọc được.

Ghi thêm: nhãn cột trái và nhãn thẻ phạm vi trong bảng **không khớp nhau hoàn toàn**.
Cột trái có `Thông báo ngắn` (2 từ) nhưng không dòng nào trong 14 dòng mẫu mang
phạm vi đó. Nghĩa là bảng mẫu chỉ là một phần của 34 từ.

---

## 5. Bố cục — vùng chính, thứ tự, bề rộng cố định

### 5.1 Ngoài khung cửa sổ

```
[ nền trang #e6e6e6, padding 20px 24px 40px ]
  ├─ dải trên (rộng 1440px, canh giữa, cách khung dưới 14px)
  │    "TỪ ĐIỂN PHÁT ÂM"  ………(đẩy phải)……… [ Sáng | Tối ]
  └─ khung cửa sổ 1440 × 900px, canh giữa
```

Khung cửa sổ: nền `var(--bg)`, viền `1px solid rgba(0,0,0,.22)`, bo 8px,
đổ bóng `0 16px 32px rgba(0,0,0,.22)`, `overflow:hidden`, xếp dọc.

Chữ toàn trang: `'Segoe UI Variable Text','Segoe UI',Inter,system-ui,sans-serif`, 14px.

### 5.2 Trong khung cửa sổ — từ trên xuống

```
┌ thanh tiêu đề  cao 32px ────────────────────────────────────────────────┐
│ [icon 16] Từ điển phát âm — Giọng Việt  [‹ Màn hình chính]   — ▢ ✕      │
├ thân  (co giãn, padding 0 8px 8px) ─────────────────────────────────────┤
│ ┌ cột trái 240px ─┐ ┌ khung phải (co giãn) ───────────────────────────┐ │
│ │ ‹ Từ điển phát │ │ thanh công cụ 56px                              │ │
│ │   âm      44px │ │   [ 🔍 Tìm từ hoặc cách đọc… 280px ] …          │ │
│ │                │ │   … [Nhập từ tệp CSV] [+ Thêm từ]               │ │
│ │ Tất cả      34 │ ├─ dải form thêm từ  (chỉ khi addOpen) ───────────┤ │
│ │ Mọi hồ sơ   12 │ ├─ tiêu đề bảng 34px ────────────────────────────┤ │
│ │ Bài viết…   16 │ │  Từ trong văn bản │ Đọc thành │ Phạm vi │ Lần   │ │
│ │ Sách nói     4 │ │                   │           │         │ dùng  │ │
│ │ Thông báo…   2 │ ├─ 14 dòng, mỗi dòng cao 42px ───────────────────┤ │
│ │ (đẩy xuống)    │ │                                                 │ │
│ │ ──────────     │ │                                                 │ │
│ │ ghi chú 13px   │ ├─ thanh trạng thái 44px ────────────────────────┤ │
│ └────────────────┘ └─────────────────────────────────────────────────┘ │
└─────────────────────────────────────────────────────────────────────────┘
```

### 5.3 Bề rộng / chiều cao cố định (con số phải giữ đúng)

| Thành phần | Kích thước |
|---|---|
| khung cửa sổ | 1440 × 900px |
| dải trên (nhãn + nút bộ màu) | rộng 1440px |
| thanh tiêu đề | cao 32px |
| ba nút cửa sổ (thu nhỏ / to / đóng) | mỗi nút 46 × 32px |
| pill "Màn hình chính" | cao 22px, `padding:0 10px 0 7px`, bo 11px |
| cột trái | rộng 240px, `padding-right:8px` |
| đầu cột trái (nút lùi + tiêu đề) | cao 44px |
| nút lùi trong cột trái | 30 × 30px, bo 4px |
| mỗi mục phạm vi | cao 38px |
| thân khung (padding) | `0 8px 8px` |
| khung phải | bo 8px, viền `1px solid var(--stroke)`, nền `var(--layer)` |
| thanh công cụ | cao 56px, `padding:0 16px`, `gap:10px` |
| ô tìm kiếm | 280 × 34px |
| nút "Nhập từ tệp CSV" | cao 34px, `padding:0 12px` |
| nút "Thêm từ" | cao 34px, `padding:0 14px` |
| tiêu đề bảng | cao 34px |
| cột "Từ trong văn bản" | 250px, `padding-left:16px` |
| cột "Đọc thành" | co giãn (`flex:1`) |
| cột "Phạm vi" | 170px |
| cột "Lần dùng" | 120px |
| cột "Hành động" | 130px, canh phải, `padding-right:16px` |
| mỗi dòng bảng | cao 42px |
| nút hành động trong dòng | 28 × 28px, bo 4px, `gap:4px` |
| thanh trạng thái | cao 44px, `padding:0 16px`, `gap:10px` |

### 5.4 Thanh tiêu đề — chi tiết

- Biểu tượng ứng dụng: hộp 16×16, bo 3px, nền `var(--acc)`; bên trong SVG 10×10
  `viewBox 0 0 24 24`, `stroke=var(--acc-txt)`, `stroke-width=2.6`, `stroke-linecap=round`,
  path `M4 9v6M9 5v14M14 8v8M19 11v2` (bốn vạch cao thấp kiểu thanh âm).
- Chữ tiêu đề 12.5px `var(--txt2)`.
- Pill "Màn hình chính": nền `var(--sub-h)`, chữ `var(--txt2)` 12px, không gạch chân,
  `white-space:nowrap`; **hover** chữ chuyển `var(--txt)`; tooltip `title="Quay lại màn hình chính"`;
  mũi nhọn trái 11×11 path `M14 6l-6 6 6 6`; `href` trỏ tới
  `GiongDoc%20-%20M%C3%A0n%20h%C3%ACnh%20ch%C3%ADnh%20v2%20%28nghe%20theo%20d%C3%B2ng%29.dc.html`.
- Ba nút cửa sổ, `cursor:default`, mỗi nút 46×32 canh giữa:
  - thu nhỏ — SVG 10×10 `viewBox 0 0 12 12`, `stroke-width=1`, path `M1 6h10`; hover nền `var(--sub-h)`
  - phóng to — `rect x=1.5 y=1.5 w=9 h=9 rx=1`, `stroke-width=1`, `fill=none`; hover nền `var(--sub-h)`
  - đóng — path `M1.5 1.5l9 9M10.5 1.5l-9 9`, `stroke-width=1.1`; **hover nền `#c42b1c`, chữ `#fff`**

### 5.5 Nút lùi trong cột trái

Là thẻ `<a>` (đã nối liên kết thật, không còn là `<div>` trơ), 30×30px, bo 4px,
`text-decoration:none`, màu `var(--txt)`; **hover** nền `var(--sub-h)`;
tooltip `title="Quay lại màn hình chính"`; mũi nhọn 16×16 path `M15 5l-7 7 7 7`;
`href` giống pill ở thanh tiêu đề.

### 5.6 Thanh công cụ — chi tiết

- Ô tìm kiếm: nền `var(--ctl)`, viền `1px solid var(--stroke2)`, bo 4px,
  `padding:0 11px`, `gap:9px`. Kính lúp 15×15 `stroke=var(--txt3)`,
  `stroke-width=1.6`, `circle cx=11 cy=11 r=6` + `path M15.5 15.5L20 20`.
  Chữ gợi ý 14px `var(--txt3)`.
- "Nhập từ tệp CSV": nút phẳng không viền không nền, chữ `var(--txt)` 14px,
  bo 4px, `gap:8px`; **hover** nền `var(--sub-h)`. Biểu tượng 15×15
  `stroke-width=1.6`, path `M12 15V4m0 11l-4-4m4 4l4-4M4 19h16` (mũi xuống trên khay).
  **Chưa nối `onClick`** trong thiết kế.
- "Thêm từ": nút chính, nền `var(--acc)`, chữ `var(--acc-txt)` 14px đậm 600, bo 4px,
  `gap:8px`; **hover** nền `var(--acc-h)`. Dấu cộng 16×16 `stroke-width=1.7`,
  path `M12 5v14M5 12h14`. `onClick = toggleAdd`.

### 5.7 Tiêu đề bảng

Cao 34px, nền `var(--layer2)`, viền dưới `1px solid var(--divider)`, chữ 12px
IN HOA (`text-transform:uppercase`), `letter-spacing:.04em`, màu `var(--txt3)`, đậm 600.

### 5.8 Dòng bảng

- Viền dưới mỗi dòng `1px solid var(--divider)`, `cursor:default`, **hover** nền `var(--sub-h)`.
- Dòng đang chọn (`word === state.sel`): nền `var(--acc-soft)`. Dòng khác nền `transparent`.
  Với dữ liệu mặc định, dòng "Bùi Thị Thanh Tâm" (dòng đầu) được tô.
- Cột từ: 15px `var(--txt)`, `white-space:nowrap; overflow:hidden; text-overflow:ellipsis`, `padding-right:12px`.
- Cột đọc thành: 15px `var(--txt2)`, cùng cách cắt bằng dấu ba chấm.
- Thẻ phạm vi: 12.5px đậm 600, `padding:4px 9px`, bo 4px — màu theo mục 5.9.
- Cột lần dùng: 13px `var(--txt3)`, `font-variant-numeric:tabular-nums`.
- Ba nút hành động: 28×28, bo 4px, màu `var(--txt2)`, `cursor:default`;
  **hover** nền `var(--sub-h)` + chữ `var(--txt)`; canh phải, `gap:4px`, `padding-right:16px`.
  - "Nghe thử" — tam giác đặc 12×12, path `M8 5l11 7-11 7z`
  - "Sửa" — bút chì 14×14, `stroke-width=1.6`, `fill=none`, `stroke-linejoin=round`, path `M4 20h4L20 8l-4-4L4 16z`
  - "Xoá" — thùng rác 14×14, `stroke-width=1.6`, `fill=none`, `stroke-linecap=round`, path `M5 7h14M9 7V4h6v3M7 7l1 13h8l1-13`
  - Cả ba **chưa nối `onClick`** trong thiết kế.

Vùng chứa dòng: `flex:1; min-height:0; overflow:hidden` — thiết kế **không** bật
thanh cuộn. 14 dòng × 42px = 588px vừa khít trong khung 900px. Khi dựng thật,
danh sách 34 từ sẽ phải cuộn → phải chuyển thành `overflow-y:auto`, và cân nhắc
giữ tiêu đề bảng dính (sticky).

### 5.9 Bảng màu thẻ phạm vi

| Mã trong dữ liệu | Nhãn hiện ra | Nền | Viền | Chữ |
|---|---|---|---|---|
| `all` | `Mọi hồ sơ` | `var(--acc-soft)` | `var(--acc)` | `var(--acc)` |
| `ho_so` | `Bài viết, văn bản` | `var(--chip-bg)` | `var(--chip-bd)` | `var(--chip-fg)` |
| `sach` | `Sách nói` | `var(--chip-bg)` | `var(--chip-bd)` | `var(--chip-fg)` |

Chỉ thẻ `Mọi hồ sơ` được tô màu nhấn; hai loại còn lại dùng chung màu xám trung tính.

### 5.10 Dữ liệu mẫu — 14 dòng, đúng thứ tự

| # | Từ trong văn bản | Đọc thành | Phạm vi | Lần dùng |
|---|---|---|---|---|
| 1 | `Bùi Thị Thanh Tâm` | `Bùi Thị Thanh Tâm (đọc chậm, rõ dấu)` | Bài viết, văn bản | `6 lần` |
| 2 | `Phúc Lâm` | `Phúc Lâm (không đọc là Phúc Lam)` | Bài viết, văn bản | `18 lần` |
| 3 | `TP.HCM` | `Thành phố Hồ Chí Minh` | Mọi hồ sơ | `42 lần` |
| 4 | `UBND` | `Uỷ ban nhân dân` | Mọi hồ sơ | `11 lần` |
| 5 | `Đ/c` | `Địa chỉ` | Mọi hồ sơ | `9 lần` |
| 6 | `Ni sư` | `Ni sư (giữ nguyên, không đọc Ni sự)` | Bài viết, văn bản | `7 lần` |
| 7 | `Bồ Đề Đạt Ma` | `Bồ Đề Đạt Ma (đọc liền, nhấn nhẹ)` | Sách nói | `4 lần` |
| 8 | `Vu Lan` | `Vu Lan (không đọc Vũ Lan)` | Mọi hồ sơ | `15 lần` |
| 9 | `A Di Đà` | `A Di Đà (kéo dài Đà)` | Sách nói | `23 lần` |
| 10 | `Đại đức` | `Đại đức` | Bài viết, văn bản | `5 lần` |
| 11 | `Ph. Tân Định` | `Phường Tân Định` | Mọi hồ sơ | `8 lần` |
| 12 | `Q.3` | `Quận ba` | Mọi hồ sơ | `8 lần` |
| 13 | `CLB` | `Câu lạc bộ` | Mọi hồ sơ | `3 lần` |
| 14 | `2.500.000đ` | `hai triệu năm trăm nghìn đồng` | Mọi hồ sơ | `31 lần` |

Đọc ra ý định thiết kế từ dữ liệu này: từ điển dùng cho **bốn nhóm việc** —
tên riêng người/chùa (dòng 1,2,6,10), viết tắt hành chính (3,4,5,11,12,13),
danh từ Phật giáo dễ đọc sai (7,8,9), và số tiền (14). Cột "Đọc thành" cho phép
ghi cả *chỉ dẫn trong ngoặc* ("đọc chậm, rõ dấu", "kéo dài Đà"), không chỉ chuỗi
thay thế thuần. Khi dựng thật phải chốt lại: ngoặc là ghi chú cho người, hay là
cú pháp máy phải hiểu.

### 5.11 Thanh trạng thái — nguyên văn, từ trái sang phải

1. `34 từ · 12 dùng cho mọi hồ sơ`
2. vạch chia: `width:1px; height:12px; background:var(--divider)`
3. `Áp dụng ngay cho lần phát và lần xuất kế tiếp`
4. (đẩy sang phải, `gap:8px`) chấm tròn 7×7px bo 4px nền `var(--warn)`
5. `3 từ trong tệp hiện tại chưa có cách đọc riêng`

Chữ 13px `var(--txt2)`, nền `var(--layer2)`, viền trên `1px solid var(--divider)`.

Ba con số `34`, `12`, `3` là số cứng trong thiết kế; khi dựng thật phải tính từ
dữ liệu và khớp với cột trái (`Tất cả 34`, `Mọi hồ sơ 12`).

---

## 6. Biến CSS — toàn bộ, kèm giá trị hai bộ màu

Bộ Sáng khai báo trên `:root` trơ; bộ Tối ghi đè trên `:root[data-theme='dark']`.
Nghĩa là `data-theme="light"` chỉ có nghĩa "không ghi đè".

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
| `--acc` | `#0067c0` | `#4cc2ff` |
| `--acc-h` | `#1a75c6` | `#47b1e8` |
| `--acc-txt` | `#ffffff` | `#000000` |
| `--acc-soft` | `rgba(0,103,192,.09)` | `rgba(76,194,255,.12)` |
| `--chip-bg` | `rgba(0,0,0,.055)` | `rgba(255,255,255,.09)` |
| `--chip-bd` | `rgba(0,0,0,.09)` | `rgba(255,255,255,.14)` |
| `--chip-fg` | `#4a4a4a` | `rgba(255,255,255,.82)` |
| `--ok` | `#0f7b0f` | `#6ccb5f` |
| `--warn` | `#9d5d00` | `#f7b84b` |
| `--rail` | `#868686` | `#9a9a9a` |
| `--shadow` | `0 8px 16px rgba(0,0,0,.14)` | `0 8px 16px rgba(0,0,0,.36)` |

**Biến khai báo nhưng màn này không dùng:** `--dis`, `--ok`, `--rail`, `--shadow`.
Chúng là phần dùng chung của bộ thiết kế; đừng bỏ khi tách CSS ra dùng cho nhiều màn.

Ngoài biến, có ba màu ghi cứng cần biết: `#e6e6e6` (nền trang), `#c42b1c` (hover nút
đóng cửa sổ), `rgba(0,0,0,.22)` (viền + bóng khung cửa sổ).

Liên kết chung: `a{color:var(--acc)}`, `a:hover{color:var(--acc-h)}`.
Riêng hai liên kết "Màn hình chính" ghi đè màu thành `var(--txt2)` / `var(--txt)`
nên không bị xanh.

---

## 7. Phím tắt

**Thiết kế không nêu phím tắt nào.** Không có nhãn phím, không có gợi ý
`Ctrl+…`, không có xử lý `keydown`. Nếu cần phím tắt (ví dụ `Ctrl+F` vào ô tìm,
`Enter` để lưu, `Esc` để huỷ dải form) thì đó là phần bổ sung ngoài thiết kế,
phải chốt lại trước khi dựng.

---

## 8. Hộp thoại và nhiều bước

**Không có.** Cụ thể:

- Không có modal, không có lớp phủ (overlay), không có `sc-if` nào khác ngoài `addOpen`.
- Việc "thêm từ" là **một bước duy nhất** trên dải form nội tuyến (mục 3):
  nhập từ → nhập cách đọc → chọn phạm vi → (Nghe thử) → Lưu. Không có bước 2.
- Không có xác nhận khi Xoá. Nút "Xoá" chỉ có tooltip, chưa nối hành vi.
  Đây là chỗ **phải bổ sung** khi dựng: người dùng lớn tuổi, xoá không hỏi lại là rủi ro.
- Việc "Nhập từ tệp CSV" chỉ có nút, thiết kế **không** vẽ bước chọn tệp, bước xem
  trước, bước đối chiếu trùng lặp, hay bước báo kết quả. Toàn bộ luồng đó còn thiếu.

### Điều kiện đi tiếp / bị chặn — thiết kế chưa quy định

Không có trạng thái nào bị làm mờ (`--dis` không được dùng ở đâu), không có câu lỗi,
không có tình huống rỗng (danh sách trống), không có tình huống đang tải.
Danh sách những thứ **phải chốt thêm** trước khi dựng:

1. Nút "Lưu" bị chặn khi nào (ô "Từ trong văn bản" rỗng? cách đọc rỗng? từ đã tồn tại?).
2. Câu báo khi từ đã có trong từ điển — ghi đè hay chặn.
3. Tình huống từ điển rỗng: bảng hiện gì.
4. Xoá có hỏi lại không, và câu hỏi ghi thế nào.
5. Bấm "Nghe thử" khi đang có tiếng khác phát — theo `CLAUDE.md` chỉ được một
   nguồn phát tiếng tại một thời điểm, nên phải chốt: cắt tiếng đang phát, hay chặn nút.
6. Cuộn danh sách khi quá 14 dòng (mục 5.8).
7. Bấm mục ở cột trái phải lọc bảng (mục 4).

---

## 9. Toàn bộ chuỗi tiếng Việt hiện ra màn hình

Nhãn và tiêu đề:

- `"Từ điển phát âm"` — nhãn dải trên (hiện IN HOA do `text-transform:uppercase`)
- `"Sáng"` · `"Tối"` — hai nút bộ màu
- `"Từ điển phát âm — Giọng Việt"` — chữ trên thanh tiêu đề
- `"Màn hình chính"` — pill liên kết ở thanh tiêu đề
- `"Từ điển phát âm"` — tiêu đề cột trái
- `"Tất cả"` · `"Mọi hồ sơ"` · `"Bài viết, văn bản"` · `"Sách nói"` · `"Thông báo ngắn"` — mục cột trái
- `"Từ điển được áp dụng trước khi đọc, ưu tiên cao hơn cách đọc mặc định của mô hình."` — ghi chú chân cột trái
- `"Tìm từ hoặc cách đọc…"` — chữ gợi ý trong ô tìm (dấu ba chấm là ký tự `…`, không phải ba dấu chấm)
- `"Nhập từ tệp CSV"` — nút
- `"Thêm từ"` — nút chính
- `"Từ trong văn bản"` — nhãn ô trong dải form **và** tiêu đề cột bảng
- `"Đọc thành"` — nhãn ô trong dải form **và** tiêu đề cột bảng
- `"Phạm vi"` — nhãn ô trong dải form **và** tiêu đề cột bảng
- `"Lần dùng"` — tiêu đề cột bảng
- `"Hành động"` — tiêu đề cột bảng
- `"Bùi Thị Thanh Tâm"` — giá trị đang có trong ô "Từ trong văn bản"
- `"ví dụ: Bùi Thị Thanh Tâm (giữ dấu, đọc chậm)"` — chữ gợi ý ô "Đọc thành"
- `"Hồ sơ hiện tại"` — giá trị hộp chọn "Phạm vi"
- `"Nghe thử"` — nút trong dải form
- `"Lưu"` — nút trong dải form
- `"Huỷ"` — nút trong dải form (viết `Huỷ`, **không** phải `Hủy`)

Thẻ phạm vi trong bảng: `"Mọi hồ sơ"` · `"Bài viết, văn bản"` · `"Sách nói"`

Tooltip (`title`):

- `"Quay lại màn hình chính"` — cả pill ở thanh tiêu đề và nút lùi ở cột trái (hai chỗ, cùng câu)
- `"Nghe thử"` — nút hành động thứ nhất trong dòng
- `"Sửa"` — nút hành động thứ hai
- `"Xoá"` — nút hành động thứ ba (viết `Xoá`, **không** phải `Xóa`)

Thanh trạng thái:

- `"34 từ · 12 dùng cho mọi hồ sơ"` (dấu giữa là `·`)
- `"Áp dụng ngay cho lần phát và lần xuất kế tiếp"`
- `"3 từ trong tệp hiện tại chưa có cách đọc riêng"`

Dữ liệu dòng bảng: xem đầy đủ ở mục 5.10 (cả 14 cặp từ / cách đọc / `N lần`).

Chuỗi trong `data-props` (không hiện trên màn, chỉ hiện trong bảng thuộc tính của
công cụ thiết kế): `"Trạng thái"`.

**Quy ước chính tả cần giữ:** `Huỷ` và `Xoá` (không phải `Hủy`, `Xóa`);
`Uỷ ban nhân dân`; dấu `·` phân tách trong thanh trạng thái; ký tự `…` (một ký tự)
ở chữ gợi ý ô tìm; dấu gạch dài `—` (em dash) trong tiêu đề cửa sổ.

---

## 10. Đối chiếu với bản snapshot cũ

So `designs-goc/` (mới kéo 2026-08-17) với `designs/` (snapshot 2026-08-14):
**khác nhau, 4 thay đổi thiết kế thật**, không có dấu hiệu ghi sai/thiếu.

| # | Thay đổi | Ý nghĩa |
|---|---|---|
| 1 | Nút lùi ở cột trái: `<div>` → `<a href="…Màn hình chính v2…">`, thêm `flex:none`, `text-decoration:none`, bỏ `cursor:default` | nút lùi giờ là liên kết thật, bấm được sang màn hình chính |
| 2 | Ba nút hành động trong dòng bảng: thêm `cursor:default` | trỏ chuột không thành bàn tay, khớp cách làm chung của bộ thiết kế |
| 3 | `state.addOpen`: `true` → `false` | màn hình mở ra **không** còn bung sẵn dải form thêm từ |
| 4 | `componentDidMount` thêm `if (location.hash === '#them') this.setState({ addOpen: true })` | có liên kết sâu `#them` để mở màn hình với dải form đã bung |

Thay đổi 3 + 4 đi cùng nhau: mặc định thu gọn, muốn bung thì vào bằng `#them`.
Thay đổi 1 nằm cùng họ với pill "Màn hình chính" ở thanh tiêu đề (pill đó đã là
liên kết từ bản cũ) — tức là đang nối dần các đường điều hướng giữa các màn.
