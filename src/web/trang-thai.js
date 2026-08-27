/* Giọng Việt — mô hình trạng thái và các phép suy ra.
   Tên khoá giữ đúng như bảng "Trạng thái ứng dụng" cuối README để đối chiếu
   được từng dòng; giải thích thì bằng tiếng Việt.

   Ở đây KHÔNG có DOM và KHÔNG có gọi Python. Chỉ dữ liệu và phép biến đổi
   thuần, để sau này thay lớp mock bằng engine thật mà không phải sửa gì. */

'use strict';

// ---------------------------------------------------------------- hằng

/* Bảy tình huống trong mục "Trạng thái lỗi và chờ". Ba tình huống đầu KHOÁ
   nút Nghe và Xuất; hai tình huống sau vẫn xuất được. */
const TINH_HUONG = {
  BINH_THUONG:  'binh_thuong',
  MAT_KET_NOI:  'mat_ket_noi',
  HET_LUOT:     'het_luot',
  GIONG_DANG_TAI: 'giong_dang_tai',
  VAN_BAN_QUA_DAI: 'van_ban_qua_dai',
  AM_THANH_CU:  'am_thanh_cu',
  DANG_TAO:     'dang_tao',
};

const KHOA_NGHE_VA_XUAT = [
  TINH_HUONG.MAT_KET_NOI, TINH_HUONG.HET_LUOT, TINH_HUONG.GIONG_DANG_TAI,
];

/* Thời lượng ước tính: số ký tự chia 11 ra giây. Con số 11 là của đặc tả,
   không phải đo từ engine - lúc nối engine thật phải đo lại. */
const KY_TU_MOI_GIAY = 11;

// ---------------------------------------------------------------- trạng thái

