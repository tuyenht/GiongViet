/* Giọng Việt — dữ liệu mẫu cho giai đoạn dựng giao diện.

   HIỆN CÓ: 6 hồ sơ · 10 tài liệu. Bản thiết kế gốc chỉ có 4 hồ sơ · 5 tài liệu;
   phần thêm là Công đức & Thiện nguyện, Doanh nghiệp & Bán hàng, Pháp quy &
   Hành chính — mở rộng có chủ ý, bám định vị "danh sách công đức chỉ là MỘT
   khuôn mẫu", không phải mọi thứ.

   ĐÃ RỜI KHỎI BẢN MẪU MỘT CHỖ, và đây là quyết định chứ không phải sơ suất:
   bản thiết kế in "215 từ · 15 đoạn · khoảng 1 phút 28 giây" lên đầu vùng đọc,
   lấy từ một thông báo có tên công ty thật và tên người thật trong đó. Bản này
   viết lại ngắn và chung chung hơn (170 từ · 7 đoạn · 54 giây), bỏ hết tên
   thật — không đưa tên người và tên doanh nghiệp vào bản xuất xưởng.
   tests/kiem-mo-hinh.mjs canh theo con số MỚI, không theo bản mẫu nữa.

   Chữ tiếng Việt ở đây vẫn là thứ người dùng nhìn thấy đầu tiên khi chưa có dữ
   liệu thật, nên ĐỪNG sửa cho "hay hơn": sửa chữ là lệch số, và bài kiểm đỏ.
   Muốn đổi thì đổi cả hai nơi cùng lượt.

   Khi nối engine thật, tệp này biến mất - không có logic nào ở đây cả. */

'use strict';

// ---------------------------------------------------------------- giọng

const GIONG = [
  { ma: 'minh-duc',   ten: 'Giọng Minh Đức',       rieng: false, gioi: 'Nam', vung: 'Bắc',
    tinh: 'tin tức, dứt khoát', dung: '620 MB', ngan: 'Nam · Bắc' },
  { ma: 'ngoc-linh',  ten: 'Giọng Ngọc Linh',      rieng: false, gioi: 'Nữ',  vung: 'Bắc',
    tinh: 'kể chuyện, truyền cảm', dung: '620 MB', ngan: 'Nữ · Bắc' },
  { ma: 'xuan-vinh',  ten: 'Giọng Xuân Vĩnh',      rieng: false, gioi: 'Nam', vung: 'Nam',
    tinh: 'tự nhiên, rõ ràng',  dung: '640 MB', ngan: 'Nam · Nam' },
  { ma: 'pham-tuyen', ten: 'Giọng Phạm Tuyên',     rieng: false, gioi: 'Nam', vung: 'Bắc',
    tinh: 'tự nhiên, trầm ấm', dung: '610 MB', ngan: 'Nam · Bắc' },
  { ma: 'thai-son',   ten: 'Giọng Thái Sơn',       rieng: false, gioi: 'Nam', vung: 'Nam',
    tinh: 'kể chuyện, trang nghiêm', dung: '630 MB', ngan: 'Nam · Nam' },
  { ma: 'truc-ly',    ten: 'Giọng Trúc Ly',        rieng: false, gioi: 'Nữ',  vung: 'Bắc',
    tinh: 'tự nhiên, nhẹ nhàng', dung: '620 MB', ngan: 'Nữ · Bắc' },
  { ma: 'bac-tuan',   ten: 'Giọng bác Tuấn',       rieng: true,  gioi: 'Nam', vung: '',
    tinh: '62 tuổi',  dung: '480 MB', ngan: 'Nam · 62 tuổi', ngayTao: '12/6/2026' },
  { ma: 'thu',        ten: 'Giọng của tôi (thử)',  rieng: true,  gioi: '',    vung: '',
    tinh: 'mẫu 30 giây', dung: '',    ngan: 'mẫu 30 giây' },
];

