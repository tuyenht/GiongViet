# Bản kiểm kê trạng thái — màn hình "Văn bản ghép"

Nguồn: `C:/Projects/DocCongDuc/design_handoff_giongdoc/designs-goc/GiongDoc - Văn bản ghép.dc.html`
(85.641 ký tự, kết thúc bằng `</html>`, không bị cắt giữa)

Ngày lập: 17/8/2026. Đây là bản mẫu tương tác tự chạy được (`.dc.html`), có `<script type="text/x-dc">`
chứa toàn bộ logic. Bản kiểm kê này ghi lại **mọi trạng thái, mọi chuỗi tiếng Việt, mọi quy tắc hiển
thị** để lập trình không cần mở lại tệp thiết kế.

---

## 0. TÓM TẮT MỘT CÂU

Màn hình cấu hình **khuôn đọc (mẫu ghép)**: chọn nguồn bảng tính → khớp từng cột với vai trò và cách
đọc → lọc/nhóm dòng → viết bốn khối văn bản (đầu / mẫu câu mỗi dòng / câu xen giữa / cuối) → xem trước
"Bản ghép hoàn chỉnh" ở cột phải → bấm "Mở bản ghép để nghe" để quay về màn hình chính.

---

## 1. DẢI NÚT PHÍA TRÊN KHUNG CỬA SỔ — DANH SÁCH ĐẦY ĐỦ

Khai báo props của bản mẫu (thuộc tính `data-props` của thẻ script):

```json
{"theme":{"editor":"enum","options":["sang","toi"],"default":"sang",
          "tsType":"'sang'|'toi'","section":"Trạng thái"}}
```

**Chỉ có MỘT công tắc trong dải nút phía trên khung cửa sổ:**

| Công tắc | Các giá trị (nguyên văn nhãn) | Mặc định |
|---|---|---|
| Bộ màu (theme) | `Sáng` · `Tối` | `Sáng` |

> **Lưu ý quan trọng:** tệp này **KHÔNG có** các công tắc "Tình huống: …", "Mở từ: …", "Bước: …".
> Mọi trạng thái khác của màn hình được đổi **bằng cách bấm trực tiếp trong bản mẫu** (chọn mục ở dải
> bên trái, bật/tắt công tắc, mở dropdown, mở hộp thoại). Xem mục 2 để biết danh sách trạng thái nội tại.

### Hình thức dải nút

Đặt trên khung cửa sổ, khối rộng 1440px, căn giữa, `margin: 0 auto 14px`, `display:flex`, `gap:14px`:

1. Nhãn chữ hoa nhỏ: **"Văn bản ghép"** — `font-size:12px; letter-spacing:.05em;
   text-transform:uppercase; color:#5d5d5d; font-weight:600`
2. Câu mô tả: **"Một mẫu ghép cho mỗi loại danh sách · phần tĩnh bạn viết, phần động lấy từ bảng tính"**
   — `font-size:13px; color:#5d5d5d`
3. Nhóm nút Sáng/Tối, đẩy sang phải bằng `margin-left:auto`:
   - vỏ ngoài: `display:flex; gap:3px; padding:3px; background:#fdfdfd;
     border:1px solid rgba(0,0,0,.09); border-radius:6px`
   - mỗi nút: `border:0; cursor:pointer; font:600 13px 'Segoe UI Variable Text','Segoe UI',Inter,sans-serif;
     padding:7px 12px; border-radius:4px`
   - **đang chọn:** `background:#0067c0; color:#fff`
   - **không chọn:** `background:transparent; color:#5d5d5d`

Bấm nút → `setState({theme:id})`. Hàm `applyTheme()` đặt `data-theme="dark"` lên `documentElement`
khi theme là `toi`, ngược lại `"light"`.

---

## 2. TRẠNG THÁI NỘI TẠI (đổi bằng cách bấm trong bản mẫu)

```js
state = { theme: null, mau: 0, maus: null, docs: null, nav: 0, stale: true,
          mauMenu: false, newOpen: false, renaming: false, renameVal: '' };
```

| Biến | Ý nghĩa | Giá trị / mặc định |
|---|---|---|
| `theme` | bộ màu | `null` → dùng prop → `'sang'` |
| `mau` | chỉ số mẫu ghép đang mở | `0` |
| `maus` | danh sách mẫu ghép trong hồ sơ | `null` → dùng mặc định 2 mẫu |
| `docs` | mọi thay đổi người dùng nhập, gom theo id mẫu | `null` |
| `nav` | mục đang chọn ở dải trái (0…6) | `0` |
| `stale` | dữ liệu bảng tính đã cũ (chưa lấy được bản mới) | `true` |
| `mauMenu` | đang mở dropdown chọn mẫu | `false` |
| `newOpen` | đang mở hộp thoại "Tạo mẫu ghép mới" | `false` |
| `renaming` | đang đổi tên mẫu (ô nhập thay dropdown) | `false` |
| `renameVal` | giá trị đang gõ khi đổi tên | `''` |

**Lưu bền:** `localStorage` khoá `giongviet.ghep.v2`, chỉ lưu 4 khoá `['mau','maus','docs','nav']`.
Đọc lại ở `componentDidMount()`; ghi ở mỗi `componentDidUpdate()`. Lỗi JSON hoặc hết chỗ lưu thì bỏ qua
im lặng.

**Trả về ban đầu (`resetAll`):** xoá khoá localStorage, đặt lại
`{mau:0, maus:null, docs:null, nav:0, stale:true, mauMenu:false, newOpen:false, renaming:false}`.

### Cấu trúc `docs[idMẫu]` — mọi thứ người dùng sửa được

| Khoá | Nội dung | Mặc định khi chưa sửa |
|---|---|---|
| `on` | `{dau, giua, cuoi}` bật/tắt ba khối tĩnh | `{dau:true, giua:false, cuoi:true}` |
| `rule` | `{trong, trung, thutu}` ba quy tắc lọc | `{trong:true, trung:true, thutu:true}` |
| `group` | bật đọc tên nhóm | `true` |
| `text` | `{dau, mau, giua, cuoi}` bốn khối văn bản | lấy từ khuôn mẫu (preset) |
| `sauMoi` | số dòng giữa hai lần đọc câu xen giữa | `'30'` |
| `src` | chỉ số nguồn dữ liệu (0/1/2) | lấy từ preset (`P.src`) |
| `srcVal` | giá trị ô nhập nguồn, theo từng chỉ số | lấy từ `P.srcVal[srcIdx]` |
| `sheet` | tên bảng trong tệp | `P.sheet` |
| `headRow` | dòng tiêu đề | `'Dòng 1'` |
| `auto` | tự kiểm tra định kỳ | `true` |
| `roles` | `{chữCột: {use, read}}` vai trò + cách đọc từng cột | lấy từ preset |
| `dupCol` | cột dùng để so trùng | cột đầu tiên không "Bỏ qua" |
| `dFrom` / `dTo` | khoảng ngày | `'2026-07-01'` / `'2026-08-15'` |

---

## 3. CẤU TRÚC BỐ CỤC

Khung cửa sổ: **rộng 1440px, cao 900px cố định**, căn giữa, `background:var(--bg)`,
`border:1px solid rgba(0,0,0,.22)`, `border-radius:8px`,
`box-shadow:0 16px 32px rgba(0,0,0,.22)`, `overflow:hidden`, `display:flex; flex-direction:column`,
`color:var(--txt)`.

Thứ tự từ trên xuống trong khung:

```
┌─ (1) Thanh tiêu đề cửa sổ .......................... cao 32px, flex:none
├─ (2) Băng cảnh báo dữ liệu cũ (chỉ khi stale) ...... flex:none, margin 0 8px 8px
├─ (3) Thân ......................................... flex:1, padding 0 8px 8px
│     ┌ (3a) Dải trái ............ rộng 240px cố định, padding-right 8px
│     ├ (3b) Khung giữa ........... flex:1 (co giãn)
│     └ (3c) Khung xem trước phải . rộng 392px cố định, padding-left 8px
├─ (4) Thanh dưới ................................... cao 46px, flex:none
├─ (5) Màn che đóng dropdown (chỉ khi mauMenu) ....... position:absolute inset:0, z-index 40
└─ (6) Hộp thoại "Tạo mẫu ghép mới" (chỉ khi newOpen)  position:absolute inset:0, z-index 60
```

Bên trong (3b) Khung giữa (`background:var(--layer)`, `border:1px solid var(--stroke)`,
`border-radius:8px`, `overflow:hidden`):

```
┌ Đầu mục ......... cao 52px, padding 0 18px, border-bottom 1px var(--divider)
└ Vùng cuộn ....... flex:1, overflow-y:auto, padding 18px, scrollbar mảnh
```

Bên trong (3c) Khung xem trước:

```
┌ Đầu ....... cao 44px, padding 0 14px, border-bottom 1px var(--divider)
├ Vùng cuộn . flex:1, overflow-y:auto, padding 12px, các khối cách nhau 10px
└ Chân ...... padding 11px 13px, border-top 1px var(--divider), background var(--layer2)
```

Nền trang bên ngoài khung: `body { margin:0; padding:28px 24px 40px; background:#e6e6e6;
font-family:'Segoe UI Variable Text','Segoe UI',Inter,sans-serif; -webkit-font-smoothing:antialiased }`.
Có `@keyframes spin{to{transform:rotate(360deg)}}` khai báo nhưng **không dùng ở đâu** trong tệp này.

---

## 4. (1) THANH TIÊU ĐỀ CỬA SỔ — cao 32px

Trái (`gap:9px`, `padding-left:12px`):
- Ô vuông 16×16, `border-radius:3px`, `background:var(--acc)`; bên trong SVG 10×10 hình bốn thanh dọc
  cao thấp khác nhau (`M4 9v6M9 5v14M14 8v8M19 11v2`), `stroke:var(--acc-txt)`, `stroke-width:2.6`.
- Chữ **"Văn bản ghép — Giọng Việt"** — `font-size:12.5px; color:var(--txt2)`.
- Chip liên kết quay lại: `<a href="GiongDoc - Màn hình chính v2 (nghe theo dòng).dc.html">`
  (URL đã mã hoá phần trăm), cao 22px, `padding:0 10px 0 7px`, `border-radius:11px`,
  `background:var(--sub-h)`, `color:var(--txt2)`, `font-size:12px`; hover `color:var(--txt)`;
  `title="Quay lại màn hình chính"`; nội dung = mũi chevron trái 11px + chữ **"Màn hình chính"**.

Phải (`margin-left:auto`): ba ô 46×32, `cursor:default` (chỉ mô phỏng):
| Nút | title | Hình | Hover |
|---|---|---|---|
| Thu nhỏ | `Thu nhỏ` | gạch ngang `M1 6h10` | `background:var(--sub-h)` |
| Phóng to | `Phóng to` | ô vuông rỗng 9×9 `rx=1` | `background:var(--sub-h)` |
| Đóng | `Đóng` | dấu X | `background:var(--close); color:#fff` |

---

## 5. (2) BĂNG CẢNH BÁO DỮ LIỆU CŨ — hiện khi `stale === true` (MẶC ĐỊNH LÀ HIỆN)

