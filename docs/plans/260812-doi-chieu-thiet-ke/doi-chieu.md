# Đối chiếu đặc tả GiongDoc (bản 2026-08-12) với dự án hiện tại

Nguồn đúng: `design_handoff_giongdoc/README.md` + 6 file bản mẫu trong `designs/`.
Dự án khảo sát: `C:\Projects\DocCongDuc` — `GiongDoc.py`, `ui/*`, `giaodien/*.py`, `DocCongDuc.py`.

Ký hiệu: **✅ đã đúng** · **⚠️ đã có nhưng sai** · **❌ chưa có**

Tổng: **167 mục — ✅ 18 · ⚠️ 90 · ❌ 57** (+2 mục bảng §12 bổ sung sau audit).

> **Đính chính (audit 2026-08-12):** bản đầu ghi *"118 mục — ✅22 ⚠️41 ❌55"*. Con số đó là **ước, không đếm**.
> Đếm bằng `awk -F'|' '/^\| [0-9]/'` ra 167 dòng — 18 / 90 / 57. Xem §Đính chính cuối file.

---

## 0. Nền tảng và khung chung

| # | Mục đặc tả | Trạng thái | File / vị trí | Ghi chú |
|---|---|---|---|---|
| 0.1 | Có framework để dựng giao diện | ✅ | `GiongDoc.py:83`, `ui/index.html` | pywebview + WebView2, HTML/CSS/JS thuần. **Không cần chọn WinUI 3 hay Electron** — đổi nền tảng sẽ phá đường đóng gói (`DongGoi.bat`), thuộc việc hội đồng. |
| 0.2 | Cửa sổ không khung, 3 nút cửa sổ | ✅ | `index.html:48-59`, `GiongDoc.py:92` | Nút đóng `--close #c42b1c` đã đúng cả 2 chế độ (`app.css:34,76`). |
| 0.3 | Đủ 6 màn hình | ⚠️ | `index.html:61,252,291,321,362` | Có 5 view: `chinh`, `giong`, `soat`, `tudien`, `caidat`. **Thiếu màn Xuất file âm thanh** (hiện là 3 modal rời, không phải 1 hộp 3 giai đoạn). |
| 0.4 | Không còn màn *Xem trước chuẩn hoá* riêng | ⚠️ | `app.js:1134` `moXemTruoc()`, `index.html:75-77` | Vẫn còn nút riêng trên thanh công cụ + modal `dialog--lg` riêng. Phải gộp thành **tab 2 của màn Soát văn bản**. |
| 0.5 | Cửa sổ 1440×900 | ✅ | `GiongDoc.py:22-44` | Cửa sổ lấp đầy vùng làm việc, `min_size=(980,620)`. 1440×900 chỉ là khung xem của bản mẫu — giữ nguyên cách hiện tại, nhưng layout phải co giãn đúng. |

---

## 1. Design tokens

| # | Mục đặc tả | Trạng thái | File / vị trí | Ghi chú |
|---|---|---|---|---|
| 1.1 | 30 token màu chế độ sáng | ⚠️ | `app.css:6-42` | Khớp gần hết. Xem 1.3–1.7 phần lệch. |
| 1.2 | Token màu chế độ tối | ⚠️ | `app.css:44-77` | Khớp gần hết. Xem 1.4, 1.6. |
| 1.3 | `sel rgba(0,0,0,.055)` — đoạn đang chọn | ❌ | — | **Không có token `--sel`**, cũng không có trạng thái "đoạn đang chọn" nào. |
| 1.4 | `warn-bg #fff9ec` / `warn-bd #f0e2c2` (sáng), `#3a3320` / `#5c4f2a` (tối) | ❌ | `app.css:31,71` | Chỉ có `--warn`. Thiếu cả nền và viền → chưa dựng được dải cảnh báo vàng. |
| 1.5 | `warn` tối = `#fce100` | ⚠️ | `app.css:71` | Hiện `#f7b84b`. |
| 1.6 | `mark` = `rgba(0,103,192,.14)` / `rgba(76,194,255,.2)` | ⚠️ | `app.css:36,77` | Hiện `.13` / `.18`. |
| 1.7 | Màn nền hộp thoại `rgba(0,0,0,.34)` | ⚠️ | `app.css:37,78` | Hiện `--scrim` `.32` (sáng) / `.45` (tối). Đặc tả dùng một giá trị `.34`. |
| 1.8 | Đổ bóng: dropdown `shadow`, hộp thoại `0 32px 64px`, thông báo góc `0 12px 28px` | ✅ | `app.css` (3 chỗ) | Đủ cả ba. |
| 1.9 | Chữ Segoe UI Variable Text → Segoe UI → Inter → system-ui | ✅ | `app.css:88` | |
| 1.10 | Thân đoạn 18px, tiêu đề đoạn 20px/700, dòng cao 1.55 | ⚠️ | `app.css:39-42,606-616,665` | **Đã đo:** `--doc-size:18px` ✅, `--doc-line: ×1.55` ✅. `app.css:665` `.line--head .line__text{font-weight:600;color:var(--txt)}` — **không đặt `font-size`** nên tiêu đề đoạn vẫn 18px (đặc tả 20px) và đậm **600** (đặc tả **700**). |
| 1.11 | `font-variant-numeric: tabular-nums` cho mọi con số | ✅ | 12 chỗ trong `app.css` | |
| 1.12 | Chữ đoạn dùng `text-wrap: pretty` | ❌ | `app.css:614` | Đang dùng `white-space: pre-wrap` + `overflow-wrap: break-word`, chưa có `text-wrap: pretty`. |
| 1.13 | Bo góc 4px control / 8px thẻ · dropdown · hộp thoại / 6px dải cảnh báo / 7px 7px 0 0 tab | ⚠️ | rải rác `app.css` | Phần lớn đúng; dải cảnh báo và tab cần đối chiếu lại từng chỗ khi dựng. |

---

## 2. Mô hình dữ liệu

| # | Mục đặc tả | Trạng thái | File / vị trí | Ghi chú |
|---|---|---|---|---|
| 2.1 | **Hồ sơ = một chỗ làm việc riêng** | ⚠️ | `giaodien/ho_so.py:1-16,28-34` | Hiện hồ sơ chỉ là **preset thiết lập**: giọng + phong cách + các khoảng nghỉ, đổi hồ sơ = đổ vào `cauhinh.ini`. Đúng cái mà đặc tả nói *không phải*. |
| 2.2 | Hồ sơ giữ **danh sách tệp đang mở** | ❌ | — | `ho_so.py` không có khái niệm tệp. Không có `tabsByProfile` / `activeByProfile`. |
| 2.3 | Đổi hồ sơ → đổi tab, nội dung, giọng, thanh chỉnh, *Cần chú ý* | ⚠️ | `cau_noi.py:311` `doi_ho_so()` | Chỉ đổi giọng + thanh chỉnh + nạp lại tệp mặc định của loại. Không đổi tab (chưa có tab), *Cần chú ý* soát lại theo nội dung mới. |
| 2.4 | 4 hồ sơ mặc định theo bảng | ⚠️ | `ho_so.py:112-125`, `hoso.json` | Hiện 2: *Danh sách công đức* (`congduc`), *Đọc văn bản* (`vanban`). Thiếu *Bài viết, văn bản* / *Thông báo ngắn* / *Sách nói*. |
| 2.5 | Hồ sơ thứ tư tên **Danh sách, biểu mẫu** | ⚠️ | `hoso.json:6` | Đang là *Danh sách công đức*. |
| 2.6 | Hồ sơ không phân theo `loai` cứng | ⚠️ | `ho_so.py:29-34` | `loai ∈ {congduc, vanban}` quyết định cả bộ khoá thiết lập lẫn tệp lời dẫn. Đặc tả mới không có khái niệm này. |
| 2.7 | Tài liệu = mảng đoạn `head \| body \| blank` | ⚠️ | `du_lieu.py:77` `dong_hien_thi()`, `app.js:286-299` | Hiện là mảng **dòng** có `text`, `amount` (số tiền), `dur` (thời lượng), `tu[]`, `kind` (`tieude`/`nguoi`). Không có `blank`. |
| 2.8 | Mỗi tài liệu có bộ *Cần chú ý* riêng | ❌ | `cau_noi.py:670`, `soat.py:128` | Soát tính cho **nội dung đang mở duy nhất**, không lưu theo tài liệu. |
| 2.9 | Thời lượng: `ký tự / 11` giây, ghi `42 giây` / `1 phút 28 giây` | ⚠️ | `du_lieu.py:24-28` | Có công thức `len/KY_TU_MOI_GIAY` nhưng in ra dạng `12,3s` và **theo từng dòng** (cột thời lượng), không phải tổng bài. |
| 2.10 | Bảng trạng thái ứng dụng 18 khoá | ⚠️ | `app.js:36-67` | `S` hiện có 25 khoá khác hẳn. **Thiếu**: `tabsByProfile`, `activeByProfile`, `situation`, `sel`, `mode` (`all`/`one`), `rail`, `find`, `tags`, `tune`, `chips`, `exportOpen`, `exporting`, `toast`. |

