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


/* ------------------------------------------------------------------------
   F. TRÁO CẤU HÌNH KHI ĐỔI HỒ SƠ

   Vòng trước bài này chỉ kiểm hai hàm tuần tự hoá (vbgCanLuu / vbgTuDaLuu),
   trong khi BỐN hàm thật sự nối vào mã chạy — vbgGhiNho, vbgDoiSang, vbgDeLuu,
   vbgNapTuHoSo — không có phép nào. Đó mới là mấy hàm chạm trạng thái thật.

   Điều phải chứng minh: link Sheet của hồ sơ này KHÔNG được rò sang hồ sơ kia.
   Đúng buổi lễ ở chùa, đổi hồ sơ mà mẫu ghép vẫn của hồ sơ cũ thì máy đọc nhầm
   danh sách.                                                              */
console.log('\n--- F. Tráo cấu hình khi đổi hồ sơ ---');

const LINK_A = 'https://docs.google.com/spreadsheets/d/CHUA-A/edit';
const LINK_B = 'https://docs.google.com/spreadsheets/d/CHUA-B/edit';

// Hồ sơ 0: đặt link A
M.vbgDoiSang(0);
const d0 = M.vbgHienTai();
d0.maus[d0.mauHienTai].srcVal = LINK_A;
ok(M.vbgHienTai().maus[M.vbgHienTai().mauHienTai].srcVal === LINK_A,
   'đặt link cho hồ sơ 0');

// Chuyển sang hồ sơ 1 — phải là bản KHÁC, chưa có link A
M.vbgGhiNho(0);
M.vbgDoiSang(1);
const d1 = M.vbgHienTai();
ok(d1 !== d0, 'đổi hồ sơ thì duLieuVBG trỏ sang bản khác hẳn');
ok(d1.maus[d1.mauHienTai].srcVal !== LINK_A,
   'link của hồ sơ 0 KHÔNG rò sang hồ sơ 1',
   d1.maus[d1.mauHienTai].srcVal.slice(-18));

// Đặt link B cho hồ sơ 1 rồi quay lại hồ sơ 0
d1.maus[d1.mauHienTai].srcVal = LINK_B;
M.vbgGhiNho(1);
M.vbgDoiSang(0);
ok(M.vbgHienTai().maus[M.vbgHienTai().mauHienTai].srcVal === LINK_A,
   'quay lại hồ sơ 0 thì link A còn nguyên');

// vbgDeLuu lấy đúng bản của từng hồ sơ, kể cả hồ sơ KHÔNG đang mở
const luu0 = M.vbgDeLuu(0, 0);
const luu1 = M.vbgDeLuu(1, 0);
ok(luu0.maus.find((m) => m.srcVal === LINK_A), 'lưu hồ sơ 0 ra đúng link A');
ok(luu1 && luu1.maus.find((m) => m.srcVal === LINK_B),
   'lưu hồ sơ 1 ra đúng link B dù nó KHÔNG phải hồ sơ đang mở');
ok(M.vbgDeLuu(5, 0) === null, 'hồ sơ chưa đụng tới thì trả null, không dựng rác');

/* ------------------------------------------------------------------------
   G. DỰNG LẠI KHO TỪ HỒ SƠ ĐÃ LƯU (lúc khởi động)                        */
console.log('\n--- G. Dựng lại kho lúc khởi động ---');

const dsHoSo = [
  { ma: 'a', ten: 'Chùa A', vanBanGhep: luu0 },
  { ma: 'b', ten: 'Chùa B', vanBanGhep: luu1 },
  { ma: 'c', ten: 'Chưa dùng' },                 // không có mẫu ghép
];
M.vbgNapTuHoSo(dsHoSo, 1);
ok(M.vbgHienTai().maus.find((m) => m.srcVal === LINK_B),
   'khởi động ở hồ sơ 1 thì mở ra đúng mẫu ghép của nó');

M.vbgDoiSang(0);
ok(M.vbgHienTai().maus.find((m) => m.srcVal === LINK_A),
   'chuyển sang hồ sơ 0 vẫn đúng mẫu ghép của nó');

M.vbgDoiSang(2);
const d2 = M.vbgHienTai();
ok(!d2.maus.some((m) => m.srcVal === LINK_A || m.srcVal === LINK_B),
   'hồ sơ chưa có mẫu ghép thì nhận bản mặc định, không mượn của ai');
ok(Array.isArray(d2.maus) && d2.maus.length > 0,
   'và bản mặc định ấy dựng được, không rỗng');

// Danh sách hồ sơ rỗng / hỏng thì không được ném lỗi
M.vbgNapTuHoSo(null, 0);
M.vbgNapTuHoSo([], 0);
M.vbgNapTuHoSo([{ ten: 'không có mẫu ghép' }], 0);
ok(true, 'danh sách hồ sơ rỗng hoặc thiếu khoá đều không ném lỗi');

console.log(loi ? `\nĐỎ — ${loi} chỗ lệch` : '\nXANH — mẫu ghép nhớ được qua lần đóng cửa sổ');
process.exit(loi ? 1 : 0);
