/* Giọng Việt — cầu nối JS <-> Python.

   Bê nguyên cách làm của ui/app.js: gọi qua pywebview.api, Python đẩy ngược
   trạng thái về bằng window.gd.push(). Giao thức đó đã chạy được, không viết
   lại.

   Thêm một thứ bản cũ không cần: ĐƯỜNG LÙI VỀ MOCK. Mở index.html bằng trình
   duyệt để dựng giao diện thì không có Python — lúc đó chạy đồng hồ giả trên
   dữ liệu mẫu. Có Python thì tiếng thật. Cùng một mã, không phải hai bản. */

'use strict';

/** Có Python bên kia không? */
const coPython = () => !!(window.pywebview && window.pywebview.api);

/** Gọi sang Python. Trả null nếu chưa sẵn sàng hoặc lỗi — người gọi tự lo. */
async function api(ten, ...thamSo) {
  const cau = window.pywebview && window.pywebview.api;
  if (!cau || typeof cau[ten] !== 'function') {
    console.warn('Chưa có hàm', ten);
    return null;
  }
  try {
    return await cau[ten](...thamSo);
  } catch (e) {
    console.error('Lỗi khi gọi', ten, e);
    return null;
  }
}

/* Python đẩy trạng thái về đây. giao-dien.js gán hàm thật vào biến này lúc
   khởi động; để rỗng ở đây cho tệp này không phụ thuộc ngược lại. */
let nhanTuPython = () => {};
const datNguoiNhan = (f) => { nhanTuPython = f; };

let khiNgheThuXong = () => {};
const datKhiNgheThuXong = (f) => { khiNgheThuXong = f; };

let khiBaoLoi = () => {};
const datKhiBaoLoi = (f) => { khiBaoLoi = f; };

/* Nhân bản giọng chạy nền vài phút, Python đẩy tiến độ về ba đường này.
   Thiếu chúng thì bấm nút xong màn hình đứng im — đúng lỗi đã vấp với
   ngheThuXong: Python gọi vào một hàm không tồn tại và lỗi chìm nghỉm. */
let khiTienDoGiong = () => {};
let khiGiongXong = () => {};
let khiGiongLoi = () => {};
const datKhiNhanBanGiong = (tienDo, xong, loi) => {
  khiTienDoGiong = tienDo; khiGiongXong = xong; khiGiongLoi = loi;
};

/* Xuất file chạy nền hàng phút, Python đẩy về bốn đường. Cùng họ với ba
   đường nhân bản giọng ở trên, và cùng một cái bẫy: giaodien/cau_noi.py gọi
   THẲNG vào window.gd.tienDoXuat / xuatXong / xuatLoi / xuatHuy. Thiếu hàm
   nào thì evaluate_js ném lỗi bên trong pywebview và bị nuốt mất — thanh
   tiến trình đứng im ở 0%, người dùng không biết là hỏng hay là chậm. */
let khiTienDoXuat = () => {};
let khiXuatXong = () => {};
let khiXuatLoi = () => {};
let khiXuatHuy = () => {};
const datKhiXuat = (tienDo, xong, loi, huy) => {
  khiTienDoXuat = tienDo; khiXuatXong = xong;
  khiXuatLoi = loi; khiXuatHuy = huy;
};

window.gd = {
  /** Vòng đọc bên Python gọi mỗi khi đổi đoạn, đổi trạng thái, hoặc báo lỗi.

      Gói tin đáng chú ý nhất: { pos, doan, state, thoiLuong }
      - doan      số ĐOẠN (ApiMoi đã dịch từ vị trí playlist)
      - thoiLuong số giây THẬT của khối WAV, đo từ chính tệp âm thanh sắp phát.
                  Đây là thứ để tô chữ chạy đúng nhịp với tiếng, gửi ngay sát
                  lúc phát chứ không gửi sớm - gửi sớm là chữ chạy trước tiếng. */
  push(goi) { nhanTuPython(goi || {}); },

  /** Bộ nghe thử báo đã phát xong — hoặc bị lần bấm mới huỷ giữa chừng.

      BẮT BUỘC phải có: nghe_thu.py:86 gọi thẳng vào đây. Thiếu hàm này thì
      nút nghe thử bấm xong sáng mãi, vì không có gì hạ nó xuống. Đã vấp. */
  ngheThuXong(ma) { khiNgheThuXong(ma || ''); },

  /** Nhân bản giọng: tiến độ · xong · lỗi. */
  tienDoGiong(msg) { khiTienDoGiong(String(msg || '')); },
  giongXong(ten) { khiGiongXong(String(ten || '')); },
  giongLoi(msg) { khiGiongLoi(String(msg || '')); },

  /** Xuất file: tiến độ · xong · lỗi · người dùng tự huỷ.

      Huỷ tách khỏi lỗi là cố ý: người dùng bấm Huỷ thì không phải hỏng hóc
      gì, đừng doạ họ bằng hộp thoại đỏ. */
  tienDoXuat(d) { khiTienDoXuat(d || {}); },
  xuatXong(kq) { khiXuatXong(kq || {}); },
  xuatLoi(msg) { khiXuatLoi(String(msg || '')); },
  xuatHuy() { khiXuatHuy(); },

  /** Bản cũ có các hàm này; giữ chỗ để Python gọi sang không bị lỗi. */
  baoTin(tieuDe, chiTiet) { console.info(tieuDe, chiTiet); },
  baoLoi(tieuDe, chiTiet) {
    console.error(tieuDe, chiTiet);
    khiBaoLoi(tieuDe || '', chiTiet || '');
  },
};
