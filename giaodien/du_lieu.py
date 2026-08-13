# -*- coding: utf-8 -*-
"""Chuyển dữ liệu của engine sang đúng hình dạng mà giao diện cần.

Giao diện hiển thị THẲNG playlist (chứ không phải file gốc): mỗi mục trong
playlist là một dòng trên màn hình. Nhờ vậy số dòng người dùng thấy khớp
đúng với thứ tự máy sẽ đọc, và bấm vào dòng nào là nhảy đúng chỗ đó.
"""

import DocCongDuc as engine

# Nhãn hiển thị cho các đoạn lời dẫn do chương trình tự chèn, không phải
# nội dung người dùng gõ - hiện dưới dạng thẻ nhỏ ở đầu dòng.
NHAN_DOAN = {
    "mo_dau": "Lời mở đầu",
    "giua": "Lời giữa chừng",
    "ket": "Lời kết",
}

# Tốc độ đọc trung bình (ký tự/giây) dùng để ước lượng thời lượng mỗi dòng.
# Lấy đúng hằng số engine dùng trong uoc_luong_thoi_gian().
KY_TU_MOI_GIAY = 14.0


def _thoi_luong(text: str) -> str:
    giay = len(text or "") / KY_TU_MOI_GIAY
    if giay < 0.05:
        return ""
    return f"{giay:.1f}s".replace(".", ",")


# ---------------------------------------------------------------------------
# TÔ MÀU THEO TỪNG CHỮ
# ---------------------------------------------------------------------------
# VieNeu-TTS tổng hợp trọn cả câu thành một khối âm thanh, KHÔNG trả về mốc
# thời gian của từng chữ. Nên mỗi chữ hiển thị được gán một khoảng [b, e] tính
# theo TỈ LỆ của cả đoạn (0 = đầu, 1 = cuối); giao diện nhân tỉ lệ đó với thời
# lượng thật đo được từ tệp WAV để biết lúc nào tô chữ nào.
#
# Với dòng công đức thì bám sát được: câu máy đọc là "{tên}, phát tâm công đức
# số tiền {tiền}." nên tìm đúng vị trí của tên và của số tiền trong câu, chữ
# nào rơi vào khoảng nào thì sáng đúng lúc đó - kể cả quãng "phát tâm công đức
# số tiền" ở giữa (đọc thành tiếng nhưng không hiện trên màn hình).


def _chia_tu(text: str, bat_dau: float = 0.0, ket_thuc: float = 1.0) -> list:
    """Chia text thành từng chữ, trải đều trong khoảng [bat_dau, ket_thuc]
    theo độ dài từng chữ - chữ dài thì đọc lâu hơn."""
    tu = text.split()
    if not tu:
        return []
    tong = sum(len(t) + 1 for t in tu)
    ket_qua, moc = [], 0
    for t in tu:
        b = bat_dau + (ket_thuc - bat_dau) * moc / tong
        moc += len(t) + 1
        e = bat_dau + (ket_thuc - bat_dau) * moc / tong
        ket_qua.append({"t": t, "b": round(b, 4), "e": round(e, 4)})
    return ket_qua


def _moc_cong_duc(seg: dict, rec: dict, tudien: dict):
    """Tìm khoảng thời gian của phần tên và phần số tiền trong câu máy đọc.
    Trả về (moc_ten, moc_tien) hoặc (None, None) nếu không khớp."""
    noi = seg.get("text") or ""
    if not noi or not rec.get("amount"):
        return None, None
    ten_doc = engine.normalize_name(rec.get("name", ""), tudien)
    tien_doc = engine.format_money_for_reading(rec["amount"])
    i_ten, i_tien = noi.find(ten_doc), noi.rfind(tien_doc)
    if i_ten < 0 or i_tien < 0:
        return None, None
    n = float(len(noi))
    return ((i_ten / n, (i_ten + len(ten_doc)) / n),
            (i_tien / n, (i_tien + len(tien_doc)) / n))


