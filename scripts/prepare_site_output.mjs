import { cpSync, existsSync, mkdirSync, rmSync } from "node:fs";
import { resolve } from "node:path";

const source = resolve("out");
const target = resolve("dist");
const workerSource = resolve("sites/server/index.js");
const hostingConfig = resolve(".openai/hosting.json");

if (!existsSync(source)) {
  throw new Error("Static export was not created at out/. Run next build first.");
}

rmSync(target, { recursive: true, force: true });
cpSync(source, target, { recursive: true });
mkdirSync(resolve(target, "server"), { recursive: true });
mkdirSync(resolve(target, ".openai"), { recursive: true });
cpSync(workerSource, resolve(target, "server/index.js"));
cpSync(hostingConfig, resolve(target, ".openai/hosting.json"));
console.log("Prepared Sites static output in dist/.");
