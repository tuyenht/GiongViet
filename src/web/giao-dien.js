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
let henGioTuDongLuu = 0;

function danhDauSua() {
  const t = tenTepDangXem(S);
  if (!t) return;
  chuaLuu.add(t);
  const nut = $('#ttLuu');
  if (nut) nut.innerHTML = veTinhTrangLuu();

  // Tự động lưu ngầm chống mất dữ liệu sau 2.5s không thao tác
  clearTimeout(henGioTuDongLuu);
  henGioTuDongLuu = setTimeout(() => {
    if (chuaLuu.has(t)) {
      tuDongLuuNgam(t);
    }
  }, 2500);
}

async function tuDongLuuNgam(ten) {
  if (!coPython() || !ten) return;
  const t = TAI_LIEU[ten];
  const doan = (t && t.doan ? t.doan : []).filter((d) => d && d.kieu !== 'blank');
  if (!doan.length) return;
  try {
    const kq = await api('moi_luu_van_ban', ten, doan.map((d) => d.chu).join('\n'));
    if (kq && kq.ten) {
      chuaLuu.delete(ten);
      gioLuuCuoi = new Date().toTimeString().slice(0, 5);
      const nut = $('#ttLuu');
      if (nut) nut.innerHTML = veTinhTrangLuu();
    }
  } catch (e) {
    // Không làm phiền người dùng khi lưu ngầm
  }
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
           ['Mở từ Google Docs…', ''],
           // Thiết kế không nêu mục này, nhưng code CÓ và nó là đường duy nhất
           // mở danh sách tên–số. Giữ lại, đã báo ở mục "code làm tốt hơn thiết kế".
           ['Mở danh sách tên và số…', ''],
           ['Dán văn bản', 'Ctrl+V'], ['Lưu', 'Ctrl+S'],
           ['Xuất file âm thanh', 'Ctrl+E'], ['Đóng tệp', 'Ctrl+W'],
           ['-'],
           ['Văn bản ghép (Live Data)…', ''],
           ['-'],
           ['Cài đặt…', ''], ['Thoát', 'Alt+F4']]],
  /* GIỮ "Thẻ cảm xúc": nó KHÔNG cần sửa văn bản. datThe() gắn thẻ cho đoạn
     đang chọn vào S.chips, và ba thẻ là tính năng thật của VieNeu. Trước đây
     chỉ Alt+1…3 chạy được, còn bấm chuột thì chết vì S.tags không nơi nào bật
     lên — nay nối vào LENH.

     Hoàn tác · Làm lại · Cắt · Sao chép · Dán để XÁM và nói thật: trình duyệt
     tự lo bốn việc ấy ngay trong vùng chữ, nhưng chưa có lệnh riêng bấm từ
     menu. Đừng nối bừa vào một lệnh gần giống.

     "Chọn tất cả" thì ĐÃ nối: chonTatCa() bôi đen cả bài, gọi được từ cả ba
     đường — Ctrl+A trong bài, Ctrl+A ngoài bài, và mục menu này. */
  ['Chỉnh sửa', [['Hoàn tác', 'Ctrl+Z', 'Bấm phím Ctrl+Z ngay trong chữ thì được; nút menu chưa nối'],
                 ['Làm lại', 'Ctrl+Y', 'Bấm phím Ctrl+Y ngay trong chữ thì được; nút menu chưa nối'],
                 ['-'],
                 ['Cắt', 'Ctrl+X', 'Bấm phím Ctrl+X ngay trong chữ thì được; nút menu chưa nối'],
                 ['Sao chép', 'Ctrl+C', 'Bấm phím Ctrl+C ngay trong chữ thì được; nút menu chưa nối'],
                 ['Dán', 'Ctrl+V', 'Chưa làm — dán tại con trỏ khác với “Dán văn bản” ở menu Tệp'],
                 ['Chọn tất cả', 'Ctrl+A'],
                 ['-'],
                 ['Xoá dòng/đoạn trắng', 'Ctrl+Shift+L'],
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
        ${muc.map(([m, phim, chuaLam]) => {
          if (m === '-') return '<div class="roi__ngan"></div>';
          const tenHienThi = (m === 'Giao diện tối' || m === 'Giao diện sáng')
            ? (S.theme === 'toi' ? 'Giao diện sáng' : 'Giao diện tối')
            : m;
          const lenh = (m === 'Giao diện tối' || m === 'Giao diện sáng') ? tenHienThi : m;
          return `<button class="roi__muc"${chuaLam
               ? ` disabled title="${esc(chuaLam)}"`
               : ` data-lenh="${esc(lenh)}"`}>
               <span class="roi__ten">${esc(tenHienThi)}</span>
               <span class="roi__phim">${esc(phim || '')}</span></button>`;
        }).join('')}
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
  const mo = coVanBan ? '' : ' la-khoa';         // chưa có văn bản thì chuyển màu dis
  const khoa = biKhoa(S) || !moHinhSanSang();
  const viKhoa = lyDoKhoa(S);
  const chuaCoChu = coVanBan ? '' : 'Chưa có văn bản — hãy Dán văn bản hoặc Mở tệp trước';
  const ten = tenTepDangXem(S);
  const laTepGhep = (S.loaiTep && S.loaiTep[ten] === 'ghep') || (ten && (ten.includes('(Ghép)') || ten.startsWith('Danh sách ghép')));

  return `
  <div class="congcu">
    <button class="nut" data-lenh="Dán văn bản"${nhac('Dán văn bản từ clipboard (Ctrl+V)')
      }>${ic('dan')}<span>Dán văn bản</span></button>
    <button class="nut" data-lenh="Mở tệp…"${nhac('Mở tệp văn bản (Ctrl+O)')
      }>${ic('thumuc')}<span>Mở file</span></button>
    <button class="nut" data-lenh="Mở từ Google Docs…"${nhac('Mở tài liệu Google Docs trực tiếp từ link')
      }>${ic('gdoc', 15)}<span>Google Docs</span></button>
    <button class="nut" data-lenh="Văn bản ghép (Live Data)…"${nhac('Ghép danh sách từ bảng tính Google Sheet / Excel (Live Data)')
      }>${ic('ghep', 15)}<span>Văn bản ghép</span></button>
    ${laTepGhep ? `
      <button class="nut" id="nutDongBoLive" style="color:var(--acc);font-weight:600"
              title="Đồng bộ lấy dòng mới nhất từ Google Sheets/Excel ngay khi đang đọc (không ngắt tiếng)">
        ${ic('dongbo', 14)}<span>Đồng bộ Live</span>
      </button>
    ` : ''}
    <span class="congcu__ngan"></span>
    <button class="nut${mo}" data-lenh="Soát văn bản"${
      nhac('Xem các chỗ dễ đọc sai và văn bản sau chuẩn hoá (Ctrl+K)', chuaCoChu)
      }>${ic('tich')}<span>Soát văn bản</span></button>
    <span class="congcu__o">
      <button class="nut${mo}" id="nutThe"${
        nhac('Chèn thẻ cảm xúc vào đoạn đang chọn', chuaCoChu)
        }>${ic('cx')}<span>Thẻ cảm xúc</span>${ic('mui', 13)}</button>
      ${S.tags ? veMenuThe() : ''}
    </span>
    <span class="congcu__phai">
      <button class="nut${mo}" id="nutTim"${
        nhac('Tìm một từ trong văn bản và thay bằng từ khác (Ctrl+H)', chuaCoChu)
        }>${ic('kinhlup')}<span>Tìm và thay thế</span></button>
      ${coVanBan ? `<span class="congcu__ngan"></span>
        <button class="nut nut--vien nut--cao${dangPhat ? ' dang-phat' : ''}${khoa ? ' la-khoa' : ''}" id="nutNghe"${nhac(dangPhat ? 'Tạm dừng (Space)'
            : daTamDung ? 'Đọc tiếp từ đoạn ' + S.pos + ' (Space)'
            : 'Nghe liền mạch toàn bộ văn bản từ đầu (Space)', viKhoa)}>
          ${ic(dangPhat ? 'tamdung' : 'tamgiac', 13)}<span>${
            dangPhat ? 'Tạm dừng' : daTamDung ? 'Đọc tiếp' : 'Nghe toàn bộ'}</span></button>
        <button class="nut nut--acc nut--cao${khoa ? ' la-khoa' : ''}" id="nutXuat"${
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
  if (S.dangChuanBiDich) {
    return `
  <div class="dai dai--info" style="background:var(--acc-soft);border-bottom:1px solid var(--acc);padding:8px 16px;display:flex;align-items:center;gap:12px">
    <span class="xoay" style="width:16px;height:16px;border-width:2px;border-color:var(--acc);border-top-color:transparent"></span>
    <span class="dai__than">
      <span class="dai__ten" style="color:var(--acc);font-weight:700">${esc(S.thongBaoDich || 'Đang chuẩn bị bản dịch sang ngôn ngữ đích…')}</span>
      <div class="dai__noi">Các nút phát và xuất sẽ tự động sáng ngay khi bản dịch sẵn sàng.</div>
    </span>
  </div>`;
  }

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
  // voiceOpen là khoá THẬT mà veCotPhai đọc để dựng dropdown giọng. Bản đầu viết
  // nhầm thành `roiGiong` — không nơi nào đọc khoá đó, nên nút "Dùng giọng khác"
  // vẫn là nút giả, mà phép canh chỉ soi `!!S.roiGiong` nên vẫn báo xanh.
  mo_chon_giong: () => dat({ ...S, situation: 'binh_thuong', voiceOpen: true }),
  // Bản mẫu nhảy tới đúng chỗ sẽ bị cắt rồi trả màn về bình thường.
  xem_cho_cat: () => dat({ ...S, situation: 'binh_thuong', sel: 9, pos: 9 }),
  nghe_lai_doan_da_sua: () => {
    dat({ ...S, situation: 'binh_thuong', sel: 4, pos: 4 });
    batDauPhat();
  },
};

// ---------------------------------------------------------------- cột trái

const ICON_HO_SO = ['baiviet', 'danto', 'sach', 'danhsach', 'baiviet'];

/* Hàng tệp nào đang được gõ lại tên. Để ở tầng module chứ không nhét vào S:
   phanCanLuu() ghi thẳng S xuống hoso-v2.json, mà "đang gõ dở tên" thì không
   phải thứ đáng nhớ qua lần chạy sau. Cùng chỗ với chuaLuu vì cùng bản chất. */
let suaTenTep = null;

/* Chữ người dùng đang gõ dở trong ô tên, và vị trí con trỏ trong đó.

   Bắt buộc phải giữ, vì ve() dựng lại TOÀN BỘ HTML: mọi gói tin Python đẩy về
   đều đi qua dat() rồi ve(), và lúc đang đọc thì mỗi mẩu đọc xong lại có gói.
   Không giữ thì ô vẽ lại với tên CŨ — chữ vừa gõ bay sạch mà ô vẫn mở như
   không có gì xảy ra. Đo được: đang đọc, nháy đúp đổi tên, gõ "Thư gửi con",
   máy sang đoạn kế → value quay về "a.txt".

   Bản mẫu không dính vì nó giữ chữ đang gõ trong state (fText) và tự lấy lại
   tiêu điểm mỗi lần vẽ (nameRef). Đây là hai thứ bản port bỏ mất — vẫn đúng
   bài học cũ: bê cả mô hình chứ đừng bê mỗi thao tác. */
let tenDangGo = null;
let viTriTenDangGo = 0;

/* Thôi sửa tên. Gọi ở MỌI chỗ rời khỏi ô — sót một chỗ là chữ gõ dở của hàng
   này nhảy sang hàng khác lúc mở ô lần sau. */
function thoiSuaTen() {
  suaTenTep = null;
  tenDangGo = null;
  viTriTenDangGo = 0;
}

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
        const laGhep = (S.loaiTep && S.loaiTep[ten] === 'ghep') || nhan.includes('(Ghép)') || nhan.startsWith('Danh sách ghép');
        const iconTep = laGhep
          ? `<span class="tep__icon" style="color:var(--acc)" title="Văn bản ghép từ mẫu">${ic('ghep', 13)}</span>`
          : `<span class="tep__icon">${ic('tep', 13)}</span>`;
        if (suaTenTep === `${i}:${j}`) {
          return `<div class="tep tep--sua">
            ${iconTep}
            <input class="tep__o" id="oTenTep" spellcheck="false"
                   value="${esc(tenDangGo != null ? tenDangGo : nhan)}" data-suatep="${j}">
          </div>`;
        }
        /* tabindex + role: hàng tệp là <div> chứ không phải <button>, vì bên
           trong đã có nút ×, mà nút lồng trong nút thì trình duyệt tự đẩy ra
           ngoài. Không có hai thuộc tính này thì người chỉ dùng bàn phím không
           tới được hàng nào - dải tab cũ vướng đúng lỗi đó, đừng bê sang. */
        return `<div class="tep${on ? ' dang-xem' : ''}" data-tep="${j}"
                     tabindex="0" role="button" aria-current="${on}"
                     title="${esc(nhan)} · nháy đúp để đổi tên">
          ${iconTep}
          <span class="tep__ten">${esc(nhan)}</span>
          <button class="tep__dong" data-dongtep="${j}" title="Đóng tệp">${ic('dong', 9)}</button>
        </div>`;
      }).join('')}
      <button class="nut tep__them" id="themTep"
              title="Mở thêm một tệp trong hồ sơ này">
        ${ic('cong', 12)}<span>Thêm tệp</span></button>
    </div>`;
}

const MA_HE_THONG = ['tin_tuc', 'loa_phuong', 'sach_noi', 'cong_duc', 'ban_hang', 'phap_quy'];

function veCotTrai() {
  const dsHeThong = [];
  const dsTuyChinh = [];
  S.profiles.forEach((h, i) => {
    const laHeThong = MA_HE_THONG.includes(h.ma) || i < 6;
    if (laHeThong && dsHeThong.length < 6) {
      dsHeThong.push({ h, i, laHeThong: true });
    } else {
      dsTuyChinh.push({ h, i, laHeThong: false });
    }
  });

  const veItemHoSo = ({ h, i, laHeThong }) => {
    const g = GIONG.find((x) => x.ma === h.giong || x.id === h.giong || x.ten === h.giong || (x.ma && h.giong && x.ma.toLowerCase() === h.giong.toLowerCase()));
    const iconTen = ICON_HO_SO[i % ICON_HO_SO.length] || 'tep';
    const on = i === S.profile;
    const coNutXoa = !laHeThong;

    return `
      <div class="hoso-wrap" style="position:relative;display:flex;align-items:center;margin-bottom:2px">
        <button class="hoso${on ? ' dang-dung' : ''}" data-hoso="${i}"
                style="flex:1;text-align:left;padding-right:${coNutXoa ? '32px' : '10px'}">
          <span class="hoso__icon">${ic(iconTen, 17)}</span>
          <span class="hoso__than">
            <span class="hoso__ten">${esc(h.ten)}</span>
            <span class="hoso__giong">${esc(g ? g.ten : h.giong || '')}</span>
          </span>
        </button>
        ${coNutXoa ? `
          <button class="nut nut--icon" data-xoahoso="${i}" title="Xóa hồ sơ tùy biến này"
                  style="position:absolute;right:6px;top:50%;transform:translateY(-50%);width:24px;height:24px;padding:0;display:inline-flex;align-items:center;justify-content:center;color:var(--txt3);border-radius:4px;border:none;background:transparent;cursor:pointer;z-index:2">
            ${ic('dong', 10)}
          </button>` : ''}
      </div>${veCayTep(i)}`;
  };

  return `
  <div class="trai${S.rail ? ' thu-gon' : ''}">
    <div class="trai__dau">
      <button class="nut nut--icon" id="thuGon" title="${
        /* Nói rõ là thu CẢ danh sách tệp. */
        S.rail ? 'Mở lại danh sách hồ sơ và tệp (Ctrl+B)'
               : 'Thu gọn danh sách hồ sơ và tệp (Ctrl+B)'}">
        ${ic('bagach')}</button>
      <span class="trai__ten">Hồ sơ đọc</span>
    </div>
    <div class="trai__ds">
      <div class="hoso-nhom-nhan">
        <span>Hồ sơ mặc định</span>
        <span style="font-size:10px;opacity:.7">6 mẫu</span>
      </div>
      ${dsHeThong.map(veItemHoSo).join('')}

      ${dsTuyChinh.length ? `
        <div class="hoso-nhom-nhan" style="margin-top:10px">
          <span>Hồ sơ của bạn</span>
          <span style="font-size:10px;opacity:.7">${dsTuyChinh.length}</span>
        </div>
        ${dsTuyChinh.map(veItemHoSo).join('')}
      ` : ''}

      <button class="nut trai__lienket nhan-chu" data-lenh="Tạo hồ sơ mới" style="margin-top:8px"
              title="Tạo hồ sơ đọc mới từ mẫu chuẩn">
        ${ic('cong', 14)}<span>Tạo hồ sơ mới</span></button>
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
    ${vePhuDeSongNgu(S, hoSoDangDung(S))}
    ${veThanhPhat()}
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

  let chuHien = esc(d.chu);
  if (S.man === 'soat' && duLieuSoat && duLieuSoat.chuY && (duLieuSoat.chuY.vanDe || []).length) {
    const dsVanDe = duLieuSoat.chuY.vanDe.filter(v => v.doan === n);
    if (dsVanDe.length) {
      dsVanDe.forEach(v => {
        if (v.loai === 'viettat' && v.tu) {
          const escTu = esc(v.tu);
          const re = new RegExp(`\\b(${escTu})\\b`, 'g');
          chuHien = chuHien.replace(re, '<span class="soat-wavy-err" title="Chưa dạy máy đọc từ này">$1</span>');
        }
      });
    }
  }

  return `<div class="${cls.join(' ')}" data-doan="${n}">
    <span class="doan__so">${
      dangCho ? '<span class="xoay xoay--nho" style="display:inline-block"></span>'
              : n}</span>
    <!-- data-doan đủ để nhịp đọc gạt lớp trên từng đoạn mà không dựng lại DOM -->
    <span class="doan__than">${d.kieu === 'blank' ? '' :
      `${the ? `<span class="doan__the" contenteditable="false" data-gothe="${n}"
             title="Bấm để gỡ thẻ cảm xúc">${esc(the)}</span>` : ''}<span
          class="doan__chu"${suaDuoc ? ' contenteditable="true" spellcheck="false"' : ''}
         >${chuHien}</span>`}</span>${
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
      <button class="nut nut--vien" data-lenh="Mở từ Google Docs…" title="Chọn một tài liệu Google Docs trên Drive">Mở từ Google Docs…</button>
    </div>
  </div></div>`;
};

const DS_NGON_NGU = [
  // Nhóm 1: Bản Địa & Đông Nam Á (ASEAN)
  { ma: 'vi', ten: 'Tiếng Việt (Gốc / Mặc định)', co: '🇻🇳', nhom: 'Đông Nam Á & Bản Địa' },
  { ma: 'th', ten: 'Tiếng Thái (ภาษาไทย)', co: '🇹🇭', nhom: 'Đông Nam Á & Bản Địa' },
  { ma: 'id', ten: 'Tiếng Indonesia (Bahasa)', co: '🇮🇩', nhom: 'Đông Nam Á & Bản Địa' },
  { ma: 'ms', ten: 'Tiếng Malaysia (Melayu)', co: '🇲🇾', nhom: 'Đông Nam Á & Bản Địa' },
  { ma: 'fil', ten: 'Tiếng Philippines (Tagalog)', co: '🇵🇭', nhom: 'Đông Nam Á & Bản Địa' },
  { ma: 'km', ten: 'Tiếng Campuchia (Khmer)', co: '🇰🇭', nhom: 'Đông Nam Á & Bản Địa' },
  { ma: 'lo', ten: 'Tiếng Lào (Lao)', co: '🇱🇦', nhom: 'Đông Nam Á & Bản Địa' },
  { ma: 'my', ten: 'Tiếng Myanmar (Burmese)', co: '🇲🇲', nhom: 'Đông Nam Á & Bản Địa' },

  // Nhóm 2: Đông Á
  { ma: 'zh', ten: 'Tiếng Trung (Phổ thông)', co: '🇨🇳', nhom: 'Đông Á' },
  { ma: 'yue', ten: 'Tiếng Trung (Quảng Đông)', co: '🇭🇰', nhom: 'Đông Á' },
  { ma: 'ja', ten: 'Tiếng Nhật (日本語)', co: '🇯🇵', nhom: 'Đông Á' },
  { ma: 'ko', ten: 'Tiếng Hàn (한국어)', co: '🇰🇷', nhom: 'Đông Á' },

  // Nhóm 3: Âu - Mỹ & Toàn Cầu
  { ma: 'en', ten: 'Tiếng Anh (Mỹ - US)', co: '🇺🇸', nhom: 'Âu - Mỹ & Toàn Cầu' },
  { ma: 'en-gb', ten: 'Tiếng Anh (Anh - UK)', co: '🇬🇧', nhom: 'Âu - Mỹ & Toàn Cầu' },
  { ma: 'fr', ten: 'Tiếng Pháp (Français)', co: '🇫🇷', nhom: 'Âu - Mỹ & Toàn Cầu' },
  { ma: 'de', ten: 'Tiếng Đức (Deutsch)', co: '🇩🇪', nhom: 'Âu - Mỹ & Toàn Cầu' },
  { ma: 'es', ten: 'Tiếng Tây Ban Nha (Español)', co: '🇪🇸', nhom: 'Âu - Mỹ & Toàn Cầu' },
  { ma: 'pt', ten: 'Tiếng Bồ Đào Nha (Português)', co: '🇵🇹', nhom: 'Âu - Mỹ & Toàn Cầu' },
  { ma: 'it', ten: 'Tiếng Ý (Italiano)', co: '🇮🇹', nhom: 'Âu - Mỹ & Toàn Cầu' },
  { ma: 'ru', ten: 'Tiếng Nga (Русский)', co: '🇷🇺', nhom: 'Âu - Mỹ & Toàn Cầu' },
  { ma: 'nl', ten: 'Tiếng Hà Lan (Nederlands)', co: '🇳🇱', nhom: 'Âu - Mỹ & Toàn Cầu' },

  // Nhóm 4: Nam Á & Trung Đông
  { ma: 'ar', ten: 'Tiếng Ả Rập (العربية)', co: '🇸🇦', nhom: 'Nam Á & Trung Đông' },
  { ma: 'hi', ten: 'Tiếng Hindi (हिन्दी)', co: '🇮🇳', nhom: 'Nam Á & Trung Đông' },
  { ma: 'bn', ten: 'Tiếng Bengal (বাংলা)', co: '🇧🇩', nhom: 'Nam Á & Trung Đông' },
  { ma: 'ur', ten: 'Tiếng Urdu (اردو)', co: '🇵🇰', nhom: 'Nam Á & Trung Đông' },
  { ma: 'ta', ten: 'Tiếng Tamil (தமிழ்)', co: '🇮🇳', nhom: 'Nam Á & Trung Đông' },
  { ma: 'mr', ten: 'Tiếng Marathi (मराठी)', co: '🇮🇳', nhom: 'Nam Á & Trung Đông' },
  { ma: 'tr', ten: 'Tiếng Thổ Nhĩ Kỳ (Türkçe)', co: '🇹🇷', nhom: 'Nam Á & Trung Đông' },
];

