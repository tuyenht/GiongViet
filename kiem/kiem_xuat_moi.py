# -*- coding: utf-8 -*-
"""Kiem duong xuat file cua ban moi. Ghi HOAN TOAN trong thu muc tam.

Khong nap mo hinh VieNeu: thay engine.Speaker bang mot vat gia tra WAV that
(dung bang module wave), nen ghep tep van la ghep that.
"""
import io, re, shutil, sys, tempfile, time, wave
from pathlib import Path


# Goc du an, tinh tu chinh vi tri tep nay. KHONG viet cung duong dan:
# kho da len GitHub, ai tai ve cho khac la vo het bo kiem.
_GOC = str(Path(__file__).resolve().parent.parent)
sys.path.insert(0, _GOC)
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8")

from giaodien_moi import xuat_moi as X

# Bit mieng nhat ky TRUOC KHI chay bat cu phep kiem nao. Phep kiem O co tinh
# lam ffmpeg hong de xem co giu duoc ban WAV khong, va moi lan nhu the
# xuat_moi goi nhat_ky.ghi_loi -> ghi thang vao GiongViet-loi.log THAT o thu
# muc du an. Da xay ra: 10 dong rac trong nhat ky, va tai suyt ket luan nham
# la chuong trinh co loi. Quy tac du an: bo kiem khong duoc dung vao du lieu
# hay nhat ky that.
X.nhat_ky.ghi_loi = lambda *a, **k: None

T = Path(tempfile.gettempdir()) / "gd-kiem-xuat"
if T.exists():
    shutil.rmtree(T)
T.mkdir(parents=True)

loi = 0
def ok(dk, nhan, them=""):
    global loi
    print(f"  {'ĐẠT ' if dk else 'LỆCH'} {nhan}{'  →  ' + str(them) if them else ''}")
    if not dk:
        loi += 1


def wav_gia(giay=0.2):
    """WAV 16 bit / 1 kenh / 48.000 Hz — dung dinh dang VieNeu tra ve."""
    buf = io.BytesIO()
    with wave.open(buf, "wb") as w:
        w.setnchannels(1)
        w.setsampwidth(2)
        w.setframerate(48000)
        w.writeframes(b"\0\0" * int(48000 * giay))
    return buf.getvalue()


class SpeakerGia:
    """Vat gia cho engine.Speaker.

    PHAI tu chung minh du giong that: phep kiem I doi chieu moi thuoc tinh
    ma xuat_moi.py go vao `speaker.` voi thuoc tinh cua lop nay. Da vap that
    — SpeakerGia thieu `_cache` tung lam mot phep kiem so None voi None roi
    bao xanh gia.
    """
    # Tong hop that co the mat toi 40 giay mot cau. Phep kiem G keo CHAM len
    # de dung lai dung tinh huong ay: nguoi dung bam Huy trong luc luong con
    # dang dung ket trong VieNeu.
    CHAM = 0.0

    def __init__(self, cfg):
        self.cfg = cfg
        self._cache = {}
        self.da_tat = False
        self.cham = SpeakerGia.CHAM

    def get_audio(self, khoa, text, khuech_dai=1.0):
        if self.cham:
            time.sleep(self.cham)
        return wav_gia(), 0.2

    def shutdown(self):
        self.da_tat = True


class EngineGia:
    Speaker = SpeakerGia


X.engine = EngineGia
CFG = {"ffplay": T / "ffmpeg" / "bin" / "ffplay.exe"}


def playlist(n):
    return [{"text": f"cau so {i}", "nghi": 0.0, "khuech_dai": 1.0} for i in range(n)]


def chay(bo, pl, doan_cua_mau, ten, tach="mot", dinh_dang="wav16", cho=20):
    bo.bat_dau(pl, doan_cua_mau, CFG, ten, str(T), tach, dinh_dang)
    bo._worker.join(cho)
    return not bo._worker.is_alive()


class Hung:
    def __init__(self):
        self.tien_do, self.xong, self.loi, self.huy = [], [], [], []

    def bo(self):
        return X.BoXuatMoi(self.tien_do.append, self.xong.append,
                           self.loi.append, lambda: self.huy.append(1))


