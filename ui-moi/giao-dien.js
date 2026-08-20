/* Giọng Việt — màn hình chính. Dựng hình từ trạng thái, không giữ trạng thái
   riêng ở DOM. Mọi biến đổi đi qua trang-thai.js rồi vẽ lại.

   Chạy được ở hai chế độ: có Python thì tiếng thật qua bo_doc, không có thì
   đồng hồ giả trên dữ liệu mẫu (để dựng giao diện bằng trình duyệt). Xem
   cau-noi.js. */

'use strict';

const $ = (s) => document.querySelector(s);
const esc = (s) => String(s == null ? '' : s)
  .replace(/&/g, '&amp;').replace(/</g, '&lt;').replace(/>/g, '&gt;').replace(/"/g, '&quot;');
const ic = (t, n = 16) => `<svg width="${n}" height="${n}" aria-hidden="true"><use href="#i-${t}"/></svg>`;

let S = trangThaiBanDau(HO_SO);
let dongHoPhat = 0;
/* HAI đồng hồ khác nhau, đừng gộp:
   giayDaNghe  = tổng đã nghe, dùng cho đồng hồ ở chế độ nghe liền mạch
   giayDoanNay = đã nghe trong ĐOẠN hiện tại, dùng để biết khi nào sang đoạn
   Gộp làm một chính là lỗi "chỉ chạy chữ ở dòng đầu": ở chế độ liền mạch,
   tổng thời lượng là của cả bài nên phải đợi hết 88 giây mới sang đoạn 2. */
let giayDaNghe = 0;
let giayDoanNay = 0;
/* Đã tạm dừng giữa chừng? Cần biết để nút ở thanh công cụ ghi "Đọc tiếp" chứ
   không phải "Nghe toàn bộ" - Nghe toàn bộ đặt pos = 1, bấm nhầm là mất chỗ
   đang nghe dở của người ta. */
let daTamDung = false;
/* Trạng thái mô hình do Python đẩy sang: kiem_tra | dang_tai | san_sang | loi.
   Chưa sẵn sàng thì KHOÁ nút Nghe và Xuất — bày nút bấm được mà bấm không ra
   tiếng còn tệ hơn là khoá lại và nói rõ đang chờ. */
let moHinh = { trangThai: 'kiem_tra', tieuDe: 'Đang kiểm tra mô hình…', phanTram: 0 };
const moHinhSanSang = () => moHinh.trangThai === 'san_sang' || !coPython();

/* Tệp nào đang có chữ sửa chưa ghi ra đĩa. Khoá theo tên tệp, cùng cách
   TAI_LIEU đánh khoá, để đóng tab nào biết tab ấy.

   Vì sao cần: Ctrl+S CÓ lưu thật (luuVanBan → moi_luu_van_ban), nhưng không có
   gì tự lưu, không có dấu hiệu nào báo "chưa lưu", và cả hai đường đóng — đóng
   tệp lẫn đóng cửa sổ — đều đi thẳng, không hỏi một câu. Người lớn tuổi không
   tự đoán ra Ctrl+S; gõ sửa cả buổi rồi bấm dấu × là mất trắng.

   KHÔNG dùng lại vanTayTaiLieu() làm cờ: hàm ấy chỉ đếm TỔNG số ký tự, nên sửa
   một chữ thành chữ khác cùng độ dài là vân tay không đổi — cờ sẽ im lặng đúng
   lúc cần kêu nhất. Đánh dấu thẳng ở từng chỗ sửa mới không lọt. */
const chuaLuu = new Set();
let gioLuuCuoi = '';
const coSuaChuaLuu = () => chuaLuu.size > 0;

/* Cập nhật ĐÚNG cái nhãn ở thanh trạng thái, không vẽ lại cả màn.
   Đường gõ chữ cố ý không gọi dat() để khỏi dựng lại DOM và ném con trỏ về đầu
   bài; nên nếu chỉ thêm vào Set rồi đợi lần vẽ sau thì gõ cả buổi mà dòng
   "Chưa lưu" vẫn chưa hiện ra — đúng lúc cần nó nhất. */
function danhDauSua() {
  const t = tenTepDangXem(S);
  if (!t) return;
  chuaLuu.add(t);
  const nut = $('#ttLuu');
  if (nut) nut.innerHTML = veTinhTrangLuu();
}

// ---------------------------------------------------------------- thanh menu

/* Sáu menu theo ĐÚNG thứ tự và câu chữ của bản thiết kế.
   Mỗi mục là [nhãn, phím tắt] hoặc [nhãn, phím tắt, 'lý do chưa làm'].
   ['-'] là gạch ngăn nhóm.

   Có phần tử thứ ba = mục ấy CHƯA làm: hiện mờ, KHÔNG bấm được, và mang tooltip
   nói rõ vì sao. Đây là yêu cầu của chủ dự án: "chức năng nào code đã có thì nối
   vào menu, chỉ để xám những mục thật sự chưa làm. Không ẩn mục, không để bấm mà
   không có gì xảy ra." Bày ra mà bấm không ăn thua chính là thứ KPI cấm; giấu đi
   thì người dùng không biết phần mềm định có gì. Làm mờ kèm lý do là đường giữa. */
const MENUS = [
  ['Tệp', [['Mở tệp…', 'Ctrl+O'],
           ['Mở từ Google Docs…', '', 'Chưa làm — cần đăng nhập Google, dự kiến ở lượt sau'],
           // Thiết kế không nêu mục này, nhưng code CÓ và nó là đường duy nhất
           // mở danh sách tên–số. Giữ lại, đã báo ở mục "code làm tốt hơn thiết kế".
           ['Mở danh sách tên và số…', ''],
           ['Dán văn bản', 'Ctrl+V'], ['Lưu', 'Ctrl+S'],
           ['Xuất file âm thanh', 'Ctrl+E'], ['Đóng tệp', 'Ctrl+W'],
           ['-'],
           ['Ghép danh sách từ Google Sheet…', '', 'Chưa làm — màn Văn bản ghép chưa dựng'],
           ['-'],
           ['Cài đặt…', ''], ['Thoát', 'Alt+F4']]],
  /* ĐÃ GỠ (13/8): Hoàn tác · Làm lại · Cắt · Sao chép · Khoảng lặng 1 giây ·
     Ngắt đoạn. Sáu mục ấy bấm vào chỉ đóng menu rồi thôi, và không mục nào
     nối được: chúng cần một VÙNG SOẠN THẢO để sửa chữ tại chỗ, mà vùng đọc
     không có contenteditable cũng chẳng có textarea — văn bản chỉ đổi được
     qua Tìm và thay thế. Ngày nào có vùng soạn thảo thì thêm lại một thể.

     GIỮ "Thẻ cảm xúc": nó KHÔNG cần sửa văn bản. datThe() gắn thẻ cho đoạn
     đang chọn vào S.chips, và ba thẻ là tính năng thật của VieNeu. Trước đây
     chỉ Alt+1…3 chạy được, còn bấm chuột thì chết vì S.tags không nơi nào bật
     lên — nay nối vào LENH. */
  /* Sáu mục Hoàn tác…Chọn tất cả: trình duyệt tự lo trong vùng contenteditable,
     nhưng CHƯA có lệnh riêng để bấm từ menu, và Ctrl+A hiện chỉ chọn trong MỘT
     đoạn chứ không cả bài. Nói thật thế, đừng nối bừa vào một lệnh gần giống. */
  ['Chỉnh sửa', [['Hoàn tác', 'Ctrl+Z', 'Bấm phím Ctrl+Z ngay trong chữ thì được; nút menu chưa nối'],
                 ['Làm lại', 'Ctrl+Y', 'Bấm phím Ctrl+Y ngay trong chữ thì được; nút menu chưa nối'],
                 ['-'],
                 ['Cắt', 'Ctrl+X', 'Bấm phím Ctrl+X ngay trong chữ thì được; nút menu chưa nối'],
                 ['Sao chép', 'Ctrl+C', 'Bấm phím Ctrl+C ngay trong chữ thì được; nút menu chưa nối'],
                 ['Dán', 'Ctrl+V', 'Chưa làm — dán tại con trỏ khác với “Dán văn bản” ở menu Tệp'],
                 ['Chọn tất cả', 'Ctrl+A', 'Chưa làm — Ctrl+A hiện chỉ chọn trong một đoạn'],
                 ['-'],
                 ['Tìm và thay thế', 'Ctrl+H'], ['Soát văn bản', 'Ctrl+K']]],
  ['Chèn', [['Thẻ cảm xúc', 'Alt+1…3'],
            ['Khoảng lặng 1 giây', 'Alt+S', 'Chưa làm'],
            ['Ngắt đoạn', 'Enter', 'Bấm Enter ngay trong chữ thì được; nút menu chưa nối'],
            ['-'],
            ['Thêm cách đọc cho từ đang chọn…', '',
             'Chưa làm — mở được Từ điển phát âm, nhưng chưa mang chữ đang chọn sang']]],
  ['Giọng', [['Đổi giọng đọc', 'Ctrl+G'], ['Nghe mẫu giọng', 'Ctrl+M'],
             ['-'],
             ['Thư viện giọng', ''], ['Nhân bản giọng từ file…', ''],
             ['Thu âm để tạo giọng mới…', '', 'Chưa làm — chưa có phần thu âm'],
             ['-'],
             ['Từ điển phát âm', '']]],
  ['Xem', [['Thu gọn danh sách hồ sơ', 'Ctrl+B'], ['Cỡ chữ lớn hơn', 'Ctrl+='],
           ['Cỡ chữ nhỏ hơn', 'Ctrl+-'],
           ['-'],
           ['Toàn màn hình', 'F11', 'Chưa làm'],
           ['Giao diện tối', '']]],
  ['Trợ giúp', [['Hướng dẫn nhanh', 'F1'], ['Danh sách phím tắt', 'Ctrl+/'],
                ['Giới thiệu Giọng Việt', ''],
                ['-'],
                ['Kiểm tra bản cập nhật', '', 'Chưa làm'],
                ['Gửi phản hồi cho nhà phát triển', '', 'Chưa làm']]],
];

const THE_CAM_XUC = [['[cười]', 'Alt+1'], ['[thở dài]', 'Alt+2'], ['[hắng giọng]', 'Alt+3']];

/* Bảng con NEO VÀO NHÃN, không dùng bảng toạ độ cứng.
   Bản trước viết left:${6 + S.menu * 74}px — tức giả định mọi nhãn rộng đúng
   74px. Nhãn thật rộng 42 · 79 · 51 · 56 · 47 · 69px, nên bảng trôi dần: đo
   được lệch 0 · +32 · +27 · +50 · +68 · +96px, tới menu cuối thì bảng nằm cách
   chữ vừa bấm gần một trăm điểm ảnh. Bọc mỗi nhãn trong một ô position:relative
   rồi cho bảng left:0 là hết, mà không phải đo gì lúc chạy. */
const veMenu = () => `
  <div class="menu">
    ${MENUS.map(([ten, muc], i) => `<span class="menu__o">
      <button class="menu__muc${S.menu === i ? ' dang-mo' : ''}" data-menu="${i}">${ten}</button>
      ${S.menu !== i ? '' : `<div class="menu__roi roi">
        ${muc.map(([m, phim, chuaLam]) => (m === '-' ? '<div class="roi__ngan"></div>'
          : `<button class="roi__muc"${chuaLam
               ? ` disabled title="${esc(chuaLam)}"`
               : ` data-lenh="${esc(m)}"`}>
               <span class="roi__ten">${esc(m)}</span>
               <span class="roi__phim">${esc(phim || '')}</span></button>`)).join('')}
      </div>`}
    </span>`).join('')}
  </div>`;

// ---------------------------------------------------------------- thanh công cụ

/* Câu nhắc cho nút: nút đang KHOÁ thì nói LÝ DO, không nói việc nó làm.
   Yêu cầu của chủ dự án: "nút không dùng được thì làm mờ KÈM TOOLTIP NÓI LÝ DO".
   Nút mờ mà tooltip vẫn tả việc bình thường là bắt người lớn tuổi tự đoán vì sao
   bấm không ăn. */
const nhac = (binhThuong, lyDo) => ` title="${esc(lyDo || binhThuong)}"`;

function veCongCu() {
  const coVanBan = hienNgheVaXuat(S, TAI_LIEU);
  const dangPhat = S.view === 'dang_doc';
  const mo = coVanBan ? '' : ' disabled';        // chưa có văn bản thì chuyển màu dis
  const khoa = biKhoa(S) || !moHinhSanSang();
  const viKhoa = lyDoKhoa(S);
  const chuaCoChu = coVanBan ? '' : 'Chưa có văn bản — hãy Dán văn bản hoặc Mở tệp trước';
  return `
  <div class="congcu">
    <button class="nut" data-lenh="Dán văn bản"${nhac('Dán văn bản từ clipboard (Ctrl+V)')
      }>${ic('dan')}<span>Dán văn bản</span></button>
    <button class="nut" data-lenh="Mở tệp…"${nhac('Mở tệp văn bản (Ctrl+O)')
      }>${ic('thumuc')}<span>Mở file</span></button>
    <span class="congcu__ngan"></span>
    <button class="nut" data-lenh="Soát văn bản"${mo}${
      nhac('Xem các chỗ dễ đọc sai và văn bản sau chuẩn hoá (Ctrl+K)', chuaCoChu)
      }>${ic('tich')}<span>Soát văn bản</span></button>
    <span class="congcu__o">
      <button class="nut" id="nutThe"${mo}${
        nhac('Chèn thẻ cảm xúc vào đoạn đang chọn', chuaCoChu)
        }>${ic('cx')}<span>Thẻ cảm xúc</span>${ic('mui', 13)}</button>
      ${S.tags ? veMenuThe() : ''}
    </span>
    <span class="congcu__phai">
      <button class="nut" id="nutTim"${mo}${
        nhac('Tìm một từ trong văn bản và thay bằng từ khác (Ctrl+H)', chuaCoChu)
        }>${ic('kinhlup')}<span>Tìm và thay thế</span></button>
      ${coVanBan ? `<span class="congcu__ngan"></span>
        <button class="nut nut--vien nut--cao${dangPhat ? ' dang-phat' : ''}" id="nutNghe"${
          khoa ? ' disabled' : ''}${nhac(dangPhat ? 'Tạm dừng (Space)'
            : daTamDung ? 'Đọc tiếp từ đoạn ' + S.pos + ' (Space)'
            : 'Nghe liền mạch toàn bộ văn bản từ đầu (Space)', viKhoa)}>
          ${ic(dangPhat ? 'tamdung' : 'tamgiac', 13)}<span>${
            dangPhat ? 'Tạm dừng' : daTamDung ? 'Đọc tiếp' : 'Nghe toàn bộ'}</span></button>
        <button class="nut nut--acc nut--cao" id="nutXuat"${khoa ? ' disabled' : ''}${
          nhac('Mở hộp thoại xuất để chọn định dạng và nơi lưu (Ctrl+E)', viKhoa)}>
          ${ic('xuat')}<span>Xuất file âm thanh</span></button>` : ''}
    </span>
  </div>`;
}

/* Menu thẻ cảm xúc 260px. Ba thẻ này là tính năng thật của VieNeu-TTS: chèn
   thẳng vào chuỗi text là mô hình đọc ra ngữ điệu tương ứng. */
/* Cũng neo vào nút của nó, không viết cứng top:76px;left:250px như trước —
   toạ độ ấy đúng đúng một lần, với đúng một bố cục thanh công cụ. */
const veMenuThe = () => `
  <div class="roi congcu__roi">
    <div class="roi__nhom">Chèn vào đoạn ${S.sel}</div>
    ${THE_CAM_XUC.map(([t, p]) =>
      `<button class="roi__muc" data-the="${esc(t)}">
         <span class="chip">${esc(t)}</span><span style="flex:1"></span>
         <span class="roi__phim">${p}</span></button>`).join('')}
    <div class="roi__ngan"></div>
    <button class="roi__muc" data-the=""><span class="roi__ten">Gỡ thẻ khỏi đoạn này</span></button>
  </div>`;

// ---------------------------------------------------------------- tìm · cảnh báo

const veThanhTim = () => !S.find ? '' : `
  <div class="tim">
    <span class="tim__nhan">Tìm</span>
    <input class="onhap tim__o" id="oTim" spellcheck="false" autofocus
           value="${esc(S.chuTim || '')}">
    <span class="tim__dem" id="timDem">${
      ketQuaTim.length ? `${timThu + 1}/${ketQuaTim.length}` : '0/0'}</span>
    <button class="nut nut--icon" id="timTruoc" title="Chỗ trước">‹</button>
    <button class="nut nut--icon" id="timSau" title="Chỗ sau">›</button>
    <span class="tim__ngan"></span>
    <span class="tim__nhan">Thay bằng</span>
    <input class="onhap tim__o" id="oThay" spellcheck="false" value="${esc(S.chuThay || '')}">
    <button class="nut nut--vien" id="nutThay">Thay thế</button>
    <button class="nut nut--vien" id="nutThayTatCa">Thay tất cả</button>
    <button class="nut nut--icon tim__dong" id="dongTim">${ic('dong', 10)}</button>
  </div>`;

/* Vì sao lúc này chưa nghe được — trả câu RỖNG khi nghe được bình thường.

   Ba đường vào việc phát (máng số, nút Nghe đoạn, phím Space) đều hỏi qua đây,
   nên không còn cảnh đường này khoá mà đường kia vẫn lọt. Chữ lấy nguyên từ
   dải cảnh báo và nhãn máy đọc đang hiện sẵn trên màn hình - người dùng không
   phải học hai cách gọi cho cùng một chuyện. */
function lyDoKhoa(S) {
  if (!moHinhSanSang()) return moHinh.tieuDe || 'Máy đọc chưa sẵn sàng';
  if (!biKhoa(S)) return '';
  const d = DAI_CANH_BAO[S.situation];
  if (!d) return 'Chưa nghe được lúc này';
  const giong = GIONG.find((g) => g.ma === hoSoDangDung(S).giong);
  return d.ten.replace('{giong}', giong ? giong.ten : '');
}

function veCanhBao() {
  /* Lỗi THẬT từ Python đứng trên mọi tình huống mẫu: nó nói đúng chuyện vừa
     xảy ra trên máy này, còn bảng DAI_CANH_BAO là chữ dựng sẵn. Nút lấy thẳng
     từ gói (Python đã kèm sẵn "Kiểm tra lại" / "Đọc tiếp" cùng mã việc). */
  if (S.loiThat) {
    const l = S.loiThat;
    const nut = (l.nut && l.nut.length ? l.nut : [{ nhan: 'Đóng', act: '' }]);
    return `
  <div class="dai dai--err">
    <span class="dai__icon">${ic('canhbao', 18)}</span>
    <span class="dai__than">
      <span class="dai__ten">${esc(l.tieu_de || 'Có lỗi xảy ra')}</span>
      <div class="dai__noi">${esc(l.chi_tiet || '')}</div>
    </span>
    <span class="dai__nut">${nut.map((n, i) =>
      `<button class="nut ${i === 0 ? 'nut--acc' : 'nut--vien'}"
               data-loithat="${esc(n.act || '')}">${esc(n.nhan)}</button>`).join('')}
      <button class="nut nut--vien" data-loithat="" title="Bỏ qua thông báo này"
              >Bỏ qua</button></span>
  </div>`;
  }

  const d = DAI_CANH_BAO[S.situation];
  if (!d) return '';
  const giong = GIONG.find((g) => g.ma === hoSoDangDung(S).giong);
  const ten = d.ten.replace('{giong}', giong ? giong.ten : '');
  return `
  <div class="dai${d.muc === 'err' ? ' dai--err' : ''}">
    <span class="dai__icon">${ic('canhbao', 18)}</span>
    <span class="dai__than">
      <span class="dai__ten">${esc(ten)}</span>
      <div class="dai__noi">${esc(d.noi)}</div>
    </span>
    <span class="dai__nut">${d.nut.map((n) =>
      `<button class="nut ${n.acc ? 'nut--acc' : 'nut--vien'}"
               data-canhbao="${esc(n.lam || '')}">${esc(n.nhan)}</button>`).join('')}</span>
  </div>`;
}

/* Việc thật sau mỗi nút trên dải cảnh báo. Trước đây sáu nút này chỉ là chữ:
   không data-lenh, không id, không nhánh nào trong bộ bắt click — bấm vào không
   có gì xảy ra. Nặng nhất là "Thử lại" của mat_ket_noi: tình huống ấy nằm trong
   KHOA_NGHE_VA_XUAT nên Nghe và Xuất đều bị khoá, mà nút duy nhất để thoát ra
   lại chết, người dùng chỉ còn nước tắt chương trình.

   Tên việc và hành vi lấy từ bảng BN của bản mẫu (act / altAct). */
const LENH_CANH_BAO = {
  ve_binh_thuong: () => dat({ ...S, situation: 'binh_thuong' }),
  mo_chon_giong: () => dat({ ...S, situation: 'binh_thuong', roiGiong: true }),
  // Bản mẫu nhảy tới đúng chỗ sẽ bị cắt rồi trả màn về bình thường.
  xem_cho_cat: () => dat({ ...S, situation: 'binh_thuong', sel: 9, pos: 9 }),
  nghe_lai_doan_da_sua: () => {
    dat({ ...S, situation: 'binh_thuong', sel: 4, pos: 4 });
    batDauPhat();
  },
};

// ---------------------------------------------------------------- cột trái

const ICON_HO_SO = ['baiviet', 'danto', 'sach', 'danhsach'];

/* Hàng tệp nào đang được gõ lại tên. Để ở tầng module chứ không nhét vào S:
   phanCanLuu() ghi thẳng S xuống hoso-v2.json, mà "đang gõ dở tên" thì không
   phải thứ đáng nhớ qua lần chạy sau. Cùng chỗ với chuaLuu vì cùng bản chất. */
let suaTenTep = null;

/* Tên hiện trên hàng tệp — BA TẦNG, đúng như bản mẫu (nameAt):
     nhãn người dùng tự đặt  ->  tên tệp thật  ->  nhãn tự sinh.

   Vì sao phải có bảng nhãn riêng thay vì sửa thẳng tên tệp: trong sản phẩm này
   TÊN TỆP CHÍNH LÀ KHOÁ của TAI_LIEU, S.duongDanTep, S.loaiTep, S.chips và
   chuaLuu. Sửa tên tức là mổ vào khoá của năm kho, và đã đo được ba đường mất
   bài vì thế: xoá trắng ô là xoá luôn nội dung, đặt tên cho tệp chưa đặt tên là
   bài kẹt dưới khoá rỗng, đặt trùng tên tệp của hồ sơ khác là nuốt bài của hồ sơ
   ấy. Bản mẫu không dính vì nó tách hẳn: mảng tệp giữ ID, nhãn để bảng riêng,
   nội dung khoá theo ID. Đây là cách bê đúng mô hình ấy sang.

   Nhãn ĐÁNH SỐ THEO VỊ TRÍ (blankLabel của bản mẫu): đóng một ô rỗng ở giữa thì
   các ô rỗng sau tự tụt số. Giữ y vậy để hai bên không lệch nhau. */
function tenHienThi(ds, j) {
  const rieng = (S.nhanTep || {})[S.profile];
  if (rieng && rieng[j]) return rieng[j];
  if (ds[j]) return ds[j];
  let n = 0;
  for (let k = 0; k <= j; k++) if (!ds[k]) n++;
  return 'Văn bản mới ' + n;
}

/* Danh sách tệp lồng trong hàng hồ sơ. Chỉ hồ sơ đang chọn mới bung ra - nhờ
   vậy chiều cao cột trái không phụ thuộc số tệp của các hồ sơ khác.

   Hàng tệp đứng NGOÀI thẻ .hoso chứ không lồng vào trong, vì .hoso là <button>
   và HTML cấm nút lồng trong nút - nút × sẽ bị trình duyệt đẩy văng ra ngoài.
   Đứng ngoài cũng tránh luôn chuyện [data-hoso] bắt mất cú bấm: bộ bắt sự kiện
   hỏi [data-hoso] trước, mà closest() đi ngược lên cây. */
function veCayTep(i) {
  if (i !== S.profile) return '';
  const ds = tabDangMo(S);
  const dangXem = S.activeByProfile[S.profile];
  return `
    <div class="tepds">
      ${ds.map((ten, j) => {
        const nhan = tenHienThi(ds, j);
        const on = j === dangXem;
        if (suaTenTep === `${i}:${j}`) {
          return `<div class="tep tep--sua">
            <span class="tep__icon">${ic('tep', 13)}</span>
            <input class="tep__o" id="oTenTep" spellcheck="false"
                   value="${esc(nhan)}" data-suatep="${j}">
          </div>`;
        }
        /* tabindex + role: hàng tệp là <div> chứ không phải <button>, vì bên
           trong đã có nút ×, mà nút lồng trong nút thì trình duyệt tự đẩy ra
           ngoài. Không có hai thuộc tính này thì người chỉ dùng bàn phím không
           tới được hàng nào - dải tab cũ vướng đúng lỗi đó, đừng bê sang. */
        return `<div class="tep${on ? ' dang-xem' : ''}" data-tep="${j}"
                     tabindex="0" role="button" aria-current="${on}"
                     title="${esc(nhan)} · nháy đúp để đổi tên">
          <span class="tep__icon">${ic('tep', 13)}</span>
          <span class="tep__ten">${esc(nhan)}</span>
          <button class="tep__dong" data-dongtep="${j}" title="Đóng tệp">${ic('dong', 9)}</button>
        </div>`;
      }).join('')}
      <button class="nut tep__them" id="themTep"
              title="Mở thêm một tệp trong hồ sơ này">
        ${ic('cong', 12)}<span>Thêm tệp</span></button>
    </div>`;
}

function veCotTrai() {
  return `
  <div class="trai${S.rail ? ' thu-gon' : ''}">
    <div class="trai__dau">
      <button class="nut nut--icon" id="thuGon" title="${
        /* Nói rõ là thu CẢ danh sách tệp. Từ khi danh sách tệp chuyển vào cột
           trái, thu gọn là mất luôn lối đổi/thêm/đóng tệp — hứa "danh sách hồ
           sơ" rồi lấy đi cả tệp thì người dùng không nối được nhân quả, cứ
           tưởng chương trình vừa hỏng. */
        S.rail ? 'Mở lại danh sách hồ sơ và tệp (Ctrl+B)'
               : 'Thu gọn danh sách hồ sơ và tệp (Ctrl+B)'}">
        ${ic('bagach')}</button>
      <span class="trai__ten">Hồ sơ đọc</span>
    </div>
    <div class="trai__ds">
      ${S.profiles.map((h, i) => {
        const g = GIONG.find((x) => x.ma === h.giong);
        return `<button class="hoso${i === S.profile ? ' dang-dung' : ''}" data-hoso="${i}"
                        title="${esc(h.ten)}">
          <span class="hoso__icon">${ic(ICON_HO_SO[i % 4], 17)}</span>
          <span class="hoso__than">
            <span class="hoso__ten">${esc(h.ten)}</span>
            <span class="hoso__giong">${esc(g ? g.ten : '')}</span>
          </span></button>${veCayTep(i)}`;
      }).join('')}
      <button class="nut trai__lienket nhan-chu" data-lenh="Tạo hồ sơ mới" style="margin-top:4px"
              title="Tạo hồ sơ đọc mới">
        ${ic('cong', 15)}<span>Tạo hồ sơ mới</span></button>
    </div>
    <div class="trai__chan">
      <button class="nut trai__lienket" data-lenh="Thư viện giọng" title="Thư viện giọng">
        ${ic('micro')}<span class="nhan-chu">Thư viện giọng</span></button>
      <button class="nut trai__lienket" data-lenh="Cài đặt" title="Cài đặt">
        ${ic('banhrang')}<span class="nhan-chu">Cài đặt</span></button>
    </div>
  </div>`;
}

// ---------------------------------------------------------------- vùng đọc

function veVungDoc() {
  const doan = doanDangXem(S, TAI_LIEU);
  if (!doan.length) return `<div class="doc">${veRong()}</div>`;

  return `
  <div class="doc">
    <div class="doc__dau">
      <span class="doc__thongke">${esc(thongKe(doan))}</span>
      <!-- Gợi ý phải tả đúng thao tác hiện có. Câu cũ bảo "bấm số đoạn" trong
           khi số đã thôi làm nút là chỉ đường sai, còn hại hơn không ghi gì. -->
      <span class="doc__goiy">Bấm vào chữ để sửa như Notepad · nút ▶ bên phải để nghe riêng đoạn</span>
    </div>
    <div class="doc__cuon" id="cuon">
      ${doan.map((d, i) => veDoan(d, i + 1)).join('')}
    </div>
  </div>`;
}

function veDoan(d, n) {
  const cls = ['doan'];
  if (d.kieu === 'head') cls.push('doan--tieude');
  if (d.kieu === 'blank') cls.push('doan--trong');
  if (S.view === 'dang_doc' && n === S.pos) cls.push('dang-doc');
  // Chỉ chế độ nghe liền mạch mới làm mờ đoạn đã đọc xong. Nghe riêng thì
  // các đoạn phía trên giữ nguyên - người dùng đang dò chứ không nghe tuyến tính.
  else if (S.mode === 'all' && S.view === 'dang_doc' && n < S.pos) cls.push('doc-xong');
  else if (n === S.sel) cls.push('dang-chon');
  // Đang tạo âm thanh: nút ▶ hiện sẵn có viền, y như lúc đang đọc.
  if (S.situation === 'dang_tao' && n === S.pos) cls.push('dang-tao');
  // Tạm dừng giữa chừng: nút trở lại hình ▶ để bấm là đọc tiếp.
  if (daTamDung && n === S.pos) cls.push('tam-dung');

  const the = theCuaDoan(S, n);
  const dangCho = S.situation === 'dang_tao' && n === S.pos;
  /* Khoá thì nút play phải TRÔNG như đang khoá: mờ đi, con trỏ báo không dùng
     được. Vẫn bấm được - bấm vào sẽ nói rõ vì sao chưa nghe được, hơn hẳn một
     nút xám ngắt bấm không ăn gì. */
  const viKhoa = lyDoKhoa(S);
  /* Không treo nút ▶ ở đoạn không có chữ - bấm ra lỗi là nút giả. Kể cả đoạn
     vừa được Enter tạo ra và còn rỗng: nó tồn tại để người dùng gõ tiếp, chưa
     có gì mà đọc. */
  const coPlay = d.kieu !== 'blank' && String(d.chu || '').trim() !== '';

  /* GÕ THẲNG VÀO CHỮ, không có chế độ vào/ra ô sửa. Chủ dự án bấm thử: phải
     bấm nút rồi mới gõ được là quá nhiều bước, "muốn như Notepad".

     contenteditable chỉ bật khi KHÔNG đọc. Lúc đang đọc, nhịp tô chữ bọc từng
     chữ vào <span> để sáng dần theo tiếng; cho gõ vào giữa cái DOM đang bị
     viết lại 60 lần một giây là hai bên giẫm chân nhau.

     plaintext-only để dán từ web vào không kéo theo cả đống thẻ HTML. */
  const suaDuoc = S.view !== 'dang_doc' && d.kieu !== 'blank';

  return `<div class="${cls.join(' ')}" data-doan="${n}">
    <span class="doan__so">${
      dangCho ? '<span class="xoay xoay--nho" style="display:inline-block"></span>'
              : n}</span>
    <!-- data-doan đủ để nhịp đọc gạt lớp trên từng đoạn mà không dựng lại DOM -->
    <span class="doan__than">${d.kieu === 'blank' ? '' :
      `${the ? `<span class="doan__the" contenteditable="false" data-gothe="${n}"
             title="Bấm để gỡ thẻ cảm xúc">${esc(the)}</span>` : ''}<span
         class="doan__chu"${suaDuoc ? ' contenteditable="plaintext-only" spellcheck="false"' : ''}
         >${esc(d.chu)}</span>`}</span>${
    coPlay ? `
    <button class="doan__play${viKhoa ? ' la-khoa' : ''}" data-nghe="${n}"
            title="${esc(viKhoa
              || `Nghe riêng đoạn này, nghe hết đoạn thì dừng`)}"></button>` : ''}
  </div>`;
}

const veRong = () => {
  const h = hoSoDangDung(S);
  const g = GIONG.find((x) => x.ma === h.giong);
  return `<div class="rong"><div class="rong__khung">
    <div class="rong__icon">${ic('danto', 52)}</div>
    <div class="rong__ten">Dán văn bản vào đây để bắt đầu</div>
    <div class="rong__phu">
      Nhấn Ctrl+V, hoặc kéo thả tệp .txt, .docx, .rtf vào cửa sổ này.<br>
      Hồ sơ đang chọn: <b>${esc(h.ten)}</b> — ${esc(g ? g.ten : '')}.
    </div>
    <div class="rong__nut">
      <button class="nut nut--acc" data-lenh="Dán văn bản">Dán văn bản</button>
      <button class="nut nut--vien" data-lenh="Mở tệp…">Chọn tệp từ máy…</button>
    </div>
  </div></div>`;
};

// ---------------------------------------------------------------- cột phải

function veCotPhai() {
  const h = hoSoDangDung(S);
  const g = GIONG.find((x) => x.ma === h.giong);
  const chuY = chuYDangXem(S, TAI_LIEU);
  const dangTai = S.situation === 'giong_dang_tai';

  return `<div class="phai">
    <div class="the">
      <div class="the__phan">
        <div class="the__nhan">Hồ sơ đang dùng</div>
        <div class="c-nhan" style="margin-top:4px">${esc(h.ten)}</div>
      </div>
      <div class="the__ngan"></div>
      <div class="the__phan">
        <div class="the__nhan">Giọng đọc</div>
        <div class="giong-hang">
          <button class="chon" id="oGiong"
                  title="${esc(g ? g.ten + (g.ngan ? ' — ' + g.ngan : '') : '')}">
            ${ic('micro')}<span class="chon__gt">${esc(g ? g.ten : '')}</span>
            <span class="chon__mui">${ic('mui', 13)}</span></button>
          <button class="nut${S.mauDangPhat ? ' nut--dang' : ''}" id="ngheMau"
                  title="${S.mauDangPhat ? 'Đang đọc thử — bấm để dừng'
                                         : 'Nghe mẫu giọng (Ctrl+M)'}"
                  >${ic(S.mauDangPhat ? 'dunghan' : 'loa')}</button>
        </div>
        ${S.mauDangPhat ? `<div class="mau-dang-phat">
          <span class="cham cham--acc"></span>Đang phát mẫu ${esc(g ? g.ten : '')}…</div>` : ''}
        ${dangTai ? `<div style="margin-top:8px">
          <div class="phat__tien" style="width:100%"><i style="width:62%"></i></div>
          <div class="c-nho" style="margin-top:4px">Đang tải · 62%</div></div>` : ''}
        ${S.voiceOpen ? veRoiGiong() : ''}
      </div>
      <div class="the__ngan"></div>
      <div class="the__phan">
        <button class="chinh__dau" id="moChinh">
          <span class="the__nhan">Điều chỉnh</span>
          <span class="chinh__mui${S.tune ? ' mo' : ''}">${ic('mui', 13)}</span>
        </button>
        ${S.tune ? veThanhChinh(h) : `<div class="chinh__tom">${esc(tomTatChinh(h.chinh))}</div>`}
      </div>
    </div>
    ${!chuY ? '' : `<div class="the"><div class="the__phan">
      <div class="the__nhan">Cần chú ý</div>
      <div class="chuy__cau">${esc(chuY.tomTat)}</div>
      <div style="margin-top:8px">
        ${chuY.loai.map((l, i) => `<button class="chuy__dong" data-chuy="${i}">
          <span class="cham${l.nang ? ' cham--err' : ''}"></span>
          <span class="chuy__ten">${esc(l.ten)}</span>
          <span class="chuy__dem${l.nang ? ' nang' : ''}">${l.dem}</span></button>`).join('')}
      </div>
      <div class="chuy__chan">
        <button class="nut nut--vien" data-lenh="Soát văn bản"
                title="Mở màn hình soát văn bản">Soát văn bản</button>
        <button class="lienket" data-lenh="Từ điển phát âm"
                title="Ghi cách đọc riêng cho từ ngữ của bạn">Từ điển phát âm ›</button>
      </div>
    </div></div>`}
  </div>`;
}

const TRUOT = [
  ['tocDo', 'Tốc độ', -50, 100, (v) => (v > 0 ? '+' : v < 0 ? '−' : '') + Math.abs(v) + '%'],
  ['caoDo', 'Cao độ', -12, 12, (v) => (v > 0 ? '+' : v < 0 ? '−' : '') + Math.abs(v)],
  ['amLuong', 'Âm lượng', 0, 100, (v) => v + '%'],
];

const veThanhChinh = (h) => `
  ${TRUOT.map(([khoa, ten, min, max, hien]) => {
    const v = h.chinh[khoa];
    const pct = ((v - min) / (max - min)) * 100;
    return `<div class="chinh__truot">
      <div class="chinh__hang"><span class="chinh__ten">${ten}</span>
        <span class="chinh__gt">${hien(v)}</span></div>
      <button class="truot" data-truot="${khoa}">
        <span class="truot__ranh"></span>
        <span class="truot__day" style="width:${pct}%"></span>
        <span class="truot__num" style="left:${pct}%"></span></button>
    </div>`;
  }).join('')}
  <button class="nut nut--vien" style="width:100%;margin-top:12px" data-lenh="Đặt lại mặc định">
    Đặt lại mặc định</button>`;

/* Ô chọn giọng.

   Máy thật có 14 giọng, tên kèm giới tính, vùng miền và phong cách. Nhét hết
   vào một dòng là cụt hết đuôi — đúng thứ vừa thấy. Nên mỗi giọng chiếm HAI
   dòng: tên đậm ở trên, giới tính · vùng · phong cách ở dưới.

   Trong mỗi nhóm xếp Nữ trước Nam rồi theo vùng miền: người dùng chọn giọng
   gần như luôn bắt đầu bằng "nam hay nữ". */
const THU_TU_VUNG = { 'Miền Bắc': 0, 'Miền Trung': 1, 'Miền Nam': 2 };
const THU_TU_GIOI = { Nam: 0, Nữ: 1 };

/* Thứ tự chủ dự án chốt (2026-08-12): VÙNG MIỀN trước, trùng vùng thì Nam/Nữ,
   trùng nữa thì A-Z theo tên. So tên bằng localeCompare tiếng Việt, không thì
   "Đoan Trang" bị xếp sau "Thùy Dung" vì chữ Đ có dấu. */
const xepGiong = (a, b) =>
  ((THU_TU_VUNG[a.vung] ?? 9) - (THU_TU_VUNG[b.vung] ?? 9))
  || ((THU_TU_GIOI[a.gioi] ?? 9) - (THU_TU_GIOI[b.gioi] ?? 9))
  || String(a.ten || '').localeCompare(String(b.ten || ''), 'vi');

function veRoiGiong() {
  const dung = hoSoDangDung(S).giong;
  const ds = GIONG.filter((g) => GIONG_TRONG_DROPDOWN.includes(g.ma));

  const nhom = (rieng) => ds.filter((g) => g.rieng === rieng).sort(xepGiong).map((g) => {
    const dangNghe = S.dangNgheThu === g.ma;
    return `
    <button class="roi__muc roi__muc--hai" data-giong="${g.ma}"
            title="${esc(g.ten)}${g.ngan ? ' — ' + esc(g.ngan) : ''}">
      <span class="roi__tich">${g.ma === dung ? ic('tich', 14) : ''}</span>
      <span class="roi__than">
        <span class="roi__ten">${esc(g.ten)}</span>
        ${g.ngan ? `<span class="roi__phu">${esc(g.ngan)}</span>` : ''}
      </span>
      <span class="roi__nghe${dangNghe ? ' roi__nghe--dang' : ''}"
            data-nghegiong="${g.ma}"
            title="${dangNghe ? 'Đang đọc thử — bấm để dừng' : 'Nghe thử giọng này'}"
            >${ic(dangNghe ? 'dunghan' : 'tamgiac', 11)}</span>
    </button>`;
  }).join('');

  const coSan = nhom(false);
  const cuaToi = nhom(true);
  return `<div class="roi roi--giong" style="position:absolute;z-index:60;margin-top:4px">
    ${coSan ? `<div class="roi__nhom">Giọng có sẵn</div>${coSan}` : ''}
    ${cuaToi ? `<div class="roi__nhom">Giọng của tôi</div>${cuaToi}` : ''}
    <div class="roi__ngan"></div>
    <button class="roi__muc" data-lenh="Nhân bản giọng từ file…">
      <span class="roi__tich">${ic('cong', 13)}</span>
      <span class="roi__ten" style="color:var(--acc)">Nhân bản giọng từ file…</span>
    </button>
  </div>`;
}

// ---------------------------------------------------------------- thanh phát

function veThanhPhat() {
  if (S.situation === 'dang_tao') {
    return `<div class="phat">
      <span class="xoay xoay--to"></span>
      <span class="phat__dong">Đang tạo âm thanh cho đoạn ${S.pos}</span>
      <span class="phat__ghi">Thường mất 5–10 giây cho mỗi đoạn</span>
      <button class="nut nut--vien phat__huy" data-lenh="Dừng">Huỷ</button>
    </div>`;
  }
  if (S.view !== 'dang_doc') return '';

  const doan = doanDangXem(S, TAI_LIEU);
  const tong = tongThoiLuongDangNghe(S, TAI_LIEU);
  const daNghe = S.mode === 'one' ? giayDoanNay : giayDaNghe;
  const pct = tong ? Math.min(100, (daNghe / tong) * 100) : 0;

  return `<div class="phat">
    <button class="nut phat__nut phat__nut--acc" data-lenh="Tạm dừng">${ic('tamdung', 15)}</button>
    <button class="nut phat__nut" data-lenh="Dừng">${ic('dunghan', 13)}</button>
    <span class="phat__dong" id="phatDong">${S.mode === 'one'
      ? `Đang nghe riêng đoạn ${S.pos}` : `Đang đọc đoạn ${S.pos}/${doan.length}`}</span>
    <span class="phat__gio" id="phatGio">${dongHo(daNghe)} / ${dongHo(tong)}</span>
    <span class="phat__tien"><i id="phatTien" style="width:${pct}%"></i></span>
    <span class="phat__ghi">${S.mode === 'one'
      ? 'Nghe hết đoạn này sẽ dừng' : 'Đang chuẩn bị đoạn tiếp theo…'}</span>
  </div>`;
}

// ---------------------------------------------------------------- thanh trạng thái

/* Trước đây chỗ này in cứng chuỗi "Đã lưu 14:02" — nói đã lưu kể cả khi chưa
   lưu gì, mà giờ thì luôn là 14:02. Người lớn tuổi đọc dòng ấy rồi yên tâm đóng
   chương trình là mất bài. Nay nói đúng ba trạng thái có thật. */
function veTinhTrangLuu() {
  const ten = tenTepDangXem(S);
  if (ten && chuaLuu.has(ten)) return '<b>Chưa lưu</b> · ';
  if (gioLuuCuoi) return `Đã lưu ${esc(gioLuuCuoi)} · `;
  return '';
}

function veTrangThai() {
  const h = hoSoDangDung(S);
  const g = GIONG.find((x) => x.ma === h.giong);
  const m = S.exporting
    ? { cham: 'acc', nhan: `Đang xuất tệp âm thanh · ${S.phanTramXuat || 0}%` }
    : !moHinhSanSang()
      ? { cham: moHinh.trangThai === 'loi' ? 'err' : 'warn',
          nhan: moHinh.tieuDe + (moHinh.phanTram ? ` · ${moHinh.phanTram}%` : '') }
      : (NHAN_MAY_DOC[S.situation] || NHAN_MAY_DOC.binh_thuong);
  const soDoan = S.view === 'dang_doc' ? S.pos : S.sel;
  return `<div class="trangthai">
    <span class="trangthai__so" id="ttSo">Đoạn ${soDoan}, Cột 1</span>
    <span class="trangthai__phai">
      <span class="cham cham--${m.cham}"></span>
      <span id="ttNhan">${esc(m.nhan.replace('{giong}', g ? g.ten : ''))}</span>
      <span class="trangthai__ngan"></span>
      <span><span id="ttLuu">${veTinhTrangLuu()}</span>Hồ sơ: ${esc(h.ten)}</span>
    </span>
  </div>`;
}

// ---------------------------------------------------------------- vẽ toàn bộ

/* Màn nào chiếm TOÀN cửa sổ, màn nào chỉ thay phần giữa.

   Căn cứ đo được, không phải ý thích: đếm nút "Quay lại màn hình chính" trong
   bảy tệp thiết kế — Thư viện giọng 3, Cài đặt 2, Từ điển phát âm 2, Văn bản
   ghép 2; còn Màn hình chính 0 và Soát văn bản 0. Bốn màn có đường quay lại là
   bốn màn đứng riêng.

   SOÁT VĂN BẢN KHÔNG nằm trong đây. Chính tệp thiết kế của nó viết: "Vẫn là cửa
   sổ chính của Giọng Việt — cùng danh sách hồ sơ, cùng văn bản ở giữa", và nút
   của nó là "Đóng bảng kết quả soát" chứ không phải "Quay lại màn hình chính".
   Nó là một BẢNG mở thêm ở dưới, không phải một màn. */
const MAN_TOAN_CUA_SO = {
  giong:  { ten: 'Thư viện giọng',   dong: 'Đóng giọng' },
  tudien: { ten: 'Từ điển phát âm',  dong: 'Đóng từ điển' },
  caidat: { ten: 'Cài đặt',          dong: 'Đóng cài đặt' },
};

/* Thanh tiêu đề dùng chung cho mọi màn. Cửa sổ dựng frameless nên ba nút
   thu nhỏ / phóng to / đóng phải luôn có, kể cả ở màn phụ. */
const veThanhTieuDe = (nhan, lenhLui) => `
    <div class="tieude">
      <span class="tieude__dau pywebview-drag-region">
        ${lenhLui
          ? `<button class="nut nut--icon tieude__lui" data-lenh="${esc(lenhLui)}"
                     title="Quay lại màn hình chính">${ic('lui', 15)}</button>`
          : `<span class="dau-hieu">${ic('hieu', 10)}</span>`}
        <span class="tieude__ten">${esc(nhan)} — Giọng Việt</span>
      </span>
      <span class="tieude__keo pywebview-drag-region"></span>
      <button class="cuaso" data-cuaso="thu_nho" title="Thu nhỏ">${ic('thunho', 10)}</button>
      <button class="cuaso" data-cuaso="phong_to"
              title="${S.cuaSoKin ? 'Thu về cỡ vừa' : 'Phóng to'}"
        >${ic(S.cuaSoKin ? 'thuvua' : 'phongto', 10)}</button>
      <button class="cuaso cuaso--dong" data-cuaso="dong" title="Đóng">${ic('dong', 10)}</button>
    </div>`;

function ve() {
  const cuonCu = $('#cuon') ? $('#cuon').scrollTop : 0;
  const ten = tenTepDangXem(S) || 'Chưa đặt tên';
  document.documentElement.dataset.theme = S.theme === 'toi' ? 'dark' : 'light';
  // Cỡ chữ chỉ áp cho VÙNG ĐỌC, không phóng cả giao diện: phóng hết thì nút và
  // menu to ra theo, tràn khỏi cửa sổ, và người lớn tuổi mất luôn chỗ bấm.
  document.documentElement.style.setProperty('--zoom-doc', (S.zoom || 100) / 100);

  const toan = MAN_TOAN_CUA_SO[S.man];
  $('#goc').innerHTML = toan
    /* Màn đứng riêng: bỏ hết khung của màn chính — không thanh menu, không thanh
       công cụ, không dải tệp, không hai cột, không dải phát. Chỉ còn thanh tiêu
       đề có đường lùi, rồi thân màn chiếm trọn phần còn lại. */
    ? `${veThanhTieuDe(toan.ten, toan.dong)}
      ${veVienKeo()}
      <div class="manphu">${veGiua()}</div>`
    : `${veThanhTieuDe(ten, null)}
      ${veVienKeo()}
    ${veMenu()}${veCongCu()}${veThanhTim()}${veCanhBao()}
    <div class="thanchinh${S.man !== 'chinh' ? ' thanchinh--phu' : ''}">${veCotTrai()}${
      veGiua()}${veCotPhai()}</div>
    ${veThanhPhat()}${veTrangThai()}`;

  if ($('#cuon')) $('#cuon').scrollTop = cuonCu;
  if ($('#oTim')) $('#oTim').focus();
  ganLaiCache();
  veLopNoi();
  veBangThu();
}

/* Tám dải mỏng ở mép để kéo đổi cỡ cửa sổ.

   Cửa sổ dựng frameless nên Windows không cho sẵn viền nào để kéo. Tự vẽ dải
   rồi nhờ chính Windows xử lý (xem ApiMoi.moi_keo_vien): làm vậy mới có đủ
   bám con trỏ, khung xem trước, tôn trọng cỡ tối thiểu và snap ra mép màn
   hình — tự tính toạ độ bằng JS thì mất hết và kéo lúc nào cũng giật. */
const VIEN_KEO = ['tren', 'duoi', 'trai', 'phai',
                  'trentrai', 'trenphai', 'duoitrai', 'duoiphai'];

const veVienKeo = () => VIEN_KEO
  .map((v) => `<span class="vien vien--${v}" data-vien="${v}"></span>`).join('');

/* Nút giữa chỉ mang MỘT nghĩa tại một thời điểm: đang nhỏ thì là "Phóng to",
   đang kín thì là "Thu về cỡ vừa" — nhãn và biểu tượng đổi theo, y như mọi
   cửa sổ Windows. Ghép "Phóng to / thu vừa" vào một nhãn là bắt người dùng tự
   đoán lần bấm này sẽ ra cái nào.

   Hỏi Python vì chỉ nó đo được cửa sổ thật; kéo mép bằng chuột cũng đổi trạng
   thái mà giao diện không hề hay biết. */
async function capNhatNutCuaSo() {
  if (!coPython()) return;
  const kin = await api('moi_cua_so_kin');
  if (!!kin !== !!S.cuaSoKin) dat({ ...S, cuaSoKin: !!kin });
}

/* Phần GIỮA cửa sổ: màn chính, hoặc một màn phụ phủ lên. Cột trái và cột phải
   luôn còn đó — người lớn tuổi mà bị nhảy sang màn khác hẳn thì mất phương
   hướng, không biết đường quay lại. */
function veGiua() {
  if (S.man === 'soat') return veManSoat(S, duLieuSoat);
  if (S.man === 'giong') { danhDauNgheThu(); return veManGiong(S, duLieuGiong); }
  if (S.man === 'tudien') return veManTuDien(S, duLieuTuDien);
  if (S.man === 'caidat') return veManCaiDat(S, duLieuCaiDat);
  return veVungDoc();
}

/* Ba thanh chỉnh phải đi xuống Python, không thì kéo xong tiếng vẫn y nguyên.

   Gắn vào dat() để mọi đường đều bao được — kéo thanh, đổi hồ sơ, nạp lúc mở
   chương trình — thay vì nhớ gọi ở từng chỗ rồi sót một chỗ. Chỉ gọi sang
   Python khi ba con số THỰC SỰ đổi: dat() chạy mỗi lần bấm bất cứ thứ gì. */
let chinhAmDaGui = null;

function guiChinhAm() {
  const h = hoSoDangDung(S);
  if (!h) return;
  /* Ba con số nằm trong h.chinh, KHÔNG phải h trực tiếp — datChinh() ghi vào
     `{ ...h, chinh: { ...h.chinh, [khoa]: gt } }`.

     Đọc nhầm thành h.tocDo là cả ba ra undefined, khoá thành
     "undefined|undefined|undefined" nên chỉ gửi đúng một lần, và Python nhận
     được ba giá trị rỗng nên dựng ra chuỗi lọc RỖNG. Kết quả: kéo thanh Tốc
     độ lên +95% mà tiếng không nhanh hơn một chút nào. Chủ dự án bấm thử mới
     lộ ra — bộ kiểm cũ chỉ canh "có gọi sang Python", không canh GIÁ TRỊ gửi
     đi, nên nó xanh trong khi tính năng chết. */
  const c = h.chinh || {};
  const khoa = `${c.tocDo}|${c.caoDo}|${c.amLuong}`;
  if (khoa === chinhAmDaGui) return;
  chinhAmDaGui = khoa;
  if (coPython()) {
    api('moi_dat_chinh_am',
        { tocDo: c.tocDo ?? 0, caoDo: c.caoDo ?? 0, amLuong: c.amLuong ?? 100 });
  }
}

const dat = (moi) => { S = moi; ve(); henLuuHoSo(); guiChinhAm(); };

// ---------------------------------------------------------------- nhịp đọc

/* HAI ĐƯỜNG VẼ, đừng gộp lại.

   ve()        dựng lại toàn bộ. Chỉ chạy khi ĐỔI CẤU TRÚC: đổi hồ sơ, đổi
               tab, mở menu, đổi tình huống. Hiếm, người dùng bấm mới có.

   veNhipDoc() chỉ sờ đúng vài node. Chạy 4 lần/giây suốt lúc đọc.

   Gộp làm một thì mỗi nhịp phát phải nhét lại toàn bộ HTML vùng đọc - đo được
   907 KB với tài liệu 3.000 đoạn. Dựng chuỗi thì nhanh (10,8 ms) nhưng nhét
   vào DOM rồi dàn trang lại mới là chỗ tốn, và nó rơi đúng vào lúc máy đang
   bận tổng hợp tiếng. Người lớn tuổi nhìn chữ giật là tưởng máy hỏng. */

let nodeDoan = [];      // các node đoạn, hứng lại sau mỗi lần vẽ toàn bộ
let posDaVe = -1;       // đoạn đang tô, để biết có phải dời không
let toChuId = 0;        // requestAnimationFrame của vòng tô chữ
/* Python đang lái vòng đọc? Lúc đó mốc tô chữ lấy từ thời lượng WAV thật do
   Python đẩy về, nên veNhipDoc KHÔNG được tự khởi động tô chữ bằng mốc ước
   lượng — làm vậy là bọc span hai lần cho cùng một đoạn. */
let pythonLai = false;

function ganLaiCache() {
  nodeDoan = Array.from(document.querySelectorAll('[data-doan]'));
  posDaVe = -1;
}

// ---------------------------------------------------------------- tô từng chữ

/* Bê nguyên nguyên lý từ ui/app.js (batDauToChu). VieNeu không cho biết mốc
   thời gian từng chữ, nên mỗi chữ mang khoảng [b, e] theo tỉ lệ của cả đoạn;
   nhân với thời lượng thật của đoạn là ra thời điểm của từng chữ.

   KHÁC bản cũ một chỗ, và là chỗ đáng kể: bản cũ bọc span cho MỌI chữ của MỌI
   dòng ngay lúc dựng — tài liệu 3.000 đoạn là hơn 40.000 span nằm sẵn trong
   DOM. Ở đây chỉ bọc span cho ĐÚNG đoạn đang đọc, đọc xong thì trả lại chữ
   thường. Cùng hiệu quả nhìn thấy, mà DOM lúc nào cũng nhẹ. */

/* Độ trễ từ lúc Python báo "sắp phát đoạn này" đến lúc tiếng thật sự ra loa.

   Python đẩy gói tin ngay TRƯỚC khi gọi Speaker.play(), rồi play() mới dựng
   tiến trình ffplay, mở thiết bị âm thanh và đệm. Suốt khoảng đó loa còn im,
   nên chữ phải đứng đợi đúng bằng ngần ấy.

   Con số này giờ do PYTHON TỰ ĐO và gửi kèm mỗi gói tin (`treMs`) — xem
   ApiMoi._cap_nhat_tre. Tự đo vì nó phụ thuộc máy và phụ thuộc cả việc máy
   đang bận gì: đo được 621–855 ms trên 12 giọng, nhưng có lúc kẹt CPU vọt lên
   2,9 giây.

   Giá trị dưới đây chỉ dùng cho MẨU ĐẦU TIÊN, lúc chưa có gì để đo. Trước đây
   để 240 ms — đó là lúc tiến trình ffplay xuất hiện, chưa tính phần mở thiết
   bị và đệm, nên chữ vượt lên trước tiếng khoảng nửa giây ở mọi đoạn.

   Đo lại: py giaodien_moi/do_tre_phat.py */
let TRE_PHAT_MS = Number(localStorage.getItem('gd-tre-phat')) || 700;

function dungToChu() {
  if (toChuId) cancelAnimationFrame(toChuId);
  toChuId = 0;
}

/** Trả một đoạn về chữ thường, gỡ hết span. */
function traLaiChuThuong(nut) {
  if (!nut) return;
  const o = nut.querySelector('.doan__chu');
  if (o && o.dataset.goc != null) {
    o.innerHTML = o.dataset.goc;
    delete o.dataset.goc;
  }
}

let toChuDoan = 0;      // đoạn đang tô
let toChuTong = 0;      // tổng số giây đã gộp cho đoạn đó
let toChuMoc = 0;       // mốc bắt đầu, giữ nguyên qua các mẩu

/** Bọc span cho từng chữ của đoạn rồi chạy vòng tô.

    `soDoan` để biết gói tin này có phải mẩu tiếp theo của CÙNG một đoạn không.
    Đoạn dài bị tach_chunk cắt làm nhiều mẩu, Python đẩy mỗi mẩu một gói kèm
    thời lượng riêng. Không gộp lại thì mỗi mẩu tô lại đoạn từ chữ đầu — nhìn
    như chữ chạy giật lùi rồi lao đi. */
function batDauToChu(nut, thoiLuong, soDoan, tu, den, trongSo, treMs) {
  // Python tự đo được độ trễ ra loa của chính máy này thì dùng số đó; chưa đo
  // được (mẩu đầu tiên) mới dùng mặc định.
  const tre = treMs > 0 ? treMs : TRE_PHAT_MS;
  dungToChu();
  if (!nut || !(thoiLuong > 0)) return;
  const o = nut.querySelector('.doan__chu');
  if (!o) return;

  /* Mẩu tiếp theo của CÙNG một đoạn? Nhận ra bằng "đoạn này đã bọc span rồi"
     (dataset.goc đã lưu bản gốc), chứ không dựa vào vòng lặp còn chạy hay
     không — vòng lặp có thể đã kết thúc trong lúc chờ mẩu sau tổng hợp xong. */
  const tiepTuc = soDoan != null && soDoan === toChuDoan && o.dataset.goc != null;

  /* Python có gửi phạm vi của mẩu không? Có thì tô ĐÚNG khúc chữ của mẩu
     này với ĐÚNG thời lượng WAV của nó, và mỗi mẩu một mốc riêng.

     Đây là chỗ chữ vốn chạy lệch tiếng. Trước đây mọi mẩu dùng chung một mốc
     và cộng dồn thời lượng, nên có hai cái sai chồng nhau:
       · tỉ lệ ký tự của mẩu không trùng tỉ lệ thời lượng của nó — câu ngắn
         nhiều số đọc lâu hơn câu dài toàn chữ;
       · khoảng nghỉ giữa hai mẩu (nghi_cau 0,30s / nghi_doan_vb 0,60s) trôi
         qua mà không ai tính, nên chữ chạy vượt lên trước tiếng, mẩu sau lệch
         hơn mẩu trước.
     Mốc riêng từng mẩu xoá cả hai. */
  const coPhamVi = typeof tu === 'number' && typeof den === 'number' && den > tu;

  if (coPhamVi) {
    toChuDoan = soDoan == null ? 0 : soDoan;
    toChuTong = thoiLuong;
    toChuMoc = performance.now() + tre;
  } else if (tiepTuc) {
    toChuTong += thoiLuong;
  } else {
    toChuDoan = soDoan == null ? 0 : soDoan;
    toChuTong = thoiLuong;
    toChuMoc = performance.now() + tre;
  }

  // Bọc span một lần cho cả đoạn; mẩu tiếp theo dùng lại span đã có.
  if (!tiepTuc) {
    const chip = o.querySelector('.doan__the');
    const html = chip ? chip.outerHTML : '';
    const chuGoc = (o.textContent || '').replace(chip ? chip.textContent : '', '').trim();
    if (!chuGoc) return;
    if (o.dataset.goc == null) o.dataset.goc = o.innerHTML;
    o.innerHTML = html + chiaTu(chuGoc, 0, 1, trongSo)
      .map((w) => `<span class="tu" data-b="${w.b}" data-e="${w.e}">${esc(w.t)}</span>`)
      .join(' ');
  }

  const chu = o.querySelectorAll('.tu');
  if (!chu.length) return;

  const chay = () => {
    // toChuMoc đã cộng sẵn TRE_PHAT_MS: chữ đứng im chờ tiếng bắt kịp rồi mới chạy.
    const f = (performance.now() - toChuMoc) / (toChuTong * 1000);
    chu.forEach((x) => {
      const t = trangThaiChu(+x.dataset.b, +x.dataset.e, f, coPhamVi ? tu : null, den);
      x.classList.toggle('da-doc', t === 'da');
      x.classList.toggle('dang-doc', t === 'dang');
    });
    toChuId = f < 1 ? requestAnimationFrame(chay) : 0;
  };
  chay();
}

/** Một chữ nên ở trạng thái nào: 'da' đã đọc · 'dang' đang đọc · '' chưa tới.

    Tách riêng khỏi vòng vẽ để đo được bằng số mà không cần DOM — xem
    ui-moi/do-lech-chu-tieng.mjs. `tu` là null nghĩa là không có phạm vi mẩu,
    lúc đó [b, e] tính theo cả đoạn như trước.

    b, e  khoảng của chữ trong ĐOẠN, 0..1
    f     đã đi được bao nhiêu phần của MẨU đang phát, 0..1
    tu,den phạm vi của mẩu trong đoạn, 0..1 */
function trangThaiChu(b, e, f, tu, den) {
  if (tu != null) {
    // Chữ ngoài mẩu này: phía trước coi như đọc xong, phía sau chưa tới. Không
    // thế thì mỗi mẩu lại tẩy trắng phần mẩu trước vừa tô.
    if (e <= tu) return 'da';
    if (b >= den) return '';
    b = (b - tu) / (den - tu);
    e = (e - tu) / (den - tu);
  }
  if (f >= e) return 'da';
  return f >= b ? 'dang' : '';
}

/** Giữ đoạn đang đọc ở khoảng giữa khung.

    Tự tính toạ độ chứ KHÔNG dùng scrollIntoView — bản cũ đã đi đường đó rồi
    quay lại: scrollIntoView kéo theo cả trang chứ không riêng khung văn bản,
    và khi đọc liên tiếp thì các lần cuộn mượt huỷ lẫn nhau nên đoạn đang đọc
    hay nằm lệch hẳn xuống đáy. */
function cuonToiDoanHienTai(nut) {
  const box = $('#cuon');
  if (!box || !nut || !box.getBoundingClientRect) return;

  const oBox = box.getBoundingClientRect();
  const oDoan = nut.getBoundingClientRect();
  const dinh = box.scrollTop + (oDoan.top - oBox.top);

  // Đoạn dài có thể cao hơn cả khung nhìn. Căn giữa lúc đó sẽ đẩy mất phần đầu
  // lên trên mép, người đọc mất chỗ bắt đầu - nên bám mép trên.
  const dich = oDoan.height >= box.clientHeight
    ? dinh
    : dinh - (box.clientHeight - oDoan.height) / 2;

  const toiDa = Math.max(0, box.scrollHeight - box.clientHeight);
  box.scrollTo({ top: Math.max(0, Math.min(dich, toiDa)), behavior: 'smooth' });
}

function veNhipDoc() {
  const doan = doanDangXem(S, TAI_LIEU);

  // --- chỉ khi ĐỔI ĐOẠN mới đụng tới danh sách đoạn ---
  if (S.pos !== posDaVe) {
    nodeDoan.forEach((nut, i) => {
      const n = i + 1;
      const dangDoc = n === S.pos;
      // Chỉ chế độ liền mạch mới làm mờ đoạn đã đọc; nghe riêng thì giữ nguyên.
      const xong = S.mode === 'all' && n < S.pos;
      nut.classList.toggle('dang-doc', dangDoc);
      nut.classList.toggle('doc-xong', xong);
      nut.classList.toggle('dang-chon', false);

      // Mũi tên ▶ nay do CSS vẽ theo lớp .dang-doc vừa gạt ở trên, nên vòng
      // này không phải sờ vào chữ trong máng số nữa.
    });

    // Đoạn vừa rời trả về chữ thường, đoạn vừa tới bọc span rồi chạy tô chữ.
    traLaiChuThuong(nodeDoan[posDaVe - 1]);
    const dang = nodeDoan[S.pos - 1];
    cuonToiDoanHienTai(dang);
    if (!pythonLai) {
      const doanNay = doan[S.pos - 1];
      batDauToChu(dang, doanNay ? doanNay.chu.length / KY_TU_MOI_GIAY : 0);
    }
    posDaVe = S.pos;

    const d = $('#phatDong');
    if (d) {
      d.textContent = S.mode === 'one'
        ? `Đang nghe riêng đoạn ${S.pos}` : `Đang đọc đoạn ${S.pos}/${doan.length}`;
    }
    const tt = $('#ttSo');
    if (tt) tt.textContent = `Đoạn ${S.pos}, Cột 1`;
  }

  // --- mỗi nhịp: đồng hồ và thanh tiến trình, hai node ---
  const tong = tongThoiLuongDangNghe(S, TAI_LIEU);
  const gio = (g) => `${String(Math.floor(g / 60)).padStart(2, '0')}:${
    String(Math.floor(g % 60)).padStart(2, '0')}`;
  // Nghe riêng thì đồng hồ đếm trong ĐOẠN, liền mạch thì đếm cả bài.
  const daNghe = S.mode === 'one' ? giayDoanNay : giayDaNghe;
  const g = $('#phatGio');
  if (g) g.textContent = `${dongHo(daNghe)} / ${dongHo(tong)}`;
  const t = $('#phatTien');
  if (t) t.style.width = (tong ? Math.min(100, (daNghe / tong) * 100) : 0) + '%';
}

// ---------------------------------------------------------------- phát giả lập

/* CẮM ENGINE: chỗ này sau thay bằng gọi sang Python (bo_doc). Giai đoạn mock
   chỉ chạy đồng hồ để thấy thanh phát và đoạn đang đọc động đậy đúng. */
const doDaiDoan = (d) => (d && d.chu ? d.chu.length / KY_TU_MOI_GIAY : 0);

/** Đoạn kế tiếp CÓ CHỮ. Đoạn rỗng không có gì để đọc nên nhảy qua. */
function doanKeTiep(doan, tu) {
  for (let k = tu + 1; k <= doan.length; k++) {
    if (doan[k - 1].chu.trim()) return k;
  }
  return 0;
}

/* HAI ĐƯỜNG PHÁT, cùng một chỗ vào.

   Có Python  → gọi sang bo_doc, tiếng thật, mốc tô chữ lấy từ thời lượng WAV.
   Không có   → đồng hồ giả trên dữ liệu mẫu, để dựng giao diện bằng trình
                duyệt mà không phải bật cả engine.

   Cùng một mã cho cả hai, không đẻ ra hai bản phải đồng bộ với nhau. */

async function batDauPhat(tiepTuc = false) {
  clearInterval(dongHoPhat);
  daTamDung = false;
  if (!tiepTuc) { giayDaNghe = 0; giayDoanNay = 0; }
  veNhipDoc();

  if (coPython()) {
    /* BẮT BUỘC chờ xong mới phát. Trước đây việc gửi đoạn nằm ở chỗ khác và
       chạy bất đồng bộ, không ai bảo đảm nó xong trước lời gọi phát — bấm
       Nghe nhanh tay sau khi đổi tab là loa đọc tài liệu của tab trước.

       "Đọc tiếp" thì KHÔNG gửi lại: gửi lại là dựng playlist mới và mất chỗ
       đang đọc dở, mà đọc tiếp thì vẫn đúng tài liệu ấy. */
    if (!tiepTuc) await guiDoanSangPython();
    pythonLai = true;
    /* Python trả {"loi": ...} khi mô hình chưa sẵn sàng hoặc đoạn không có chữ
       để đọc. Trước đây không ai đọc giá trị trả về nên lỗi bị nuốt sạch: màn
       "đang đọc" vẫn hiện, đồng hồ vẫn nhích, mà loa im - người dùng tưởng máy
       treo. dungPhat() dọn cả nhịp lẫn nguồn phát rồi trả về màn sẵn sàng.

       Dùng .then() chứ KHÔNG await: await ở đây sẽ dời thời điểm khởi nhịp
       đồng hồ sang sau lượt gọi Python, làm đồng hồ lệch với tiếng. */
    (tiepTuc ? api('moi_doc_tiep')
      : S.mode === 'one' ? api('moi_nghe_doan', S.pos)
        : api('moi_nghe_toan_bo')
    ).then((kq) => {
      if (!kq || !kq.loi) return;
      dungPhat();
      moBao(kq.loi, 'Chưa nghe được');
    });

    /* Vẫn phải chạy một nhịp, nhưng CHỈ để nhích đồng hồ và thanh tiến trình.
       Việc sang đoạn do Python đẩy về, không phải việc của nhịp này.

       Thiếu đoạn dưới đây là đồng hồ đứng im 00:00 suốt cả bài trong khi tiếng
       vẫn chạy - người dùng tưởng máy treo. */
    dongHoPhat = setInterval(() => {
      giayDoanNay += 0.25;
      giayDaNghe += 0.25;
      veNhipDoc();
    }, 250);
    return;
  }
  dongHoPhat = setInterval(() => {
    const doan = doanDangXem(S, TAI_LIEU);
    const dai = doDaiDoan(doan[S.pos - 1]);

    giayDoanNay += 0.25;
    giayDaNghe += 0.25;
    if (giayDoanNay < dai) { veNhipDoc(); return; }

    // Nghe riêng thì hết đoạn là dừng, không chạy tiếp.
    if (S.mode === 'one') { dungPhat(); return; }
    const ke = doanKeTiep(doan, S.pos);
    if (!ke) { dungPhat(); return; }

    // Đổi đoạn KHÔNG phải đổi cấu trúc: danh sách đoạn vẫn y nguyên, chỉ dời
    // chỗ tô. Nên vẫn đi đường nhẹ, không dựng lại DOM.
    S = { ...S, pos: ke, sel: ke };
    giayDoanNay = 0;
    veNhipDoc();
  }, 250);
}

function dungPhat() {
  clearInterval(dongHoPhat);
  pythonLai = false;
  daTamDung = false;
  if (coPython()) api('moi_dung');
  dungToChu();
  traLaiChuThuong(nodeDoan[posDaVe - 1]);
  dongHoPhat = 0;
  giayDaNghe = 0;
  giayDoanNay = 0;
  dat({ ...S, view: 'san_sang' });
}

// ---------------------------------------------------------------- bắt sự kiện

// ---------------------------------------------------------------- nạp văn bản

/* Đặt nội dung mới vào tab đang xem. Dùng chung cho dán, mở tệp, kéo thả. */
function datTaiLieu(kq) {
  if (!kq) return;
  if (kq.loi) { moBao(kq.loi); return; }

  const ten = kq.ten || 'Chưa đặt tên';
  // Vừa nạp từ đĩa thì trong bộ nhớ đúng bằng trên đĩa — sạch cờ chưa lưu.
  chuaLuu.delete(ten);
  TAI_LIEU[ten] = {
    /* KHÔNG có đoạn rỗng - bỏ ngay lúc nạp, đúng bản thiết kế. Giữ lại thì
       văn bản hiện những dòng đánh số mà không có chữ nào, và mọi thứ bám theo
       số đoạn (thẻ cảm xúc, dấu đã-bỏ-qua ở màn Soát) phải đếm cả chúng. */
    doan: (kq.doan || []).filter(
      (d) => d && d.kieu !== 'blank' && String(d.chu || '').trim() !== ''),
    // Soát văn bản chưa nối; để rỗng chứ không bịa ra con số.
    chuY: { tomTat: '', loai: [] },
  };
  const ds = tabDangMo(S).slice();
  ds[S.activeByProfile[S.profile]] = ten;
  // Nhớ đường dẫn để lần chạy sau mở lại được. Văn bản dán không có đường dẫn.
  const dd = kq.duongDan
    ? { ...S.duongDanTep, [ten]: kq.duongDan } : S.duongDanTep;
  // Nhớ LOẠI tài liệu: danh sách công đức đọc theo đường khác hẳn văn bản.
  const lt = { ...(S.loaiTep || {}), [ten]: kq.loai === 'congduc' ? 'congduc' : 'vanban' };
  dungPhat();
  dat({ ...dongHetMenu(S),
        tabsByProfile: { ...S.tabsByProfile, [S.profile]: ds },
        duongDanTep: dd, loaiTep: lt,
        view: 'san_sang', pos: 1, sel: 1 });
  // Danh sách vừa mở thì Python đã dựng playlist rồi — đánh dấu là đã gửi để
  // khỏi bắt nó đọc lại tệp lần nữa ngay lập tức.
  if (kq.loai === 'congduc') vanTayDaGui = vanTayTaiLieu();
  else guiDoanSangPython();
  if ((kq.canhBao || []).length) {
    moBao(`${kq.canhBao.length} dòng máy chưa hiểu số tiền, sẽ đọc nguyên văn. `
          + `Ví dụ: ${kq.canhBao[0]}`);
  }
}

async function danVanBan() {
  if (!coPython()) { moBao('Dán văn bản cần chạy bằng GiongViet.py.'); return; }
  datTaiLieu(await api('moi_dan_van_ban'));
}

async function moTep() {
  if (!coPython()) { moBao('Mở tệp cần chạy bằng GiongViet.py.'); return; }
  datTaiLieu(await api('moi_mo_tep'));
}

/* Danh sách tên và số — chức năng gốc của chương trình, dùng ở chùa. Mỗi dòng
   một người; engine dựng câu từ mẫu trong lời dẫn của hồ sơ, chèn lời mở đầu,
   lời giữa, lời kết và cứ mấy người thì nghỉ dài một nhịp. */
async function moDanhSach() {
  if (!coPython()) { moBao('Mở danh sách cần chạy bằng GiongViet.'); return; }
  datTaiLieu(await api('moi_mo_danh_sach'));
}

// ---------------------------------------------------------------- tìm và thay thế

let ketQuaTim = [];     // [{doan, viTri}] các chỗ khớp
let timThu = 0;         // đang ở kết quả thứ mấy

function chayTim(chuoi) {
  ketQuaTim = [];
  timThu = 0;
  const q = (chuoi || '').trim().toLowerCase();
  if (!q) return;
  doanDangXem(S, TAI_LIEU).forEach((d, i) => {
    let k = -1;
    const chu = d.chu.toLowerCase();
    while ((k = chu.indexOf(q, k + 1)) >= 0) ketQuaTim.push({ doan: i + 1, viTri: k });
  });
}

function toiKetQua(buoc) {
  if (!ketQuaTim.length) return;
  timThu = (timThu + buoc + ketQuaTim.length) % ketQuaTim.length;
  const k = ketQuaTim[timThu];
  dat(chonDoan(S, k.doan));
  const nut = nodeDoan[k.doan - 1];
  if (nut) cuonToiDoanHienTai(nut);
}

/** Thay thế: sửa thẳng vào mảng đoạn rồi gửi lại sang Python. */
function thayThe(tim, thay, tatCa) {
  const q = (tim || '').trim();
  if (!q) return 0;
  const ten = tenTepDangXem(S);
  const t = TAI_LIEU[ten];
  if (!t) return 0;

  let dem = 0;
  const re = new RegExp(q.replace(/[.*+?^${}()|[\]\\]/g, '\\$&'), tatCa ? 'gi' : 'i');
  const batDau = tatCa ? 0 : Math.max(0, (ketQuaTim[timThu] || {}).doan - 1);
  for (let i = batDau; i < t.doan.length; i++) {
    if (!re.test(t.doan[i].chu)) continue;
    const truoc = t.doan[i].chu;
    t.doan[i] = { ...t.doan[i], chu: truoc.replace(re, thay || '') };
    dem += tatCa ? (truoc.match(new RegExp(re.source, 'gi')) || []).length : 1;
    if (!tatCa) break;
  }
  if (dem) {
    danhDauSua();
    dungPhat();
    // Sửa văn bản xong thì bản âm thanh đã nghe là bản cũ — đúng tình huống 5.
    dat({ ...S, situation: 'am_thanh_cu' });
    chayTim(q);
    guiDoanSangPython();
  }
  return dem;
}

// ---------------------------------------------------------------- xuất file

let hopXuat = null;     // { ten, duoi, dinhDang, thuMuc, tach, … }

async function moHopXuat() {
  const doan = doanDangXem(S, TAI_LIEU);
  if (!doan.length) return;
  const ten = tenTepDangXem(S) || 'giongdoc';
  const g = GIONG.find((x) => x.ma === hoSoDangDung(S).giong);

  const goi = coPython() ? await api('moi_goi_y_xuat', ten) : null;
  hopXuat = {
    tenTep: ten,
    soDoan: doan.length,
    tenGiong: g ? g.ten : '',
    ten: (goi && goi.ten) || ten.replace(/\.[^.]+$/, ''),
    duoi: '.wav',
    dinhDang: 'wav24',
    thuMuc: (goi && goi.thu_muc) || 'Tài liệu\\GiongViet\\Export',
    tach: 'mot',
  };
  dat({ ...dongHetMenu(S), exportOpen: true });
}

function veLopNoi() {
  const noi = $('#lopnoi');
  if (!noi) return;
  noi.innerHTML = (S.exportOpen && hopXuat ? veHopXuat(hopXuat) : '')
                + (S.xuatGiaiDoan === 'chay' ? veHopDangXuat(S.xuatTienDo || {}) : '')
                + (S.xuatGiaiDoan === 'xong' ? veHopXuatXong(S.xuatKetQua || {}) : '')
                + (S.hopTin ? veHopTin(S.hopTin) : '')
                + (S.toast ? veBaoXuatXong(S.toast) : '');

  const g = (id) => noi.querySelector('#' + id);

  if (S.hopTin) {
    const dsNut = S.hopTin.nut || [];
    if (dsNut.length) {
      dsNut.forEach((b) => {
        const el = g('tin_' + b.ma);
        if (!el) return;
        el.onclick = () => {
          const xong = hopHoiXong;
          hopHoiXong = null;
          dat({ ...S, hopTin: null });
          if (xong) xong(b.ma);
        };
      });
    } else {
      g('tinDong').onclick = () => dat({ ...S, hopTin: null });
    }
    return;
  }

  if (S.xuatGiaiDoan === 'chay') {
    // Chạy nền chỉ giấu hộp đi; việc xuất vẫn chạy và phần trăm chuyển xuống
    // thanh trạng thái. Xong lúc đang chạy nền thì báo bằng thông báo góc.
    g('xChayNen').onclick = () => dat({ ...S, xuatGiaiDoan: null });
    g('xHuyXuat').onclick = (e) => {
      /* Đổi nhãn NGAY, đừng đợi Python trả lời. Mẩu đang tổng hợp có thể còn
         chạy tới 40 giây nữa mới tới chốt kiểm huỷ được — trong khoảng đó
         người dùng bấm Huỷ mà không thấy gì đổi sẽ bấm tiếp mấy lần rồi tưởng
         máy treo. Chủ dự án bấm thử đã nhận xét "lâu mới đóng". */
      e.target.disabled = true;
      e.target.textContent = 'Đang dừng…';
      huyXuat();
    };
    return;
  }
  if (S.xuatGiaiDoan === 'xong') {
    g('xMoThuMuc').onclick = () => {
      if (coPython()) api('mo_thu_muc', (S.xuatKetQua || {}).thuMuc);
      dat({ ...S, xuatGiaiDoan: null, xuatKetQua: null });
    };
    g('xDongXong').onclick = () => dat({ ...S, xuatGiaiDoan: null, xuatKetQua: null });
    return;
  }
  if (!S.exportOpen || !hopXuat) return;

  g('xHuy').onclick = () => dat({ ...S, exportOpen: false });
  g('xDinhDang').onchange = (e) => {
    hopXuat.dinhDang = e.target.value;
    hopXuat.duoi = e.target.value.startsWith('mp3') ? '.mp3' : '.wav';
    g('xDuoi').textContent = hopXuat.duoi;
  };
  g('xChon').onclick = async () => {
    const d = coPython() ? await api('chon_thu_muc') : null;
    if (d) { hopXuat.thuMuc = d; g('xThuMuc').textContent = d; g('xThuMuc').title = d; }
  };
  noi.querySelectorAll('[data-tach]').forEach((b) => {
    b.onclick = () => { hopXuat.tach = b.dataset.tach; veLopNoi(); };
  });
  g('xBatDau').onclick = () => {
    hopXuat.ten = g('xTen').value.trim() || 'giongdoc';
    batDauXuat();
  };
}

/* Bấm Bắt đầu xuất: hộp chuyển sang giai đoạn 2 và ở lại đó, vì đó là chỗ
   duy nhất có nút Huỷ — xuất mất hàng phút thật, không phải hai giây. Muốn
   làm việc tiếp thì bấm "Chạy nền", lúc ấy mới đóng hộp và chuyển phần trăm
   xuống thanh trạng thái.

   Không có Python (mở index.html bằng trình duyệt để dựng giao diện) thì
   chạy đồng hồ giả qua đúng ba giai đoạn ấy. Đường lùi này CHỈ để xem giao
   diện; trong chương trình thật mọi con số đều do Python đo và gửi sang. */
let dongHoXuat = 0;

function trongHopXuat() {
  return S.xuatGiaiDoan === 'chay' || S.xuatGiaiDoan === 'xong';
}

async function batDauXuat() {
  const ten = hopXuat.ten + hopXuat.duoi;
  if (!coPython()) { xuatGia(ten); return; }

  /* Gửi lại đoạn TRƯỚC khi xuất, và ÉP gửi. Bên Python xuất từ self._playlist,
     mà playlist chỉ dựng lại ở moi_dat_doan / moi_nghe_doan / moi_doc_danh_sach
     - không đường nào trong số đó nằm trên lối xuất. Không gửi thì gõ sửa xong
     bấm Xuất luôn là ra tệp mang chữ CŨ, mà màn hình vẫn hiện chữ mới nên người
     dùng không có cách nào biết.
     Ép (true) chứ không để nó tự so vân tay: vanTayTaiLieu() chỉ đếm TỔNG số ký
     tự, nên sửa một chữ thành chữ khác cùng độ dài là vân tay không đổi và lần
     gửi bị bỏ qua. Xuất là việc hiếm, gửi thừa một lượt rẻ hơn ra tệp sai.
     Còn nếu vừa bấm "Nghe đoạn này" thì playlist đang chỉ có ĐÚNG đoạn ấy -
     không gửi lại là tệp xuất ra mất gần hết tài liệu. */
  await guiDoanSangPython(true);

  const loi = await api('moi_bat_dau_xuat',
                        hopXuat.ten, hopXuat.thuMuc, hopXuat.tach, hopXuat.dinhDang);
  // Python trả về chuỗi là chưa chạy được gì cả — giữ nguyên hộp giai đoạn 1
  // để người dùng sửa lựa chọn, đừng đẩy họ sang màn tiến trình rỗng.
  if (typeof loi === 'string' && loi) { moBao(loi); return; }
  dat({ ...S, exportOpen: false, exporting: true, phanTramXuat: 0,
        xuatGiaiDoan: 'chay', xuatKetQua: null,
        xuatTienDo: { ten, moTa: 'Đang chuẩn bị…', troiQua: '00:00', conLai: '—' } });
}

function huyXuat() {
  if (coPython()) { api('moi_huy_xuat'); return; }
  clearInterval(dongHoXuat);
  dongHoXuat = 0;
  dat({ ...S, exporting: false, xuatGiaiDoan: null });
}

/** Đồng hồ giả cho lúc không có Python. Không ghi tệp nào. */
function xuatGia(ten) {
  const pct = { v: 0 };
  dat({ ...S, exportOpen: false, exporting: true, phanTramXuat: 0,
        xuatGiaiDoan: 'chay', xuatKetQua: null,
        xuatTienDo: { ten, moTa: 'Đang chuẩn bị…', troiQua: '00:00', conLai: '—' } });
  clearInterval(dongHoXuat);
  dongHoXuat = setInterval(() => {
    pct.v += 12;
    if (pct.v < 100) {
      nhanTienDoXuat({
        ten, phanTram: pct.v, moTa: `Đang xử lý mục ${Math.ceil(pct.v / 12)}/9`,
        troiQua: '00:0' + Math.ceil(pct.v / 12), conLai: '00:0' + (9 - Math.ceil(pct.v / 12)),
        daGhi: (pct.v / 8).toFixed(1).replace('.', ',') + ' MB',
      });
      return;
    }
    clearInterval(dongHoXuat);
    dongHoXuat = 0;
    nhanXuatXong({
      ten,
      thoiLuong: dinhDangThoiLuong(soGiay(doanDangXem(S, TAI_LIEU))),
      kichThuoc: '11,6 MB', xuLy: '00:27',
      duongDan: hopXuat.thuMuc + '\\' + ten, thuMuc: hopXuat.thuMuc,
    });
  }, 250);
}

/* Tiến độ về mỗi khi xong một mẩu. KHÔNG đi qua dat(): dat() dựng lại toàn
   bộ HTML, mà đây là lúc máy đang bận tổng hợp tiếng và người dùng có thể
   đang gõ trong ô tìm kiếm — vẽ lại cả trang là cướp mất chỗ gõ của họ.

   Hộp đang mở  -> vẽ lại mỗi lớp nổi, rẻ và không đụng vùng đọc.
   Đang chạy nền -> sờ đúng một chữ trên thanh trạng thái. */
function nhanTienDoXuat(d) {
  if (!S.exporting) return;
  S = { ...S, phanTramXuat: d.phanTram || 0,
        xuatTienDo: { ...(S.xuatTienDo || {}), ...d } };
  if (S.xuatGiaiDoan === 'chay') { veLopNoi(); return; }
  const nhan = $('#ttNhan');
  if (nhan) {
    nhan.textContent = `Đang xuất tệp âm thanh · ${S.phanTramXuat}%`;
    return;
  }
  ve();
}

function nhanXuatXong(kq) {
  // Hộp còn mở thì chuyển sang giai đoạn 3; đang chạy nền thì báo bằng thông
  // báo góc, đúng luồng mục "Hộp thoại xuất file" của đặc tả.
  if (trongHopXuat()) {
    dat({ ...S, exporting: false, xuatGiaiDoan: 'xong', xuatKetQua: kq });
    return;
  }
  dat({ ...S, exporting: false, xuatGiaiDoan: null, toast: {
    ten: kq.ten, thoiLuong: kq.thoiLuong, dungLuong: kq.kichThuoc,
    thuMuc: kq.thuMuc || kq.duongDan,
  } });
}

datKhiXuat(
  nhanTienDoXuat,
  nhanXuatXong,
  (msg) => {
    dat({ ...S, exporting: false, xuatGiaiDoan: null });
    moBao(msg || 'Chưa xuất được tệp âm thanh.');
  },
  () => {
    // Người dùng tự bấm Huỷ thì không phải hỏng hóc, chỉ cần xác nhận gọn.
    dat({ ...S, exporting: false, xuatGiaiDoan: null });
    moBao('Đã dừng xuất tệp âm thanh.');
  });

/** Thông báo ngắn cho các lỗi nhẹ. Dùng lại khung thông báo góc. */
/* Thông báo ngắn. PHẢI truyền tiêu đề riêng: khung thông báo góc vốn có tiêu
   đề đóng cứng "Đã xuất xong tệp âm thanh", nên trước đây bấm Huỷ xuất xong
   lại hiện ra đúng dòng "Đã xuất xong" — trái ngược hẳn việc vừa làm. Chủ dự
   án bấm thử mới thấy. */
function moBao(chu, tieuDe = 'Thông báo') {
  dat({ ...S, toast: { tieuDe, ten: chu, thoiLuong: '', dungLuong: '', thuMuc: '' } });
}

// ---------------------------------------------------------------- bảng lệnh

const LENH = {
  'Dán văn bản': () => danVanBan(),
  'Mở tệp…': () => moTep(),
  'Mở danh sách tên và số…': () => moDanhSach(),
  'Xuất file âm thanh': () => moHopXuat(),
  'Tạo hồ sơ mới': () => {
    // Đặc tả: thêm hồ sơ trống (một tab chưa đặt tên) và chuyển sang ngay.
    const moi = { ma: 'moi-' + S.profiles.length, ten: 'Hồ sơ mới',
                  giong: hoSoDangDung(S).giong,
                  chinh: { tocDo: 0, caoDo: 0, amLuong: 100 }, tep: [''] };
    const i = S.profiles.length;
    dungPhat();
    dat({ ...dongHetMenu(S),
          profiles: [...S.profiles, moi],
          tabsByProfile: { ...S.tabsByProfile, [i]: [''] },
          activeByProfile: { ...S.activeByProfile, [i]: 0 },
          profile: i, view: 'san_sang', pos: 1, sel: 1 });
  },
  'Soát văn bản': () => moManSoat(),
  'Đóng soát': () => dat({ ...dongHetMenu(S), man: 'chinh' }),
  'Thư viện giọng': () => moManGiong(),
  'Nhân bản giọng từ file…': () => nhanBanGiong(),
  'Đóng giọng': () => { dungNgheThu(); dat({ ...dongHetMenu(S), man: 'chinh' }); },
  'Từ điển phát âm': () => moManTuDien(),
  'Cài đặt': () => moManCaiDat(),
  // Thiết kế ghi nhãn có ba chấm; giữ nguyên nhãn, trỏ về cùng một việc.
  'Cài đặt…': () => moManCaiDat(),
  /* Thoát đi qua đúng cửa mà nút × của cửa sổ đi: hỏi trước nếu còn chữ chưa
     lưu, rồi mới gọi thoat() — thoat() dừng mọi thứ chạy nền rồi mới đóng. */
  'Thoát': () => hoiTruocKhiThoat(() => { if (coPython()) api('thoat'); }),
  'Đóng cài đặt': () => dat({ ...dongHetMenu(S), man: 'chinh' }),
  'Đóng từ điển': () => { dungNgheThu(); dat({ ...dongHetMenu(S), man: 'chinh',
                                               tuDienSua: null }); },
  'Tìm và thay thế': () => dat({ ...dongHetMenu(S), find: !S.find }),
  'Thu gọn danh sách hồ sơ': () => dat({ ...dongHetMenu(S), rail: !S.rail }),
  'Giao diện tối': () => dat({ ...dongHetMenu(S), theme: S.theme === 'toi' ? 'sang' : 'toi' }),
  'Tạm dừng': () => {
    clearInterval(dongHoPhat); dongHoPhat = 0; dungToChu();
    pythonLai = false;
    if (coPython()) api('moi_tam_dung');
    daTamDung = true;                      // giữ pos để bấm Đọc tiếp là chạy tiếp
    dat({ ...S, view: 'san_sang' });
  },
  'Dừng': () => dungPhat(),
  'Đặt lại mặc định': () => {
    let x = S;
    for (const k of ['tocDo', 'caoDo', 'amLuong']) x = datChinh(x, k, k === 'amLuong' ? 100 : 0);
    dat(x);
  },

  /* Chín mục dưới đây trước nay bấm vào chỉ đóng menu rồi thôi — bảng LENH
     không có khoá tương ứng nên `f ? f() : dongHetMenu(S)` rơi vào nhánh sau.
     Người lớn tuổi bấm hai ba lần rồi tưởng máy hỏng. */
  'Lưu': () => luuVanBan(),
  'Đóng tệp': () => {
    const i = S.activeByProfile[S.profile] || 0;
    hoiTruocKhiDongTep(tabDangMo(S)[i], () => chuyenSang(dongTab(S, i)));
  },
  'Thẻ cảm xúc': () => dat({ ...dongHetMenu(S), tags: true }),
  'Đổi giọng đọc': () => LENH['Thư viện giọng'](),
  'Nghe mẫu giọng': () => {
    const g = hoSoDangDung(S).giong;
    dat(dongHetMenu(S));
    if (coPython()) {
      api('nghe_thu_giong', g);
    } else {
      moBao('Cần chạy trong chương trình mới nghe được.');
    }
  },
  'Cỡ chữ lớn hơn': () => doiCoChu(+10),
  'Cỡ chữ nhỏ hơn': () => doiCoChu(-10),
  'Hướng dẫn nhanh': () => moHopTin('Hướng dẫn nhanh', [
    'Mở một tệp văn bản, hoặc dán chữ vào bằng Ctrl+V.',
    'Chọn giọng ở cột bên trái. Bấm Nghe toàn bộ để nghe thử cả bài.',
    'Ba thanh Tốc độ · Cao độ · Âm lượng chỉnh riêng cho từng hồ sơ đọc.',
    'Bấm vào một đoạn để nghe riêng đoạn đó.',
    'Xong thì bấm Xuất file âm thanh để ghi ra tệp WAV hoặc MP3.',
    'Máy đọc chậm hơn thời lượng bài đọc chừng bốn lần, nên bài dài phải chờ.',
  ]),
  'Danh sách phím tắt': () => moHopTin('Danh sách phím tắt',
    MENUS.flatMap(([, ds]) => ds).filter(([, p]) => p)
      .concat([['Nghe toàn bộ / Tạm dừng', 'Space']])),
  'Giới thiệu Giọng Việt': () => moHopTin('Giới thiệu Giọng Việt', [
    'Giọng Việt — chương trình đọc văn bản tiếng Việt thành tiếng nói.',
    'Tiếng nói do mô hình VieNeu-TTS tạo ra, chạy thẳng trên máy này. '
      + 'Không gửi văn bản của bạn đi đâu cả.',
    'Tốc độ, cao độ và âm lượng do ffmpeg xử lý.',
  ]),
};

/* Cỡ chữ VÙNG ĐỌC, không phóng cả giao diện. Kẹp trong 80–200%: dưới 80 thì
   người lớn tuổi không đọc nổi, trên 200 thì một đoạn tràn hết màn hình. */
function doiCoChu(buoc) {
  const moi = Math.max(80, Math.min(200, (S.zoom || 100) + buoc));
  dat({ ...dongHetMenu(S), zoom: moi });
}

function moHopTin(ten, dong) {
  dat({ ...dongHetMenu(S), hopTin: { ten, dong } });
}

/* Hộp hỏi nhiều nút, dùng chung khung hopTin. Hàm gọi lại để NGOÀI state chứ
   không nhét vào S: dat() sao chép state khắp nơi, mang theo hàm là sớm muộn
   cũng có chỗ so sánh state rồi vấp. */
let hopHoiXong = null;
function moHopHoi(ten, dong, nut, xong) {
  hopHoiXong = xong;
  dat({ ...dongHetMenu(S), hopTin: { ten, dong, nut } });
}

/* Chặn mọi đường ĐÓNG khi còn chữ chưa lưu.
   Ctrl+S có lưu thật, nhưng không có gì tự lưu và trước đây không đường đóng
   nào hỏi một câu — gõ cả buổi rồi bấm dấu × là mất trắng. */
function hoiTruocKhiDongTep(ten, tiep) {
  /* KHÔNG được bỏ qua khi tên rỗng. Tệp chưa đặt tên chính là bản VỪA DÁN —
     mà bản dán không có tệp nào trên đĩa, nên đóng đi là mất hẳn, không đường
     nào lấy lại. Trước đây nhánh `!ten` cho nó trôi thẳng qua hộp hỏi: dán bài,
     sửa vài chữ, bấm × là mất trắng không một câu hỏi. Đo được bằng
     kiem-giao-dien.mjs mục N2.

     Chỉ `chuaLuu.has(ten)` mới được quyền quyết định, vì đó mới là câu hỏi thật:
     tệp này có chữ chưa ghi ra không. */
  if (!chuaLuu.has(ten)) { tiep(); return; }
  // Tên rỗng không hiện ra được cho người dùng đọc — gọi đúng nhãn họ đang thấy
  // trên hàng tệp.
  const nhan = ten || tenHienThi(tabDangMo(S), S.activeByProfile[S.profile]);
  moHopHoi('Chưa lưu', [
    `Tệp “${nhan}” có chữ bạn vừa sửa mà chưa lưu.`,
    'Lưu thì phần mềm ghi ra một bản trong Tài liệu\\GiongViet — tệp gốc của bạn không bị đè.',
  ], [
    { ma: 'luu', nhan: 'Lưu rồi đóng', chinh: true },
    { ma: 'bo', nhan: 'Đóng không lưu' },
    { ma: 'huy', nhan: 'Quay lại' },
  ], async (ma) => {
    if (ma === 'huy') return;
    /* Lưu HỎNG thì ĐỪNG đóng. Bỏ chốt này là gặp đúng cái nó sinh ra để chặn:
       người dùng bấm "Lưu rồi đóng", lưu thất bại, tệp vẫn đóng, bài mất sạch —
       mà lần này còn tệ hơn vì họ tưởng đã lưu rồi. */
    if (ma === 'luu' && !(await luuVanBan())) return;
    chuaLuu.delete(ten);
    tiep();
  });
}

/* Đóng cả cửa sổ: có thể NHIỀU tệp đang dở, mà Lưu ở đây chỉ lưu được tệp đang
   xem. Nên không bày nút Lưu để khỏi hứa suông — chỉ nói rõ tệp nào đang dở. */
function hoiTruocKhiThoat(tiep) {
  if (!coSuaChuaLuu()) { tiep(); return; }
  const ds = Array.from(chuaLuu);
  moHopHoi('Còn chữ chưa lưu', [
    ds.length === 1
      ? `Tệp “${ds[0]}” có chữ bạn vừa sửa mà chưa lưu.`
      : `${ds.length} tệp đang có chữ chưa lưu: ${ds.join(' · ')}.`,
    'Quay lại rồi bấm Ctrl+S ở từng tệp nếu bạn muốn giữ.',
  ], [
    { ma: 'huy', nhan: 'Quay lại', chinh: true },
    { ma: 'bo', nhan: 'Thoát không lưu' },
  ], (ma) => { if (ma === 'bo') tiep(); });
}

/* Ctrl+S ghi ra TỆP MỚI đánh số kiểu Explorer, không đè bản gốc — quyết định
   của chủ dự án 12/8. Văn bản ở bản này chỉ đổi được qua Tìm và thay thế,
   nhưng đúng vì thế mà Lưu càng cần: thay xong mà không ghi được ra đâu thì
   công thay thế mất trắng lúc đóng chương trình. */
async function luuVanBan() {
  const doan = doanDangXem(S, TAI_LIEU);
  dat(dongHetMenu(S));
  if (!doan.length) { moBao('Chưa có văn bản nào để lưu.'); return false; }
  if (!coPython()) { moBao('Cần chạy trong chương trình mới lưu được.'); return false; }

  const kq = await api('moi_luu_van_ban', tenTepDangXem(S) || 'vanban.txt',
                       doan.map((d) => d.chu).join('\n'));
  if (kq && kq.ten) {
    chuaLuu.delete(tenTepDangXem(S));
    gioLuuCuoi = new Date().toTimeString().slice(0, 5);
    ve();                       // thanh trạng thái đổi từ "Chưa lưu" sang giờ lưu
  }
  moBao(kq && kq.ten ? `Đã lưu “${kq.ten}”.` : 'Chưa lưu được tệp.');
  return !!(kq && kq.ten);
}

document.addEventListener('click', (e) => {
  const t = (s) => e.target.closest(s);
  let n;

  /* Nút trên dải LỖI THẬT. Mã việc do Python gửi kèm, và bên ấy đã có sẵn
     xu_ly_loi(act) từ bản cũ: thuLaiMoHinh nạp lại bộ giọng, docTiep đọc tiếp
     từ chỗ hỏng. Không viết lại, chỉ gọi. Mã rỗng = chỉ dọn dải đi. */
  if ((n = t('[data-loithat]'))) {
    const act = n.dataset.loithat;
    dat({ ...S, loiThat: null });
    if (act && coPython()) api('xu_ly_loi', act);
    return;
  }
  if ((n = t('[data-canhbao]'))) { const f = LENH_CANH_BAO[n.dataset.canhbao];
                                   return f ? f() : undefined; }
  if ((n = t('[data-menu]')))   return dat(moMenu(S, +n.dataset.menu));
  if ((n = t('[data-lenh]')))   { const f = LENH[n.dataset.lenh];
                                  return f ? f() : dat(dongHetMenu(S)); }
  /* Ba nhánh cây tệp hỏi TRƯỚC [data-hoso]. Hàng tệp nằm ngoài thẻ .hoso nên
     closest() không trúng nó, nhưng để trước thì thứ tự đọc khớp thứ tự nhìn
     thấy trên màn hình, và thêm hàng vào trong hồ sơ sau này cũng không gãy. */
  if (t('#themTep'))            { suaTenTep = null; return chuyenSang(themTab(S)); }
  if ((n = t('[data-dongtep]'))) { e.stopPropagation();
                                   const i = +n.dataset.dongtep;
                                   suaTenTep = null;
                                   return hoiTruocKhiDongTep(tabDangMo(S)[i],
                                            () => chuyenSang(dongTab(S, i))); }
  if (t('.tep__o'))             return;          // đang gõ tên, đừng cướp cú bấm
  if ((n = t('[data-tep]')))    { const i = +n.dataset.tep;
                                  if (suaTenTep) { suaTenTep = null; ve(); }
                                  if (i === S.activeByProfile[S.profile]) return;
                                  return chuyenSang(doiTab(S, i)); }
  if ((n = t('[data-hoso]')))   { suaTenTep = null;
                                  return chuyenSang(doiHoSo(S, +n.dataset.hoso)); }
  /* Bấm vào chính chữ đang sửa được thì để yên cho con trỏ đứng đó - dat() ở
     dưới sẽ vẽ lại vùng đọc và ném con trỏ về đầu bài. */
  if (t('.doan__chu[contenteditable]')) {
    const o = t('[data-doan]');
    if (o && +o.dataset.doan !== S.sel) S = { ...S, sel: +o.dataset.doan };
    return;
  }
  /* Bấm thẻ cảm xúc = gỡ thẻ. Đoạn giữ nguyên, KHÔNG nối lên trên. */
  if ((n = t('[data-gothe]'))) {
    e.stopPropagation();
    const so = +n.dataset.gothe;
    const tep = tenTepDangXem(S);
    const cua = { ...(S.chips[tep] || {}) };
    delete cua[so];
    return dat({ ...S, chips: { ...S.chips, [tep]: cua } });
  }
  if ((n = t('[data-nghe]'))) {
    e.stopPropagation();
    /* Đang đọc chính đoạn này thì nút ấy là nút DỪNG - CSS đã đổi nó thành ■.
       Kiểm ở đây chứ không gắn thuộc tính riêng vào HTML: nhịp đọc chuyển đoạn
       bằng cách gạt lớp, không dựng lại DOM, nên thuộc tính viết sẵn sẽ ôi. */
    const soDoan = +n.dataset.nghe;
    /* Theo chuẩn trình phát: đang phát thì nút là TẠM DỪNG, tạm dừng rồi thì
       bấm tiếp là đọc tiếp - không phải dừng hẳn rồi đọc lại từ đầu. Bản mẫu
       chưa nói tới trạng thái này, lấy lệ thường. */
    if (S.view === 'dang_doc' && soDoan === S.pos) return LENH['Tạm dừng']();
    if (daTamDung && soDoan === S.pos) {
      dat({ ...S, view: 'dang_doc' });
      return batDauPhat(true);
    }
    /* Lớp chặn TRONG: lớp ngoài là nút mờ đi, nhưng nút Nghe toàn bộ khoá được
       mà đường này lọt là giao diện chạy màn "đang đọc" không có tiếng. */
    const viKhoa = lyDoKhoa(S);
    if (viKhoa) return moBao(viKhoa, 'Chưa nghe được');
    dat(ngheRiengDoan(S, soDoan));
    return batDauPhat();
  }
  if ((n = t('[data-doan]')))   return dat(chonDoan(S, +n.dataset.doan));
  if (t('#nutXuat'))            return moHopXuat();
  if (t('#bDong'))              return dat({ ...S, toast: false });
  if (t('#bMoThuMuc'))          { if (coPython()) api('mo_thu_muc', hopXuat && hopXuat.thuMuc);
                                  return dat({ ...S, toast: false }); }
  if (t('#nutNghe')) {
    if (S.view === 'dang_doc') return LENH['Tạm dừng']();
    if (daTamDung) { dat({ ...S, view: 'dang_doc' }); return batDauPhat(true); }
    dat(ngheToanBo(S)); return batDauPhat();
  }
  if (t('#nutTim'))             return dat({ ...dongHetMenu(S), find: !S.find });
  if (t('#dongTim'))            return dat({ ...S, find: false });
  if (t('#timTruoc'))           return toiKetQua(-1);
  if (t('#timSau'))             return toiKetQua(1);
  if (t('#nutThay') || t('#nutThayTatCa')) {
    const q = $('#oTim') ? $('#oTim').value : '';
    const v = $('#oThay') ? $('#oThay').value : '';
    const n = thayThe(q, v, !!t('#nutThayTatCa'));
    if (!n) moBao('Không tìm thấy chỗ nào để thay.');
    return;
  }
  if (t('#thuGon'))             return dat({ ...S, rail: !S.rail });
  if (t('#nutThe'))             return dat({ ...dongHetMenu(S), tags: !S.tags });
  if ((n = t('[data-the]')))    return dat(datThe(S, n.dataset.the));
  if (t('#oGiong')) {
    // Đóng ô chọn giọng thì tắt luôn tiếng đang thử: nút dừng nằm trong ô, ô
    // đóng rồi thì người dùng không còn chỗ nào bấm cho nó im.
    if (S.voiceOpen) dungNgheThu();
    return dat({ ...S, voiceOpen: !S.voiceOpen, menu: -1 });
  }
  if ((n = t('[data-nghegiong]'))) {
    e.stopPropagation();                       // đừng chọn giọng, chỉ nghe thử
    const ma = n.dataset.nghegiong;
    if (S.dangNgheThu === ma) return dungNgheThu();   // bấm lần nữa = dừng
    if (coPython()) api('nghe_thu_giong', ma);
    return dat({ ...S, dangNgheThu: ma });
  }
  if ((n = t('[data-cdtheme]')))  return dat({ ...S, theme: n.dataset.cdtheme });
  if ((n = t('[data-cdzoom]')))   return dat({ ...S, zoom: +n.dataset.cdzoom });
  if ((n = t('[data-cdcongtac]'))) return datCaiDat(n.dataset.cdcongtac,
                                                    n.dataset.cdbat === '1');
  if (t('[data-cdthumuc]'))     return doiThuMucXuat();
  if (t('[data-tudienmoi]'))    return dat({ ...S, tuDienSua: { tuCu: '', tu: '', doc: '' } });
  if (t('[data-tudienhuy]'))    return dat({ ...S, tuDienSua: null });
  if (t('[data-tudiennghe]'))   return ngheThuCachDoc();
  if (t('[data-tudienluu]')) {
    const tu = $('#oTuMoi') ? $('#oTuMoi').value.trim() : '';
    const doc = $('#oDocMoi') ? $('#oDocMoi').value.trim() : '';
    if (!tu || !doc) { moBao('Cần điền cả chữ và cách đọc.'); return; }
    const cu = (S.tuDienSua || {}).tuCu || '';
    return suaTuDien(cu ? 'sua' : 'them', tu, doc, cu);
  }
  if ((n = t('[data-tudiensua]'))) {
    return dat({ ...S, tuDienSua: { tuCu: n.dataset.tudiensua,
                                    tu: n.dataset.tudiensua,
                                    doc: n.dataset.tudiendoc || '' } });
  }
  if ((n = t('[data-tudienxoa]'))) {
    // Xoá là việc không lấy lại được, mà người dùng đích là người lớn tuổi —
    // hỏi lại một câu rõ ràng trước khi xoá.
    const tu = n.dataset.tudienxoa;
    if (!window.confirm(`Xoá “${tu}” khỏi từ điển phát âm?\n\n`
                        + 'Máy sẽ quay lại đọc chữ này theo cách mặc định.')) return;
    return suaTuDien('xoa', tu);
  }
  if (t('[data-nhanbangiong]')) return nhanBanGiong();
  if ((n = t('[data-xoagiong]'))) { e.stopPropagation();
                                    return xoaGiongRieng(n.dataset.xoagiong,
                                                         n.dataset.xoaten); }
  if ((n = t('[data-giongloc]')))  return dat({ ...S, giongLoc: n.dataset.giongloc });
  if ((n = t('[data-gionggioi]'))) return dat({ ...S, giongGioi: n.dataset.gionggioi });
  if ((n = t('[data-giong]')))  {
    // Thẻ trong Thư viện giọng cũng dùng data-giong: chọn xong phải dời nhãn
    // "Đang dùng" sang thẻ mới, không thì hai thẻ cùng sáng.
    if (duLieuGiong) {
      for (const nhom of ['cuaToi', 'coSan']) {
        (duLieuGiong[nhom] || []).forEach((g) => { g.dangDung = g.id === n.dataset.giong; });
      }
    }
    dat(datGiong(S, n.dataset.giong));
    // doi_giong của Api cũ chỉ còn đổi cfg trong bộ nhớ; đường ghi ra
    // cauhinh.ini và hoso.json đã bị khoa_du_lieu.py bịt lại.
    dongBoGiongSangPython();
    return;
  }
  if (t('#moChinh'))            return dat({ ...S, tune: !S.tune });
  if ((n = t('[data-soattab]')))  return dat({ ...S, soatTab: n.dataset.soattab });
  if ((n = t('[data-soatloc]')))  return dat({ ...S, soatLoc: n.dataset.soatloc });
  /* Bỏ qua một chỗ, hoặc bỏ qua sạch những chỗ CÒN LẠI. "Còn lại" chứ không
     phải toàn bộ: bấm Bỏ qua tất cả rồi Hoàn lại thì phải về đúng chỗ cũ. */
  if ((n = t('[data-soatboqua]'))) {
    e.stopPropagation();
    const khoa = n.dataset.soatboqua;
    const moi = { ...(S.soatBoQua || {}) };
    if (khoa === 'tatca') {
      (((duLieuSoat || {}).chuY || {}).vanDe || []).forEach((v) => { moi[khoaVanDe(v)] = true; });
    } else {
      moi[khoa] = true;
    }
    return dat({ ...S, soatBoQua: moi });
  }
  if (t('[data-soathoanlai]')) { e.stopPropagation(); return dat({ ...S, soatBoQua: {} }); }
  if ((n = t('[data-quytac]')))   return datQuyTacSoat(n.dataset.quytac,
                                                       n.dataset.quytacbat === '1');
  if ((n = t('[data-soatthem]'))) { e.stopPropagation();
                                    return themVaoTuDien(n.dataset.soatthem); }
  if ((n = t('[data-soatdi]')))   { e.stopPropagation();
                                    // Tới đoạn: đóng màn soát rồi chọn đoạn đó,
                                    // để người dùng thấy ngay chỗ cần sửa.
                                    return dat({ ...chonDoan(S, +n.dataset.soatdi),
                                                 man: 'chinh' }); }
  if ((n = t('[data-soatdoan]'))) return dat(chonDoan(S, +n.dataset.soatdoan));
  if ((n = t('[data-cuaso]'))) {
    const viec = n.dataset.cuaso;
    if (viec === 'dong') {
      // thoat() dừng mọi thứ đang chạy nền rồi mới đóng cửa sổ. Đừng gọi
      // window.close(): WebView2 đóng khung mà tiến trình Python còn sống.
      hoiTruocKhiThoat(() => { if (coPython()) api('thoat'); });
      return;
    }
    if (coPython()) {
      api('cua_so', viec).then(() => {
        // Chờ Windows đổi cỡ xong rồi mới hỏi lại, không thì đo trúng lúc
        // cửa sổ còn đang dịch chuyển và nút hiện sai một nhịp.
        if (viec === 'phong_to') setTimeout(capNhatNutCuaSo, 260);
      });
    }
    return;
  }
  if (t('#ngheMau')) {
    // Nút loa = nghe thử CHÍNH giọng đang dùng. Trước đây nó chỉ hiện dòng
    // chữ giả trong 2,5 giây rồi tắt, không hề gọi sang Python — bấm mãi
    // không ra tiếng.
    const ma = hoSoDangDung(S).giong;
    if (S.dangNgheThu === ma) return dungNgheThu();
    if (coPython()) api('nghe_thu_giong', ma);
    return dat({ ...S, dangNgheThu: ma, mauDangPhat: true });
  }
  if ((n = t('[data-chuy]')))   {
    const c = chuYDangXem(S, TAI_LIEU);
    return dat(chonDoan(S, c.loai[+n.dataset.chuy].doan[0]));
  }
  if ((n = t('[data-truot]')))  {
    const r = n.getBoundingClientRect();
    const [, , min, max] = TRUOT.find((x) => x[0] === n.dataset.truot);
    const ty = Math.max(0, Math.min(1, (e.clientX - r.left) / r.width));
    return dat(datChinh(S, n.dataset.truot, Math.round(min + ty * (max - min))));
  }
  /* Bấm ra ngoài thì đóng hết menu — NHƯNG phải chừa hộp thoại và mọi ô nhập.
     dat() dựng lại toàn bộ HTML, nên bấm vào <select> là nó bị thay bằng một
     thẻ mới ngay lúc trình duyệt sắp bung danh sách xuống: ô "Định dạng" bấm
     mãi không mở được. Cùng họ với cái bẫy đã ghi trong CLAUDE.md — sự kiện
     nổi lên document rồi đóng ngay thứ vừa mở. */
  if (!t('.menu, .roi, .hop, .bao, select, input, textarea, button')) {
    dat(dongHetMenu(S));
  }
});

/* Đổi NHÃN của một hàng tệp — chép đúng setNameAt của bản mẫu.

   Chỉ ghi vào bảng nhãn, TUYỆT ĐỐI không đụng mảng tệp và không dời khoá nào.
   Tên tệp vẫn là khoá của TAI_LIEU · S.duongDanTep · S.loaiTep · S.chips ·
   chuaLuu, nên hễ mổ vào nó là mất bài — đã đo được ba đường: xoá trắng ô xoá
   luôn nội dung, đặt tên cho tệp chưa đặt tên làm bài kẹt dưới khoá rỗng, đặt
   trùng tên tệp của hồ sơ khác thì nuốt bài của hồ sơ ấy. Bảng nhãn riêng làm
   cả ba đường ấy biến mất cùng lúc, vì không còn lệnh delete nào.

   Để trống thì trả về null, tức quay lại tên tệp thật hoặc nhãn tự sinh — đúng
   `String(name || '').trim() || null` của bản mẫu, và ngược với ô tên HỒ SƠ
   (bỏ trống thì giữ tên cũ). Hai chỗ cố ý khác nhau.

   Trùng nhãn KHÔNG cần chặn nữa: hai hàng cùng nhãn vẫn là hai tệp riêng, vì
   nội dung tra theo tên tệp chứ không theo nhãn. */
function doiTenTep(j, tenGo) {
  suaTenTep = null;
  const rieng = ((S.nhanTep || {})[S.profile] || []).slice();
  while (rieng.length <= j) rieng.push(null);
  rieng[j] = String(tenGo || '').trim() || null;
  dat({ ...S, nhanTep: { ...(S.nhanTep || {}), [S.profile]: rieng } });
}

function moODoiTenTep(e) {
  const h = e.target.closest('[data-tep]');
  if (!h) return false;
  e.preventDefault();
  suaTenTep = `${S.profile}:${+h.dataset.tep}`;
  ve();
  const o = $('#oTenTep');
  if (o) { o.focus(); o.select(); }
  return true;
}

/* Rời ô cũng lưu, đúng như bản mẫu: người lớn tuổi hay gõ xong rồi bấm ra chỗ
   khác chứ không nhấn Enter, mất chữ vừa gõ là mất niềm tin. */
function chotTenTepNeuDangGo(e) {
  const o = e.target.closest && e.target.closest('.tep__o');
  if (o && suaTenTep) doiTenTep(+o.dataset.suatep, o.value);
}

/* Gõ trong ô Tìm thì chạy tìm ngay, không phải bấm nút. Nhớ chữ vào S để lần
   vẽ lại không xoá mất thứ người dùng đang gõ. */
/* Chạm vào dải mép = bắt đầu kéo đổi cỡ. Phải bắt ở `mousedown` chứ không
   phải `click`: kéo là một thao tác giữ chuột, đợi tới lúc click là đã muộn. */
document.addEventListener('mousedown', (e) => {
  const v = e.target.closest('[data-vien]');
  if (!v || e.button !== 0) return;
  e.preventDefault();
  if (!coPython()) return;
  api('moi_keo_vien', v.dataset.vien);
  // Kéo xong cửa sổ có thể vừa lấp kín hoặc vừa rời khỏi trạng thái đó, mà
  // JS không nhận được sự kiện nào — hỏi lại sau khi người dùng buông chuột.
  window.addEventListener('mouseup',
                          () => setTimeout(capNhatNutCuaSo, 200), { once: true });
});

/* Nháy đúp thanh tiêu đề = phóng to / thu về, y như mọi cửa sổ Windows khác.
   Người lớn tuổi làm theo thói quen cả đời chứ không đi tìm nút; thiếu cái này
   là họ nháy đúp mấy lần rồi tưởng chương trình đơ. */
document.addEventListener('dblclick', (e) => {
  // Nháy đúp hàng tệp = đổi tên. Gộp vào cùng một chỗ bắt thay vì đăng ký thêm
  // một listener nữa: cả tệp này chỉ có MỘT chỗ bắt cho mỗi loại sự kiện, và
  // hai listener cùng loại thì thứ tự chạy thành thứ ngầm không ai thấy.
  if (moODoiTenTep(e)) return;
  const thanh = e.target.closest('.tieude');
  // Trừ ba nút cửa sổ: nháy đúp trúng nút Đóng mà lại phóng to thì vô lý.
  if (!thanh || e.target.closest('.cuaso')) return;
  if (!coPython()) return;
  api('cua_so', 'phong_to').then(() => setTimeout(capNhatNutCuaSo, 260));
});

document.addEventListener('input', (e) => {
  if (e.target.id === 'oTim') {
    S.chuTim = e.target.value;
    chayTim(S.chuTim);
    const d = $('#timDem');
    if (d) d.textContent = ketQuaTim.length ? `1/${ketQuaTim.length}` : '0/0';
    if (ketQuaTim.length) { timThu = -1; toiKetQua(1); }
  }
  if (e.target.id === 'oThay') S.chuThay = e.target.value;
  if (e.target.id === 'oTimTuDien') {
    S.tuDienTim = e.target.value;
    timTuDien(e.target.value);
  }
  if (e.target.id === 'oTuMoi' || e.target.id === 'oDocMoi') {
    // Giữ chữ đang gõ vào S nhưng KHÔNG vẽ lại: vẽ lại là ô input thành node
    // mới, mất tiêu điểm và người dùng gõ được đúng một chữ.
    S.tuDienSua = { ...(S.tuDienSua || {}),
                    [e.target.id === 'oTuMoi' ? 'tu' : 'doc']: e.target.value };
  }
  if (e.target.id === 'oTimGiong') {
    /* Vẽ lại rồi trả con trỏ về ô tìm: ve() dựng lại cả khối HTML nên ô input
       là node mới, không giữ được tiêu điểm lẫn vị trí con trỏ. Không trả lại
       thì gõ được đúng một chữ rồi mất tiêu điểm. */
    const vt = e.target.selectionStart;
    dat({ ...S, giongTim: e.target.value });
    const o = $('#oTimGiong');
    if (o) { o.focus(); o.setSelectionRange(vt, vt); }
  }
});

/* Gõ vào chữ thì chép ngay sang tài liệu, KHÔNG vẽ lại - vẽ lại là con trỏ
   nhảy về đầu bài, gõ được đúng một chữ rồi mất chỗ. Việc tách hay bỏ đoạn
   đợi tới lúc rời khỏi đoạn (focusout) mới làm, lúc ấy vẽ lại mới an toàn. */
const _nutChu = (e) => {
  const el = e.target && (e.target.nodeType === 1 ? e.target : e.target.parentElement);
  return el && el.closest ? el.closest('.doan__chu[contenteditable]') : null;
};
document.addEventListener('input', (e) => {
  const nut = _nutChu(e);
  if (nut) chuDangGo(nut);
});
document.addEventListener('focusout', (e) => {
  chotTenTepNeuDangGo(e);
  const nut = _nutChu(e);
  if (nut) roiDoanDangGo(nut);
});

document.addEventListener('keydown', (e) => {
  /* isContentEditable PHẢI có ở đây. Vùng chữ gõ thẳng không phải INPUT cũng
     không phải TEXTAREA, thiếu nó là phím tắt toàn cục nuốt mất phím Space -
     gõ văn bản mà không đánh được dấu cách. */
  const dangGoChu = !!(document.activeElement && document.activeElement.isContentEditable);
  if (dangGoChu || ['INPUT', 'TEXTAREA'].includes(document.activeElement.tagName)) {
    /* Ctrl+S phải ăn NGAY GIỮA LÚC gõ - sửa xong là muốn lưu liền. Bắt bấm ra
       ngoài rồi mới lưu được là thừa một bước không ai đoán ra.

       blur() trước đã: rời ô mới kích focusout, mà focusout mới là chỗ chép
       chữ vừa gõ sang tài liệu. Lưu trước khi chép là ghi ra bản thiếu đúng
       những chữ vừa gõ. */
    if ((e.ctrlKey || e.metaKey) && e.key.toLowerCase() === 's') {
      e.preventDefault();
      if (document.activeElement.blur) document.activeElement.blur();
      return LENH['Lưu']();
    }
    /* Ô đổi tên tệp: Enter chốt, Escape bỏ. Phải chặn ở đây chứ không để rơi
       xuống nhánh phím tắt chung - Escape ở dưới đóng menu rồi vẽ lại, ô nhập
       biến mất mà tên vẫn nguyên, trông y như máy treo. */
    if (document.activeElement.classList
        && document.activeElement.classList.contains('tep__o')) {
      const o = document.activeElement;
      if (e.key === 'Enter')  { e.preventDefault(); return doiTenTep(+o.dataset.suatep, o.value); }
      if (e.key === 'Escape') { e.preventDefault(); suaTenTep = null; return ve(); }
      return;
    }
    if (dangGoChu) {
      /* Ctrl+A phải bôi đen CẢ BÀI như Notepad. Để mặc thì nó chỉ bôi trong
         một đoạn, vì mỗi đoạn là một vùng gõ riêng. */
      if ((e.ctrlKey || e.metaKey) && e.key.toLowerCase() === 'a') {
        e.preventDefault();
        const cuon = $('#cuon');
        const sel = window.getSelection && window.getSelection();
        if (cuon && sel) {
          const r = document.createRange();
          r.selectNodeContents(cuon);
          sel.removeAllRanges();
          sel.addRange(r);
        }
        return;
      }
      /* Xoá khi vùng bôi đen trải nhiều đoạn: trình duyệt chỉ xoá được phần
         nằm trong đoạn có con trỏ, các đoạn còn lại trơ ra. Tự gom mà xoá. */
      if (e.key === 'Delete' || e.key === 'Backspace') {
        const ds = doanTrongVungChon();
        if (ds.length > 1) { e.preventDefault(); return xoaCacDoan(ds); }
      }

      /* Bốn thao tác làm cả bài cư xử như MỘT tài liệu chứ không phải nhiều ô
         rời: Backspace đầu đoạn gộp lên, Delete cuối đoạn kéo đoạn dưới lên,
         mũi tên lên/xuống ở đầu/cuối đoạn thì sang đoạn kề.

         Chỉ xử lý khi con trỏ ĐỨNG MỘT CHỖ và nằm đúng mép: giữa đoạn thì để
         trình duyệt lo, không giành việc của nó. */
      const oChu = document.activeElement;
      const sel = window.getSelection && window.getSelection();
      if (oChu && oChu.classList && oChu.classList.contains('doan__chu')
          && sel && sel.isCollapsed) {
        const oDoan = oChu.closest('[data-doan]');
        const n = oDoan ? +oDoan.dataset.doan : 0;
        const vt = viTriCaret(oChu);
        const het = oChu.textContent.length;

        /* Enter tách đoạn NGAY tại con trỏ. Không chặn ở đây thì trình duyệt
           chèn một dấu xuống dòng vào giữa đoạn, và mãi tới lúc rời đoạn mới
           tách - người dùng bấm Enter xong không thấy gì xảy ra. */
        if (n && e.key === 'Enter' && !e.shiftKey && !e.ctrlKey && !e.metaKey) {
          const chu = oChu.textContent;
          if (tachDoanTaiCho(n, chu.slice(0, vt), chu.slice(vt))) {
            e.preventDefault();
            return;
          }
        }
        if (n && e.key === 'Backspace' && vt === 0) {
          if (gopLenDoanTren(n)) { e.preventDefault(); return; }
        }
        if (n && e.key === 'Delete' && vt === het) {
          // Kéo đoạn dưới lên = gộp đoạn dưới vào đoạn này.
          const duoi = doanGoDuoc(n, 1);
          const oDuoi = duoi && duoi.closest('[data-doan]');
          if (oDuoi && gopLenDoanTren(+oDuoi.dataset.doan)) { e.preventDefault(); return; }
        }
        if (n && e.key === 'ArrowUp' && vt === 0) {
          const tren = doanGoDuoc(n, -1);
          if (tren && datCaret(tren, tren.textContent.length)) { e.preventDefault(); return; }
        }
        if (n && e.key === 'ArrowDown' && vt === het) {
          const duoi = doanGoDuoc(n, 1);
          if (duoi && datCaret(duoi, 0)) { e.preventDefault(); return; }
        }
      }
    }
    if (e.key === 'Escape') dat({ ...S, find: false });
    if (e.key === 'Enter' && document.activeElement.id === 'oTim') {
      e.preventDefault(); toiKetQua(e.shiftKey ? -1 : 1);
    }
    return;
  }
  /* Enter trên hàng tệp đang được bàn phím chọn = mở tệp ấy. Space CỐ Ý không
     nhận: Space là phím Nghe/Dừng toàn cục, cướp nó ở đây là người dùng đứng
     trong cột trái bấm Space rồi không hiểu vì sao loa không chạy. */
  if (e.key === 'Enter' && document.activeElement
      && document.activeElement.dataset
      && document.activeElement.dataset.tep !== undefined) {
    e.preventDefault();
    const i = +document.activeElement.dataset.tep;
    if (i === S.activeByProfile[S.profile]) return;
    return chuyenSang(doiTab(S, i));
  }
  if (e.ctrlKey && e.key.toLowerCase() === 'v') { e.preventDefault(); return danVanBan(); }
  if (e.ctrlKey && e.key.toLowerCase() === 'o') { e.preventDefault(); return moTep(); }
  if (e.ctrlKey && e.key.toLowerCase() === 'e') {
    e.preventDefault(); return moHopXuat();
  }
  const c = e.ctrlKey || e.metaKey;
  const k = e.key.toLowerCase();
  if (e.key === 'Escape') return dat(dongHetMenu(S));
  if (c && k === 'h') { e.preventDefault(); return dat({ ...S, find: !S.find }); }
  if (c && k === 'b') { e.preventDefault(); return dat({ ...S, rail: !S.rail }); }
  /* Bốn phím này VỐN ĐÃ ghi trong menu mà chưa có ai nối: bấm Ctrl+S theo đúng
     chữ menu bày ra mà không có gì xảy ra thì cũng là một dạng hứa suông. */
  if (c && k === 's') { e.preventDefault(); return LENH['Lưu'](); }
  if (c && k === 'w') { e.preventDefault(); return LENH['Đóng tệp'](); }
  if (c && k === 'g') { e.preventDefault(); return LENH['Đổi giọng đọc'](); }
  if (c && k === 'm') { e.preventDefault(); return LENH['Nghe mẫu giọng'](); }
  /* NĂM phím nữa cùng một họ với bốn phím trên: menu tự bày chúng ra mà không
     nhánh nào bắt, bấm không có gì xảy ra — đúng thứ KPI "không bày nút giả"
     cấm. Bốn cái đầu đã in sẵn trong MENUS; Ctrl+. thì bản thiết kế đòi qua
     tooltip nút dừng ("Dừng (Ctrl+.)") và README mục Phím tắt.
     Nhận cả '+' vì bàn phím có Shift trả '+' chứ không trả '='. */
  if (c && (e.key === '=' || e.key === '+')) { e.preventDefault(); return LENH['Cỡ chữ lớn hơn'](); }
  if (c && e.key === '-') { e.preventDefault(); return LENH['Cỡ chữ nhỏ hơn'](); }
  if (c && e.key === '/') { e.preventDefault(); return LENH['Danh sách phím tắt'](); }
  if (c && e.key === '.') { e.preventDefault(); return LENH['Dừng'](); }
  if (c && k === 'k')     { e.preventDefault(); return LENH['Soát văn bản'](); }
  if (e.key === 'F1')     { e.preventDefault(); return LENH['Hướng dẫn nhanh'](); }
  if (e.altKey && ['1', '2', '3'].includes(e.key)) {
    e.preventDefault(); return dat(datThe(S, THE_CAM_XUC[+e.key - 1][0]));
  }
  if (e.key === ' ') {
    e.preventDefault();
    if (S.view === 'dang_doc') return LENH['Tạm dừng']();
    if (!hienNgheVaXuat(S, TAI_LIEU)) return;
    /* Nút Nghe toàn bộ mờ đi khi khoá, nhưng phím Space thì không ai làm mờ
       được - phải tự hỏi lại, không thì bấm Space lúc giọng đang tải là màn
       "đang đọc" chạy suông. */
    const viKhoa = lyDoKhoa(S);
    if (viKhoa) return moBao(viKhoa, 'Chưa nghe được');
    if (daTamDung) { dat({ ...S, view: 'dang_doc' }); return batDauPhat(true); }
    dat(ngheToanBo(S)); batDauPhat();
  }
});

// ---------------------------------------------------------------- bảng thử

/* Bảng điều khiển để XEM THIẾT KẾ, không phải một phần của sản phẩm. Chỉ hiện
   khi mở kèm ?thu=1 nên bản giao cho người dùng không bao giờ thấy. */
function veBangThu() {
  if (!new URLSearchParams(location.search).has('thu')) return;
  const cu = document.getElementById('bangThu');
  if (cu) cu.remove();
  const d = document.createElement('div');
  d.className = 'bangthu';
  d.id = 'bangThu';
  d.innerHTML = `<h4>Bảng thử — không phải sản phẩm</h4>
    <select class="chon" id="thuTH">${TEN_TINH_HUONG.map(([m, t]) =>
      `<option value="${m}"${S.situation === m ? ' selected' : ''}>${t}</option>`).join('')}</select>
    <button class="nut nut--vien" id="thuTheme">Đổi sáng / tối</button>
    <button class="nut nut--vien" id="thuRong">Tab rỗng / có văn bản</button>
    <div style="margin-top:10px;border-top:1px solid var(--divider);padding-top:8px">
      <div class="c-nho" style="margin-bottom:6px">Chữ so với tiếng:
        <b id="thuTre">${TRE_PHAT_MS} ms</b></div>
      <button class="nut nut--vien" id="thuSom">Chữ chạy SỚM quá → chờ thêm</button>
      <button class="nut nut--vien" id="thuTre2">Chữ chạy TRỄ quá → chờ ít lại</button>
    </div>`;
  document.body.appendChild(d);
  d.querySelector('#thuTH').onchange = (ev) => dat({ ...S, situation: ev.target.value });
  d.querySelector('#thuTheme').onclick = () => LENH['Giao diện tối']();
  const chinhTre = (b) => {
    TRE_PHAT_MS = Math.max(0, Math.min(1500, TRE_PHAT_MS + b));
    localStorage.setItem('gd-tre-phat', String(TRE_PHAT_MS));
    d.querySelector('#thuTre').textContent = TRE_PHAT_MS + ' ms';
  };
  d.querySelector('#thuSom').onclick = () => chinhTre(50);
  d.querySelector('#thuTre2').onclick = () => chinhTre(-50);
  d.querySelector('#thuRong').onclick = () => {
    dungPhat();
    dat(tabDangMo(S).includes('') ? doiTab(dongTab(S, tabDangMo(S).indexOf('')), 0) : themTab(S));
  };
}

// ---------------------------------------------------------------- nhận từ Python

/* Vòng đọc bên Python đẩy sang mỗi khi đổi đoạn hoặc đổi trạng thái.
   `thoiLuong` là số giây THẬT của khối WAV sắp phát — dùng nó làm mốc tô chữ
   thì chữ chạy khớp tiếng, thay vì ước lượng ký tự/11 như lúc mock. */
datNguoiNhan((goi) => {
  /* Gói tin mô hình: { model: { trangThai, tieuDe, ghiChu, phanTram } }.
     Nạp mô hình mất khoảng 40 giây — không báo gì thì người dùng bấm Nghe,
     không thấy tiếng, tưởng hỏng. */
  if (goi.model) {
    moHinh = goi.model;
    if (moHinh.trangThai === 'san_sang') {
      // Lúc này Python vừa nạp xong danh sách giọng đầy đủ, lấy lại bản chuẩn.
      api('moi_danh_sach_giong').then(datGiongThat);
    }
    ve();
    return;
  }
  if (goi.state === 'dang_doc' && goi.doan) {
    /* HAI gói tin khác nhau cho cùng một đoạn, phân biệt bằng `thoiLuong`:

       KHÔNG có thoiLuong — bo_doc.py:153, đẩy TRƯỚC khi tổng hợp. Máy còn đang
         dựng tiếng, mất 5–10 giây. Đây là tình huống "Đang tạo âm thanh":
         vòng xoay ở máng số, thanh phát dạng chờ, đồng hồ ĐỨNG IM.
       CÓ thoiLuong — bo_doc.py:183, đẩy ngay trước khi phát. Từ đây mới chạy
         đồng hồ và tô chữ.

       Trộn hai gói làm một chính là lỗi "chữ chạy trước tiếng": đồng hồ và
       thanh tiến trình chạy suốt quãng tổng hợp, trong khi loa còn im. Đo trên
       video của chủ dự án: đoạn 1 sáng 13 giây cho một câu đọc hết 4 giây. */
    const dangTao = !(goi.thoiLuong > 0);
    const doiDoan = goi.doan !== S.pos;

    S = { ...S, view: 'dang_doc', pos: goi.doan, sel: goi.doan,
          situation: dangTao ? 'dang_tao' : 'binh_thuong' };
    if (doiDoan) { giayDoanNay = 0; posDaVe = -1; }

    if (dangTao) {
      // Dừng đồng hồ lại, chờ tiếng. Vẽ lại cả màn để hiện thanh phát dạng chờ.
      clearInterval(dongHoPhat); dongHoPhat = 0;
      dungToChu(); traLaiChuThuong(nodeDoan[goi.doan - 1]);
      ve();
      return;
    }

    // Tổng hợp xong, tiếng sắp ra: chạy lại đồng hồ và bắt đầu tô chữ.
    if (!dongHoPhat) {
      dongHoPhat = setInterval(() => {
        giayDoanNay += 0.25; giayDaNghe += 0.25; veNhipDoc();
      }, 250);
    }
    ve();
    batDauToChu(nodeDoan[goi.doan - 1], goi.thoiLuong, goi.doan,
                goi.tu, goi.den, goi.trongSo, goi.treMs);
    return;
  }
  if (goi.state === 'san_sang' || goi.state === 'trong') {
    clearInterval(dongHoPhat); dongHoPhat = 0; pythonLai = false;
    dungToChu(); traLaiChuThuong(nodeDoan[posDaVe - 1]);
    daTamDung = false;
    dat({ ...S, view: 'san_sang' });
    return;
  }
  if (goi.state === 'tam_dung') {
    clearInterval(dongHoPhat); dongHoPhat = 0; pythonLai = false;
    dungToChu(); daTamDung = true;
    dat({ ...S, view: 'san_sang' });
    return;
  }
  if (goi.state === 'loi' && goi.loi) {
    /* GIỮ nguyên gói lỗi để dải cảnh báo nói đúng chuyện đã xảy ra.

       Trước đây chỗ này nuốt sạch nội dung gói và chỉ đặt situation
       'mat_ket_noi', nên máy thiếu bộ giọng thì người dùng đọc được câu "Không
       kết nối được máy chủ đọc… Kiểm tra lại mạng" trong một chương trình chạy
       hoàn toàn trên máy, không dùng mạng một giây nào. Còn hướng dẫn cài thật
       — mo_hinh.py _huong_dan_cai(), "bấm đúp tệp CaiDat.bat" — thì nằm sẵn
       trong gói mà không bao giờ hiện ra. */
    dat({ ...S, view: 'san_sang', situation: 'binh_thuong', loiThat: goi.loi });
  }
});

/* Dấu vân của tài liệu ĐÃ gửi sang Python. Đổi tab mà quên gửi lại là loa đọc
   tài liệu cũ trong khi màn hình hiện tài liệu mới — đã xảy ra thật: màn hình
   là "thông báo phun thuốc", loa đọc "thông báo nghỉ lễ", mà số đoạn hai bên
   gần bằng nhau nên thanh phát trông vẫn hợp lý. */
let vanTayDaGui = '';

/** Tab đang xem là danh sách công đức hay văn bản thường? */
const loaiTepDangXem = (s = S) => (s.loaiTep || {})[tenTepDangXem(s)] || 'vanban';

function vanTayTaiLieu() {
  const doan = doanDangXem(S, TAI_LIEU);
  // Kèm loại và tổng số chữ: sửa văn bản bằng Tìm-thay-thế thì tên tệp và số
  // đoạn giữ nguyên mà nội dung đã khác, vẫn phải gửi lại.
  // Kèm cả thẻ cảm xúc: đặt thêm một thẻ thì chữ không đổi một ký tự nào, mà
  // playlist bên Python phải dựng lại thì tiếng mới có cảm xúc ấy.
  return `${tenTepDangXem(S)}|${loaiTepDangXem()}|${doan.length}|`
       + doan.reduce((s, d) => s + d.chu.length, 0)
       + '|' + JSON.stringify(S.chips[tenTepDangXem(S)] || {});
}

/* ------------------------------------------------------------- gõ thẳng vào chữ

   KHÔNG dựng lại DOM trong lúc người dùng đang gõ. dat() gọi ve() vẽ lại cả
   vùng đọc, mà vẽ lại là con trỏ nhảy về đầu bài - gõ được đúng một chữ rồi
   mất chỗ. Nên đường này chỉ chép chữ vào TAI_LIEU, còn vẽ lại thì đợi tới
   lúc rời đoạn. */
function chuDangGo(nut) {
  const n = +((nut.closest('[data-doan]') || {}).dataset || {}).doan;
  const ten = tenTepDangXem(S);
  const t = TAI_LIEU[ten];
  if (!n || !t || !t.doan[n - 1]) return;
  t.doan[n - 1] = { ...t.doan[n - 1], chu: nut.textContent };
  danhDauSua();
  henLuuHoSo();
}

/* Rời đoạn mới xét tách - gõ Enter giữa câu là muốn xuống dòng chứ chưa chắc
   đã muốn cắt đoạn ngay lúc ấy, mà cắt ngay thì DOM dựng lại và mất con trỏ. */
function roiDoanDangGo(nut) {
  /* BỎ QUA nếu ô này đã bị gỡ khỏi màn hình.

     Tách hay gộp đoạn đều gọi dat() để vẽ lại vùng đọc, và vẽ lại là mọi ô cũ
     bị thay. Trình duyệt bắn focusout TRÊN Ô ĐÃ CHẾT ấy sau khi việc tách đã
     xong, mang theo `textContent` là nguyên câu CHƯA cắt - chép nó vào tài
     liệu là ghi đè đúng kết quả vừa tách.

     Triệu chứng chủ dự án gặp: bấm Enter thấy tách, bấm ra chỗ khác thì đâu
     lại vào đấy, và văn bản đầy những đoạn giống hệt nhau. */
  if (nut.isConnected === false) return;
  const n = +((nut.closest('[data-doan]') || {}).dataset || {}).doan;
  if (n) luuSuaDoan(n, nut.textContent);
}

/* ---- đi lại và gộp đoạn: cho cả bài cư xử như MỘT tài liệu ------------------

   Mỗi đoạn là một vùng gõ riêng, nên trình duyệt không tự đưa con trỏ sang
   đoạn kề, cũng không tự gộp khi bấm Backspace ở đầu đoạn. Thiếu mấy thứ này
   thì gõ vẫn thấy rời rạc dù xoá và tách đã chạy. */

/** Con trỏ đang ở ký tự thứ mấy trong đoạn. */
function viTriCaret(el) {
  const sel = window.getSelection && window.getSelection();
  if (!sel || !sel.rangeCount) return 0;
  const goc = sel.getRangeAt(0);
  const r = goc.cloneRange();
  r.selectNodeContents(el);
  r.setEnd(goc.endContainer, goc.endOffset);
  return r.toString().length;
}

function datCaret(el, vt) {
  if (!el) return false;
  el.focus();
  const sel = window.getSelection && window.getSelection();
  if (!sel) return false;
  const r = document.createRange();
  const t = el.firstChild;
  if (t && t.nodeType === 3) {
    r.setStart(t, Math.max(0, Math.min(vt, t.textContent.length)));
    r.collapse(true);
  } else {
    r.selectNodeContents(el);
    r.collapse(vt <= 0);
  }
  sel.removeAllRanges();
  sel.addRange(r);
  return true;
}

/** Đoạn gõ được gần nhất theo hướng `buoc`, bỏ qua dòng trống. */
function doanGoDuoc(n, buoc) {
  for (let i = n + buoc; i >= 1; i += buoc) {
    const el = document.querySelector(`[data-doan="${i}"] .doan__chu[contenteditable]`);
    if (el) return el;
    if (!document.querySelector(`[data-doan="${i}"]`)) return null;
  }
  return null;
}

/* Gộp đoạn n vào đoạn gõ được ngay trên nó, con trỏ dừng đúng chỗ nối - y như
   bấm Backspace ở đầu dòng trong Notepad. */
function gopLenDoanTren(n) {
  const ten = tenTepDangXem(S);
  const t = TAI_LIEU[ten];
  if (!t || !t.doan[n - 1]) return false;
  let tren = 0;
  for (let i = n - 1; i >= 1; i--) {
    if (t.doan[i - 1] && t.doan[i - 1].kieu !== 'blank') { tren = i; break; }
  }
  if (!tren) return false;

  const noi = String(t.doan[tren - 1].chu || '');
  const moi = t.doan.slice();
  moi[tren - 1] = { ...moi[tren - 1], chu: noi + String(t.doan[n - 1].chu || '') };
  moi.splice(n - 1, 1);
  TAI_LIEU[ten] = { ...t, doan: moi };
  danhDauSua();
  duLieuSoat = null;
  dat({ ...S, chips: dichThe(S.chips, ten, n, -1), soatBoQua: {}, sel: tren });
  datCaret(document.querySelector(`[data-doan="${tren}"] .doan__chu`), noi.length);
  return true;
}

/* Enter TÁCH ĐOẠN NGAY tại con trỏ, không đợi rời đoạn: phần sau con trỏ thành
   đoạn mới, con trỏ nhảy vào đầu đoạn ấy.

   Enter ở cuối đoạn tạo đoạn RỖNG và giữ nó lại - đặc tả nói rõ, vì người dùng
   vừa bấm Enter là để gõ tiếp. Đoạn rỗng ấy chỉ mất khi con trỏ rời đi mà vẫn
   không có chữ, việc đó do luuSuaDoan lo. */
function tachDoanTaiCho(n, phanTren, phanDuoi) {
  const ten = tenTepDangXem(S);
  const t = TAI_LIEU[ten];
  if (!t || !t.doan[n - 1]) return false;

  const goc = t.doan[n - 1];
  const moi = t.doan.slice();
  moi[n - 1] = { ...goc, chu: phanTren };
  moi.splice(n, 0, { kieu: 'body', chu: phanDuoi });
  TAI_LIEU[ten] = { ...t, doan: moi };
  danhDauSua();

  duLieuSoat = null;
  dat({ ...S, chips: dichThe(S.chips, ten, n + 1, 1), soatBoQua: {}, sel: n + 1 });
  datCaret(document.querySelector(`[data-doan="${n + 1}"] .doan__chu`), 0);
  return true;
}

/* Những đoạn mà vùng bôi đen đang chạm tới.

   Mỗi đoạn là một vùng gõ RIÊNG, nên quét chuột qua nhiều đoạn rồi bấm Xoá thì
   trình duyệt chỉ xoá phần nằm trong đoạn có con trỏ - phải tự gom lấy. */
function doanTrongVungChon() {
  const sel = window.getSelection && window.getSelection();
  if (!sel || sel.isCollapsed || !sel.rangeCount) return [];
  const r = sel.getRangeAt(0);
  return Array.from(document.querySelectorAll('#cuon [data-doan]'))
    .filter((el) => r.intersectsNode(el))
    .map((el) => +el.dataset.doan);
}

/* Xoá hẳn một loạt đoạn - đường của Ctrl+A rồi Xoá, và của quét chọn nhiều
   đoạn. Xoá từ dưới lên để số đoạn phía trên không xê dịch giữa chừng. */
function xoaCacDoan(ds) {
  const ten = tenTepDangXem(S);
  const t = TAI_LIEU[ten];
  if (!t || !ds.length) return;
  const bo = new Set(ds);
  const moi = t.doan.filter((_, i) => !bo.has(i + 1));
  TAI_LIEU[ten] = { ...t, doan: moi };
  danhDauSua();
  let chips = S.chips;
  Array.from(bo).sort((a, b) => b - a).forEach((n) => {
    chips = dichThe(chips, ten, n, -1);
  });
  duLieuSoat = null;
  dungPhat();
  dat({ ...S, chips, soatBoQua: {},
        sel: Math.max(1, Math.min(ds[0], moi.length)),
        pos: 1 });
}

/* Chép chữ vào tài liệu, và tách hoặc bỏ đoạn nếu cần. Một đoạn có thể ra
   NHIỀU đoạn (có xuống dòng) hoặc KHÔNG còn đoạn nào (xoá sạch chữ).

   Kết quả soát cũ bỏ hết: nó nói về bản chữ trước khi sửa, giữ lại là màn Soát
   chỉ vào những chỗ không còn tồn tại. */
function luuSuaDoan(n, chuMoi) {
  const ten = tenTepDangXem(S);
  const t = TAI_LIEU[ten];
  const cu = t && t.doan;
  if (!cu || !cu[n - 1]) return;

  const dong = String(chuMoi).split(/\r?\n/).map((x) => x.trim()).filter((x) => x);
  /* Không có gì đổi thì ĐỪNG vẽ lại. Rời đoạn nào cũng vẽ lại cả vùng đọc là
     bài dài giật một cái mỗi lần bấm sang dòng khác, mà chẳng để làm gì. */
  if (dong.length === 1 && dong[0] === cu[n - 1].chu) return;

  const moi = dong.length
    ? cu.slice(0, n - 1)
        .concat(dong.map((chu, i) => (i === 0 ? { ...cu[n - 1], chu } : { kieu: 'body', chu })),
                cu.slice(n))
    : cu.slice(0, n - 1).concat(cu.slice(n));

  const delta = moi.length - cu.length;
  TAI_LIEU[ten] = { ...t, doan: moi };
  danhDauSua();
  // Thẻ của đoạn n ở nguyên chỗ khi tách (dời từ n+1), nhưng phải bỏ khi xoá.
  const chips = delta ? dichThe(S.chips, ten, delta > 0 ? n + 1 : n, delta) : S.chips;
  duLieuSoat = null;
  dat({ ...S, chips, soatBoQua: {},
        sel: Math.max(1, Math.min(n, moi.length)),
        pos: Math.max(1, Math.min(S.pos, moi.length)) });
}

/** Gửi tài liệu của tab đang xem sang Python để dựng playlist. */
async function guiDoanSangPython(ep = false) {
  if (!coPython()) return;
  const van = vanTayTaiLieu();
  if (!ep && van === vanTayDaGui) return;   // Python đang giữ đúng tài liệu này

  /* Danh sách công đức KHÔNG gửi đoạn: chữ hiện trên màn hình là
     "Nguyễn Văn A — 500.000", còn câu engine đọc do mẫu trong lời dẫn dựng ra
     ("{ten}, {tien}."). Gửi đoạn hiển thị đi là Python dựng lại playlist kiểu
     văn bản thường và đọc trẹo hết. Bảo nó mở lại tệp gốc mới đúng. */
  let kq;
  if (loaiTepDangXem() === 'congduc') {
    const dd = S.duongDanTep[tenTepDangXem(S)];
    kq = dd ? await api('moi_doc_danh_sach', dd) : null;
    if (kq && kq.loi) { moBao(kq.loi); kq = null; }
  } else {
    /* Gửi thẻ cảm xúc kèm từng đoạn, dưới khoá `the` RIÊNG chứ không nhét vào
       `chu`. Nhét vào chu là mọi vị trí tô chữ lệch đúng bằng độ dài thẻ, vì
       tach_chunk đếm start/end trên chính chuỗi hiển thị. */
    const doanGui = doanDangXem(S, TAI_LIEU).map((d, i) => {
      const the = theCuaDoan(S, i + 1);
      return the ? { ...d, the } : d;
    });
    kq = await api('moi_dat_doan', doanGui);
  }
  // Chỉ ghi nhận khi Python xác nhận. Gửi hỏng mà vẫn đánh dấu là đã gửi thì
  // lần bấm Nghe sau lại bỏ qua, và đọc nhầm tài liệu lần nữa.
  vanTayDaGui = kq ? van : '';
}

// ---------------------------------------------------------------- nhớ hồ sơ

/* Hồ sơ, tab, ba thanh điều chỉnh và thẻ cảm xúc phải sống qua lần đóng cửa
   sổ. Ghi vào hoso-v2.json RIÊNG, không đụng hoso.json của bản đang dùng hằng
   ngày — xem giaodien_moi/khoa_du_lieu.py. */

const CHO_LUU_MS = 600;

/* Cố ý KHÔNG lưu pos/sel/view: mở chương trình lên mà thấy nó đang đứng giữa
   bài với thanh phát sáng đèn thì người dùng tưởng máy tự đọc. */
function phanCanLuu() {
  return {
    dangDung: S.profile,
    theme: S.theme,
    zoom: S.zoom,
    the: S.chips,
    duongDan: S.duongDanTep,
    loaiTep: S.loaiTep,
    hoSo: S.profiles.map((h, i) => ({
      ma: h.ma, ten: h.ten, giong: h.giong, chinh: h.chinh,
      tep: S.tabsByProfile[i] || [''],
      dangXem: S.activeByProfile[i] || 0,
    })),
  };
}

let chuKyDaLuu = '';
let henGioLuu = 0;

/* Gộp nhiều lần đổi liên tiếp thành MỘT lần ghi. Kéo thanh Tốc độ là dat()
   chạy theo từng nhịp chuột; ghi đĩa mỗi nhịp thì vừa phí vừa có lúc hai lần
   ghi chồng lên nhau. So chữ ký trước để bấm nút không liên quan (mở menu,
   chọn đoạn) không sinh ra lượt ghi nào. */
function henLuuHoSo() {
  if (!coPython()) return;
  const chuKy = JSON.stringify(phanCanLuu());
  if (chuKy === chuKyDaLuu) return;
  chuKyDaLuu = chuKy;
  clearTimeout(henGioLuu);
  henGioLuu = setTimeout(() => api('moi_luu_ho_so', JSON.parse(chuKy)), CHO_LUU_MS);
}

/* Tab nhớ TÊN tệp, còn nội dung thì không nằm trong hoso-v2.json — mở lại từ
   đường dẫn đã lưu. Chỉ mở tệp ĐANG XEM: mở hết mọi tab là bắt người dùng chờ
   ngay lúc khởi động, trong khi phần lớn tab họ không đụng tới phiên đó. */
async function moLaiTepDangXem() {
  const ten = tenTepDangXem(S);
  if (!ten || TAI_LIEU[ten] || !coPython()) return;
  const dd = S.duongDanTep[ten];
  if (!dd) return;
  const kq = await api('moi_doc_tep', dd);
  // Tệp đã bị xoá hoặc đổi tên từ lần trước: để tab trống, đừng doạ người dùng
  // bằng hộp thoại đỏ ngay lúc vừa mở chương trình.
  if (!kq || kq.loi) return;
  TAI_LIEU[ten] = { doan: kq.doan || [], chuY: { tomTat: '', loai: [] } };
}

/** Đổi hồ sơ / đổi tab: nạp nội dung tệp nếu chưa có, rồi mới dựng playlist. */
async function chuyenSang(trangThaiMoi) {
  dungPhat();
  dat(trangThaiMoi);
  // Mỗi hồ sơ một giọng riêng — đổi hồ sơ mà quên báo sang Python là cột phải
  // ghi giọng này còn loa đọc giọng của hồ sơ trước.
  dongBoGiongSangPython();
  await moLaiTepDangXem();
  ve();
  guiDoanSangPython();
}

async function napHoSoDaLuu() {
  const d = coPython() ? await api('moi_doc_ho_so') : null;
  if (!d || !d.hoSo || !d.hoSo.length) return;   // lần chạy đầu: dùng hồ sơ mẫu

  const tabs = {}, dangXem = {};
  d.hoSo.forEach((h, i) => { tabs[i] = h.tep.slice(); dangXem[i] = h.dangXem || 0; });

  S = { ...S,
        profiles: d.hoSo.map((h) => ({ ma: h.ma, ten: h.ten, giong: h.giong,
                                       chinh: h.chinh, tep: h.tep.slice() })),
        tabsByProfile: tabs,
        activeByProfile: dangXem,
        profile: Math.min(d.dangDung || 0, d.hoSo.length - 1),
        theme: d.theme === 'toi' ? 'toi' : 'sang',
        zoom: d.zoom || 100,
        chips: d.the || {},
        duongDanTep: d.duongDan || {},
        loaiTep: d.loaiTep || {},
        pos: 1, sel: 1, view: 'san_sang' };

  // Vừa đọc lên thì chữ ký đã khớp đĩa: đừng ghi lại y nguyên một lần nữa.
  chuKyDaLuu = JSON.stringify(phanCanLuu());
  await moLaiTepDangXem();
  ve();
}

/* Thay danh sách giọng mock bằng giọng THẬT trên máy.

   GIONG là const nên không gán lại được — sửa tại chỗ. Cố ý: mọi nơi khác đã
   giữ tham chiếu tới mảng này rồi, gán lại là chúng trỏ vào mảng cũ. */
function datGiongThat(kq) {
  if (!kq || !kq.giong || !kq.giong.length) return;

  GIONG.length = 0;
  kq.giong.forEach((g) => GIONG.push(g));
  GIONG_TRONG_DROPDOWN.length = 0;
  GIONG.forEach((g) => GIONG_TRONG_DROPDOWN.push(g.ma));

  /* Hồ sơ nào trỏ vào giọng không có trên máy thì lấy GIỌNG ĐẦU DANH SÁCH.

     Quyết định của chủ dự án (2026-08-12): dùng lại thiết lập của lần chạy
     gần nhất; chưa có lần nào thì lấy giọng đầu tiên trong danh sách giọng
     thật. Cố ý KHÔNG dùng kq.dangDung: giá trị đó đến từ cauhinh.ini của bản
     đang chạy hằng ngày. Lấy nó là bản mới lại đi đọc dữ liệu bản cũ, đúng
     thứ vừa bịt ở khoa_du_lieu.py — và đang có sẵn một dấu vết thử nghiệm
     nằm trong đó. Hồ sơ của lần chạy trước nằm ở hoso-v2.json, napHoSoDaLuu
     đã đổ vào S trước khi hàm này chạy. */
  const co = new Set(GIONG.map((g) => g.ma));
  dat({ ...S, profiles: S.profiles.map((h) =>
    co.has(h.giong) ? h : { ...h, giong: GIONG[0].ma }) });
  dongBoGiongSangPython();
}

/* Engine đọc bằng giọng trong cfg của Python, còn giao diện hiện giọng của hồ
   sơ. Hai bên phải khớp, không thì cột phải ghi một giọng mà loa đọc giọng
   khác. Gửi sang mỗi khi giọng của hồ sơ đang dùng đổi — kể cả lúc vừa mở
   chương trình, vì cfg lúc đó đang mang giọng đọc từ cauhinh.ini của bản cũ. */
let giongDaGui = '';

function dongBoGiongSangPython() {
  const h = hoSoDangDung(S);
  if (!coPython() || !h || !h.giong || h.giong === giongDaGui) return;
  giongDaGui = h.giong;
  api('doi_giong', h.giong);
}

// ---------------------------------------------------------------- màn soát

/* Số liệu của màn soát do Python tính. Giữ ngoài S vì nó là DỮ LIỆU DẪN XUẤT
   từ văn bản, không phải trạng thái người dùng chọn — nhét vào S là mỗi lần
   lưu hồ sơ lại ghi cả đống kết quả soát xuống đĩa. */
let duLieuSoat = null;

async function moManSoat() {
  if (!coPython()) {
    moBao('Soát văn bản cần chạy bằng GiongViet.');
    return;
  }
  if (!doanDangXem(S, TAI_LIEU).length) {
    moBao('Chưa có văn bản nào để soát. Hãy Dán văn bản hoặc Mở tệp trước.');
    return;
  }
  // Gửi lại đoạn trước khi soát: tab 2 so văn bản gốc với chuỗi engine THẬT
  // sẽ đọc, mà chuỗi đó nằm trong playlist bên Python. Playlist cũ là so nhầm
  // với tài liệu khác — đúng cái lỗi đã vấp ở nút Nghe.
  await guiDoanSangPython();
  duLieuSoat = await api('moi_soat');
  dat({ ...dongHetMenu(S), man: 'soat', soatTab: 'chuy', soatLoc: 'tatca' });
}

async function datQuyTacSoat(khoa, bat) {
  const kq = await api('moi_dat_quy_tac', khoa, bat);
  if (kq) { duLieuSoat = kq; ve(); }
}

/** Thêm một chữ viết tắt vào từ điển phát âm, ngay từ màn soát. */
async function themVaoTuDien(tu) {
  if (!tu) return;
  const doc = window.prompt(
    `Máy nên đọc “${tu}” thành gì?\n\n`
    + 'Ví dụ: UBND → Uỷ ban nhân dân', '');
  if (!doc || !doc.trim()) return;
  const kq = await api('them_tu', tu, doc.trim());
  if (!kq) { moBao('Chưa thêm được vào từ điển.'); return; }
  await guiDoanSangPython(true);      // từ điển đổi → chuỗi đọc đổi
  duLieuSoat = await api('moi_soat');
  ve();
  moBao(`Đã dạy máy đọc “${tu}” thành “${doc.trim()}”.`);
}

// ---------------------------------------------------------------- màn giọng

let duLieuGiong = null;

async function moManGiong() {
  if (!coPython()) { moBao('Thư viện giọng cần chạy bằng GiongViet.'); return; }
  // Giọng "đang dùng" là giọng của HỒ SƠ, không phải của cfg — mỗi hồ sơ giữ
  // giọng riêng, lấy nhầm cfg là thẻ sáng ở giọng khác với cột phải đang ghi.
  duLieuGiong = await api('moi_thu_vien_giong', hoSoDangDung(S).giong);
  if (!duLieuGiong) { moBao('Chưa đọc được danh sách giọng.'); return; }
  dat({ ...dongHetMenu(S), man: 'giong', giongLoc: 'tatca',
        giongGioi: 'Tất cả', giongTim: '' });
}

/* Nhân bản giọng riêng. Chạy nền vài phút; Python đẩy tiến độ về qua
   window.gd.tienDoGiong / giongXong / giongLoi. */
async function nhanBanGiong() {
  if (S.dangNhanBan) return;
  const tep = await api('chon_file_mau');
  if (!tep) return;
  const ten = window.prompt(
    'Đặt tên cho giọng này là gì?\n\n'
    + 'Ví dụ: Giọng bác Tuấn', '');
  if (!ten || !ten.trim()) return;
  dat({ ...S, dangNhanBan: true, tienDoGiong: 'Đang chuẩn bị…' });
  api('nhan_ban_giong', ten.trim(), tep);
}

datKhiNhanBanGiong(
  (msg) => { if (S.dangNhanBan) dat({ ...S, tienDoGiong: msg }); },
  async (ten) => {
    duLieuGiong = await api('moi_thu_vien_giong', hoSoDangDung(S).giong);
    dat({ ...S, dangNhanBan: false, tienDoGiong: '' });
    moBao(`Đã tạo xong “${ten}”. Bấm Nghe thử để nghe.`);
  },
  (msg) => {
    dat({ ...S, dangNhanBan: false, tienDoGiong: '' });
    // Engine viết sẵn thông báo dài, dễ hiểu (thiếu PyTorch, máy không đủ
    // điều kiện…). Đưa nguyên văn chứ đừng rút gọn thành "có lỗi".
    moBao(msg || 'Chưa nhân bản được giọng.');
  });

async function xoaGiongRieng(ma, ten) {
  if (!window.confirm(`Xoá giọng “${ten}” khỏi máy?\n\n`
                      + 'Tệp mẫu đã thu cũng bị xoá, không lấy lại được.')) return;
  const kq = await api('xoa_giong', ma);
  if (!kq) { moBao('Chưa xoá được giọng này.'); return; }
  duLieuGiong = await api('moi_thu_vien_giong', hoSoDangDung(S).giong);
  ve();
  moBao(`Đã xoá giọng “${ten}”.`);
}

/** Dán cờ "đang nghe thử" vào đúng thẻ, để nút đổi thành Dừng. */
function danhDauNgheThu() {
  if (!duLieuGiong) return;
  for (const nhom of ['cuaToi', 'coSan']) {
    (duLieuGiong[nhom] || []).forEach((g) => { g.dangNgheThu = g.id === S.dangNgheThu; });
  }
}

// ---------------------------------------------------------------- màn cài đặt

let duLieuCaiDat = null;

async function moManCaiDat() {
  if (!coPython()) { moBao('Cài đặt cần chạy bằng GiongViet.'); return; }
  duLieuCaiDat = await api('moi_cai_dat');
  if (!duLieuCaiDat) { moBao('Chưa đọc được cài đặt.'); return; }
  dat({ ...dongHetMenu(S), man: 'caidat' });
}

async function datCaiDat(khoa, bat) {
  const kq = await api('moi_dat_cai_dat', khoa, bat);
  if (!kq) { moBao('Chưa đổi được thiết lập này.'); return; }
  duLieuCaiDat = kq;
  ve();
}

async function doiThuMucXuat() {
  const kq = await api('moi_chon_thu_muc_xuat');
  if (kq) { duLieuCaiDat = kq; ve(); }
}

// ---------------------------------------------------------------- màn từ điển

let duLieuTuDien = null;

async function moManTuDien() {
  if (!coPython()) { moBao('Từ điển phát âm cần chạy bằng GiongViet.'); return; }
  duLieuTuDien = await api('moi_tu_dien', '');
  if (!duLieuTuDien) { moBao('Chưa đọc được từ điển.'); return; }
  dat({ ...dongHetMenu(S), man: 'tudien', tuDienTim: '', tuDienSua: null });
}

async function timTuDien(chu) {
  duLieuTuDien = await api('moi_tu_dien', chu) || duLieuTuDien;
  ve();
  const o = $('#oTimTuDien');
  if (o) { o.focus(); o.setSelectionRange(o.value.length, o.value.length); }
}

/** Thêm / sửa / xoá một mục. Python ghi tudien.ini rồi trả bảng đã cập nhật. */
async function suaTuDien(viec, tu, doc, tuCu) {
  const kq = await api('moi_sua_tu_dien', viec, tu, doc || '', tuCu || '');
  if (!kq) { moBao('Chưa lưu được. Hãy kiểm lại chữ và cách đọc.'); return; }
  duLieuTuDien = kq;
  dat({ ...S, tuDienSua: null });
  moBao(viec === 'xoa' ? `Đã xoá “${tu}” khỏi từ điển.`
                       : `Đã lưu cách đọc cho “${tu}”.`);
}

/** Nghe thử cách đọc vừa gõ, trước khi lưu. */
function ngheThuCachDoc() {
  const doc = $('#oDocMoi') ? $('#oDocMoi').value.trim() : '';
  if (!doc) { moBao('Hãy gõ cách đọc trước đã.'); return; }
  if (coPython()) api('moi_nghe_cau', doc);
}

// ---------------------------------------------------------------- nghe thử

/* Hạ nút xuống NGAY, không chờ Python báo về: BoNgheThu.dung() tăng số phiên
   để vô hiệu lần đang chạy, nên nó không gọi ngheThuXong nữa. Chờ tín hiệu
   không bao giờ đến là nút sáng mãi. */
function dungNgheThu() {
  if (!S.dangNgheThu) return;
  if (coPython()) api('moi_dung_nghe_thu');
  dat({ ...S, dangNgheThu: '', mauDangPhat: false });
}

datKhiNgheThuXong((ma) => {
  // Chỉ hạ nút của ĐÚNG giọng vừa xong. Bấm giọng khác trong lúc giọng cũ còn
  // đang tổng hợp thì tín hiệu về mang mã giọng cũ — hạ bừa là tắt mất nút của
  // giọng mới vừa bấm, trong khi tiếng của nó sắp ra.
  if (!ma || S.dangNgheThu === ma) dat({ ...S, dangNgheThu: '', mauDangPhat: false });
});

datKhiBaoLoi((tieuDe, chiTiet) => {
  // Lỗi lúc nghe thử: hạ nút rồi nói cho người dùng biết. Trước đây chỉ ghi vào
  // console — người dùng ngồi nhìn nút sáng, không hiểu vì sao không có tiếng.
  dat({ ...S, dangNgheThu: '', mauDangPhat: false });
  moBao(chiTiet || tieuDe || 'Máy đọc gặp lỗi, chưa phát được.');
});

/* BẮT BUỘC gọi moi_khoi_dong: nó nạp danh sách giọng và BẬT MÔ HÌNH. Thiếu
   dòng này thì mọi thứ vẽ ra vẫn đẹp mà bấm Nghe không ra tiếng, vì mô hình
   chưa bao giờ được khởi động. Đã vấp đúng lỗi này một lần. */
async function khoiDong() {
  if (!coPython()) return;
  // Hồ sơ đã lưu phải nạp TRƯỚC danh sách giọng: datGiongThat còn phải sửa lại
  // hồ sơ nào trỏ vào giọng không còn trên máy, mà muốn sửa thì hồ sơ thật
  // phải có mặt rồi.
  await napHoSoDaLuu();
  datGiongThat(await api('moi_khoi_dong'));
  await guiDoanSangPython();
  await capNhatNutCuaSo();      // nút giữa phải đúng ngay từ lúc mở
}
window.addEventListener('pywebviewready', khoiDong);

ve();
khoiDong();
