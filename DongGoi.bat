@echo off
setlocal EnableExtensions
cd /d "%~dp0"

echo =========================================
echo   DONG GOI GIONGDOC BAN MOI (thu nghiem)
echo =========================================
echo.
echo KHAC DongGoi.bat mot diem QUAN TRONG:
echo   DongGoi.bat chep de vao THU MUC GOC (xoa _internal cu roi robocopy).
echo   Ban nay build vao thu muc RIENG GiongViet\ va KHONG dung gi o goc,
echo   nen ban cu anh dang dung hang ngay van nguyen ven.
echo.
echo Dat GIONGDOC_TU_DONG=1 truoc khi goi de bo qua pause:
echo   set GIONGDOC_TU_DONG=1 ^&^& DongGoi.bat
echo.

set "ROOT=%~dp0"
set "DICH=%ROOT%GiongViet"
set "BUILD_DIR=%ROOT%_build_moi"
set "SPEC_DIR=%ROOT%_spec_moi"

where py >nul 2>nul
if errorlevel 1 (
    echo [LOI] Khong tim thay Python.
    goto :fail
)
if not exist "%ROOT%GiongViet.py" (
    echo [LOI] Khong tim thay GiongViet.py.
    goto :fail
)
if not exist "%ROOT%src\web\index.html" (
    if not exist "%ROOT%ui-moi\index.html" (
        echo [LOI] Khong tim thay giao dien web.
        goto :fail
    )
)
rem ffmpeg va mo hinh VieNeu KHONG nam trong kho git - chung nang ~530 MB va
rem co tep vuot gioi han 100 MB cua GitHub. Nguoi clone kho ve chay thang
rem file nay thi phai tu tai duoc, khong duoc dung lai bat nguoi ta di tim.
rem Engine da co san hai nhanh dong lenh cho dung viec nay.
set "CO_FFMPEG="
if exist "%ROOT%bin\ffmpeg\bin\ffplay.exe" (
    if exist "%ROOT%bin\ffmpeg\bin\ffmpeg.exe" set "CO_FFMPEG=1"
)
if exist "%ROOT%ffmpeg\bin\ffplay.exe" (
    if exist "%ROOT%ffmpeg\bin\ffmpeg.exe" set "CO_FFMPEG=1"
)

if not defined CO_FFMPEG (
    echo [!] Chua co ffmpeg - dang tu dong tai ve...
    py "%ROOT%DocCongDuc.py" --tai-ffmpeg
)

set "CO_MODELS="
if exist "%ROOT%models\vieneu" set "CO_MODELS=1"
if exist "%ROOT%vieneu_models" set "CO_MODELS=1"

if not defined CO_MODELS (
    echo [!] Chua co mo hinh VieNeu - dang tu dong tai ve ^(vai tram MB^)...
    py "%ROOT%DocCongDuc.py" --tai-vieneu
)

echo [1/5] Don thu muc build cu...
rem KHONG xoa %DICH% o day. Ban truoc xoa ngay buoc nay, nen moi lan build dut
rem ganh la mat luon ban .exe dang chay duoc - da xay ra nhieu lan. Ban moi chi
rem dung toi %DICH% o buoc 4, sau khi da build xong VA kiem du 3 tep mau chot.
if exist "%BUILD_DIR%"       rmdir /s /q "%BUILD_DIR%"
if exist "%SPEC_DIR%"        rmdir /s /q "%SPEC_DIR%"
if exist "%ROOT%_dist_moi"   rmdir /s /q "%ROOT%_dist_moi"
mkdir "%BUILD_DIR%"
mkdir "%SPEC_DIR%"

