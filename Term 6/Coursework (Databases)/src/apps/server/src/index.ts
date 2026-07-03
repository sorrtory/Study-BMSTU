import Config from "./config.js";
import { createApp } from "./app.js";

const app = createApp();

app.listen(Config.EXPRESS_PORT, Config.EXPRESS_HOST, () => {
  console.log(`Server running at ${Config.EXPRESS_HOST}:${Config.EXPRESS_PORT}`);
});