Khung: `margin:0 8px 8px; padding:11px 13px; border-radius:6px; background:var(--warn-bg);
border:1px solid var(--warn-bd)`, `display:flex; align-items:flex-start; gap:11px`.

- Biểu tượng tam giác cảnh báo 18×18, `color:var(--warn)`, `stroke-width:1.7`.
- **Tiêu đề** (`font-size:14px; font-weight:600; color:var(--txt)`), nguyên văn:
  > "Chưa lấy được danh sách mới, đang dùng bản đã tải lúc 14:03 hôm nay"
- **Thân** (`font-size:13.5px; line-height:1.5; color:var(--txt2)`), ghép động, nguyên văn:
  > "{SỐ DÒNG} dòng của bản cũ vẫn đọc và xuất được bình thường. Nếu bảng tính vừa thêm dòng, hãy thử lấy lại trước khi đọc."

  (với mẫu mặc định "Danh sách công đức", `{SỐ DÒNG}` = `248`)
- Hai nút bên phải (`gap:8px`):
  | Nhãn nguyên văn | Kiểu | Hành vi |
  |---|---|---|
  | **"Vẫn dùng bản cũ"** | nút chữ trơn, cao 32px, `padding:0 13px`, hover `background:var(--sub-h)` | `stale = false` |
  | **"Thử lấy lại"** | cao 32px, `padding:0 14px`, `background:var(--ctl)`, `border:1px solid var(--stroke2)`, hover `background:var(--ctl-h)` | `stale = false` |

**Khi `stale === false`:** cả băng cảnh báo biến mất; đèn ở thanh dưới đổi từ vàng sang xanh và câu
trạng thái đổi (xem mục 9).

---

## 6. (3a) DẢI TRÁI — rộng 240px

### 6.1 Hàng đầu (min-height 44px, `padding:0 6px 0 10px`, `position:relative`)

1. Nút mũi chevron trái 30×30, `border-radius:4px`, hover `background:var(--sub-h)`,
   `title="Quay lại màn hình chính"`, liên kết về màn hình chính.

2. **Khi KHÔNG đổi tên** (`notRenaming`): nút mở dropdown — `flex:1`, cao 34px,
   `padding:0 4px 0 8px`, `border:1px solid var(--stroke2)`, `background:var(--ctl)`,
   `border-radius:4px`, hover `background:var(--ctl-h)`.
   - Tên mẫu: `font-size:14.5px; font-weight:600; color:var(--txt)`, cắt bằng `text-overflow:ellipsis`.
   - Chevron xuống 13px, `stroke:var(--txt2)`.
   - `title` ghép động, nguyên văn: **"Mẫu {i}/{n} trong hồ sơ này — bấm để đổi mẫu, đổi tên hoặc tạo mẫu mới"**
     (ví dụ mặc định: "Mẫu 1/2 trong hồ sơ này — bấm để đổi mẫu, đổi tên hoặc tạo mẫu mới").

3. **Khi đang đổi tên** (`renaming === true`): dropdown bị thay bằng ô nhập —
   `flex:1`, cao 32px, `padding:0 8px`, `border:1px solid var(--stroke2)`,
   **`border-bottom:2px solid var(--acc)`**, `border-radius:4px`, `background:var(--ctl)`,
   `font:600 15px …`, `spellCheck=false`, `outline:none`.
   - Tự động `focus()` + `select()` khi vừa hiện (cờ `_focusRename`).
   - **Enter** → lưu tên; **Escape** → thôi đổi tên, không lưu; **mất tiêu điểm (blur)** → lưu tên.
   - Lưu: chỉ nhận tên sau khi `trim()` còn khác rỗng; tên rỗng thì giữ tên cũ. Sau đó `renaming = false`.

### 6.2 Dropdown chọn mẫu — hiện khi `mauMenu === true`

`position:absolute; left:6px; top:42px; z-index:45; width:268px; background:var(--layer);
border:1px solid var(--stroke2); border-radius:8px; box-shadow:var(--shadow); padding:5px`.

Từ trên xuống:
1. Nhãn nhóm chữ hoa: **"Mẫu ghép trong hồ sơ này"** — `padding:7px 9px 5px; font-size:11.5px;
   letter-spacing:.04em; text-transform:uppercase; color:var(--txt3); font-weight:600`.
2. Danh sách mẫu (mặc định 2 dòng), mỗi dòng min-height 38px, `padding:5px 9px`, `border-radius:4px`,
   hover `background:var(--sub-h)`:
   - tên mẫu `font-size:14px`, `font-weight:600` nếu là mẫu hiện tại, `400` nếu không;
   - dòng phụ `font-size:12px; color:var(--txt3)` — nguyên văn ghép: **"{số dòng} dòng · {tên khuôn mẫu}"**
     (ví dụ: "248 dòng · Danh sách công đức", "96 dòng · Quyên góp, ủng hộ");
   - nền `var(--acc-soft)` nếu là mẫu hiện tại, ngược lại trong suốt;
   - dấu tích 15px `color:var(--acc)` chỉ hiện ở mẫu hiện tại;
   - `title` = **"{tên mẫu} — {số dòng} dòng"**;
   - bấm → đổi mẫu, đóng menu, đưa `nav` về `0`.
3. Đường kẻ 1px `var(--divider)`, `margin:5px 0`.
4. **"Tạo mẫu ghép mới…"** — cao 34px, `color:var(--acc)`, có dấu cộng 15px. Bấm → mở hộp thoại
   (`newOpen = true`), đóng menu.
5. **"Đổi tên mẫu này"** — cao 32px, `color:var(--txt)`. Bấm → vào chế độ đổi tên, đóng menu.
6. **"Xoá mẫu này"** — **chỉ hiện khi có nhiều hơn 1 mẫu** (`canDelete`). Cao 32px,
   hover `background:var(--sub-h); color:var(--err)`.
   Xoá: bỏ mẫu khỏi danh sách, xoá `docs[id]` của mẫu đó, chuyển sang mẫu ngay trước
   (`max(0, chỉSốHiệnTại - 1)`), đóng menu. Nếu chỉ còn 1 mẫu thì hàm thoát ngay, không xoá.

Kèm **màn che** `position:absolute; inset:0; z-index:40` ở cấp khung cửa sổ; bấm vào → đóng menu.

### 6.3 Danh sách 7 mục điều hướng (gap 2px, margin-top 4px)

Mỗi mục: `position:relative; min-height:38px; padding:6px 10px 6px 13px; border-radius:5px; gap:9px`,
hover `background:var(--sub-h)`, `title = "{nhãn} — {dòng phụ}"`.

- **Vạch chỉ báo trái:** `position:absolute; left:2px; top:50%; margin-top:-9px; width:3px; height:18px;
  border-radius:2px` — `var(--acc)` khi đang chọn, trong suốt khi không.
- **Đèn tròn:** 7×7, `border-radius:4px`, `border:1px solid …`
  - có cảnh báo → nền và viền `var(--warn)`
  - phần đang tắt → nền trong suốt, viền `var(--stroke2)`
  - bình thường → nền và viền `var(--ok)`
- **Nhãn:** `font-size:14px; line-height:1.3`, `font-weight:600` khi đang chọn, `400` khi không.
- **Dòng phụ:** `font-size:12px; line-height:1.4; color:var(--txt3)`, cắt bằng ellipsis.
- **Nền mục đang chọn:** `background:var(--layer); border:1px solid var(--stroke)`;
  mục khác: nền và viền trong suốt.

| # | Nhãn nguyên văn | Dòng phụ (nguyên văn / công thức) | Có công tắc bật-tắt? | Đèn cảnh báo |
|---|---|---|---|---|
| 0 | **Nguồn dữ liệu** | tên nguồn đang chọn: `Dán link chia sẻ công khai` / `Đăng nhập Google` / `File trên máy` | không | không |
| 1 | **Khớp cột** | `"{n} cột đang dùng"`, cộng thêm `" · cần xem lại"` nếu có vấn đề | không | **có** — bật khi có ít nhất 1 vấn đề |
| 2 | **Lọc & nhóm** | các bộ lọc đang bật, nối bằng `" · "` từ tập `bỏ dòng thiếu` · `gộp trùng` · `nhóm theo cột`; nếu không bật cái nào → `"không lọc"` | không | không |
| 3 | **Đầu danh sách** | `"Đang bật · {n} đoạn"` hoặc `"Đang tắt"` | có (khoá `dau`, mặc định BẬT) | không |
| 4 | **Mẫu câu mỗi dòng** | `"Luôn đọc · {số dòng} dòng"` | **không** (luôn đọc) | không |
| 5 | **Câu xen giữa** | `"Sau mỗi {N} dòng"` hoặc `"Đang tắt"` | có (khoá `giua`, mặc định TẮT) | không |
| 6 | **Cuối danh sách** | `"Đang bật · {n} đoạn"` hoặc `"Đang tắt"` | có (khoá `cuoi`, mặc định BẬT) | không |

"{n} đoạn" đếm bằng cách tách chuỗi theo **hai dòng trống trở lên** (`/\n{2,}/`), bỏ đoạn rỗng.

### 6.4 Chân dải trái

- Ghi chú (`margin-top:auto; padding-top:8px; border-top:1px solid var(--divider); padding-left:4px;
  font-size:13px; color:var(--txt3); line-height:1.55`), nguyên văn:
  > "Mẫu này thuộc hồ sơ **Danh sách, biểu mẫu**. Các hồ sơ khác không bị ảnh hưởng."

  (chữ "Danh sách, biểu mẫu" là `<strong style="color:var(--txt2); font-weight:600">`)
- Nút **"Trả mẫu về ban đầu"** — cao 30px, `padding:0 8px`, `border-radius:4px`, `font-size:13px`,
  `color:var(--txt3)`, hover `background:var(--sub-h); color:var(--txt2)`; có biểu tượng mũi tròn 13px.
  `title="Xoá mọi thay đổi bạn đã nhập, trả các mẫu về nội dung ban đầu"`. Bấm → chạy `resetAll`.

---

## 7. (3b) KHUNG GIỮA — bảy trạng thái theo `nav`

### 7.1 Đầu mục (52px) — thay đổi theo `nav`

| `nav` | Tiêu đề (17px/600) | Câu gợi ý bên cạnh (13px, `var(--txt3)`) |
|---|---|---|
| 0 | **Nguồn dữ liệu** | "Nơi lấy danh sách và lúc nào lấy lại" |
| 1 | **Khớp cột** | "Phần mềm tự đoán, bạn sửa lại nếu đoán sai" |
| 2 | **Lọc & nhóm** | "Dòng nào được đọc, đọc theo thứ tự nào" |
| 3 | **Đầu danh sách** | "Phần tĩnh — bạn viết một lần, dùng cho mọi lần đọc" |
| 4 | **Mẫu câu mỗi dòng** | "Phần động — mỗi dòng bảng tính thành một câu" |
| 5 | **Câu xen giữa** | "Phần tĩnh — bạn viết một lần, dùng cho mọi lần đọc" |
| 6 | **Cuối danh sách** | "Phần tĩnh — bạn viết một lần, dùng cho mọi lần đọc" |

