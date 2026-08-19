# Bản kiểm kê trạng thái — màn "Soát văn bản"

Nguồn: `design_handoff_giongdoc2/designs-goc/GiongDoc - Soát văn bản.dc.html` (kéo từ dự án thiết kế
ngày 17/8/2026, 61 302 byte, 681 dòng, md5 `7a6b76d163c5d214027f310f6e0fbf0d`).

> **Chú ý đường dẫn:** tệp được ghi vào `design_handoff_giongdoc/designs-goc/`, nhưng trong lúc làm
> việc thư mục cha bị đổi tên thành `design_handoff_giongdoc2/`. Nội dung tệp còn nguyên
> (md5 và kích thước không đổi), chỉ khác chỗ đứng.

Bản snapshot cũ trong `designs/` chỉ 27 340 byte (md5 `b535016d98f9a35f173ac73c6080006b`) —
**đã lạc hậu**, xem mục 16 để biết khác gì.

Đọc bản kiểm kê này là đủ để dựng lại màn hình, không cần mở lại tệp thiết kế.

---

## 1. Hai công tắc ở dải nút phía trên khung cửa sổ

Dải nút nằm NGOÀI khung cửa sổ giả lập (vùng nền xám `#e6e6e6`), gồm:

| Vị trí | Nội dung |
|---|---|
| Bên trái | Nhãn `Soát văn bản` — chữ hoa, 12px, letter-spacing `.05em`, màu `#5d5d5d`, weight 600 |
| Bên phải (`margin-left:auto`) | Nhóm 2 nút chọn bộ màu |

**Công tắc 1 — Bộ màu** (`themeTabs`, prop `theme`, mục "Trạng thái"):

| Giá trị | Nhãn nguyên văn | Mặc định |
|---|---|---|
| `sang` | `Sáng` | ✔ mặc định |
| `toi` | `Tối` | |

- Hộp chứa: `background:#fdfdfd`, `border:1px solid rgba(0,0,0,.09)`, `border-radius:6px`, `padding:3px`, `gap:3px`.
- Nút: `padding:7px 12px`, `border-radius:4px`, `font:600 13px`.
- Đang chọn: `background:#0067c0`, `color:#fff`. Không chọn: `background:transparent`, `color:#5d5d5d`.
- Tác dụng: đặt `document.documentElement[data-theme] = 'dark' | 'light'` (chạy ở cả `componentDidMount` và `componentDidUpdate`).

**Công tắc 2 — Thẻ mặc định của bảng Kết quả soát** (`tabMacDinh`) — CHỈ có trong bảng thuộc tính của
công cụ thiết kế, KHÔNG có nút trên dải phía trên:

| Giá trị | Chọn thẻ nào | Mặc định |
|---|---|---|
| `chu-y` | thẻ `Chỗ cần chú ý` (tab 0) | ✔ mặc định |
| `chuan-hoa` | thẻ `Văn bản sau chuẩn hoá` (tab 1) | |

Chỉ có tác dụng lúc mở màn; sau khi người dùng bấm thẻ thì `state.tab` thắng.

**Câu dẫn dưới dải nút** (rộng 1440px, 13px, line-height 1.65, màu `#5d5d5d`), nguyên văn:

> `Vẫn là cửa sổ chính của Giọng Việt — cùng danh sách hồ sơ, cùng văn bản ở giữa. Bấm **Soát văn bản** chỉ mở thêm bảng **Kết quả soát** ở dưới; bấm một dòng cảnh báo thì đoạn tương ứng ở trên sáng lên.`

(hai chữ in đậm `Soát văn bản` và `Kết quả soát` dùng `<strong>` màu `#1a1a1a`)

---

## 2. Toàn bộ trạng thái bên trong (state) — 11 biến

```js
state = { theme: null, tab: null, sel: 1, filter: 0, kind: null,
          open: 0, pf: 0, fi: 1, scanned: {}, rules: [true,true,true,false], menu: -1 }
```

| Biến | Miền giá trị | Mặc định | Nghĩa |
|---|---|---|---|
| `theme` | `null` \| `'sang'` \| `'toi'` | `null` → lấy prop | Bộ màu |
| `tab` | `null` \| `0` \| `1` | `null` → lấy `tabMacDinh` | 0 = Chỗ cần chú ý, 1 = Văn bản sau chuẩn hoá |
| `sel` | số đoạn | `1` | Đoạn đang chọn — dùng chung cho CẢ BA bảng (văn bản, danh sách cảnh báo, bảng đối chiếu chuẩn hoá) |
| `filter` | `0` \| `1` \| `2` | `0` | 0 = Tất cả, 1 = Lỗi, 2 = Cảnh báo |
| `kind` | `null` \| tên loại | `null` | Lọc thêm theo loại cảnh báo (bấm từ thẻ "Cần chú ý" bên phải) |
| `open` | `-1` \| `0..3` | `0` | Hồ sơ nào đang bung danh sách tệp (`-1` = không hồ sơ nào) |
| `pf` | `0..3` | `0` | Hồ sơ đang dùng |
| `fi` | chỉ số tệp | `1` | Tệp đang mở trong hồ sơ đó |
| `scanned` | map `"pf:fi" → true` | `{}` | Những tệp đã bấm soát trong phiên này |
| `rules` | 4 boolean | `[true,true,true,false]` | 4 quy tắc chuẩn hoá |
| `menu` | `-1` \| `0..5` | `-1` | Menu nào đang mở (`-1` = đóng hết) |

---

## 3. Bố cục — thứ tự từ trên xuống, từ trái sang phải

Khung cửa sổ: **rộng 1440px cố định, cao 900px cố định**, `background:var(--bg)`,
`border:1px solid rgba(0,0,0,.22)`, `border-radius:8px`,
`box-shadow:0 16px 32px rgba(0,0,0,.22)`, `overflow:hidden`, flex dọc.

Từ trên xuống:

| # | Vùng | Cao | Ghi chú |
|---|---|---|---|
| 1 | Thanh tiêu đề | 32px | icon app + tên cửa sổ + 3 nút hệ thống |
| 2 | Thanh menu | 30px | 6 menu, `z-index:46` |
| 3 | Lớp bắt click ngoài menu | phủ kín (`inset:0`) | chỉ hiện khi `menu >= 0`, `z-index:44` |
| 4 | Thanh công cụ | 44px | |
| 5 | Khoảng đệm | 8px | trống |
| 6 | Thân | `flex:1` | `padding:0 8px 8px`, flex ngang 3 cột |
| 7 | Thanh trạng thái | 28px | `background:var(--layer2)`, viền trên `var(--divider)` |

Thân (vùng 6) chia 3 cột từ trái sang phải:

| Cột | Bề rộng | Nội dung |
|---|---|---|
| Trái | **240px cố định** (`padding-right:8px`) | Hồ sơ đọc + 3 liên kết đáy |
| Giữa | `flex:1` (co giãn), `gap:8px` dọc | Trên: thẻ văn bản (`flex:1`). Dưới: bảng **Kết quả soát** (**cao 300px cố định**) |
| Phải | **300px cố định** (`padding-left:8px`) | Thẻ "Hồ sơ đang dùng" + thẻ "Cần chú ý" |

Cả bảng Kết quả soát (cột giữa) **và** thẻ "Cần chú ý" (cột phải) đều nằm trong `sc-if hasScan` —
tệp chưa soát thì **cả hai biến mất**, cột giữa chỉ còn thẻ văn bản chiếm hết chiều cao.

---

## 4. Vùng 1 — Thanh tiêu đề (32px)

- Icon app: 16×16, `border-radius:3px`, `background:var(--acc)`, bên trong SVG 4 vạch dọc kiểu
  thanh sóng (`M4 9v6M9 5v14M14 8v8M19 11v2`), `stroke:var(--acc-txt)`, `stroke-width:2.6`.
- Tên cửa sổ (12.5px, `var(--txt2)`), công thức:
  `'Giọng Việt — ' + {tên tệp đang mở} + (đã soát ? ' — đang soát' : '')`
  - Ví dụ đã soát: `Giọng Việt — thongbao-quoc-khanh.txt — đang soát`
  - Ví dụ chưa soát: `Giọng Việt — chuong-01-lang-que.docx`
- 3 nút hệ thống, mỗi nút 46×32, hover `background:var(--sub-h)`:

| Nút | Tooltip nguyên văn | Ghi chú |
|---|---|---|
| Thu nhỏ (một gạch) | `Thu nhỏ` | |
| Phóng to (ô vuông) | `Phóng to` | |
| Đóng (dấu ✕) | `Đóng` | hover đổi `background:var(--close)` + `color:#fff` |

---

## 5. Vùng 2 — Thanh menu (30px) — 6 menu, 47 mục

Nhãn menu: `padding:0 9px`, 14px, `color:var(--txt)`. Đang mở → `background:var(--sub-h)`.

Hộp thả xuống: `position:absolute; top:100%; left:0`, `min-width:250px`,
`background:var(--layer)`, `border:1px solid var(--stroke2)`, `border-radius:8px`,
`box-shadow:var(--shadow)`, `padding:4px`, `z-index:50`.

Mục menu: cao 32px, `padding:0 10px`, `gap:18px`, nhãn 14px bên trái, phím tắt 13px
`var(--txt3)` bên phải, hover `background:var(--sub-h)`.
Vạch phân cách: cao 1px, `background:var(--divider)`, `margin:5px 8px`.

