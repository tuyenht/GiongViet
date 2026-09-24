# -*- coding: utf-8 -*-
"""Danh mục thông tin chi tiết và số hóa chuẩn hóa toàn bộ 111 giọng đọc AI (VieNeu và Đa ngữ).

Tách bạch 100% giữa ID Kỹ thuật (ASCII chuẩn) và Dữ liệu Hiển thị (Tiếng Việt đầy đủ,
gợi ý đặc điểm, vùng miền, sở trường, mục đích sử dụng tốt nhất).
"""

import re
import unicodedata

# 1. Danh mục chi tiết các giọng dựng sẵn tiếng Việt trong mô hình VieNeu
DANH_MUC_VIENEU = {
    "vi_minh_duc": {
        "id": "vi_minh_duc",
        "alias": ["Minh Đức", "minh duc", "minhduc", "Minh Đức (Nam)"],
        "ten": "Minh Đức",
        "gioi": "Nam",
        "vung": "Miền Bắc",
        "phong_cach": "Tin tức · Thời sự",
        "dac_trung": "Giọng nam miền Bắc chuẩn phát thanh viên thời sự, trầm vang, dứt khoát",
        "khuyen_dung": "Bản tin thời sự, tài liệu chính luận, thuyết trình doanh nghiệp",
        "cau_mau": "Tôi là Minh Đức, giọng nam miền Bắc chuẩn phong cách tin tức và tài liệu chính luận.",
        "icon": "📢",
        "cls": "the-giong__avatar--tintuc"
    },
    "vi_pham_tuyen": {
        "id": "vi_pham_tuyen",
        "alias": ["Phạm Tuyên", "pham tuyen", "phamtuyen", "Phạm Tuyên (Nam)"],
        "ten": "Phạm Tuyên",
        "gioi": "Nam",
        "vung": "Miền Bắc",
        "phong_cach": "Tự nhiên · Gần gũi",
        "dac_trung": "Giọng nam miền Bắc tự nhiên, ấm áp, thân thiện, rõ từng từ ngữ",
        "khuyen_dung": "Đọc sách báo hàng ngày, tản văn, bài giảng giáo dục, blog",
        "cau_mau": "Tôi là Phạm Tuyên, giọng đọc tự nhiên, gần gũi, phù hợp đọc sách và thông tin hàng ngày.",
        "icon": "👨",
        "cls": "the-giong__avatar--nam"
    },
    "vi_thai_son": {
        "id": "vi_thai_son",
        "alias": ["Thái Sơn", "thai son", "thaison", "Thái Sơn (Nam)"],
        "ten": "Thái Sơn",
        "gioi": "Nam",
        "vung": "Miền Nam",
        "phong_cach": "Hào sảng · Kể chuyện",
        "dac_trung": "Giọng nam miền Nam hào sảng, truyền cảm, nhịp điệu cuốn hút",
        "khuyen_dung": "Đọc truyện kiếm hiệp, tiểu thuyết dã sử, ký sự phóng sự",
        "cau_mau": "Tôi là Thái Sơn, giọng nam miền Nam hào sảng, chuyên đọc truyện và ký sự truyền cảm.",
        "icon": "🎙️",
        "cls": "the-giong__avatar--doctruyen"
    },
    "vi_xuan_vinh": {
        "id": "vi_xuan_vinh",
        "alias": ["Xuân Vĩnh", "xuan vinh", "xuanvinh", "Xuân Vĩnh (Nam)"],
        "ten": "Xuân Vĩnh",
        "gioi": "Nam",
        "vung": "Miền Nam",
        "phong_cach": "Nhẹ nhàng · Tản văn",
        "dac_trung": "Giọng nam miền Nam nhẹ nhàng, thư thái, phát âm rõ ràng êm tai",
        "khuyen_dung": "Đọc tản văn, podcast trò chuyện, truyện ngắn đời sống",
        "cau_mau": "Tôi là Xuân Vĩnh, giọng nam miền Nam tự nhiên, nhẹ nhàng và rõ ràng.",
        "icon": "👨",
        "cls": "the-giong__avatar--nam"
    },
    "vi_thanh_binh": {
        "id": "vi_thanh_binh",
        "alias": ["Thanh Bình", "thanh binh", "thanhbinh", "Thanh Bình (Nam)"],
        "ten": "Thanh Bình",
        "gioi": "Nam",
        "vung": "Miền Bắc",
        "phong_cach": "Trầm ấm · Sâu lắng",
        "dac_trung": "Giọng nam miền Bắc trầm ấm, sâu lắng, nhịp điệu thong thả truyền cảm",
        "khuyen_dung": "Đọc truyện đêm khuya, sách triết lý, không gian thiền tịnh",
        "cau_mau": "Tôi là Thanh Bình, giọng nam miền Bắc ấm áp, phù hợp cho các bài tản văn và sách nói.",
        "icon": "☕",
        "cls": "the-giong__avatar--sachnoi"
    },
    "vi_truc_ly": {
        "id": "vi_truc_ly",
        "alias": ["Trúc Ly", "truc ly", "trucly", "Trúc Ly (Nữ)"],
        "ten": "Trúc Ly",
        "gioi": "Nữ",
        "vung": "Miền Bắc",
        "phong_cach": "Trong trẻo · Tự nhiên",
        "dac_trung": "Giọng nữ miền Bắc trong trẻo, thanh thoát, phát âm chuẩn mực",
        "khuyen_dung": "Đọc sách thiếu nhi, tản văn nhẹ nhàng, tài liệu hướng dẫn",
        "cau_mau": "Tôi là Trúc Ly, giọng nữ miền Bắc trong trẻo, phù hợp đọc sách và bài viết nhẹ nhàng.",
        "icon": "👩",
        "cls": "the-giong__avatar--nu"
    },
    "vi_ngoc_linh": {
        "id": "vi_ngoc_linh",
        "alias": ["Ngọc Linh", "ngoc linh", "ngoclinh", "Ngọc Linh (Nữ)"],
        "ten": "Ngọc Linh",
        "gioi": "Nữ",
        "vung": "Miền Bắc",
        "phong_cach": "Truyền cảm · Dịu dàng",
        "dac_trung": "Giọng nữ miền Bắc truyền cảm, dịu dàng, âm sắc ngọt ngào",
        "khuyen_dung": "Chuyên đọc sách nói, tiểu thuyết tình cảm, tự sự tâm tình",
        "cau_mau": "Tôi là Ngọc Linh, giọng nữ miền Bắc truyền cảm, chuyên đọc sách nói và tiểu thuyết.",
        "icon": "☕",
        "cls": "the-giong__avatar--sachnoi"
    },
    "vi_doan_trang": {
        "id": "vi_doan_trang",
        "alias": ["Đoan Trang", "doan trang", "doantrang", "Đoan Trang (Nữ)"],
        "ten": "Đoan Trang",
        "gioi": "Nữ",
        "vung": "Miền Bắc",
        "phong_cach": "Trẻ trung · Năng động",
        "dac_trung": "Giọng nữ miền Bắc hiện đại, trẻ trung, tươi sáng và linh hoạt",
        "khuyen_dung": "Tin tức đời sống, hướng dẫn du lịch, review công nghệ và ẩm thực",
        "cau_mau": "Tôi là Đoan Trang, giọng nữ miền Bắc tươi trẻ, phù hợp đọc tin tức đời sống và review.",
        "icon": "🛍️",
        "cls": "the-giong__avatar--quangcao"
    },
    "vi_mai_anh": {
        "id": "vi_mai_anh",
        "alias": ["Mai Anh", "mai anh", "maianh", "Mai Anh (Nữ)"],
        "ten": "Mai Anh",
        "gioi": "Nữ",
        "vung": "Miền Bắc",
        "phong_cach": "Dứt khoát · Bản tin",
        "dac_trung": "Giọng nữ miền Bắc đĩnh đạc, phát âm sắc nét, chuẩn phát thanh viên",
        "khuyen_dung": "Bản tin nhanh, thông báo công ty, tài liệu tổng kết",
        "cau_mau": "Tôi là Mai Anh, giọng phát thanh viên nữ miền Bắc, chuyên đọc bản tin và thông cáo.",
        "icon": "📢",
        "cls": "the-giong__avatar--tintuc"
    },
    "vi_thuc_doan": {
        "id": "vi_thuc_doan",
        "alias": ["Thục Đoan", "thuc doan", "thucdoan", "Thục Đoan (Nữ)"],
        "ten": "Thục Đoan",
        "gioi": "Nữ",
        "vung": "Miền Nam",
        "phong_cach": "Ấm áp · Nam Bộ",
        "dac_trung": "Giọng nữ miền Nam mượt mà, đằm thắm, giàu cảm xúc sông nước",
        "khuyen_dung": "Đọc truyện ngắn Nam Bộ, ký sự đồng bằng, sách tâm lý",
        "cau_mau": "Tôi là Thục Đoan, giọng nữ Nam Bộ ấm áp, phù hợp cho truyện kể và tản văn quê hương.",
        "icon": "🎙️",
        "cls": "the-giong__avatar--doctruyen"
    },
    "vi_minh_triet": {
        "id": "vi_minh_triet",
        "alias": ["Minh Triết", "minh triet", "minhtriet", "Minh Triết (Nam)"],
        "ten": "Minh Triết",
        "gioi": "Nam",
        "vung": "Miền Nam",
        "phong_cach": "Sắc sảo · Bản tin",
        "dac_trung": "Giọng nam miền Nam năng động, sắc sảo, phát âm hiện đại",
        "khuyen_dung": "Tin tức kinh tế, tài chính, khởi nghiệp, công nghệ",
        "cau_mau": "Tôi là Minh Triết, giọng nam miền Nam hiện đại, chuyên đọc tin tức kinh tế và công nghệ.",
        "icon": "📢",
        "cls": "the-giong__avatar--tintuc"
    },
    "vi_thuy_dung": {
        "id": "vi_thuy_dung",
        "alias": ["Thùy Dung", "thuy dung", "thuydung", "Thùy Dung (Nữ)"],
        "ten": "Thùy Dung",
        "gioi": "Nữ",
        "vung": "Miền Nam",
        "phong_cach": "Thời sự · Thuyết trình",
        "dac_trung": "Giọng nữ miền Nam chuẩn mực, giọng vang rõ, lưu loát",
        "khuyen_dung": "Thời sự miền Nam, đọc bài thuyết trình, phóng sự truyền hình",
        "cau_mau": "Tôi là Thùy Dung, giọng nữ thời sự miền Nam, phù hợp đọc tài liệu và thuyết trình.",
        "icon": "📢",
        "cls": "the-giong__avatar--tintuc"
    },
    "vi_quang_son": {
        "id": "vi_quang_son",
        "alias": ["Quang Sơn", "quang son", "quangson", "Quang Sơn (Nam)"],
        "ten": "Quang Sơn",
        "gioi": "Nam",
        "vung": "Miền Trung",
        "phong_cach": "Đậm đà · Miền Trung",
        "dac_trung": "Giọng nam miền Trung hào sảng, chân chất, mang đậm bản sắc vùng miền",
        "khuyen_dung": "Ký sự miền Trung, đọc tư liệu lịch sử, truyện dân gian",
        "cau_mau": "Tôi là Quang Sơn, giọng nam miền Trung đậm đà, phù hợp đọc tư liệu và ký sự quê hương.",
        "icon": "👨",
        "cls": "the-giong__avatar--nam"
    },
    "vi_ngoc_tran": {
        "id": "vi_ngoc_tran",
        "alias": ["Ngọc Trân", "ngoc tran", "ngoctran", "Ngọc Trân (Nữ)"],
        "ten": "Ngọc Trân",
        "gioi": "Nữ",
        "vung": "Miền Trung",
        "phong_cach": "Duyên dáng · Ngọt ngào",
        "dac_trung": "Giọng nữ Huế - Miền Trung ngọt ngào, duyên dáng, âm sắc êm dịu",
        "khuyen_dung": "Đọc thơ ca, tản văn xứ Huế, truyện tình cảm nhẹ nhàng",
        "cau_mau": "Tôi là Ngọc Trân, giọng nữ Huế ngọt ngào, chuyên đọc thơ và tản văn miền Trung.",
        "icon": "👩",
        "cls": "the-giong__avatar--nu"
    },
    "vi_my_duyen": {
        "id": "vi_my_duyen",
        "alias": ["Mỹ Duyên", "my duyen", "myduyen", "Mỹ Duyên (Nữ)"],
        "ten": "Mỹ Duyên",
        "gioi": "Nữ",
        "vung": "Miền Nam",
        "phong_cach": "Tự sự · Truyện dài",
        "dac_trung": "Giọng nữ miền Nam mộc mạc, diễn cảm, giữ nhịp câu chuyện lôi cuốn",
        "khuyen_dung": "Đọc tiểu thuyết dài kỳ, truyện tâm lý xã hội",
        "cau_mau": "Tôi là Mỹ Duyên, giọng nữ miền Nam chuyên đọc tiểu thuyết và truyện dài kỳ.",
        "icon": "🎙️",
        "cls": "the-giong__avatar--doctruyen"
    }
}

