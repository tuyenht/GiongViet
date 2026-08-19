# Bản kiểm kê trạng thái — màn "Thư viện giọng"

Nguồn: `design_handoff_giongdoc2/designs-goc/GiongDoc - Thư viện giọng.dc.html`
(kéo từ dự án thiết kế ngày 17/8/2026 — 977 dòng, 77.491 byte, md5 `b9ecf5823ee068c7b31c1e6164289d96`)

> Lưu ý đường dẫn: lúc kéo tệp về, thư mục còn tên `design_handoff_giongdoc/`.
> Trong lúc đang làm, thư mục bị đổi tên thành `design_handoff_giongdoc2/` bởi một tiến trình
> bên ngoài (không phải việc của tài liệu này). Tệp vẫn nguyên vẹn — md5 sau khi đổi tên
> vẫn đúng bằng md5 lúc ghi. Nếu về sau thư mục được đổi tên lại thì sửa đường dẫn ở trên.

Bản snapshot cũ trong `designs/` chỉ có 257 dòng và là bản **tĩnh** (chỉ có thẻ giọng, không có
hộp thoại, không có tình huống lỗi). Bản mới là **bản mẫu tương tác đầy đủ**. Chi tiết khác biệt
ghi ở mục 12 cuối tài liệu.

Tài liệu này ghi đủ để lập trình mà **không cần mở lại tệp thiết kế**.

---

## 1. Dải nút chuyển trạng thái (nằm NGOÀI khung cửa sổ, phía trên)

Dải nút này chỉ là công cụ của bản mẫu để xem các trạng thái — **không phải phần giao diện thật**
của chương trình. Nhưng mỗi giá trị trong đó là **một yêu cầu xử lý thật** phải làm được.

Thứ tự từ trái sang phải, trong khối `width:1440px; margin:0 auto 14px; display:flex; gap:14px`:

| # | Nhãn nhóm | Kiểu | Các giá trị (nguyên văn) | Biến state |
|---|---|---|---|---|
| 1 | `Thư viện giọng` | chữ tiêu đề, không bấm được | — | — |
| 2 | `Mở từ` | 2 nút gạt | `Menu Giọng` · `Chọn giọng cho hồ sơ` | `entry` = 0 / 1 |
| 3 | `Tình huống` | 5 nút gạt | `Bình thường` · `Bản ghi quá ngắn` · `Hai người nói` · `Hết lượt nhân bản` · `Tạo giọng lỗi` | `sit` = `binh_thuong` / `ngan` / `hai_nguoi` / `het_luot` / `that_bai` |
| 4 | (không nhãn, dồn phải `margin-left:auto`) | 2 nút gạt | `Sáng` · `Tối` | `theme` = `sang` / `toi` |

**Không có công tắc "Bước:" trong tệp này.** Các bước của hộp thoại nhân bản đi tới bằng cách
bấm nút trong hộp thoại, không đổi bằng dải nút phía trên.

Kiểu dáng nút gạt: nhóm bọc `padding:3px; background:#fdfdfd; border:1px solid rgba(0,0,0,.09);
border-radius:6px; gap:3px`. Nút bên trong `padding:7px 12px` (nhóm `Tình huống` dùng `7px 10px`),
`border-radius:4px`, `font:600 13px`. Nút đang chọn: `background:#0067c0; color:#fff`.
Nút không chọn: `background:transparent; color:#5d5d5d`.

**Khai báo prop** (dòng `data-props`): chỉ khai `theme`, kiểu enum, options `["sang","toi"]`,
mặc định `"sang"`, section `"Trạng thái"`.

### Mở màn hình bằng đường dẫn (deep-link)

`componentDidMount` đọc `window.location.search + window.location.hash`:

- chuỗi có chứa `thuam` → mở luôn hộp thoại ở bước thu âm (`clone: 6, src: 'rec'`)
- chuỗi có chứa `nhanban` → mở luôn hộp thoại ở bước chọn nguồn (`clone: 0`)

### Trạng thái khởi tạo đầy đủ

```
theme: null          nav: 0               active: 'Giọng Ngọc Linh'   prof: 0
menu: null           profOpen: false      toast: null                entry: 0
def: 'Giọng Ngọc Linh'   clone: -1        agree: false               cloned: false
sit: 'binh_thuong'   mode: 'moi'          addTo: ''                  src: 'file'
rec: false           recSec: 0            recTick: 0                 confirm: null
rename: null         renameVal: ''        names: null                removed: null
bg: 0                bgName: ''           playing: null              limit: false
```

Ngoài ra có `dlMap` khởi tạo ngầm (khi chưa ai đụng tới):
`{ 'Giọng Minh Quân': 'dl', 'Giọng Hải Yến': 'absent', 'Giọng Thiện Tâm': 'absent' }`

`componentWillUnmount` phải dọn: `clearInterval(_rec)`, `clearTimeout(_t1)`, `clearTimeout(_t2)`,
`clearTimeout(_p)`.

---

## 2. Cấu trúc bố cục

Bề rộng cố định: **1440 × 900** cho khung cửa sổ. Trang ngoài `padding:20px 24px 40px`,
nền `#e6e6e6`, chữ `'Segoe UI Variable Text','Segoe UI',Inter,system-ui,sans-serif` 14px.
Khung cửa sổ: `position:relative` (bắt buộc — mọi hộp thoại và lớp phủ định vị theo nó),
`border:1px solid rgba(0,0,0,.22)`, `border-radius:8px`,
`box-shadow:0 16px 32px rgba(0,0,0,.22)`, `overflow:hidden`, xếp dọc.

Từ trên xuống trong khung cửa sổ:

```
┌ Thanh tiêu đề (cao 32) ────────────────────────────────────────────┐
│ [logo 16] Thư viện giọng — Giọng Việt  [◄ Màn hình chính]  … ─ □ ✕ │
├────────────────────────────────────────────────────────────────────┤
│ Thân (flex:1, padding 0 8px 8px)                                   │
│ ┌ Cột trái 240 ──┐ ┌ Khung chính (flex:1, layer, radius 8) ──────┐ │
│ │ [◄] Thư viện   │ │ Thanh công cụ (cao 56)                      │ │
│ │     giọng      │ ├────────────────────────────────────────────┤ │
│ │                │ │ [Băng "đang chọn giọng" — chỉ khi entry=1]  │ │
│ │ 4 mục điều     │ ├────────────────────────────────────────────┤ │
│ │ hướng          │ │ Vùng nội dung (flex:1, padding 16)          │ │
│ │                │ │   GIỌNG CỦA TÔI  →  thẻ giọng 270px         │ │
│ │ ── (auto) ──   │ │   GIỌNG CÓ SẴN   →  thẻ giọng 270px, wrap   │ │
│ │ Dung lượng     │ ├────────────────────────────────────────────┤ │
│ └────────────────┘ │ Thanh chân (cao 44)                         │ │
│                    └────────────────────────────────────────────┘ │
└────────────────────────────────────────────────────────────────────┘
```

### 2.1 Thanh tiêu đề (cao 32, `padding-left:12`)

- Logo 16×16, `border-radius:3`, nền `var(--acc)`, bên trong SVG 4 vạch dọc màu `var(--acc-txt)`
- Chữ `Thư viện giọng — Giọng Việt`, 12.5px, `var(--txt2)`
- Nút dạng viên thuốc `Màn hình chính`: cao 22, `border-radius:11`, nền `var(--sub-h)`,
  12px, có mũi tên `◄` bên trái, `title="Quay lại màn hình chính"`,
  liên kết tới `GiongDoc - Màn hình chính v2 (nghe theo dòng).dc.html`
- Dồn phải: 3 nút cửa sổ, mỗi nút 46×32 — thu nhỏ (gạch ngang), phóng to (ô vuông),
  đóng (dấu ✕, khi trỏ vào đổi nền `#c42b1c` chữ `#fff`)

### 2.2 Cột trái (rộng 240, `padding-right:8`)

- Hàng đầu cao 44: nút mũi tên quay lại 30×30 (`title="Quay lại màn hình chính"`, liên kết tới
  màn hình chính) + chữ `Thư viện giọng` 16px/600
- Danh sách 4 mục điều hướng, `gap:2`, mỗi mục cao 38, `border-radius:5`,
  `padding:0 12px 0 13px`. Mục đang chọn có vạch chỉ thị 3×18px `border-radius:2` ở `left:2px`,
  màu `var(--acc)`; nền `var(--layer)`; viền `var(--stroke)`; chữ đậm 600.
  Mục không chọn: vạch trong suốt, nền trong suốt, chữ 400. Số đếm bên phải 13px
  `var(--txt3)`, `font-variant-numeric:tabular-nums`.
- Dưới cùng (`margin-top:auto`, `border-top:1px solid var(--divider)`), 13px `var(--txt3)`,
  `line-height:1.5`: dòng `{{ quotaLine }}` rồi xuống dòng
  `Đã dùng 6,4 GB cho mô hình giọng, còn trống 128 GB.`

