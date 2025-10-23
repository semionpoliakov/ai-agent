import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { EXAMPLE_PROMPTS } from "@/config/prompts";

export function AgentEmptyState() {
  return (
    <Card>
      <CardHeader>
        <CardTitle>Example prompts</CardTitle>
      </CardHeader>
      <CardContent>
        <ul className="list-disc space-y-2 pl-5 text-sm text-muted-foreground">
          {EXAMPLE_PROMPTS.map((prompt) => (
            <li key={prompt}>{prompt}</li>
          ))}
        </ul>
      </CardContent>
    </Card>
  );
}
