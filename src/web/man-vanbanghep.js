/* Giọng Việt — Màn hình 6: Văn bản ghép (Live Data & Template Engine).
   Dựng hình từ trạng thái, khớp 100% với thiết kế GiongDoc - Văn bản ghép.dc.html. */

'use strict';

function svgIcon(name, size = 14) {
  if (name === 'refresh' || name === 'sync') {
    return `<svg width="${size}" height="${size}" viewBox="0 0 24 24" stroke="currentColor" stroke-width="1.8" fill="none" stroke-linecap="round" stroke-linejoin="round"><path d="M20 12a8 8 0 11-2.3-5.7"/><path d="M20 4v4h-4"/></svg>`;
  }
  if (name === 'chevron_left' || name === 'back') {
    return `<svg width="${size}" height="${size}" viewBox="0 0 24 24" stroke="currentColor" stroke-width="1.8" fill="none" stroke-linecap="round" stroke-linejoin="round"><path d="M15 18l-6-6 6-6"/></svg>`;
  }
  if (name === 'chevron_down' || name === 'mui') {
    return `<svg width="${size}" height="${size}" viewBox="0 0 24 24" stroke="currentColor" stroke-width="1.8" fill="none" stroke-linecap="round"><path d="M6 9.5l6 6 6-6"/></svg>`;
  }
  if (name === 'check' || name === 'tich') {
    return `<svg width="${size}" height="${size}" viewBox="0 0 24 24" stroke="currentColor" stroke-width="2.2" fill="none" stroke-linecap="round" stroke-linejoin="round"><path d="M5 12.5l4.5 4.5L19 7"/></svg>`;
  }
  if (name === 'plus' || name === 'cong') {
    return `<svg width="${size}" height="${size}" viewBox="0 0 24 24" stroke="currentColor" stroke-width="2" fill="none" stroke-linecap="round"><path d="M12 5v14M5 12h14"/></svg>`;
  }
  return '';
}

const DANH_SACH_SHEET_MAU = [
  'Công đức & Thiện nguyện',
  'Thu học phí & Phụ huynh',
  'Lương thưởng & Doanh nghiệp',
  'Bán hàng & Chốt đơn',
  'Lịch trực & Phân công',
  'Tổ dân phố & Phường xã',
  'Trang tính1',
  'Sheet1'
];

const GOOGLE_SHEET_MAC_DINH = 'https://docs.google.com/spreadsheets/d/1SVg-mnMl1wwtZHW2HkGAWGUhROdO2MsHUYgI9uxzi2U/edit?usp=sharing';

const EXCEL_MAC_DINH_LOCAL = 'data/mau_google_sheets/Mau_Du_Lieu_Giong_Viet.xlsx';

