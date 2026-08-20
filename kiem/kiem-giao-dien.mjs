/* Chạy giao-dien.js trong DOM giả để bắt lỗi tham chiếu và kiểm HTML dựng ra
   có đúng đặc tả không — không cần mở trình duyệt.

   Chạy:  node ui-moi/kiem-giao-dien.mjs
   Không thay được việc nhìn tận mắt, nhưng bắt được mọi lỗi "undefined is not
   a function" trước khi phiền người dùng mở cửa sổ. */

import { readFileSync } from 'fs';
import { createContext, runInContext } from 'vm';
import { fileURLToPath } from 'url';
import { dirname, join } from 'path';

const DIR = dirname(fileURLToPath(import.meta.url));
// Bộ kiểm nằm trong kiem/, mã nguồn giao diện ở ui-moi/ bên cạnh.
const UI = join(DIR, '..', 'ui-moi');
let HTML = '';
let batSuKien = {};

function nutGia(id = '') {
  return {
    id, dataset: {}, style: {}, classList: { toggle() {}, add() {}, remove() {} },
    // select() có mặt vì <input> thật luôn có — thiếu nó thì bài kiểm đỏ ở chỗ
    // sản phẩm chạy tốt, tức là DOM giả nói dối chứ không phải mã nguồn sai.
    scrollTop: 0, value: '', focus() {}, select() {}, remove() {}, appendChild() {},
    querySelector: () => nutGia(), querySelectorAll: () => [],
    getBoundingClientRect: () => ({ left: 0, width: 200 }),
    set innerHTML(v) { if (this.id === 'goc') HTML = v; }, get innerHTML() { return ''; },
    set onchange(f) {}, set onclick(f) {},
  };
}

const ctx = {
  console,
  setInterval: () => 0, clearInterval() {}, setTimeout: () => 0,
  location: { search: '' },
  URLSearchParams,
  document: {
    documentElement: { dataset: {}, style: { setProperty() {}, removeProperty() {} } },
    body: { appendChild() {} },
    activeElement: { tagName: 'DIV' },
    querySelector: (s) => {
      if (s === '#goc') return ctx.__goc;
      if (s === '#cuon') return null;
      /* Trả phần tử BIẾT nó thuộc đoạn nào khi selector có [data-doan="N"].
         doanGoDuoc() lấy phần tử rồi hỏi ngược .closest('[data-doan]') để biết
         số đoạn; trả một nút vô danh là chuỗi ấy đứt ngay. */
      const m = /\[data-doan="(\d+)"\]/.exec(s);
      if (m) {
        const n = m[1];
        const el = nutGia();
        el.textContent = 'chữ giả';
        el.closest = (q) => (q === '[data-doan]' ? { dataset: { doan: n } } : null);
        return el;
      }
      return nutGia();
    },
    // Đường vẽ nhẹ (veNhipDoc) hứng danh sách đoạn qua đây.
    querySelectorAll: () => [],
    getElementById: () => null,
    createElement: () => nutGia(),
    // datCaret() dựng Range để đặt con trỏ; thiếu cái này là phép kiểm gõ phím
    // thật ném lỗi ngay ở lần gộp đoạn đầu tiên.
    createRange: () => ({
      setStart() {}, setEnd() {}, collapse() {}, selectNodeContents() {},
      toString: () => '',
    }),
    addEventListener: (t, f) => { batSuKien[t] = f; },
  },
  window: { addEventListener() {} },
  localStorage: { getItem: () => null, setItem() {} },
  module: undefined,
};
ctx.__goc = nutGia('goc');
ctx.globalThis = ctx;
createContext(ctx);

// Đúng thứ tự index.html khai, để bộ kiểm gặp cùng cảnh mà cửa sổ thật gặp.
for (const f of ['du-lieu-mau.js', 'trang-thai.js', 'tinh-huong.js', 'cau-noi.js',
                 'hop-thoai.js', 'man-soat.js', 'man-giong.js', 'man-tudien.js',
                 'man-caidat.js', 'giao-dien.js']) {
  runInContext(readFileSync(join(UI, f), 'utf8'), ctx, { filename: f });
}

let loi = 0;
const ok = (dk, nhan, them = '') => {
  console.log(`  ${dk ? 'ĐẠT ' : 'LỆCH'} ${nhan}${them ? '  →  ' + them : ''}`);
  if (!dk) loi++;
};
const co = (s) => HTML.includes(s);
const dem = (s) => HTML.split(s).length - 1;

/* `const` cấp cao nhất trong vm nằm ở phạm vi script, KHÔNG thành thuộc tính
   của object ngữ cảnh - nên phải chạy biểu thức bên trong ngữ cảnh mới với
   tới được S, dat(), doiHoSo()… */
const chay = (ma) => runInContext(ma, ctx, { filename: 'kiem' });

/* GÕ PHÍM THẬT vào handler keydown, thay vì grep mã nguồn tìm dòng chữ.

   Grep chỉ chứng minh trong tệp CÓ dòng ấy - nó xanh kể cả khi nhánh không bao
   giờ chạy tới, khi điều kiện phía trên đã return, hay khi một quy tắc khác
   nuốt mất phím. Ba lần tôi kết luận sai trong phiên này đều có bộ kiểm xanh
   kèm theo, và đều vì canh dấu hiệu thay vì canh hành vi.

   `vt` là vị trí con trỏ trong đoạn; `chu` là chữ của đoạn đang gõ. */
function goPhim(soDoan, phim, { vt = 0, chu = 'abc', ...them } = {}) {
  const o = {
    nodeType: 1, tagName: 'SPAN', isContentEditable: true, textContent: chu,
    classList: { contains: (c) => c === 'doan__chu' },
    closest: (s) => (s === '[data-doan]' ? { dataset: { doan: String(soDoan) } } : null),
    focus() {}, blur() {},
  };
  ctx.document.activeElement = o;
  ctx.window.getSelection = () => ({
    isCollapsed: true, rangeCount: 1,
    getRangeAt: () => ({
      endContainer: o, endOffset: vt,
      cloneRange: () => ({
        selectNodeContents() {}, setEnd() {}, toString: () => chu.slice(0, vt),
      }),
    }),
    removeAllRanges() {}, addRange() {},
  });
  let daChan = false;
  batSuKien.keydown({ key: phim, ...them, preventDefault: () => { daChan = true; } });
  ctx.document.activeElement = { tagName: 'DIV' };
  return daChan;                       // có chặn hành vi mặc định hay không
}

/* BẤM CHUỘT THẬT vào handler click, cùng lý lẽ với goPhim: canh hành vi chứ
   không canh dấu hiệu. `dat()` chạy đồng bộ ngay đầu chuyenSang() nên trạng
   thái đã đổi khi hàm này trả về, dù phần đuôi của chuyenSang còn chờ Python. */
function bam(sel, ds = {}) {
  const nut = { dataset: ds, closest: (s) => (s === sel ? nut : null) };
  let daChan = false;
  batSuKien.click({
    target: nut,
    stopPropagation() { daChan = true; },
    preventDefault() {},
  });
  return daChan;
}

console.log('--- A. Khung dọc đủ 8 tầng ---');
// Dải tab ngang đã bỏ theo bản thiết kế; danh sách tệp chuyển vào cột trái.
// Canh luôn rằng nó KHÔNG mọc lại, không thì gỡ xong lại có người dựng lại.
for (const [cls, ten] of [['tieude', 'thanh tiêu đề'], ['menu', 'thanh menu'],
  ['congcu', 'thanh công cụ'], ['thanchinh', 'vùng ba cột'],
  ['trai', 'cột trái'], ['doc', 'vùng đọc'], ['phai', 'cột phải'],
  ['trangthai', 'thanh trạng thái']]) {
  ok(co(`class="${cls}`) || co(` ${cls}"`) || co(`"${cls}"`), ten);
}
ok(!co('class="daitab') && !co('data-tab=') && !co('id="themTab"'),
   'KHÔNG còn dải tab ngang — danh sách tệp nằm trong cột trái');

console.log('\n--- B. Thanh công cụ đúng đặc tả ---');
ok(co('Dán văn bản') && HTML.indexOf('Dán văn bản') < HTML.indexOf('Mở file'),
   'Dán văn bản đứng TRƯỚC Mở file');
ok(co('Soát văn bản'), 'có Soát văn bản');
ok(co('Thẻ cảm xúc'), 'có Thẻ cảm xúc');
ok(co('Tìm và thay thế'), 'nút kính lúp có NHÃN CHỮ');
ok(!co('Xem trước chuẩn hoá'), 'KHÔNG còn Xem trước chuẩn hoá');
ok(!co('i-more') && !co('data-lenh="…"'), 'KHÔNG còn nút …');
ok(co('Nghe toàn bộ') && co('Xuất file âm thanh'), 'có cặp Nghe / Xuất');
ok(HTML.indexOf('nut--acc nut--cao') > 0, 'chỉ Xuất là nút accent');