function trangThaiBanDau(hoSo) {
  const tabs = {}, dangXem = {};
  hoSo.forEach((h, i) => { tabs[i] = h.tep.slice(); dangXem[i] = 0; });

  return {
    profile: 0,                 // hồ sơ đang chọn
    profiles: hoSo,             // tên, giọng, tốc độ, cao độ, âm lượng
    tabsByProfile: tabs,        // danh sách tệp mở của TỪNG hồ sơ
    activeByProfile: dangXem,   // tệp đang xem của từng hồ sơ

    view: 'san_sang',           // san_sang | dang_doc | rong
    situation: TINH_HUONG.BINH_THUONG,

    pos: 1,                     // đoạn đang đọc
    sel: 1,                     // đoạn đang chọn (con trỏ)
    mode: 'all',                // all = nghe liền mạch · one = nghe riêng một đoạn

    rail: false,                // cột trái thu gọn
    menu: -1,                   // menu trên cùng đang mở, -1 là không mở cái nào
    find: false,                // thanh tìm và thay thế
    tags: false,                // menu thẻ cảm xúc
    voiceOpen: false,           // dropdown chọn giọng
    tune: false,                // mục ĐIỀU CHỈNH đang mở

    /* Mã giọng đang nghe thử, '' là không nghe gì. Bấm nghe thử rồi máy tổng
       hợp mất mấy giây; không có cờ này thì nút bấm xong trông y như chưa bấm
       và người dùng bấm tiếp mấy lần nữa. */
    dangNgheThu: '',

    /* Màn đang xem. 'chinh' hoặc 'soat'. Các màn phụ phủ lên phần GIỮA của
       màn chính chứ không thay cả cửa sổ — người lớn tuổi mà bị nhảy sang màn
       khác hẳn thì mất phương hướng, không biết đường quay lại. */
    man: 'chinh',
    soatTab: 'chuy',            // chuy | chuanhoa
    soatLoc: 'tatca',           // tatca | nang | nhe

    /* Những chỗ người dùng đã xem và quyết bỏ qua: { 'loai|tu|đoạn': true }.
       Soát ra chín chỗ mà không đánh dấu được đã xử lý chỗ nào thì càng nhìn
       càng rối - lần nào mở ra cũng thấy y nguyên chín chỗ ấy.

       Chỉ giữ trong phiên, KHÔNG ghi xuống hồ sơ: đây là việc đang làm dở
       trong một lượt soát, không phải thiết lập của người dùng. */
    soatBoQua: {},
    zoom: 100,                  // cỡ chữ vùng đọc, %

    /* Cửa sổ đang lấp kín vùng làm việc chưa. Quyết định nút giữa mang nghĩa
       "Phóng to" hay "Thu về cỡ vừa" — một thời điểm chỉ một nghĩa. */
    cuaSoKin: false,

    // Thẻ cảm xúc theo đoạn, lồng theo tên tệp: { 'ten-tep.txt': { 11: '[hắng giọng]' } }
    chips: { 'thongbao-quoc-khanh.txt': { 11: '[hắng giọng]' } },

    /* Đường dẫn thật của từng tệp đã mở: { 'thongbao.txt': 'C:\\...\\thongbao.txt' }.
       Tab chỉ giữ TÊN tệp, mà tên thì không mở lại được sau khi đóng chương
       trình. Để riêng ở đây chứ không nhét vào mảng tab: mảng tab là mảng chuỗi
       và đã dùng ở hơn mười chỗ, đổi hình dạng của nó là sửa lan ra cả tệp.
       Văn bản dán từ clipboard không có đường dẫn nên không có mặt trong map. */
    duongDanTep: {},

    /* Loại của từng tệp đã mở: { 'danhsach.txt': 'congduc' }. Danh sách tên và
       số đọc theo đường khác hẳn văn bản thường — engine dựng câu từ mẫu trong
       lời dẫn, chèn lời mở đầu/giữa/kết. Không nhớ loại thì đổi tab xong nó
       đọc nguyên cả dòng "Nguyễn Văn A — 500.000". */
    loaiTep: {},

    exportOpen: false, exporting: false, toast: false,
    /* Hộp xuất đang ở giai đoạn nào: null (không hiện) | 'chay' | 'xong'.
       Tách khỏi `exporting`: bấm "Chạy nền" thì hộp biến mất nhưng việc xuất
       vẫn chạy, lúc ấy exporting còn true mà xuatGiaiDoan đã về null. */
    xuatGiaiDoan: null, xuatTienDo: null, xuatKetQua: null,
    hopTin: null,               // hộp chỉ để đọc: Trợ giúp
    theme: 'sang',              // sang | toi
  };
}

// ---------------------------------------------------------------- đọc ra

const hoSoDangDung = (S) => S.profiles[S.profile];
const tabDangMo    = (S) => S.tabsByProfile[S.profile] || [];
const tenTepDangXem = (S) => tabDangMo(S)[S.activeByProfile[S.profile]] || '';

/** Đoạn của tệp đang xem. Tab "Chưa đặt tên" thì trả mảng rỗng. */
function doanDangXem(S, TAI_LIEU) {
  const t = TAI_LIEU[tenTepDangXem(S)];
  return t ? t.doan : [];
}

function chuYDangXem(S, TAI_LIEU) {
  const t = TAI_LIEU[tenTepDangXem(S)];
  return t ? t.chuY : null;
}

const theCuaDoan = (S, so) => (S.chips[tenTepDangXem(S)] || {})[so] || '';

/** Đang khoá nút Nghe / Xuất vì máy đọc không dùng được hoặc đang chuẩn bị dịch? */
const biKhoa = (S) => !!(S && (S.dangChuanBiDich || KHOA_NGHE_VA_XUAT.includes(S.situation)));

/** Cặp Nghe toàn bộ + Xuất ẨN HẲN khi chưa có văn bản, không phải hiện mờ. */
const hienNgheVaXuat = (S, TAI_LIEU) => doanDangXem(S, TAI_LIEU).length > 0;

// ---------------------------------------------------------------- suy ra số

const soGiay = (doan) =>
  doan.reduce((t, d) => t + d.chu.length, 0) / KY_TU_MOI_GIAY;

