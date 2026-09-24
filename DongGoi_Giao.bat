@echo off
setlocal enabledelayedexpansion
chcp 65001 >nul 2>&1

rem ============================================================================
rem   DONG GOI DE GIAO - bien ban build thanh thu muc chep di duoc
rem ============================================================================
rem
rem VI SAO CAN TEP RIENG NAY:
rem
rem DongGoi.bat dung junction cho bin\ffmpeg, models\vieneu va data\giong_rieng.
rem Do la lua chon DUNG cho luc build: mo hinh VieNeu 313 MB, chep ra moi lan
rem build la ton cho va lech ban. Nhung junction chi song tren MOT may - chep
rem thu muc bang Explorer hay nen bang ZIP thuong thi ra thu muc rong hoac loi
rem tat gay.
rem
rem Do duoc hau qua: may nguoi dung khong co bin\ffmpeg\bin\ffplay.exe thi
rem lay_duong_dan_ffplay() roi xuong nhanh muon cua may; may chua cai ffmpeg
rem thi khong thay gi, phai tu tai ve - can mang, va im lang toi 30 giay truoc
rem khi cua so kip hien.
rem
rem KHONG MANG THEO DU LIEU CUA CHU DU AN. Vong cuu du lieu trong DongGoi.bat
rem co y chep giongviet.db va noi giong_rieng sang ban build moi - dung cho anh
rem cap nhat ban minh dang dung. Nhung ban GIAO ma mang chung theo thi nguoi
rem nhan duoc ca thiet lap cua anh va ca NAM TEP GHI AM GIONG THAT trong
rem data\giong_rieng. Tep nay chi mang thu nguoi dung can de bat dau.
rem ============================================================================

set "ROOT=%~dp0"
set "NGUON=%ROOT%GiongViet"
set "DICH=%ROOT%_giao\GiongViet"

echo =========================================
echo   DONG GOI DE GIAO
echo =========================================
echo.

if not exist "%NGUON%\GiongViet.exe" (
    echo [LOI] Chua co ban build. Chay DongGoi.bat truoc.
    goto :fail
)

echo [1/5] Don thu muc giao cu...
if exist "%ROOT%_giao" rmdir /s /q "%ROOT%_giao"
mkdir "%DICH%" 2>nul

echo [2/5] Chep phan PyInstaller dung ra...
rem /XD loai ba thu muc junction: chung duoc chep RIENG o buoc 3 tu thu muc
rem GOC, khong di qua junction. Lam vay thi khong phai danh cuoc vao chuyen
rem robocopy co di theo junction hay khong - hanh vi do con khac nhau giua
rem cac ban Windows.
robocopy "%NGUON%" "%DICH%" /E /NFL /NDL /NJH /NJS /NP ^
    /XD "%NGUON%\bin" "%NGUON%\models" "%NGUON%\data" >nul
if errorlevel 8 (
    echo [LOI] Chep phan chinh that bai.
    goto :fail
)

echo [3/5] Chep ffmpeg va mo hinh thanh thu muc THAT...
if exist "%ROOT%bin\ffmpeg" (
    robocopy "%ROOT%bin\ffmpeg" "%DICH%\bin\ffmpeg" /E /NFL /NDL /NJH /NJS /NP >nul
) else if exist "%ROOT%ffmpeg" (
    robocopy "%ROOT%ffmpeg" "%DICH%\bin\ffmpeg" /E /NFL /NDL /NJH /NJS /NP >nul
)
if errorlevel 8 (
    echo [LOI] Chep ffmpeg that bai.
    goto :fail
)

if exist "%ROOT%models\vieneu" (
    robocopy "%ROOT%models\vieneu" "%DICH%\models\vieneu" /E /NFL /NDL /NJH /NJS /NP >nul
) else if exist "%ROOT%vieneu_models" (
    robocopy "%ROOT%vieneu_models" "%DICH%\models\vieneu" /E /NFL /NDL /NJH /NJS /NP >nul
)
if errorlevel 8 (
    echo [LOI] Chep mo hinh VieNeu that bai.
    goto :fail
)

