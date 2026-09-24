/* Kiểm ĐƯỜNG CÓ PYTHON: giả lập gói tin vòng đọc đẩy về, xem giao diện có
   phản ứng đúng không.

   Chạy:  node ui-moi/kiem-nhan-python.mjs

   Bộ kiểm kia (kiem-giao-dien.mjs) chỉ chạy đường mock. Đường này khác hẳn:
   vị trí đoạn do Python quyết, mốc tô chữ lấy từ thời lượng WAV thật. */

import { readFileSync } from 'fs';
import { createContext, runInContext } from 'vm';
import { fileURLToPath } from 'url';
import { dirname, join } from 'path';

const DIR = dirname(fileURLToPath(import.meta.url));
// Bộ kiểm nằm trong tests/, mã nguồn giao diện ở src/web/
const UI = join(DIR, '..', 'src', 'web');
const goiSangPython = [];
let soLanBocSpan = 0;
let nhipDangChay = 0;

function nutChu() {
  return {
    dataset: {},   // batDauToChu lưu bản gốc vào dataset.goc — phải giữ được
    querySelector: () => null, querySelectorAll: () => [],
    get textContent() { return 'Kính gửi toàn thể cán bộ nhân viên'; },
    set textContent(v) {},
    set innerHTML(v) { if (v.includes('class="tu"')) soLanBocSpan++; },
    get innerHTML() { return ''; },
  };
}
const chuCuaDoan = {};   // giữ NGUYÊN một node .doan__chu cho mỗi đoạn
function nutDoan(n) {
  if (!chuCuaDoan[n]) chuCuaDoan[n] = nutChu();
  return {
    dataset: { doan: String(n) },
    classList: { toggle() {}, add() {}, remove() {} },
    querySelector: (s) => (s === '.doan__chu' ? chuCuaDoan[n] : { set textContent(v) {} }),
    getBoundingClientRect: () => ({ top: 0, height: 40 }),
  };
}
const ghiNhan = {};
function nutThuong(id = '') {
  return {
    id, dataset: {}, style: {}, scrollTop: 0, value: '',
    classList: { toggle() {}, add() {}, remove() {} },
    focus() {}, remove() {}, appendChild() {}, scrollTo() {},
    querySelector: () => nutThuong(), querySelectorAll: () => [],
    getBoundingClientRect: () => ({ left: 0, top: 0, width: 200, height: 40 }),
    set textContent(v) { ghiNhan[id] = v; },
    set innerHTML(v) {}, get innerHTML() { return ''; },
    set onchange(f) {}, set onclick(f) {},
  };
}

const henDangCho = [];
let soHen = 0;
const xaHenGio = () => { const ds = henDangCho.splice(0); ds.forEach((f) => f()); };

/* Câu trả lời giả cho từng hàm Python, đặt theo bài kiểm. */
const ketQuaGia = {};

const ctx = {
  console,
  performance: { now: () => 0 },
  requestAnimationFrame: () => 1, cancelAnimationFrame() {},
  setInterval: (f) => { nhipDangChay++; return nhipDangChay; },
  clearInterval() { if (nhipDangChay) nhipDangChay--; },
  /* Hẹn giờ KHÔNG tự chạy: bài kiểm gọi xaHenGio() lúc muốn. Đường lưu hồ sơ
     có debounce 600 ms, để nó tự chạy thì hoặc phải chờ thật, hoặc mọi hẹn giờ
     khác (nghe mẫu 2,5 giây) cũng nổ theo và làm lệch trạng thái. */
  setTimeout: (f) => { if (typeof f === 'function') henDangCho.push(f); return ++soHen; },
  clearTimeout(id) { if (id === soHen) henDangCho.pop(); },
  location: { search: '' }, URLSearchParams,
  document: {
    documentElement: { dataset: {}, style: { setProperty() {}, removeProperty() {} } }, body: { appendChild() {} },
    activeElement: { tagName: 'DIV' },
    querySelector: (s) => (s === '#cuon' ? nutThuong('cuon') : nutThuong(s.replace('#', ''))),
    querySelectorAll: (s) => (s === '[data-doan]'
      ? Array.from({ length: 16 }, (_, i) => nutDoan(i + 1)) : []),
    getElementById: () => null, createElement: () => nutThuong(),
    addEventListener() {},
  },
  window: {
    addEventListener() {},
    // Giả có Python: mọi lời gọi ghi lại để kiểm đúng hàm, đúng tham số.
    pywebview: {
      api: new Proxy({}, {
        get: (_, ten) => (...ts) => {
          goiSangPython.push([String(ten), ...ts]);
          // Mặc định trả null như một Api chưa có gì; bài kiểm nào cần câu trả
          // lời thật thì đặt trước vào ketQuaGia.
          return Promise.resolve(
            Object.prototype.hasOwnProperty.call(ketQuaGia, ten) ? ketQuaGia[ten] : null);
        },
        has: () => true,
      }),
    },
  },
  localStorage: { getItem: () => null, setItem() {} },
  module: undefined,
};
ctx.globalThis = ctx;
createContext(ctx);
for (const f of ['du-lieu-mau.js', 'trang-thai.js', 'tinh-huong.js', 'cau-noi.js', 'hop-thoai.js', 'giao-dien.js']) {
  runInContext(readFileSync(join(UI, f), 'utf8'), ctx, { filename: f });
}

let loi = 0;
const ok = (dk, nhan, them = '') => {
  console.log(`  ${dk ? 'ĐẠT ' : 'LỆCH'} ${nhan}${them ? '  →  ' + them : ''}`);
  if (!dk) loi++;
};
const chay = (ma) => runInContext(ma, ctx, { filename: 'kiem' });

/* batDauPhat() nay CHO gui doan sang Python xong moi phat — neu khong thi doi
   tab roi bam Nghe nhanh tay la loa doc tai lieu cua tab truoc. Nen sau khi
   goi no phai xa het microtask moi thay duoc loi goi phat. */