---

## 3. Màn hình 1 — Màn hình chính

### 3a. Thanh menu

| # | Mục đặc tả | Trạng thái | File / vị trí | Ghi chú |
|---|---|---|---|---|
| 3.1 | 6 menu: Tệp · Chỉnh sửa · **Chèn** · Giọng · Xem · Trợ giúp | ⚠️ | `app.js:71-108` | Hiện 5: Tệp · Chỉnh sửa · Giọng đọc · Xem · Trợ giúp. **Thiếu menu Chèn**. |
| 3.2 | Menu Tệp: Mở tệp… `Ctrl+O` · Dán `Ctrl+V` · Lưu `Ctrl+S` · Xuất `Ctrl+E` · Đóng tệp `Ctrl+W` | ⚠️ | `app.js:72-80` | Có Mở/Dán/Xuất. **Thiếu Lưu, Đóng tệp**. Thừa *Nạp lại tệp*, *Thoát*. Dán ghi `Ctrl+Shift+V`. |
| 3.3 | Menu Chỉnh sửa: Hoàn tác · Làm lại · Cắt · Sao chép · **Tìm và thay thế `Ctrl+H`** | ❌ | `app.js:81-85` | Hiện là *Sửa tệp đang mở*, *Lời dẫn đầu và cuối*, *Từ điển phát âm* — khác hoàn toàn. |
| 3.4 | Menu Chèn: Thẻ cảm xúc `Alt+1…3` · Khoảng lặng 1 giây `Alt+S` · Ngắt đoạn `Enter` | ❌ | — | Chưa có. |
| 3.5 | Menu Giọng: Đổi giọng `Ctrl+G` · Nghe mẫu `Ctrl+M` · Thư viện giọng · Nhân bản giọng từ file… | ⚠️ | `app.js:86-93` | Có 4 mục tương đương nhưng nghe mẫu gán `Ctrl+K`, thiếu *Thư viện giọng*, thừa *Tải lại danh sách giọng*. |
| 3.6 | Menu Xem: Thu gọn danh sách hồ sơ `Ctrl+B` · Cỡ chữ ± · Giao diện tối | ⚠️ | `app.js:94-103` | Thiếu *Thu gọn danh sách hồ sơ*. Thừa *Xem trước chuẩn hoá*, *Soát văn bản*, *Cỡ chữ mặc định*. |
| 3.7 | Menu Trợ giúp: Hướng dẫn nhanh `F1` · Danh sách phím tắt `Ctrl+/` · Giới thiệu | ⚠️ | `app.js:104-107` | Thiếu *Danh sách phím tắt*. |
| 3.8 | Menu thả xuống ≥250px, mục cao 32px, phím tắt bên phải `txt3`, bấm ra ngoài đóng | ✅ | `app.js:110-133`, `app.css` `.menupop` | Cơ chế đã đúng, chỉ cần đổi nội dung. |

### 3b. Thanh công cụ

| # | Mục đặc tả | Trạng thái | File / vị trí | Ghi chú |
|---|---|---|---|---|
| 3.9 | Thứ tự: Dán · Mở file · ngăn · Soát văn bản · Thẻ cảm xúc | ⚠️ | `index.html:67-85` | Thứ tự hiện: **Mở file · Dán · ngăn · Xem trước chuẩn hoá · Soát văn bản**. Phải đảo Dán lên đầu. |
| 3.10 | Bỏ hẳn nút **…** | ⚠️ | `index.html:83`, `app.js:1562` | Nút `btnMore` vẫn còn (mở menu cỡ chữ/chế độ tối). Phải gỡ. |
| 3.11 | Bỏ nút *Xem trước chuẩn hoá* khỏi thanh công cụ | ⚠️ | `index.html:75-77` | Vẫn còn. |
| 3.12 | *Dán văn bản* là nút chìm, cùng mức nhấn với nhóm trái | ⚠️ | `index.html:68,71` | Ngược lại: *Mở file* mang `tbtn--primary` (nút viền), *Dán* là nút chìm. |
| 3.13 | **Thẻ cảm xúc** có chevron, mở menu chèn thẻ | ❌ | — | Chưa có nút, chưa có menu. |
| 3.14 | **Tìm và thay thế** — có nhãn chữ, bật/tắt thanh tìm | ⚠️ | `index.html:82`, `app.js:1558` | Nút chỉ có icon, không nhãn. **Bấm vào chỉ hiện hộp thoại báo "chưa làm"** → đang là nút giả, vi phạm KPI của dự án. |
| 3.15 | **Nghe toàn bộ** — nút viền 34px, icon tam giác, ở góc phải | ❌ | — | Không có. Việc phát nằm ở thanh phát dưới cùng. |
| 3.16 | **Xuất file âm thanh** — nút accent 34px, ở góc phải thanh công cụ | ⚠️ | `index.html:230-232` | Có nút nhưng nằm ở **thanh phát**, không phải thanh công cụ. |
| 3.17 | Cặp (Nghe toàn bộ)(Xuất) **ẩn hẳn** khi chưa có văn bản | ⚠️ | `app.js:602` | Hiện chỉ `disabled` (hiện mờ), không ẩn. |
| 3.18 | Khi chưa có văn bản: Soát · Thẻ cảm xúc · Tìm chuyển màu `dis` | ❌ | — | Chưa có xử lý. |
| 3.19 | Khi mất kết nối / hết lượt / giọng đang tải: Nghe → `dis`, Xuất → nút viền `dis` | ❌ | — | Chưa có khái niệm tình huống. |
| 3.20 | Menu Thẻ cảm xúc 260px: *Chèn vào đoạn N* + 3 thẻ + *Gỡ thẻ khỏi đoạn này* | ❌ | — | Chưa có. `app.js:294` có vẽ `line__chip` nhưng chip đến từ dữ liệu Python, người dùng không chèn được. |

### 3c. Dải tab tệp

| # | Mục đặc tả | Trạng thái | File / vị trí | Ghi chú |
|---|---|---|---|---|
| 3.21 | Nhiều tab, chuyển được | ❌ | `app.js:223-233` | Chỉ vẽ **một tab cứng** từ `S.docName`. |
| 3.22 | Đóng tab bằng dấu × | ❌ | `app.js:225-229` | Không có dấu ×. |
| 3.23 | Nút `+` 28px cuối dải | ⚠️ | `app.js:230-232` | Có nút `+` nhưng gọi `moFile()` (mở hộp chọn tệp), không phải *Tệp mới*. |
| 3.24 | Tab đang mở: nền `layer`, viền trên/trái/phải, tên đậm 600, icon accent · rộng tối đa **230px** | ⚠️ | `app.css:314-328` | **Đã đo:** cao 34px ✅, `border-radius:7px 7px 0 0` ✅, nhưng `max-width:260px` (đặc tả **230px**). Chưa có tab thứ hai để phân biệt. |
| 3.25 | Dải tab thuộc về hồ sơ đang chọn | ❌ | — | Chưa có. |
| 3.26 | Đóng tab cuối → còn một tab *Chưa đặt tên* rỗng | ❌ | — | Chưa có. |

### 3d. Thanh tìm và thay thế

| # | Mục đặc tả | Trạng thái | File / vị trí | Ghi chú |
|---|---|---|---|---|
| 3.27 | Thanh dưới dải tab: Tìm + ô nhập + `1/1` + Thay bằng + ô nhập + Thay thế + Thay tất cả + × | ❌ | — | Chưa có gì. |

### 3e. Cột trái — Hồ sơ đọc (240px)