echo [4/5] Chep tep mau nguoi dung can de bat dau...
rem Man Van ban ghep dien san duong dan nay vao o nhap nguon "File tren may"
rem (man-vanbanghep.js) va cau_noi_moi.py mo no khi nguoi dung bam Chon tep.
rem Thieu no thi o nhap hien mot duong dan khong ton tai ngay lan chay dau.
if exist "%ROOT%data\mau_google_sheets" (
    mkdir "%DICH%\data" 2>nul
    robocopy "%ROOT%data\mau_google_sheets" "%DICH%\data\mau_google_sheets" ^
        /E /NFL /NDL /NJH /NJS /NP >nul
)

echo [5/5] Kiem lai ban giao...
set "HONG=0"
call :kiem "%DICH%\GiongViet.exe"                                  "GiongViet.exe"
call :kiem "%DICH%\_internal\ui-moi\index.html"                    "giao dien web"
call :kiem "%DICH%\_internal\sea_g2p\sea_g2p.bin"                  "sea_g2p.bin"
call :kiem "%DICH%\_internal\vieneu\assets\voices_v3_turbo.json"   "danh sach giong"
call :kiem "%DICH%\bin\ffmpeg\bin\ffplay.exe"                      "ffplay.exe - tep THAT"
call :kiem "%DICH%\bin\ffmpeg\bin\ffmpeg.exe"                      "ffmpeg.exe - tep THAT"
call :kiem "%DICH%\models\vieneu"                                  "mo hinh VieNeu - thu muc THAT"

rem Ba thu duoi day PHAI KHONG co trong ban giao.
call :cam "%DICH%\data\giongviet.db"   "thiet lap cua chu du an"
call :cam "%DICH%\data\congduc.txt"    "danh sach cua chu du an"
call :cam "%DICH%\data\giong_rieng"    "TEP GHI AM GIONG THAT cua chu du an"

echo.
if "%HONG%"=="1" (
    echo =========================================
    echo   BAN GIAO CHUA DAT - xem cac dong LOI o tren
    echo =========================================
    goto :fail
)

rem -Path phai ghi tuong minh: -File la CONG TAC, de duong dan roi vao vi tri
rem tham so khac thi PowerShell bao "Second path fragment must not be a drive"
rem va con so ra 0.00 GB trong khi thu muc nang 1,4 GB - da vap that.
for /f "usebackq delims=" %%S in (`powershell -NoProfile -Command ^
    "'{0:N2}' -f ((Get-ChildItem -Path '%DICH%' -Recurse -File ^| Measure-Object -Property Length -Sum).Sum/1GB)"`) do set "CO=%%S"

echo =========================================
echo   BAN GIAO SAN SANG
echo =========================================
echo   %DICH%
echo   Dung luong: %CO% GB
echo.
echo   Nen ca thu muc GiongViet roi gui. Nguoi nhan giai nen ra cho nao
echo   cung chay duoc - khong con junction, khong phu thuoc may nay.
echo =========================================
if not "%GIONGDOC_TU_DONG%"=="1" pause
exit /b 0

rem KHONG dat dau ngoac don vao chuoi nhan: batch coi dau ) trong chuoi la
rem ket thuc khoi if ( ) else ( ), nen ca hai nhanh cung chay - da vap that,
rem mot muc in ra ca OK lan LOI.
:kiem
if exist %1 (
    echo    OK     %~2
) else (
    echo    LOI    THIEU %~2
    set "HONG=1"
)
goto :eof

:cam
if exist %1 (
    echo    LOI    ban giao DANG MANG THEO %~2 - phai bo di
    set "HONG=1"
) else (
    echo    OK     khong mang theo %~2
)
goto :eof

:fail
echo.
if not "%GIONGDOC_TU_DONG%"=="1" pause
exit /b 1
