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

```
GiongViet.py           điểm vào — cửa sổ pywebview + WebView2, không khung
DocCongDuc.py          ENGINE dùng chung: VieNeu-TTS, chuẩn hoá tiền/tên, giọng riêng.
                       KHÔNG phải chương trình cũ. Xoá là mất sạch.
                       (~1.800 dòng UI Tkinter bên trong đã chết, chờ gỡ riêng)
                       [GiongDoc] trong đó là TÊN SECTION của cauhinh.ini —
                       đổi là mất sạch cấu hình người dùng. ĐỪNG đổi.

giaodien/              THƯ VIỆN DÙNG CHUNG — cả 15 tệp đều đang được bản mới gọi.
                       Đây KHÔNG phải "bản cũ"; xoá là vỡ toàn bộ chương trình.
  cau_noi.py             lớp Api, cầu JS <-> Python (mọi phương thức công khai lộ ra JS)
  bo_doc.py              vòng đọc playlist          | có SỐ PHIÊN
  nghe_thu.py            phát thử một giọng         | có SỐ PHIÊN
  xuat_file.py           ghép WAV (đường xuất của bản cũ, bản mới dùng xuat_moi)
  ds_giong.py            đọc nhanh danh sách giọng từ JSON (85 ms, không đợi mô hình)
  nhat_ky.py             ghi lỗi + traceback ra GiongViet-loi.log
  mo_hinh.py · du_lieu.py · thu_vien_giong.py · he_thong.py · ho_so.py
  soat.py · tu_dien.py · cai_dat.py

giaodien_moi/          TẦNG ỨNG DỤNG — 11 tệp, toàn bộ là mã chạy thật
  cau_noi_moi.py         ApiMoi kế thừa Api
  xuat_moi.py            bộ xuất WAV/MP3            | có SỐ PHIÊN
  am_thanh_loc.py        chuỗi -af cho ba thanh chỉnh
  ho_so_v2.py · soat_moi.py · luu_tep.py · so_dien_thoai.py · khoa_du_lieu.py

ui-moi/                giao diện — 16 tệp (index.html · app.css · giao-dien.js …)

kiem/                  TOÀN BỘ bộ kiểm và bài đo — 28 tệp, không tệp nào vào
                       bản đóng gói. Đường dẫn tính từ vị trí tệp, KHÔNG viết
                       cứng: kho đã lên GitHub, viết cứng là ai tải về chỗ
                       khác cũng vỡ hết.
_luutru/               bản cũ đã ngừng dùng: GiongDoc.py · ui/ · GiongDoc.exe · DongGoi.bat cũ
```

**Tên ba thư mục `giaodien/` · `giaodien_moi/` · `ui-moi/` còn gây nhầm** — "moi"
là di sản từ hồi chạy song song hai bản. Đã chốt đổi thành `loi/` · `ungdung/` ·
`web/`, nhưng HOÃN đến khi build được `.exe` để kiểm chứng: việc đó đụng ~100
chỗ import cộng `--hidden-import` và `--add-data`, mà rủi ro thật nằm ở đóng gói.

**Có git từ 13/8/2026** — kho riêng tư `github.com/tuyenht/GiongViet`. Trước đó
dự án không dùng git; các ghi chép cũ nói "không dùng git" là đã lỗi thời.
Dữ liệu người dùng nằm trong `.gitignore`, không bao giờ commit.

Vẫn xác minh thực địa bằng mtime, `py_compile`, kiểm bundle, đọc log — git
không thay được việc đó.

## 3. Việc thuộc HỘI ĐỒNG — propose-first, DỪNG chờ duyệt

- Đụng `DocCongDuc.py` (engine dùng chung)
- Đụng đường đóng gói (`DongGoi.bat`, `--collect-data`, `--hidden-import`)
- Đụng dữ liệu người dùng (`congduc.txt`, `cauhinh.ini`, `noidung.ini`, `tudien.ini`, `giong_rieng/`)
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
| PowerShell không bung dấu sao | `py_compile a.py giaodien/*.py` → `[Errno 22]`, thoát mã 1, tưởng nhầm code lỗi. Dùng `glob.glob` |
| `evaluate_js` gọi `pywebview.api` | Trả **Promise**, đọc đồng bộ chỉ nhận `{}`. Phải `.then()` gán biến global |
| Bản `--windowed` in tiếng Việt ra stdout | `UnicodeEncodeError` cp1252. Ghi log ra tệp UTF-8 |

## 5. Quy tắc làm việc

- **Đo, đừng đoán.** Có cách kiểm bằng lệnh/số liệu thì phải chạy. Dự án này đã mất nhiều vòng vì
  suy luận nghe hợp lý thay vì đo.
- **Sửa cả họ, đừng vá lẻ.** Tìm được 1 lỗi thuộc một họ đã biết → rà toàn bộ chỗ cùng họ.
- **KHÔNG chụp toàn màn hình** máy người dùng (đã 2 lần bắt trúng dữ liệu công việc của họ) và
  **KHÔNG chiếm foreground** khi họ đang làm. Cần xem giao diện → nhờ họ bấm, hoặc đo bằng
  `evaluate_js` trong cửa sổ probe riêng.
- **KHÔNG test bằng file cấu hình thật** — app tự ghi đè khi đổi thiết lập. Dùng bản sao.
- **Báo cáo phân biệt rạch ròi:** đã chạy trên `.exe` / mới chạy từ source / chưa kiểm chứng được.
- VieNeu **không có** tham số tốc độ và cao độ. Thứ chỉnh được là các khoảng nghỉ.
- Trả lời bằng tiếng Việt.

## 6. Lệnh hay dùng

```
py -c "import glob,py_compile;[py_compile.compile(f,doraise=True) for f in ['GiongDoc.py']+glob.glob('giaodien/*.py')]"
set GIONGDOC_TU_DONG=1 && DongGoi.bat      # build; thieu bien nay se treo o pause
Get-Process ffplay                          # dem tien trinh phat tieng, toi da 1
```

Bundle phải có đủ 3 tệp mấu chốt:
`_internal\ui\index.html` · `_internal\sea_g2p\sea_g2p.bin` · `_internal\vieneu\assets\voices_v3_turbo.json`

Lệnh hội đồng: `/bs:spec` · `/bs:audit` · `/bs:next` · `/bs:review` · `/bs:ship` · `/bs:close`