**Quy tắc quan trọng về màu chữ mục menu:** mục CÓ hành động thật → `color:var(--txt)`;
mục CHƯA nối hành động → `color:var(--txt3)` (bị làm mờ). Bảng dưới ghi rõ cột "Nối".

### Menu 1 — `Tệp`
| Nhãn | Phím tắt | Nối |
|---|---|---|
| `Mở tệp…` | `Ctrl+O` | — (mờ) |
| `Dán văn bản` | `Ctrl+V` | → Màn hình chính |
| `Lưu` | `Ctrl+S` | — (mờ) |
| `Xuất file âm thanh` | `Ctrl+E` | → Xuất file âm thanh |
| `Đóng tệp` | `Ctrl+W` | — (mờ) |
| *vạch phân cách* | | |
| `Ghép danh sách từ Google Sheet…` | (không) | → Văn bản ghép |
| *vạch phân cách* | | |
| `Cài đặt…` | (không) | → Cài đặt |
| `Thoát` | `Alt+F4` | — (mờ) |

### Menu 2 — `Chỉnh sửa`
| Nhãn | Phím tắt | Nối |
|---|---|---|
| `Hoàn tác` | `Ctrl+Z` | — (mờ) |
| `Làm lại` | `Ctrl+Y` | — (mờ) |
| *vạch phân cách* | | |
| `Cắt` | `Ctrl+X` | — (mờ) |
| `Sao chép` | `Ctrl+C` | — (mờ) |
| `Dán` | `Ctrl+V` | — (mờ) |
| `Chọn tất cả` | `Ctrl+A` | — (mờ) |
| *vạch phân cách* | | |
| `Tìm và thay thế` | `Ctrl+H` | — (mờ) |
| `Soát lại tệp này` | `Ctrl+K` | ✔ đặt `scanned[pf:fi]=true`, `sel=1`, đóng menu |

### Menu 3 — `Chèn`
| Nhãn | Phím tắt | Nối |
|---|---|---|
| `Thẻ cảm xúc` | `Alt+1…3` | → Màn hình chính |
| `Khoảng lặng 1 giây` | `Alt+S` | — (mờ) |
| `Ngắt đoạn` | `Enter` | — (mờ) |
| *vạch phân cách* | | |
| `Thêm cách đọc cho từ đang chọn…` | (không) | → Từ điển phát âm |

### Menu 4 — `Giọng`
| Nhãn | Phím tắt | Nối |
|---|---|---|
| `Đổi giọng đọc` | `Ctrl+G` | → Màn hình chính |
| `Nghe mẫu giọng` | `Ctrl+M` | — (mờ) |
| *vạch phân cách* | | |
| `Thư viện giọng` | (không) | → Thư viện giọng |
| `Nhân bản giọng từ file…` | (không) | → Thư viện giọng `?nhanban=1` |
| `Thu âm để tạo giọng mới…` | (không) | → Thư viện giọng `?thuam=1` |
| *vạch phân cách* | | |
| `Từ điển phát âm` | (không) | → Từ điển phát âm |

### Menu 5 — `Xem`
| Nhãn | Phím tắt | Nối |
|---|---|---|
| `Chỗ cần chú ý` | (không) | ✔ `tab = 0` |
| `Văn bản sau chuẩn hoá` | (không) | ✔ `tab = 1` |
| *vạch phân cách* | | |
| `Cỡ chữ lớn hơn` | `Ctrl+=` | — (mờ) |
| `Cỡ chữ nhỏ hơn` | `Ctrl+-` | — (mờ) |
| *vạch phân cách* | | |
| `Toàn màn hình` | `F11` | — (mờ) |
| `Giao diện tối` | (không) | ✔ đảo `theme` sáng ↔ tối |

### Menu 6 — `Trợ giúp`
| Nhãn | Phím tắt | Nối |
|---|---|---|
| `Hướng dẫn nhanh` | `F1` | — (mờ) |
| `Danh sách phím tắt` | `Ctrl+/` | — (mờ) |
| `Giới thiệu Giọng Việt` | (không) | — (mờ) |
| *vạch phân cách* | | |
| `Kiểm tra bản cập nhật` | (không) | — (mờ) |
| `Gửi phản hồi cho nhà phát triển` | (không) | — (mờ) |

**Đóng menu:** bấm lại nhãn menu đang mở (toggle), hoặc bấm vào lớp phủ `inset:0 / z-index:44`
(chỉ tồn tại khi có menu mở). Mọi mục "mờ" khi bấm cũng chỉ đóng menu.

---

## 6. Vùng 4 — Thanh công cụ (44px)

Nhóm bên trái (theo thứ tự):

| # | Nhãn | Icon | Tooltip nguyên văn | Ghi chú |
|---|---|---|---|---|
| 1 | `Dán văn bản` | clipboard | `Dán văn bản từ clipboard (Ctrl+V)` | cao 32px, hover `var(--sub-h)` |
| 2 | `Mở file` | thư mục | `Mở tệp văn bản (Ctrl+O)` | cao 32px |
| — | *vạch dọc 1px × 22px* `var(--stroke2)`, `margin:0 10px` | | | |
| 3 | `Soát văn bản` | dấu tick + gạch chân | `Bảng kết quả soát đang mở — bấm để đóng lại` | **ĐANG BẬT**: `background:var(--acc-soft)`, `border:1px solid var(--acc)`, `color:var(--acc)`, `font-weight:600`. Liên kết → Màn hình chính |
| 4 | `Thẻ cảm xúc` | 3 gạch + dấu cộng, kèm mũi xuống | `Chèn thẻ cảm xúc vào đoạn đang chọn` | có chevron `var(--txt2)` 12px |

Nhóm bên phải (`margin-left:auto`):

| # | Nhãn | Icon | Tooltip nguyên văn | Ghi chú |
|---|---|---|---|---|
| 5 | `Tìm và thay thế` | kính lúp | `Tìm một từ trong văn bản và thay bằng từ khác (Ctrl+H)` | cao 32px |
| — | *vạch dọc 1px × 22px* | | | |
| 6 | `Nghe toàn bộ` | tam giác play | `Nghe liền mạch toàn bộ văn bản từ đầu (Space)` | cao 34px, `background:var(--ctl)`, `border:1px solid var(--stroke2)` |
| 7 | `Xuất file âm thanh` | mũi xuống + gạch | `Mở hộp thoại xuất để chọn định dạng và nơi lưu (Ctrl+E)` | cao 34px, `font-weight:600`, `margin-left:6px`, liên kết → Xuất file âm thanh |

---

## 7. Cột trái (240px) — "Hồ sơ đọc"

Dòng đầu cao 38px: nút hamburger 32×32 (tooltip `Thu gọn danh sách hồ sơ`) + nhãn
`Hồ sơ đọc` (14px, weight 600).

Danh sách cuộn dọc, `gap:7px`, thanh cuộn mảnh — **ẩn khi không hover**
(`scrollbar-color:transparent transparent`, hover → `var(--stroke2) transparent`).

### 4 hồ sơ mẫu

| # | Tên hồ sơ | Giọng | Điều chỉnh | Tệp |
|---|---|---|---|---|
| 0 | `Bài viết, văn bản` | `Giọng Ngọc Linh` | `Tốc độ 0 · Cao độ 0 · Âm lượng 100` | `Thư cảm ơn cuối năm.docx`, `thongbao-quoc-khanh.txt` |
| 1 | `Thông báo ngắn` | `Giọng Xuân Vĩnh` | `Tốc độ +10 · Cao độ 0 · Âm lượng 100` | `thong-bao-hop-giao-ban.txt` |
| 2 | `Sách nói` | `Giọng bác Tuấn` | `Tốc độ −10 · Cao độ 0 · Âm lượng 90` | `chuong-01-lang-que.docx` |
| 3 | `Danh sách, biểu mẫu` | `Giọng Bình An` | `Tốc độ 0 · Cao độ 0 · Âm lượng 100` | `danh-sach-cong-duc.txt`, `bieu-mau-thu-phi.txt` |

(dấu `−` ở hồ sơ 2 là dấu trừ U+2212, không phải gạch nối)

### Dòng hồ sơ — hai trạng thái

**Thu gọn** (`open !== i`): hiện 3 dòng chữ + cụm bên phải
1. Tên hồ sơ — 14px, `line-height:1.35`, cắt bằng `…` nếu dài. Weight 600 nếu là hồ sơ đang dùng (`i === pf`), ngược lại 400.
2. Tên giọng — 12px, `var(--txt3)`, cắt bằng `…`.
3. Dòng tệp — icon tài liệu 11px + tên tệp, 12px `var(--txt3)`, tooltip = chính tên tệp đó.
   Tệp hiển thị: nếu là hồ sơ đang dùng → tệp đang mở; hồ sơ khác → tệp đầu tiên.
- Bên phải: **chấm đỏ 6×6** (`background:var(--err)`) nếu hồ sơ có lỗi, rồi số tệp dạng `{n} tệp`
  (ví dụ `2 tệp`, `1 tệp`).
  - Tooltip chấm đỏ: `Hồ sơ này có tệp đang có lỗi nên sửa trước khi xuất`
  - Điều kiện có lỗi: hồ sơ đang dùng → văn bản hiện tại có đoạn `sev === 'err'`;
    hồ sơ khác → **cứng: chỉ hồ sơ số 3 (`Danh sách, biểu mẫu`) mới có chấm đỏ**.

