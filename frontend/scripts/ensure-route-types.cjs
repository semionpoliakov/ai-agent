const fs = require("node:fs");
const path = require("node:path");

const routesPath = path.resolve(__dirname, "../.next/types/routes.d.ts");

if (!fs.existsSync(routesPath)) {
  fs.mkdirSync(path.dirname(routesPath), { recursive: true });
  fs.writeFileSync(
    routesPath,
    "// Placeholder generated for local type-checking. Next.js overwrites this during builds.\nexport {};\n",
  );
}
