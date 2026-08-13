/* Giọng Việt — bảy tình huống lỗi và chờ.
   Chữ lấy NGUYÊN VĂN từ README mục "Trạng thái lỗi và chờ". Đây là bản cuối
   của đặc tả, không được sửa cho gọn hay cho hay hơn.

   Nguyên tắc viết lỗi: nói điều đã xảy ra → trấn an dữ liệu còn nguyên →
   nói việc cần làm. Không mã lỗi, không thuật ngữ. */

'use strict';

const DAI_CANH_BAO = {
  binh_thuong: null,
  dang_tao: null,          // không có dải; chỉ vòng xoay ở máng số + thanh phát chờ

  mat_ket_noi: {
    muc: 'err',
    ten: 'Không kết nối được máy chủ đọc',
    noi: 'Văn bản của bạn vẫn được giữ nguyên. Kiểm tra lại mạng rồi thử lại.',
    nut: [{ nhan: 'Thử lại', acc: false }],
  },
  het_luot: {
    muc: 'warn',
    ten: 'Đã dùng hết dung lượng gói tháng này',
    noi: 'Bạn đã đọc 100.000/100.000 ký tự. Gói làm mới sau 12 ngày, '
       + 'hoặc nâng gói để dùng tiếp ngay.',
    nut: [{ nhan: 'Xem chi tiết', acc: false }, { nhan: 'Nâng gói', acc: true }],
  },
  giong_dang_tai: {
    muc: 'warn',
    ten: 'Đang tải giọng {giong} về máy',
    noi: 'Còn khoảng 1 phút nữa. Bạn vẫn soạn và sửa văn bản được, chưa nghe được.',
    nut: [{ nhan: 'Dùng giọng khác', acc: false }],
    phanTram: 62,          // thẻ giọng ở cột phải hiện thanh tiến trình
  },
  van_ban_qua_dai: {
    muc: 'warn',
    ten: 'Văn bản dài hơn giới hạn một lần xuất',
    noi: '12.400 ký tự, giới hạn 10.000. Khi xuất, phần mềm sẽ cắt thành 2 tệp, '
       + 'cắt ở ranh giới đoạn.',
    nut: [{ nhan: 'Xem chỗ cắt', acc: false }],
  },
  am_thanh_cu: {
    muc: 'warn',
    ten: 'Bạn vừa sửa văn bản, bản đã nghe là bản cũ',
    noi: '3 đoạn đã đổi: đoạn 4, 9 và 10. Nghe lại hoặc xuất lại để lấy bản mới.',
    nut: [{ nhan: 'Nghe lại 3 đoạn', acc: false }],
  },
};

/* Chấm và nhãn máy đọc ở góc phải thanh trạng thái. */
const NHAN_MAY_DOC = {
  binh_thuong:    { cham: 'ok',   nhan: 'VieNeu v3 Turbo · sẵn sàng' },
  dang_tao:       { cham: 'acc',  nhan: 'VieNeu v3 Turbo · đang tạo âm thanh' },
  dang_xuat:      { cham: 'acc',  nhan: 'Đang xuất tệp âm thanh · 34%' },
  mat_ket_noi:    { cham: 'err',  nhan: 'VieNeu v3 Turbo · mất kết nối' },
  het_luot:       { cham: 'warn', nhan: 'VieNeu v3 Turbo · hết lượt tháng này' },
  giong_dang_tai: { cham: 'warn', nhan: 'Đang tải {giong} · 62%' },
  van_ban_qua_dai:{ cham: 'ok',   nhan: 'VieNeu v3 Turbo · sẵn sàng' },
  am_thanh_cu:    { cham: 'ok',   nhan: 'VieNeu v3 Turbo · sẵn sàng' },
};

const TEN_TINH_HUONG = [
  ['binh_thuong',     'Bình thường'],
  ['mat_ket_noi',     'Mất kết nối máy chủ'],
  ['het_luot',        'Hết lượt / hết dung lượng gói'],
  ['giong_dang_tai',  'Giọng đang tải'],
  ['van_ban_qua_dai', 'Văn bản quá dài phải cắt'],
  ['am_thanh_cu',     'Âm thanh cũ sau khi sửa'],
  ['dang_tao',        'Đang tạo âm thanh'],
];

if (typeof module !== 'undefined') {
  module.exports = { DAI_CANH_BAO, NHAN_MAY_DOC, TEN_TINH_HUONG };
}
