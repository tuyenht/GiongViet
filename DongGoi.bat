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
if not exist "%ROOT%ui-moi\index.html" (
    echo [LOI] Khong tim thay ui-moi\index.html - giao dien moi khong the thieu.
    goto :fail
)
rem ffmpeg va mo hinh VieNeu KHONG nam trong kho git - chung nang ~530 MB va
rem co tep vuot gioi han 100 MB cua GitHub. Nguoi clone kho ve chay thang
rem file nay thi phai tu tai duoc, khong duoc dung lai bat nguoi ta di tim.
rem Engine da co san hai nhanh dong lenh cho dung viec nay.
if not exist "%ROOT%ffmpeg\bin\ffplay.exe" (
    echo [!] Chua co ffmpeg - dang tu dong tai ve...
    py "%ROOT%DocCongDuc.py" --tai-ffmpeg
    if not exist "%ROOT%ffmpeg\bin\ffplay.exe" (
        echo [LOI] Tai ffmpeg khong thanh cong. Chay CaiDat.bat roi thu lai.
        goto :fail
    )
)
if not exist "%ROOT%ffmpeg\bin\ffmpeg.exe" (
    echo [LOI] Co ffplay.exe nhung thieu ffmpeg.exe - MP3 va WAV 24 bit se hong.
    echo       Xoa thu muc ffmpeg roi chay lai de tai day du.
    goto :fail
)
if not exist "%ROOT%vieneu_models" (
    echo [!] Chua co mo hinh VieNeu - dang tu dong tai ve ^(vai tram MB^)...
    py "%ROOT%DocCongDuc.py" --tai-vieneu
    if not exist "%ROOT%vieneu_models" (
        echo [LOI] Tai mo hinh khong thanh cong. Chay CaiDat.bat roi thu lai.
        goto :fail
    )
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
py -m PyInstaller --noconfirm --onedir --windowed --name GiongViet ^
    --add-data "%ROOT%ui-moi;ui-moi" ^
    --collect-data vieneu ^
    --collect-data sea_g2p ^
    --hidden-import giaodien.cau_noi --hidden-import giaodien.bo_doc ^
    --hidden-import giaodien.ds_giong --hidden-import giaodien.du_lieu ^
    --hidden-import giaodien.he_thong --hidden-import giaodien.mo_hinh ^
    --hidden-import giaodien.nghe_thu --hidden-import giaodien.nhat_ky ^
    --hidden-import giaodien.thu_vien_giong --hidden-import giaodien.xuat_file ^
    --hidden-import giaodien.ho_so --hidden-import giaodien.soat ^
    --hidden-import giaodien.tu_dien --hidden-import giaodien.cai_dat ^
    --hidden-import giaodien_moi.cau_noi_moi --hidden-import giaodien_moi.khoa_du_lieu ^
    --hidden-import giaodien_moi.ho_so_v2 --hidden-import giaodien_moi.luu_tep ^
    --hidden-import giaodien_moi.so_dien_thoai --hidden-import giaodien_moi.sdt_mau ^
    --hidden-import giaodien_moi.sdt_nhip --hidden-import giaodien_moi.am_thanh_loc ^
    --hidden-import giaodien_moi.soat_moi --hidden-import giaodien_moi.xuat_moi ^
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
if not exist "%B%\ui-moi\index.html" (
    echo [LOI] Thieu ui-moi\index.html - cua so se mo ra trang trong.
    goto :fail
)
if not exist "%B%\sea_g2p\sea_g2p.bin" (
    echo [LOI] Thieu sea_g2p.bin - bam doc se bao "os error 2".
    goto :fail
)
if not exist "%B%\vieneu\assets\voices_v3_turbo.json" (
    echo [LOI] Thieu voices_v3_turbo.json - danh sach giong se RONG.
    goto :fail
)
echo   OK: ui-moi\index.html
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
if exist "%CU%" rmdir /s /q "%CU%"
if exist "%DICH%" (
    for %%L in (ffmpeg vieneu_models giong_rieng) do (
        if exist "%DICH%\%%L" rmdir "%DICH%\%%L" 2>nul
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
if not exist "%DICH%\ffmpeg"        mklink /J "%DICH%\ffmpeg" "%ROOT%ffmpeg" >nul
if not exist "%DICH%\vieneu_models" mklink /J "%DICH%\vieneu_models" "%ROOT%vieneu_models" >nul
if not exist "%DICH%\giong_rieng"   if exist "%ROOT%giong_rieng" mklink /J "%DICH%\giong_rieng" "%ROOT%giong_rieng" >nul

rem CHEP (khong noi) cac tep cau hinh: ban moi chi DOC chung - moi duong GHI da
rem bi giaodien_moi\khoa_du_lieu.py bit lai. Chep ra ban sao de du co so hong
rem thi ban that o goc van nguyen.
for %%F in (cauhinh.ini hoso.json congduc.txt noidung.ini tudien.ini giaodien.json) do (
    if exist "%ROOT%%%F" if not exist "%DICH%\%%F" copy /Y "%ROOT%%%F" "%DICH%\%%F" >nul
)

rem Cuu du lieu do CHINH CHUONG TRINH ghi ra ben ban cu. hoso-v2.json la vi du
rem ro nhat: no khong co o thu muc goc nen vong chep ben tren khong dung toi,
rem ma no giu ho so - giong - ba thanh chinh - the cam xuc cua nguoi dung. Xoa
rem ban cu ma khong cuu la nguoi dung mo len thay moi thu ve mac dinh.
rem Chi chep thu %DICH% CHUA co, de ban moi luon uu tien.
if exist "%CU%" (
    for %%F in ("%CU%\*.json" "%CU%\*.ini" "%CU%\*.txt") do (
        if not exist "%DICH%\%%~nxF" copy /Y "%%F" "%DICH%\%%~nxF" >nul
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
