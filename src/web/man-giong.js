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
  { ma: 'dangu', ten: '🌐 Đa ngôn ngữ' },
];

const LOC_GIOI = ['Tất cả', 'Nữ', 'Nam'];

const DS_LOC_NGON_NGU = [
  // Nhóm 1: Bản Địa & Đông Nam Á (ASEAN)
  { ma: 'vi', ten: 'Tiếng Việt (Gốc)', co: '🇻🇳', nhom: 'Đông Nam Á', alias: ['vn', 'vietnam', 'viet'] },
  { ma: 'th', ten: 'Tiếng Thái (ภาษาไทย)', co: '🇹🇭', nhom: 'Đông Nam Á', alias: ['th', 'thailand', 'thai'] },
  { ma: 'id', ten: 'Tiếng Indonesia (Bahasa)', co: '🇮🇩', nhom: 'Đông Nam Á', alias: ['id', 'indonesia', 'indo'] },
  { ma: 'ms', ten: 'Tiếng Malaysia (Melayu)', co: '🇲🇾', nhom: 'Đông Nam Á', alias: ['ms', 'my', 'malaysia', 'malay'] },
  { ma: 'fil', ten: 'Tiếng Philippines (Tagalog)', co: '🇵🇭', nhom: 'Đông Nam Á', alias: ['ph', 'philippines', 'filipino', 'tagalog'] },
  { ma: 'km', ten: 'Tiếng Campuchia (Khmer)', co: '🇰🇭', nhom: 'Đông Nam Á', alias: ['kh', 'campuchia', 'cambodia', 'khmer'] },
  { ma: 'lo', ten: 'Tiếng Lào (Lao)', co: '🇱🇦', nhom: 'Đông Nam Á', alias: ['la', 'laos', 'lao'] },
  { ma: 'my', ten: 'Tiếng Myanmar (Burmese)', co: '🇲🇲', nhom: 'Đông Nam Á', alias: ['mm', 'myanmar', 'burma', 'burmese'] },

  // Nhóm 2: Đông Á
  { ma: 'zh', ten: 'Tiếng Trung (Phổ thông)', co: '🇨🇳', nhom: 'Đông Á', alias: ['cn', 'china', 'trung', 'chinese', 'mandarin'] },
  { ma: 'yue', ten: 'Tiếng Trung (Quảng Đông)', co: '🇭🇰', nhom: 'Đông Á', alias: ['hk', 'hongkong', 'cantonese', 'quangdong'] },
  { ma: 'zh-tw', ten: 'Tiếng Trung (Đài Loan)', co: '🇹🇼', nhom: 'Đông Á', alias: ['tw', 'taiwan', 'dailoan'] },
  { ma: 'ja', ten: 'Tiếng Nhật (日本語)', co: '🇯🇵', nhom: 'Đông Á', alias: ['jp', 'japan', 'nhat', 'japanese'] },
  { ma: 'ko', ten: 'Tiếng Hàn (한국어)', co: '🇰🇷', nhom: 'Đông Á', alias: ['kr', 'korea', 'han', 'korean'] },

  // Nhóm 3: Âu - Mỹ & Toàn Cầu
  { ma: 'en', ten: 'Tiếng Anh (Mỹ - US)', co: '🇺🇸', nhom: 'Âu - Mỹ & Toàn Cầu', alias: ['us', 'usa', 'america', 'anh', 'english'] },
  { ma: 'en-gb', ten: 'Tiếng Anh (Anh - UK)', co: '🇬🇧', nhom: 'Âu - Mỹ & Toàn Cầu', alias: ['uk', 'greatbritain', 'england', 'anh'] },
  { ma: 'fr', ten: 'Tiếng Pháp (Français)', co: '🇫🇷', nhom: 'Âu - Mỹ & Toàn Cầu', alias: ['fr', 'france', 'phap', 'french'] },
  { ma: 'de', ten: 'Tiếng Đức (Deutsch)', co: '🇩🇪', nhom: 'Âu - Mỹ & Toàn Cầu', alias: ['de', 'germany', 'duc', 'german'] },
  { ma: 'es', ten: 'Tiếng Tây Ban Nha (Español)', co: '🇪🇸', nhom: 'Âu - Mỹ & Toàn Cầu', alias: ['es', 'spain', 'taybannha', 'spanish'] },
  { ma: 'pt', ten: 'Tiếng Bồ Đào Nha (Português)', co: '🇵🇹', nhom: 'Âu - Mỹ & Toàn Cầu', alias: ['pt', 'br', 'portugal', 'brazil', 'bodaonha', 'portuguese'] },
  { ma: 'it', ten: 'Tiếng Ý (Italiano)', co: '🇮🇹', nhom: 'Âu - Mỹ & Toàn Cầu', alias: ['it', 'italy', 'y', 'italian'] },
  { ma: 'ru', ten: 'Tiếng Nga (Русский)', co: '🇷🇺', nhom: 'Âu - Mỹ & Toàn Cầu', alias: ['ru', 'russia', 'nga', 'russian'] },
  { ma: 'nl', ten: 'Tiếng Hà Lan (Nederlands)', co: '🇳🇱', nhom: 'Âu - Mỹ & Toàn Cầu', alias: ['nl', 'netherlands', 'dutch', 'halan'] },

  // Nhóm 4: Nam Á & Trung Đông
  { ma: 'ar', ten: 'Tiếng Ả Rập (العربية)', co: '🇸🇦', nhom: 'Nam Á & Trung Đông', alias: ['sa', 'arab', 'arabic', 'arap'] },
  { ma: 'hi', ten: 'Tiếng Hindi (हिन्दी)', co: '🇮🇳', nhom: 'Nam Á & Trung Đông', alias: ['in', 'india', 'hindi', 'ando'] },
  { ma: 'bn', ten: 'Tiếng Bengal (বাংলা)', co: '🇧🇩', nhom: 'Nam Á & Trung Đông', alias: ['bd', 'bangladesh', 'bengali', 'bengal'] },
  { ma: 'ur', ten: 'Tiếng Urdu (اردو)', co: '🇵🇰', nhom: 'Nam Á & Trung Đông', alias: ['pk', 'pakistan', 'urdu'] },
  { ma: 'ta', ten: 'Tiếng Tamil (தமிழ்)', co: '🇮🇳', nhom: 'Nam Á & Trung Đông', alias: ['tamil'] },
  { ma: 'mr', ten: 'Tiếng Marathi (मराठी)', co: '🇮🇳', nhom: 'Nam Á & Trung Đông', alias: ['marathi'] },
  { ma: 'tr', ten: 'Tiếng Thổ Nhĩ Kỳ (Türkçe)', co: '🇹🇷', nhom: 'Nam Á & Trung Đông', alias: ['tr', 'turkey', 'turkish', 'thonhiky'] },
];

