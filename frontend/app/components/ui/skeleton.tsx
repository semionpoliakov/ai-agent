import { clsx } from "clsx";

type SkeletonProps = React.HTMLAttributes<HTMLDivElement>;

export function Skeleton({ className, ...props }: SkeletonProps) {
  return (
    <div
      className={clsx(
        "animate-shimmer rounded-md bg-gradient-to-r from-muted via-muted/80 to-muted",
        className,
      )}
      {...props}
    />
  );
}
