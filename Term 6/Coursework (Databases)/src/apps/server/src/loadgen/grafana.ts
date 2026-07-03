import Config from "../config.js";
import type { RunRequest } from "./contracts.js";

export function buildGrafanaLinks(req: Pick<RunRequest, "model" | "scenario"> & { run_id?: string }) {
  const url = new URL("/d/loadgen-experiment/loadgen-experiment", Config.GRAFANA_URL);

  if (req.run_id) {
    url.searchParams.set("var-run_id", req.run_id);
  }

  url.searchParams.set("var-model", req.model);
  url.searchParams.set("var-scenario", req.scenario);

  const embedUrl = new URL(url.toString());
  embedUrl.searchParams.set("kiosk", "");
  embedUrl.searchParams.set("refresh", "5s");
  embedUrl.searchParams.set("theme", "light");

  return {
    dashboard: url.toString(),
    embed: embedUrl.toString(),
  };
}
