# User Guide

## Purpose

This guide shows the intended OrchFlow usage flow from a user perspective.

## Example Scenario

A user wants to bring a local project under OrchFlow control so they can start, stop, inspect, and review it consistently from one place.

## End-To-End Flow

### 1. Sign In

The user signs in with an existing OrchFlow account through one of the available operational surfaces.

At the current implementation stage, the operational surfaces already implemented are:

- `CLI`
- `API`
- `web`

`CLI` and `API` remain the reference backend delivery surfaces, and the `web` interface now mirrors the first practical operator workflow on top of those same contracts, including registration of existing projects with compatible `.bat` lifecycle scripts.

- `member` users work with their permitted projects
- `admin` users can manage all projects and user permissions

### 2. Register A Project

The user chooses one of the supported registration paths.

#### Option A: Register From An Existing `.bat`

The user selects a project lifecycle `.bat` file that already defines how the project should be controlled.

At the current implementation stage, the selected script must support first-argument command dispatch for the effective lifecycle identifiers. For example, OrchFlow may execute `control.bat STATUS`, `control.bat START`, `control.bat STOP`, and `control.bat RESTART`, or mapped equivalents such as `control.bat INICIAR`.

The user then provides or confirms:

- a project reference name
- the project folder
- optional descriptive metadata
- any project-specific settings required by the lifecycle script
- any lifecycle action mappings needed when the script uses non-canonical labels

If the selected script only exposes an interactive menu or labels without first-argument dispatch, OrchFlow rejects the registration with guidance so the script can be adjusted before becoming an operational project definition.

The authenticated web workspace now exposes this existing-script registration flow directly. The form collects project reference name, optional description, project root path, lifecycle script path, and optional lifecycle action mappings for scripts that use identifiers different from `STATUS`, `START`, `STOP`, or `RESTART`.

#### Option B: Analyze A Folder With AI Assistance

The user selects a project folder and asks OrchFlow to assist with lifecycle setup.

OrchFlow then:

- asks for explicit authorization to inspect the selected project
- verifies that AI assistance is enabled and configured through the OrchFlow adapter
- uses LiteLLM as the planned gateway for the selected local or configured model provider
- starts or verifies a local provider process only when that behavior is explicitly configured
- lists available configured models or agents when the gateway supports that capability
- lets the user choose a model or agent
- analyzes only the project files and metadata explicitly allowed for the session
- suggests a `.bat` lifecycle script
- follows the documented lifecycle script template

OrchFlow then asks for explicit authorization before creating or overwriting the lifecycle `.bat` file.

The user reviews the generated suggestion and confirms or edits it before saving the project definition. AI output is treated as a proposal, not as verified operational truth.

If the project script uses different action names such as `iniciar`, `parar`, or `reiniciar`, the user can explicitly map them to OrchFlow canonical actions before finishing the registration.

### 3. Inspect Project Status

After registration, the user can inspect:

- current lifecycle state
- status explanation
- known ports
- application URL reachability when `APP_URL` is present
- active processes
- uptime
- CPU and memory usage
- inspection timestamp

At the current implementation stage, these inspection capabilities are already exposed through `CLI`, `API`, and the authenticated `web` workspace.

### 4. Control The Lifecycle

The user can request:

- `status`
- `start`
- `stop`
- `restart`

OrchFlow executes the action using the registered lifecycle `.bat` contract and records the event.

At the current implementation stage, these lifecycle actions are already available through the mirrored `CLI` and `API` surfaces, and the web workspace can trigger them for authenticated users, with runtime status summaries returned when inspection is available.

### 5. Review History

The user can review recent lifecycle activity and operational outcomes to understand what happened and when.

At the current implementation stage, recent audit history is available to authenticated admins through:

- `CLI`: `orchflow audit events --token <TOKEN> --limit 25`
- `API`: `GET /audit/events?limit=25`
- `web`: the audit history panel in the authenticated operator workspace

The first history view covers already recorded user registration, login, admin listing, project registration, project listing, project reads, and lifecycle action events.

## Operating Expectations

- A project should not be treated as fully managed unless it has a reviewable lifecycle `.bat` definition
- AI-assisted analysis is optional and does not bypass user review
- AI-assisted analysis must pass through explicit user authorization for inspection and file generation
- LiteLLM may provide model connectivity, but OrchFlow controls which data and files are shared with the selected model
- Permissions determine which users can view and control each project

## Admin Workflow

An `admin` can additionally:

- view platform users
- update user role and activation state
- review recent audit history
- add or remove project owners while keeping at least one owner per project
- inspect projects across the system
- troubleshoot access and operational issues

The mirrored admin commands now include:

- `CLI`: `orchflow auth update-user --token <TOKEN> --user-id <ID> --role admin`
- `CLI`: `orchflow project add-owner --token <TOKEN> --project-id <ID> --user-id <ID>`
- `CLI`: `orchflow project remove-owner --token <TOKEN> --project-id <ID> --user-id <ID>`
- `API`: `PATCH /auth/users/{user_id}`
- `API`: `POST /projects/{project_id}/owners/{user_id}`
- `API`: `DELETE /projects/{project_id}/owners/{user_id}`
- `web`: the admin management panel in the authenticated operator workspace
