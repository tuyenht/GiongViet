# Giọng Việt — Kim chỉ nam

Chương trình đọc văn bản tiếng Việt thành tiếng nói, chạy hoàn toàn trên máy.

**Định vị (chủ dự án chốt 13/8/2026):** cốt lõi là đọc được **dữ liệu sống** —
nội dung ghép từ phần cố định (tệp, chữ dán) và phần thay đổi theo thời gian
(nguồn động lấy từ URL/Drive). Format là thứ mở rộng được: chương trình nhận
một *khuôn đọc* rồi áp lên dữ liệu.

**Danh sách công đức đọc ở chùa chỉ là MỘT khuôn mẫu có sẵn**, không phải mục
đích của chương trình. Đừng thiết kế thứ gì gắn cứng vào riêng nó.

Người dùng cuối phần lớn **lớn tuổi, không rành máy tính**. Mọi quyết định lấy
đó làm gốc.

## 1. CORE KPI

Ổn định · dễ dùng cho người không rành máy tính · **KHÔNG bày nút giả** (mọi nút phải nối vào chức
năng có thật) · **bản `.exe` phải chạy được, không chỉ bản source** · một nguồn phát tiếng tại một
thời điểm · đóng cửa sổ là tiến trình phải thoát sạch · không đụng dữ liệu người dùng · chạm tối thiểu,
giữ nguyên phần đang chạy được.

## 2. Kiến trúc

**Cây thư mục đã đổi tên (soát lại 24/9/2026).** Ghi chép cũ nói `giaodien/` ·
`giaodien_moi/` · `ui-moi/` · `kiem/` · `_luutru/` là đã lỗi thời — đọc bảng
dưới, đừng tin bản cũ.

```
GiongViet.py           điểm vào — cửa sổ pywebview + WebView2, không khung
DocCongDuc.py          ENGINE dùng chung, 4.892 dòng: VieNeu-TTS, chuẩn hoá
                       tiền/tên, giọng riêng. KHÔNG phải chương trình cũ.
                       Xoá là mất sạch.
                       (~1.800 dòng UI Tkinter bên trong đã chết, chờ gỡ riêng)
                       [GiongDoc] trong đó là TÊN SECTION của cauhinh.ini —
                       đổi là mất sạch cấu hình người dùng. ĐỪNG đổi.

src/paths.py           một chỗ duy nhất tính mọi đường dẫn. Thêm đường dẫn mới
                       thì vào đây, đừng rải Path(__file__) khắp nơi.

src/core/              THƯ VIỆN DÙNG CHUNG — 23 tệp, đều đang được gọi thật
                       (trước là giaodien/). Đây KHÔNG phải "bản cũ".
  cau_noi.py             lớp Api, cầu JS <-> Python (mọi phương thức công khai lộ ra JS)
  bo_doc.py              vòng đọc playlist          | có SỐ PHIÊN
  nghe_thu.py            phát thử một giọng         | có SỐ PHIÊN
  xuat_file.py           ghép WAV (đường xuất của bản cũ, bản mới dùng xuat_moi)
  ds_giong.py            đọc nhanh danh sách giọng từ JSON (85 ms, không đợi mô hình)
  nhat_ky.py             ghi lỗi + traceback ra GiongViet-loi.log
  kho_cau_hinh.py        kho thiết lập trong giongviet.db (thay các tệp .ini rời)
  danh_muc_giong.py · mo_hinh.py · du_lieu.py · thu_vien_giong.py · he_thong.py
  ho_so.py · soat.py · tu_dien.py · cai_dat.py · chuan_hoa_am_thanh.py
  bo_dieu_phoi_ngu_canh.py · bo_chuyen_ngu_khoa_hoc.py · da_ngon_ngu_tts.py
  dich_thuat.py
  chuyen_mau_giong.py · kiem_dinh_1_1.py   ← CHƯA có chỗ nào trong bản chạy gọi

src/app/               TẦNG ỨNG DỤNG — 10 tệp, toàn bộ là mã chạy thật
                       (trước là giaodien_moi/)
  cau_noi_moi.py         ApiMoi kế thừa Api
  xuat_moi.py            bộ xuất WAV/MP3            | có SỐ PHIÊN
  am_thanh_loc.py        chuỗi -af cho ba thanh chỉnh
  ho_so_v2.py · soat_moi.py · luu_tep.py · khoa_du_lieu.py
  so_dien_thoai.py · sdt_mau.py · sdt_nhip.py

src/web/               giao diện — 18 tệp (11 .js · 5 .css · 2 .html)
                       (trước là ui-moi/)

tests/                 TOÀN BỘ bộ kiểm và bài đo — 44 .py + 12 .mjs, không tệp
                       nào vào bản đóng gói (trước là kiem/). Đường dẫn tính từ
                       vị trí tệp, KHÔNG viết cứng: kho đã lên GitHub, viết cứng
                       là ai tải về chỗ khác cũng vỡ hết.
  chay_tat_ca.py         chạy cả bộ VÀ đọc giùm kết quả cho đúng — xem §4, dòng
                         "hai loại bài". Mặc định bỏ 7 bài chiếm màn hình.

giaodien/ · giaodien_moi/
                       mỗi thư mục CHỈ CÒN MỘT tệp __init__.py làm cầu bắc sang
                       src/core và src/app, giữ cho ~100 chỗ import cũ khỏi phải
                       sửa. Không có mã thật trong đó. Bẫy đi kèm: xem §4.

_archive/              bản cũ đã ngừng dùng (trước là _luutru/): GiongDoc.py ·
                       GiongDoc.exe · DongGoi.bat cũ · giaodien/ giaodien_moi/
                       kiem/ bản cũ. Riêng _archive/config_backups/ là nơi
                       nhap_tu_tep_cu() DỜI các tệp .ini cũ tới.
docs/                  PROJECT_MAP.md · designs/ · plans/ · specs/
DongGoi.bat            build ra GiongViet/ — dùng junction, chỉ chạy được máy này
DongGoi_Giao.bat       biến bản build thành thư mục CHÉP ĐI ĐƯỢC (xem §7)
```