# 2. Danh mục chi tiết các giọng riêng tùy chỉnh (Cloned Voices)
DANH_MUC_GIONG_RIENG = {
    "rieng_001": {
        "id": "rieng_001",
        "alias": ["Ngạn kể chuyện", "ngan ke chuyen", "rieng_001"],
        "ten": "Ngạn kể chuyện",
        "gioi": "Nam",
        "vung": "Miền Bắc",
        "phong_cach": "Kiếm hiệp · Cổ trang",
        "dac_trung": "Giọng nam già hào sảng, khí chất phong trần, đậm nét cổ trang dã sử",
        "khuyen_dung": "Chuyên đọc truyện kiếm hiệp, tiểu thuyết võ hiệp, dã sử kịch tính",
        "cau_mau": "Tôi là giọng kể chuyện dã sử cổ trang. Đêm đen như mực, gió rít từng cơn qua khe núi hiểm trở, trận quyết chiến sinh tử sắp sửa bắt đầu.",
        "icon": "⚔️",
        "cls": "the-giong__avatar--kiemhiep"
    },
    "rieng_002": {
        "id": "rieng_002",
        "alias": ["Duy Onyx", "duy onyx", "duyonyx", "rieng_002"],
        "ten": "Duy Onyx",
        "gioi": "Nam",
        "vung": "Miền Bắc",
        "phong_cach": "Review phim · Kịch bản",
        "dac_trung": "Giọng nam Hà Nội trầm ấm, lôi cuốn, nhịp điệu dồn dập hấp dẫn",
        "khuyen_dung": "Chuyên đọc review phim điện ảnh, tóm tắt kịch bản, video recap",
        "cau_mau": "Tôi là Duy Onyx, chuyên đọc review phim và kịch bản lôi cuốn. Một vụ trộm thế kỷ tưởng chừng hoàn hảo, nhưng kẻ chủ mưu đã bị gài bẫy từ đầu.",
        "icon": "🍿",
        "cls": "the-giong__avatar--review"
    },
    "rieng_003": {
        "id": "rieng_003",
        "alias": ["Sách Nói", "sach noi", "sachnoi", "rieng_003"],
        "ten": "Sách Nói",
        "gioi": "Nữ",
        "vung": "Miền Bắc",
        "phong_cach": "Sách nói · Truyền cảm",
        "dac_trung": "Giọng nữ miền Bắc sâu lắng, ấm áp, nhả chữ tinh tế và truyền cảm",
        "khuyen_dung": "Chuyên đọc sách nói nghệ thuật, podcast chữa lành, tản văn tâm sự",
        "cau_mau": "Tôi là giọng đọc sách nói truyền cảm. Có những ngày bình yên đến lạ, khi ta ngồi lắng nghe tiếng mưa rơi nhẹ ngoài hiên.",
        "icon": "☕",
        "cls": "the-giong__avatar--sachnoi"
    },
    "rieng_004": {
        "id": "rieng_004",
        "alias": ["Tin Tức", "tin tuc", "tintuc", "rieng_004"],
        "ten": "Tin Tức",
        "gioi": "Nam",
        "vung": "Miền Bắc",
        "phong_cach": "Tin tức · Dứt khoát",
        "dac_trung": "Giọng nam thanh niên dứt khoát, âm sắc sắc nét, phong thái chuyên nghiệp",
        "khuyen_dung": "Chuyên đọc bản tin thời sự hàng ngày, thông báo, báo cáo tài chính",
        "cau_mau": "Tôi là giọng phát thanh viên tin tức. Kính chào quý vị, sau đây là những diễn biến kinh tế và xã hội đáng chú ý nhất trong ngày.",
        "icon": "📢",
        "cls": "the-giong__avatar--tintuc"
    },
    "rieng_005": {
        "id": "rieng_005",
        "alias": ["Đọc Truyện", "doc truyen", "doctruyen", "rieng_005"],
        "ten": "Đọc Truyện",
        "gioi": "Nam",
        "vung": "Miền Bắc",
        "phong_cach": "Kể chuyện · Sâu lắng",
        "dac_trung": "Giọng nam trẻ trầm ấm, sâu lắng, mang âm hưởng tự sự đêm khuya",
        "khuyen_dung": "Chuyên đọc truyện đêm muộn, tản văn tự sự, câu chuyện cuộc sống",
        "cau_mau": "Tôi là giọng đọc truyện tự sự sâu lắng. Đường phố về đêm tĩnh lặng, những ánh đèn vàng hắt hiu trải dài trên con đường vắng thân quen.",
        "icon": "🎙️",
        "cls": "the-giong__avatar--doctruyen"
    }
}