const chayPhat = async (ma) => {
  chay(ma);
  await new Promise((r) => setTimeout(r, 0));
  await new Promise((r) => setTimeout(r, 0));
};
const day = (goi) => chay(`window.gd.push(${JSON.stringify(goi)})`);

/* khoiDong() await nạp giọng trước rồi mới gửi đoạn, nên phải xả hết microtask
   mới thấy đủ lời gọi. Không xả là bắt hụt và tưởng app hỏng. */
await new Promise((r) => setTimeout(r, 0));

console.log('--- A. Nhận ra có Python ---');
ok(chay('coPython()') === true, 'coPython() thấy pywebview.api');
/* moi_khoi_dong là bắt buộc: nó vừa trả danh sách giọng THẬT vừa BẬT MÔ HÌNH.
   Thiếu lời gọi này thì giao diện vẽ đẹp mà bấm Nghe không ra tiếng — đã vấp
   đúng một lần, giữ phép kiểm này lại. */
ok(goiSangPython.some((g) => g[0] === 'moi_khoi_dong'),
   'lúc mở có gọi moi_khoi_dong (nạp giọng + bật mô hình)');
ok(goiSangPython.some((g) => g[0] === 'moi_dat_doan'),
   'lúc mở đã gửi đoạn sang Python', (goiSangPython[0] || [])[0]);
{
  const g = goiSangPython.find((x) => x[0] === 'moi_dat_doan');
  ok(Array.isArray(g[1]) && g[1].length === 7, 'gửi đủ 7 đoạn của tin tức', String(g[1] && g[1].length));
}

console.log('\n--- B. Nghe toàn bộ gọi đúng hàm bên Python ---');
goiSangPython.length = 0;
await chayPhat('dat(ngheToanBo(S)); batDauPhat();');
ok(goiSangPython.some((g) => g[0] === 'moi_nghe_toan_bo'), 'gọi moi_nghe_toan_bo');
ok(!goiSangPython.some((g) => g[0] === 'moi_nghe_doan'), 'KHÔNG gọi nhầm moi_nghe_doan');
ok(nhipDangChay > 0, 'CÓ chạy nhịp đồng hồ (nếu không thì 00:00 đứng im cả bài)');
ok(chay('pythonLai') === true, 'bật cờ Python đang lái');

console.log('\n--- C. Nghe riêng một đoạn ---');
goiSangPython.length = 0;
await chayPhat('dungPhat(); dat(ngheRiengDoan(S, 5)); batDauPhat();');
{
  const g = goiSangPython.find((x) => x[0] === 'moi_nghe_doan');
  ok(!!g, 'gọi moi_nghe_doan');
  ok(g && g[1] === 5, 'kèm đúng số đoạn 5', g && String(g[1]));
}

console.log('\n--- D. Python đẩy vị trí về thì giao diện đi theo ---');
await chayPhat('dungPhat(); dat(ngheToanBo(S)); batDauPhat();');
soLanBocSpan = 0;
day({ state: 'dang_doc', pos: 1, doan: 1, thoiLuong: 1.52 });
ok(chay('S.pos') === 1, 'đoạn 1');
ok(soLanBocSpan === 1, 'bọc span ĐÚNG MỘT LẦN cho đoạn 1', String(soLanBocSpan));

soLanBocSpan = 0;
day({ state: 'dang_doc', pos: 2, doan: 3, thoiLuong: 2.8 });
ok(chay('S.pos') === 3, 'Python báo mẩu 2 = đoạn 3 → giao diện nhảy đúng đoạn 3', String(chay('S.pos')));
ok(chay('S.sel') === 3, 'con trỏ đi theo');
ok(soLanBocSpan === 1, 'lại chỉ bọc span một lần (không bọc hai lần)', String(soLanBocSpan));

console.log('\n--- E. Đồng hồ nhích theo nhịp ---');
chay('giayDaNghe = 0; giayDoanNay = 0;');
for (let i = 0; i < 8; i++) chay('giayDaNghe += 0.25; giayDoanNay += 0.25; veNhipDoc();');
ok(ghiNhan.phatGio && ghiNhan.phatGio.startsWith('00:02'),
   'sau 8 nhịp đồng hồ chạy tới 00:02', ghiNhan.phatGio);

console.log('\n--- F. Python báo xong thì giao diện dừng hẳn ---');
day({ state: 'san_sang', pos: 1 });
ok(chay('S.view') === 'san_sang', 'về trạng thái sẵn sàng');
ok(chay('pythonLai') === false, 'hạ cờ Python đang lái');
ok(chay('daTamDung') === false, 'không phải tạm dừng → nút về "Nghe toàn bộ"');

console.log('\n--- G. Python báo tạm dừng ---');
await chayPhat('dat(ngheToanBo(S)); batDauPhat();');
day({ state: 'tam_dung', pos: 3 });
ok(chay('S.view') === 'san_sang', 'ngừng đọc');
ok(chay('daTamDung') === true, 'nhớ là đang tạm dừng → nút ghi "Đọc tiếp"');

console.log('\n--- H. Bấm Tạm dừng / Dừng thì báo sang Python ---');
goiSangPython.length = 0;
await chayPhat("dat(ngheToanBo(S)); batDauPhat(); LENH['Tạm dừng']();");
ok(goiSangPython.some((g) => g[0] === 'moi_tam_dung'), 'gọi moi_tam_dung');
goiSangPython.length = 0;
chay('dungPhat();');
ok(goiSangPython.some((g) => g[0] === 'moi_dung'), 'gọi moi_dung');

console.log('\n--- I. Đổi hồ sơ / đổi tab thì gửi lại đoạn sang Python ---');
goiSangPython.length = 0;
chay('dat(doiHoSo(S, 2)); guiDoanSangPython();');
{
  const g = goiSangPython.find((x) => x[0] === 'moi_dat_doan');
  ok(!!g, 'gửi lại moi_dat_doan');
  ok(g && g[1].length === 5, 'gửi đoạn của tài liệu MỚI (chuong-01.docx, 5 đoạn)',
     g && String(g[1].length));
}