const laNam = (g) => {
  if (/\(nam\)/i.test(g.ten)) return true;
  const moTa = (g.moTa || '').replace(/miền\s+nam/gi, '');
  return /\bnam\b/i.test(moTa);
};

const laNu = (g) => {
  if (/\(nữ\)/i.test(g.ten)) return true;
  return /\bnữ\b/i.test(g.moTa || '');
};

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
  const timLang = (S.timLang || '').trim().toLowerCase();
  const dsNgonNguLoc = S.giongNgonNgu || [];
  const soDaNgu = cuaToi.concat(coSan).filter((g) => g.daNgonNgu).length;

  const hop = (g) => {
    if (loc === 'dangu' && !g.daNgonNgu) return false;
    if (gioi === 'Nam' && !laNam(g)) return false;
    if (gioi === 'Nữ' && !laNu(g)) return false;
    if (dsNgonNguLoc.length > 0) {
      if (!g.daNgonNgu && !dsNgonNguLoc.includes(g.ngonNgu || 'vi')) return false;
    }
    if (!tim) return true;
    return `${g.ten} ${g.moTa} ${g.phu}`.toLowerCase().includes(tim);
  };
  const nhomCuaToi = loc === 'cosan' ? [] : cuaToi.filter(hop);
  const nhomCoSan = loc === 'cuatoi' ? [] : coSan.filter(hop);
  const tong = cuaToi.length + coSan.length;

  const nhanNgonNgu = dsNgonNguLoc.length === 0
    ? 'Ngôn ngữ: Tất cả'
    : `Ngôn ngữ: ${dsNgonNguLoc.map((m) => (DS_LOC_NGON_NGU.find((x) => x.ma === m) || {}).co || m).join('')} (${dsNgonNguLoc.length})`;

  const normSearch = (s) => (s || '').toLowerCase().normalize('NFD').replace(/[\u0300-\u036f]/g, '').replace(/đ/g, 'd').trim();
  const timLangNorm = normSearch(timLang);

  const dsLangHienThi = DS_LOC_NGON_NGU.filter((l) => {
    if (!timLangNorm) return true;
    const maMatch = l.ma.toLowerCase().includes(timLangNorm);
    const tenMatch = normSearch(l.ten).includes(timLangNorm);
    const aliasMatch = (l.alias || []).some(a => normSearch(a).includes(timLangNorm));
    return maMatch || tenMatch || aliasMatch;
  });

  return `<div class="giongkho">
    <div class="giongkho__thanh">
      ${LOC_GIONG.map((c) => `
        <button class="soat__chip${loc === c.ma ? ' mo' : ''}" data-giongloc="${c.ma}">
          ${c.ten} ${c.ma === 'tatca' ? tong : c.ma === 'cosan' ? coSan.length : c.ma === 'dangu' ? soDaNgu : cuaToi.length}
        </button>`).join('')}

      <div style="position:relative;display:inline-block">
        <button class="soat__chip${dsNgonNguLoc.length > 0 ? ' mo' : ''}" id="nutLocNgonNgu" data-molocngonngu="1">
          ${nhanNgonNgu} ▾
        </button>
        ${S.moDropdownNgonNgu ? `
          <div class="giongkho__menu-ngonngu" style="position:absolute;top:calc(100% + 4px);left:0;z-index:99;background:var(--layer);border:1px solid var(--stroke2);border-radius:8px;padding:8px 0 4px;width:260px;box-shadow:0 8px 24px rgba(0,0,0,.15);max-height:360px;display:flex;flex-direction:column">
            <div style="padding:4px 12px 6px;font-size:11.5px;font-weight:700;color:var(--txt3);text-transform:uppercase;letter-spacing:.03em;display:flex;justify-content:space-between;align-items:center;border-bottom:1px solid var(--stroke);flex:none">
              <span>Lọc ngôn ngữ (28)</span>
              ${dsNgonNguLoc.length > 0 ? `<button class="lienket" id="xoaLocNgonNgu" style="font-size:11px">Bỏ chọn hết</button>` : ''}
            </div>
            <div style="padding:6px 10px;border-bottom:1px solid var(--stroke);flex:none">
              <input id="oTimLang" placeholder="🔍 Tìm ngôn ngữ…" value="${esc(S.timLang || '')}" style="width:100%;height:26px;font-size:12px;padding:0 8px;border:1px solid var(--stroke2);border-radius:4px;background:var(--sub-h);color:var(--txt)">
            </div>
            <div style="flex:1;min-height:0;overflow-y:auto;padding:4px 0" id="dsLangItems">
              ${dsLangHienThi.length === 0 ? '<div style="padding:12px;font-size:12px;color:var(--txt3);text-align:center">Không tìm thấy ngôn ngữ</div>' : ''}
              ${dsLangHienThi.map((l) => {
                const checked = dsNgonNguLoc.includes(l.ma);
                return `
                  <label style="display:flex;align-items:center;gap:8px;padding:6px 12px;font-size:12.5px;color:var(--txt);cursor:pointer;user-select:none" class="giongkho__item-ngonngu">
                    <input type="checkbox" data-loclang="${l.ma}" ${checked ? 'checked' : ''} style="accent-color:var(--acc);cursor:pointer;width:15px;height:15px">
                    <span>${l.co}</span>
                    <span style="flex:1;min-width:0;overflow:hidden;text-overflow:ellipsis;white-space:nowrap">${l.ten}</span>
                  </label>
                `;
              }).join('')}
            </div>
          </div>
        ` : ''}
      </div>

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
        <div class="giongkho__luoi">${nhomCuaToi.map((g) => veTheGiong(g, S)).join('')}
          ${veTheNhanBan(S)}</div>` : ''}
      ${nhomCoSan.length && loc !== 'cuatoi' ? `<div class="giongkho__nhan">Giọng có sẵn</div>
        <div class="giongkho__luoi">${nhomCoSan.map((g) => veTheGiong(g, S)).join('')}</div>` : ''}
      ${!nhomCuaToi.length && !nhomCoSan.length
        ? '<div class="giongkho__trong">Không tìm thấy giọng nào khớp.</div>' : ''}
    </div>

    <div class="giongkho__chan">
      <span>${esc(D.boNho || '')}</span>
    </div>
  </div>`;
}

function veTheGiong(g, S) {
  const dangNghe = g.dangNgheThu;
  const daNgu = !!g.daNgonNgu;
  const langCode = g.ngonNgu || 'vi';
  const langObj = DS_LOC_NGON_NGU.find((x) => x.ma === langCode) || { co: '🇻🇳', ten: 'Tiếng Việt' };
  const moMenu = S && S.moMenuLangGiongId === g.id;

  return `<div class="the-giong${g.dangDung ? ' dung' : ''}" style="position:relative">
    <div class="the-giong__dau">
      <span class="the-giong__tron${g.rieng ? ' rieng' : ''}">${ic('micro', 17)}</span>
      <span class="the-giong__ten" title="${esc(g.ten)}">${esc(g.ten)}</span>
      <button class="the-giong__dangu-btn${daNgu ? ' bat' : ''}" data-toggledangu="${esc(g.id)}" title="Bấm để chọn ngôn ngữ hoặc bật/tắt chế độ Đa ngôn ngữ">
        ${daNgu ? '🌐 Đa ngữ ▾' : `${langObj.co} ${langObj.ten.split(' ')[0]} ▾`}
      </button>
      ${g.dangDung ? '<span class="the-giong__nhan">Đang dùng</span>' : ''}
      ${g.rieng ? `<button class="the-giong__xoa-top" data-xoagiong="${esc(g.id)}" data-xoaten="${esc(g.ten)}" title="Xoá giọng này khỏi máy">
        <svg width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><polyline points="3 6 5 6 21 6"></polyline><path d="M19 6v14a2 2 0 0 1-2 2H7a2 2 0 0 1-2-2V6m3 0V4a2 2 0 0 1 2-2h4a2 2 0 0 1 2 2v2"></path></svg>
        <span>Xoá</span>
      </button>` : ''}
    </div>

    ${moMenu ? `
      <div class="the-giong__menu-lang" style="position:absolute;top:40px;left:30px;right:10px;z-index:99;background:var(--card-bg,#fff);border:1px solid var(--stroke);border-radius:8px;box-shadow:0 8px 24px rgba(0,0,0,.18);max-height:240px;overflow-y:auto;padding:6px">
        <div style="font-size:11px;font-weight:700;color:var(--txt3);padding:4px 8px;text-transform:uppercase">Chọn ngôn ngữ phát âm</div>
        <button class="giongkho__item-ngonngu${daNgu ? ' da-chon' : ''}" data-chonlanggiong="${esc(g.id)}" data-langcode="all" style="width:100%;text-align:left;display:flex;align-items:center;gap:6px;padding:6px 8px;font-size:12.5px;border-radius:4px;border:none;background:${daNgu ? 'var(--acc-soft)' : 'transparent'};cursor:pointer">
          <span style="font-size:14px">🌐</span>
          <span style="font-weight:600;flex:1">Đa ngôn ngữ (Toàn cầu)</span>
          ${daNgu ? '<span style="color:var(--acc);font-weight:bold">✓</span>' : ''}
        </button>
        <div style="height:1px;background:var(--divider);margin:4px 0"></div>
        ${DS_LOC_NGON_NGU.map((l) => `
          <button class="giongkho__item-ngonngu${!daNgu && langCode === l.ma ? ' da-chon' : ''}" data-chonlanggiong="${esc(g.id)}" data-langcode="${l.ma}" style="width:100%;text-align:left;display:flex;align-items:center;gap:6px;padding:5px 8px;font-size:12px;border-radius:4px;border:none;background:${!daNgu && langCode === l.ma ? 'var(--acc-soft)' : 'transparent'};cursor:pointer">
            <span>${l.co}</span>
            <span style="flex:1">${l.ten}</span>
            ${!daNgu && langCode === l.ma ? '<span style="color:var(--acc);font-weight:bold">✓</span>' : ''}
          </button>
        `).join('')}
      </div>
    ` : ''}

    <div class="the-giong__phu">${esc([g.moTa, g.phu].filter(Boolean).join(' · '))}</div>
    ${veSongAm(g)}
    <div class="the-giong__nut">
      <button class="nut nut--vien${dangNghe ? ' nut--dang' : ''}"
              data-nghegiong="${esc(g.id)}"
        >${ic(dangNghe ? 'dunghan' : 'tamgiac', 11)} ${dangNghe ? 'Dừng' : 'Nghe thử'}</button>
      ${g.dangDung
        ? '<span class="the-giong__dangdung">Đang dùng</span>'
        : `<button class="nut nut--acc" data-giong="${esc(g.id)}">Dùng giọng này</button>`}
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

if (typeof window !== 'undefined') {
  window.DS_LOC_NGON_NGU = DS_LOC_NGON_NGU;
}

if (typeof module !== 'undefined') {
  module.exports = { veManGiong, veTheGiong, LOC_GIONG, LOC_GIOI, DS_LOC_NGON_NGU };
}