| # | Mục đặc tả | Trạng thái | File / vị trí | Ghi chú |
|---|---|---|---|---|
| 3.28 | Nút ba gạch thu gọn ở đầu cột | ❌ | `index.html:94-99` | Đầu cột hiện là tiêu đề + nút `+` (tạo hồ sơ). |
| 3.29 | Thu gọn còn dải icon 44px, có tooltip | ❌ | — | Chưa có. |
| 3.30 | Mỗi mục hồ sơ ~52px: icon + tên + tên giọng 12px `txt3` | ✅ | `app.js:147-165`, `app.css` `.mode` | Đúng cấu trúc. |
| 3.31 | Mục đang chọn có vạch dọc 3×18px `acc` ở `left:2px` | ✅ | `app.css:400-410` | **Đã đo:** `left:2px; width:3px; height:18px; border-radius:2px; background:var(--acc)` — khớp từng con số. |
| 3.32 | Nút **Tạo hồ sơ mới** (nút chìm, icon +) **dưới danh sách** | ⚠️ | `index.html:96-98` | Đang là nút icon nằm ở đầu cột, không có nhãn chữ. |
| 3.33 | Đáy cột chỉ có **Thư viện giọng** + **Cài đặt** | ⚠️ | `index.html:101-105` | Có 3 mục — thừa *Từ điển phát âm* (đặc tả chuyển nó xuống thẻ *Cần chú ý* ở cột phải). |
| 3.34 | Mỗi mục hồ sơ **không** có nút sửa/xoá inline | ⚠️ | `app.js:156-163` | Đang có 2 nút bánh răng + thùng rác trên từng mục. Đặc tả không có. |

### 3f. Cột giữa — Vùng đọc

| # | Mục đặc tả | Trạng thái | File / vị trí | Ghi chú |
|---|---|---|---|---|
| 3.35 | Đầu thẻ trái: `215 từ · 16 đoạn · khoảng 1 phút 28 giây` | ⚠️ | `index.html:110-111`, `app.js:242` | Có `docMeta` nhưng nội dung khác và **kèm tên tệp** ở bên trái. |
| 3.36 | **Không lặp lại tên tệp** ở đầu vùng đọc | ⚠️ | `index.html:110` | `#docName` vẫn in tên tệp. Phải gỡ. |
| 3.37 | Đầu thẻ phải: gợi ý *Bấm số đoạn để nghe riêng đoạn đó* 12.5px `txt3` | ❌ | `index.html:112` | Chỗ đó hiện là nhãn `THỜI LƯỢNG`. |
| 3.38 | **Bỏ nhãn `THỜI LƯỢNG`** | ⚠️ | `index.html:112`, `app.css:485-495` | Vẫn còn. |
| 3.39 | **Bỏ cột thời lượng từng đoạn** | ⚠️ | `app.js:297`, `app.css:636-646` | `.line__dur` rộng 84px vẫn còn. |
| 3.40 | Cột số tiền (di sản công đức) | ⚠️ | `app.js:278-280,296`, `app.css:623-634` | `.line__amount` rộng 170px — đặc tả mới **không có** cột này. |
| 3.41 | Máng số rộng 54px, cách chữ 14px, 12.5px `txt3` | ⚠️ | `app.css:592-601` | Rộng 54px ✅, cỡ 12.5px ✅, nhưng `padding-right: 16px` (đặc tả 14px). |
| 3.42 | Rê chuột máng số: chữ `acc` nền `acc-soft` | ❌ | `app.css:586` | Chỉ có hover cả dòng nền `sub-h`. Máng số không có hover riêng. |
| 3.43 | **Bấm số đoạn = nghe riêng đoạn đó, hết đoạn thì dừng** | ⚠️ | `app.js:292,1410`, `cau_noi.py:514` | Bấm **cả dòng** gọi `nhay_toi()` = dời con trỏ đọc trong luồng liền mạch. Không phải nghe riêng. |
| 3.44 | Tooltip *Nghe riêng đoạn này, nghe hết đoạn thì dừng* | ❌ | — | Chưa có. |
| 3.45 | Bấm thân đoạn = **chọn đoạn** (nền `sel`, con trỏ nháy, đổi số ở thanh trạng thái) | ❌ | — | Chưa có trạng thái "đang chọn". |
| 3.46 | Đo chữ tối đa **700px**, đệm phải **24px** | ❌ | `app.css:606-617` | `.line__text` là `flex:1` chiếm hết chiều rộng, `padding-right: 12px`. Không giới hạn đo chữ. |
| 3.47 | Đoạn `blank` cao 24px, chỉ có số | ❌ | — | Chưa có loại đoạn này. |
| 3.48 | Chip thẻ cảm xúc đặt trước chữ, cách 8px, không xuống dòng | ⚠️ | `app.js:294`, `app.css:650+` | Có `.line__chip` nhưng dữ liệu đến từ Python, người dùng không tạo/gỡ được. |
| 3.49 | Trạng thái *Đang đọc*: nền `hl` + vạch trong 3px `acc`, chữ đậm 600, máng số `acc`/700 + tam giác nhỏ | ⚠️ | `app.css:588-591,603-604` | Nền + vạch + chữ đậm ✅. **Thiếu tam giác nhỏ** ở máng số. |
| 3.50 | *Đã đọc xong* chỉ mờ **khi nghe liền mạch** | ⚠️ | `app.js:290`, `app.css:604,621` | Hiện luôn mờ mọi đoạn có `stt < S.pos`, không phân biệt chế độ. |
| 3.51 | *Đang tạo âm thanh*: vòng xoay 11px thay tam giác ở máng số | ❌ | — | Chưa có. |
| 3.52 | Thanh cuộn giả 6px bo 3px `rail` mờ .4 | ✅ | `app.css:102-110` | Đã tạo kiểu cho thanh cuộn. |
| 3.53 | Trạng thái rỗng: khung nét đứt 500px, icon clipboard 52px, tiêu đề *Dán văn bản vào đây để bắt đầu* | ⚠️ | `index.html:130-140`, `app.js:260-271` | Có khung rỗng nhưng: icon là `filebig` (tài liệu) không phải clipboard; tiêu đề là *Chưa có văn bản để đọc*; hai dòng phụ khác chữ; **thứ tự nút ngược** — *Chọn tệp từ máy…* đang là nút accent, đặc tả cho *Dán văn bản* làm accent. |

### 3g. Cột phải (300px)

| # | Mục đặc tả | Trạng thái | File / vị trí | Ghi chú |
|---|---|---|---|---|
| 3.54 | Phần đầu thẻ: nhãn `HỒ SƠ ĐANG DÙNG` + tên hồ sơ 14px/600 | ❌ | `index.html:148-149` | Thẻ bắt đầu thẳng bằng *Giọng đọc*. |
| 3.55 | Nhãn `GIỌNG ĐỌC` + ô chọn 36px + nút loa 36×36 bên cạnh | ⚠️ | `index.html:149-161` | Có ô chọn (kiểu hai dòng) nhưng nút nghe thử là **nút chữ rộng cả hàng** bên dưới, không phải nút loa vuông bên cạnh. |
| 3.56 | Bấm loa hiện *Đang phát mẫu {tên giọng}…* + chấm nhấp nháy, tắt sau ~2,5s | ❌ | `app.js:1845` `ngheThuXong` | Có cơ chế báo xong, chưa có dòng chữ + chấm theo đặc tả. |
| 3.57 | Dropdown giọng: nhóm `GIỌNG CÓ SẴN` / `GIỌNG CỦA TÔI` + **Nhân bản giọng từ file…** | ⚠️ | `app.js:397-440` | Có dropdown chia nhóm. Cần đối chiếu nhãn nhóm và mục *Nhân bản* ở cuối. |
| 3.58 | Nhãn `ĐIỀU CHỈNH` có chevron thu gọn, dòng tóm tắt khi đóng | ❌ | `index.html:166-176` | Có 2 khối *Điều chỉnh* (phong cách) và *Nhịp đọc* (thanh trượt), **không thu gọn được**, không có dòng tóm tắt. |
| 3.59 | 3 thanh trượt: **Tốc độ** (−50…+100%) · **Cao độ** (−12…+12) · **Âm lượng** (0…100%) | ❌ | `du_lieu.py:154-183`, `app.js:473-502` | Thanh trượt hiện là **các khoảng nghỉ** (nghỉ giữa người/nhóm/đoạn/câu, số ký tự mỗi đoạn). **Xung đột với CLAUDE.md §5: "VieNeu không có tham số tốc độ và cao độ"** → xem mục *Việc cần quyết* #1. |
| 3.60 | Nút **Đặt lại mặc định** | ❌ | — | Chưa có. |
| 3.61 | Chọn giọng / kéo thanh = **ghi vào hồ sơ đang dùng** | ⚠️ | `cau_noi.py:429,441`, `ho_so.py:168-180` | Ghi vào `cauhinh.ini` rồi mới cất vào hồ sơ khi chuyển hồ sơ. Kết quả gần đúng nhưng nguồn đúng đang là `cauhinh.ini`, không phải hồ sơ. |
| 3.62 | Khối *Phong cách đọc* | ⚠️ | `index.html:166-169`, `app.js:462-471` | Đặc tả **không có** khối này. Phải gỡ hoặc chốt lại. |
| 3.63 | Công tắc *Nhấn mạnh dòng có số lớn* | ⚠️ | `index.html:185-192` | Di sản công đức, đặc tả không có. |
| 3.64 | **Thẻ dưới — Cần chú ý** (thẻ riêng, chỉ hiện khi có văn bản) | ⚠️ | `index.html:178-183`, `app.js:504-515` | Hiện là **một nút một dòng** nhét trong thẻ *Nhịp đọc*, không phải thẻ riêng. |
| 3.65 | Câu tóm tắt *9 chỗ cần chú ý, trong đó 2 lỗi nên sửa trước khi xuất.* | ⚠️ | `app.js:512-514` | Câu hiện là *"N chỗ nên sửa trước khi đọc"* — khác chữ. |
| 3.66 | Danh sách loại lỗi, mỗi dòng 31px: chấm 7px + tên loại + số đếm dạng nhãn bo 4px | ❌ | — | Chưa có danh sách theo loại, chỉ có 1 dòng tổng. |
| 3.67 | Bấm một dòng → chọn đoạn tương ứng ở giữa | ❌ | — | Chưa có. |
| 3.68 | Đáy thẻ: nút viền **Soát văn bản** + liên kết **Từ điển phát âm ›** | ❌ | — | Chưa có. |
| 3.69 | Bỏ khoảng trống lớn giữa thẻ giọng và thẻ *Cần chú ý* | ❌ | `index.html:196-204` | Chỗ đó hiện là khối trạng thái mô hình (`#modelStatus`) — đặc tả chuyển thông tin này xuống **thanh trạng thái**. |