console.log('\n--- I2. Gói KHÔNG có thoiLuong = đang tổng hợp, chưa phát ---');
await chayPhat('dungPhat(); dat(ngheToanBo(S)); batDauPhat();');
soLanBocSpan = 0;
day({ state: 'dang_doc', pos: 1, doan: 1 });           // chưa có thoiLuong
ok(chay("S.situation") === 'dang_tao', 'vào tình huống "Đang tạo âm thanh"',
   chay('S.situation'));
ok(chay('dongHoPhat') === 0, 'đồng hồ ĐỨNG IM trong lúc tổng hợp');
ok(soLanBocSpan === 0, 'chưa bọc span, chưa tô chữ nào');

day({ state: 'dang_doc', pos: 1, doan: 1, thoiLuong: 2.4 });   // tổng hợp xong
ok(chay("S.situation") === 'binh_thuong', 'có thoiLuong → về bình thường');
ok(chay('dongHoPhat') !== 0, 'đồng hồ chạy lại');
ok(soLanBocSpan === 1, 'giờ mới bọc span và tô chữ', String(soLanBocSpan));

console.log('\n--- I3. Đoạn dài cắt nhiều mẩu thì tô TIẾP, không tô lại từ đầu ---');
soLanBocSpan = 0;
day({ state: 'dang_doc', pos: 2, doan: 1, thoiLuong: 1.8 });   // mẩu 2 của CÙNG đoạn 1
ok(soLanBocSpan === 0, 'mẩu tiếp theo KHÔNG bọc span lại', String(soLanBocSpan));
ok(Math.abs(chay('toChuTong') - 4.2) < 1e-6, 'cộng dồn thời lượng 2,4 + 1,8 = 4,2 giây',
   String(chay('toChuTong')));

console.log('\n--- J. Dán văn bản / Mở tệp gọi sang Python ---');
goiSangPython.length = 0;
chay("LENH['Dán văn bản']()");
await new Promise((r) => setTimeout(r, 0));
ok(goiSangPython.some((g) => g[0] === 'moi_dan_van_ban'), 'Dán văn bản → moi_dan_van_ban');
goiSangPython.length = 0;
chay("LENH['Mở tệp…']()");
await new Promise((r) => setTimeout(r, 0));
ok(goiSangPython.some((g) => g[0] === 'moi_mo_tep'), 'Mở file → moi_mo_tep');

console.log('\n--- K. Nhận nội dung mới thì thay vào tab đang xem ---');
chay(`datTaiLieu({ ten: 'thu.txt', doan: [
  { kieu: 'head', chu: 'TIÊU ĐỀ THỬ' },
  { kieu: 'blank', chu: '' },
  { kieu: 'body', chu: 'Một câu để tìm và thay thế.' }] })`);
ok(chay('tenTepDangXem(S)') === 'thu.txt', 'tab đổi sang tệp mới', chay('tenTepDangXem(S)'));
/* Gửi sang 3 đoạn trong đó có MỘT dòng trống, nhận về phải còn 2: bản thiết
   kế cấm đoạn rỗng, và datTaiLieu lọc ngay lúc nạp. Đây là chỗ chứng minh việc
   lọc chạy thật trên đường nạp tệp, không chỉ đúng ở dữ liệu mẫu. */
ok(chay('doanDangXem(S, TAI_LIEU).length') === 2,
   'dòng trống bị bỏ ngay khi nạp: 3 đoạn gửi sang còn 2',
   String(chay('doanDangXem(S, TAI_LIEU).length')));
ok(chay('S.pos') === 1 && chay('S.sel') === 1, 'về đoạn 1');

console.log('\n--- L. Tìm và thay thế chạy thật ---');
chay("chayTim('câu')");
ok(chay('ketQuaTim.length') === 1, 'tìm thấy 1 chỗ', String(chay('ketQuaTim.length')));
chay("chayTim('KHÔNG CÓ CHỮ NÀY')");
ok(chay('ketQuaTim.length') === 0, 'không có thì trả 0');
chay("chayTim('câu'); thayThe('câu', 'dòng', false)");
ok(chay("TAI_LIEU['thu.txt'].doan[1].chu").includes('dòng'), 'đã thay chữ',
   chay("TAI_LIEU['thu.txt'].doan[1].chu"));
ok(chay('S.situation') === 'am_thanh_cu',
   'sửa văn bản xong thì bật tình huống "âm thanh cũ"', chay('S.situation'));

console.log('\n--- M. Hộp thoại xuất ---');
chay("dat({ ...S, situation: 'binh_thuong' }); moHopXuat();");
await new Promise((r) => setTimeout(r, 0));
ok(chay('S.exportOpen') === true, 'bấm Xuất → mở hộp thoại');
// Tài liệu thử gửi sang 3 đoạn nhưng một là dòng trống, đã bị lọc khi nạp.
ok(chay('hopXuat.soDoan') === 2, 'hộp thoại biết số đoạn', String(chay('hopXuat.soDoan')));
/* Luồng ĐÃ ĐỔI (2026-08-13, chủ dự án chốt bám bản mẫu
   designs/GiongDoc - Xuất file âm thanh): bấm Bắt đầu xuất KHÔNG đóng hộp
   nữa mà chuyển nó sang giai đoạn 2, vì đó là chỗ duy nhất có nút Huỷ.
   Muốn đóng hộp thì bấm "Chạy nền". Phép kiểm cũ khoá theo luồng cũ (hộp
   đóng ngay) nên phải viết lại theo luồng này. */
chay('batDauXuat()');
await new Promise((r) => setTimeout(r, 0));
ok(chay('S.exportOpen') === false, 'giai đoạn 1 nhường chỗ');
ok(chay('S.xuatGiaiDoan') === 'chay', 'hộp Ở LẠI, chuyển sang giai đoạn 2',
   String(chay('S.xuatGiaiDoan')));
