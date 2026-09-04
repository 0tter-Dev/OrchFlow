@echo off
setlocal enabledelayedexpansion

set "ROOT_DIR=%~dp0"
if "%ROOT_DIR:~-1%"=="\" set "ROOT_DIR=%ROOT_DIR:~0,-1%"
set "WEB_DIR=%ROOT_DIR%\interface\web"
set "API_HOST=localhost"
set "API_PORT=8000"
set "WEB_URL=http://localhost:5174"

:MENU
cls
echo ============================================
echo        OrchFlow Local Dev Launcher
echo ============================================
echo.
echo   [1] Check local prerequisites
echo   [2] Prepare local .env files
echo   [3] Install backend and web dependencies
echo   [4] Run database migrations
echo   [5] Validate CLI and bootstrap status
echo   [6] Start API server
echo   [7] Start web client
echo   [8] Start API, web, and open browser
echo   [9] Run setup steps 1-5
echo   [0] Exit
echo.
set /p "ACTION=Choose an option: "

if "%ACTION%"=="1" goto MENU_CHECK_PREREQUISITES
if "%ACTION%"=="2" goto MENU_PREPARE_ENV_FILES
if "%ACTION%"=="3" goto MENU_INSTALL_DEPENDENCIES
if "%ACTION%"=="4" goto MENU_RUN_MIGRATIONS
if "%ACTION%"=="5" goto MENU_VALIDATE_BOOTSTRAP
if "%ACTION%"=="6" goto MENU_START_API
if "%ACTION%"=="7" goto MENU_START_WEB
if "%ACTION%"=="8" goto MENU_START_ALL
if "%ACTION%"=="9" goto MENU_RUN_SETUP
if "%ACTION%"=="0" goto EXIT

echo Unsupported option: %ACTION%
pause
goto MENU

:MENU_CHECK_PREREQUISITES
call :CHECK_PREREQUISITES
pause
goto MENU

:MENU_PREPARE_ENV_FILES
call :PREPARE_ENV_FILES
pause
goto MENU

:MENU_INSTALL_DEPENDENCIES
call :INSTALL_DEPENDENCIES
pause
goto MENU

:MENU_RUN_MIGRATIONS
call :RUN_MIGRATIONS
pause
goto MENU

:MENU_VALIDATE_BOOTSTRAP
call :VALIDATE_BOOTSTRAP
pause
goto MENU

:MENU_START_API
call :START_API
pause
goto MENU

:MENU_START_WEB
call :START_WEB
pause
goto MENU

:MENU_START_ALL
call :START_ALL
pause
goto MENU

:MENU_RUN_SETUP
call :RUN_SETUP
pause
goto MENU

:CHECK_PREREQUISITES
echo.
echo Checking required local tools...
set "MISSING_TOOLS=0"
call :CHECK_TOOL uv "Install uv from https://docs.astral.sh/uv/"
call :CHECK_TOOL node "Install Node.js from https://nodejs.org/"
call :CHECK_TOOL corepack "Install a Node.js version that includes Corepack."
call :CHECK_TOOL pnpm "Run corepack enable, then re-run this check."

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
call corepack enable
if errorlevel 1 (
  popd
  exit /b 1
)
call pnpm install
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

:START_API
echo.
echo Starting OrchFlow API at http://%API_HOST%:%API_PORT% ...
call :REQUIRE_TOOL uv "Install uv from https://docs.astral.sh/uv/"
if errorlevel 1 exit /b 1
start "OrchFlow API" cmd /k "cd /d ""%ROOT_DIR%"" && uv run uvicorn orchflow.external.api.app:create_app --factory --host %API_HOST% --port %API_PORT% --reload"
exit /b 0

:START_WEB
echo.
echo Starting OrchFlow web client at %WEB_URL% ...
call :REQUIRE_TOOL pnpm "Run corepack enable from option 3 before starting the web client."
if errorlevel 1 exit /b 1
start "OrchFlow Web" cmd /k "cd /d ""%WEB_DIR%"" && pnpm dev"
exit /b 0

:START_ALL
call :START_API
if errorlevel 1 exit /b 1
call :START_WEB
if errorlevel 1 exit /b 1
timeout /t 3 >nul
start "" "%WEB_URL%"
exit /b 0

:RUN_SETUP
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
echo Leaving OrchFlow launcher.
exit /b 0
