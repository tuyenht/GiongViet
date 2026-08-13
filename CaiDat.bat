@echo off
setlocal EnableExtensions
cd /d "%~dp0"

echo =========================================
echo   CAI DAT THU VIEN DOC CONG DUC
echo =========================================
echo.
echo File nay cai VieNeu-TTS, PyTorch (CPU), PyInstaller, tai FFmpeg
echo neu thieu, va TAI SAN mo hinh giong noi - de sau khi cai xong, mo
echo chuong trinh la dung duoc ngay CA phan doc thuong LAN tinh nang
echo "Tao giong rieng tu file mau", khong can cai gi them sau nay.
echo KHONG XOA D:\GiongDoc va KHONG XOA DU LIEU.
echo.
echo Buoc nay se tai khoang 350-450 MB thu vien (gom ca PyTorch ban
echo CPU, ~200MB) + vai tram MB mo hinh giong noi - can Internet on
echo dinh, co the mat 10-20 phut tuy mang.
echo.

where py >nul 2>nul
if errorlevel 1 (
    echo [LOI] Khong tim thay Python.
    echo Hay cai Python 3.11/3.12/3.13/3.14 64-bit.
    pause
    exit /b 1
)

py --version

echo.
echo [1/4] Cai VieNeu-TTS va PyInstaller...
py -m pip install vieneu pyinstaller
if errorlevel 1 goto :fail

echo.
echo Dang cai PyTorch ^(ban CPU, khong can GPU^) - can cho tinh nang
echo "Tao giong rieng tu file mau". Rieng buoc nay co the mat vai
echo phut vi PyTorch kha nang^(~200MB^)...
py -m pip install torch --index-url https://download.pytorch.org/whl/cpu
if errorlevel 1 (
    echo.
    echo [CANH BAO] Cai PyTorch khong thanh cong. Doc cong duc/van ban
    echo van dung binh thuong - chi rieng tinh nang "Tao giong rieng tu
    echo file mau" se khong dung duoc cho toi khi cai lai PyTorch bang:
    echo py -m pip install torch --index-url https://download.pytorch.org/whl/cpu
)

echo.
echo [2/4] Kiem tra / tai FFmpeg (ffplay.exe) neu can...
py "%~dp0DocCongDuc.py" --tai-ffmpeg
if errorlevel 1 (
    echo.
    echo [CANH BAO] Tu dong tai FFmpeg khong thanh cong.
    echo Ban van co the tai thu cong tai:
    echo https://github.com/BtbN/FFmpeg-Builds/releases
    echo ^(chon ban ffmpeg-master-latest-win64-gpl.zip^)
    echo roi giai nen, chep ffplay.exe vao ffmpeg\bin\
    echo Chuong trinh se tu hoi lai khi chay neu van thieu.
)

echo.
echo =========================================
echo   [3/4] TAI MO HINH VIENEU-TTS
echo =========================================
echo Dang tai mo hinh giong noi ve thu muc vieneu_models\ va thu tong
echo hop mot cau de xac nhan hoat dong dung - lam viec nay NGAY BAY GIO
echo de sau khong can tai gi khi dang dung chuong trinh that.
echo.
py "%~dp0DocCongDuc.py" --tai-vieneu
if errorlevel 1 (
    echo.
    echo [CANH BAO] Chua tai duoc mo hinh VieNeu-TTS - co the do mat
    echo Internet giua chung. Chuong trinh se tu tai lai khi mo lan dau
    echo dung den giong doc ^(se cham hon vi phai tai luc do^). Co the
    echo chay lai rieng buoc nay bang: py DocCongDuc.py --tai-vieneu
)

echo.
echo [4/4] Xac nhan hoan tat.
echo.
echo CAI DAT THANH CONG.
echo Tiep theo chay DongGoi.bat de dong goi thanh chuong trinh, hoac
echo chay thang: py DocCongDuc.py
echo.
echo LUU Y: vi da cai them PyTorch, ban dong goi .exe qua DongGoi.bat
echo se nang hon truoc (co the 500-700MB thay vi 300-500MB), vi PyTorch
echo cung se bi nhet vao ban dong goi.
pause
exit /b 0

:fail
echo.
echo CAI DAT THAT BAI.
pause
exit /b 1
