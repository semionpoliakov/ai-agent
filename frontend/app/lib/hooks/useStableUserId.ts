import { nanoid } from "nanoid";
import { useEffect, useRef } from "react";

export function useStableUserId(): string {
  const idRef = useRef<string>("");

  if (!idRef.current) {
    if (typeof window === "undefined") {
      idRef.current = nanoid();
    } else {
      idRef.current = sessionStorage.getItem("userId") ?? nanoid();
      sessionStorage.setItem("userId", idRef.current);
    }
  }

  useEffect(() => {
    if (typeof window !== "undefined") {
      sessionStorage.setItem("userId", idRef.current);
    }
  }, []);

  return idRef.current;
}
