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
  const dangDich = d.ngonNgu && d.ngonNgu !== 'vi';

  return `<div class="man" id="manXuat"><div class="hop">
    <div class="hop__dau">
      <div class="hop__ten">Xuất file âm thanh</div>
      <div class="hop__phu">${e(d.tenTep)} · ${d.soDoan} đoạn · ${e(d.tenGiong)} ${dangDich ? `· <span class="vanbanghep__badge" style="font-size:10.5px;padding:1px 5px;background:rgba(0,103,192,.1);color:var(--acc);border-radius:3px">🌐 Lồng tiếng ${e(d.ngonNgu.toUpperCase())}</span>` : ''}</div>
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
      ${(d.nut || []).length
        ? d.nut.map((b) => `<button class="nut${b.chinh ? ' nut--acc' : ''}"
             id="tin_${_e(b.ma)}">${_e(b.nhan)}</button>`).join('')
        : '<button class="nut nut--acc" id="tinDong">Đóng</button>'}
    </div>
  </div></div>`;
}

/** Thông báo góc dưới phải sau khi xuất xong. */
function veBaoXuatXong(d) {
  const e = (s) => String(s == null ? '' : s)
    .replace(/&/g, '&amp;').replace(/</g, '&lt;').replace(/>/g, '&gt;');
  // Khung này dùng cho HAI việc: báo xuất xong, và thông báo ngắn bất kỳ.
  // Nên tiêu đề phải theo dữ liệu, đừng đóng cứng — đóng cứng thì bấm Huỷ
  // xuất xong cũng hiện ra dòng "Đã xuất xong tệp âm thanh".
  const nhe = !d.thoiLuong && !d.dungLuong;
  return `<div class="bao" id="baoXuat">
    <div class="bao__ten">${e(d.tieuDe || 'Đã xuất xong tệp âm thanh')}</div>
    <div class="bao__noi">${nhe ? e(d.ten)
      : `${e(d.ten)} · ${e(d.thoiLuong)} · ${e(d.dungLuong)}<br>Lưu tại: ${e(d.thuMuc)}`}</div>
    <div class="bao__nut">
      ${nhe ? '' : '<button class="nut nut--vien" id="bMoThuMuc">Mở thư mục</button>'}
      <button class="nut" id="bDong">Đóng</button>
    </div>
  </div>`;
}

