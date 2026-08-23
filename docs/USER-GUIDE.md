# User Guide

## Purpose

This guide shows the intended OrchFlow usage flow from a user perspective.

## Example Scenario

A user wants to bring a local project under OrchFlow control so they can start, stop, inspect, and review it consistently from one place.

## End-To-End Flow

### 1. Sign In

The user signs in with an existing OrchFlow account.

- `member` users work with their permitted projects
- `admin` users can manage all projects and user permissions

### 2. Register A Project

The user chooses one of the supported registration paths.

#### Option A: Register From An Existing `.bat`

The user selects a project lifecycle `.bat` file that already defines how the project should be controlled.

The user then provides or confirms:

- a project reference name
- the project folder
- optional descriptive metadata
- any project-specific settings required by the lifecycle script
- any lifecycle action mappings needed when the script uses non-canonical labels

#### Option B: Analyze A Folder With An AI Agent Adapter

The user selects a project folder and asks OrchFlow to assist with lifecycle setup.

OrchFlow then:

- asks for explicit authorization to inspect the selected project
- verifies that an enabled local AI provider is available through the adapter layer
- starts the provider process if necessary
- lists already available models or agents when the provider supports that capability
- lets the user choose a model or agent
- analyzes the project folder
- suggests a `.bat` lifecycle script
- follows the documented lifecycle script template

OrchFlow then asks for explicit authorization before creating or overwriting the lifecycle `.bat` file.

The user reviews the generated suggestion and confirms or edits it before saving the project definition.

If the project script uses different action names such as `iniciar`, `parar`, or `reiniciar`, the user can explicitly map them to OrchFlow canonical actions before finishing the registration.

### 3. Inspect Project Status

After registration, the user can inspect:

- current lifecycle state
- known ports
- active processes
- uptime
- CPU and memory usage

### 4. Control The Lifecycle

The user can request:

- `status`
- `start`
- `stop`
- `restart`

OrchFlow executes the action using the registered lifecycle `.bat` contract and records the event.

### 5. Review History

The user can review recent lifecycle activity and operational outcomes to understand what happened and when.

## Operating Expectations

- A project should not be treated as fully managed unless it has a reviewable lifecycle `.bat` definition
- AI-assisted analysis is optional and does not bypass user review
- AI-assisted analysis must pass through explicit user authorization for inspection and file generation
- Permissions determine which users can view and control each project

## Admin Workflow

An `admin` can additionally:

- view platform users
- manage user permissions
- inspect projects across the system
- troubleshoot access and operational issues