const MAU_VAN_BAN_GHEP_MAC_DINH = {
  mauHienTai: 0,
  nav: 0,
  stale: false,
  menuMauOpen: false,
  modalTaoMoi: false,
  maus: [
    {
      id: 'congduc',
      name: '🌸 Công đức chùa & Thiện nguyện',
      preset: 'congduc',
      srcType: 0,
      srcVal: GOOGLE_SHEET_MAC_DINH,
      sheet: 'Công đức & Thiện nguyện',
      sheetOpts: DANH_SACH_SHEET_MAU,
      headRow: 'Dòng 1',
      autoSync: true,
      cols: [
        { letter: 'A', head: 'Họ và tên', use: 'Tên người {ten}', varName: '{ten}', read: 'Tên riêng' },
        { letter: 'B', head: 'Địa chỉ / Pháp danh', use: 'Địa chỉ {diachi}', varName: '{diachi}', read: 'Tên riêng' },
        { letter: 'C', head: 'Số tiền công đức', use: 'Số tiền {sotien}', varName: '{sotien}', read: 'Số tiền' },
        { letter: 'D', head: 'Ngày nộp', use: 'Ngày tháng {ngay}', varName: '{ngay}', read: 'Ngày tháng' },
        { letter: 'E', head: 'Ghi chú', use: 'Bỏ qua', varName: '', read: 'Đọc thường' }
      ],
      rows: [
        ['Nguyễn Văn An', 'Phật tử Diệu Tâm - TP. Hà Nội', '2.000.000', '15/08/2026', 'Cúng dường đúc chuông'],
        ['Trần Thị Bích', 'Tổ 5 Phường Bến Nghé Q1 TP.HCM', '1.500.000', '16/08/2026', 'Hộ trì Tam Bảo'],
        ['Lê Hoàng Long', 'Pháp danh Minh Trí - TP. Đà Nẵng', '5.000.000', '16/08/2026', 'Tu bổ chánh điện'],
        ['Phạm Thị Dung', 'Gia đình bà Phúc Lâm - Cần Thơ', '3.000.000', '17/08/2026', 'Cầu an gia đạo'],
        ['Hoàng Minh Đức', 'Phật tử Thiện Nhân - Hải Phòng', '1.000.000', '17/08/2026', 'Đóng góp mua ngói'],
        ['Vũ Thị Mai', 'Thôn 2 Xã Đông Mỹ Thanh Trì', '500.000', '18/08/2026', 'Cúng dường Trai tăng'],
        ['Đỗ Tuấn Kiệt', 'Công ty TNHH Hưng Thịnh', '10.000.000', '18/08/2026', 'Cúng dường tạc tượng'],
        ['Bùi Thu Hà', 'Phật tử Diệu Hòa - Nam Định', '800.000', '19/08/2026', 'Công đức tu tạo'],
        ['Ngô Quang Hải', 'Số 12 Đường Hùng Vương Nha Trang', '2.500.000', '19/08/2026', 'Hộ trì chùa'],
        ['Dương Thị Tuyết', 'Pháp danh Ngọc Liên - TP. Huế', '1.200.000', '20/08/2026', 'Cầu siêu tiên linh'],
        ['Lý Minh Khang', 'Tập thể cựu sinh viên K45', '4.000.000', '20/08/2026', 'Đúc đại hồng chung'],
        ['Đặng Thị Hằng', 'Gia đình cụ Nguyễn Văn Sửu - Bắc Ninh', '6.000.000', '21/08/2026', 'Xây dựng giảng đường'],
        ['Mai Văn Thắng', 'Phật tử Chúc An - Quảng Ninh', '2.000.000', '21/08/2026', 'Cúng dường đèn dầu'],
        ['Trịnh Thùy Linh', 'Số 45 Lê Lợi TP. Vinh', '1.500.000', '22/08/2026', 'Hộ trì Tam Bảo'],
        ['Phan Thanh Tùng', 'Khu đô thị Ecopark Hưng Yên', '3.500.000', '22/08/2026', 'Phát tâm làm đường'],
        ['Võ Thị Kim Oanh', 'Pháp danh Tịnh Nhã - Bình Dương', '2.000.000', '23/08/2026', 'Cúng dường hương hoa'],
        ['Lương Thế Vinh', 'Phật tử Quảng Tuệ - Thái Nguyên', '1.000.000', '23/08/2026', 'Tu tạo Tam Bảo'],
        ['Đoàn Hải Yến', 'Gia đình bác sĩ Hoàng Tuấn - Vũng Tàu', '5.000.000', '24/08/2026', 'Cúng dường tượng Phật'],
        ['Trương Văn Cường', 'Phố Cổ Hội An Quảng Nam', '1.800.000', '24/08/2026', 'Hộ trì tu viện'],
        ['Cao Thị Lan', 'Pháp danh Diệu Âm - Kiên Giang', '700.000', '25/08/2026', 'Cúng dường gạo chay'],
        ['Hồ Quốc Bảo', 'Số 88 Trần Hưng Đạo Quy Nhơn', '3.000.000', '25/08/2026', 'Xây cổng Tam Quan'],
        ['Đinh Thị Thu', 'Thôn Thượng Xã Ninh Hải Ninh Bình', '1.000.000', '26/08/2026', 'Cầu bình an'],
        ['Tạ Quang Minh', 'Phật tử Trí Đức - Lâm Đồng', '2.200.000', '26/08/2026', 'Hộ trì chư tăng'],
        ['Nguyễn Thị Ngọc Ánh', 'Pháp danh Huệ Tâm - Đồng Nai', '1.500.000', '26/08/2026', 'Cúng dường kinh sách'],
        ['Chùa Viên Giác', 'Hội Phật tử Đạo tràng Pháp Hoa', '15.000.000', '26/08/2026', 'Cúng dường đại lễ']
      ],
      tongSo: 25,
      rule: { trong: true, trung: false, dupCol: 'A', thutu: true, group: false },
      on: { dau: true, giua: true, cuoi: true },
      sauMoi: '20',
      T: {
        dau: 'Nam Mô Bổn Sư Thích Ca Mâu Ni Phật.\nBan Trị sự xin thành tâm tán thán công đức của quý Phật tử và các nhà hảo tâm đã phát tâm cúng dường Tam Bảo.',
        mau: '{ten}, {diachi}, phát tâm công đức số tiền {sotien}.',
        giua: 'Kính chúc quý Phật tử cùng gia quyến luôn thân tâm an lạc, vạn sự cát tường.',
        cuoi: 'Nguyện đem công đức này, hướng về khắp tất cả, đệ tử và chúng sanh, đều trọn thành Phật đạo.\nNam Mô A Di Đà Phật.'
      }
    },
    {
      id: 'hocphi',
      name: '🎓 Thu học phí & Họp phụ huynh',
      preset: 'hocphi',
      srcType: 0,
      srcVal: GOOGLE_SHEET_MAC_DINH,
      sheet: 'Thu học phí & Phụ huynh',
      sheetOpts: DANH_SACH_SHEET_MAU,
      headRow: 'Dòng 1',
      autoSync: true,
      cols: [
        { letter: 'A', head: 'Họ và tên học sinh', use: 'Tên người {ten}', varName: '{ten}', read: 'Tên riêng' },
        { letter: 'B', head: 'Lớp / Khóa học', use: 'Địa chỉ {diachi}', varName: '{diachi}', read: 'Tên riêng' },
        { letter: 'C', head: 'Số tiền cần nộp', use: 'Số tiền {sotien}', varName: '{sotien}', read: 'Số tiền' },
        { letter: 'D', head: 'Hạn nộp', use: 'Ngày tháng {ngay}', varName: '{ngay}', read: 'Ngày tháng' },
        { letter: 'E', head: 'Tình trạng', use: 'Bỏ qua', varName: '', read: 'Đọc thường' }
      ],
      rows: [
        ['Nguyễn Minh Quân', 'Lớp 9A1 - THCS Chu Văn An', '1.850.000', '05/09/2026', 'Chưa hoàn thành'],
        ['Trần Bảo Ngọc', 'Lớp 9A1 - THCS Chu Văn An', '1.850.000', '05/09/2026', 'Đã nộp 1.000.000'],
        ['Lê Tuấn Kiệt', 'Lớp 9A2 - THCS Chu Văn An', '2.100.000', '05/09/2026', 'Chưa hoàn thành'],
        ['Phạm Thảo Vy', 'Lớp 10 Chuyên Toán - THPT Amsterdam', '2.500.000', '10/09/2026', 'Chưa hoàn thành'],
        ['Hoàng Gia Bảo', 'Lớp 11A3 - THPT Lương Thế Vinh', '2.200.000', '10/09/2026', 'Chưa hoàn thành'],
        ['Vũ Phương Linh', 'Lớp 12A1 - THPT Kim Liên', '2.600.000', '12/09/2026', 'Chưa hoàn thành'],
        ['Đỗ Hoàng Nam', 'Lớp 6A4 - THCS Lê Quý Đôn', '1.650.000', '05/09/2026', 'Chưa hoàn thành'],
        ['Bùi Gia Hưng', 'Lớp 7A2 - THCS Trưng Vương', '1.750.000', '08/09/2026', 'Chưa hoàn thành'],
        ['Ngô Thanh Trúc', 'Lớp 8A1 - THCS Giảng Võ', '1.800.000', '08/09/2026', 'Chưa hoàn thành'],
        ['Dương Khánh Linh', 'Lớp 10A5 - THPT Thăng Long', '2.300.000', '10/09/2026', 'Chưa hoàn thành'],
        ['Lý Hải Đăng', 'Lớp 11A2 - THPT Trần Phú', '2.200.000', '10/09/2026', 'Chưa hoàn thành'],
        ['Đặng Ngọc Mai', 'Lớp 12 Chuyên Anh - THPT Chuyên Hà Nội', '2.800.000', '15/09/2026', 'Chưa hoàn thành'],
        ['Mai Quốc Tuấn', 'Lớp 8A3 - THCS Nghĩa Tân', '1.800.000', '08/09/2026', 'Chưa hoàn thành'],
        ['Trịnh Thùy Trang', 'Lớp 9A3 - THCS Cầu Giấy', '1.900.000', '05/09/2026', 'Chưa hoàn thành'],
        ['Phan Đức Anh', 'Lớp 11A1 - THPT Việt Đức', '2.250.000', '10/09/2026', 'Chưa hoàn thành'],
        ['Võ Tường Vy', 'Lớp 7A1 - THCS Đoàn Thị Điểm', '1.700.000', '08/09/2026', 'Chưa hoàn thành'],
        ['Lương Minh Triết', 'Lớp 10A2 - THPT Phan Đình Phùng', '2.400.000', '10/09/2026', 'Chưa hoàn thành'],
        ['Đoàn Yến Nhi', 'Lớp 12D1 - THPT Nhân Chính', '2.500.000', '12/09/2026', 'Chưa hoàn thành'],
        ['Trương Hữu Phước', 'Lớp 9A5 - THCS Tân Định', '1.850.000', '05/09/2026', 'Chưa hoàn thành'],
        ['Cao Thùy Dương', 'Lớp 8A2 - THCS Dịch Vọng Hậu', '1.800.000', '08/09/2026', 'Chưa hoàn thành'],
        ['Hồ Anh Dũng', 'Lớp 11A4 - THPT Quang Trung', '2.200.000', '10/09/2026', 'Chưa hoàn thành'],
        ['Đinh Mỹ Uyên', 'Lớp 10A1 - THPT Cầu Giấy', '2.350.000', '10/09/2026', 'Chưa hoàn thành'],
        ['Tạ Đình Phong', 'Lớp 12A3 - THPT Yên Hòa', '2.550.000', '12/09/2026', 'Chưa hoàn thành'],
        ['Nguyễn Khánh Huyền', 'Lớp 6A1 - THCS Marie Curie', '1.600.000', '05/09/2026', 'Chưa hoàn thành'],
        ['Trần Nhật Minh', 'Lớp 9A2 - THCS Archimedes', '2.000.000', '05/09/2026', 'Chưa hoàn thành']
      ],
      tongSo: 25,
      rule: { trong: true, trung: false, dupCol: 'A', thutu: true, group: false },
      on: { dau: true, giua: false, cuoi: true },
      sauMoi: '20',
      T: {
        dau: 'Kính gửi quý phụ huynh và các em học sinh thông báo thu các khoản đầu kỳ:',
        mau: 'Học sinh {ten}, lớp {diachi}, số tiền cần nộp là {sotien}, hạn hoàn thành trước {ngay}.',
        giua: '',
        cuoi: 'Nhà trường trân trọng cảm ơn sự phối hợp của quý phụ huynh.'
      }
    },
    {
      id: 'khenthuong',
      name: '🏢 Lương thưởng & Thi đua công ty',
      preset: 'khenthuong',
      srcType: 0,
      srcVal: GOOGLE_SHEET_MAC_DINH,
      sheet: 'Lương thưởng & Doanh nghiệp',
      sheetOpts: DANH_SACH_SHEET_MAU,
      headRow: 'Dòng 1',
      autoSync: true,
      cols: [
        { letter: 'A', head: 'Họ và tên', use: 'Tên người {ten}', varName: '{ten}', read: 'Tên riêng' },
        { letter: 'B', head: 'Đơn vị / Phòng ban', use: 'Địa chỉ {diachi}', varName: '{diachi}', read: 'Tên riêng' },
        { letter: 'C', head: 'Thành tích đạt được', use: 'Ghi chú {ghichu}', varName: '{ghichu}', read: 'Đọc thường' },
        { letter: 'D', head: 'Mức khen thưởng', use: 'Số tiền {sotien}', varName: '{sotien}', read: 'Số tiền' },
        { letter: 'E', head: 'Xếp loại', use: 'Bỏ qua', varName: '', read: 'Đọc thường' }
      ],
      rows: [
        ['Nguyễn Thành Long', 'Phòng Kỹ thuật & R&D', 'Xuất sắc hoàn thành dự án AI Core', '8.000.000', 'Loại A+'],
        ['Trần Thu Trang', 'Phòng Kinh doanh & Khách hàng', 'Vượt 150% chỉ tiêu doanh số tháng 8', '6.500.000', 'Loại A'],
        ['Lê Văn Hùng', 'Phòng Vận hành & Hệ thống', 'Đảm bảo hệ thống 99.99% uptime', '5.000.000', 'Loại A'],
        ['Phạm Ngọc Mai', 'Phòng Marketing & Truyền thông', 'Chiến dịch tiếp cận 500.000 người dùng', '5.500.000', 'Loại A'],
        ['Hoàng Quốc Tuấn', 'Bộ phận Chăm sóc Khách hàng', 'Tỉ lệ hài lòng khách hàng đạt 98.5%', '4.500.000', 'Loại A'],
        ['Vũ Thùy Dương', 'Phòng Kế toán & Tài chính', 'Báo cáo quyết toán chính xác trước hạn', '4.000.000', 'Loại B+'],
        ['Đỗ Minh Khoa', 'Phòng Kỹ thuật & R&D', 'Khắc phục hoàn toàn lỗi giao diện', '6.000.000', 'Loại A'],
        ['Bùi Thị Phương', 'Phòng Hành chính & Nhân sự', 'Tổ chức thành công hội nghị công ty', '3.500.000', 'Loại B+'],
        ['Ngô Đình Trọng', 'Phòng Kinh doanh 2', 'Mở rộng mạng lưới 12 đại lý mới', '5.000.000', 'Loại A'],
        ['Dương Văn Nam', 'Bộ phận Kho vận Logistics', 'Giao nhận chính xác không trễ hẹn', '3.800.000', 'Loại B+'],
        ['Lý Thị Thu Hương', 'Phòng Đảm bảo Chất lượng QA', 'Xử lý sớm 25 điểm tối ưu quan trọng', '5.000.000', 'Loại A'],
        ['Đặng Quốc Việt', 'Phòng Phát triển Đối tác', 'Ký kết 3 hợp đồng chiến lược lớn', '7.000.000', 'Loại A'],
        ['Mai Thị Quỳnh Chi', 'Phòng Thiết kế UI/UX', 'Hoàn thiện bộ giao diện người dùng mới', '4.800.000', 'Loại A'],
        ['Trịnh Văn Hưng', 'Phòng Hạ tầng Mạng', 'Tối ưu máy chủ tiết kiệm 30% chi phí', '6.000.000', 'Loại A'],
        ['Phan Thị Ngọc Hà', 'Phòng CSKH VIP', 'Xử lý 100% phản hồi trong 15 phút', '4.200.000', 'Loại B+'],
        ['Võ Minh Tâm', 'Phòng Kinh doanh Quốc tế', 'Đạt mốc 2.000 khách hàng quốc tế', '5.800.000', 'Loại A'],
        ['Lương Thu Uyên', 'Phòng Đào tạo Nội bộ', 'Xây dựng giáo trình đào tạo chuẩn mực', '3.500.000', 'Loại B+'],
        ['Đoàn Văn Thịnh', 'Bộ phận Xử lý Âm thanh DSP', 'Nâng cao chất lượng âm thanh trong trẻo', '6.500.000', 'Loại A'],
        ['Trương Thị Hạnh', 'Phòng Kế toán Tổng hợp', 'Quản lý tài chính minh bạch hiệu quả', '4.000.000', 'Loại B+'],
        ['Cao Đình Luật', 'Phòng Pháp chế Bản quyền', 'Hoàn tất đăng ký bản quyền phần mềm', '5.000.000', 'Loại A'],
        ['Hồ Văn Tiến', 'Phòng An toàn An ninh Mạng', 'Bảo vệ an toàn tuyệt đối cơ sở dữ liệu', '6.000.000', 'Loại A'],
        ['Đinh Thị Thảo', 'Phòng Biên tập Nội dung', 'Biên soạn trọn bộ mẫu văn bản chuẩn', '4.500.000', 'Loại A'],
        ['Tạ Minh Châu', 'Phòng Bán hàng Doanh nghiệp', 'Doanh thu quý vượt mức chỉ tiêu 130%', '6.200.000', 'Loại A'],
        ['Nguyễn Thị Thúy', 'Phòng Đời sống Nhân viên', 'Chăm sóc chu đáo phúc lợi tập thể', '3.500.000', 'Loại B+'],
        ['Tập thể Công ty', 'Toàn thể Cán bộ Nhân viên', 'Đoàn kết sáng tạo và đổi mới vượt bậc', '20.000.000', 'Tuyên dương']
      ],
      tongSo: 25,
      rule: { trong: true, trung: false, dupCol: 'A', thutu: true, group: false },
      on: { dau: true, giua: false, cuoi: true },
      sauMoi: '20',
      T: {
        dau: 'Ban Giám đốc biểu dương và chúc mừng các cá nhân có thành tích xuất sắc:',
        mau: 'Chúc mừng anh chị {ten}, phòng {diachi}, đạt thành tích {ghichu}, mức thưởng {sotien}.',
        giua: '',
        cuoi: 'Chúc toàn thể cán bộ nhân viên tiếp tục nỗ lực và gặt hái thêm nhiều thành công.'
      }
    },
    {
      id: 'donhang',
      name: '🛍️ Bán hàng & Chốt đơn Livestream',
      preset: 'donhang',
      srcType: 0,
      srcVal: GOOGLE_SHEET_MAC_DINH,
      sheet: 'Bán hàng & Chốt đơn',
      sheetOpts: DANH_SACH_SHEET_MAU,
      headRow: 'Dòng 1',
      autoSync: true,
      cols: [
        { letter: 'A', head: 'Tên khách hàng', use: 'Tên người {ten}', varName: '{ten}', read: 'Tên riêng' },
        { letter: 'B', head: 'Số điện thoại', use: 'Ghi chú {ghichu}', varName: '{ghichu}', read: 'Số điện thoại' },
        { letter: 'C', head: 'Sản phẩm đặt mua', use: 'Địa chỉ {diachi}', varName: '{diachi}', read: 'Đọc thường' },
        { letter: 'D', head: 'Tổng thanh toán', use: 'Số tiền {sotien}', varName: '{sotien}', read: 'Số tiền' },
        { letter: 'E', head: 'Địa chỉ giao hàng', use: 'Bỏ qua', varName: '', read: 'Đọc thường' }
      ],
      rows: [
        ['Chị Nguyễn Lan Anh', '0912.345.678', 'Bộ 2 hộp trà hoa vàng đặc sản', '1.250.000', 'Hàng Bạc Hoàn Kiếm Hà Nội'],
        ['Anh Trần Tuấn Đạt', '0988.765.432', 'Máy xông tinh dầu + 3 chai tinh dầu quế', '890.000', 'Vinhomes Central Park Bình Thạnh'],
        ['Chị Lê Thu Trang', '0903.112.233', 'Set 5 váy linen thiết kế cao cấp', '2.150.000', 'Lê Duẩn Quận 1 TP.HCM'],
        ['Anh Phạm Hùng Cường', '0977.889.900', 'Bộ dụng cụ cơ khí 120 chi tiết', '1.450.000', 'Trần Phú TP. Đà Nẵng'],
        ['Chị Hoàng Mai Ly', '0945.667.889', 'Nồi chiên không dầu điện tử 8 lít', '1.690.000', 'Văn Quán Hà Đông Hà Nội'],
        ['Anh Vũ Đình Trọng', '0932.445.566', 'Đôi giày thể thao running size 42', '980.000', 'Quang Trung TP. Hải Phòng'],
        ['Chị Đỗ Phương Thảo', '0966.123.789', 'Bộ dưỡng da thảo mộc cao cấp', '1.850.000', 'Hùng Vương TP. Huế'],
        ['Anh Bùi Quang Khải', '0915.778.899', 'Loa bluetooth công suất lớn chống nước', '1.100.000', 'Nguyễn Thị Minh Khai Cần Thơ'],
        ['Chị Ngô Thùy Tiên', '0983.556.677', 'Vòng tay phong thủy thạch anh tự nhiên', '650.000', 'Phan Bội Châu Nha Trang'],
        ['Anh Dương Gia Huy', '0909.223.344', 'Đồng hồ cơ lộ máy dây da thật', '2.800.000', 'Điện Biên Phủ Quận 3 TP.HCM'],
        ['Chị Lý Kim Oanh', '0972.990.011', 'Bộ chăn ga cotton lụa Hàn Quốc', '1.750.000', 'Phố Nối Hưng Yên'],
        ['Anh Đặng Văn Long', '0938.667.788', 'Bình giữ nhiệt inox 316 thể tích 1.5L', '420.000', 'TP. Bắc Ninh'],
        ['Chị Mai Thanh Vân', '0961.445.566', 'Set 3 son môi kem lì cao cấp', '790.000', 'TP. Vũng Tàu'],
        ['Anh Trịnh Quốc Bảo', '0942.112.233', 'Bộ cần câu máy carbon 3.6m', '1.350.000', 'TP. Nam Định'],
        ['Chị Phan Diệu Linh', '0987.334.455', 'Máy ép chậm hoa quả đa năng', '1.990.000', 'TP. Thái Nguyên'],
        ['Anh Võ Thành Đạt', '0918.556.677', 'Balo du lịch chống nước cổng sạc USB', '580.000', 'TP. Quy Nhơn'],
        ['Chị Lương Ngọc Bích', '0908.776.655', 'Thùng 12 hộp sữa hạt óc chó hạnh nhân', '620.000', 'TP. Biên Hòa Đồng Nai'],
        ['Anh Đoàn Thế Anh', '0975.223.344', 'Camera wifi thông minh 360 độ xoay tự động', '850.000', 'TP. Hạ Long Quảng Ninh'],
        ['Chị Trương Hải Yến', '0936.889.900', 'Máy massage cổ vai gáy hồng ngoại', '1.150.000', 'TP. Thanh Hóa'],
        ['Anh Cao Minh Đức', '0968.112.233', 'Bàn phím cơ không dây Bluetooth gaming', '1.490.000', 'TP. Thủ Đức TP.HCM'],
        ['Chị Hồ Thị Nga', '0949.556.677', 'Set 10 khăn mặt sợi tre kháng khuẩn', '290.000', 'TP. Rạch Giá Kiên Giang'],
        ['Anh Đinh Trọng Hiếu', '0982.778.899', 'Đèn bàn chống cận cảm ứng thông minh', '480.000', 'TP. Long Xuyên An Giang'],
        ['Chị Tạ Thúy Hằng', '0916.334.455', 'Bộ ấm chén gốm sứ men rạn mạ vàng', '1.600.000', 'TP. Buôn Ma Thuột Đắk Lắk'],
        ['Anh Nguyễn Văn Thái', '0906.990.011', 'Khóa cửa vân tay thông minh FaceID', '3.900.000', 'Quận Cầu Giấy Hà Nội'],
        ['Chị Trần Ngọc Diệp', '0971.223.344', 'Bộ 6 hộp yến sào chưng đường phèn', '1.550.000', 'Quận Phú Nhuận TP.HCM']
      ],
      tongSo: 25,
      rule: { trong: true, trung: false, dupCol: 'A', thutu: true, group: false },
      on: { dau: true, giua: false, cuoi: true },
      sauMoi: '20',
      T: {
        dau: 'Cảm ơn quý khách đã theo dõi và đặt hàng trong phiên livestream hôm nay:',
        mau: 'Khách hàng {ten}, số điện thoại {ghichu}, đặt mua {diachi}, tổng tiền {sotien}.',
        giua: '',
        cuoi: 'Đơn hàng của quý khách sẽ được đóng gói và giao sớm nhất.'
      }
    },
    {
      id: 'lichtruc',
      name: '📅 Lịch trực & Phân công công tác',
      preset: 'lichtruc',
      srcType: 0,
      srcVal: GOOGLE_SHEET_MAC_DINH,
      sheet: 'Lịch trực & Phân công',
      sheetOpts: DANH_SACH_SHEET_MAU,
      headRow: 'Dòng 1',
      autoSync: true,
      cols: [
        { letter: 'A', head: 'Họ tên cán bộ', use: 'Tên người {ten}', varName: '{ten}', read: 'Tên riêng' },
        { letter: 'B', head: 'Địa điểm / Phòng trực', use: 'Địa chỉ {diachi}', varName: '{diachi}', read: 'Tên riêng' },
        { letter: 'C', head: 'Thời gian trực', use: 'Ngày tháng {ngay}', varName: '{ngay}', read: 'Ngày tháng' },
        { letter: 'D', head: 'Ca trực', use: 'Ghi chú {ghichu}', varName: '{ghichu}', read: 'Đọc thường' },
        { letter: 'E', head: 'Ghi chú nhiệm vụ', use: 'Bỏ qua', varName: '', read: 'Đọc thường' }
      ],
      rows: [
        ['Bác sĩ Nguyễn Văn Hoàng', 'Phòng Cấp cứu Trung tâm', 'Thứ Hai ngày 01/09/2026', 'Ca trực đêm 24h', 'Chỉ huy cấp cứu ngoại viện'],
        ['Điều dưỡng Trần Thị Bích', 'Khu điều trị nội trú Tầng 3', 'Thứ Hai ngày 01/09/2026', 'Ca đêm 19h đến 7h', 'Theo dõi bệnh nhân hậu phẫu'],
        ['Dược sĩ Lê Minh Tâm', 'Kho Dược & Cấp phát thuốc', 'Thứ Hai ngày 01/09/2026', 'Ca ngày 7h đến 17h', 'Cung ứng thuốc vật tư y tế'],
        ['Bác sĩ Phạm Quỳnh Nga', 'Khoa Khám bệnh Ngoại trú', 'Thứ Ba ngày 02/09/2026', 'Ca ngày 7h đến 17h', 'Khám sàng lọc ban ngày'],
        ['Kỹ thuật viên Hoàng Tuấn', 'Phòng Chẩn đoán Hình ảnh X-Quang', 'Thứ Ba ngày 02/09/2026', 'Ca đêm 19h đến 7h', 'Chụp CT Scanner và X-quang'],
        ['Bác sĩ Vũ Hải Đăng', 'Phòng Mổ cấp cứu Trung tâm', 'Thứ Ba ngày 02/09/2026', 'Ca trực đêm 24h', 'Phẫu thuật viên chính thường trực'],
        ['Điều dưỡng Đỗ Thúy Hà', 'Khoa Hồi sức Sơ sinh Nhi', 'Thứ Tư ngày 03/09/2026', 'Ca ngày 7h đến 17h', 'Chăm sóc lồng ấp sơ sinh'],
        ['Bác sĩ Bùi Quốc Hùng', 'Khoa Tim mạch Can thiệp', 'Thứ Tư ngày 03/09/2026', 'Ca trực đêm 24h', 'Xử trí cấp cứu tim mạch'],
        ['Dược sĩ Ngô Phương Thảo', 'Quầy phát thuốc BHYT Tầng 1', 'Thứ Tư ngày 03/09/2026', 'Ca ngày 7h đến 17h', 'Kiểm tra và hướng dẫn dùng thuốc'],
        ['Kỹ thuật viên Dương Minh', 'Phòng Xét nghiệm Huyết học', 'Thứ Năm ngày 04/09/2026', 'Ca đêm 19h đến 7h', 'Xét nghiệm sinh hóa máu cấp cứu'],
        ['Bác sĩ Lý Gia Bảo', 'Khoa Chấn thương Chỉnh hình', 'Thứ Năm ngày 04/09/2026', 'Ca ngày 7h đến 17h', 'Xử trí bó bột nẹp cố định'],
        ['Điều dưỡng Đặng Mai Lan', 'Khoa Thận nhân tạo Lọc máu', 'Thứ Năm ngày 04/09/2026', 'Ca sáng 6h đến 14h', 'Vận hành máy lọc máu chu kỳ'],
        ['Bác sĩ Mai Thế Cường', 'Phòng Khám Răng Hàm Mặt', 'Thứ Sáu ngày 05/09/2026', 'Ca ngày 7h đến 17h', 'Điều trị nha khoa và tiểu phẫu'],
        ['Kỹ thuật viên Trịnh Văn Nam', 'Trung tâm Nội soi Tiêu hóa', 'Thứ Sáu ngày 05/09/2026', 'Ca ngày 7h đến 17h', 'Nội soi dạ dày đại tràng'],
        ['Bác sĩ Phan Thị Thu Thủy', 'Khoa Sản phụ khoa', 'Thứ Sáu ngày 05/09/2026', 'Ca trực đêm 24h', 'Đỡ đẻ và theo dõi chuyển dạ'],
        ['Điều dưỡng Võ Thị Kim Huệ', 'Phòng Tiêm chủng Vắc xin', 'Thứ Bảy ngày 06/09/2026', 'Ca sáng 7h đến 12h', 'Tư vấn tiêm chủng vắc xin'],
        ['Bác sĩ Lương Đình Dũng', 'Khoa Y học Cổ truyền', 'Thứ Bảy ngày 06/09/2026', 'Ca ngày 7h đến 17h', 'Châm cứu bấm huyệt trị liệu'],
        ['Kỹ thuật viên Đoàn Văn Hải', 'Phòng Đo Điện tim & Siêu âm', 'Thứ Bảy ngày 06/09/2026', 'Ca sáng 7h đến 12h', 'Siêu âm Doppler tim mạch'],
        ['Bác sĩ Trương Quốc Thắng', 'Khoa Truyền nhiễm & Nhiệt đới', 'Chủ Nhật ngày 07/09/2026', 'Ca trực đêm 24h', 'Giám sát cách ly phòng dịch'],
        ['Điều dưỡng Cao Thị Mỹ Linh', 'Khoa Cấp cứu Đa khoa', 'Chủ Nhật ngày 07/09/2026', 'Ca đêm 19h đến 7h', 'Tiếp nhận phân loại bệnh nhân'],
        ['Bác sĩ Hồ Đức Trọng', 'Trực Lãnh đạo Bệnh viện', 'Chủ Nhật ngày 07/09/2026', 'Ca trực 24h', 'Điều hành toàn diện công tác'],
        ['Dược sĩ Đinh Văn Hậu', 'Kho Dược Trung tâm', 'Chủ Nhật ngày 07/09/2026', 'Ca ngày 7h đến 17h', 'Kiểm kê xuất nhập kho dược phẩm'],
        ['Bảo vệ Tạ Văn Bình', 'Cổng chính & Khuôn viên', 'Hàng ngày 24/24', 'Ca 12h luân phiên', 'Đảm bảo an ninh trật tự bệnh viện'],
        ['Lái xe Nguyễn Văn Hùng', 'Đội Xe cấp cứu 115', 'Hàng ngày 24/24', 'Thường trực 24h', 'Sẵn sàng chuyển viện khẩn cấp'],
        ['Nhân viên Trần Thị Mùi', 'Sảnh đón tiếp & Hành lang', 'Hàng ngày', 'Ca sáng 6h đến 14h', 'Vệ sinh khử khuẩn môi trường']
      ],
      tongSo: 25,
      rule: { trong: true, trung: false, dupCol: 'A', thutu: true, group: false },
      on: { dau: true, giua: false, cuoi: true },
      sauMoi: '20',
      T: {
        dau: 'Thông báo phân công lịch trực công tác trong tuần:',
        mau: 'Đồng chí {ten}, phụ trách {ghichu}, thời gian {ngay} tại {diachi}.',
        giua: '',
        cuoi: 'Đề nghị các đồng chí nghiêm túc thực hiện nhiệm vụ được giao.'
      }
    },
    {
      id: 'phuongxa',
      name: '🏘️ Tổ dân phố & Thông báo Phường xã',
      preset: 'phuongxa',
      srcType: 0,
      srcVal: GOOGLE_SHEET_MAC_DINH,
      sheet: 'Tổ dân phố & Phường xã',
      sheetOpts: DANH_SACH_SHEET_MAU,
      headRow: 'Dòng 1',
      autoSync: true,
      cols: [
        { letter: 'A', head: 'Chủ hộ', use: 'Tên người {ten}', varName: '{ten}', read: 'Tên riêng' },
        { letter: 'B', head: 'Số nhà / Tổ dân phố', use: 'Địa chỉ {diachi}', varName: '{diachi}', read: 'Tên riêng' },
        { letter: 'C', head: 'Nội dung thông báo', use: 'Ghi chú {ghichu}', varName: '{ghichu}', read: 'Đọc thường' },
        { letter: 'D', head: 'Thời hạn', use: 'Ngày tháng {ngay}', varName: '{ngay}', read: 'Ngày tháng' },
        { letter: 'E', head: 'Ghi chú', use: 'Bỏ qua', varName: '', read: 'Đọc thường' }
      ],
      rows: [
        ['Ông Nguyễn Văn Hùng', 'Số nhà 12 Tổ dân phố 1', 'Nộp quỹ đền ơn đáp nghĩa và vì người nghèo', 'Trước ngày 05/09/2026', 'Mức 100.000đ/hộ'],
        ['Bà Trần Thị Loan', 'Số nhà 34 Tổ dân phố 1', 'Đăng ký khám sức khỏe người cao tuổi miễn phí', 'Trước ngày 08/09/2026', 'Tại Trạm y tế'],
        ['Ông Lê Đình Trọng', 'Số nhà 56 Tổ dân phố 2', 'Tổng vệ sinh môi trường phòng sốt xuất huyết', 'Sáng thứ Bảy 06/09/2026', 'Tại nhà văn hóa'],
        ['Bà Phạm Thị Thúy', 'Số nhà 78 Tổ dân phố 2', 'Kê khai biến động nhân khẩu tạm trú tạm vắng', 'Trước ngày 10/09/2026', 'Nộp công an phường'],
        ['Ông Hoàng Văn Minh', 'Số nhà 90 Tổ dân phố 3', 'Nhận quà thăm hỏi gia đình chính sách thương binh', 'Sáng ngày 02/09/2026', 'Tại trụ sở UBND'],
        ['Bà Vũ Thị Hằng', 'Số nhà 102 Tổ dân phố 3', 'Tham gia hội nghị tiếp xúc cử tri đại biểu HĐND', '14h00 ngày 04/09/2026', 'Nhà văn hóa'],
        ['Ông Đỗ Văn Nam', 'Số nhà 15 Tổ dân phố 4', 'Đăng ký học bổng khuyến học cho học sinh giỏi', 'Trước ngày 12/09/2026', 'Kèm bản sao học bạ'],
        ['Bà Bùi Thị Nga', 'Số nhà 27 Tổ dân phố 4', 'Đóng tiền thu gom rác thải sinh hoạt quý 3', 'Trước ngày 15/09/2026', 'Mức thu 30.000đ/tháng'],
        ['Ông Ngô Quốc Tuấn', 'Số nhà 39 Tổ dân phố 5', 'Cắt tỉa cành cây trước nhà phòng chống mưa bão', 'Trước ngày 07/09/2026', 'Đảm bảo an toàn lưới điện'],
        ['Bà Dương Thị Mai', 'Số nhà 41 Tổ dân phố 5', 'Đăng ký làm căn cước công dân gắn chip cho trẻ', 'Thứ Hai đến thứ Sáu', 'Tại Công an quận'],
        ['Ông Lý Văn Sơn', 'Số nhà 53 Tổ dân phố 6', 'Tham dự ngày hội Đại đoàn kết toàn dân tộc', '8h00 Chủ Nhật 15/11/2026', 'Tại sân thể thao'],
        ['Bà Đặng Thị Hòa', 'Số nhà 65 Tổ dân phố 6', 'Tiêm phòng dại định kỳ cho chó mèo nuôi', 'Sáng Chủ Nhật 07/09/2026', 'Trạm thú y phường'],
        ['Ông Mai Văn Đức', 'Số nhà 77 Tổ dân phố 7', 'Lắp đặt camera an ninh theo mô hình tự quản', 'Trước ngày 20/09/2026', 'Xã hội hóa khu dân cư'],
        ['Bà Trịnh Thị Lan', 'Số nhà 89 Tổ dân phố 7', 'Họp bình xét gia đình văn hóa năm 2026', '19h30 thứ Sáu 11/09/2026', 'Nhà sinh hoạt cộng đồng'],
        ['Ông Phan Văn Thái', 'Số nhà 101 Tổ dân phố 8', 'Kiểm tra an toàn PCCC và trang bị bình chữa cháy', '10/09 đến 20/09/2026', 'Từng hộ gia đình'],
        ['Bà Võ Thị Kim Oanh', 'Số nhà 113 Tổ dân phố 8', 'Đăng ký câu lạc bộ dưỡng sinh thể thao', 'Trước ngày 15/09/2026', 'Phụ nữ và NCT'],
        ['Ông Lương Văn Thành', 'Số nhà 125 Tổ dân phố 9', 'Vận động hiến máu nhân đạo đợt 2 năm 2026', 'Sáng thứ Bảy 12/09/2026', 'Tại Trạm y tế'],
        ['Bà Đoàn Thị Nhàn', 'Số nhà 137 Tổ dân phố 9', 'Thông báo lịch cắt điện phục vụ bảo dưỡng lưới điện', '8h00 đến 12h00 09/09/2026', 'Tổ dân phố 9'],
        ['Ông Trương Văn Long', 'Số nhà 149 Tổ dân phố 10', 'Đăng ký học nghề ngắn hạn miễn phí cho lao động', 'Trước ngày 25/09/2026', 'Trung tâm giáo dục nghề'],
        ['Bà Cao Thị Dung', 'Số nhà 161 Tổ dân phố 10', 'Nhận thông báo thuế đất phi nông nghiệp năm 2026', 'Trước ngày 30/09/2026', 'Tại bộ phận một cửa'],
        ['Ông Hồ Văn Tuấn', 'Số nhà 173 Tổ dân phố 11', 'Khen thưởng học sinh đỗ thủ khoa đại học năm 2026', 'Tối Trung thu 15/08 Âm lịch', 'Tại nhà văn hóa'],
        ['Bà Đinh Thị Thơm', 'Số nhà 185 Tổ dân phố 11', 'Đăng ký nhận cây hoa trang trí ngõ phố xanh sạch', 'Trước ngày 18/09/2026', 'Cảnh quan khu dân cư'],
        ['Ông Tạ Văn Hải', 'Số nhà 197 Tổ dân phố 12', 'Tham gia tổ liên gia an toàn phòng cháy chữa cháy', 'Trước ngày 22/09/2026', 'Tập huấn kỹ năng'],
        ['Bà Nguyễn Thị Huệ', 'Số nhà 209 Tổ dân phố 12', 'Đăng ký tặng quà thiếu nhi nhân dịp Tết Trung thu', 'Trước 10/08 Âm lịch', 'Ban công tác mặt trận'],
        ['Toàn thể nhân dân', '12 Tổ dân phố trên toàn phường', 'Treo cờ Tổ quốc chào mừng ngày Quốc khánh 2/9', '30/08 đến 03/09/2026', 'Treo cờ trang nghiêm']
      ],
      tongSo: 25,
      rule: { trong: true, trung: false, dupCol: 'A', thutu: true, group: false },
      on: { dau: true, giua: false, cuoi: true },
      sauMoi: '20',
      T: {
        dau: 'Ủy ban nhân dân phường kính gửi bà con nhân dân trong khu phố thông báo sau:',
        mau: 'Hộ gia đình ông bà {ten}, {diachi}, {ghichu}, hạn thực hiện {ngay}.',
        giua: '',
        cuoi: 'Kính mong bà con nhân dân phối hợp thực hiện.'
      }
    }
  ]
};

