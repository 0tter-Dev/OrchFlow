# Lifecycle Script Template

## Purpose

This module defines the standard structure expected for lifecycle `.bat` scripts managed by OrchFlow.

## Objective

Provide a concrete contract that guides users and AI-assisted generation so scripts remain predictable, inspectable, and compatible with OrchFlow.

## Current Status

`implemented`

## Canonical Lifecycle Actions

Every managed project should expose, directly or indirectly, the following canonical actions:

- `status`
- `start`
- `stop`
- `restart`

The script may also expose:

- `exit`
- helper labels for runtime inspection
- helper labels for silent stop or internal restart composition

## Minimum Requirements

The first template version should define:

- a clear configuration block at the top of the file
- a stable menu or command-dispatch structure
- explicit labels for lifecycle actions or a documented mapping to them
- explicit variables for project title, project label, root path, start directory, start command, known port, application URL, and startup wait
- predictable labels and control flow
- human-readable operational messages
- at least one runtime inspection strategy, initially expected to support port-based checks when applicable

## Recommended Structure

The recommended structure is:

1. environment setup and delayed expansion
2. configuration block
3. menu or command dispatcher
4. public lifecycle labels
5. helper labels
6. exit path

## Label Direction

The preferred label names are:

- `:STATUS`
- `:START`
- `:STOP`
- `:RESTART`
- `:EXIT`

Helper labels may include:

- `:GET_PORT_PIDS`
- `:SHOW_PID_DETAILS`
- `:STOP_SILENT`

Projects may use different label names, but those differences must be normalized through the `Project Adapter` action mapping configuration.

## Example Template

The following example is based on the control pattern validated in the reference `Search-VideoHub.bat` script:

```bat
@echo off
setlocal enabledelayedexpansion

set "APP_TITLE=Example Project"
set "APP_LABEL=example-project"
set "APP_ROOT=%~dp0"
set "APP_PORT=8080"
set "APP_URL=http://localhost:%APP_PORT%"
set "APP_START_DIR=%APP_ROOT%"
set "APP_START_COMMAND=npm start"
set "APP_WINDOW_TITLE=%APP_LABEL%-App"
set "STARTUP_WAIT_SECONDS=3"

title %APP_TITLE%

:MENU
cls
echo ============================================
echo        %APP_TITLE% ^| Menu
echo ============================================
echo.
echo   [1] Check status
echo   [2] Start application
echo   [3] Stop application
echo   [4] Restart application
echo   [0] Exit
echo.
set /p "CHOICE=Choose an option: "

if "%CHOICE%"=="1" goto STATUS
if "%CHOICE%"=="2" goto START
if "%CHOICE%"=="3" goto STOP
if "%CHOICE%"=="4" goto RESTART
if "%CHOICE%"=="0" goto EXIT
echo Invalid option.
timeout /t 2 >nul
goto MENU

:STATUS
cls
call :GET_PORT_PIDS
if defined PORT_PIDS (
  echo [%APP_LABEL%] Running at %APP_URL%
  echo PID(s): %PORT_PIDS%
) else (
  echo [%APP_LABEL%] Application appears to be stopped.
)
echo.
pause
goto MENU

:START
cls
call :GET_PORT_PIDS
if defined PORT_PIDS (
  echo [%APP_LABEL%] Port %APP_PORT% is already in use.
  pause
  goto MENU
)
start "%APP_WINDOW_TITLE%" cmd /c "cd /d ""%APP_START_DIR%"" && set PORT=%APP_PORT% && %APP_START_COMMAND%"
timeout /t %STARTUP_WAIT_SECONDS% >nul
goto STATUS

:STOP
cls
call :GET_PORT_PIDS
if not defined PORT_PIDS (
  echo [%APP_LABEL%] Application already appears to be stopped.
  timeout /t 2 >nul
  goto MENU
)
for %%P in (%PORT_PIDS%) do (
  taskkill /PID %%P /F >nul 2>&1
)
timeout /t 2 >nul
goto STATUS

:RESTART
cls
call :STOP_SILENT
timeout /t 2 >nul
goto START

:EXIT
exit /b 0

:GET_PORT_PIDS
set "PORT_PIDS="
for /f "tokens=5" %%P in ('
    netstat -ano ^| findstr /C:":%APP_PORT%" ^| findstr /C:"LISTENING"
') do (
    if not defined PORT_PIDS (
        set "PORT_PIDS=%%P"
    ) else (
        echo !PORT_PIDS! | findstr /C:" %%P " >nul
        if errorlevel 1 set "PORT_PIDS=!PORT_PIDS! %%P"
    )
)
exit /b 0

:STOP_SILENT
call :GET_PORT_PIDS
if not defined PORT_PIDS exit /b 0
for %%P in (%PORT_PIDS%) do (
  taskkill /PID %%P /F >nul 2>&1
)
exit /b 0
```

## Mapping Compatibility

OrchFlow should prefer canonical lifecycle action names, but some existing scripts may expose different labels such as:

- `:INICIAR` instead of `:START`
- `:PARAR` instead of `:STOP`
- `:REINICIAR` instead of `:RESTART`
- `:VERIFICAR` instead of `:STATUS`

For those cases, OrchFlow should rely on project-specific action mappings managed through the `Project Adapter`.

## Key Rules

- the template should be generic enough to support different projects
- the template should remain Windows-first for `v0.1.0`
- the template should be easy for a human to review and adjust
- the template should be easy for the `AI Agent Adapter` to generate or update
- the template should avoid hidden behavior and implicit side effects
- the template should make its lifecycle labels discoverable
- the template should support audit-friendly and operator-friendly messages

## Main Relationships

- guides `Project Registry` during project onboarding
- guides `Project Adapter` during lifecycle execution expectations
- guides `AI Agent Adapter` when generating or updating scripts
- supports `User Guide` examples and future setup documentation