**Việc đổi tên đã XONG** — trước đây hoãn để chờ build được `.exe`, nay `.exe`
đã build và chạy thật. Cách giữ cho ~100 chỗ import cũ khỏi phải sửa là hai gói
cầu bắc `giaodien/` và `giaodien_moi/`.

**Bốn màn đứng riêng, Soát văn bản thì không** (chốt 19/8). Thư viện giọng · Từ điển
phát âm · Cài đặt · Văn bản ghép chiếm **toàn cửa sổ**: bỏ thanh menu, thanh công cụ,
hai cột; chỉ còn thanh tiêu đề mang tên màn kèm mũi tên lùi. Căn cứ đếm được là nút
*"Quay lại màn hình chính"* trong tệp thiết kế — bốn màn ấy có, **Màn hình chính 0 và
Soát văn bản 0**. Soát văn bản là một **bảng mở thêm ở dưới** trong cửa sổ chính, không
phải một màn; chính tệp thiết kế của nó viết *"Vẫn là cửa sổ chính của Giọng Việt"*.

**Có git từ 13/8/2026** — kho riêng tư `github.com/tuyenht/GiongViet`. Trước đó
dự án không dùng git; các ghi chép cũ nói "không dùng git" là đã lỗi thời.
Dữ liệu người dùng nằm trong `.gitignore`, không bao giờ commit.

Vẫn xác minh thực địa bằng mtime, `py_compile`, kiểm bundle, đọc log — git
không thay được việc đó.

## 3. Việc thuộc HỘI ĐỒNG — propose-first, DỪNG chờ duyệt

- Đụng `DocCongDuc.py` (engine dùng chung)
- Đụng đường đóng gói (`DongGoi.bat`, `DongGoi_Giao.bat`, `--collect-data`, `--hidden-import`)
- Đụng dữ liệu người dùng (`congduc.txt`, `giongviet.db`, `cauhinh.ini`, `noidung.ini`, `tudien.ini`, `giong_rieng/`)
- Thêm nguồn phát âm thanh thứ N (hiện có 3: `bo_doc`, `nghe_thu`, `xuat_file`)
- Lật một quyết định đã chốt

Còn lại → làm thẳng, báo cáo sau. Đừng hỏi vụn vặt.

## 4. Bẫy — đã vấp thật, có số liệu