console.log('\n--- C. Vùng đọc ---');
ok(/\d+ từ · 15 đoạn/.test(HTML), 'dòng thống kê',
   (HTML.match(/\d+ từ · \d+ đoạn · khoảng [^<]+/) || [''])[0]);
/* Gợi ý phải tả đúng thao tác đang có. Máng số đã thôi làm nút, nên câu cũ
   "Bấm số đoạn..." là chỉ đường sai - canh để nó không lẻn về. */
ok(co('Bấm vào chữ để sửa như Notepad · nút ▶ bên phải để nghe riêng đoạn'),
   'gợi ý bên phải đầu vùng đọc');
ok(!co('Bấm số đoạn'), 'KHÔNG còn gợi ý cũ bảo bấm vào số đoạn');
ok(!co('THỜI LƯỢNG') && !co('doan__dur'), 'KHÔNG còn cột/nhãn thời lượng');
ok(dem('data-doan=') === 15, '15 đoạn, KHÔNG còn dòng trống đánh số',
   String(dem('data-doan=')));
ok(co('doan--tieude'), 'có đoạn tiêu đề');
ok(!co('doan--trong'), 'KHÔNG còn đoạn rỗng nào - bản thiết kế cấm dòng trống đánh số');
ok(co('[hắng giọng]'), 'thẻ cảm xúc hiện ra');
/* Nghe riêng đoạn nay đi bằng nút ▶ nổi bên phải mỗi dòng, hiện lúc đưa chuột
   vào. Máng số trở lại đúng vai bản mẫu: chỉ là số, KHÔNG phải nút — nên nó
   không được mang data-nghe nữa, không thì lại thành hai nút chồng vai. */
ok(/<button class="doan__play"[\s\S]*?data-nghe="\d+"/.test(HTML), 'mỗi đoạn có nút ▶ riêng');
ok(co('Nghe riêng đoạn này, nghe hết đoạn thì dừng'),
   'mách nước nút ▶ đúng nguyên văn bản mẫu');
ok(!/class="doan__so[^"]*"[^>]*data-nghe/.test(HTML), 'máng số KHÔNG còn là nút');
ok(!co('doc__nghe'), 'KHÔNG còn nút Nghe đoạn ở thanh trên');
/* Dòng trống không có chữ để đọc; treo nút ở đó là bày nút bấm ra lỗi.
   Đếm thẳng từ HTML chứ không viết cứng con số - tài liệu mẫu đổi một dòng là
   phép kiểm viết cứng đỏ oan, mà đọc dòng đỏ ấy lại tưởng mã hỏng. */
const soDoanVe = (HTML.match(/data-doan=/g) || []).length;
const soTrongVe = (HTML.match(/doan--trong/g) || []).length;
const soPlayVe = (HTML.match(/doan__play/g) || []).length;
ok(soPlayVe === soDoanVe - soTrongVe,
   `dòng trống không có nút ▶ (${soDoanVe} đoạn, ${soTrongVe} trống)`,
   `${soPlayVe} nút`);

/* Dáng vẻ nút nằm bên CSS nên HTML không nói được, phải soi thẳng tệp. */
const CSS_CHINH = readFileSync(join(UI, 'man-hinh-chinh.css'), 'utf8');
ok(/\.doan__play\s*\{[^}]*position:\s*absolute/.test(CSS_CHINH), 'nút ▶ nổi trên nội dung');
ok(/\.doan__play\s*\{[^}]*top:\s*50%/.test(CSS_CHINH)
   && /\.doan__play\s*\{[^}]*translateY\(-50%\)/.test(CSS_CHINH),
   'nút ▶ canh giữa theo chiều cao đoạn');
ok(/\.doan__play\s*\{[^}]*right:\s*\d/.test(CSS_CHINH), 'nút ▶ nằm sát mép phải');
ok(/\.doan__play\s*\{[^}]*opacity:\s*0\b/.test(CSS_CHINH)
   && /\.doan:hover\s+\.doan__play\s*\{[^}]*opacity:\s*1/.test(CSS_CHINH),
   'nút ▶ ẩn sẵn, hiện khi đưa chuột vào đoạn');
ok(/\.doan__play\s*\{[^}]*z-index/.test(CSS_CHINH), 'nút ▶ nằm trên nội dung');
/* Dáng phải theo ngôn ngữ PHẲNG của app (xem .roi__nghe). Bản đầu tròn 50% có
   viền có bóng, nhìn ra ngay là rời rạc - canh để nó không lẻn về. */
ok(!/\.doan__play\s*\{[^}]*border-radius:\s*50%/.test(CSS_CHINH)
   && !/\.doan__play\s*\{[^}]*box-shadow/.test(CSS_CHINH),
   'nút ▶ giữ dáng phẳng: không bo tròn hẳn, không bóng đổ');

/* Nền đặc dưới nút đẻ ra một Ô TRẮNG giữa dòng, vì nền dòng lúc rê chuột là
   --sub-h chứ không phải --layer. Đã thử và hỏng đúng thế. Nút phải trong
   suốt; nền lúc rê vào nút thì dùng rgba (--acc-soft) nên chồng nền nào cũng
   hoà. Dải mờ dần cũng bỏ - nó chính là mảng trắng thứ hai. */
ok(/\.doan__play\s*\{[^}]*background:\s*transparent/.test(CSS_CHINH),
   'nút ▶ trong suốt, KHÔNG đục ra ô trắng giữa dòng');
ok(!/\.doan__play::before/.test(CSS_CHINH), 'KHÔNG còn dải mờ dần');
ok(/\.doan__play:hover\s*\{[^}]*var\(--acc-soft\)/.test(CSS_CHINH),
   'rê vào nút thì nền là màu rgba hoà được với mọi nền dòng');
/* Chữ chạy hết bề ngang ô. Chỗ tránh nút nay là padding-right chứ không phải
   trần 700px - bỏ trần mà quên chừa chỗ là nút đè lên chữ ngay. */
ok(!/\.doan__than\s*\{[^}]*max-width/.test(CSS_CHINH),
   'chữ chạy hết bề ngang ô, không chặn ở 700px');
ok(/\.doan__than\s*\{[^}]*padding-right:\s*(4[6-9]|[5-9]\d)px/.test(CSS_CHINH),
   'vùng chữ chừa đủ chỗ bên phải cho nút ▶');

/* Nhịp đọc chuyển đoạn bằng cách gạt lớp, KHÔNG dựng lại DOM. Ký hiệu nút phải
   do CSS vẽ theo lớp, viết vào HTML là đoạn sang lượt đọc vẫn trơ hình ▶. */
ok(/\.doan__play::after\s*\{[^}]*content:\s*'▶'/.test(CSS_CHINH)
   && /\.doan\.dang-doc\s+\.doan__play::after\s*\{[^}]*content:\s*'❚❚'/.test(CSS_CHINH)
   && /\.doan\.tam-dung\s+\.doan__play::after\s*\{[^}]*content:\s*'▶'/.test(CSS_CHINH),
   'nút theo chuẩn trình phát: đang đọc thành tạm dừng, tạm dừng thành phát');
ok(/\.doan\.dang-doc\s+\.doan__play,\s*\.doan\.dang-tao\s+\.doan__play\s*\{[^}]*opacity:\s*1/.test(CSS_CHINH),
   'đoạn đang đọc hoặc đang tạo âm thanh thì nút hiện sẵn, có viền accent');
ok(/S\.view === 'dang_doc' && soDoan === S\.pos\) return LENH\['Tạm dừng'\]/
   .test(readFileSync(join(UI, 'giao-dien.js'), 'utf8')),
   'bấm nút ở đoạn đang đọc thì TẠM DỪNG theo chuẩn trình phát');

/* HỌ LỖI: kích thước CỨNG gặp nội dung do người dùng nhập thì sớm muộn cũng vỡ.
   Hàng bảng Soát tab 2 đựng nguyên đoạn văn - để height cứng là chữ tràn ra
   ngoài hàng và đè lên hàng dưới, chủ dự án mở bản .exe gặp ngay. */
