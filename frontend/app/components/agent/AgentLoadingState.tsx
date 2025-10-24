import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Skeleton } from "@/components/ui/skeleton";

export function AgentLoadingState() {
  return (
    <Card>
      <CardHeader>
        <CardTitle>Working on it…</CardTitle>
      </CardHeader>
      <CardContent className="space-y-3">
        <Skeleton className="h-4 w-3/4" />
        <Skeleton className="h-4 w-2/3" />
        <Skeleton className="h-40 w-full" />
      </CardContent>
    </Card>
  );
}
