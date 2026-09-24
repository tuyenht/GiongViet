/* L4 — phần JS: chạy ĐÚNG giao-dien.js của sản phẩm trong DOM giả.

   Không mở trình duyệt, không chiếm màn hình người dùng. Dựng lại y hệt cách
   kiem/kiem-giao-dien.mjs làm: nạp 10 tệp .js theo đúng thứ tự index.html khai,
   trong một ngữ cảnh vm riêng. window.pywebview KHÔNG có nên coPython() sai —
   nghĩa là không một lời gọi nào chạm sang Python, không ghi đĩa.

   Chạy:  node l4.mjs <đường-dẫn-ui-moi> <đường-dẫn-tệp-Thang7> <đường-dẫn-tệp-Thang8>
*/

import { readFileSync } from 'fs';
import { join, dirname } from 'path';
import { fileURLToPath } from 'url';
import { createContext, runInContext } from 'vm';

// Khong truyen tham so thi lay thu muc giao dien cua chinh du an.
// Truoc day bo trong la join() nhan undefined roi bai vo ngay dong dau.
const DIR = dirname(fileURLToPath(import.meta.url));
const UI = process.argv[2] || join(DIR, '..', 'src', 'web');
const P7 = process.argv[3];
const P8 = process.argv[4];

let HTML = '';
const batSuKien = {};

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
  setInterval: () => 0, clearInterval() {}, setTimeout: () => 0, clearTimeout() {},
  location: { search: '' },
  URLSearchParams,
  document: {
    documentElement: { dataset: {}, style: { setProperty() {}, removeProperty() {} } },
    body: { appendChild() {} },
    activeElement: { tagName: 'DIV' },
    querySelector: (s) => {
      if (s === '#goc') return ctx.__goc;
      if (s === '#cuon') return null;
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
    querySelectorAll: () => [],
    getElementById: () => null,
    createElement: () => nutGia(),
    createRange: () => ({
      setStart() {}, setEnd() {}, collapse() {}, selectNodeContents() {},
      toString: () => '',
    }),
    addEventListener: (t, f) => { batSuKien[t] = f; },
  },
  window: { addEventListener() {} },   // KHÔNG có pywebview -> coPython() = false
  localStorage: { getItem: () => null, setItem() {} },
  module: undefined,
};
ctx.__goc = nutGia('goc');
ctx.globalThis = ctx;
createContext(ctx);

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
const chay = (ma) => runInContext(ma, ctx, { filename: 'l4' });

console.log(`  [ngữ cảnh] coPython() = ${chay('coPython()')}  (sai = không chạm Python, không ghi đĩa)`);

// Dọn về một trạng thái sạch: một hồ sơ, một tab rỗng, không tài liệu nào.
chay(`
  for (const k of Object.keys(TAI_LIEU)) delete TAI_LIEU[k];
  dat({ ...S, tabsByProfile: { ...S.tabsByProfile, [S.profile]: [''] },
        activeByProfile: { ...S.activeByProfile, [S.profile]: 0 },
        duongDanTep: {}, loaiTep: {}, chips: {} });
`);
ok(chay('Object.keys(TAI_LIEU).length') === 0, 'khởi điểm: TAI_LIEU rỗng',
   `${chay('JSON.stringify(tabDangMo(S))')}`);

console.log('\n  --- mở tệp thứ nhất: Thang7\\congduc.txt ---');
chay(`datTaiLieu(${JSON.stringify({
  ten: 'congduc.txt', duongDan: P7,
  doan: [{ kieu: 'body', chu: 'THANG BAY - Nguyen Van A - 500.000' }],
})})`);
console.log(`  TAI_LIEU  = ${chay('JSON.stringify(Object.keys(TAI_LIEU))')}`);
console.log(`  tab       = ${chay('JSON.stringify(tabDangMo(S))')}  (đang xem thứ ${chay('S.activeByProfile[S.profile]')})`);
console.log(`  đường dẫn = ${chay('JSON.stringify(S.duongDanTep)')}`);
console.log(`  chữ tab 1 = ${chay('JSON.stringify(doanDangXem(S, TAI_LIEU)[0].chu)')}`);

