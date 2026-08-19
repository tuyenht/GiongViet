# Kế hoạch xử lý 233 điểm lệch

---

## TRẠNG THÁI KHI ĐÓNG PHIÊN — 19/8/2026

### Chủ dự án đã chốt bốn câu

| Câu | Chốt |
|---|---|
| 1.1 Dải thẻ tệp ngang | **Làm cả hai cùng lượt** — dựng cây tệp trong cột trái RỒI bỏ dải tab, gộp luôn sửa lỗi L4 |
| 1.2 Màn Văn bản ghép | **v2 đầy đủ** *(khác khuyến nghị "v2 rút gọn" — theo quyết định chủ dự án)* |
| 1.3 Khung màn phụ | **Tất cả màn phụ toàn cửa sổ** — và đo lại thì chốt này **bám thiết kế hơn** khuyến nghị cũ |
| 1.4 `DongGoi.bat` | **Để sau**, chưa build nên chưa gấp |
| `--warn` bộ Tối | Không cần quyết — code đúng, chỉ cần sửa 2 tệp thiết kế |

**Ngoại lệ đã đo được của câu 1.3:** Soát văn bản **KHÔNG** phải màn phụ. Đếm nút
*"Quay lại màn hình chính"*: Thư viện giọng 3 · Cài đặt 2 · Từ điển 2 · Văn bản ghép 2 ·
**Màn hình chính 0 · Soát văn bản 0**. Tệp thiết kế của Soát tự nói *"Vẫn là cửa sổ chính
của Giọng Việt"*, nút của nó là *"Đóng bảng kết quả soát"*. Nên nó ở lại khung chính.

### Đã sửa xong — 5 lượt

| Lượt | Việc | Bằng chứng |
|---|---|---|
| 1 | Xuất dùng bản cũ (L2) · cảnh báo chưa lưu (L3) | bấm thật 7 kịch bản |
| 2 | Cả họ "hứa suông": neo menu (lệch +96px → **0**), menu thẻ, 5 phím tắt | gõ phím thật |
| 3 | Dựng lại 6 menu đúng thiết kế: **23 mục sống · 15 mục mờ kèm lý do · 9 gạch ngăn** | bấm mở từng menu |
| 4 | Tooltip màn chính **28/53 → 40/53**, nút khoá nói lý do | đếm bằng máy |
| 5 | Khung toàn cửa sổ cho Thư viện giọng · Từ điển · Cài đặt | 22 phép canh mới |

**Tệp đã đổi:** `ui-moi/giao-dien.js` · `ui-moi/man-hinh-chinh.css` · `ui-moi/hop-thoai.js` ·
`ui-moi/index.html` · `kiem/kiem-giao-dien.mjs`.

**Tệp mới:** 8 bài kiểm trong `kiem/` (7 bài chứng minh lỗi + `kiem_dong_goi_cuu_du_lieu.py`)
cộng 2 tệp `.mjs` phụ trợ.

**Chưa hề đụng:** `DocCongDuc.py` · `GiongViet.py` · `kho_cau_hinh.py` · `giaodien/` ·
`giaodien_moi/` · `DongGoi.bat`. Dữ liệu người dùng khớp md5 từ đầu tới cuối.

### Bộ kiểm — 14 bài

12 xanh. Hai bài đỏ **cố ý**, đừng "sửa" nhầm:
- `kiem_xuat_ban_cu.py` — bài CHỨNG MINH lỗi L2. Nó xanh khi lỗi còn, đỏ khi lỗi hết.
  Đỏ = đúng. Ngày nào rảnh thì đảo lại mệnh đề khẳng định cho nó thành bài canh hồi quy.
- `kiem_dong_goi_cuu_du_lieu.py` — đỏ để nhắc câu 1.4 chưa vá. **Đừng chạy `DongGoi.bat`**
  cho tới khi vá xong.

### Việc dở dang — chưa bắt đầu dòng nào

**Lượt 6 (kế tiếp): cây tệp trong cột trái + bỏ dải tab + sửa L4.** Đụng `veCotTrai`,
`veDaiTab`, `doiTab`/`dongTab`/`themTab` trong `trang-thai.js`, CSS `.daitab`/`.trai`, và
mô hình khoá tài liệu. Chi tiết yêu cầu ở mục 1.1 và README mục *"Danh sách tệp (trong cột
trái, không có dải tab)"* — README có bốn chi tiết bản mẫu không nói: nháy đúp đổi tên tệp,
*Thêm tệp* cao 28px, đóng tệp cuối còn lại một tệp rỗng *Văn bản mới 1*, và mỗi hồ sơ giữ
danh sách riêng.

