/* Giọng Việt — Màn hình 4: Thư viện giọng.

   Xem, tìm, lọc, nghe thử và chọn giọng cho hồ sơ đang dùng.

   Sóng âm trên thẻ giọng riêng là sóng THẬT, đọc từ chính tệp mẫu người dùng
   đã thu (giaodien/thu_vien_giong.py). Giọng dựng sẵn nằm trong mô hình nên
   không có tệp mẫu — thẻ của chúng để trống chỗ đó, cố ý không vẽ hình bịa.

   CHƯA CÓ nút Nhân bản giọng mới và Xoá giọng: hai việc đó ghi vào thư mục
   giong_rieng/ của người dùng, mà đường ghi ấy đang bị giaodien_moi/
   khoa_du_lieu.py bịt lại. Bày nút ra rồi bấm không được là đúng thứ KPI dự
   án cấm, nên thà chưa có còn hơn. */

'use strict';

const LOC_GIONG = [
  { ma: 'tatca', ten: 'Tất cả giọng' },
  { ma: 'cosan', ten: 'Giọng có sẵn' },
  { ma: 'cuatoi', ten: 'Giọng của tôi' },
];

const LOC_GIOI = ['Tất cả', 'Nữ', 'Nam'];

function veManGiong(S, D) {
  if (!D) {
    return `<div class="giongkho"><div class="giongkho__trong">
      Đang đọc danh sách giọng…</div></div>`;
  }
  const cuaToi = D.cuaToi || [];
  const coSan = D.coSan || [];
  const loc = S.giongLoc || 'tatca';
  const gioi = S.giongGioi || 'Tất cả';
  const tim = (S.giongTim || '').trim().toLowerCase();

  const hop = (g) => {
    if (gioi !== 'Tất cả' && !(g.moTa || '').includes(gioi)) return false;
    if (!tim) return true;
    return `${g.ten} ${g.moTa} ${g.phu}`.toLowerCase().includes(tim);
  };
  const nhomCuaToi = loc === 'cosan' ? [] : cuaToi.filter(hop);
  const nhomCoSan = loc === 'cuatoi' ? [] : coSan.filter(hop);
  const tong = cuaToi.length + coSan.length;

  return `<div class="giongkho">
    <div class="giongkho__thanh">
      ${LOC_GIONG.map((c) => `
        <button class="soat__chip${loc === c.ma ? ' mo' : ''}" data-giongloc="${c.ma}">
          ${c.ten} ${c.ma === 'tatca' ? tong : c.ma === 'cosan' ? coSan.length : cuaToi.length}
        </button>`).join('')}
      <input id="oTimGiong" class="giongkho__tim" placeholder="Tìm theo tên, vùng miền…"
             value="${esc(S.giongTim || '')}">
      ${LOC_GIOI.map((g) => `
        <button class="soat__chip${gioi === g ? ' mo' : ''}" data-gionggioi="${g}"
        >${g === 'Tất cả' ? 'Giới tính: Tất cả' : g}</button>`).join('')}
      <span class="soat__phu">${tong} giọng · ${cuaToi.length} giọng của tôi</span>
      <button class="nut" data-lenh="Đóng giọng">Xong</button>
    </div>

    <div class="giongkho__than">
      ${loc !== 'cosan' ? `<div class="giongkho__nhan">Giọng của tôi</div>
        <div class="giongkho__luoi">${nhomCuaToi.map((g) => veTheGiong(g)).join('')}
          ${veTheNhanBan(S)}</div>` : ''}
      ${nhomCoSan.length ? `<div class="giongkho__nhan">Giọng có sẵn</div>
        <div class="giongkho__luoi">${nhomCoSan.map((g) => veTheGiong(g)).join('')}</div>` : ''}
      ${!nhomCuaToi.length && !nhomCoSan.length
        ? '<div class="giongkho__trong">Không tìm thấy giọng nào khớp.</div>' : ''}
    </div>

    <div class="giongkho__chan">
      <span>${esc(D.boNho || '')}</span>
    </div>
  </div>`;
}

function veTheGiong(g) {
  const dangNghe = g.dangNgheThu;
  return `<div class="the-giong${g.dangDung ? ' dung' : ''}">
    <div class="the-giong__dau">
      <span class="the-giong__tron${g.rieng ? ' rieng' : ''}">${ic('micro', 17)}</span>
      <span class="the-giong__ten">${esc(g.ten)}</span>
      ${g.dangDung ? '<span class="the-giong__nhan">Đang dùng</span>' : ''}
    </div>
    <div class="the-giong__phu">${esc([g.moTa, g.phu].filter(Boolean).join(' · '))}</div>
    ${veSongAm(g)}
    <div class="the-giong__nut">
      <button class="nut nut--vien${dangNghe ? ' nut--dang' : ''}"
              data-nghegiong="${esc(g.id)}"
        >${ic(dangNghe ? 'dunghan' : 'tamgiac', 11)} ${dangNghe ? 'Dừng' : 'Nghe thử'}</button>
      ${g.dangDung
        ? '<span class="the-giong__dangdung">Đang dùng</span>'
        : `<button class="nut nut--acc" data-giong="${esc(g.id)}">Dùng giọng này</button>`}
      ${g.rieng ? `<button class="lienket the-giong__xoa"
                     data-xoagiong="${esc(g.id)}" data-xoaten="${esc(g.ten)}"
                     title="Xoá giọng này khỏi máy">Xoá</button>` : ''}
    </div>
  </div>`;
}

/* Ô nét đứt cuối nhóm "Giọng của tôi" — chỗ bắt đầu nhân bản giọng mới.
   Lúc đang nhân bản thì chính ô này báo tiến độ: việc chạy vài phút, không
   nói gì là người dùng tưởng máy treo và bấm lại lần nữa. */
function veTheNhanBan(S) {
  if (S.dangNhanBan) {
    return `<div class="the-giong the-giong--moi dang">
      <span class="cham cham--acc"></span>
      <div class="the-giong__ten">Đang nhân bản giọng…</div>
      <div class="the-giong__phu">${esc(S.tienDoGiong || 'Đang chuẩn bị…')}</div>
      <div class="the-giong__phu">Việc này mất vài phút. Cứ để máy chạy.</div>
    </div>`;
  }
  return `<button class="the-giong the-giong--moi" data-nhanbangiong="1">
    ${ic('cong', 26)}
    <div class="the-giong__ten">Nhân bản giọng mới</div>
    <div class="the-giong__phu">Cần một tệp thu âm khoảng 30 giây</div>
  </button>`;
}

/* Sóng âm: chỉ vẽ khi ĐỌC ĐƯỢC tệp mẫu thật. Giọng dựng sẵn không có tệp mẫu
   nên chỗ này để trống — vẽ một dải sóng bịa ra thì nhìn thẻ nào cũng như thẻ
   nào, và người dùng mất luôn cách nhận ra mẫu thu của mình bị rè hay im. */
function veSongAm(g) {
  if (!g.song || !g.song.length) return '<div class="the-giong__song"></div>';
  return `<div class="the-giong__song">${g.song.map((v) => `
    <i style="height:${Math.max(6, Math.round(v * 28))}px"></i>`).join('')}</div>`;
}

if (typeof module !== 'undefined') {
  module.exports = { veManGiong, veTheGiong, LOC_GIONG, LOC_GIOI };
}