let duLieuVBG = JSON.parse(JSON.stringify(MAU_VAN_BAN_GHEP_MAC_DINH));

/* ---------------------------------------------------------- nhớ mẫu ghép

   Trước đây duLieuVBG là MỘT biến toàn cục duy nhất và không nơi nào lưu nó
   xuống đĩa. Hai hậu quả:

   · Đóng chương trình là mất link Sheet, mất khớp cột, mất bốn khối văn bản
     vừa gõ. Mở lại, bấm "Đồng bộ Live" thì nó kéo về GOOGLE_SHEET_MAC_DINH —
     đúng buổi lễ, máy đọc to danh sách người mẫu.
   · Chân dải trái vẫn in tên hồ sơ đang dùng, nhưng đổi hồ sơ thì mẫu ghép y
     nguyên. Chữ nói một đằng, máy làm một nẻo.

   Nay mỗi hồ sơ giữ mẫu ghép RIÊNG (đúng thiết kế VG-15). Lưu theo hồ sơ là
   tập cha của lưu dùng chung, nên sau này không phải viết bộ chuyển đổi ngược.

   KHÔNG lưu `rows`: một bảng tính 2.000 dòng mà nhét vào hoso-v2.json thì tệp
   phình theo, và henLuuHoSo() JSON.stringify nó mỗi lần dat() — máy yếu đứng
   hình. Dữ liệu tải lại được từ nguồn; cấu hình thì không. `sheetOpts` cũng bỏ
   vì đó là danh sách tab lấy về từ Sheet.                                    */