### 2.3 Thanh công cụ khung chính (cao 56, `padding:0 16`, `gap:10`)

Từ trái sang phải:

1. Hộp tìm kiếm: rộng 300, cao 34, `border-radius:4`, viền `var(--stroke2)`, nền `var(--ctl)`;
   biểu tượng kính lúp + chữ mờ `Tìm theo tên, vùng miền…`
2. Nút lọc `Giới tính: Tất cả` + mũi tên xuống (cao 34)
3. Nút lọc `Vùng: Tất cả` + mũi tên xuống (cao 34)
4. Dồn phải: nút chính cao 34, `padding:0 14`, nền `var(--acc)`, chữ `var(--acc-txt)` 14px/600,
   biểu tượng `+`, nhãn `Nhân bản giọng mới` → gọi `openClone`

### 2.4 Thanh chân (cao 44, `padding:0 16`, nền `var(--layer2)`, 13px `var(--txt2)`)

- `{{ footCount }}` (không cho ngắt dòng)
- vạch phân cách 1×12px
- `{{ footRight }}` (cắt bằng dấu … khi dài)
- Chỉ khi `bgOn` — dồn phải: vòng xoay 13×13 (`border:2px solid var(--stroke2)`,
  `border-top-color:var(--acc)`, `animation:spin .9s linear infinite`) +
  `{{ bgLabel }}` màu `var(--txt)` + thanh tiến độ 74×4 nền `var(--rail)` với phần chạy
  `var(--acc)` rộng `{{ bgPct }}`

---

## 3. Thẻ giọng — mọi trạng thái

Thẻ rộng **270px cố định**, nền `var(--layer2)`, viền `1px solid {{ v.bd }}`,
`border-radius:8`, `padding:13`.

Cấu trúc trong thẻ, từ trên xuống:

1. Hàng đầu (`gap:10`, `align-items:flex-start`)
   - Ảnh đại diện 34×34 `border-radius:17`, biểu tượng micro.
     Giọng của tôi: nền `var(--acc-soft)` chữ `var(--acc)`.
     Giọng có sẵn: nền `var(--chip-bg)` chữ `var(--txt2)`.
   - Tên giọng `{{ v.name }}` 15px/600, cắt bằng dấu …
   - Nhãn tròn `{{ v.badge }}` — **chỉ hiện khi `v.isActive`** — 11.5px/600,
     `padding:2px 7px`, `border-radius:9`, nền `var(--acc)`, chữ `var(--acc-txt)`
   - Dòng mô tả `{{ v.meta }}` 13px `var(--txt3)`, `margin-top:2`
2. Dải sóng âm: **26 vạch**, cao khối 30px, `gap:2`, `margin:12px 0 10px`, mỗi vạch
   `flex:1; border-radius:1px`
   - Thẻ **giọng của tôi**: nền vạch ghi cứng `var(--wave)` (không đổi màu theo trạng thái)
   - Thẻ **giọng có sẵn**: nền vạch theo `{{ w.bg }}` → mờ thành `var(--rail)` khi giọng
     không được chọn và không đang phát; sáng `var(--wave)` khi được chọn hoặc đang phát
3. Chỉ khi `v.dlBar` — thanh tải về (`margin:-3px 0 10px`):
   - hàng chữ: bên trái `Đang tải về máy…`, bên phải `{{ v.dlPct }}` (tabular-nums), 12.5px
   - thanh: cao 4, `border-radius:2`, nền `var(--rail)`, phần chạy nền `var(--acc)`
     rộng `{{ v.dlPct }}` (giá trị cố định `46%`)
4. Hàng nút (`gap:6`)
   - Nút nghe thử: `flex:none`, cao 32, `padding:0 12`, nền `{{ v.playBg }}`,
     viền `var(--stroke2)`, `title="{{ v.playTip }}"`, biểu tượng `{{ v.playIcon }}`,
     nhãn `{{ v.playLabel }}`
   - Nút chính: `flex:1`, cao 32, nền `{{ v.btnBg }}`, viền `{{ v.btnBd }}`,
     chữ `{{ v.btnFg }}` 13px/600, `title="{{ v.btnTip }}"`, nhãn `{{ v.btn }}`
   - Nút `⋯` 32×32, nền `{{ v.menuBg }}`, `title="Tuỳ chọn khác cho giọng này"`

### 3.1 Nút nghe thử — hai trạng thái

| | Chưa phát | Đang phát |
|---|---|---|
| Nhãn | `Nghe thử` | `Đang nghe…` |
| Biểu tượng | tam giác `M8 5l11 7-11 7z` | hai vạch `M7 6h3.6v12H7zM13.4 6H17v12h-3.6z` |
| Nền | `var(--ctl)` | `var(--acc-soft)` |
| Tooltip | `Nghe 8 giây mẫu của {tên}` | `Đang nghe mẫu {tên} — bấm để dừng` |

Chỉ **một giọng phát tại một thời điểm** (`state.playing` là một tên, không phải danh sách).
Bấm lại nút đang phát thì dừng. Tự dừng sau **4000 ms**. Bấm nghe thử cũng đóng luôn
menu `⋯` và dropdown hồ sơ.

### 3.2 Nút chính — bảng đầy đủ theo `entry` và trạng thái tải

Điều kiện "đang được chọn" (`on`) khác nhau theo `entry`:
- `entry = 0` (Menu Giọng): `on` = giọng này đúng bằng `state.def`
- `entry = 1` (Chọn giọng cho hồ sơ): `on` = giọng này đúng bằng `state.active`

| Trạng thái tải | entry | `on` | Nhãn nút | Nền / viền / chữ | Tooltip |
|---|---|---|---|---|---|
| đã có trên máy | 0 | có | `Giọng mặc định` | `transparent` / `var(--stroke2)` / `var(--txt3)` | `{tên} đang là giọng mặc định cho hồ sơ mới` |
| đã có trên máy | 0 | không | `Đặt làm mặc định` | `var(--acc)` / `var(--acc)` / `var(--acc-txt)` | `Đặt {tên} làm giọng mặc định cho hồ sơ tạo sau này` |
| đã có trên máy | 1 | có | `Đang dùng` | `transparent` / `var(--stroke2)` / `var(--txt3)` | `Hồ sơ {tên hồ sơ} đang dùng {tên}` |
| đã có trên máy | 1 | không | `Dùng cho hồ sơ này` | `var(--acc)` / `var(--acc)` / `var(--acc-txt)` | `Gán {tên} cho hồ sơ {tên hồ sơ}` |
| chưa tải (`absent`) | cả hai | — | `Tải về · {dung lượng}` | `var(--ctl)` / `var(--stroke2)` / `var(--txt)` | `Tải mô hình {tên} về máy, sau đó mới dùng để đọc được` |
| đang tải (`dl`) | cả hai | — | `Đang tải…` | `var(--ctl)` / `var(--stroke2)` / `var(--txt3)` | `Chờ tải xong rồi mới dùng được giọng này` |

Ghi chú quan trọng:

- Dung lượng trong nhãn `Tải về · …` **lấy từ dòng mô tả** bằng biểu thức `/[\d,]+ MB/`,
  không có thì mặc định `620 MB`.
- Giọng `absent` bị **thêm hậu tố vào dòng mô tả**: `{{ meta }} + ' · chưa tải về máy'`.
- `isActive` = `on && !dl` → giọng đang tải hoặc chưa tải **không bao giờ** hiện nhãn tròn.
- `v.bd` = `var(--acc)` chỉ khi `on && !dl`, còn lại `var(--stroke)`.
- Bấm nút `Tải về` → đổi `dlMap[tên] = 'dl'` (chuyển sang trạng thái đang tải).
- Bấm nút `Đang tải…` → không làm gì, chỉ đóng menu đang mở.
- Bấm nút chính khi `on` đã đúng → không làm gì, chỉ đóng menu.

### 3.3 Menu `⋯` — nội dung theo từng loại giọng

Hộp menu: `position:absolute; bottom:38px; right:0; min-width:248px`, nền `var(--layer)`,
viền `var(--stroke2)`, `border-radius:8`, `box-shadow:var(--shadow)`, `padding:4`,
`z-index:40`. Mỗi dòng cao 32, `padding:0 10`, 14px. Dòng nguy hiểm dùng chữ `var(--err)`.
Vạch ngăn: cao 1px, nền `var(--divider)`, `margin:5px 8px`.

Nút `⋯` khi menu đang mở: nền `var(--sub-h)`; khi đóng: `transparent`.

**Giọng của tôi** (danh sách cứng: `Giọng chú Hoà`, `Giọng bác Tuấn`, `Giọng của tôi (thử)`):

1. `Đổi tên giọng…` → mở hộp thoại đổi tên
2. `Thêm mẫu để giọng giống hơn…` → mở hộp thoại ở bước 0 với `mode:'them'`,
   `addTo` = tên giọng, `src:'file'`, `agree:true`