### 3h. Thanh phát

| # | Mục đặc tả | Trạng thái | File / vị trí | Ghi chú |
|---|---|---|---|---|
| 3.70 | Thanh phát **chỉ hiện khi đang phát hoặc đang tạo** | ⚠️ | `index.html:209` | Luôn hiện. |
| 3.71 | **Không có thanh tua** | ⚠️ | `index.html:218-222`, `app.js:1546`, `app.css:1477` | **Có thanh tua bấm được** (`#seek`, tooltip *"Bấm để nhảy tới vị trí"*) → gọi `nhay_toi`. Đặc tả cấm. |
| 3.72 | Nút *Câu trước* / *Câu sau* | ⚠️ | `index.html:211,214` | Đặc tả không có. Chỉ có tạm dừng + dừng. |
| 3.73 | Nút tạm dừng 32px nền accent + nút dừng 32px chìm | ⚠️ | `index.html:212-213` | Có nhưng kèm 2 nút thừa (3.72). |
| 3.74 | *Đang đọc đoạn 4/16* / *Đang nghe riêng đoạn 4* | ⚠️ | `app.js:609-612` | Có nhãn dòng nhưng chưa có chế độ nghe riêng. |
| 3.75 | Đồng hồ `00:35 / 02:12`; ở chế độ nghe riêng đếm theo độ dài đoạn đó | ⚠️ | `app.js:613` | Hiện in *"Ước tính {tổng}"*, không phải đồng hồ chạy / tổng. |
| 3.76 | Thanh tiến trình 150px × 3px, không kéo được | ❌ | — | Hiện là thanh tua kéo/bấm được (3.71). |
| 3.77 | *Đang chuẩn bị đoạn tiếp theo…* / *Nghe hết đoạn này sẽ dừng* | ⚠️ | `app.js:615-619` | Có `bufferLabel` cho phần chuẩn bị; thiếu câu cho chế độ nghe riêng. |
| 3.78 | Trạng thái *Đang tạo âm thanh*: vòng xoay 18px + *Đang tạo âm thanh cho đoạn N* + *Thường mất 5–10 giây* + nút **Huỷ** | ❌ | — | Chưa có. |

### 3i. Thanh trạng thái

| # | Mục đặc tả | Trạng thái | File / vị trí | Ghi chú |
|---|---|---|---|---|
| 3.79 | Trái: `Đoạn 13, Cột 1` | ⚠️ | `index.html:239`, `app.js:621-623` | Hiện in *"Dòng N"* — chữ *dòng*, không có *Cột*. |
| 3.80 | **Bỏ `UTF-8 · CRLF`** | ⚠️ | `index.html:241` | `#statusEnc` vẫn in `UTF-8`. |
| 3.81 | **Bỏ mức phóng to `100%`** | ⚠️ | `index.html:245`, `app.js:625` | `#statusZoom` vẫn còn. |
| 3.82 | Phải: chấm trạng thái + nhãn máy đọc + `Đã lưu 14:02 · Hồ sơ: {tên}` | ⚠️ | `index.html:242-246`, `app.js:624` | Chỉ có `Hồ sơ: {tên}`. **Thiếu chấm + nhãn máy đọc** (đang nằm ở cột phải) và **thiếu `Đã lưu hh:mm`**. |
| 3.83 | 6 tình huống đổi màu chấm và nhãn (`ok`/`acc`/`err`/`warn`) | ❌ | `app.js:531-549` | Khối `#modelStatus` chỉ có 2 trạng thái (đang tải / lỗi), lại nằm sai chỗ. |

### 3j. Hộp thoại xuất (từ màn chính)

| # | Mục đặc tả | Trạng thái | File / vị trí | Ghi chú |
|---|---|---|---|---|
| 3.84 | Bấm *Xuất* → **mở hộp thoại thiết lập** trước | ✅ | `app.js:1180-1247` | Đã đúng luồng này. |
| 3.85 | Hộp rộng 600px, tiêu đề 20px/600 + dòng phụ `{tệp} · {số} đoạn · {giọng}` | ⚠️ | `app.js:1185-1189`, `cau_noi.py:550` | **Đã đo:** `mo_ta = f"{doc_name} · {len(lines)} **dòng** · {giong}"` — đặc tả dùng chữ **đoạn**. |
| 3.86 | **Tên tệp + Định dạng trên cùng một hàng** (WAV 24/16, MP3 320/128) | ⚠️ | `app.js:1191-1197` | Có Tên tệp, đuôi cứng `.wav`. **Không có lựa chọn Định dạng**. |
| 3.87 | Lưu vào (đường dẫn + nút *Chọn…*) | ✅ | `app.js:1198-1204` | |
| 3.88 | Tách tệp: 3 lựa chọn tròn | ✅ | `app.js:1205-1213`, `cau_noi.py:541` | Có. Cần đối chiếu chữ và dòng ước tính. |
| 3.89 | Chân nền `layer2`: ước tính bên trái, Huỷ + Bắt đầu xuất bên phải | ⚠️ | `app.js:1214-1222` | Ước tính đang nằm trong thân (khối `.info`), không ở chân. Thứ tự nút: accent trước, Huỷ sau (đặc tả ngược lại). |
| 3.90 | Bấm *Bắt đầu xuất* → **hộp thoại đóng**, thanh trạng thái chạy *Đang xuất… 34%* | ⚠️ | `app.js:1239-1243,1249-1269` | Hộp **không đóng** — chuyển sang modal tiến trình. Thanh trạng thái không báo gì. |
| 3.91 | ~2 giây sau hiện thông báo góc dưới phải 360px với 2 nút Mở thư mục / Đóng | ⚠️ | `app.js:1271-1307` | Có cả modal *Đã xuất xong* **lẫn** hàm toast. Đặc tả chỉ dùng toast. |

### 3k. Bảy tình huống lỗi và chờ

