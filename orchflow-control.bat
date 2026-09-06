@echo off
setlocal

set "ROOT_DIR=%~dp0"
if "%ROOT_DIR:~-1%"=="\" set "ROOT_DIR=%ROOT_DIR:~0,-1%"
set "SETUP_LAUNCHER=%ROOT_DIR%\orchflow-setup.bat"

:MENU
cls
echo ============================================
echo        OrchFlow Control Launcher
echo ============================================
echo.
echo   [1] Start API and Web
echo   [2] Exit
echo.
set /p "ACTION=Choose an option: "

if "%ACTION%"=="1" goto MENU_START
if "%ACTION%"=="2" goto EXIT

echo Unsupported option: %ACTION%
pause
goto MENU

:MENU_START
call "%SETUP_LAUNCHER%" start-all
pause
goto MENU

:EXIT
echo.
echo Leaving OrchFlow control launcher.
exit /b 0