/** Hộp thoại mở tài liệu từ Google Docs (khớp 100% Claude Design). */
function veHopGoogleDocs(d) {
  const e = (s) => String(s == null ? '' : s)
    .replace(/&/g, '&amp;').replace(/</g, '&lt;').replace(/>/g, '&gt;').replace(/"/g, '&quot;');
  
  return `<div class="man" id="manGdoc"><div class="hop" style="width:540px">
    <div class="hop__dau" style="display:flex;align-items:flex-start;justify-content:space-between">
      <div style="flex:1;min-width:0;padding-right:12px">
        <div class="hop__ten">Mở tài liệu Google Docs</div>
        <div class="hop__phu">Tải trực tiếp văn bản từ Google Docs vào vùng đọc</div>
      </div>
      <button class="nut nut--icon" id="gdocDong" title="Đóng" style="font-size:20px;line-height:1;width:32px;height:32px;display:flex;align-items:center;justify-content:center;color:var(--txt3);border-radius:6px;flex:none;cursor:pointer">×</button>
    </div>
    <div class="hop__than" style="padding:20px 22px">
      <div style="display:flex;align-items:center;gap:12px;margin-bottom:16px">
        <span style="width:40px;height:40px;border-radius:20px;background:var(--acc-soft);color:var(--acc);display:flex;align-items:center;justify-content:center;flex:none">
          <svg width="20" height="20" viewBox="0 0 24 24" stroke="currentColor" stroke-width="1.6" fill="none" stroke-linecap="round" stroke-linejoin="round"><path d="M14 3v5h5"/><path d="M14 3H7a2 2 0 00-2 2v14a2 2 0 002 2h10a2 2 0 002-2V8z"/><path d="M9 13h6M9 17h4"/></svg>
        </span>
        <div style="font-size:13px;line-height:1.5;color:var(--txt2)">
          Nhập đường link tài liệu Google Docs công khai (chế độ <b>"Bất kỳ ai có đường link đều xem được"</b>).
        </div>
      </div>
      <div style="margin-bottom:8px">
        <div class="the__nhan" style="margin-bottom:6px">Đường link Google Docs</div>
        <input class="onhap" id="gdocUrl" style="width:100%" placeholder="https://docs.google.com/document/d/.../edit" value="${e(d && d.url ? d.url : '')}" autofocus spellcheck="false">
      </div>
      <div style="font-size:12px;color:var(--txt3);line-height:1.4">
        Ví dụ: https://docs.google.com/document/d/1BxiMVs0XRA5nFMdKvBdBZjgmUUqptlbs74OgvE2upms/edit
      </div>
    </div>
    <div class="hop__chan" style="justify-content:flex-end;gap:8px">
      <button class="nut nut--vien" id="gdocHuy">Huỷ</button>
      <button class="nut nut--acc" id="gdocTai">Mở tài liệu</button>
    </div>
  </div></div>`;
}

/** Hộp thoại Dạy máy phát âm (chuẩn AdminKit thay thế window.prompt). */
function veHopDayTu(d) {
  const e = (s) => String(s == null ? '' : s)
    .replace(/&/g, '&amp;').replace(/</g, '&lt;').replace(/>/g, '&gt;').replace(/"/g, '&quot;');
  const tu = e(d.tu || '');
  const goiY = d.goiY || [];

  return `<div class="man" id="manDayTu"><div class="hop" style="width:480px">
    <div class="hop__dau" style="display:flex;align-items:flex-start;justify-content:space-between">
      <div style="flex:1;min-width:0;padding-right:12px">
        <div class="hop__ten">Dạy máy phát âm</div>
        <div class="hop__phu">Thêm cách đọc chính xác cho từ viết tắt vào Từ điển phát âm</div>
      </div>
      <button class="nut nut--icon" id="dayTuDong" title="Đóng" style="font-size:20px;line-height:1;width:32px;height:32px;display:flex;align-items:center;justify-content:center;color:var(--txt3);border-radius:6px;flex:none;cursor:pointer">×</button>
    </div>
    <div class="hop__than" style="padding:18px 22px">
      <div style="display:flex;align-items:center;gap:10px;margin-bottom:14px">
        <span style="font-size:13px;color:var(--txt3)">Từ viết tắt cần dạy:</span>
        <span class="vanbanghep__badge" style="font-size:15px;font-weight:700;letter-spacing:.02em;padding:4px 10px;background:var(--acc-soft);color:var(--acc);border-radius:5px">${tu}</span>
      </div>

      ${goiY && goiY.length ? `
        <div style="margin-bottom:14px">
          <div class="the__nhan" style="margin-bottom:6px;font-size:11.5px">Gợi ý cách đọc phổ biến (bấm để chọn nhanh):</div>
          <div style="display:flex;flex-wrap:wrap;gap:6px">
            ${goiY.map(g => `<button class="nut nut--vien soat__chip-goiy" data-goiy="${e(g)}" style="font-size:12.5px;padding:4px 9px;height:auto">${e(g)}</button>`).join('')}
          </div>
        </div>
      ` : ''}

      <div style="margin-bottom:6px">
        <div class="the__nhan" style="margin-bottom:6px">Máy nên đọc thành</div>
        <input class="onhap" id="dayTuDoc" style="width:100%;font-size:14.5px;padding:8px 12px" placeholder="Ví dụ: Uỷ ban nhân dân" value="${e(d.doc || '')}" autofocus spellcheck="false">
      </div>
      <div style="font-size:12px;color:var(--txt3);line-height:1.45;margin-top:8px">
        Sau khi lưu, động cơ AI sẽ tự động đọc từ “<b>${tu}</b>” theo đúng phiên âm trên ở mọi tài liệu.
      </div>
    </div>
    <div class="hop__chan" style="justify-content:flex-end;gap:8px">
      <button class="nut nut--vien" id="dayTuHuy">Huỷ</button>
      <button class="nut nut--acc" id="dayTuLuu" data-tu="${tu}">Lưu vào từ điển</button>
    </div>
  </div></div>`;
}

const THE_LOAI_GIONG_MAU = [
  {
    ma: 'kiemhiep',
    ten: 'Truyện kiếm hiệp / Dã sử',
    icon: '⚔️',
    phongCach: 'Hào sảng, kịch tính, hùng hồn',
    cacDoanMau: [
      'Đêm đen như mực, gió rít từng cơn qua khe núi hiểm trở. Hắn nắm chặt thanh trường kiếm trong tay, ánh mắt lạnh như băng nhìn về phía chân trời xa xăm, nơi trận quyết chiến sinh tử sắp sửa bắt đầu.',
      'Dưới ánh trăng mờ ảo, bóng hình đại hiệp lướt qua ngọn trúc như cơn gió thoảng. Một tiếng kiếm vang lên xé toạc màn đêm tĩnh mịch, định đoạt số phận của cả giang hồ võ lâm.',
    ],
    goiYTen: 'Giọng Kiếm Hiệp'
  },
  {
    ma: 'reviewphim',
    ten: 'Review phim / Recap kịch bản',
    icon: '🍿',
    phongCach: 'Lôi cuốn, nhịp nhanh, cuốn hút',
    cacDoanMau: [
      'Một vụ trộm thế kỷ tưởng chừng hoàn hảo, nhưng kẻ chủ mưu lại không ngờ rằng mình đã bị gài bẫy từ đầu. Liệu hắn có thể lật ngược ván cờ nguy hiểm này hay không? Hãy cùng theo dõi ngay sau đây.',
      'Người đàn ông này vừa bước ra khỏi cánh cửa bí mật thì bỗng nhận ra toàn bộ thành phố đã bị phong tỏa. Thời gian chỉ còn đúng năm phút để anh ta tìm ra lối thoát duy nhất.',
    ],
    goiYTen: 'Giọng Review Phim'
  },
  {
    ma: 'kechuyen',
    ten: 'Kể chuyện radio / Sách nói',
    icon: '☕',
    phongCach: 'Thủ thỉ, sâu lắng, ấm áp',
    cacDoanMau: [
      'Có những ngày bình yên đến lạ, khi ta ngồi một mình bên tách trà ấm, lắng nghe tiếng mưa rơi nhẹ ngoài hiên và nhớ về những kỷ niệm đã xa, thấy lòng mình thanh thản và nhẹ nhõm vô cùng.',
      'Mỗi chuyến đi đều để lại trong tim ta những dấu ấn khó phai. Đôi khi điều làm ta nhớ nhất không phải là phong cảnh rực rỡ, mà là sự chân thành của những con người ta từng gặp gỡ.',
    ],
    goiYTen: 'Giọng Kể Chuyện'
  },
  {
    ma: 'tintuc',
    ten: 'Tin tức thời sự / Bản tin',
    icon: '📢',
    phongCach: 'Chuẩn xác, rõ ràng, dứt khoát',
    cacDoanMau: [
      'Bản tin sáng nay xin chuyển đến quý vị những diễn biến kinh tế và xã hội đáng chú ý. Các chuyên gia dự báo thị trường sẽ có những bước phục hồi tích cực trong những tháng cuối năm.',
      'Trung tâm dự báo khí tượng thủy văn cho biết các tỉnh miền Trung chuẩn bị đón đợt không khí lạnh tăng cường, nhiệt độ giảm sâu kèm theo mưa rải rác trên diện rộng.',
    ],
    goiYTen: 'Giọng Tin Tức'
  },
  {
    ma: 'quangcao',
    ten: 'Quảng cáo / TikTok / Reels',
    icon: '🛍️',
    phongCach: 'Năng động, tươi sáng, tự tin',
    cacDoanMau: [
      'Chiếc tai nghe chống ồn thế hệ mới với thiết kế siêu gọn nhẹ và thời lượng pin lên đến ba mươi giờ liên tục. Đây chắc chắn là sự lựa chọn hoàn hảo nhất dành cho bạn trong tầm giá dưới một triệu đồng.',
      'Khám phá ngay bộ sưu tập thời trang mùa hè với phong cách trẻ trung, chất liệu thoáng mát cực đỉnh. Đặt hàng ngay hôm nay để nhận ưu đãi giảm giá lên tới năm mươi phần trăm!',
    ],
    goiYTen: 'Giọng Quảng Cáo'
  },
  {
    ma: 'congduc',
    ten: 'Hành chính / Đọc công đức',
    icon: '🏛️',
    phongCach: 'Trang nghiêm, mẫu mực, vang sáng',
    cacDoanMau: [
      'Hôm nay, ngày lành tháng tốt, toàn thể gia đình tín chủ thành tâm dâng nén tâm hương, kính lễ mười phương chư Phật, chư Thánh linh thiêng, phù hộ độ trì quốc thái dân an, gia đạo hưng long, vạn sự cát tường như ý.',
      'Ban tổ chức xin chân thành tri ân công đức của toàn thể quý phật tử và các nhà hảo tâm đã phát tâm công đức xây dựng, tôn tạo cảnh quan di tích lịch sử ngày một khang trang, tố hảo.',
    ],
    goiYTen: 'Giọng Trang Nghiêm'
  },
  {
    ma: 'giaoduc',
    ten: 'Giáo dục / Bài giảng / Khóa học',
    icon: '📚',
    phongCach: 'Truyền cảm, từ tốn, dễ hiểu',
    cacDoanMau: [
      'Đường mũi của bạn chứa chất nhầy có khả năng bẫy vi rút, ngăn chúng xâm nhập vào phổi, giống như giáo dục giúp chặn đứng những thông tin sai lệch trước khi chúng lọt vào tâm trí bạn.',
      'Trong bài học ngày hôm nay, chúng ta sẽ cùng nhau tìm hiểu về các nguyên lý cơ bản của tư duy logic và cách áp dụng phương pháp này vào việc giải quyết những bài toán phức tạp trong thực tế.',
    ],
    goiYTen: 'Giọng Giáo Dục'
  },
  {
    ma: 'canhan',
    ten: 'Giọng cá nhân tự nhiên (Đa năng)',
    icon: '🎙️',
    phongCach: 'Tự nhiên, giao tiếp hàng ngày',
    cacDoanMau: [
      'Xin chào các bạn, đây là mẫu giọng nói tự nhiên của tôi. Tôi sử dụng công nghệ nhân bản giọng nói để hỗ trợ đọc tài liệu, thông báo, tin tức và sáng tạo nội dung một cách nhanh chóng, thuận tiện nhất.',
      'Hôm nay thời tiết thật đẹp để bắt đầu những dự định mới. Cảm ơn các bạn đã lắng nghe và đồng hành cùng tôi trong suốt chặng đường vừa qua.',
    ],
    goiYTen: 'Giọng Cá Nhân'
  }
];

/** Hộp thoại Wizard Nhân bản giọng nói 3 bước. */
function veHopNhanBanGiong(d) {
  const e = (s) => String(s == null ? '' : s)
    .replace(/&/g, '&amp;').replace(/</g, '&lt;').replace(/>/g, '&gt;').replace(/"/g, '&quot;');
  
  const buoc = d.buoc || 1;
  const theLoaiChon = THE_LOAI_GIONG_MAU.find(t => t.ma === d.theLoai) || THE_LOAI_GIONG_MAU[0];
  const dsMau = theLoaiChon.cacDoanMau || [theLoaiChon.doanMau || ''];
  const idxMau = d.idxMau || 0;
  const doanMauHienTai = dsMau[idxMau % dsMau.length] || dsMau[0];
  const tenGiong = d.tenGiong != null ? d.tenGiong : (theLoaiChon ? theLoaiChon.goiYTen : 'Giọng mới');
  const fileDaChon = d.fileDaChon || '';

  return `<div class="man" id="manNhanBan"><div class="hop" style="width:680px;max-width:95vw">
    <div class="hop__dau" style="display:flex;align-items:flex-start;justify-content:space-between">
      <div style="flex:1;min-width:0;padding-right:12px">
        <div class="hop__ten">Nhân bản giọng nói AI (Voice Cloning)</div>
        <div class="hop__phu">Quy trình 3 bước chuẩn hóa để tạo giọng đọc tự nhiên, chuẩn phong cách</div>
      </div>
      <button class="nut nut--icon" id="nbDong" title="Đóng" style="font-size:20px;line-height:1;width:32px;height:32px;display:flex;align-items:center;justify-content:center;color:var(--txt3);border-radius:6px;flex:none;cursor:pointer">×</button>
    </div>

    <!-- Thanh tiến trình các bước -->
    <div style="display:flex;align-items:center;padding:12px 22px;background:var(--sub-h);border-bottom:1px solid var(--stroke);font-size:12.5px;gap:8px">
      <div style="display:flex;align-items:center;gap:6px;color:${buoc === 1 ? 'var(--acc)' : 'var(--txt2)'};font-weight:${buoc === 1 ? '700' : '500'}">
        <span style="width:20px;height:20px;border-radius:10px;background:${buoc === 1 ? 'var(--acc)' : 'var(--stroke2)'};color:${buoc === 1 ? '#fff' : 'var(--txt3)'};display:flex;align-items:center;justify-content:center;font-size:11px">1</span>
        <span>Chọn thể loại</span>
      </div>
      <span style="color:var(--stroke2)">›</span>
      <div style="display:flex;align-items:center;gap:6px;color:${buoc === 2 ? 'var(--acc)' : 'var(--txt2)'};font-weight:${buoc === 2 ? '700' : '500'}">
        <span style="width:20px;height:20px;border-radius:10px;background:${buoc === 2 ? 'var(--acc)' : 'var(--stroke2)'};color:${buoc === 2 ? '#fff' : 'var(--txt3)'};display:flex;align-items:center;justify-content:center;font-size:11px">2</span>
        <span>Thu âm mẫu</span>
      </div>
      <span style="color:var(--stroke2)">›</span>
      <div style="display:flex;align-items:center;gap:6px;color:${buoc >= 3 ? 'var(--acc)' : 'var(--txt2)'};font-weight:${buoc >= 3 ? '700' : '500'}">
        <span style="width:20px;height:20px;border-radius:10px;background:${buoc >= 3 ? 'var(--acc)' : 'var(--stroke2)'};color:${buoc >= 3 ? '#fff' : 'var(--txt3)'};display:flex;align-items:center;justify-content:center;font-size:11px">3</span>
        <span>${buoc === 4 ? 'Đang tạo…' : (buoc === 5 ? 'Hoàn tất ✓' : 'Tải tệp & Tạo')}</span>
      </div>
    </div>

    <div class="hop__than" style="padding:18px 22px;max-height:460px;overflow-y:auto">
      ${buoc === 1 ? `
        <div style="font-size:13px;color:var(--txt2);margin-bottom:12px">
          Chọn <b>phong cách đọc</b> bạn muốn nhân bản. Mỗi thể loại có ngữ điệu và đoạn mẫu chuẩn riêng:
        </div>
        <div style="display:grid;grid-template-columns:1fr 1fr;gap:10px">
          ${THE_LOAI_GIONG_MAU.map(t => `
            <div class="the-theloai${t.ma === theLoaiChon.ma ? ' dung' : ''}" data-nbtheloai="${t.ma}" style="padding:12px;border:1px solid ${t.ma === theLoaiChon.ma ? 'var(--acc)' : 'var(--stroke)'};border-radius:8px;cursor:pointer;background:${t.ma === theLoaiChon.ma ? 'var(--acc-soft)' : 'var(--card-bg, transparent)'}">
              <div style="display:flex;align-items:center;gap:8px;font-weight:600;font-size:13.5px;color:var(--txt)">
                <span style="font-size:18px">${t.icon}</span>
                <span>${t.ten}</span>
              </div>
              <div style="font-size:12px;color:var(--txt3);margin-top:4px">${t.phongCach}</div>
            </div>
          `).join('')}
        </div>
      ` : ''}

      ${buoc === 2 ? `
        <!-- 3 Tiêu chí vàng thu âm chất lượng cao -->
        <div style="display:grid;grid-template-columns:1fr 1fr 1fr;gap:10px;margin-bottom:14px">
          <div style="background:var(--sub-h);border:1px solid var(--stroke);border-radius:8px;padding:10px 12px">
            <div style="font-weight:700;font-size:12.5px;color:var(--txt);display:flex;align-items:center;gap:6px;margin-bottom:4px">
              <span style="font-size:15px">🔕</span>
              <span>Tránh môi trường ồn</span>
            </div>
            <div style="font-size:11.5px;color:var(--txt3);line-height:1.4">
              Tiếng vang, tạp âm xung quanh sẽ ảnh hưởng trực tiếp đến độ trong trẻo của giọng.
            </div>
          </div>

          <div style="background:var(--sub-h);border:1px solid var(--stroke);border-radius:8px;padding:10px 12px">
            <div style="font-weight:700;font-size:12.5px;color:var(--txt);display:flex;align-items:center;gap:6px;margin-bottom:4px">
              <span style="font-size:15px">🎙️</span>
              <span>Kiểm tra chất lượng mic</span>
            </div>
            <div style="font-size:11.5px;color:var(--txt3);line-height:1.4">
              Sử dụng micro tai nghe hoặc mic rời, đặt cách miệng 15–20cm để bắt rõ âm sắc.
            </div>
          </div>

          <div style="background:var(--sub-h);border:1px solid var(--stroke);border-radius:8px;padding:10px 12px">
            <div style="font-weight:700;font-size:12.5px;color:var(--txt);display:flex;align-items:center;gap:6px;margin-bottom:4px">
              <span style="font-size:15px">👤</span>
              <span>Audio 1 giọng đọc</span>
            </div>
            <div style="font-size:11.5px;color:var(--txt3);line-height:1.4">
              Chỉ dùng một giọng nói duy nhất xuyên suốt bản thu, không chèn nhạc nền.
            </div>
          </div>
        </div>

        <!-- Khung đọc đoạn văn gợi ý -->
        <div style="background:var(--sub-h);border:1px solid var(--stroke2);border-radius:10px;padding:16px 18px;margin-bottom:12px">
          <div style="display:flex;align-items:center;justify-content:space-between;margin-bottom:10px">
            <div style="font-size:11px;font-weight:700;letter-spacing:.05em;color:var(--txt3);text-transform:uppercase;display:flex;align-items:center;gap:6px">
              <span>ĐỌC ĐOẠN VĂN GỢI Ý</span>
              <span style="color:var(--acc);font-weight:600">(${theLoaiChon.ten})</span>
            </div>
            <div style="display:flex;align-items:center;gap:6px">
              <button class="nut nut--vien" id="nbDoiMau" title="Đổi sang đoạn mẫu ngữ âm khác" style="font-size:12px;padding:3px 9px;height:26px">
                🔄 Đổi đoạn khác
              </button>
              <button class="nut nut--vien" id="nbCopyMau" title="Sao chép đoạn văn vào bộ nhớ tạm" style="font-size:12px;padding:3px 10px;height:26px">
                📋 Sao chép
              </button>
            </div>
          </div>

          <div id="nbNoiDungMau" style="font-size:15px;font-weight:500;line-height:1.75;color:var(--txt);font-family:inherit">
            ${e(doanMauHienTai)}
          </div>
        </div>

        <div style="font-size:12px;color:var(--txt3);text-align:center">
          ⏱️ <i>Khuyến nghị: Hãy đọc với tốc độ vừa phải, tự nhiên trong khoảng <b>15 – 25 giây</b>.</i>
        </div>
      ` : ''}

      ${buoc === 3 ? `
        <div style="margin-bottom:14px">
          <div class="the__nhan" style="margin-bottom:6px">Ngôn ngữ của bản thu âm</div>
          <select class="chon" id="nbNgonNguGoc" style="width:100%">
            ${['Đông Nam Á & Bản Địa', 'Đông Á', 'Âu - Mỹ & Toàn Cầu', 'Nam Á & Trung Đông'].map(nhom => `
              <optgroup label="${nhom}">
                ${(typeof DS_NGON_NGU !== 'undefined' ? DS_NGON_NGU : []).filter(x => x.nhom === nhom).map(l => `<option value="${l.ma}"${(d.ngonNguGoc || 'vi') === l.ma ? ' selected' : ''}>${l.co} ${l.ten}</option>`).join('')}
              </optgroup>
            `).join('')}
          </select>
        </div>

        <div style="margin-bottom:14px">
          <div class="the__nhan" style="margin-bottom:6px">Tệp âm thanh thu âm (.wav, .mp3, .m4a, .flac)</div>
          <div style="display:flex;align-items:center;gap:10px">
            <button class="nut nut--vien" id="nbChonTep">📂 Chọn tệp âm thanh…</button>
            <span style="font-size:13px;color:${fileDaChon ? 'var(--txt)' : 'var(--txt3)'};font-weight:${fileDaChon ? '600' : 'normal'};flex:1;overflow:hidden;text-overflow:ellipsis;white-space:nowrap" id="nbTenFile">
              ${fileDaChon ? e(fileDaChon.split('\\').pop().split('/').pop()) : 'Chưa chọn tệp'}
            </span>
          </div>
        </div>

        <div style="margin-bottom:14px">
          <div class="the__nhan" style="margin-bottom:6px">Đặt tên cho giọng nhân bản</div>
          <input class="onhap" id="nbTenGiong" style="width:100%;font-size:14px;padding:8px 12px" placeholder="Ví dụ: Giọng Review Phim - Hoàng Nam" value="${e(tenGiong)}" autofocus spellcheck="false">
        </div>

        <div class="nb-dangu-card" id="nbHopDaNgonNgu" style="margin-bottom:14px;padding:12px 14px;background:var(--sub-h);border:1px solid ${d.daNgonNgu ? 'var(--acc)' : 'var(--stroke2)'};border-radius:8px;cursor:pointer;user-select:none;transition:border-color .15s">
          <label style="display:flex;align-items:flex-start;gap:10px;cursor:pointer;margin:0">
            <input type="checkbox" id="nbChkDaNgonNgu" ${d.daNgonNgu ? 'checked' : ''} style="margin-top:2px;accent-color:var(--acc);width:16px;height:16px;cursor:pointer">
            <div style="flex:1;min-width:0">
              <div style="font-weight:600;font-size:13.5px;color:var(--txt);display:flex;align-items:center;gap:6px">
                <span>🌐 Kích hoạt khả năng đọc Đa ngôn ngữ (Toàn cầu)</span>
                <span class="vanbanghep__badge" style="font-size:10px;padding:1px 5px;background:var(--acc-soft);color:var(--acc);border-radius:3px">Tùy chọn</span>
              </div>
              <div style="font-size:12px;color:var(--txt3);line-height:1.45;margin-top:3px">
                Mặc định tắt (chỉ đọc ngôn ngữ gốc đã chọn ở trên). Tích chọn nếu muốn AI dùng chất giọng này để đọc thêm 28 ngoại ngữ khác (Tiếng Anh, Pháp, Trung, Nhật, v.v.).
              </div>
            </div>
          </label>
        </div>
      ` : ''}

      ${buoc === 4 ? `
        <div style="padding:28px 16px;text-align:center">
          <div style="display:inline-block;width:44px;height:44px;border:3px solid var(--stroke2);border-top-color:var(--acc);border-radius:50%;animation:vbgXoay 1s linear infinite;margin-bottom:16px"></div>
          <div style="font-size:16px;font-weight:600;color:var(--txt);margin-bottom:8px">Đang nhân bản giọng "${e(tenGiong)}"…</div>
          <div style="font-size:13px;color:var(--txt2);margin-bottom:16px" id="nbTienDoText">${e(d.tienDo || 'Hệ thống đang trích xuất đặc trưng âm sắc và huấn luyện vector giọng…')}</div>
          <div style="background:var(--sub-h);border:1px solid var(--stroke2);border-radius:8px;padding:12px 14px;font-size:12px;color:var(--txt3);line-height:1.5;max-width:440px;margin:0 auto;text-align:left">
            💡 <b>Ghi chú:</b> Quá trình nhân bản diễn ra cục bộ trên máy. Bạn có thể bấm <b>"Chạy nền"</b> để tiếp tục làm việc, hệ thống sẽ tự động thông báo khi hoàn tất.
          </div>
        </div>
      ` : ''}

      ${buoc === 5 ? `
        <div style="padding:24px 16px;text-align:center">
          <div style="width:52px;height:52px;border-radius:50%;background:rgba(16,124,65,.1);color:#107c41;display:inline-flex;align-items:center;justify-content:center;font-size:26px;margin-bottom:14px;margin-left:auto;margin-right:auto">✓</div>
          <div style="font-size:17px;font-weight:700;color:var(--txt);margin-bottom:6px">Nhân bản thành công giọng "${e(tenGiong)}"!</div>
          <div style="font-size:13px;color:var(--txt3);margin-bottom:20px">
            Giọng đọc đã sẵn sàng và được lưu vào mục <b>"Giọng của tôi"</b> trong Thư viện giọng.
          </div>
          <div style="display:flex;justify-content:center;gap:10px;flex-wrap:wrap">
            <button class="nut nut--vien" id="nbNgheThuMoi" data-nghegiong="${e(d.idMoi || '')}">▶ Nghe thử mẫu</button>
            <button class="nut nut--acc" id="nbDatGiongMoi" data-giong="${e(d.idMoi || '')}">✨ Đặt làm giọng đọc hiện tại</button>
          </div>
        </div>
      ` : ''}
    </div>

    <div class="hop__chan" style="justify-content:space-between">
      <div>
        ${buoc === 2 || buoc === 3 ? `<button class="nut nut--vien" id="nbQuayLai">‹ Quay lại</button>` : ''}
        ${buoc === 1 ? `<button class="nut nut--vien" id="nbHuy">Huỷ</button>` : ''}
        ${buoc === 4 ? `<button class="nut nut--vien" id="nbChayNen">Chạy nền (Đóng cửa sổ)</button>` : ''}
      </div>
      <div style="display:flex;gap:8px">
        ${buoc === 1 ? `<button class="nut nut--acc" id="nbSangBuoc2">Tiếp tục (Xem mẫu) ›</button>` : ''}
        ${buoc === 2 ? `<button class="nut nut--acc" id="nbSangBuoc3">Đã thu âm xong (Tải tệp) ›</button>` : ''}
        ${buoc === 3 ? `<button class="nut nut--acc" id="nbBatDau">✨ Bắt đầu nhân bản giọng</button>` : ''}
        ${buoc === 5 ? `<button class="nut nut--acc" id="nbDongXong">Xong · Đóng</button>` : ''}
      </div>
    </div>
  </div></div>`;
}

if (typeof module !== 'undefined') {
  module.exports = {
    DINH_DANG, CACH_TACH, THE_LOAI_GIONG_MAU, veHopXuat, veHopDangXuat, veHopXuatXong, veBaoXuatXong,
    veHopTin, veHopGoogleDocs, veHopDayTu, veHopNhanBanGiong,
  };
}