3. `Nghe mẫu dài 30 giây` → chạy đúng hàm nghe thử như nút `Nghe thử`
4. — vạch ngăn —
5. `Xuất bản sao ra tệp…` → hiện thông báo loại `exp`
6. `Dùng cho một hồ sơ…` (khi `entry=0`) → đặt `active`, chuyển `entry=1`, hiện thông báo loại `use`
   · **hoặc** `Đặt làm giọng mặc định cho hồ sơ mới` (khi `entry=1`) → đặt `def`, thông báo loại `def`
7. — vạch ngăn —
8. `Xoá giọng này khỏi máy` (đỏ) → mở hộp thoại xác nhận

**Giọng có sẵn, đã tải về máy:**

1. `Nghe mẫu dài 30 giây`
2. `Xem chi tiết giọng`
3. `Dùng cho một hồ sơ…` (khi `entry=0`) · **hoặc** `Đặt làm giọng mặc định cho hồ sơ mới` (khi `entry=1`)
4. — vạch ngăn —
5. `Gỡ khỏi máy, giữ trong thư viện` (đỏ) → mở hộp thoại xác nhận

**Giọng chưa tải (`absent`)** — menu bị thay hoàn toàn:

1. `Nghe mẫu dài 30 giây`
2. `Xem chi tiết giọng`
3. — vạch ngăn —
4. `Tải về máy · {dung lượng}`

**Giọng đang tải (`dl`)** — menu bị thay hoàn toàn:

1. `Xem chi tiết giọng`
2. — vạch ngăn —
3. `Tạm dừng tải`
4. `Huỷ tải về` (đỏ)

### 3.4 Thẻ dấu cộng (cuối hàng "Giọng của tôi")

Rộng 270, `border:1.5px dashed var(--stroke2)`, `border-radius:8`, xếp dọc giữa, `gap:8`,
chữ `var(--txt3)`, khi trỏ vào nền `var(--sub-h)`:
biểu tượng `+` 26px, chữ `Nhân bản giọng mới` 14px, chữ `Cần 30 giây thu âm` 12.5px.
Bấm → `openClone`.

---

## 4. Danh mục giọng (dữ liệu mẫu)

### Giọng của tôi

| Tên | Dòng mô tả | seed sóng |
|---|---|---|
| `Giọng chú Hoà` | `Nam · nhân bản hôm nay · mẫu 76 giây · 480 MB` | 91 |
| `Giọng bác Tuấn` | `Nam · 62 tuổi · nhân bản 12/6/2026 · 480 MB` | 7 |
| `Giọng của tôi (thử)` | `Nam · mẫu 30 giây · chất lượng trung bình` | 13 |

`Giọng chú Hoà` **chỉ xuất hiện** khi `cloned = true` (vừa nhân bản xong) hoặc
`sit = 'het_luot'`, và được **chèn lên đầu** danh sách.
Giọng nào nằm trong `removed` thì bị lọc khỏi danh sách.

### Giọng có sẵn (6 giọng, thứ tự cố định)

| Tên | Dòng mô tả | seed | Trạng thái tải mặc định |
|---|---|---|---|
| `Giọng Bình An` | `Nữ · miền Bắc · trầm ấm · 620 MB` | 21 | đã có |
| `Giọng Ngọc Linh` | `Nữ · miền Nam · nhẹ nhàng · 620 MB` | 33 | đã có |
| `Giọng Xuân Vĩnh` | `Nam · miền Trung · rõ ràng · 640 MB` | 45 | đã có |
| `Giọng Minh Quân` | `Nam · miền Bắc · dứt khoát · 610 MB` | 57 | **đang tải** (`dl`) |
| `Giọng Hải Yến` | `Nữ · miền Bắc · truyền cảm · 630 MB` | 69 | **chưa tải** (`absent`) |
| `Giọng Thiện Tâm` | `Nam · miền Nam · chậm, phù hợp kinh sách · 660 MB` | 81 | **chưa tải** (`absent`) |

### Hồ sơ đọc (4 hồ sơ)

| Tên hồ sơ | Giọng gắn sẵn |
|---|---|
| `Bài viết, văn bản` | `Giọng Ngọc Linh` |
| `Thông báo ngắn` | `Giọng Xuân Vĩnh` |
| `Sách nói` | `Giọng bác Tuấn` |
| `Danh sách, biểu mẫu` | `Giọng Bình An` |

Trong dropdown đổi hồ sơ, riêng hồ sơ **đang chọn** thì cột giọng hiện `state.active`
(giọng vừa chọn), các hồ sơ khác hiện giọng gắn sẵn.

### Hàm sinh sóng âm

`wave(seed, dim)`: sinh 26 vạch bằng bộ sinh số `s = (s*9301 + 49297) % 233280`,
chiều cao mỗi vạch `h = 6 + round((s/233280) * 22)` px → khoảng **6px đến 28px**.
`dim = true` → màu `var(--rail)`, ngược lại `var(--wave)`.

---

## 5. Bốn mục điều hướng cột trái

| # | Nhãn | Số đếm | Hiện "Giọng của tôi" | Hiện "Giọng có sẵn" | Tiêu đề mục có sẵn |
|---|---|---|---|---|---|
| 0 | `Tất cả giọng` | `6 + số giọng của tôi` | có | có | `Giọng có sẵn` |
| 1 | `Giọng có sẵn` | `6` | không | có | `Giọng có sẵn` |
| 2 | `Giọng của tôi` | số giọng của tôi | có | không | — |
| 3 | `Đang tải về` | số giọng đang tải, không có thì `—` | không | chỉ giọng đang tải | `Đang tải về máy` |

Tiêu đề mục "Giọng của tôi" ghi cứng: `Giọng của tôi` — 12px, chữ in hoa,
`letter-spacing:.04em`, `var(--txt3)`, 600, `margin-bottom:10`.

Mục 3 lọc `stock` chỉ lấy thẻ có `dlBar = true`. Mục "Giọng có sẵn" chỉ hiện khi
danh sách sau lọc **còn phần tử**.

### Trạng thái rỗng (chỉ ở mục 3, khi không còn giọng nào đang tải)

`padding:80px 20px`, xếp dọc giữa, `gap:9`, chữ `var(--txt3)`:

- biểu tượng mũi tên tải xuống 34px
- `Không có giọng nào đang tải về` — 15px, `var(--txt2)`
- `Giọng chưa tải nằm ở mục “Giọng có sẵn”, bấm “Tải về” để thêm vào đây.` — 13.5px

Bấm mục điều hướng cũng đóng menu `⋯` và dropdown hồ sơ.

---

## 6. Công tắc `Mở từ` — hai lối vào

### 6.1 `Menu Giọng` (`entry = 0`)

- **Không** hiện băng "đang chọn giọng cho hồ sơ"
- Nhãn tròn trên thẻ ghi `Mặc định`
- So sánh chọn theo `state.def`
- Thanh chân bên phải: `Giọng mặc định cho hồ sơ mới: {tên giọng mặc định}`
- Menu `⋯` có dòng `Dùng cho một hồ sơ…`

### 6.2 `Chọn giọng cho hồ sơ` (`entry = 1`)

- **Hiện băng** ngay dưới thanh công cụ: `padding:11px 16px`, nền `var(--acc-soft)`,
  `border-bottom:1px solid var(--divider)`, `gap:9`:
  - biểu tượng danh sách màu `var(--acc)`
  - `Đang chọn giọng cho hồ sơ **{{ profName }}**` — 14px, `var(--txt)`, tên hồ sơ in đậm 600
  - `· giọng hiện tại: {{ current }}` — 13.5px, `var(--txt3)`
  - dồn phải: nút `Đổi hồ sơ` + mũi tên xuống, cao 28, `padding:0 10`, 13.5px, `var(--acc)`
- Nhãn tròn trên thẻ ghi `Đang dùng`
- So sánh chọn theo `state.active`
- Thanh chân bên phải: `Giọng đang dùng cho hồ sơ “{tên hồ sơ}”: {tên giọng}`
- Menu `⋯` đổi dòng thành `Đặt làm giọng mặc định cho hồ sơ mới`

### 6.3 Dropdown đổi hồ sơ

Chỉ hiện khi `profOpen`. `position:absolute; top:32px; right:0; min-width:230px`,
nền `var(--layer)`, viền `var(--stroke2)`, `border-radius:8`, `box-shadow:var(--shadow)`,
`padding:4`, `z-index:45`. Mỗi dòng cao 34, `padding:0 10`, `gap:9`:
tên hồ sơ (`flex:1`, 14px) + tên giọng (12.5px, `var(--txt3)`).
Dòng hồ sơ đang chọn: chữ đậm 600, nền `var(--sub-h)`.

Chọn một hồ sơ → đặt `prof`, đặt `active` = giọng gắn sẵn của hồ sơ đó, đóng dropdown,
đóng menu `⋯`, xoá thông báo đang hiện.

Đổi nút gạt `Mở từ` sẽ **xoá** `menu`, `profOpen`, `toast`.

### 6.4 Lớp phủ bắt cú bấm ra ngoài