**Bung** (`open === i`): ẨN dòng tệp và cụm số tệp/chấm đỏ, thay bằng danh sách tệp bên dưới.
Vì `open` mặc định `0`, **hồ sơ 0 bung sẵn khi mở màn**.

Nền dòng hồ sơ:
- Đang dùng (`i === pf`): `background:var(--layer)`, `border:1px solid var(--stroke)`, hover giữ `var(--layer)`.
- Không dùng: `background:transparent`, `border:1px solid transparent`, hover `var(--sub-h)`.
- Tooltip dòng: đang bung → `Thu gọn hồ sơ này`; đang thu gọn → `Mở hồ sơ {tên hồ sơ}`
  (ví dụ `Mở hồ sơ Sách nói`).
- Bấm dòng hồ sơ **chỉ bung/thu gọn**, KHÔNG đổi hồ sơ đang dùng.

### Dòng tệp trong hồ sơ đã bung
Cao 30px, `margin-left:9px`, `padding:0 6px 0 15px`, `border-left:2px solid …`, `border-radius:0 4px 4px 0`.

| Thuộc tính | Tệp đang mở | Tệp khác |
|---|---|---|
| Viền trái 2px | `var(--acc)` | `var(--stroke2)` |
| Nền | `var(--sel)` | `transparent` (hover `var(--sub-h)`) |
| Màu icon | `var(--acc)` | `var(--txt3)` |
| Màu chữ | `var(--txt)` | `var(--txt2)` |
| Weight | 600 | 400 |
| Tooltip | `Tệp đang mở` | `Mở tệp {tên tệp}` |
| Chấm đỏ 6×6 | có, nếu văn bản có đoạn lỗi — tooltip `Tệp này có lỗi nên sửa trước khi xuất` | không bao giờ |

Bấm dòng tệp → `pf = i`, `fi = j`, **đồng thời reset `sel = 1`, `filter = 0`, `kind = null`**.

Cuối danh sách tệp: dòng `Thêm tệp` cao 28px, icon dấu cộng 12px, màu `var(--txt3)`,
hover `background:var(--sub-h)` + `color:var(--txt2)`, tooltip `Mở thêm một tệp trong hồ sơ này`.

Dưới toàn bộ danh sách hồ sơ: dòng `Tạo hồ sơ mới` cao 34px, icon dấu cộng 15px,
màu `var(--txt2)`, hover `var(--sub-h)` + `color:var(--txt)`, tooltip `Tạo hồ sơ đọc mới`.

### 3 liên kết ở đáy cột trái
Ngăn bằng `border-top:1px solid var(--divider)`, mỗi liên kết cao 36px, `padding:0 12px`, 14px:

| Nhãn | Icon | Tooltip | Đích |
|---|---|---|---|
| `Thư viện giọng` | micro | (không) | Thư viện giọng |
| `Văn bản ghép` | danh sách + dấu cộng | `Ghép phần tĩnh với danh sách từ Google Sheet` | Văn bản ghép |
| `Cài đặt` | bánh răng | (không) | Cài đặt |

---

## 8. Cột giữa — Thẻ văn bản (trên) và bảng Kết quả soát (dưới)

### 8.1 Đầu thẻ văn bản (38px, viền dưới `var(--divider)`)
Từ trái sang phải:
1. Icon tài liệu 14px, `var(--txt3)`
2. Tên tệp đang mở — 14px weight 600, `max-width:340px`, cắt `…`
3. Vạch dọc 1px × 16px `var(--stroke2)`
4. `docMeta` — 13.5px `var(--txt2)`, số căn bảng: `215 từ · 15 đoạn` / `96 từ · 7 đoạn` /
   `52 từ · 5 đoạn`; **nếu chưa soát thì là `chưa soát`**
5. `headerHint` — căn phải, 12.5px `var(--txt3)`, cắt `…`:
   - Đã soát: `Đã soát lúc {giờ} · tự động soát lại khi tệp thay đổi`
     (ví dụ `Đã soát lúc 14:03 · tự động soát lại khi tệp thay đổi`)
   - Chưa soát: `Bấm “Soát tệp này” để bắt đầu` (dùng nháy kép cong “ ”)

### 8.2 Trạng thái RỖNG — tệp chưa soát (`needScan`)

Điều kiện: tổ hợp `pf:fi` không nằm trong bảng cứng và chưa bấm soát (xem mục 9).

Hộp giữa thẻ: rộng **460px**, căn giữa, `border:1.5px dashed var(--stroke2)`,
`border-radius:8px`, `padding:38px 32px`, `background:var(--layer2)`, chữ căn giữa.
1. Icon dấu tick + gạch chân, **46×46**, `stroke-width:1.1`, màu `var(--txt3)`, `opacity:.75`
2. Tiêu đề 17px weight 600 `var(--txt)`: `Tệp này chưa được soát`
3. Câu giải thích 14px `line-height:1.6` `var(--txt2)`:
   `Máy sẽ đọc thử toàn bộ văn bản để tìm những chỗ dễ đọc sai. Thường mất khoảng 8 giây.`
4. Nút cao 36px, `padding:0 18px`, `background:var(--acc)`, `color:var(--acc-txt)`,
   14px weight 600, icon tick 15px, nhãn `Soát tệp này`.
   Hover `background:var(--acc-h)`. Bấm → đặt `scanned[pf:fi]=true`, `sel=1`.

**Khi ở trạng thái này:** bảng Kết quả soát (dưới) và thẻ "Cần chú ý" (phải) đều KHÔNG hiện;
thanh trạng thái đọc `Chưa mở đoạn nào` và `Tệp chưa soát`; tên cửa sổ KHÔNG có hậu tố `— đang soát`.

### 8.3 Danh sách đoạn văn (`hasScan`)

Vùng cuộn dọc, `padding:8px 10px 8px 8px`, thanh cuộn mảnh `var(--stroke2)`.
Mỗi đoạn là một dòng `padding:7px 8px`, `border-radius:6px`, hover `background:var(--sub-h)`.

Cấu trúc dòng từ trái sang phải:

| Cột | Bề rộng | Nội dung |
|---|---|---|
| Số đoạn | 30px, căn phải, `padding-right:12px` | 12.5px, chữ số đều (`tabular-nums`) |
| Thẻ cảm xúc (nếu có) | tự co | 12.5px weight 600, `padding:4px 8px`, `border-radius:4px`, `background:var(--chip-bg)`, `border:1px solid var(--chip-bd)`, `color:var(--chip-fg)`, tooltip `Thẻ cảm xúc` |
| Nội dung đoạn | `flex:1` | **16px**, `line-height:1.55`, `var(--txt)` |
| Nhãn loại | tự co, `padding-right:10px` | 12.5px, màu `var(--err)` (lỗi) hoặc `var(--warn)` (cảnh báo); rỗng nếu đoạn không có cảnh báo |
| Nút nghe | 30px | ô 26×26, `border:1px solid var(--stroke2)`, `background:var(--ctl)`, `color:var(--txt2)`, tooltip `Nghe riêng đoạn này` |

Gạch chân chỗ sai: phần `bad` được bọc bằng
`text-decoration: underline wavy {màu}`, `text-underline-offset:5px`, `text-decoration-skip-ink:none`.
Màu = `var(--err)` nếu lỗi, `var(--warn)` nếu cảnh báo, `transparent` nếu đoạn không có cảnh báo.

**Đoạn đang chọn (`sel`) đổi 4 thứ cùng lúc:**
- Nền dòng: `var(--hl)` (không chọn: `transparent`)
- Vạch dọc bên trái: `box-shadow: inset 3px 0 0 var(--acc)` (không chọn: `none`)
- Số đoạn: màu `var(--acc)` + weight 600 (không chọn: `var(--txt3)` + weight 400)
- Nút nghe: `opacity:1` (không chọn: `opacity:.35`)

Nút nghe khi hover: `border-color:var(--acc)`, `background:var(--acc-soft)`, `color:var(--acc)`.

Bấm bất kỳ đâu trên dòng → `sel = số đoạn`.

### 8.4 Bảng "Kết quả soát" — cao 300px cố định

Chỉ hiện khi đã soát. `background:var(--layer)`, `border:1px solid var(--stroke)`, `border-radius:8px`.

**Đầu bảng cao 42px**, `background:var(--layer2)`, viền dưới `var(--divider)`,
`padding:0 8px 0 14px`, từ trái sang phải:

1. Nhãn `Kết quả soát` — 14px weight 600
2. Nhóm 2 thẻ: hộp `background:var(--ctl)`, `border:1px solid var(--stroke2)`,
   `border-radius:6px`, `padding:3px`, `gap:3px`. Mỗi thẻ cao 26px, `padding:0 11px`,
   13.5px weight 600.

   | Thẻ | Nhãn nguyên văn | Đang chọn | Không chọn |
   |---|---|---|---|
   | 0 | `Chỗ cần chú ý` | `background:var(--acc)`, `color:var(--acc-txt)` | `transparent`, `var(--txt2)` |
   | 1 | `Văn bản sau chuẩn hoá` | như trên | như trên |

3. `panelHint` — 13px `var(--txt3)`, cắt `…`:
   - Thẻ 0: `{tổng} chỗ cần chú ý · {số lỗi} lỗi nên sửa trước khi xuất`
   - Thẻ 1: `{số chỗ đổi} chỗ sẽ được đọc khác văn bản gốc`
