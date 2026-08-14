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
    scrollTop: 0, value: '', focus() {}, remove() {}, appendChild() {},
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
    querySelector: (s) => (s === '#goc' ? ctx.__goc : (s === '#cuon' ? null : nutGia())),
    // Đường vẽ nhẹ (veNhipDoc) hứng danh sách đoạn qua đây.
    querySelectorAll: () => [],
    getElementById: () => null,
    createElement: () => nutGia(),
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

console.log('--- A. Khung dọc đủ 9 tầng ---');
for (const [cls, ten] of [['tieude', 'thanh tiêu đề'], ['menu', 'thanh menu'],
  ['congcu', 'thanh công cụ'], ['daitab', 'dải tab'], ['thanchinh', 'vùng ba cột'],
  ['trai', 'cột trái'], ['doc', 'vùng đọc'], ['phai', 'cột phải'],
  ['trangthai', 'thanh trạng thái']]) {
  ok(co(`class="${cls}`) || co(` ${cls}"`) || co(`"${cls}"`), ten);
}

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
ok(co('215 từ') || /\d+ từ · 16 đoạn/.test(HTML), 'dòng thống kê',
   (HTML.match(/\d+ từ · \d+ đoạn · khoảng [^<]+/) || [''])[0]);
/* Gợi ý phải tả đúng thao tác đang có. Máng số đã thôi làm nút, nên câu cũ
   "Bấm số đoạn..." là chỉ đường sai - canh để nó không lẻn về. */
ok(co('Đưa chuột vào đoạn rồi bấm ▶ để nghe riêng đoạn đó'), 'gợi ý bên phải đầu vùng đọc');
ok(!co('Bấm số đoạn'), 'KHÔNG còn gợi ý cũ bảo bấm vào số đoạn');
ok(!co('THỜI LƯỢNG') && !co('doan__dur'), 'KHÔNG còn cột/nhãn thời lượng');
ok(dem('data-doan=') === 16, '16 đoạn', String(dem('data-doan=')));
ok(co('doan--tieude'), 'có đoạn tiêu đề');
ok(co('doan--trong'), 'có đoạn rỗng (blank)');
ok(co('[hắng giọng]'), 'thẻ cảm xúc ở đoạn 11');
/* Nghe riêng đoạn nay đi bằng nút ▶ nổi bên phải mỗi dòng, hiện lúc đưa chuột
   vào. Máng số trở lại đúng vai bản mẫu: chỉ là số, KHÔNG phải nút — nên nó
   không được mang data-nghe nữa, không thì lại thành hai nút chồng vai. */
ok(/<button class="doan__play"[\s\S]*?data-nghe="\d+"/.test(HTML), 'mỗi đoạn có nút ▶ riêng');
ok(/Nghe riêng đoạn \d+\. Đang đọc đoạn này thì bấm để dừng\./.test(HTML),
   'mách nước nút ▶ kèm số đoạn và nói rõ bấm lần nữa là dừng');
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
ok(/\.doan__than\s*\{[^}]*padding-right:\s*(4[89]|[5-9]\d)px/.test(CSS_CHINH),
   'vùng chữ chừa đủ chỗ bên phải cho nút ▶');

/* Nhịp đọc chuyển đoạn bằng cách gạt lớp, KHÔNG dựng lại DOM. Ký hiệu nút phải
   do CSS vẽ theo lớp, viết vào HTML là đoạn sang lượt đọc vẫn trơ hình ▶. */
ok(/\.doan__play::after\s*\{[^}]*content:\s*'▶'/.test(CSS_CHINH)
   && /\.doan\.dang-doc\s+\.doan__play::after\s*\{[^}]*content:\s*'■'/.test(CSS_CHINH),
   'nút đổi ▶ thành ■ ở đoạn đang đọc');
ok(/\.doan\.dang-doc\s+\.doan__play\s*\{[^}]*opacity:\s*1/.test(CSS_CHINH),
   'đoạn đang đọc thì nút hiện sẵn, không bắt rê chuột mới thấy');
ok(/S\.view === 'dang_doc' && soDoan === S\.pos\) return dungPhat\(\)/
   .test(readFileSync(join(UI, 'giao-dien.js'), 'utf8')),
   'bấm nút ở đoạn đang đọc thì DỪNG, không đọc lại từ đầu');

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
ok(/\[data-nghe\][\s\S]{0,900}?lyDoKhoa\(S\)[\s\S]{0,200}?moBao/.test(JS_CHINH),
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
ok(co('Đã lưu 14:02'), 'Đã lưu hh:mm');
ok(!co('UTF-8') && !co('CRLF') && !co('100%</span>'), 'KHÔNG còn UTF-8 / CRLF / mức phóng to');

console.log('\n--- G. Dải tab ---');
ok(dem('class="tab') >= 2, '2 tab của hồ sơ 1', String(dem('data-tab=')));
ok(co('thongbao-quoc-khanh.txt'), 'tên tệp trên tab');
ok(co('data-dongtab='), 'tab đóng được');
ok(co('id="themTab"'), 'nút + thêm tab');

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

console.log('\n--- O. Sang đoạn kế tiếp thì bỏ qua đoạn rỗng ---');
{
  const doan = chay("doanDangXem(S, TAI_LIEU)");
  // Tài liệu mẫu: đoạn 2, 4, 8, 13, 15 là blank
  ok(chay('doanKeTiep(doanDangXem(S, TAI_LIEU), 1)') === 3,
     'từ đoạn 1 (tiêu đề) nhảy qua đoạn 2 rỗng, sang đoạn 3',
     String(chay('doanKeTiep(doanDangXem(S, TAI_LIEU), 1)')));
  ok(chay('doanKeTiep(doanDangXem(S, TAI_LIEU), 3)') === 5,
     'từ đoạn 3 nhảy qua đoạn 4 rỗng, sang đoạn 5');
  ok(chay(`doanKeTiep(doanDangXem(S, TAI_LIEU), ${doan.length})`) === 0,
     'hết bài trả 0 để dừng');
  ok(chay('doDaiDoan(doanDangXem(S, TAI_LIEU)[1])') === 0, 'đoạn rỗng dài 0 giây');
  ok(chay('doDaiDoan(doanDangXem(S, TAI_LIEU)[2])') > 0, 'đoạn có chữ dài hơn 0');
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
  const khai = [...new Set([...JS.matchAll(/'Ctrl\+([A-Z])'/g)].map((m) => m[1].toLowerCase()))];
  const coHandler = (p) =>
    new RegExp(`k === '${p}'|key\\.toLowerCase\\(\\) === '${p}'`).test(JS);
  const thieu = khai.filter((p) => !coHandler(p));
  ok(thieu.length === 0, `mọi phím tắt Ctrl khai trong menu đều có handler (${khai.length} phím)`,
     thieu.length ? 'thiếu: Ctrl+' + thieu.join(', Ctrl+').toUpperCase() : '');
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

console.log(`\n${loi === 0 ? 'XANH — khớp hết' : `ĐỎ — ${loi} chỗ lệch`}`);
process.exit(loi ? 1 : 0);
