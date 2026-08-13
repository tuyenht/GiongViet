# Kiểm 6 tệp dữ liệu của bản CŨ có còn nguyên vẹn không.
#
# Dùng để nghiệm thu bản mới: GiongViet KHÔNG được phép ghi vào cauhinh.ini,
# hoso.json, congduc.txt, noidung.ini, tudien.ini, giaodien.json của chương
# trình đang dùng hằng ngày.
#
# Chạy hai lần: lần đầu ghi mốc, lần sau so lại. Mốc để trong %TEMP% nên không
# đẻ thêm tệp nào vào thư mục chương trình.

param([switch]$Chup)

$ErrorActionPreference = 'Stop'
[Console]::OutputEncoding = [Text.Encoding]::UTF8
Set-Location $PSScriptRoot

$moc = Join-Path $env:TEMP 'giongdoc-moc-du-lieu.json'
$ten = @('cauhinh.ini', 'hoso.json', 'congduc.txt', 'noidung.ini',
         'tudien.ini', 'giaodien.json')

# Chụp cả giờ sửa lẫn mã băm nội dung: ghi đè đúng y nội dung cũ trong cùng
# một giây thì riêng giờ sửa có thể không đổi.
$nay = @{}
foreach ($t in $ten) {
  if (Test-Path $t) {
    $bam = (Get-FileHash $t -Algorithm SHA256).Hash
    $gio = (Get-Item $t).LastWriteTime.ToString('yyyy-MM-dd HH:mm:ss.fff')
    $nay[$t] = "$gio|$bam"
  } else {
    $nay[$t] = '(không có tệp)'
  }
}

function Gio($v) { $v.Split('|')[0] }

if ($Chup -or -not (Test-Path $moc)) {
  $nay | ConvertTo-Json | Set-Content $moc -Encoding utf8
  Write-Host ''
  Write-Host '  ĐÃ GHI MỐC cho 6 tệp dữ liệu:' -ForegroundColor Cyan
  Write-Host ''
  foreach ($t in $ten) { Write-Host ('   {0,-15} {1}' -f $t, (Gio $nay[$t])) }
  Write-Host ''
  Write-Host '  Giờ hãy mở GiongViet.py, bấm thoải mái, đóng lại,' -ForegroundColor Yellow
  Write-Host '  rồi chạy lại tệp này để kiểm.' -ForegroundColor Yellow
  Write-Host ''
  exit 0
}

$cu = Get-Content $moc -Raw | ConvertFrom-Json
$hong = 0
Write-Host ''
foreach ($t in $ten) {
  $truoc = $cu.$t
  $sau = $nay[$t]
  if ($truoc -eq $sau) {
    Write-Host ('   CÒN NGUYÊN   {0,-15} {1}' -f $t, (Gio $sau)) -ForegroundColor Green
  } else {
    $hong++
    Write-Host ('   BỊ ĐỔI !!!   {0,-15}' -f $t) -ForegroundColor Red
    Write-Host ('                  trước: {0}' -f (Gio $truoc)) -ForegroundColor Red
    Write-Host ('                  sau  : {0}' -f (Gio $sau)) -ForegroundColor Red
  }
}
Write-Host ''
if ($hong -eq 0) {
  Write-Host '  ĐẠT — bản mới không đụng gì vào dữ liệu của bản cũ.' -ForegroundColor Green
} else {
  Write-Host ("  HỎNG — {0} tệp bị ghi đè. Báo lại để sửa khoá." -f $hong) -ForegroundColor Red
}
Write-Host ''
Write-Host '  (Muốn ghi mốc mới: KiemDuLieu.bat chup)' -ForegroundColor DarkGray
Write-Host ''
exit $hong
