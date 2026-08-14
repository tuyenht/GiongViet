/* Giọng Việt — dữ liệu mẫu cho giai đoạn dựng giao diện.
   Nội dung lấy đúng từ design_handoff_giongdoc/README.md: 4 hồ sơ, 5 tài liệu,
   8 giọng (dropdown ở màn chính chỉ hiện 3 giọng có sẵn đầu + 2 giọng của tôi).

   Chữ tiếng Việt ở đây là bản cuối của đặc tả, ĐỪNG sửa cho "hay hơn".
   Số liệu cũng vậy: tài liệu A phải ra đúng 215 từ · 16 đoạn · 1 phút 28 giây
   vì con số đó in trên đầu vùng đọc trong bản mẫu. Sửa chữ là lệch số.

   Khi nối engine thật, tệp này biến mất - không có logic nào ở đây cả. */

'use strict';

// ---------------------------------------------------------------- giọng

const GIONG = [
  { ma: 'binh-an',    ten: 'Giọng Bình An',        rieng: false, gioi: 'Nữ',  vung: 'Bắc',
    tinh: 'trầm ấm',  dung: '620 MB', ngan: 'Nữ · Bắc' },
  { ma: 'ngoc-linh',  ten: 'Giọng Ngọc Linh',      rieng: false, gioi: 'Nữ',  vung: 'Nam',
    tinh: 'nhẹ nhàng', dung: '620 MB', ngan: 'Nữ · Nam' },
  { ma: 'xuan-vinh',  ten: 'Giọng Xuân Vĩnh',      rieng: false, gioi: 'Nam', vung: 'Trung',
    tinh: 'rõ ràng',  dung: '640 MB', ngan: 'Nam · Trung' },
  { ma: 'minh-quan',  ten: 'Giọng Minh Quân',      rieng: false, gioi: 'Nam', vung: 'Bắc',
    tinh: 'dứt khoát', dung: '610 MB', ngan: 'Nam · Bắc' },
  { ma: 'hai-yen',    ten: 'Giọng Hải Yến',        rieng: false, gioi: 'Nữ',  vung: 'Bắc',
    tinh: 'truyền cảm', dung: '630 MB', ngan: 'Nữ · Bắc' },
  { ma: 'thien-tam',  ten: 'Giọng Thiện Tâm',      rieng: false, gioi: 'Nam', vung: 'Nam',
    tinh: 'chậm, phù hợp kinh sách', dung: '660 MB', ngan: 'Nam · Nam' },
  { ma: 'bac-tuan',   ten: 'Giọng bác Tuấn',       rieng: true,  gioi: 'Nam', vung: '',
    tinh: '62 tuổi',  dung: '480 MB', ngan: 'Nam · 62 tuổi', ngayTao: '12/6/2026' },
  { ma: 'thu',        ten: 'Giọng của tôi (thử)',  rieng: true,  gioi: '',    vung: '',
    tinh: 'mẫu 30 giây', dung: '',    ngan: 'mẫu 30 giây' },
];

/* Ô chọn giọng ở màn chính chỉ liệt kê 3 giọng có sẵn đầu tiên, còn Thư viện
   giọng mới hiện đủ 8. Đây là đúng đặc tả chứ không phải thiếu sót: dropdown
   dài quá thì người lớn tuổi cuộn không ra. */
const GIONG_TRONG_DROPDOWN = ['binh-an', 'ngoc-linh', 'xuan-vinh', 'bac-tuan', 'thu'];

// ---------------------------------------------------------------- tài liệu

const D = (kieu, chu) => ({ kieu, chu });      // 'head' | 'body' | 'blank'
const TRONG = () => ({ kieu: 'blank', chu: '' });