def _bo_dau(s: str) -> str:
    s = str(s or "").replace("đ", "d").replace("Đ", "D")
    return "".join(c for c in unicodedata.normalize("NFD", s.lower()) if unicodedata.category(c) != "Mn").replace("-", " ").replace("_", " ").strip()


# Ô ID do máy tự cấp (rieng_001, rieng_002...), KHÔNG phải tên người dùng đặt.
_LA_O_ID_RIENG = re.compile(r"^rieng_\d+$", re.I)


def tra_cuu_thong_tin_giong(identifier: str) -> dict:
    """Tra cứu toàn bộ thông tin giàu đặc trưng của giọng theo ID hoặc Tên bất kỳ."""
    raw = str(identifier or "").strip()
    slug = _bo_dau(raw)
    pref = slug.split("(")[0].strip()

    # 1. Tra cứu giọng riêng — CHỈ theo TÊN, không theo ô ID.
    #
    # `_id_giong_rieng_moi()` cấp ID tuần tự rieng_001, rieng_002... nên giọng
    # nhân bản ĐẦU TIÊN của BẤT KỲ ai cũng nhận rieng_001. Khớp theo ID thì thẻ
    # giọng của họ hiện mô tả của người khác, và bấm nghe thử máy đọc to "Tôi là
    # Duy Onyx, chuyên đọc review phim..." — dữ liệu của một máy cụ thể rò sang
    # mọi người dùng.
    #
    # Khớp theo TÊN thì an toàn: ai đặt đúng tên ấy mới ra mô tả ấy. Người dùng
    # đặt "Giọng bà nội" sẽ rơi xuống nhánh mặc định ở cuối hàm — mô tả trung
    # tính, không bịa đặc điểm.
    if not _LA_O_ID_RIENG.match(raw):
        for k, v in DANH_MUC_GIONG_RIENG.items():
            ds_alias = [_bo_dau(a) for a in v["alias"]
                        if not _LA_O_ID_RIENG.match(a)]
            if v["ten"].lower() == raw.lower() or slug in ds_alias:
                return v
        if pref and pref == _bo_dau(v["ten"]).split("(")[0].strip():
            return v

    # 2. Tra cứu giọng VieNeu
    if raw in DANH_MUC_VIENEU:
        return DANH_MUC_VIENEU[raw]
    for k, v in DANH_MUC_VIENEU.items():
        if k == raw or v["ten"].lower() == raw.lower() or slug in [ _bo_dau(a) for a in v["alias"] ]:
            return v
        if pref and pref == _bo_dau(v["ten"]).split("(")[0].strip():
            return v

    # 3. Tra cứu giọng quốc tế chi tiết
    try:
        from src.core.da_ngon_ngu_tts import DS_GIONG_QUOC_TE_CHI_TIET
        for g in DS_GIONG_QUOC_TE_CHI_TIET:
            if g["id"] == raw or g["ten"].lower() == raw.lower():
                is_n = "nữ" in str(g.get("gioi", "")).lower()
                return {
                    "id": g["id"],
                    "ten": g["ten"],
                    "gioi": g.get("gioi", "Nữ" if is_n else "Nam"),
                    "vung": g.get("vung", "Quốc tế"),
                    "phong_cach": f"{g.get('vung', 'Bản xứ')} · Chuẩn quốc tế",
                    "dac_trung": f"Giọng đọc {g.get('gioi', 'bản ngữ')} chuẩn bản xứ {g.get('vung', '')}, phát âm chuẩn xác",
                    "khuyen_dung": f"Học ngoại ngữ, dịch thuật đa ngữ, đọc tài liệu tiếng {g.get('ngon_ngu', 'quốc tế')}",
                    "cau_mau": "Xin chào, đây là giọng đọc bản xứ chuẩn quốc tế bạn vừa chọn.",
                    "icon": "👩" if is_n else "👨",
                    "cls": "the-giong__avatar--nu" if is_n else "the-giong__avatar--nam"
                }
    except Exception:
        pass

    # 4. Fallback mặc định
    is_nu = "nữ" in raw.lower() or "nu" in slug or "female" in slug
    return {
        "id": raw,
        "ten": raw.split("(")[0].strip() or "Giọng đọc",
        "gioi": "Nữ" if is_nu else "Nam",
        "vung": "Toàn quốc",
        "phong_cach": "Tự nhiên · Đa dụng",
        "dac_trung": "Giọng đọc tự nhiên, âm thanh rõ ràng chuẩn studio",
        "khuyen_dung": "Đọc sách, tài liệu, tin tức và văn bản đa thể loại",
        "cau_mau": "Xin chào, đây là giọng đọc bạn vừa chọn. Giọng này đọc tự nhiên, rõ ràng và truyền cảm.",
        "icon": "👩" if is_nu else "👨",
        "cls": "the-giong__avatar--nu" if is_nu else "the-giong__avatar--nam"
    }


def chuan_hoa_id_ky_thuat(identifier: str) -> str:
    """Chuyển đổi mọi tên gọi hiển thị sang đúng ID Kỹ thuật chuẩn ASCII."""
    info = tra_cuu_thong_tin_giong(identifier)
    return info["id"]