**Lượt 7: Văn bản ghép v2 đầy đủ** — cần khung toàn cửa sổ (đã có từ lượt 5).

### Một rủi ro cần chủ dự án biết

Toàn bộ 5 lượt sửa **chưa commit**. `git status` có 5 tệp `M` và ~12 tệp `??`.
Mất phiên là mất dấu vết. Nên commit trước khi nghỉ.

---

*Lập 19/8/2026, sau vòng audit. Đi kèm `DOI-CHIEU.md` ở gốc dự án — tệp đó là **sổ ghi**,
tệp này là **thứ tự làm**.*

---

## 0. Chuẩn là gì — đã xác minh, không phải giả định

| | |
|---|---|
| **Chuẩn** | 7 tệp `.dc.html` trong dự án thiết kế trực tuyến `5c70b20f-0f8b-4da8-ad19-800b0fb6ae19` |
| **Bản chụp** | `design_handoff_giongdoc/designs/` — đã kéo lại bản trực tuyến qua MCP ngày 19/8 và so md5: **khớp từng byte cả bảy tệp** |
| **Bản đang chạy** | `ui-moi/` + `giaodien_moi/` + `giaodien/` — luôn là *đối tượng bị đối chiếu*, không bao giờ là chuẩn |
| **Phân xử khi lệch nhau** | `.dc.html` thắng `README.md`. Đã bắt được một chỗ README lạc hậu: `Ctrl+T` (tệp mới) — v2 đã bỏ, đừng làm |

Chi tiết cách kiểm nằm ở `DOI-CHIEU.md` phụ lục C.

---

## 1. Phải chốt trước khi động vào code

Không làm được nhóm nào cho tới khi ba câu này có câu trả lời.

### 1.1 Dải thẻ tệp ngang — bỏ hay giữ? *(chặn nhóm 4)*

Thiết kế v2 **bỏ hẳn** dải tab 36px, chuyển danh sách tệp thành cây lồng trong bảng hồ sơ
bên trái. `README.md` mục *"Danh sách tệp (trong cột trái, không có dải tab)"* nói y hệt —
**hai nguồn thống nhất, không mơ hồ**.

Code đang có dải tab (`veDaiTab`, `giao-dien.js:119-128`) và không có cây tệp.

Đây là hai việc dính nhau: **bỏ dải tab trước khi cây tệp chạy được là người dùng mất luôn
đường đổi tệp**. Ba lối:

- **(a) Làm cả hai cùng một lượt** — đúng thiết kế, chi phí LỚN, đụng `veDaiTab`, `veCotTrai`,
  `doiTab`/`dongTab`/`themTab` trong `trang-thai.js`, CSS `.daitab` và `.trai`. *Tôi nghiêng về
  cái này.*
- **(b) Dựng cây tệp trước, để dải tab lại vài vòng, bỏ sau khi cây chạy ổn** — an toàn hơn
  nhưng có lúc hai đường cùng tồn tại, dễ lệch nhau.
- **(c) Giữ dải tab, sửa thiết kế theo code** — nếu anh thấy dải tab ngang dễ dùng hơn cho
  người lớn tuổi. Nếu chọn cái này thì phải cập nhật cả `.dc.html` lẫn README, đừng để lửng.

### 1.2 Màn Văn bản ghép — làm bản nào? *(chặn nhóm 6)*

Khối lớn nhất còn thiếu: 45 dòng, 12 mục chặn, **cả màn chưa từng tồn tại trong code**.

Dự án thiết kế có **hai bản**. Đã đọc kỹ cả hai và đếm từng chuỗi:

| | v1 *(một mẫu công đức)* | v2 *(bản bàn giao)* |
|---|---|---|
| Cỡ | 726 dòng · 56.411 byte | 1.130 dòng · 90.108 byte |
| Markup | 393 dòng | 505 dòng (v1 = 78%) |
| Logic | 333 dòng | 625 dòng (v1 = 53%) |
| Khung, dải trái 240px, xem trước 392px, thanh dưới 46px, 28 biến CSS | **giống hệt** | **giống hệt** |
| Bảy mục điều hướng | có đủ | có đủ |