ok(chay('S.exporting') === true, 'chuyển sang trạng thái đang xuất');
{
  const g = goiSangPython.find((x) => x[0] === 'moi_bat_dau_xuat');
  ok(!!g, 'gọi Python xuất THẬT, không chạy đồng hồ giả');
  ok(!!g && g.length === 5, 'gửi đủ tên · thư mục · kiểu tách · định dạng',
     g ? g.slice(1).join(' | ') : '');
}

chay("nhanTienDoXuat({ phanTram: 40, moTa: 'Đang xử lý mục 4/10', daGhi: '2,1 MB' })");
ok(chay('S.phanTramXuat') === 40, 'tiến độ Python đẩy về tới nơi',
   String(chay('S.phanTramXuat')));
ok(chay('S.xuatGiaiDoan') === 'chay', 'tiến độ KHÔNG làm hộp nhảy giai đoạn');

chay("dat({ ...S, xuatGiaiDoan: null })");   // người dùng bấm "Chạy nền"
chay("nhanXuatXong({ ten: 'a.wav', thoiLuong: '1 phút', kichThuoc: '5 MB', thuMuc: 'D:\\\\x' })");
ok(chay('S.exporting') === false, 'chạy nền xong thì hết trạng thái đang xuất');
ok(chay('!!S.toast') === true, 'chạy nền xong → báo bằng thông báo góc');
ok(chay('S.xuatGiaiDoan') === null, 'không bật lại hộp khi người dùng đã cho chạy nền');

chay("dat({ ...S, toast: false, exporting: true, xuatGiaiDoan: 'chay' });"
     + "nhanXuatXong({ ten: 'b.wav', thoiLuong: '2 phút', kichThuoc: '9 MB' })");
ok(chay('S.xuatGiaiDoan') === 'xong', 'hộp còn mở → sang giai đoạn 3, không phải toast');
ok(chay('!S.toast') === true, 'giai đoạn 3 thì KHÔNG hiện thêm thông báo góc');
chay("dat({ ...S, xuatGiaiDoan: null, xuatKetQua: null })");
chay('clearInterval(dongHoXuat)');

console.log('\n--- N. Tạo hồ sơ mới ---');
{
  const truoc = chay('S.profiles.length');
  chay("LENH['Tạo hồ sơ mới']()");
  ok(chay('S.profiles.length') === truoc + 1, 'thêm một hồ sơ');
  ok(chay('S.profile') === truoc, 'chuyển sang hồ sơ mới ngay');
  ok(chay('tabDangMo(S).length') === 1 && chay("tabDangMo(S)[0]") === '',
     'hồ sơ mới có đúng một tab chưa đặt tên');
}

console.log('\n--- O. Hồ sơ được ghi xuống hoso-v2.json ---');
{
  goiSangPython.length = 0;
  henDangCho.length = 0;
  chay("dat(datChinh(S, 'tocDo', 15))");
  ok(henDangCho.length === 1, 'đổi thanh chỉnh thì hẹn MỘT lượt ghi, chưa ghi ngay',
     String(henDangCho.length));
  ok(!goiSangPython.some((g) => g[0] === 'moi_luu_ho_so'), 'chưa hết hẹn thì chưa gọi');

  xaHenGio();
  const goi = goiSangPython.find((g) => g[0] === 'moi_luu_ho_so');
  ok(!!goi, 'hết hẹn thì gọi moi_luu_ho_so');
  const d = goi ? goi[1] : {};
  ok(Array.isArray(d.hoSo) && d.hoSo.length === chay('S.profiles.length'),
     'gói tin có đủ hồ sơ', String(d.hoSo && d.hoSo.length));
  ok(d.hoSo[chay('S.profile')].chinh.tocDo === 15, 'tốc độ vừa kéo nằm trong gói',
     String(d.hoSo[chay('S.profile')].chinh.tocDo));
  ok(Array.isArray(d.hoSo[0].tep), 'mỗi hồ sơ mang theo danh sách tab');
  ok(typeof d.dangDung === 'number' && typeof d.theme === 'string',
     'có hồ sơ đang dùng và giao diện sáng/tối');
  ok(!('pos' in d) && !('sel' in d) && !('view' in d),
     'KHÔNG lưu chỗ đang đọc — mở lên phải là trạng thái nghỉ');

  // Bấm việc không dính đến hồ sơ thì đừng sinh thêm lượt ghi đĩa nào.
  goiSangPython.length = 0;
  chay('dat(moMenu(S, 0)); dat(dongHetMenu(S));');
  xaHenGio();
  ok(!goiSangPython.some((g) => g[0] === 'moi_luu_ho_so'),
     'mở rồi đóng menu KHÔNG ghi lại đĩa');
}