const TAI_LIEU = {
  'thongbao-quoc-khanh.txt': {
    doan: [
      D('head', "THÔNG BÁO LỊCH NGHỈ LỄ QUỐC KHÁNH 2/9"),
      D('body', "Kính gửi toàn thể cán bộ, nhân viên Công ty TNHH Bảo Sơn."),
      D('body', "Căn cứ Bộ luật Lao động 2019 và thông báo của UBND TP.HCM, Ban Giám đốc thông báo lịch nghỉ lễ Quốc khánh năm 2026 như sau."),
      D('body', "Thời gian nghỉ tính từ thứ Hai ngày 31/8/2026 đến hết thứ Tư ngày 2/9/2026, tổng cộng 3 ngày làm việc. Công ty làm việc trở lại bình thường từ sáng thứ Năm ngày 3/9."),
      D('body', "Các bộ phận trực tiếp sản xuất bố trí người trực theo lịch đã gửi qua email ngày 12/8. Danh sách trực cụ thể như sau."),
      D('body', "Phòng Kinh doanh — anh Trần Minh Đức"),
      D('body', "Phòng Kỹ thuật — anh Lê Hoàng Nam"),
      D('body', "Phòng Kho vận — chị Phạm Thu Hà"),
      D('body', "Nhân viên có nhu cầu nghỉ thêm vui lòng đăng ký với Phòng Nhân sự trước 17h00 ngày 25/8/2026 để bộ phận sắp xếp nhân lực thay thế."),
      D('body', "Trong thời gian nghỉ lễ, mọi sự cố khẩn cấp xin liên hệ số hotline 1900 6868, máy lẻ 2."),
      D('body', "Kính chúc toàn thể anh chị em cùng gia đình một kỳ nghỉ lễ vui vẻ và an toàn."),
      D('body', "Trân trọng thông báo."),
      D('body', "TM. BAN GIÁM ĐỐC"),
      D('body', "Giám đốc điều hành"),
      D('body', "Nguyễn Văn Tuyến"),
    ],
    chuY: {
      tomTat: '9 chỗ cần chú ý, trong đó 2 lỗi nên sửa trước khi xuất.',
      loai: [
        { ten: 'Lỗi phải sửa',             nang: true,  dem: 2, doan: [1] },
        { ten: 'Từ viết tắt',              nang: false, dem: 4, doan: [2] },
        { ten: 'Đoạn dài, ký tự lạ',       nang: false, dem: 2, doan: [4] },
        { ten: 'Tên riêng, số điện thoại', nang: false, dem: 1, doan: [10] },
      ],
    },
  },

  'bai-viet-nghe-lai.docx': {
    doan: [
      D('head', 'Vì sao người lớn tuổi ngại dùng máy tính'),
      D('body', 'Chữ nhỏ, nút bấm san sát nhau, và mỗi lần bấm nhầm là một thông báo '
              + 'toàn chữ lạ hiện ra. Không phải họ không học được, mà là chương trình '
              + 'chưa từng được viết cho họ.'),
      D('body', 'Người ta bỏ một phần mềm không phải vì thiếu tính năng. '
              + 'Người ta bỏ vì lần đầu mở lên đã thấy sợ.'),
      D('body', 'Cách sửa thì đơn giản đến mức nhàm chán: chữ to lên, nút ít đi, '
              + 'lỗi viết bằng tiếng người.'),
    ],
    chuY: {
      tomTat: '2 chỗ cần chú ý, không có lỗi nào bắt buộc sửa.',
      loai: [
        { ten: 'Câu quá dài, nên tách',  nang: false, dem: 1, doan: [2] },
        { ten: 'Tên riêng dễ đọc sai',   nang: false, dem: 1, doan: [1] },
      ],
    },
  },

  'thongbao-phun-thuoc.txt': {
    doan: [
      D('head', 'THÔNG BÁO PHUN THUỐC DIỆT MUỖI'),
      D('body', 'Kính mời bà con nhân dân trong khu phố chú ý nghe thông báo.'),
      D('body', 'Sáng mai, từ 6h00 đến 9h00, Trạm Y tế phường sẽ phun thuốc diệt muỗi '
              + 'phòng chống sốt xuất huyết trên toàn địa bàn.'),
      D('body', 'Đề nghị bà con đóng kín cửa, che đậy thức ăn và nước uống, '
              + 'đưa trẻ nhỏ và người già ra khỏi nhà trong lúc phun.'),
      D('body', 'Sau khi phun khoảng ba mươi phút thì mở cửa cho thoáng rồi vào nhà bình thường.'),
    ],
    chuY: {
      tomTat: '3 chỗ cần chú ý, trong đó 1 lỗi nên sửa trước khi xuất.',
      loai: [
        { ten: 'Giờ viết tắt',           nang: true,  dem: 1, doan: [4] },
        { ten: 'Viết tắt chưa có trong từ điển', nang: false, dem: 2, doan: [3, 4] },
      ],
    },
  },

  'chuong-01.docx': {
    doan: [
      D('head', 'Chương một — Người gác đèn'),
      D('body', 'Ngọn hải đăng đứng đó đã bốn mươi năm. Ông Tư cũng vậy.'),
      D('body', 'Mỗi tối, đúng lúc mặt trời chạm mặt biển, ông leo một trăm hai mươi bậc '
              + 'thang xoắn ốc lên đỉnh tháp, lau lại tấm kính, rồi bật đèn.'),
      D('body', 'Chưa một đêm nào ngọn đèn ấy tắt.'),
      D('body', 'Người trong làng bảo ông lẩn thẩn. Ông không cãi. '
              + 'Ông chỉ biết ngoài kia còn thuyền chưa về.'),
    ],
    chuY: {
      tomTat: '1 chỗ cần chú ý, không có lỗi nào bắt buộc sửa.',
      loai: [
        { ten: 'Số đọc dễ sai', nang: false, dem: 1, doan: [4] },
      ],
    },
  },

  'danh-sach-ung-ho.txt': {
    doan: [
      D('head', 'DANH SÁCH ỦNG HỘ ĐỒNG BÀO VÙNG LŨ'),
      D('body', 'Bùi Thị Thanh Tâm — hai triệu đồng'),
      D('body', 'Nguyễn Văn Đức — một triệu năm trăm nghìn đồng'),
      D('body', 'Gia đình bà Phúc Lâm — năm triệu đồng'),
      D('body', 'Tập thể lớp 9A trường Trung học cơ sở Lê Lợi — tám trăm nghìn đồng'),
      D('body', 'Ban vận động xin trân trọng cảm ơn.'),
    ],
    chuY: {
      tomTat: '4 chỗ cần chú ý, không có lỗi nào bắt buộc sửa.',
      loai: [
        { ten: 'Tên riêng dễ đọc sai', nang: false, dem: 3, doan: [2, 3, 4] },
        { ten: 'Viết tắt chưa có trong từ điển', nang: false, dem: 1, doan: [5] },
      ],
    },
  },
};