| # | Mục đặc tả | Trạng thái | File / vị trí | Ghi chú |
|---|---|---|---|---|
| 3.92 | Khung dải cảnh báo (icon 18px + tiêu đề + giải thích + nút) | ⚠️ | `index.html:120-128`, `app.css` `.errbox` | Có `#errBox` gần đúng khung, nhưng **nằm trong vùng đọc**, đặc tả đặt **giữa dải tab và vùng ba cột**, cách hai bên 8px. |
| 3.93 | 1. Mất kết nối máy chủ đọc | ❌ | — | Chưa có. |
| 3.94 | 2. Hết lượt / hết dung lượng gói | ❌ | — | Chưa có. |
| 3.95 | 3. Giọng đang tải (+ thanh tiến trình 62% trên thẻ giọng) | ❌ | — | Chưa có. |
| 3.96 | 4. Văn bản quá dài phải cắt (+ nút *Xem chỗ cắt*) | ❌ | — | Chưa có. |
| 3.97 | 5. Âm thanh cũ sau khi sửa văn bản (+ nút *Nghe lại 3 đoạn*) | ❌ | — | Chưa có. |
| 3.98 | 6. Đang tạo âm thanh (không có dải, chỉ vòng xoay + thanh phát chờ) | ❌ | — | Chưa có. |
| 3.99 | 7. Bình thường | ✅ | — | Mặc định. |
| 3.100 | Mỗi tình huống khoá đúng nút Nghe/Xuất + đổi thẻ giọng + đổi thanh trạng thái | ❌ | — | Chưa có. |

---

## 4. Màn hình 2 — Soát văn bản

| # | Mục đặc tả | Trạng thái | File / vị trí | Ghi chú |
|---|---|---|---|---|
| 4.1 | Là **chế độ phủ** lên màn chính, cột trái/phải mờ đi (opacity .55) | ⚠️ | `index.html:291-318`, `app.js:872` | Là một view **thay thế** hoàn toàn, không phủ. |
| 4.2 | Thanh công cụ riêng 42px có **hai tab** | ❌ | `index.html:310-313` | Chỉ có tiêu đề *Kết quả soát* + dòng phụ. |
| 4.3 | Tab 1 — Chỗ cần chú ý: vùng văn bản có gạch chân lượn sóng + nhãn loại ở lề phải | ❌ | `app.js:630-676` | Chỉ có danh sách phẳng, không hiển thị văn bản. |
| 4.4 | Bảng *Kết quả soát* 302px: 3 chip lọc + 2 nút + 5 cột (Đoạn/Loại/Nội dung/Đề xuất/Hành động) | ❌ | `app.js:660-676` | Danh sách hiện chỉ có mức + tiêu đề + chi tiết + nút nhảy tới dòng. |
| 4.5 | Tab 2 — Văn bản sau chuẩn hoá | ⚠️ | `app.js:1134-1179` | Tồn tại nhưng là **modal riêng** `moXemTruoc()` mở từ thanh công cụ màn chính. |
| 4.6 | Tab 2: 4 chip quy tắc bật/tắt (Số thành chữ 48 · Viết tắt 6 · Ngày tháng 3 · Bỏ dấu câu lặp 0) | ❌ | — | Chưa có. |
| 4.7 | Tab 2: bảng 2 cột GỐC / MÁY SẼ ĐỌC THÀNH, phần đổi tô nền `mark` bo 3px đậm 600 | ⚠️ | `app.js:1145-1179`, `highlightKhac()` | Có so sánh và tô khác biệt — cần đối chiếu bố cục 2 cột + số đoạn cột 52px. |
| 4.8 | Tab 2 chân: chú thích + **Nghe thử đoạn đang chọn** · **Thêm vào từ điển phát âm** | ❌ | — | Chưa có. |

---

## 5. Khung chung của các màn phụ

| # | Mục đặc tả | Trạng thái | File / vị trí | Ghi chú |
|---|---|---|---|---|
| 5.1 | Thanh tiêu đề 32px: logo + tên màn + `— GiongDoc` + chip **‹ Màn hình chính** | ❌ | `index.html:48-59` | Thanh tiêu đề dùng chung, chỉ in *GiongDoc* hoặc tên tệp. Không có chip quay lại. |
| 5.2 | Nút quay lại nằm ở **thanh tiêu đề** | ⚠️ | `index.html:257,296,326,367` | Đang là nút icon `‹` nằm trong **đầu cột trái** của từng màn. |
| 5.3 | Cột trái 240px + thẻ phải `layer`/`stroke`/bo 8px | ✅ | `index.html:255-266` v.v. | Đúng bố cục. |
| 5.4 | Mục đang chọn cột trái: nền `layer`, viền, đậm 600, vạch dọc 3×18px `acc` | ⚠️ | `app.css` `.mode.is-active` | Dùng chung kiểu với hồ sơ, cần đối chiếu kích thước vạch. |
| 5.5 | Đáy cột trái có một dòng thông tin phụ 13px `txt3` | ✅ | `index.html:264,338,374` | Có. |

---

## 6. Màn hình 3 — Xuất file âm thanh (3 giai đoạn)

| # | Mục đặc tả | Trạng thái | File / vị trí | Ghi chú |
|---|---|---|---|---|
| 6.1 | **Ba giai đoạn trong CÙNG một hộp 600px** | ⚠️ | `app.js:1180,1249,1271` | Ba modal rời (`dialog--md`, `dialog--sm`, `dialog--sm`) thay nhau. |
| 6.2 | GĐ1 có thêm **Khoảng lặng giữa các đoạn** (thanh trượt) | ❌ | — | Chưa có. |
| 6.3 | GĐ1: dòng ước tính đổi theo lựa chọn tách tệp, 3 câu mẫu | ⚠️ | `app.js:1216,1236`, `cau_noi.py:541` | Có cơ chế đổi; cần đối chiếu đúng 3 câu. |
| 6.4 | GĐ2: vòng xoay 16px + tiêu đề + thanh 5px + 3 dòng số liệu (*Đã trôi qua* / *Còn lại* / **Đã ghi**) | ⚠️ | `app.js:1249-1269` | Có 2 dòng, **thiếu *Đã ghi***. Thiếu danh sách đoạn đang xử lý dạng vạch mờ. |
| 6.5 | GĐ3: thẻ tóm tắt + đường dẫn `word-break: break-all` + 3 nút (**Mở thư mục** · **Xuất tiếp bản khác** · **Đóng**) | ⚠️ | `app.js:1271-1296` | Có thẻ tóm tắt và đường dẫn. **Thiếu nút *Xuất tiếp bản khác***. |

---

## 7. Màn hình 4 — Thư viện giọng

| # | Mục đặc tả | Trạng thái | File / vị trí | Ghi chú |
|---|---|---|---|---|
| 7.1 | Cột trái 4 bộ lọc có số đếm: Tất cả 8 · Có sẵn 6 · Của tôi 2 · Đang tải về — | ⚠️ | `app.js:907-908,965-971` | Có 3 nhóm (Tất cả / Có sẵn / Của tôi). **Thiếu *Đang tải về***. Cần kiểm số đếm. |
| 7.2 | Đáy cột: *Đã dùng 6,4 GB… / Còn trống 128 GB.* | ⚠️ | `thu_vien_giong.py:118-121` | Có nhưng gộp thành một câu dài, khác cách trình bày 2 dòng. |
| 7.3 | Đầu thẻ 56px: ô tìm 300px + lọc Giới tính + lọc Vùng + nút accent **Nhân bản giọng mới** | ✅ | `index.html:269-281` | Đúng. (Nhãn đang là *Miền*, đặc tả ghi *Vùng*.) |
| 7.4 | Hai nhóm `GIỌNG CỦA TÔI` rồi `GIỌNG CÓ SẴN` | ✅ | `app.js:958-1001` | |
| 7.5 | Thẻ giọng 270px: vòng tròn 34px + tên 15px/600 + chip **Đang dùng** + dòng phụ + **dải sóng âm 26 vạch** + 3 nút | ⚠️ | `app.js:924-957`, `thu_vien_giong.py:33-62` | Có dải sóng âm nhưng **chỉ cho giọng riêng** (đọc từ file mẫu); giọng có sẵn `song: []`. Cần kiểm số vạch = 26 và bộ 3 nút. |
| 7.6 | 6 giọng có sẵn theo danh sách (Bình An, Ngọc Linh, Xuân Vĩnh, Minh Quân, Hải Yến, Thiện Tâm) kèm giới tính · vùng · tính chất · dung lượng | ❌ | `thu_vien_giong.py:110-111` | Giọng có sẵn lấy từ VieNeu (`Phạm Tuyên`…), dòng phụ cứng *"Giọng dựng sẵn trong mô hình"*. |
| 7.7 | Ô nét đứt 270px cuối nhóm *Giọng của tôi* | ❌ | — | Chưa có. |
| 7.8 | Chân thẻ 44px: `8 giọng · 2 giọng của tôi` \| `Giọng đang dùng cho hồ sơ "…": **…**` | ⚠️ | `app.js:1006-1013` | Có chân thẻ, cần đối chiếu chữ. |