| Bẫy | Hậu quả đã đo |
|---|---|
| Kết luận "chạy được" khi mới chạy từ source | Mất 4 vòng. Đóng gói là mắt xích riêng, phải build rồi chạy thật |
| Thiếu `--collect-data vieneu` | Danh sách giọng RỖNG |
| Thiếu `--collect-data sea_g2p` | `os error 2` đúng lúc bấm đọc (`sea_g2p.bin` 61 MB) |
| Nguồn phát tiếng thiếu SỐ PHIÊN | 4 tiến trình `ffplay` cùng nói. Cờ dừng KHÔNG đủ: tổng hợp 1 câu mất tới 40 s, `join(timeout)` bỏ cuộc rồi luồng cũ sống lại |
| Không `os._exit(0)` sau `webview.start()` | 66 luồng treo, ôm vài GB RAM |
| Alt+F4 | `thoat()` không chạy, `ffplay` đọc tiếp. Dọn dẹp phải đặt SAU `webview.start()` |
| Sự kiện nổi lên `document` | Đóng ngay cái vừa mở. Cần `stopPropagation` |
| Đóng dropdown khi cuộn, quên loại trừ cuộn TRONG nó | Không ai cuộn nổi |
| `position:absolute` trong `overflow:auto` | Bị cắt cụt giữa thân. Dùng `position:fixed` + tự tính toạ độ |
| `.bat` có `pause` | Agent chạy treo vô hạn. Đặt `GIONGDOC_TU_DONG=1` |
| PowerShell không bung dấu sao | `py_compile a.py src/core/*.py` → `[Errno 22]`, thoát mã 1, tưởng nhầm code lỗi. Dùng `glob.glob` |
| `evaluate_js` gọi `pywebview.api` | Trả **Promise**, đọc đồng bộ chỉ nhận `{}`. Phải `.then()` gán biến global |
| Bản `--windowed` in tiếng Việt ra stdout | `UnicodeEncodeError` cp1252. Ghi log ra tệp UTF-8 |
| Tưởng `_archive/config_backups/` là chỗ sửa cấu hình bằng Notepad | Nó là **đầu ra thuần**, không nằm trên đường đọc nào. `GiongViet.py` gọi `kho_cau_hinh.nhap_tu_tep_cu()` mỗi lần khởi động; hàm đó **dời** `noidung.ini`+`tudien.ini` khỏi thư mục cài đặt, rồi engine luôn ưu tiên bản trong `giongviet.db` — chép về chỗ cũ rồi sửa cũng vô hiệu. Bài đo: `tests/kiem_duong_sua_loi_dan.py` |
| Chạy `DongGoi.bat` khi vòng cứu dữ liệu còn thiếu | Glob cứu chỉ bắt `*.json *.ini *.txt`, **không có `*.db`, không đệ quy**. Sau khi gom thì thiết lập thật nằm trong `giongviet.db` — build lại là lùi về mốc tệp `.ini` rời, build lần hai là mất hẳn. Bài đo `tests/kiem_dong_goi_cuu_du_lieu.py` đỏ cho tới khi vá |
| Tin `vanTayTaiLieu()` để biết tài liệu có đổi không | Nó chỉ đếm **tổng số ký tự**. Sửa một chữ thành chữ khác cùng độ dài là vân tay y nguyên, mọi thứ dựa vào nó im lặng bỏ qua |
| "Sửa" một bài trong `tests/` đang đỏ | `tests/` có **hai loại** bài: *bài canh* (xanh = tốt) và *bài chứng minh lỗi* (**xanh = lỗi còn nguyên**, mã `L1`..`L7` ở đầu docstring). Chạy `py tests/chay_tat_ca.py` — nó đọc giùm cho đúng. Đã suýt đi chữa 4 cái lỗi không còn tồn tại |
| `import giaodien_moi.ho_so_v2` (có dấu chấm) qua gói cầu bắc | Tạo ra **module THỨ HAI** song song với `src.app.ho_so_v2`: hai bản biến toàn cục, ghi bên này đọc bên kia không thấy. `from giaodien_moi import ho_so_v2` thì KHÔNG bị |
| Neo một phép kiểm vào **số dòng** của tệp nguồn | Sửa vài dòng phía trên là bài kiểm soi nhầm chỗ mà vẫn xanh. Đã gặp 4 chỗ trong cùng một tệp. Tìm theo **nội dung**, đừng theo số dòng |
| Tưởng `bin/ffmpeg` · `models/vieneu` trong `GiongViet/` là thư mục thật | Chúng là **junction** do `DongGoi.bat` nối. `find`/`du` không đi xuyên qua → tưởng rỗng; chép bằng Explorer hay nén ZIP thường → ra thư mục rỗng ở máy người nhận. Muốn giao thì chạy `DongGoi_Giao.bat` |
| Dấu `)` nằm trong chuỗi của `.bat` | `cmd` coi đó là hết khối `if ( ) else ( )` nên **cả hai nhánh cùng chạy** — một mục in ra cả OK lẫn LỖI |
| `rem` chen giữa hai dòng nối bằng `^` | `rem` thành ĐỐI SỐ của lệnh đang nối chứ không phải chú thích. Đặt chú thích TRƯỚC cả lệnh |
| `Get-ChildItem -Recurse -File 'đường\dẫn'` | `-File` là CÔNG TẮC, đường dẫn rơi vào tham số khác → "Second path fragment must not be a drive", ra 0.00 GB trong khi thư mục nặng 1,34 GB. Phải ghi `-Path` tường minh |
| `cmd /c foo.bat` | Tìm trong PATH chứ không tìm thư mục hiện tại. Ghi đường dẫn đầy đủ |