/** Dưới 60 giây ghi "42 giây", từ 60 giây trở lên ghi "1 phút 28 giây". */
function dinhDangThoiLuong(giay) {
  const g = Math.round(giay);
  if (g < 60) return `${g} giây`;
  const p = Math.floor(g / 60);
  const du = g % 60;
  return du ? `${p} phút ${du} giây` : `${p} phút`;
}

/** Đồng hồ `mm:ss` của thanh phát.

    Làm tròn giống hệt dinhDangThoiLuong, nếu không thì cùng một tài liệu mà
    đầu vùng đọc ghi "1 phút 28 giây" còn thanh phát ghi "01:27" - người dùng
    nhìn thấy hai con số khác nhau là mất tin vào cả hai. */
function dongHo(giay) {
  const g = Math.round(giay);
  return `${String(Math.floor(g / 60)).padStart(2, '0')}:${String(g % 60).padStart(2, '0')}`;
}

/** Chia một đoạn thành từng chữ, mỗi chữ mang khoảng [b, e] theo TỈ LỆ của cả
    đoạn (0 = đầu, 1 = cuối), chia theo độ dài chữ vì chữ dài thì đọc lâu hơn.

    Thuật toán giống hệt `_chia_tu` trong giaodien/du_lieu.py. Cố ý trùng: lúc
    chưa nối Python thì bản mock tự chia, nối rồi thì lấy mốc từ Python — hai
    bên phải ra cùng kết quả, không thì tô chữ nhảy khác nhau ở hai chế độ. */
function chiaTu(text, batDau = 0, ketThuc = 1, trongSo = null) {
  const tu = String(text || '').split(/\s+/).filter(Boolean);
  if (!tu.length) return [];

  /* `trongSo` là độ dài chữ ĐỌC RA, do Python tính bằng chính engine. Dùng nó
     thay cho độ dài chữ hiển thị, vì hai thứ đó lệch nhau rất xa ở chữ có số:
     "31/8/2026" chỉ 9 ký tự mà đọc thành "ba mươi mốt tháng tám năm hai nghìn
     không trăm hai mươi sáu". Chia theo ký tự hiển thị là chữ đó vụt qua trong
     khi loa còn đang đọc dở — đo được 0,68 giây lệch.

     Số phần tử phải khớp số chữ, không thì bỏ qua: thà chia đều còn hơn ghép
     nhầm trọng số của chữ này cho chữ kia. */
  /* Chia theo ký tự thì cộng thêm 1 cho khoảng trắng — nó chiếm chỗ trên màn
     hình. Chia theo âm tiết thì KHÔNG: khoảng trắng không được đọc thành
     tiếng, cộng vào là lệch với cách Python tính phạm vi mẩu, và hai thước
     vênh nhau bao nhiêu thì chữ nhảy sai bấy nhiêu. */
  const co = Array.isArray(trongSo) && trongSo.length === tu.length;
  const nang = (t, i) => (co ? trongSo[i] : t.length + 1);

  const tong = tu.reduce((s, t, i) => s + nang(t, i), 0);
  let moc = 0;
  return tu.map((t, i) => {
    const b = batDau + (ketThuc - batDau) * moc / tong;
    moc += nang(t, i);
    const e = batDau + (ketThuc - batDau) * moc / tong;
    return { t, b: +b.toFixed(4), e: +e.toFixed(4) };
  });
}

const soTu = (doan) =>
  doan.reduce((t, d) => t + (d.chu.trim() ? d.chu.trim().split(/\s+/).length : 0), 0);

/** Dòng thống kê đầu vùng đọc: "215 từ · 16 đoạn · khoảng 1 phút 28 giây". */
function thongKe(doan) {
  if (!doan.length) return '';
  return `${soTu(doan)} từ · ${doan.length} đoạn · `
       + `khoảng ${dinhDangThoiLuong(soGiay(doan))}`;
}

/** Đồng hồ thanh phát. Nghe riêng thì đếm theo ĐỘ DÀI ĐOẠN ĐÓ, không phải cả bài. */
function tongThoiLuongDangNghe(S, TAI_LIEU) {
  const doan = doanDangXem(S, TAI_LIEU);
  if (S.mode === 'one') {
    const d = doan[S.pos - 1];
    return d ? d.chu.length / KY_TU_MOI_GIAY : 0;
  }
  return soGiay(doan);
}

