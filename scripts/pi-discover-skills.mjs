#!/usr/bin/env node

import { pathToFileURL } from "node:url";
import path from "node:path";

const [sdkEntry, consumerRoot] = process.argv.slice(2);
if (!sdkEntry || !consumerRoot) {
  console.error("usage: pi-discover-skills.mjs PI_SDK_ENTRY CONSUMER_ROOT");
  process.exit(2);
}

const sdk = await import(pathToFileURL(path.resolve(sdkEntry)).href);
const root = path.resolve(consumerRoot);
const loader = new sdk.DefaultResourceLoader({
  cwd: root,
  agentDir: sdk.getAgentDir(),
});
await loader.reload();

const prefix = `${root}${path.sep}`;
const discovered = loader
  .getSkills()
  .skills.filter((skill) => path.resolve(skill.filePath).startsWith(prefix))
  .map((skill) => ({
    name: skill.name,
    path: path.relative(root, path.dirname(path.resolve(skill.filePath))).split(path.sep).join("/"),
  }))
  .sort((left, right) => left.name.localeCompare(right.name));

const diagnostics = loader
  .getSkills()
  .diagnostics.filter((item) => {
    const filePath = item.path ?? item.filePath ?? "";
    return filePath && path.resolve(filePath).startsWith(prefix);
  })
  .map((item) => item.message ?? String(item));

process.stdout.write(`${JSON.stringify({ diagnostics, skills: discovered }, null, 2)}\n`);