// Gắn thẻ cảm xúc cho đoạn 1 của tài liệu tháng Bảy.
chay(`dat(datThe(S, '[cười]'))`);
console.log(`  thẻ tab 1 = ${chay('JSON.stringify(theCuaDoan(S, 1))')}  · kho thẻ = ${chay('JSON.stringify(S.chips)')}`);

console.log('\n  --- mở TAB MỚI rồi mở tệp thứ hai: Thang8\\congduc.txt ---');
chay('dat(themTab(S))');
chay(`datTaiLieu(${JSON.stringify({
  ten: 'congduc.txt', duongDan: P8,
  doan: [{ kieu: 'body', chu: 'THANG TAM - Tran Thi B - 200.000' }],
})})`);
console.log(`  TAI_LIEU  = ${chay('JSON.stringify(Object.keys(TAI_LIEU))')}`);
console.log(`  tab       = ${chay('JSON.stringify(tabDangMo(S))')}  (đang xem thứ ${chay('S.activeByProfile[S.profile]')})`);
console.log(`  đường dẫn = ${chay('JSON.stringify(S.duongDanTep)')}`);
console.log(`  chữ tab 2 = ${chay('JSON.stringify(doanDangXem(S, TAI_LIEU)[0].chu)')}`);

console.log('\n  --- quay về TAB 1 (đáng lẽ là tháng Bảy) ---');
chay('dat(doiTab(S, 0))');
const chuTab1 = chay('doanDangXem(S, TAI_LIEU)[0].chu');
console.log(`  chữ tab 1 = ${JSON.stringify(chuTab1)}`);
console.log(`  thẻ tab 1 = ${chay('JSON.stringify(theCuaDoan(S, 1))')}`);

/* ĐỔI CHIỀU BA MỆNH ĐỀ (20/8).

   Bài này vốn CHỨNG MINH lỗi: xanh = lỗi còn nguyên. Ba mệnh đề đầu nay đã được
   vá — datTaiLieu() đánh số cho tên trùng khi nó đang thuộc về một hàng khác,
   nên hai tệp cùng tên ở hai thư mục không giẫm lên nhau nữa. Giữ nguyên mệnh đề
   cũ thì bài đỏ ở đúng chỗ sản phẩm vừa làm đúng, nên đảo chúng sang chiều CANH
   (xanh = tốt) và ghi rõ ở đây.

   Mệnh đề thứ tư vẫn giữ chiều chứng-minh-lỗi vì phần ấy chưa vá: thẻ cảm xúc
   còn khoá theo tên, và việc dời nó thuộc lượt đổi mô hình khoá. */
console.log('\n  --- kết ---');
ok(chay('Object.keys(TAI_LIEU).length') === 2,
   'hai tệp khác nhau giữ được HAI mục riêng trong TAI_LIEU',
   `số mục = ${chay('Object.keys(TAI_LIEU).length')}`);
ok(chuTab1.includes('THANG BAY'),
   'tab 1 hiện ĐÚNG nội dung tháng Bảy của nó',
   JSON.stringify(chuTab1));
/* Phép này chỉ có nghĩa khi bài chạy qua kiem_khoa_ten_tep.py — bên ấy dựng
   duongDanTep bằng ApiMoi thật. Chạy tay `node soi_khoa_ten_tep.mjs ui-moi` thì
   kho ấy rỗng, nên bỏ qua thay vì báo đỏ giả. */
if (chay('Object.keys(S.duongDanTep).length') === 0) {
  console.log('  BỎ QUA  đường dẫn — chạy tay không có bước dựng của bài .py');
} else {
  ok(chay('Object.keys(S.duongDanTep).length') === 2,
     'hai đường dẫn được nhớ riêng, không cái nào ghi đè cái nào',
     chay('JSON.stringify(S.duongDanTep)'));
}
// CÒN LỖI: thẻ cảm xúc vẫn khoá theo tên nên hai tài liệu dùng chung một kho.
ok(chay('theCuaDoan(S, 1)') === '[cười]' && chay('Object.keys(S.chips).length') === 1,
   'thẻ cảm xúc VẪN dùng chung một khoá cho cả hai tài liệu (chưa vá)',
   chay('JSON.stringify(S.chips)'));

console.log(`\n  [JS] ${loi === 0 ? 'mọi phép đều ĐẠT' : loi + ' phép LỆCH'}`);
process.exit(loi === 0 ? 0 : 1);