**Công tắc bật/tắt phần** — chỉ hiện ở `nav` 3, 5, 6 (`secCanOff`). Đặt `margin-left:auto`, cao 30px,
`padding:0 4px 0 10px`, hover `background:var(--sub-h)`, `title="Tắt thì phần này không được đọc"`.
- Nhãn (13.5px, `var(--txt2)`): **"Đang đọc phần này"** khi bật / **"Đang bỏ qua phần này"** khi tắt.
- Công tắc: rãnh 40×20 `border-radius:10px`, `padding:0 3px`; núm 12×12 `border-radius:6px`.
  - **Bật:** rãnh `background:var(--acc)`, viền `var(--acc)`, núm `var(--acc-txt)`, `justify-content:flex-end`.
  - **Tắt:** rãnh trong suốt, viền `var(--stroke2)`, núm `var(--txt2)`, `justify-content:flex-start`.
  (Đây là mẫu công tắc dùng lại ở mọi nơi trong màn hình — hàm `sw(on)`.)

### 7.2 Băng "có vấn đề" — hiện khi có ít nhất 1 vấn đề, ở ĐẦU vùng cuộn của MỌI mục

Khung: `padding:11px 13px; margin-bottom:16px; border-radius:6px; background:var(--warn-bg);
border:1px solid var(--warn-bd)`; tam giác cảnh báo 17px `color:var(--warn)`.
Mỗi dòng vấn đề: `font-size:13.5px; line-height:1.5; color:var(--txt)`.

Nút **"Mở Khớp cột"** ở bên phải — **chỉ hiện khi `nav !== 1`** — cao 30px, `padding:0 13px`,
`background:var(--ctl)`, `border:1px solid var(--stroke2)`, hover `background:var(--ctl-h)`.
Bấm → `nav = 1`.

**Năm câu vấn đề, nguyên văn (theo đúng thứ tự sinh ra):**

1. "Mẫu câu đang trống — các dòng trong bảng tính sẽ không được đọc."
   — khi khối "Mẫu câu mỗi dòng" chỉ có khoảng trắng.
2. "Mẫu câu đang dùng {danh sách biến, nối bằng `, `} nhưng không cột nào cấp dữ liệu này (hoặc cột đó đang đặt “Bỏ qua”) — những chỗ đó sẽ bị đọc trống."
   — khi mẫu câu chứa `{biến}` mà không cột nào cấp. Biến khớp theo `/\{[a-z0-9]+\}/g`, loại trùng lặp.
3. "Cột {chữ cột} ({tên cột}) cũng đặt “{vai trò}”, nhưng mỗi mẫu chỉ dùng được một cột — cột {chữ cột được dùng} được dùng, cột {chữ cột bị bỏ} bị bỏ."
   — sinh một dòng cho MỖI cột trùng vai trò độc quyền (`Nhóm theo cột này`, `Lọc theo ngày`).
   Cột **xuất hiện trước** thắng.
4. "Đang bật đọc tên nhóm nhưng chưa có cột nào đặt “Nhóm theo cột này”."
5. "Chưa có cột nào đặt “Lọc theo ngày” — bộ lọc khoảng ngày sẽ bị bỏ qua."

> Với dữ liệu mặc định (mẫu "Danh sách công đức"), **không có vấn đề nào** — băng này ẩn, đèn ở mục
> "Khớp cột" là xanh.

---

### 7.3 `nav = 0` — NGUỒN DỮ LIỆU

#### a) Ba thẻ chọn nguồn (radio), gap 8px

Mỗi thẻ: `padding:13px 14px; border-radius:6px; gap:11px`, hover `background:var(--sub-h)`.
- Vòng radio 18×18 `border-radius:9px; border:1.5px solid`; điểm giữa 8×8.
- Tiêu đề `font-size:14.5px; font-weight:600; color:var(--txt)`.
- Giải thích `font-size:13px; line-height:1.5; color:var(--txt2); margin-top:2px`.
- Nhãn nhỏ bên phải: `font-size:12px; font-weight:600; padding:3px 8px; border-radius:4px`.

| Trạng thái | Nền thẻ | Viền thẻ | Vòng radio | Điểm giữa | Nhãn | Nền nhãn / viền / chữ |
|---|---|---|---|---|---|---|
| Đang chọn | `var(--acc-soft)` | `var(--acc)` | `var(--acc)` | `var(--acc)` | **"Đang dùng"** | `var(--acc)` / `var(--acc)` / `var(--acc-txt)` |
| Không chọn | `var(--layer2)` | `var(--stroke)` | `var(--stroke2)` | trong suốt | **"Có sẵn"** | `var(--chip-bg)` / `var(--chip-bd)` / `var(--chip-fg)` |

Ba nguồn, nguyên văn:

| # | Nhãn | Giải thích |
|---|---|---|
| 0 | **Dán link chia sẻ công khai** | "Bảng tính phải bật “Bất kỳ ai có đường liên kết đều xem được”. Không cần đăng nhập, cài xong dùng ngay." |
| 1 | **Đăng nhập Google** | "Đăng nhập một lần, sau đó chọn bảng tính từ Drive. Dùng được cả bảng riêng tư, không cần đổi quyền chia sẻ." |
| 2 | **File trên máy** | "Chọn tệp .xlsx hoặc .csv đã tải về. Không cần mạng — dùng khi mất Internet." |

