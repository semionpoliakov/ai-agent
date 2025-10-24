import * as React from "react";

import { cn } from "@/lib/utils";

type ButtonVariant = "default" | "outline" | "ghost" | "destructive";

type ButtonProps = React.ButtonHTMLAttributes<HTMLButtonElement> & {
  variant?: ButtonVariant;
};

const variantStyles: Record<ButtonVariant, string> = {
  default:
    "bg-primary text-primary-foreground hover:bg-primary/90 focus-visible:ring-2 focus-visible:ring-offset-2 focus-visible:ring-primary",
  outline:
    "border border-muted-foreground text-foreground hover:bg-muted focus-visible:ring-2 focus-visible:ring-offset-2 focus-visible:ring-muted-foreground",
  ghost: "text-foreground hover:bg-muted",
  destructive:
    "bg-destructive text-destructive-foreground hover:bg-destructive/90 focus-visible:ring-2 focus-visible:ring-offset-2 focus-visible:ring-destructive",
};

export const Button = React.forwardRef<HTMLButtonElement, ButtonProps>(
  ({ className, variant = "default", type = "button", ...props }, ref) => (
    <button
      ref={ref}
      type={type}
      className={cn(
        "inline-flex items-center justify-center rounded-md px-4 py-2 text-sm font-medium transition-colors disabled:opacity-60 disabled:pointer-events-none",
        variantStyles[variant],
        className,
      )}
      {...props}
    />
  ),
);

Button.displayName = "Button";