echo.
echo [2/5] Dang dong goi ^(10-20 phut^)...
rem --collect-data la BAT BUOC, y het ban cu:
rem   vieneu   -> assets\voices_v3_turbo.json, thieu thi danh sach giong RONG
rem   sea_g2p  -> sea_g2p.bin (61 MB), thieu thi "os error 2" dung luc bam doc
rem
rem --add-data ui-moi la thu ban cu KHONG co. Thieu no thi cua so mo ra trang
rem tron - dung ho loi "thieu tep du lieu khi dong goi" da vap.
rem
rem hidden-import giaodien_moi.*: GiongViet.py import ApiMoi ben trong ham
rem main(), PyInstaller co the tu tim thay hoac khong. Liet ke ra cho chac -
rem cung dung cach ban cu lam voi giaodien.*.
rem
rem Nam module src.core them sau khi doi cay thu muc (chuan_hoa_am_thanh,
rem danh_muc_giong, da_ngon_ngu_tts, dich_thuat, kho_cau_hinh) deu duoc import
rem LUOI - trong than ham - nen cung thuoc dien "co the tu tim thay hoac khong".
rem CO Y bo qua chuyen_mau_giong va kiem_dinh_1_1: ca hai khong co mot loi goi
rem nao trong ma san pham, liet ke vao la ngam bao chung dang duoc dung.
rem
rem edge_tts la thu vien tong hop tieng ngoai ngu, da_ngon_ngu_tts import no o
rem tang module. Khong co tep du lieu nao (chi py.typed) nen khong can
rem --collect-data, nhung thieu hidden-import thi bam doc ngoai ngu la vo.
py -m PyInstaller --noconfirm --onedir --windowed --name GiongViet ^
    --add-data "%ROOT%src\web;web" ^
    --add-data "%ROOT%src\web;ui-moi" ^
    --collect-data vieneu ^
    --collect-data sea_g2p ^
    --hidden-import src.paths ^
    --hidden-import src.core.cau_noi --hidden-import src.core.bo_doc ^
    --hidden-import src.core.ds_giong --hidden-import src.core.du_lieu ^
    --hidden-import src.core.he_thong --hidden-import src.core.mo_hinh ^
    --hidden-import src.core.nghe_thu --hidden-import src.core.nhat_ky ^
    --hidden-import src.core.thu_vien_giong --hidden-import src.core.xuat_file ^
    --hidden-import src.core.ho_so --hidden-import src.core.soat ^
    --hidden-import src.core.tu_dien --hidden-import src.core.cai_dat ^
    --hidden-import src.core.bo_dieu_phoi_ngu_canh --hidden-import src.core.bo_chuyen_ngu_khoa_hoc ^
    --hidden-import src.core.chuan_hoa_am_thanh --hidden-import src.core.danh_muc_giong ^
    --hidden-import src.core.da_ngon_ngu_tts --hidden-import src.core.dich_thuat ^
    --hidden-import src.core.kho_cau_hinh --hidden-import edge_tts ^
    --hidden-import src.app.cau_noi_moi --hidden-import src.app.khoa_du_lieu ^
    --hidden-import src.app.ho_so_v2 --hidden-import src.app.luu_tep ^
    --hidden-import src.app.so_dien_thoai --hidden-import src.app.sdt_mau ^
    --hidden-import src.app.sdt_nhip --hidden-import src.app.am_thanh_loc ^
    --hidden-import src.app.soat_moi --hidden-import src.app.xuat_moi ^
    --hidden-import giaodien.cau_noi --hidden-import giaodien.bo_doc ^
    --hidden-import giaodien.ds_giong --hidden-import giaodien.du_lieu ^
    --hidden-import giaodien.he_thong --hidden-import giaodien.mo_hinh ^
    --hidden-import giaodien.nghe_thu --hidden-import giaodien.nhat_ky ^
    --hidden-import giaodien.thu_vien_giong --hidden-import giaodien.xuat_file ^
    --hidden-import giaodien.ho_so --hidden-import giaodien.soat ^
    --hidden-import giaodien.tu_dien --hidden-import giaodien.cai_dat ^
    --hidden-import giaodien.bo_dieu_phoi_ngu_canh --hidden-import giaodien.bo_chuyen_ngu_khoa_hoc ^
    --hidden-import giaodien_moi.cau_noi_moi --hidden-import giaodien_moi.khoa_du_lieu ^
    --hidden-import giaodien_moi.ho_so_v2 --hidden-import giaodien_moi.luu_tep ^
    --hidden-import giaodien_moi.so_dien_thoai --hidden-import giaodien_moi.sdt_mau ^
    --hidden-import giaodien_moi.sdt_nhip --hidden-import giaodien_moi.am_thanh_loc ^
    --hidden-import giaodien_moi.soat_moi --hidden-import giaodien_moi.xuat_moi ^
    --hidden-import kho_cau_hinh ^
    --distpath "%ROOT%_dist_moi" --workpath "%BUILD_DIR%" --specpath "%SPEC_DIR%" ^
    "%ROOT%GiongViet.py"
if errorlevel 1 goto :fail