// ---------------------------------------------------------------- chuyển trạng thái

/* Sáu quy tắc chuyển trạng thái ở cuối README. Gom vào một chỗ để không rải
   rác mỗi nơi một kiểu - đó là cách sinh ra lỗi "bấm chỗ này thì chỗ kia quên
   cập nhật". */

/** Bấm số đoạn = nghe riêng đoạn đó. Nghe hết đoạn thì DỪNG, không chạy tiếp. */
function ngheRiengDoan(S, n) {
  return { ...dongHetMenu(S), view: 'dang_doc', mode: 'one', pos: n, sel: n };
}

function ngheToanBo(S) {
  return { ...dongHetMenu(S), view: 'dang_doc', mode: 'all', pos: 1 };
}

/** Bấm vào thân đoạn = chọn đoạn, KHÔNG phát tiếng. */
function chonDoan(S, n) {
  return { ...dongHetMenu(S), sel: n };
}

/** Tạm dừng giữ nguyên vị trí để bấm Phát là đọc tiếp đúng chỗ đang dở. */
const tamDung = (S) => ({ ...S, view: 'san_sang' });
const dungHan = (S) => ({ ...S, view: 'san_sang', mode: 'all' });

/** Hết đoạn ở chế độ nghe riêng thì tự dừng. */
const hetDoan = (S) =>
  S.mode === 'one' ? { ...S, view: 'san_sang' } : S;

/* Đổi hồ sơ hay đổi tab là đổi sang văn bản khác, nên những chỗ đã bỏ qua của
   văn bản cũ phải quên đi - giữ lại thì số đoạn trỏ vào một bài không còn nữa. */
function doiHoSo(S, i) {
  return { ...dongHetMenu(S), profile: i, view: 'san_sang', pos: 1, sel: 1, soatBoQua: {} };
}

function doiTab(S, i) {
  const m = { ...S.activeByProfile, [S.profile]: i };
  return { ...dongHetMenu(S), activeByProfile: m,
           view: 'san_sang', pos: 1, sel: 1, soatBoQua: {} };
}

/** Đóng tab cuối cùng thì còn lại một tab "Chưa đặt tên" rỗng, không đóng hết. */
function dongTab(S, i) {
  const ds = tabDangMo(S).slice();
  ds.splice(i, 1);
  if (!ds.length) ds.push('');
  const dang = Math.min(S.activeByProfile[S.profile], ds.length - 1);
  /* Bảng nhãn đánh theo VỊ TRÍ, nên đóng một hàng thì phải cắt nhãn ở đúng vị
     trí ấy (spliceName của bản mẫu). Không cắt thì nhãn của hàng dưới tụt lên
     đeo nhầm tệp — người dùng thấy tên mình đặt cho bài này nhảy sang bài khác. */
  const nhan = { ...(S.nhanTep || {}) };
  const cua = nhan[S.profile];
  if (cua && cua.length) {
    const n = cua.slice();
    n.splice(i, 1);
    nhan[S.profile] = n;
  }
  return {
    ...dongHetMenu(S),
    tabsByProfile: { ...S.tabsByProfile, [S.profile]: ds },
    activeByProfile: { ...S.activeByProfile, [S.profile]: Math.max(0, dang) },
    nhanTep: nhan,
    view: 'san_sang', pos: 1, sel: 1,
  };
}

function themTab(S) {
  const ds = tabDangMo(S).concat('');
  return {
    ...dongHetMenu(S),
    tabsByProfile: { ...S.tabsByProfile, [S.profile]: ds },
    activeByProfile: { ...S.activeByProfile, [S.profile]: ds.length - 1 },
    view: 'san_sang', pos: 1, sel: 1,
  };
}

/** Mở một menu thì đóng hết các menu còn lại; bấm ra ngoài thì đóng tất cả. */
function moMenu(S, i) {
  return { ...dongHetMenu(S), menu: S.menu === i ? -1 : i };
}