print("--- A. Chia nhom theo ba kieu tach ---")
h = Hung(); b = h.bo()
pl6 = playlist(6)
doan6 = [1, 1, 2, 2, 3, 3]
ok(len(b._nhom(pl6, doan6, "mot")) == 1, "mot tep duy nhat -> 1 nhom")
ok(len(b._nhom(pl6, doan6, "moi-doan")) == 3, "moi doan mot tep -> 3 nhom",
   len(b._nhom(pl6, doan6, "moi-doan")))
ok(sum(len(x) for x in b._nhom(pl6, doan6, "moi-doan")) == 6,
   "khong lam roi mau nao khi chia theo doan")
dai = [{"text": "x" * 9000, "nghi": 0.0} for _ in range(4)]
ok(len(b._nhom(dai, [1, 2, 3, 4], "do-dai")) >= 2,
   "van ban dai -> cat theo 10 phut ra nhieu tep",
   len(b._nhom(dai, [1, 2, 3, 4], "do-dai")))
ok(len(b._nhom(pl6, doan6, "do-dai")) == 1,
   "van ban ngan -> chua toi 10 phut nen khong cat")

print("\n--- B. Ba dong uoc tinh ---")
u = X.uoc_tinh(pl6, 3)
ok(u["mot"].startswith("Ước tính: 1 tệp"), "dong 'mot' dung dang", u["mot"])
ok("3 tệp" in u["moi-doan"], "dong 'moi-doan' dem dung so doan", u["moi-doan"])
ok("chưa tới 10 phút" in u["do-dai"], "van ban ngan -> bao khong cat", u["do-dai"])
ok(u["goiY"]["moi-doan"] == "3 tệp", "goi y ben canh nut tron", u["goiY"])

print("\n--- C. Xuat that ra tep WAV, khong phai dong ho gia ---")
h = Hung(); b = h.bo()
xong = chay(b, playlist(5), [1, 2, 3, 4, 5], "thongbao")
ok(xong, "luong ket thuc")
tep = T / "thongbao.wav"
ok(tep.exists(), "co tep that tren dia", tep.name)
ok(tep.stat().st_size > 1000, "tep co noi dung", format(tep.stat().st_size, ","))
with wave.open(str(tep), "rb") as w:
    giay = w.getnframes() / w.getframerate()
ok(abs(giay - 1.0) < 0.05, "ghep du 5 mau x 0,2 giay", round(giay, 3))
ok(len(h.xong) == 1 and not h.loi, "bao xong dung mot lan", h.xong[:1])
ok(h.xong[0]["kichThuoc"] and h.xong[0]["thoiLuong"],
   "so lieu tra ve co that", h.xong[0].get("kichThuoc"))

print("\n--- D. Tien do co du bon so lieu man 2 ---")
ok(len(h.tien_do) == 5, "moi mau mot lan bao tien do", len(h.tien_do))
can = {"phanTram", "moTa", "troiQua", "conLai", "daGhi"}
thieu = can - set(h.tien_do[-1])
ok(not thieu, "goi tien do du khoa cho giai doan 2", thieu or "du")
ok(h.tien_do[-1]["phanTram"] == 100, "mau cuoi la 100%", h.tien_do[-1]["phanTram"])
ok(h.tien_do[-1]["daGhi"] != h.tien_do[0]["daGhi"],
   "so byte da ghi tang dan, khong phai so bia",
   (h.tien_do[0]["daGhi"], h.tien_do[-1]["daGhi"]))

print("\n--- E. Tach 'moi doan' de ra dung so tep ---")
h = Hung(); b = h.bo()
chay(b, playlist(4), [1, 1, 2, 3], "nhieu", tach="moi-doan")
ds = sorted(p.name for p in T.glob("nhieu-*.wav"))
ok(len(ds) == 3, "3 doan -> 3 tep", ds)

print("\n--- F. KHONG ghi de tep nguoi dung da co ---")
(T / "trung.wav").write_bytes(b"BAN GOC CUA NGUOI DUNG")
h = Hung(); b = h.bo()
chay(b, playlist(2), [1, 2], "trung")
ok((T / "trung.wav").read_bytes() == b"BAN GOC CUA NGUOI DUNG",
   "ban goc con nguyen tung byte")
