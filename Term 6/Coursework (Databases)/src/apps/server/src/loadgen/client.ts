import type {
  ClearRequest,
  LoadgenServiceHealth,
  LoadgenTarget,
  LoadgenRunSummary,
  RunRequest,
  SeedRequest,
  StorageModel,
} from "./contracts.js";
import { loadgenUrlForModel } from "./targets.js";
import Config from "../config.js";

class LoadgenHttpError extends Error {
  constructor(
    message: string,
    readonly status: number,
    readonly details: unknown,
  ) {
    super(message);
  }
}

async function requestLoadgen<TResponse>(
  model: StorageModel,
  path: "/clear" | "/seed" | "/run",
  body: ClearRequest | SeedRequest | RunRequest,
): Promise<TResponse> {
  const baseUrl = loadgenUrlForModel(model);
  const response = await fetch(new URL(path, baseUrl), {
    body: JSON.stringify(body),
    headers: {
      "Content-Type": "application/json",
    },
    method: "POST",
  });

  const payload = await response.json().catch(() => null) as unknown;

  if (!response.ok) {
    const message = payload && typeof payload === "object" && "error" in payload
      ? String(payload.error)
      : `Loadgen returned ${response.status}`;
    throw new LoadgenHttpError(message, response.status, payload);
  }

  return payload as TResponse;
}

export async function clearModel(req: ClearRequest) {
  return requestLoadgen<{ model: StorageModel; status: "ok" }>(req.model, "/clear", req);
}

export async function seedModel(req: SeedRequest) {
  return requestLoadgen<{ model: StorageModel; profile: string; seed: number; status: "ok" }>(
    req.model,
    "/seed",
    req,
  );
}

export async function runExperiment(req: RunRequest) {
  return requestLoadgen<LoadgenRunSummary>(req.model, "/run", req);
}

export function isLoadgenHttpError(error: unknown): error is LoadgenHttpError {
  return error instanceof LoadgenHttpError;
}

export function loadgenUrlForTarget(target: LoadgenTarget): string {
  return target === "postgres"
    ? Config.LOADGEN_POSTGRES_URL
    : Config.LOADGEN_MONGO_URL;
}

export async function checkLoadgenHealth(target: LoadgenTarget): Promise<{
  details?: string;
  health: LoadgenServiceHealth;
}> {
  const baseUrl = loadgenUrlForTarget(target);
  const controller = new AbortController();
  const timeout = setTimeout(() => controller.abort(), 1500);

  try {
    const response = await fetch(new URL("/health", baseUrl), {
      method: "GET",
      signal: controller.signal,
    });
    const details = await response.text().catch(() => "");

    return {
      details: details || undefined,
      health: response.ok ? "up" : "down",
    };
  } catch (error) {
    return {
      details: error instanceof Error ? error.message : "health request failed",
      health: "down",
    };
  } finally {
    clearTimeout(timeout);
  }
}