**v1 là tập con thật sự của v2** — không có nhánh riêng nào.

**Nhưng v1 chỉ rẻ hơn 20–25%, không phải một nửa.** Trong 45 dòng: bỏ hẳn được 7, làm nhẹ 8,
giữ nguyên 30. Trong **12 mục chặn thì v1 chỉ bỏ được 3**, tám mục còn nguyên.

**Ba việc tốn công nhất của cả màn thì v1 vẫn phải làm đủ** — đã đếm từng chuỗi, chúng có mặt
ở v1 y hệt v2: đăng nhập Google + chọn tệp trên Drive · đọc `.xlsx` (phải thêm `openpyxl`,
tức đụng đường đóng gói — **việc hội đồng**) · vòng đời dữ liệu cũ/mới có tự kiểm tra 5 phút
một lần. Ba lỗi đang sống (đọc sai `.csv`, lời dẫn bị xoá âm thầm, `so_nguoi_nhom` vô hình)
cũng phải sửa dù chọn bản nào.

**v1 làm người dùng tắc ở bốn chỗ**, đáng kể nhất là hai chỗ:
- Không có cột *Cách đọc* → số điện thoại, số báo danh, điểm trung bình bị đọc thành số
  lượng khổng lồ. **Lỗi nghe thấy được** — người lớn tuổi kết luận "máy đọc lung tung".
- Vai cột gắn cứng nghĩa công đức (*Tên · Số tiền · Ngày · Đợt*). Người làm lịch trực phải
  đặt "Người trực" là "Tên", "Ca" là "Cột thường" — chữ trên màn không khớp việc họ đang làm.
  Điều này **đi ngược thẳng câu định vị trong `CLAUDE.md`**: *"Danh sách công đức chỉ là MỘT
  khuôn mẫu có sẵn… Đừng thiết kế thứ gì gắn cứng vào riêng nó."*

**Một phát hiện làm đổi phép tính:** cột *Cách đọc* — thứ trông như phần đắt nhất của v2 —
thực ra **bảy trong tám nhánh đã có hàm chạy thật trong engine**: `format_money_for_reading`,
`_doi_ngay_thang`, `number_to_vietnamese`, `_ap_dung_tudien`, `normalize_name`, và cả một
module đọc số điện thoại từng chữ số (`giaodien_moi/so_dien_thoai.py`). Chỉ *Điểm, số thập
phân* là phải viết mới, cỡ mười dòng. Nó gần như chỉ là **nối dây**, bỏ đi không tiết kiệm
được mấy mà mất đúng cái làm máy đọc đúng.

#### Phương án tôi nghiêng về: **v2 rút gọn**

Lấy **mô hình dữ liệu đầy đủ của v2**, nhưng giao diện đợt đầu chỉ giao **một mẫu**:
hoãn thư viện mẫu, hộp thoại tạo mẫu, năm khuôn còn lại (chỉ giao khuôn *congduc*), lớp che
và phím tắt, hai mẫu sẵn khi cài mới.

Tiết kiệm gần bằng v1, nhưng **không mang nợ chuyển đổi dữ liệu**, **không gắn cứng vào công
đức**, và giữ được *Cách đọc*.

#### Nếu anh vẫn chọn v1 nguyên bản

Được, nhưng xin ba việc — cộng lại chưa tới một phần mười công của cả màn:

1. **Tên biến dùng `slug(tên cột)` cho mọi cột** theo luật v2, đừng dùng `{tien}` cố định của
   v1. Cùng một cột "Số tiền": v1 ra `{tien}`, v2 ra `{sotien}` — **làm v1 nguyên bản thì mọi
   mẫu câu người dùng đã gõ sẽ vỡ khi lên v2**. Đây là điểm va chạm dữ liệu người dùng duy nhất.
2. **Lưu vai cột dạng hai trục `{use, read}`** ngay từ đầu, dù giao diện chỉ bày một ô chọn.
3. **Chỗ lưu dạng danh sách theo id mẫu**, dù chỉ có một phần tử.

Không chốt ba điểm này trước khi viết dòng nào thì sau phải viết bộ chuyển đổi dữ liệu người
dùng — việc hội đồng.

### 1.3 Màn phụ chiếm toàn cửa sổ hay chỉ thay phần giữa? *(độc lập với 1.2)*

