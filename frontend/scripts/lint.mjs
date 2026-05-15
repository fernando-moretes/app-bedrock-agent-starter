import { access, readFile } from "node:fs/promises";

const requiredFiles = ["public/index.html", "public/styles.css"];

for (const file of requiredFiles) {
  await access(file);
}

const html = await readFile("public/index.html", "utf8");
const css = await readFile("public/styles.css", "utf8");

const checks = [
  [html.includes("<main"), "index.html must include a main landmark"],
  [html.includes("bedrock-agent-starter"), "index.html must include the project name"],
  [
    html.includes("https://github.com/fernandofatech/bedrock-agent-starter"),
    "index.html must link to the repository",
  ],
  [css.includes(":focus-visible"), "styles.css must include visible focus states"],
  [css.includes("@media"), "styles.css must include responsive rules"],
];

const failures = checks.filter(([passed]) => !passed).map(([, message]) => message);

if (failures.length > 0) {
  console.error(failures.join("\n"));
  process.exit(1);
}

console.log("Static landing checks passed.");