#### b) Thẻ nhập nguồn (`margin-top:16px; padding:14px; background:var(--layer2);
border:1px solid var(--stroke); border-radius:6px`)

- Nhãn ô nhập (`font-size:13px; color:var(--txt2); margin-bottom:6px`) — đổi theo nguồn:

| Nguồn | Nhãn | Placeholder |
|---|---|---|
| 0 | **"Link chia sẻ của bảng tính"** | "Dán link https://docs.google.com/spreadsheets/…" |
| 1 | **"Tệp đã chọn trên Google Drive"** | "Chưa chọn tệp trên Drive" |
| 2 | **"Tệp trên máy"** | "Chưa chọn tệp trên máy" |

- Ô nhập: cao 36px, `padding:0 10px`, `border:1px solid var(--stroke2)`,
  **`border-bottom:2px solid var(--acc)`**, `border-radius:4px`, `background:var(--ctl)`,
  `font:400 14px …`, `spellCheck=false`.
- Nút **"Kiểm tra kết nối"** — cao 36px, `padding:0 14px`, `background:var(--ctl)`,
  `border:1px solid var(--stroke2)`, hover `background:var(--ctl-h)`, có biểu tượng mũi tròn 15px.
  Trong bản mẫu, bấm → `stale = false` (giống nút lấy dữ liệu).
- Hàng hai ô chọn (`gap:12px; margin-top:12px`), mỗi ô `flex:1`, cao 36px,
  `padding:0 30px 0 11px`, chevron xuống 13px đặt tuyệt đối `right:10px; top:12px`,
  `appearance:none`, `cursor:default`:
  - **"Bảng trong tệp"** — các lựa chọn lấy từ khuôn mẫu (ví dụ mẫu công đức:
    `CongDuc2026`, `CongDuc2025`, `DanhSachChung`, `Sheet1`).
  - **"Dòng tiêu đề"** — bốn lựa chọn cố định, nguyên văn:
    `Dòng 1` · `Dòng 2` · `Dòng 3` · `Không có dòng tiêu đề`. Mặc định `Dòng 1`.

#### c) Nhóm "Lấy dữ liệu mới"

Nhãn nhóm chữ hoa: **"Lấy dữ liệu mới"** — `margin-top:16px; font-size:12px; letter-spacing:.04em;
text-transform:uppercase; color:var(--txt3); font-weight:600; margin-bottom:9px`.

Ba thẻ (`padding:12px 14px; background:var(--layer2); border:1px solid var(--stroke);
border-radius:6px; gap:14px`):

| Tiêu đề (14px/600) | Giải thích (13px, `var(--txt3)`) | Phần bên phải |
|---|---|---|
| **Bấm nút để lấy dữ liệu mới** | "Luôn bật. Nút nằm ở thanh dưới của màn hình này và trên màn hình chính." | Nhãn nhỏ **"Luôn bật"** — `background:var(--chip-bg); border:1px solid var(--chip-bd); color:var(--chip-fg)`, không bấm được |
| **Tự kiểm tra định kỳ** | "Chỉ kiểm tra, không tự đổi giữa lúc đang đọc. Có dòng mới thì hiện nút “Cập nhật danh sách”." | Chữ **"5 phút một lần"** (khi bật) / **"Đang tắt"** (khi tắt) + công tắc 40×20. **Mặc định BẬT.** Cả thẻ bấm được (hover `background:var(--sub-h)`) |
| **Khi không lấy được** | "Dùng bản đã tải lần trước và báo rõ là dữ liệu ngày nào — không dừng buổi đọc." | Nhãn nhỏ **"Đã chọn"** — `background:var(--acc-soft); border:1px solid var(--acc); color:var(--acc)`, không bấm được |

---

### 7.4 `nav = 1` — KHỚP CỘT

#### a) Băng giải thích (bg `var(--acc-soft)`, `border-radius:6px`, `padding:11px 13px`,
`margin-bottom:14px`) — biểu tượng chữ "i" trong vòng tròn 16px `color:var(--acc)`

Nguyên văn (13.5px, `line-height:1.55`, `color:var(--txt)`):
> "Phần mềm đọc dòng tiêu đề và tự đoán cách dùng từng cột. Cột nào cũng chèn được vào mẫu câu, trừ cột đặt “Bỏ qua”. **Cách đọc** quyết định máy đọc ô đó thành gì — cùng một ô \`2.500.000\` có thể đọc thành “hai triệu năm trăm nghìn đồng” hoặc đọc từng chữ số."

(chữ "Cách đọc" là `<strong style="font-weight:600">`; `2.500.000` viết trong dấu backtick trong nguồn)

#### b) Bảng cột (`border:1px solid var(--stroke); border-radius:6px; overflow:hidden`)

Hàng tiêu đề: cao 34px, `background:var(--layer2)`, `border-bottom:1px solid var(--divider)`,
`font-size:12px; letter-spacing:.04em; text-transform:uppercase; color:var(--txt3); font-weight:600`.

| Cột bảng (nguyên văn) | Bề rộng |
|---|---|
| **Cột** | 38px, căn giữa |
| **Cột trong sheet** | `flex:1` |
| **Dùng làm** | 158px |
| **Cách đọc** | 168px |
| **Chèn được** | 104px, `padding-right:14px`, căn phải |

Mỗi hàng dữ liệu: `min-height:52px; border-bottom:1px solid var(--divider)`.
- **Cột**: chữ cột (A…F), `font-size:13px; color:var(--txt3); font-variant-numeric:tabular-nums`.
- **Cột trong sheet**: tên tiêu đề `font-size:14px; font-weight:600; color:var(--txt)`;
  dòng phụ `font-size:12.5px; color:var(--txt3)` — nguyên văn **"Ví dụ: {giá trị mẫu}"**,
  hoặc **"Ô trống"** nếu không có giá trị mẫu.
- **Dùng làm**: ô chọn cao 32px, `padding:0 26px 0 10px`, `border-radius:4px`,
  `background:var(--ctl)`, `font:400 13.5px …`, `appearance:none`, `cursor:default`,
  chevron 12px ở `right:8px; top:10px`; `title="Cột này dùng để làm gì"`.
- **Cách đọc**: ô chọn cùng kiểu, viền luôn `var(--stroke2)`; `title="Máy sẽ đọc ô này thành gì"`.
- **Chèn được**: chip biến — `font-size:12.5px; font-weight:600; padding:4px 8px; border-radius:4px;
  background:var(--chip-bg); border:1px solid var(--chip-bd); color:var(--chip-fg);
  font-family:Consolas,monospace`. Chỉ hiện khi cột có biến và **không trùng vai trò**.

**Bốn lựa chọn "Dùng làm" (nguyên văn, đúng thứ tự):**
`Dùng trong câu` · `Nhóm theo cột này` · `Lọc theo ngày` · `Bỏ qua`

**Tám lựa chọn "Cách đọc" (nguyên văn, đúng thứ tự):**
`Nguyên văn` · `Số tiền` · `Ngày tháng` · `Số thứ tự` · `Đọc từng chữ số` ·
`Tên riêng (đọc chậm)` · `Điểm, số thập phân` · `Viết tắt đọc đầy`

**Ba trạng thái hàng:**

| Trạng thái | Nền hàng | Ô "Dùng làm" | Ô "Cách đọc" | Chip biến |
|---|---|---|---|---|
| Bình thường | `var(--layer)` | viền `var(--stroke2)`, chữ `var(--txt)` | chữ `var(--txt)` | **có** |
| Đặt "Bỏ qua" | trong suốt | viền `var(--stroke2)`, chữ `var(--txt3)` | chữ `var(--txt3)` | **không** |
| Trùng vai trò độc quyền | `var(--warn-bg)` | viền **`var(--err)`**, chữ **`var(--err)`** | chữ `var(--txt)` | **không** |

**Cách sinh tên biến:** `'{' + slug(tênCột) + '}'`, với `slug` = chữ thường → bỏ dấu (NFD, xoá
`[\u0300-\u036f]`) → `đ`→`d` → xoá mọi ký tự không phải `a-z0-9`.
Ví dụ: `Tên` → `{ten}`, `Số tiền` → `{sotien}`, `Họ và tên` → `{hovaten}`,
`Số quyết định` → `{soquyetdinh}`, `Điểm trung bình` → `{diemtrungbinh}`, `Tổ dân phố` → `{todanpho}`.
Cột đặt "Bỏ qua" → tên biến rỗng.

#### c) Ghi chú cuối (`margin-top:12px; font-size:13px; color:var(--txt3); line-height:1.55`)

Nguyên văn:
> "Cột đặt “Bỏ qua” vẫn nằm trong sheet, chỉ là không đọc tới. Mỗi mẫu chỉ có một cột nhóm và một cột lọc ngày."

---

### 7.5 `nav = 2` — LỌC & NHÓM

#### a) Ba thẻ công tắc (gap 8px, mỗi thẻ `padding:12px 14px; background:var(--layer2);
border:1px solid var(--stroke); border-radius:6px`, hover `background:var(--sub-h)`)

| Tiêu đề (14px/600) | Giải thích (13px, `var(--txt3)`) | Chữ hiệu ứng bên phải (13px, `var(--txt3)`) | Mặc định |
|---|---|---|---|
| **Bỏ dòng thiếu dữ liệu** | "Dòng thiếu dữ liệu ở cột dùng trong câu sẽ không đọc." | **"4 dòng bị bỏ"** (cố định trong bản mẫu) | BẬT |
| **Gộp dòng trùng** | có cột "Số tiền": "Trùng nhau thì chỉ đọc lần đầu, số tiền được cộng gộp." — không có: "Trùng nhau thì chỉ đọc lần đầu." | **"2 dòng gộp lại"** (cố định) | BẬT |
| **Giữ đúng thứ tự trong sheet** | "Đọc từ trên xuống như trong bảng tính. Tắt thì sắp theo cột số giảm dần." | **"Theo bảng tính"** khi bật / **"Số lớn trước"** khi tắt | BẬT |

**Hàng con của "Gộp dòng trùng"** — chỉ hiện khi công tắc đó ĐANG BẬT. Nằm cùng thẻ
(`padding:0 14px 13px`), bấm vào hàng con **không** làm lật công tắc (`stopPropagation`):
- Chữ **"So trùng theo cột"** (13.5px, `var(--txt2)`).
- Ô chọn rộng **210px**, cao 32px, cùng kiểu ô chọn khác. Các lựa chọn là **chữ cột** (A, B, …),
  chỉ gồm cột **không** đặt "Bỏ qua". Mặc định = cột đầu tiên không "Bỏ qua".
- Ghi chú (13px, `var(--txt3)`): **"Hai dòng có cùng {tên cột viết chữ thường} được coi là một."**
  (ví dụ: "Hai dòng có cùng tên được coi là một."). Nếu không xác định được cột →
  **"Chọn cột để so trùng."**

#### b) Nhóm "Khoảng ngày"

Nhãn nhóm chữ hoa: **"Khoảng ngày"**.
Thẻ (`padding:14px; background:var(--layer2); border:1px solid var(--stroke); border-radius:6px`,
`display:flex; align-items:flex-end; gap:10px`):
- **"Từ ngày"** — `<input type="date">`, ô rộng 170px, cao 34px, `padding:0 9px`,
  `border:1px solid var(--stroke2)`, `border-radius:4px`, `background:var(--ctl)`,
  `font-variant-numeric:tabular-nums`. Mặc định `2026-07-01`.
- **"Đến ngày"** — cùng kiểu, rộng 170px. Mặc định `2026-08-15`.
- Ghi chú `flex:1`, 13px, `var(--txt3)`, `padding-bottom:8px`:
  - có cột lọc ngày → **"Lấy theo cột {tên cột}. Bỏ trống hai ô này thì đọc toàn bộ danh sách."**
    (ví dụ: "Lấy theo cột Ngày. Bỏ trống hai ô này thì đọc toàn bộ danh sách.")
  - không có → **"Chưa có cột nào đặt “Lọc theo ngày”, nên bộ lọc này chưa có tác dụng."**

#### c) Nhóm "Nhóm theo cột"

Nhãn nhóm chữ hoa: **"Nhóm theo cột"**.
Một thẻ công tắc:
- Tiêu đề: **"Đọc tên nhóm trước mỗi nhóm"**
- Giải thích:
  - có cột nhóm → **"Nhóm theo cột {tên cột}. Trước mỗi nhóm sẽ đọc: “{câu đọc tên nhóm}”"**
    (ví dụ: "Nhóm theo cột Đợt. Trước mỗi nhóm sẽ đọc: “Đợt cúng dường Rằm tháng Bảy.”")
  - không có → **"Chọn một cột đặt “Nhóm theo cột này” ở mục Khớp cột trước đã."**
- Chữ hiệu ứng bên phải: **"{số nhóm} nhóm"** (ví dụ "3 nhóm") hoặc **"chưa có cột nhóm"**
- Mặc định BẬT.

---

### 7.6 `nav = 3, 5, 6` — BA KHỐI VĂN BẢN TĨNH; `nav = 4` — KHỐI MẪU CÂU

#### a) Thẻ "Đọc câu này sau mỗi …" — **CHỈ hiện khi `nav === 5`** (Câu xen giữa)

`padding:12px 14px; background:var(--layer2); border:1px solid var(--stroke); border-radius:6px;
margin-bottom:14px; gap:10px`:
- Chữ **"Đọc câu này sau mỗi"** (14px, `var(--txt)`)
- Ô chọn rộng **96px**, cao 34px, `padding:0 28px 0 11px`, chevron ở `right:9px; top:11px`,
  `font-variant-numeric:tabular-nums`.
  Lựa chọn nguyên văn: `10` · `20` · `30` · `40` · `50` · `100`. **Mặc định `30`.**
- Chữ **"dòng"** (14px)
- Bên phải (`margin-left:auto`, 13px, `var(--txt3)`, tabular-nums): **"Sẽ đọc {N} lần trong {M} dòng"**
  - `N = floor(số dòng / bước)` **chỉ khi công tắc "Câu xen giữa" đang BẬT**; khi TẮT thì `N = 0`.
  - Ví dụ mẫu công đức, bước 30, 248 dòng, đang bật → "Sẽ đọc 8 lần trong 248 dòng".

#### b) Hàng nhãn ô soạn (`display:flex; align-items:baseline; gap:10px; margin-bottom:7px`)

| `nav` | Nhãn trái (13px, `var(--txt2)`) | Đếm bên phải (12.5px, `var(--txt3)`, tabular-nums) |
|---|---|---|
| 4 | **"Mỗi dòng trong bảng tính sẽ được đọc theo mẫu này"** | **"{n} ký tự"** |
| 3, 5, 6 | **"Nội dung đọc — cách dòng để ngắt đoạn"** | **"{n} đoạn · {m} ký tự"** |

#### c) Ô soạn (textarea)

`width:100%; border:1px solid var(--stroke2);` **`border-bottom:2px solid var(--acc);`**
`border-radius:4px; background:var(--ctl); padding:13px 14px; resize:vertical;
font:400 15px/1.65 'Segoe UI Variable Text','Segoe UI',Inter,sans-serif; color:var(--txt);
spellCheck=false; outline:none`.

| `nav` | `min-height` | Placeholder nguyên văn |
|---|---|---|
| 4 | **120px** | "Ví dụ: {ten}, phát tâm công đức số tiền {sotien}." |
| 3, 5, 6 | **260px** | "Gõ nội dung sẽ được đọc. Cách dòng một lần để ngắt đoạn." |

#### d) `nav === 4` — nhóm "Chèn dữ liệu từ sheet" (chỉ ở mục Mẫu câu)

Nhãn nhóm chữ hoa: **"Chèn dữ liệu từ sheet"** (`margin-top:14px`).
Dãy chip xếp cuộn dòng (`flex-wrap:wrap; gap:7px`), mỗi chip cao 30px, `padding:0 11px`,
`border-radius:15px`, `font-size:13px`, hover `border-color:var(--acc); color:var(--acc)`:
- Tên biến: `font-family:Consolas,monospace; font-weight:600`
- Tên cột đi kèm: `color:var(--txt3)`
- `title` nguyên văn (ghép động):
  **"Bấm để chèn {biến} vào mẫu câu — lấy từ cột {chữ cột} ({tên cột}), đọc theo kiểu {cách đọc viết chữ thường}"**
  (ví dụ: "Bấm để chèn {sotien} vào mẫu câu — lấy từ cột B (Số tiền), đọc theo kiểu số tiền")

| Trạng thái chip | Nền | Viền | Chữ |
|---|---|---|---|
| Biến **đã có mặt** trong mẫu câu | `var(--acc-soft)` | `var(--acc)` | `var(--acc)` |
| Biến **chưa dùng** | `var(--layer2)` | `var(--stroke2)` | `var(--txt2)` |

**Hành vi chèn:** chèn vào **đúng vị trí con trỏ** trong ô soạn (thay đoạn đang chọn nếu có). Nếu chưa
có tiêu điểm/con trỏ → nối vào cuối, có thêm một dấu cách trước. Sau khi chèn, con trỏ được đặt lại
ngay sau biến vừa chèn (`_caret = a + độ dài biến`), ô soạn tự lấy lại tiêu điểm.

Thẻ ghi chú dưới cùng (`margin-top:12px; padding:12px 13px; background:var(--layer2);
border:1px solid var(--stroke); border-radius:6px; font-size:13.5px; line-height:1.55;
color:var(--txt2)`):
- Nửa đầu đổi theo dữ liệu:
  - **có** cột đặt cách đọc "Số tiền" và không "Bỏ qua":
    "Ô số tiền 2.500.000 sẽ được đọc thành “hai triệu năm trăm nghìn đồng”, ô điện thoại đọc từng chữ số."
  - **không có**:
    "Mỗi cột được đọc theo Cách đọc đã đặt: ngày tháng đọc thành lời, số điện thoại đọc từng chữ số, tên riêng đọc chậm và rõ dấu."
- Nửa sau cố định: " Muốn đọc khác, đổi **Cách đọc** của cột đó ở mục Khớp cột, hoặc thêm dòng vào
  [Từ điển phát âm](GiongDoc - Từ điển phát âm.dc.html)."
  (chữ "Cách đọc" in đậm `color:var(--txt)`; "Từ điển phát âm" là liên kết sang tệp thiết kế Từ điển phát âm)

#### e) `nav === 3, 5, 6` — thẻ ghi chú tĩnh (thay cho phần chip)

`margin-top:14px; padding:12px 13px; background:var(--layer2); border:1px solid var(--stroke);
border-radius:6px; font-size:13.5px; line-height:1.55; color:var(--txt2)`. Nguyên văn:
> "Cách dòng một lần là ngắt đoạn — phần mềm sẽ nghỉ một nhịp ở đó. Muốn nghỉ lâu hơn, chèn thẻ khoảng lặng ở màn hình chính."

#### f) Ghi ngược vào trạng thái

Sửa ô soạn ghi vào khoá theo `nav`: `3 → dau`, `4 → mau`, `5 → giua`, `6 → cuoi`.
Mục `nav` 0, 1, 2 không có ô soạn nên không ghi gì.

---

## 8. (3c) KHUNG XEM TRƯỚC PHẢI — "Bản ghép hoàn chỉnh", rộng 392px

### 8.1 Đầu khung (44px)

- Tiêu đề **"Bản ghép hoàn chỉnh"** (14px/600, `var(--txt)`)
- Dòng phụ (12.5px, `var(--txt3)`, tabular-nums): **"{số khối} khối · {số đoạn} đoạn"**

### 8.2 Các khối xem trước

Mỗi khối: `border:1px solid {màu viền}; border-left:3px solid {màu vạch}; border-radius:5px;
background:{màu nền}; overflow:hidden`.
- Hàng nhãn (`padding:7px 10px; gap:8px`): nhãn `font-size:11.5px; letter-spacing:.03em;
  text-transform:uppercase; font-weight:600` + số liệu bên phải `font-size:12px; color:var(--txt3)`.
- Nội dung: `padding:9px 11px 11px; font-size:13.5px; line-height:1.6; color:var(--txt);
  white-space:pre-wrap`.
- Dòng "còn nữa" (nếu có): `padding:0 11px 11px; font-size:12.5px; color:var(--txt3)`.

**Hai bộ màu khối:**

| Loại | Viền | Vạch trái | Nền | Màu chữ nhãn |
|---|---|---|---|---|
| **Phần động** (lấy từ bảng tính) | `var(--acc)` | `var(--acc)` | `var(--acc-soft)` | `var(--acc)` |
| **Phần tĩnh** (bạn viết) | `var(--stroke)` | `var(--stroke2)` | `var(--layer2)` | `var(--txt3)` |

**Thứ tự và điều kiện xuất hiện các khối:**

| # | Nhãn nguyên văn | Điều kiện | Số liệu bên phải | Nội dung |
|---|---|---|---|---|
| 1 | **"Đầu danh sách · tĩnh"** | công tắc `dau` BẬT | "{n} đoạn" | văn bản khối Đầu danh sách |
| 2 | **"Tên nhóm · {từ Google Sheet \| từ tệp trên máy}"** | bật nhóm **và** có cột nhóm | "nhóm 1/{số nhóm}" | câu đọc tên nhóm của khuôn mẫu |
| 3 | **"Danh sách · {từ Google Sheet \| từ tệp trên máy}"** | **luôn có** | "{số dòng} dòng" | 4 dòng mẫu đã dựng thật, mỗi dòng đánh số "1. ", "2. "… |
| 4 | **"Câu xen giữa · tĩnh"** | công tắc `giua` BẬT | "lặp {N} lần" | văn bản khối Câu xen giữa |
| 5 | **"Cuối danh sách · tĩnh"** | công tắc `cuoi` BẬT | "{n} đoạn" | văn bản khối Cuối danh sách |

- Đuôi nhãn nguồn: **"từ tệp trên máy"** khi nguồn = File trên máy (chỉ số 2); ngược lại
  **"từ Google Sheet"**.
- Khối 3 có thêm dòng: **"… còn {số dòng − 4} dòng nữa, đọc theo đúng mẫu câu ở trên."**
  (ví dụ: "… còn 244 dòng nữa, đọc theo đúng mẫu câu ở trên.")

### 8.3 Chân khung xem trước

`padding:11px 13px; border-top:1px solid var(--divider); background:var(--layer2);
font-size:12.5px; line-height:1.55; color:var(--txt2)`. Nguyên văn:
> "Khối viền xanh là phần lấy từ bảng tính, sẽ tự đổi theo dữ liệu. Khối viền xám là phần bạn viết, không đổi."

### 8.4 Cách dựng 4 dòng mẫu (phải làm đúng — đây là chỗ chứng minh cấu hình có tác dụng)

Với mỗi dòng mẫu: lấy văn bản mẫu câu, thay từng `{biến}` bằng kết quả hàm `say(giá trị, cách đọc,
từ điển đọc)`. Sau đó:
- Biến còn sót (không cột nào cấp) → thay bằng **"(chưa có cột {tên biến})"**
- Xoá khoảng trắng trước dấu `.` và `,` (`/\s+([.,])/g → '$1'`)
- Nén nhiều khoảng trắng thành một (`/\s{2,}/g → ' '`)
- Thêm tiền tố **"{i}. "** (i đếm từ 1)
- Bốn dòng nối bằng ký tự xuống dòng.

**Hàm `say(v, read, says)` — thứ tự ưu tiên:**
1. Giá trị rỗng (sau `trim`) → chuỗi rỗng.
2. `read === 'Đọc từng chữ số'` → đọc từng chữ số (bảng `0..9` → `không một hai ba bốn năm sáu bảy tám chín`),
   nối bằng khoảng trắng, bỏ mọi ký tự không phải chữ số.
3. Có trong **từ điển đọc** (`says`) → dùng nguyên câu trong từ điển. (Đây là đường ưu tiên chính
   cho tiền, ngày và viết tắt — xem mục 11.)
4. `read === 'Số thứ tự'` → đọc số thành chữ (`numWords`), thất bại thì để nguyên.
5. `read === 'Điểm, số thập phân'` → tách theo dấu phẩy, đọc `"{phần nguyên} phẩy {từng chữ số phần thập phân}"`.
   Ví dụ `9,8` → "chín phẩy tám".
6. `read === 'Số tiền'` → nối thêm **" đồng"** vào nguyên văn ô.
7. Còn lại → nguyên văn (áp dụng cho `Nguyên văn`, `Ngày tháng`, `Tên riêng (đọc chậm)`,
   `Viết tắt đọc đầy` khi không có trong từ điển).

**Hàm `numWords`** đọc số nguyên tiếng Việt tới hàng nghìn: dùng `mười`, `mươi`, `mốt` (đơn vị 1 sau
`mươi`), `lăm` (đơn vị 5 sau `mươi`), `lẻ` (khi hàng đơn vị < 10 sau hàng trăm/nghìn), `trăm`, `nghìn`.

---

## 9. (4) THANH DƯỚI — cao 46px

`padding:0 12px; border-top:1px solid var(--divider); background:var(--bg); gap:12px`.

Từ trái sang phải:
1. **Đèn tròn** 7×7 `border-radius:4px` — `var(--warn)` khi `stale`, `var(--ok)` khi đã cập nhật.
2. **Câu trạng thái** (13px, `var(--txt2)`), hai biến thể nguyên văn:
   - `stale === true`: **"Dữ liệu cũ — lấy lúc 14:03 hôm nay · {số dòng} dòng"**
     (ví dụ: "Dữ liệu cũ — lấy lúc 14:03 hôm nay · 248 dòng")
   - `stale === false`: **"Đã cập nhật 14:58 hôm nay · {số dòng} dòng · tự kiểm tra 5 phút một lần"**
3. **Nút "Lấy dữ liệu mới"** — cao 32px, `padding:0 13px`, `background:var(--ctl)`,
   `border:1px solid var(--stroke2)`, `border-radius:4px`, `font-size:14px`, `color:var(--txt)`,
   hover `background:var(--ctl-h)`; có biểu tượng mũi tròn 15px. Bấm → `stale = false`.
4. **Tổng kết** (`margin-left:auto`, 13px, `var(--txt3)`, tabular-nums):
   **"{số đoạn} đoạn · khoảng {số phút} phút"**
5. **Nút chính "Mở bản ghép để nghe"** — liên kết `<a>` sang
   `GiongDoc - Màn hình chính v2 (nghe theo dòng).dc.html#banghep`; cao 34px, `padding:0 16px`,
   `border-radius:4px`, `background:var(--acc)`, `color:var(--acc-txt)`, `font-size:14px;
   font-weight:600`, hover `background:var(--acc-h)`;
   `title="Mở bản ghép thành một tab tệp ở màn hình chính"`.