Cả v1 lẫn v2 của màn ghép đều đòi một màn **chiếm toàn cửa sổ**: thanh tiêu đề riêng, ba cột
trong đó cột phải 392px, thanh dưới 46px riêng. Trong khi **bốn màn phụ đang có đều chỉ thay
phần GIỮA** của màn chính — đây là quyết định đã ghi thành chú thích ở
`ui-moi/trang-thai.js:63-66`.

Chọn sai là dựng lại cả khung. Phải chốt trước, không liên quan tới chuyện v1 hay v2.

### 1.5 Đường đóng gói làm lùi thiết lập người dùng — *phát hiện mới 19/8, việc hội đồng*

Hội đồng chốt bước 1 là build `.exe` mới. Tôi đọc `DongGoi.bat` trước khi chạy và **dừng lại**.

Bộ build rất cẩn thận: dựng vào `_dist_moi`, kiểm đủ 3 tệp mấu chốt rồi mới hoán đổi, đổi tên
chứ không xoá, hỏng thì lùi được, và có hẳn vòng cứu dữ liệu (`DongGoi.bat:175-179`). Nhưng
bộ cứu chỉ bắt **ba kiểu tệp**:

```bat
for %%F in ("%CU%\*.json" "%CU%\*.ini" "%CU%\*.txt")
```

Không có `*.db`, và glob **không đi vào thư mục con**. Trong khi đó:

| Nguồn | Ngày | Khi build lại |
|---|---|---|
| `cauhinh.ini` gốc | 12/8 | được chép sang bản mới |
| `noidung.ini` · `tudien.ini` · `congduc.txt` gốc | 7/8 | được chép sang bản mới |
| `GiongViet/giongviet.db` | **15/8 10:31** | **bỏ lại `GiongViet_cu/`; build lần sau `rmdir /s /q` xoá sạch** |
| `GiongViet/sao-luu-cu/` | **15/8 12:18** | **cùng số phận — glob không đệ quy** |

Cơ chế (`DocCongDuc.py:86-100`): sau khi gom, **mọi lệnh ghi vào kho, không vào tệp `.ini` rời**.
Nên tệp rời đứng yên từ 7–12/8 trong khi thiết lập thật đã chạy tới 15/8.

**Hệ quả: build lại là thiết lập người dùng lặng lẽ lùi về mốc 7–12/8.** Build lần hai thì bản
15/8 mất hẳn.

Cùng họ với bảy lỗi trên — dữ liệu mất mà không một lời báo — nhưng nằm ở **đường đóng gói**,
tức việc hội đồng. Cách vá rẻ nhất: thêm `*.db` vào glob dòng 176 và cứu cả thư mục
`sao-luu-cu/`. Xin anh chốt trước khi tôi đụng vào `DongGoi.bat`.

**Cho tới khi chốt: không build `.exe`.** Đó là lý do vòng chứng minh vừa rồi chạy từ source
và trong thư mục tạm.

### 1.4 `--warn` bộ Tối — *câu này audit đã trả lời, chỉ cần anh gật*

Không phải chuyện chọn màu. `#f7b84b` trong hai tệp *Từ điển phát âm* và *Cài đặt* là
`--color-admin-warning` của bộ **BSSaaS AdminKit** — design system của **sản phẩm khác**
(nền tảng web SaaS Laravel của Bảo Sơn) đính kèm trong `_ds/`. Bốn tệp cập nhật gần nhất
đều dùng `#fce100`.

**Code đang dùng `#fce100`, tức code đúng.** Đề nghị: giữ code, anh sửa hai tệp thiết kế kia.

---

## 2. Thứ tự làm

Theo đúng luật anh đặt: **chặn → nặng → nhẹ**, trong mỗi mức theo thứ tự màn. Nhưng tôi
tách riêng nhóm 1 lên trước cả mức chặn, lý do nói ngay dưới đây.

### Nhóm 1 — Bảy lỗi ăn vào dữ liệu người dùng · **làm trước tiên**

Bảy dòng này **không phải lệch thiết kế** mà là lỗi của bản đang chạy, do lượt phản biện
tìm ra. Chúng không mang nhãn "chặn" vì người dùng vẫn bấm được — nhưng cái mất là **công
sức và dữ liệu của họ**, không phải sự tiện tay. Với người lớn tuổi, mất một buổi gõ mà
không có lời cảnh báo nào là thứ làm họ bỏ hẳn chương trình.