ok((T / "trung (1).wav").exists(), "ne sang 'trung (1).wav' kieu Explorer")

print("\n--- G. SO PHIEN: huy giua chung thi luong cu phai im hang ---")
SpeakerGia.CHAM = 0.25          # moi mau 0,25 giay -> huy kip luc dang tong hop
h = Hung(); b = h.bo()
b.bat_dau(playlist(6), [1] * 6, CFG, "huygiua", str(T), "mot", "wav16")
time.sleep(0.1)                 # dang ket trong get_audio cua mau dau
b.huy()
b._worker.join(20)
ok(not b._worker.is_alive(), "luong dung han")
ok(not h.xong, "KHONG bao xong sau khi huy", h.xong)
ok(len(h.huy) == 1, "bao huy dung mot lan", len(h.huy))
ok(len(h.tien_do) <= 1, "dung ngay sau mau dang do, khong chay het 6 mau",
   len(h.tien_do))

tep_huy = T / "huygiua.wav"
co_truoc = tep_huy.stat().st_size if tep_huy.exists() else 0
so_tien_do = len(h.tien_do)
time.sleep(0.6)                 # du lau de luong cu chay not neu no con song
ok(len(h.tien_do) == so_tien_do, "luong cu khong day them tien do nao nua")
co_sau = tep_huy.stat().st_size if tep_huy.exists() else 0
ok(co_sau == co_truoc, "tep KHONG phinh them sau khi da huy", (co_truoc, co_sau))
SpeakerGia.CHAM = 0.0

print("\n--- H. Phien moi de len phien cu: phien cu khong duoc bao gi ---")
h = Hung(); b = h.bo()
b._phien = 7
b._bao_huy(3)
ok(not h.huy, "phien cu (3) goi bao huy -> bi bo qua", h.huy)
b._bao_tien_do(3, 1, 5, time.time(), 100)
ok(not h.tien_do, "phien cu day tien do -> bi bo qua", h.tien_do)
ok(not b._con_hieu_luc(3) and b._con_hieu_luc(7), "chi phien hien hanh con hieu luc")

print("\n--- I. Vat gia du giong that (khong so None voi None) ---")
nguon = Path(_GOC + r"\giaodien_moi\xuat_moi.py").read_text(encoding="utf-8")
goi = set(re.findall(r"speaker\.(\w+)", nguon))
thieu = {g for g in goi if not hasattr(SpeakerGia(CFG), g)}
ok(not thieu, f"SpeakerGia co du {len(goi)} thu xuat_moi go vao", thieu or sorted(goi))
ok(hasattr(SpeakerGia(CFG), "_cache"), "co _cache — dung cai tung lam xanh gia")

print("\n--- J. Bang dinh dang: chi wav16 khoi can ffmpeg ---")
ok(X.DINH_DANG["wav16"]["ma"] is None, "wav16 ghi thang")
ok(X.DINH_DANG["wav24"]["ma"] and X.DINH_DANG["mp3-320"]["ma"],
   "wav24 va mp3 deu phai qua ffmpeg")
ok(X.DINH_DANG["mp3-320"]["duoi"] == ".mp3", "mp3 dung duoi .mp3")
ok("320k" in X.DINH_DANG["mp3-320"]["ma"] and "128k" in X.DINH_DANG["mp3-128"]["ma"],
   "hai muc mp3 dat dung bitrate")
ok(X.duong_ffmpeg(CFG).name == "ffmpeg.exe"
   and X.duong_ffmpeg(CFG).parent == CFG["ffplay"].parent,
   "ffmpeg tim canh ffplay, khong do lai tu dau", X.duong_ffmpeg(CFG))

print("\n--- K. Cau goi nguoc: window.gd phai co du bon duong xuat ---")
js = Path(_GOC + r"\ui-moi\cau-noi.js").read_text(encoding="utf-8")
for ten in ["tienDoXuat", "xuatXong", "xuatLoi", "xuatHuy"]:
    ok(re.search(r"^\s*" + ten + r"\s*\(", js, re.M) is not None,
       f"window.gd.{ten} co that")
