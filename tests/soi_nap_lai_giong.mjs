/* Chạy giao-dien.js THẬT trong DOM giả để đo hệ quả của L5.

   Bê nguyên cách dựng ngữ cảnh của kiem/kiem-giao-dien.mjs — cùng thứ tự nạp
   tệp như index.html khai, nên cảnh mà bài này gặp là cảnh cửa sổ thật gặp.
   Không mở loa, không gọi Python: coPython() trả false vì không có
   window.pywebview, api() trả null.

   Chạy:  node soi_l5.mjs <đường dẫn thư mục ui-moi>
*/

import { readFileSync } from 'fs';
import { createContext, runInContext } from 'vm';
import { join } from 'path';

const UI = process.argv[2];
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
  window: { addEventListener() {} },
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

/* `const` cấp cao nhất trong vm nằm ở phạm vi từ vựng của ngữ cảnh, không
   thành thuộc tính của object — phải chạy biểu thức TRONG ngữ cảnh mới với tới
   được S, dat(), GIONG… */
const chay = (ma) => runInContext(ma, ctx, { filename: 'soi' });

const lay = (re) => { const m = re.exec(HTML); return m === null ? null : m[1]; };
const oGiongCotPhai = () => lay(/<span class="chon__gt">([\s\S]*?)<\/span>/);
const tieuDeOGiong = () => lay(/<button class="chon"\s+id="oGiong"\s+title="([\s\S]*?)">/);
const giongHoSoDangDung = () => {
  const ds = [...HTML.matchAll(/<span class="hoso__giong">([\s\S]*?)<\/span>/g)]
    .map((m) => m[1]);
  return ds[chay('S.profile')];
};

const MA_MOI = 'giong-bac-tuan-moi';   // mã giọng vừa nhân bản, chưa có trong GIONG

const ra = {};

chay('ve()');
ra.truoc = {
  oGiong: oGiongCotPhai(),
  tieuDe: tieuDeOGiong(),
  cotTrai: giongHoSoDangDung(),
  soGiong: chay('GIONG.length'),
  maHoSo: chay('hoSoDangDung(S).giong'),
};

/* Đúng đường mà nút "Dùng giọng này" trong Thư viện giọng đi qua:
   giao-dien.js:1492  dat(datGiong(S, n.dataset.giong)); */
chay(`dat(datGiong(S, ${JSON.stringify(MA_MOI)}))`);
ra.sau = {
  oGiong: oGiongCotPhai(),
  tieuDe: tieuDeOGiong(),
  cotTrai: giongHoSoDangDung(),
  timThay: chay(`String(GIONG.find((g) => g.ma === ${JSON.stringify(MA_MOI)}))`),
  maHoSo: chay('hoSoDangDung(S).giong'),
};

/* Gói tin Python ĐẨY THẬT sau khi nhân bản xong:
   cau_noi.py:128  _day({voices, voiceId, thuVien})   (trong _nap_giong)
   cau_noi.py:846  _day({thuVien: ...})
   Đưa nguyên hình dạng ấy vào window.gd.push xem giao diện có nhặt không. */
const goiVoices = [{ id: MA_MOI, ten: 'Giọng bác Tuấn mới', rieng: true }];
const goiThuVien = { cuaToi: [{ id: MA_MOI, ten: 'Giọng bác Tuấn mới' }], coSan: [] };
chay(`window.gd.push({voices: ${JSON.stringify(goiVoices)}, `
   + `voiceId: ${JSON.stringify(MA_MOI)}, thuVien: ${JSON.stringify(goiThuVien)}})`);
chay(`window.gd.push({thuVien: ${JSON.stringify(goiThuVien)}})`);
ra.sauPush = {
  soGiong: chay('GIONG.length'),
  soDropdown: chay('GIONG_TRONG_DROPDOWN.length'),
  timThay: chay(`String(GIONG.find((g) => g.ma === ${JSON.stringify(MA_MOI)}))`),
};

/* Rồi Python gọi window.gd.giongXong(ten) — cau_noi.py:847. */
chay('window.gd.giongXong("Giọng bác Tuấn mới")');
chay('ve()');
ra.sauGiongXong = {
  soGiong: chay('GIONG.length'),
  timThay: chay(`String(GIONG.find((g) => g.ma === ${JSON.stringify(MA_MOI)}))`),
  oGiong: oGiongCotPhai(),
  cotTrai: giongHoSoDangDung(),
};

/* Đối chứng: gọi datGiongThat với đúng gói mà moi_danh_sach_giong trả về thì
   danh sách CÓ nhận giọng mới — chứng minh hàm không hỏng, chỉ là không ai gọi. */
const goiDanhSach = {
  giong: [{ ma: MA_MOI, ten: 'Giọng bác Tuấn mới', rieng: true, gioi: 'Nam', vung: '' }],
};
chay(`datGiongThat(${JSON.stringify(goiDanhSach)})`);
chay('ve()');
ra.doiChung = {
  soGiong: chay('GIONG.length'),
  timThay: chay(`String((GIONG.find((g) => g.ma === ${JSON.stringify(MA_MOI)}) || {}).ten)`),
  oGiong: oGiongCotPhai(),
};

process.stdout.write(JSON.stringify(ra));
