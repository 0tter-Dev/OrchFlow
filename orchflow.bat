@echo off
setlocal

title OrchFlow

set "ROOT_DIR=%~dp0"
if "%ROOT_DIR:~-1%"=="\" set "ROOT_DIR=%ROOT_DIR:~0,-1%"
set "TOOLS_DIR=%ROOT_DIR%\tools\windows"
set "SETUP_LAUNCHER=%TOOLS_DIR%\orchflow-setup.bat"
set "CONTROL_LAUNCHER=%TOOLS_DIR%\orchflow-control.bat"

:MENU
cls
echo ============================================
echo                   OrchFlow
echo ============================================
echo.
echo   [1] Run checks and start OrchFlow
echo   [2] Open in browser
echo   [3] Go to Setup menu
echo   [4] Go to Control menu
echo   [0] Exit
echo.
set /p "ACTION=Choose an option: "

if "%ACTION%"=="1" goto MENU_CHECK_AND_START
if "%ACTION%"=="2" goto MENU_OPEN_BROWSER
if "%ACTION%"=="3" goto MENU_SETUP
if "%ACTION%"=="4" goto MENU_CONTROL
if "%ACTION%"=="0" goto EXIT

echo Unsupported option: %ACTION%
pause
goto MENU

:MENU_CHECK_AND_START
call "%SETUP_LAUNCHER%" check
if errorlevel 1 (
  echo.
  echo OrchFlow setup checks failed. Fix the reported issue and try again.
  pause
  goto MENU
)
call "%CONTROL_LAUNCHER%" start
pause
goto MENU

:MENU_OPEN_BROWSER
call :OPEN_BROWSER
pause
goto MENU

:MENU_SETUP
call "%SETUP_LAUNCHER%"
goto MENU

:MENU_CONTROL
call "%CONTROL_LAUNCHER%"
goto MENU

:OPEN_BROWSER
call :RESOLVE_WEB_URL
echo.
echo Opening OrchFlow at %WEB_URL%
start "" "%WEB_URL%"
exit /b 0

:RESOLVE_WEB_URL
set "WEB_URL=%ORCHFLOW_WEB_URL%"
if "%WEB_URL%"=="" call :READ_ENV_VALUE ORCHFLOW_WEB_URL WEB_URL
if not "%WEB_URL%"=="" exit /b 0

set "WEB_HOST=%ORCHFLOW_WEB_HOST%"
if "%WEB_HOST%"=="" call :READ_ENV_VALUE ORCHFLOW_WEB_HOST WEB_HOST
if "%WEB_HOST%"=="" set "WEB_HOST=localhost"

set "WEB_PORT=%ORCHFLOW_WEB_PORT%"
if "%WEB_PORT%"=="" call :READ_ENV_VALUE ORCHFLOW_WEB_PORT WEB_PORT
if "%WEB_PORT%"=="" set "WEB_PORT=5174"

set "WEB_URL=http://%WEB_HOST%:%WEB_PORT%"
exit /b 0

:READ_ENV_VALUE
set "ENV_KEY=%~1"
set "ENV_TARGET=%~2"
if not exist "%ROOT_DIR%\.env" exit /b 0
for /f "usebackq tokens=1,* delims==" %%A in ("%ROOT_DIR%\.env") do (
  if /I "%%A"=="%ENV_KEY%" set "%ENV_TARGET%=%%B"
)
exit /b 0

:EXIT
echo.
echo Leaving OrchFlow launcher.
exit /b 0