**Công thức số đoạn và thời lượng:**

```
số đoạn = (dau bật ? số đoạn của Đầu danh sách : 0)
        + (bật nhóm và có cột nhóm ? số nhóm : 0)
        + số dòng
        + số lần đọc câu xen giữa
        + (cuoi bật ? số đoạn của Cuối danh sách : 0)

số phút = round(số đoạn * 9 / 60)      // ước 9 giây một đoạn
```

Ví dụ mặc định (Danh sách công đức, `dau` bật 4 đoạn, nhóm bật 3 nhóm, 248 dòng, `giua` tắt → 0,
`cuoi` bật 4 đoạn): số đoạn = 4 + 3 + 248 + 0 + 4 = **259**; số phút = round(259×9/60) = **39**.
Nhãn: "259 đoạn · khoảng 39 phút"; dòng phụ khung xem trước: "3 khối · 259 đoạn".

---

## 10. (6) HỘP THOẠI "TẠO MẪU GHÉP MỚI" — hiện khi `newOpen === true`

Màn che: `position:absolute; inset:0; z-index:60; background:rgba(0,0,0,.34)`, nội dung căn giữa.
Thẻ: **rộng 660px**, `background:var(--layer)`, `border:1px solid var(--stroke2)`,
`border-radius:8px`, `box-shadow:0 32px 64px rgba(0,0,0,.32)`, `overflow:hidden`.

