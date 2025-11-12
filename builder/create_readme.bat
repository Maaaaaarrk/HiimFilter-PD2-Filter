@echo off
setlocal enabledelayedexpansion

:: === Configuration ===
set "sourceFile=README.md"
set "keyword={{REPLACE_ME}}"
set "replacementFile=01-Version.filter"
set "finalFile=..\README.md"

:: === Read the replacement text into a variable ===
set "replacementText="
for /f "usebackq delims=" %%A in ("%replacementFile%") do (
    set "line=%%A"
    set "line=!line:%%CL%%= !"
    set "replacementText=!replacementText!!line!\n"
)

:: Remove trailing newline
set "replacementText=!replacementText:~0,-2!"

:: === Replace keyword with replacement text and &&& with ! ===
(
    for /f "usebackq delims=" %%A in ("%sourceFile%") do (
        set "line=%%A"
        set "line=!line:%keyword%=%replacementText%!"
        set "line=!line:&&&=!"
        echo !line!
    )
) > "%finalFile%"
echo Done. Replaced "%keyword%" and replaced "&&&" with "!" in "%finalFile%".