console.log('\n--- P. Mở chương trình lên thì lấy lại hồ sơ đã lưu ---');
{
  ketQuaGia.moi_doc_ho_so = {
    phienBan: 1, dangDung: 1, theme: 'toi',
    the: { 'a.txt': { 3: '[cười]' } },
    duongDan: { 'a.txt': 'C:\\thu\\a.txt' },
    hoSo: [
      { ma: 'h1', ten: 'Hồ sơ một', giong: 'g1',
        chinh: { tocDo: 0, caoDo: 0, amLuong: 100 }, tep: ['a.txt'], dangXem: 0 },
      { ma: 'h2', ten: 'Hồ sơ hai', giong: 'g2',
        chinh: { tocDo: -10, caoDo: 2, amLuong: 90 }, tep: ['b.txt', ''], dangXem: 1 },
    ],
  };
  ketQuaGia.moi_doc_tep = { ten: 'a.txt', duongDan: 'C:\\thu\\a.txt',
                            doan: [{ kieu: 'body', chu: 'Một dòng.' }] };
  goiSangPython.length = 0;
  chay('napHoSoDaLuu()');
  await new Promise((r) => setTimeout(r, 0));
  await new Promise((r) => setTimeout(r, 0));

  ok(chay('S.profiles.length') === 2, 'nạp đúng 2 hồ sơ', String(chay('S.profiles.length')));
  ok(chay('S.profiles[1].ten') === 'Hồ sơ hai', 'đúng tên', chay('S.profiles[1].ten'));
  ok(chay('S.profile') === 1, 'mở lại đúng hồ sơ đang dùng lần trước');
  ok(chay('S.profiles[1].chinh.amLuong') === 90, 'thanh chỉnh sống lại',
     String(chay('S.profiles[1].chinh.amLuong')));
  ok(chay('tabDangMo(S).length') === 2, 'tab của hồ sơ 2 còn đủ',
     String(chay('tabDangMo(S).length')));
  ok(chay('S.activeByProfile[1]') === 1, 'nhớ cả tab đang xem');
  ok(chay('S.theme') === 'toi', 'nhớ giao diện tối');
  ok(chay("S.chips['a.txt'][3]") === '[cười]', 'thẻ cảm xúc còn nguyên');
  ok(chay('S.view') === 'san_sang' && chay('S.pos') === 1,
     'mở lên ở trạng thái nghỉ, không phải đang đọc');
}

console.log('\n--- Q. Đổi sang tab đã lưu thì mở lại nội dung từ đường dẫn ---');
{
  goiSangPython.length = 0;
  chay('chuyenSang(doiHoSo(S, 0))');
  await new Promise((r) => setTimeout(r, 0));
  await new Promise((r) => setTimeout(r, 0));
  const g = goiSangPython.find((x) => x[0] === 'moi_doc_tep');
  ok(!!g, 'có gọi moi_doc_tep để lấy lại nội dung');
  ok(g && g[1] === 'C:\\thu\\a.txt', 'gọi đúng đường dẫn đã lưu', g && String(g[1]));
  ok(chay("!!TAI_LIEU['a.txt']"), 'nội dung đã nằm trong TAI_LIEU');
  ok(goiSangPython.some((x) => x[0] === 'moi_dat_doan'), 'rồi mới dựng playlist');
}

console.log('\n--- R. Giọng: lấy của lần chạy trước, chưa có thì lấy giọng ĐẦU danh sách ---');
{
  const GIONG_THAT = {
    giong: [{ ma: 'that-1', ten: 'Giọng thật một' },
            { ma: 'that-2', ten: 'Giọng thật hai' },
            { ma: 'that-3', ten: 'Giọng thật ba' }],
    // Api cũ vẫn trả trường này (đọc từ cauhinh.ini). Bản mới phải BỎ QUA nó.
    dangDung: 'that-3',
  };

  // R1 — lần chạy đầu: hồ sơ mẫu trỏ giọng mock không có thật.
  chay(`S = { ...S, profiles: [
          { ma: 'a', ten: 'A', giong: 'giong-mock', chinh: { tocDo: 0, caoDo: 0, amLuong: 100 } },
          { ma: 'b', ten: 'B', giong: 'giong-mock-2', chinh: { tocDo: 0, caoDo: 0, amLuong: 100 } }],
        profile: 0, tabsByProfile: { 0: [''], 1: [''] }, activeByProfile: { 0: 0, 1: 0 } };
        giongDaGui = '';
        datGiongThat(${JSON.stringify(GIONG_THAT)})`);
  ok(chay('S.profiles[0].giong') === 'that-1',
     'chưa có lần chạy trước → giọng ĐẦU danh sách', chay('S.profiles[0].giong'));
  ok(chay('S.profiles[0].giong') !== 'that-3',
     'KHÔNG lấy giọng trong cauhinh.ini của bản cũ');

  // R2 — có hồ sơ đã lưu, giọng vẫn còn trên máy thì giữ nguyên.
  chay(`S = { ...S, profiles: [
          { ma: 'a', ten: 'A', giong: 'that-2', chinh: { tocDo: 0, caoDo: 0, amLuong: 100 } }],
        profile: 0, tabsByProfile: { 0: [''] }, activeByProfile: { 0: 0 } };
        giongDaGui = '';
        datGiongThat(${JSON.stringify(GIONG_THAT)})`);
  ok(chay('S.profiles[0].giong') === 'that-2',
     'giọng đã lưu còn trên máy → giữ nguyên', chay('S.profiles[0].giong'));

  // R3 — giọng đã lưu bị gỡ khỏi máy thì rơi về giọng đầu.
  chay(`S = { ...S, profiles: [
          { ma: 'a', ten: 'A', giong: 'da-go-mat', chinh: { tocDo: 0, caoDo: 0, amLuong: 100 } }],
        profile: 0 };
        giongDaGui = '';
        datGiongThat(${JSON.stringify(GIONG_THAT)})`);
  ok(chay('S.profiles[0].giong') === 'that-1',
     'giọng đã bị gỡ → về giọng đầu danh sách', chay('S.profiles[0].giong'));

  // R4 — giọng của hồ sơ phải được báo sang Python, không thì loa đọc giọng khác.
  goiSangPython.length = 0;
  chay("giongDaGui = ''; dongBoGiongSangPython()");
  const g = goiSangPython.find((x) => x[0] === 'doi_giong');
  ok(!!g && g[1] === 'that-1', 'báo giọng sang Python', g && String(g[1]));
  goiSangPython.length = 0;
  chay('dongBoGiongSangPython()');
  ok(!goiSangPython.some((x) => x[0] === 'doi_giong'),
     'giọng không đổi thì KHÔNG gọi lại');
}