Khi `profOpen` **hoặc** có menu `⋯` đang mở, chèn một lớp `position:absolute; inset:0;
z-index:35` phủ toàn khung cửa sổ. Bấm vào lớp này → đóng cả dropdown hồ sơ và menu `⋯`.
Lớp này có `z-index` **thấp hơn** menu (40) và dropdown (45) nên không che chúng.

---

## 7. Công tắc `Tình huống` — năm tình huống

Đổi tình huống sẽ **đặt lại**: `clone = -1`, `limit = false`, `mode = 'moi'`, `addTo = ''`,
`confirm = null`, `rename = null`, `toast = null`, `bg = 0`.

### 7.1 `Bình thường` (`binh_thuong`)

- Giọng của tôi: 2 giọng (`Giọng bác Tuấn`, `Giọng của tôi (thử)`)
- Dòng dung lượng: `Đã nhân bản 2/5 giọng của gói.`
- Thanh chân đếm: `8 giọng · 2 giọng của tôi · 1 đang tải`
- Bước 1 hộp thoại: đoạn chọn `Đã chọn 1:12 – 2:28 · 76 giây`, **không** có hộp đỏ chặn
- Ba dòng kiểm tra: 2 dòng đạt (xanh) + 1 dòng cảnh báo (vàng)
- Nhân bản chạy tới bước thành công

### 7.2 `Bản ghi quá ngắn` (`ngan`)

Chỉ khác ở **bước 1** của hộp thoại nhân bản:

- Đoạn chọn: `Đã chọn 0:04 – 0:16 · 12 giây`
- **Hiện hộp đỏ chặn** (viền `var(--err)`):
  - Tiêu đề: `Đoạn đã chọn quá ngắn`
  - Nội dung: `Chỉ dài 12 giây, cần ít nhất 30 giây để máy học được cách bạn nói. Kéo rộng vùng chọn, hoặc lấy tệp dài hơn.`
  - Nút sửa: `Chọn đoạn dài hơn` → chuyển tình huống về `Bình thường`
- Nút `Dùng đoạn này` **bị làm mờ** (nền `var(--stroke2)`, chữ `var(--txt3)`),
  tooltip `Bản ghi chưa đạt — chọn đoạn khác hoặc thu lại`
- Ba dòng kiểm tra đổi thành:
  1. ✕ đỏ `Đoạn đã chọn chỉ dài 12 giây` — `Cần ít nhất 30 giây liền mạch để máy học được.`
  2. ✓ xanh `Chỉ có một người nói` — `Không phát hiện giọng thứ hai trong đoạn đã chọn.`
  3. ✓ xanh `Độ ồn nền thấp` — `Nền yên, đủ để tách giọng sạch.`

### 7.3 `Hai người nói` (`hai_nguoi`)

Chỉ khác ở **bước 1**:

- Đoạn chọn: `Đã chọn 1:12 – 2:28 · 76 giây` (giống bình thường)
- **Hiện hộp đỏ chặn**:
  - Tiêu đề: `Có hai người nói trong đoạn này`
  - Nội dung: `Từ 1:48 có giọng thứ hai chen vào. Máy chỉ học được khi bản ghi có đúng một người nói.`
  - Nút sửa: `Chọn đoạn khác` → chuyển tình huống về `Bình thường`
- Nút `Dùng đoạn này` bị làm mờ, cùng tooltip như trên
- Ba dòng kiểm tra:
  1. ✕ đỏ `Phát hiện hai người nói` — `Có giọng thứ hai từ 1:48 đến hết đoạn đã chọn.`
  2. ✓ xanh `Độ ồn nền thấp` — `Nền yên, đủ để tách giọng sạch.`
  3. ⚠ vàng `Có tiếng vọng nhẹ ở phút thứ hai` — `Chọn đoạn khác nếu muốn kết quả sạch hơn.`

### 7.4 `Hết lượt nhân bản` (`het_luot`)

- Giọng của tôi: **3 giọng** (thêm `Giọng chú Hoà` lên đầu)
- Dòng dung lượng đổi thành: `Đã nhân bản 3/3 giọng — hết lượt của gói Cơ bản.`
- Thanh chân đếm: `9 giọng · 3 giọng của tôi · 1 đang tải`
- Bấm `Nhân bản giọng mới` (cả nút trên thanh công cụ và thẻ dấu cộng)
  **không** mở hộp thoại nhân bản mà mở **hộp thoại hết lượt** (xem mục 9.2)

### 7.5 `Tạo giọng lỗi` (`that_bai`)

Giống `Bình thường` cho tới lúc bấm `Bắt đầu tạo giọng`. Sau 2200 ms màn tiến độ
**không** chuyển sang bước thành công mà chuyển sang **màn báo lỗi** (bước 7, xem mục 8.7).

---

## 8. Hộp thoại nhân bản giọng — từng bước

Hiện khi `clone >= 0`. Nền phủ `rgba(0,0,0,.4)`, `z-index:70`, hộp rộng **620px**,
nền `var(--layer)`, viền `var(--stroke2)`, `border-radius:8`, `box-shadow:var(--shadow)`,
`overflow:hidden`.

Các giá trị `clone` được dùng: **0, 1, 2, 3, 4, 6, 7** (giá trị 5 không dùng).

### 8.0 Đầu hộp và dải bước

Đầu hộp: `padding:15px 18px 13px`, `border-bottom:1px solid var(--divider)`:
`{{ cloneTitle }}` 17px/600 + nút ✕ 28×28 → đóng hộp thoại.

Dải bước: `padding:12px 18px 0`, mỗi bước `flex:1` gồm vạch cao 3px
(`border-radius:2`, `margin-right:6`) và nhãn 12px.
Bước đã qua hoặc đang ở: vạch `var(--acc)`, chữ `var(--txt)`.
Bước chưa tới: vạch `var(--stroke2)`, chữ `var(--txt3)`.
Riêng bước **đang ở**: chữ đậm 600.

**Nhãn các bước** phụ thuộc `mode`:

- `mode = 'moi'` (nhân bản mới): `Nguồn` · `Kiểm tra` · `Xác nhận` · `Tạo giọng`
- `mode = 'them'` (thêm mẫu cho giọng có sẵn): `Nguồn` · `Kiểm tra` · `Cập nhật giọng`

Bước đang sáng (`stepIx`) tính như sau: `clone = 6` → bước 0; `clone = 7` → bước cuối;
`mode='them'` → `clone >= 3` thì bước 2, ngược lại `min(clone, 1)`;
`mode='moi'` → `min(clone, 3)`.

### 8.1 Tiêu đề hộp thoại theo bước

| `clone` | `mode = 'moi'` | `mode = 'them'` |
|---|---|---|
| 0 | `Nhân bản giọng mới` | `Thêm mẫu cho {tên giọng}` |
| 1 | `Kiểm tra bản ghi` | `Kiểm tra bản ghi` |
| 2 | `Đặt tên và xác nhận` | (rỗng — bước 2 không dùng ở chế độ thêm mẫu) |
| 3 | `Đang tạo giọng` | `Đang cập nhật giọng` |
| 4 | `Giọng đã sẵn sàng` | `{tên giọng} đã cập nhật` |
| 6 | `Thu âm mẫu giọng` | `Thu âm mẫu giọng` |
| 7 | `Không tạo được giọng` | `Không tạo được giọng` |

### 8.2 Chân hộp thoại — nút và điều kiện

Chân hộp: `padding:13px 18px`, `border-top:1px solid var(--divider)`, nền `var(--ctl)`.

- Nút `Quay lại` (bên trái, cao 36, `padding:0 15`, không viền) — **chỉ hiện** khi
  `clone` là 1, 2 hoặc 7
- Dồn phải: nút huỷ `{{ cloneCancel }}` — ghi `Đóng` khi `clone` là 3 hoặc 4,
  còn lại ghi `Huỷ`
- Nút tiếp `{{ cloneNext }}` — **ẩn hoàn toàn** khi `clone = 3`

**Nhãn nút tiếp:**

| `clone` | Nhãn |
|---|---|
| 0 | `Chọn tệp…` |
| 1 | `Dùng đoạn này` (mode `moi`) / `Thêm mẫu và tạo lại` (mode `them`) |
| 2 | `Bắt đầu tạo giọng` |
| 3 | (không có nút) |
| 4 | `Dùng giọng này ngay` (mode `moi`) / `Nghe thử ngay` (mode `them`) |
| 6 | `Dùng bản thu này` |
| 7 | `Tạo lại` |

**Điều kiện chặn nút tiếp** (`canNext`), khi bị chặn thì nền `var(--stroke2)`,
chữ `var(--txt3)`, và có tooltip:

| `clone` | Điều kiện đi tiếp | Tooltip khi bị chặn |
|---|---|---|
| 1 | không có hộp đỏ chặn (tình huống phải là `Bình thường`) | `Bản ghi chưa đạt — chọn đoạn khác hoặc thu lại` |
| 2 | đã tích ô xác nhận (`agree`) | `Cần tích xác nhận bạn có quyền dùng giọng này` |
| 6 | đã dừng thu **và** thời lượng ≥ 30 giây | `Bản thu cần dài ít nhất 30 giây` |
| còn lại | luôn đi tiếp được | — |

