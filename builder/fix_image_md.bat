@echo off
setlocal


set "in=..\README.md"
set "out=..\README.md"

powershell -NoProfile -Command ^
  "(Get-Content -Raw -LiteralPath '%in%') -replace '\[\[','![' | Set-Content -NoNewline -LiteralPath '%out%' -Encoding UTF8"

echo Done: "%out%"
endlocal