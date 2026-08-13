/* Giọng Việt — Màn hình 6: Cài đặt.

   Chỉ bày ra thiết lập engine LÀM ĐƯỢC THẬT. Bản thiết kế gốc vẽ 36 mục
   (ngôn ngữ giao diện, tăng tốc GPU, giới hạn RAM, kênh cập nhật, mã giấy
   phép…) nhưng chương trình chạy ONNX trên CPU, chỉ có tiếng Việt và không có
   hệ thống bản quyền nào — dựng đủ 36 mục là bày ra hơn hai chục cái công tắc
   bấm vào không xảy ra gì. giaodien/cai_dat.py đã quyết vậy, giữ nguyên.

   Màu nền và cỡ chữ do GIAO DIỆN tự giữ (hoso-v2.json), không gửi sang Python:
   hai nơi cùng nhớ một thứ là có ngày chúng lệch nhau. */

'use strict';

const CO_CHU_CHON = [[70, 'Nhỏ'], [85, 'Hơi nhỏ'], [100, 'Vừa'],
                     [120, 'Hơi lớn'], [150, 'Lớn'], [200, 'Rất lớn']];

function veManCaiDat(S, D) {
  if (!D) {
    return `<div class="tudien"><div class="giongkho__trong">
      Đang đọc cài đặt…</div></div>`;
  }
  return `<div class="tudien">
    <div class="giongkho__thanh">
      <span class="soat__nhan">Cài đặt</span>
      <span class="soat__phu">Chỉ những thứ chương trình làm được thật</span>
      <button class="nut" data-lenh="Đóng cài đặt">Xong</button>
    </div>
    <div class="caidat">
      ${veNhomGiaoDien(S)}
      ${(D.nhom || []).map(veNhomCaiDat).join('')}
      ${vePhimTat(D.phimTat || [])}
    </div>
  </div>`;
}

/* Nhóm này KHÔNG lấy từ Python: màu nền và cỡ chữ là chuyện của giao diện. */
function veNhomGiaoDien(S) {
  return `<div class="caidat__nhom">
    <div class="caidat__ten">Chung</div>
    <div class="caidat__mota">Màu nền và cỡ chữ</div>
    <div class="caidat__muc">
      <div class="caidat__nhan">Màu nền
        <span class="caidat__goiy">Nền sáng dễ đọc ban ngày, nền tối đỡ chói buổi tối.</span>
      </div>
      <div class="caidat__dieu">
        <button class="soat__chip${S.theme !== 'toi' ? ' mo' : ''}" data-cdtheme="sang">Sáng</button>
        <button class="soat__chip${S.theme === 'toi' ? ' mo' : ''}" data-cdtheme="toi">Tối</button>
      </div>
    </div>
    <div class="caidat__muc">
      <div class="caidat__nhan">Cỡ chữ vùng văn bản
        <span class="caidat__goiy">Chỉ đổi cỡ chữ của văn bản đang đọc.</span>
      </div>
      <div class="caidat__dieu">
        ${CO_CHU_CHON.map(([v, n]) => `
          <button class="soat__chip${(S.zoom || 100) === v ? ' mo' : ''}"
                  data-cdzoom="${v}">${n} · ${v}%</button>`).join('')}
      </div>
    </div>
  </div>`;
}

function veNhomCaiDat(n) {
  return `<div class="caidat__nhom">
    <div class="caidat__ten">${esc(n.nhan)}</div>
    ${n.moTa ? `<div class="caidat__mota">${esc(n.moTa)}</div>` : ''}
    ${(n.muc || []).map(veMucCaiDat).join('')}
  </div>`;
}

function veMucCaiDat(m) {
  const nhan = `<div class="caidat__nhan">${esc(m.nhan)}
    ${m.goiY ? `<span class="caidat__goiy">${esc(m.goiY)}</span>` : ''}</div>`;

  if (m.kieu === 'congtac') {
    return `<div class="caidat__muc">${nhan}
      <div class="caidat__dieu">
        <button class="soat__chip${m.bat ? ' mo' : ''}" data-cdcongtac="${esc(m.khoa)}"
                data-cdbat="${m.bat ? '0' : '1'}"
          >${m.bat ? '✓ Đang bật' : '× Đang tắt'}</button>
      </div></div>`;
  }
  if (m.kieu === 'duongdan') {
    // Chỉ thư mục xuất mới đổi được; tệp danh sách thuộc chế độ công đức mà
    // bản mới chưa có, nên hiện dạng chữ chứ không bày nút.
    const doiDuoc = m.khoa === 'thu_muc_xuat';
    return `<div class="caidat__muc">${nhan}
      <div class="caidat__dieu">
        <span class="caidat__gt">${esc(m.giaTri || '')}</span>
        ${doiDuoc ? '<button class="nut nut--vien" data-cdthumuc="1">Đổi…</button>' : ''}
      </div></div>`;
  }
  return `<div class="caidat__muc">${nhan}
    <div class="caidat__dieu"><span class="caidat__gt">${esc(m.giaTri || '')}</span></div>
  </div>`;
}

/* Phím tắt chỉ để XEM — đổi được phím tắt là một tính năng khác hẳn, chưa có.
   Bày ô cho bấm vào rồi không đổi được thì thà in ra cho đọc. */
function vePhimTat(ds) {
  if (!ds.length) return '';
  return `<div class="caidat__nhom">
    <div class="caidat__ten">Phím tắt</div>
    <div class="caidat__mota">Chỉ để xem, chưa đổi được</div>
    ${ds.map((p) => `<div class="caidat__muc">
      <div class="caidat__nhan">${esc(p.nhan)}</div>
      <div class="caidat__dieu"><kbd>${esc(p.phim)}</kbd></div>
    </div>`).join('')}
  </div>`;
}

if (typeof module !== 'undefined') {
  module.exports = { veManCaiDat, veMucCaiDat, CO_CHU_CHON };
}