Khi đi tiếp được, tooltip là chuỗi rỗng, nền `var(--acc)`, chữ `var(--acc-txt)`.

**Đường đi của nút `Quay lại`:** `clone=7` → về 1; `clone=1` → về 6 nếu nguồn là thu âm,
về 0 nếu nguồn là tệp; còn lại → `max(0, clone-1)`.

**Đường đi của nút tiếp:** `clone=4` → mode `them`: đóng hộp, đặt lại mode/addTo, và
**bắt đầu phát thử** giọng vừa cập nhật; mode `moi`: đóng hộp, chuyển `entry=1`,
`cloned=true`, `active='Giọng chú Hoà'`, hiện thông báo loại `use`.
`clone=7` hoặc `clone=2` → chạy tạo giọng. `clone=1` → mode `them` thì chạy tạo giọng luôn,
mode `moi` thì sang bước 2. `clone=6` → sang bước 1.

### 8.3 Bước 0 — chọn nguồn (`clone = 0`)

Hai ô lớn cạnh nhau, mỗi ô `flex:1`, `padding:22px 14px`, xếp dọc giữa, `gap:9`:

**Ô trái** (viền `1.5px dashed var(--acc)`, nền `var(--acc-soft)`):
- biểu tượng mũi tên lên 26px màu `var(--acc)`
- `Tải tệp âm thanh lên` — 14.5px/600
- `Kéo thả vào đây` (xuống dòng) `hoặc bấm để chọn tệp` — 12.5px `var(--txt3)`, canh giữa
- Bấm → sang bước 1 với `src = 'file'`

**Ô phải** (viền `1px solid var(--stroke2)`, khi trỏ vào nền `var(--sub-h)`):
- biểu tượng micro 26px màu `var(--txt2)`
- `Thu âm trực tiếp` — 14.5px/600
- `Đọc theo đoạn mẫu` (xuống dòng) `khoảng 30 giây` — 12.5px
- Bấm → sang bước **6** với `src = 'rec'`, đặt lại `rec=false, recSec=0, recTick=0`

**Hộp điều kiện** phía dưới (`margin-top:16`, `padding:12px 14px`, nền `var(--ctl)`,
viền `var(--stroke2)`, `border-radius:6`):

Tiêu đề `Tệp cần đạt các điều kiện sau` 13px/600, rồi 4 dòng gạch đầu dòng 13px `var(--txt2)`:

1. `Định dạng .mp3, .wav, .m4a hoặc .flac — dưới 200 MB`
2. `Dài từ 30 giây, tốt nhất 1–3 phút`
3. `Chỉ một người nói, không nhạc nền, không tiếng vọng`
4. `Bạn phải là chủ giọng nói, hoặc được người đó đồng ý`

### 8.4 Bước 1 — kiểm tra bản ghi (`clone = 1`)

**Hàng nguồn** (`padding:11px 13px`, nền `var(--ctl)`, viền `var(--stroke2)`,
`border-radius:6`, `gap:10`):
- biểu tượng nốt nhạc `var(--txt2)`
- `{{ srcName }}` 14px, cắt bằng dấu … — `ban-thu-moi.wav` nếu nguồn là thu âm,
  `ghi-am-chu-hoa.mp3` nếu nguồn là tệp
- `{{ srcMeta }}` 13px `var(--txt3)` — nguồn tệp: `4 phút 12 giây · 18 MB`;
  nguồn thu âm: `{phút:giây} · {max(1, round(số giây × 0,17))} MB`
- Liên kết `Đổi tệp` 13px `var(--acc)` → chạy đúng hàm `Quay lại`

**Chú thích:** `Chọn đoạn dùng làm mẫu — nên lấy chỗ nói rõ, không có nhạc nền`
— 13px `var(--txt2)`, `margin-top:14`

**Dải sóng lớn:** cao 64, `padding:0 2px`, nền `var(--ctl)`, viền `var(--stroke2)`,
`border-radius:6`, `position:relative`. **60 vạch** (ghép 3 lần hàm sinh sóng với
seed 29, 53, 71). Vạch thứ **17 đến 45** màu `var(--acc)`, còn lại `var(--rail)`.
Hai tay kéo dọc rộng 2px màu `var(--acc)` ở `left:28%` và `left:58%`.

**Hàng thời gian** (`margin-top:6`, 12.5px `var(--txt3)`, tabular-nums):
`0:00` bên trái · `{{ selLabel }}` ở giữa (màu `var(--txt)`, đậm 600) · `4:12` bên phải

**Hộp đỏ chặn** — chỉ hiện ở tình huống `ngan` hoặc `hai_nguoi` (xem mục 7.2 và 7.3):
`margin-top:16`, `padding:12px 13px`, viền `1px solid var(--err)`, nền `var(--ctl)`,
biểu tượng tam giác cảnh báo màu `var(--err)`, tiêu đề 13.5px/600, nội dung 13px
`var(--txt2)`, nút sửa cao 28 `padding:0 12` nền `var(--acc)`.

**Ba dòng kiểm tra** (`margin-top:16`, `gap:8`): mỗi dòng có biểu tượng 16px màu theo
kết quả (`var(--ok)` dấu ✓ / `var(--err)` tam giác / `var(--warn)` tam giác),
tiêu đề 13.5px/600, nội dung 13px `var(--txt2)`. Nội dung ba dòng đổi theo tình huống —
xem bảng ở mục 7.

Ba dòng ở tình huống `Bình thường`:
1. ✓ xanh `Chỉ có một người nói` — `Không phát hiện giọng thứ hai trong đoạn đã chọn.`
2. ✓ xanh `Độ ồn nền thấp` — `Nền yên, đủ để tách giọng sạch.`
3. ⚠ vàng `Có tiếng vọng nhẹ ở phút thứ hai` — `Vẫn nhân bản được, nhưng giọng tạo ra sẽ hơi vang. Chọn đoạn khác nếu muốn kết quả sạch hơn.`

### 8.5 Bước 2 — đặt tên và xác nhận (`clone = 2`)

Chỉ dùng ở `mode = 'moi'`.

- Nhãn `Tên giọng` 13px `var(--txt2)`
- Ô nhập **giả** (không phải `<input>` thật): cao 36, `padding:0 11`, viền `var(--stroke2)`,
  `border-bottom:2px solid var(--acc)`, nền `var(--ctl)`, hiện chữ cứng `Giọng chú Hoà`
  kèm con trỏ nháy 1.5×16px (`animation:caret 1.1s step-end infinite`)
- Chú thích `Tên này hiện trong danh sách giọng, đổi lại lúc nào cũng được.` — 12.5px `var(--txt3)`
- **Ô tích xác nhận** (`margin-top:16`, `padding:13`, nền `var(--ctl)`, viền `var(--stroke2)`):
  - ô vuông 18×18, `border-radius:3`; khi tích: nền `var(--acc)` viền `var(--acc)` +
    dấu ✓ màu `var(--acc-txt)`; khi chưa: nền `var(--ctl)` viền `var(--stroke2)`
  - chữ 13.5px `var(--txt2)`, `line-height:1.55`:
    `Tôi xác nhận mình là chủ giọng nói trong bản ghi, hoặc đã được người đó đồng ý cho nhân bản. Giọng nhân bản chỉ nằm trên máy này, không gửi lên máy chủ.`
  - **cả ô vuông và cả đoạn chữ đều bấm được** để bật/tắt
- Ghi chú cuối: `Máy sẽ xử lý khoảng 5 phút. Trong lúc đó bạn vẫn soạn và nghe văn bản bằng giọng khác được.` — 13px `var(--txt3)`

Chưa tích ô này thì nút `Bắt đầu tạo giọng` bị làm mờ.

### 8.6 Bước 3 — đang xử lý (`clone = 3`)

Xếp dọc, canh giữa, `padding:14px 0 6px`:

- Vòng xoay 38×38, `border:3px solid var(--stroke2)`, `border-top-color:var(--acc)`,
  `animation:spin .9s linear infinite`
- `{{ makingTitle }}` 15px/600:
  - mode `moi`: `Đang học giọng từ bản ghi…`
  - mode `them`: `Đang học thêm mẫu mới…`
- `{{ makingSub }}` 13.5px `var(--txt2)`:
  - mode `moi`: `Bước 2/3 · tách giọng khỏi tạp âm · còn khoảng 3 phút`
  - mode `them`: `Bước 2/2 · trộn với mẫu đã có · còn khoảng 2 phút`
- Thanh tiến độ rộng 100%, cao 5, `border-radius:3`, nền `var(--stroke2)`,
  phần chạy **cố định 46%** nền `var(--acc)`
- Ghi chú canh giữa: `Bạn đóng cửa sổ này được — phần mềm chạy tiếp ở nền và báo khi xong.`
  — 13px `var(--txt3)`