**Cập nhật 19/8 — đã qua HAI vòng: chứng minh, rồi phản biện.**

Vòng chứng minh cho 6 xác nhận · 1 đúng một phần. Nhưng vòng đó mắc lỗi thiết kế nhiệm vụ:
agent được giao *"hãy tái hiện lỗi X"* thì có động cơ tái hiện được. Nên đã chạy thêm một vòng
**phản biện** — nhiệm vụ là *bác bỏ*, mặc định nghiêng về bác bỏ, phải thử đủ ba hướng (có đường
khác đã tồn tại / là hành vi cố ý có ghi chú / cách diễn đạt quá rộng) rồi mới được đồng ý.

**Vòng phản biện: 2 giữ nguyên · 4 đúng một phần · 3 lỗi bị hạ mức.** Bảng dưới là bản sau cùng.

| | Việc | Mức đầu | **Mức sau phản biện** | Bài đo |
|---|---|---|---|---|
| 2 | Xuất file dùng bản cũ / thiếu đoạn | nặng | **nặng** *(giữ)* | `kiem_xuat_ban_cu.py` |
| 4 | Khoá theo tên tệp trần | nặng | **nặng** *(giữ, phạm vi RỘNG hơn)* | `kiem_khoa_ten_tep.py` |
| 3 | Không có cảnh báo chưa lưu | nặng | **nặng** *(viết lại, rẻ hơn nhiều)* | `kiem_luu_sua_doan.py` |
| 1 | Đọc sai `.csv` qua đường *Mở danh sách* | chặn | **nặng** *(phạm vi hẹp hơn)* | `kiem_doc_csv.py` |
| 5 | Nhân bản xong không nạp lại `GIONG` | nặng | **nhẹ** ↓ | `kiem_nap_lai_giong.py` |
| 6 | Mất đường sửa lời dẫn | nặng | **nhẹ** ↓ | `kiem_duong_sua_loi_dan.py` |
| 7 | `so_nguoi_nhom` vô hình | nặng | **nhẹ** ↓ | `kiem_so_nguoi_nhom.py` |

**Bốn chỗ mô tả cũ phải sửa:**

- **Lỗi 3 — sai như đã viết.** `luuVanBan()` (`giao-dien.js:1351`) lấy `doanDangXem(S, TAI_LIEU)`
  tức **chữ đã sửa**, gửi sang `moi_luu_van_ban` (`cau_noi_moi.py:696`) ghi thật ra đĩa; nối vào
  cả menu **Lưu** lẫn **Ctrl+S**. Vậy *"không bao giờ được ghi lại"* là sai. Câu đúng:
  **không có dấu hiệu "chưa lưu", `Đóng tệp` gọi thẳng `dongTab`, đóng cửa sổ gọi thẳng
  `api('thoat')`, không cái nào hỏi** (grep `beforeunload`/`chưa lưu`/`dirty` trong `ui-moi/`:
  0 kết quả). Vẫn nặng — người lớn tuổi không tự đoán ra Ctrl+S — nhưng **cách sửa nhỏ hơn hẳn**:
  một cờ bẩn cộng một hộp xác nhận, không phải dựng tầng lưu trữ.
- **Lỗi 1 — hẹp hơn, nhưng bẩn hơn.** Chỉ đường *"Mở danh sách tên và số…"* (mục menu, **không
  phím tắt, không nút thanh công cụ**) dùng `parse_data_file`. Mở đúng tệp `.csv` ấy bằng
  *"Mở tệp…"* / `Ctrl+O` — đường phổ biến hơn hẳn — thì đọc **gần đúng**
  (`"Nguyễn Văn An, năm trăm nghìn"`). Ngược lại, phần bẩn thì bẩn hơn mô tả cũ: máy không "đọc
  nguyên cục" mà **chèn thêm chữ không có trong tệp** — `_xu_ly_dau_phay`
  (`DocCongDuc.py:1226`) biến `"Nguyễn Văn An,500000"` thành `"Nguyễn Văn An **và** 500000"`,
  tệp ba cột thành `"1 và **ông** Nguyễn Văn An,500000"`. Riêng dấu chấm phẩy **có** khoảng
  trắng lại tách đúng — nên không phải mọi `.csv` đều hỏng.