py = Path(_GOC + r"\giaodien\cau_noi.py").read_text(encoding="utf-8")
goi_py = set(re.findall(r"window\.gd\.(\w+)", py))
thieu_js = {g for g in goi_py if not re.search(r"^\s*" + g + r"\s*\(", js, re.M)}
ok(not thieu_js, f"khong ham nao Python goi ma JS thieu ({len(goi_py)} ham)",
   thieu_js or sorted(goi_py))

print("\n--- L. Nut Xuat khong con la nut gia ---")
gd = Path(_GOC + r"\ui-moi\giao-dien.js").read_text(encoding="utf-8")
ok("moi_bat_dau_xuat" in gd, "co goi sang Python de xuat that")
ok("moi_huy_xuat" in gd, "co duong huy")
ok(gd.count("'11,6 MB'") <= 1,
   "khong con dung luong bia trong duong Python", gd.count("'11,6 MB'"))
# Cat dung THAN ham batDauXuat (toi dau ngoac dong o cot 0), roi doi chieu THU TU
# hai moc trong do. Truoc day cho canh la "nam trong 800 ky tu dau" — mot cua so
# CUNG, nen them may dong chu thich vao dau ham la do, du ma nguon dung hon truoc.
# Da xay ra that: L1 chen khoi chu thich giai thich vi sao phai ep gui, day loi goi
# ra moc 901, va bai nay do 101 ky tu vi ly do chang lien quan gi toi nut gia.
def than_ham_js(nguon, mo_dau):
    """Than mot ham JS, cat bang cach DEM NGOAC chu khong bang dinh dang.

    Cach cu cat toi chuoi "\\n}\\n" - tuc la trong vao mot dau ngoac dong nam
    dung cot 0. Ai bo ham vao mot khoi khac, hay dat ngoac dong o cho khac, la
    cua so co lai con vai ky tu va phep canh xanh gia; con mot refactor lanh
    manh thi do. Dem ngoac thi khong phu thuoc cach trinh bay.
    """
    i = nguon.find(mo_dau)
    if i < 0:
        return ""
    j = nguon.find("{", i)
    if j < 0:
        return ""
    sau = 0
    for k in range(j, len(nguon)):
        c = nguon[k]
        if c == "{":
            sau += 1
        elif c == "}":
            sau -= 1
            if sau == 0:
                return nguon[i:k + 1]
    return nguon[i:]


than = than_ham_js(gd, "async function batDauXuat")
ok(len(than) > 0, "cat duoc than ham batDauXuat")
i_goi = than.find("api('moi_bat_dau_xuat'")
i_man = than.find("exporting: true")
ok(i_goi >= 0, "batDauXuat co goi Python that trong than ham")
ok(i_man >= 0, "batDauXuat co mo man tien do")
ok(0 <= i_goi < i_man, "goi Python TRUOC khi mo man tien do, khong ve san man rong",
   f"goi o {i_goi}, mo man o {i_man}")

print("\n--- M. MP3 va WAV 24 bit chay THAT bang ffmpeg cua du an ---")
ff = Path(_GOC + r"\ffmpeg\bin\ffmpeg.exe")
if not ff.exists():
    print("  BO QUA — khong thay", ff)
else:
    cfg_that = {"ffplay": ff.parent / "ffplay.exe"}
    goc_cfg = CFG["ffplay"]
    CFG["ffplay"] = cfg_that["ffplay"]
    for ma, duoi in [("mp3-128", ".mp3"), ("wav24", ".wav")]:
        h = Hung(); b = h.bo()
        chay(b, playlist(3), [1, 2, 3], "ma-" + ma, dinh_dang=ma, cho=60)
        tep = T / ("ma-" + ma + duoi)
        ok(tep.exists() and tep.stat().st_size > 500,
           f"{ma} de ra tep that", tep.name if tep.exists() else "KHONG CO")
        ok(not h.loi, f"{ma} khong bao loi", h.loi)
        ok(not list(T.glob("*.goc.wav")), f"{ma} don sach tep tam WAV")
    with wave.open(str(T / "ma-wav24.wav"), "rb") as w:
        ok(w.getsampwidth() == 3, "WAV 24 bit dung la 24 bit that",
           f"{w.getsampwidth() * 8} bit")
    dau = (T / "ma-mp3-128.mp3").read_bytes()[:3]
    ok(dau in (b"ID3", b"\xff\xfb", b"\xff\xf3"), "tep mp3 dung dinh dang MP3",
       dau.hex())
    CFG["ffplay"] = goc_cfg

