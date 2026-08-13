---
description: Chốt & bàn giao cuối session — trích + phân loại tri thức bền + payload resume
argument-hint: [tùy chọn — bối cảnh thêm]
---
[/bs:close — CHỐT & BÀN GIAO CUỐI SESSION · dự án DocCongDuc / GiongDoc]

Với vai trò hội đồng chuyên gia cao cấp phù hợp: QUÉT SESSION 1 LẦN rồi in ra 2 khối —
A) tri thức BỀN cần lưu docs/memory; B) payload RESUME dán vào session mới để nối việc liền mạch.
Đây là TRÍCH + PHÂN LOẠI, KHÔNG diễn kịch nhiều-vai, KHÔNG tự sửa tài liệu gốc.
Mỗi khối TỰ no-op: không có gì thì nói rõ, đừng bịa.
[Bối cảnh thêm do tôi cung cấp — nếu có, ưu tiên khi quét]: $ARGUMENTS

── DÙNG CHUNG (làm 1 lần cho cả A và B) ──
- DỰ ÁN NÀY KHÔNG PHẢI REPO GIT. Không có `git status` / `git log` để dựa vào. Xác minh thực địa bằng:
  • `ls -la` thư mục gốc + mtime các file vừa động
  • `py -c "import glob,py_compile;[py_compile.compile(f,doraise=True) for f in ['GiongDoc.py']+glob.glob('giaodien/*.py')]"` (cú pháp)
  • SO mtime `GiongDoc.exe` VỚI file nguồn vừa sửa - nguồn mới hơn nghĩa là bản `.exe` ĐÃ CŨ,
    mọi kết luận "đã chạy được" trên nó hết giá trị
  • Bundle: `_internal\ui\index.html` · `_internal\sea_g2p\sea_g2p.bin` · `_internal\vieneu\assets\voices_v3_turbo.json`
  • `GiongDoc-loi.log` (nếu có → đọc traceback, đừng đoán)
- Chỉ xét phần CÒN trong context. Đầu session đã rơi → ghi "có thể sót phần đầu" VÀ bơm cảnh báo đó
  vào payload RESUME (để session mới cũng biết).
- CẤM đưa dữ liệu riêng của người dùng vào BẤT KỲ khối nào: nội dung `congduc.txt` (tên và số tiền
  người thật) · mẫu thu âm trong `giong_rieng/` · đường dẫn chứa thông tin cá nhân. Cần nhắc thì ghi
  "(dữ liệu người dùng — không chép)".
- KHÔNG khối nào tự ghi file. Cả 2 chỉ IN RA. Diff CLAUDE.md / memory chỉ soạn SAU khi tôi duyệt.
- Cả session sạch (không delta + không việc dang dở) → chỉ nói "session sạch", bỏ toàn bộ khung dưới.

═══════ KHỐI A · LƯU TRI THỨC BỀN (chờ tôi duyệt để vào docs/memory) ═══════
Phạm vi: chỉ DELTA của CHÍNH session này — tính năng mới · quyết định · ràng buộc/mìn vừa phát hiện ·
giả định bị bác bỏ · chỗ tài liệu LỆCH code thực tế. KHÔNG tính thứ tài liệu đã ghi sẵn.

Xác minh & nhãn NGUỒN GỐC (mỗi mục):
- Trước khi nói "chưa có trong tài liệu": grep `HuongDan.txt` + `~/.claude/CLAUDE.md` + memory
  (`~/.claude/projects/C--Projects-DocCongDuc/memory/`) → GHI RÕ từ khóa grep đã dùng.
- Neo mỗi mục vào 1 mốc THẬT trong session rồi gắn: 🟦 tôi đã chốt · ✅ có output thật (trích 1 dòng
  bằng chứng: log/đo đạc/ảnh chụp) · 🟨 mới đề xuất/chưa chắc. Không neo được → 🟨 hoặc bỏ.
  TUYỆT ĐỐI không ghi "đã quyết/đã xong" cho thứ chỉ mới bàn, hoặc mới chạy được từ source mà chưa
  kiểm trên bản `.exe`.

