# AI Assistance Adapter

## Purpose

This module defines the optional AI assistance adapter layer used to control project analysis and lifecycle script generation through a review-driven OrchFlow workflow.

## Objective

Help the user analyze a project folder and produce a reviewable lifecycle `.bat` script proposal without coupling OrchFlow business rules to a single AI provider or allowing model output to bypass user approval.

## Current Status

`in_progress`

## LiteLLM Gateway Direction

OrchFlow should use `LiteLLM` as the central gateway for LLM, model, and agent connectivity.

LiteLLM may provide provider routing, OpenAI-compatible request and response handling, local `Ollama` connectivity, retries, fallback, cost tracking, rate limits, virtual keys, and gateway observability when those capabilities are configured.

LiteLLM is not the OrchFlow AI product boundary. The OrchFlow adapter remains responsible for deciding which files and metadata can be sent to a model, requesting explicit user authorization, shaping prompts, validating responses, requiring review before writes, and recording audit events.

## Implementation Shape

The first implementation should prefer a minimal integration path:

1. define an OrchFlow-owned AI assistance boundary
2. define a LiteLLM gateway client behind that boundary
3. support a disabled-by-default configuration contract
4. expose authenticated, audited status through API and CLI without model requests
5. verify configured model availability without sending project files
6. create authorized analysis sessions that return proposals only
7. add file generation and mapping persistence only after proposal review is implemented

The first seven items are implemented in `v0.3.17`. The current boundary can report whether AI assistance is disabled, configured, or misconfigured, verify LiteLLM gateway health when gateway mode is configured, list models when the gateway supports discovery, persist authorized context manifests with included paths, excluded paths, ignored/generated artifacts, secret filtering rules, size limits, selected model, requesting user, and intended operation, create structured analysis proposals from manifest-approved context, record proposal review decisions, and apply approved proposals through a separate confirmed operation. The web workspace now consumes the same status, manifest, proposal, review, and apply contracts for authenticated operators, including contextual API and validation error notices when backend requests fail. Proposal creation may send only the approved context listed in the manifest to LiteLLM and persists lifecycle strategy, runtime hints, candidate `.bat` content, proposed action mappings, and warnings for review. Proposal approval validates first-argument dispatch, required canonical actions, and proposed mapping consistency before accepting the approval. Proposal application requires explicit file-write and mapping-persistence confirmations, writes or overwrites the lifecycle `.bat`, expands effective mappings for ideal labels that were omitted from the proposal payload, persists mappings as `ai_approved`, and records a dedicated application record plus audit event. Focused API contract tests now lock the external AI route behavior for authentication, request validation, response shapes, and explicit application confirmations.

## Scope

- define an OrchFlow-owned AI assistance boundary for review-driven onboarding
- integrate `LiteLLM` as the central model/provider gateway behind the boundary
- support local providers such as `Ollama` through LiteLLM when configured
- verify whether AI assistance is enabled and whether the configured gateway is available
- start or verify a local provider process only when explicitly configured
- list configured models or agents when supported by the LiteLLM mode in use
- let the user choose a model or agent
- analyze only explicitly authorized files and metadata from a selected project folder
- suggest a lifecycle `.bat` script for user review
- suggest improvements that move a project closer to the ideal lifecycle function model
- follow the documented lifecycle script template when generating or updating scripts
- suggest canonical lifecycle labels when possible
- detect non-canonical labels in existing scripts and suggest action mappings for user approval
- explain missing, undefined, or explicitly unconfigured lifecycle functions in operator-friendly language
- validate model responses into structured, reviewable proposals before any persistence or file write
- apply only approved and valid proposals through a separate confirmed operation that revalidates the candidate script before writing

## Adapter Responsibilities

- create and enforce an allowed-context manifest for each AI analysis session
- exclude secrets, ignored files, generated artifacts, large binary files, and unauthorized paths from model context
- keep prompt construction in application-level services rather than CLI, API, or UI components
- normalize model output into explicit proposal objects
- include the ideal lifecycle model and the project's current function configuration state when requesting improvement proposals
- validate proposed `.bat` scripts against the lifecycle script template and first-argument dispatch expectations
- require user approval before writing or overwriting files
- require user approval before persisting AI-suggested mappings
- audit authorization, analysis request metadata, proposal creation, approval, rejection, file writes, and mapping persistence
- record which approved proposal application wrote a lifecycle script and which effective mappings became operational

## LiteLLM Responsibilities

- connect to configured local or remote model providers
- provide model invocation through a stable gateway/client interface
- support provider-specific authentication through environment configuration
- optionally support retries, fallback, cost tracking, rate limiting, virtual keys, and gateway observability

LiteLLM must not decide which project files are allowed, approve generated scripts, persist project definitions, execute lifecycle actions, or mutate managed projects directly.

## Authorization Rules

- OrchFlow must request explicit user authorization before AI inspection of a project begins
- authorization must identify the project folder, selected file/context scope, model or agent target, and intended operation
- OrchFlow must request explicit user authorization before creating or overwriting a lifecycle `.bat` file
- OrchFlow must request explicit user authorization before persisting AI-suggested action mappings
- AI outputs must remain reviewable before they become part of a project definition
- rejected proposals must not be persisted as operational project definitions
- approved proposals must not mutate project files or mappings until the user explicitly confirms the application step

## Key Rules

- OrchFlow must not download new models automatically
- AI assistance must remain optional
- AI analysis supports registration but does not replace the lifecycle script contract
- the adapter boundary must isolate LiteLLM and future provider/gateway changes from core business rules
- no delivery adapter should call LiteLLM directly
- AI should prefer standard label conventions, but must tolerate project-specific variations through the `Project Adapter`
- AI assistance should be able to propose mappings or script changes for partially configured projects, but the user remains the final approver
- AI-generated claims about runtime behavior must be treated as suggestions until validated by OrchFlow rules and, where practical, runtime inspection

## Main Relationships

- supports `Project Registry`
- may propose mapping data consumed by `Project Adapter`
- may use information from `Runtime Inspection` within approved boundaries
- may surface information through `External Surfaces`
- may surface proposal review and application through `Interface Layer`
- is governed by `Project Architecture` scope boundaries
- depends on `Configuration And Environment` for LiteLLM gateway settings
- depends on `Persistence And Audit` for session, proposal, authorization, approval, rejection, and application records