**Đầu** (`padding:18px 20px 14px; border-bottom:1px solid var(--divider)`):
- Tiêu đề **"Tạo mẫu ghép mới"** — `font-size:20px; font-weight:600; color:var(--txt)`
- Phụ đề (13px, `var(--txt3)`): **"Chọn loại danh sách gần giống của bạn. Tên cột, mẫu câu và câu chữ đều sửa lại được sau."**
- Nút X 28×28, `border-radius:4px`, `color:var(--txt2)`, hover `background:var(--sub-h)`,
  `title="Đóng"`. Bấm → đóng hộp thoại.

**Thân** (`padding:16px 20px; display:grid; grid-template-columns:1fr 1fr; gap:10px;
max-height:430px; overflow-y:auto`): **6 thẻ khuôn mẫu**, mỗi thẻ `padding:13px 14px;
background:var(--layer2); border:1px solid var(--stroke); border-radius:6px`,
hover `border-color:var(--acc); background:var(--acc-soft)`,
`title="Tạo mẫu ghép theo {tên khuôn mẫu}"`. Mỗi thẻ có 3 dòng:
tên (14.5px/600, `var(--txt)`) · mô tả (13px, `var(--txt2)`) · gợi ý cột (12.5px, `var(--txt3)`).

**Chân** (`padding:14px 20px; background:var(--layer2); border-top:1px solid var(--divider)`):
- Ghi chú (12.5px, `var(--txt3)`): **"Mẫu mới được thêm vào hồ sơ Danh sách, biểu mẫu — các mẫu đang có không đổi."**
- Nút **"Huỷ"** — cao 34px, `padding:0 16px`, `background:var(--layer)`,
  `border:1px solid var(--stroke2)`, hover `background:var(--sub-h)`. Bấm → đóng hộp thoại.

**Hộp thoại này chỉ có MỘT bước** — không có nhiều bước, không có điều kiện chặn.
Bấm một thẻ khuôn mẫu là tạo mẫu ngay và đóng hộp thoại.

**Quy tắc đặt tên khi tạo:** lấy tên khuôn mẫu; nếu đã có mẫu cùng tên thì thêm hậu tố
`" (2)"`, `" (3)"`… cho tới khi không trùng. Mẫu mới được đưa vào cuối danh sách, tự chuyển sang mẫu
đó, đặt `nav = 0`, đóng cả hộp thoại và dropdown.

---

## 11. SÁU KHUÔN MẪU CÓ SẴN (dữ liệu mẫu — bản lập trình cần đúng bộ này)

Hai mẫu ghép mặc định trong hồ sơ: `m1` = **"Danh sách công đức"** (khuôn `congduc`),
`m2` = **"Quỹ khuyến học tháng 8"** (khuôn `quyengop`).

### 11.1 `congduc` — "Danh sách công đức"
- Mô tả: "Sổ công đức của chùa, đền, nhà thờ — đọc tên người phát tâm và số tiền."
- Gợi ý: "Cột gợi ý: Tên · Số tiền · Ngày · Đợt · Pháp danh"
- Bảng mặc định `CongDuc2026`; các bảng: `CongDuc2026`, `CongDuc2025`, `DanhSachChung`, `Sheet1`
- 248 dòng · 3 nhóm · nguồn mặc định = 0 (dán link)
- Giá trị ô nguồn mẫu: `https://docs.google.com/spreadsheets/d/1aB…/edit?usp=sharing` /
  `Sổ công đức 2026 — Drive của chùa` / `D:\ChuaAnLac\so-cong-duc-2026.xlsx`
- Cột: A `Tên` (Dùng trong câu · Tên riêng (đọc chậm)) · B `Số tiền` (Dùng trong câu · Số tiền) ·
  C `Ngày` (Lọc theo ngày · Ngày tháng) · D `Đợt` (Nhóm theo cột này · Nguyên văn) ·
  E `Pháp danh` (Dùng trong câu · Tên riêng (đọc chậm)) · F `Ghi chú` (Bỏ qua · Nguyên văn)
- Mẫu câu: `{ten}, phát tâm công đức số tiền {sotien}.`
- Câu đọc tên nhóm: "Đợt cúng dường Rằm tháng Bảy."
- 4 dòng mẫu: Gia đình Phật tử Nguyễn Văn Tuyến / 5.000.000 · Bà Trần Thị Kim Loan / 2.500.000 ·
  Công ty TNHH Bảo Sơn / 20.000.000 · Phật tử Lê Minh Hoà / 500.000 (đều ngày 12/07/2026,
  đợt "Rằm tháng Bảy")
- Đầu danh sách (4 đoạn):
  > Nam mô A Di Đà Phật.
  >
  > Nhà chùa xin thành kính thông báo và ghi nhận danh sách quý Phật tử, quý gia đình, quý cơ quan, đơn vị và quý mạnh thường quân đã phát tâm công đức xây dựng, tu bổ và hộ trì Tam Bảo.
  >
  > Nhà chùa xin thành kính tri ân công đức của quý vị.
  >
  > Sau đây là danh sách công đức.
- Câu xen giữa: "Nhà chùa xin thành kính tri ân công đức và tấm lòng phát tâm của quý Phật tử."
- Cuối danh sách (4 đoạn):
  > Danh sách công đức đến đây xin được khép lại.
  >
  > Nhà chùa xin thành kính tri ân công đức, tấm lòng hoan hỷ và sự phát tâm hộ trì Tam Bảo của quý Phật tử, quý gia đình, quý cơ quan, đơn vị và quý mạnh thường quân.
  >
  > Nguyện đem công đức này hồi hướng cho quốc thái dân an, chúng sinh an lạc, gia đình bình an, mọi người mọi nhà được mạnh khỏe, hạnh phúc và sở cầu như nguyện.
  >
  > Nam mô Công Đức Lâm Bồ Tát Ma Ha Tát.

### 11.2 `quyengop` — "Quyên góp, ủng hộ"
- Mô tả: "Quỹ khuyến học, ủng hộ bão lụt, quỹ lớp — đọc tên và mức ủng hộ."
- Gợi ý: "Cột gợi ý: Người ủng hộ · Số tiền · Ngày · Tổ dân phố · Hiện vật"
- Bảng `UngHo_T8`; các bảng: `UngHo_T8`, `UngHo_T7`, `TongHop2026`, `Sheet1`; 96 dòng · 6 nhóm · nguồn 0
- Cột: A `Người ủng hộ` (Dùng trong câu · Tên riêng) · B `Số tiền` (Dùng trong câu · Số tiền) ·
  C `Ngày` (Lọc theo ngày · Ngày tháng) · D `Tổ dân phố` (Nhóm theo cột này · Nguyên văn) ·
  E `Hiện vật` (Dùng trong câu · Nguyên văn) · F `Điện thoại` (Bỏ qua · Đọc từng chữ số)
- Mẫu câu: `{nguoiungho}, tổ {todanpho}, ủng hộ {sotien}.`
- Câu đọc tên nhóm: "Tổ dân phố Tổ 4."
- Đầu: "Ban vận động Quỹ khuyến học phường xin thông báo danh sách các cá nhân, gia đình và đơn vị đã ủng hộ trong tháng 8 năm 2026." + "Ban vận động xin trân trọng cảm ơn tấm lòng của quý vị."
- Xen giữa: "Ban vận động xin trân trọng cảm ơn sự đóng góp của quý vị."
- Cuối: "Danh sách ủng hộ đến đây xin được khép lại." + "Toàn bộ số tiền và hiện vật sẽ được chuyển tới các em học sinh có hoàn cảnh khó khăn trong phường trước ngày khai giảng." + "Ban vận động xin trân trọng cảm ơn."

### 11.3 `bangluong` — "Chi trả, bảng lương"
- Mô tả: "Chi trả lương, trợ cấp, tiền hỗ trợ — đọc tên và số tiền được nhận."
- Gợi ý: "Cột gợi ý: Họ và tên · Số tiền nhận · Ngày chi trả · Bộ phận · Số quyết định"
- Bảng `ChiTra_T7`; các bảng: `ChiTra_T7`, `ChiTra_T6`, `DanhSachNhanSu`, `Sheet1`;
  64 dòng · 5 nhóm · **nguồn mặc định = 2 (File trên máy)**
- Cột: A `Họ và tên` · B `Số tiền nhận` (Số tiền) · C `Ngày chi trả` (Lọc theo ngày) ·
  D `Bộ phận` (Nhóm theo cột này) · E `Số quyết định` (Dùng trong câu · **Viết tắt đọc đầy**) ·
  F `Ghi chú` (Bỏ qua)
- Mẫu câu: `{hovaten}, nhận {sotiennhan}, theo {soquyetdinh}.`
- Câu đọc tên nhóm: "Bộ phận Phòng Kỹ thuật."
- Đầu: "Phòng Hành chính thông báo danh sách chi trả tiền lương và các khoản phụ cấp kỳ tháng 7 năm 2026." + "Đề nghị các anh chị nghe đúng tên mình và ký nhận tại phòng Hành chính."
- Xen giữa: "Đề nghị các anh chị nghe đúng tên mình và ký nhận tại phòng Hành chính."
- Cuối: "Danh sách chi trả đến đây là hết." + "Mọi thắc mắc về số tiền xin liên hệ phòng Hành chính trong giờ làm việc, trước ngày 20 tháng 8."

### 11.4 `khenthuong` — "Khen thưởng, kết quả"
- Mô tả: "Học sinh đạt danh hiệu, kết quả thi, danh sách trúng tuyển — đọc tên, lớp và điểm."
- Gợi ý: "Cột gợi ý: Họ và tên · Lớp · Điểm trung bình · Danh hiệu · Ngày xét"
- Bảng `KhenThuong_HK2`; các bảng: `KhenThuong_HK2`, `KhenThuong_HK1`, `DiemTongKet`, `Sheet1`;
  132 dòng · 9 nhóm · nguồn 0
- Cột: A `Họ và tên` · B `Lớp` (Nhóm theo cột này) · C `Điểm trung bình` (**Điểm, số thập phân**) ·
  D `Danh hiệu` (Nguyên văn) · E `Ngày xét` (Lọc theo ngày) · F `Số báo danh` (Bỏ qua · Đọc từng chữ số)
- Mẫu câu: `Em {hovaten}, lớp {lop}, điểm trung bình {diemtrungbinh}, đạt {danhhieu}.`
- Câu đọc tên nhóm: "Lớp 5A1."
- Đầu: "Nhà trường xin thông báo danh sách học sinh đạt danh hiệu học kỳ hai năm học 2025 – 2026." + "Nhà trường chúc mừng các em và gia đình."
- Xen giữa: "Nhà trường chúc mừng các em và gia đình."
- Cuối: "Danh sách khen thưởng đến đây là hết." + "Lễ trao thưởng được tổ chức vào sáng thứ Bảy ngày 30 tháng 5, tại sân trường. Đề nghị các em có tên đến trước 7 giờ 15."

### 11.5 `lichtruc` — "Lịch trực, phân công"
- Mô tả: "Lịch trực cơ quan, phân công nhiệm vụ theo ngày — đọc ngày, người và việc."
- Gợi ý: "Cột gợi ý: Ngày trực · Người trực · Bộ phận · Ca · Điện thoại"
- Bảng `LichTruc_T9`; các bảng: `LichTruc_T9`, `LichTruc_T8`, `PhanCong`, `Sheet1`;
  42 dòng · 4 nhóm · nguồn 0
