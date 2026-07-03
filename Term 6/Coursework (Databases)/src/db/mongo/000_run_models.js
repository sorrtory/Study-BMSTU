globalThis.nestedDatabase = process.env.MONGO_NESTED_DATABASE || "coursework_nested";
globalThis.normalizedDatabase = process.env.MONGO_NORMALIZED_DATABASE || "coursework_normalized";

load("/docker-entrypoint-initdb.d/nested/001_schema.js");
load("/docker-entrypoint-initdb.d/nested/002_indexes.js");

load("/docker-entrypoint-initdb.d/normalized/001_schema.js");
load("/docker-entrypoint-initdb.d/normalized/002_indexes.js");
