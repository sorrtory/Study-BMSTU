import express from "express";
import cors from "cors";
import Config from "./config.js";
import loadgenRouter from "./loadgen/router.js";

export function createApp() {
  const app = express();

  app.use(cors({
    origin: corsOrigin,
  }));
  app.use(express.json());

  app.get("/api/hello", (_req, res) => {
    res.json({ message: "Hello from Express + TypeScript" });
  });

  app.use("/api/loadgen", loadgenRouter);

  return app;
}

function corsOrigin(origin: string | undefined, callback: (error: Error | null, allow?: boolean) => void) {
  if (!origin) {
    callback(null, true);
    return;
  }

  const configuredOrigins = Config.EXPRESS_CORS_ORIGIN
    ? Config.EXPRESS_CORS_ORIGIN.split(",").map((item) => item.trim()).filter(Boolean)
    : [];
  const devOrigins = [
    "http://localhost:5173",
    "http://127.0.0.1:5173",
    "http://localhost:4173",
    "http://127.0.0.1:4173",
  ];
  const allowedOrigins = new Set([...configuredOrigins, ...devOrigins]);

  callback(null, allowedOrigins.has(origin));
}
