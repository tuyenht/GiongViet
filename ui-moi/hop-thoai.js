/* Giọng Việt — hộp thoại và thông báo góc.

   Chỉ dựng HTML từ dữ liệu, không giữ trạng thái, không bắt sự kiện. Nơi gọi
   (giao-dien.js) lo phần gắn nút. Tách ra đây để lớp vẽ màn chính khỏi phình.

   Kích thước lấy từ README mục "Hộp thoại xuất file". */

'use strict';

const DINH_DANG = [
  ['wav24', 'WAV 24 bit'], ['wav16', 'WAV 16 bit'],
  ['mp3-320', 'MP3 320 kbps'], ['mp3-128', 'MP3 128 kbps'],
];

/* Ba lựa chọn tách tệp. Dòng ước tính đổi theo lựa chọn — chữ lấy nguyên văn
   từ README mục "Màn hình 3 — Giai đoạn 1". */
const CACH_TACH = [
  { ma: 'mot', nhan: 'Một tệp duy nhất', goiY: '11,6 MB',
    uoc: 'Ước tính: 1 tệp · 11,6 MB · khoảng 27 giây xử lý' },
  { ma: 'moi-doan', nhan: 'Mỗi đoạn một tệp', goiY: '{soDoan} tệp',
    uoc: 'Ước tính: {soDoan} tệp · tổng 11,9 MB · khoảng 34 giây xử lý' },
  { ma: 'do-dai', nhan: 'Cắt theo độ dài', goiY: 'mỗi 10 phút một tệp',
    uoc: 'Ước tính: 1 tệp · 11,6 MB · chưa tới 10 phút nên không cắt' },
];

/** Hộp thoại xuất, giai đoạn 1 — thiết lập.
    Ba giai đoạn đầy đủ thuộc màn hình 3; màn chính chỉ dựng giai đoạn này. */
