@echo off
REM Kiem 6 tep du lieu cua ban CU con nguyen ven khong.
REM Bam dup: lan 1 ghi moc, lan 2 so lai. Xem KiemDuLieu.ps1 de biet chi tiet.
powershell -NoProfile -ExecutionPolicy Bypass -File "%~dp0KiemDuLieu.ps1" %*
echo.
pause