Phân loại rủi ro (chuyển HỘI ĐỒNG, không tự chốt):
- Đụng `DocCongDuc.py` (engine dùng chung: VieNeu, chuẩn hoá tiền/tên, giọng riêng) → [HỘI ĐỒNG].
- Đụng đường đóng gói (`DongGoi.bat`, cờ `--collect-data`, `--hidden-import`) → [HỘI ĐỒNG]: hỏng là
  người dùng cuối không chạy được, mà lỗi chỉ lộ ra trên bản `.exe`.
- Đụng dữ liệu người dùng (`congduc.txt`, `cauhinh.ini`, `noidung.ini`, `tudien.ini`, `giong_rieng/`)
  → [HỘI ĐỒNG] + ⚠RỦI RO CAO.
- Thêm nguồn phát âm thanh thứ N (ngoài `bo_doc`, `nghe_thu`, `xuat_file`) → [HỘI ĐỒNG]: đã có tiền
  lệ chồng tiếng 2 lần.
- LẬT một quyết định đã ghi trong CLAUDE.md / memory → [HỘI ĐỒNG] + ⚠RỦI RO CAO.

Đích đến (chỉ ĐỀ XUẤT):
- `HuongDan.txt` → tài liệu cho người dùng cuối (viết cho người không rành máy tính).
- CLAUDE.md root (`~/.claude/CLAUDE.md`) → chỉ khi là quy ước áp cho mọi dự án.
- memory (`~/.claude/projects/C--Projects-DocCongDuc/memory/`) → Claude Code GHI ĐƯỢC (Write + cập
  nhật MEMORY.md index), nhưng close = propose-first: chỉ ĐỀ XUẤT, chờ duyệt rồi ghi. Chỉ fact BỀN,
  KHÔNG trạng thái tạm.
- Chú thích trong code → khi là cái bẫy phải cảnh báo ngay tại chỗ dễ vấp.

Bảng (không có delta → ghi "không có delta", bỏ bảng):
| # | Nội dung | Loại (tính-năng/quyết-định/ràng-buộc/lệch-doc) | Nhãn | Đích | Trạng thái (net-new/cập-nhật/⚠xung-đột) | Hành động (diff-sau-duyệt / [HỘI ĐỒNG] / memory) |
MEMORY UPDATE: mỗi dòng 1 fact bền, gắn [MỚI] hoặc [THAY ĐỔI: trước X → nay Y].

═══════ KHỐI B · BÀN GIAO NỐI VIỆC (payload dán vào session mới) ═══════
Payload phải GỌN & TỰ-ĐỦ: trỏ đường dẫn thay vì dán nguyên nội dung; DÙNG-MỘT-LẦN.
Mục rỗng ghi "—". Nhãn TIẾN ĐỘ: ✅ xong+bằng chứng · 🔄 đang · ⬜ chưa · ⚠ chặn.

┌──── RESUME — DÁN VÀO SESSION MỚI ────
Dự án DocCongDuc — chương trình đọc tiếng Việt cho chùa. Giao diện mới tên GiongDoc.
Trước khi làm BẤT CỨ GÌ: theo [GIAO THỨC] ở cuối khối này.
[CẢNH BÁO] <"có thể sót phần đầu session" — nếu có; nếu không, bỏ dòng>
[MỐC THỰC ĐỊA] (không có git — dùng mốc vật lý)
  • kiến trúc: <...> · điểm vào: <...>
  • bản `.exe` gần nhất build lúc <mtime GiongDoc.exe> · trạng thái: <chạy được / chưa kiểm / lỗi ...>
  • cú pháp: <ngày giờ chạy py_compile gần nhất, kết quả>
[TÀI LIỆU CẦN ĐỌC] <chỉ mục liên quan việc dưới — KHÔNG đọc cả file>
[VIỆC ĐANG DANG DỞ]  (dừng sạch → "không có việc dang dở; việc kế tiếp = <...>")
  - Mục tiêu: <...>
  - Đã tới đâu (🔄): <...>
  - HÀNH ĐỘNG KẾ TIẾP CHÍNH XÁC: <bước cụ thể + file + lệnh nếu có>
