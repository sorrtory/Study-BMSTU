import { z } from "zod";
import type { ExperimentState } from "./state.js";

export const models = [
  "pg-jsonb",
  "pg-normalized",
  "mongo-nested",
  "mongo-normalized",
] as const;

export const scenarios = ["write-heavy", "analytics-heavy", "balanced"] as const;
export const profiles = ["small", "medium", "large"] as const;

export const modelSchema = z.enum(models);
export const scenarioSchema = z.enum(scenarios);
export const profileSchema = z.enum(profiles);

export const clearRequestSchema = z.object({
  model: modelSchema,
});

export const seedRequestSchema = z.object({
  model: modelSchema,
  profile: profileSchema.default("small"),
  seed: z.coerce.number().int().positive().default(42),
});

export const runRequestSchema = z.object({
  model: modelSchema,
  scenario: scenarioSchema.default("balanced"),
  profile: profileSchema.default("small"),
  seed: z.coerce.number().int().positive().default(42),
  run_id: z.string().min(1).optional(),
  duration_seconds: z.coerce.number().int().min(1).max(3600).default(60),
  stages: z.array(z.coerce.number().int().min(1).max(1000)).min(1).default([1, 5, 10, 25]),
  event_batch_size: z.coerce.number().int().min(1).max(10000).default(25),
  telemetry_batch_size: z.coerce.number().int().min(1).max(10000).default(50),
});

export const prepareRequestSchema = seedRequestSchema;

export type StorageModel = z.infer<typeof modelSchema>;
export type LoadScenario = z.infer<typeof scenarioSchema>;
export type SizeProfile = z.infer<typeof profileSchema>;
export type ClearRequest = z.infer<typeof clearRequestSchema>;
export type SeedRequest = z.infer<typeof seedRequestSchema>;
export type RunRequest = z.infer<typeof runRequestSchema>;
export type PrepareRequest = z.infer<typeof prepareRequestSchema>;

export interface LoadgenRunSummary {
  run_id: string;
  model: StorageModel;
  scenario: LoadScenario;
  started_at: string;
  finished_at: string;
  stages: unknown[];
  totals: Record<string, unknown>;
}

export interface GrafanaLinks {
  dashboard: string;
  embed: string;
}

export type LoadgenTarget = "postgres" | "mongo";
export type LoadgenServiceMode = "idle" | "busy" | "running";
export type LoadgenServiceHealth = "up" | "down";

export interface LoadgenServiceStatus {
  target: LoadgenTarget;
  title: string;
  url: string;
  health: LoadgenServiceHealth;
  mode: LoadgenServiceMode;
  checked_at: string;
  details?: string;
}

export interface StandStatus {
  experiment: ExperimentState;
  services: LoadgenServiceStatus[];
  grafana: GrafanaLinks;
}