echo.
echo [3/5] Kiem 3 tep mau chot + phan rieng cua ban moi...
set "B=%ROOT%_dist_moi\GiongViet\_internal"
if not exist "%ROOT%_dist_moi\GiongViet\GiongViet.exe" (
    echo [LOI] PyInstaller khong tao duoc EXE.
    goto :fail
)
if not exist "%B%\web\index.html" (
    if not exist "%B%\ui-moi\index.html" (
        echo [LOI] Thieu index.html giao dien - cua so se mo ra trang trong.
        goto :fail
    )
)
if not exist "%B%\sea_g2p\sea_g2p.bin" (
    echo [LOI] Thieu sea_g2p.bin - bam doc se bao "os error 2".
    goto :fail
)
if not exist "%B%\vieneu\assets\voices_v3_turbo.json" (
    echo [LOI] Thieu voices_v3_turbo.json - danh sach giong se RONG.
    goto :fail
)
echo   OK: web\index.html
echo   OK: sea_g2p\sea_g2p.bin
echo   OK: vieneu\assets\voices_v3_turbo.json

echo.
echo [4/5] Dua ban build ra %DICH% va noi du lieu dung chung...
rem Ban cu chi bi dung toi o day - build da xong va da kiem du 3 tep mau chot.
rem Doi TEN chu khong xoa: move that bai thi con duong lui.
rem
rem Go junction TRUOC khi don ban cu. rmdir /s khong di theo junction, nhung
rem ffmpeg va vieneu_models nang vai GB va nam ngoai git - khong danh cuoc vao
rem mot hanh vi cua he dieu hanh khi cai gia la phai tai lai tu dau.
set "CU=%DICH%_cu"
set "CUU=%ROOT%_cuu_dulieu"
if exist "%CU%" rmdir /s /q "%CU%"

rem CUU DU LIEU NGUOI DUNG TRUOC KHI GO JUNCTION.
rem Vong go junction ngay duoi xoa ca thu muc data\, ma giongviet.db - noi THAT
rem SU giu thiet lap sau khi gom - nam trong do. Truoc ban va nay, moi lan build
rem la thiet lap nguoi dung bien mat khong mot loi bao: vong cuu o cuoi tep di
rem tim no trong %CU%\data, ma thu muc ay da bi xoa tu truoc do roi.
rem Chi cuu TEP. giong_rieng la junction nen khong dung toi - rmdir khong di theo.
if exist "%CUU%" rmdir /s /q "%CUU%"
if exist "%DICH%\data" (
    if not exist "%CUU%" mkdir "%CUU%"
    for %%F in ("%DICH%\data\*.db" "%DICH%\data\*.txt" "%DICH%\data\*.json" "%DICH%\data\*.ini") do (
        if exist "%%~fF" copy /Y "%%~fF" "%CUU%\" >nul
    )
    if exist "%DICH%\data\mau_google_sheets" xcopy /E /I /Y /Q "%DICH%\data\mau_google_sheets" "%CUU%\mau_google_sheets" >nul
)

if exist "%DICH%" (
    for %%L in (ffmpeg vieneu_models giong_rieng bin models data) do (
        if exist "%DICH%\%%L" rmdir /s /q "%DICH%\%%L" 2>nul
    )
    move "%DICH%" "%CU%" >nul
    if errorlevel 1 (
        echo [LOI] Khong doi ten duoc ban cu - co the dang mo GiongViet.exe.
        echo       Dong chuong trinh roi chay lai. Ban cu van nguyen ven.
        goto :fail
    )
)
move "%ROOT%_dist_moi\GiongViet" "%DICH%" >nul
if errorlevel 1 (
    echo [LOI] Khong dua duoc ban moi ra %DICH% - dang khoi phuc ban cu...
    if exist "%CU%" move "%CU%" "%DICH%" >nul
    goto :fail
)
rmdir /s /q "%ROOT%_dist_moi" 2>nul

rem Noi (junction) thay vi chep: mo hinh VieNeu vai GB, chep ra la ton cho va
rem lech ban. Junction khong can quyen admin.
if not exist "%DICH%\bin\ffmpeg" (
    if not exist "%DICH%\bin" mkdir "%DICH%\bin"
    if exist "%ROOT%bin\ffmpeg" (
        mklink /J "%DICH%\bin\ffmpeg" "%ROOT%bin\ffmpeg" >nul
    ) else if exist "%ROOT%ffmpeg" (
        mklink /J "%DICH%\bin\ffmpeg" "%ROOT%ffmpeg" >nul
    )
)