[PLAN / TODO]  ✅ <...> (bằng chứng: <...>) · 🔄 <...> · ⬜ <...> · ⚠ <chặn>: <...>
[QUYẾT ĐỊNH CHỐT — bản rút gọn, CHỈ thứ cần để tiếp việc]
  - 🟦 <...>
[CHỜ TÔI DUYỆT / CÂU HỎI MỞ] <...>
[DOC/MEMORY CHỜ ÁP] <n> đề xuất đã nêu cuối session trước (chưa chắc đã áp) — grep hoặc hỏi trước khi
  dựa vào, đừng giả định.
[FILE ĐÃ ĐỘNG] <path + trạng thái>
[BẪY ĐANG CÓ — dự án này đã vấp thật, đừng vấp lại]
  • Chạy được từ source KHÔNG chứng minh bản `.exe` chạy được. Mọi kết luận về đóng gói phải build
    rồi chạy thật. Đã mất nhiều vòng vì bỏ qua bước này.
  • PyInstaller không tự gói file dữ liệu của package. Thiếu `--collect-data vieneu` → danh sách
    giọng RỖNG; thiếu `--collect-data sea_g2p` → "os error 2" đúng lúc bấm đọc.
  • Mọi nguồn phát tiếng phải có số phiên (xem `bo_doc.py`, `nghe_thu.py`). Quên là chồng tiếng —
    đã đo được 4 tiến trình ffplay cùng chạy.
  • KHÔNG chụp toàn màn hình máy người dùng (đã lỡ bắt trúng dữ liệu công việc của họ 2 lần) và
    KHÔNG chiếm foreground khi họ đang làm việc. Cần xem giao diện → nhờ họ bấm, hoặc đo bằng
    `evaluate_js` trong cửa sổ probe riêng.
  • KHÔNG test bằng file cấu hình thật của người dùng — app tự ghi đè khi đổi thiết lập.
  • Đóng cửa sổ xong phải `os._exit(0)`, không thì tiến trình treo lại ôm vài GB RAM.
[VIỆC ĐỖ (parked)] <thread phụ — đừng làm ngay>

[GIAO THỨC TIẾP TỤC — session mới PHẢI theo, đúng thứ tự]
1. XÁC MINH THỰC ĐỊA trước khi tin gói (KHÔNG có git, nên):
   `ls -la` thư mục gốc · `py -c "import glob,py_compile;[py_compile.compile(f,doraise=True) for f in ['GiongDoc.py']+glob.glob('giaodien/*.py')]"` ·
   kiểm bundle: `_internal\ui\index.html`, `_internal\sea_g2p\sea_g2p.bin`,
   `_internal\vieneu\assets\voices_v3_turbo.json` · đọc `GiongDoc-loi.log` nếu có.
   Đối chiếu [MỐC THỰC ĐỊA].
2. RECONCILE — thực địa THẮNG gói: "HÀNH ĐỘNG KẾ TIẾP" đã xong (có bằng chứng) → bỏ, nhảy mục kế.
   Lệch vật chất (quyết định đã chốt bị đụng / task đổi bản chất) → DỪNG, báo tôi. Lệch vặt → ghi
   chú 1 dòng rồi tiếp.
3. Đọc CHỈ [TÀI LIỆU CẦN ĐỌC].
4. PHÂN LOẠI hành động kế tiếp:
   • ĐƠN GIẢN → nói 1 câu "đang làm X" rồi TỰ LÀM, báo cáo sau.
   • PHỨC TẠP / HỘI ĐỒNG (engine `DocCongDuc.py` · đường đóng gói · dữ liệu người dùng · nguồn phát
     âm thanh mới · LẬT quyết định đã chốt) → DỪNG, lên plan, propose, chờ tôi.
5. Định XÂY TIẾP lên mục ✅ → tự kiểm bằng chứng trước, đừng tin nhãn suông. Riêng mục nào có chữ
   "chưa kiểm trên .exe" thì coi như CHƯA XONG.
└──── HẾT RESUME ────
═══════ HẾT ═══════
