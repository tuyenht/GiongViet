/* Canh SỐ ĐO của cây tệp bằng cách đọc thẳng bản thiết kế, không chép tay.

   Vì sao bài này tồn tại: chủ dự án yêu cầu giao diện khớp bản thiết kế 100%.
   Chép số đo vào đầu bài kiểm rồi so là vô nghĩa — chép sai một lần là bài kiểm
   canh chính cái sai ấy mãi mãi. Ở đây số đo được RÚT TỪ CHÍNH tệp .dc.html mỗi
   lần chạy, nên thiết kế đổi thì bài này đỏ lên ngay, và không ai phải nhớ.

   Bài canh (xanh = tốt). Không nạp mô hình, không phát tiếng, không mở cửa sổ.

   Chạy:  node kiem/kiem-so-do-cay-tep.mjs
*/
import { existsSync, readFileSync } from 'fs';
import { join, dirname } from 'path';
import { fileURLToPath } from 'url';

// Gốc dự án tính từ chính vị trí tệp này. KHÔNG viết cứng đường dẫn: kho đã lên
// GitHub, ai tải về chỗ khác là vỡ hết bộ kiểm.
const DIR = dirname(fileURLToPath(import.meta.url));
const GOC = join(DIR, '..');
const MAU = [
  join(GOC, 'docs', 'designs', 'design_handoff_giongdoc', 'designs',
       'GiongDoc - Màn hình chính v2 (nghe theo dòng).dc.html'),
  join(GOC, 'design_handoff_giongdoc', 'designs',
       'GiongDoc - Màn hình chính v2 (nghe theo dòng).dc.html'),
].find(existsSync) || join(GOC, 'docs', 'designs', 'design_handoff_giongdoc', 'designs',
                          'GiongDoc - Màn hình chính v2 (nghe theo dòng).dc.html');

const CSS = [
  join(GOC, 'src', 'web', 'man-hinh-chinh.css'),
  join(GOC, 'ui-moi', 'man-hinh-chinh.css'),
].find(existsSync) || join(GOC, 'src', 'web', 'man-hinh-chinh.css');

const mau = readFileSync(MAU, 'utf8');
const css = readFileSync(CSS, 'utf8');

let loi = 0;
const ok = (dk, nhan, them = '') => {
  console.log(`  ${dk ? 'ĐẠT ' : 'LỆCH'} ${nhan}${them ? '  →  ' + them : ''}`);
  if (!dk) loi++;
};

/** Khối style trong bản thiết kế, tìm bằng một mẩu đặc trưng nằm trong nó. */
function khoiMau(dauHieu) {
  const re = new RegExp('style="([^"]*' + dauHieu.replace(/[.*+?^${}()|[\]\\]/g, '\\$&') + '[^"]*)"');
  const m = re.exec(mau);
  return m ? m[1] : null;
}

/** Một quy tắc CSS của sản phẩm, tìm bằng tên lớp. */
function khoiCss(ten) {
  const re = new RegExp('(^|\\n)\\.' + ten + '\\s*\\{([^}]*)\\}');
  const m = re.exec(css);
  return m ? m[2].replace(/\s+/g, ' ').trim() : null;
}

/** Giá trị của một thuộc tính trong khối, đã chuẩn hoá khoảng trắng. */
function tri(khoi, ten) {
  if (!khoi) return null;
  const re = new RegExp('(?:^|[;{\\s])' + ten + '\\s*:\\s*([^;}]+)');
  const m = re.exec(khoi);
  return m ? m[1].trim().replace(/\s+/g, ' ') : null;
}

function soSanh(nhan, khoiM, khoiC, thuocTinh, tenCss = thuocTinh) {
  const a = tri(khoiM, thuocTinh);
  const b = tri(khoiC, tenCss);
  if (a === null) { ok(false, `${nhan} — KHÔNG đọc được từ bản thiết kế`); return; }
  ok(a === b, `${nhan}: ${thuocTinh}`, a === b ? a : `thiết kế ${a} · code ${b || 'KHÔNG CÓ'}`);
}

console.log('Bản thiết kế:', MAU.replace(GOC, '.'));
console.log('Mã sản phẩm :', CSS.replace(GOC, '.'));

// ---------------------------------------------------------------- hàng tệp
console.log('\n--- Hàng tệp ---');
const mHang = khoiMau('border-left:2px solid {{ f.rail }}');
const cHang = khoiCss('tep');
ok(!!mHang, 'đọc được khối hàng tệp trong bản thiết kế');
ok(!!cHang, 'đọc được quy tắc .tep trong man-hinh-chinh.css');
for (const t of ['height', 'gap', 'padding', 'margin-left', 'border-radius']) {
  soSanh('hàng tệp', mHang, cHang, t);
}
ok((tri(mHang, 'border-left') || '').startsWith('2px solid')
   && (tri(cHang, 'border-left') || '').startsWith('2px solid'),
   'hàng tệp: vạch trái dày 2px',
   `thiết kế ${tri(mHang, 'border-left')} · code ${tri(cHang, 'border-left')}`);

// ---------------------------------------------------------------- cụm bọc
console.log('\n--- Cụm bọc danh sách tệp ---');
const mCum = khoiMau('flex-direction:column;gap:1px;margin-top:2px');
const cCum = khoiCss('tepds');
for (const t of ['gap', 'margin-top', 'flex-direction']) soSanh('cụm tệp', mCum, cCum, t);

// ---------------------------------------------------------------- nút đóng
console.log('\n--- Nút đóng tệp ---');
const mDong = khoiMau('width:18px;height:18px;flex:none;display:flex');
const cDong = khoiCss('tep__dong');
for (const t of ['width', 'height', 'border-radius']) soSanh('nút đóng', mDong, cDong, t);

// ---------------------------------------------------------------- ô đổi tên
console.log('\n--- Ô gõ lại tên ---');
const mO = khoiMau('height:22px;padding:0 5px;border:1px solid var(--acc)');
const cO = khoiCss('tep__o');
for (const t of ['height', 'padding', 'border', 'border-radius', 'box-sizing']) {
  soSanh('ô tên', mO, cO, t);
}

// ---------------------------------------------------------------- Thêm tệp
console.log('\n--- Hàng "Thêm tệp" ---');
const mThem = khoiMau('height:28px;padding:0 6px 0 15px');
const cThem = khoiCss('tep__them');
for (const t of ['height', 'gap', 'padding', 'margin-left', 'font-size', 'border-radius']) {
  soSanh('Thêm tệp', mThem, cThem, t);
}
ok((tri(mThem, 'border-left') || '') === (tri(cThem, 'border-left') || ''),
   'Thêm tệp: vạch trái trong suốt để thẳng cột với hàng tệp',
   `thiết kế ${tri(mThem, 'border-left')} · code ${tri(cThem, 'border-left')}`);

console.log('\n' + (loi ? `ĐỎ — ${loi} chỗ lệch` : 'XANH — khớp bản thiết kế'));
process.exit(loi ? 1 : 0);