def dong_hien_thi(playlist: list, che_do: str, tudien: dict = None) -> list:
    """Đổi playlist thành danh sách dòng cho giao diện."""
    tudien = tudien or {}
    ket_qua = []
    for seg in playlist:
        loai = seg.get("loai", "")
        chip = NHAN_DOAN.get(loai, "")
        rec = seg.get("rec")
        moc_tien = None

        if che_do == "congduc" and loai == "nguoi" and rec:
            text = rec.get("name", "")
            amount = engine.format_money_for_display(rec.get("amount", ""))
            ten, tien = _moc_cong_duc(seg, rec, tudien)
            if ten:
                tu = _chia_tu(" ".join(text.split()), ten[0], ten[1])
                moc_tien = {"b": round(tien[0], 4), "e": round(tien[1], 4)}
            else:
                tu = _chia_tu(" ".join(text.split()))
        elif che_do == "congduc" and loai == "tieude" and rec:
            text = rec.get("name", "")
            amount = ""
            tu = _chia_tu(" ".join(text.split()))
        else:
            # Văn bản thường: hiện đúng đoạn gốc người dùng gõ, không hiện
            # bản đã chuẩn hoá - bản chuẩn hoá xem ở "Xem trước chuẩn hoá".
            text = (seg.get("goc") or seg.get("text") or "").strip()
            amount = ""
            tu = _chia_tu(" ".join(text.split()))

        ket_qua.append({
            "text": " ".join(text.split()),
            "amount": amount,
            "chip": chip,
            "kind": "tieude" if loai == "tieude" else loai,
            "dur": _thoi_luong(seg.get("text", "")),
            "tu": tu,
            "tien": moc_tien,
        })
    return ket_qua


# ---------------------------------------------------------------------------
# THANH TRƯỢT
# ---------------------------------------------------------------------------
# VieNeu-TTS KHÔNG có tham số tốc độ hay cao độ (xem chú thích ở đầu
# DocCongDuc.py). Thứ thật sự chỉnh được là các khoảng nghỉ do chương trình
# tự chèn giữa câu/người/nhóm, nên thanh trượt gắn vào đúng những giá trị đó.

THANH_TRUOT = {
    "congduc": [
        ("nghi_nguoi", "Nghỉ giữa mỗi người", 0.0, 5.0, "giay",
         "Khoảng lặng sau mỗi tên, từ 0 đến 5 giây"),
        ("nghi_nhom", "Nghỉ giữa mỗi nhóm", 0.0, 8.0, "giay",
         "Khoảng lặng sau mỗi nhóm, từ 0 đến 8 giây"),
        ("so_nguoi_nhom", "Số người mỗi nhóm", 1, 50, "nguoi",
         "Cứ bao nhiêu tên thì nghỉ dài một lần"),
    ],
    "vanban": [
        ("nghi_cau", "Nghỉ giữa các câu", 0.0, 2.0, "giay",
         "Khoảng lặng giữa hai câu, từ 0 đến 2 giây"),
        ("nghi_doan_vb", "Nghỉ giữa các đoạn", 0.0, 3.0, "giay",
         "Khoảng lặng giữa hai đoạn, từ 0 đến 3 giây"),
        ("so_ky_tu", "Độ dài mỗi lần đọc", 120, 600, "kytu",
         "Số ký tự tối đa mỗi lần gửi đi tổng hợp giọng"),
    ],
}


def _hien_thi_gia_tri(kieu: str, gia_tri) -> str:
    if kieu == "giay":
        return f"{gia_tri:.2f}".rstrip("0").rstrip(".").replace(".", ",") + " giây"
    if kieu == "nguoi":
        return f"{int(gia_tri)} người"
    return f"{int(gia_tri)} ký tự"