print("\n--- N. Huy GIUA CHUNG khong de lai tep cut tren dia ---")
# Khac phep kiem G: lan nay huy SAU khi mau dau da ghi xong, nen da co tep
# that nam do. Nguoi lon tuoi nhin mot tep cut khong phan biet duoc voi ban
# xuat thanh cong - ho mo ra nghe duoc nua bai roi tuong phan mem hong.
SpeakerGia.CHAM = 0.2
h = Hung(); b = h.bo()
b.bat_dau(playlist(8), [1] * 8, CFG, "cutgiua", str(T), "mot", "wav16")
time.sleep(0.5)                 # du cho 1-2 mau ghi xong
# Trong luc ghi, tep phai mang duoi .dangxuat CHU KHONG PHAI .wav: dong cua so
# giua chung thi luong daemon chet ngang, khong ai don duoc, nen thu con lai
# tren dia phai la thu nguoi dung khong the nham voi ban xuat that.
dang_ghi = (T / ("cutgiua.wav" + X.DUOI_DANG_XUAT)).exists()
chua_co_ten_that = not (T / "cutgiua.wav").exists()
b.huy()
b._worker.join(20)
SpeakerGia.CHAM = 0.0
ok(dang_ghi, "dang ghi thi tep mang duoi .dangxuat (dung tinh huong can kiem)")
ok(chua_co_ten_that, "CHUA co tep mang ten that luc con dang ghi")
ok(not list(T.glob("cutgiua*")),
   "huy xong khong con manh nao, ke ca .dangxuat",
   [p.name for p in T.glob("cutgiua*")])
ok(len(h.huy) == 1 and not h.xong, "van bao huy dung mot lan")

print("\n--- O. ffmpeg hong thi GIU LAI ban WAV, khong vut hang phut tong hop ---")
h = Hung(); b = h.bo()
goc_cfg = CFG["ffplay"]
CFG["ffplay"] = T / "khong-co-that" / "ffplay.exe"    # -> ffmpeg.exe khong ton tai
chay(b, playlist(3), [1, 2, 3], "ffhong", dinh_dang="mp3-320")
CFG["ffplay"] = goc_cfg
con = sorted(p.name for p in T.glob("ffhong*"))
ok(any(n.endswith(".wav") for n in con),
   "ban WAV van con, cong tong hop khong mat", con)
ok(len(h.xong) == 1, "van bao XONG chu khong bao loi cut ngang", h.xong[:1])
ok(bool(h.xong) and h.xong[0]["ten"].endswith(".wav"),
   "bao dung ten tep that su co tren dia",
   h.xong[0]["ten"] if h.xong else "")

print("\n--- P. Tep tam .goc.wav cua nguoi dung KHONG bi de ---")
ff = Path(_GOC + r"\ffmpeg\bin\ffmpeg.exe")
if not ff.exists():
    print("  BO QUA — khong co ffmpeg")
else:
    CFG["ffplay"] = ff.parent / "ffplay.exe"
    (T / "detam.goc.wav").write_bytes(b"BAN GOC WAV CUA NGUOI DUNG")
    h = Hung(); b = h.bo()
    chay(b, playlist(2), [1, 2], "detam", dinh_dang="mp3-128", cho=60)
    ok((T / "detam.goc.wav").read_bytes() == b"BAN GOC WAV CUA NGUOI DUNG",
       "tep .goc.wav san co con nguyen tung byte")
    ok((T / "detam.mp3").exists(), "van xuat ra mp3 binh thuong")
    CFG["ffplay"] = goc_cfg

print("\n" + ("XANH — khớp hết" if not loi else f"ĐỎ — {loi} chỗ lệch"))
sys.exit(1 if loi else 0)