**Không có nút tiếp** ở bước này; nút huỷ ghi `Đóng`.

Sau **2200 ms** tự chuyển: tình huống `that_bai` → bước 7; còn lại → bước 4.

**Đóng hộp thoại ở bước này = chuyển sang chạy ở nền:**
đặt `clone = -1`, `bg = 46`, `bgName` = tên giọng đang tạo
(mode `them` thì là `addTo`, mode `moi` thì là `Giọng chú Hoà`).
Thanh chân hiện vòng xoay + `Đang tạo {tên} · 46%`.
Sau **2600 ms** nữa: `bg = 0` và hiện thông báo — mode `them` loại `add`,
mode `moi` loại `new` kèm đặt `cloned = true`.

### 8.7 Bước 4 — xong (`clone = 4`)

- Hàng đầu `gap:11`: ảnh đại diện 38×38 `border-radius:19` nền `var(--acc-soft)`
  chữ `var(--acc)` (biểu tượng micro), rồi:
  - `{{ doneTitle }}` 15.5px/600 — mode `moi`: `Giọng chú Hoà đã sẵn sàng`;
    mode `them`: `{tên giọng} đã cập nhật`
  - `{{ doneMeta }}` 13px `var(--txt3)` — mode `moi`: `Nam · mẫu 76 giây · 480 MB`;
    mode `them`: `Nam · đã có 3 mẫu · 480 MB`
- Dải sóng cao 38, **52 vạch** (ghép seed 91 và 17), màu `var(--wave)`, `margin:14px 0 12px`
- Hộp ghi chú (`padding:12px 13px`, nền `var(--ctl)`, viền `var(--stroke2)`), 13.5px:
  `Nghe thử câu mẫu: “Kính gửi toàn thể cán bộ, nhân viên Công ty.”` (phần trong ngoặc kép
  màu `var(--txt)`) rồi xuống dòng
  `Chưa giống lắm? Thêm 1–2 mẫu nữa ở mục ⋯ của thẻ giọng, giọng sẽ sát hơn.`

Nút huỷ ghi `Đóng`.

### 8.8 Bước 6 — thu âm (`clone = 6`)

- **Hộp đoạn mẫu** (`padding:11px 13px`, nền `var(--ctl)`, viền `var(--stroke2)`,
  13.5px, `line-height:1.6`):
  `Đọc to, rõ đoạn dưới đây bằng giọng nói bình thường của bạn:` rồi xuống dòng, phần
  màu `var(--txt)`:
  `“Hôm nay trời trong, gió nhẹ. Tôi đang thu âm để phần mềm học giọng đọc của mình. Mong rằng bản thu đủ rõ để máy nhận ra cách tôi nói từng chữ.”`
- **Dải sóng trực tiếp** cao 64, `padding:0 2px`, nền `var(--ctl)`, viền `var(--stroke2)`,
  **60 vạch**:
  - đang thu: chiều cao `5 + (k*53) % 50` px với `k = (i*37 + recTick*13) % 97`,
    màu `var(--acc)` — dải nhảy theo nhịp đếm
  - không thu: chiều cao cố định `3px`, màu `var(--rail)`
- **Hàng điều khiển** (`margin-top:12`, `gap:11`):
  - đèn tròn 9×9 `{{ recDot }}`: đang thu → `var(--err)`; đã thu xong (có số giây) →
    `var(--ok)`; chưa thu gì → `var(--rail)`
  - `{{ recTime }}` 20px/600 tabular-nums, định dạng `phút:giây` (giây luôn 2 chữ số)
  - `{{ recHint }}` 13px `var(--txt2)` (bảng dưới)
  - nút `{{ recBtnLabel }}` cao 34, `padding:0 15`, `gap:8`
- Ghi chú cuối: `Micro đang dùng: Micro của tai nghe (Realtek) — đổi ở Cài đặt · Âm thanh. Bản thu chỉ nằm trên máy này.` — 13px `var(--txt3)`

**Bảng câu gợi ý `recHint`:**

| Trạng thái | Câu nguyên văn |
|---|---|
| đang thu, chưa đủ 30 giây | `Đang thu — cần ít nhất 30 giây, tốt nhất 1–3 phút.` |
| đang thu, đã ≥ 30 giây | `Đủ dài rồi. Đọc hết đoạn mẫu rồi bấm Dừng thu.` |
| chưa thu gì (0 giây) | `Bấm Bắt đầu thu, rồi đọc đoạn mẫu ở trên.` |
| đã dừng, ≥ 30 giây | `Bản thu đã đủ dài. Bấm “Dùng bản thu này” để sang bước kiểm tra.` |
| đã dừng, 1–29 giây | `Bản thu chỉ dài {N} giây, chưa đủ 30 giây. Thu lại nhé.` |

**Bảng nút thu:**

| Trạng thái | Nhãn | Biểu tượng | Nền | Viền | Chữ |
|---|---|---|---|---|---|
| đang thu | `Dừng thu` | ô vuông `M7 6h10v12H7z` | `var(--err)` | `var(--err)` | `#ffffff` |
| chưa thu gì | `Bắt đầu thu` | micro | `var(--ctl)` | `var(--stroke2)` | `var(--txt)` |
| đã dừng, có bản thu | `Thu lại` | micro | `var(--ctl)` | `var(--stroke2)` | `var(--txt)` |

Bộ đếm: `setInterval` **200 ms**, mỗi nhịp tăng số giây lên 1 (bản mẫu chạy nhanh gấp 5 lần
thời gian thật). Bắt đầu thu lại thì đặt lại số giây về 0.
Đóng hộp thoại lúc đang thu thì phải **dừng bộ đếm**.

### 8.9 Bước 7 — không tạo được giọng (`clone = 7`)

- Hàng đầu `gap:11`: ảnh đại diện 38×38 `border-radius:19` nền `var(--ctl)`,
  viền `1px solid var(--err)`, chữ `var(--err)`, biểu tượng tam giác cảnh báo
- Tiêu đề `Máy dừng ở bước tách giọng` 15.5px/600
- Nội dung 13.5px `var(--txt2)`:
  `Đoạn 1:12 – 2:28 có chỗ méo tiếng nên máy không học được. Bản ghi gốc vẫn còn — bạn chọn đoạn khác rồi tạo lại, hoặc thu một bản mới rõ hơn.`
- Hộp ghi chú (`margin-top:14`, `padding:12px 13px`, nền `var(--ctl)`, viền `var(--stroke2)`),
  13px: `Đã thử 1 lần, không mất lượt nhân bản nào. Nếu tạo lại vẫn lỗi, gửi bản ghi cho bộ phận hỗ trợ ở Trợ giúp · Gửi phản hồi.`
- Có nút `Quay lại` (về bước 1) và nút `Tạo lại` (chạy lại tạo giọng)

---

## 9. Các hộp thoại khác

### 9.1 Xác nhận xoá / gỡ giọng

Hiện khi `confirm` có giá trị. `z-index:80`, rộng **440px**, nền phủ `rgba(0,0,0,.4)`.

Thân (`padding:18`, `gap:12`): ảnh đại diện 34×34 `border-radius:17` nền `var(--ctl)`,
viền `1px solid var(--err)`, chữ `var(--err)`, biểu tượng tam giác; rồi tiêu đề 16px/600
và nội dung 13.5px `var(--txt2)`.

Chân: nút `Huỷ` (nền `var(--layer)`, viền `var(--stroke2)`) và nút nguy hiểm
`{{ confirmBtn }}` (nền `var(--err)`, viền `var(--err)`, chữ `#ffffff`).

| | Giọng của tôi | Giọng có sẵn |
|---|---|---|
| Tiêu đề | `Xoá {tên} khỏi máy?` | `Gỡ {tên} khỏi máy?` |
| Nội dung | `Mô hình giọng và các mẫu đã thu sẽ bị xoá hẳn khỏi máy này, không lấy lại được. Hồ sơ đang dùng giọng này sẽ chuyển về {tên giọng mặc định}.` | `Xoá mô hình khỏi ổ đĩa để lấy lại dung lượng. Giọng vẫn nằm trong thư viện, tải lại lúc nào cũng được.` |
| Nút đỏ | `Xoá giọng` | `Gỡ khỏi máy` |
| Sau khi bấm | thêm vào `removed`; nếu giọng đó đang là mặc định thì `def` chuyển về `Giọng Ngọc Linh`; nếu đang là giọng của hồ sơ thì `active` cũng chuyển về `Giọng Ngọc Linh`; hiện thông báo loại `del` | đặt `dlMap[tên] = 'absent'`; hiện thông báo loại `go` |

### 9.2 Hết lượt nhân bản

Hiện khi `limit = true`. `z-index:75`, rộng **470px**.

