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

for (const f of ['du-lieu-mau.js', 'trang-thai.js', 'tinh-huong.js', 'cau-noi.js', 'hop-thoai.js', 'giao-dien.js']) {
  runInContext(readFileSync(join(DIR, f), 'utf8'), ctx, { filename: f });
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
ok(co('Bấm số đoạn để nghe riêng đoạn đó'), 'gợi ý bên phải đầu vùng đọc');
ok(!co('THỜI LƯỢNG') && !co('doan__dur'), 'KHÔNG còn cột/nhãn thời lượng');
ok(dem('data-doan=') === 16, '16 đoạn', String(dem('data-doan=')));
ok(co('doan--tieude'), 'có đoạn tiêu đề');
ok(co('doan--trong'), 'có đoạn rỗng (blank)');
ok(co('[hắng giọng]'), 'thẻ cảm xúc ở đoạn 11');
ok(co('Nghe riêng đoạn này, nghe hết đoạn thì dừng'), 'tooltip máng số');

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

console.log(`\n${loi === 0 ? 'XANH — khớp hết' : `ĐỎ — ${loi} chỗ lệch`}`);
process.exit(loi ? 1 : 0);
