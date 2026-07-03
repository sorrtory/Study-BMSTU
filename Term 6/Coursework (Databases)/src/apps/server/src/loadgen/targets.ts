import Config from "../config.js";
import type { StorageModel } from "./contracts.js";

type TargetDB = "postgres" | "mongo";

const postgresModels = new Set<StorageModel>(["pg-jsonb", "pg-normalized"]);
const mongoModels = new Set<StorageModel>(["mongo-nested", "mongo-normalized"]);

export function targetForModel(model: StorageModel): TargetDB {
  if (postgresModels.has(model)) {
    return "postgres";
  }

  if (mongoModels.has(model)) {
    return "mongo";
  }

  throw new Error(`Unsupported model: ${model}`);
}

export function loadgenUrlForModel(model: StorageModel): string {
  return targetForModel(model) === "postgres"
    ? Config.LOADGEN_POSTGRES_URL
    : Config.LOADGEN_MONGO_URL;
}
