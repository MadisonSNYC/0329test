"use client";

import Link from "next/link";
import { Home, LineChart, BarChart3, Settings } from "lucide-react";

export function Sidebar() {
  return (
    <aside className="w-64 border-r bg-card p-6 hidden md:block">
      <div className="text-lg font-bold mb-8">📊 Kalshi AI</div>
      <nav className="space-y-4">
        <Link href="/" className="flex items-center gap-2 hover:underline">
          <Home size={18} /> Dashboard
        </Link>
        <Link href="/strategies" className="flex items-center gap-2 hover:underline">
          <LineChart size={18} /> Strategies
        </Link>
        <Link href="/portfolio" className="flex items-center gap-2 hover:underline">
          <BarChart3 size={18} /> Portfolio
        </Link>
        <Link href="/settings" className="flex items-center gap-2 hover:underline">
          <Settings size={18} /> Settings
        </Link>
      </nav>
    </aside>
  );
} 