const _VBG_BO_KHI_LUU = ['rows', 'sheetOpts'];
const _VBG_BO_O_GOC = ['menuMauOpen', 'modalTaoMoi', 'stale'];

let vbgTheoHoSo = {};

function vbgCanLuu(d) {
  if (!d || !Array.isArray(d.maus)) return null;
  const goc = {};
  Object.keys(d).forEach((k) => {
    if (k !== 'maus' && !_VBG_BO_O_GOC.includes(k)) goc[k] = d[k];
  });
  goc.maus = d.maus.map((m) => {
    const r = {};
    Object.keys(m).forEach((k) => { if (!_VBG_BO_KHI_LUU.includes(k)) r[k] = m[k]; });
    return r;
  });
  return goc;
}

function vbgTuDaLuu(daLuu) {
  const moi = JSON.parse(JSON.stringify(MAU_VAN_BAN_GHEP_MAC_DINH));
  if (!daLuu || !Array.isArray(daLuu.maus)) return moi;
  Object.keys(daLuu).forEach((k) => { if (k !== 'maus') moi[k] = daLuu[k]; });
  /* Ghép theo ID chứ không theo thứ tự: bản sau có thể thêm khuôn mẫu mới,
     lấy theo chỉ số là gán nhầm cấu hình của khuôn này sang khuôn kia. Khuôn
     nào đã lưu thì dùng bản lưu và mượn lại rows/sheetOpts của bản mặc định
     để màn hình có cái mà vẽ trước khi tải lại. */
  moi.maus = moi.maus.map((mm) => {
    const cu = daLuu.maus.find((x) => x && x.id === mm.id);
    if (!cu) return mm;
    const gop = { ...mm, ...cu };
    _VBG_BO_KHI_LUU.forEach((k) => { gop[k] = mm[k]; });
    return gop;
  });
  // Khuôn người dùng tự tạo (không có trong bản mặc định) thì giữ nguyên.
  daLuu.maus.forEach((cu) => {
    if (cu && cu.id && !moi.maus.some((x) => x.id === cu.id)) {
      moi.maus.push({ ...cu, rows: [], sheetOpts: [] });
    }
  });
  if (!(moi.mauHienTai >= 0 && moi.mauHienTai < moi.maus.length)) moi.mauHienTai = 0;
  return moi;
}

