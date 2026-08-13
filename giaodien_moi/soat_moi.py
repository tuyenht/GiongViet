# -*- coding: utf-8 -*-
"""Dữ liệu cho màn hình 2 — Soát văn bản.

Bê nguyên phần khó từ giaodien/soat.py: nó đã biết tìm chữ viết tắt chưa dạy
máy đọc, ký tự máy đọc trẹo, số tiền không hiểu được. Ở đây chỉ đổi cách ĐẾM:
bản cũ đếm theo dòng trong tệp, giao diện mới đếm theo ĐOẠN.

Hai tab, hai nguồn số liệu khác nhau:
  tab 1  giaodien/soat.py  — những chỗ máy sẽ đọc sai
  tab 2  chính playlist    — văn bản gốc so với chuỗi engine thật sẽ đọc

Tab 2 KHÔNG tự dựng lại chuỗi đọc: nó lấy đúng `goc` và `text` mà
ApiMoi._dung_playlist đã sinh ra. Dựng lại là có ngày hai bên lệch nhau, và
lúc đó màn soát sẽ nói dối - hứa máy đọc một đằng, loa đọc một nẻo.
"""

import re

from giaodien import soat

# Bốn nhóm quy tắc trong đặc tả. `congTac` là khoá trong cấu hình - có khoá
# thì người dùng bật tắt được thật, không có thì CHỈ ĐẾM chứ không bày nút.
#
# Cố ý không làm nút cho hai nhóm cuối: engine chuẩn hoá ngày tháng và dấu câu
# lặp không qua công tắc nào cả. Bày ra một cái nút bấm không đổi gì là đúng
# thứ KPI dự án cấm.
QUY_TAC = [
    {"ma": "so", "ten": "Số thành chữ", "congTac": "doc_so_bang_chu"},
    {"ma": "kyhieu", "ten": "Viết tắt, ký hiệu", "congTac": "bo_markdown"},
    {"ma": "ngay", "ten": "Ngày tháng", "congTac": None},
    {"ma": "daucau", "ten": "Bỏ dấu câu lặp", "congTac": None},
]

_SO = re.compile(r"\d")
_NGAY = re.compile(r"\b\d{1,2}\s*[/-]\s*\d{1,2}(\s*[/-]\s*\d{2,4})?\b")
_DAU_LAP = re.compile(r"([.,;:!?…])\1+|\.{2,}|-{2,}")
_VIET_TAT = re.compile(r"(?<![0-9A-Za-zÀ-ỹĐđ])([A-ZĐ]{2,})(?![0-9a-zà-ỹ])")


def _dem_quy_tac(doan: list, tudien: dict) -> list:
    """Mỗi nhóm quy tắc chạm vào bao nhiêu chỗ trong văn bản này."""
    chu = "\n".join(str(d.get("chu", "")) for d in doan or [])
    dem = {
        "so": sum(1 for t in chu.split() if _SO.search(t)),
        "kyhieu": len([t for t in _VIET_TAT.findall(chu) if t in (tudien or {})]),
        "ngay": len(_NGAY.findall(chu)),
        "daucau": len(_DAU_LAP.findall(chu)),
    }
    return dem


def chu_y(doan: list, tudien: dict) -> dict:
    """Tab 1 — những chỗ máy sẽ đọc sai, đếm theo ĐOẠN.

    soat.soat_van_ban đánh số theo dòng, mà mỗi đoạn ở đây đúng là một dòng
    nên hai con số trùng nhau - miễn là ghép lại bằng đúng ký tự xuống dòng.
    """
    doan = list(doan or [])
    if not any(str(d.get("chu", "")).strip() for d in doan):
        return {"vanDe": [], "nang": 0, "nhe": 0, "moTa": "", "trong": True}

    van_ban = "\n".join(str(d.get("chu", "")) for d in doan)
    van_de = soat.gop_trung(soat.soat_van_ban(van_ban, tudien or {}))
    van_de.sort(key=lambda v: (v["muc"] != soat.MUC_NANG, v["dong"]))
    for v in van_de:
        v["doan"] = v.get("dong", 0)
    co_chu = sum(1 for d in doan if str(d.get("chu", "")).strip())
    return {
        "vanDe": van_de,
        "nang": sum(1 for v in van_de if v["muc"] == soat.MUC_NANG),
        "nhe": sum(1 for v in van_de if v["muc"] == soat.MUC_NHE),
        "moTa": f"{co_chu} đoạn có chữ",
        "trong": False,
    }


def chuan_hoa(doan: list, playlist: list, doan_cua_mau: list) -> dict:
    """Tab 2 — văn bản gốc so với chuỗi engine THẬT sẽ đọc.

    Một đoạn dài bị cắt thành nhiều mẩu, nên phải gom các mẩu của cùng một
    đoạn lại rồi mới so. Lấy thẳng `text` mà playlist đang giữ chứ không
    chuẩn hoá lại lần nữa.
    """
    gom = {}
    for i, seg in enumerate(playlist or []):
        n = doan_cua_mau[i] if i < len(doan_cua_mau or []) else 0
        if n:
            gom.setdefault(n, []).append(str(seg.get("text", "")).strip())

    dong, so_doi = [], 0
    for n, d in enumerate(doan or [], 1):
        goc = str(d.get("chu", "")).strip()
        if not goc:
            continue
        doc = " ".join(x for x in gom.get(n, []) if x)
        khac = " ".join(goc.split()) != " ".join(doc.split())
        so_doi += 1 if khac else 0
        dong.append({"doan": n, "goc": goc, "doc": doc, "doi": khac})

    return {"dong": dong, "soDoi": so_doi,
            "tomTat": f"{so_doi} chỗ sẽ được đọc khác văn bản gốc · "
                      f"{len(dong)} đoạn"}


def du_lieu(doan: list, playlist: list, doan_cua_mau: list, tudien: dict,
            cfg: dict) -> dict:
    dem = _dem_quy_tac(doan, tudien)
    quy_tac = []
    for q in QUY_TAC:
        cong_tac = q["congTac"]
        quy_tac.append({
            "ma": q["ma"],
            "ten": q["ten"],
            "so": dem.get(q["ma"], 0),
            # Bật/tắt được thì giao diện mới cho bấm. Không có công tắc thật
            # thì `doiDuoc` = False và nó chỉ là con số, không phải cái nút.
            "bat": bool((cfg or {}).get(cong_tac, True)) if cong_tac else True,
            "doiDuoc": bool(cong_tac),
            "khoa": cong_tac or "",
        })
    return {
        "chuY": chu_y(doan, tudien),
        "chuanHoa": chuan_hoa(doan, playlist, doan_cua_mau),
        "quyTac": quy_tac,
    }
