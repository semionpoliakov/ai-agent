import { AgentConsole, AgentHero } from "@/components/agent";

export default function HomePage() {
  return (
    <main className="mx-auto flex max-w-5xl flex-col gap-8 px-6 py-10 lg:px-0">
      <AgentHero />
      <AgentConsole />
    </main>
  );
}