const CSS_SOAT = readFileSync(join(UI, 'man-soat.css'), 'utf8');
ok(/\.soat__hang\s*\{[\s\S]*?min-height:\s*38px/.test(CSS_SOAT),
   'hàng bảng Soát dùng min-height');
ok(!/[^-]height:\s*38px/.test(CSS_SOAT),
   'KHÔNG còn chiều cao cứng 38px ở bảng Soát (chữ dài sẽ đè lên nhau)');
ok(/\.soat__bang--doi\s+\.soat__hang\s*\{[^}]*align-items:\s*flex-start/.test(CSS_SOAT),
   'bảng hai cột canh chữ từ trên xuống, không để hai cột so le');
ok(/\.doan__so\s*\{[^}]*cursor:\s*default/.test(CSS_CHINH), 'máng số trở lại con trỏ thường');

/* ---- HỌ LỖI KHOÁ PHÁT TIẾNG ----------------------------------------------
   Từng có ba đường vào việc phát (máng số · nút Nghe đoạn · phím Space) mà
   chỉ nút Nghe toàn bộ bị khoá; hai đường kia lọt, giao diện chạy màn "đang
   đọc" không có tiếng và không báo gì. Kiểm HÀNH VI bằng cách gọi thẳng hàm
   trong ngữ cảnh vừa chạy giao diện, không soi chuỗi mã. */
ok(chay('typeof lyDoKhoa') === 'function', 'có hàm lyDoKhoa dùng chung cho cả ba đường');
ok(chay('lyDoKhoa(S)') === '', 'lúc bình thường thì không khoá');

const viTai = chay("lyDoKhoa({ ...S, situation: 'giong_dang_tai' })");
ok(!!viTai && !viTai.includes('{giong}'),
   'giọng đang tải thì nêu lý do, đã thay {giong} bằng tên giọng', viTai);
ok(!!chay("lyDoKhoa({ ...S, situation: 'mat_ket_noi' })"), 'mất kết nối thì nêu lý do');
ok(!!chay("lyDoKhoa({ ...S, situation: 'het_luot' })"), 'hết lượt thì nêu lý do');

const doanKhoa = chay(
  "(() => { const cu = S; S = { ...S, situation: 'giong_dang_tai' };"
  + " const r = veDoan({ kieu: 'text', chu: 'thử' }, 3); S = cu; return r; })()");
ok(/class="doan__play la-khoa"/.test(doanKhoa), 'nút ▶ mang lớp la-khoa khi khoá');
ok(!doanKhoa.includes('Nghe riêng đoạn 3'), 'lúc khoá, mách nước đổi thành lý do thật');

ok(/\.doan__play\.la-khoa\s*\{[^}]*cursor:\s*not-allowed/.test(CSS_CHINH),
   'CSS: nút ▶ khoá đổi con trỏ');
ok(/\.doan__play\.la-khoa:hover\s*\{[^}]*background:\s*transparent/.test(CSS_CHINH),
   'CSS: khoá thì rê vào nút ▶ KHÔNG sáng lên mời bấm');

const JS_CHINH = readFileSync(join(UI, 'giao-dien.js'), 'utf8');
ok(/\[data-nghe\][\s\S]{0,1400}?lyDoKhoa\(S\)[\s\S]{0,200}?moBao/.test(JS_CHINH),
   'đường nút ▶ hỏi lyDoKhoa trước khi phát');
ok(/e\.key === ' '[\s\S]{0,600}?lyDoKhoa\(S\)[\s\S]{0,200}?moBao/.test(JS_CHINH),
   'phím Space hỏi lyDoKhoa trước khi phát');
ok(/\.then\(\(kq\)[\s\S]{0,200}?kq\.loi[\s\S]{0,200}?dungPhat\(\)/.test(JS_CHINH),
   'batDauPhat đọc lỗi Python trả về rồi dừng sạch, không để màn đang đọc chạy suông');

console.log('\n--- D. Cột phải ---');
ok(co('Hồ sơ đang dùng'), 'nhãn HỒ SƠ ĐANG DÙNG');
ok(co('Bài viết, văn bản'), 'tên hồ sơ');
ok(co('Giọng đọc') && co('Giọng Ngọc Linh'), 'nhãn GIỌNG ĐỌC + tên giọng');
ok(co('Điều chỉnh'), 'nhãn ĐIỀU CHỈNH');
ok(co('Theo mặc định của hồ sơ'), 'dòng tóm tắt khi đóng');
ok(co('Cần chú ý') && co('9 chỗ cần chú ý, trong đó 2 lỗi nên sửa trước khi xuất.'),
   'thẻ Cần chú ý, đúng câu tóm tắt');
ok(co('chuy__dem nang'), 'lỗi bắt buộc có nhãn đỏ');
ok(co('Từ điển phát âm ›'), 'liên kết Từ điển phát âm');

console.log('\n--- E. Cột trái ---');
ok(dem('data-hoso=') === 4, '4 hồ sơ', String(dem('data-hoso=')));
ok(co('Danh sách, biểu mẫu'), 'hồ sơ 4 đã đổi tên');
ok(co('Tạo hồ sơ mới'), 'nút Tạo hồ sơ mới');
ok(co('Thư viện giọng') && co('Cài đặt'), 'đáy cột có 2 mục');
ok(!/data-lenh="Từ điển phát âm"[^]*trai__chan/.test(HTML), 'Từ điển KHÔNG ở đáy cột trái');

console.log('\n--- F. Thanh trạng thái ---');
ok(/Đoạn \d+, Cột 1/.test(HTML), 'Đoạn N, Cột 1');
ok(co('VieNeu v3 Turbo · sẵn sàng'), 'nhãn máy đọc');
/* Trước đây chỗ này canh đúng chuỗi "Đã lưu 14:02" in cứng — tức canh chính một
   lời hứa suông: thanh trạng thái nói ĐÃ LƯU kể cả khi chưa lưu gì, và luôn là
   14:02. Bản mẫu ghi 14:02 chỉ để MINH HOẠ trạng thái "đã lưu lúc mấy giờ";
   sản phẩm phải in giờ thật. Nay canh ngược lại: không được có chuỗi cứng ấy. */
ok(!co('Đã lưu 14:02'), 'KHÔNG in cứng "Đã lưu 14:02"');
ok(co('Hồ sơ:'), 'thanh trạng thái vẫn nói hồ sơ đang dùng');
ok(!co('UTF-8') && !co('CRLF') && !co('100%</span>'), 'KHÔNG còn UTF-8 / CRLF / mức phóng to');

console.log('\n--- G. Cây tệp trong cột trái ---');
/* Đếm data-tep= chứ KHÔNG đếm 'class="tep'. Phép canh cũ đếm 'class="tab' và
   trúng cả tab__icon / tab__ten / tab__dong, nên MỘT tab đã cho 4 — nó xanh kể
   cả khi dải chỉ còn một tệp. Thuộc tính data- thì mỗi hàng đúng một cái. */
ok(dem('data-tep=') === 2, 'hồ sơ 1 bung ra đúng 2 hàng tệp', String(dem('data-tep=')));
ok(co('thongbao-quoc-khanh.txt'), 'tên tệp hiện trên hàng tệp');
ok(co('data-dongtep='), 'đóng được từng tệp');
ok(co('id="themTep"') && co('Thêm tệp'), 'có lối Thêm tệp');
ok(co('class="tepds"'), 'danh sách tệp lồng trong cột trái');
// Chỉ hồ sơ ĐANG CHỌN mới bung danh sách tệp. Bốn hồ sơ mà bung cả bốn thì cột
// trái dài ra theo số tệp của hồ sơ người dùng không xem — đúng thứ bản thiết
// kế nêu tên để tránh.
ok(dem('class="tepds"') === 1, 'chỉ MỘT hồ sơ bung danh sách tệp', String(dem('class="tepds"')));
ok(dem('class="tep dang-xem"') === 1, 'đúng một hàng tệp được đánh dấu đang xem',
   String(dem('class="tep dang-xem"')));

/* Hàng tệp phải nằm NGOÀI thẻ .hoso. .hoso là <button>, mà HTML cấm nút lồng
   trong nút: trình duyệt tự đẩy nút × ra ngoài và cú bấm rơi nhầm chỗ. Đứng
   ngoài cũng tránh [data-hoso] nuốt mất cú bấm, vì closest() đi ngược lên cây. */
{
  const iHoso = HTML.indexOf('data-hoso="0"');
  const iDong = HTML.indexOf('</button>', iHoso);
  const iCum = HTML.indexOf('class="tepds"');
  ok(iCum > iDong, 'cụm tệp bắt đầu SAU khi thẻ .hoso đã đóng — không nút lồng nút');
}

/* Ba mục dưới đây ĐỔI THẬT danh sách tệp, nên phải trả trạng thái về chỗ cũ khi
   xong. Không trả là các mục sau chạy trên một tài liệu rỗng và đỏ lên vì lý do
   chẳng liên quan gì tới thứ chúng canh — đã vấp đúng thế một lần lúc viết. */
chay('globalThis.__Scu = S');
// TAI_LIEU là object toàn cục bị sửa TẠI CHỖ, nên trả S về chỗ cũ vẫn chưa đủ:
// mục G5 đổi khoá của nó và các mục sau đọc phải kho rỗng.
chay('globalThis.__TLcu = { ...TAI_LIEU }');

console.log('\n--- G2. Cây tệp: bấm thật, không chỉ soi chuỗi ---');
{
  chay("dat({ ...S, man: 'chinh' })");
  const truoc = chay('S.activeByProfile[S.profile]');
  bam('[data-tep]', { tep: '1' });
  ok(truoc === 0 && chay('S.activeByProfile[S.profile]') === 1,
     'bấm hàng tệp thứ hai thì tệp đang xem đổi theo',
     `${truoc} → ${chay('S.activeByProfile[S.profile]')}`);

  const n1 = chay('tabDangMo(S).length');
  bam('#themTep');
  const n2 = chay('tabDangMo(S).length');
  ok(n2 === n1 + 1, 'Thêm tệp đẻ ra đúng một hàng', `${n1} → ${n2}`);
  ok(chay('S.activeByProfile[S.profile]') === n2 - 1, 'và nhảy sang hàng vừa tạo');
  ok(co('Văn bản mới 1'), 'hàng chưa đặt tên mang nhãn tự sinh "Văn bản mới 1"');

  // Nút × phải chặn sự kiện nổi lên, không thì vừa đóng tệp vừa nhảy tệp.
  ok(bam('[data-dongtep]', { dongtep: '0' }),
     'nút đóng chặn sự kiện nổi lên (stopPropagation)');
  ok(chay('tabDangMo(S).length') === n2 - 1, 'đóng một hàng thì danh sách ngắn đi',
     String(chay('tabDangMo(S).length')));
}

console.log('\n--- G3. Đóng tệp cuối cùng vẫn còn đúng một hàng rỗng ---');
{
  chay("dat({ ...S, tabsByProfile: { ...S.tabsByProfile, [S.profile]: ['mot.txt'] },"
       + ' activeByProfile: { ...S.activeByProfile, [S.profile]: 0 } })');
  bam('[data-dongtep]', { dongtep: '0' });
  ok(chay('tabDangMo(S).length') === 1, 'không bao giờ còn 0 tệp — đường nạp văn bản '
     + 'đổ vào ô rỗng ấy', String(chay('tabDangMo(S).length')));
  ok(co('Văn bản mới 1'), 'hàng còn lại là ô rỗng mang nhãn tự sinh');
}

console.log('\n--- G4. Cột thu gọn 44px thì cụm tệp tự ẩn ---');
{
  chay('dat({ ...S, rail: true })');
  ok(co('trai thu-gon'), 'cột đang ở chế độ thu gọn');
  const css = readFileSync(join(UI, '..', 'ui-moi', 'man-hinh-chinh.css'), 'utf8');
  ok(/\.trai\.thu-gon \.tepds\s*\{[^}]*display:\s*none/.test(css),
     'CSS ẩn cụm tệp khi thu gọn — không thì cột 44px vỡ');
}

/* Đổi tên là phép NGUY HIỂM NHẤT của cây tệp, vì trong sản phẩm này TÊN TỆP
   CHÍNH LÀ KHOÁ của TAI_LIEU · duongDanTep · loaiTep · chips · chuaLuu.

   Bản đầu của lượt 6 đổi tên bằng cách DỜI khoá cả năm kho, và đo được ba đường
   mất bài: xoá trắng ô xoá luôn nội dung; đặt tên cho tệp chưa đặt tên làm bài
   kẹt dưới khoá rỗng; đặt trùng tên tệp của hồ sơ khác thì nuốt bài hồ sơ ấy.
   Nay theo đúng bản mẫu: nhãn để BẢNG RIÊNG (S.nhanTep), mảng tệp và năm kho
   không bị đụng tới. Ba mục dưới canh đúng ba đường ấy. */
console.log('\n--- G5. Đổi tên chỉ ghi NHÃN, không được đụng khoá nào ---');
{
  chay("dat({ ...globalThis.__Scu, man: 'chinh' })");
  const cu = chay('tabDangMo(S)[0]');
  chay(`dat({ ...S, duongDanTep: { ...S.duongDanTep, ['${cu}']: 'C:/thu/a.txt' },`
       + ` loaiTep: { ...S.loaiTep, ['${cu}']: 'congduc' },`
       + ` chips: { ...S.chips, ['${cu}']: { 1: '[vui]' } } })`);
  chay(`TAI_LIEU['${cu}'] = { doan: [{ kieu: 'p', chu: 'BAI CUA NGUOI DUNG' }],`
       + " chuY: { tomTat: '', loai: [] } }");
  chay(`chuaLuu.add('${cu}')`);

  batSuKien.dblclick({
    target: { closest: (s) => (s === '[data-tep]' ? { dataset: { tep: '0' } } : null) },
    preventDefault() {},
  });
  ok(co('tep__o') && co('id="oTenTep"'), 'nháy đúp mở ô gõ lại tên');

  chay("doiTenTep(0, 'Thư gửi con')");
  ok(co('Thư gửi con'), 'nhãn mới hiện trên hàng tệp');
  ok(chay(`tabDangMo(S)[0] === '${cu}'`), 'mảng tệp KHÔNG đổi — tên tệp vẫn là khoá');
  ok(chay(`!!TAI_LIEU['${cu}']`), 'kho nội dung còn nguyên chỗ cũ');
  ok(chay(`S.duongDanTep['${cu}'] === 'C:/thu/a.txt'`), 'đường dẫn còn nguyên');
  ok(chay(`!!S.chips['${cu}']`), 'thẻ cảm xúc còn nguyên');
  ok(chay(`chuaLuu.has('${cu}')`), 'cờ chưa-lưu còn nguyên');

  // Ca 1 — xoá trắng ô. Bản cũ xoá luôn bài. Nay phải quay về tên tệp thật.
  chay('doiTenTep(0, "")');
  ok(chay('doanDangXem(S, TAI_LIEU).length') === 1,
     'XOÁ TRẮNG ô tên KHÔNG được làm mất bài', String(chay('doanDangXem(S, TAI_LIEU).length')));
  ok(chay(`chuaLuu.has('${cu}')`), 'xoá trắng cũng không được tắt cảnh báo chưa lưu');
  ok(co(cu), 'xoá trắng thì quay về tên tệp thật');

  // Ca 2 — tệp CHƯA ĐẶT TÊN (khoá rỗng). Bản cũ bỏ qua cả khối vì cu falsy.
  chay("dat({ ...S, tabsByProfile: { ...S.tabsByProfile, [S.profile]: [''] },"
       + ' activeByProfile: { ...S.activeByProfile, [S.profile]: 0 }, nhanTep: {} })');
  chay("TAI_LIEU[''] = { doan: [{ kieu: 'p', chu: 'CHU VUA DAN' }], chuY: { tomTat: '', loai: [] } }");
  chay("doiTenTep(0, 'thu-moi.txt')");
  ok(chay('doanDangXem(S, TAI_LIEU).length') === 1,
     'đặt tên cho tệp CHƯA ĐẶT TÊN không được làm bài biến mất',
     String(chay('doanDangXem(S, TAI_LIEU).length')));

  // Ca 3 — đặt trùng tên tệp của HỒ SƠ KHÁC. Bản cũ nuốt bài của hồ sơ ấy.
  chay("dat({ ...S, profile: 0, nhanTep: {},"
       + " tabsByProfile: { ...S.tabsByProfile, 0: ['cua-hs-0.txt'], 1: ['chung.txt'] },"
       + ' activeByProfile: { ...S.activeByProfile, 0: 0, 1: 0 } })');
  chay("TAI_LIEU['chung.txt'] = { doan: [{ kieu: 'p', chu: 'BAI HO SO 1' }], chuY: { tomTat: '', loai: [] } }");
  chay("TAI_LIEU['cua-hs-0.txt'] = { doan: [{ kieu: 'p', chu: 'BAI HO SO 0' }], chuY: { tomTat: '', loai: [] } }");
  chay("doiTenTep(0, 'chung.txt')");
  ok(chay("TAI_LIEU['chung.txt'].doan[0].chu") === 'BAI HO SO 1',
     'đặt trùng tên tệp của hồ sơ KHÁC không được nuốt bài của hồ sơ ấy',
     chay("TAI_LIEU['chung.txt'].doan[0].chu"));

  // Đóng một hàng thì nhãn phải cắt theo vị trí, không thì nhãn đeo nhầm tệp.
  chay("dat({ ...S, tabsByProfile: { ...S.tabsByProfile, [S.profile]: ['a.txt', 'b.txt'] },"
       + ' activeByProfile: { ...S.activeByProfile, [S.profile]: 0 }, nhanTep: {} })');
  chay("doiTenTep(1, 'NHAN CUA B')");
  chay('dat(dongTab(S, 0))');
  ok(co('NHAN CUA B') && chay("tabDangMo(S)[0]") === 'b.txt',
     'đóng hàng trên thì nhãn vẫn đi đúng tệp của nó');
}
console.log('\n--- G6. Bàn phím với tới được hàng tệp ---');
{
  chay("dat({ ...globalThis.__Scu, man: 'chinh' })");
  ok(co('data-tep="0"') && co('tabindex="0"'), 'hàng tệp nhận được nét chọn của bàn phím');
  ok(co('role="button"'), 'trình đọc màn hình hiểu hàng tệp là thứ bấm được');

  // Gõ Enter THẬT khi nét chọn đang đứng ở hàng tệp thứ hai.
  const truoc = chay('S.activeByProfile[S.profile]');
  ctx.document.activeElement = { tagName: 'DIV', dataset: { tep: '1' } };
  batSuKien.keydown({ key: 'Enter', preventDefault() {} });
  ctx.document.activeElement = { tagName: 'DIV' };
  ok(truoc === 0 && chay('S.activeByProfile[S.profile]') === 1,
     'Enter trên hàng tệp thì mở tệp ấy', `${truoc} → ${chay('S.activeByProfile[S.profile]')}`);

  /* Space PHẢI rơi xuống phím Nghe toàn cục, không bị hàng tệp nuốt. Người dùng
     đứng trong cột trái bấm Space mà loa im là lỗi khó đoán nhất. */
  chay("dat({ ...S, activeByProfile: { ...S.activeByProfile, [S.profile]: 0 } })");
  ctx.document.activeElement = { tagName: 'DIV', dataset: { tep: '1' } };
  batSuKien.keydown({ key: ' ', preventDefault() {} });
  ctx.document.activeElement = { tagName: 'DIV' };
  ok(chay('S.activeByProfile[S.profile]') === 0,
     'Space KHÔNG bị hàng tệp nuốt — vẫn là phím Nghe');
}

// Trả cả hai về mốc trước mục G2: S bằng dat(), TAI_LIEU bằng cách dọn sạch rồi
// chép lại — không thể gán đè vì các nơi khác đang giữ chính tham chiếu ấy.
chay('Object.keys(TAI_LIEU).forEach((k) => delete TAI_LIEU[k]);'
     + ' Object.assign(TAI_LIEU, globalThis.__TLcu); dat(globalThis.__Scu)');

console.log('\n--- H. Thanh phát: chưa phát thì KHÔNG hiện ---');
ok(!co('class="phat"'), 'chưa phát → không có thanh phát');
ok(!co('seek') && !co('tua'), 'KHÔNG có thanh tua');

console.log('\n--- I. Bảy tình huống đều dựng được dải cảnh báo ---');
for (const [ma, ten] of chay('TEN_TINH_HUONG')) {
  chay(`dat({ ...S, situation: '${ma}' })`);
  const d = chay(`DAI_CANH_BAO['${ma}']`);
  // Phải khớp chính xác: 'class="dai' còn trúng cả 'class="daitab"'.
  const coDai = co('class="dai"') || co('class="dai ');
  ok(coDai === !!d, `${ten} → ${d ? 'có dải' : 'không dải'}`);
  if (d) ok(co(d.noi.slice(0, 40)), `   nội dung nguyên văn`);
}

console.log('\n--- J. Tình huống khoá đúng nút ---');
for (const ma of ['mat_ket_noi', 'het_luot', 'giong_dang_tai']) {
  chay(`dat({ ...S, situation: '${ma}' })`);
  ok(co('id="nutNghe" disabled') || co('nutNghe" disabled'), `${ma} khoá nút Nghe`);
}
chay("dat({ ...S, situation: 'giong_dang_tai' })");
ok(co('62%'), 'giọng đang tải → thẻ giọng hiện tiến trình 62%');

/* Nút trên dải cảnh báo phải LÀM THẬT. Trước đây cả sáu chỉ là chữ: không
   data-lenh, không id, không nhánh nào trong bộ bắt click. Nặng nhất là "Thử
   lại" của mat_ket_noi — tình huống ấy khoá cả Nghe lẫn Xuất, mà nút duy nhất
   để thoát ra lại chết, nên người dùng chỉ còn nước tắt chương trình. */
console.log('\n--- J2. Dải cảnh báo: mọi nút đều làm thật ---');
{
  const dais = chay('Object.keys(DAI_CANH_BAO).filter((k) => DAI_CANH_BAO[k])');
  ok(dais.length >= 5, 'có đủ các dải cảnh báo', String(dais.length));

  // Không dải nào được phép bày một nút không gắn việc.
  const treo = chay('Object.keys(DAI_CANH_BAO).filter((k) => DAI_CANH_BAO[k])'
                    + '.flatMap((k) => (DAI_CANH_BAO[k].nut || [])'
                    + '.filter((n) => !n.lam).map((n) => k + ":" + n.nhan))');
  ok(treo.length === 0, 'KHÔNG có nút nào thiếu việc — không bày nút giả',
     treo.length ? treo.join(' · ') : 'không có');

  // Mọi mã việc khai trong bảng phải có hàm thật đứng sau.
  const thieu = chay('Object.keys(DAI_CANH_BAO).filter((k) => DAI_CANH_BAO[k])'
                     + '.flatMap((k) => (DAI_CANH_BAO[k].nut || []).map((n) => n.lam))'
                     + '.filter((m) => m && !LENH_CANH_BAO[m])');
  ok(thieu.length === 0, 'mọi mã việc đều có hàm thật', thieu.join(' · ') || 'không có');

  // Bấm THẬT nút thoát của tình huống khoá cả Nghe lẫn Xuất.
  chay("dat({ ...S, situation: 'mat_ket_noi' })");
  ok(chay("S.situation") === 'mat_ket_noi', 'đang ở tình huống mất kết nối');
  bam('[data-canhbao]', { canhbao: 've_binh_thuong' });
  ok(chay("S.situation") === 'binh_thuong',
     'bấm "Thử lại" thì thoát được tình huống khoá', chay('S.situation'));

  chay("dat({ ...S, situation: 'giong_dang_tai' })");
  bam('[data-canhbao]', { canhbao: 'mo_chon_giong' });
  ok(chay('!!S.roiGiong'), 'bấm "Dùng giọng khác" thì mở đúng ô chọn giọng');

  chay("dat({ ...S, situation: 'van_ban_qua_dai' })");
  bam('[data-canhbao]', { canhbao: 'xem_cho_cat' });
  ok(chay('S.sel') === 9 && chay("S.situation") === 'binh_thuong',
     'bấm "Xem chỗ cắt" thì nhảy tới chỗ bị cắt', `sel=${chay('S.sel')}`);

  chay('dat(globalThis.__Scu)');
}

/* Lỗi THẬT từ Python phải hiện đúng chuyện đã xảy ra. Gói dựng dưới đây chép
   nguyên hình dạng mà giaodien/mo_hinh.py đẩy sang khi máy thiếu bộ giọng —
   tình huống có thật và hay gặp nhất với người dùng lớn tuổi. */
console.log('\n--- J3. Máy thiếu bộ giọng: nói đúng việc phải làm ---');
{
  chay("dat({ ...globalThis.__Scu, loiThat: { tieu_de: 'Chưa có bộ giọng VieNeu-TTS',"
       + " chi_tiet: 'Máy chưa cài bộ giọng VieNeu-TTS. Cách cài: mở thư mục chương"
       + " trình, bấm đúp vào tệp CaiDat.bat rồi làm theo hướng dẫn trên màn hình.',"
       + " nut: [{ nhan: 'Kiểm tra lại', act: 'thuLaiMoHinh' }] } })");
  ok(co('Chưa có bộ giọng VieNeu-TTS'), 'hiện đúng tiêu đề lỗi thật của máy này');
  ok(co('CaiDat.bat'), 'chỉ đúng việc phải làm — hướng dẫn cài có sẵn từ bản cũ');
  ok(co('Kiểm tra lại'), 'dựng nút từ chính gói Python gửi');
  ok(!co('Kiểm tra lại mạng') && !co('máy chủ đọc'),
     'KHÔNG còn nói máy chủ hay mạng — chương trình chạy hoàn toàn trên máy');
  ok(co('Bỏ qua'), 'luôn có đường đóng dải lại, không nhốt người dùng');

  bam('[data-loithat]', { loithat: '' });
  ok(!chay('S.loiThat'), 'bấm Bỏ qua thì dải biến đi');
  chay('dat(globalThis.__Scu)');
}

console.log('\n--- K. Đang tạo âm thanh ---');
chay("dat({ ...S, situation: 'dang_tao' })");
ok(co('Đang tạo âm thanh cho đoạn'), 'thanh phát dạng chờ');
ok(co('Thường mất 5–10 giây cho mỗi đoạn'), 'câu giải thích nguyên văn');
ok(co('xoay--nho'), 'vòng xoay ở máng số đoạn đang chờ');

console.log('\n--- L. Đổi hồ sơ thì đổi hết ---');
chay("dat({ ...trangThaiBanDau(HO_SO), situation: 'binh_thuong' })");
chay('dat(doiHoSo(S, 2))');
ok(co('chuong-01.docx'), 'tab đổi theo hồ sơ Sách nói');
ok(co('Giọng bác Tuấn'), 'giọng đổi theo');
ok(co('Tốc độ −10% · Âm lượng 90%'), 'thanh điều chỉnh đổi theo');
ok(co('1 chỗ cần chú ý'), 'Cần chú ý đổi theo tài liệu');

console.log('\n--- M. Trạng thái rỗng ---');
chay('dat(themTab(S))');
ok(co('Dán văn bản vào đây để bắt đầu'), 'tiêu đề trạng thái rỗng');
ok(co('Nhấn Ctrl+V, hoặc kéo thả tệp .txt, .docx, .rtf vào cửa sổ này.'), 'copy nguyên văn');
ok(!co('Nghe toàn bộ'), 'chưa có văn bản → cặp Nghe/Xuất ẨN HẲN');
ok(co('data-lenh="Soát văn bản" disabled') || co('Soát văn bản</span></button>'),
   'công cụ phụ thuộc văn bản chuyển màu mờ');

console.log('\n--- N. Nút Nghe toàn bộ đổi theo trạng thái ---');
chay("dat({ ...trangThaiBanDau(HO_SO), situation: 'binh_thuong' })");
ok(co('>Nghe toàn bộ<'), 'chưa phát → "Nghe toàn bộ"');
chay('dat(ngheToanBo(S))');
ok(co('>Tạm dừng<') && co('dang-phat'), 'đang phát → "Tạm dừng", có nền accent nhạt');
chay("daTamDung = true; dat({ ...S, view: 'san_sang' })");
ok(co('>Đọc tiếp<'), 'tạm dừng giữa chừng → "Đọc tiếp"');
ok(/title="Đọc tiếp từ đoạn \d+/.test(HTML), 'tooltip nói rõ đọc tiếp từ đoạn nào');
chay('daTamDung = false; dat(dungHan(S))');
ok(co('>Nghe toàn bộ<'), 'dừng hẳn → quay lại "Nghe toàn bộ"');

console.log('\n--- O. Sang đoạn kế tiếp ---');
{
  /* Bản thiết kế cập nhật CẤM đoạn rỗng, nên không còn cảnh phải nhảy cóc:
     đoạn kế tiếp luôn là đoạn ngay dưới. Phép kiểm cũ canh việc nhảy qua đoạn
     rỗng - giữ lại là canh một hành vi không còn tồn tại. */
  const doan = chay('doanDangXem(S, TAI_LIEU)');
  ok(doan.every((d) => d.kieu !== 'blank'), 'tài liệu mẫu KHÔNG còn đoạn rỗng nào');
  ok(chay('doanKeTiep(doanDangXem(S, TAI_LIEU), 1)') === 2,
     'đoạn kế tiếp là đoạn ngay dưới, không phải nhảy cóc',
     String(chay('doanKeTiep(doanDangXem(S, TAI_LIEU), 1)')));
  ok(chay(`doanKeTiep(doanDangXem(S, TAI_LIEU), ${doan.length})`) === 0,
     'hết bài trả 0 để dừng');
  ok(chay('doDaiDoan(doanDangXem(S, TAI_LIEU)[0])') > 0, 'đoạn có chữ dài hơn 0');
}

console.log('\n--- P. Màn Soát: đánh dấu đã xử lý ---');
{
  /* Soát ra chín chỗ mà không đánh dấu được đã xem chỗ nào thì lần nào mở ra
     cũng thấy y nguyên chín chỗ. Kiểm bằng cách dựng thật màn Soát trên một
     bộ dữ liệu nhỏ rồi soi HTML nó sinh ra. */
  const D = {
    chuY: {
      trong: false, nang: 1, nhe: 1, moTa: '2 đoạn có chữ',
      vanDe: [
        { muc: 'nang', loai: 'viettat', doan: 3, tu: 'XKLĐ',
          tieuDe: 'Chưa dạy máy đọc “XKLĐ”', chiTiet: 'Máy sẽ đánh vần.' },
        { muc: 'nhe', loai: 'kytu', doan: 4, tu: '',
          tieuDe: 'Có ký tự máy không đọc được', chiTiet: 'Chứa ☎.' },
      ],
    },
    chuanHoa: { dong: [{ doan: 3, goc: 'tổ XKLĐ', doc: 'tổ ích xì kờ lờ đờ', doi: true }],
                soDoi: 1, tomTat: '1 chỗ sẽ được đọc khác' },
    quyTac: [],
  };
  const ve1 = (them) => chay(
    `veManSoat({ ...S, man: 'soat', soatTab: 'chuy', soatLoc: 'tatca', ${them} },`
    + ` ${JSON.stringify(D)})`);

  const chua = ve1('soatBoQua: {}');
  ok((chua.match(/>Bỏ qua<\/button>/g) || []).length === 2, 'mỗi hàng có nút Bỏ qua',
     String((chua.match(/>Bỏ qua<\/button>/g) || []).length));
  ok(/data-soatboqua="tatca"/.test(chua), 'đầu bảng có nút Bỏ qua tất cả');
  ok(/Tất cả \(2\)/.test(chua), 'chưa bỏ qua gì thì chip đếm đủ 2');
  ok(!/Hoàn lại/.test(chua), 'chưa bỏ qua gì thì KHÔNG bày lối hoàn lại');

  const roi = ve1(`soatBoQua: { ${JSON.stringify('viettat|XKLĐ|3')}: true }`);
  ok(!roi.includes('XKLĐ'), 'chỗ đã bỏ qua biến hẳn khỏi bảng');
  ok(/Tất cả \(1\)/.test(roi), 'chip đếm lại theo số CÒN LẠI, không kêu 2 nữa');
  ok(/Hoàn lại 1 chỗ đã bỏ qua/.test(roi), 'có lối lấy lại chỗ đã bỏ qua');
  ok(/data-soathoanlai/.test(roi), 'lối hoàn lại là nút bấm được');

  const het = ve1(`soatBoQua: { ${JSON.stringify('viettat|XKLĐ|3')}: true,`
                  + ` ${JSON.stringify('kytu||4')}: true }`);
  ok(/Đã xem xong cả 2 chỗ/.test(het), 'bỏ qua hết thì nói rõ đã xem xong, không để bảng rỗng');
  ok(/data-soathoanlai/.test(het), 'bỏ qua hết vẫn lấy lại được');

  /* Khoá phải gồm cả `tu`: gop_trung gộp mỗi chữ viết tắt thành một mục, hai
     chữ khác nhau trong CÙNG một đoạn mà đè khoá lên nhau là bỏ một cái thì
     cái kia biến mất theo. */
  const haiTu = JSON.parse(JSON.stringify(D));
  haiTu.chuY.vanDe = [
    { muc: 'nang', loai: 'viettat', doan: 3, tu: 'XKLĐ', tieuDe: 'A', chiTiet: '' },
    { muc: 'nang', loai: 'viettat', doan: 3, tu: 'TĐC', tieuDe: 'B', chiTiet: '' },
  ];
  const conTDC = chay(
    `veManSoat({ ...S, man: 'soat', soatTab: 'chuy', soatLoc: 'tatca',`
    + ` soatBoQua: { ${JSON.stringify('viettat|XKLĐ|3')}: true } }, ${JSON.stringify(haiTu)})`);
  ok(!conTDC.includes('XKLĐ') && conTDC.includes('TĐC'),
     'hai chữ viết tắt cùng đoạn: bỏ chữ này thì chữ kia vẫn còn');

  const tab2 = chay(`veManSoat({ ...S, man: 'soat', soatTab: 'chuanhoa', sel: 3 },`
                    + ` ${JSON.stringify(D)})`);
  ok(/data-nghe="3"/.test(tab2) && /Nghe thử đoạn 3/.test(tab2),
     'chân tab 2 có nút Nghe thử đoạn đang chọn');
  ok(/data-lenh="Từ điển phát âm"/.test(tab2), 'chân tab 2 có nút Thêm vào từ điển');

  const tab2x = chay(`veManSoat({ ...S, man: 'soat', soatTab: 'chuanhoa', sel: 99 },`
                     + ` ${JSON.stringify(D)})`);
  ok(!/data-nghe=/.test(tab2x),
     'đoạn đang chọn không có trong bảng thì KHÔNG bày nút nghe (bấm ra lỗi là nút giả)');
}

console.log('\n--- Q. Sửa chữ tại chỗ ---');
{
  /* Gõ THẲNG vào chữ, không có chế độ vào/ra ô sửa: chủ dự án bấm thử bảo phải
     bấm nút rồi mới gõ được là quá nhiều bước, "muốn như Notepad". */
  ok(/class="doan__chu" contenteditable="plaintext-only"/.test(HTML.replace(/\s+/g, ' '))
     || /doan__chu[^>]*contenteditable="plaintext-only"/.test(HTML),
     'chữ trong đoạn gõ thẳng được, không phải bấm nút mở ô');
  ok(!/data-sua=|doan__o|data-suaxong/.test(HTML), 'KHÔNG còn chế độ ô sửa riêng');

  /* Đang đọc thì KHOÁ gõ: nhịp tô chữ bọc từng chữ vào <span> và viết lại liên
     tục, cho gõ vào giữa cái DOM ấy là hai bên giẫm chân nhau. */
  const dangDoc = chay("(() => { const cu = S; S = { ...S, view: 'dang_doc', pos: 3 };"
    + " const r = veDoan({ kieu: 'body', chu: 'đang đọc' }, 3); S = cu; return r; })()");
  ok(!/contenteditable="plaintext-only"/.test(dangDoc), 'đang đọc thì không cho gõ vào chữ');

  const trong = chay("veDoan({ kieu: 'blank', chu: '' }, 2)");
  ok(!/contenteditable="plaintext-only"/.test(trong), 'dòng trống không mở ô gõ');

  ok(chay('typeof chuDangGo') === 'function' && chay('typeof roiDoanDangGo') === 'function',
     'có đường chép chữ lúc gõ và đường xét tách lúc rời đoạn');
  /* Bẫy đã suýt vấp: contenteditable KHÔNG phải INPUT/TEXTAREA, thiếu
     isContentEditable trong chặn phím tắt là phím Space bị nuốt. */
  ok(/isContentEditable/.test(readFileSync(join(UI, 'giao-dien.js'), 'utf8')),
     'phím tắt toàn cục nhường phím khi đang gõ chữ (không nuốt dấu cách)');

  /* Menu bày phím tắt nào thì phím ấy phải ăn. Bấm Ctrl+S theo đúng chữ menu
     ghi mà không có gì xảy ra cũng là một dạng hứa suông - đã sót 4 phím. */
  const JS = readFileSync(join(UI, 'giao-dien.js'), 'utf8');
  /* Chỉ đòi handler cho mục SỐNG. Mục có phần tử thứ ba là mục đang làm mờ, có
     tooltip nói rõ chưa làm — nó KHÔNG hứa gì nên không nợ gì. Cắt đúng khối
     MENUS chứ đừng quét cả tệp: quét cả tệp là dính luôn phím ghi trong chú
     thích rồi đỏ lên vô cớ. */
  const khoiMenu = JS.slice(JS.indexOf('const MENUS'), JS.indexOf('const THE_CAM_XUC'));
  const song = [...khoiMenu.matchAll(/\['([^']+)',\s*'Ctrl\+([A-Za-z])'\]/g)];
  const khai = [...new Set(song.map((m) => m[2].toLowerCase()))];
  const coHandler = (p) =>
    new RegExp(`k === '${p}'|key\\.toLowerCase\\(\\) === '${p}'`).test(JS);
  const thieu = khai.filter((p) => !coHandler(p));
  ok(thieu.length === 0,
     `mọi phím tắt Ctrl của mục SỐNG đều có handler (${khai.length} phím)`,
     thieu.length ? 'thiếu: Ctrl+' + thieu.join(', Ctrl+').toUpperCase() : '');
  /* Và ngược lại: mục làm mờ phải có LÝ DO, không được mờ trơ trọi. */
  const mo = [...khoiMenu.matchAll(/\['([^']+)',\s*'[^']*',\s*'([^']*)'\]/g)];
  ok(mo.length > 0 && mo.every((m) => m[2].trim().length > 5),
     `mục làm mờ nào cũng kèm lý do (${mo.length} mục)`,
     mo.filter((m) => m[2].trim().length <= 5).map((m) => m[1]).join(', '));
  ok(/document\.activeElement\.blur\(\)[\s\S]{0,80}LENH\['Lưu'\]/.test(JS),
     'Ctrl+S lúc đang gõ thì rời ô trước rồi mới lưu, không ghi ra bản thiếu chữ vừa gõ');

  /* Mỗi đoạn là một vùng gõ RIÊNG, nên Ctrl+A để mặc chỉ bôi đen trong một
     đoạn, và quét nhiều đoạn rồi bấm Xoá thì các đoạn ngoài con trỏ trơ ra. */
  ok(chay('typeof doanTrongVungChon') === 'function'
     && chay('typeof xoaCacDoan') === 'function',
     'có đường gom đoạn trong vùng bôi đen và xoá cả loạt');
  ok(/selectNodeContents\(cuon\)/.test(JS), 'Ctrl+A bôi đen cả bài, không chỉ một đoạn');
  ok(/'Delete' \|\| e\.key === 'Backspace'[\s\S]{0,200}xoaCacDoan/.test(JS),
     'quét nhiều đoạn rồi Xoá thì xoá hết các đoạn ấy');

  const truocXoa = chay('doanDangXem(S, TAI_LIEU).length');
  chay('xoaCacDoan([1, 2])');
  ok(chay('doanDangXem(S, TAI_LIEU).length') === truocXoa - 2,
     'xoá hai đoạn một lượt thì bớt đúng hai',
     `${truocXoa} → ${chay('doanDangXem(S, TAI_LIEU).length')}`);

  /* Cả bài phải cư xử như MỘT tài liệu. Trình duyệt không tự đưa con trỏ sang
     đoạn kề cũng không tự gộp, vì mỗi đoạn là một vùng gõ riêng. */
  ok(chay('typeof gopLenDoanTren') === 'function'
     && chay('typeof doanGoDuoc') === 'function'
     && chay('typeof viTriCaret') === 'function',
     'có đủ đường gộp đoạn, tìm đoạn kề và đo vị trí con trỏ');
  /* Enter phải tách NGAY, không đợi rời đoạn: không chặn thì trình duyệt chỉ
     chèn một dấu xuống dòng, người dùng bấm Enter xong không thấy gì xảy ra. */
  ok(chay('typeof tachDoanTaiCho') === 'function', 'có đường tách đoạn tại con trỏ');
  {
    // Gõ Enter THẬT giữa câu, xem đoạn có tách ngay không.
    const truoc = chay('doanDangXem(S, TAI_LIEU).length');
    const chan = goPhim(3, 'Enter', { vt: 4, chu: 'một hai ba' });
    ok(chan && chay('doanDangXem(S, TAI_LIEU).length') === truoc + 1,
       'gõ Enter giữa câu → tách ngay thành hai đoạn',
       `${truoc} → ${chay('doanDangXem(S, TAI_LIEU).length')}`);
    /* Cắt ĐÚNG vị trí con trỏ, giữ nguyên cả dấu cách - không tự ý trim.
       Con trỏ ở ký tự thứ 4 của "một hai ba" thì phần trên là "một " kèm
       khoảng trắng; cắt bỏ nó là sửa chữ người dùng sau lưng họ. */
    ok(chay('doanDangXem(S, TAI_LIEU)[2].chu') === 'một '
       && chay('doanDangXem(S, TAI_LIEU)[3].chu') === 'hai ba',
       'chữ cắt đúng chỗ con trỏ, không mất ký tự nào',
       chay('doanDangXem(S, TAI_LIEU)[2].chu') + ' | '
       + chay('doanDangXem(S, TAI_LIEU)[3].chu'));
    // Shift+Enter KHÔNG tách - để dành cho xuống dòng trong cùng đoạn.
    const truoc2 = chay('doanDangXem(S, TAI_LIEU).length');
    ok(!goPhim(3, 'Enter', { vt: 2, chu: 'abc', shiftKey: true })
       && chay('doanDangXem(S, TAI_LIEU).length') === truoc2,
       'Shift+Enter KHÔNG tách đoạn');
  }
  {
    const truoc = chay('doanDangXem(S, TAI_LIEU).length');
    const chuGoc = chay('doanDangXem(S, TAI_LIEU)[2].chu');
    chay(`tachDoanTaiCho(3, ${JSON.stringify('phần trên')}, ${JSON.stringify('phần dưới')})`);
    ok(chay('doanDangXem(S, TAI_LIEU).length') === truoc + 1, 'tách xong thêm đúng một đoạn',
       `${truoc} → ${chay('doanDangXem(S, TAI_LIEU).length')}`);
    ok(chay('doanDangXem(S, TAI_LIEU)[2].chu') === 'phần trên'
       && chay('doanDangXem(S, TAI_LIEU)[3].chu') === 'phần dưới',
       'phần sau con trỏ thành đoạn mới ngay dưới', String(chuGoc).slice(0, 20));
    ok(chay('S.sel') === 4, 'con trỏ chuyển sang đoạn mới');
    // Enter ở CUỐI đoạn: đoạn rỗng phải được GIỮ để người dùng gõ tiếp.
    const truoc2 = chay('doanDangXem(S, TAI_LIEU).length');
    chay(`tachDoanTaiCho(3, ${JSON.stringify('còn nguyên')}, '')`);
    ok(chay('doanDangXem(S, TAI_LIEU).length') === truoc2 + 1
       && chay('doanDangXem(S, TAI_LIEU)[3].chu') === '',
       'Enter ở cuối đoạn tạo đoạn rỗng và GIỮ lại để gõ tiếp');
  }
  ok(/coPlay = d\.kieu !== 'blank' && String\(d\.chu/.test(JS),
     'đoạn chưa có chữ thì không treo nút ▶ (bấm ra lỗi là nút giả)');

  /* Ô ĐÃ BỊ GỠ khỏi màn hình thì focusout của nó phải bị BỎ QUA.

     Tách đoạn gọi dat() vẽ lại vùng đọc, ô cũ bị thay; trình duyệt vẫn bắn
     focusout trên ô chết ấy, mang theo nguyên câu CHƯA cắt. Chép nó vào tài
     liệu là ghi đè đúng kết quả vừa tách - chủ dự án gặp cảnh bấm Enter thấy
     tách, bấm ra chỗ khác thì đâu lại vào đấy, văn bản đầy đoạn giống hệt nhau. */
  {
    const truoc = chay('doanDangXem(S, TAI_LIEU).length');
    const chuTruoc = chay('doanDangXem(S, TAI_LIEU)[2].chu');
    chay(`roiDoanDangGo({
      isConnected: false,
      textContent: 'CHỮ CŨ CHƯA CẮT',
      closest: () => ({ dataset: { doan: '3' } }),
    })`);
    ok(chay('doanDangXem(S, TAI_LIEU).length') === truoc
       && chay('doanDangXem(S, TAI_LIEU)[2].chu') === chuTruoc,
       'ô đã bị gỡ thì focusout KHÔNG ghi đè tài liệu',
       chay('doanDangXem(S, TAI_LIEU)[2].chu').slice(0, 24));
    // Ô còn sống thì vẫn phải chép chữ như thường.
    chay(`roiDoanDangGo({
      isConnected: true,
      textContent: 'chữ mới gõ',
      closest: () => ({ dataset: { doan: '3' } }),
    })`);
    ok(chay('doanDangXem(S, TAI_LIEU)[2].chu') === 'chữ mới gõ',
       'ô còn sống thì vẫn chép chữ vào tài liệu như thường');
  }

  /* GÕ THẬT thay vì grep. Mỗi phép dưới đây gọi đúng handler keydown mà cửa sổ
     thật dùng, rồi soi kết quả trong tài liệu - không phải soi mã nguồn. */
  {
    const truoc = chay('doanDangXem(S, TAI_LIEU).length');
    const chan = goPhim(3, 'Backspace', { vt: 0, chu: 'đoạn ba' });
    ok(chan && chay('doanDangXem(S, TAI_LIEU).length') === truoc - 1,
       'gõ Backspace ở ĐẦU đoạn 3 → gộp lên đoạn trên, bớt một đoạn',
       `${truoc} → ${chay('doanDangXem(S, TAI_LIEU).length')}`);
  }
  {
    const truoc = chay('doanDangXem(S, TAI_LIEU).length');
    const chu = chay('doanDangXem(S, TAI_LIEU)[2].chu');
    const chan = goPhim(3, 'Delete', { vt: chu.length, chu });
    ok(chan && chay('doanDangXem(S, TAI_LIEU).length') === truoc - 1,
       'gõ Delete ở CUỐI đoạn 3 → kéo đoạn dưới lên',
       `${truoc} → ${chay('doanDangXem(S, TAI_LIEU).length')}`);
  }
  {
    const truoc = chay('doanDangXem(S, TAI_LIEU).length');
    const chan = goPhim(3, 'Backspace', { vt: 2, chu: 'giữa câu' });
    ok(!chan && chay('doanDangXem(S, TAI_LIEU).length') === truoc,
       'Backspace GIỮA câu thì để trình duyệt lo, không gộp đoạn nào');
  }
  ok(goPhim(3, 'ArrowUp', { vt: 0, chu: 'abc' }), 'mũi tên LÊN ở đầu đoạn được xử lý');
  ok(goPhim(3, 'ArrowDown', { vt: 3, chu: 'abc' }), 'mũi tên XUỐNG ở cuối đoạn được xử lý');
  ok(!goPhim(3, 'ArrowUp', { vt: 2, chu: 'abc' }),
     'mũi tên LÊN ở giữa đoạn thì KHÔNG giành phím của trình duyệt');
  ok(/sel && sel\.isCollapsed/.test(JS),
     'chỉ giành phím khi con trỏ đứng một chỗ, đang bôi đen thì để trình duyệt lo');

  // Gộp thật: hai đoạn liền nhau nhập làm một, chữ nối liền.
  const truocGop = chay('doanDangXem(S, TAI_LIEU).length');
  const chuTren = chay('doanDangXem(S, TAI_LIEU)[0].chu');
  const chuDuoi = chay('doanDangXem(S, TAI_LIEU)[1].chu');
  chay('gopLenDoanTren(2)');
  ok(chay('doanDangXem(S, TAI_LIEU).length') === truocGop - 1,
     'gộp xong thì bớt một đoạn', `${truocGop} → ${chay('doanDangXem(S, TAI_LIEU).length')}`);
  ok(chay('doanDangXem(S, TAI_LIEU)[0].chu') === chuTren + chuDuoi,
     'chữ hai đoạn nối liền, không mất chữ nào');

  /* Thẻ cảm xúc đánh theo SỐ ĐOẠN, nên tách hay xoá đoạn là phải dời chúng
     theo. Không dời thì thẻ nhảy sang nhầm câu mà người dùng không hề đụng. */
  const themGiua = chay("dichThe({ t: { 2: 'a', 5: 'b' } }, 't', 3, 1)");
  ok(themGiua.t[2] === 'a' && themGiua.t[6] === 'b' && !themGiua.t[5],
     'chèn đoạn: thẻ phía trên yên chỗ, thẻ phía dưới dời xuống');
  const xoa = chay("dichThe({ t: { 2: 'a', 3: 'x', 5: 'b' } }, 't', 3, -1)");
  ok(xoa.t[2] === 'a' && xoa.t[3] === undefined && xoa.t[4] === 'b',
     'xoá đoạn: thẻ của đoạn bị xoá bỏ hẳn, phần dưới dời lên');

  // Đường thật: gọi luuSuaDoan rồi đếm lại số đoạn.
  const truoc = chay('doanDangXem(S, TAI_LIEU).length');
  chay("luuSuaDoan(3, 'dòng một\\ndòng hai')");
  const sauTach = chay('doanDangXem(S, TAI_LIEU).length');
  ok(sauTach === truoc + 1, 'xuống dòng trong ô sửa thì tách thành hai đoạn',
     `${truoc} → ${sauTach}`);
  ok(chay('doanDangXem(S, TAI_LIEU)[2].chu') === 'dòng một', 'đoạn đầu giữ chữ đã sửa');
  ok(chay('doanDangXem(S, TAI_LIEU)[3].chu') === 'dòng hai', 'đoạn tách ra nằm ngay sau');

  chay("luuSuaDoan(4, '')");
  const sauXoa = chay('doanDangXem(S, TAI_LIEU).length');
  ok(sauXoa === sauTach - 1, 'xoá sạch chữ thì bỏ hẳn đoạn đó', `${sauTach} → ${sauXoa}`);

  ok(Object.keys(chay('S.soatBoQua') || {}).length === 0,
     'sửa chữ thì bỏ kết quả soát cũ, vì nó nói về bản chữ trước khi sửa');
}

/* ============================================================ màn đứng riêng

   Bốn tệp thiết kế có nút "Quay lại màn hình chính" (Thư viện giọng 3, Cài đặt
   2, Từ điển phát âm 2, Văn bản ghép 2) — đó là bốn màn chiếm TOÀN cửa sổ.
   Soát văn bản có 0, và tệp của nó tự nói "Vẫn là cửa sổ chính của Giọng Việt",
   nên nó phải Ở LẠI trong khung chính. Canh đúng ranh giới ấy. */
console.log('\n--- M. Màn đứng riêng vs bảng mở thêm ---');

for (const [ma, ten] of [['giong', 'Thư viện giọng'],
                         ['tudien', 'Từ điển phát âm'],
                         ['caidat', 'Cài đặt']]) {
  chay(`dat({ ...S, man: '${ma}' })`);
  ok(co(`${ten} — Giọng Việt`), `${ten}: thanh tiêu đề mang tên màn`);
  ok(co('title="Quay lại màn hình chính"'), `${ten}: có đường lùi về màn chính`);
  ok(co('class="manphu"'), `${ten}: thân màn chiếm trọn cửa sổ`);
  ok(!co('class="menu"') && !co('class="congcu"'),
     `${ten}: KHÔNG còn thanh menu và thanh công cụ của màn chính`);
  ok(!co('class="thanchinh'), `${ten}: KHÔNG còn hai cột trái/phải`);
  /* Cửa sổ dựng frameless — mất ba nút này là không thu nhỏ / phóng to / đóng
     được nữa, mà người dùng KHÔNG có viền hệ điều hành để thay thế. */
  ok(co('data-cuaso="thu_nho"') && co('data-cuaso="phong_to"') && co('data-cuaso="dong"'),
     `${ten}: vẫn còn ba nút cửa sổ`);
}

chay("dat({ ...S, man: 'soat' })");
ok(!co('class="manphu"'), 'Soát văn bản KHÔNG phải màn đứng riêng');
ok(co('class="menu"') && co('class="thanchinh'),
   'Soát văn bản giữ nguyên khung màn chính, đúng câu thiết kế tự nói');
ok(!co('title="Quay lại màn hình chính"'),
   'Soát văn bản không có đường lùi — nó đóng bảng, không rời màn');

chay("dat({ ...S, man: 'chinh' })");
ok(co('class="menu"') && !co('class="manphu"'), 'quay về màn chính thì khung trở lại đủ');

console.log(`\n${loi === 0 ? 'XANH — khớp hết' : `ĐỎ — ${loi} chỗ lệch`}`);
process.exit(loi ? 1 : 0);
