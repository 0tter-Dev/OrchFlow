@echo off
setlocal

set "TOOLS_DIR=%~dp0"
if "%TOOLS_DIR:~-1%"=="\" set "TOOLS_DIR=%TOOLS_DIR:~0,-1%"
for %%I in ("%TOOLS_DIR%\..\..") do set "ROOT_DIR=%%~fI"
set "SETUP_LAUNCHER=%TOOLS_DIR%\orchflow-setup.bat"
set "CONTROL_LAUNCHER=%TOOLS_DIR%\orchflow-control.bat"

:MENU
cls
echo ============================================
echo                   OrchFlow
echo ============================================
echo.
echo   [1] Check environment, prerequisites, and dependencies
echo   [2] Start API and Web
echo   [3] Open setup launcher
echo   [4] Open control launcher
echo   [0] Exit
echo.
set /p "ACTION=Choose an option: "

if "%ACTION%"=="1" goto MENU_CHECK
if "%ACTION%"=="2" goto MENU_START
if "%ACTION%"=="3" goto MENU_SETUP
if "%ACTION%"=="4" goto MENU_CONTROL
if "%ACTION%"=="0" goto EXIT

echo Unsupported option: %ACTION%
pause
goto MENU

:MENU_CHECK
call "%SETUP_LAUNCHER%" check
pause
goto MENU

:MENU_START
call "%CONTROL_LAUNCHER%" start
pause
goto MENU

:MENU_SETUP
call "%SETUP_LAUNCHER%"
goto MENU

:MENU_CONTROL
call "%CONTROL_LAUNCHER%"
goto MENU

:EXIT
echo.
echo Leaving OrchFlow launcher.
exit /b 0
