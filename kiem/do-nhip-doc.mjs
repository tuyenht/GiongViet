/* Đo công phải làm cho MỖI NHỊP ĐỌC (4 nhịp/giây), so hai đường vẽ.

   Chạy:  node ui-moi/do-nhip-doc.mjs

   Đo được: số byte HTML phải nhét vào DOM, và số node phải sờ tới.
   KHÔNG đo được: mili giây thật trong WebView2 — dàn trang và vẽ lại là việc
   của trình duyệt, DOM giả không mô phỏng. Con số dưới đây là KHỐI LƯỢNG
   CÔNG VIỆC, không phải thời gian. */

import { readFileSync } from 'fs';
import { createContext, runInContext } from 'vm';
import { fileURLToPath } from 'url';
import { dirname, join } from 'path';

const DIR = dirname(fileURLToPath(import.meta.url));
// Bộ kiểm nằm trong kiem/, mã nguồn giao diện ở ui-moi/ bên cạnh.
const UI = join(DIR, '..', 'ui-moi');

const dem = { byteHTML: 0, soNode: 0 };

/* Đoạn giả. Có đủ mặt để batDauToChu chạy được: nó bọc span cho ĐÚNG một đoạn
   nên phần HTML sinh ra ở đây cũng phải tính vào cột "cách mới". */
function nutDoan(n) {
  const chu = {
    dataset: {},
    querySelector: () => null,
    querySelectorAll: () => [],
    get textContent() { return 'Kính gửi toàn thể cán bộ, nhân viên Công ty đoạn ' + n; },
    set textContent(v) { dem.soNode++; },
    set innerHTML(v) { dem.byteHTML += v.length; },
    get innerHTML() { return ''; },
  };
  return {
    dataset: { doan: String(n) },
    classList: { toggle() { dem.soNode++; }, add() {}, remove() {} },
    querySelector: (s) => (s === '.doan__chu' ? chu : { set textContent(v) { dem.soNode++; } }),
    getBoundingClientRect: () => ({ top: 0, height: 40 }),
    scrollIntoView() { dem.soNode++; },
  };
}

function nutThuong(id = '') {
  return {
    id, dataset: {}, style: { set width(v) { dem.soNode++; } }, scrollTop: 0, value: '',
    classList: { toggle() {}, add() {}, remove() {} },
    focus() {}, remove() {}, appendChild() {},
    querySelector: () => nutThuong(), querySelectorAll: () => [],
    getBoundingClientRect: () => ({ left: 0, width: 200 }),
    set textContent(v) { dem.soNode++; },
    set innerHTML(v) { dem.byteHTML += v.length; },
    get innerHTML() { return ''; },
    set onchange(f) {}, set onclick(f) {},
  };
}

let SO_DOAN = 0;
const ctx = {
  console,
  // batDauToChu cần hai thứ này của trình duyệt
  performance: { now: () => 0 },
  requestAnimationFrame: () => 0, cancelAnimationFrame() {},
  setInterval: () => 0, clearInterval() {}, setTimeout: () => 0,
  location: { search: '' }, URLSearchParams,
  document: {
    documentElement: { dataset: {}, style: { setProperty() {}, removeProperty() {} } }, body: { appendChild() {} },
    activeElement: { tagName: 'DIV' },
    querySelector: (s) => (s === '#cuon' ? null : nutThuong(s.replace('#', ''))),
    querySelectorAll: (s) => (s === '[data-doan]'
      ? Array.from({ length: SO_DOAN }, (_, i) => nutDoan(i + 1)) : []),
    getElementById: () => null, createElement: () => nutThuong(),
    addEventListener() {},
  },
  window: { addEventListener() {} },
  localStorage: { getItem: () => null, setItem() {} },
  module: undefined,
};
ctx.globalThis = ctx;
createContext(ctx);
for (const f of ['du-lieu-mau.js', 'trang-thai.js', 'tinh-huong.js', 'cau-noi.js', 'hop-thoai.js', 'giao-dien.js']) {
  runInContext(readFileSync(join(UI, f), 'utf8'), ctx, { filename: f });
}

const NHIP = 40;   // 10 giây đọc, 4 nhịp một giây

function dungTaiLieu(n) {
  SO_DOAN = n;
  runInContext(`TAI_LIEU['do.txt'] = { doan: Array.from({length:${n}}, (_,i)=>
      ({ kieu: i%7===3?'blank':(i%23===0?'head':'body'),
         chu: i%7===3?'':'Kính gửi toàn thể cán bộ, nhân viên Công ty trách nhiệm hữu hạn Phúc Lâm, đoạn số '+(i+1)+'.' })),
      chuY: { tomTat:'x', loai:[] } };
    S = { ...S, tabsByProfile:{...S.tabsByProfile, 0:['do.txt']},
                activeByProfile:{...S.activeByProfile, 0:0} };
    dat(ngheToanBo(S));
    ganLaiCache();`, ctx);
}

console.log(`Mỗi nhịp đọc = 250 ms. Đo ${NHIP} nhịp (10 giây đọc).\n`);
console.log('  số đoạn |          CÁCH CŨ vẽ lại toàn bộ |     CÁCH MỚI sờ đúng node | nhẹ hơn');
console.log('  --------|---------------------------------|---------------------------|--------');

for (const n of [16, 200, 1000, 3000]) {
  dungTaiLieu(n);

  dem.byteHTML = 0; dem.soNode = 0;
  for (let i = 0; i < NHIP; i++) runInContext('ve()', ctx);
  const cu = dem.byteHTML;

  dungTaiLieu(n);
  dem.byteHTML = 0; dem.soNode = 0;
  for (let i = 0; i < NHIP; i++) {
    // Cứ 10 nhịp thì sang đoạn mới — đúng nhịp một đoạn dài ~2,5 giây.
    const doiDoan = i % 10 === 0 ? `S = { ...S, pos: Math.min(S.pos + 1, ${n}) };` : '';
    runInContext(`giayDaNghe += 0.25; ${doiDoan} veNhipDoc();`, ctx);
  }
  const moi = dem.byteHTML;

  console.log(`  ${String(n).padStart(7)} | ${(cu / 1024 / 1024).toFixed(2).padStart(8)} MB HTML nhét vào DOM `
            + `| ${(moi / 1024).toFixed(1).padStart(9)} KB HTML         | ${
              moi ? Math.round(cu / moi) + '×' : '∞'}`);
}

console.log('\n2,1 KB còn lại là span bọc từng chữ cho ĐÚNG đoạn đang đọc, để tô chữ chạy'
          + '\ntheo tiếng. Con số này KHÔNG đổi theo độ dài tài liệu — 16 đoạn hay 3.000'
          + '\nđoạn đều 2,1 KB, vì lúc nào cũng chỉ một đoạn được bọc span.');
console.log('\nCHƯA ĐO ĐƯỢC: mili giây thật trong WebView2. Dàn trang và vẽ lại là việc'
          + '\ncủa trình duyệt, DOM giả không mô phỏng được. Muốn biết phải mở cửa sổ thật.');
