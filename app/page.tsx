import { Sidebar } from "@/components/sidebar";
import { Header } from "@/components/Header";
import { MarketTrackers } from "@/components/market-trackers";
import { StrategyPanel } from "@/components/strategy-panel";
import RequireAuth from "@/components/require-auth";

export default function DashboardPage() {
  return (
    <RequireAuth>
      <div className="flex min-h-screen bg-background text-foreground">
        <Sidebar />
        <div className="flex flex-col flex-1">
          <Header />
          <main className="p-6 space-y-6">
            <h1 className="text-2xl font-semibold tracking-tight">Welcome to Kalshi AI</h1>
            <p className="text-muted-foreground text-sm">Your AI-powered prediction market assistant</p>
            <MarketTrackers />
            <StrategyPanel />
          </main>
        </div>
      </div>
    </RequireAuth>
  );
} 