/* Cất mẫu ghép của hồ sơ đang mở trước khi chuyển sang hồ sơ khác. */
function vbgGhiNho(iHoSo) {
  if (iHoSo == null) return;
  vbgTheoHoSo[iHoSo] = duLieuVBG;
}

/* Lấy mẫu ghép của hồ sơ vừa chuyển sang. Hồ sơ chưa có thì cho bản mặc định. */
function vbgDoiSang(iHoSo) {
  if (iHoSo == null) return;
  duLieuVBG = vbgTheoHoSo[iHoSo]
    || JSON.parse(JSON.stringify(MAU_VAN_BAN_GHEP_MAC_DINH));
  vbgTheoHoSo[iHoSo] = duLieuVBG;
}

/* Gọi lúc lưu hồ sơ: trả về mẫu ghép đã bỏ rows, của đúng một hồ sơ. */
function vbgDeLuu(iHoSo, iDangMo) {
  const d = (iHoSo === iDangMo) ? duLieuVBG : vbgTheoHoSo[iHoSo];
  return vbgCanLuu(d);
}

/* Gọi lúc khởi động: dựng lại kho từ danh sách hồ sơ đã lưu. */
function vbgNapTuHoSo(dsHoSo, iDangMo) {
  vbgTheoHoSo = {};
  (dsHoSo || []).forEach((h, i) => {
    if (h && h.vanBanGhep) vbgTheoHoSo[i] = vbgTuDaLuu(h.vanBanGhep);
  });
  if (vbgTheoHoSo[iDangMo]) duLieuVBG = vbgTheoHoSo[iDangMo];
}


function veManVanBanGhep(S, duLieu) {
  const cur = duLieuVBG.maus[duLieuVBG.mauHienTai] || duLieuVBG.maus[0];
  const nav = duLieuVBG.nav || 0;

  const NAVS = [
    ['Nguồn dữ liệu', cur.srcType === 0 ? 'Google Sheet' : 'Tệp máy', null],
    ['Khớp cột', cur.cols.filter(c => c.varName).length + ' cột đang dùng', null],
    ['Lọc & nhóm', (cur.rule.trong ? 'bỏ dòng thiếu' : '') + (cur.rule.trung ? ' · gộp trùng' : ''), null],
    ['Đầu danh sách', cur.on.dau ? 'Đang bật' : 'Đang tắt', 'dau'],
    ['Mẫu câu mỗi dòng', 'Luôn đọc · ' + cur.cols.filter(c => c.varName).length + ' biến', null],
    ['Câu xen giữa', cur.on.giua ? 'Sau mỗi ' + cur.sauMoi + ' dòng' : 'Đang tắt', 'giua'],
    ['Cuối danh sách', cur.on.cuoi ? 'Đang bật' : 'Đang tắt', 'cuoi']
  ];

  return `<div class="vanbanghep">
    <!-- KHUNG 3 CỘT THÂN CHÍNH -->
    <div class="vanbanghep__than-chinh">
      <!-- CỘT TRÁI (240px) -->
      <div class="vanbanghep__trai">
        <div class="vanbanghep__chonmau">
          <button class="vanbanghep__nutquaylai" data-vbg="quay_ve_chinh" title="Quay lại màn hình chính">
            ${svgIcon('chevron_left', 14)}
          </button>
          <button class="vanbanghep__nutmau" data-vbg="menu_mau">
            <span style="flex:1;text-align:left;font-weight:600;font-size:13.5px;white-space:nowrap;overflow:hidden;text-overflow:ellipsis">${esc(cur.name)}</span>
            ${svgIcon('chevron_down', 12)}
          </button>
          ${duLieuVBG.menuMauOpen ? `
            <div class="vanbanghep__menumau">
              <div style="padding:6px 8px 4px;font-size:11px;letter-spacing:.04em;text-transform:uppercase;color:var(--txt3);font-weight:600">Mẫu ghép trong hồ sơ này</div>
              ${duLieuVBG.maus.map((m, idx) => `
                <div class="vanbanghep__nav-muc${idx === duLieuVBG.mauHienTai ? ' chon' : ''}" data-vbgpreset="${idx}" style="border-radius:4px;padding:6px 8px;cursor:pointer">
                  <span style="font-weight:${idx === duLieuVBG.mauHienTai ? '600' : '400'};font-size:13px;color:var(--txt)">${esc(m.name)}</span>
                </div>
              `).join('')}
              <div style="height:1px;background:var(--divider);margin:4px 0"></div>
              <div class="vanbanghep__nav-muc" data-vbg="mo_tao_moi" style="color:var(--acc);font-size:13px;font-weight:600;display:flex;align-items:center;gap:6px">
                ${svgIcon('plus', 12)} Tạo mẫu ghép mới…
              </div>
            </div>
          ` : ''}
        </div>

        <div class="vanbanghep__nav">
          ${NAVS.map(([label, meta, key], i) => {
            const sel = nav === i;
            const off = key && !cur.on[key];
            return `<div class="vanbanghep__nav-muc${sel ? ' chon' : ''}" data-vbgnav="${i}">
              <span class="vanbanghep__nav-vach"></span>
              <span class="vanbanghep__dot${off ? ' tat' : ''}"></span>
              <div style="flex:1;min-width:0">
                <div style="font-size:13.5px;font-weight:${sel ? '600' : '400'};color:var(--txt)">${esc(label)}</div>
                <div style="font-size:11.5px;color:var(--txt3)">${esc(meta)}</div>
              </div>
            </div>`;
          }).join('')}
        </div>

        <div class="vanbanghep__chan-trai">
          <div>Mẫu này thuộc hồ sơ <strong style="color:var(--txt2);font-weight:600">${esc(hoSoDangDung(S).ten)}</strong>. Các hồ sơ khác không bị ảnh hưởng.</div>
          <div class="vanbanghep__nut-reset" data-vbg="tra_ve_dau" title="Xoá mọi thay đổi bạn đã nhập, trả các mẫu về nội dung ban đầu">
            ${svgIcon('refresh', 12)} Trả mẫu về ban đầu
          </div>
        </div>
      </div>

      <!-- CỘT GIỮA (Trình biên tập mục) -->
      <div class="vanbanghep__giua">
        <div class="vanbanghep__dau">
          <span style="font-size:15.5px;font-weight:600;color:var(--txt)">${esc(NAVS[nav][0])}</span>
          <span style="font-size:12.5px;color:var(--txt3);flex:1;min-width:0;overflow:hidden;text-overflow:ellipsis">${esc(layGoiYNav(nav))}</span>
          ${NAVS[nav][2] ? `
            <button class="soat__chip${cur.on[NAVS[nav][2]] ? ' mo' : ''}" style="margin-left:auto"
                    data-vbgcongtac="${NAVS[nav][2]}">
              ${cur.on[NAVS[nav][2]] ? '✓ Đang bật' : '× Đang tắt'}
            </button>
          ` : ''}
        </div>

        <div class="vanbanghep__than">
          ${veNoiDungNav(nav, cur)}
        </div>
      </div>

      <!-- CỘT PHẢI (380px - Bản ghép hoàn chỉnh) -->
      <div class="vanbanghep__phai">
        ${vePreviewGhep(cur)}
      </div>
    </div>

    <!-- THANH DƯỚI CÙNG (46px) - PHÂN VÙNG CỘT CHUẨN XÁC -->
    <div class="vanbanghep__duoi">
      <div class="vanbanghep__duoi-trai"></div>
      <div class="vanbanghep__duoi-phai">
        ${(() => {
          /* Chấm này trước đây LUÔN xanh và chữ LUÔN là "Đã đồng bộ", kể cả khi
             chưa tải gì và bảng còn nguyên 25 dòng dữ liệu mẫu, hoặc khi người
             dùng đã tắt tự đồng bộ. Nhìn chấm xanh, người dùng tưởng đây là
             danh sách thật rồi bấm "Mở bản ghép để nghe" — máy đọc to tên người
             mẫu kèm số tiền. CSS đã có sẵn .tat và .canhbao, chỉ là chưa ai gán. */
          const soDong = cur.tongSo || (cur.rows ? cur.rows.length : 0);
          if (!cur.daTaiThat) {
            return `<span class="vanbanghep__dot canhbao"></span>
        <span style="font-size:13px;color:var(--txt2);white-space:nowrap">
          Dữ liệu mẫu · <strong>${soDong}</strong> dòng · bấm “Tải dữ liệu” để lấy danh sách thật
        </span>`;
          }
          if (!cur.autoSync) {
            return `<span class="vanbanghep__dot tat"></span>
        <span style="font-size:13px;color:var(--txt2);white-space:nowrap">
          Đã tải · <strong>${soDong}</strong> dòng · không tự kiểm tra
        </span>`;
          }
          return `<span class="vanbanghep__dot"></span>
        <span style="font-size:13px;color:var(--txt2);white-space:nowrap">
          Đã đồng bộ · <strong>${soDong}</strong> dòng · tự kiểm tra định kỳ 5 phút/lần
        </span>`;
        })()}
        <span style="margin-left:auto;font-size:13px;color:var(--txt3);white-space:nowrap">
          ${cur.tongSo || (cur.rows ? cur.rows.length : 0)} dòng dữ liệu
        </span>
        <button class="nut nut--acc" data-vbg="apdung" style="height:34px;padding:0 16px;font-weight:600;font-size:13.5px;display:flex;align-items:center;gap:6px">
          ${svgIcon('check', 13)} Mở bản ghép để nghe
        </button>
      </div>
    </div>

    <!-- MODAL TẠO MẪU GHÉP MỚI -->
    ${duLieuVBG.modalTaoMoi ? veModalTaoMoi() : ''}
  </div>`;
}

