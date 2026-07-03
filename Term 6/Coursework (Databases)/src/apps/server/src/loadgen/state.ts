import type { GrafanaLinks, LoadgenRunSummary, RunRequest, StorageModel } from "./contracts.js";

export type ExperimentPhase = "idle" | "clearing" | "seeding" | "running" | "finished" | "failed";

export interface ExperimentState {
  phase: ExperimentPhase;
  active: boolean;
  model?: StorageModel;
  run_id?: string;
  request?: RunRequest;
  summary?: LoadgenRunSummary;
  grafana?: GrafanaLinks;
  error?: string;
  started_at?: string;
  finished_at?: string;
}

const state: ExperimentState = {
  active: false,
  phase: "idle",
};

export function getExperimentState(): ExperimentState {
  return { ...state };
}

export function ensureExperimentIsIdle() {
  if (state.active) {
    throw new Error(`Experiment action is already in progress: ${state.phase}`);
  }
}

export function startAction(
  phase: Extract<ExperimentPhase, "clearing" | "seeding" | "running">,
  model: StorageModel,
  request?: RunRequest,
  grafana?: GrafanaLinks,
) {
  state.active = true;
  state.phase = phase;
  state.model = model;
  state.request = request;
  state.summary = undefined;
  state.grafana = grafana;
  state.error = undefined;
  state.started_at = new Date().toISOString();
  state.finished_at = undefined;
  state.run_id = request?.run_id;
}

export function finishAction(summary?: LoadgenRunSummary, grafana?: GrafanaLinks) {
  state.active = false;
  state.phase = "finished";
  state.summary = summary;
  state.grafana = grafana;
  state.run_id = summary?.run_id ?? state.run_id;
  state.finished_at = new Date().toISOString();
}

export function failAction(error: string) {
  state.active = false;
  state.phase = "failed";
  state.error = error;
  state.finished_at = new Date().toISOString();
}