- Tiêu đề `Đã dùng hết lượt nhân bản` — 17px/600, `padding:17px 18px 0`
- Nội dung `Gói Cơ bản cho nhân bản 3 giọng, hiện đã dùng đủ 3. Xoá một giọng cũ để lấy chỗ, hoặc nâng gói để nhân bản thêm.` — 13.5px `var(--txt2)`
- Bảng giọng của tôi (`margin:14px 18px 16px`, viền `var(--stroke2)`, `border-radius:6`):
  mỗi hàng cao 40, `padding:0 12`, `gap:10` — tên giọng (`flex:1`, 13.5px, cắt dấu …),
  chữ `giọng nhân bản` (12.5px `var(--txt3)`), liên kết `Xoá` (13px `var(--err)`,
  trỏ vào thì gạch chân) → mở hộp thoại xác nhận xoá.
  Hàng cuối không có vạch ngăn dưới.
- Chân: `Để sau` (đóng hộp) và `Xem gói cao hơn` (nền `var(--acc)`) → đóng hộp và hiện
  thông báo loại `up`

### 9.3 Đổi tên giọng

Hiện khi `rename` có giá trị. `z-index:80`, rộng **440px**.

- Tiêu đề `Đổi tên giọng` — 17px/600
- Nhãn `Tên giọng` 13px `var(--txt2)`
- **Ô `<input>` thật** (khác bước 2 của hộp nhân bản): rộng 100%, cao 36, `padding:0 11`,
  viền `var(--stroke2)`, `border-bottom:2px solid var(--acc)`, nền `var(--ctl)`,
  `outline:none`, giá trị mở sẵn = tên hiện tại của giọng
- Chú thích `Chỉ đổi tên hiện trong thư viện và trong hồ sơ đọc. Mô hình giọng và các mẫu đã thu giữ nguyên.` — 12.5px `var(--txt3)`
- Chân: `Huỷ` và `Lưu tên mới`.
  Nút `Lưu tên mới` **chỉ bật khi ô nhập có chữ** (đã cắt khoảng trắng hai đầu):
  bật → nền `var(--acc)` chữ `var(--acc-txt)`; tắt → nền `var(--stroke2)` chữ `var(--txt3)`.
  Bấm khi tắt thì không làm gì.
- Lưu xong: ghi tên mới vào bảng tên (`names`), đóng hộp, hiện thông báo loại `ren`.
  Tên mới **thay thế tên hiển thị ở mọi nơi** (thẻ giọng, thanh chân, dropdown hồ sơ,
  tooltip, nội dung thông báo).

---

## 10. Thông báo góc (toast)

Hiện khi `toast` có giá trị. `position:absolute; right:16px; bottom:16px`, rộng **340px**,
nền `var(--layer)`, viền `var(--stroke2)`, `border-radius:8`, `box-shadow:var(--shadow)`,
`padding:13px 14px`, `z-index:60`.

- Hàng đầu: dấu ✓ 17px màu `var(--ok)`, `{{ toastTitle }}` 14.5px/600,
  nút ✕ 24×24 → đóng
- `{{ toastBody }}` 13.5px `var(--txt2)`, `line-height:1.5`
- Hàng nút (`margin-top:12`, `gap:8`):
  - Chỉ với loại `use`, `def`, `new`, `add`: liên kết `Quay lại màn hình chính`
    cao 32, `padding:0 14`, nền `var(--acc)`, chữ `var(--acc-txt)` 13.5px/600
  - Nút đóng `{{ toastClose }}` — ghi `Chọn tiếp` với loại `use` và `def`,
    còn lại ghi `Đóng`

**Chín loại thông báo, nguyên văn:**

| Loại | Tiêu đề | Nội dung |
|---|---|---|
| `use` | `Đã đổi giọng cho hồ sơ {tên hồ sơ}` | `Hồ sơ này giờ đọc bằng {tên giọng}. Các tệp trong hồ sơ sẽ dùng giọng mới ở lần nghe và lần xuất tiếp theo.` |
| `def` | `Đã đặt giọng mặc định` | `{tên giọng} sẽ được dùng cho các hồ sơ đọc tạo sau này. Các hồ sơ đang có giữ nguyên giọng của chúng.` |
| `new` | `Đã tạo xong {tên giọng}` | `Giọng nằm ở mục “Giọng của tôi”. Bấm “Dùng cho một hồ sơ…” trong thẻ giọng để gán cho hồ sơ đọc.` |
| `add` | `Đã cập nhật {tên giọng}` | `Giọng học thêm mẫu mới xong. Lần nghe và lần xuất tiếp theo sẽ dùng bản vừa cập nhật.` |
| `ren` | `Đã đổi tên giọng` | `Giọng này giờ hiện là “{tên mới}” trong thư viện và trong các hồ sơ đang dùng nó.` |
| `exp` | `Đã xuất bản sao giọng` | `Tệp {tên giọng}.giongviet nằm ở Tài liệu\GiongViet\Giọng. Chép sang máy khác là dùng lại được.` |
| `del` | `Đã xoá {tên giọng} khỏi máy` | `Mô hình và các mẫu đã thu đã bị xoá. Hồ sơ đang dùng giọng này chuyển về {tên giọng mặc định}.` |
| `go` | `Đã gỡ {tên giọng} khỏi máy` | `Giọng vẫn nằm trong thư viện. Bấm “Tải về” khi cần dùng lại.` |
| `up` | `Đã ghi nhận yêu cầu nâng gói` | `Bộ phận bán hàng sẽ liên hệ trong giờ làm việc. Trong lúc đó bạn vẫn dùng bình thường các giọng hiện có.` |

Cách mã hoá: giá trị `toast` là chuỗi `"loại:tên giọng"`. Nếu **không có dấu hai chấm**
thì mặc định là loại `use` và cả chuỗi là tên giọng. Loại không nhận ra cũng rơi về `use`.

---

## 11. Chuỗi tính động ở thanh chân và cột trái

| Biến | Công thức | Ví dụ ở trạng thái mặc định |
|---|---|---|
| `footCount` | `{6 + số giọng của tôi} giọng · {số giọng của tôi} giọng của tôi` + (nếu có giọng đang tải) ` · {số} đang tải` | `8 giọng · 2 giọng của tôi · 1 đang tải` |
| `footRight` (entry 0) | `Giọng mặc định cho hồ sơ mới: {tên giọng}` | `Giọng mặc định cho hồ sơ mới: Giọng Ngọc Linh` |
| `footRight` (entry 1) | `Giọng đang dùng cho hồ sơ “{tên hồ sơ}”: {tên giọng}` | `Giọng đang dùng cho hồ sơ “Bài viết, văn bản”: Giọng Ngọc Linh` |
| `quotaLine` (thường) | `Đã nhân bản {số}/5 giọng của gói.` | `Đã nhân bản 2/5 giọng của gói.` |
| `quotaLine` (hết lượt) | `Đã nhân bản 3/3 giọng — hết lượt của gói Cơ bản.` | — |
| `bgLabel` | `Đang tạo {tên giọng} · {số}%` | `Đang tạo Giọng chú Hoà · 46%` |

Lưu ý: `footCount` tính `6 +` cứng, **không** trừ đi giọng có sẵn đã bị gỡ khỏi máy —
gỡ giọng không làm giảm con số này.

---

## 12. Biến CSS — cả hai bộ màu

Bộ sáng khai ở `:root`, bộ tối khai ở `:root[data-theme='dark']`.
`applyTheme()` đặt thuộc tính `data-theme` trên `<html>` = `dark` khi chọn `Tối`,
= `light` khi chọn `Sáng` (gọi cả trong `componentDidMount` và `componentDidUpdate`).

| Biến | Sáng | Tối | Số lần dùng |
|---|---|---|---|
| `--bg` | `#f3f3f3` | `#202020` | 2 |
| `--layer` | `#ffffff` | `#2b2b2b` | 14 |
| `--layer2` | `#fafafa` | `#272727` | 3 |
| `--stroke` | `rgba(0,0,0,.0578)` | `rgba(255,255,255,.07)` | 3 |
| `--stroke2` | `rgba(0,0,0,.16)` | `rgba(255,255,255,.10)` | 39 |
| `--divider` | `#e5e5e5` | `#303030` | 13 |
| `--txt` | `#1a1a1a` | `#ffffff` | 50 |
| `--txt2` | `#5d5d5d` | `rgba(255,255,255,.73)` | 30 |
| `--txt3` | `#767676` | `rgba(255,255,255,.60)` | 29 |
| `--dis` | `#a3a3a3` | `rgba(255,255,255,.38)` | **0 — khai nhưng không dùng** |
| `--ctl` | `#fdfdfd` | `rgba(255,255,255,.06)` | 23 |
| `--ctl-h` | `#f6f6f6` | `rgba(255,255,255,.084)` | 2 |
| `--sub-h` | `rgba(0,0,0,.037)` | `rgba(255,255,255,.06)` | 25 |
| `--acc` | `#0067c0` | `#4cc2ff` | 36 |
| `--acc-h` | `#1a75c6` | `#47b1e8` | 5 |
| `--acc-txt` | `#ffffff` | `#000000` | 11 |
| `--acc-soft` | `rgba(0,103,192,.09)` | `rgba(76,194,255,.12)` | 5 |
| `--chip-bg` | `rgba(0,0,0,.055)` | `rgba(255,255,255,.09)` | 1 |
| `--chip-bd` | `rgba(0,0,0,.09)` | `rgba(255,255,255,.14)` | **0 — khai nhưng không dùng** |
| `--chip-fg` | `#4a4a4a` | `rgba(255,255,255,.82)` | **0 — khai nhưng không dùng** |
| `--ok` | `#0f7b0f` | `#6ccb5f` | 7 |
| `--err` | `#c42b1c` | `#ff99a4` | 15 |
| `--warn` | `#9d5d00` | `#fce100` | 2 |
| `--rail` | `#868686` | `#9a9a9a` | 6 |
| `--wave` | `rgba(0,103,192,.35)` | `rgba(76,194,255,.45)` | 3 |
| `--shadow` | `0 8px 16px rgba(0,0,0,.14)` | `0 8px 16px rgba(0,0,0,.36)` | 8 |

