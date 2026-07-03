import { Router, type NextFunction, type Request, type Response } from "express";
import { z } from "zod";
import {
  clearRequestSchema,
  type LoadgenServiceMode,
  type LoadgenTarget,
  models,
  prepareRequestSchema,
  profiles,
  runRequestSchema,
  scenarios,
  seedRequestSchema,
} from "./contracts.js";
import {
  checkLoadgenHealth,
  clearModel,
  isLoadgenHttpError,
  loadgenUrlForTarget,
  runExperiment,
  seedModel,
} from "./client.js";
import { buildGrafanaLinks } from "./grafana.js";
import {
  ensureExperimentIsIdle,
  failAction,
  finishAction,
  getExperimentState,
  startAction,
} from "./state.js";
import { targetForModel } from "./targets.js";

const router = Router();

function asyncHandler(
  handler: (req: Request, res: Response) => Promise<void>,
) {
  return (req: Request, res: Response, next: NextFunction) => {
    handler(req, res).catch(next);
  };
}

router.get("/options", (_req, res) => {
  res.json({
    defaults: {
      duration_seconds: 60,
      event_batch_size: 25,
      profile: "small",
      scenario: "balanced",
      seed: 42,
      stages: [1, 5, 10, 25],
      telemetry_batch_size: 50,
    },
    models,
    profiles,
    scenarios,
  });
});

router.get("/status", (_req, res) => {
  res.json(getExperimentState());
});

router.get("/stand", asyncHandler(async (_req, res) => {
  const experiment = getExperimentState();
  const services = await Promise.all((["postgres", "mongo"] as const).map(async (target) => {
    const health = await checkLoadgenHealth(target);

    return {
      ...health,
      checked_at: new Date().toISOString(),
      mode: serviceMode(target, experiment),
      target,
      title: target === "postgres" ? "PostgreSQL loadgen" : "MongoDB loadgen",
      url: loadgenUrlForTarget(target),
    };
  }));

  res.json({
    experiment,
    grafana: experiment.grafana ?? buildGrafanaLinks({
      model: experiment.model ?? "pg-jsonb",
      run_id: experiment.run_id,
      scenario: experiment.request?.scenario ?? "balanced",
    }),
    services,
  });
}));

router.post("/clear", asyncHandler(async (req, res) => {
  const payload = clearRequestSchema.parse(req.body);
  ensureExperimentIsIdle();
  startAction("clearing", payload.model);

  try {
    const result = await clearModel(payload);
    finishAction();
    res.json({
      ...result,
      state: getExperimentState(),
    });
  } catch (error) {
    failAction(errorMessage(error));
    throw error;
  }
}));

router.post("/seed", asyncHandler(async (req, res) => {
  const payload = seedRequestSchema.parse(req.body);
  ensureExperimentIsIdle();
  startAction("seeding", payload.model);

  try {
    const result = await seedModel(payload);
    finishAction();
    res.json({
      ...result,
      state: getExperimentState(),
    });
  } catch (error) {
    failAction(errorMessage(error));
    throw error;
  }
}));

router.post("/prepare", asyncHandler(async (req, res) => {
  const payload = prepareRequestSchema.parse(req.body);
  ensureExperimentIsIdle();
  startAction("clearing", payload.model);

  try {
    const clear = await clearModel({ model: payload.model });
    startAction("seeding", payload.model);
    const seed = await seedModel(payload);
    finishAction();
    res.json({
      clear,
      seed,
      state: getExperimentState(),
    });
  } catch (error) {
    failAction(errorMessage(error));
    throw error;
  }
}));

router.post("/run", asyncHandler(async (req, res) => {
  const payload = withRunId(runRequestSchema.parse(req.body));
  ensureExperimentIsIdle();
  const initialGrafana = buildGrafanaLinks(payload);
  startAction("running", payload.model, payload, initialGrafana);

  try {
    const summary = await runExperiment(payload);
    const grafana = buildGrafanaLinks({
      model: summary.model,
      run_id: summary.run_id,
      scenario: summary.scenario,
    });
    finishAction(summary, grafana);
    res.json({
      grafana,
      state: getExperimentState(),
      summary,
    });
  } catch (error) {
    failAction(errorMessage(error));
    throw error;
  }
}));

router.use((error: unknown, _req: Request, res: Response, _next: NextFunction) => {
  if (error instanceof z.ZodError) {
    res.status(400).json({
      details: z.treeifyError(error),
      message: "Invalid loadgen request",
    });
    return;
  }

  if (isLoadgenHttpError(error)) {
    res.status(502).json({
      details: error.details,
      message: error.message,
    });
    return;
  }

  if (error instanceof Error && error.message.includes("already in progress")) {
    res.status(409).json({
      message: error.message,
      state: getExperimentState(),
    });
    return;
  }

  res.status(500).json({
    message: errorMessage(error),
  });
});

function errorMessage(error: unknown) {
  return error instanceof Error ? error.message : "Unknown loadgen error";
}

function serviceMode(target: LoadgenTarget, experiment: ReturnType<typeof getExperimentState>): LoadgenServiceMode {
  if (!experiment.active || !experiment.model) {
    return "idle";
  }

  if (targetForModel(experiment.model) !== target) {
    return "idle";
  }

  return experiment.phase === "running" ? "running" : "busy";
}

function withRunId(payload: ReturnType<typeof runRequestSchema.parse>) {
  if (payload.run_id) {
    return payload;
  }

  const timestamp = new Date()
    .toISOString()
    .replace("T", "_")
    .replace(/\.\d{3}Z$/, "")
    .replaceAll(":", "-");

  return {
    ...payload,
    run_id: `${timestamp}_${payload.model}_${payload.scenario}_seed-${payload.seed}`,
  };
}

export default router;