- **Lỗi 4 — phạm vi RỘNG hơn câu cũ.** Không cần hai tệp trùng tên: `moi_dan_van_ban` trả tên
  **cố định** `"Văn bản đã dán"` (`cau_noi_moi.py:499`), nên **dán chữ hai lần là đã đè nhau** —
  mà dán chữ chính là việc *Hướng dẫn nhanh* bảo làm đầu tiên. Chuỗi tên làm khoá cho **năm** kho
  dùng chung toàn ứng dụng, không tách theo hồ sơ.
- **Lỗi 6 — hạ xuống nhẹ.** Bỏ hẳn cách nói *"sửa bằng Notepad bị ghi đè âm thầm"*:
  `sao-luu-cu/` là thư mục **đầu ra thuần**. Và vế "mất đường sửa **từ điển phát âm**" **sai** —
  giao diện mới có màn Từ điển riêng (`ui-moi/man-tudien.js`, vào từ cột phải và từ màn Soát),
  sửa được bình thường. Chỉ còn **lời dẫn của chế độ danh sách** bị ảnh hưởng, mà đó là một
  khuôn mẫu chứ không phải cốt lõi.

**Ba lỗi hạ xuống nhẹ, lý do:**

- **L5** là lỗi **nhãn**, không mất dữ liệu: giọng vừa tạo vẫn nằm trên đĩa, màn Thư viện giọng
  vẫn hiện đủ, bấm Nghe vẫn ra đúng tiếng; chỉ ô tên ở cột phải in rỗng **trong phiên đó**, mở
  lại chương trình là đúng.
- **L6** xem trên.
- **L7** đo được: `so_nguoi_nhom` đang đúng giá trị mặc định 20, chưa ai từng đổi, và chênh lệch
  đo trên danh sách 80 người chỉ **4,7–9,4 giây**. Chú thích `cau_noi_moi.py:812-814` nói rõ cố ý
  lọc bỏ thiết lập của chế độ danh sách — tức **con nợ đã ghi thành chữ**, không phải lỗi âm thầm.

> **Đọc bài đo cho đúng:** bảy bài này là **bài chứng minh**, không phải bài canh hồi quy —
> chúng báo XANH khi *lỗi còn nguyên*. Sửa xong thì chúng sẽ đỏ; lúc đó phải đảo lại mệnh đề
> khẳng định, đừng tưởng là hỏng thêm.

**Đụng tới:** `giao-dien.js` (`moHopXuat`, `batDauXuat`, `chuDangGo`, `phanCanLuu`, `datTaiLieu`,
`giongXong`), `DocCongDuc.py` (`parse_data_file`), `GiongViet.py` (`xuat_ra_tep` lúc thoát),
`kho_cau_hinh.py`.

**Cách tự kiểm:** mỗi lỗi có một phép thử chạy được — gõ sửa rồi xuất và mở tệp WAV nghe;
gõ sửa rồi tắt mở lại; mở hai tệp trùng tên khác thư mục; cho một `.csv` bốn dòng vào.
Bốn phép này nên thành bài đo trong `kiem/`.

> ⚠ Mục 1 và 7 nằm trong màn *Văn bản ghép*, nhưng **sửa được ngay mà không cần dựng cả màn** —
> chúng là lỗi của đường đọc danh sách hiện có.
> Mục 3, 4, 6 đụng **dữ liệu người dùng** → theo `CLAUDE.md` là việc thuộc hội đồng, tôi sẽ
> trình phương án trước khi làm.

### Nhóm 2 — Ba chỗ người dùng đang tắc thật *(mức chặn, màn chính)*

Cả ba đều là **dải cảnh báo**: `veCanhBao()` dựng nút bằng `<button class="nut">` không có
`data-lenh`, không có `id`, nên sáu nút *Thử lại · Xem chi tiết · Nâng gói · Dùng giọng khác ·
Xem chỗ cắt · Nghe lại 3 đoạn* bấm không có gì xảy ra. Nặng nhất là `Thử lại` khi mất kết nối:
tình huống đó nằm trong `KHOA_NGHE_VA_XUAT` nên Nghe và Xuất đều bị khoá, mà `S.situation`
không có đường nào về `binh_thuong` — **vào rồi không ra được**.

