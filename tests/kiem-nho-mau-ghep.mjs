/* Canh viec NHO MAU GHEP qua lan dong cua so.

   RUI RO THAT SU can chung minh: truoc day duLieuVBG la mot bien toan cuc va
   khong noi nao luu no xuong dia. Dong chuong trinh la mat link Google Sheet,
   mat khop cot, mat bon khoi van ban vua go. Mo lai, bam "Dong bo Live" thi no
   keo ve GOOGLE_SHEET_MAC_DINH - dung buoi le o chua, may doc to danh sach
   nguoi mau.

   Bai nay kiem VONG TRON luu -> doc lai:
     A. Cau hinh song sot: link Sheet, khop cot, bon khoi van ban
     B. `rows` KHONG duoc luu - bang tinh 2.000 dong ma vao hoso-v2.json thi tep
        phinh theo, va henLuuHoSo() JSON.stringify no moi lan dat()
     C. Ghep theo ID chu khong theo thu tu - ban sau them khuon mau moi thi lay
        theo chi so la gan nham cau hinh khuon nay sang khuon kia
     D. Khuon nguoi dung tu tao van con sau khi doc lai

   Khong mo cua so, khong goi Python, khong cham du lieu nguoi dung. */

import { createRequire } from 'module';
import { dirname, join } from 'path';
import { fileURLToPath } from 'url';

const DIR = dirname(fileURLToPath(import.meta.url));
const req = createRequire(import.meta.url);
const M = req(join(DIR, '..', 'src', 'web', 'man-vanbanghep.js'));

let loi = 0;
const ok = (dk, nhan, them = '') => {
  console.log(`  ${dk ? 'ĐẠT ' : 'LỆCH'} ${nhan}${them ? '  →  ' + them : ''}`);
  if (!dk) loi++;
};

const ban_sao = (x) => JSON.parse(JSON.stringify(x));

// --- A. Cau hinh nguoi dung go vao phai song sot ---
console.log('--- A. Cấu hình sống sót qua vòng lưu → đọc lại ---');
const d = ban_sao(M.MAU_VAN_BAN_GHEP_MAC_DINH);
const cur = d.maus[d.mauHienTai];
cur.srcVal = 'https://docs.google.com/spreadsheets/d/SHEET-CUA-CHUA/edit';
cur.sheet = 'Công đức tháng 9';
cur.headRow = 'Dòng 2';
cur.cols[0].use = 'Tên người {ten}';
cur.T.mau = 'Xin tán thán {ten} đã phát tâm {sotien} đồng.';
cur.T.dau = 'Nam mô A Di Đà Phật.';
d.nav = 4;

const daLuu = M.vbgCanLuu(d);
const doc = M.vbgTuDaLuu(daLuu);
const c2 = doc.maus[doc.mauHienTai];

ok(c2.srcVal === cur.srcVal, 'link Google Sheet còn nguyên', c2.srcVal.slice(-24));
ok(c2.sheet === 'Công đức tháng 9', 'tên trang tính còn nguyên', c2.sheet);
ok(c2.headRow === 'Dòng 2', 'dòng tiêu đề còn nguyên', c2.headRow);
ok(c2.cols[0].use === 'Tên người {ten}', 'khớp cột còn nguyên');
ok(c2.T.mau === cur.T.mau, 'mẫu câu mỗi dòng còn nguyên');
ok(c2.T.dau === 'Nam mô A Di Đà Phật.', 'khối đầu danh sách còn nguyên');
ok(doc.nav === 4, 'mục đang mở ở dải trái còn nguyên', String(doc.nav));

// --- B. rows KHONG duoc mang xuong dia ---
console.log('\n--- B. Dữ liệu bảng tính KHÔNG đi vào tệp hồ sơ ---');
const chu = JSON.stringify(daLuu);
ok(daLuu.maus.every((m) => !('rows' in m)), 'không mẫu nào mang theo rows');
ok(daLuu.maus.every((m) => !('sheetOpts' in m)), 'không mẫu nào mang theo sheetOpts');
ok(!chu.includes('Nguyễn Văn An'), 'không một dòng dữ liệu nào lọt vào bản lưu');
ok(chu.length < 12000, 'bản lưu gọn dưới 12 KB', `${chu.length} ký tự`);
ok(Array.isArray(c2.maus === undefined ? c2.rows : c2.rows),
   'đọc lại vẫn có rows để màn hình vẽ được (mượn của bản mặc định)');

// --- C. Ghep theo ID, khong theo thu tu ---
console.log('\n--- C. Ghép theo ID chứ không theo thứ tự ---');
const luoiDao = ban_sao(daLuu);
luoiDao.maus.reverse();
const doc2 = M.vbgTuDaLuu(luoiDao);
const khuon = doc2.maus.find((m) => m.id === cur.id);
ok(khuon && khuon.srcVal === cur.srcVal,
   'đảo ngược thứ tự mẫu vẫn ghép đúng khuôn', khuon ? khuon.id : '(không thấy)');

// --- D. Khuon nguoi dung tu tao ---
console.log('\n--- D. Khuôn người dùng tự tạo không bị bỏ rơi ---');
const themMoi = ban_sao(daLuu);
themMoi.maus.push({ id: 'cua-toi', name: 'Bảng lương tổ 3', preset: 'congduc',
                    srcType: 2, srcVal: 'D:/bangluong.xlsx', cols: [], T: {} });
const doc3 = M.vbgTuDaLuu(themMoi);
const tuTao = doc3.maus.find((m) => m.id === 'cua-toi');
ok(!!tuTao, 'khuôn tự tạo còn sau khi đọc lại');
ok(tuTao && tuTao.srcVal === 'D:/bangluong.xlsx', 'đường dẫn tệp của nó còn nguyên');
ok(tuTao && Array.isArray(tuTao.rows), 'nó có rows rỗng để màn hình khỏi vỡ');

// --- E. Ban luu hong / rong thi ve mac dinh, khong nem loi ---
console.log('\n--- E. Bản lưu hỏng thì về mặc định, không ném lỗi ---');
for (const xau of [null, undefined, {}, { maus: 'khong phai mang' }]) {
  const r = M.vbgTuDaLuu(xau);
  if (!(r && Array.isArray(r.maus) && r.maus.length)) {
    ok(false, `bản lưu ${JSON.stringify(xau)} -> vẫn phải ra bản mặc định`);
  }
}
ok(true, 'bốn kiểu bản lưu hỏng đều về bản mặc định');
ok(M.vbgCanLuu(null) === null, 'không có gì để lưu thì trả null, không dựng rác');

console.log(loi ? `\nĐỎ — ${loi} chỗ lệch` : '\nXANH — mẫu ghép nhớ được qua lần đóng cửa sổ');
process.exit(loi ? 1 : 0);
