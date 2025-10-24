import { cn } from "@/lib/utils";

type SkeletonProps = React.HTMLAttributes<HTMLDivElement>;

export function Skeleton({ className, ...props }: SkeletonProps) {
  return (
    <div
      className={cn(
        "animate-shimmer rounded-md bg-gradient-to-r from-muted via-muted/80 to-muted",
        className,
      )}
      {...props}
    />
  );
}
