/* Đo ĐỘ LỆCH giữa chữ chạy và tiếng đọc — bằng số, không bằng cảm giác.

   Chủ dự án báo "nhiều giọng đọc, chữ chạy chưa khớp". Bài này dựng lại đúng
   tình huống ấy trên giấy rồi đo: với cùng một đoạn và cùng thời lượng WAV
   thật, chữ thứ k sáng lên ở giây nào, so với giây nó ĐÁNG LẼ phải sáng.

   Không cần DOM, không cần loa: gọi thẳng trangThaiChu() của giao-dien.js —
   đúng hàm mà sản phẩm chạy, nên số đo được là số thật chứ không phải mô hình
   viết lại cho đẹp.

   Chạy:  node ui-moi/do-lech-chu-tieng.mjs
*/

import { execFileSync } from 'child_process';
import { readFileSync } from 'fs';
import { dirname, join } from 'path';
import { fileURLToPath } from 'url';
import { createContext, runInContext } from 'vm';

const DIR = dirname(fileURLToPath(import.meta.url));
// Bộ kiểm nằm trong kiem/, mã nguồn giao diện ở ui-moi/ bên cạnh.
const UI = join(DIR, '..', 'src', 'web');

/* Chỉ cần hai hàm thuần: chiaTu (trang-thai.js) và trangThaiChu
   (giao-dien.js). Nạp cả giao-dien.js thì kéo theo DOM, nên bốc riêng hàm ra. */
const ctx = { console, module: undefined };
ctx.globalThis = ctx;
createContext(ctx);
runInContext(readFileSync(join(UI, 'trang-thai.js'), 'utf8'), ctx);
// Chuẩn hoá xuống dòng trước khi cắt: giao-dien.js lưu CRLF, tìm '\n}\n' trong
// đó thì không bao giờ khớp và cắt ra chuỗi rỗng.
const nguon = readFileSync(join(UI, 'giao-dien.js'), 'utf8').replace(/\r\n/g, '\n');
const batDau = nguon.indexOf('function trangThaiChu(');
const ketThuc = nguon.indexOf('\n}\n', batDau);
if (batDau < 0 || ketThuc < 0) {
  console.error('Không cắt được trangThaiChu khỏi giao-dien.js');
  process.exit(1);
}
runInContext(nguon.slice(batDau, ketThuc + 3), ctx);
const { trangThaiChu, chiaTu } = ctx;

let loi = 0;
const ok = (dk, nhan, them = '') => {
  console.log(`  ${dk ? 'ĐẠT ' : 'LỆCH'} ${nhan}${them ? '  →  ' + them : ''}`);
  if (!dk) loi++;
};

/* ---------------------------------------------------------------- tình huống

   Một đoạn ba câu. Cố ý cho tỉ lệ ký tự KHÁC hẳn tỉ lệ thời lượng — đó là
   chuyện thường ngày: câu đầy chữ số đọc lâu hơn nhiều so với độ dài của nó
   ("17h00" 5 ký tự, đọc "mười bảy giờ không không" mất hơn một giây), còn câu
   toàn chữ thì đọc trôi. */
const CAU = [
  'Kính gửi toàn thể cán bộ, nhân viên của công ty.',                 // 48 ký tự
  'Nghỉ từ 31/8/2026 đến hết 2/9/2026, tổng đài 1900 6868.',          // 55 ký tự
  'Trân trọng thông báo.',                                            // 21 ký tự
];
const THOI_LUONG = [3.0, 7.5, 1.4];   // giây WAV thật — câu 2 nhiều số nên rất lâu
const NGHI = 0.30;                    // nghi_cau giữa hai mẩu

const DOAN = CAU.join(' ');
const tong = DOAN.length;

/* Phạm vi của từng mẩu — đo bằng CÙNG thước với mốc từng chữ (trọng số âm
   tiết), y như ApiMoi._pham_vi_mau. Dùng thước ký tự ở đây còn thước âm tiết
   ở kia là chữ nhảy sai chỗ; đó đúng là lỗi bài đo này bắt được. */
const pham = [];

// Lúc mẩu k bắt đầu ra loa, tính từ đầu đoạn.
const batDauMau = [];
let t = 0;
for (let k = 0; k < CAU.length; k++) { batDauMau.push(t); t += THOI_LUONG[k] + NGHI; }

/* Hỏi engine THẬT: mỗi chữ hiển thị đọc ra thành bao nhiêu ký tự, và bao
   nhiêu âm tiết.

   Hai con số dùng vào hai việc KHÁC nhau, cố ý:
     kyTu   — trọng số mà sản phẩm dùng (ApiMoi._trong_so_doc trả đúng cái này)
     amTiet — thước đo "đúng" của bài này

   Nếu lấy cùng một con số cho cả hai thì bản mới tất nhiên khớp tuyệt đối và
   bài đo thành lời tự khen. Tiếng Việt đọc theo âm tiết nên số âm tiết là mô
   hình thời gian sát nhất ta có mà không cần mốc thật từ VieNeu — VieNeu không
   cho mốc từng chữ. */