if not exist "%DICH%\models\vieneu" (
    if not exist "%DICH%\models" mkdir "%DICH%\models"
    if exist "%ROOT%models\vieneu" (
        mklink /J "%DICH%\models\vieneu" "%ROOT%models\vieneu" >nul
    ) else if exist "%ROOT%vieneu_models" (
        mklink /J "%DICH%\models\vieneu" "%ROOT%vieneu_models" >nul
    )
)

if not exist "%DICH%\data\giong_rieng" (
    if not exist "%DICH%\data" mkdir "%DICH%\data"
    if exist "%ROOT%data\giong_rieng" (
        mklink /J "%DICH%\data\giong_rieng" "%ROOT%data\giong_rieng" >nul
    ) else if exist "%ROOT%giong_rieng" (
        mklink /J "%DICH%\data\giong_rieng" "%ROOT%giong_rieng" >nul
    )
)

rem TRA LAI du lieu nguoi dung da cuu o buoc tren. Phai chay TRUOC doan chep tu
rem %ROOT% ben duoi: cac lenh do deu co "if not exist" nen ban CUA NGUOI DUNG
rem thang. Do la co y - ban trong %ROOT% van nam nguyen o thu muc goc, mat cung
rem lay lai duoc; ban cua nguoi dung mat la mat han.
if not exist "%DICH%\data" mkdir "%DICH%\data"
if exist "%CUU%" (
    for %%F in ("%CUU%\*.db" "%CUU%\*.txt" "%CUU%\*.json" "%CUU%\*.ini") do (
        if exist "%%~fF" copy /Y "%%~fF" "%DICH%\data\" >nul
    )
    if exist "%CUU%\mau_google_sheets" xcopy /E /I /Y /Q "%CUU%\mau_google_sheets" "%DICH%\data\mau_google_sheets" >nul
)

rem CHEP co so du lieu SQLite vao duy nhat thu muc data\:
if not exist "%DICH%\data" mkdir "%DICH%\data"
if exist "%ROOT%data\giongviet.db" (
    if not exist "%DICH%\data\giongviet.db" copy /Y "%ROOT%data\giongviet.db" "%DICH%\data\giongviet.db" >nul
) else if exist "%ROOT%giongviet.db" (
    if not exist "%DICH%\data\giongviet.db" copy /Y "%ROOT%giongviet.db" "%DICH%\data\giongviet.db" >nul
)

if exist "%ROOT%LICENSE.txt" copy /Y "%ROOT%LICENSE.txt" "%DICH%\LICENSE.txt" >nul

rem Cuu co so du lieu SQLite ban cu neu co
if exist "%CU%" (
    if exist "%CU%\data\giongviet.db" (
        if not exist "%DICH%\data\giongviet.db" copy /Y "%CU%\data\giongviet.db" "%DICH%\data\giongviet.db" >nul
    ) else if exist "%CU%\giongviet.db" (
        if not exist "%DICH%\data\giongviet.db" copy /Y "%CU%\giongviet.db" "%DICH%\data\giongviet.db" >nul
    )
)

echo.
echo [5/5] Don thu muc tam...
if exist "%BUILD_DIR%" rmdir /s /q "%BUILD_DIR%"
if exist "%SPEC_DIR%"  rmdir /s /q "%SPEC_DIR%"
rem Ban cu chi bi don SAU KHI ban moi da yen vi va da cuu xong du lieu.
rem
rem Windows hay giu handle them mot nhip sau khi noi dung da xoa xong: lan
rem build dau tien voi ban nay, rmdir don sach ben trong roi van bao "The
rem directory is not empty" va de lai cai vo rong. Cho mot nhip roi xoa lai.
if exist "%CU%" rmdir /s /q "%CU%" 2>nul
if exist "%CU%" (
    ping -n 3 127.0.0.1 >nul 2>nul
    rmdir /s /q "%CU%" 2>nul
)
rem Con sot cai vo rong thi KHONG coi la that bai: ban moi da xong va da kiem.
if exist "%CU%" echo   [!] Con sot %CU% ^(rong^) - xoa tay luc nao cung duoc.

echo.
echo =========================================
echo   BUILD BAN MOI THANH CONG
echo =========================================
echo   %DICH%\GiongViet.exe
echo.
echo   Ban CU o thu muc goc KHONG bi dung toi.
echo =========================================
if not "%GIONGDOC_TU_DONG%"=="1" pause
exit /b 0

:fail
echo.
echo =========================================
echo   BUILD BAN MOI THAT BAI
echo =========================================
echo Giu lai _build_moi va _spec_moi de con xem log loi.
if not "%GIONGDOC_TU_DONG%"=="1" pause
exit /b 1
