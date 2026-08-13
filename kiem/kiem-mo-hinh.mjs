import { createRequire } from 'module';
const req = createRequire(import.meta.url);
const D = req('../ui-moi/du-lieu-mau.js');
const T = req('../ui-moi/trang-thai.js');

let loi = 0;
const ok = (dk, nhan, them = '') => {
  console.log(`  ${dk ? 'ĐẠT ' : 'LỆCH'} ${nhan}${them ? '  →  ' + them : ''}`);
  if (!dk) loi++;
};

console.log('--- A. Tài liệu chính phải khớp con số in trong bản mẫu ---');
const A = D.TAI_LIEU['thongbao-quoc-khanh.txt'].doan;
const tu = T.soTu(A), giay = T.soGiay(A), tk = T.thongKe(A);
console.log(`  thống kê dựng ra: "${tk}"`);
console.log(`  (thô: ${tu} từ · ${A.length} đoạn · ${giay.toFixed(1)} giây · ${A.reduce((t,d)=>t+d.chu.length,0)} ký tự)`);
ok(A.length === 16, '16 đoạn', String(A.length));
ok(Math.abs(tu - 215) <= 4, '≈215 từ (sai số ±4)', String(tu));
ok(tk.includes('1 phút 28 giây'), 'thời lượng "1 phút 28 giây"');

console.log('\n--- B. Loại đoạn và thẻ cảm xúc ---');
const kieu = new Set(A.map(d => d.kieu));
ok(kieu.has('head') && kieu.has('body') && kieu.has('blank'), 'có đủ head/body/blank',
   [...kieu].join(','));
let S = T.trangThaiBanDau(D.HO_SO);
ok(T.theCuaDoan(S, 11) === '[hắng giọng]', 'đoạn 11 có [hắng giọng]', T.theCuaDoan(S,11));

console.log('\n--- C. Bốn hồ sơ và tab riêng ---');
ok(S.profiles.length === 4, '4 hồ sơ');
ok(S.profiles[3].ten === 'Danh sách, biểu mẫu', 'hồ sơ 4 đã đổi tên', S.profiles[3].ten);
ok(T.tabDangMo(S).length === 2, 'hồ sơ 1 có 2 tệp mở');
ok(T.tomTatChinh(S.profiles[2].chinh) === 'Tốc độ −10% · Âm lượng 90%',
   'tóm tắt điều chỉnh hồ sơ Sách nói', T.tomTatChinh(S.profiles[2].chinh));

console.log('\n--- D. Đổi hồ sơ thì ĐỔI HẾT theo ---');
const truoc = { tep: T.tenTepDangXem(S), giong: T.hoSoDangDung(S).giong,
                chuY: T.chuYDangXem(S, D.TAI_LIEU).tomTat };
let S2 = T.doiHoSo(S, 2);
const sau = { tep: T.tenTepDangXem(S2), giong: T.hoSoDangDung(S2).giong,
              chuY: T.chuYDangXem(S2, D.TAI_LIEU).tomTat };
ok(truoc.tep !== sau.tep, 'tệp đang xem đổi', `${truoc.tep} → ${sau.tep}`);
ok(truoc.giong !== sau.giong, 'giọng đổi', `${truoc.giong} → ${sau.giong}`);
ok(truoc.chuY !== sau.chuY, 'Cần chú ý đổi');
ok(S2.pos === 1 && S2.sel === 1 && S2.view === 'san_sang', 'về đoạn 1, ngừng đọc');

console.log('\n--- E. Bấm số đoạn vs Nghe toàn bộ ---');
let S3 = T.ngheRiengDoan(S, 5);
ok(S3.mode === 'one' && S3.pos === 5 && S3.sel === 5 && S3.view === 'dang_doc',
   'bấm số đoạn 5 → nghe riêng đoạn 5');
ok(T.hetDoan(S3).view === 'san_sang', 'hết đoạn ở chế độ nghe riêng thì DỪNG');
let S4 = T.ngheToanBo(S);
ok(S4.mode === 'all' && S4.pos === 1, 'Nghe toàn bộ → liền mạch từ đoạn 1');
ok(T.hetDoan(S4).view === 'dang_doc', 'liền mạch thì KHÔNG dừng giữa chừng');
const rieng = T.tongThoiLuongDangNghe(S3, D.TAI_LIEU);
const caBai = T.tongThoiLuongDangNghe(S4, D.TAI_LIEU);
ok(rieng < caBai, 'đồng hồ nghe riêng đếm theo đoạn, không phải cả bài',
   `${rieng.toFixed(1)}s vs ${caBai.toFixed(1)}s`);
ok(T.chonDoan(S, 7).view === 'san_sang' && T.chonDoan(S, 7).sel === 7,
   'bấm thân đoạn = chọn, KHÔNG phát tiếng');