---

## 8. Màn hình 5 — Từ điển phát âm

| # | Mục đặc tả | Trạng thái | File / vị trí | Ghi chú |
|---|---|---|---|---|
| 8.1 | Cột trái = **phạm vi** có số đếm (Tất cả 34 · Mọi hồ sơ 12 · từng hồ sơ…) | ❌ | `index.html:331-336` | Cột trái chỉ có một đoạn chữ giải thích. Từ điển hiện **dùng chung cho mọi hồ sơ**, không có phạm vi. |
| 8.2 | Đầu thẻ: ô tìm 280px + **Nhập từ tệp CSV** + **Thêm từ** | ⚠️ | `index.html:343-349` | Có ô tìm + nút *Thêm chữ*. **Thiếu Nhập CSV**; nhãn nút khác (*Thêm chữ* vs *Thêm từ*). |
| 8.3 | **Khung thêm từ** mở ra ngay trong trang, nền `acc-soft`, 6 ô/nút | ⚠️ | `app.js:714-786` | Đang là **hộp thoại modal**, không phải khung mở ra đóng được. Thiếu ô *Phạm vi* và nút *Nghe thử*. |
| 8.4 | Bảng **5 cột**: Từ (250px) · Đọc thành · Phạm vi (170px) · Lần dùng (120px) · Hành động (130px) | ⚠️ | `index.html:350-354`, `app.js:699-713` | Chỉ **3 cột**: Chữ · Máy sẽ đọc thành · Hành động. Thiếu *Phạm vi*, *Lần dùng*. |
| 8.5 | Hàng 42px, từ gốc 15px `txt`, cách đọc `txt2`, chip phạm vi | ⚠️ | `app.css` `.td__*` | Cần đối chiếu kích thước. |

---

## 9. Màn hình 6 — Cài đặt

| # | Mục đặc tả | Trạng thái | File / vị trí | Ghi chú |
|---|---|---|---|---|
| 9.1 | **6 nhóm**: Chung · Giọng & mô hình · Xuất file · Phím tắt · Bộ nhớ · Về GiongDoc | ⚠️ | `cai_dat.py:74-160` | Hiện **4 nhóm**: Chung · Cách đọc · Tệp · Máy và phiên bản. |
| 9.2 | Mỗi nhóm cột trái có tên **+ một dòng mô tả** | ✅ | `cai_dat.py` khoá `moTa`, `app.js:797-805` | |
| 9.3 | Đáy cột trái: `GiongDoc 1.4.2` / `Bản quyền đã kích hoạt` | ❌ | `index.html:374` | Hiện là *"Thay đổi được lưu ngay."* |
| 9.4 | Bốn kiểu điều khiển: `toggle` · `select` · `path` · **`meter`** | ⚠️ | `cai_dat.py:55-68`, `app.js:824-863` | Có `cong_tac` (toggle), `chon` (select), `duong_dan` (path), `chu` (text). **Thiếu `meter`** (thanh dung lượng). |
| 9.5 | Nội dung mẫu (Tăng tốc GPU, Tải mô hình sẵn, Giải phóng mô hình, Cảnh báo RAM…) | ❌ | `cai_dat.py:74-160` | Nội dung hiện khác hoàn toàn. |

---

## 10. Phím tắt

| # | Mục đặc tả | Trạng thái | File / vị trí | Ghi chú |
|---|---|---|---|---|
| 10.1 | Dán = `Ctrl+V` ở **mọi chỗ** | ⚠️ | `app.js:74,1806`, `index.html:71` | Đang là `Ctrl+Shift+V` ở cả 3 chỗ. |
| 10.2 | Đủ 16 phím tắt trong đặc tả | ⚠️ | `app.js:1785-1819` | Có `Ctrl+O/E/G/D/.` `Space` `F1` cỡ chữ. **Thiếu**: `Ctrl+S` `Ctrl+T` `Ctrl+W` `Ctrl+H` `Ctrl+K` `Ctrl+B` `Ctrl+M` `Ctrl+/` `Alt+1…3`. **Thừa**: `Ctrl+P` `Ctrl+D` `Ctrl+0` `F5` `Ctrl+←/→`. |
| 10.3 | `Ctrl+K` = soát văn bản (đặc tả) | ⚠️ | `app.js:88,1811` | Hiện `Ctrl+K` = nghe thử giọng. Đặc tả cho nghe mẫu là `Ctrl+M`. |

---

## 11. Mục đặc tả bảng lần đầu BỎ SÓT (bổ sung sau audit)

| # | Mục đặc tả | Trạng thái | File / vị trí | Ghi chú |
|---|---|---|---|---|
| 11.1 | Đọc tệp **`.docx`** | ❌ | `cau_noi.py:379-380` | `file_types=("*.txt;*.md;*.csv")`, đọc bằng `read_text()`. `.docx` là ZIP+XML → ra rác. **2/5 tài liệu mẫu là `.docx`** (`bai-viet-nghe-lai.docx`, `chuong-01.docx`). Không có `python-docx` trong dự án (grep toàn `.py` = 0 kết quả). |
| 11.2 | Đọc tệp **`.rtf`** | ❌ | như trên | Copy trạng thái rỗng hứa `.txt, .docx, .rtf`. |
| 11.3 | **Kéo thả tệp vào cửa sổ** | ❌ | `ui/app.js` | Grep `drop`/`dragover`/`DataTransfer` = 0 (các kết quả đều là `dropdown`). Copy trạng thái rỗng hứa *"kéo thả tệp… vào cửa sổ này"*. Rủi ro riêng: pywebview + WebView2 kéo thả tệp cần bật riêng, **chưa kiểm chứng được** trên bản `.exe`. |
| 11.4 | Chuyển động: đổi nền 0.15–0.2s · vòng xoay 0.8s · chấm nhấp nháy 1.2s · con trỏ nháy 1.1s step-end · **không hiệu ứng nảy** | ⚠️ | `app.css:112-114` | Có `spin`, `pulse`, `toastin`. Thiếu con trỏ nháy 1.1s (chưa có "đoạn đang chọn"). Cần rà thời lượng từng cái. |
| 11.5 | Bậc khoảng cách 2·4·6·8·12·14·16·24px | ⚠️ | rải rác | Chưa hệ thống hoá thành biến; nhiều chỗ dùng 3px, 11px, 13px, 18px, 20px, 22px ngoài bậc. |
| 11.6 | Thanh tiêu đề: logo **16px bo 3px** nền accent; nút cửa sổ **46×32px** | ⚠️ | `index.html:50`, `app.css` `.brandmark`/`.winbtn` | Có `.brandmark` + 3 `.winbtn`; **chưa đo** đúng 16/3/46/32. |
| 11.7 | 6 quy tắc **chuyển trạng thái** (bấm số đoạn / Nghe toàn bộ / tạm dừng / đổi hồ sơ / xuất / mở menu) | ❌ | `app.js:1352` `capNhat()` | Trạng thái do Python đẩy sang, không có bảng chuyển trạng thái ở giao diện. Toàn bộ 6 quy tắc chưa có. |
| 11.8 | Dữ liệu mock: **5 tài liệu · 4 hồ sơ · 5 giọng** (dropdown) | ❌ | — | Chưa có lớp dữ liệu mock nào. |
| 11.9 | Thư viện giọng: **8 thẻ** (6 có sẵn + 2 của tôi) | ❌ | — | **Đặc tả tự vênh:** `PROMPT.md:97` ghi *"5 giọng"*, `README.md:220` dropdown liệt kê 5, `README.md:354` + nghiệm thu ghi **8**. Hiểu đúng: dropdown 5, thư viện 8 — cần anh xác nhận. |
| 11.10 | 7 ví dụ chuẩn hoá ở màn 2 giữ nguyên từng chữ | ⚠️ | `DocCongDuc.py:1251` | **Đã đo bằng engine thật** (`load_tudien` 43 mục): chỉ **2/7 khớp**. Bảng đo ở §Đính chính. |
| 11.11 | Nguyên tắc viết lỗi: nói việc đã xảy ra → trấn an dữ liệu còn nguyên → nói việc cần làm; không mã lỗi, không thuật ngữ | ⚠️ | `app.js:1122-1132`, `cau_noi.py:864` | Có khung báo lỗi; nội dung hiện chưa theo khuôn này. |
| 11.12 | **Điều phối phát tiếng** — đặc tả mới có ~12 loại điểm vào phát tiếng | ⚠️ | `cau_noi.py:463-489` | Xem §Đính chính, mục *Họ lỗi chồng tiếng*. |
| 11.13 | Giao diện mới phải vào được bản đóng gói | ⚠️ | `DongGoi.bat:103,124` | `--add-data "%ROOT%ui;ui"` + chốt kiểm `_internal\ui\index.html`. Thêm thư mục giao diện mới **phải sửa cả hai chỗ**. |

