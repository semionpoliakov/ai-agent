import next from "@next/eslint-plugin-next";
import tseslint from "typescript-eslint";
import unusedImports from "eslint-plugin-unused-imports";

const nextCoreWebVitals = next.configs["core-web-vitals"];
const nextLanguageOptions = nextCoreWebVitals.languageOptions ?? {};
const nextRules = nextCoreWebVitals.rules ?? {};
const nextSettings = nextCoreWebVitals.settings ?? {};

export default tseslint.config(
  {
    ignores: ["node_modules", ".next", "dist"],
  },
  ...tseslint.configs.recommendedTypeChecked,
  ...tseslint.configs.stylisticTypeChecked,
  {
    plugins: {
      "@next/next": next,
    },
  },
  {
    files: ["**/*.{ts,tsx,js,jsx}"],
    languageOptions: {
      ...nextLanguageOptions,
      parserOptions: {
        ...nextLanguageOptions.parserOptions,
        project: true,
        tsconfigRootDir: import.meta.dirname,
      },
    },
    plugins: {
      "unused-imports": unusedImports,
    },
    settings: nextSettings,
    rules: {
      ...nextRules,
      "unused-imports/no-unused-imports": "error",
      "unused-imports/no-unused-vars": [
        "warn",
        { vars: "all", varsIgnorePattern: "^_", args: "after-used", argsIgnorePattern: "^_" },
      ],
    },
  },
);