function layGoiYNav(nav) {
  switch (nav) {
    case 0: return 'Nơi lấy danh sách và lúc nào lấy lại';
    case 1: return 'Gán các cột trong bảng tính vào các biến để đọc';
    case 2: return 'Điều kiện lọc dòng và thứ tự đọc danh sách';
    case 3: return 'Lời mở đầu cố định trước khi đọc danh sách';
    case 4: return 'Mẫu câu áp dụng cho từng dòng trong bảng tính';
    case 5: return 'Câu đọc nhắc lại sau mỗi N dòng danh sách';
    case 6: return 'Lời cảm ơn và kết thúc sau khi đọc hết danh sách';
    default: return '';
  }
}

function veNoiDungNav(nav, cur) {
  if (nav === 0) {
    if (cur.srcType === 1) cur.srcType = 0;
    const SOURCES = [
      {
        type: 0,
        label: 'Google Sheet (Dán link chia sẻ công khai)',
        hint: 'Bảng tính trực tuyến — chỉ cần bật quyền “Bất kỳ ai có đường liên kết đều xem được”. Không cần đăng nhập, dán link là dùng ngay.',
        fieldLabel: 'Đường link Google Sheet:',
        placeholder: 'Dán link https://docs.google.com/spreadsheets/…'
      },
      {
        type: 2,
        label: 'File trên máy (.xlsx, .csv, .tsv, .txt)',
        hint: 'Chọn tệp bảng tính đã lưu trên máy tính. Hoạt động ngoại tuyến 100%, không cần mạng Internet.',
        fieldLabel: 'Tệp bảng tính trên máy:',
        placeholder: 'Dán đường dẫn tệp hoặc bấm Chọn tệp…'
      }
    ];

    if (!cur.srcVals) {
      cur.srcVals = {
        0: cur.srcVal && cur.srcVal.startsWith('http') ? cur.srcVal : GOOGLE_SHEET_MAC_DINH,
        2: cur.srcVal && !cur.srcVal.startsWith('http') ? cur.srcVal : EXCEL_MAC_DINH_LOCAL
      };
    }
    const curVal = cur.srcVals[cur.srcType] != null && cur.srcVals[cur.srcType] !== '' ? cur.srcVals[cur.srcType] : (cur.srcType === 0 ? GOOGLE_SHEET_MAC_DINH : EXCEL_MAC_DINH_LOCAL);
    const activeSource = SOURCES.find(s => s.type === cur.srcType) || SOURCES[0];

    return `<div style="display:flex;flex-direction:column;gap:8px">
      <!-- 2 THẺ NGUỒN CHUẨN MỰC (BAO QUANH CẢ TIÊU ĐỀ VÀ MÔ TẢ) -->
      ${SOURCES.map(o => {
        const isSelected = cur.srcType === o.type;
        return `<div data-vbgsrc="${o.type}" style="display:flex;align-items:flex-start;gap:11px;padding:13px 14px;border-radius:6px;background:${isSelected ? 'var(--acc-soft)' : 'var(--layer2)'};border:1px solid ${isSelected ? 'var(--acc)' : 'var(--stroke)'};cursor:pointer;transition:all .15s ease">
          <span style="width:18px;height:18px;flex:none;margin-top:1px;border-radius:9px;border:1.5px solid ${isSelected ? 'var(--acc)' : 'var(--stroke2)'};display:flex;align-items:center;justify-content:center;box-sizing:border-box;background:var(--ctl)">
            <span style="width:8px;height:8px;border-radius:4px;background:${isSelected ? 'var(--acc)' : 'transparent'}"></span>
          </span>
          <div style="flex:1;min-width:0">
            <div style="font-size:14.5px;font-weight:600;color:var(--txt)">${esc(o.label)}</div>
            <div style="font-size:13px;line-height:1.5;color:var(--txt2);margin-top:2px;text-wrap:pretty">${esc(o.hint)}</div>
          </div>
          <span style="flex:none;margin-top:2px;font-size:12px;font-weight:600;padding:3px 8px;border-radius:4px;background:${isSelected ? 'var(--acc)' : 'var(--chip-bg)'};border:1px solid ${isSelected ? 'var(--acc)' : 'var(--chip-bd)'};color:${isSelected ? 'var(--acc-txt)' : 'var(--chip-fg)'};white-space:nowrap">
            ${isSelected ? 'Đang dùng' : 'Có sẵn'}
          </span>
        </div>`;
      }).join('')}

      <!-- HỘP NHẬP ĐƯỜNG DẪN / URL VÀ CHỌN BẢNG / TIÊU ĐỀ -->
      <div style="margin-top:8px;padding:14px;background:var(--layer2);border:1px solid var(--stroke);border-radius:6px">
        <div style="font-size:13px;color:var(--txt2);margin-bottom:6px">
          ${esc(activeSource.fieldLabel)}
        </div>
        <div style="display:flex;gap:8px">
          <input class="giongkho__tim vanbanghep__o-nhap-acc" style="flex:1;min-width:0;box-sizing:border-box;height:36px;padding:0 10px;font-size:14px" id="vbgSrcVal" value="${esc(curVal)}"
                 placeholder="${esc(activeSource.placeholder)}">
          ${cur.srcType === 2 ? `
            <button class="nut nut--vien" data-vbg="chon_tep" style="height:36px;padding:0 13px;font-size:14px;white-space:nowrap;display:flex;align-items:center;gap:6px">
              ${svgIcon('plus', 12)} Chọn tệp…
            </button>
          ` : ''}
          <button class="nut nut--vien" data-vbg="kiem_tra_ket_noi" style="height:36px;padding:0 14px;font-size:14px;white-space:nowrap;display:flex;align-items:center;gap:8px">
            ${svgIcon('refresh', 14)} Cập nhật dữ liệu
          </button>
        </div>
        
        <div style="display:flex;gap:12px;margin-top:12px">
          <div style="flex:1;min-width:0">
            <div style="font-size:13px;color:var(--txt2);margin-bottom:6px">Bảng trong tệp</div>
            <div class="vanbanghep__select-wrap">
              <select id="vbgSheet" data-vbgfield="sheet" ${cur.isSingleSheet ? 'disabled' : ''} style="height:36px;font-size:14px${cur.isSingleSheet ? ';opacity:0.8;background:var(--layer2)' : ''}">
                ${(cur.sheetOpts || [cur.sheet || 'Sheet1']).map(s => `<option value="${esc(s)}" ${cur.sheet === s ? 'selected' : ''}>${esc(s)}</option>`).join('')}
              </select>
              <span class="vanbanghep__select-icon" style="right:10px">${svgIcon('chevron_down', 13)}</span>
            </div>
            ${cur.isSingleSheet ? '<div style="font-size:11.5px;color:var(--txt3);margin-top:3px">Tệp này chỉ có 1 bảng dữ liệu duy nhất</div>' : ''}
          </div>
          <div style="flex:1;min-width:0">
            <div style="font-size:13px;color:var(--txt2);margin-bottom:6px">Dòng tiêu đề</div>
            <div class="vanbanghep__select-wrap">
              <select id="vbgHeadRow" data-vbgfield="headRow" style="height:36px;font-size:14px">
                <option value="Dòng 1" ${cur.headRow === 'Dòng 1' ? 'selected' : ''}>Dòng 1</option>
                <option value="Dòng 2" ${cur.headRow === 'Dòng 2' ? 'selected' : ''}>Dòng 2</option>
                <option value="Dòng 3" ${cur.headRow === 'Dòng 3' ? 'selected' : ''}>Dòng 3</option>
                <option value="Không có dòng tiêu đề" ${cur.headRow === 'Không có dòng tiêu đề' ? 'selected' : ''}>Không có dòng tiêu đề</option>
              </select>
              <span class="vanbanghep__select-icon" style="right:10px">${svgIcon('chevron_down', 13)}</span>
            </div>
          </div>
        </div>
      </div>

      <!-- KHỐI 3 THẺ TÙY CHỌN LẤY DỮ LIỆU MỚI -->
      <div style="margin-top:8px;font-size:12px;letter-spacing:.04em;text-transform:uppercase;color:var(--txt3);font-weight:600;margin-bottom:2px">Lấy dữ liệu mới</div>
      <div style="display:flex;flex-direction:column;gap:8px">
        <div style="display:flex;align-items:center;gap:14px;padding:12px 14px;background:var(--layer2);border:1px solid var(--stroke);border-radius:6px">
          <div style="flex:1;min-width:0">
            <div style="font-size:14px;font-weight:600;color:var(--txt)">Bấm nút để lấy dữ liệu mới</div>
            <div style="font-size:13px;color:var(--txt3);margin-top:2px">Luôn bật. Nút nằm ở thanh dưới của màn hình này và trên màn hình chính.</div>
          </div>
          <span style="flex:none;font-size:12.5px;font-weight:600;padding:4px 9px;border-radius:4px;background:var(--chip-bg);border:1px solid var(--chip-bd);color:var(--chip-fg);white-space:nowrap">Luôn bật</span>
        </div>
        <div style="display:flex;align-items:center;gap:14px;padding:12px 14px;background:var(--layer2);border:1px solid var(--stroke);border-radius:6px;cursor:pointer" data-vbgfield="autoSync">
          <div style="flex:1;min-width:0">
            <div style="font-size:14px;font-weight:600;color:var(--txt)">Tự kiểm tra định kỳ</div>
            <div style="font-size:13px;color:var(--txt3);margin-top:2px">Chỉ kiểm tra, không tự đổi giữa lúc đang đọc. Có dòng mới thì hiện nút “Cập nhật danh sách”.</div>
          </div>
          <div style="flex:none;display:flex;align-items:center;gap:8px">
            <span style="font-size:13.5px;color:var(--txt2);white-space:nowrap">${cur.autoSync ? '5 phút một lần' : 'Đang tắt'}</span>
            <span style="width:40px;height:20px;flex:none;border-radius:10px;background:${cur.autoSync ? 'var(--acc)' : 'transparent'};border:1px solid ${cur.autoSync ? 'var(--acc)' : 'var(--stroke2)'};display:flex;align-items:center;padding:0 3px;justify-content:${cur.autoSync ? 'flex-end' : 'flex-start'};box-sizing:border-box">
              <span style="width:12px;height:12px;border-radius:6px;background:${cur.autoSync ? 'var(--acc-txt)' : 'var(--txt2)'}"></span>
            </span>
          </div>
        </div>
        <div style="display:flex;align-items:center;gap:14px;padding:12px 14px;background:var(--layer2);border:1px solid var(--stroke);border-radius:6px">
          <div style="flex:1;min-width:0">
            <div style="font-size:14px;font-weight:600;color:var(--txt)">Khi không lấy được</div>
            <div style="font-size:13px;color:var(--txt3);margin-top:2px">Dùng bản đã tải lần trước và báo rõ là dữ liệu ngày nào — không dừng buổi đọc.</div>
          </div>
          <span style="flex:none;font-size:12.5px;font-weight:600;padding:4px 9px;border-radius:4px;background:var(--acc-soft);border:1px solid var(--acc);color:var(--acc);white-space:nowrap">Đã chọn</span>
        </div>
      </div>
    </div>`;
  }

  if (nav === 1) {
    return `<div style="display:flex;flex-direction:column;gap:10px">
      <!-- BĂNG GIẢI THÍCH MỤC KHỚP CỘT -->
      <div style="display:flex;align-items:flex-start;gap:9px;padding:11px 13px;background:var(--acc-soft);border-radius:6px">
        <span style="display:flex;flex:none;margin-top:1px;color:var(--acc)">
          <svg width="16" height="16" viewBox="0 0 24 24" fill="currentColor"><path d="M12 2a10 10 0 100 20 10 10 0 000-20zm1 15h-2v-6h2zm0-8h-2V7h2z"/></svg>
        </span>
        <span style="font-size:13px;line-height:1.55;color:var(--txt)">Phần mềm đọc dòng tiêu đề và tự đoán cách dùng từng cột. Cột nào cũng chèn được vào mẫu câu, trừ cột đặt “Bỏ qua”. <strong style="font-weight:600">Cách đọc</strong> quyết định máy đọc ô đó thành gì — cùng một ô <code>2.500.000</code> có thể đọc thành “hai triệu năm trăm nghìn đồng” hoặc đọc từng chữ số.</span>
      </div>

      <div style="border:1px solid var(--stroke);border-radius:6px;overflow:hidden">
        <div style="height:34px;display:flex;align-items:center;background:var(--layer2);border-bottom:1px solid var(--divider);font-size:12px;letter-spacing:.04em;text-transform:uppercase;color:var(--txt3);font-weight:600;padding:0 10px">
          <span style="width:44px;flex:none;text-align:center">Cột</span>
          <span style="flex:1;min-width:0">Tiêu đề trong sheet</span>
          <span style="width:160px;flex:none;padding-right:8px">Dùng làm</span>
          <span style="width:160px;flex:none;padding-right:8px">Cách đọc</span>
          <span style="width:100px;flex:none;text-align:right">Tên biến</span>
        </div>
        ${cur.cols.map((c, i) => `
          <div style="display:flex;align-items:center;min-height:50px;border-bottom:1px solid var(--divider);padding:0 10px;background:var(--layer)">
            <span style="width:44px;flex:none;text-align:center;font-size:13px;font-weight:600;color:var(--acc)">Cột ${esc(c.letter)}</span>
            <div style="flex:1;min-width:0;padding-right:8px">
              <div style="font-size:13.5px;font-weight:600;color:var(--txt)">${esc(c.head)}</div>
            </div>
            <span style="width:160px;flex:none;padding-right:8px">
              <div class="vanbanghep__select-wrap">
                <select data-vbgcolmap="${i}">
                  <option value="{ten}" ${c.varName === '{ten}' ? 'selected' : ''}>Tên người {ten}</option>
                  <option value="{diachi}" ${c.varName === '{diachi}' ? 'selected' : ''}>Địa chỉ {diachi}</option>
                  <option value="{sotien}" ${c.varName === '{sotien}' ? 'selected' : ''}>Số tiền {sotien}</option>
                  <option value="{ngay}" ${c.varName === '{ngay}' ? 'selected' : ''}>Ngày tháng {ngay}</option>
                  <option value="{so}" ${c.varName === '{so}' ? 'selected' : ''}>Số thứ tự {so}</option>
                  <option value="{ghichu}" ${c.varName === '{ghichu}' ? 'selected' : ''}>Ghi chú {ghichu}</option>
                  <option value="" ${!c.varName ? 'selected' : ''}>Bỏ qua (không đọc)</option>
                </select>
                <span class="vanbanghep__select-icon">${svgIcon('chevron_down', 11)}</span>
              </div>
            </span>
            <span style="width:160px;flex:none;padding-right:8px">
              <div class="vanbanghep__select-wrap">
                <select data-vbgcolread="${i}">
                  <option value="Tên riêng" ${c.read === 'Tên riêng' ? 'selected' : ''}>Tên riêng (đọc chậm)</option>
                  <option value="Số tiền" ${c.read === 'Số tiền' ? 'selected' : ''}>Số tiền</option>
                  <option value="Ngày tháng" ${c.read === 'Ngày tháng' ? 'selected' : ''}>Ngày tháng</option>
                  <option value="Số đếm" ${c.read === 'Số đếm' ? 'selected' : ''}>Số thứ tự</option>
                  <option value="Đọc thường" ${c.read === 'Đọc thường' ? 'selected' : ''}>Nguyên văn</option>
                </select>
                <span class="vanbanghep__select-icon">${svgIcon('chevron_down', 11)}</span>
              </div>
            </span>
            <span style="width:100px;flex:none;text-align:right">
              ${c.varName ? `<span class="vanbanghep__badge" style="font-family:Consolas,monospace">${esc(c.varName)}</span>` : '<span style="color:var(--txt3);font-size:12px">—</span>'}
            </span>
          </div>
        `).join('')}
      </div>
      <div style="font-size:12.5px;color:var(--txt3);line-height:1.5">Cột đặt “Bỏ qua” vẫn nằm trong sheet, chỉ là không đọc tới.</div>
    </div>`;
  }

  if (nav === 2) {
    return `<div style="display:flex;flex-direction:column;gap:10px">
      <!-- 3 CÔNG TẮC LỌC & NHÓM -->
      <div class="vanbanghep__the" style="cursor:pointer;align-items:center" data-vbgrule="trong">
        <div style="flex:1">
          <div style="font-weight:600;font-size:14px;color:var(--txt)">Bỏ dòng thiếu dữ liệu</div>
          <div style="font-size:12.5px;color:var(--txt3);margin-top:2px">Dòng thiếu tên hoặc thiếu số tiền sẽ không được đọc.</div>
        </div>
        <span style="font-size:13px;color:var(--txt3);margin-right:8px">${cur.rule.trong ? 'Đang lọc' : 'Tắt'}</span>
        <span style="width:40px;height:20px;flex:none;border-radius:10px;background:${cur.rule.trong ? 'var(--acc)' : 'transparent'};border:1px solid ${cur.rule.trong ? 'var(--acc)' : 'var(--stroke2)'};display:flex;align-items:center;padding:0 3px;justify-content:${cur.rule.trong ? 'flex-end' : 'flex-start'};box-sizing:border-box">
          <span style="width:12px;height:12px;border-radius:6px;background:${cur.rule.trong ? 'var(--acc-txt)' : 'var(--txt2)'}"></span>
        </span>
      </div>

      <div class="vanbanghep__the" style="cursor:pointer;flex-direction:column" data-vbgrule="trung">
        <div style="display:flex;align-items:center;width:100%">
          <div style="flex:1">
            <div style="font-weight:600;font-size:14px;color:var(--txt)">Gộp các dòng trùng nhau</div>
            <div style="font-size:12.5px;color:var(--txt3);margin-top:2px">Nếu trùng tên và địa chỉ, tự động cộng dồn số tiền thành một câu.</div>
          </div>
          <span style="font-size:13px;color:var(--txt3);margin-right:8px">${cur.rule.trung ? 'Đang gộp' : 'Tắt'}</span>
          <span style="width:40px;height:20px;flex:none;border-radius:10px;background:${cur.rule.trung ? 'var(--acc)' : 'transparent'};border:1px solid ${cur.rule.trung ? 'var(--acc)' : 'var(--stroke2)'};display:flex;align-items:center;padding:0 3px;justify-content:${cur.rule.trung ? 'flex-end' : 'flex-start'};box-sizing:border-box">
            <span style="width:12px;height:12px;border-radius:6px;background:${cur.rule.trung ? 'var(--acc-txt)' : 'var(--txt2)'}"></span>
          </span>
        </div>
      </div>

      <div class="vanbanghep__the" style="cursor:pointer;align-items:center" data-vbgrule="thutu">
        <div style="flex:1">
          <div style="font-weight:600;font-size:14px;color:var(--txt)">Giữ đúng thứ tự trong sheet</div>
          <div style="font-size:12.5px;color:var(--txt3);margin-top:2px">Đọc từ trên xuống như trong bảng tính. Tắt thì sắp theo số tiền giảm dần.</div>
        </div>
        <span style="font-size:13px;color:var(--txt3);margin-right:8px">${cur.rule.thutu !== false ? 'Theo bảng tính' : 'Sắp xếp'}</span>
        <span style="width:40px;height:20px;flex:none;border-radius:10px;background:${cur.rule.thutu !== false ? 'var(--acc)' : 'transparent'};border:1px solid ${cur.rule.thutu !== false ? 'var(--acc)' : 'var(--stroke2)'};display:flex;align-items:center;padding:0 3px;justify-content:${cur.rule.thutu !== false ? 'flex-end' : 'flex-start'};box-sizing:border-box">
          <span style="width:12px;height:12px;border-radius:6px;background:${cur.rule.thutu !== false ? 'var(--acc-txt)' : 'var(--txt2)'}"></span>
        </span>
      </div>
    </div>`;
  }

  if (nav === 4) {
    const len = (cur.T.mau || '').length;
    return `<div style="display:flex;flex-direction:column;gap:10px">
      <div style="display:flex;align-items:baseline;justify-content:space-between">
        <span style="font-size:13px;color:var(--txt2)">Mỗi dòng trong bảng tính sẽ được đọc theo mẫu này</span>
        <span id="vbgDoanDem" style="font-size:12.5px;color:var(--txt3)">${len} ký tự</span>
      </div>
      
      <div style="margin-top:2px">
        <div style="font-size:11.5px;letter-spacing:.04em;text-transform:uppercase;color:var(--txt3);font-weight:600;margin-bottom:6px">Chèn dữ liệu từ sheet</div>
        <div>
          ${cur.cols.filter(c => c.varName).map(c => {
            const inUse = (cur.T.mau || '').includes(c.varName);
            return `<button class="vanbanghep__chip-bien${inUse ? ' dung' : ''}" data-vbginsert="${esc(c.varName)}" title="Bấm để chèn ${c.varName}">
              ${svgIcon('plus', 11)} ${esc(c.varName)} <span style="font-size:11px;opacity:.75">(${esc(c.head)})</span>
            </button>`;
          }).join('')}
        </div>
      </div>

      <textarea id="vbgMauText" class="soat__hop-sua vanbanghep__o-nhap-acc" spellcheck="false" autocomplete="off" style="min-height:110px;font-size:14.5px;line-height:1.6"
                placeholder="Ví dụ: {ten}, {diachi}, phát tâm công đức số tiền {sotien}.">${esc(cur.T.mau)}</textarea>

      <div style="padding:12px 14px;background:var(--layer2);border:1px solid var(--stroke);border-radius:6px;font-size:13px;line-height:1.55;color:var(--txt2)">
        Ô số tiền <code>2.500.000</code> sẽ được đọc thành “hai triệu năm trăm nghìn đồng”. Muốn đổi cách đọc, chỉnh ở mục <strong style="color:var(--txt)">Khớp cột</strong> hoặc thêm vào <strong style="color:var(--acc)">Từ điển phát âm</strong>.
      </div>
    </div>`;
  }

  const key = nav === 3 ? 'dau' : nav === 5 ? 'giua' : 'cuoi';
  const val = cur.T[key] || '';
  const paras = val.split(/\n{2,}/).filter(x => x.trim()).length || (val.trim() ? 1 : 0);
  const chars = val.length;

  return `<div style="display:flex;flex-direction:column;gap:10px">
    <div style="display:flex;align-items:baseline;justify-content:space-between">
      <span style="font-size:13px;color:var(--txt2)">Nội dung đọc — cách dòng để ngắt đoạn</span>
      <span id="vbgDoanDem" style="font-size:12.5px;color:var(--txt3)">${paras} đoạn · ${chars} ký tự</span>
    </div>

    ${nav === 5 ? `
      <div style="display:flex;align-items:center;gap:10px;padding:10px 14px;background:var(--layer2);border:1px solid var(--stroke);border-radius:6px">
        <span style="font-size:13.5px;font-weight:600;color:var(--txt)">Đọc nhắc lại sau mỗi:</span>
        <div class="vanbanghep__select-wrap" style="width:110px">
          <select id="vbgSauMoi">
            <option value="10" ${cur.sauMoi === '10' ? 'selected' : ''}>10 dòng</option>
            <option value="20" ${cur.sauMoi === '20' ? 'selected' : ''}>20 dòng</option>
            <option value="30" ${cur.sauMoi === '30' ? 'selected' : ''}>30 dòng</option>
            <option value="50" ${cur.sauMoi === '50' ? 'selected' : ''}>50 dòng</option>
          </select>
          <span class="vanbanghep__select-icon">${svgIcon('chevron_down', 11)}</span>
        </div>
      </div>
    ` : ''}

    <textarea id="vbgText_${key}" class="soat__hop-sua vanbanghep__o-nhap-acc" spellcheck="false" autocomplete="off" style="min-height:220px;font-size:14.5px;line-height:1.65"
              placeholder="Nhập nội dung tĩnh... Cách dòng một lần để ngắt đoạn.">${esc(val)}</textarea>

    <div style="padding:12px 14px;background:var(--layer2);border:1px solid var(--stroke);border-radius:6px;font-size:13px;line-height:1.55;color:var(--txt2)">
      Cách dòng một lần là ngắt đoạn — phần mềm sẽ nghỉ một nhịp ở đó. Muốn nghỉ lâu hơn, chèn thẻ khoảng lặng ở màn hình chính.
    </div>
  </div>`;
}

