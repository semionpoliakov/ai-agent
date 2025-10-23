import { useMemo } from "react";
import { nanoid } from "nanoid";

export function useStableUserId(): string {
  return useMemo(() => {
    if (typeof crypto !== "undefined" && typeof crypto.randomUUID === "function") {
      return crypto.randomUUID();
    }
    return nanoid();
  }, []);
}
