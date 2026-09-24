/* BÀI CANH (xanh = tốt): ghép danh sách công đức phải đúng và sạch.

   VÌ SAO CÓ BÀI NÀY

   Đo ngày 08/09/2026, hai lỗi nghiệp vụ ở màn Văn bản ghép:

   1. BA CÔNG TẮC "Lọc & nhóm" LÀ NÚT GIẢ. `cur.rule` chỉ được lật giá trị
      (giao-dien.js) rồi vẽ trạng thái công tắc (man-vanbanghep.js) — không một
      dòng nào áp nó vào dữ liệu. Người dùng bật "Bỏ dòng thiếu", chữ đổi thành
      "Đang lọc", mà danh sách vẫn nguyên si. `rule.dupCol` và `rule.group`
      thì chưa ai đọc lần nào.

   2. Ô TRỐNG LÀM CÂU QUÈ, và máy đọc to nguyên câu ấy ở buổi lễ:
        "Xin tán thán Trần Thị Bích, ở, đã công đức 1.200.000 đồng."
      Ô địa chỉ hay pháp danh bỏ trống là chuyện rất thường trong danh sách
      công đức.

   Bài nạp thẳng ba hàm dùng chung từ giao-dien.js và chạy chúng. Không mở cửa
   sổ, không phát tiếng, không chạm dữ liệu người dùng.

   Chạy:  node tests/kiem-ghep-danh-sach.mjs
*/
import { readFileSync } from 'fs';
import { createContext, runInContext } from 'vm';
import { join, dirname } from 'path';
import { fileURLToPath } from 'url';

const DIR = dirname(fileURLToPath(import.meta.url));
const src = readFileSync(join(DIR, '..', 'src', 'web', 'giao-dien.js'), 'utf8');

/* Trích đúng ba hàm cần dùng, không nạp cả tệp 5000 dòng (nó cần DOM thật). */
function layHam(ten) {
  const i = src.indexOf(`function ${ten}(`);
  if (i < 0) throw new Error(`Không tìm thấy hàm ${ten} trong giao-dien.js`);
  let d = 0, j = src.indexOf('{', i);
  while (j < src.length) {
    if (src[j] === '{') d++;
    else if (src[j] === '}') { d--; if (!d) break; }
    j++;
  }
  return src.slice(i, j + 1);
}
const iHelper = src.indexOf('const _oCuaDongVBG');
if (iHelper < 0) throw new Error('Không tìm thấy _oCuaDongVBG — hàm dùng chung đã bị đổi tên?');
const helper = src.slice(iHelper, src.indexOf('function locDongTheoQuyTacVBG'));

const ctx = { console, String, Array, Set, parseInt, Object };
ctx.globalThis = ctx;
createContext(ctx);
runInContext(helper + layHam('locDongTheoQuyTacVBG') + layHam('ghepMotCauVBG')
             + layHam('lanVaoDoanGhepVBG'), ctx);

let loi = 0;
const ok = (dk, nhan, them = '') => {
  console.log(`  ${dk ? 'ĐẠT ' : 'LỆCH'} ${nhan}${them ? '  →  ' + them : ''}`);
  if (!dk) loi++;
};

const MAU_CUR = () => ({
  cols: [{ letter: 'A', varName: '{ten}' },
         { letter: 'B', varName: '{diachi}' },
         { letter: 'C', varName: '{sotien}' }],
  T: { mau: 'Xin tán thán {ten}, ở {diachi}, đã công đức {sotien} đồng.',
       dau: '', giua: '', cuoi: '' },
  on: {}, sauMoi: '20',
  rows: [
    { A: 'Nguyễn Văn An', B: 'Hà Nội', C: '500.000' },
    { A: 'Trần Thị Bích', B: '', C: '1.200.000' },
    { A: '', B: '', C: '' },
    { A: 'Nguyễn Văn An', B: 'Hà Nội', C: '500.000' },
    { A: 'Lê Hoàng Long', B: 'Đà Nẵng', C: '' },
  ],
  rule: { trong: false, trung: false, dupCol: 'A', thutu: true },
});

