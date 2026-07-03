import * as z from "zod";
import dotenv from "dotenv";
import path from "path";
import { fileURLToPath } from "url";

// Load project root .env
const __filename = fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename);


const envPath = path.resolve(__dirname, "../../../.env");
dotenv.config({
  path: envPath,
});
console.log(`Loaded environment variables from ${envPath}`);


const cfg = z.object({
    EXPRESS_HOST: z.string(),
    EXPRESS_PORT: z.coerce.number().min(1000).max(65535),
    EXPRESS_CORS_ORIGIN: z.string().optional(),
    LOADGEN_POSTGRES_URL: z.string().url(),
    LOADGEN_MONGO_URL: z.string().url(),
    GRAFANA_URL: z.string().url(),
});


const Config = cfg.parse(process.env);
export default Config;
