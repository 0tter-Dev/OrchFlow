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

The target workflow is for OrchFlow to compare the script against an ideal lifecycle function model. The initial ideal model includes `status`, `start`, `stop`, and `restart`, each with a clear operational purpose. When a `.bat` script is connected, OrchFlow attempts to detect matching functions automatically. Functions it can match become configured. Functions it cannot match start as undefined until the user manually maps them or explicitly marks them as unconfigured through the API or CLI.

If every ideal lifecycle function remains undefined or unconfigured, OrchFlow should block the project from operational use because it has no executable lifecycle control path. If at least one function is configured, the project remains usable for its configured actions. Missing functions should appear as warnings rather than hard blockers, with a path to manual mapping and a path to AI-assisted `.bat` improvement.

If all ideal lifecycle functions are configured, OrchFlow communicates that the project has complete lifecycle configuration.

Manual lifecycle configuration currently replaces the function configuration set for a project. The user can map one or more ideal functions to concrete script identifiers, or mark one or more functions as explicitly unconfigured. At least one function must remain configured.

If the selected script only exposes an interactive menu or labels without a usable dispatch path, OrchFlow should guide the user to map available functions manually or improve the script before it can become operationally controllable.

The authenticated web workspace now exposes this existing-script registration flow directly. The form collects project reference name, optional description, project root path, lifecycle script path, and optional lifecycle action mappings for scripts that use identifiers different from `STATUS`, `START`, `STOP`, or `RESTART`.

#### Option B: Analyze A Folder With AI Assistance

The user selects a project folder and asks OrchFlow to assist with lifecycle setup.

OrchFlow then:

- asks for explicit authorization to inspect the selected project
- verifies that AI assistance is enabled and configured through the OrchFlow adapter
- uses LiteLLM as the gateway for the selected local or configured model provider
- starts or verifies a local provider process only when that behavior is explicitly configured
- lists available configured models or agents when the gateway supports that capability
- lets the user choose a model or agent
- analyzes only the project files and metadata explicitly allowed for the session
- suggests a `.bat` lifecycle script
- follows the documented lifecycle script template

OrchFlow then asks for explicit authorization before creating or overwriting the lifecycle `.bat` file.

The user reviews the generated suggestion and confirms or edits it before saving the project definition. AI output is treated as a proposal, not as verified operational truth.

If the project script uses different action names such as `iniciar`, `parar`, or `reiniciar`, the user can explicitly map them to OrchFlow canonical actions before finishing the registration.

At the current implementation stage, the AI assistance flow exposes safe status, LiteLLM gateway health, model discovery checks, authorized context manifests, reviewable analysis proposals, API/CLI proposal reviews, and confirmed proposal application. Authenticated users can run `orchflow ai status --token <TOKEN>`, `orchflow ai health --token <TOKEN>`, `orchflow ai models --token <TOKEN>`, `orchflow ai manifest-create --token <TOKEN> --project-id <ID> --selected-model <MODEL> --intended-operation improve_lifecycle_script`, `orchflow ai manifest-show --token <TOKEN> --manifest-id <ID>`, `orchflow ai proposal-create --token <TOKEN> --manifest-id <ID>`, `orchflow ai proposal-show --token <TOKEN> --proposal-id <ID>`, `orchflow ai proposal-review --token <TOKEN> --proposal-id <ID> --decision approved`, and `orchflow ai proposal-apply --token <TOKEN> --proposal-id <ID> --confirm-file-write --confirm-mapping-persistence`, or call `GET /ai/status`, `GET /ai/gateway/health`, `GET /ai/models`, `POST /ai/context-manifests`, `GET /ai/context-manifests/{manifest_id}`, `POST /ai/analysis-proposals`, `GET /ai/analysis-proposals/{proposal_id}`, `POST /ai/analysis-proposals/{proposal_id}/review`, and `POST /ai/analysis-proposals/{proposal_id}/apply`. Context manifests record authorization metadata without storing file contents. Proposal creation may send only manifest-approved context to LiteLLM, records audit events, and persists structured proposal output for review without writing `.bat` scripts. Proposal approval validates first-argument dispatch, required canonical actions, and proposed mapping consistency before recording the review decision. Proposal application is separate from approval and requires explicit file-write plus mapping-persistence confirmations before writing the lifecycle `.bat`, saving effective mappings as `ai_approved`, and recording application audit details.

### 2.1. Reload Project Configuration

When a user changes a project's `.bat` script or updates the project structure, the implemented workflow lets the user explicitly reload one project or a selected group of projects through `API` and `CLI`.