- Cột: A `Ngày trực` (Lọc theo ngày · Ngày tháng) · B `Người trực` · C `Bộ phận` (Nhóm theo cột này) ·
  D `Ca` (Nguyên văn) · E `Điện thoại` (Dùng trong câu · Đọc từng chữ số) · F `Ghi chú` (Bỏ qua)
- Mẫu câu: `{ngaytruc}, {nguoitruc} trực {ca}, số điện thoại {dienthoai}.`
- Câu đọc tên nhóm: "Bộ phận Phòng Kỹ thuật."
- Đầu: "Văn phòng thông báo lịch trực tháng 9 năm 2026." + "Đề nghị các anh chị nghe đúng ngày trực của mình."
- Xen giữa: "Đề nghị các anh chị nghe đúng ngày trực của mình."
- Cuối: "Lịch trực đến đây là hết." + "Anh chị nào cần đổi ca xin báo văn phòng trước một ngày để cập nhật lại lịch."

### 11.6 `thongbao` — "Thông báo tìm người, tạm trú"
- Mô tả: "Loa phát thanh phường: tìm người, nhắn tin, danh sách tạm trú — đọc tên, năm sinh, đặc điểm."
- Gợi ý: "Cột gợi ý: Họ và tên · Năm sinh · Địa chỉ · Loại thông báo · Số liên hệ"
- Bảng `ThongBao_T8`; các bảng: `ThongBao_T8`, `TamTru_2026`, `TimNguoi`, `Sheet1`;
  18 dòng · 3 nhóm · nguồn 0
- Cột: A `Họ và tên` · B `Năm sinh` (**Số thứ tự**) · C `Địa chỉ` (Nguyên văn) ·
  D `Loại thông báo` (Nhóm theo cột này) · E `Ngày báo` (Lọc theo ngày) ·
  F `Số liên hệ` (Dùng trong câu · Đọc từng chữ số)
- Mẫu câu: `{hovaten}, sinh năm {namsinh}, địa chỉ {diachi}. Ai biết tin xin liên hệ số {solienhe}.`
- Câu đọc tên nhóm: "Loại thông báo Tìm người."
- Đầu: "Uỷ ban nhân dân phường thông báo tới toàn thể nhân dân một số nội dung sau đây." + "Đề nghị bà con chú ý lắng nghe."
- Xen giữa: "Đề nghị bà con chú ý lắng nghe và thông tin lại cho Uỷ ban nhân dân phường."
- Cuối: "Thông báo đến đây là hết." + "Uỷ ban nhân dân phường xin trân trọng cảm ơn bà con đã chú ý lắng nghe."

### 11.7 Từ điển đọc dùng chung cho cả 6 khuôn mẫu (`says`)

**Tiền:** `5.000.000`→"năm triệu đồng" · `2.500.000`→"hai triệu năm trăm nghìn đồng" ·
`20.000.000`→"hai mươi triệu đồng" · `500.000`→"năm trăm nghìn đồng" ·
`1.200.000`→"một triệu hai trăm nghìn đồng" · `300.000`→"ba trăm nghìn đồng" ·
`7.850.000`→"bảy triệu tám trăm năm mươi nghìn đồng" · `9.200.000`→"chín triệu hai trăm nghìn đồng" ·
`6.400.000`→"sáu triệu bốn trăm nghìn đồng" · `12.100.000`→"mười hai triệu một trăm nghìn đồng"

**Ngày:** `12/07/2026`, `03/08/2026`, `05/08/2026`, `01/09/2026`, `02/09/2026`, `03/09/2026`,
`04/09/2026`, `28/05/2026`, `10/08/2026` → dạng "ngày {số} tháng {số} năm hai nghìn không trăm hai mươi sáu"

**Viết tắt:** `QĐ 142/2026`→"quyết định một trăm bốn mươi hai năm hai nghìn không trăm hai mươi sáu" ·
`QĐ 143/2026`→"quyết định một trăm bốn mươi ba năm hai nghìn không trăm hai mươi sáu" ·
`TNHH`→"trách nhiệm hữu hạn" · `UBND`→"Uỷ ban nhân dân"

---

## 12. BIẾN CSS — GIÁ TRỊ HAI BỘ MÀU

| Biến | Bộ SÁNG (`:root`) | Bộ TỐI (`:root[data-theme='dark']`) | Dùng ở đâu |
|---|---|---|---|
| `--bg` | `#f3f3f3` | `#202020` | nền khung cửa sổ, thanh tiêu đề, thanh dưới |
| `--layer` | `#ffffff` | `#2b2b2b` | khung giữa, khung xem trước, dropdown, hộp thoại, hàng cột bình thường |
| `--layer2` | `#fafafa` | `#272727` | thẻ phụ, đầu bảng, thẻ chưa chọn, chân khung xem trước |
| `--stroke` | `rgba(0,0,0,.0578)` | `rgba(255,255,255,.07)` | viền nhẹ khung/thẻ |
| `--stroke2` | `rgba(0,0,0,.16)` | `rgba(255,255,255,.10)` | viền ô nhập, ô chọn, nút phụ |
| `--divider` | `#e5e5e5` | `#303030` | đường kẻ ngang |
| `--txt` | `#1a1a1a` | `#ffffff` | chữ chính |
| `--txt2` | `#5d5d5d` | `rgba(255,255,255,.73)` | chữ phụ cấp 1 |
| `--txt3` | `#767676` | `rgba(255,255,255,.60)` | chữ phụ cấp 2, ghi chú, số liệu |
| `--dis` | `#a3a3a3` | `rgba(255,255,255,.38)` | **khai báo nhưng không dùng trong tệp này** |
| `--ctl` | `#fdfdfd` | `rgba(255,255,255,.06)` | nền ô nhập, ô chọn, nút phụ |
| `--ctl-h` | `#f6f6f6` | `rgba(255,255,255,.084)` | hover của nút phụ / ô nhập |
| `--sub-h` | `rgba(0,0,0,.037)` | `rgba(255,255,255,.06)` | hover mục danh sách, chip quay lại |
| `--acc` | `#0067c0` | `#4cc2ff` | nhấn: nút chính, công tắc bật, viền khối động, gạch dưới ô nhập |
| `--acc-h` | `#1a75c6` | `#47b1e8` | hover nút chính, hover liên kết |
| `--acc-txt` | `#ffffff` | `#000000` | chữ trên nền nhấn, núm công tắc khi bật |
| `--acc-soft` | `rgba(0,103,192,.09)` | `rgba(76,194,255,.12)` | nền thẻ đang chọn, nền khối động, nền băng giải thích |
| `--chip-bg` | `rgba(0,0,0,.055)` | `rgba(255,255,255,.09)` | nền chip biến, nhãn "Có sẵn", "Luôn bật" |
| `--chip-bd` | `rgba(0,0,0,.09)` | `rgba(255,255,255,.14)` | viền chip |
| `--chip-fg` | `#4a4a4a` | `rgba(255,255,255,.82)` | chữ chip |
| `--ok` | `#0f7b0f` | `#6ccb5f` | đèn xanh (mục bình thường, đã cập nhật) |
| `--err` | `#c42b1c` | `#ff99a4` | chữ/viền lỗi (cột trùng vai trò), hover "Xoá mẫu này" |
| `--warn` | `#9d5d00` | `#fce100` | biểu tượng cảnh báo, đèn vàng |
| `--warn-bg` | `#fff9ec` | `#3a3320` | nền băng cảnh báo, nền hàng cột trùng |
| `--warn-bd` | `#f0e2c2` | `#5c4f2a` | viền băng cảnh báo |
| `--rail` | `#868686` | `#9a9a9a` | **khai báo nhưng không dùng trong tệp này** |
| `--close` | `#c42b1c` | `#c42b1c` | nền nút Đóng khi hover (giống nhau hai bộ) |
| `--shadow` | `0 8px 16px rgba(0,0,0,.14)` | `0 8px 16px rgba(0,0,0,.36)` | bóng dropdown chọn mẫu |

Bóng của khung cửa sổ và hộp thoại không dùng biến: `0 16px 32px rgba(0,0,0,.22)` và
`0 32px 64px rgba(0,0,0,.32)`.

---

## 13. PHÍM TẮT ĐƯỢC NÊU TRONG THIẾT KẾ

Chỉ có hai phím, và **chỉ trong ô nhập đổi tên mẫu**:

| Phím | Hành vi |
|---|---|
| **Enter** | Lưu tên mới (bỏ khoảng trắng hai đầu; rỗng thì giữ tên cũ), thoát chế độ đổi tên |
| **Escape** | Thoát chế độ đổi tên, **không lưu** |

Ngoài ra: mất tiêu điểm (blur) ô đổi tên cũng lưu như Enter. Thiết kế không nêu phím tắt nào khác
(không có Ctrl+S, không có Tab tuỳ biến, không có phím tắt chuyển mục).

---

## 14. HỘP THOẠI / NHIỀU BƯỚC

Màn hình này **không có luồng nhiều bước** (không wizard, không "Bước 1/3"). Các lớp che phủ:

| Lớp | z-index | Điều kiện hiện | Cách đóng | Điều kiện chặn |
|---|---|---|---|---|
| Dropdown chọn mẫu | 45 (nội dung) / 40 (màn che) | `mauMenu === true` | bấm màn che, chọn một mẫu, chọn "Tạo mẫu ghép mới…", chọn "Đổi tên mẫu này" | mục "Xoá mẫu này" **bị ẩn hoàn toàn** khi chỉ còn 1 mẫu |
| Ô nhập đổi tên (thay chỗ dropdown) | — | `renaming === true` | Enter / Escape / blur | tên rỗng thì không ghi (giữ tên cũ) |
| Hộp thoại "Tạo mẫu ghép mới" | 60 | `newOpen === true` | nút X, nút "Huỷ", bấm một thẻ khuôn mẫu (vừa tạo vừa đóng) | không có điều kiện chặn — thẻ nào cũng bấm được ngay |

Bấm hàng con "So trùng theo cột" (ô chọn cột) **không** làm lật công tắc "Gộp dòng trùng" —
sự kiện bị chặn nổi bằng `stopPropagation()`. Đây là bẫy đã gặp ở dự án này; phải làm đúng.

---

## 15. TOÀN BỘ CHUỖI TIẾNG VIỆT HIỆN RA MÀN HÌNH (danh sách gom lại để soát)

### 15.1 Nhãn nút và mục bấm được
"Sáng" · "Tối" · "Màn hình chính" · "Thu nhỏ" · "Phóng to" · "Đóng" · "Vẫn dùng bản cũ" ·
"Thử lấy lại" · "Tạo mẫu ghép mới…" · "Đổi tên mẫu này" · "Xoá mẫu này" · "Trả mẫu về ban đầu" ·
"Mở Khớp cột" · "Kiểm tra kết nối" · "Lấy dữ liệu mới" · "Mở bản ghép để nghe" · "Huỷ"