Hai hoạt ảnh khai ở đầu tệp:

```css
@keyframes caret { 50% { opacity: 0 } }   /* con trỏ nháy ở ô nhập giả bước 2 */
@keyframes spin  { to { transform: rotate(360deg) } }  /* vòng xoay bước 3 và thanh chân */
```

Màu ghi cứng (không qua biến), cần lưu ý vì **không đổi theo bộ màu**:
nền trang `#e6e6e6`; dải nút trạng thái phía trên dùng `#fdfdfd`, `rgba(0,0,0,.09)`,
`#0067c0`, `#fff`, `#5d5d5d`; nút đóng cửa sổ khi trỏ vào `#c42b1c`;
chữ trên nút nguy hiểm `#ffffff`.

---

## 13. Phím tắt

**Thiết kế không nêu phím tắt nào.** Trong tệp không có xử lý `keydown`, `keyup`,
`onKeyDown` hay khai báo phím tắt. Mọi tương tác đều bằng chuột.
Ô `<input>` đổi tên chỉ có `onChange`, **không** có xử lý phím Enter.

---

## 14. Khác biệt so với bản snapshot cũ trong `designs/`

(Đối chiếu chạy hai lần — một lần trước khi thư mục bị đổi tên, một lần sau. Cả hai lần
cho cùng kết quả md5 và cùng số dòng thêm/bớt.)

Bản cũ 257 dòng / 19.451 byte, md5 `db46de0b89e046b010bba750153104dd`.
Bản mới 977 dòng / 77.491 byte, md5 `b9ecf5823ee068c7b31c1e6164289d96`.
Diff: **771 dòng thêm, 51 dòng bớt**.

Đây là **thay đổi thiết kế thật**, không phải sai lệch do ghi lại: nội dung được lấy
nguyên khối từ trường `content` của phản hồi công cụ (`truncated = false`) và ghi ra tệp
bằng mã, không qua bước gõ lại. 51 dòng bị bớt đều là **bản tĩnh cũ bị thay bằng bản
có trạng thái**, không có dấu hiệu mất ký tự hay cắt dòng.

Bản cũ chỉ có: dải nút `Sáng`/`Tối`, khung cửa sổ, cột trái, thanh công cụ, thẻ giọng
tĩnh và thanh chân ghi cứng `8 giọng · 2 giọng của tôi`. Toàn bộ những thứ dưới đây
là **mới**:

**Công tắc trạng thái mới**
- Nhóm `Mở từ` (`Menu Giọng` / `Chọn giọng cho hồ sơ`)
- Nhóm `Tình huống` với 5 giá trị
- Hai biến màu mới `--err` và `--warn` (cả hai bộ sáng/tối)
- Hai hoạt ảnh `caret` và `spin`
- Mở màn hình bằng đường dẫn `?thuam` và `?nhanban`

**Khối giao diện mới**
- Băng "Đang chọn giọng cho hồ sơ …" kèm dropdown `Đổi hồ sơ` (4 hồ sơ)
- Hộp thoại nhân bản 620px với 7 bước: chọn nguồn, kiểm tra bản ghi, đặt tên và xác nhận,
  đang xử lý, xong, thu âm, báo lỗi
- Hộp thoại `Đã dùng hết lượt nhân bản` (470px)
- Hộp thoại xác nhận xoá/gỡ giọng (440px)
- Hộp thoại `Đổi tên giọng` (440px, có `<input>` thật)
- Thông báo góc với 9 loại nội dung
- Thanh tải về trong thẻ giọng + trạng thái `Đang tải…` / `Tải về · {dung lượng}`
- Trạng thái rỗng `Không có giọng nào đang tải về`
- Chỉ báo chạy nền ở thanh chân (vòng xoay + phần trăm)
- Menu `⋯` với nội dung thật (bản cũ chỉ có nút `⋯` chết, `title="Tuỳ chọn"`)
- Lớp phủ bắt cú bấm ra ngoài

**Nhãn chữ đổi**
- Nút chính trên thẻ: bản cũ chỉ có `Đang dùng` / `Dùng giọng này`.
  Bản mới có 6 nhãn: `Giọng mặc định`, `Đặt làm mặc định`, `Đang dùng`,
  `Dùng cho hồ sơ này`, `Tải về · {dung lượng}`, `Đang tải…`
- Nhãn tròn: bản cũ ghi cứng `Đang dùng`. Bản mới đổi theo lối vào: `Đang dùng` / `Mặc định`
- Nút nghe thử: bản cũ ghi cứng `Nghe thử`. Bản mới thêm `Đang nghe…`
- Tiêu đề mục có sẵn: bản cũ ghi cứng `Giọng có sẵn`. Bản mới đổi thành
  `Đang tải về máy` ở mục điều hướng thứ 4
- Dòng dung lượng cột trái: bản cũ `Đã dùng 6,4 GB cho mô hình giọng.` +
  `Còn trống 128 GB.`. Bản mới thêm dòng hạn mức nhân bản phía trên và gộp câu thành
  `Đã dùng 6,4 GB cho mô hình giọng, còn trống 128 GB.`
- Thanh chân: bản cũ ghi cứng 2 chuỗi. Bản mới tính động cả hai
- Tooltip: bản cũ chỉ có `Quay lại màn hình chính` và `Tuỳ chọn`.
  Bản mới có tooltip cho mọi nút chính, nút nghe thử, nút `⋯`, và nút tiếp khi bị chặn

**Nút chết được nối vào chức năng thật**
- Nút mũi tên quay lại ở cột trái: bản cũ là `<div>` chết → bản mới là `<a href>`
  trỏ tới tệp màn hình chính
- Nút viên thuốc `Màn hình chính` ở thanh tiêu đề: **hoàn toàn mới**
- Nút `Nhân bản giọng mới` (thanh công cụ) và thẻ dấu cộng: bản cũ chết → bản mới gọi `openClone`

**Số liệu đổi**
- Số đếm mục điều hướng: bản cũ ghi cứng `8` / `6` / `2` / `—`.
  Bản mới tính động theo số giọng của tôi và số giọng đang tải
- Khung cửa sổ thêm `position:relative` (bắt buộc để định vị hộp thoại và lớp phủ)

---

## 15. Những chỗ cần chú ý khi làm thật

1. **Một nguồn phát tiếng tại một thời điểm.** `state.playing` là một tên duy nhất.
   Bấm nghe thử giọng khác phải dừng giọng đang phát. Tự dừng sau 4 giây (bản mẫu);
   bản thật là hết mẫu thì dừng.
2. **Đóng hộp thoại ở bước "đang xử lý" không phải là huỷ** — nó chuyển việc sang chạy
   ở nền và báo bằng thông báo góc khi xong. Đây là hành vi có chủ ý, không phải nút huỷ.
3. **Đóng hộp thoại lúc đang thu âm phải dừng bộ đếm/bộ thu.**
4. **Xoá giọng đang được dùng phải có đường lùi:** cả `def` và `active` đều phải
   chuyển về `Giọng Ngọc Linh`.
5. **Giọng chưa tải / đang tải không được hiện nhãn tròn** và không được viền nhấn,
   dù nó đang là giọng mặc định.
6. `--dis`, `--chip-bd`, `--chip-fg` khai nhưng chưa dùng — đừng suy ra là thiếu sót,
   cứ giữ nguyên.
7. Bản mẫu chạy nhanh hơn thật: bộ đếm thu âm 200 ms = 1 giây, tạo giọng 2200 ms,
   chạy nền 2600 ms. Con số thật lấy theo lời trong giao diện: xử lý **khoảng 5 phút**.
8. Thanh tiến độ tải về và tiến độ tạo giọng đều **ghi cứng 46%** trong bản mẫu.
9. Ô nhập tên ở bước 2 hộp nhân bản là **ô giả** (chữ cứng `Giọng chú Hoà` + con trỏ nháy),
   còn ô đổi tên ở hộp thoại riêng là `<input>` thật. Bản thật cần ô nhập thật ở cả hai chỗ.
