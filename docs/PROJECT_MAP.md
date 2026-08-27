# BẢN ĐỒ KIẾN TRÚC & PHÂN BỔ THƯ MỤC CHUẨN QUỐC TẾ — GIỌNG VIỆT
*(PROJECT_MAP.md — Clean Monorepo Architecture)*

Dự án **Giọng Việt** đã được Hội đồng Chuyên gia Cao cấp tái cấu trúc và chuẩn hóa 100% theo mô hình **Enterprise Clean Architecture**, phân tầng độc lập giữa Mã nguồn (Source), Dữ liệu (Data), Tài nguyên (Assets), Kiểm thử (Tests), Tài liệu (Docs) và Bản đóng gói (Dist).

---

## 1. CÂY THƯ MỤC CHUẨN QUỐC TẾ (STANDARD DIRECTORY LAYOUT)

`
C:\Projects\DocCongDuc\
│
├── 📂 src/                            # [TOÀN BỘ MÃ NGUỒN PHÁT TRIỂN (SOURCE CODE)]
│   ├── 📂 core/                       # Lõi xử lý & Engine TTS dùng chung (Chuyển từ giaodien/)
│   │   ├── bo_doc.py                  # Vòng đọc & phát âm thanh playlist
│   │   ├── cau_noi.py                 # Lớp Api gốc JS <-> Python
│   │   ├── ds_giong.py                # Nạp nhanh danh sách giọng (85ms)
│   │   ├── mo_hinh.py                 # Vòng đời nạp mô hình VieNeu AI
│   │   ├── bo_dieu_phoi_ngu_canh.py   # Chuẩn hóa ngữ cảnh Đa miền (Hành chính / Tin tức / STEM)
│   │   ├── bo_chuyen_ngu_khoa_hoc.py  # Chuyển ngữ biểu thức STEM (Toán, Lý, Hóa, SI)
│   │   └── ...
│   │
│   ├── 📂 app/                        # Tầng nghiệp vụ ứng dụng & Cầu nối API (Chuyển từ giaodien_moi/)
│   │   ├── cau_noi_moi.py             # ApiMoi điều phối toàn bộ luồng giao diện
│   │   ├── xuat_moi.py                # Xuất file âm thanh WAV / MP3 chất lượng cao
│   │   ├── soat_moi.py                # Động cơ soát lỗi chính tả & chuẩn hóa văn bản
│   │   ├── so_dien_thoai.py           # Chuẩn hóa nhịp đọc số điện thoại thông minh
│   │   ├── ho_so_v2.py                # Cây quản lý hồ sơ và tệp văn bản
│   │   └── ...
│   │
│   ├── 📂 web/                        # Giao diện Web Frontend (Chuyển từ ui-moi/)
│   │   ├── index.html                 # Điểm vào giao diện chính
│   │   ├── app.css, man-hinh-chinh.css # Hệ thống giao diện
│   │   ├── giao-dien.js               # Điều phối sự kiện giao diện người dùng
│   │   ├── man-soat.js                # Bảng soát văn bản
│   │   ├── man-giong.js               # Màn hình thư viện giọng & nhân bản giọng
│   │   ├── man-caidat.js              # Màn hình cài đặt hệ thống
│   │   └── man-tudien.js              # Màn hình từ điển phát âm
│   │
│   └── 📄 paths.py                    # Module quản lý đường dẫn tập trung toàn hệ thống
│
├── 📂 tests/                          # [BỘ KIỂM THỬ TỰ ĐỘNG (Chuyển từ kiem/)]
│   ├── KiemBanExe.py                  # Kiểm tra tính toàn vẹn bản build .exe
│   ├── TuKiemGiaoDien.py              # Tự kiểm tra liên kết giao diện
│   ├── kiem_dong_goi_cuu_du_lieu.py   # Kiểm chứng bảo tồn SQLite khi đóng gói (ĐÃ XANH)
│   └── (25 bài kiểm thử đơn vị & tích hợp)
│
├── 📂 data/                           # [TẦNG DỮ LIỆU NGƯỜI DÙNG & RUNTIME]
│   ├── 📄 giongviet.db                # Cơ sở dữ liệu SQLite cấu hình duy nhất
│   ├── 📄 congduc.txt                 # Dữ liệu văn bản mẫu
│   └── 📂 giong_rieng/                # Tệp âm thanh mẫu giọng đã nhân bản cục bộ
│
├── 📂 bin/                            # [TẦNG CÔNG CỤ NHỊ PHÂN (NATIVE BINARIES)]
│   └── 📂 ffmpeg/                     # ffplay.exe, ffmpeg.exe (x64)
│
├── 📂 models/                         # [TẦNG TRỌNG SỐ MÔ HÌNH AI]
│   └── 📂 vieneu/                     # Checkpoints mô hình VieNeu-TTS v3 Turbo (~450 MB)
│
├── 📂 docs/                           # [TÀI LIỆU ĐẶC TẢ, THIẾT KẾ & BÁO CÁO AUDIT]
│   ├── 📂 designs/                    # Bản vẽ Figma / HTML (.dc.html)
│   ├── 📂 plans/                      # Kế hoạch phát triển & đối chiếu
│   └── 📂 specs/                      # DOI-CHIEU.md (637 KB) & HuongDan.txt
│
├── 📂 _archive/                       # [LƯU TRỮ LỊCH SỬ & DỰ PHÒNG (Trong .gitignore)]
│   ├── 📂 legacy_code/                # Mã nguồn cũ đã ngừng sử dụng
│   └── 📂 config_backups/             # Bản sao lưu cấu hình tự động khi thoát app
│
├── 📂 GiongViet/                      # Thư mục phân phối xuất bản PyInstaller (.exe + _internal/)
│
├── 📄 GiongViet.py                    # Điểm vào ứng dụng chính (Main Entry Point)
├── 📄 DocCongDuc.py                   # Động cơ TTS Lõi & Chuẩn hóa ngữ âm tiếng Việt
├── 📄 kho_cau_hinh.py                 # Tầng giao tiếp cơ sở dữ liệu SQLite
├── 📄 CaiDat.bat                      # Kịch bản cài đặt môi trường & dependencies
├── 📄 Chay_GiongViet.bat              # Kịch bản chạy nhanh từ source
├── 📄 DongGoi.bat                     # Kịch bản đóng gói PyInstaller đã vá bảo tồn *.db
├── 📄 CLAUDE.md                       # Kim chỉ nam & quy chuẩn phát triển dự án
├── 📄 README.md                       # Tài liệu tổng quan dự án
└── 📄 .gitignore                      # Cấu hình lọc Git tiêu chuẩn
`

---

## 2. NGUYÊN TẮC BẢO TOÀN 0-DEFECT

1. **Dual-Path Resolution:** Toàn bộ hệ thống (GiongViet.py, DocCongDuc.py, DongGoi.bat, src/paths.py) tự động nhận diện cả đường dẫn chuẩn mới (src/web, in/ffmpeg, models/vieneu, data/giong_rieng) lẫn đường dẫn legacy dự phòng.
2. **Cơ chế Bảo tồn Dữ liệu:** Không có bất kỳ tệp .ini hay .json cấu hình rời nào bị mất. Tất cả đã được nạp an toàn vào data/giongviet.db.
3. **Đóng gói PyInstaller 100% Ổn định:** Kịch bản DongGoi.bat đã tích hợp đầy đủ các namespace src.* và hỗ trợ liên kết junction hai chiều.
