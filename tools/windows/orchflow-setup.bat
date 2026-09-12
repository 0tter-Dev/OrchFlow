@echo off
setlocal enabledelayedexpansion

set "TOOLS_DIR=%~dp0"
if "%TOOLS_DIR:~-1%"=="\" set "TOOLS_DIR=%TOOLS_DIR:~0,-1%"
for %%I in ("%TOOLS_DIR%\..\..") do set "ROOT_DIR=%%~fI"
set "WEB_DIR=%ROOT_DIR%\interface\web"
set "CONTROL_LAUNCHER=%TOOLS_DIR%\orchflow-control.bat"

if /I "%~1"=="check" goto RUN_CHECK_FROM_ARGUMENT
if /I "%~1"=="start-all" goto RUN_START_FROM_ARGUMENT

:MENU
cls
echo ============================================
echo              OrchFlow - Setup
echo ============================================
echo.
echo   [1] Check environment, prerequisites, and dependencies
echo   [2] Start API and Web
echo   [0] Exit
echo.
set /p "ACTION=Choose an option: "

if "%ACTION%"=="1" goto MENU_CHECK
if "%ACTION%"=="2" goto MENU_START
if "%ACTION%"=="0" goto EXIT

echo Unsupported option: %ACTION%
pause
goto MENU

:MENU_CHECK
call :RUN_SETUP_CHECK
pause
goto MENU

:MENU_START
call :START_ALL
pause
goto MENU

:RUN_CHECK_FROM_ARGUMENT
call :RUN_SETUP_CHECK
exit /b %ERRORLEVEL%

:RUN_START_FROM_ARGUMENT
call :START_ALL
exit /b %ERRORLEVEL%

:CHECK_PREREQUISITES
echo.
echo Checking required local tools...
set "MISSING_TOOLS=0"
call :CHECK_TOOL uv "Install uv from https://docs.astral.sh/uv/"
call :CHECK_TOOL node "Install Node.js from https://nodejs.org/"
call :CHECK_TOOL corepack "Install a Node.js version that includes Corepack."

if "%MISSING_TOOLS%"=="1" (
  echo.
  echo One or more required tools are missing. Install them first, then re-run this launcher.
  exit /b 1
)

echo.
echo All required tools were found.
exit /b 0

:CHECK_TOOL
where %~1 >nul 2>nul
if errorlevel 1 (
  echo [missing] %~1
  echo           %~2
  set "MISSING_TOOLS=1"
) else (
  echo [ok] %~1
)
exit /b 0

:REQUIRE_TOOL
where %~1 >nul 2>nul
if errorlevel 1 (
  echo [error] Required tool not found: %~1
  echo         %~2
  exit /b 1
)
exit /b 0

:PREPARE_ENV_FILES
echo.
echo Preparing local environment files...
call :COPY_IF_MISSING "%ROOT_DIR%\.env.example" "%ROOT_DIR%\.env"
if errorlevel 1 exit /b 1
call :COPY_IF_MISSING "%WEB_DIR%\.env.example" "%WEB_DIR%\.env"
if errorlevel 1 exit /b 1
echo.
echo Local environment files are ready. Existing files were preserved.
exit /b 0

:COPY_IF_MISSING
set "SOURCE_FILE=%~1"
set "TARGET_FILE=%~2"
if not exist "%SOURCE_FILE%" (
  echo [error] Source file not found: %SOURCE_FILE%
  exit /b 1
)
if exist "%TARGET_FILE%" (
  echo [skip] %TARGET_FILE% already exists.
  exit /b 0
)
copy "%SOURCE_FILE%" "%TARGET_FILE%" >nul
if errorlevel 1 (
  echo [error] Could not create %TARGET_FILE%.
  exit /b 1
)
echo [created] %TARGET_FILE%
exit /b 0

:INSTALL_DEPENDENCIES
echo.
echo Installing backend and web dependencies...
call :REQUIRE_TOOL uv "Install uv from https://docs.astral.sh/uv/"
if errorlevel 1 exit /b 1
call :REQUIRE_TOOL node "Install Node.js from https://nodejs.org/"
if errorlevel 1 exit /b 1
call :REQUIRE_TOOL corepack "Install a Node.js version that includes Corepack."
if errorlevel 1 exit /b 1

cd /d "%ROOT_DIR%" || exit /b 1
call uv sync --dev
if errorlevel 1 exit /b 1

pushd "%WEB_DIR%" || exit /b 1
call corepack pnpm install
if errorlevel 1 (
  popd
  exit /b 1
)
popd

echo.
echo Dependencies are installed.
exit /b 0

:RUN_MIGRATIONS
echo.
echo Running database migrations...
call :REQUIRE_TOOL uv "Install uv from https://docs.astral.sh/uv/"
if errorlevel 1 exit /b 1
cd /d "%ROOT_DIR%" || exit /b 1
call uv run alembic upgrade head
exit /b %ERRORLEVEL%

:VALIDATE_BOOTSTRAP
echo.
echo Validating OrchFlow CLI and bootstrap status...
call :REQUIRE_TOOL uv "Install uv from https://docs.astral.sh/uv/"
if errorlevel 1 exit /b 1
cd /d "%ROOT_DIR%" || exit /b 1
call uv run orchflow info
if errorlevel 1 exit /b 1
call uv run orchflow health
if errorlevel 1 exit /b 1
call uv run orchflow database
exit /b %ERRORLEVEL%

:START_ALL
call "%CONTROL_LAUNCHER%" start
exit /b %ERRORLEVEL%

:RUN_SETUP_CHECK
call :CHECK_PREREQUISITES
if errorlevel 1 exit /b 1
call :PREPARE_ENV_FILES
if errorlevel 1 exit /b 1
call :INSTALL_DEPENDENCIES
if errorlevel 1 exit /b 1
call :RUN_MIGRATIONS
if errorlevel 1 exit /b 1
call :VALIDATE_BOOTSTRAP
exit /b %ERRORLEVEL%

:EXIT
echo.
echo Leaving OrchFlow setup launcher.
exit /b 0
