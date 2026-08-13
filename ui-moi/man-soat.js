/* Giọng Việt — Màn hình 2: Soát văn bản.

   Là một chế độ PHỦ LÊN màn chính: cột trái và cột phải vẫn thấy nhưng mờ đi,
   phần giữa thay bằng nội dung màn này. Không phải một trang riêng — người
   lớn tuổi mà bị nhảy sang màn hoàn toàn khác thì mất phương hướng, không biết
   đường quay lại.

   Hai tab:
     1. Chỗ cần chú ý          — những chỗ máy sẽ đọc sai
     2. Văn bản sau chuẩn hoá  — gốc so với chuỗi engine THẬT sẽ đọc

   Số liệu do Python tính (giaodien_moi/soat_moi.py), ở đây chỉ dựng hình. */

'use strict';

/* Ba chip lọc ở tab 1. `muc` khớp với giaodien/soat.py: 'nang' là lỗi nên sửa
   trước khi xuất, 'nhe' là cảnh báo. */
const LOC_SOAT = [
  { ma: 'tatca', ten: 'Tất cả', cham: '' },
  { ma: 'nang', ten: 'Lỗi', cham: 'err' },
  { ma: 'nhe', ten: 'Cảnh báo', cham: 'warn' },
];

const TEN_LOAI_SOAT = {
  viettat: 'Viết tắt chưa dạy',
  kytu: 'Ký tự lạ',
  tien: 'Số tiền không hiểu',
  trung: 'Tên trùng',
};

/* Hành động ứng với từng loại. Chỉ để đúng những nút LÀM ĐƯỢC THẬT:
   · viettat  → Thêm vào từ điển (màn 5 chưa xong nên tạm mở hộp nhập nhanh)
   · còn lại  → chỉ có "Tới đoạn", vì máy không tự quyết thay người dùng được
   Đặc tả gốc có thêm Sửa / Tách / Đổi; cố tình chưa bày ra — bày nút bấm
   không làm gì là đúng thứ KPI dự án cấm. */
const HANH_DONG_SOAT = { viettat: 'Thêm vào từ điển' };

function veManSoat(S, D) {
  if (!D) {
    return `<div class="soat"><div class="soat__trong">
      Chưa soát được. Hãy mở một tệp hoặc dán văn bản trước.</div></div>`;
  }
  const tab = S.soatTab === 'chuanhoa' ? 'chuanhoa' : 'chuy';
  const cy = D.chuY || {};
  const ch = D.chuanHoa || {};
  const phu = tab === 'chuy'
    ? (cy.trong ? 'Chưa có văn bản để soát'
                : `${(cy.nang || 0) + (cy.nhe || 0)} chỗ cần chú ý · ${esc(cy.moTa || '')}`)
    : esc(ch.tomTat || '');

  return `<div class="soat">
    <div class="soat__thanh">
      <button class="soat__tab${tab === 'chuy' ? ' mo' : ''}" data-soattab="chuy">
        Chỗ cần chú ý</button>
      <button class="soat__tab${tab === 'chuanhoa' ? ' mo' : ''}" data-soattab="chuanhoa">
        Văn bản sau chuẩn hoá</button>
      <span class="soat__phu">${phu}</span>
      <button class="nut" data-lenh="Đóng soát">Xong</button>
    </div>
    ${tab === 'chuy' ? veSoatChuY(S, cy) : veSoatChuanHoa(S, D)}
  </div>`;
}

// ---------------------------------------------------------------- tab 1

function veSoatChuY(S, cy) {
  if (cy.trong) {
    return `<div class="soat__trong">Chưa có văn bản nào để soát.<br>
      Hãy bấm <strong>Dán văn bản</strong> hoặc <strong>Mở tệp</strong> trước.</div>`;
  }
  const ds = cy.vanDe || [];
  if (!ds.length) {
    return `<div class="soat__trong soat__trong--vui">
      Không tìm thấy chỗ nào đáng lo. Văn bản này máy đọc được bình thường.</div>`;
  }

  const loc = S.soatLoc || 'tatca';
  const hien = ds.filter((v) => loc === 'tatca' || v.muc === loc);
  const dem = { tatca: ds.length, nang: cy.nang || 0, nhe: cy.nhe || 0 };

  return `
    <div class="soat__dau">
      <span class="soat__nhan">Kết quả soát</span>
      ${LOC_SOAT.map((c) => `
        <button class="soat__chip${loc === c.ma ? ' mo' : ''}" data-soatloc="${c.ma}">
          ${c.cham ? `<span class="cham cham--${c.cham}"></span>` : ''}
          ${c.ten} (${dem[c.ma]})
        </button>`).join('')}
    </div>
    <div class="soat__bang">
      <div class="soat__hang soat__hang--dau">
        <span class="soat__c1">Đoạn</span>
        <span class="soat__c2">Loại</span>
        <span class="soat__c3">Nội dung cảnh báo</span>
        <span class="soat__c4">Đề xuất</span>
        <span class="soat__c5">Hành động</span>
      </div>
      ${hien.map((v) => veHangSoat(S, v)).join('')
        || '<div class="soat__trong">Không có mục nào ở nhóm này.</div>'}
    </div>`;
}

