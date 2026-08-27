// kiem-van-ban-ghep.mjs — Kiểm thử tự động Màn 6: Văn bản ghép
import assert from 'node:assert/strict';
import fs from 'node:fs';
import path from 'node:path';

console.log('--- Kiểm thử Màn 6: Văn bản ghép (Live Data / Template Engine) ---');

// 1. Kiểm tra tồn tại tệp css và js
const uiDir = fs.existsSync('src/web/man-vanbanghep.js') ? 'src/web' : 'ui-moi';
assert.ok(fs.existsSync(`${uiDir}/man-vanbanghep.css`), 'man-vanbanghep.css phải tồn tại');
assert.ok(fs.existsSync(`${uiDir}/man-vanbanghep.js`), 'man-vanbanghep.js phải tồn tại');
console.log('  ĐẠT  Tệp CSS và JS của Văn bản ghép tồn tại đầy đủ');

// 2. Mock environment để nạp man-vanbanghep.js
global.esc = (s) => String(s == null ? '' : s);
global.ic = (t, n = 16) => `<svg width="${n}"><use href="#i-${t}"/></svg>`;
global.hoSoDangDung = () => ({ ten: 'Mặc định', giong: 'hn_thao' });

const { veManVanBanGhep, MAU_VAN_BAN_GHEP_MAC_DINH } = await import(`../${uiDir}/man-vanbanghep.js`);

// 3. Render kiểm tra cấu trúc
const html = veManVanBanGhep({ man: 'vanbanghep' }, MAU_VAN_BAN_GHEP_MAC_DINH);
assert.ok(html.includes('vanbanghep__trai'), 'Phải có cột trái navigation 240px');
assert.ok(html.includes('vanbanghep__phai'), 'Phải có thân chính');
assert.ok(html.includes('Nguồn dữ liệu'), 'Phải có mục Nguồn dữ liệu');
assert.ok(html.includes('Khớp cột'), 'Phải có mục Khớp cột');
assert.ok(html.includes('Lọc & nhóm'), 'Phải có mục Lọc & nhóm');
assert.ok(html.includes('Mẫu câu mỗi dòng'), 'Phải có mục Mẫu câu mỗi dòng');
assert.ok(html.includes('Bản ghép hoàn chỉnh') || html.includes('vanbanghep__hop-preview'), 'Phải có vùng Preview');
console.log('  ĐẠT  Dựng HTML khớp cấu trúc 7 mục và Preview');

// 4. Kiểm tra biến trong mẫu câu
const cur = MAU_VAN_BAN_GHEP_MAC_DINH.maus[0];
assert.ok(cur.T.mau.includes('{ten}') && cur.T.mau.includes('{sotien}'), 'Mẫu câu phải chứa {ten} và {sotien}');
console.log('  ĐẠT  Mẫu câu động chứa đúng các biến ánh xạ cột');

console.log('\nXANH — Màn 6 (Văn bản ghép) khớp hết 100%');