def thanh_truot(cfg: dict, che_do: str) -> list:
    ket_qua = []
    for khoa, nhan, thap, cao, kieu, pham_vi in THANH_TRUOT[che_do]:
        gia_tri = cfg.get(khoa, thap)
        ket_qua.append({
            "khoa": khoa,
            "nhan": nhan,
            "min": thap,
            "max": cao,
            "gia_tri": gia_tri,
            "kieu": kieu,          # giao diện tự định dạng lại khi đang kéo
            "hien_thi": _hien_thi_gia_tri(kieu, gia_tri),
            "pham_vi": pham_vi,
        })
    return ket_qua


def ep_gia_tri(khoa: str, gia_tri: float, che_do: str):
    """Ép giá trị thanh trượt về đúng kiểu và khoảng cho phép."""
    for k, _nhan, thap, cao, kieu, _pv in THANH_TRUOT[che_do]:
        if k != khoa:
            continue
        gia_tri = max(thap, min(cao, float(gia_tri)))
        if kieu in ("nguoi", "kytu"):
            return int(round(gia_tri))
        # Làm tròn 0,1 giây: "2,6 giây" dễ đọc hơn "2,64 giây", mà chênh lệch
        # phần trăm giây thì tai người cũng không nghe ra.
        return round(gia_tri, 1)
    return None


def phong_cach() -> list:
    return [{"ten": ten, "mo_ta": pc["mo_ta"]}
            for ten, pc in engine.PHONG_CACH.items()]


GIOI_TINH = {"nam", "nữ", "nu"}
VUNG_MIEN = {"bắc", "trung", "nam"}


def _tach_nhan_giong(nhan: str):
    """Engine trả nhãn dạng "Minh Đức — Nam · Bắc · Phong cách tin tức".

    Tách thành hai dòng cho giao diện, giới tính đưa lên cạnh tên:
        dòng 1:  Minh Đức (Nam)
        dòng 2:  Bắc · Phong cách tin tức

    Để nguyên một chuỗi dài thì nó tự ngắt giữa chừng, danh sách nhìn rất rối.
    Giọng riêng do người dùng nhân bản không có phần mô tả, chỉ còn mỗi tên.
    """
    ten, mo_ta = nhan.strip(), ""
    for dau in ("—", "–", " - "):
        if dau in nhan:
            ten, _, mo_ta = nhan.partition(dau)
            ten, mo_ta = ten.strip(), mo_ta.strip()
            break

    phan = [p.strip() for p in mo_ta.split("·") if p.strip()]
    # Chỉ ngoặc đơn khi phần đầu đúng là giới tính - phòng khi bản VieNeu khác
    # đặt nhãn theo kiểu khác thì không bịa ra dấu ngoặc vô nghĩa.
    if phan and phan[0].lower() in GIOI_TINH:
        ten = f"{ten} ({phan[0]})"
        phan = phan[1:]

    # Engine ghi vùng miền trơ trọi là "Bắc"/"Trung"/"Nam". Đứng ngay sau
    # "(Nam)" của giới tính thì chữ "Nam" hiện hai lần với hai nghĩa khác nhau,
    # người đọc rất dễ hiểu nhầm - thêm chữ "Miền" cho tách bạch.
    if phan and phan[0].lower() in VUNG_MIEN:
        phan[0] = "Miền " + phan[0]
    return ten, " · ".join(phan)


def danh_sach_giong(ds: list) -> list:
    """Đánh dấu giọng riêng để giao diện tách nhóm. Engine trả về tên giọng
    riêng có tiền tố 🎙️ và hậu tố '(giọng riêng)' - bỏ đi cho gọn vì giao
    diện đã có nhóm riêng và huy hiệu 'Nhân bản'."""
    ket_qua = []
    ma_rieng = {g["id"] for g in engine.doc_ds_giong_rieng()}
    for g in ds:
        nhan = g.get("ten", g.get("nhan", g["id"]))
        rieng = g["id"] in ma_rieng
        if rieng:
            nhan = nhan.replace("🎙️", "").replace("(giọng riêng)", "").strip()
        ten, mo_ta = _tach_nhan_giong(nhan)
        ket_qua.append({"id": g["id"], "ten": ten, "mo_ta": mo_ta,
                        "rieng": rieng})
    return ket_qua