function veHangSoat(S, v) {
  const chon = v.doan === S.sel ? ' chon' : '';
  const hd = HANH_DONG_SOAT[v.loai];
  return `<div class="soat__hang${chon}" data-soatdoan="${v.doan}">
    <span class="soat__c1">${v.doan || '—'}</span>
    <span class="soat__c2">
      <span class="cham cham--${v.muc === 'nang' ? 'err' : 'warn'}"></span>
      ${esc(TEN_LOAI_SOAT[v.loai] || v.loai)}</span>
    <span class="soat__c3">${esc(v.tieuDe || '')}</span>
    <span class="soat__c4">${esc(v.chiTiet || '')}</span>
    <span class="soat__c5">
      ${hd ? `<button class="nut nut--vien" data-soatthem="${esc(v.tu || '')}"
              >${hd}</button>` : ''}
      <button class="lienket" data-soatdi="${v.doan}">Tới đoạn</button>
    </span>
  </div>`;
}

// ---------------------------------------------------------------- tab 2

function veSoatChuanHoa(S, D) {
  const ch = D.chuanHoa || {};
  const ds = ch.dong || [];
  if (!ds.length) {
    return '<div class="soat__trong">Chưa có văn bản nào để so sánh.</div>';
  }
  return `
    <div class="soat__dau">
      <span class="soat__nhan">Quy tắc đang bật</span>
      ${(D.quyTac || []).map(veChipQuyTac).join('')}
    </div>
    <div class="soat__bang soat__bang--doi">
      <div class="soat__hang soat__hang--dau">
        <span class="soat__d1">Đoạn</span>
        <span class="soat__d2">Văn bản gốc</span>
        <span class="soat__d3">Máy sẽ đọc thành</span>
      </div>
      ${ds.map((d) => `
        <div class="soat__hang${d.doan === S.sel ? ' chon' : ''}" data-soatdoan="${d.doan}">
          <span class="soat__d1">${d.doan}</span>
          <span class="soat__d2">${esc(d.goc)}</span>
          <span class="soat__d3${d.doi ? '' : ' mo-nhat'}">${
            d.doi ? `<mark>${esc(d.doc)}</mark>` : esc(d.doc || d.goc)}</span>
        </div>`).join('')}
    </div>
    <div class="soat__chan">
      Chuẩn hoá chỉ ảnh hưởng đến âm thanh, văn bản gốc của bạn không thay đổi.
    </div>`;
}

/* Chip quy tắc: bấm được KHI VÀ CHỈ KHI có công tắc thật bên cấu hình.
   `doiDuoc` do Python quyết (soat_moi.QUY_TAC) — engine chuẩn hoá ngày tháng
   và dấu câu lặp không qua công tắc nào, nên hai cái đó chỉ hiện con số. */
function veChipQuyTac(q) {
  if (!q.doiDuoc) {
    return `<span class="soat__chip soat__chip--tinh"
             title="Quy tắc này luôn bật, không tắt được">${esc(q.ten)} ${q.so}</span>`;
  }
  return `<button class="soat__chip${q.bat ? ' mo' : ''}" data-quytac="${esc(q.khoa)}"
           data-quytacbat="${q.bat ? '0' : '1'}"
           title="${q.bat ? 'Đang bật — bấm để tắt' : 'Đang tắt — bấm để bật'}"
          >${q.bat ? '✓' : '×'} ${esc(q.ten)} ${q.so}</button>`;
}

if (typeof module !== 'undefined') {
  module.exports = { veManSoat, LOC_SOAT, TEN_LOAI_SOAT, HANH_DONG_SOAT };
}