function formatRowSentence(template, row, cols) {
  let s = template;
  cols.forEach((c, cIdx) => {
    const val = row && (row[c.letter] != null ? row[c.letter] : (Array.isArray(row) ? row[cIdx] : ''));
    if (c.varName && val != null && val !== '') {
      s = s.split(c.varName).join(val);
    }
  });
  return s.replace(/\{[a-z0-9]+\}/g, '').replace(/\s+([.,])/g, '$1').replace(/\s{2,}/g, ' ').trim();
}

function vePreviewGhep(cur) {
  const tong = cur.tongSo || (cur.rows ? cur.rows.length : 3);
  const sampleRows = cur.rows && cur.rows.length ? cur.rows.slice(0, 4) : [
    { A: 'Nguyễn Văn An', B: 'Tổ 5 Phường Yên Hoà', C: '500.000 đồng', D: '15/08/2026' },
    { A: 'Trần Thị Mai', B: 'Khu tập thể Nam Đồng', C: '1.000.000 đồng', D: '18/08/2026' },
    { A: 'Lê Hoàng Long', B: 'Số 12 phố Huế', C: '2.000.000 đồng', D: '20/08/2026' },
    { A: 'Phạm Thị Lan', B: 'Đội 3 thôn Đoài', C: '500.000 đồng', D: '21/08/2026' }
  ];

  return `<div class="vanbanghep__hop-preview">
    <div class="vanbanghep__preview-dau">
      <span style="font-size:14px;font-weight:600;color:var(--txt);white-space:nowrap">Bản ghép hoàn chỉnh</span>
      <span style="font-size:12px;color:var(--txt3);margin-left:auto">${tong} dòng dữ liệu</span>
    </div>

    <div class="vanbanghep__preview-than">
      ${cur.on.dau && cur.T.dau ? `
        <div class="vanbanghep__khoi">
          <div class="vanbanghep__khoi-dau">
            <span class="vanbanghep__khoi-ten">ĐẦU DANH SÁCH (TĨNH)</span>
          </div>
          <div class="vanbanghep__khoi-chu">${esc(cur.T.dau)}</div>
        </div>
      ` : ''}

      <div class="vanbanghep__khoi dong">
        <div class="vanbanghep__khoi-dau">
          <span class="vanbanghep__khoi-ten">DANH SÁCH — TỪ BẢNG TÍNH (${tong} DÒNG)</span>
        </div>
        <div class="vanbanghep__khoi-chu">${sampleRows.map((r, i) => {
            /* Dung DUNG ham ma bai doc that dung. Truoc day khung xem truoc
               co ban don cau rieng, con thieu buoc go gioi tu bi bo roi:
                 xem truoc : "Tran Thi Bich, o, da cong duc 1.200.000 dong."
                 doc that  : "Tran Thi Bich, da cong duc 1.200.000 dong."
               Nguoi dung nhin cau que tren man hinh roi tuong may hong,
               trong khi tieng doc ra lai sach. Hai noi ghep cau la mot ho
               loi chinh tep giao-dien.js da tung ghi chu phai tranh.
               ghepMotCauVBG nam trong giao-dien.js - khong co khi chay bang
               Node (module.exports o cuoi tep nay), nen van giu duong lui. */
            const cau = (typeof ghepMotCauVBG === 'function')
              ? ghepMotCauVBG(cur, r)
              : formatRowSentence(cur.T.mau, r, cur.cols);
            return `<div style="margin-bottom:6px">${i + 1}. ${esc(cau)}</div>`;
          }).join('')}${tong > sampleRows.length ? `<div style="color:var(--txt3);font-size:12.5px;margin-top:6px">… và ${tong - sampleRows.length} dòng tiếp theo trong bảng tính</div>` : ''}</div>
      </div>

      ${cur.on.giua && cur.T.giua ? `
        <div class="vanbanghep__khoi">
          <div class="vanbanghep__khoi-dau">
            <span class="vanbanghep__khoi-ten">CÂU XEN GIỮA (LẶP MỖI ${cur.sauMoi} DÒNG)</span>
          </div>
          <div class="vanbanghep__khoi-chu">${esc(cur.T.giua)}</div>
        </div>
      ` : ''}

      ${cur.on.cuoi && cur.T.cuoi ? `
        <div class="vanbanghep__khoi">
          <div class="vanbanghep__khoi-dau">
            <span class="vanbanghep__khoi-ten">CUỐI DANH SÁCH (TĨNH)</span>
          </div>
          <div class="vanbanghep__khoi-chu">${esc(cur.T.cuoi)}</div>
        </div>
      ` : ''}
    </div>

    <div class="vanbanghep__preview-chan">
      Khối viền xanh là phần lấy từ bảng tính (động). Khối viền xám là phần bạn viết (tĩnh).
    </div>
  </div>`;
}