**Đụng tới:** `giao-dien.js:164-179` (`veCanhBao`), bộ bắt click `:1362-1567`, bảng `LENH:1254`,
`trang-thai.js:14` (`TINH_HUONG`), `:24` (`KHOA_NGHE_VA_XUAT`).
**Chi phí:** vừa. **Tự kiểm:** ép từng tình huống rồi bấm đủ sáu nút, phải về được `binh_thuong`.

### Nhóm 3 — Menu · phím tắt · tooltip *(65 dòng — khối lớn nhất, một họ)*

Chiếm **28% cả báo cáo** và rải khắp bảy màn, nhưng là **một việc duy nhất**, làm một lượt
rẻ hơn nhiều so với chạm bảy lần.

| Phần | Việc |
|---|---|
| a | Dựng lại 6 menu đúng thứ tự, đúng mục, đúng gạch ngăn (code hiện **không có gạch ngăn nào**) |
| b | Neo bảng menu vào nhãn — bỏ `left:${6 + S.menu * 74}px`, đo được lệch tới **+96px** ở menu cuối |
| c | Nối 4 phím tắt code tự bày mà chưa bắt: `Ctrl+=` `Ctrl+-` `F1` `Ctrl+/`, cộng `Ctrl+.` (dừng hẳn) |
| d | Bổ sung 20 tooltip còn thiếu trên màn chính (hiện 12/32), và nối `lyDoKhoa()` vào `title` của nút bị khoá |
| e | Menu *Xem* trên màn Soát: thêm *Chỗ cần chú ý* / *Văn bản sau chuẩn hoá*; *Chỉnh sửa → Soát lại tệp này* `Ctrl+K` |
| f | Hai mục *Nhân bản giọng từ file…* / *Thu âm để tạo giọng mới…* mở **thẳng** hộp nhân bản đúng bước |

**Chú ý một cái bẫy:** chú thích `giao-dien.js:40-49` nói sáu mục Hoàn tác/Làm lại/Cắt/Sao chép/
Khoảng lặng/Ngắt đoạn bị gỡ vì "không có contenteditable". **Chú thích đó đã cũ** — `.doan__chu`
nay có `isContentEditable = true`. Lý do gỡ không còn.

**Riêng `Ctrl+Z`/`Ctrl+Y` phải đo trước khi hứa:** giao diện vẽ lại toàn bộ `#goc` sau mỗi
`dat()`, undo của trình duyệt rất dễ đứt. Đo xong mới quyết làm hay để lại.

### Nhóm 4 — Màn hình chính, phần còn lại *(≈27 dòng nặng)*

Cây tệp trong cột trái · vòng đời hồ sơ (đổi tên bằng nháy đúp, nút xoá, đánh số
*Hồ sơ mới N*) · hàng đầu vùng văn bản · thẻ *Cần chú ý* đang rỗng · dải Tìm-thay-thế
mất vị trí con trỏ khi gõ. **Phụ thuộc quyết định 1.1.**

### Nhóm 5 — Soát văn bản · Thư viện giọng · Xuất file *(theo thứ tự màn)*

- **Soát văn bản (11 nặng):** bảng soát đang *thay* vùng đọc thay vì nằm dưới nó; nút *Soát
  văn bản* không thành công tắc; cột *Máy sẽ đọc thành* tô sáng cả câu thay vì chỉ phần đổi.
- **Thư viện giọng (20 nặng):** hộp nhân bản 8 trạng thái; bộ lọc giới tính **đang lọc sai
  đo được bằng số** (bấm «Nữ» ra 0 giọng, bấm «Nam» ra 5 trong đó 2 giọng nữ); xoá/gỡ giọng
  chưa có hộp xác nhận.
- **Xuất file (8 nặng):** thiếu hàng *Khoảng lặng giữa các đoạn* và ba ô đánh dấu; `Ctrl+E`
  thiếu chốt `lyDoKhoa`.

### Nhóm 6 — Văn bản ghép *(45 dòng — dựng mới cả màn)*

**Phụ thuộc quyết định 1.2 và 1.3.** Không bắt đầu trước khi chốt cả hai.

**Đã có sẵn trong code, không phải dựng lại** (đã grep, không đoán):
- `DocCongDuc.py:320` `class NoiDung` — đủ `dau_bat/dau_text`, `giua_bat/giua_sau_moi/giua_text`,
  `cuoi_bat/cuoi_text`, `mau_cau`. Bốn khối văn bản đã có cả bộ đọc/ghi lẫn chỗ lưu.