console.log('\n--- F. Ghi vào hồ sơ đang dùng, không phải biến toàn cục ---');
let S5 = T.datGiong(S, 'thien-tam');
ok(S5.profiles[0].giong === 'thien-tam', 'hồ sơ đang dùng đổi giọng');
ok(S5.profiles[1].giong === S.profiles[1].giong, 'hồ sơ khác KHÔNG bị đổi lây');
let S6 = T.datChinh(S, 'amLuong', 70);
ok(S6.profiles[0].chinh.amLuong === 70 && S6.profiles[3].chinh.amLuong === 100,
   'kéo thanh chỉ ghi vào hồ sơ đang dùng');

console.log('\n--- G. Tab: đóng / thêm ---');
let S7 = T.dongTab(T.dongTab(S, 0), 0);
ok(T.tabDangMo(S7).length === 1 && T.tabDangMo(S7)[0] === '',
   'đóng hết tab thì còn lại 1 tab Chưa đặt tên rỗng');
ok(T.themTab(S).tabsByProfile[0].length === 3, 'thêm tab');
ok(S.tabsByProfile[1].length === 1, 'thao tác trên hồ sơ 1 không đụng hồ sơ 2');

console.log('\n--- H. Khoá nút theo tình huống ---');
for (const [th, mongKhoa] of [['binh_thuong',false],['mat_ket_noi',true],['het_luot',true],
                              ['giong_dang_tai',true],['van_ban_qua_dai',false],
                              ['am_thanh_cu',false],['dang_tao',false]]) {
  ok(T.biKhoa({situation: th}) === mongKhoa,
     `${th} → ${mongKhoa ? 'khoá' : 'không khoá'} Nghe/Xuất`);
}
ok(T.hienNgheVaXuat(S, D.TAI_LIEU) === true, 'có văn bản → hiện cặp Nghe/Xuất');
const rong = T.themTab(S);
ok(T.hienNgheVaXuat(rong, D.TAI_LIEU) === false, 'tab rỗng → ẨN HẲN cặp Nghe/Xuất');

console.log('\n--- I. Định dạng thời lượng ---');
ok(T.dinhDangThoiLuong(42) === '42 giây', '42 giây');
ok(T.dinhDangThoiLuong(88) === '1 phút 28 giây', '1 phút 28 giây');
ok(T.dinhDangThoiLuong(120) === '2 phút', '2 phút (chẵn thì không ghi 0 giây)');
ok(T.dinhDangThoiLuong(59) === '59 giây', 'dưới 60 giây');

console.log('\n--- J. Thẻ cảm xúc chèn/gỡ đúng đoạn đang chọn ---');
let S8 = T.datThe(T.chonDoan(S, 5), '[cười]');
ok(T.theCuaDoan(S8, 5) === '[cười]', 'chèn vào đoạn đang chọn');
ok(T.theCuaDoan(S8, 11) === '[hắng giọng]', 'thẻ cũ ở đoạn khác còn nguyên');
ok(T.theCuaDoan(T.datThe(S8, ''), 5) === '', 'gỡ thẻ được');

console.log('\n--- K. Chia chữ để tô chạy theo tiếng ---');
{
  const w = T.chiaTu('Kính gửi toàn thể cán bộ, nhân viên Công ty TNHH Phúc Lâm.');
  ok(w.length === 13, 'chia đúng số chữ', String(w.length));
  ok(w[0].b === 0 && Math.abs(w[w.length - 1].e - 1) < 1e-9, 'phủ kín khoảng [0,1]');
  ok(w.every((x, i) => i === 0 || Math.abs(x.b - w[i - 1].e) < 1e-9), 'không hở, không chồng');
  ok(T.chiaTu('').length === 0, 'đoạn rỗng trả mảng rỗng');
  ok(T.chiaTu('   ').length === 0, 'đoạn toàn khoảng trắng trả mảng rỗng');
  const d = T.chiaTu('a bbbb');
  ok(d[1].e - d[1].b > d[0].e - d[0].b, 'chữ dài chiếm khoảng thời gian dài hơn');
}

console.log('\n--- L. Đồng hồ làm tròn giống dòng thống kê ---');
ok(T.dongHo(87.9) === '01:28' && T.dinhDangThoiLuong(87.9) === '1 phút 28 giây',
   'cùng tài liệu ra cùng con số', T.dongHo(87.9) + ' / ' + T.dinhDangThoiLuong(87.9));
ok(T.dongHo(8) === '00:08', 'dưới 10 giây có số 0 đứng đầu', T.dongHo(8));

console.log(`\n${loi === 0 ? 'XANH — khớp hết' : `ĐỎ — ${loi} chỗ lệch`}`);
process.exit(loi ? 1 : 0);
