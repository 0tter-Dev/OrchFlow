@echo off
setlocal

set "ROOT_DIR=%~dp0"
if "%ROOT_DIR:~-1%"=="\" set "ROOT_DIR=%ROOT_DIR:~0,-1%"
set "CONTROL_SCRIPT=%ROOT_DIR%\scripts\orchflow-local-process-control.ps1"

if /I "%~1"=="status" goto RUN_STATUS_FROM_ARGUMENT
if /I "%~1"=="start" goto RUN_START_FROM_ARGUMENT
if /I "%~1"=="stop" goto RUN_STOP_FROM_ARGUMENT
if /I "%~1"=="restart" goto RUN_RESTART_FROM_ARGUMENT

:MENU
cls
echo ============================================
echo        OrchFlow Control Launcher
echo ============================================
echo.
echo   [1] Check status
echo   [2] Start
echo   [3] Stop
echo   [4] Restart
echo   [5] Exit
echo.
set /p "ACTION=Choose an option: "

if "%ACTION%"=="1" goto MENU_STATUS
if "%ACTION%"=="2" goto MENU_START
if "%ACTION%"=="3" goto MENU_STOP
if "%ACTION%"=="4" goto MENU_RESTART
if "%ACTION%"=="5" goto EXIT

echo Unsupported option: %ACTION%
pause
goto MENU

:MENU_STATUS
call :RUN_CONTROL status
pause
goto MENU

:MENU_START
call :RUN_CONTROL start
pause
goto MENU

:MENU_STOP
call :RUN_CONTROL stop
pause
goto MENU

:MENU_RESTART
call :RUN_CONTROL restart
pause
goto MENU

:RUN_STATUS_FROM_ARGUMENT
call :RUN_CONTROL status
exit /b %ERRORLEVEL%

:RUN_START_FROM_ARGUMENT
call :RUN_CONTROL start
exit /b %ERRORLEVEL%

:RUN_STOP_FROM_ARGUMENT
call :RUN_CONTROL stop
exit /b %ERRORLEVEL%

:RUN_RESTART_FROM_ARGUMENT
call :RUN_CONTROL restart
exit /b %ERRORLEVEL%

:RUN_CONTROL
powershell -NoProfile -ExecutionPolicy Bypass -File "%CONTROL_SCRIPT%" %~1
exit /b %ERRORLEVEL%

:EXIT
echo.
echo Leaving OrchFlow control launcher.
exit /b 0
