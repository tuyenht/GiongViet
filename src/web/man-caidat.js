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
      ${veNhomDichThuat(S, D)}
      ${veNhomBoNhoCache(S, D)}
      ${(D.nhom || []).map(veNhomCaiDat).join('')}
      ${vePhimTat(D.phimTat || [])}
    </div>
  </div>`;
}

function veNhomBoNhoCache(S, D) {
  const cacheInfo = S.cacheInfo || { dungLuongMB: 0, soTep: 0, gioiHanMB: 150 };
  const thongBaoCache = S.thongBaoCache || '';

  return `<div class="caidat__nhom">
    <div class="caidat__ten">Bộ nhớ đệm âm thanh (Cache)</div>
    <div class="caidat__mota">Lưu tạm âm thanh đã tổng hợp để nghe lại tức thì, không tốn thời gian và tài nguyên CPU</div>
    
    <div class="caidat__muc">
      <div class="caidat__nhan">Dung lượng bộ nhớ đệm
        <span class="caidat__goiy">Tự động áp dụng mã băm đa chiều (Ngôn ngữ + Giọng + Giới tính + Phong cách + Bộ lọc + Nội dung). Tự động dọn dẹp sau 7 ngày hoặc khi vượt ngưỡng 150 MB.</span>
      </div>
      <div class="caidat__dieu" style="display:flex;align-items:center;gap:10px">
        <span class="caidat__gt" style="font-weight:600">${cacheInfo.dungLuongMB} MB / ${cacheInfo.gioiHanMB} MB (${cacheInfo.soTep} mẩu)</span>
        <button class="nut nut--vien" id="btnXoaCacheDia" style="padding:5px 12px;font-size:12.5px;color:var(--txt)">🗑 Dọn sạch bộ nhớ đệm</button>
      </div>
    </div>
    ${thongBaoCache ? `<div style="font-size:12px;color:var(--acc);font-weight:600;padding:2px 14px 8px 14px">${esc(thongBaoCache)}</div>` : ''}
  </div>`;
}

function veNhomDichThuat(S, D) {
  const cfg = (D && D.cauHinh) || {};
  const dongCo = cfg.dong_co_dich || 'neural';
  const testStatus = S.testApiStatus || {};

  return `<div class="caidat__nhom">
    <div class="caidat__ten">Dịch thuật & Lồng tiếng 28 Ngôn ngữ</div>
    <div class="caidat__mota">Chọn công cụ dịch tự động & giọng đọc bản xứ Neural chuẩn quốc tế</div>
    
    <div class="caidat__muc">
      <div class="caidat__nhan">Ưu tiên sử dụng động cơ
        <span class="caidat__goiy">Chọn công cụ xử lý dịch khi chuyển sang đọc tiếng nước ngoài.</span>
      </div>
      <div class="caidat__dieu">
        <button class="soat__chip${dongCo === 'neural' ? ' mo' : ''}" data-cddongco="neural" title="Dịch siêu tốc 0.1s, miễn phí 0đ, không cần cấu hình tài khoản">⚡ Neural Siêu Tốc (0đ)</button>
        <button class="soat__chip${dongCo === 'gemini' ? ' mo' : ''}" data-cddongco="gemini" title="Dịch thông minh qua Google Gemini 1.5 Flash (Có gói miễn phí 15 RPM)">🌟 Google Gemini AI</button>
        <button class="soat__chip${dongCo === 'openai' ? ' mo' : ''}" data-cddongco="openai" title="Dịch văn học chuyên sâu qua OpenAI GPT-4o-mini">💎 OpenAI GPT-4o</button>
      </div>
    </div>

    ${dongCo === 'neural' ? `
      <div class="caidat__muc" style="background:var(--sub-h);padding:10px 14px;border-radius:6px;border:1px solid var(--stroke2)">
        <div class="caidat__nhan" style="color:var(--txt)">Trạng thái: Hoạt động tức thì (Miễn phí 100%)
          <span class="caidat__goiy">Đã tích hợp sẵn trong ứng dụng. Tốc độ 0.1s/câu, không cần cài đặt API Key hay đăng ký tài khoản.</span>
        </div>
        <div class="caidat__dieu">
          <span class="soat__chip mo" style="cursor:default">✅ Đang kích hoạt (0đ)</span>
        </div>
      </div>
    ` : ''}

    ${dongCo === 'gemini' ? `
      <div class="caidat__muc" style="background:var(--acc-soft);padding:12px 14px;border-radius:6px;border:1px solid var(--acc);flex-direction:column;align-items:stretch;gap:10px">
        <div style="display:flex;justify-content:space-between;align-items:flex-start">
          <div class="caidat__nhan" style="color:var(--txt);font-weight:700">Google Gemini API Key (Miễn phí 15 lượt/phút)
            <div class="caidat__goiy" style="margin-top:2px">
              <b>Cách lấy Key miễn phí:</b> Bấm link bên dưới đăng nhập Google → Bấm <i>Create API key</i> → Sao chép và dán vào ô bên dưới.
            </div>
            <button class="lienket" data-molink="https://aistudio.google.com/app/apikey" style="display:inline-flex;align-items:center;gap:4px;color:var(--acc);font-weight:700;margin-top:6px;font-size:12.5px;cursor:pointer">
              🔗 Bấm để mở trang lấy Key miễn phí tại Google AI Studio ↗
            </button>
          </div>
        </div>
        <div style="display:flex;align-items:center;gap:8px;margin-top:4px">
          <input id="cdGeminiKey" type="password" placeholder="Dán mã API Key (bắt đầu bằng AIzaSy...)" value="${esc(cfg.gemini_api_key || '')}" style="flex:1;height:30px;padding:0 10px;border:1px solid var(--stroke2);border-radius:4px;background:var(--layer);color:var(--txt);font-size:12.5px">
          <button class="nut nut--acc" id="luuKeyGemini" style="font-size:12.5px;padding:5px 14px;white-space:nowrap">Kiểm tra & Lưu</button>
        </div>
        ${testStatus.gemini ? `<div style="font-size:12px;color:${testStatus.gemini.ok ? 'var(--acc)' : '#ff4d4f'};font-weight:600;padding-left:2px">${esc(testStatus.gemini.msg)}</div>` : ''}
      </div>
    ` : ''}

    ${dongCo === 'openai' ? `
      <div class="caidat__muc" style="background:var(--acc-soft);padding:12px 14px;border-radius:6px;border:1px solid var(--acc);flex-direction:column;align-items:stretch;gap:10px">
        <div style="display:flex;justify-content:space-between;align-items:flex-start">
          <div class="caidat__nhan" style="color:var(--txt);font-weight:700">OpenAI API Key (Tài khoản riêng)
            <div class="caidat__goiy" style="margin-top:2px">
              <b>Cách lấy Key:</b> Đăng nhập tài khoản OpenAI → Bấm <i>Create new secret key</i> → Dán vào ô bên dưới.
            </div>
            <button class="lienket" data-molink="https://platform.openai.com/api-keys" style="display:inline-flex;align-items:center;gap:4px;color:var(--acc);font-weight:700;margin-top:6px;font-size:12.5px;cursor:pointer">
              🔗 Bấm để mở trang quản lý Key tại OpenAI Platform ↗
            </button>
          </div>
        </div>
        <div style="display:flex;align-items:center;gap:8px;margin-top:4px">
          <input id="cdOpenAIKey" type="password" placeholder="Dán mã API Key (bắt đầu bằng sk-...)" value="${esc(cfg.openai_api_key || '')}" style="flex:1;height:30px;padding:0 10px;border:1px solid var(--stroke2);border-radius:4px;background:var(--layer);color:var(--txt);font-size:12.5px">
          <button class="nut nut--acc" id="luuKeyOpenAI" style="font-size:12.5px;padding:5px 14px;white-space:nowrap">Kiểm tra & Lưu</button>
        </div>
        ${testStatus.openai ? `<div style="font-size:12px;color:${testStatus.openai.ok ? 'var(--acc)' : '#ff4d4f'};font-weight:600;padding-left:2px">${esc(testStatus.openai.msg)}</div>` : ''}
      </div>
    ` : ''}
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
