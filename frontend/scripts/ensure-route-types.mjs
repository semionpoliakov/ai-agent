import fs from "node:fs";
import path from "node:path";

const routesPath = path.resolve(process.cwd(), ".next/types/routes.d.ts");

if (!fs.existsSync(routesPath)) {
  fs.mkdirSync(path.dirname(routesPath), { recursive: true });
  fs.writeFileSync(
    routesPath,
    "// Placeholder for local type-checking. Next.js overwrites this during builds.\nexport {};\n",
  );
}