4. **Chỉ ở thẻ 0** — hai nút:
   - `Sửa tất cả có thể ({n})` — cao 30px, `background:var(--ctl)`, `border:1px solid var(--stroke2)`,
     13px. `n` = số đoạn có hành động `Sửa`.
   - `Bỏ qua tất cả` — cao 30px, 13px `var(--txt2)`, không viền, hover `background:var(--sub-h)`.
5. Nút ✕ 28×28 — liên kết → Màn hình chính, tooltip `Đóng bảng kết quả soát`,
   hover `background:var(--sub-h)` + `color:var(--txt)`.

---

## 8.5 Thẻ 0 — "Chỗ cần chú ý"

**Hàng lọc cao 38px**, `padding:0 14px`, `gap:6px`, viền dưới `var(--divider)`:

3 viên lọc cao 26px, `border-radius:13px`, `padding:0 11px`, 13px weight 600,
mỗi viên có chấm 7×7 bên trái:

| Viên | Nhãn (số thay đổi theo tệp) | Màu chấm |
|---|---|---|
| 0 | `Tất cả ({tổng})` | `var(--txt3)` |
| 1 | `Lỗi ({số lỗi})` | `var(--err)` |
| 2 | `Cảnh báo ({số cảnh báo})` | `var(--warn)` |

Đang chọn: `background:var(--acc-soft)`, `border:1px solid var(--acc)`, `color:var(--acc)`.
Không chọn: `transparent`, `border:1px solid var(--stroke2)`, `color:var(--txt2)`.

**Viên lọc theo loại** (chỉ hiện khi `kind !== null`): cao 26px, `border-radius:13px`,
`background:var(--acc-soft)`, `border:1px solid var(--acc)`, `color:var(--acc)`,
nội dung = tên loại + dấu ✕ 9px, tooltip `Bỏ lọc theo loại`. Bấm → xoá lọc loại.

Cuối hàng (`margin-left:auto`): `Bấm một dòng để nhảy tới đoạn tương ứng` — 12.5px `var(--txt3)`.

**Hàng tiêu đề cột cao 30px**, chữ hoa 12px weight 600 `var(--txt3)`,
`letter-spacing:.04em`, viền dưới `var(--divider)`:

| Cột | Bề rộng | Nhãn |
|---|---|---|
| 1 | 64px, căn phải, `padding-right:12px` | `Đoạn` |
| 2 | 140px | `Loại` |
| 3 | `flex:1` | `Nội dung cảnh báo` |
| 4 | 280px | `Đề xuất` |
| 5 | 140px, căn phải, `padding-right:14px` | `Hành động` |

**Dòng dữ liệu cao 38px**, viền dưới `var(--divider)`, hover `background:var(--sub-h)`,
đang chọn `background:var(--hl)`:
- Cột 1: số đoạn, 13px `var(--txt2)`, chữ số đều
- Cột 2: chấm 7×7 (`var(--err)` / `var(--warn)`) + tên loại 13px `var(--txt2)`
- Cột 3: câu cảnh báo 14px `var(--txt)`, cắt `…`
- Cột 4: câu đề xuất 14px `var(--txt2)`, cắt `…`
- Cột 5: nút hành động cao 26px, `padding:0 10px`, `background:var(--ctl)`,
  `border:1px solid var(--stroke2)`, 13px (nhãn: `Sửa` / `Nghe` / `Tách` / `Đổi` / `Thêm`)
  + nút `Bỏ qua` cao 26px, `padding:0 8px`, 13px `var(--txt3)`, hover `var(--sub-h)` + `var(--txt2)`

Bấm dòng → `sel = số đoạn` (đoạn tương ứng ở bảng văn bản trên sáng lên).

**Trạng thái rỗng** (không dòng nào qua bộ lọc), `padding:34px 14px`, căn giữa,
13.5px `line-height:1.6` `var(--txt3)`, nguyên văn:
`Không có cảnh báo nào thuộc nhóm này.`

---

## 8.6 Thẻ 1 — "Văn bản sau chuẩn hoá"

**Hàng quy tắc cao 38px**, `padding:0 14px`, `gap:6px`, viền dưới `var(--divider)`:
- Nhãn chữ hoa `Quy tắc đang bật` — 12px weight 600 `var(--txt3)`
- 4 viên bật/tắt cao 26px, `border-radius:13px`, `padding:0 11px 0 9px`:

| # | Nhãn | Số | Mặc định |
|---|---|---|---|
| 0 | `Số thành chữ` | `48` | BẬT |
| 1 | `Viết tắt, ký hiệu` | `6` | BẬT |
| 2 | `Ngày tháng` | `3` | BẬT |
| 3 | `Bỏ dấu câu lặp` | `0` | TẮT |

  - Bật: icon tick 12px `stroke-width:2.6`, `background:var(--acc-soft)`,
    `border:1px solid var(--acc)`, `color:var(--acc)`
  - Tắt: icon ✕ 10px, `background:transparent`, `border:1px solid var(--stroke2)`,
    `color:var(--txt3)`
  - Nhãn 13px; số 12.5px `opacity:.7`, chữ số đều
  - Bấm → đảo bật/tắt. **Lưu ý: bật/tắt CHỈ đổi hình viên, KHÔNG đổi nội dung bảng đối chiếu bên dưới.**
- Cuối hàng (`margin-left:auto`): `Chuẩn hoá chỉ ảnh hưởng đến âm thanh, văn bản gốc không đổi`
  — 12.5px `var(--txt3)`

**Hàng tiêu đề cột cao 30px**, viền dưới `var(--divider)`:

| Cột | Bề rộng | Nhãn |
|---|---|---|
| 1 | 52px | (trống) |
| 2 | `flex:1`, `padding-left:4px` | `Văn bản gốc` |
| — | 1px `var(--divider)` | vạch dọc chia đôi |
| 3 | `flex:1`, `padding-left:16px` | `Máy sẽ đọc thành` |

**Dòng đối chiếu**, viền dưới `var(--divider)`, hover `var(--sub-h)`, đang chọn `var(--hl)`:
- Cột 1: số đoạn, `padding:9px 12px 9px 0`, căn phải, 12.5px `var(--txt3)`, chữ số đều
- Cột 2 (gốc): `padding:9px 12px 9px 4px`, **14.5px** `var(--txt2)`, `line-height:1.45`.
  Nội dung = `pre + bad + post` (nguyên văn đoạn, kể cả phần bị gạch chân)
- Cột 3 (máy đọc): `padding:9px 16px`, 14.5px `line-height:1.45`, hai kiểu:
  - **Có đổi** (`changed`): `trước` + **phần đổi được tô** + `sau`.
    Phần tô: `background:var(--mark)`, `border-radius:3px`, `padding:1px 3px`, `font-weight:600`,
    màu chữ `var(--txt)`.
  - **Không đổi** (`same`): cả câu màu nhạt `var(--txt3)`.

Cách suy ra "có đổi": lấy `norm` nếu có; nếu không có `norm` mà có `say` thì
dựng `[pre, say, post]`; nếu cả hai đều không có → không đổi, và câu hiển thị là
`plain` (nếu có) hoặc chính văn bản gốc.

Đếm `{số chỗ đổi}` = số dòng có đổi + số đoạn chỉ có `plain` (bị lược ký tự) mà không có `norm`/`say`.

Bấm dòng → `sel = số đoạn`.

---

## 9. Ba văn bản mẫu và cách chọn văn bản theo tệp

**Bảng tra cứng** (`docId`):

```
{ '0:0': 'B', '0:1': 'A', '1:0': 'C' }   // khoá = "{hồ sơ}:{tệp}"
```

| Hồ sơ : Tệp | Tên tệp | Văn bản | Trạng thái mặc định |
|---|---|---|---|
| `0:0` | `Thư cảm ơn cuối năm.docx` | **B** | đã soát |
| `0:1` | `thongbao-quoc-khanh.txt` | **A** | đã soát — **ĐÂY LÀ TRẠNG THÁI MỞ MÀN** (`pf=0, fi=1`) |
| `1:0` | `thong-bao-hop-giao-ban.txt` | **C** | đã soát |
| `2:0` | `chuong-01-lang-que.docx` | — | **chưa soát** → hiện trạng thái rỗng |
| `3:0` | `danh-sach-cong-duc.txt` | — | **chưa soát** |
| `3:1` | `bieu-mau-thu-phi.txt` | — | **chưa soát** |

Bấm `Soát tệp này` (hoặc menu `Chỉnh sửa → Soát lại tệp này`) trên một tệp chưa soát
→ tệp đó dùng **nội dung của văn bản C** (52 từ · 5 đoạn · `vừa xong`).

### Văn bản A — `thongbao-quoc-khanh.txt` · `215 từ · 15 đoạn` · soát lúc `14:03`