/* Mô tả một dòng cho mỗi mẫu, tra theo ID của chính mẫu đó. */
const MO_TA_MAU = {
  congduc: 'Đọc lời tán thán đầu/cuối, câu ghép tên + địa chỉ + số tiền công đức.',
  hocphi: 'Đọc danh sách học sinh, lớp, số tiền học phí và hạn nộp.',
  khenthuong: 'Đọc tuyên dương cá nhân, phòng ban, thành tích và mức thưởng.',
  donhang: 'Đọc tên khách, mặt hàng, số lượng và tiền phải trả.',
  lichtruc: 'Đọc lịch trực, người phụ trách, thời gian và nơi làm việc.',
  phuongxa: 'Đọc thông báo tổ dân phố: hộ gia đình, nội dung, thời hạn.',
};


function veModalTaoMoi() {
  /* Dựng thẳng từ duLieuVBG.maus, KHÔNG chép lại thành một bảng riêng.
     Bảng chép tay trước đây có 4 mục trong khi thật ra có 6 mẫu, và một mục
     mang id 'lichhen' — cái id đó không tồn tại. Bấm vào nó, bản cũ nhảy sang
     mẫu "Bán hàng & Chốt đơn Livestream" vì gắn theo thứ tự mảng. */
  const presets = duLieuVBG.maus.map((m) => ({
    id: m.id,
    name: m.name,
    desc: MO_TA_MAU[m.id] || '',
  }));

  return `<div class="man" style="z-index:90">
    <div class="hop" style="width:620px">
      <div class="hop__dau" style="display:flex;align-items:flex-start;justify-content:space-between">
        <div style="flex:1;min-width:0">
          <div class="hop__ten">Chọn mẫu ghép</div>
          <div class="hop__phu">Chuyển sang mẫu có sẵn gần giống danh sách của bạn</div>
        </div>
        <button class="nut nut--icon" data-vbg="dong_tao_moi" title="Đóng" style="font-size:20px;width:32px;height:32px;display:flex;align-items:center;justify-content:center;color:var(--txt3);cursor:pointer">×</button>
      </div>
      <div class="hop__than" style="padding:16px 22px;display:grid;grid-template-columns:1fr 1fr;gap:10px">
        ${/* Gắn theo ID, KHÔNG theo thứ tự trong mảng này: hai danh sách xếp
              khác nhau nên idx=3 ("Thông báo lịch hẹn") từng nhảy sang mẫu
              "Bán hàng & Chốt đơn Livestream". Trường p.id có sẵn từ đầu mà
              chưa ai dùng. */
          presets.map((p) => `
          <div class="vanbanghep__the" data-vbgpreset="${esc(p.id)}" style="flex-direction:column;cursor:pointer;padding:12px 14px">
            <div style="font-weight:600;font-size:14px;color:var(--txt)">${esc(p.name)}</div>
            <div style="font-size:12.5px;color:var(--txt2);margin-top:4px;line-height:1.4">${esc(p.desc)}</div>
          </div>
        `).join('')}
      </div>
      <div class="hop__chan" style="justify-content:flex-end">
        <button class="nut nut--vien" data-vbg="dong_tao_moi">Huỷ</button>
      </div>
    </div>
  </div>`;
}

if (typeof module !== 'undefined') {
  module.exports = { veManVanBanGhep, MAU_VAN_BAN_GHEP_MAC_DINH, formatRowSentence,
                     vbgCanLuu, vbgTuDaLuu };
}