// ---------------------------------------------------------------- hồ sơ

/* Hồ sơ là MỘT CHỖ LÀM VIỆC, không phải preset giọng: nó giữ cả danh sách tệp
   đang mở của riêng nó. Đổi hồ sơ là đổi luôn dải tab và nội dung ở giữa. */
const HO_SO = [
  { ma: 'bai-viet', ten: 'Bài viết, văn bản', giong: 'ngoc-linh',
    chinh: { tocDo: 0, caoDo: 0, amLuong: 100 },
    tep: ['thongbao-quoc-khanh.txt', 'bai-viet-nghe-lai.docx'] },

  { ma: 'thong-bao', ten: 'Thông báo ngắn', giong: 'xuan-vinh',
    chinh: { tocDo: 10, caoDo: 0, amLuong: 100 },
    tep: ['thongbao-phun-thuoc.txt'] },

  { ma: 'sach-noi', ten: 'Sách nói', giong: 'bac-tuan',
    chinh: { tocDo: -10, caoDo: 0, amLuong: 90 },
    tep: ['chuong-01.docx'] },

  { ma: 'danh-sach', ten: 'Danh sách, biểu mẫu', giong: 'binh-an',
    chinh: { tocDo: 0, caoDo: 0, amLuong: 100 },
    tep: ['danh-sach-ung-ho.txt'] },
];

if (typeof module !== 'undefined') {
  module.exports = { GIONG, GIONG_TRONG_DROPDOWN, TAI_LIEU, HO_SO };
}