| Đoạn | Nội dung (phần gạch chân in **đậm**) | Mức | Loại | Câu cảnh báo | Đề xuất | Nút |
|---|---|---|---|---|---|---|
| 1 | `THÔNG BÁO LỊCH NGHỈ LỄ QUỐC KHÁNH ` **`2/9`** | lỗi | `Ngày tháng` | `“2/9” trong tiêu đề sẽ đọc là “hai phần chín”` | `Viết thành “mùng 2 tháng 9”` | `Sửa` |
| 2 | `Kính gửi toàn thể cán bộ, nhân viên Công ty ` **`TNHH`** ` Bảo Sơn.` | cảnh báo | `Viết tắt` | `“TNHH” sẽ đọc là “trách nhiệm hữu hạn”` | `Giữ nguyên cách đọc này` | `Nghe` |
| 3 | `Căn cứ Bộ luật Lao động 2019 và thông báo của ` **`UBND TP.HCM`** `, Ban Giám đốc thông báo lịch nghỉ lễ Quốc khánh năm 2026 như sau.` | cảnh báo | `Viết tắt` | `“UBND TP.HCM” sẽ đọc ở dạng đầy đủ` | `Giữ nguyên cách đọc này` | `Nghe` |
| 4 | `Thời gian nghỉ tính từ thứ Hai ngày 31/8/2026 đến hết thứ Tư ngày 2/9/2026, tổng cộng 3 ngày làm việc. Công ty làm việc trở lại bình thường từ sáng thứ Năm ngày 3/9.` (không gạch chân) | cảnh báo | `Đoạn dài` | `Đoạn 4 dài 168 ký tự, nên tách để dễ nghe` | `Tách thành 2 đoạn` | `Tách` |
| 5 | `Các bộ phận trực tiếp sản xuất bố trí người trực theo lịch đã gửi qua email ngày 12/8. Danh sách trực cụ thể như sau.` | — | — | — | — | — |
| 6 | `Phòng Kinh doanh ` **`—`** ` anh Trần Minh Đức` | cảnh báo | `Ký tự lạ` | `Ký tự “—” sẽ bị bỏ qua khi đọc` | `Thay bằng dấu phẩy` | `Sửa` |
| 7 | `Phòng Kỹ thuật — anh Lê Hoàng Nam` | — | — | — | — | — |
| 8 | `Phòng Kho vận — chị Phạm Thu Hà` | — | — | — | — | — |
| 9 | `Nhân viên có nhu cầu trực thay đăng ký với quản lý trực tiếp trước ` **`17h00`** ` ngày 25/8/2026.` | lỗi | `Giờ` | `“17h00” sẽ đọc là “mười bảy hắt không không”` | `Viết thành “17 giờ”` | `Sửa` |
| 10 | `Trong thời gian nghỉ lễ, việc gấp xin liên hệ số hotline ` **`1900 6868`** `, máy lẻ 2.` | cảnh báo | `Số điện thoại` | `“1900 6868” sẽ đọc từng chữ số` | `Đọc theo nhóm 4 số` | `Đổi` |
| 11 | *thẻ* `hắng giọng` + `Kính chúc toàn thể anh chị em kỳ nghỉ lễ vui vẻ, an toàn bên gia đình.` | — | — | — | — | — |
| 12 | `Trân trọng thông báo.` | — | — | — | — | — |
| 13 | **`TM.`** ` BAN GIÁM ĐỐC` | cảnh báo | `Viết tắt` | `“TM.” sẽ đọc là “tê mờ”` | `Thêm vào từ điển phát âm` | `Thêm` |
| 14 | `Giám đốc điều hành` | — | — | — | — | — |
| 15 | **`Nguyễn Văn Tuyến`** | cảnh báo | `Tên riêng` | `“Nguyễn Văn Tuyến” có thể đọc sai dấu` | `Thêm vào từ điển phát âm` | `Thêm` |

Cách máy đọc (cột "Máy sẽ đọc thành"):

| Đoạn | Kiểu | Phần tô sáng / câu đọc |
|---|---|---|
| 1 | đổi (`say`) | `mùng hai tháng chín` |
| 2 | đổi (`say`) | `trách nhiệm hữu hạn` |
| 3 | đổi (`say`) | `Uỷ ban nhân dân Thành phố Hồ Chí Minh` |
| 4 | đổi (`norm`) | trước `Thời gian nghỉ tính từ thứ Hai ngày ` · tô `ba mươi mốt tháng tám năm hai nghìn không trăm hai mươi sáu` · sau ` đến hết thứ Tư ngày mùng hai tháng chín, tổng cộng ba ngày làm việc. Công ty làm việc trở lại bình thường từ sáng thứ Năm ngày mùng ba tháng chín.` |
| 5 | đổi (`norm`) | trước `Các bộ phận trực tiếp sản xuất bố trí người trực theo lịch đã gửi qua email ngày ` · tô `mười hai tháng tám` · sau `. Danh sách trực cụ thể như sau.` |
| 6 | KHÔNG đổi (chỉ lược ký tự, `plain`) | `Phòng Kinh doanh anh Trần Minh Đức` |
| 7 | KHÔNG đổi (`plain`) | `Phòng Kỹ thuật anh Lê Hoàng Nam` |
| 8 | KHÔNG đổi (`plain`) | `Phòng Kho vận chị Phạm Thu Hà` |
| 9 | đổi (`norm`) | trước `Nhân viên có nhu cầu trực thay đăng ký với quản lý trực tiếp trước ` · tô `mười bảy hắt không không` · sau ` ngày hai mươi lăm tháng tám năm hai nghìn không trăm hai mươi sáu.` |
| 10 | đổi (`norm`) | trước `Trong thời gian nghỉ lễ, việc gấp xin liên hệ số hotline ` · tô `một chín không không, sáu tám sáu tám` · sau `, máy lẻ hai.` |
| 11, 12, 14 | KHÔNG đổi | y nguyên văn bản gốc |
| 13 | đổi (`say`) | `Tê mờ` |
| 15 | KHÔNG đổi | `Nguyễn Văn Tuyến` |

Số liệu suy ra cho văn bản A:
- Viên lọc: `Tất cả (9)` · `Lỗi (2)` · `Cảnh báo (7)`
- `panelHint` thẻ 0: `9 chỗ cần chú ý · 2 lỗi nên sửa trước khi xuất`
- `panelHint` thẻ 1: `11 chỗ sẽ được đọc khác văn bản gốc`
- Nút gộp: `Sửa tất cả có thể (3)` (đoạn 1, 6, 9)
- Câu dẫn thẻ phải: `9 chỗ cần chú ý, trong đó 2 lỗi nên sửa trước khi xuất.`
- Thanh trạng thái trái: `Đoạn 1 / 15` (theo `sel`); phải: `Đã soát lúc 14:03`
- Danh sách loại ở thẻ "Cần chú ý", đúng thứ tự xuất hiện:
  `Ngày tháng 1` (đỏ) · `Viết tắt 3` (vàng) · `Đoạn dài 1` (vàng) · `Ký tự lạ 1` (vàng) ·
  `Giờ 1` (đỏ) · `Số điện thoại 1` (vàng) · `Tên riêng 1` (vàng)

### Văn bản B — `Thư cảm ơn cuối năm.docx` · `96 từ · 7 đoạn` · soát lúc `09:41`

| Đoạn | Nội dung | Mức | Loại | Câu cảnh báo | Đề xuất | Nút | Máy đọc |
|---|---|---|---|---|---|---|---|
| 1 | `Kính gửi Quý khách hàng và Quý đối tác,` | — | — | — | — | — | y nguyên |
| 2 | `Năm 2025 khép lại với nhiều thử thách. Công ty Bảo Sơn xin gửi lời cảm ơn chân thành đến Quý vị đã đồng hành cùng chúng tôi.` | — | — | — | — | — | đổi: trước `Năm ` · tô `hai nghìn không trăm hai mươi lăm` · sau ` khép lại với nhiều thử thách. Công ty Bảo Sơn xin gửi lời cảm ơn chân thành đến Quý vị đã đồng hành cùng chúng tôi.` |
| 3 | `Tổng giá trị hợp đồng ký mới trong năm đạt ` **`4.200.000.000 ₫`** `.` | lỗi | `Đơn vị tiền` | `Ký hiệu “₫” sẽ bị bỏ qua khi đọc` | `Đọc thành “bốn tỷ hai trăm triệu đồng”` | `Sửa` | tô `bốn tỷ hai trăm triệu đồng` |
| 4 | `Kế hoạch mở rộng nhà xưởng tại ` **`TP.HCM`** ` sẽ khởi động trong quý một.` | cảnh báo | `Viết tắt` | `“TP.HCM” sẽ đọc ở dạng đầy đủ` | `Giữ nguyên cách đọc này` | `Nghe` | tô `Thành phố Hồ Chí Minh` |
| 5 | `Lịch làm việc đầu năm bắt đầu từ ` **`02/01/2026`** `.` | cảnh báo | `Ngày tháng` | `“02/01/2026” sẽ đọc là “không hai trên không một”` | `Viết thành “ngày 2 tháng 1 năm 2026”` | `Sửa` | tô `ngày mùng hai tháng một năm hai nghìn không trăm hai mươi sáu` |
| 6 | `Kính chúc Quý vị một năm mới an khang, thịnh vượng.` | — | — | — | — | — | y nguyên |
| 7 | `Ban Giám đốc Công ty Bảo Sơn` | — | — | — | — | — | y nguyên |

Số liệu: `Tất cả (3)` · `Lỗi (1)` · `Cảnh báo (2)`;
`panelHint` thẻ 0 `3 chỗ cần chú ý · 1 lỗi nên sửa trước khi xuất`;
thẻ 1 `4 chỗ sẽ được đọc khác văn bản gốc`; `Sửa tất cả có thể (2)`;
câu dẫn `3 chỗ cần chú ý, trong đó 1 lỗi nên sửa trước khi xuất.`;
loại: `Đơn vị tiền 1` (đỏ) · `Viết tắt 1` (vàng) · `Ngày tháng 1` (vàng);
thanh trạng thái phải `Đã soát lúc 09:41`, trái `Đoạn {sel} / 7`.

