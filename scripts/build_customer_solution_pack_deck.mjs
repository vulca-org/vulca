#!/usr/bin/env node
import { spawnSync } from "node:child_process";
import fs from "node:fs";
import fsp from "node:fs/promises";
import os from "node:os";
import path from "node:path";
import { fileURLToPath } from "node:url";

const __filename = fileURLToPath(import.meta.url);
const ROOT = path.resolve(path.dirname(__filename), "..");
const OUTPUT_PPTX = path.join(ROOT, "output/pptx/vulca-solution-pack-v1-customer-sample-public-examples.pptx");
const OUTPUT_PDF = path.join(ROOT, "output/pdf/vulca-solution-pack-v1-customer-sample-public-examples.pdf");
const SKILL_DIR =
  process.env.PRESENTATIONS_SKILL_DIR ||
  "/Users/yhryzy/.codex/plugins/cache/openai-primary-runtime/presentations/26.619.11828/skills/presentations";
const THREAD_ID = process.env.CODEX_THREAD_ID || `manual-${Date.now()}`;
const TASK_SLUG = "vulca-customer-solution-pack-deck";
const SCRATCH_ROOT = process.env.SCRATCH_ROOT || os.tmpdir();
const WORKSPACE = path.join(SCRATCH_ROOT, "codex-presentations", THREAD_ID, TASK_SLUG);
const TMP_DIR = path.join(WORKSPACE, "tmp");
const PREVIEW_DIR = path.join(TMP_DIR, "preview");
const LAYOUT_DIR = path.join(TMP_DIR, "layout");
const QA_DIR = path.join(TMP_DIR, "qa");

function run(command, args, options = {}) {
  const result = spawnSync(command, args, {
    cwd: options.cwd || ROOT,
    env: { ...process.env, ...(options.env || {}) },
    encoding: "utf8",
    stdio: options.stdio || "pipe",
  });
  if (result.status !== 0) {
    if (result.stdout) process.stdout.write(result.stdout);
    if (result.stderr) process.stderr.write(result.stderr);
    throw new Error(`${command} ${args.join(" ")} exited with ${result.status}`);
  }
  return result;
}

function requireApproval(args) {
  if (!args.includes("--approval-recorded")) {
    process.stderr.write(
      [
        "Refusing to generate formal customer deck without --approval-recorded.",
        `PPTX path: ${path.relative(ROOT, OUTPUT_PPTX)}`,
        `PDF path: ${path.relative(ROOT, OUTPUT_PDF)}`,
        "This command replaces the canonical customer sample outputs after main-review approval.",
        "",
      ].join("\n"),
    );
    process.exit(2);
  }
}

async function main() {
  requireApproval(process.argv.slice(2));
  await fsp.mkdir(TMP_DIR, { recursive: true });
  await fsp.mkdir(PREVIEW_DIR, { recursive: true });
  await fsp.mkdir(LAYOUT_DIR, { recursive: true });
  await fsp.mkdir(QA_DIR, { recursive: true });
  await fsp.mkdir(path.dirname(OUTPUT_PPTX), { recursive: true });
  await fsp.mkdir(path.dirname(OUTPUT_PDF), { recursive: true });

  const setupScript = path.join(SKILL_DIR, "container_tools/setup_artifact_tool_workspace.mjs");
  if (!fs.existsSync(setupScript)) {
    throw new Error(`Missing artifact-tool setup script: ${setupScript}`);
  }

  run("node", [setupScript, "--workspace", TMP_DIR], { stdio: "inherit" });

  const configPath = path.join(TMP_DIR, "deck-config.json");
  const scratchBuilderPath = path.join(TMP_DIR, "customer_solution_pack_deck_builder.mjs");
  const repoBuilderPath = path.join(ROOT, "scripts/customer_solution_pack_deck_builder.mjs");
  await fsp.copyFile(repoBuilderPath, scratchBuilderPath);
  await fsp.writeFile(
    configPath,
    JSON.stringify(
      {
        root: ROOT,
        outputPptx: OUTPUT_PPTX,
        outputPdf: OUTPUT_PDF,
        previewDir: PREVIEW_DIR,
        layoutDir: LAYOUT_DIR,
        qaDir: QA_DIR,
      },
      null,
      2,
    ),
  );

  run("node", [scratchBuilderPath, configPath], { cwd: TMP_DIR, stdio: "inherit" });
  await fsp.rm(`${OUTPUT_PPTX}.inspect.ndjson`, { force: true });
  run(
    "osascript",
    [
      "-e",
      `tell application "Keynote"
  activate
  set inputFile to POSIX file "${OUTPUT_PPTX}"
  set outputFile to POSIX file "${OUTPUT_PDF}"
  open inputFile
  set deckDocument to front document
  export deckDocument to outputFile as PDF
  close deckDocument saving no
end tell`,
    ],
    { stdio: "inherit" },
  );
  run("python3", ["scripts/customer_pdf_preflight.py", "--json", OUTPUT_PPTX, OUTPUT_PDF], { stdio: "inherit" });
}

main().catch((error) => {
  console.error(error.message);
  process.exitCode = 1;
});