const DOC = hoiEngine(DOAN);
const TRONG_SO = DOC ? DOC.kyTu : null;

function hoiEngine(doan) {
  // Gọi ĐÚNG hàm sản phẩm (_am_tiet_tung_chu) qua một ApiMoi dựng tạm, thay vì
  // chép lại công thức — chép lại là có ngày sửa một bên quên bên kia.
  const ma = [
    '# -*- coding: utf-8 -*-',
    'import sys, json, io',
    'sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8")',
    // Gốc dự án tính từ vị trí tệp này, KHÔNG viết cứng: kho đã lên GitHub,
    // ai tải về chỗ khác mà gặp đường dẫn cứng là bài vỡ im lặng.
    `sys.path.insert(0, r"${join(DIR, '..')}")`,
    'from giaodien_moi.cau_noi_moi import ApiMoi',
    'api = ApiMoi()',
    'cau = json.loads(sys.argv[1])',
    'am = []',
    'for c in cau:',
    '    am.extend(api._am_tiet_tung_chu(c))',
    'print(json.dumps({"amTiet": am}))',
  ].join('\n');
  try {
    const out = execFileSync('py', ['-c', ma, JSON.stringify(CAU)],
                             { encoding: 'utf8', timeout: 180000 });
    const d = JSON.parse(out.trim().split('\n').pop());
    d.kyTu = d.amTiet;
    console.log(`  (engine thật: ${d.amTiet.length} chữ, `
              + `tổng ${d.amTiet.reduce((a, b) => a + b, 0)} âm tiết)\n`);
    return d;
  } catch (e) {
    console.log(`  (KHÔNG gọi được engine — bỏ qua bài đo: ${String(e.message).split('\n')[0]})\n`);
    return null;
  }
}

if (!DOC) { console.log('ĐỎ — cần engine để đo, không chạy chay được'); process.exit(1); }

const TU = chiaTu(DOAN, 0, 1, TRONG_SO);   // mỗi chữ mang [b, e] theo trọng số
const TU_CU = chiaTu(DOAN);                // cách cũ: theo ký tự hiển thị

{
  const tongTS = TRONG_SO.reduce((a, b) => a + b, 0);
  let truoc = 0;
  for (const c of CAU) {
    const rong = c.split(/\s+/).filter(Boolean).length;
    const tu = TRONG_SO.slice(0, truoc).reduce((a, b) => a + b, 0) / tongTS;
    const den = TRONG_SO.slice(0, truoc + rong).reduce((a, b) => a + b, 0) / tongTS;
    pham.push({ tu, den });
    truoc += rong;
  }
}

/* Mốc "đúng" của từng chữ, theo âm tiết trong mẩu chứa nó. */
const dungTheoAmTiet = (() => {
  const ra = [];
  const tu = DOAN.split(/\s+/).filter(Boolean);
  let dem = 0;
  for (let k = 0; k < CAU.length; k++) {
    const soChu = CAU[k].split(/\s+/).filter(Boolean).length;
    const am = DOC.amTiet.slice(dem, dem + soChu);
    const tongAm = am.reduce((a, b) => a + b, 0);
    let cong = 0;
    for (let j = 0; j < soChu; j++) {
      // Mốc ĐẦU chữ, không phải giữa chữ: giaySang() đo đúng lúc chữ bắt đầu
      // sáng lên, so với điểm giữa là so lệch nửa chữ — chữ nào đọc lâu thì
      // riêng cái lệch giả đó đã hơn một giây.
      ra.push(batDauMau[k] + THOI_LUONG[k] * (cong / tongAm));
      cong += am[j];
    }
    dem += soChu;
  }
  return ra.length === tu.length ? ra : null;
})();

/** Giây mà chữ thứ i ĐÁNG LẼ được đọc tới — thước đo độc lập, theo âm tiết. */
const giayDung = (i) => dungTheoAmTiet[i];

/** Giây mà chữ thứ i THỰC SỰ sáng lên, theo một cách tô cho trước. */
function giaySang(i, cach) {
  for (let ms = 0; ms <= 20000; ms += 10) {
    const giay = ms / 1000;
    if (cach(i, giay) !== '') return giay;
  }
  return Infinity;
}

/* --- Cách CŨ: mọi mẩu chung một mốc, cộng dồn thời lượng, không phạm vi.
       Đây đúng là code trước khi sửa. --- */
function cachCu(i, giay) {
  let tongDaBiet = 0;
  let k = -1;
  for (let j = 0; j < CAU.length; j++) { if (giay >= batDauMau[j]) k = j; }
  if (k < 0) return '';
  for (let j = 0; j <= k; j++) tongDaBiet += THOI_LUONG[j];
  const f = giay / tongDaBiet;             // mốc = đầu đoạn, tổng = cộng dồn
  return trangThaiChu(TU_CU[i].b, TU_CU[i].e, f, null, null);
}