### Văn bản C — `thong-bao-hop-giao-ban.txt` · `52 từ · 5 đoạn` · soát `vừa xong`

| Đoạn | Nội dung | Mức | Loại | Câu cảnh báo | Đề xuất | Nút | Máy đọc |
|---|---|---|---|---|---|---|---|
| 1 | `Kính gửi các anh chị,` | — | — | — | — | — | y nguyên |
| 2 | `Cuộc họp giao ban tháng 8 diễn ra lúc ` **`8h30`** ` ngày 20/8/2026 tại phòng họp tầng 3.` | lỗi | `Giờ` | `“8h30” sẽ đọc là “tám hắt ba mươi”` | `Viết thành “8 giờ 30”` | `Sửa` | tô `tám hắt ba mươi` |
| 3 | `Đề nghị các bộ phận gửi báo cáo tháng về ` **`P.HC`** ` trước 17 giờ ngày 19/8.` | cảnh báo | `Viết tắt` | `“P.HC” sẽ đọc là “pê chấm hắt xê”` | `Thêm vào từ điển phát âm` | `Thêm` | tô `pê chấm hắt xê` |
| 4 | `Trân trọng.` | — | — | — | — | — | y nguyên |
| 5 | `Phòng Hành chính` | — | — | — | — | — | y nguyên |

Số liệu: `Tất cả (2)` · `Lỗi (1)` · `Cảnh báo (1)`;
`panelHint` thẻ 0 `2 chỗ cần chú ý · 1 lỗi nên sửa trước khi xuất`;
thẻ 1 `2 chỗ sẽ được đọc khác văn bản gốc`; `Sửa tất cả có thể (1)`;
câu dẫn `2 chỗ cần chú ý, trong đó 1 lỗi nên sửa trước khi xuất.`;
loại: `Giờ 1` (đỏ) · `Viết tắt 1` (vàng);
thanh trạng thái phải `Đã soát lúc vừa xong` (chú ý: ghép cứng nên đọc là "Đã soát lúc vừa xong"),
trái `Đoạn {sel} / 5`.

**Nhánh chưa bao giờ chạm tới:** câu `{n} chỗ cần chú ý, không có lỗi nặng.`
(dùng khi `số lỗi === 0`) — cả ba văn bản mẫu đều có ít nhất 1 lỗi nên câu này không hiện ra.
Nếu dựng bản thật thì vẫn phải làm nhánh này.

---

## 10. Cột phải (300px)

### Thẻ 1 — luôn hiện
`background:var(--layer)`, `border:1px solid var(--stroke)`, `border-radius:8px`, 3 khối
ngăn bằng vạch 1px `var(--divider)`:

1. `padding:11px 13px 12px` — nhãn chữ hoa `Hồ sơ đang dùng` (12px weight 600 `var(--txt3)`,
   `letter-spacing:.04em`) + tên hồ sơ 14px weight 600, cắt `…`
2. `padding:12px 13px 13px` — nhãn chữ hoa `Giọng đọc`, rồi một hàng `gap:6px`:
   - Hộp chọn giọng `flex:1`, cao 36px, `border:1px solid var(--stroke2)`,
     `background:var(--ctl)`, icon micro 16px + tên giọng 14px (cắt `…`) + chevron 13px,
     hover `background:var(--ctl-h)`
   - Nút loa 36×36, `border:1px solid var(--stroke2)`, `background:var(--ctl)`,
     tooltip `Nghe mẫu giọng này (5 giây)`, hover `background:var(--ctl-h)` + `color:var(--txt)`
3. `padding:11px 13px 13px` — hàng gập cao 26px: nhãn chữ hoa `Điều chỉnh` + chevron 13px
   bên phải (hover `background:var(--sub-h)`), rồi dòng tóm tắt 13.5px `var(--txt2)`,
   chữ số đều — nội dung là cột "Điều chỉnh" của hồ sơ (ví dụ `Tốc độ 0 · Cao độ 0 · Âm lượng 100`)

### Thẻ 2 — "Cần chú ý" — chỉ hiện khi đã soát
`padding:12px 13px 13px`:
1. Nhãn chữ hoa `Cần chú ý`
2. Câu dẫn 13.5px `line-height:1.5` `var(--txt2)`:
   - có lỗi: `{tổng} chỗ cần chú ý, trong đó {số lỗi} lỗi nên sửa trước khi xuất.`
   - không lỗi: `{tổng} chỗ cần chú ý, không có lỗi nặng.`
3. Danh sách loại — mỗi loại một dòng cao 31px, `padding:0 7px`, `border-radius:4px`,
   `margin:0 -7px 4px` (tràn lề để nền hover rộng hơn thẻ):
   - Chấm 7×7 — `var(--err)` nếu loại đó có ít nhất một đoạn lỗi, ngược lại `var(--warn)`
   - Tên loại 14px `var(--txt)`, cắt `…`
   - Số đếm: `min-width:22px`, `padding:2px 6px`, `border-radius:4px`, 12.5px weight 600,
     chữ số đều. Loại có lỗi → `color:var(--err)` trên `background:var(--err-bg)`;
     ngược lại `color:var(--warn)` trên `background:var(--warn-bg)`
   - Đang lọc theo loại này → nền dòng `var(--hl)`; hover `var(--sub-h)`
   - Tooltip: `Chỉ xem cảnh báo loại “{tên loại}” ở bảng dưới`
   - **Bấm → 3 việc cùng lúc:** đảo lọc loại (`kind`), đặt `filter = 0` (về "Tất cả"),
     và đặt `tab = 0` (nhảy sang thẻ "Chỗ cần chú ý")
   - Thứ tự: theo lần xuất hiện đầu tiên của loại trong danh sách đoạn (KHÔNG sắp xếp theo số lượng)
4. Liên kết `Từ điển phát âm` cao 30px, 13.5px `color:var(--acc)`, kèm chevron 13px,
   `margin:2px -7px -4px`, tooltip `Ghi cách đọc riêng cho từ ngữ của bạn`,
   hover `background:var(--sub-h)`, đích → Từ điển phát âm

---

## 11. Vùng 7 — Thanh trạng thái (28px)

`background:var(--layer2)`, `border-top:1px solid var(--divider)`, `padding:0 12px`,
12px `var(--txt2)`.

| Vị trí | Nội dung |
|---|---|
| Trái | `Đoạn {sel} / {tổng đoạn}` khi đã soát; `Chưa mở đoạn nào` khi chưa soát. Chữ số đều. |
| Phải, cụm 1 | Chấm 7×7 `background:var(--ok)` + `VieNeu v3 Turbo · sẵn sàng` (chữ cứng, không đổi theo trạng thái) |
| Phải, vạch | 1px × 12px `var(--divider)` |
| Phải, cụm 2 | `Đã soát lúc {giờ}` khi đã soát; `Tệp chưa soát` khi chưa soát |

---

## 12. Biến CSS — giá trị bộ Sáng và bộ Tối

Bộ Sáng nằm ở `:root`; bộ Tối ở `:root[data-theme='dark']`.

| Biến | Sáng | Tối | Dùng ở đâu |
|---|---|---|---|
| `--bg` | `#f3f3f3` | `#202020` | nền khung cửa sổ, thanh tiêu đề, thanh menu, thanh công cụ |
| `--layer` | `#ffffff` | `#2b2b2b` | thẻ văn bản, bảng kết quả, thẻ cột phải, hộp menu thả xuống, dòng hồ sơ đang dùng |
| `--layer2` | `#fafafa` | `#272727` | đầu bảng Kết quả soát, hộp rỗng "chưa soát", thanh trạng thái |
| `--stroke` | `rgba(0,0,0,.0578)` | `rgba(255,255,255,.07)` | viền thẻ, viền dòng hồ sơ đang dùng |
| `--stroke2` | `rgba(0,0,0,.16)` | `rgba(255,255,255,.10)` | viền nút/hộp chọn, vạch dọc, viền nét đứt hộp rỗng, viền trái tệp không chọn |
| `--divider` | `#e5e5e5` | `#303030` | vạch ngang chia hàng/khối |
| `--txt` | `#1a1a1a` | `#ffffff` | chữ chính |
| `--txt2` | `#5d5d5d` | `rgba(255,255,255,.73)` | chữ phụ |
| `--txt3` | `#767676` | `rgba(255,255,255,.60)` | chữ mờ, nhãn chữ hoa, phím tắt, mục menu chưa nối |
| `--dis` | `#a3a3a3` | `rgba(255,255,255,.38)` | **khai báo nhưng KHÔNG dùng trong tệp này** |
| `--ctl` | `#fdfdfd` | `rgba(255,255,255,.06)` | nền nút/hộp chọn |
| `--ctl-h` | `#f6f6f6` | `rgba(255,255,255,.084)` | hover của nút/hộp chọn |
| `--sub-h` | `rgba(0,0,0,.037)` | `rgba(255,255,255,.06)` | hover chung (menu, dòng, nút phẳng) |
| `--sel` | `rgba(0,0,0,.055)` | `rgba(255,255,255,.08)` | nền dòng tệp đang mở ở cột trái |
| `--acc` | `#0067c0` | `#4cc2ff` | màu nhấn: nút chính, thẻ đang chọn, viền trái đoạn đang chọn, liên kết |
| `--acc-h` | `#1a75c6` | `#47b1e8` | hover nút `Soát tệp này` |
| `--acc-txt` | `#ffffff` | `#000000` | chữ trên nền nhấn |
| `--acc-soft` | `rgba(0,103,192,.09)` | `rgba(76,194,255,.12)` | nền nút `Soát văn bản` đang bật, viên lọc đang chọn, viên quy tắc đang bật |
| `--hl` | `rgba(0,103,192,.11)` | `rgba(76,194,255,.13)` | nền dòng đang chọn (cả 3 bảng + dòng loại) |
| `--chip-bg` | `rgba(0,0,0,.055)` | `rgba(255,255,255,.09)` | nền thẻ cảm xúc |
| `--chip-fg` | `#4a4a4a` | `rgba(255,255,255,.82)` | chữ thẻ cảm xúc |
| `--chip-bd` | `rgba(0,0,0,.09)` | `rgba(255,255,255,.14)` | viền thẻ cảm xúc |
| `--ok` | `#0f7b0f` | `#6ccb5f` | chấm xanh "sẵn sàng" ở thanh trạng thái |
| `--err` | `#c42b1c` | `#ff99a4` | chấm/gạch chân/nhãn loại của LỖI |
| `--err-bg` | `#fdf3f4` | `#442726` | nền số đếm của loại có lỗi |
| `--err-bd` | `#eecfd2` | `#6b3a38` | **khai báo nhưng KHÔNG dùng** |
| `--warn` | `#9d5d00` | `#fce100` | chấm/gạch chân/nhãn loại của CẢNH BÁO |
| `--warn-bg` | `#fff9ec` | `#3a3320` | nền số đếm của loại cảnh báo |
| `--warn-bd` | `#f0e2c2` | `#5c4f2a` | **khai báo nhưng KHÔNG dùng** |
| `--rail` | `#868686` | `#9a9a9a` | **khai báo nhưng KHÔNG dùng** (viền trái tệp dùng `--acc`/`--stroke2`) |
| `--close` | `#c42b1c` | `#c42b1c` | hover nút Đóng cửa sổ (giống nhau ở cả hai bộ) |
| `--mark` | `rgba(0,103,192,.14)` | `rgba(76,194,255,.2)` | nền tô phần chữ đổi ở cột "Máy sẽ đọc thành" |
| `--shadow` | `0 8px 16px rgba(0,0,0,.14)` | `0 8px 16px rgba(0,0,0,.36)` | bóng hộp menu thả xuống |

