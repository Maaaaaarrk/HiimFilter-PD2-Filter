@echo off
setlocal ENABLEDELAYEDEXPANSION

rem === Read current version from version.txt (default to 1 if missing/invalid) ===
set "VERSION=0"
if exist "version.txt" (
    for /f "usebackq delims=" %%A in ("version.txt") do (
        set "VERSION=%%A"
        goto :GotVersion
    )
)

:GotVersion
rem Fallback if VERSION is empty or not numeric
echo(!VERSION!| findstr /R "^[0-9][0-9]*$" >nul || set "VERSION=0"

rem === Increment version ===
set /a VERSION+=1

rem === Save new version back to version.txt ===
> "version.txt" echo(!VERSION!

rem === Get current date components ===
for /f "tokens=2-4 delims=/.- " %%a in ('echo %date%') do (
    set "MM=%%a"
    set "DD=%%b"
    set "YYYY=%%c"
)

rem You may need to adjust token order depending on your system date format.
rem If the date text is wrong, echo %date% in a cmd window and adjust the tokens above.

rem === Build friendly date string like 'November 23rd' ===

call :GetMonthName %MM% MONTHNAME

set "DAY=%DD%"
if "!DAY:~0,1!"=="0" set "DAY=!DAY:~1!"

set "SUFFIX=th"
if "!DAY!"=="1"  set "SUFFIX=st"
if "!DAY!"=="21" set "SUFFIX=st"
if "!DAY!"=="31" set "SUFFIX=st"
if "!DAY!"=="2"  set "SUFFIX=nd"
if "!DAY!"=="22" set "SUFFIX=nd"
if "!DAY!"=="3"  set "SUFFIX=rd"
if "!DAY!"=="23" set "SUFFIX=rd"

set "PRETTYDATE=!MONTHNAME! !DAY!!SUFFIX!"

rem === Output file name (change as you like) ===
set "OUTFILE=01-Version.filter"

rem === Build the file content ===
> "%OUTFILE%" (
    <nul set /p "=Last updated !PRETTYDATE!%%CL%%Season 12 - version !VERSION!"
)

echo Created/updated "%OUTFILE%" with version !VERSION! and date !PRETTYDATE!.
endlocal
goto :eof

rem === Helper: convert month number to month name ===
:GetMonthName
setlocal
set "NUM=%1"
if "%NUM:~0,1%"=="0" set "NUM=%NUM:~1%"
set "NAME="

if "%NUM%"=="1"  set "NAME=January"
if "%NUM%"=="2"  set "NAME=February"
if "%NUM%"=="3"  set "NAME=March"
if "%NUM%"=="4"  set "NAME=April"
if "%NUM%"=="5"  set "NAME=May"
if "%NUM%"=="6"  set "NAME=June"
if "%NUM%"=="7"  set "NAME=July"
if "%NUM%"=="8"  set "NAME=August"
if "%NUM%"=="9"  set "NAME=September"
if "%NUM%"=="10" set "NAME=October"
if "%NUM%"=="11" set "NAME=November"
if "%NUM%"=="12" set "NAME=December"

endlocal & set "%2=%NAME%"
goto :eof
