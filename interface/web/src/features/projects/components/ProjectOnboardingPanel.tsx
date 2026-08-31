import "./ProjectOnboardingPanel.css";

import type {
  LifecycleConfigurationHealth,
  ProjectSummary,
  RuntimeInspectionSnapshot,
} from "../../../shared/types/project";

type OnboardingStepState = "complete" | "attention" | "blocked";

type ProjectOnboardingPanelProps = {
  isLoadingRuntime: boolean;
  isReloadingProject: boolean;
  onConfigureMappings: () => void;
  onRefreshRuntime: () => void;
  onReloadProject: () => void;
  project: ProjectSummary;
  runtimeSnapshot: RuntimeInspectionSnapshot | null;
};

type OnboardingStep = {
  action?: {
    disabled?: boolean;
    label: string;
    onClick: () => void;
  };
  detail: string;
  id: string;
  label: string;
  state: OnboardingStepState;
};

function lifecycleDetail(health: LifecycleConfigurationHealth): string {
  if (health === "complete") {
    return "All ideal functions resolve to script labels.";
  }
  if (health === "partial") {
    return "At least one action works, with remaining functions still open.";
  }
  return "No lifecycle action is currently executable.";
}

function runtimeStepState(
  runtimeSnapshot: RuntimeInspectionSnapshot | null,
): OnboardingStepState {
  if (runtimeSnapshot === null) {
    return "attention";
  }
  if (runtimeSnapshot.status === "unsupported") {
    return "attention";
  }
  return "complete";
}

function reviewStepState(health: LifecycleConfigurationHealth): OnboardingStepState {
  if (health === "complete") {
    return "complete";
  }
  if (health === "blocked") {
    return "blocked";
  }
  return "attention";
}

function buildProjectOnboardingSteps({
  isLoadingRuntime,
  isReloadingProject,
  onConfigureMappings,
  onRefreshRuntime,
  onReloadProject,
  project,
  runtimeSnapshot,
}: ProjectOnboardingPanelProps): OnboardingStep[] {
  const missingFunctionCount = project.lifecycle_function_configurations.filter(
    (configuration) => configuration.state !== "configured",
  ).length;

  return [
    {
      action: {
        disabled: isReloadingProject,
        label: isReloadingProject ? "Reloading..." : "Reload script",
        onClick: onReloadProject,
      },
      detail: project.lifecycle_script_path,
      id: "script",
      label: "Lifecycle script connected",
      state: "complete",
    },
    {
      action:
        project.lifecycle_configuration_health === "complete"
          ? undefined
          : {
              label: "Open mappings",
              onClick: onConfigureMappings,
            },
      detail:
        project.lifecycle_configuration_health === "complete"
          ? lifecycleDetail(project.lifecycle_configuration_health)
          : `${lifecycleDetail(project.lifecycle_configuration_health)} Missing functions: ${missingFunctionCount}.`,
      id: "lifecycle",
      label: "Lifecycle action readiness",
      state: project.lifecycle_configuration_health === "blocked" ? "blocked" : "complete",
    },
    {
      action: {
        disabled: isLoadingRuntime,
        label: isLoadingRuntime ? "Refreshing..." : "Refresh runtime",
        onClick: onRefreshRuntime,
      },
      detail:
        runtimeSnapshot === null
          ? "Runtime inspection has not returned a snapshot."
          : `Current signal: ${runtimeSnapshot.status_reason}`,
      id: "runtime",
      label: "Runtime diagnostics",
      state: runtimeStepState(runtimeSnapshot),
    },
    {
      detail:
        project.lifecycle_configuration_health === "complete"
          ? "AI proposal review remains available for controlled script improvements."
          : "Use manual mappings or the AI proposal panel before applying script changes.",
      id: "review",
      label: "Review path",
      state: reviewStepState(project.lifecycle_configuration_health),
    },
  ];
}

export function ProjectOnboardingPanel(props: ProjectOnboardingPanelProps) {
  const steps = buildProjectOnboardingSteps(props);
  const blockedCount = steps.filter((step) => step.state === "blocked").length;
  const attentionCount = steps.filter((step) => step.state === "attention").length;
  const readinessLabel =
    blockedCount > 0 ? "Blocked" : attentionCount > 0 ? "Needs review" : "Ready";

  return (
    <section className="project-onboarding" aria-label="Operational readiness">
      <header className="project-onboarding__header">
        <h3 className="project-onboarding__title">Operational readiness</h3>
        <span className="project-onboarding__status">{readinessLabel}</span>
      </header>
      <div className="project-onboarding__steps">
        {steps.map((step) => (
          <article className="project-onboarding__step" data-state={step.state} key={step.id}>
            <span className="project-onboarding__marker" aria-hidden="true" />
            <div>
              <strong>{step.label}</strong>
              <span>{step.detail}</span>
            </div>
            {step.action === undefined ? null : (
              <button
                className="project-onboarding__button"
                disabled={step.action.disabled}
                onClick={step.action.onClick}
                type="button"
              >
                {step.action.label}
              </button>
            )}
          </article>
        ))}
      </div>
    </section>
  );
}