---

## Đính chính và phát hiện thêm (audit 2026-08-12)

### Đ1. Số liệu tổng sai
Bản đầu ghi *118 mục — ✅22 ⚠️41 ❌55*. Đếm thật: **167 — 18 / 90 / 57**. Đó là ước chứ không đếm — đúng lỗi
*"đo, đừng đoán"*. Lệnh đếm lại:
```
awk -F'|' '/^\| [0-9]/ {n++; c[$4]++} END {print n; for(k in c) print k, c[k]}' doi-chieu.md
```

### Đ2. Bốn mục kết luận khi chưa đo — đã đo lại
| Mục | Bản đầu | Sau khi đo | Kết quả |
|---|---|---|---|
| 3.31 / 5.4 vạch dọc `acc` | ⚠️ *"cần đối chiếu"* | `app.css:400-410` khớp từng con số | **Sửa thành ✅** |
| 1.10 tiêu đề đoạn | ⚠️ *"cần kiểm lại cỡ"* | `app.css:665` không đặt `font-size`, đậm 600 | Giữ ⚠️, đã có số |
| 3.24 tab tệp | ⚠️ *"cần đối chiếu"* | `max-width:260px` vs đặc tả 230px | Giữ ⚠️, đã có số |
| 3.85 dòng phụ hộp xuất | ⚠️ *"cần đối chiếu chữ"* | `cau_noi.py:550` dùng chữ *"dòng"* | Giữ ⚠️, đã có số |

### Đ3. Chuẩn hoá văn bản — đo bằng engine thật, 2/7 khớp
Chạy `DocCongDuc.chuan_hoa_van_ban(goc, load_tudien(TUDIEN_FILE), cfg)` — **chạy từ source, chưa chạy trên `.exe`**:

| Gốc | Đặc tả (README:294-301) | Engine hiện tại | |
|---|---|---|---|
| `2/9` | hai phần chín | `ngày 2 tháng 9` | ❌ |
| `TNHH` | trách nhiệm hữu hạn | `trách nhiệm hữu hạn` | ✅ |
| `UBND TP.HCM` | Uỷ ban nhân dân Thành phố Hồ Chí Minh | `Ủy ban nhân dân Thành phố Hồ Chí Minh` | ✅* |
| `31/8/2026` | ba mươi mốt tháng tám năm hai nghìn không trăm hai mươi sáu | `ngày 31 tháng 8 năm hai nghìn không trăm hai mươi sáu` | ❌ |
| `17h00` | mười bảy hắt không không | `17h00` (không đổi) | ❌ |
| `1900 6868` | một chín không không sáu tám sáu tám | `một nghìn chín trăm sáu nghìn tám trăm sáu mươi tám` | ❌ |
| `TM. BAN GIÁM ĐỐC` | Tê mờ ban giám đốc | `TM. BAN GIÁM ĐỐC` (không đổi) | ❌ |

\* khác chính tả `Uỷ` / `Ủy` — đặc tả nói *"giữ nguyên từng chữ"*, cần chốt lấy bên nào.

**Lần đo đầu tôi sai phương pháp**: truyền từ điển rỗng `{}` nên `TNHH` và `UBND` báo không đổi. Đo lại với
`load_tudien(TUDIEN_FILE)` (43 mục) mới ra bảng trên. Ghi lại để không ai lặp lại.

**Ý nghĩa:** giai đoạn mock chỉ cần in đúng chữ trong README. Nhưng lúc nối engine thật, tab 2 màn Soát sẽ
đổi nội dung ở 5/7 ví dụ — người dùng sẽ tưởng bị hỏng. Riêng `2/9` → *hai phần chín* trong tệp mẫu
`thongbao-quoc-khanh.txt` **là ví dụ máy đọc SAI**, không phải kết quả mong muốn; engine hiện đọc đúng hơn.

### Đ4. Họ lỗi "chồng tiếng" — ĐÍNH CHÍNH: đã có sẵn bộ điều phối, tôi kết luận sai

> **Sai của tôi (sửa 2026-08-12).** Mục này ban đầu viết *"dàn xếp hiện tại là đôi một, thủ công"*
> và đề xuất dựng `giaodien/am_thanh.py` làm bộ điều phối duy nhất. **Thứ đó đã có rồi.**
>
> `DocCongDuc.py` `class Speaker` có `_khoa_loa` (Lock) + `_dang_giu_loa`. `Speaker.play()` mở đầu
> bằng `_gianh_loa()` — chiếm khoá và **giết nguồn đang giữ**; sau khi sinh tiến trình `ffplay` còn
> **kiểm lại quyền một lần nữa** rồi mới cho phát, để bịt khe hở vài chục mili giây lúc dựng tiến
> trình; và trả về theo *"tôi còn giữ loa không"* chứ không theo cờ dừng. Chính chú thích trong
> code đã nói rõ: *"Mọi tiếng động của chương trình đều chui qua play() […] kể cả nguồn viết thêm
> sau này quên đi dừng nguồn đang chạy."*
>
> Nghĩa là thêm bao nhiêu nút phát cũng an toàn, miễn là đi qua `Speaker.play()`. Rủi ro tôi báo
> động là **không có**. Bỏ mục *Việc cần anh quyết #9* — không có việc gì để quyết.
>
> Bài học: tôi đã đọc chú thích ở `cau_noi.py:474-486` nói thẳng rằng *"Speaker.play() còn một chốt
> nữa chặn đúng chuyện này, nhưng ĐỪNG bỏ hàm này đi vì thấy trùng"* — đọc rồi vẫn kết luận ngược.
> Đọc chú thích chưa phải là đọc code.

Phần dưới đây giữ lại vì phần **đếm điểm vào** vẫn đúng và vẫn hữu ích:

Dàn xếp ở tầng `cau_noi` là **đôi một, thủ công**: `cau_noi.py:468` `_nghe_thu()` gọi
`self._bo_doc.tam_dung()`; `cau_noi.py:493` `phat()` gọi `_nhuong_duong_phat()` →
`self._bo_nghe_thu.dung()`. Nhưng đó chỉ là lớp **huỷ sớm cho đỡ tốn CPU**, không phải lớp bảo đảm.

Đặc tả mới có **12 loại điểm vào phát tiếng** (đếm từ README):

| Nhóm | Điểm vào | Dòng README |
|---|---|---|
| Đọc nội dung | bấm số đoạn · Nghe toàn bộ · `Space` · *Nghe lại 3 đoạn* (dải cảnh báo) · nút *Nghe* trong bảng Kết quả soát · *Nghe thử đoạn đang chọn* (màn 2 tab 2) | 193 · 156 · 434 · 263 · 287 · 303 |
| Nghe mẫu giọng | nút loa cột phải · **nút tam giác trên từng dòng dropdown** (5 nút) · `Ctrl+M` · **nút *Nghe thử* trên từng thẻ giọng** (8 nút) · *Nghe thử* trong khung thêm từ điển | 219 · 220 · 139 · 348 · 367 |
| Xuất | Bắt đầu xuất | 252 |

Tức khoảng **28 nút cụ thể** thay vì 4 như hiện nay. Giữ cách dàn xếp đôi một thì mỗi nút mới phải nhớ gọi
tay sang tất cả nguồn còn lại — chắc chắn sót, và sót là chồng tiếng.

Hai điểm vào là **nguồn phát mới thật sự** (đọc một từ / một đoạn với từ điển tạm), thuộc việc hội đồng theo
`CLAUDE.md` §3: *Nghe thử* trong khung thêm từ điển (màn 5) và *Nghe thử đoạn đang chọn* (màn 2 tab 2).

### Đ5. Bản mẫu HTML cần Internet
`designs/support.js:1143-1147` nạp React 18.3.1, ReactDOM và Babel standalone từ `unpkg.com`.
Mất mạng → mở bản mẫu ra trang trắng. Thư mục `_ds/` chỉ chứa font Inter, không chứa React.
Cần biết trước khi anh mở bản mẫu để bấm thử.

