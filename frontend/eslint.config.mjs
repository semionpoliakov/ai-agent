import eslintPluginNext from "@next/eslint-plugin-next";
import eslintPluginUnusedImports from "eslint-plugin-unused-imports";
import { defineConfig } from "eslint/config";
import tseslint from "typescript-eslint";

export default defineConfig([
  {
    ignores: [
      "node_modules",
      ".next",
      "dist",
      ".turbo",
      "coverage",
      "next.config.*",
      "prettier.config.*",
      "postcss.config.*",
      "scripts/**",
      "eslint.config.mjs",
    ],
  },

  ...tseslint.configs.recommended,
  ...tseslint.configs.recommendedTypeChecked,
  ...tseslint.configs.stylisticTypeChecked,

  {
    files: ["**/*.{ts,tsx,js,jsx}"],

    languageOptions: {
      parserOptions: {
        projectService: true,
        project: "./tsconfig.json",
        tsconfigRootDir: import.meta.dirname,
      },
    },

    plugins: {
      "@next/next": eslintPluginNext,
      "unused-imports": eslintPluginUnusedImports,
    },

    rules: {
      ...eslintPluginNext.configs["core-web-vitals"].rules,

      "unused-imports/no-unused-imports": "error",
      "unused-imports/no-unused-vars": [
        "warn",
        {
          vars: "all",
          varsIgnorePattern: "^_",
          args: "after-used",
          argsIgnorePattern: "^_",
        },
      ],
    },
  },
]);