const dongHetMenu = (S) => ({ ...S, menu: -1, tags: false, voiceOpen: false });

/** Chèn thẻ cảm xúc vào ĐOẠN ĐANG CHỌN, gỡ được bằng cách truyền chuỗi rỗng. */
function datThe(S, the) {
  const tep = tenTepDangXem(S);
  const cua = { ...(S.chips[tep] || {}) };
  if (the) { cua[S.sel] = the; } else { delete cua[S.sel]; }
  return { ...dongHetMenu(S), chips: { ...S.chips, [tep]: cua } };
}

/* Sửa chữ làm số đoạn xê dịch, mà thẻ cảm xúc lại đánh THEO SỐ ĐOẠN. Không
   dời theo thì tách một đoạn ở giữa bài là mọi thẻ phía dưới nhảy sang nhầm
   câu, trong khi người dùng không hề đụng tới chúng.

   delta > 0: chèn thêm đoạn, mọi thẻ từ `tuDoan` trở xuống dời xuống.
   delta < 0: bớt đoạn, thẻ của những đoạn bị xoá bỏ hẳn, phần còn lại dời lên. */
function dichThe(chips, tep, tuDoan, delta) {
  const cu = chips[tep] || {};
  const moi = {};
  Object.keys(cu).forEach((k) => {
    const n = +k;
    if (n < tuDoan) { moi[n] = cu[k]; return; }
    if (delta < 0 && n < tuDoan - delta) return;   // đoạn này bị xoá mất
    moi[n + delta] = cu[k];
  });
  return { ...chips, [tep]: moi };
}

/* Chọn giọng và kéo thanh điều chỉnh ghi vào HỒ SƠ ĐANG DÙNG, không phải
   một biến toàn cục dùng chung. Đây là điểm mấu chốt của mô hình hồ sơ. */
function datGiong(S, maGiong) {
  const ds = S.profiles.map((h, i) => i === S.profile ? { ...h, giong: maGiong } : h);
  return { ...dongHetMenu(S), profiles: ds };
}

function datChinh(S, khoa, gt) {
  const ds = S.profiles.map((h, i) =>
    i === S.profile ? { ...h, chinh: { ...h.chinh, [khoa]: gt } } : h);
  return { ...S, profiles: ds };
}

/** Dòng tóm tắt khi mục ĐIỀU CHỈNH đang đóng. */
function tomTatChinh(chinh) {
  const p = [];
  if (chinh.tocDo) p.push(`Tốc độ ${chinh.tocDo > 0 ? '+' : '−'}${Math.abs(chinh.tocDo)}%`);
  if (chinh.caoDo) p.push(`Cao độ ${chinh.caoDo > 0 ? '+' : '−'}${Math.abs(chinh.caoDo)}`);
  if (chinh.amLuong !== 100) p.push(`Âm lượng ${chinh.amLuong}%`);
  
  const kg = String(chinh.khongGian || '').toLowerCase();
  if (kg === 'podcast') p.push('Studio/Podcast');
  else if (kg === 'hoitruong') p.push('Hội trường');
  else if (kg === 'loaphuong') p.push('Loa phường');
  else if (kg === 'radio') p.push('Radio FM');
  
  return p.length ? p.join(' · ') : 'Theo mặc định của hồ sơ';
}

if (typeof module !== 'undefined') {
  module.exports = {
    TINH_HUONG, KY_TU_MOI_GIAY, trangThaiBanDau,
    hoSoDangDung, tabDangMo, tenTepDangXem, doanDangXem, chuYDangXem, theCuaDoan,
    biKhoa, hienNgheVaXuat,
    soGiay, dinhDangThoiLuong, dongHo, chiaTu, soTu, thongKe, tongThoiLuongDangNghe,
    ngheRiengDoan, ngheToanBo, chonDoan, tamDung, dungHan, hetDoan,
    doiHoSo, doiTab, dongTab, themTab, moMenu, dongHetMenu, datThe, dichThe,
    datGiong, datChinh, tomTatChinh,
  };
}