const GIONG_BAN_XU_MAC_DINH = {
  'vi': { nam: 'ngan', nu: 'sach-noi' },
  'en': { nam: 'en-US-GuyNeural', nu: 'en-US-JennyNeural' },
  'en-gb': { nam: 'en-GB-RyanNeural', nu: 'en-GB-SoniaNeural' },
  'en-au': { nam: 'en-AU-WilliamMultilingualNeural', nu: 'en-AU-NatashaNeural' },
  'de': { nam: 'de-DE-ConradNeural', nu: 'de-DE-KatjaNeural' },
  'fr': { nam: 'fr-FR-HenriNeural', nu: 'fr-FR-DeniseNeural' },
  'es': { nam: 'es-ES-AlvaroNeural', nu: 'es-ES-ElviraNeural' },
  'it': { nam: 'it-IT-DiegoNeural', nu: 'it-IT-ElsaNeural' },
  'pt': { nam: 'pt-BR-AntonioNeural', nu: 'pt-BR-FranciscaNeural' },
  'ru': { nam: 'ru-RU-DmitryNeural', nu: 'ru-RU-SvetlanaNeural' },
  'zh': { nam: 'zh-CN-YunxiNeural', nu: 'zh-CN-XiaoxiaoNeural' },
  'yue': { nam: 'zh-HK-WanLungNeural', nu: 'zh-HK-HiuGaaiNeural' },
  'zh-tw': { nam: 'zh-TW-YunJheNeural', nu: 'zh-TW-HsiaoChenNeural' },
  'ja': { nam: 'ja-JP-KeitaNeural', nu: 'ja-JP-NanamiNeural' },
  'ko': { nam: 'ko-KR-InJoonNeural', nu: 'ko-KR-SunHiNeural' },
  'th': { nam: 'th-TH-NiwatNeural', nu: 'th-TH-PremwadeeNeural' },
  'lo': { nam: 'lo-LA-ChanthavongNeural', nu: 'lo-LA-KeomanyNeural' },
  'id': { nam: 'id-ID-ArdiNeural', nu: 'id-ID-GadisNeural' },
  'ms': { nam: 'ms-MY-OsmanNeural', nu: 'ms-MY-YasminNeural' },
  'fil': { nam: 'fil-PH-AngeloNeural', nu: 'fil-PH-BlessicaNeural' },
  'km': { nam: 'km-KH-PisethNeural', nu: 'km-KH-SreymomNeural' },
  'my': { nam: 'my-MM-ThihaNeural', nu: 'my-MM-NilarNeural' },
  'nl': { nam: 'nl-NL-MaartenNeural', nu: 'nl-NL-FennaNeural' },
  'ar': { nam: 'ar-SA-HamedNeural', nu: 'ar-SA-ZariyahNeural' },
  'hi': { nam: 'hi-IN-MadhurNeural', nu: 'hi-IN-SwaraNeural' },
  'tr': { nam: 'tr-TR-AhmetNeural', nu: 'tr-TR-EmelNeural' }
};

function doanGioiTinhGiong(giongMa) {
  if (!giongMa) return 'nam';
  const g = GIONG.find(x => (x.id || x.ma) === giongMa || x.ten === giongMa);
  if (g) {
    if (g.gioi) {
      const gStr = String(g.gioi).toLowerCase();
      if (gStr.includes('nữ') || gStr.includes('nu') || gStr.includes('female')) return 'nu';
      if (gStr.includes('nam') || gStr.includes('male')) return 'nam';
    }
    const ten = (g.ten || '') + ' ' + (g.moTa || '') + ' ' + (g.ma || '') + ' ' + (g.id || '');
    const tenNorm = ten.toLowerCase().normalize('NFD').replace(/[\u0300-\u036f]/g, '');
    if (['nu', 'linh', 'ly', 'trang', 'dung', 'thao', 'huyen', 'jenny', 'sonia', 'katja', 'denise', 'xiaoxiao', 'nanami', 'sunhi', 'gadis', 'premwadee', 'keomany', 'sach noi'].some(k => tenNorm.includes(k))) {
      return 'nu';
    }
  }
  return 'nam';
}

// ---------------------------------------------------------------- cột phải