Ngoài ra: `@keyframes spin{to{transform:rotate(360deg)}}` được khai báo nhưng **không phần tử nào dùng**
(dấu vết của mẫu chung, màn này không có vòng xoay chờ).

Nền ngoài khung: `body{margin:0;background:#e6e6e6}`.
Font: `'Segoe UI Variable Text','Segoe UI',Inter,system-ui,sans-serif`, cỡ gốc 14px.
Liên kết: `a{color:var(--acc)}`, `a:hover{color:var(--acc-h)}`.

---

## 13. Phím tắt được nêu trong thiết kế

**Cảnh báo:** tệp thiết kế KHÔNG có bộ bắt bàn phím nào (không `keydown`, không
`addEventListener`). Mọi phím tắt dưới đây chỉ là **nhãn chữ**, chưa nối hành động.
Khi dựng bản thật thì phải tự nối.

| Phím | Việc | Nêu ở đâu |
|---|---|---|
| `Ctrl+O` | Mở tệp | menu Tệp + tooltip nút `Mở file` |
| `Ctrl+V` | Dán văn bản | menu Tệp, menu Chỉnh sửa, tooltip nút `Dán văn bản` |
| `Ctrl+S` | Lưu | menu Tệp |
| `Ctrl+E` | Xuất file âm thanh | menu Tệp + tooltip nút `Xuất file âm thanh` |
| `Ctrl+W` | Đóng tệp | menu Tệp |
| `Alt+F4` | Thoát | menu Tệp |
| `Ctrl+Z` | Hoàn tác | menu Chỉnh sửa |
| `Ctrl+Y` | Làm lại | menu Chỉnh sửa |
| `Ctrl+X` | Cắt | menu Chỉnh sửa |
| `Ctrl+C` | Sao chép | menu Chỉnh sửa |
| `Ctrl+A` | Chọn tất cả | menu Chỉnh sửa |
| `Ctrl+H` | Tìm và thay thế | menu Chỉnh sửa + tooltip nút `Tìm và thay thế` |
| `Ctrl+K` | **Soát lại tệp này** | menu Chỉnh sửa (có nối hành động thật) |
| `Alt+1…3` | Thẻ cảm xúc | menu Chèn |
| `Alt+S` | Khoảng lặng 1 giây | menu Chèn |
| `Enter` | Ngắt đoạn | menu Chèn |
| `Ctrl+G` | Đổi giọng đọc | menu Giọng |
| `Ctrl+M` | Nghe mẫu giọng | menu Giọng |
| `Ctrl+=` | Cỡ chữ lớn hơn | menu Xem |
| `Ctrl+-` | Cỡ chữ nhỏ hơn | menu Xem |
| `F11` | Toàn màn hình | menu Xem |
| `F1` | Hướng dẫn nhanh | menu Trợ giúp |
| `Ctrl+/` | Danh sách phím tắt | menu Trợ giúp |
| `Space` | Nghe toàn bộ | tooltip nút `Nghe toàn bộ` |

---

## 14. Hộp thoại / nhiều bước

Màn này **không có hộp thoại nhiều bước nào**. Chỉ có 2 lớp nổi:
1. **Menu thả xuống** — mở bằng bấm nhãn menu, đóng bằng bấm lại nhãn đó hoặc bấm lớp phủ
   `inset:0 z-index:44`. Không có menu con nhiều cấp.
2. **Trạng thái rỗng "Tệp này chưa được soát"** — không phải hộp thoại mà là nội dung thay
   thế trong thẻ văn bản. Điều kiện đi tiếp: bấm `Soát tệp này` hoặc `Ctrl+K` trong menu.
   Không có điều kiện nào chặn.

Không có hộp thoại nào bị chặn (disabled) trong thiết kế này. Thứ duy nhất bị "làm mờ" là:
- Nút nghe từng đoạn: `opacity:.35` khi đoạn đó không phải đoạn đang chọn
- Mục menu chưa nối hành động: chữ `var(--txt3)` thay vì `var(--txt)`

---

## 15. Danh sách gọn TOÀN BỘ chuỗi tiếng Việt hiện ra màn hình

**Ngoài khung:** `Soát văn bản` · `Sáng` · `Tối` ·
`Vẫn là cửa sổ chính của Giọng Việt — cùng danh sách hồ sơ, cùng văn bản ở giữa. Bấm Soát văn bản chỉ mở thêm bảng Kết quả soát ở dưới; bấm một dòng cảnh báo thì đoạn tương ứng ở trên sáng lên.`

**Tên cửa sổ:** `Giọng Việt — {tên tệp}` (+ ` — đang soát`)

**Tooltip nút hệ thống:** `Thu nhỏ` · `Phóng to` · `Đóng`

**Nhãn menu:** `Tệp` · `Chỉnh sửa` · `Chèn` · `Giọng` · `Xem` · `Trợ giúp`

**Mục menu (47 mục, đã liệt kê đầy đủ ở mục 5)**

**Nút thanh công cụ:** `Dán văn bản` · `Mở file` · `Soát văn bản` · `Thẻ cảm xúc` ·
`Tìm và thay thế` · `Nghe toàn bộ` · `Xuất file âm thanh`

**Tooltip thanh công cụ:** `Dán văn bản từ clipboard (Ctrl+V)` · `Mở tệp văn bản (Ctrl+O)` ·
`Bảng kết quả soát đang mở — bấm để đóng lại` · `Chèn thẻ cảm xúc vào đoạn đang chọn` ·
`Tìm một từ trong văn bản và thay bằng từ khác (Ctrl+H)` ·
`Nghe liền mạch toàn bộ văn bản từ đầu (Space)` ·
`Mở hộp thoại xuất để chọn định dạng và nơi lưu (Ctrl+E)`

**Cột trái:** `Hồ sơ đọc` · `Thêm tệp` · `Tạo hồ sơ mới` · `{n} tệp` ·
`Thư viện giọng` · `Văn bản ghép` · `Cài đặt`

**Tooltip cột trái:** `Thu gọn danh sách hồ sơ` · `Thu gọn hồ sơ này` · `Mở hồ sơ {tên}` ·
`Tệp đang mở` · `Mở tệp {tên}` · `Mở thêm một tệp trong hồ sơ này` · `Tạo hồ sơ đọc mới` ·
`Hồ sơ này có tệp đang có lỗi nên sửa trước khi xuất` · `Tệp này có lỗi nên sửa trước khi xuất` ·
`Ghép phần tĩnh với danh sách từ Google Sheet`

**Đầu thẻ văn bản:** `chưa soát` · `Đã soát lúc {giờ} · tự động soát lại khi tệp thay đổi` ·
`Bấm “Soát tệp này” để bắt đầu`

**Trạng thái rỗng:** `Tệp này chưa được soát` ·
`Máy sẽ đọc thử toàn bộ văn bản để tìm những chỗ dễ đọc sai. Thường mất khoảng 8 giây.` ·
`Soát tệp này`

**Tooltip trong danh sách đoạn:** `Thẻ cảm xúc` · `Nghe riêng đoạn này`

