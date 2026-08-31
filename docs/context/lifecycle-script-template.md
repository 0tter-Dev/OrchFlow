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

## Ideal Lifecycle Function Model

The ideal lifecycle model is the fixed reference OrchFlow uses to describe the expected lifecycle functions for a managed project.

The initial model is:

| Function | Purpose | Preferred script identifier |
| --- | --- | --- |
| `status` | Report whether the project appears to be running and expose useful runtime hints | `STATUS` |
| `start` | Start the project using the configured local command and working directory | `START` |
| `stop` | Stop the project using a clear local process or port-based strategy | `STOP` |
| `restart` | Stop and start the project again through predictable control flow | `RESTART` |

The model is a reference for validation, user guidance, and AI-assisted improvement. It does not require every existing project script to use the preferred identifiers, but every executable lifecycle operation in OrchFlow should resolve back to one of these ideal functions.

## Function Configuration States

Each ideal lifecycle function should have a configuration state for each registered project:

- `configured`: OrchFlow has an automatic or manual mapping from the ideal function to a concrete script identifier.
- `undefined`: OrchFlow did not detect a mapping and the user has not made an explicit decision.
- `unconfigured`: the user explicitly chose not to configure that function for the project.

Automatic script analysis should only produce `configured` or `undefined` states. The `unconfigured` state is a deliberate user decision.

Projects with partial configuration should remain usable for configured actions and should show warnings with improvement paths. Projects where every ideal lifecycle function is either `undefined` or `unconfigured` should be blocked from operational use because OrchFlow has no configured lifecycle action to execute.

The script may also expose:

- `exit`
- helper labels for runtime inspection
- helper labels for silent stop or internal restart composition

## Minimum Requirements

The first template version should define:

- a clear configuration block at the top of the file
- a first-argument command-dispatch structure compatible with `control.bat ACTION`
- an optional interactive menu for human use after command dispatch is handled
- explicit labels for lifecycle actions or a documented mapping to them
- explicit variables for project title, project label, root path, start directory, start command, known port, application URL, and startup wait
- predictable labels and control flow
- human-readable operational messages
- at least one runtime inspection strategy, initially expected to support port-based checks when applicable

## Recommended Structure

The recommended structure is:

1. environment setup and delayed expansion
2. configuration block
3. command dispatcher
4. public lifecycle labels
5. optional menu
6. helper labels
7. exit path

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

Projects may use different label names, but those differences must be normalized through the `Project Adapter` action mapping configuration. Matching preferred identifiers can be automatic; non-preferred identifiers should be reviewable and manually configurable unless AI assistance proposes mappings that the user later approves.

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

if /I "%~1"=="STATUS" goto STATUS
if /I "%~1"=="START" goto START
if /I "%~1"=="STOP" goto STOP
if /I "%~1"=="RESTART" goto RESTART
if not "%~1"=="" (
  echo Unsupported action: %~1
  exit /b 1
)

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

When a script is connected, OrchFlow now inspects the available dispatch identifiers and compares them with the ideal lifecycle model. Detected preferred identifiers are mapped automatically. Missing functions begin as `undefined` and can become `configured` or `unconfigured` through explicit user review in the API or CLI manual mapping workflows.

When a project is reloaded in a later workflow, OrchFlow should reuse the same inspection rules while preserving user decisions where appropriate.

## Key Rules

- the template should be generic enough to support different projects
- the template should remain Windows-first for `v0.3.8`
- the template should be easy for a human to review and adjust
- the template should be easy for the `AI Assistance Adapter` to generate or update
- the template should avoid hidden behavior and implicit side effects
- the template should make its lifecycle labels discoverable
- the template should support audit-friendly and operator-friendly messages
- the template should provide the ideal lifecycle model used for automatic mapping, manual mapping, AI-assisted improvement, and project reload validation

## Main Relationships

- guides `Project Registry` during project onboarding
- guides `Project Adapter` during lifecycle execution expectations
- guides `AI Assistance Adapter` when generating or updating scripts
- supports `User Guide` examples and future setup documentation
