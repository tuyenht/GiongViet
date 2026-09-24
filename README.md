# Giọng Việt (GiongViet)

[![Python 3.10+](https://img.shields.io/badge/python-3.10+-blue.svg)](https://www.python.org/downloads/)
[![Platform](https://img.shields.io/badge/platform-Windows%2010%2B-lightgrey.svg)](https://microsoft.com/windows)
[![TTS Engine](https://img.shields.io/badge/TTS-VieNeu--TTS%20Turbo-success.svg)](https://github.com/pnnbao-ump/VieNeu-TTS)
[![UI](https://img.shields.io/badge/UI-pywebview%20%2B%20HTML5%2FCSS3-orange.svg)](https://pywebview.flowrl.com/)
[![License](https://img.shields.io/badge/license-MIT-green.svg)](LICENSE.txt)

Ứng dụng đọc văn bản tiếng Việt thành giọng nói tự nhiên chất lượng cao, **đọc tiếng Việt hoàn toàn trên máy, không cần mạng**. Sử dụng mô hình AI tiên tiến **VieNeu-TTS Turbo** kết hợp cùng hệ thống xử lý ngôn ngữ tự nhiên tối ưu hóa cho tiếng Việt.

> **Hai tính năng CẦN MẠNG** — phần còn lại chạy offline:
> - **Đọc ngoại ngữ (28+ thứ tiếng)** dùng dịch vụ giọng đọc của Microsoft. Câu văn được gửi tới máy chủ `speech.platform.bing.com` để tổng hợp, nên cần Internet và văn bản có rời khỏi máy. Đọc tiếng Việt thì không.
>   Và xin nói rõ: phần ngoại ngữ **chưa dùng chất giọng bạn nhân bản** — nó đọc bằng giọng mẫu sẵn có. Giọng riêng của bạn chỉ dùng cho tiếng Việt, và phần đó chạy hoàn toàn trên máy.
> - **Dịch thuật song ngữ** gọi dịch vụ dịch trực tuyến. Mất mạng thì câu giữ nguyên văn gốc.
>
> Nếu bạn đọc danh sách có tên và số tiền của người khác, hãy cân nhắc điều này trước khi bật đọc ngoại ngữ.

---

## 🌟 Điểm nổi bật & Tính năng cốt lõi

### 1. Xử lý & Chuẩn hoá tiếng Việt chuyên sâu
- **Văn bản pháp quy & Hành chính**: Tự động nhận diện chuẩn theo Nghị định 30/2020/NĐ-CP và văn bản Đảng (VD: `30/2020/NĐ-CP` → *số 30 năm 2020 Nghị định Chính phủ*, `66-QĐ/TW` → *Quy định số 66 Quyết định Trung ương*).
- **Quy tắc số học & Tiền tệ**: Đọc chuẩn tiền tệ (VNĐ, $, k, tr), phân số, số La Mã, số điện thoại (tách nhịp hotline/di động tự nhiên), ngày tháng năm.
- **Từ điển phát âm & Viết tắt**: Dạy máy đọc đúng tên riêng, địa danh, thuật ngữ viết tắt và từ mượn tiếng nước ngoài.

### 2. Mô hình giọng AI VieNeu-TTS Turbo Offline
- **Đa dạng vùng miền**: Thư viện giọng phong phú (Bắc, Trung, Nam; Nam / Nữ).
- **Nhân bản giọng nói (Voice Cloning)**: Tạo giọng đọc riêng từ tệp âm thanh mẫu trong vài giây.
- **Thẻ biểu cảm thời gian thực**: Hỗ trợ thẻ cảm xúc `[cười]`, `[thở dài]`, `[hắng giọng]`.
- **Dịch thuật song ngữ tự động** *(cần mạng)*: Hỗ trợ chuyển ngữ tức thì khi cần phát âm đa ngôn ngữ. Mất mạng thì câu giữ nguyên văn gốc.

### 3. Trình phát & Biên tập âm thanh chuẩn Studio
- **Đồng bộ chữ và tiếng**: Chữ chạy sáng theo nhịp đọc với cơ chế tự bù trừ độ trễ phần cứng loa.
- **Bộ lọc âm thanh chuyên nghiệp**: Chỉnh Tốc độ (−50% … +100%), Cao độ (±12 nửa cung), Âm lượng, Bộ lọc EQ làm dày và ấm tiếng.
- **Hồ sơ cấu hình (Profiles)**: Lưu riêng từng hồ sơ đọc, tự động khôi phục các tệp và tab đang làm việc.

### 4. Xuất tệp âm thanh đa định dạng
- Xuất WAV (16-bit / 24-bit studio) và MP3 (128 kbps / 320 kbps cao cấp).
- Linh hoạt: Xuất thành 1 tệp duy nhất, tách theo từng đoạn, hoặc tự chia tệp mỗi 10 phút.
- Quản lý phiên tác vụ ngầm (Background Task Session) an toàn, chống rò rỉ và không tạo tệp rác khi huỷ tác vụ.

---

## 📂 Cấu trúc dự án (Clean Architecture)

```
GiongViet/
├── GiongViet.py               # Điểm khởi động ứng dụng (pywebview Desktop Host)
├── DocCongDuc.py              # Engine lõi: Tổng hợp tiếng, ngữ âm, chuẩn hoá văn bản
├── Chay_GiongViet.bat         # Script khởi chạy nhanh
├── CaiDat.bat                 # Script cài đặt môi trường & nạp tài nguyên tự động
├── DongGoi.bat                # Script đóng gói ứng dụng độc lập (.exe)
│
├── src/                       # TOÀN BỘ MÃ NGUỒN CHÍNH
│   ├── paths.py               # Quản lý đường dẫn tập trung (Source & Frozen .exe)
│   ├── core/                  # Tầng lõi nghiệp vụ (TTS, Audio, G2P, DB SQLite, Config)
│   ├── app/                   # Tầng điều phối ứng dụng (State, Session, Export, Guard)
│   └── web/                   # Tầng giao diện người dùng (HTML5, CSS3, ES2024 JS)
│
├── tests/                     # 28 BỘ KIỂM THỬ TỰ ĐỘNG (Python & Node.js ESM)
│   ├── kiem_*.py              # Bộ kiểm thử đơn vị, an toàn luồng, không rò rỉ dữ liệu
│   └── kiem-*.mjs             # Bộ kiểm thử logic giao diện, máy ảo JS, thiết kế pixel
│
├── docs/                      # TÀI LIỆU DỰ ÁN
│   ├── specs/                 # Đặc tả yêu cầu kỹ thuật & Kiến trúc
│   ├── designs/               # Bản mẫu thiết kế giao diện & Design System
│   └── plans/                 # Kế hoạch phát triển & Lịch sử nâng cấp
│
├── data/                      # Dữ liệu mẫu (Google Sheets / Excel) & CSDL cục bộ
├── models/                    # Trọng số mô hình AI VieNeu-TTS (được nạp tự động)
└── bin/                       # Bộ công cụ nhị phân hỗ trợ (FFmpeg, FFplay)
```

---

## 🚀 Hướng dẫn Cài đặt & Sử dụng

### Yêu cầu môi trường
- Hệ điều hành: Windows 10 / 11 (64-bit).
- Python: 3.10 trở lên.
- Microsoft Edge WebView2 Runtime (đã tích hợp sẵn trên Windows 10/11).

### Cài đặt môi trường phát triển (Source code)

1. **Clone mã nguồn**:
   ```bash
   git clone https://github.com/tuyenht/GiongViet.git
   cd GiongViet
   ```

2. **Cài đặt thư viện & tài nguyên tự động**:
   ```bat
   CaiDat.bat
   ```
   *Lệnh này sẽ tự động cài đặt `pip requirements`, tải `ffmpeg` và thiết lập mô hình AI vào thư mục dự án.*

3. **Chạy chương trình**:
   ```bat
   Chay_GiongViet.bat
   ```
   *Hoặc chạy trực tiếp:* `py GiongViet.py`

---

## 📦 Quy trình Đóng gói Bản chạy độc lập (.exe)

Chương trình cung cấp quy trình đóng gói tự động chuẩn hoá bằng PyInstaller:

```bat
DongGoi.bat
```

Sau khi hoàn tất, gói ứng dụng độc lập hoàn chỉnh sẽ nằm tại thư mục `GiongViet/GiongViet.exe` (sẵn sàng sử dụng mà không cần cài đặt Python).

---

## 🧪 Kiểm thử chất lượng (Zero-Defect Quality Gates)

Toàn bộ hệ thống được bảo vệ bởi 28 bộ kiểm thử tự động, chạy hoàn toàn trong môi trường cô lập `%TEMP%` để đảm bảo an toàn 100% dữ liệu người dùng:

```bash
# Chạy toàn bộ kiểm thử đơn vị Python
py -c "import glob, subprocess, sys; [subprocess.run([sys.executable, t]) for t in sorted(glob.glob('tests/kiem_*.py'))]"

# Chạy toàn bộ kiểm thử giao diện & máy ảo JS
node tests/kiem-giao-dien.mjs
node tests/kiem-mo-hinh.mjs
node tests/kiem-nhan-python.mjs
node tests/kiem-so-do-cay-tep.mjs
```

---

## 🛡️ Bảo mật & Dữ liệu cá nhân

- **Không gửi dữ liệu lên máy chủ**: Toàn bộ quá trình xử lý văn bản, tổng hợp giọng nói và lưu trữ cơ sở dữ liệu đều thực hiện cục bộ trên máy tính người dùng.
- **Không theo dõi / Không quảng cáo**: Ứng dụng không thu thập bất kỳ telemetry hay thông tin định danh nào.

---

## 📄 Bản quyền & Giấy phép

Phát triển bởi [tuyenht](https://github.com/tuyenht). Dự án được phân phối theo [Giấy phép MIT](LICENSE.txt).