console.log('\n--- S. Nút nghe thử phải cho thấy nó đang chạy ---');
{
  /* rieng: false là BẮT BUỘC — veRoiGiong lọc theo `g.rieng === false`, thiếu
     trường này thì cả hai nhóm rỗng và dropdown không vẽ ra nút nào. */
  chay(`datGiongThat({ giong: [
    { ma: 'that-1', ten: 'Giọng một', gioi: 'Nam', vung: 'Miền Bắc', rieng: false },
    { ma: 'that-2', ten: 'Giọng hai', gioi: 'Nữ',  vung: 'Miền Bắc', rieng: false },
    { ma: 'that-3', ten: 'Giọng ba',  gioi: 'Nữ',  vung: 'Miền Nam', rieng: false }] })`);
  chay("S = { ...S, voiceOpen: true, dangNgheThu: '' }");
  goiSangPython.length = 0;
  chay("dat({ ...S, dangNgheThu: 'that-2' }); if (coPython()) api('nghe_thu_giong', 'that-2')");
  ok(chay('S.dangNgheThu') === 'that-2', 'bấm nghe thử thì có cờ đang nghe',
     chay('S.dangNgheThu'));
  ok(goiSangPython.some((g) => g[0] === 'nghe_thu_giong'), 'có gọi sang Python');

  // Nút phải VẼ RA khác lúc thường, không thì cờ có cũng như không.
  const html = chay("veRoiGiong()");
  ok(html.includes('roi__nghe--dang'), 'nút của giọng đó được đánh dấu đang chạy');
  ok(html.includes('bấm để dừng'), 'lời mách nước đổi thành "bấm để dừng"');
  ok((html.match(/roi__nghe--dang/g) || []).length === 1,
     'CHỈ một nút được đánh dấu',
     String((html.match(/roi__nghe--dang/g) || []).length));

  console.log('     · bấm lần nữa = dừng');
  goiSangPython.length = 0;
  chay("dungNgheThu()");
  ok(goiSangPython.some((g) => g[0] === 'moi_dung_nghe_thu'), 'gọi moi_dung_nghe_thu');
  ok(chay('S.dangNgheThu') === '', 'hạ cờ NGAY, không chờ Python báo về');

  console.log('     · Python báo xong thì hạ cờ');
  chay("dat({ ...S, dangNgheThu: 'that-2' })");
  chay("window.gd.ngheThuXong('that-2')");
  ok(chay('S.dangNgheThu') === '', 'ngheThuXong hạ đúng cờ');

  console.log('     · tín hiệu của giọng CŨ không được tắt nút giọng mới');
  chay("dat({ ...S, dangNgheThu: 'that-3' })");
  chay("window.gd.ngheThuXong('that-2')");
  ok(chay('S.dangNgheThu') === 'that-3', 'nút giọng mới còn nguyên',
     chay('S.dangNgheThu'));

  console.log('     · lỗi bên Python thì hạ cờ và nói cho người dùng biết');
  chay("window.gd.baoLoi('Không nghe thử được', 'Thiếu tệp giọng')");
  ok(chay('S.dangNgheThu') === '', 'hạ cờ khi lỗi');
  ok(chay('!!S.toast'), 'có hiện thông báo, không chỉ ghi console');

  console.log('     · đóng ô chọn giọng thì tắt tiếng đang thử');
  chay("dat({ ...S, voiceOpen: true, dangNgheThu: 'that-1', toast: false })");
  goiSangPython.length = 0;
  chay("document.addEventListener; if (S.voiceOpen) dungNgheThu(); dat({ ...S, voiceOpen: false })");
  ok(goiSangPython.some((g) => g[0] === 'moi_dung_nghe_thu'), 'có bảo Python dừng');
  ok(chay('S.dangNgheThu') === '' && chay('S.voiceOpen') === false, 'ô đóng, cờ hạ');
}

console.log('\n--- T. Thứ tự giọng: vùng miền → Nam/Nữ → A-Z tên ---');
{
  const G = [
    { ma: '1', ten: 'Thùy Dung', gioi: 'Nữ',  vung: 'Miền Nam',   rieng: false },
    { ma: '2', ten: 'Trúc Ly',   gioi: 'Nữ',  vung: 'Miền Bắc',   rieng: false },
    { ma: '3', ten: 'Minh Đức',  gioi: 'Nam', vung: 'Miền Bắc',   rieng: false },
    { ma: '4', ten: 'Đoan Trang', gioi: 'Nữ', vung: 'Miền Bắc',   rieng: false },
    { ma: '5', ten: 'Ngọc Trân', gioi: 'Nữ',  vung: 'Miền Trung', rieng: false },
    { ma: '6', ten: 'Anh Khoa',  gioi: 'Nam', vung: 'Miền Bắc',   rieng: false },
  ];
  const ten = chay(`${JSON.stringify(G)}.sort(xepGiong).map((g) => g.ten)`);
  ok(ten[0] === 'Anh Khoa' && ten[1] === 'Minh Đức',
     'Miền Bắc trước, trong đó Nam trước Nữ, A-Z', ten.join(' · '));
  ok(ten[2] === 'Đoan Trang' && ten[3] === 'Trúc Ly',
     'nữ Miền Bắc xếp A-Z, "Đoan Trang" trước "Trúc Ly"');
  ok(ten[4] === 'Ngọc Trân', 'rồi tới Miền Trung', ten[4]);
  ok(ten[5] === 'Thùy Dung', 'cuối cùng Miền Nam', ten[5]);
}