### 15.2 Tiêu đề, nhãn nhóm, tiêu đề cột
"Văn bản ghép" · "Văn bản ghép — Giọng Việt" · "Mẫu ghép trong hồ sơ này" · "Nguồn dữ liệu" ·
"Khớp cột" · "Lọc & nhóm" · "Đầu danh sách" · "Mẫu câu mỗi dòng" · "Câu xen giữa" · "Cuối danh sách" ·
"Lấy dữ liệu mới" · "Bảng trong tệp" · "Dòng tiêu đề" · "Cột" · "Cột trong sheet" · "Dùng làm" ·
"Cách đọc" · "Chèn được" · "Khoảng ngày" · "Từ ngày" · "Đến ngày" · "Nhóm theo cột" ·
"Chèn dữ liệu từ sheet" · "Bản ghép hoàn chỉnh" · "Tạo mẫu ghép mới" · "So trùng theo cột" ·
"Đọc câu này sau mỗi" · "dòng"

### 15.3 Nhãn công tắc và thẻ
"Đang đọc phần này" · "Đang bỏ qua phần này" · "Bấm nút để lấy dữ liệu mới" · "Tự kiểm tra định kỳ" ·
"Khi không lấy được" · "Luôn bật" · "Đã chọn" · "5 phút một lần" · "Đang tắt" ·
"Bỏ dòng thiếu dữ liệu" · "Gộp dòng trùng" · "Giữ đúng thứ tự trong sheet" ·
"Đọc tên nhóm trước mỗi nhóm" · "Đang dùng" · "Có sẵn" · "Theo bảng tính" · "Số lớn trước" ·
"4 dòng bị bỏ" · "2 dòng gộp lại" · "chưa có cột nhóm"

### 15.4 Nhãn khối xem trước
"Đầu danh sách · tĩnh" · "Tên nhóm · từ Google Sheet" · "Tên nhóm · từ tệp trên máy" ·
"Danh sách · từ Google Sheet" · "Danh sách · từ tệp trên máy" · "Câu xen giữa · tĩnh" ·
"Cuối danh sách · tĩnh"

### 15.5 Câu trạng thái, cảnh báo, gợi ý (nguyên văn đầy đủ)
- "Một mẫu ghép cho mỗi loại danh sách · phần tĩnh bạn viết, phần động lấy từ bảng tính"
- "Chưa lấy được danh sách mới, đang dùng bản đã tải lúc 14:03 hôm nay"
- "{n} dòng của bản cũ vẫn đọc và xuất được bình thường. Nếu bảng tính vừa thêm dòng, hãy thử lấy lại trước khi đọc."
- "Dữ liệu cũ — lấy lúc 14:03 hôm nay · {n} dòng"
- "Đã cập nhật 14:58 hôm nay · {n} dòng · tự kiểm tra 5 phút một lần"
- "Mẫu này thuộc hồ sơ Danh sách, biểu mẫu. Các hồ sơ khác không bị ảnh hưởng."
- "Nơi lấy danh sách và lúc nào lấy lại"
- "Phần mềm tự đoán, bạn sửa lại nếu đoán sai"
- "Dòng nào được đọc, đọc theo thứ tự nào"
- "Phần động — mỗi dòng bảng tính thành một câu"
- "Phần tĩnh — bạn viết một lần, dùng cho mọi lần đọc"
- "Bảng tính phải bật “Bất kỳ ai có đường liên kết đều xem được”. Không cần đăng nhập, cài xong dùng ngay."
- "Đăng nhập một lần, sau đó chọn bảng tính từ Drive. Dùng được cả bảng riêng tư, không cần đổi quyền chia sẻ."
- "Chọn tệp .xlsx hoặc .csv đã tải về. Không cần mạng — dùng khi mất Internet."
- "Luôn bật. Nút nằm ở thanh dưới của màn hình này và trên màn hình chính."
- "Chỉ kiểm tra, không tự đổi giữa lúc đang đọc. Có dòng mới thì hiện nút “Cập nhật danh sách”."
- "Dùng bản đã tải lần trước và báo rõ là dữ liệu ngày nào — không dừng buổi đọc."
- "Phần mềm đọc dòng tiêu đề và tự đoán cách dùng từng cột. Cột nào cũng chèn được vào mẫu câu, trừ cột đặt “Bỏ qua”. Cách đọc quyết định máy đọc ô đó thành gì — cùng một ô 2.500.000 có thể đọc thành “hai triệu năm trăm nghìn đồng” hoặc đọc từng chữ số."
- "Cột đặt “Bỏ qua” vẫn nằm trong sheet, chỉ là không đọc tới. Mỗi mẫu chỉ có một cột nhóm và một cột lọc ngày."
- "Dòng thiếu dữ liệu ở cột dùng trong câu sẽ không đọc."
- "Trùng nhau thì chỉ đọc lần đầu, số tiền được cộng gộp."
- "Trùng nhau thì chỉ đọc lần đầu."
- "Đọc từ trên xuống như trong bảng tính. Tắt thì sắp theo cột số giảm dần."
- "Hai dòng có cùng {tên cột} được coi là một."
- "Chọn cột để so trùng."
- "Lấy theo cột {tên cột}. Bỏ trống hai ô này thì đọc toàn bộ danh sách."
- "Chưa có cột nào đặt “Lọc theo ngày”, nên bộ lọc này chưa có tác dụng."
- "Nhóm theo cột {tên cột}. Trước mỗi nhóm sẽ đọc: “{câu nhóm}”"
- "Chọn một cột đặt “Nhóm theo cột này” ở mục Khớp cột trước đã."
- "Sẽ đọc {n} lần trong {m} dòng"
- "Mỗi dòng trong bảng tính sẽ được đọc theo mẫu này"
- "Nội dung đọc — cách dòng để ngắt đoạn"
- "Ô số tiền 2.500.000 sẽ được đọc thành “hai triệu năm trăm nghìn đồng”, ô điện thoại đọc từng chữ số."
- "Mỗi cột được đọc theo Cách đọc đã đặt: ngày tháng đọc thành lời, số điện thoại đọc từng chữ số, tên riêng đọc chậm và rõ dấu."
- "Muốn đọc khác, đổi Cách đọc của cột đó ở mục Khớp cột, hoặc thêm dòng vào Từ điển phát âm."
- "Cách dòng một lần là ngắt đoạn — phần mềm sẽ nghỉ một nhịp ở đó. Muốn nghỉ lâu hơn, chèn thẻ khoảng lặng ở màn hình chính."
- "Khối viền xanh là phần lấy từ bảng tính, sẽ tự đổi theo dữ liệu. Khối viền xám là phần bạn viết, không đổi."
- "… còn {n} dòng nữa, đọc theo đúng mẫu câu ở trên."
- "Chọn loại danh sách gần giống của bạn. Tên cột, mẫu câu và câu chữ đều sửa lại được sau."
- "Mẫu mới được thêm vào hồ sơ Danh sách, biểu mẫu — các mẫu đang có không đổi."
- Năm câu vấn đề — xem mục 7.2

### 15.6 Placeholder
- "Dán link https://docs.google.com/spreadsheets/…"
- "Chưa chọn tệp trên Drive"
- "Chưa chọn tệp trên máy"
- "Ví dụ: {ten}, phát tâm công đức số tiền {sotien}."
- "Gõ nội dung sẽ được đọc. Cách dòng một lần để ngắt đoạn."

### 15.7 Tooltip (`title`)
- "Quay lại màn hình chính" (2 chỗ: chip thanh tiêu đề, mũi chevron dải trái)
- "Thu nhỏ" · "Phóng to" · "Đóng" (2 chỗ: nút cửa sổ, nút X hộp thoại)
- "Mẫu {i}/{n} trong hồ sơ này — bấm để đổi mẫu, đổi tên hoặc tạo mẫu mới"
- "{tên mẫu} — {số dòng} dòng"
- "{nhãn mục} — {dòng phụ}" (7 mục dải trái)
- "Xoá mọi thay đổi bạn đã nhập, trả các mẫu về nội dung ban đầu"
- "Tắt thì phần này không được đọc"
- "Cột này dùng để làm gì"
- "Máy sẽ đọc ô này thành gì"
- "Bấm để chèn {biến} vào mẫu câu — lấy từ cột {chữ cột} ({tên cột}), đọc theo kiểu {cách đọc}"
- "Tạo mẫu ghép theo {tên khuôn mẫu}"
- "Mở bản ghép thành một tab tệp ở màn hình chính"

---

## 16. LIÊN KẾT SANG MÀN HÌNH KHÁC

| Đích | Vị trí trong màn hình |
|---|---|
| `GiongDoc - Màn hình chính v2 (nghe theo dòng).dc.html` | chip "Màn hình chính" ở thanh tiêu đề; nút chevron trái ở đầu dải trái |
| `GiongDoc - Màn hình chính v2 (nghe theo dòng).dc.html#banghep` | nút chính "Mở bản ghép để nghe" ở thanh dưới |
| `GiongDoc - Từ điển phát âm.dc.html` | liên kết "Từ điển phát âm" trong thẻ ghi chú ở mục Mẫu câu (`nav = 4`) |

---

## 17. CHỖ CẦN CHÚ Ý KHI LẬP TRÌNH (rút từ thiết kế)

1. **Băng cảnh báo dữ liệu cũ mặc định HIỆN** (`stale: true`). Đây là trạng thái khởi động của bản mẫu,
   không phải trạng thái ngoại lệ. Cả hai nút của nó đều chỉ tắt băng, không có hành vi khác nhau
   trong bản mẫu — nhưng thực tế "Thử lấy lại" phải gọi lấy dữ liệu thật.
2. **"Mẫu câu mỗi dòng" không có công tắc tắt** — luôn đọc. Chỉ ba khối tĩnh (đầu / xen giữa / cuối)
   tắt được.
3. **"Câu xen giữa" mặc định TẮT**, hai khối tĩnh còn lại mặc định BẬT.
4. **Vai trò độc quyền:** chỉ một cột được "Nhóm theo cột này" và một cột được "Lọc theo ngày".
   Cột xuất hiện trước thắng; cột sau bị đánh dấu đỏ + nền vàng + mất chip biến + sinh câu vấn đề.
5. **Cột "Bỏ qua" không sinh biến** — nên không chèn được vào mẫu câu.
6. **Chèn biến phải đúng vị trí con trỏ**, giữ được đoạn đang chọn (thay thế), và đặt lại con trỏ ngay
   sau biến. Nối vào cuối chỉ là đường dự phòng khi chưa có tiêu điểm.
7. **Số "4 dòng bị bỏ" và "2 dòng gộp lại" là số cứng trong bản mẫu** — bản thật phải tính từ dữ liệu.
8. **Đếm đoạn tách theo hai dòng trống trở lên**, không phải theo một lần xuống dòng. Một lần xuống
   dòng chỉ là ngắt đoạn khi đọc (nghỉ một nhịp), không tính thành đoạn mới ở đây.
9. **Ước thời lượng 9 giây một đoạn** (`round(số đoạn * 9 / 60)` phút).
10. **Khung 1440×900 cố định** trong bản mẫu; dải trái 240px và khung xem trước 392px cũng cố định,
    chỉ khung giữa co giãn.
11. Ô nhập và ô soạn đều có **gạch dưới 2px `var(--acc)`** — đây là dấu hiệu nhận biết trường sửa được
    trong bộ thiết kế này.
12. Bấm hàng con "So trùng theo cột" phải chặn nổi sự kiện, không được lật công tắc cha.