Reloading rereads the lifecycle script, refreshes automatic detection against the ideal lifecycle model, preserves valid user-defined or AI-approved decisions where the referenced script handler still exists, keeps explicit `unconfigured` decisions, and shows whether the project is fully configured, partially configured with warnings, or blocked because no lifecycle function is configured.

Available backend commands include:

- `CLI`: `orchflow project reload --token <TOKEN> --project-id <ID>`
- `CLI`: `orchflow project reload-many --token <TOKEN> --project-id <ID> --project-id <ID>`
- `API`: `POST /projects/{project_id}/reload`
- `API`: `POST /projects/reload`

### 3. Inspect Project Status

After registration, the user can inspect:

- current lifecycle state
- status explanation
- known ports
- application URL reachability when `APP_URL` is present, including `APP_URL`-only projects without `APP_PORT`
- active processes
- uptime
- CPU and memory usage
- inspection timestamp

At the current implementation stage, these inspection capabilities are already exposed through `CLI`, `API`, and the authenticated `web` workspace. If a script has no `APP_PORT` but does define `APP_URL`, OrchFlow uses URL reachability as the runtime signal. If neither runtime hint exists, OrchFlow reports `unsupported` with an explanation instead of implying the project is stopped. URL timeout and reachability failures are included in the status explanation.

### 4. Control The Lifecycle

The user can request:

- `status`
- `start`
- `stop`
- `restart`

OrchFlow executes the action using the registered lifecycle `.bat` contract and records the event.

Only configured lifecycle actions can be executed. If the user requests an undefined action, an explicitly unconfigured action, or any action on a project with no configured lifecycle functions, OrchFlow rejects the request before calling the `.bat` adapter and records an audit event explaining why the action was blocked.

At the current implementation stage, configured lifecycle actions are available through the mirrored `CLI` and `API` surfaces, and the web workspace can trigger only configured actions for authenticated users, with runtime status summaries returned when inspection is available.

The web project detail view also shows lifecycle configuration health, function-level configured or missing states, a reload action for rereading the `.bat` script, and a manual configuration dialog for mapping script labels or explicitly leaving ideal functions unconfigured.

### 4.1. Update A Registered Project

When a project changes after registration, the implemented backend workflow lets an authorized user update project metadata, the lifecycle script path, and lifecycle action mappings without using AI assistance.

Available backend commands include:

- `CLI`: `orchflow project update --token <TOKEN> --project-id <ID> --reference-name <NAME>`
- `CLI`: `orchflow project update --token <TOKEN> --project-id <ID> --lifecycle-script-path <PATH> --map-start START`
- `API`: `PATCH /projects/{project_id}`

The update path reuses lifecycle script validation, preserves audit details, and keeps the project blocked from operational use if the submitted lifecycle configuration leaves no executable lifecycle function.

The authenticated web workspace now exposes project settings from the project detail view. Operators can update the reference name, optional description, project root path, and lifecycle script path through the same backend update contract, while lifecycle mappings remain editable through the lifecycle configuration dialog.

### 5. Review History

The user can review recent lifecycle activity and operational outcomes to understand what happened and when.

At the current implementation stage, recent audit history is available to authenticated admins through:

- `CLI`: `orchflow audit events --token <TOKEN> --limit 25 --project-id <ID> --actor-user-id <ID> --action project.register --created-from <ISO_DATETIME> --created-to <ISO_DATETIME>`
- `API`: `GET /audit/events?limit=25&project_id=<ID>&actor_user_id=<ID>&action=project.register&created_from=<ISO_DATETIME>&created_to=<ISO_DATETIME>`
- `web`: the audit history panel in the authenticated operator workspace, including compact filters for limit, actor, action, project, and time window

The history view covers already recorded user registration, login, admin listing, project registration, project listing, project reads, lifecycle action events, project updates, ownership changes, AI assistance events, and audit list activity. Admins can narrow the view by actor, action, project target, and time window for troubleshooting.

## Operating Expectations

- A project should not be treated as fully managed unless it has a reviewable lifecycle `.bat` definition
- A project should expose at least one configured lifecycle function before it can be operated through OrchFlow
- Partially configured projects can remain usable, but the interface should warn users about missing ideal lifecycle functions
- AI-assisted analysis is optional and does not bypass user review
- AI-assisted analysis must pass through explicit user authorization for inspection and file generation
- LiteLLM may provide model connectivity, but OrchFlow controls which data and files are shared with the selected model
- Permissions determine which users can view and control each project

## Admin Workflow

An `admin` can additionally:

- view platform users
- update user role and activation state
- review recent audit history
- filter recent audit history by actor, action, project, and time window
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
