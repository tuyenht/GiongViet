/* Giọng Việt — Màn hình 5: Từ điển phát âm.

   Dạy máy đọc tên riêng, viết tắt ngành, từ địa phương — để khỏi phải sửa đi
   sửa lại trong từng văn bản.

   Bảng phẳng: chữ trong văn bản -> cách đọc. Đặc tả gốc có thêm cột "Phạm vi"
   (áp cho danh sách công đức hay cho văn bản), nhưng tudien.ini không có chỗ
   chứa thông tin đó và engine áp chung cho cả hai chế độ — dựng cột ấy là bày
   ra một ô chọn không đổi được gì. giaodien/tu_dien.py đã quyết như vậy, giữ
   nguyên. Cột "Lần dùng" cũng bỏ vì không ai đếm được con số đó. */

'use strict';

function veManTuDien(S, D) {
  if (!D) {
    return `<div class="tudien"><div class="giongkho__trong">
      Đang đọc từ điển…</div></div>`;
  }
  const muc = D.muc || [];
  const sua = S.tuDienSua || null;      // { tuCu, tu, doc } khi đang sửa/thêm

  return `<div class="tudien">
    <div class="giongkho__thanh">
      <input id="oTimTuDien" class="giongkho__tim" placeholder="Tìm từ hoặc cách đọc…"
             value="${esc(S.tuDienTim || '')}">
      <button class="nut nut--acc" data-tudienmoi="1">${ic('cong', 13)} Thêm từ</button>
      <span class="soat__phu">${D.hienThi}/${D.tong} mục${
        D.rieng ? ` · ${D.rieng} mục anh tự thêm` : ''}</span>
      <button class="nut" data-lenh="Đóng từ điển">Xong</button>
    </div>

    ${sua ? veKhungSuaTu(sua) : ''}

    <div class="soat__bang">
      <div class="soat__hang soat__hang--dau">
        <span class="tudien__c1">Từ trong văn bản</span>
        <span class="tudien__c2">Đọc thành</span>
        <span class="tudien__c3">Hành động</span>
      </div>
      ${muc.length ? muc.map(veHangTu).join('')
        : `<div class="giongkho__trong">${
            S.tuDienTim ? 'Không tìm thấy mục nào khớp.'
                        : 'Từ điển đang trống. Bấm “Thêm từ” để dạy máy đọc.'}</div>`}
    </div>

    <div class="soat__chan">
      Máy sẽ đọc theo bảng này ở mọi văn bản. Sửa xong nghe lại là thấy ngay.
    </div>
  </div>`;
}

function veHangTu(m) {
  return `<div class="soat__hang">
    <span class="tudien__c1">
      <strong>${esc(m.tu)}</strong>
      ${m.sanCo ? `<span class="tudien__nhan">${m.daSua ? 'đã sửa' : 'có sẵn'}</span>` : ''}
    </span>
    <span class="tudien__c2">${esc(m.doc)}</span>
    <span class="tudien__c3">
      <button class="lienket" data-tudiensua="${esc(m.tu)}" data-tudiendoc="${esc(m.doc)}"
        >Sửa</button>
      <button class="lienket" data-tudienxoa="${esc(m.tu)}">Xoá</button>
    </span>
  </div>`;
}

function veKhungSuaTu(sua) {
  const them = !sua.tuCu;
  return `<div class="tudien__khung">
    <label class="tudien__o">
      <span>Từ trong văn bản</span>
      <input id="oTuMoi" value="${esc(sua.tu || '')}" placeholder="ví dụ: UBND">
    </label>
    <label class="tudien__o tudien__o--rong">
      <span>Đọc thành</span>
      <input id="oDocMoi" value="${esc(sua.doc || '')}"
             placeholder="ví dụ: Uỷ ban nhân dân">
    </label>
    <button class="nut nut--vien" data-tudiennghe="1">${ic('tamgiac', 11)} Nghe thử</button>
    <button class="nut nut--acc" data-tudienluu="1">${them ? 'Thêm' : 'Lưu'}</button>
    <button class="lienket" data-tudienhuy="1">Huỷ</button>
  </div>`;
}

if (typeof module !== 'undefined') {
  module.exports = { veManTuDien, veHangTu, veKhungSuaTu };
}
