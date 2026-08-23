# AI Agent Adapter

## Purpose

This module defines the optional AI adapter layer used to assist project analysis and lifecycle script generation.

## Objective

Help the user analyze a project folder and produce a reviewable lifecycle `.bat` script proposal without coupling OrchFlow to a single AI provider.

## Current Status

`planned`

## Scope

- define a provider-agnostic adapter boundary for AI integrations
- support an initial local provider direction such as `Ollama`
- verify whether an enabled provider is available
- start a local provider process if needed
- list already available models or agents when supported
- let the user choose a model or agent
- analyze a selected project folder
- suggest a lifecycle `.bat` script for user review

## Authorization Rules

- OrchFlow must request explicit user authorization before AI inspection of a project begins
- OrchFlow must request explicit user authorization before creating or overwriting a lifecycle `.bat` file
- AI outputs must remain reviewable before they become part of a project definition

## Key Rules

- OrchFlow must not download new models automatically
- AI assistance must remain optional
- AI analysis supports registration but does not replace the lifecycle script contract
- the adapter boundary must allow future providers to be added without changing core business rules significantly

## Main Relationships

- supports `Project Registry`
- may use information from `Runtime Inspection` within approved boundaries
- may surface information through `External Surfaces`
- is governed by `Project Architecture` scope boundaries