/* Ô chọn giọng ở màn chính chỉ liệt kê 3 giọng có sẵn đầu tiên, còn Thư viện
   giọng mới hiện đủ 8. Đây là đúng đặc tả chứ không phải thiếu sót: dropdown
   dài quá thì người lớn tuổi cuộn không ra. */
const GIONG_TRONG_DROPDOWN = ['minh-duc', 'ngoc-linh', 'xuan-vinh', 'bac-tuan', 'thu'];

// ---------------------------------------------------------------- tài liệu

const D = (kieu, chu) => ({ kieu, chu });      // 'head' | 'body' | 'blank'
const TRONG = () => ({ kieu: 'blank', chu: '' });

const TAI_LIEU = {
  'tin-tuc-thoi-su.txt': {
    doan: [
      D('head', "BẢN TIN PHÁT TRIỂN KINH TẾ XÃ HỘI VÀ ĐỜI SỐNG HÔM NAY"),
      D('body', "Sáng nay, các địa phương trên cả nước đồng loạt tổ chức các hoạt động hưởng ứng phong trào xây dựng nông thôn mới và đô thị văn minh."),
      D('body', "Tại các thành phố lớn, công tác cải cách thủ tục hành chính và chuyển đổi số đang mang lại nhiều thuận tiện trực tiếp cho người dân và doanh nghiệp."),
      D('body', "Chỉ số phát triển kinh tế và thu hút đầu tư tiếp tục ghi nhận mức tăng trưởng tích cực trong các tháng đầu năm 2026."),
      D('body', "Các chuyên gia kinh tế nhận định việc mở rộng hạ tầng giao thông kết nối liên vùng sẽ tạo động lực bứt phá mạnh mẽ cho các trung tâm kinh tế trọng điểm."),
      D('body', "Nhiều mô hình sản xuất nông nghiệp công nghệ cao và kinh tế xanh đang được nhân rộng, góp phần nâng cao đời sống vật chất và tinh thần của bà con nông dân."),
      D('body', "Dự báo thời tiết những ngày tới tại khu vực Bắc Bộ và Trung Bộ trời tiếp tục có nắng đẹp, thuận lợi cho các hoạt động sản xuất và giao thương của nhân dân."),
    ],
    chuY: {
      tomTat: '1 chỗ cần chú ý, không có lỗi nào bắt buộc sửa.',
      loai: [
        { ten: 'Chỉ số kinh tế', nang: false, dem: 1, doan: [3] },
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

  'thongbao-to-dan-pho.txt': {
    doan: [
      D('head', 'THÔNG BÁO CỦA TỔ DÂN PHỐ'),
      D('body', 'Mời toàn thể nhân dân trong tổ dân phố chú ý lắng nghe thông báo.'),
      D('body', 'Thực hiện kế hoạch của Ủy ban nhân dân về việc tổng vệ sinh môi trường, Tổ dân phố xin thông báo tới toàn thể bà con nội dung như sau.'),
      D('body', 'Vào lúc 7 giờ 30 phút sáng Chủ Nhật tuần này, đề nghị mỗi gia đình cử ít nhất một thành viên tham gia quét dọn đường làng, ngõ xóm và khơi thông cống rãnh khu dân cư.'),
      D('body', 'Các hộ gia đình chủ động thu gom rác thải đúng nơi quy định, không để rác và vật liệu xây dựng lấn chiếm lòng đường, vỉa hè.'),
      D('body', 'Tổ dân phố kính mong toàn thể bà con nhân dân nhiệt tình hưởng ứng để cùng giữ gìn khu phố xanh, sạch, đẹp và văn minh.'),
    ],
    chuY: {
      tomTat: '1 chỗ cần chú ý, không có lỗi nào bắt buộc sửa.',
      loai: [
        { ten: 'Khung giờ sinh hoạt', nang: false, dem: 1, doan: [3] },
      ],
    },
  },

  'thongbao-phuong-xa.txt': {
    doan: [
      D('head', 'THÔNG BÁO CỦA ỦY BAN NHÂN DÂN XÃ PHƯỜNG'),
      D('body', 'Mời toàn thể nhân dân trong xã phường chú ý lắng nghe thông báo của Ủy ban nhân dân.'),
      D('body', 'Ủy ban nhân dân xin thông báo về việc đăng ký tài khoản định danh điện tử mức độ 2 và giải quyết thủ tục hành chính cho công dân trên địa bàn.'),
      D('body', 'Thời gian tiếp nhận hồ sơ từ thứ Hai đến thứ Sáu hàng tuần, buổi sáng từ 8 giờ 00 đến 11 giờ 30 phút, buổi chiều từ 13 giờ 30 phút đến 17 giờ 00.'),
      D('body', 'Địa điểm tại Bộ phận tiếp nhận và trả kết quả giải quyết thủ tục hành chính, tầng 1 trụ sở Ủy ban nhân dân.'),
      D('body', 'Khi đi, công dân mang theo Căn cước công dân và các giấy tờ liên quan để cán bộ chuyên môn hướng dẫn kịp thời.'),
      D('body', 'Ủy ban nhân dân trân trọng thông báo để toàn thể nhân dân trong xã phường được biết và chủ động thực hiện.'),
    ],
    chuY: {
      tomTat: '1 chỗ cần chú ý, không có lỗi nào bắt buộc sửa.',
      loai: [
        { ten: 'Thời gian làm việc', nang: false, dem: 1, doan: [3] },
      ],
    },
  },

  'thongbao-phun-thuoc.txt': {
    doan: [
      D('head', 'THÔNG BÁO PHUN THUỐC DIỆT MUỖI'),
      D('body', 'Mời toàn thể nhân dân trong thôn tổ chú ý lắng nghe thông báo.'),
      D('body', 'Sáng mai, từ 6 giờ 00 đến 9 giờ 00, Trạm Y tế phường sẽ phun thuốc diệt muỗi phòng chống sốt xuất huyết trên toàn địa bàn.'),
      D('body', 'Đề nghị bà con đóng kín cửa, che đậy thức ăn và nước uống, đưa trẻ nhỏ và người già ra khỏi nhà trong lúc phun thuốc.'),
      D('body', 'Sau khi phun khoảng ba mươi phút thì mở cửa cho thoáng rồi vào nhà sinh hoạt bình thường.'),
    ],
    chuY: {
      tomTat: '1 chỗ cần chú ý, không có lỗi nào bắt buộc sửa.',
      loai: [
        { ten: 'Giờ viết tắt', nang: false, dem: 1, doan: [3] },
      ],
    },
  },

  'thongbao-quoc-khanh.txt': {
    doan: [
      D('head', "THÔNG BÁO LỊCH NGHỈ LỄ QUỐC KHÁNH 2/9"),
      D('body', "Kính gửi toàn thể cán bộ, nhân viên cơ quan."),
      D('body', "Căn cứ Bộ luật Lao động và thông báo của Ủy ban nhân dân Thành phố Hồ Chí Minh, Ban Giám đốc thông báo lịch nghỉ lễ Quốc khánh năm 2026 như sau."),
      D('body', "Thời gian nghỉ tính từ thứ Hai ngày 31/8/2026 đến hết thứ Tư ngày 2/9/2026, tổng cộng 3 ngày làm việc. Cơ quan làm việc trở lại bình thường từ sáng thứ Năm ngày 3/9."),
      D('body', "Các bộ phận trực bố trí người trực theo lịch đã phân công. Danh sách trực cụ thể như sau: Phòng Kinh doanh — anh Trần Minh Đức; Phòng Kỹ thuật — anh Lê Hoàng Nam; Phòng Kho vận — chị Phạm Thu Hà."),
      D('body', "Trong thời gian nghỉ lễ, mọi sự cố khẩn cấp xin liên hệ số điện thoại đường dây nóng 1900 6868."),
      D('body', "Kính chúc toàn thể anh chị em cùng gia đình một kỳ nghỉ lễ vui vẻ và an toàn."),
    ],
    chuY: {
      tomTat: '1 chỗ cần chú ý, không có lỗi nào bắt buộc sửa.',
      loai: [
        { ten: 'Số điện thoại đường dây nóng', nang: false, dem: 1, doan: [5] },
      ],
    },
  },

  'chuong-01.docx': {
    doan: [
      D('head', 'Chương một — Người gác đèn'),
      D('body', 'Ngọn hải đăng đứng đó đã bốn mươi năm. Ông Tư cũng vậy.'),
      D('body', 'Mỗi tối, đúng lúc mặt trời chạm mặt biển, ông leo một trăm hai mươi bậc thang xoắn ốc lên đỉnh tháp, lau lại tấm kính, rồi bật đèn.'),
      D('body', 'Chưa một đêm nào ngọn đèn ấy tắt.'),
      D('body', 'Người trong làng bảo ông lẩn thẩn. Ông không cãi. Ông chỉ biết ngoài kia còn thuyền chưa về.'),
    ],
    chuY: {
      tomTat: '1 chỗ cần chú ý, không có lỗi nào bắt buộc sửa.',
      loai: [
        { ten: 'Số đọc dễ sai', nang: false, dem: 1, doan: [3] },
      ],
    },
  },

  'danh-sach-ung-ho.txt': {
    doan: [
      D('head', 'DANH SÁCH ỦNG HỘ ĐỒNG BÀO VÀ CÔNG ĐỨC THIỆN NGUYỆN'),
      D('body', 'Bùi Thị Thanh Tâm — hai triệu đồng'),
      D('body', 'Nguyễn Văn Đức — một triệu năm trăm nghìn đồng'),
      D('body', 'Gia đình bà Phúc Lâm — năm triệu đồng'),
      D('body', 'Tập thể lớp 9A trường Trung học cơ sở Lê Lợi — tám trăm nghìn đồng'),
      D('body', 'Phật tử Diệu Tâm chùa Viên Giác — ba triệu đồng'),
      D('body', 'Ban vận động xin trân trọng cảm ơn tấm lòng hảo tâm của quý vị.'),
    ],
    chuY: {
      tomTat: '1 chỗ cần chú ý, không có lỗi nào bắt buộc sửa.',
      loai: [
        { ten: 'Tên riêng xưng danh', nang: false, dem: 1, doan: [5] },
      ],
    },
  },

  'kich-ban-ban-hang.txt': {
    doan: [
      D('head', 'KỊCH BẢN TRI ÂN KHÁCH HÀNG & CHỐT ĐƠN LIVESTREAM'),
      D('body', 'Chào mừng quý khách đang theo dõi buổi phát sóng trực tiếp ngày hôm nay.'),
      D('body', 'Cửa hàng xin trân trọng cảm ơn quý khách đã luôn tin tưởng và đồng hành cùng chúng tôi trong suốt thời gian qua.'),
      D('body', 'Trong khung giờ vàng từ 19 giờ 00 đến 21 giờ 00 hôm nay, toàn bộ sản phẩm trà hoa vàng đặc sản và yến sào thượng hạng sẽ được áp dụng mức ưu đãi giảm 20%.'),
      D('body', 'Khách hàng để lại số điện thoại và địa chỉ nhận hàng tại phần bình luận sẽ được miễn phí vận chuyển trên toàn quốc.'),
      D('body', 'Đội ngũ chăm sóc khách hàng sẽ liên hệ xác nhận và gửi hàng trong ngày mai.'),
      D('body', 'Kính chúc quý khách có một buổi tối mua sắm thật nhiều niềm vui và chọn được sản phẩm ưng ý.'),
    ],
    chuY: {
      tomTat: '1 chỗ cần chú ý, không có lỗi nào bắt buộc sửa.',
      loai: [
        { ten: 'Khung giờ ưu đãi', nang: false, dem: 1, doan: [3] },
      ],
    },
  },

  'nghi-dinh-hanh-chinh.docx': {
    doan: [
      D('head', 'NGHỊ ĐỊNH SỐ 30/2020/NĐ-CP VỀ CÔNG TÁC VĂN THƯ'),
      D('body', 'Chính phủ ban hành Nghị định quy định về công tác văn thư và quản lý văn bản điện tử trong các cơ quan, tổ chức.'),
      D('body', 'Điều 1. Phạm vi điều chỉnh và đối tượng áp dụng.'),
      D('body', 'Nghị định này quy định về soạn thảo, ban hành văn bản; quản lý văn bản; lập hồ sơ và nộp lưu hồ sơ, tài liệu vào Lưu trữ cơ quan.'),
      D('body', 'Điều 2. Kỹ thuật trình bày văn bản hành chính.'),
      D('body', 'Văn bản hành chính phải được trình bày đúng thể thức, cỡ chữ, phông chữ và căn lề chuẩn theo quy định tại Phụ lục I kèm theo.'),
      D('body', 'Nghị định này có hiệu lực thi hành kể từ ngày 05 tháng 3 năm 2020.'),
    ],
    chuY: {
      tomTat: '1 chỗ cần chú ý, không có lỗi nào bắt buộc sửa.',
      loai: [
        { ten: 'Số hiệu văn bản pháp quy', nang: false, dem: 1, doan: [1] },
      ],
    },
  },
};

// ---------------------------------------------------------------- hồ sơ

/* Hồ sơ là MỘT CHỖ LÀM VIỆC, không phải preset giọng: nó giữ cả danh sách tệp
   đang mở của riêng nó. Đổi hồ sơ là đổi luôn dải tab và nội dung ở giữa. */
const HO_SO = [
  { ma: 'bai-viet', ten: 'Bài viết & Tin tức', giong: 'ngoc-linh',
    chinh: { tocDo: 0, caoDo: 0, amLuong: 100 },
    tep: ['tin-tuc-thoi-su.txt', 'bai-viet-nghe-lai.docx'] },

  { ma: 'thong-bao', ten: 'Thông báo & Loa phường', giong: 'xuan-vinh',
    chinh: { tocDo: 10, caoDo: 1, amLuong: 100 },
    tep: ['thongbao-to-dan-pho.txt', 'thongbao-phuong-xa.txt', 'thongbao-phun-thuoc.txt'] },

  { ma: 'sach-noi', ten: 'Sách nói & Kể chuyện', giong: 'bac-tuan',
    chinh: { tocDo: -10, caoDo: 0, amLuong: 90 },
    tep: ['chuong-01.docx'] },

  { ma: 'cong-duc', ten: 'Công đức & Thiện nguyện', giong: 'minh-duc',
    chinh: { tocDo: 0, caoDo: 0, amLuong: 100 },
    tep: ['danh-sach-ung-ho.txt'] },

  { ma: 'ban-hang', ten: 'Doanh nghiệp & Bán hàng', giong: 'truc-ly',
    chinh: { tocDo: 10, caoDo: 0, amLuong: 100 },
    tep: ['kich-ban-ban-hang.txt'] },

  { ma: 'phap-quy', ten: 'Pháp quy & Hành chính', giong: 'xuan-vinh',
    chinh: { tocDo: 0, caoDo: 0, amLuong: 100 },
    tep: ['nghi-dinh-hanh-chinh.docx'] },
];

if (typeof module !== 'undefined') {
  module.exports = { GIONG, GIONG_TRONG_DROPDOWN, TAI_LIEU, HO_SO };
}