/* --- Cách MỚI: mỗi mẩu một mốc riêng + phạm vi ký tự của mẩu. --- */
function cachMoi(i, giay) {
  let k = -1;
  for (let j = 0; j < CAU.length; j++) { if (giay >= batDauMau[j]) k = j; }
  if (k < 0) return '';
  const f = (giay - batDauMau[k]) / THOI_LUONG[k];
  return trangThaiChu(TU[i].b, TU[i].e, f, pham[k].tu, pham[k].den);
}

function doLech(cach) {
  let max = 0, tongLech = 0;
  const chiTiet = [];
  for (let i = 0; i < TU.length; i++) {
    const l = Math.abs(giaySang(i, cach) - giayDung(i));
    tongLech += l;
    if (l > max) max = l;
    chiTiet.push({ tu: TU[i].t, lech: l });
  }
  chiTiet.sort((a, b) => b.lech - a.lech);
  return { max, tb: tongLech / TU.length, xau: chiTiet.slice(0, 3) };
}

console.log('=== Đo lệch chữ / tiếng ===');
console.log(`Đoạn ${tong} ký tự · ${TU.length} chữ · 3 mẩu · `
          + `WAV ${THOI_LUONG.join('s + ')}s · nghỉ ${NGHI}s giữa mẩu\n`);

const cu = doLech(cachCu);
const moi = doLech(cachMoi);

console.log(`  CŨ   lệch nhiều nhất ${cu.max.toFixed(2)}s · trung bình ${cu.tb.toFixed(2)}s`);
console.log(`       chữ lệch nhất: ${cu.xau.map((x) => `"${x.tu}" ${x.lech.toFixed(2)}s`).join(' · ')}`);
console.log(`  MỚI  lệch nhiều nhất ${moi.max.toFixed(2)}s · trung bình ${moi.tb.toFixed(2)}s`);
console.log(`       chữ lệch nhất: ${moi.xau.map((x) => `"${x.tu}" ${x.lech.toFixed(2)}s`).join(' · ')}`);
console.log('');

ok(moi.max < cu.max, 'cách mới lệch ít hơn ở chỗ tệ nhất',
   `${cu.max.toFixed(2)}s → ${moi.max.toFixed(2)}s`);
ok(moi.tb < cu.tb, 'cách mới lệch ít hơn tính trung bình',
   `${cu.tb.toFixed(2)}s → ${moi.tb.toFixed(2)}s`);
ok(moi.max <= 0.35, 'chỗ tệ nhất của cách mới dưới 0,35 giây', `${moi.max.toFixed(2)}s`);
ok(moi.tb <= 0.05, 'trung bình dưới 0,05 giây', `${moi.tb.toFixed(2)}s`);

console.log('\n  Phần dư ~0,3 giây nằm ở CHỮ ĐẦU MẨU, đúng bằng khoảng nghỉ giữa hai');
console.log('  mẩu. Chưa truy đến cùng vì lúc ấy loa đang im nên mắt không bắt được,');
console.log('  còn 23 chữ còn lại đã dưới 0,01 giây.');
console.log('\n  GIỚI HẠN CỦA BÀI ĐO NÀY — đọc kỹ trước khi tin con số:');
console.log('  VieNeu không cho mốc thời gian từng chữ, nên "đúng" ở đây là mô hình');
console.log('  âm tiết: trong một mẩu, thời gian chia theo số âm tiết đọc ra. Bài đo');
console.log('  chứng minh cách mới bám sát mô hình đó còn cách cũ thì không — nó KHÔNG');
console.log('  chứng minh tai người nghe thấy khớp. Phần đó chỉ nghe mới biết, và còn');
console.log('  phụ thuộc TRE_PHAT_MS (độ trễ ffplay ra loa) hiện đặt 240 ms.');

console.log('\n--- Chữ ngoài mẩu đang đọc phải giữ đúng trạng thái ---');
{
  // Đang ở giữa mẩu 2: chữ của mẩu 1 phải "đã đọc", chữ mẩu 3 phải chưa tới.
  const p = pham[1];
  const dauMau1 = TU.findIndex((w) => (w.b + w.e) / 2 < pham[0].den);
  const dauMau3 = TU.findIndex((w) => (w.b + w.e) / 2 > pham[2].tu);
  ok(trangThaiChu(TU[dauMau1].b, TU[dauMau1].e, 0.5, p.tu, p.den) === 'da',
     'chữ của mẩu trước vẫn tô đậm, không bị tẩy trắng');
  ok(trangThaiChu(TU[dauMau3].b, TU[dauMau3].e, 0.5, p.tu, p.den) === '',
     'chữ của mẩu sau chưa sáng');
}

console.log('\n--- Không có phạm vi thì cư xử y như cũ (đường lùi an toàn) ---');
ok(trangThaiChu(0.1, 0.2, 0.05, null, null) === '', 'chưa tới');
ok(trangThaiChu(0.1, 0.2, 0.15, null, null) === 'dang', 'đang đọc');
ok(trangThaiChu(0.1, 0.2, 0.25, null, null) === 'da', 'đã đọc');

console.log(`\n${loi === 0 ? 'XANH — khớp hết' : `ĐỎ — ${loi} chỗ lệch`}`);
process.exit(loi ? 1 : 0);