- `DocCongDuc.py:1471` `build_playlist_congduc` — đã dựng đúng trình tự Đầu → tiêu đề nhóm →
  mỗi dòng theo mẫu câu → Câu xen giữa sau mỗi N dòng → Cuối. Xương nối vào máy đọc đã có.
- `giaodien/ho_so.py` — mỗi hồ sơ đã có `noidung-{slug}.ini` riêng.
- **Bảy trong tám nhánh *Cách đọc*** đã có hàm chạy thật (xem mục 1.2).

**Chưa có gì:** đọc `.csv` đúng cách · `.xlsx` · lấy từ Google Sheet · đăng nhập Google ·
khớp cột · lọc/nhóm/khoảng ngày · khung xem trước · và cả màn hình.

### Nhóm 7 — Toàn bộ mức nhẹ *(112 dòng)*

Làm cuối, gom theo họ chứ đừng theo màn:
- **Biến CSS (40 dòng):** `--close` (đang bị đổi tên thành `--dong`), `--scrim` (.34 → .32,
  và thêm .45 cho bộ tối), `--wave` (chưa có), `letter-spacing:.01em` cho tiêu đề đoạn.
- Còn lại là khoảng cách, cỡ chữ, câu chữ — rẻ, làm một lượt.

---

## 3. Sau mỗi nhóm

Theo đúng luật anh đặt, và cũng là cách dự án này tránh mất vòng:

1. Chạy thử **được** — không gom hết rồi mới chạy.
2. Mở lại **đúng tệp thiết kế**, bấm lại **đúng trạng thái đó** để so.
3. Cập nhật cột **Trạng thái** trong `DOI-CHIEU.md`: `xong` / `bỏ qua, lý do` / `chờ anh quyết`.
4. Báo anh. Dừng. Không chạy liền mạch sang nhóm sau.

Thêm một điều dự án này đã học bằng bốn vòng mất trắng: **chạy được từ source chưa phải là
xong**. Nhóm nào đụng đường đóng gói thì phải build `.exe` rồi chạy thật mới được tính.

---

## 4. Ba việc thuộc hội đồng — sẽ trình trước, không tự làm

Theo `CLAUDE.md` mục 3:

- Nhóm 1 mục **3, 4, 6** — đụng dữ liệu người dùng (`noidung.ini`, kho cấu hình, nội dung đã gõ).
- Bất kỳ chỗ nào phải sửa `DocCongDuc.py` — engine dùng chung. Nhóm 1 mục 1 và 7 rơi vào đây.
- Nhóm 6 cần `openpyxl` để đọc `.xlsx` — **đụng đường đóng gói**, phải thêm `--collect-data`
  và build `.exe` rồi chạy thật mới được tính là xong.
- Nếu chọn v1 nguyên bản mà không chốt ba điểm ở mục 1.2 → sau phải viết bộ chuyển đổi dữ
  liệu người dùng đã lưu.

---

## 5. Một việc dọn nhà, nhỏ nhưng nên làm sớm

Bảy tệp thiết kế trong thư mục làm việc **khớp bản trực tuyến**, nhưng so với `HEAD` của git
thì chúng đang ở trạng thái `M` (đã sửa, chưa commit) — và `GiongDoc - Văn bản ghép.dc.html`
còn là `??` (chưa được theo dõi).

Nghĩa là: **ai lỡ `git checkout` hay `git revert` thư mục đó là mất đồng bộ với dự án thiết
kế ngay**, mà lại không có dấu hiệu gì báo. Nên commit bộ thiết kế 17/8 lại cho chắc, kèm md5
trong thông điệp commit để lần sau đối chiếu được.

---

## Bẫy để lại cho lượt 6

`kiem/kiem_khoa_ten_tep.py` mục A đọc mã nguồn bằng **số dòng cứng**
(`cau_noi_moi.py` 557/599 · `giao-dien.js` 947/948/958/960/962 · `trang-thai.js` 126).
Lượt 6 sửa `giao-dien.js` nhiều thì các số ấy trỏ nhầm và bài kiểm đỏ lên **vì lý do
chẳng liên quan gì đến lỗi nó canh**. Đã vấp đúng chuyện này một lần ở lượt 3 với
`kiem_so_nguoi_nhom.py`. Gặp thì đổi sang tìm theo NỘI DUNG, đừng nới lỏng phép canh.