const chayVoi = (rule) => {
  ctx.__cur = MAU_CUR();
  ctx.__cur.rule = rule;
  const ds = runInContext('locDongTheoQuyTacVBG(__cur)', ctx);
  const doan = runInContext('lanVaoDoanGhepVBG([], __cur, locDongTheoQuyTacVBG(__cur))', ctx);
  return { ds, doan };
};

console.log('--- A. Ba công tắc "Lọc & nhóm" phải THẬT SỰ lọc ---');
const khong = chayVoi({ trong: false, trung: false, thutu: true });
ok(khong.ds.length === 5, 'không lọc gì → giữ đủ 5 dòng', String(khong.ds.length));

const boThieu = chayVoi({ trong: true, trung: false, thutu: true });
ok(boThieu.ds.length === 4, '"Bỏ dòng thiếu" bỏ đúng dòng rỗng hoàn toàn',
   `${khong.ds.length} → ${boThieu.ds.length}`);

const gopTrung = chayVoi({ trong: true, trung: true, dupCol: 'A', thutu: true });
ok(gopTrung.ds.length === 3, '"Gộp trùng" bỏ bản trùng theo cột A',
   `${boThieu.ds.length} → ${gopTrung.ds.length}`);

const sapXep = chayVoi({ trong: true, trung: true, dupCol: 'A', thutu: false });
const tenDau = sapXep.ds.map(r => r.A);
ok(tenDau[0] === 'Lê Hoàng Long',
   '"Thứ tự" tắt → xếp theo cột đầu', tenDau.join(' · '));

console.log('\n--- B. Ô trống KHÔNG được để lại câu què ---');
for (const d of khong.doan) {
  ok(!/,\s*,/.test(d), `không có dấu phẩy đôi: ${d.slice(0, 46)}`);
}
const cauThieuDiaChi = khong.doan[1];
ok(!/,\s*ở\s*,/.test(cauThieuDiaChi) && !/\bở,/.test(cauThieuDiaChi),
   'thiếu địa chỉ → bỏ luôn chữ "ở" treo lơ lửng', cauThieuDiaChi);
ok(cauThieuDiaChi.includes('Trần Thị Bích') && cauThieuDiaChi.includes('1.200.000'),
   'nhưng vẫn giữ đủ tên và số tiền');

console.log('\n--- C. Không bỏ sót người chỉ vì thiếu một ô ---');
// "Bỏ dòng thiếu" cố ý hiểu HẸP: chỉ bỏ dòng mà MỌI ô có biến đều rỗng.
// Ở buổi lễ, bỏ sót một người vì họ không ghi địa chỉ là chuyện lớn.
ok(boThieu.doan.some(d => d.includes('Trần Thị Bích')),
   'người thiếu địa chỉ VẪN được đọc tên');
ok(boThieu.doan.some(d => d.includes('Lê Hoàng Long')),
   'người thiếu số tiền VẪN được đọc tên');

console.log('\n--- D. Câu xen giữa: mốc "sau mỗi N dòng" ---');
ctx.__cur = MAU_CUR();
ctx.__cur.on = { giua: true };
ctx.__cur.T.giua = 'Nam mô A Di Đà Phật.';
ctx.__cur.sauMoi = '2';
const coGiua = runInContext('lanVaoDoanGhepVBG([], __cur, __cur.rows)', ctx);
const soXen = coGiua.filter(d => d === 'Nam mô A Di Đà Phật.').length;
ok(soXen === 2, 'chèn đúng số câu xen giữa (5 dòng, mỗi 2 dòng)', String(soXen));
ok(coGiua[coGiua.length - 1] !== 'Nam mô A Di Đà Phật.',
   'không chèn câu xen sau dòng cuối');

ctx.__cur.sauMoi = '0';
const khongChia = runInContext('lanVaoDoanGhepVBG([], __cur, __cur.rows)', ctx);
ok(khongChia.length === 5, 'N = 0 không làm vỡ và không chèn vô hạn',
   String(khongChia.length));

console.log();
if (loi) {
  console.log(`ĐỎ — ${loi} chỗ lệch.`);
  process.exit(1);
}
console.log('XANH — lọc chạy thật, câu ghép sạch, không bỏ sót người.');