## 5. Quy tắc làm việc

- **Đo, đừng đoán.** Có cách kiểm bằng lệnh/số liệu thì phải chạy. Dự án này đã mất nhiều vòng vì
  suy luận nghe hợp lý thay vì đo.
- **Sửa cả họ, đừng vá lẻ.** Tìm được 1 lỗi thuộc một họ đã biết → rà toàn bộ chỗ cùng họ.
- **KHÔNG chụp toàn màn hình** máy người dùng (đã 2 lần bắt trúng dữ liệu công việc của họ) và
  **KHÔNG chiếm foreground** khi họ đang làm. Cần xem giao diện → nhờ họ bấm, hoặc đo bằng
  `evaluate_js` trong cửa sổ probe riêng.
- **KHÔNG test bằng file cấu hình thật** — app tự ghi đè khi đổi thiết lập. Dùng bản sao.
- **Báo cáo phân biệt rạch ròi:** đã chạy trên `.exe` / mới chạy từ source / chưa kiểm chứng được.
- **Ngưỡng cứng đặt trên số đo ngẫu nhiên là bẫy.** In con số MONG MUỐN ra màn hình, còn phép
  khẳng định thì đặt ở sàn rộng — không thì bài lúc xanh lúc đỏ, rồi chẳng ai tin nó nữa.
- VieNeu **không có** tham số tốc độ và cao độ. Thứ chỉnh được là các khoảng nghỉ.
- Trả lời bằng tiếng Việt.

## 6. Lệnh hay dùng

```
py -c "import glob,py_compile;[py_compile.compile(f,doraise=True) for f in ['GiongViet.py','DocCongDuc.py']+glob.glob('src/core/*.py')+glob.glob('src/app/*.py')]"
py tests/chay_tat_ca.py                     # ca bo kiem, co doc gium ket qua
set GIONGDOC_TU_DONG=1 && DongGoi.bat       # build; thieu bien nay se treo o pause
set GIONGDOC_TU_DONG=1 && DongGoi_Giao.bat  # dong goi de GIAO (sau khi da build)
Get-Process ffplay                          # dem tien trinh phat tieng, toi da 1
```

Bundle phải có đủ 3 tệp mấu chốt:
`_internal\web\index.html` · `_internal\sea_g2p\sea_g2p.bin` · `_internal\vieneu\assets\voices_v3_turbo.json`

`DongGoi.bat` cố ý chép `src\web` **hai lần** — ra `_internal\web\` và
`_internal\ui-moi\` — để đường lùi trong `src/paths.py` chắc chắn tìm thấy một
trong hai. Tốn 596 KB, đổi lấy việc giao diện không vỡ nếu một đường bị hụt.

Lệnh hội đồng: `/bs:spec` · `/bs:audit` · `/bs:next` · `/bs:review` · `/bs:ship` · `/bs:close`

## 7. Giao bản cho người khác

`DongGoi.bat` ra bản chạy được **trên máy này**. Muốn gửi đi phải chạy tiếp
`DongGoi_Giao.bat`: nó chép `bin\ffmpeg` và `models\vieneu` từ thư mục GỐC
thành thư mục thật (không đi qua junction), kèm tệp mẫu bảng tính, ra
`_giao\GiongViet\` — khoảng 1,34 GB, nén rồi gửi.

Tệp đó có sẵn ba phép canh ngược: bản giao **không được** mang theo
`data\giongviet.db`, `data\congduc.txt` hay `data\giong_rieng\` — thiết lập và
**năm tệp ghi âm giọng thật** của chủ dự án. Vòng cứu dữ liệu trong
`DongGoi.bat` cố ý kéo chúng sang bản build mới (đúng cho việc tự cập nhật),
nên bước giao phải gỡ ra.