**Bảng Kết quả soát:** `Kết quả soát` · `Chỗ cần chú ý` · `Văn bản sau chuẩn hoá` ·
`{n} chỗ cần chú ý · {m} lỗi nên sửa trước khi xuất` · `{n} chỗ sẽ được đọc khác văn bản gốc` ·
`Sửa tất cả có thể ({n})` · `Bỏ qua tất cả` · tooltip `Đóng bảng kết quả soát`

**Thẻ 0:** `Tất cả ({n})` · `Lỗi ({n})` · `Cảnh báo ({n})` ·
tooltip `Bỏ lọc theo loại` · `Bấm một dòng để nhảy tới đoạn tương ứng` ·
`Đoạn` · `Loại` · `Nội dung cảnh báo` · `Đề xuất` · `Hành động` ·
`Sửa` · `Nghe` · `Tách` · `Đổi` · `Thêm` · `Bỏ qua` ·
`Không có cảnh báo nào thuộc nhóm này.`

**Thẻ 1:** `Quy tắc đang bật` · `Số thành chữ` · `Viết tắt, ký hiệu` · `Ngày tháng` ·
`Bỏ dấu câu lặp` · `Chuẩn hoá chỉ ảnh hưởng đến âm thanh, văn bản gốc không đổi` ·
`Văn bản gốc` · `Máy sẽ đọc thành`

**Tên loại cảnh báo (8 loại trong dữ liệu mẫu):** `Ngày tháng` · `Viết tắt` · `Đoạn dài` ·
`Ký tự lạ` · `Giờ` · `Số điện thoại` · `Tên riêng` · `Đơn vị tiền`

**Cột phải:** `Hồ sơ đang dùng` · `Giọng đọc` · `Điều chỉnh` · `Cần chú ý` ·
`{n} chỗ cần chú ý, trong đó {m} lỗi nên sửa trước khi xuất.` ·
`{n} chỗ cần chú ý, không có lỗi nặng.` · `Từ điển phát âm` ·
tooltip `Nghe mẫu giọng này (5 giây)` · `Chỉ xem cảnh báo loại “{loại}” ở bảng dưới` ·
`Ghi cách đọc riêng cho từ ngữ của bạn`

**Thanh trạng thái:** `Đoạn {n} / {m}` · `Chưa mở đoạn nào` · `VieNeu v3 Turbo · sẵn sàng` ·
`Đã soát lúc {giờ}` · `Tệp chưa soát`

---

## 16. Khác gì bản snapshot cũ (`designs/`, 27 340 byte)

Bản mới **lớn hơn hơn gấp đôi** (61 302 byte, 681 dòng so với 341 dòng). Đây là thay đổi thiết kế
thật, không phải sai lệch do ghi lại (md5 `7a6b76d1…` mới vs `b535016d…` cũ).

Thêm mới hoàn toàn:
1. **Thanh menu 6 menu / 47 mục với phím tắt** — bản cũ không có thanh menu nào.
2. **Thanh công cụ 44px với 7 nút** — bản cũ không có.
3. **Cột trái hoạt động thật**: 4 hồ sơ có tên/giọng/điều chỉnh/danh sách tệp, bung–thu gọn,
   chấm đỏ báo lỗi, `Thêm tệp`, `Tạo hồ sơ mới`, 3 liên kết đáy.
   Bản cũ chỉ có một khối giả `width:240px` bị làm mờ `opacity:.55`.
4. **Cột phải 300px** với thẻ "Hồ sơ đang dùng" (giọng + điều chỉnh) và thẻ "Cần chú ý"
   (danh sách loại + số đếm + lọc theo loại + liên kết Từ điển phát âm). Bản cũ cũng có
   một khối 240px bị làm mờ, không có nội dung thật.
5. **Trạng thái rỗng "Tệp này chưa được soát"** + nút `Soát tệp này` + cơ chế `scanned`.
   Bản cũ luôn coi như đã soát.
6. **Ba văn bản mẫu A/B/C thay cho một bộ dữ liệu duy nhất.** Bản cũ chỉ có một tệp
   `thongbao-quoc-khanh.txt` với 8 đoạn hiển thị và 9 cảnh báo ghi cứng, nhiều câu bị
   cắt bằng `…` (ví dụ `Kính gửi… Công ty`), số đoạn nhảy 1–11 rồi 14, 16.
   Bản mới: dữ liệu đầy đủ, 15 đoạn liền mạch, số liệu (9/2/7, 11 chỗ đổi) được **tính ra**
   từ dữ liệu chứ không ghi cứng.
7. **Prop mới `tabMacDinh`** (`chu-y` / `chuan-hoa`) — bản cũ chỉ có prop `theme`.
8. **Lọc theo loại cảnh báo** (`kind`) và viên lọc xoá được — bản cũ không có.
9. **Nút `Sửa tất cả có thể (n)` và `Bỏ qua tất cả`** ở đầu bảng — bản cũ không có.
10. **Nút nghe riêng từng đoạn** trong danh sách văn bản — bản cũ không có.
11. **Thẻ cảm xúc hiển thị thành viên chip** (`hắng giọng` ở đoạn 11) — bản cũ nhét
    `[hắng giọng]` vào giữa chữ.

Đổi khác:
- Nền dòng đang chọn: cũ dùng `var(--acc-soft)`, mới dùng **biến mới `--hl`** và thêm
  `box-shadow: inset 3px 0 0 var(--acc)` làm vạch trái.
- Nền dòng tệp đang mở dùng **biến mới `--sel`**.
- Nhóm biến `--err-bg` / `--warn-bg` đổi từ màu trong suốt (`rgba(196,43,28,.10)`) thành
  màu đục (`#fdf3f4`, `#fff9ec`), và thêm `--err-bd`, `--warn-bd`, `--close`, `--sel`, `--hl`.
  Biến `--info` của bản cũ đã **bỏ**.
- Bộ Tối: `--warn` đổi từ `#f7b84b` thành `#fce100` (vàng chanh gắt hơn).
- Cột `Đề xuất` trong bảng cảnh báo hẹp lại từ **300px xuống 280px**.
- Thanh tiêu đề cũ có viên `Màn hình chính` để quay lại; bản mới bỏ viên đó, việc quay lại
  chuyển vào nút `Soát văn bản` trên thanh công cụ (bấm để đóng bảng) và nút ✕ của bảng.
- Số đoạn của dữ liệu mẫu đổi: `TM. BAN GIÁM ĐỐC` từ đoạn 14 thành **đoạn 13**;
  `Nguyễn Văn Tuyến` từ đoạn 16 thành **đoạn 15**.
- Cách đọc số điện thoại thêm dấu phẩy: cũ `một chín không không sáu tám sáu tám`,
  mới `một chín không không, sáu tám sáu tám`.
- Câu ở thanh trạng thái / dòng gợi ý viết lại hoàn toàn (cũ:
  `Lần soát cuối: 14:03 · tự động soát khi mở tệp`, `Chuẩn hoá theo 3 quy tắc đang bật`;
  mới: xem mục 11).

**Không tìm thấy sai lệch nào thuộc loại "ghi lại bị lỗi"** — không có dòng bị cắt,
không thiếu ký tự, không lệch xuống dòng. Toàn bộ 892 dòng diff là thay đổi thiết kế thật.

---

## 17. Lưu ý cho người dựng bản thật

- **Số liệu không được ghi cứng.** Bản thiết kế tính `Tất cả/Lỗi/Cảnh báo`, `panelHint`,
  `Sửa tất cả có thể (n)`, câu dẫn "Cần chú ý", danh sách loại, `Đoạn n / m` — tất cả **suy ra**
  từ danh sách đoạn. Đừng nhét số cố định vào giao diện.
- **`sel` là một biến dùng chung cho ba bảng.** Bấm dòng ở bảng cảnh báo, bảng chuẩn hoá,
  hay dòng văn bản đều phải làm sáng đoạn tương ứng ở cả ba nơi.
- **Đổi tệp phải reset.** Bấm dòng tệp mới → xoá lọc (`filter=0`, `kind=null`) và về `sel=1`.
- **Bật/tắt quy tắc chuẩn hoá trong bản thiết kế chưa tính lại bảng đối chiếu** — chỉ đổi hình
  viên. Nếu bản thật muốn đúng thì phải nối thật, đây là điểm còn hở của bản mẫu.
- **Nhánh `{n} chỗ cần chú ý, không có lỗi nặng.` chưa từng hiện** trong bản mẫu vì cả 3 văn bản
  đều có lỗi. Vẫn phải làm.
- Câu `Đã soát lúc vừa xong` (văn bản C) là hệ quả của việc ghép cứng `'Đã soát lúc ' + scanAt`;
  nếu bản thật muốn câu tự nhiên thì cần xử lý riêng khi `scanAt` là mô tả tương đối.
- Nhiều mục menu và nhiều nút (`Dán văn bản`, `Mở file`, `Thẻ cảm xúc`, `Tìm và thay thế`,
  `Nghe toàn bộ`, `Thêm tệp`, `Tạo hồ sơ mới`, `Sửa`/`Nghe`/`Tách`/`Đổi`/`Thêm`/`Bỏ qua`,
  `Sửa tất cả có thể`, `Bỏ qua tất cả`, nút nghe từng đoạn, hộp chọn giọng, nút nghe mẫu giọng,
  hàng gập `Điều chỉnh`) **chưa nối hành động trong bản mẫu**. Theo KPI "KHÔNG bày nút giả",
  bản thật phải nối hết hoặc không bày.