function veHopXuat(d) {
  const e = (s) => String(s == null ? '' : s)
    .replace(/&/g, '&amp;').replace(/</g, '&lt;').replace(/>/g, '&gt;').replace(/"/g, '&quot;');
  const uoc = (CACH_TACH.find((x) => x.ma === d.tach) || CACH_TACH[0]).uoc
    .replace('{soDoan}', d.soDoan);

  return `<div class="man" id="manXuat"><div class="hop">
    <div class="hop__dau">
      <div class="hop__ten">Xuất file âm thanh</div>
      <div class="hop__phu">${e(d.tenTep)} · ${d.soDoan} đoạn · ${e(d.tenGiong)}</div>
    </div>
    <div class="hop__than">
      <div class="xuat__hang">
        <div style="flex:1;min-width:0">
          <div class="the__nhan" style="margin-bottom:6px">Tên tệp</div>
          <div class="xuat__oten">
            <input class="onhap" id="xTen" value="${e(d.ten)}" spellcheck="false"
                   style="flex:1;min-width:0">
            <span class="c-goiy" id="xDuoi">${e(d.duoi)}</span>
          </div>
        </div>
        <div style="width:170px;flex:none">
          <div class="the__nhan" style="margin-bottom:6px">Định dạng</div>
          <select class="chon" id="xDinhDang" style="width:100%">
            ${DINH_DANG.map(([m, n]) =>
              `<option value="${m}"${m === d.dinhDang ? ' selected' : ''}>${n}</option>`).join('')}
          </select>
        </div>
      </div>

      <div style="margin-top:14px">
        <div class="the__nhan" style="margin-bottom:6px">Lưu vào</div>
        <div class="xuat__oten">
          <span class="onhap xuat__duong" id="xThuMuc" title="${e(d.thuMuc)}">${e(d.thuMuc)}</span>
          <button class="nut nut--vien" id="xChon">Chọn…</button>
        </div>
      </div>

      <div style="margin-top:14px">
        <div class="the__nhan" style="margin-bottom:6px">Tách tệp</div>
        ${CACH_TACH.map((t) => `
          <button class="tron${t.ma === d.tach ? ' da-chon' : ''}" data-tach="${t.ma}">
            <span class="tron__vong"></span>
            <span class="tron__nhan">${t.nhan}</span>
            <span class="tron__goiy">${t.goiY.replace('{soDoan}', d.soDoan)}</span>
          </button>`).join('')}
      </div>
    </div>
    <div class="hop__chan">
      <span class="c-goiy" style="flex:1" id="xUoc">${e(uoc)}</span>
      <button class="nut nut--vien" id="xHuy">Huỷ</button>
      <button class="nut nut--acc" id="xBatDau">Bắt đầu xuất</button>
    </div>
  </div></div>`;
}

/* Giai đoạn 2 và 3 bám theo BẢN MẪU designs/GiongDoc - Xuất file âm thanh,
   không theo mục "Hộp thoại xuất file" của README — hai chỗ đó nói khác nhau
   và chủ dự án đã chốt lấy bản mẫu. Ba chỗ bản mẫu khác README:
     · hộp hẹp lại còn 520px (giai đoạn 1 vẫn 600px)
     · giai đoạn 2 có HAI nút: Chạy nền và Huỷ xuất — README chỉ nói Huỷ
     · giai đoạn 3 chỉ hai nút Mở thư mục / Đóng — README kể ba

   Nút "Chạy nền" chính là chỗ hai mục README gặp nhau: bấm nó thì hộp đóng,
   phần trăm chạy tiếp ở thanh trạng thái, xong thì hiện thông báo góc — đúng
   luồng mục màn hình 1 tả. Mặc định vẫn giữ hộp, vì đó là chỗ duy nhất có
   nút Huỷ. */

const _e = (s) => String(s == null ? '' : s)
  .replace(/&/g, '&amp;').replace(/</g, '&lt;').replace(/>/g, '&gt;').replace(/"/g, '&quot;');

/** Một dòng "nhãn ... giá trị" của bảng số liệu. */
const _dong = (nhan, giaTri) =>
  `<div class="xuat2__dong"><span>${_e(nhan)}</span><b>${_e(giaTri)}</b></div>`;

/** Hộp thoại xuất, giai đoạn 2 — đang xuất. */
function veHopDangXuat(d) {
  const pt = Math.max(0, Math.min(100, Number(d.phanTram) || 0));
  return `<div class="man" id="manXuat2"><div class="hop hop--hep">
    <div class="xuat2">
      <div class="xuat2__dau">
        <span class="quay"></span>
        <span class="xuat2__ten">Đang xuất ${_e(d.ten)}</span>
      </div>
      <div class="xuat2__rai"><i style="width:${pt}%"></i></div>
      <div class="xuat2__dong xuat2__dong--nhe">
        <span>${_e(d.moTa || 'Đang chuẩn bị…')}</span><span>${pt}%</span>
      </div>
      <div class="xuat2__bang">
        ${_dong('Đã trôi qua', d.troiQua || '00:00')}
        ${_dong('Còn lại (ước tính)', d.conLai || '—')}
        ${_dong('Đã ghi', d.daGhi || '0 KB')}
      </div>
      <div class="xuat2__nhac">Có thể tiếp tục soạn thảo trong lúc xuất. Không tắt máy.</div>
    </div>
    <div class="hop__chan hop__chan--doi">
      <button class="nut nut--vien nut--rong" id="xChayNen">Chạy nền</button>
      <button class="nut nut--vien nut--rong" id="xHuyXuat">Huỷ xuất</button>
    </div>
  </div></div>`;
}

/** Hộp thoại xuất, giai đoạn 3 — xong. */
function veHopXuatXong(d) {
  return `<div class="man" id="manXuat3"><div class="hop hop--hep">
    <div class="xuat2">
      <div class="xuat2__dau">
        <span class="xuat3__tich">
          <svg width="14" height="14" viewBox="0 0 24 24" stroke="currentColor"
               stroke-width="3" fill="none" stroke-linecap="round" stroke-linejoin="round">
            <path d="M5 12.5l4.5 4.5L19 7"/></svg>
        </span>
        <span class="xuat2__ten">Đã xuất xong</span>
      </div>
      <div class="xuat3__the">
        <div class="xuat3__tep">${_e(d.ten)}</div>
        <div class="xuat3__so">
          ${_dong('Thời lượng', d.thoiLuong)}
          ${_dong('Kích thước', d.kichThuoc)}
          ${_dong('Thời gian xử lý', d.xuLy)}
        </div>
      </div>
      <div class="xuat3__duong">${_e(d.duongDan)}</div>
    </div>
    <div class="hop__chan hop__chan--doi">
      <button class="nut nut--acc nut--rong" id="xMoThuMuc">Mở thư mục</button>
      <button class="nut nut--vien nut--rong" id="xDongXong">Đóng</button>
    </div>
  </div></div>`;
}

/** Hộp thoại chỉ để đọc: Hướng dẫn nhanh · Danh sách phím tắt · Giới thiệu.

    Ba mục Trợ giúp trước đây bấm vào chỉ đóng menu rồi thôi. Dùng chung một
    khung thay vì ba hộp riêng: nội dung khác nhau, hình dáng thì không. */
function veHopTin(d) {
  const dong = (d.dong || []).map((x) => Array.isArray(x)
    ? `<div class="tin__cap"><span>${_e(x[0])}</span><b>${_e(x[1])}</b></div>`
    : `<div class="tin__doan">${_e(x)}</div>`).join('');
  return `<div class="man" id="manTin"><div class="hop hop--hep">
    <div class="hop__dau"><div class="hop__ten">${_e(d.ten)}</div></div>
    <div class="hop__than tin">${dong}</div>
    <div class="hop__chan">
      <span style="flex:1"></span>
      <button class="nut nut--acc" id="tinDong">Đóng</button>
    </div>
  </div></div>`;
}

/** Thông báo góc dưới phải sau khi xuất xong. */
function veBaoXuatXong(d) {
  const e = (s) => String(s == null ? '' : s)
    .replace(/&/g, '&amp;').replace(/</g, '&lt;').replace(/>/g, '&gt;');
  return `<div class="bao" id="baoXuat">
    <div class="bao__ten">Đã xuất xong tệp âm thanh</div>
    <div class="bao__noi">${e(d.ten)} · ${e(d.thoiLuong)} · ${e(d.dungLuong)}<br>
      Lưu tại: ${e(d.thuMuc)}</div>
    <div class="bao__nut">
      <button class="nut nut--vien" id="bMoThuMuc">Mở thư mục</button>
      <button class="nut" id="bDong">Đóng</button>
    </div>
  </div>`;
}

if (typeof module !== 'undefined') {
  module.exports = {
    DINH_DANG, CACH_TACH, veHopXuat, veHopDangXuat, veHopXuatXong, veBaoXuatXong,
    veHopTin,
  };
}