function veCotPhai() {
  const h = hoSoDangDung(S);
  const tgtLang = h.ngonNgu || 'vi';
  let g = GIONG.find((x) => (x.id || x.ma) === h.giong || x.ten === h.giong);
  if (!g && GIONG.length) {
    g = GIONG[0];
  }
  const chuY = chuYDangXem(S, TAI_LIEU);
  const dangTai = S.situation === 'giong_dang_tai';
  const srcLang = h.ngonNguNguon || 'auto';
  const phatHien = S.ngonNguPhatHien || 'vi';
  const objPhatHien = DS_NGON_NGU.find((l) => l.ma === phatHien) || { co: '🇻🇳', ten: 'Tiếng Việt' };
  const thucTeNguon = srcLang === 'auto' ? phatHien : srcLang;
  const dangDich = thucTeNguon !== tgtLang;

  return `<div class="phai">
    <div class="the">
      <div class="the__phan">
        <div class="the__nhan">Hồ sơ đang dùng</div>
        <div class="c-nhan" style="margin-top:4px">${esc(h.ten)}</div>
      </div>
      <div class="the__ngan"></div>
      <div class="the__phan">
        <div class="the__nhan" style="display:flex;align-items:center;justify-content:space-between;white-space:nowrap">
          <span>Ngôn ngữ & Dịch</span>
          ${dangDich ? '<span class="vanbanghep__badge" style="font-size:10px;padding:2px 6px;background:rgba(0,103,192,.12);color:var(--acc);border-radius:4px;font-weight:600" title="Tự động dịch sang ngôn ngữ đích khi đọc">🌐 Lồng tiếng</span>' : '<span style="font-size:10.5px;color:var(--txt3)">Bản gốc</span>'}
        </div>

        <div style="margin-top:8px">
          <div style="font-size:11.5px;color:var(--txt3);margin-bottom:3px;display:flex;justify-content:space-between;align-items:center">
            <span>Ngôn ngữ nguồn:</span>
            ${srcLang === 'auto' ? `<span style="color:var(--acc);font-weight:600;font-size:11px">${objPhatHien.co} ${objPhatHien.ten.replace(' (Gốc)', '').split(' (')[0]}</span>` : ''}
          </div>
          <select class="chon" id="oNgonNguNguon" style="width:100%">
            <option value="auto"${srcLang === 'auto' ? ' selected' : ''}>🌐 Tự động (${objPhatHien.co} ${objPhatHien.ten.replace(' (Gốc)', '').split(' (')[0]})</option>
            ${['Đông Nam Á & Bản Địa', 'Đông Á', 'Âu - Mỹ & Toàn Cầu', 'Nam Á & Trung Đông'].map(nhom => `
              <optgroup label="${nhom}">
                ${DS_NGON_NGU.filter(x => x.nhom === nhom).map(l => `<option value="${l.ma}"${srcLang === l.ma ? ' selected' : ''}>${l.co} ${l.ten}</option>`).join('')}
              </optgroup>
            `).join('')}
          </select>
        </div>

        <div style="margin-top:8px">
          <div style="font-size:11.5px;color:var(--txt3);margin-bottom:3px">Ngôn ngữ đích (Đọc / Xuất):</div>
          <div style="display:flex;align-items:center;gap:6px">
            <select class="chon" id="oNgonNgu" style="flex:1;min-width:0">
              ${['Đông Nam Á & Bản Địa', 'Đông Á', 'Âu - Mỹ & Toàn Cầu', 'Nam Á & Trung Đông'].map(nhom => `
                <optgroup label="${nhom}">
                  ${DS_NGON_NGU.filter(x => x.nhom === nhom).map(l => `<option value="${l.ma}"${tgtLang === l.ma ? ' selected' : ''}>${l.co} ${l.ten}</option>`).join('')}
                </optgroup>
              `).join('')}
            </select>
            <button class="nut nut--vien" id="btnHoanDoiLang" title="Hoán đổi nguồn ⇄ đích" style="flex:none;padding:0 8px;height:32px;font-size:14px">⇄</button>
          </div>
        </div>
      </div>
      <div class="the__ngan"></div>
      <div class="the__phan">
        <div class="the__nhan">Giọng đọc</div>
        <div class="giong-hang">
          <button class="chon" id="oGiong"
                  title="${esc(g ? g.ten + (g.ngan ? ' — ' + g.ngan : '') : '')}">
            ${ic('micro')}<span class="chon__gt">${esc(g ? g.ten : '')}</span>
            <span class="chon__mui">${ic('mui', 13)}</span></button>
          <button class="nut nut--nghemau${S.mauDangPhat ? ' nut--dang' : ' nut--acc-soft'}" id="ngheMau"
                  title="${S.mauDangPhat ? 'Đang đọc thử — bấm để dừng (Ctrl+M)'
                                         : 'Nghe mẫu giọng (Ctrl+M)'}"
                  >${ic(S.mauDangPhat ? 'dunghan' : 'loa', 15)}<span>${S.mauDangPhat ? 'Dừng' : 'Thử'}</span></button>
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

const CAI_DAT_SAN_PHO_BIEN = [
  {
    ma: 'tu_nhien',
    ten: '🌟 Tự nhiên',
    moTa: 'Cân bằng, đọc báo, văn bản thường nhật (Tốc độ 0%, Cao độ 0)',
    chinh: { tocDo: 0, caoDo: 0, amLuong: 100 },
    phongCach: 'Tự nhiên'
  },
  {
    ma: 'tin_tuc',
    ten: '📢 Tin tức',
    moTa: 'Dứt khoát, hào sảng, thông báo (Tốc độ +10%, Cao độ +1)',
    chinh: { tocDo: 10, caoDo: 1, amLuong: 100 },
    phongCach: 'Tin tức - thông báo'
  },
  {
    ma: 'sach_noi',
    ten: '📖 Sách nói',
    moTa: 'Trầm ấm, ngắt nghỉ sâu, diễn cảm (Tốc độ -5%, Cao độ -1)',
    chinh: { tocDo: -5, caoDo: -1, amLuong: 100 },
    phongCach: 'Kể chuyện'
  },
  {
    ma: 'tam_su',
    ten: '☕ Tâm sự',
    moTa: 'Êm dịu, nhẹ nhàng, sâu lắng (Tốc độ -10%, Cao độ -2)',
    chinh: { tocDo: -10, caoDo: -2, amLuong: 90 },
    phongCach: 'Kể chuyện'
  },
  {
    ma: 'nghe_nhanh',
    ten: '⚡ Nghe nhanh',
    moTa: 'Tốc độ cao, tiết kiệm thời gian (Tốc độ +35%, Cao độ 0)',
    chinh: { tocDo: 35, caoDo: 0, amLuong: 100 },
    phongCach: 'Tự nhiên'
  }
];

const TRUOT = [
  ['tocDo', 'Tốc độ', -50, 100, (v) => (v > 0 ? '+' : v < 0 ? '−' : '') + Math.abs(v) + '%'],
  ['caoDo', 'Cao độ', -12, 12, (v) => (v > 0 ? '+' : v < 0 ? '−' : '') + Math.abs(v)],
  ['amLuong', 'Âm lượng', 0, 100, (v) => v + '%'],
];

const veThanhChinh = (h) => {
  const cur = (h && h.chinh) || { tocDo: 0, caoDo: 0, amLuong: 100 };
  const curStyle = (h && h.phongCach) || 'Tự nhiên';

  return `
    <div style="margin-bottom:14px;padding-bottom:12px;border-bottom:1px solid var(--stroke2)">
      <div style="font-size:11px;font-weight:700;color:var(--txt2);text-transform:uppercase;letter-spacing:0.5px;margin-bottom:8px">Cài đặt sẵn phổ biến</div>
      <div style="display:flex;flex-wrap:wrap;gap:6px">
        ${CAI_DAT_SAN_PHO_BIEN.map((p) => {
          const khop = p.chinh.tocDo === cur.tocDo && p.chinh.caoDo === cur.caoDo && p.chinh.amLuong === cur.amLuong && (p.phongCach === curStyle);
          return `<button class="soat__chip${khop ? ' mo' : ''}" data-cdsan="${p.ma}" title="${p.moTa}" style="padding:4px 8px;font-size:12px;border-radius:4px;cursor:pointer">
            ${p.ten}
          </button>`;
        }).join('')}
      </div>
    </div>
    
    <div style="font-size:11px;font-weight:700;color:var(--txt2);text-transform:uppercase;letter-spacing:0.5px;margin-bottom:8px">Tự điều chỉnh chi tiết</div>
    ${TRUOT.map(([khoa, ten, min, max, hien]) => {
      const v = cur[khoa] !== undefined ? cur[khoa] : (khoa === 'amLuong' ? 100 : 0);
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
    
    <div style="margin-top:16px; margin-bottom:8px;">
      <div style="font-size:11px;font-weight:700;color:var(--txt2);text-transform:uppercase;letter-spacing:0.5px;margin-bottom:6px">Không gian âm học</div>
      <select id="oKhongGian" class="giongkho__tim" style="width:100%; height:32px; padding:0 8px;" data-doikhonggian="1">
        <option value="" ${!cur.khongGian ? 'selected' : ''}>Mặc định (Nguyên bản)</option>
        <option value="podcast" ${cur.khongGian === 'podcast' ? 'selected' : ''}>Studio / Podcast</option>
        <option value="hoitruong" ${cur.khongGian === 'hoitruong' ? 'selected' : ''}>Hội trường / Nhà thờ</option>
        <option value="radio" ${cur.khongGian === 'radio' ? 'selected' : ''}>Radio FM</option>
        <option value="loaphuong" ${cur.khongGian === 'loaphuong' ? 'selected' : ''}>Loa phường (Vintage)</option>
      </select>
    </div>

    <button class="nut nut--vien" style="width:100%;margin-top:12px" data-lenh="Đặt lại mặc định">
      Đặt lại mặc định</button>`;
};

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
  const hoso = hoSoDangDung(S);
  const dung = hoso.giong;
  const nn = (hoso.ngonNgu || 'vi').toLowerCase();

  // Lọc giọng:
  // 1. Giọng của tôi (rieng = true): LUÔN LUÔN hiển thị ở mọi ngôn ngữ (hỗ trợ đọc 28+ thứ tiếng).
  // 2. Giọng chuẩn / dựng sẵn: CHỈ hiển thị giọng thuộc đúng ngôn ngữ đích tương ứng.
  let ds = GIONG.filter((g) => {
    if (g.rieng) return true;
    const gnn = (g.ngonNgu || g.ngon_ngu || 'vi').toLowerCase();
    const gId = (g.id || g.ma || '').toLowerCase();
    const gVung = (g.vung || '').toLowerCase();

    if (nn === 'vi') {
      return gnn === 'vi' || !gnn;
    }
    if (nn === 'en') {
      return gnn === 'en' || gVung.includes('us') || gVung.includes('mỹ') || gId.startsWith('en-us');
    }
    if (nn === 'en-gb') {
      return gnn === 'en-gb' || gVung.includes('uk') || gVung.includes('anh') || gId.startsWith('en-gb');
    }
    if (nn === 'en-au') {
      return gnn === 'en-au' || gVung.includes('au') || gVung.includes('úc') || gId.startsWith('en-au');
    }
    if (nn === 'zh') {
      return gnn === 'zh' || gId.startsWith('zh-cn');
    }
    if (nn === 'yue') {
      return gnn === 'yue' || gId.startsWith('zh-hk');
    }
    if (nn === 'zh-tw') {
      return gnn === 'zh-tw' || gId.startsWith('zh-tw');
    }
    return gnn === nn || gId.startsWith(`${nn}-`);
  });

  // Nếu danh sách lọc bị rỗng (ví dụ ngôn ngữ hiếm), fallback lấy giọng mặc định của ngôn ngữ đó
  if (!ds.length) {
    const dMap = GIONG_BAN_XU_MAC_DINH[nn] || GIONG_BAN_XU_MAC_DINH[nn.split('-')[0]];
    if (dMap) {
      const gFallback = GIONG.filter(g => (g.id || g.ma) === dMap.nam || (g.id || g.ma) === dMap.nu);
      ds.push(...gFallback);
    }
  }

  // Đảm bảo nếu giọng đang chọn hợp lệ với ngôn ngữ này thì được ưu tiên hiển thị
  if (dung && !ds.find(g => (g.id || g.ma) === dung)) {
    const gd = GIONG.find(g => (g.id || g.ma) === dung);
    if (gd && (gd.rieng || (gd.ngonNgu || 'vi').toLowerCase() === nn)) {
      ds.unshift(gd);
    }
  }

  const nhom = (rieng) => ds.filter((g) => Boolean(g.rieng) === rieng).sort(xepGiong).map((g) => {
    const ma = g.id || g.ma;
    const dangNghe = S.dangNgheThu === ma;
    const moTa = g.ngan || g.moTa || g.mo_ta || '';
    return `
    <button class="roi__muc roi__muc--hai" data-giong="${ma}"
            title="${esc(g.ten)}${moTa ? ' — ' + esc(moTa) : ''}">
      <span class="roi__tich">${ma === dung ? ic('tich', 14) : ''}</span>
      <span class="roi__than">
        <span class="roi__ten">${esc(g.ten)}</span>
        ${moTa ? `<span class="roi__phu">${esc(moTa)}</span>` : ''}
      </span>
      <span class="roi__nghe${dangNghe ? ' roi__nghe--dang' : ''}"
            data-nghegiong="${ma}"
            title="${dangNghe ? 'Đang đọc thử — bấm để dừng' : 'Nghe thử giọng này'}"
            >${ic(dangNghe ? 'dunghan' : 'tamgiac', 11)}</span>
    </button>`;
  }).join('');

  const cuaToi = nhom(true);
  const coSan = nhom(false);
  const langObj = (typeof DS_NGON_NGU !== 'undefined' ? DS_NGON_NGU : []).find((x) => x.ma === nn) || { co: '🌐', ten: nn };
  const tieuDeCoSan = nn === 'vi' ? 'Giọng có sẵn (Tiếng Việt)' : `${langObj.co || '🌐'} Giọng bản xứ ${langObj.ten || nn}`;

  return `<div class="roi roi--giong" style="position:absolute;z-index:60;margin-top:4px;max-height:420px;overflow-y:auto;box-shadow:0 10px 30px rgba(0,0,0,0.18);border-radius:8px">
    ${coSan ? `<div class="roi__nhom">${esc(tieuDeCoSan)}</div>${coSan}` : ''}
    ${cuaToi ? `<div class="roi__nhom">🎙️ Giọng của tôi (Nhân bản)</div>${cuaToi}` : ''}
    <div class="roi__ngan"></div>
    <button class="roi__muc" data-lenh="Nhân bản giọng từ file…">
      <span class="roi__tich">${ic('cong', 13)}</span>
      <span class="roi__ten" style="color:var(--acc)">Nhân bản giọng từ file…</span>
    </button>
  </div>`;
}

// ---------------------------------------------------------------- phụ đề song ngữ


function vePhuDeSongNgu(S, h) {
  if (S.view !== 'dang_doc' || !h || !h.ngonNgu || h.ngonNgu === 'vi') return '';
  if (S.anPhuDe) return '';

  const doan = doanDangXem(S, TAI_LIEU);
  const curD = doan[S.pos - 1];
  const chuGoc = S.cauGocHienTai || (curD ? (curD.chu || '') : '');
  const chuDich = S.cauDocHienTai || 'Đang chuẩn bị bản dịch và âm thanh…';

  const langObj = (typeof DS_NGON_NGU !== 'undefined' ? DS_NGON_NGU : []).find((x) => x.ma === h.ngonNgu) || { co: '🌐', ten: h.ngonNgu };

  // Chia bản dịch thành từng từ để chạy karaoke bám sát giọng đọc
  const wordsDich = (chuDich || '').split(/\s+/).filter(Boolean);
  const chuDichHtml = wordsDich.map((w, idx) => {
    const b = idx / wordsDich.length;
    const e = (idx + 1) / wordsDich.length;
    return `<span class="tu-dich" data-b="${b}" data-e="${e}">${esc(w)}</span>`;
  }).join(' ');

  return `
    <div class="phude-songngu" id="phuDeSongNgu">
      <div class="phude-songngu__dau">
        <div class="phude-songngu__nhan">
          <span class="phude-songngu__dot"></span>
          <span>🌐 Phụ đề song ngữ: 🇻🇳 Tiếng Việt ➔ ${langObj.co} ${esc(langObj.ten)}</span>
        </div>
        <div class="phude-songngu__nut-nhom">
          <button class="phude-songngu__nut" data-lenh="Thu gọn phụ đề" title="Thu gọn / Mở rộng">${S.phuDeThuGon ? '▲ Mở rộng' : '▼ Thu gọn'}</button>
          <button class="phude-songngu__nut phude-songngu__nut--dong" data-lenh="Ẩn phụ đề" title="Tắt khung phụ đề">✕</button>
        </div>
      </div>
      ${!S.phuDeThuGon ? `
        <div class="phude-songngu__than">
          <div class="phude-songngu__goc" title="Văn bản gốc đoạn ${S.pos}">
            <span class="phude-songngu__tag">Gốc (Đoạn ${S.pos})</span> ${esc(chuGoc)}
          </div>
          <div class="phude-songngu__dich" title="Bản dịch đang phát âm">
            <span class="phude-songngu__tag phude-songngu__tag--dich">${langObj.co} Đang đọc</span>
            <span class="phude-songngu__chu-dich">${chuDichHtml}</span>
          </div>
        </div>
      ` : ''}
    </div>
  `;
}

// ---------------------------------------------------------------- thanh phát

function veThanhPhat() {
  if (S.dangChuanBiDich) {
    return `<div class="phat">
      <span class="xoay xoay--to"></span>
      <span class="phat__dong">${esc(S.thongBaoDich || 'Đang chuẩn bị bản dịch sang ngôn ngữ đích…')}</span>
      <span class="phat__ghi">Tự động dịch song song siêu tốc…</span>
    </div>`;
  }
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
  const h = hoSoDangDung(S);
  const coPhuDe = h && h.ngonNgu && h.ngonNgu !== 'vi';

  return `<div class="phat">
    <button class="nut phat__nut phat__nut--acc" data-lenh="Tạm dừng">${ic('tamdung', 15)}</button>
    <button class="nut phat__nut" data-lenh="Dừng">${ic('dunghan', 13)}</button>
    <span class="phat__dong" id="phatDong">${S.mode === 'one'
      ? `Đang nghe riêng đoạn ${S.pos}` : `Đang đọc đoạn ${S.pos}/${doan.length}`}</span>
    <span class="phat__gio" id="phatGio">${dongHo(daNghe)} / ${dongHo(tong)}</span>
    <span class="phat__tien"><i id="phatTien" style="width:${pct}%"></i></span>
    <span class="phat__ghi">${S.mode === 'one'
      ? 'Nghe hết đoạn này sẽ dừng' : 'Đang chuẩn bị đoạn tiếp theo…'}</span>
    ${coPhuDe ? `<button class="nut nut--vien" data-lenh="Chuyển phụ đề" style="flex:none;height:28px;padding:0 9px;font-size:11.5px;margin-left:auto;display:flex;align-items:center;gap:4px;border-color:${!S.anPhuDe ? 'var(--acc)' : 'var(--stroke2)'};color:${!S.anPhuDe ? 'var(--acc)' : 'var(--txt3)'}" title="${!S.anPhuDe ? 'Đang hiển thị phụ đề song ngữ (Bấm để ẩn)' : 'Bấm để hiển thị khung phụ đề song ngữ'}">
      🌐 <span>${!S.anPhuDe ? 'Phụ đề: Bật' : 'Phụ đề: Tắt'}</span>
    </button>` : ''}
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

function thongKeTaiLieu(S, TAI_LIEU) {
  const doan = doanDangXem(S, TAI_LIEU) || [];
  const dsThuc = doan.filter((d) => d && d.kieu !== 'blank' && String(d.chu || '').trim());
  let tongTu = 0;
  dsThuc.forEach((d) => {
    const tu = String(d.chu || '').trim().split(/\s+/).filter(Boolean).length;
    tongTu += tu;
  });
  const h = hoSoDangDung(S);
  const heSo = Math.max(0.5, Math.min(2.0, (100 + (h.tocDo || 0)) / 100));
  const giayUocTinh = Math.round((tongTu / (145 * heSo)) * 60);
  const phut = Math.floor(giayUocTinh / 60);
  const giay = giayUocTinh % 60;
  const thoiLuongStr = tongTu > 0
    ? (phut > 0 ? `${phut}p ${giay.toString().padStart(2, '0')}s` : `${giay}s`)
    : '0s';
  return { tongDoan: dsThuc.length, tongTu, thoiLuongStr };
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
  const tk = thongKeTaiLieu(S, TAI_LIEU);
  const ttSoStr = tk.tongTu > 0
    ? `Đoạn ${soDoan}/${tk.tongDoan} · ${tk.tongTu.toLocaleString('vi-VN')} từ (~${tk.thoiLuongStr})`
    : `Đoạn ${soDoan}, Cột 1`;

  return `<div class="trangthai">
    <span class="trangthai__so" id="ttSo">${esc(ttSoStr)}</span>
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
  giong:      { ten: 'Thư viện giọng',   dong: 'Đóng giọng' },
  tudien:     { ten: 'Từ điển phát âm',  dong: 'Đóng từ điển' },
  caidat:     { ten: 'Cài đặt',          dong: 'Đóng cài đặt' },
  vanbanghep: { ten: 'Văn bản ghép',     dong: 'Đóng văn bản ghép' },
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
  /* MỌI khung cuộn phải giữ chỗ, không riêng vùng đọc. ve() dựng lại toàn bộ
     HTML nên khung nào cũng bị kéo về đầu; trước đây chỉ #cuon được trả lại.
     Từ khi danh sách tệp vào cột trái thì .trai__ds mới có thứ để cuộn, và cột
     phải, dropdown giọng, bảng soát, màn cài đặt, kho giọng đều đã có sẵn.

     Hậu quả với người lớn tuổi: cuộn xuống tìm một công tắc, bấm vào, màn hình
     nhảy phắt về đầu, phải cuộn lại từ đầu cho MỖI lần bấm. */
  /* Man Van ban ghep ra sau dot va "tam khung cuon deu giu cho", nen ba khung
     cua no lot luoi. Dang ke nhat: napDuLieuVBGTuDong() tu goi ve() moi 5 phut
     khi dang o man nay - nguoi dung cuon xuong giua bang khop cot, 5 phut sau
     man hinh tu nhay ve dau ma khong ai dong vao. */
  const KHUNG_CUON = ['#cuon', '.trai__ds', '.phai', '.roi--giong',
                      '.soat__bang', '.caidat', '.giongkho__than', '.tin',
                      '.vanbanghep__than', '.vanbanghep__preview-than',
                      '.vanbanghep__khoi-chu'];
  /* querySelectorAll chu khong phai $(): .vanbanghep__khoi-chu co BON o
     (dau danh sach / danh sach / xen giua / cuoi), moi o max-height 160px
     va cuon rieng. Dung $() thi chi o dau tien duoc giu cho, ba o kia van
     nhay ve dau moi lan ve lai. */
  const cuonCu = KHUNG_CUON.map((s) =>
    [s, Array.from(document.querySelectorAll(s)).map((o) => o.scrollTop)]);
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
    ${veTrangThai()}`;

  if ($('#oTim')) $('#oTim').focus();
  /* Trả tiêu điểm về ô tên tệp sau mỗi lần dựng lại HTML, kèm đúng vị trí con
     trỏ. Thiếu đoạn này thì người dùng đang gõ tên mà máy sang đoạn đọc mới là
     mất tiêu điểm — gõ tiếp thì chữ rơi vào hư không. Đặt SAU nhánh #oTim vì ô
     tên mở ra sau và cụ thể hơn. */
  if (suaTenTep) {
    const oTen = $('#oTenTep');
    if (oTen && oTen.focus) {
      oTen.focus();
      if (oTen.setSelectionRange) oTen.setSelectionRange(viTriTenDangGo, viTriTenDangGo);
    }
  }
  ganLaiCache();
  veLopNoi();
  veBangThu();
  /* Trả chỗ cuộn SAU veLopNoi(): .tin nằm trong lớp nổi mà veLopNoi() mới dựng
     ra, trả trước là trả vào một phần tử sắp bị thay. Trình duyệt tự kẹp về mức
     lớn nhất khi nội dung ngắn đi, nên không phải tự tính. */
  cuonCu.forEach(([s, ds]) => {
    const os = document.querySelectorAll(s);
    ds.forEach((v, i) => { if (os[i] && v) os[i].scrollTop = v; });
  });
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
let _vbgDangNap = false;
let _vbgLanNapCuoi = 0;
let _vbgNguonDaNap = '';

/* ---- Ghép danh sách: dùng chung cho đường "Áp dụng" và đường đồng bộ ngầm ----

   Ba công tắc ở mục "Lọc & nhóm" trước đây chỉ SÁNG LÊN chứ không làm gì:
   `cur.rule` chỉ được lật giá trị rồi vẽ trạng thái, không một dòng nào áp nó
   vào dữ liệu. Người dùng bật "Bỏ dòng thiếu", chữ đổi thành "Đang lọc", mà
   danh sách vẫn nguyên si — đúng thứ KPI dự án cấm. `rule.dupCol` và
   `rule.group` thì không ai đọc lần nào. */

const _oCuaDongVBG = (cur, r, c) => {
  const cIdx = cur.cols.indexOf(c);
  const v = r && (r[c.letter] != null ? r[c.letter] : (Array.isArray(r) ? r[cIdx] : ''));
  return String(v == null ? '' : v).trim();
};

function locDongTheoQuyTacVBG(cur) {
  let ds = (cur.rows && cur.rows.length) ? cur.rows.slice() : [];
  if (!ds.length || !cur.cols) return ds;
  const quy = cur.rule || {};

  /* "Bỏ dòng thiếu" hiểu HẸP: chỉ bỏ dòng mà MỌI ô có biến đều rỗng. Ở buổi lễ,
     bỏ sót một người chỉ vì họ không ghi địa chỉ là chuyện lớn hơn nhiều so với
     một câu hơi cụt — mà câu cụt thì đã được dọn ở lanVaoDoanGhepVBG. */
  if (quy.trong) {
    const cotCoBien = cur.cols.filter(c => c.varName);
    if (cotCoBien.length) {
      ds = ds.filter(r => cotCoBien.some(c => _oCuaDongVBG(cur, r, c) !== ''));
    }
  }

  // "Gộp trùng": giữ lần xuất hiện đầu, so theo cột đã chọn (mặc định cột A).
  if (quy.trung) {
    const cotTrung = cur.cols.find(c => c.letter === (quy.dupCol || 'A')) || cur.cols[0];
    if (cotTrung) {
      const daCo = new Set();
      ds = ds.filter(r => {
        const k = _oCuaDongVBG(cur, r, cotTrung).toLowerCase();
        if (!k) return true;
        if (daCo.has(k)) return false;
        daCo.add(k);
        return true;
      });
    }
  }

  // "Thứ tự": bật = giữ nguyên thứ tự bảng tính; tắt = xếp theo cột đầu.
  if (quy.thutu === false && cur.cols.length) {
    const cot0 = cur.cols[0];
    ds = ds.slice().sort((a, b) =>
      _oCuaDongVBG(cur, a, cot0).localeCompare(_oCuaDongVBG(cur, b, cot0), 'vi'));
  }
  return ds;
}

function ghepMotCauVBG(cur, r) {
  let cau = (cur.T && cur.T.mau) || '';
  cur.cols.forEach((c) => {
    const val = _oCuaDongVBG(cur, r, c);
    if (c.varName && val !== '') cau = cau.split(c.varName).join(val);
  });
  /* Ô trống để lại câu què, và máy đọc to nguyên câu ấy:
       "Xin tán thán Trần Thị Bích, ở, đã công đức 1.200.000 đồng."
     Ô địa chỉ hay pháp danh bỏ trống là chuyện rất thường trong danh sách
     công đức. */
  /* `\b` của JavaScript chỉ biết chữ cái ASCII, nên `\b(ở|tại|…)` KHÔNG khớp
     được từ tiếng Việt có dấu — dùng (^|\s) mới bắt đúng. Đã đo: thiếu chỗ này
     thì "ở," vẫn nằm nguyên trong câu. */
  return cau
    // 1. bỏ biến không có cột nào cấp giá trị
    .replace(/\{[a-z0-9]+\}/gi, '')
    // 2. bỏ giới từ bị bỏ rơi ngay trước dấu câu ("… , ở , …")
    .replace(/(^|\s)(ở|tại|của|cho|với|từ|đến|thuộc|là)\s*(?=[,.;:])/gi, '$1')
    // 3. dồn dấu câu trùng — phải chạy SAU bước 2, vì chính bước 2 sinh ra chúng
    .replace(/\s+([.,;:])/g, '$1')
    .replace(/([,;:])[\s,;:]*(?=[,.;:])/g, '')
    .replace(/[,;:\s]+\./g, '.')
    // 4. dọn khoảng trắng và dấu câu thừa ở hai đầu
    .replace(/\s{2,}/g, ' ')
    .replace(/^[\s,;:]+/, '')
    .trim();
}

function lanVaoDoanGhepVBG(doanGhep, cur, dsDong) {
  const every = parseInt(cur.sauMoi || '20', 10) || 20;
  dsDong.forEach((r, idx) => {
    doanGhep.push(`${idx + 1}. ${ghepMotCauVBG(cur, r)}`);
    const giua = cur.on && cur.on.giua && cur.T && cur.T.giua && cur.T.giua.trim();
    if (giua && every > 0 && (idx + 1) % every === 0 && (idx + 1) < dsDong.length) {
      doanGhep.push(cur.T.giua.trim());
    }
  });
  return doanGhep;
}

async function napDuLieuVBGTuDong(force = false) {
  if (typeof duLieuVBG === 'undefined') return;
  const cur = duLieuVBG.maus && (duLieuVBG.maus[duLieuVBG.mauHienTai] || duLieuVBG.maus[0]);
  if (!cur || !cur.srcVal) return;
  
  const key = `${cur.srcType}|${cur.srcVal}|${cur.sheet || ''}|${cur.headRow || 'Dòng 1'}`;
  const now = Date.now();
  
  if (!force && _vbgNguonDaNap === key && (now - _vbgLanNapCuoi) < 300000) return;
  if (_vbgDangNap) return;
  if (!coPython()) return;
  
  _vbgDangNap = true;
  try {
    const kq = await api('moi_tai_bang_tinh', cur.srcVal, cur.srcType, cur.sheet || '', cur.headRow || 'Dòng 1');
    if (kq && kq.thanhCong) {
      if (kq.rows && kq.rows.length > 0) {
        cur.cols = kq.cols;
        cur.rows = kq.rows;
      cur.daTaiThat = true;   /* hết là dữ liệu mẫu — chấm trạng thái dựa vào cờ này */
        cur.tongSo = kq.tongSo;
      }
      if (kq.currentSheet) cur.sheet = kq.currentSheet;
      if (kq.sheets && kq.sheets.length > 0) {
        const mergedSheets = [...kq.sheets];
        if (typeof DANH_SACH_SHEET_MAU !== 'undefined') {
          DANH_SACH_SHEET_MAU.forEach(s => {
            if (!mergedSheets.includes(s)) mergedSheets.push(s);
          });
        }
        cur.sheetOpts = mergedSheets;
      }
      cur.isSingleSheet = !!kq.isSingleSheet;
      if (kq.headRow) cur.headRow = kq.headRow;
      _vbgLanNapCuoi = Date.now();
      _vbgNguonDaNap = `${cur.srcType}|${cur.srcVal}|${cur.sheet || ''}|${cur.headRow || 'Dòng 1'}`;
      
      // BẢO VỆ BỘ GÕ TIẾNG VIỆT (IME/Unikey/EVKey):
      // Tuyệt đối KHÔNG gọi ve() phá DOM khi người dùng đang đặt con trỏ / gõ phím
      const activeEl = document.activeElement;
      const dangGo = activeEl && (activeEl.tagName === 'TEXTAREA' || activeEl.tagName === 'INPUT');
      if (!dangGo && S.man === 'vanbanghep') {
        ve();
      } else {
        const previewEl = document.querySelector('.vanbanghep__phai');
        if (previewEl && typeof vePreviewGhep === 'function') {
          previewEl.innerHTML = vePreviewGhep(cur);
        }
      }
    }
  } catch (err) {
    console.error('Lỗi nạp bảng tính VBG:', err);
    /* Chạy nền mỗi 5 phút thì im lặng là đúng — không quấy người dùng vì một
       lần mất mạng thoáng qua. Nhưng khi họ CHỦ ĐỘNG bấm (force) mà hỏng thì
       phải nói: bản trước chỉ ghi console, người dùng bấm xong thấy màn hình y
       nguyên dữ liệu cũ và không hiểu vì sao. */
    if (force) {
      moBao('Không tải được dữ liệu. Kiểm tra đường mạng hoặc quyền xem của bảng tính.');
    }
  } finally {
    _vbgDangNap = false;
  }
}

setInterval(() => {
  if (typeof duLieuVBG !== 'undefined') {
    const cur = duLieuVBG.maus && (duLieuVBG.maus[duLieuVBG.mauHienTai] || duLieuVBG.maus[0]);
    const activeEl = document.activeElement;
    const dangGo = activeEl && (activeEl.tagName === 'TEXTAREA' || activeEl.tagName === 'INPUT');
    if (!dangGo && cur && cur.autoSync && (Date.now() - _vbgLanNapCuoi) >= 300000) {
      napDuLieuVBGTuDong(true);
    }
  }
}, 30000);

async function dongBoDuLieuLive(btn) {
  if (!coPython()) return moBao('Tính năng đồng bộ cần chạy trên GiongViet.');
  if (typeof duLieuVBG === 'undefined') return moBao('Chưa có cấu hình văn bản ghép.');
  const cur = duLieuVBG.maus && (duLieuVBG.maus[duLieuVBG.mauHienTai] || duLieuVBG.maus[0]);
  if (!cur || !cur.srcVal) return moBao('Chưa cấu hình liên kết bảng tính. Vui lòng mở "Văn bản ghép" để cài đặt.');

  const oldHtml = btn ? btn.innerHTML : '';
  if (btn) {
    btn.disabled = true;
    btn.innerHTML = `<span class="vong-xoay" style="width:13px;height:13px;border:2px solid var(--acc);border-top-color:transparent;border-radius:50%;display:inline-block;animation:xoay 0.8s linear infinite;vertical-align:middle;margin-right:4px"></span><span>Đang đồng bộ…</span>`;
  }

  try {
    const kq = await api('moi_tai_bang_tinh', cur.srcVal, cur.srcType, cur.sheet || '', cur.headRow || 'Dòng 1');
    if (kq && kq.loi) {
      if (btn) {
        btn.disabled = false;
        btn.innerHTML = `✕ Thất bại`;
        setTimeout(() => { if (btn) { btn.disabled = false; btn.innerHTML = oldHtml; } }, 2500);
      }
      return moBao(`Lỗi đồng bộ: ${kq.loi}`);
    }

    if (kq && kq.thanhCong) {
      cur.cols = kq.cols;
      cur.rows = kq.rows;
      cur.daTaiThat = true;   /* hết là dữ liệu mẫu — chấm trạng thái dựa vào cờ này */
      cur.tongSo = kq.tongSo;
      cur.sheet = kq.currentSheet;
      if (kq.sheets) cur.sheetOpts = kq.sheets;

      const doanGhep = [];
      if (cur.on && cur.on.dau && cur.T && cur.T.dau && cur.T.dau.trim()) {
        cur.T.dau.trim().split(/\n+/).forEach(s => { if (s.trim()) doanGhep.push(s.trim()); });
      }

      // Dùng CHUNG một hàm với đường "Áp dụng" bên dưới. Trước đây hai nơi chép
      // lại cùng một đoạn ghép, nên vá một bên là bên kia vẫn hỏng.
      const rowsToProcess = locDongTheoQuyTacVBG(cur);
      lanVaoDoanGhepVBG(doanGhep, cur, rowsToProcess);

      if (cur.on && cur.on.cuoi && cur.T && cur.T.cuoi && cur.T.cuoi.trim()) {
        cur.T.cuoi.trim().split(/\n+/).forEach(s => { if (s.trim()) doanGhep.push(s.trim()); });
      }

      const ten = tenTepDangXem(S) || (cur.name + ' (Ghép).txt');
      const textDoc = doanGhep.join('\n\n');
      TAI_LIEU[ten] = {
        doan: doanGhep.map(chu => ({ chu, goc: chu })),
        doc: textDoc
      };
      danhDauSua();

      const dangDoc = S.view === 'dang_doc';
      const giuPos = (dangDoc || S.view === 'tam_dung') && S.pos > 0 ? S.pos : 1;

      henLuuHoSo();
      api('moi_luu_van_ban', ten, textDoc).then((res) => {
        if (res && res.duongDan) {
          S = { ...S, duongDanTep: { ...(S.duongDanTep || {}), [ten]: res.duongDan } };
          henLuuHoSo();
        }
      });

      const doanGui = doanDangXem(S, TAI_LIEU).map((d, i) => {
        const the = theCuaDoan(S, i + 1);
        return the ? { ...d, the } : d;
      });
      await api('moi_dat_doan_giu_vi_tri', doanGui, giuPos);

      dat({ ...S, pos: giuPos, sel: giuPos });
      ve();

      if (btn) {
        btn.disabled = false;
        btn.innerHTML = `✓ Đã cập nhật (${rowsToProcess.length})`;
        setTimeout(() => { if (btn) btn.innerHTML = oldHtml; }, 2500);
      }
      moBao(`✓ Đã đồng bộ thành công (${rowsToProcess.length} dòng)${dangDoc ? ` · Đang đọc tiếp đoạn ${giuPos}` : ''}!`, 'Đồng bộ Live');
      return;
    }
  } catch (e) {
    if (btn) {
      btn.disabled = false;
      btn.innerHTML = `✕ Lỗi`;
      setTimeout(() => { if (btn) { btn.disabled = false; btn.innerHTML = oldHtml; } }, 2500);
    }
    moBao('Lỗi kết nối khi đồng bộ bảng tính.');
  }
}

function veGiua() {
  if (S.man === 'soat') return veManSoat(S, duLieuSoat);
  if (S.man === 'giong') { danhDauNgheThu(); return veManGiong(S, duLieuGiong); }
  if (S.man === 'tudien') return veManTuDien(S, duLieuTuDien);
  if (S.man === 'caidat') return veManCaiDat(S, duLieuCaiDat);
  if (S.man === 'vanbanghep') return veManVanBanGhep(S, duLieuVBG);
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
  const khoa = `${c.tocDo}|${c.caoDo}|${c.amLuong}|${c.khongGian || ''}`;
  if (khoa === chinhAmDaGui) return;
  chinhAmDaGui = khoa;
  if (coPython()) {
    api('moi_dat_chinh_am',
        { tocDo: c.tocDo ?? 0, caoDo: c.caoDo ?? 0, amLuong: c.amLuong ?? 100, khongGian: c.khongGian || '' });
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
let TRE_PHAT_MS = Number(localStorage.getItem('gd-tre-phat')) || 250;

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
  if (!(thoiLuong > 0)) return;

  const o = nut ? nut.querySelector('.doan__chu') : null;
  const oPhuDe = document.querySelector('.phude-songngu__chu-dich');

  /* Mẩu tiếp theo của CÙNG một đoạn? Nhận ra bằng "đoạn này đã bọc span rồi"
     (dataset.goc đã lưu bản gốc), chứ không dựa vào vòng lặp còn chạy hay
     không — vòng lặp có thể đã kết thúc trong lúc chờ mẩu sau tổng hợp xong. */
  const tiepTuc = soDoan != null && soDoan === toChuDoan && o && o.dataset.goc != null;

  /* Python có gửi phạm vi của mẩu không? Có thì tô ĐÚNG khúc chữ của mẩu
     này với ĐÚNG thời lượng WAV của nó, và mỗi mẩu một mốc riêng. */
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
  if (o && !tiepTuc) {
    const chip = o.querySelector('.doan__the');
    const html = chip ? chip.outerHTML : '';
    const chuGoc = (o.textContent || '').replace(chip ? chip.textContent : '', '').trim();
    if (chuGoc) {
      if (o.dataset.goc == null) o.dataset.goc = o.innerHTML;
      o.innerHTML = html + chiaTu(chuGoc, 0, 1, trongSo)
        .map((w) => `<span class="tu" data-b="${w.b}" data-e="${w.e}">${esc(w.t)}</span>`)
        .join(' ');
    }
  }

  const chuMain = o ? o.querySelectorAll('.tu') : [];
  const chuPhu = oPhuDe ? oPhuDe.querySelectorAll('.tu-dich') : [];

  if (!chuMain.length && !chuPhu.length) return;

  const h = typeof hoSoDangDung === 'function' ? hoSoDangDung(S) : null;
  const laDich = h && h.ngonNgu && h.ngonNgu !== 'vi';

  const chay = () => {
    // toChuMoc đã cộng sẵn TRE_PHAT_MS: chữ đứng im chờ tiếng bắt kịp rồi mới chạy.
    const f = (performance.now() - toChuMoc) / (toChuTong * 1000);
    if (laDich) {
      // Khi đang đọc bản dịch (tiếng nước ngoài):
      // KHÔNG chạy karaoke từng từ trên văn bản gốc (tiếng Việt) vì nhịp âm tiết không khớp.
      // Chỉ tô sáng tĩnh cả cụm câu gốc tương ứng đang đọc để người dùng nắm mạch ngữ cảnh.
      chuMain.forEach((x) => {
        const b = +x.dataset.b;
        const e = +x.dataset.e;
        const dangDoc = coPhamVi ? (b >= tu && b < den) : true;
        const daDoc = coPhamVi ? (e <= tu) : false;
        x.classList.toggle('da-doc', daDoc);
        x.classList.toggle('dang-doc', dangDoc);
      });
    } else {
      chuMain.forEach((x) => {
        const t = trangThaiChu(+x.dataset.b, +x.dataset.e, f, coPhamVi ? tu : null, den);
        x.classList.toggle('da-doc', t === 'da');
        x.classList.toggle('dang-doc', t === 'dang');
      });
    }
    chuPhu.forEach((x) => {
      const b = +x.dataset.b;
      const e = +x.dataset.e;
      const da = f >= e;
      const dang = f >= b && f < e;
      x.classList.toggle('da-doc', da);
      x.classList.toggle('dang-doc', dang);
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
    if (!tiepTuc) {
      dongBoGiongSangPython();
      await guiDoanSangPython();
    }
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
  if (S.dangNgheThu) dungNgheThu();
  clearInterval(dongHoPhat);
  pythonLai = false;
  daTamDung = false;
  if (coPython()) api('moi_dung');
  dungToChu();
  traLaiChuThuong(nodeDoan[posDaVe - 1]);
  dongHoPhat = 0;
  giayDaNghe = 0;
  giayDoanNay = 0;
  dat({ ...S, view: 'san_sang', situation: 'binh_thuong', dangChuanBiDich: false, thongBaoDich: '' });
}

// ---------------------------------------------------------------- bắt sự kiện

// ---------------------------------------------------------------- nạp văn bản

/* Đặt nội dung mới vào tab đang xem. Dùng chung cho dán, mở tệp, kéo thả. */
/* Tên chưa ai dùng, GIỮ NGUYÊN ĐUÔI TỆP. Đánh số thô sau cả tên là hỏng đuôi:
   "baocao.txt 2" ghi ra đĩa đúng như thế, Windows không còn mở được bằng chương
   trình nào. Phải thành "baocao 2.txt". */
function tenKhongTrung(goc, dsCo) {
  const i = goc.lastIndexOf('.');
  const than = i > 0 ? goc.slice(0, i) : goc;
  const duoi = i > 0 ? goc.slice(i) : '';
  let so = 2;
  while (dsCo.includes(`${than} ${so}${duoi}`) || TAI_LIEU[`${than} ${so}${duoi}`]) so += 1;
  return `${than} ${so}${duoi}`;
}

function datTaiLieu(kq) {
  if (!kq) return;
  if (kq.loi) { moBao(kq.loi); return; }

  /* Tên tệp là KHOÁ của TAI_LIEU, nên hai bài cùng tên là bài sau ĐÈ bài trước.
     Nặng nhất là đường dán: moi_dan_van_ban luôn trả tên cố định "Văn bản đã
     dán", nên dán lần thứ hai xoá mất bài dán lần đầu — đo được: kho còn đúng
     một khoá, mở lại hàng cũ thì ra bài mới.

     Vá tối thiểu ở đây: nếu tên ấy đang thuộc về một HÀNG KHÁC thì đánh số cho
     khác đi. Không đổi mô hình khoá (việc đó lớn hơn nhiều và phải trình riêng),
     chỉ thôi không cho hai hàng giẫm lên nhau. Tệp mở lại từ đĩa cùng đường dẫn
     thì vẫn dùng chung khoá như cũ — đó là mở lại chính nó, không phải va chạm. */
  const tenGoc = kq.ten || 'Chưa đặt tên';
  const viTri = S.activeByProfile[S.profile];
  const hangMinh = (S.tabsByProfile[S.profile] || [])[viTri];
  /* Soi MỌI hàng của MỌI hồ sơ, vì TAI_LIEU · duongDanTep · loaiTep · chips đều
     là kho CHUNG cho cả bốn hồ sơ. Bản đầu chỉ soi tabDangMo(S) — hàng của hồ sơ
     đang mở — nên dán ở hồ sơ này rồi dán ở hồ sơ kia vẫn nuốt bài của nhau.

     Và KHÔNG được hỏi TAI_LIEU[ten] nữa: tài liệu nạp LƯỜI từng hàng một
     (moLaiTepDangXem chỉ mở tệp đang xem), nên vừa khởi động là kho gần như
     rỗng, phép canh đoản mạch và đường dẫn hàng cũ bị ghi đè — rồi henLuuHoSo()
     chép thẳng xuống hoso-v2.json, mất luôn qua lần chạy sau. Sự thật cần soi là
     DANH SÁCH HÀNG, thứ sống qua các lần chạy, không phải kho đã nạp. */
  const moiHang = Object.values(S.tabsByProfile || {}).flat();
  const soCho = moiHang.filter((x) => x === tenGoc).length;
  const daCoChoKhac = soCho > (hangMinh === tenGoc ? 1 : 0);

  let ten = tenGoc;
  if (daCoChoKhac) {
    /* Mở LẠI đúng tệp ấy thì dùng chung khoá — nhưng chỉ khi bản trong bộ nhớ
       CHƯA bị sửa. Nếu đang có chữ chưa lưu thì dùng chung khoá là xoá chữ ấy
       VÀ xoá luôn cờ cảnh báo, nên lúc thoát cũng không ai hỏi. Đo được: chữ
       mất, cờ mất, không một dòng báo. */
    const cungTep = kq.duongDan && S.duongDanTep[tenGoc] === kq.duongDan;
    if (!cungTep || chuaLuu.has(tenGoc)) ten = tenKhongTrung(tenGoc, moiHang);
  }
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
  const maPhatHien = nhanDienNgonNguNhanh(TAI_LIEU[ten].doan);
  dat({ ...dongHetMenu(S),
        tabsByProfile: { ...S.tabsByProfile, [S.profile]: ds },
        duongDanTep: dd, loaiTep: lt,
        ngonNguPhatHien: maPhatHien,
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

async function moGoogleDocs() {
  dat({ ...dongHetMenu(S), gdocOpen: true });
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
                + (S.gdocOpen ? veHopGoogleDocs(S.gdocData || {}) : '')
                + (S.dayTuOpen && typeof veHopDayTu === 'function' ? veHopDayTu(S.dayTuOpen) : '')
                + (S.nhanBanWizard && typeof veHopNhanBanGiong === 'function' ? veHopNhanBanGiong(S.nhanBanWizard) : '')
                + (S.toast ? veBaoXuatXong(S.toast) : '');

  const g = (id) => noi.querySelector('#' + id);

  if (S.nhanBanWizard) {
    const dongNB = () => dat({ ...S, nhanBanWizard: null });
    const btnDong = g('nbDong');
    const btnHuy = g('nbHuy');
    const btnQuayLai = g('nbQuayLai');
    const btnSangBuoc2 = g('nbSangBuoc2');
    const btnSangBuoc3 = g('nbSangBuoc3');
    const btnCopyMau = g('nbCopyMau');
    const btnChonTep = g('nbChonTep');
    const btnBatDau = g('nbBatDau');
    const inpTenGiong = g('nbTenGiong');

    if (btnDong) btnDong.onclick = dongNB;
    if (btnHuy) btnHuy.onclick = dongNB;

    const theLoaiEls = noi.querySelectorAll('[data-nbtheloai]');
    theLoaiEls.forEach((el) => {
      el.onclick = () => {
        const ma = el.dataset.nbtheloai;
        const theLoaiObj = (typeof THE_LOAI_GIONG_MAU !== 'undefined' ? THE_LOAI_GIONG_MAU : []).find(t => t.ma === ma);
        dat({
          ...S,
          nhanBanWizard: {
            ...S.nhanBanWizard,
            theLoai: ma,
            tenGiong: theLoaiObj ? theLoaiObj.goiYTen : 'Giọng mới'
          }
        });
      };
    });

    if (btnSangBuoc2) {
      btnSangBuoc2.onclick = () => {
        dat({
          ...S,
          nhanBanWizard: {
            ...S.nhanBanWizard,
            buoc: 2
          }
        });
      };
    }

    if (btnSangBuoc3) {
      btnSangBuoc3.onclick = () => {
        dat({
          ...S,
          nhanBanWizard: {
            ...S.nhanBanWizard,
            buoc: 3
          }
        });
      };
    }

    if (btnQuayLai) {
      btnQuayLai.onclick = () => {
        const buocHienTai = S.nhanBanWizard.buoc || 1;
        dat({
          ...S,
          nhanBanWizard: {
            ...S.nhanBanWizard,
            buoc: Math.max(1, buocHienTai - 1)
          }
        });
      };
    }

    if (inpTenGiong) {
      inpTenGiong.oninput = (e) => {
        S.nhanBanWizard.tenGiong = e.target.value;
      };
      inpTenGiong.onkeydown = (e) => {
        if (e.key === 'Enter' && btnBatDau) btnBatDau.click();
        if (e.key === 'Escape') dongNB();
      };
    }

    const manNB = noi.querySelector('#manNhanBan');
    if (manNB) {
      manNB.onclick = (e) => {
        if (e.target === manNB) dongNB();
      };
    }

    const chkDaNgonNgu = g('nbChkDaNgonNgu');
    if (chkDaNgonNgu) {
      chkDaNgonNgu.onchange = (e) => {
        S.nhanBanWizard.daNgonNgu = e.target.checked;
        const hop = g('nbHopDaNgonNgu');
        if (hop) hop.style.borderColor = e.target.checked ? 'var(--acc)' : 'var(--stroke2)';
      };
    }

    const selNgonNguGoc = g('nbNgonNguGoc');
    if (selNgonNguGoc) {
      selNgonNguGoc.onchange = (e) => {
        S.nhanBanWizard.ngonNguGoc = e.target.value;
      };
    }

    const btnDoiMau = g('nbDoiMau');
    if (btnDoiMau) {
      btnDoiMau.onclick = () => {
        const curIdx = S.nhanBanWizard.idxMau || 0;
        dat({
          ...S,
          nhanBanWizard: {
            ...S.nhanBanWizard,
            idxMau: curIdx + 1
          }
        });
      };
    }

    if (btnCopyMau) {
      btnCopyMau.onclick = async () => {
        const theLoaiObj = (typeof THE_LOAI_GIONG_MAU !== 'undefined' ? THE_LOAI_GIONG_MAU : []).find(t => t.ma === S.nhanBanWizard.theLoai) || (typeof THE_LOAI_GIONG_MAU !== 'undefined' ? THE_LOAI_GIONG_MAU[0] : null);
        const dsMau = (theLoaiObj && theLoaiObj.cacDoanMau) || (theLoaiObj && [theLoaiObj.doanMau]) || [];
        const curIdx = S.nhanBanWizard.idxMau || 0;
        const textToCopy = dsMau[curIdx % dsMau.length] || (theLoaiObj && theLoaiObj.doanMau) || '';
        if (textToCopy) {
          try {
            await navigator.clipboard.writeText(textToCopy);
          } catch (_) {
            const ta = document.createElement('textarea');
            ta.value = textToCopy;
            ta.style.position = 'fixed';
            ta.style.opacity = '0';
            document.body.appendChild(ta);
            ta.select();
            document.execCommand('copy');
            document.body.removeChild(ta);
          }
          btnCopyMau.innerHTML = '<span style="color:var(--ok,#107c41);font-weight:600;display:inline-flex;align-items:center;gap:4px">✓ Đã sao chép</span>';
          btnCopyMau.style.borderColor = 'var(--ok, #107c41)';
          btnCopyMau.style.background = 'rgba(16, 124, 65, 0.08)';
          if (btnCopyMau._timer) clearTimeout(btnCopyMau._timer);
          btnCopyMau._timer = setTimeout(() => {
            if (btnCopyMau) {
              btnCopyMau.innerHTML = '📋 Sao chép';
              btnCopyMau.style.borderColor = '';
              btnCopyMau.style.background = '';
            }
          }, 2200);
        }
      };
    }

    const inpStart = g('nbInpStart');
    const inpEnd = g('nbInpEnd');
    if (inpStart) {
      inpStart.oninput = (e) => {
        S.nhanBanWizard.startTrim = parseFloat(e.target.value) || 0;
      };
      inpStart.onchange = (e) => {
        dat({ ...S, nhanBanWizard: { ...S.nhanBanWizard, startTrim: parseFloat(e.target.value) || 0 } });
      };
    }
    if (inpEnd) {
      inpEnd.oninput = (e) => {
        S.nhanBanWizard.endTrim = parseFloat(e.target.value) || 8;
      };
      inpEnd.onchange = (e) => {
        dat({ ...S, nhanBanWizard: { ...S.nhanBanWizard, endTrim: parseFloat(e.target.value) || 8 } });
      };
    }

    const btnNgheDoanCat = g('nbNgheDoanCat');
    if (btnNgheDoanCat) {
      btnNgheDoanCat.onclick = async () => {
        if (S.nhanBanWizard.fileDaChon && coPython()) {
          btnNgheDoanCat.innerHTML = '🔊 Đang phát…';
          await api('moi_nghe_thu_doan_cat', S.nhanBanWizard.fileDaChon, S.nhanBanWizard.startTrim, S.nhanBanWizard.endTrim);
          setTimeout(() => {
            if (btnNgheDoanCat) btnNgheDoanCat.innerHTML = '▶ Nghe đoạn đã chọn';
          }, 3000);
        }
      };
    }

    const btnDungGolden = g('nbDungGolden');
    if (btnDungGolden) {
      btnDungGolden.onclick = () => {
        if (S.nhanBanWizard && S.nhanBanWizard.phanTich && S.nhanBanWizard.phanTich.goldenWindow) {
          const gw = S.nhanBanWizard.phanTich.goldenWindow;
          dat({
            ...S,
            nhanBanWizard: {
              ...S.nhanBanWizard,
              startTrim: gw.start,
              endTrim: gw.end
            }
          });
        }
      };
    }

    if (btnChonTep) {
      btnChonTep.onclick = async () => {
        if (!coPython()) {
          moBao('Cần chạy trên ứng dụng GiongViet.');
          return;
        }
        const tep = await api('chon_file_mau');
        if (tep) {
          const pt = await api('moi_phan_tich_file_am_thanh', tep);
          const gw = (pt && pt.goldenWindow) || { start: 0, end: 8 };
          dat({
            ...S,
            nhanBanWizard: {
              ...S.nhanBanWizard,
              fileDaChon: tep,
              phanTich: pt,
              startTrim: gw.start,
              endTrim: gw.end
            }
          });
        }
      };
    }

    if (btnBatDau) {
      btnBatDau.onclick = async () => {
        const fileDaChon = S.nhanBanWizard.fileDaChon;
        if (!fileDaChon) {
          moBao('Vui lòng bấm "Chọn tệp âm thanh" để tải bản thu âm lên.');
          return;
        }
        const ten = inpTenGiong ? inpTenGiong.value.trim() : (S.nhanBanWizard.tenGiong || 'Giọng nhân bản');
        if (!ten) {
          moBao('Vui lòng đặt tên cho giọng mới.');
          return;
        }
        const sTrim = S.nhanBanWizard.startTrim;
        const eTrim = S.nhanBanWizard.endTrim;
        const daNgonNgu = !!S.nhanBanWizard.daNgonNgu;
        const ngonNguGoc = S.nhanBanWizard.ngonNguGoc || 'vi';

        dat({
          ...S,
          nhanBanWizard: { ...S.nhanBanWizard, buoc: 4, dangTao: true, tenGiong: ten },
          dangNhanBan: true,
          tienDoGiong: 'Đang chuẩn hóa DSP và trích xuất đặc trưng âm sắc…'
        });

        if (coPython()) {
          api('nhan_ban_giong', ten, fileDaChon, sTrim, eTrim, daNgonNgu, ngonNguGoc);
        }
      };
    }
    return;
  }

  if (S.dayTuOpen) {
    const dongDayTu = () => dat({ ...S, dayTuOpen: null });
    const btnDong = g('dayTuDong');
    const btnHuy = g('dayTuHuy');
    const btnLuu = g('dayTuLuu');
    const inpDoc = g('dayTuDoc');
    if (btnDong) btnDong.onclick = dongDayTu;
    if (btnHuy) btnHuy.onclick = dongDayTu;

    const chips = noi.querySelectorAll('.soat__chip-goiy');
    chips.forEach((c) => {
      c.onclick = () => {
        if (inpDoc && c.dataset.goiy) {
          inpDoc.value = c.dataset.goiy;
          inpDoc.focus();
        }
      };
    });

    if (btnLuu && inpDoc) {
      btnLuu.onclick = async () => {
        const tu = btnLuu.dataset.tu;
        const doc = inpDoc.value.trim();
        if (!doc) {
          moBao('Vui lòng nhập cách đọc cho từ viết tắt.');
          return;
        }
        btnLuu.disabled = true;
        btnLuu.textContent = 'Đang lưu…';
        try {
          if (coPython()) {
            const kq = await api('them_tu', tu, doc);
            if (kq) {
              await guiDoanSangPython(true);
              duLieuSoat = await api('moi_soat');
              dat({ ...S, dayTuOpen: null });
              moBao(`Đã dạy máy đọc “${tu}” thành “${doc}”.`, 'Từ điển phát âm');
            } else {
              moBao('Chưa thêm được vào từ điển.');
              btnLuu.disabled = false;
              btnLuu.textContent = 'Lưu vào từ điển';
            }
          }
        } catch (err) {
          moBao('Lỗi: ' + err);
          btnLuu.disabled = false;
          btnLuu.textContent = 'Lưu vào từ điển';
        }
      };
      inpDoc.onkeydown = (e) => {
        if (e.key === 'Enter') btnLuu.click();
        if (e.key === 'Escape') dongDayTu();
      };
    }
    return;
  }

  if (S.gdocOpen) {
    const dong = () => dat({ ...S, gdocOpen: false });
    const btnDong = g('gdocDong');
    const btnHuy = g('gdocHuy');
    const btnTai = g('gdocTai');
    const inpUrl = g('gdocUrl');
    if (btnDong) btnDong.onclick = dong;
    if (btnHuy) btnHuy.onclick = dong;
    if (btnTai && inpUrl) {
      btnTai.onclick = async () => {
        const url = inpUrl.value.trim();
        if (!url) {
          moBao('Vui lòng dán đường link tài liệu Google Docs.');
          return;
        }
        btnTai.disabled = true;
        btnTai.textContent = 'Đang tải…';
        try {
          if (coPython()) {
            const res = await api('moi_mo_google_docs', url);
            if (res && res.loi) {
              moBao(res.loi, 'Lỗi Google Docs');
              btnTai.disabled = false;
              btnTai.textContent = 'Mở tài liệu';
            } else if (res) {
              dat({ ...S, gdocOpen: false });
              datTaiLieu(res);
              moBao('Đã tải tài liệu từ Google Docs thành công!', 'Thành công');
            }
          } else {
            moBao('Cần khởi chạy qua GiongViet.py để tải từ Google Docs.');
            dong();
          }
        } catch (err) {
          moBao('Lỗi kết nối: ' + err, 'Lỗi');
          btnTai.disabled = false;
          btnTai.textContent = 'Mở tài liệu';
        }
      };
      inpUrl.onkeydown = (e) => {
        if (e.key === 'Enter') btnTai.click();
        if (e.key === 'Escape') dong();
      };
    }
    return;
  }

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

let henGioBao = 0;
function moBao(chu, tieuDe = 'Thông báo', thoiGianMs = 5000) {
  clearTimeout(henGioBao);
  dat({ ...S, toast: { tieuDe, ten: chu, thoiLuong: '', dungLuong: '', thuMuc: '' } });
  if (thoiGianMs > 0) {
    henGioBao = setTimeout(() => {
      if (S.toast) dat({ ...S, toast: false });
    }, thoiGianMs);
  }
}

// ---------------------------------------------------------------- bảng lệnh

const LENH = {
  'Dán văn bản': () => danVanBan(),
  'Mở tệp…': () => moTep(),
  'Mở từ Google Docs…': () => moGoogleDocs(),
  'Mở danh sách tên và số…': () => moDanhSach(),
  'Xuất file âm thanh': () => moHopXuat(),
  'Thu gọn phụ đề': () => dat({ ...S, phuDeThuGon: !S.phuDeThuGon }),
  'Ẩn phụ đề': () => dat({ ...S, anPhuDe: true }),
  'Chuyển phụ đề': () => dat({ ...S, anPhuDe: !S.anPhuDe }),
  'Tạo hồ sơ mới': () => {
    const SO_MAU = [
      { ten: 'Bài viết & Tin tức', giong: 'ngoc-linh', chinh: { tocDo: 0, caoDo: 0, amLuong: 100 }, phongCach: 'Tự nhiên' },
      { ten: 'Thông báo & Loa phường', giong: 'xuan-vinh', chinh: { tocDo: 10, caoDo: 1, amLuong: 100, khongGian: 'loaphuong' }, phongCach: 'Tin tức - thông báo' },
      { ten: 'Sách nói & Kể chuyện', giong: 'pham-tuyen', chinh: { tocDo: -8, caoDo: -1, amLuong: 95 }, phongCach: 'Kể chuyện' },
      { ten: 'Công đức & Thiện nguyện', giong: 'minh-duc', chinh: { tocDo: 0, caoDo: 0, amLuong: 100, khongGian: 'hoitruong' }, phongCach: 'Kể chuyện' },
      { ten: 'Doanh nghiệp & Bán hàng', giong: 'truc-ly', chinh: { tocDo: 10, caoDo: 0, amLuong: 100 }, phongCach: 'Tự nhiên' },
      { ten: 'Pháp quy & Hành chính', giong: 'xuan-vinh', chinh: { tocDo: 0, caoDo: 0, amLuong: 100 }, phongCach: 'Tin tức - thông báo' },
    ];
    const mauChon = SO_MAU[S.profiles.length % SO_MAU.length];
    const tenMoi = `${mauChon.ten} (${S.profiles.length + 1})`;
    const moi = {
      ma: 'moi-' + Date.now(),
      ten: tenMoi,
      giong: mauChon.giong,
      chinh: { ...mauChon.chinh },
      phongCach: mauChon.phongCach,
      tep: ['']
    };
    const i = S.profiles.length;
    dungPhat();
    dat({
      ...dongHetMenu(S),
      profiles: [...S.profiles, moi],
      tabsByProfile: { ...S.tabsByProfile, [i]: [''] },
      activeByProfile: { ...S.activeByProfile, [i]: 0 },
      profile: i,
      view: 'san_sang',
      pos: 1,
      sel: 1
    });
    moBao(`Đã tạo hồ sơ "${tenMoi}"`, 'Tạo hồ sơ mới', 4000);
  },
  'Soát văn bản': () => moManSoat(),
  'Chọn tất cả': () => { dat(dongHetMenu(S)); chonTatCa(); },
  'Xoá dòng/đoạn trắng': () => xoaDongTrang(),
  'Xoá dòng trống': () => xoaDongTrang(),
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
  'Văn bản ghép': () => { napDuLieuVBGTuDong(); dat({ ...dongHetMenu(S), man: 'vanbanghep' }); },
  'Văn bản ghép (Live Data)…': () => { napDuLieuVBGTuDong(); dat({ ...dongHetMenu(S), man: 'vanbanghep' }); },
  'Đóng văn bản ghép': () => dat({ ...dongHetMenu(S), man: 'chinh' }),
  'Tìm và thay thế': () => dat({ ...dongHetMenu(S), find: !S.find }),
  'Thu gọn danh sách hồ sơ': () => dat({ ...dongHetMenu(S), rail: !S.rail }),
  'Giao diện tối': () => dat({ ...dongHetMenu(S), theme: S.theme === 'toi' ? 'sang' : 'toi' }),
  'Giao diện sáng': () => dat({ ...dongHetMenu(S), theme: S.theme === 'toi' ? 'sang' : 'toi' }),
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
    x = datChinh(x, 'khongGian', '');
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
    if (S.dangNgheThu === g) return dungNgheThu();
    dat({ ...dongHetMenu(S), dangNgheThu: g, mauDangPhat: true });
    if (coPython()) {
      api('nghe_thu_giong', g).then((res) => {
        if (res && res.loi) { moBao(res.loi); dungNgheThu(); }
      });
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
    'Tiếng nói do mô hình AI tạo ra, chạy trực tiếp ngoại tuyến (Offline) trên máy này. '
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
  /* Nhãn phải tra theo ĐÚNG hàng đang đóng, không phải hàng đang xem. Trước đây
     tra theo S.activeByProfile nên hộp thoại gọi tên một tệp THỨ BA: người dùng
     bấm × trên bài vừa dán, máy hỏi về "thongbao.txt" đang mở ở hàng khác. Đọc
     một cái tên lạ thì họ mất luôn khả năng phán đoán nên bấm gì. */
  const ds = tabDangMo(S);
  const j = ds.indexOf(ten);
  const nhan = ten || tenHienThi(ds, j >= 0 ? j : S.activeByProfile[S.profile]);
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
    // Lưu ĐÚNG tệp đang đóng, không phải tệp đang xem.
    if (ma === 'luu' && !(await luuVanBan(ten))) return;
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
/* Lưu MỘT tệp cụ thể, mặc định là tệp đang xem.

   Phải nhận tên vì "Lưu rồi đóng" trong hộp Chưa lưu chạy trên tệp BỊ ĐÓNG, mà
   tệp ấy thường không phải tệp đang xem. Trước đây hàm này luôn lấy
   doanDangXem() + tenTepDangXem(), nên đo được: hỏi về B.txt, ghi ra A.txt, rồi
   xoá cờ chưa-lưu của B — chữ của B mất sạch mà máy báo "Đã lưu". */
async function luuVanBan(ten = tenTepDangXem(S)) {
  const t = TAI_LIEU[ten];
  const doan = (t && t.doan ? t.doan : []).filter((d) => d && d.kieu !== 'blank');
  dat(dongHetMenu(S));
  if (!doan.length) { moBao('Chưa có văn bản nào để lưu.'); return false; }
  if (!coPython()) { moBao('Cần chạy trong chương trình mới lưu được.'); return false; }

  const kq = await api('moi_luu_van_ban', ten || 'vanban.txt',
                       doan.map((d) => d.chu).join('\n'));
  if (kq && kq.ten) {
    chuaLuu.delete(ten);
    gioLuuCuoi = new Date().toTimeString().slice(0, 5);
    ve();                       // thanh trạng thái đổi từ "Chưa lưu" sang giờ lưu
  }
  moBao(kq && kq.ten ? `Đã lưu “${kq.ten}”.` : 'Chưa lưu được tệp.');
  return !!(kq && kq.ten);
}

document.addEventListener('click', async (e) => {
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
  if (t('#themTep'))            { thoiSuaTen(); return chuyenSang(themTab(S)); }
  if ((n = t('[data-dongtep]'))) { e.stopPropagation();
                                   const i = +n.dataset.dongtep;
                                   thoiSuaTen();
                                   return hoiTruocKhiDongTep(tabDangMo(S)[i],
                                            () => chuyenSang(dongTab(S, i))); }
  if (t('.tep__o'))             return;          // đang gõ tên, đừng cướp cú bấm
  if ((n = t('[data-tep]')))    { const i = +n.dataset.tep;
                                  if (suaTenTep) { thoiSuaTen(); ve(); }
                                  if (i === S.activeByProfile[S.profile]) return;
                                  return chuyenSang(doiTab(S, i)); }
  if ((n = t('[data-hoso]')))   { thoiSuaTen();
                                  const iHoSoMoi = +n.dataset.hoso;
                                  /* Mau ghep di theo ho so (VG-15): cat ban dang
                                     dung roi lay ban cua ho so vua chon. Thieu hai
                                     dong nay thi chan dai trai in ten ho so moi ma
                                     mau ghep van y nguyen cua ho so cu. */
                                  if (typeof vbgGhiNho === 'function') {
                                    vbgGhiNho(S.profile);
                                    vbgDoiSang(iHoSoMoi);
                                  }
                                  return chuyenSang(doiHoSo(S, iHoSoMoi)); }
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
  if ((n = t('[data-doan]'))) {
    const soDoan = +n.dataset.doan;
    if (coPython()) api('moi_chuan_bi_doan', soDoan);
    return dat(chonDoan(S, soDoan));
  }
  /* CHỐT CHẶN cho năm nút mang lớp .la-khoa. Trước đây chúng dùng `disabled`,
     mà `disabled` chặn luôn sự kiện chuột nên tooltip nói LÝ DO không bao giờ
     hiện — người dùng thấy nút mờ đi mà không biết vì sao, đúng thứ KPI "dễ
     dùng cho người không rành máy tính" cấm. Nay nút bấm được và tự nói lý do,
     nên PHẢI có chốt ở đây: thiếu nó là bấm Nghe lúc máy chưa sẵn sàng, giao
     diện chạy màn "đang đọc" mà loa im — bẫy CLAUDE.md ghi là đã vấp thật. */
  if ((n = t('.nut.la-khoa'))) {
    const vi = lyDoKhoa(S) || (doanDangXem(S, TAI_LIEU).length ? ''
      : 'Chưa có văn bản — hãy Dán văn bản hoặc Mở tệp trước');
    return moBao(vi || 'Chưa dùng được lúc này', 'Chưa dùng được');
  }
  if (t('#nutXuat'))            return moHopXuat();
  if (t('#bDong'))              return dat({ ...S, toast: false });
  if (t('#bMoThuMuc'))          { if (coPython()) api('mo_thu_muc', hopXuat && hopXuat.thuMuc);
                                  return dat({ ...S, toast: false }); }
  if (t('#nutNghe')) {
    if (S.view === 'dang_doc') return LENH['Tạm dừng']();
    if (daTamDung) { dat({ ...S, view: 'dang_doc' }); return batDauPhat(true); }
    dat(ngheToanBo(S)); return batDauPhat();
  }
  if ((n = t('#nutDongBoLive'))) {
    dongBoDuLieuLive(n);
    return;
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
    if (coPython()) {
      api('nghe_thu_giong', ma).then((res) => {
        if (res && res.loi) { moBao(res.loi); dungNgheThu(); }
      });
    }
    return dat({ ...S, dangNgheThu: ma, mauDangPhat: true });
  }
  if (t('[data-vbg="quay_ve_chinh"]')) {
    luuTamVBG();
    return dat({ ...S, man: 'chinh' });
  }
  if (t('[data-vbg="mo_tao_moi"]')) {
    duLieuVBG.modalTaoMoi = true;
    duLieuVBG.menuMauOpen = false;
    return ve();
  }
  if (t('[data-vbg="dong_tao_moi"]')) {
    duLieuVBG.modalTaoMoi = false;
    return ve();
  }
  if (t('[data-vbg="menu_mau"]')) {
    duLieuVBG.menuMauOpen = !duLieuVBG.menuMauOpen;
    return ve();
  }
  if ((n = t('[data-vbgpreset]'))) {
    luuTamVBG();
    /* Hai nơi dùng chung thuộc tính này với hai ý nghĩa: menu bên trái gắn CHỈ
       SỐ (lặp thẳng trên duLieuVBG.maus), còn hộp chọn mẫu gắn ID vì hai danh
       sách xếp khác thứ tự — trước đây nó gắn chỉ số nên bấm "Thông báo lịch
       hẹn" lại nhảy sang mẫu "Bán hàng & Chốt đơn Livestream". */
    const khoa = n.dataset.vbgpreset;
    const theoId = duLieuVBG.maus.findIndex(m => m.id === khoa);
    duLieuVBG.mauHienTai = theoId >= 0 ? theoId : (+khoa || 0);
    duLieuVBG.menuMauOpen = false;
    duLieuVBG.modalTaoMoi = false;
    napDuLieuVBGTuDong(true);
    return ve();
  }
  if ((n = t('[data-vbgnav]'))) {
    luuTamVBG();
    duLieuVBG.nav = +n.dataset.vbgnav;
    duLieuVBG.menuMauOpen = false;
    return ve();
  }
  if ((n = t('[data-vbgcongtac]'))) {
    luuTamVBG();
    const k = n.dataset.vbgcongtac;
    const cur = duLieuVBG.maus[duLieuVBG.mauHienTai];
    cur.on[k] = !cur.on[k];
    return ve();
  }
  if ((n = t('[data-vbgrule]'))) {
    luuTamVBG();
    const k = n.dataset.vbgrule;
    const cur = duLieuVBG.maus[duLieuVBG.mauHienTai];
    cur.rule[k] = !cur.rule[k];
    return ve();
  }
  if ((n = t('[data-vbgfield="autoSync"]'))) {
    luuTamVBG();
    const cur = duLieuVBG.maus[duLieuVBG.mauHienTai];
    cur.autoSync = !cur.autoSync;
    return ve();
  }
  if ((n = t('[data-vbgsrc]'))) {
    luuTamVBG();
    const cur = duLieuVBG.maus[duLieuVBG.mauHienTai];
    cur.srcType = +n.dataset.vbgsrc;
    if (!cur.srcVals) {
      cur.srcVals = {
        0: cur.srcVal && cur.srcVal.startsWith('http') ? cur.srcVal : (typeof GOOGLE_SHEET_MAC_DINH !== 'undefined' ? GOOGLE_SHEET_MAC_DINH : ''),
        2: cur.srcVal && !cur.srcVal.startsWith('http') ? cur.srcVal : (typeof EXCEL_MAC_DINH_LOCAL !== 'undefined' ? EXCEL_MAC_DINH_LOCAL : '')
      };
    }
    cur.srcVal = cur.srcVals[cur.srcType] || (cur.srcType === 0 ? (typeof GOOGLE_SHEET_MAC_DINH !== 'undefined' ? GOOGLE_SHEET_MAC_DINH : '') : (typeof EXCEL_MAC_DINH_LOCAL !== 'undefined' ? EXCEL_MAC_DINH_LOCAL : ''));
    napDuLieuVBGTuDong(true);
    return ve();
  }
  if ((n = t('[data-vbginsert]'))) {
    const v = n.dataset.vbginsert;
    const txt = $('#vbgMauText');
    if (txt) {
      const p = txt.selectionStart || txt.value.length;
      txt.value = txt.value.slice(0, p) + v + txt.value.slice(p);
      const cur = duLieuVBG.maus[duLieuVBG.mauHienTai];
      cur.T.mau = txt.value;
      txt.focus();
      txt.setSelectionRange(p + v.length, p + v.length);
      const previewEl = document.querySelector('.vanbanghep__phai');
      if (previewEl && typeof vePreviewGhep === 'function') {
        previewEl.innerHTML = vePreviewGhep(cur);
      }
      const demEl = document.getElementById('vbgDoanDem');
      if (demEl) demEl.textContent = `${txt.value.length} ký tự`;
      document.querySelectorAll('.vanbanghep__chip-bien').forEach(btn => {
        const varName = btn.dataset.vbginsert;
        if (varName) {
          btn.classList.toggle('dung', txt.value.includes(varName));
        }
      });
    }
    return;
  }
  if (t('[data-vbg="tra_ve_dau"]')) {
    duLieuVBG = JSON.parse(JSON.stringify(MAU_VAN_BAN_GHEP_MAC_DINH));
    return ve();
  }
  if (t('[data-vbg="chon_tep"]')) {
    luuTamVBG();
    const cur = duLieuVBG.maus[duLieuVBG.mauHienTai];
    if (!coPython()) {
      moBao('Chọn tệp bảng tính cần chạy trên GiongViet.');
      return;
    }
    const kq = await api('moi_tai_bang_tinh', '', 2, cur.sheet || '', cur.headRow || 'Dòng 1');
    if (kq && kq.loi) {
      moBao(kq.loi);
      return;
    }
    if (kq && kq.thanhCong) {
      cur.cols = kq.cols;
      cur.rows = kq.rows;
      cur.daTaiThat = true;   /* hết là dữ liệu mẫu — chấm trạng thái dựa vào cờ này */
      cur.tongSo = kq.tongSo;
      cur.srcVal = kq.nguon;
      cur.sheet = kq.currentSheet;
      if (kq.sheets) cur.sheetOpts = kq.sheets;
      cur.isSingleSheet = !!kq.isSingleSheet;
      if (kq.headRow) cur.headRow = kq.headRow;
      if (!cur.srcVals) cur.srcVals = { 0: '', 1: '', 2: '' };
      cur.srcVals[2] = kq.nguon;
      moBao(`Đã nạp thành công: ${kq.cols.length} cột, ${kq.tongSo} dòng (${cur.sheet})!`, 'Nạp tệp bảng tính');
      return ve();
    }
    return;
  }
  if ((n = t('[data-vbg="kiem_tra_ket_noi"]'))) {
    luuTamVBG();
    const btn = n;
    const oldHtml = btn.innerHTML;
    btn.disabled = true;
    btn.innerHTML = `<span class="vong-xoay" style="width:13px;height:13px;border:2px solid var(--acc);border-top-color:transparent;border-radius:50%;display:inline-block;animation:xoay 0.8s linear infinite;vertical-align:middle;margin-right:6px"></span> Đang tải…`;

    const cur = duLieuVBG.maus[duLieuVBG.mauHienTai];
    const srcInput = $('#vbgSrcVal');
    if (srcInput) {
      cur.srcVal = srcInput.value.trim();
      if (!cur.srcVals) cur.srcVals = { 0: '', 1: '', 2: '' };
      cur.srcVals[cur.srcType] = cur.srcVal;
    }
    if (!coPython()) {
      btn.disabled = false;
      btn.innerHTML = oldHtml;
      moBao('Kết nối bảng tính cần chạy trên GiongViet.');
      return;
    }
    try {
      const kq = await api('moi_tai_bang_tinh', cur.srcVal, cur.srcType, cur.sheet || '', cur.headRow || 'Dòng 1');
      if (kq && kq.loi) {
        btn.disabled = false;
        btn.innerHTML = `✕ Thất bại`;
        setTimeout(() => { if (btn) { btn.disabled = false; btn.innerHTML = oldHtml; } }, 2500);
        moBao(kq.loi);
        return;
      }
      if (kq && kq.thanhCong) {
        cur.cols = kq.cols;
        cur.rows = kq.rows;
      cur.daTaiThat = true;   /* hết là dữ liệu mẫu — chấm trạng thái dựa vào cờ này */
        cur.tongSo = kq.tongSo;
        cur.sheet = kq.currentSheet;
        if (kq.sheets) cur.sheetOpts = kq.sheets;
        cur.isSingleSheet = !!kq.isSingleSheet;
        if (kq.headRow) cur.headRow = kq.headRow;
        if (kq.nguon) {
          cur.srcVal = kq.nguon;
          if (!cur.srcVals) cur.srcVals = { 0: '', 1: '', 2: '' };
          cur.srcVals[cur.srcType] = kq.nguon;
        }
        btn.innerHTML = `✓ Đã cập nhật (${kq.tongSo} dòng)`;
        moBao(`Đã nạp bảng tính thành công: ${kq.cols.length} cột, ${kq.tongSo} dòng (${cur.sheet})!`, 'Nạp dữ liệu');
        setTimeout(() => { ve(); }, 900);
        return;
      }
    } catch (err) {
      btn.disabled = false;
      btn.innerHTML = `✕ Lỗi tải`;
      setTimeout(() => { if (btn) { btn.disabled = false; btn.innerHTML = oldHtml; } }, 2500);
      moBao('Không thể kết nối đến nguồn dữ liệu.');
      return;
    }
    btn.disabled = false;
    btn.innerHTML = oldHtml;
    return;
  }
  if (t('[data-vbg="apdung"]')) {
    const cur = duLieuVBG.maus[duLieuVBG.mauHienTai];
    if ($('#vbgMauText')) cur.T.mau = $('#vbgMauText').value;
    if ($('#vbgText_dau')) cur.T.dau = $('#vbgText_dau').value;
    if ($('#vbgText_giua')) cur.T.giua = $('#vbgText_giua').value;
    if ($('#vbgText_cuoi')) cur.T.cuoi = $('#vbgText_cuoi').value;
    
    const doanGhep = [];
    if (cur.on.dau && cur.T.dau.trim()) {
      cur.T.dau.trim().split(/\n+/).forEach(s => { if (s.trim()) doanGhep.push(s.trim()); });
    }
    
    /* Chưa có dòng nào thì DỪNG, đừng độn người vào.

       Bản trước, khi danh sách rỗng, chỗ này nhét sẵn ba dòng "Nguyễn Văn An ·
       500.000 đồng", "Trần Thị Mai · 1.000.000 đồng", "Lê Hoàng Long ·
       2.000.000 đồng" rồi ghép luôn vào bài. Nghĩa là bấm "Áp dụng" lúc chưa
       tải dữ liệu là máy đọc to tên ba người không có thật, kèm số tiền, giữa
       buổi lễ ở chùa — và câu báo còn nói "Đã cập nhật danh sách (3 dòng)!"
       nên không ai biết ba dòng ấy ở đâu ra. */
    const rowsToProcess = (cur.rows && cur.rows.length) ? cur.rows : null;
    if (!rowsToProcess) {
      moBao('Chưa có dòng dữ liệu nào để ghép. Hãy bấm “Tải dữ liệu” '
            + 'hoặc chọn tệp danh sách trước.');
      return;
    }

    
    const dsDong = locDongTheoQuyTacVBG(cur);
    if (!dsDong.length) {
      moBao('Sau khi lọc thì không còn dòng nào. Hãy tắt bớt “Lọc & nhóm”.');
      return;
    }
    lanVaoDoanGhepVBG(doanGhep, cur, dsDong);
    
    if (cur.on.cuoi && cur.T.cuoi.trim()) {
      cur.T.cuoi.trim().split(/\n+/).forEach(s => { if (s.trim()) doanGhep.push(s.trim()); });
    }
    
    const ten = cur.name + ' (Ghép).txt';
    const textDoc = doanGhep.join('\n\n');
    TAI_LIEU[ten] = {
      doan: doanGhep.map(chu => ({ chu, goc: chu })),
      doc: textDoc
    };
    danhDauSua();

    const dangDoc = S.view === 'dang_doc';
    const giuPos = (dangDoc || S.view === 'tam_dung') && S.pos > 0 ? S.pos : 1;

    const tabs = tabDangMo(S).slice();
    let idxTab = tabs.indexOf(ten);
    if (idxTab < 0) {
      tabs.push(ten);
      idxTab = tabs.length - 1;
    }
    dat({ ...dongHetMenu(S), man: 'chinh',
          tabsByProfile: { ...S.tabsByProfile, [S.profile]: tabs },
          activeByProfile: { ...S.activeByProfile, [S.profile]: idxTab },
          loaiTep: { ...(S.loaiTep || {}), [ten]: 'ghep' },
          pos: giuPos, sel: giuPos });
    henLuuHoSo();
    if (coPython()) {
      api('moi_luu_van_ban', ten, textDoc).then((res) => {
        if (res && res.duongDan) {
          S = { ...S, duongDanTep: { ...(S.duongDanTep || {}), [ten]: res.duongDan } };
          henLuuHoSo();
        }
      });
      const doanGui = doanDangXem(S, TAI_LIEU).map((d, i) => {
        const the = theCuaDoan(S, i + 1);
        return the ? { ...d, the } : d;
      });
      api('moi_dat_doan_giu_vi_tri', doanGui, giuPos);
    }
    // Báo số dòng THẬT SỰ đã ghép, tức số sau khi lọc — không phải số dòng thô
    // của bảng tính. Bật "Bỏ dòng thiếu" mà vẫn báo số cũ là nói sai.
    moBao(`Đã cập nhật danh sách (${dsDong.length} dòng)${dangDoc ? ` · Tiếp tục đọc từ đoạn ${giuPos}` : ''}!`);
    return;
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
  if (t('#btnHoanDoiLang')) {
    e.stopPropagation();
    const h = hoSoDangDung(S);
    const curSrc = h.ngonNguNguon === 'auto' ? (S.ngonNguPhatHien || 'vi') : (h.ngonNguNguon || 'vi');
    const curTgt = h.ngonNgu || 'vi';
    const newTgt = curSrc;
    const newSrc = curTgt;

    const curGiong = h.giong || '';
    const gTheoNN = { ...(h.giongTheoNgonNgu || {}) };
    if (curGiong) {
      gTheoNN[curTgt] = curGiong;
    }

    let giongMoi = '';
    if (newTgt === 'vi') {
      giongMoi = gTheoNN['vi'] || 'ngan';
    } else {
      const daLuu = gTheoNN[newTgt];
      const daLuuHopLe = daLuu && GIONG.some(g => (g.id || g.ma) === daLuu && ((g.ngonNgu || '').toLowerCase() === newTgt.toLowerCase() || (g.ngonNgu || '').toLowerCase().startsWith(newTgt.toLowerCase().split('-')[0])));
      if (daLuuHopLe) {
        giongMoi = daLuu;
      } else {
        const gioi = doanGioiTinhGiong(curGiong);
        const mapNN = GIONG_BAN_XU_MAC_DINH[newTgt] || GIONG_BAN_XU_MAC_DINH[newTgt.split('-')[0]] || { nam: 'en-US-GuyNeural', nu: 'en-US-JennyNeural' };
        giongMoi = (gioi === 'nu' ? mapNN.nu : mapNN.nam) || mapNN.nam || mapNN.nu || curGiong;
        gTheoNN[newTgt] = giongMoi;
      }
    }

    const newProfiles = S.profiles ? S.profiles.map((p, i) => i === S.profile ? {
      ...p,
      ngonNguNguon: newSrc,
      ngonNgu: newTgt,
      giong: giongMoi,
      giongTheoNgonNgu: gTheoNN
    } : p) : S.profiles;

    danhDauSua();
    dat({ ...S, profiles: newProfiles, anPhuDe: false });
    dongBoGiongSangPython();
    if (coPython()) {
      api('moi_dat_ngon_ngu', newSrc, newTgt, S.pos || 1);
    }
    return;
  }
  if (t('#nutLocNgonNgu') || t('[data-molocngonngu]')) {
    e.stopPropagation();
    return dat({ ...S, moDropdownNgonNgu: !S.moDropdownNgonNgu });
  }
  if (t('#xoaLocNgonNgu')) {
    e.stopPropagation();
    return dat({ ...S, giongNgonNgu: [] });
  }
  if (S.moDropdownNgonNgu && !t('.giongkho__menu-ngonngu') && !t('#nutLocNgonNgu') && !t('[data-molocngonngu]')) {
    dat({ ...S, moDropdownNgonNgu: false });
  }
  if ((n = t('[data-toggledangu]'))) {
    e.stopPropagation();
    const gId = n.dataset.toggledangu;
    dat({ ...S, moMenuLangGiongId: S.moMenuLangGiongId === gId ? null : gId });
    return;
  }
  if ((n = t('[data-dongmenulang]'))) {
    e.stopPropagation();
    dat({ ...S, moMenuLangGiongId: null });
    return;
  }
  if ((n = t('[data-checklang]'))) {
    e.stopPropagation();
    const gId = n.dataset.checklang;
    const langCode = n.dataset.langcode;
    const checked = n.checked;

    if (duLieuGiong) {
      for (const nhom of ['cuaToi', 'coSan']) {
        const found = (duLieuGiong[nhom] || []).find((x) => x.id === gId);
        if (found) {
          let ds = Array.isArray(found.dsNgonNgu) && found.dsNgonNgu.length > 0
            ? [...found.dsNgonNgu]
            : (found.daNgonNgu ? DS_LOC_NGON_NGU.map((x) => x.ma) : [found.ngonNgu || 'vi']);

          if (langCode === 'all') {
            if (checked) {
              found.daNgonNgu = true;
              found.dsNgonNgu = DS_LOC_NGON_NGU.map((x) => x.ma);
              found.ngonNgu = 'all';
            } else {
              found.daNgonNgu = false;
              found.dsNgonNgu = ['vi'];
              found.ngonNgu = 'vi';
            }
          } else {
            if (found.daNgonNgu) {
              found.daNgonNgu = false;
              ds = DS_LOC_NGON_NGU.map((x) => x.ma).filter((x) => x !== langCode);
            } else {
              if (checked) {
                if (!ds.includes(langCode)) ds.push(langCode);
              } else {
                ds = ds.filter((x) => x !== langCode);
                if (ds.length === 0) ds = ['vi'];
              }
            }
            if (ds.length >= DS_LOC_NGON_NGU.length) {
              found.daNgonNgu = true;
              found.dsNgonNgu = DS_LOC_NGON_NGU.map((x) => x.ma);
              found.ngonNgu = 'all';
            } else {
              found.daNgonNgu = ds.length > 1;
              found.dsNgonNgu = ds;
              found.ngonNgu = ds.length === 1 ? ds[0] : (found.daNgonNgu ? 'all' : ds[0]);
            }
          }
          if (found.rieng && coPython()) {
            api('moi_cap_nhat_da_ngu_giong', gId, found.daNgonNgu, found.ngonNgu, found.dsNgonNgu);
          }
          break;
        }
      }
    }
    dat({ ...S });
    return;
  }
  if (S.moMenuLangGiongId && !t('.the-giong__menu-lang') && !t('[data-toggledangu]')) {
    dat({ ...S, moMenuLangGiongId: null });
  }
  if ((n = t('[data-molink]'))) {
    e.stopPropagation();
    const url = n.dataset.molink;
    if (url && coPython()) {
      api('moi_mo_lien_ket', url);
    } else if (url) {
      window.open(url, '_blank');
    }
    return;
  }
  if ((n = t('[data-xoahoso]'))) {
    e.stopPropagation();
    const idx = parseInt(n.dataset.xoahoso, 10);
    if (isNaN(idx) || S.profiles.length <= 1) return;
    const tenHoSo = S.profiles[idx].ten;
    const profilesMoi = S.profiles.filter((_, i) => i !== idx);
    const tabsMoi = {};
    const activeMoi = {};
    let newProfileIdx = S.profile;
    if (idx === S.profile) {
      newProfileIdx = Math.max(0, idx - 1);
    } else if (idx < S.profile) {
      newProfileIdx = S.profile - 1;
    }
    profilesMoi.forEach((_, i) => {
      const oldIdx = i >= idx ? i + 1 : i;
      tabsMoi[i] = S.tabsByProfile[oldIdx] || [''];
      activeMoi[i] = S.activeByProfile[oldIdx] || 0;
    });
    dungPhat();
    dat({
      ...S,
      profiles: profilesMoi,
      tabsByProfile: tabsMoi,
      activeByProfile: activeMoi,
      profile: newProfileIdx
    });
    moBao(`Đã xóa hồ sơ "${tenHoSo}"`, 'Quản lý hồ sơ');
    return;
  }
  if ((n = t('[data-cdsan]'))) {
    e.stopPropagation();
    const ma = n.dataset.cdsan;
    const preset = CAI_DAT_SAN_PHO_BIEN.find((p) => p.ma === ma);
    if (!preset) return;
    const h = hoSoDangDung(S);
    if (!h) return;
    const hoSoMoi = S.profiles.map((p, i) => {
      if (i !== S.profile) return p;
      return {
        ...p,
        chinh: { ...p.chinh, ...preset.chinh },
        phongCach: preset.phongCach
      };
    });
    dat({ ...S, profiles: hoSoMoi });
    if (coPython()) {
      api('moi_dat_phong_cach', preset.phongCach);
    }
    return;
  }
  if ((n = t('[data-cddongco]'))) {
    e.stopPropagation();
    const loai = n.dataset.cddongco;
    if (duLieuCaiDat && duLieuCaiDat.cauHinh) {
      duLieuCaiDat.cauHinh.dong_co_dich = loai;
    }
    if (coPython()) {
      api('moi_luu_cau_hinh_khoa', 'dong_co_dich', loai);
    }
    return dat({ ...S });
  }
  if (t('#luuKeyOpenAI')) {
    e.stopPropagation();
    const val = (($('#cdOpenAIKey') || {}).value || '').trim();
    if (!val) {
      return dat({ ...S, testApiStatus: { ...S.testApiStatus, openai: { ok: false, msg: '❌ Vui lòng nhập API Key trước khi lưu' } } });
    }
    dat({ ...S, testApiStatus: { ...S.testApiStatus, openai: { ok: true, msg: '⏳ Đang kiểm tra kết nối tới OpenAI...' } } });
    if (coPython()) {
      api('moi_kiem_tra_api_dich', 'openai', val).then((kq) => {
        if (kq && kq.thanhCong) {
          api('moi_luu_cau_hinh_khoa', 'openai_api_key', val);
          if (duLieuCaiDat && duLieuCaiDat.cauHinh) duLieuCaiDat.cauHinh.openai_api_key = val;
          dat({ ...S, testApiStatus: { ...S.testApiStatus, openai: { ok: true, msg: `✅ Kết nối thành công! Đã lưu (${kq.moHinh})` } } });
        } else {
          dat({ ...S, testApiStatus: { ...S.testApiStatus, openai: { ok: false, msg: kq.loi || '❌ Lỗi kiểm tra API Key' } } });
        }
      }).catch((err) => {
        dat({ ...S, testApiStatus: { ...S.testApiStatus, openai: { ok: false, msg: `❌ Lỗi mạng: ${err}` } } });
      });
    }
    return;
  }
  if (t('#luuKeyGemini')) {
    e.stopPropagation();
    const val = (($('#cdGeminiKey') || {}).value || '').trim();
    if (!val) {
      return dat({ ...S, testApiStatus: { ...S.testApiStatus, gemini: { ok: false, msg: '❌ Vui lòng nhập API Key trước khi lưu' } } });
    }
    dat({ ...S, testApiStatus: { ...S.testApiStatus, gemini: { ok: true, msg: '⏳ Đang kiểm tra kết nối tới Google Gemini...' } } });
    if (coPython()) {
      api('moi_kiem_tra_api_dich', 'gemini', val).then((kq) => {
        if (kq && kq.thanhCong) {
          api('moi_luu_cau_hinh_khoa', 'gemini_api_key', val);
          if (duLieuCaiDat && duLieuCaiDat.cauHinh) duLieuCaiDat.cauHinh.gemini_api_key = val;
          dat({ ...S, testApiStatus: { ...S.testApiStatus, gemini: { ok: true, msg: `✅ Kết nối thành công! Đã lưu (${kq.moHinh})` } } });
        } else {
          dat({ ...S, testApiStatus: { ...S.testApiStatus, gemini: { ok: false, msg: kq.loi || '❌ Lỗi kiểm tra API Key' } } });
        }
      }).catch((err) => {
        dat({ ...S, testApiStatus: { ...S.testApiStatus, gemini: { ok: false, msg: `❌ Lỗi mạng: ${err}` } } });
      });
    }
    return;
  }
  if (t('#btnXoaCacheDia')) {
    e.stopPropagation();
    if (coPython()) {
      api('moi_xoa_cache_dia').then((res) => {
        dat({
          ...S,
          cacheInfo: res.thongTin || { dungLuongMB: 0, soTep: 0, gioiHanMB: 150 },
          thongBaoCache: res.thongBao || 'Đã dọn sạch bộ nhớ đệm âm thanh!'
        });
      });
    }
    return;
  }
  if (t('#nbChayNen') || t('#nbDongXong')) {
    e.stopPropagation();
    return dat({ ...S, nhanBanWizard: null });
  }
  if ((n = t('#nbDatGiongMoi'))) {
    e.stopPropagation();
    const gId = n.dataset.giong;
    if (gId) {
      dat({ ...datGiong(S, gId), nhanBanWizard: null });
      dongBoGiongSangPython();
    } else {
      dat({ ...S, nhanBanWizard: null });
    }
    return;
  }
  if ((n = t('#nbNgheThuMoi'))) {
    e.stopPropagation();
    const gId = n.dataset.nghegiong;
    if (gId) {
      batNgheThu(gId);
    }
    return;
  }
  if ((n = t('[data-giongloc]')))  return dat({ ...S, giongLoc: n.dataset.giongloc });
  if ((n = t('[data-gionggioi]'))) return dat({ ...S, giongGioi: n.dataset.gionggioi });
  if ((n = t('[data-giong]')))  {
    if (S.dangNgheThu) dungNgheThu();
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
  if ((n = t('[data-soatxoa-kytu]'))) { e.stopPropagation();
                                        return lamSachKyTuDoan(+n.dataset.soatxoaKytu); }
  if (t('[data-soatlamsach]'))        { e.stopPropagation();
                                        return lamSachKyTuTatCa(); }
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
    if (coPython()) {
      api('nghe_thu_giong', ma).then((res) => {
        if (res && res.loi) { moBao(res.loi); dungNgheThu(); }
      });
    }
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
  thoiSuaTen();
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

let _vbgPreviewTimer = null;
function henCapNhatPreviewVBG(cur, delay = 120) {
  if (_vbgPreviewTimer) clearTimeout(_vbgPreviewTimer);
  _vbgPreviewTimer = setTimeout(() => {
    _vbgPreviewTimer = null;
    const previewEl = document.querySelector('.vanbanghep__phai');
    if (previewEl && typeof vePreviewGhep === 'function') {
      previewEl.innerHTML = vePreviewGhep(cur);
    }
  }, delay);
}

let _timGiongTimer = null;
let _timTuDienTimer = null;

document.addEventListener('input', (e) => {
  /* Gõ thẳng trong một đoạn văn bản. Gộp vào ĐÂY chứ không đăng ký listener
     'input' thứ hai: trước đây có hai cái, và cái sau ghi đè cái trước trong bộ
     kiểm nên nửa số nhánh không bao giờ được canh. */
  const nutChu = _nutChu(e);
  if (nutChu) { chuDangGo(nutChu); return; }
  /* Ô tên tệp: chỉ ghi lại chữ đang gõ, KHÔNG vẽ lại. Vẽ lại theo từng phím là
     ô nhảy con trỏ về đầu. Việc trả tiêu điểm để cuối ve() lo, cho những lần vẽ
     lại đến từ nơi khác — gói tin Python chẳng hạn. */
  if (e.target.id === 'oTenTep') {
    tenDangGo = e.target.value;
    viTriTenDangGo = e.target.selectionStart != null
      ? e.target.selectionStart : String(e.target.value || '').length;
    return;
  }
  if (e.target.id === 'oTim') {
    S.chuTim = e.target.value;
    chayTim(S.chuTim);
    const d = $('#timDem');
    if (d) d.textContent = ketQuaTim.length ? `1/${ketQuaTim.length}` : '0/0';
    if (ketQuaTim.length) {
      timThu = 0;
      const k = ketQuaTim[0];
      const nut = nodeDoan && nodeDoan[k.doan - 1];
      if (nut) cuonToiDoanHienTai(nut);
    }
    return;
  }
  if (e.target.id === 'oThay') {
    S.chuThay = e.target.value;
    return;
  }
  if (e.target.id === 'oTimTuDien') {
    S.tuDienTim = e.target.value;
    if (_timTuDienTimer) clearTimeout(_timTuDienTimer);
    _timTuDienTimer = setTimeout(() => {
      _timTuDienTimer = null;
      timTuDien(e.target.value);
    }, 120);
    return;
  }
  if (e.target.id === 'oTuMoi' || e.target.id === 'oDocMoi') {
    // Giữ chữ đang gõ vào S nhưng KHÔNG vẽ lại: vẽ lại là ô input thành node
    // mới, mất tiêu điểm và người dùng gõ được đúng một chữ.
    S.tuDienSua = { ...(S.tuDienSua || {}),
                    [e.target.id === 'oTuMoi' ? 'tu' : 'doc']: e.target.value };
    return;
  }
  if (e.target.id === 'oTimLang') {
    S.timLang = e.target.value;
    const timVal = (e.target.value || '').trim().toLowerCase();
    const container = document.getElementById('dsLangItems');
    if (container && typeof DS_LOC_NGON_NGU !== 'undefined') {
      const filtered = DS_LOC_NGON_NGU.filter(
        (l) => !timVal || l.ten.toLowerCase().includes(timVal) || l.ma.toLowerCase().includes(timVal)
      );
      const dsNgonNguLoc = S.giongNgonNgu || [];
      if (filtered.length === 0) {
        container.innerHTML = '<div style="padding:12px;font-size:12px;color:var(--txt3);text-align:center">Không tìm thấy ngôn ngữ</div>';
      } else {
        container.innerHTML = filtered.map((l) => {
          const checked = dsNgonNguLoc.includes(l.ma);
          return `
            <label style="display:flex;align-items:center;gap:8px;padding:6px 12px;font-size:12.5px;color:var(--txt);cursor:pointer;user-select:none" class="giongkho__item-ngonngu">
              <input type="checkbox" data-loclang="${l.ma}" ${checked ? 'checked' : ''} style="accent-color:var(--acc);cursor:pointer;width:15px;height:15px">
              <span>${l.co}</span>
              <span style="flex:1;min-width:0;overflow:hidden;text-overflow:ellipsis;white-space:nowrap">${l.ten}</span>
            </label>
          `;
        }).join('');
      }
    }
    return;
  }
  if (e.target.id === 'oTimGiong') {
    S.giongTim = e.target.value;
    if (_timGiongTimer) clearTimeout(_timGiongTimer);
    _timGiongTimer = setTimeout(() => {
      _timGiongTimer = null;
      const thanEl = document.querySelector('.giongkho__than');
      if (thanEl && typeof veManGiong === 'function') {
        const coSan = (duLieuGiong && duLieuGiong.coSan) || [];
        const cuaToi = (duLieuGiong && duLieuGiong.cuaToi) || [];
        const loc = S.giongLoc || 'tatca';
        const gioi = S.giongGioi || 'Tất cả';
        const tim = (S.giongTim || '').trim().toLowerCase();
        const dsNgonNguLoc = S.giongNgonNgu || [];
        const laNam = (g) => {
          if (/\(nam\)/i.test(g.ten)) return true;
          const moTa = (g.moTa || '').replace(/miền\s+nam/gi, '');
          return /\bnam\b/i.test(moTa);
        };
        const laNu = (g) => {
          if (/\(nữ\)/i.test(g.ten)) return true;
          return /\bnữ\b/i.test(g.moTa || '');
        };
        const hop = (g) => {
          if (loc === 'dangu' && !g.daNgonNgu) return false;
          if (gioi === 'Nam' && !laNam(g)) return false;
          if (gioi === 'Nữ' && !laNu(g)) return false;
          if (dsNgonNguLoc.length > 0) {
            if (!g.daNgonNgu && !dsNgonNguLoc.includes('vi')) return false;
          }
          if (!tim) return true;
          return `${g.ten} ${g.moTa} ${g.phu}`.toLowerCase().includes(tim);
        };
        const nhomCuaToi = loc === 'cosan' ? [] : cuaToi.filter(hop);
        const nhomCoSan = loc === 'cuatoi' ? [] : coSan.filter(hop);
        thanEl.innerHTML = `
          ${loc !== 'cosan' ? `<div class="giongkho__nhan">Giọng của tôi</div>
            <div class="giongkho__luoi">${nhomCuaToi.map((g) => veTheGiong(g)).join('')}
              ${veTheNhanBan(S)}</div>` : ''}
          ${nhomCoSan.length && loc !== 'cuatoi' ? `<div class="giongkho__nhan">Giọng có sẵn</div>
            <div class="giongkho__luoi">${nhomCoSan.map((g) => veTheGiong(g)).join('')}</div>` : ''}
          ${!nhomCuaToi.length && !nhomCoSan.length
            ? '<div class="giongkho__trong">Không tìm thấy giọng nào khớp.</div>' : ''}
        `;
      }
    }, 120);
    return;
  }
  if (e.target && (e.target.id && e.target.id.startsWith('vbg') || (e.target.closest && e.target.closest('.vanbanghep')))) {
    if (typeof duLieuVBG !== 'undefined') {
      const cur = duLieuVBG.maus && (duLieuVBG.maus[duLieuVBG.mauHienTai] || duLieuVBG.maus[0]);
      if (cur) {
        if (e.target.id === 'vbgMauText') cur.T.mau = e.target.value;
        else if (e.target.id === 'vbgText_dau') cur.T.dau = e.target.value;
        else if (e.target.id === 'vbgText_giua') cur.T.giua = e.target.value;
        else if (e.target.id === 'vbgText_cuoi') cur.T.cuoi = e.target.value;
        else if (e.target.id === 'vbgSauMoi') cur.sauMoi = e.target.value;
        else if (e.target.id === 'vbgSrcVal') {
          cur.srcVal = e.target.value;
          if (!cur.srcVals) cur.srcVals = { 0: '', 2: '' };
          cur.srcVals[cur.srcType] = cur.srcVal;
        }

        // Cập nhật bộ đếm ký tự / đoạn siêu nhanh (0.001ms)
        const demEl = document.getElementById('vbgDoanDem');
        if (demEl) {
          const val = e.target.value || '';
          if (e.target.id === 'vbgMauText') {
            demEl.textContent = `${val.length} ký tự`;
            const chips = document.querySelectorAll('.vanbanghep__chip-bien');
            for (let i = 0; i < chips.length; i++) {
              const varName = chips[i].dataset.vbginsert;
              if (varName) chips[i].classList.toggle('dung', val.includes(varName));
            }
          } else {
            const doanCount = val.split(/\n{2,}/).filter(x => x.trim()).length || (val.trim() ? 1 : 0);
            demEl.textContent = `${doanCount} đoạn · ${val.length} ký tự`;
          }
        }

        // Trì hoãn cập nhật preview cột phải qua debounce để không gây nghẽn luồng UniKey
        henCapNhatPreviewVBG(cur, 100);
      }
    }
  }
});

document.addEventListener('change', (e) => {
  if (e.target && e.target.dataset && e.target.dataset.doikhonggian) {
    const val = e.target.value;
    dat(datChinh(S, 'khongGian', val));
    return;
  }
  if (e.target && e.target.dataset && e.target.dataset.loclang) {
    const m = e.target.dataset.loclang;
    const checked = e.target.checked;
    let ds = [...(S.giongNgonNgu || [])];
    if (checked) {
      if (!ds.includes(m)) ds.push(m);
    } else {
      ds = ds.filter((x) => x !== m);
    }
    dat({ ...S, giongNgonNgu: ds });
    return;
  }
  if (e.target && e.target.id === 'oNgonNguNguon') {
    const maLang = e.target.value;
    const h = hoSoDangDung(S);
    h.ngonNguNguon = maLang;
    const ds = S.hoSoList || [];
    const idx = S.profile || 0;
    if (ds[idx]) {
      ds[idx].ngonNguNguon = maLang;
    }
    danhDauSua();
    const laDich = h.ngonNgu && h.ngonNgu !== 'vi';
    const tenLang = (typeof DS_LOC_NGON_NGU !== 'undefined' ? (DS_LOC_NGON_NGU.find(x => x.ma === h.ngonNgu) || {}).ten : h.ngonNgu) || h.ngonNgu;
    dat({
      ...S,
      dangChuanBiDich: laDich,
      thongBaoDich: laDich ? `🌐 Đang chuẩn bị bản dịch sang [${tenLang}]…` : ''
    });
    if (coPython()) {
      api('moi_dat_ngon_ngu', maLang, h.ngonNgu || 'vi').then(() => {
        guiDoanSangPython(true);
        setTimeout(() => {
          dat({ ...S, dangChuanBiDich: false, thongBaoDich: '' });
        }, 350);
      }).catch(() => {
        dat({ ...S, dangChuanBiDich: false, thongBaoDich: '' });
      });
    }
    return;
  }
  if (e.target && e.target.id === 'oNgonNgu') {
    const maLang = e.target.value;
    const curH = hoSoDangDung(S) || {};
    const curGiong = curH.giong || '';
    const curLang = curH.ngonNgu || 'vi';

    const gTheoNN = { ...(curH.giongTheoNgonNgu || {}) };
    if (curGiong) {
      gTheoNN[curLang] = curGiong;
    }

    let giongMoi = '';

    if (maLang === 'vi') {
      giongMoi = gTheoNN['vi'] || 'ngan';
    } else {
      const daLuu = gTheoNN[maLang];
      const daLuuHopLe = daLuu && GIONG.some(g => (g.id || g.ma) === daLuu && ((g.ngonNgu || '').toLowerCase() === maLang.toLowerCase() || (g.ngonNgu || '').toLowerCase().startsWith(maLang.toLowerCase().split('-')[0])));

      if (daLuuHopLe) {
        giongMoi = daLuu;
      } else {
        const gioi = doanGioiTinhGiong(curGiong);
        const mapNN = GIONG_BAN_XU_MAC_DINH[maLang] || GIONG_BAN_XU_MAC_DINH[maLang.split('-')[0]] || { nam: 'en-US-GuyNeural', nu: 'en-US-JennyNeural' };
        giongMoi = (gioi === 'nu' ? mapNN.nu : mapNN.nam) || mapNN.nam || mapNN.nu || curGiong;
        gTheoNN[maLang] = giongMoi;
      }
    }

    const newProfiles = S.profiles ? S.profiles.map((p, i) => i === S.profile ? {
      ...p,
      ngonNgu: maLang,
      giong: giongMoi,
      giongTheoNgonNgu: gTheoNN
    } : p) : S.profiles;

    danhDauSua();
    const laDich = maLang && maLang !== 'vi';
    const tenLang = (typeof DS_LOC_NGON_NGU !== 'undefined' ? (DS_LOC_NGON_NGU.find(x => x.ma === maLang) || {}).ten : maLang) || maLang;
    dat({
      ...S,
      profiles: newProfiles,
      anPhuDe: false,
      dangChuanBiDich: laDich,
      thongBaoDich: laDich ? `🌐 Đang chuẩn bị bản dịch sang [${tenLang}]…` : ''
    });

    dongBoGiongSangPython();

    if (coPython()) {
      api('moi_dat_ngon_ngu', (hoSoDangDung(S) || {}).ngonNguNguon || 'auto', maLang, S.pos || 1).then(() => {
        guiDoanSangPython(true);
        setTimeout(() => {
          dat({ ...S, dangChuanBiDich: false, thongBaoDich: '' });
        }, 350);
      }).catch(() => {
        dat({ ...S, dangChuanBiDich: false, thongBaoDich: '' });
      });
    }
    return;
  }
  if (e.target && e.target.id === 'vbgSrcVal') {
    luuTamVBG();
    napDuLieuVBGTuDong(true);
    return;
  }
  if (e.target && e.target.id === 'vbgSheet') {
    luuTamVBG();
    const cur = duLieuVBG.maus[duLieuVBG.mauHienTai];
    cur.sheet = e.target.value;
    if (coPython() && cur.srcVal) {
      api('moi_tai_bang_tinh', cur.srcVal, cur.srcType, cur.sheet, cur.headRow || 'Dòng 1').then(kq => {
        if (kq && kq.thanhCong) {
          cur.cols = kq.cols;
          cur.rows = kq.rows;
          cur.daTaiThat = true;   /* hết là dữ liệu mẫu — chấm trạng thái dựa vào cờ này */
          cur.tongSo = kq.tongSo;
          cur.sheet = kq.currentSheet;
          if (kq.sheets) cur.sheetOpts = kq.sheets;
          cur.isSingleSheet = !!kq.isSingleSheet;
          ve();
        } else {
          /* Không có nhánh này thì ô chọn đã đổi chữ, dữ liệu thì không đổi, và
             không một lời nào báo - người dùng tưởng đã đổi bảng xong. */
          moBao((kq && kq.loi) || 'Không đọc được bảng vừa chọn. Dữ liệu giữ nguyên như cũ.');
        }
      }).catch(() => moBao('Không đọc được bảng vừa chọn. Dữ liệu giữ nguyên như cũ.'));
    }
    return;
  }
  if (e.target && e.target.id === 'vbgHeadRow') {
    luuTamVBG();
    const cur = duLieuVBG.maus[duLieuVBG.mauHienTai];
    cur.headRow = e.target.value;
    if (coPython() && cur.srcVal) {
      api('moi_tai_bang_tinh', cur.srcVal, cur.srcType, cur.sheet || '', cur.headRow).then(kq => {
        if (kq && kq.thanhCong) {
          cur.cols = kq.cols;
          cur.rows = kq.rows;
          cur.daTaiThat = true;   /* hết là dữ liệu mẫu — chấm trạng thái dựa vào cờ này */
          cur.tongSo = kq.tongSo;
          ve();
        } else {
          moBao((kq && kq.loi) || 'Không đọc được với dòng tiêu đề vừa chọn. Dữ liệu giữ nguyên.');
        }
      }).catch(() => moBao('Không đọc được với dòng tiêu đề vừa chọn. Dữ liệu giữ nguyên.'));
    }
    return;
  }
  if (e.target.dataset && e.target.dataset.vbgcolmap !== undefined) {
    const idx = +e.target.dataset.vbgcolmap;
    const cur = duLieuVBG.maus[duLieuVBG.mauHienTai];
    if (cur && cur.cols[idx]) {
      cur.cols[idx].varName = e.target.value;
      cur.cols[idx].use = e.target.options[e.target.selectedIndex].text;
      return ve();
    }
  }
  if (e.target.dataset && e.target.dataset.vbgcolread !== undefined) {
    const idx = +e.target.dataset.vbgcolread;
    const cur = duLieuVBG.maus[duLieuVBG.mauHienTai];
    if (cur && cur.cols[idx]) {
      cur.cols[idx].read = e.target.value;
      return ve();
    }
  }
});

function luuTamVBG() {
  if (typeof duLieuVBG === 'undefined') return;
  const cur = duLieuVBG.maus && (duLieuVBG.maus[duLieuVBG.mauHienTai] || duLieuVBG.maus[0]);
  if (!cur) return;
  if ($('#vbgMauText')) cur.T.mau = $('#vbgMauText').value;
  if ($('#vbgText_dau')) cur.T.dau = $('#vbgText_dau').value;
  if ($('#vbgText_giua')) cur.T.giua = $('#vbgText_giua').value;
  if ($('#vbgText_cuoi')) cur.T.cuoi = $('#vbgText_cuoi').value;
  if ($('#vbgSauMoi')) cur.sauMoi = $('#vbgSauMoi').value;
  if ($('#vbgSrcVal')) {
    cur.srcVal = $('#vbgSrcVal').value;
    if (!cur.srcVals) cur.srcVals = { 0: '', 2: '' };
    cur.srcVals[cur.srcType] = cur.srcVal;
  }
  if ($('#vbgSheet')) cur.sheet = $('#vbgSheet').value;
  if ($('#vbgHeadRow')) cur.headRow = $('#vbgHeadRow').value;
}

/* Gõ vào chữ thì chép ngay sang tài liệu, KHÔNG vẽ lại - vẽ lại là con trỏ
   nhảy về đầu bài, gõ được đúng một chữ rồi mất chỗ. Việc tách hay bỏ đoạn
   đợi tới lúc rời khỏi đoạn (focusout) mới làm, lúc ấy vẽ lại mới an toàn. */
const _nutChu = (e) => {
  const el = e.target && (e.target.nodeType === 1 ? e.target : e.target.parentElement);
  return el && el.closest ? el.closest('.doan__chu[contenteditable]') : null;
};
let dangGoIME = false;
document.addEventListener('compositionstart', () => { dangGoIME = true; });
document.addEventListener('compositionend', (e) => {
  dangGoIME = false;
  const nut = _nutChu(e);
  if (nut) chuDangGo(nut);
});

document.addEventListener('focusout', (e) => {
  dangGoIME = false;
  chotTenTepNeuDangGo(e);
  const nut = _nutChu(e);
  if (nut) roiDoanDangGo(nut);
});

document.addEventListener('paste', (e) => {
  const nut = _nutChu(e);
  if (nut) {
    e.preventDefault();
    let text = (e.clipboardData || window.clipboardData).getData('text/plain') || '';
    // Chuẩn hoá Unicode dựng sẵn NFC và lọc bỏ toàn bộ khoảng trắng đặc biệt / ký tự vô hình
    text = text.normalize('NFC')
      .replace(/[\u00a0\u1680\u2000-\u200a\u202f\u205f\u3000]/g, ' ')
      .replace(/[\u200b-\u200d\ufeff\u00ad]/g, '');

    // Tự động xoá toàn bộ dòng/đoạn trắng thừa khi dán
    text = text.split(/\r?\n/).map(s => s.trim()).filter(s => s.length > 0).join('\n');

    if (document.queryCommandSupported && document.queryCommandSupported('insertText')) {
      document.execCommand('insertText', false, text);
    } else {
      const sel = window.getSelection();
      if (!sel || !sel.rangeCount) return;
      sel.deleteFromDocument();
      sel.getRangeAt(0).insertNode(document.createTextNode(text));
    }
    chuDangGo(nut);
  }
});

function chonTatCa() {
  const cuon = $('#cuon');
  const sel = window.getSelection && window.getSelection();
  if (!cuon || !sel) return;
  const r = document.createRange();
  r.selectNodeContents(cuon);
  sel.removeAllRanges();
  sel.addRange(r);
}

const PHIM_CHU_CAI_TOAN_CUC = ['o', 'e', 'h', 'b', 'w', 'g', 'm', 'k', 'l'];
const PHIM_DAU_TOAN_CUC = ['=', '+', '-', '/', '.'];

function phimToanCucKhiDangGo(e) {
  if (e.key === 'F1') return true;
  if (e.altKey && ['1', '2', '3'].includes(e.key)) return true;
  if (!(e.ctrlKey || e.metaKey)) return false;
  if (PHIM_DAU_TOAN_CUC.includes(e.key)) return true;
  return PHIM_CHU_CAI_TOAN_CUC.includes(e.key.toLowerCase());
}

document.addEventListener('keydown', (e) => {
  // BẢO VỆ BỘ GÕ TIẾNG VIỆT (UniKey / EVKey / Windows Telex):
  // Khi đang ghép dấu hoặc gõ phím tổ hợp IME, tuyệt đối không can thiệp sự kiện.
  if (e.isComposing || e.keyCode === 229 || dangGoIME) return;

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
      if (e.key === 'Escape') { e.preventDefault(); thoiSuaTen(); return ve(); }
      return;
    }
    if (dangGoChu) {
      if ((e.ctrlKey || e.metaKey) && e.key.toLowerCase() === 'a') {
        e.preventDefault();
        chonTatCa();
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
    /* Trước đây chỗ này `return` VÔ ĐIỀU KIỆN, nên mọi phím tắt bên dưới chết
       hẳn khi con trỏ đang trong một đoạn. Mà MỌI đoạn đều contenteditable, nên
       chỉ cần bấm chuột vào bài một cái là mất sạch phím tắt — người dùng bấm
       Ctrl+E để xuất, không có gì xảy ra, và không đoán nổi vì sao.

       Đo được: Ctrl+E · Ctrl+H · Ctrl+B · Ctrl+= · Alt+1 đều CHẠY khi con trỏ
       đứng ngoài và CHẾT khi con trỏ trong đoạn.

       Nay cho đi tiếp đúng những phím KHÔNG có nghĩa riêng lúc đang gõ chữ.
       Cố ý CHẶN LẠI: Space (gõ dấu cách — CLAUDE.md ghi đây là bẫy đã vấp thật),
       Ctrl+V/C/X/Z/Y (dán, chép, cắt, hoàn tác — trình duyệt lo trong ô chữ),
       Ctrl+A (đã có nhánh riêng bôi đen cả bài ở trên), Escape, Enter. */
    if (!phimToanCucKhiDangGo(e)) return;
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
  if (c && e.shiftKey && k === 'l') { e.preventDefault(); return xoaDongTrang(); }
  /* Ctrl+A khi con trỏ ĐỨNG NGOÀI vùng chữ. Thiếu nhánh này thì nó rơi xuống mặc
     định của trình duyệt và bôi đen cả nhãn menu lẫn thanh trạng thái — trông
     như chương trình vừa hỏng. */
  if (c && k === 'a')     { e.preventDefault(); return chonTatCa(); }
  if (e.key === 'F1')     { e.preventDefault(); return LENH['Hướng dẫn nhanh'](); }
  if (e.altKey && ['1', '2', '3'].includes(e.key)) {
    e.preventDefault(); return dat(datThe(S, THE_CAM_XUC[+e.key - 1][0]));
  }
  if (c && k === 'z' && !e.shiftKey) {
    if (hoanTac(tenTepDangXem(S))) { e.preventDefault(); return; }
  }
  if (c && (k === 'y' || (e.shiftKey && k === 'z'))) {
    if (lamLai(tenTepDangXem(S))) { e.preventDefault(); return; }
  }
  if (e.key === '[' || e.key === ']') {
    e.preventDefault();
    const h = hoSoDangDung(S);
    const buoc = e.key === ']' ? 5 : -5;
    const tocDoMoi = Math.max(-50, Math.min(100, (h.tocDo || 0) + buoc));
    datThongSo('tocDo', tocDoMoi);
    moBao(`Tốc độ đọc: ${tocDoMoi >= 0 ? '+' : ''}${tocDoMoi}%`, 'Tốc độ giọng đọc');
    return;
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

document.addEventListener('mouseover', (e) => {
  const n = e.target.closest('[data-nghe]');
  if (n && n.dataset.nghe && coPython()) {
    api('moi_chuan_bi_doan', +n.dataset.nghe);
  }
});

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
  const soDoan = Number(goi.doan || goi.pos);
  if (goi.state === 'dang_doc' && soDoan) {
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
    const doiDoan = soDoan !== S.pos;

    S = { ...S, view: 'dang_doc', pos: soDoan, sel: soDoan,
          situation: dangTao ? 'dang_tao' : 'binh_thuong',
          cauDocHienTai: goi.cauDoc || S.cauDocHienTai,
          cauGocHienTai: goi.cauGoc || S.cauGocHienTai };
    if (doiDoan) { giayDoanNay = 0; posDaVe = -1; }

    if (dangTao) {
      // Dừng đồng hồ lại, chờ tiếng. Vẽ lại cả màn để hiện thanh phát dạng chờ.
      clearInterval(dongHoPhat); dongHoPhat = 0;
      dungToChu(); traLaiChuThuong(nodeDoan[soDoan - 1]);
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
    batDauToChu(nodeDoan[soDoan - 1], goi.thoiLuong, soDoan,
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
  const h = hoSoDangDung(S);
  const lang = (h && h.ngonNgu) || 'vi';
  const g = (h && h.giong) || '';
  return `${S.profile}|${tenTepDangXem(S)}|${lang}|${g}|${loaiTepDangXem()}|${doan.length}|`
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

  // Đo đếm ký tự, số từ và thời lượng đọc live 100% không gián đoạn
  const ttSo = document.getElementById('ttSo');
  if (ttSo) {
    const tk = thongKeTaiLieu(S, TAI_LIEU);
    const soDoan = S.view === 'dang_doc' ? S.pos : (S.sel || 1);
    ttSo.textContent = tk.tongTu > 0
      ? `Đoạn ${soDoan}/${tk.tongDoan} · ${tk.tongTu.toLocaleString('vi-VN')} từ (~${tk.thoiLuongStr})`
      : `Đoạn ${soDoan}, Cột 1`;
  }
  const ttLuu = document.getElementById('ttLuu');
  if (ttLuu) ttLuu.innerHTML = '<b>Chưa lưu</b> · ';
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

// ------------------------------------------------------------- LỊCH SỬ HOÀN TÁC (UNDO / REDO STACK)
const STACK_UNDO = {}; // { [tenTep]: { undo: [], redo: [] } }
const MAX_UNDO_DEPTH = 30;

function ghiLichSu(ten, doan) {
  if (!ten || !doan) return;
  if (!STACK_UNDO[ten]) STACK_UNDO[ten] = { undo: [], redo: [] };
  const st = STACK_UNDO[ten];
  const snapshot = JSON.stringify(doan);
  if (st.undo.length && st.undo[st.undo.length - 1] === snapshot) return;
  st.undo.push(snapshot);
  if (st.undo.length > MAX_UNDO_DEPTH) st.undo.shift();
  st.redo = [];
}

function hoanTac(ten) {
  if (!ten || !STACK_UNDO[ten] || !STACK_UNDO[ten].undo.length) return false;
  const st = STACK_UNDO[ten];
  const t = TAI_LIEU[ten];
  if (!t) return false;
  const snapshot = st.undo.pop();
  st.redo.push(JSON.stringify(t.doan));
  TAI_LIEU[ten] = { ...t, doan: JSON.parse(snapshot) };
  danhDauSua();
  duLieuSoat = null;
  dat({ ...S, pos: 1, sel: 1 });
  guiDoanSangPython(true);
  moBao('Đã hoàn tác thao tác vừa rồi.', 'Hoàn tác (Undo)');
  return true;
}

function lamLai(ten) {
  if (!ten || !STACK_UNDO[ten] || !STACK_UNDO[ten].redo.length) return false;
  const st = STACK_UNDO[ten];
  const t = TAI_LIEU[ten];
  if (!t) return false;
  const snapshot = st.redo.pop();
  st.undo.push(JSON.stringify(t.doan));
  TAI_LIEU[ten] = { ...t, doan: JSON.parse(snapshot) };
  danhDauSua();
  duLieuSoat = null;
  dat({ ...S, pos: 1, sel: 1 });
  guiDoanSangPython(true);
  moBao('Đã làm lại thao tác.', 'Làm lại (Redo)');
  return true;
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

  ghiLichSu(ten, t.doan);
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

  ghiLichSu(ten, t.doan);
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
  ghiLichSu(ten, t.doan);
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

  const chuMoiStr = String(chuMoi != null ? chuMoi : '');

  // 1. Nếu đoạn bị xoá sạch chỉ còn khoảng trắng hoặc rỗng:
  if (!chuMoiStr.trim()) {
    if (cu.length > 1) {
      ghiLichSu(ten, t.doan);
      const moi = cu.slice(0, n - 1).concat(cu.slice(n));
      TAI_LIEU[ten] = { ...t, doan: moi };
      danhDauSua();
      const chips = dichThe(S.chips, ten, n, -1);
      duLieuSoat = null;
      dat({ ...S, chips, soatBoQua: {},
            sel: Math.max(1, Math.min(n, moi.length)),
            pos: Math.max(1, Math.min(S.pos, moi.length)) });
      guiDoanSangPython();
      return;
    } else {
      if (cu[0].chu !== '') {
        cu[0] = { ...cu[0], chu: '' };
        danhDauSua();
      }
      return;
    }
  }

  // 2. Nếu không chứa ký tự xuống dòng (\n): Chỉ cập nhật văn bản, TUYỆT ĐỐI KHÔNG re-render gây giật IME
  if (!chuMoiStr.includes('\n')) {
    if (cu[n - 1].chu !== chuMoiStr) {
      cu[n - 1] = { ...cu[n - 1], chu: chuMoiStr };
      danhDauSua();
    }
    return;
  }

  // 3. Khi dán hoặc có ký tự xuống dòng: Tách thành nhiều đoạn và TỰ ĐỘNG XOÁ TOÀN BỘ CÁC DÒNG/ĐOẠN TRẮNG
  const dong = chuMoiStr.split(/\r?\n/).map(s => s.trim()).filter(s => s.length > 0);
  if (!dong.length) {
    if (cu.length > 1) {
      ghiLichSu(ten, t.doan);
      const moi = cu.slice(0, n - 1).concat(cu.slice(n));
      TAI_LIEU[ten] = { ...t, doan: moi };
      danhDauSua();
      const chips = dichThe(S.chips, ten, n, -1);
      duLieuSoat = null;
      dat({ ...S, chips, soatBoQua: {},
            sel: Math.max(1, Math.min(n, moi.length)),
            pos: Math.max(1, Math.min(S.pos, moi.length)) });
      guiDoanSangPython();
      return;
    }
    return;
  }

  ghiLichSu(ten, t.doan);
  const moi = cu.slice(0, n - 1)
    .concat(dong.map((chu, i) => (i === 0 ? { ...cu[n - 1], chu } : { kieu: 'body', chu })),
            cu.slice(n));

  const delta = moi.length - cu.length;
  TAI_LIEU[ten] = { ...t, doan: moi };
  danhDauSua();
  const chips = delta ? dichThe(S.chips, ten, n + 1, delta) : S.chips;
  duLieuSoat = null;
  dat({ ...S, chips, soatBoQua: {},
        sel: Math.max(1, Math.min(n, moi.length)),
        pos: Math.max(1, Math.min(S.pos, moi.length)) });
  guiDoanSangPython();
}

/** Tự động xoá toàn bộ dòng/đoạn trắng trong văn bản đang xem, không làm ảnh hưởng dòng có chữ. */
function xoaDongTrang() {
  const ten = tenTepDangXem(S);
  const t = TAI_LIEU[ten];
  if (!t || !t.doan) return;
  const cu = t.doan;
  const moi = cu.filter((d) => d && d.kieu !== 'blank' && String(d.chu || '').trim() !== '');
  if (!moi.length) moi.push({ kieu: 'body', chu: '' });

  const daXoa = cu.length - moi.length;
  if (daXoa <= 0) {
    moBao('Văn bản hiện tại đã sạch, không có dòng/đoạn trắng nào.', 'Dọn dẹp văn bản');
    return;
  }

  ghiLichSu(ten, cu);
  TAI_LIEU[ten] = { ...t, doan: moi };
  danhDauSua();
  duLieuSoat = null;
  dungPhat();

  // Ánh xạ lại thẻ cảm xúc cho các đoạn còn tồn tại
  const chipCu = (S.chips && S.chips[ten]) || {};
  const chipMoi = {};
  let idxMoi = 1;
  cu.forEach((d, idxCu) => {
    const numCu = idxCu + 1;
    if (d && d.kieu !== 'blank' && String(d.chu || '').trim() !== '') {
      if (chipCu[numCu]) chipMoi[idxMoi] = chipCu[numCu];
      idxMoi++;
    }
  });

  dat({ ...dongHetMenu(S),
        chips: { ...S.chips, [ten]: chipMoi },
        pos: 1, sel: 1 });
  guiDoanSangPython(true);
  moBao(`Đã tự động xoá ${daXoa} dòng/đoạn trắng thừa.`, 'Dọn dẹp văn bản');
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
  const noiDungTab = {};
  Object.keys(TAI_LIEU).forEach((ten) => {
    if (TAI_LIEU[ten] && TAI_LIEU[ten].doan && TAI_LIEU[ten].doan.length) {
      noiDungTab[ten] = {
        doan: TAI_LIEU[ten].doan,
        doc: TAI_LIEU[ten].doc || ''
      };
    }
  });

  return {
    dangDung: S.profile,
    theme: S.theme,
    zoom: S.zoom,
    the: S.chips,
    duongDan: S.duongDanTep,
    loaiTep: S.loaiTep,
    noiDung: noiDungTab,
    hoSo: S.profiles.map((h, i) => ({
      /* Mau ghep cua RIENG ho so nay, da bo `rows`: mot bang tinh 2.000 dong ma
         nhet vao hoso-v2.json thi tep phinh theo, va henLuuHoSo() JSON.stringify
         no moi lan dat() - may yeu dung hinh. Du lieu tai lai duoc; cau hinh thi
         khong. */
      vanBanGhep: (typeof vbgDeLuu === 'function') ? vbgDeLuu(i, S.profile) : null,
      ma: h.ma, ten: h.ten, giong: h.giong, chinh: h.chinh,
      ngonNgu: h.ngonNgu || 'vi',
      ngonNguNguon: h.ngonNguNguon || 'auto',
      phongCach: h.phongCach || 'Tự nhiên',
      giongTheoNgonNgu: h.giongTheoNgonNgu || {},
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

function nhanDienNgonNguNhanh(doan) {
  if (!doan || !doan.length) return 'vi';
  const mau = doan.slice(0, 3).map((d) => String(d.chu || '')).join(' ').trim();
  if (!mau) return 'vi';
  if (/[\u3040-\u30ff]/.test(mau)) return 'ja';
  if (/[\uac00-\ud7af]/.test(mau)) return 'ko';
  if (/[\u4e00-\u9fa5]/.test(mau)) return 'zh';
  if (/[\u0e00-\u0e7f]/.test(mau)) return 'th';
  if (/[\u0600-\u06ff]/.test(mau)) return 'ar';
  if (/[\u0900-\u097f]/.test(mau)) return 'hi';
  if (/[\u0980-\u09ff]/.test(mau)) return 'bn';
  if (/[\u0400-\u04ff]/.test(mau)) return 'ru';
  if (/[\u1780-\u17ff]/.test(mau)) return 'km';
  if (/[\u0e80-\u0eff]/.test(mau)) return 'lo';
  if (/[\u1000-\u109f]/.test(mau)) return 'my';
  if (/[àáảãạăằắẳẵặâầấẩẫậèéẻẽẹêềếểễệìíỉĩịòóỏõọôồốổỗộơờớởỡợùúủũụưừứửữựỳýỷỹỵđĐ]/i.test(mau)) return 'vi';
  return 'en';
}

/* Tab nhớ TÊN tệp, còn nội dung thì không nằm trong hoso-v2.json — mở lại từ
   đường dẫn đã lưu. Chỉ mở tệp ĐANG XEM: mở hết mọi tab là bắt người dùng chờ
   ngay lúc khởi động, trong khi phần lớn tab họ không đụng tới phiên đó. */
async function moLaiTepDangXem() {
  const ten = tenTepDangXem(S);
  if (!ten) return;
  // Nếu đã có sẵn trong bộ nhớ (ví dụ tab ghép hoặc vừa dán), không cần đọc lại
  if (TAI_LIEU[ten] && TAI_LIEU[ten].doan && TAI_LIEU[ten].doan.length) return;
  if (!coPython()) return;
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
  const ten = tenTepDangXem(S);
  if (ten && TAI_LIEU[ten] && TAI_LIEU[ten].doan) {
    S = { ...S, ngonNguPhatHien: nhanDienNgonNguNhanh(TAI_LIEU[ten].doan) };
  }
  ve();
  await guiDoanSangPython(true);
}

async function napHoSoDaLuu() {
  const d = coPython() ? await api('moi_doc_ho_so') : null;
  if (!d || !d.hoSo || !d.hoSo.length) return;   // lần chạy đầu: dùng hồ sơ mẫu

  const tabs = {}, dangXem = {};
  d.hoSo.forEach((h, i) => { tabs[i] = h.tep.slice(); dangXem[i] = h.dangXem || 0; });

  /* Dung lai kho mau ghep theo tung ho so. Phai chay TRUOC khi ve() lan dau,
     khong thi man Van ban ghep hien ban mac dinh mot nhip roi moi nhay sang ban
     that - va neu nguoi dung kip bam "Dong bo Live" trong nhip do thi no keo ve
     GOOGLE_SHEET_MAC_DINH chu khong phai Sheet cua ho. */
  if (typeof vbgNapTuHoSo === 'function') {
    vbgNapTuHoSo(d.hoSo, d.dangDung || 0);
  }

  // Khôi phục nội dung các tab đã lưu (văn bản ghép, tab tự tạo)
  if (d.noiDung) {
    Object.keys(d.noiDung).forEach((ten) => {
      if (d.noiDung[ten] && (!TAI_LIEU[ten] || !TAI_LIEU[ten].doan || !TAI_LIEU[ten].doan.length)) {
        TAI_LIEU[ten] = d.noiDung[ten];
      }
    });
  }

  S = { ...S,
        profiles: d.hoSo.map((h) => ({ ma: h.ma, ten: h.ten, giong: h.giong,
                                       chinh: h.chinh, tep: h.tep.slice(),
                                       ngonNgu: h.ngonNgu || 'vi',
                                       ngonNguNguon: h.ngonNguNguon || 'auto',
                                       phongCach: h.phongCach || 'Tự nhiên',
                                       giongTheoNgonNgu: h.giongTheoNgonNgu || {} })),
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
  const ten = tenTepDangXem(S);
  if (ten && TAI_LIEU[ten] && TAI_LIEU[ten].doan) {
    S = { ...S, ngonNguPhatHien: nhanDienNgonNguNhanh(TAI_LIEU[ten].doan) };
  }
  dongBoGiongSangPython();
  ve();
}

/* Thay danh sách giọng mock bằng giọng THẬT trên máy.

   GIONG là const nên không gán lại được — sửa tại chỗ. Cố ý: mọi nơi khác đã
   giữ tham chiếu tới mảng này rồi, gán lại là chúng trỏ vào mảng cũ. */
function datGiongThat(kq) {
  if (!kq || !kq.giong || !kq.giong.length) return;

  GIONG.length = 0;
  kq.giong.forEach((g) => {
    const moTa = g.mo_ta || g.ngan || g.moTa || '';
    GIONG.push({
      ...g,
      ma: g.id || g.ma,
      ten: g.ten || g.id || '',
      moTa: moTa,
      ngan: moTa,
      ngonNgu: g.ngon_ngu || g.ngonNgu || 'vi',
      daNgonNgu: Boolean(g.da_ngon_ngu)
    });
  });
  GIONG_TRONG_DROPDOWN.length = 0;
  GIONG.forEach((g) => GIONG_TRONG_DROPDOWN.push(g.id || g.ma));

  const norm = (s) => (s || '').toLowerCase().replace(/[-_\s]/g, '');
  const timGiong = (giongId, fallbackId) => {
    if (!giongId) return fallbackId || GIONG[0].ma;
    const idNorm = norm(giongId);
    const found = GIONG.find((g) => g.ma === giongId || g.ten === giongId || norm(g.ma) === idNorm || norm(g.ten) === idNorm);
    if (found) return found.ma;
    if (fallbackId) {
      const fbNorm = norm(fallbackId);
      const foundFb = GIONG.find((g) => g.ma === fallbackId || g.ten === fallbackId || norm(g.ma) === fbNorm || norm(g.ten) === fbNorm);
      if (foundFb) return foundFb.ma;
    }
    return GIONG[0].ma;
  };

  const GIONG_HO_SO_MAC_DINH = {
    'bai-viet': 'Ngọc Linh',
    'thong-bao': 'Xuân Vĩnh',
    'sach-noi': 'Phạm Tuyên',
    'cong-duc': 'Minh Đức',
    'ban-hang': 'Trúc Ly',
    'phap-quy': 'Xuân Vĩnh',
  };

  dat({
    ...S,
    profiles: S.profiles.map((h) => {
      const fb = GIONG_HO_SO_MAC_DINH[h.ma] || (HO_SO.find((m) => m.ma === h.ma || m.ten === h.ten) || {}).giong;
      const giongMoi = timGiong(h.giong, fb);
      return { ...h, giong: giongMoi };
    })
  });
  dongBoGiongSangPython();
}

/* Engine đọc bằng giọng trong cfg của Python, còn giao diện hiện giọng của hồ
   sơ. Hai bên phải khớp, không thì cột phải ghi một giọng mà loa đọc giọng
   khác. Gửi sang mỗi khi giọng của hồ sơ đang dùng đổi — kể cả lúc vừa mở
   chương trình, vì cfg lúc đó đang mang giọng đọc từ cauhinh.ini của bản cũ. */
let giongDaGui = '';
let ngonNguNguonDaGui = '';
let ngonNguDichDaGui = '';
let phongCachDaGui = '';

function dongBoGiongSangPython() {
  const h = hoSoDangDung(S);
  if (!coPython() || !h) return;
  if (h.giong && h.giong !== giongDaGui) {
    giongDaGui = h.giong;
    api('doi_giong', h.giong);
  }
  const nguon = h.ngonNguNguon || 'auto';
  const dich = h.ngonNgu || 'vi';
  if (nguon !== ngonNguNguonDaGui || dich !== ngonNguDichDaGui) {
    ngonNguNguonDaGui = nguon;
    ngonNguDichDaGui = dich;
    api('moi_dat_ngon_ngu', nguon, dich);
  }
  if (h.phongCach && h.phongCach !== phongCachDaGui) {
    phongCachDaGui = h.phongCach;
    api('moi_dat_phong_cach', h.phongCach);
  }
  guiChinhAm();
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

const GOI_Y_VIET_TAT = {
  'UBND': ['Uỷ ban nhân dân'],
  'HĐND': ['Hội đồng nhân dân'],
  'TP': ['Thành phố'],
  'TPHCM': ['Thành phố Hồ Chí Minh'],
  'TP.HCM': ['Thành phố Hồ Chí Minh'],
  'HN': ['Hà Nội'],
  'BGDĐT': ['Bộ Giáo dục và Đào tạo'],
  'BGD&ĐT': ['Bộ Giáo dục và Đào tạo'],
  'BYT': ['Bộ Y tế'],
  'BCA': ['Bộ Công an'],
  'BQP': ['Bộ Quốc phòng'],
  'CSGT': ['Cảnh sát giao thông'],
  'USD': ['đô la Mỹ'],
  'VND': ['Việt Nam đồng', 'đồng'],
  'EUR': ['ơ-rô'],
  'KM': ['ki-lô-mét', 'cây số'],
  'KG': ['ki-lô-gam', 'cân'],
  'HA': ['héc-ta'],
  'M2': ['mét vuông'],
  'M3': ['mét khối'],
  'PGS': ['Phó Giáo sư'],
  'TS': ['Tiến sĩ'],
  'THS': ['Thạc sĩ'],
  'BS': ['Bác sĩ'],
  'CLB': ['Câu lạc bộ'],
  'THPT': ['Trung học phổ thông'],
  'THCS': ['Trung học cơ sở'],
  'ĐH': ['Đại học'],
  'CĐ': ['Cao đẳng'],
  'NXB': ['Nhà xuất bản'],
  'TW': ['Trung ương'],
  'TNHH': ['Trách nhiệm hữu hạn'],
  'CP': ['Cổ phần'],
  'KCN': ['Khu công nghiệp'],
  'TT': ['Thị trấn', 'Trung tâm', 'Thủ tướng'],
  'QL': ['Quốc lộ'],
  'XKLĐ': ['Xuất khẩu lao động'],
  'TĐC': ['Tái định cư'],
  'BHXH': ['Bảo hiểm xã hội'],
  'BHYT': ['Bảo hiểm y tế'],
  'CNTT': ['Công nghệ thông tin'],
  'ATGT': ['An toàn giao thông'],
  'PCCC': ['Phòng cháy chữa cháy']
};

function moHopDayTuPhatAm(tu) {
  if (!tu) return;
  const tuUpper = String(tu).trim().toUpperCase();
  const goiY = GOI_Y_VIET_TAT[tuUpper] || GOI_Y_VIET_TAT[tu] || [];
  dat({
    ...S,
    dayTuOpen: {
      tu,
      doc: goiY.length ? goiY[0] : '',
      goiY
    }
  });
}

function locKyTuLa(text) {
  return String(text || '')
    .replace(/[\u200b-\u200d\ufeff\u00ad]/g, '')
    .replace(/[^\x20-\x7E\u00A0-\u024F\u1EA0-\u1EF9.,;:!?\-–—/()\[\]{}'\"“”‘’…%+*&@#°²³\s\n\r]/g, ' ')
    .replace(/\s{2,}/g, ' ')
    .trim();
}

async function lamSachKyTuDoan(soDoan) {
  const ten = tenTepDangXem(S);
  const t = TAI_LIEU[ten];
  if (!t || !t.doan || !t.doan[soDoan - 1]) return;
  ghiLichSu(ten, t.doan);
  const cu = t.doan[soDoan - 1].chu;
  const moi = locKyTuLa(cu);
  t.doan[soDoan - 1].chu = moi;
  danhDauSua();
  await guiDoanSangPython(true);
  duLieuSoat = await api('moi_soat');
  dat({ ...S });
  moBao(`Đã làm sạch ký tự lạ ở đoạn ${soDoan}.`, 'Soát văn bản');
}

async function lamSachKyTuTatCa() {
  const ten = tenTepDangXem(S);
  const t = TAI_LIEU[ten];
  if (!t || !t.doan) return;
  ghiLichSu(ten, t.doan);
  let dem = 0;
  t.doan.forEach((d) => {
    const cu = d.chu;
    const moi = locKyTuLa(cu);
    if (cu !== moi) {
      d.chu = moi;
      dem++;
    }
  });
  if (dem === 0) {
    moBao('Văn bản không có ký tự lạ nào cần làm sạch.');
    return;
  }
  danhDauSua();
  await guiDoanSangPython(true);
  duLieuSoat = await api('moi_soat');
  dat({ ...S });
  moBao(`Đã làm sạch ký tự lạ ở ${dem} đoạn.`, 'Soát văn bản');
}

/** Thêm một chữ viết tắt vào từ điển phát âm, ngay từ màn soát. */
function themVaoTuDien(tu) {
  return moHopDayTuPhatAm(tu);
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

/* Nhân bản giọng riêng qua Wizard 3 bước. Chạy nền vài phút; Python đẩy tiến độ về qua
   window.gd.tienDoGiong / giongXong / giongLoi. */
function nhanBanGiong() {
  if (S.dangNhanBan) return;
  dat({
    ...dongHetMenu(S),
    nhanBanWizard: {
      buoc: 1,
      theLoai: 'kiemhiep',
      tenGiong: 'Giọng Kiếm Hiệp',
      fileDaChon: '',
      daNgonNgu: false
    }
  });
}

datKhiNhanBanGiong(
  (msg) => {
    if (S.dangNhanBan) {
      dat({
        ...S,
        tienDoGiong: msg,
        nhanBanWizard: S.nhanBanWizard && S.nhanBanWizard.dangTao ? {
          ...S.nhanBanWizard,
          tienDo: msg
        } : S.nhanBanWizard
      });
    }
  },
  async (ten) => {
    /* Nạp lại DANH SÁCH GIỌNG, không chỉ thư viện. Hai thứ khác nhau:
       moi_thu_vien_giong đổ vào duLieuGiong (màn Thư viện giọng), còn ô "Giọng
       đọc" ở cột phải đọc từ GIONG - thứ chỉ datGiongThat mới đặt được. Thiếu
       lượt này thì người dùng ngồi đợi máy học giọng con cháu mình mấy phút,
       bấm "Dùng giọng này", rồi cột phải vẫn trơ tên giọng CŨ. */
    datGiongThat(await api('moi_danh_sach_giong'));
    duLieuGiong = await api('moi_thu_vien_giong', hoSoDangDung(S).giong);
    const gMoi = (duLieuGiong && duLieuGiong.cuaToi || []).find((x) => x.ten === ten)
      || (duLieuGiong && duLieuGiong.cuaToi && duLieuGiong.cuaToi[duLieuGiong.cuaToi.length - 1]);
    const idMoi = gMoi ? gMoi.id : '';
    /* null = Python không đo được độ khớp. Không bịa số thay: bản trước rơi về
       98.6 nên màn hình lúc nào cũng khoe một con số đẹp, kể cả khi phép đo
       chưa từng chạy. Không có số thì không nói gì về độ khớp. */
    const doKhop = (gMoi && typeof gMoi.do_khop === 'number') ? gMoi.do_khop : null;

    if (S.nhanBanWizard && S.nhanBanWizard.dangTao) {
      dat({
        ...S,
        dangNhanBan: false,
        tienDoGiong: '',
        nhanBanWizard: {
          ...S.nhanBanWizard,
          buoc: 5,
          dangTao: false,
          tenGiong: ten,
          idMoi: idMoi,
          doKhop: doKhop
        }
      });
    } else {
      dat({ ...S, dangNhanBan: false, tienDoGiong: '' });
      moBao(doKhop === null
        ? `Đã tạo xong “${ten}”. Bấm Nghe thử để nghe.`
        : `Đã tạo xong “${ten}” (Độ khớp: ${doKhop}%). Bấm Nghe thử để nghe.`);
    }
  },
  (msg) => {
    if (S.nhanBanWizard && S.nhanBanWizard.dangTao) {
      dat({
        ...S,
        dangNhanBan: false,
        tienDoGiong: '',
        nhanBanWizard: {
          ...S.nhanBanWizard,
          buoc: 3,
          dangTao: false,
          loiMsg: msg
        }
      });
    } else {
      dat({ ...S, dangNhanBan: false, tienDoGiong: '' });
    }
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
  const [caiDat, cInfo] = await Promise.all([
    api('moi_cai_dat'),
    api('moi_thong_tin_cache')
  ]);
  if (!caiDat) { moBao('Chưa đọc được cài đặt.'); return; }
  duLieuCaiDat = caiDat;
  dat({
    ...dongHetMenu(S),
    man: 'caidat',
    cacheInfo: cInfo || { dungLuongMB: 0, soTep: 0, gioiHanMB: 150 },
    thongBaoCache: ''
  });
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
  const bangEl = document.querySelector('.tudien .soat__bang');
  if (bangEl && typeof veHangTu === 'function') {
    const muc = (duLieuTuDien && duLieuTuDien.muc) || [];
    bangEl.innerHTML = `<div class="soat__hang soat__hang--dau">
        <span class="tudien__c1">Từ trong văn bản</span>
        <span class="tudien__c2">Đọc thành</span>
        <span class="tudien__c3">Hành động</span>
      </div>
      ${muc.length ? muc.map(veHangTu).join('')
        : `<div class="giongkho__trong">${
            S.tuDienTim ? 'Không tìm thấy mục nào khớp.'
                        : 'Từ điển đang trống. Bấm “Thêm từ” để dạy máy đọc.'}</div>`}`;
  }
  const phuEl = document.querySelector('.tudien .soat__phu');
  if (phuEl && duLieuTuDien) {
    phuEl.textContent = `${duLieuTuDien.hienThi || 0}/${duLieuTuDien.tong || 0} mục${
      duLieuTuDien.rieng ? ` · ${duLieuTuDien.rieng} mục anh tự thêm` : ''}`;
  }
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
  // Hạ cờ nghe thử khi mẫu phát xong (chỉ hạ nếu đúng mã giọng đang nghe hoặc ma rỗng)
  if (!ma || !S.dangNgheThu || S.dangNgheThu === ma) {
    dat({ ...S, dangNgheThu: '', mauDangPhat: false });
  }
});


datKhiBaoLoi((tieuDe, chiTiet) => {
  // Lỗi lúc nghe thử: hạ nút rồi nói cho người dùng biết. Trước đây chỉ ghi vào
  // console — người dùng ngồi nhìn nút sáng, không hiểu vì sao không có tiếng.
  dat({ ...S, dangNgheThu: '', mauDangPhat: false });
  moBao(chiTiet || tieuDe || 'Máy đọc gặp lỗi, chưa phát được.');
});

/* BẮT BUỘC gọi moi_khoi_dong hoặc moi_khoi_dong_toan_dien: nó nạp danh sách giọng và BẬT MÔ HÌNH. Thiếu
   dòng này thì mọi thứ vẽ ra vẫn đẹp mà bấm Nghe không ra tiếng, vì mô hình
   chưa bao giờ được khởi động. Đã vấp đúng lỗi này một lần. */
async function khoiDong() {
  if (!coPython()) return;
  try {
    const startup = await api('moi_khoi_dong_toan_dien');
    if (startup && startup.giong) {
      if (startup.hoSo && startup.hoSo.hoSo && startup.hoSo.hoSo.length) {
        const d = startup.hoSo;
        const tabs = {}, dangXem = {};
        d.hoSo.forEach((h, i) => { tabs[i] = h.tep.slice(); dangXem[i] = h.dangXem || 0; });
        /* Duong khoi dong NHANH nay khong di qua napHoSoDaLuu(), nen phai dung
           lai kho mau ghep o day nua - neu khong thi ban .exe that khong bao gio
           khoi phuc duoc, chi duong lui moi khoi phuc. */
        if (typeof vbgNapTuHoSo === 'function') {
          vbgNapTuHoSo(d.hoSo, d.dangDung || 0);
        }
        if (d.noiDung) {
          Object.keys(d.noiDung).forEach((ten) => {
            if (d.noiDung[ten] && (!TAI_LIEU[ten] || !TAI_LIEU[ten].doan || !TAI_LIEU[ten].doan.length)) {
              TAI_LIEU[ten] = d.noiDung[ten];
            }
          });
        }
        S = { ...S,
              profiles: d.hoSo.map((h) => ({ ma: h.ma, ten: h.ten, giong: h.giong,
                                             chinh: h.chinh, tep: h.tep.slice(),
                                             ngonNgu: h.ngonNgu || 'vi',
                                             ngonNguNguon: h.ngonNguNguon || 'auto',
                                             phongCach: h.phongCach || 'Tự nhiên',
                                             giongTheoNgonNgu: h.giongTheoNgonNgu || {} })),
              tabsByProfile: tabs,
              activeByProfile: dangXem,
              profile: Math.min(d.dangDung || 0, d.hoSo.length - 1),
              theme: d.theme === 'toi' ? 'toi' : 'sang',
              zoom: d.zoom || 100,
              chips: d.the || {},
              duongDanTep: d.duongDan || {},
              loaiTep: d.loaiTep || {},
              pos: 1, sel: 1, view: 'san_sang' };
        chuKyDaLuu = JSON.stringify(phanCanLuu());
        await moLaiTepDangXem();
        const ten = tenTepDangXem(S);
        if (ten && TAI_LIEU[ten] && TAI_LIEU[ten].doan) {
          S = { ...S, ngonNguPhatHien: nhanDienNgonNguNhanh(TAI_LIEU[ten].doan) };
        }
      }
      datGiongThat({ giong: startup.giong });
      await guiDoanSangPython();
      await capNhatNutCuaSo();
      return;
    }
  } catch (e) {
    // Fallback an toàn sang đường đọc tuần tự
  }
  // Fallback nếu startup không trả về gói toàn diện
  await napHoSoDaLuu();
  datGiongThat(await api('moi_khoi_dong'));
  await guiDoanSangPython();
  await capNhatNutCuaSo();      // nút giữa phải đúng ngay từ lúc mở
}
window.addEventListener('pywebviewready', khoiDong);

ve();
khoiDong();