### Đ6. Báo động hụt — hidden-import (đã đo, KHÔNG phải lỗi)
`DongGoi.bat:106-110` liệt kê `--hidden-import` cho 10 module `giaodien.*`, **thiếu** `cai_dat`, `ho_so`,
`soat`, `tu_dien`. Nhìn thì giống họ lỗi *"thiếu `--collect-data` → danh sách giọng rỗng"*.

**Đo lại thì không phải lỗi:** `cau_noi.py:16` dùng `from . import (cai_dat, ..., ho_so, ..., soat, tu_dien)`
tĩnh ở đầu tệp nên PyInstaller tự tìm ra. Kiểm bằng cách tìm chuỗi trong `GiongDoc.exe`: cả 4 module **đều có mặt**.

Vẫn là nợ vệ sinh: danh sách hidden-import là lưới an toàn cho module nạp động, mà nó đã lạc hậu 4 module.
Module mới nào nạp trong thân hàm hoặc qua `importlib` sẽ rơi thẳng vào bẫy này.

### Đ7. Bản đóng gói đang khớp source (đã đo)
`md5sum` `ui/index.html · app.css · app.js` **khớp hoàn toàn** với `_internal/ui/*`.
Ba tệp mấu chốt đều có: `_internal\ui\index.html` (22.200 B) · `_internal\sea_g2p\sea_g2p.bin` (62.829.820 B) ·
`_internal\vieneu\assets\voices_v3_turbo.json` (235.683 B). Không có `GiongDoc-loi.log` → chưa ghi nhận lỗi lần chạy gần nhất.
Nghĩa là **mốc so sánh hiện tại là một bản `.exe` sạch** — mọi hồi quy sau này quy được về thay đổi của mình.

---

## Việc cần anh quyết trước khi tôi động vào code

**1. Tốc độ / Cao độ / Âm lượng — mâu thuẫn với engine.**
Đặc tả §Cột phải yêu cầu 3 thanh trượt Tốc độ (−50…+100%), Cao độ (−12…+12), Âm lượng (0…100%).
`CLAUDE.md` §5 ghi rõ: *"VieNeu **không có** tham số tốc độ và cao độ. Thứ chỉnh được là các khoảng nghỉ."*
Dựng UI mock thì được, nhưng khi nối thật, 2/3 thanh trượt sẽ là **nút giả** — vi phạm CORE KPI của dự án.
Ba lối đi: (a) dựng đủ 3 rồi xử lý Tốc độ bằng cách co giãn khoảng nghỉ, Cao độ báo *"giọng này không chỉnh được cao độ"*; (b) chỉ dựng Tốc độ + Âm lượng; (c) dựng đủ 3, chấp nhận mock, ghi nợ. **Tôi nghiêng về (a).**

**2. Di sản "danh sách công đức" — gỡ tới đâu?**
Đặc tả mới không có cột số tiền, không có lời dẫn đầu/cuối, không có *Nhấn mạnh dòng có số lớn*, không có phân loại hồ sơ `congduc`/`vanban`.
Nhưng engine `DocCongDuc.py` và `noidung.ini` · `congduc.txt` đang phục vụ đúng những thứ đó, và **anh đang dùng thật** (`hoso.json` có hồ sơ *Danh sách công đức* với nhịp đã chỉnh tay).
Gỡ khỏi giao diện = mất tính năng đang chạy. Đây là **việc hội đồng** (đụng engine + dữ liệu người dùng). Anh muốn: (a) giữ engine, chỉ đổi giao diện, đọc danh sách vẫn chạy nền; (b) gỡ hẳn; (c) để lại sau, giai đoạn này chỉ dựng giao diện mock.

**3. Dữ liệu người dùng khi đổi mô hình hồ sơ.**
Mô hình mới (hồ sơ có danh sách tab) không tương thích `hoso.json` hiện tại. `cauhinh.ini`, `noidung.ini`, `congduc.txt`, `giong_rieng/` đều thuộc diện hội đồng.
Đề xuất: giai đoạn dựng giao diện dùng **file dữ liệu riêng** (`hoso-v2.json`), không đụng file cũ; khi nào chốt mới viết bước di trú.

**4. Dựng tại chỗ hay dựng song song?**
`ui/app.js` 80KB / `app.css` 50KB đang chạy được và đã đóng gói thành `.exe`. Thay đổi theo đặc tả mới là viết lại phần lớn.
Đề xuất: dựng bộ mới song song (`ui2/`), bật bằng biến môi trường, chỉ đổi `GiongDoc.py` trỏ sang khi anh duyệt xong. `DongGoi.bat` phải thêm `ui2` — **đụng đường đóng gói, cần anh duyệt**.

**5. Nền tảng.**
Dự án đã có nền tảng (pywebview + WebView2 + HTML/CSS/JS thuần). Tôi **không** đề xuất đổi sang WinUI 3 hay Electron — đổi là phá `DongGoi.bat`, `--collect-data vieneu`, `--collect-data sea_g2p` và toàn bộ chuỗi đóng gói đã mất nhiều vòng mới chạy được. Xác nhận giúp tôi giữ nguyên.

**6. Xác nhận bỏ thanh tua.**
`#seek` hiện **chạy thật** (bấm để nhảy tới vị trí, `cau_noi.py:514`). Đặc tả cấm. Bỏ đi là mất một cách điều hướng anh có thể đang dùng. Xác nhận giúp.

**7. Năm chỗ đặc tả tự vênh** (tôi sẽ theo bản mẫu HTML nếu anh không chỉ định khác):
- `Ctrl+T` (tệp mới) có trong danh sách phím tắt nhưng không có trong menu Tệp.
- `Ctrl+K` (soát văn bản) có trong danh sách phím tắt nhưng menu không ghi phím tắt cho *Soát văn bản*.
- Màn 4 nhãn bộ lọc: đặc tả ghi *Vùng*, dòng phụ thẻ giọng ghi *miền Nam / miền Bắc*.
- Số giọng: `PROMPT.md:97` ghi *"5 giọng"*, `README.md:354` + nghiệm thu ghi **8 thẻ**. Hiểu của tôi: dropdown 5, thư viện 8.
- `Uỷ ban` (README:297) vs `Ủy ban` (engine + `tudien.ini`) — đặc tả nói giữ nguyên từng chữ.

**8. Đọc `.docx` / `.rtf` và kéo thả tệp** *(bổ sung sau audit — bảng đầu bỏ sót)*
2/5 tài liệu mẫu là `.docx`, và copy trạng thái rỗng hứa *"kéo thả tệp .txt, .docx, .rtf vào cửa sổ này"*.
Dự án hiện **không đọc được `.docx` lẫn `.rtf`** (`cau_noi.py:379` chỉ nhận `.txt;.md;.csv`, đọc bằng `read_text()`),
và **không có kéo thả**. Thêm `python-docx` là thêm phụ thuộc vào bản đóng gói (`--hidden-import`, dung lượng) — việc hội đồng.
Ba lối: (a) mock giai đoạn này, ghi nợ; (b) làm `.docx` bằng `python-docx`, `.rtf` bỏ; (c) đổi copy trạng thái rỗng cho khớp thứ đọc được.

**9. Điều phối phát tiếng** *(bổ sung sau audit — quan trọng nhất về mặt ổn định)*
Xem §Đ4: từ 4 nút phát lên ~28 nút, dàn xếp đôi một hiện tại sẽ vỡ. Đề xuất dựng **một bộ điều phối duy nhất**
(`giaodien/am_thanh.py`): mọi nguồn muốn kêu phải xin quyền, bộ điều phối tăng số phiên toàn cục và dừng nguồn đang giữ.
Không nguồn nào tự gọi sang nguồn khác nữa. Đây là *sửa cả họ* thay vì vá lẻ — nhưng đụng `bo_doc`/`nghe_thu`/`xuat_file`, cần anh duyệt.

**10. Chuẩn hoá văn bản lệch 5/7 so với đặc tả** *(bổ sung sau audit)*
Xem §Đ3. Giai đoạn mock in đúng chữ README là xong; nhưng phải chốt trước: khi nối engine thật, tab 2 màn Soát
hiển thị **kết quả engine thật** (đúng nhưng khác đặc tả) hay **ép engine chạy theo đặc tả** (5 chỗ phải sửa engine = việc hội đồng)?