console.log('\n--- U. Đổi tab rồi bấm Nghe: phải đọc ĐÚNG tài liệu đang hiện ---');
{
  // Dựng hai tài liệu khác hẳn nhau, giống hệt tình huống đã xảy ra thật:
  // màn hình hiện "phun thuốc" mà loa đọc "nghỉ lễ".
  chay(`TAI_LIEU['nghi-le.txt'] = { doan: [
          { kieu: 'head', chu: 'THÔNG BÁO NGHỈ LỄ' },
          { kieu: 'body', chu: 'Nghỉ từ ngày mai.' }], chuY: { tomTat: '', loai: [] } };
        TAI_LIEU['phun-thuoc.txt'] = { doan: [
          { kieu: 'head', chu: 'THÔNG BÁO PHUN THUỐC DIỆT MUỖI' },
          { kieu: 'body', chu: 'Kính mời bà con chú ý nghe thông báo.' },
          { kieu: 'body', chu: 'Sáng mai từ sáu giờ đến chín giờ.' }], chuY: { tomTat: '', loai: [] } };
        S = { ...S, profiles: [{ ma: 'a', ten: 'A', giong: 'that-1',
                                 chinh: { tocDo: 0, caoDo: 0, amLuong: 100 } }],
              profile: 0,
              tabsByProfile: { 0: ['nghi-le.txt', 'phun-thuoc.txt'] },
              activeByProfile: { 0: 0 }, view: 'san_sang', mode: 'all', pos: 1 };
        vanTayDaGui = '';`);

  // Api thật trả {soMau, soDoan}; Proxy mặc định trả null, mà null nghĩa là
  // "gửi hỏng" nên lần nào cũng gửi lại — phải giả cho đúng.
  ketQuaGia.moi_dat_doan = { soMau: 3, soDoan: 3 };

  goiSangPython.length = 0;
  chay('guiDoanSangPython()');
  await new Promise((r) => setTimeout(r, 0));
  const g1 = goiSangPython.find((x) => x[0] === 'moi_dat_doan');
  ok(!!g1 && g1[1][0].chu.includes('NGHỈ LỄ'), 'gửi tài liệu của tab 1');

  // Đổi sang tab 2 rồi bấm Nghe NGAY, không chờ gì cả.
  chay('S = { ...S, activeByProfile: { 0: 1 } }');
  goiSangPython.length = 0;
  chay('batDauPhat()');
  await new Promise((r) => setTimeout(r, 0));
  await new Promise((r) => setTimeout(r, 0));

  const iDat = goiSangPython.findIndex((x) => x[0] === 'moi_dat_doan');
  const iNghe = goiSangPython.findIndex((x) => x[0] === 'moi_nghe_toan_bo');
  ok(iDat >= 0, 'có gửi lại đoạn của tab mới');
  ok(iNghe >= 0, 'có gọi phát');
  ok(iDat >= 0 && iNghe >= 0 && iDat < iNghe,
     'gửi đoạn TRƯỚC rồi mới phát', `moi_dat_doan #${iDat} < moi_nghe #${iNghe}`);
  const g2 = goiSangPython[iDat];
  ok(g2 && g2[1][0].chu.includes('PHUN THUỐC'),
     'nội dung gửi đi là của tab ĐANG HIỆN', g2 && g2[1][0].chu.slice(0, 30));
  ok(g2 && g2[1].length === 3, 'đúng 3 đoạn của tài liệu mới', g2 && g2[1].length);

  console.log('     · cùng một tài liệu thì không gửi lại thừa');
  goiSangPython.length = 0;
  chay('batDauPhat()');
  await new Promise((r) => setTimeout(r, 0));
  await new Promise((r) => setTimeout(r, 0));
  ok(!goiSangPython.some((x) => x[0] === 'moi_dat_doan'),
     'bấm Nghe lần nữa KHÔNG dựng lại playlist');

  console.log('     · sửa chữ trong tài liệu thì phải gửi lại');
  chay("TAI_LIEU['phun-thuoc.txt'].doan[1].chu = 'Câu này đã bị sửa dài thêm ra.'");
  goiSangPython.length = 0;
  chay('batDauPhat()');
  await new Promise((r) => setTimeout(r, 0));
  await new Promise((r) => setTimeout(r, 0));
  ok(goiSangPython.some((x) => x[0] === 'moi_dat_doan'),
     'nội dung đổi → gửi lại');

  console.log('     · gửi hỏng thì KHÔNG được đánh dấu là đã gửi');
  ketQuaGia.moi_dat_doan = null;
  chay("TAI_LIEU['phun-thuoc.txt'].doan[1].chu = 'Sửa lần nữa cho khác đi.'");
  chay('guiDoanSangPython()');
  await new Promise((r) => setTimeout(r, 0));
  ok(chay('vanTayDaGui') === '', 'dấu vân bị xoá để lần sau gửi lại');
  delete ketQuaGia.moi_dat_doan;
}

/* Chín lệnh menu vừa nối: CHẠY THẬT từng cái.

   kiem_menu.py chỉ đọc mã nguồn — nó chứng minh "có khoá, có thân hàm", chứ
   không chứng minh hàm chạy không ném lỗi. Mà với người dùng đích, một lệnh
   ném exception cho ra đúng triệu chứng của nút giả cũ: bấm vào, menu đóng,
   không có gì xảy ra. Nên phải gọi thật. */
console.log('\n--- Z. Chín lệnh menu mới chạy thật, không chỉ có tên ---');
{
  chay("dat({ ...S, man: 'chinh', situation: 'binh_thuong', hopTin: null, tags: false })");
  const TEN = ['Lưu', 'Đóng tệp', 'Thẻ cảm xúc', 'Đổi giọng đọc', 'Nghe mẫu giọng',
               'Cỡ chữ lớn hơn', 'Cỡ chữ nhỏ hơn', 'Hướng dẫn nhanh',
               'Danh sách phím tắt', 'Giới thiệu Giọng Việt'];
  for (const ten of TEN) {
    let vap = null;
    try {
      chay(`LENH[${JSON.stringify(ten)}]()`);
    } catch (e) {
      vap = String(e && e.message ? e.message : e);
    }
    ok(!vap, `'${ten}' gọi được, không ném lỗi`, vap || '');
    chay("dat({ ...S, hopTin: null, tags: false })");
  }

  // Gọi được là một chuyện, LÀM ĐÚNG VIỆC lại là chuyện khác.
  const truoc = chay('S.zoom');
  chay("LENH['Cỡ chữ lớn hơn']()");
  ok(chay('S.zoom') === truoc + 10, 'Cỡ chữ lớn hơn thực sự tăng cỡ chữ',
     `${truoc} → ${chay('S.zoom')}`);
  chay("LENH['Cỡ chữ nhỏ hơn']()");
  ok(chay('S.zoom') === truoc, 'Cỡ chữ nhỏ hơn trả về như cũ', String(chay('S.zoom')));

  chay('dat({ ...S, zoom: 200 })');
  chay("LENH['Cỡ chữ lớn hơn']()");
  ok(chay('S.zoom') === 200, 'kịch trần 200% thì không vọt tiếp', String(chay('S.zoom')));
  chay('dat({ ...S, zoom: 80 })');
  chay("LENH['Cỡ chữ nhỏ hơn']()");
  ok(chay('S.zoom') === 80, 'kịch sàn 80% thì không tụt tiếp', String(chay('S.zoom')));
  chay('dat({ ...S, zoom: 100 })');

  chay("LENH['Thẻ cảm xúc']()");
  ok(chay('S.tags') === true, 'Thẻ cảm xúc BẬT menu thẻ — thứ trước đây không nơi nào bật');
  chay('dat({ ...S, tags: false })');

  for (const ten of ['Hướng dẫn nhanh', 'Danh sách phím tắt', 'Giới thiệu Giọng Việt']) {
    chay(`LENH[${JSON.stringify(ten)}]()`);
    ok(chay('!!S.hopTin') === true, `'${ten}' mở được hộp thoại`);
    ok(chay('(S.hopTin.dong || []).length') > 0, `'${ten}' có nội dung, không rỗng`,
       String(chay('(S.hopTin.dong || []).length')));
    chay('dat({ ...S, hopTin: null })');
  }

  goiSangPython.length = 0;
  chay("LENH['Lưu']()");
  await new Promise((r) => setTimeout(r, 0));
  ok(goiSangPython.some((g) => g[0] === 'moi_luu_van_ban'),
     'Lưu gọi thật sang Python để ghi tệp',
     goiSangPython.map((g) => g[0]).join(', ') || '(không gọi gì)');
}

/* Ba thanh chỉnh: kiểm GIÁ TRỊ gửi sang Python, không chỉ kiểm "có gọi".

   Bộ kiểm cũ chỉ canh `moi_dat_chinh_am` có được gọi hay không, nên nó xanh
   suốt trong khi tính năng chết hẳn: guiChinhAm() đọc h.tocDo, mà datChinh()
   ghi vào h.chinh.tocDo — cả ba ra undefined, Python nhận giá trị rỗng nên
   dựng chuỗi lọc rỗng. Kéo Tốc độ lên +95% mà tiếng y nguyên. Chủ dự án bấm
   thử mới lộ. Từ nay phải soi đúng con số đi qua dây. */
console.log('\n--- Y. Ba thanh chỉnh gửi ĐÚNG GIÁ TRỊ sang Python ---');
{
  chay("dat({ ...S, man: 'chinh' })");
  goiSangPython.length = 0;
  chay("dat(datChinh(S, 'tocDo', 80))");
  await new Promise((r) => setTimeout(r, 0));

  const g = goiSangPython.find((x) => x[0] === 'moi_dat_chinh_am');
  ok(!!g, 'kéo thanh Tốc độ thì có gọi sang Python');
  const d = g ? g[1] : {};
  ok(d.tocDo === 80, 'gửi ĐÚNG con số vừa kéo, không phải undefined',
     `tocDo = ${JSON.stringify(d.tocDo)}`);
  ok(d.caoDo !== undefined && d.amLuong !== undefined,
     'hai thanh còn lại cũng có giá trị thật',
     `caoDo=${JSON.stringify(d.caoDo)} amLuong=${JSON.stringify(d.amLuong)}`);

  // Kéo tiếp giá trị khác thì phải gửi lại, không được nghĩ là "chưa đổi".
  goiSangPython.length = 0;
  chay("dat(datChinh(S, 'tocDo', -30))");
  await new Promise((r) => setTimeout(r, 0));
  const g2 = goiSangPython.find((x) => x[0] === 'moi_dat_chinh_am');
  ok(!!g2 && g2[1].tocDo === -30, 'kéo lần nữa thì gửi lại giá trị mới',
     g2 ? String(g2[1].tocDo) : '(không gọi)');

  // Không đổi gì thì đừng gọi lại — dat() chạy mỗi lần bấm bất cứ thứ gì.
  goiSangPython.length = 0;
  chay("dat({ ...S })");
  await new Promise((r) => setTimeout(r, 0));
  ok(!goiSangPython.some((x) => x[0] === 'moi_dat_chinh_am'),
     'không đổi gì thì KHÔNG gọi lại, tránh dội Python');

  // Đổi không gian âm học: phải gửi sang Python cùng các thông số khác
  goiSangPython.length = 0;
  chay("dat(datChinh(S, 'khongGian', 'podcast'))");
  await new Promise((r) => setTimeout(r, 0));
  const g3 = goiSangPython.find((x) => x[0] === 'moi_dat_chinh_am');
  ok(!!g3 && g3[1].khongGian === 'podcast', 'đổi không gian âm học thì gửi sang Python',
     g3 ? JSON.stringify(g3[1]) : '(không gọi)');

  // Đặt lại mặc định: phải xoá không gian âm học về rỗng
  goiSangPython.length = 0;
  chay("LENH['Đặt lại mặc định']()");
  await new Promise((r) => setTimeout(r, 0));
  const g4 = goiSangPython.find((x) => x[0] === 'moi_dat_chinh_am');
  ok(!!g4 && g4[1].khongGian === '' && g4[1].tocDo === 0 && g4[1].caoDo === 0 && g4[1].amLuong === 100,
     'đặt lại mặc định đưa cả 4 thông số về chuẩn', g4 ? JSON.stringify(g4[1]) : '(không gọi)');

  chay("dat(datChinh(S, 'tocDo', 0))");
}

console.log(`\n${loi === 0 ? 'XANH — khớp hết' : `ĐỎ — ${loi} chỗ lệch`}`);
process.exit(loi ? 1 : 0);
