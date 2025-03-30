"use client";

import { useEffect } from "react";
import { useRouter } from "next/navigation";

export default function LoginPage() {
  const router = useRouter();

  useEffect(() => {
    fetch("/api/auth/me").then(res => {
      if (res.ok) router.push("/"); // you're already logged in, skip login page
    });
  }, []);

  return (
    <div className="min-h-screen bg-gradient-to-br from-pink-100 via-purple-100 to-white flex items-center justify-center px-6">
      <div className="max-w-md w-full bg-white dark:bg-zinc-900 border rounded-xl shadow-lg p-8 text-center space-y-6">
        <h1 className="text-2xl font-semibold">Welcome, Madison 👋</h1>
        <p className="text-muted-foreground text-sm">Private Kalshi AI Access</p>
        <a
          href="/api/auth/login"
          className="inline-block mt-4 px-5 py-2 text-sm rounded-md bg-gradient-to-r from-purple-500 to-pink-500 text-white font-medium shadow"
        >
          Sign in to your dashboard
        </a>
        <p className="text-xs text-muted-foreground mt-4">Access is private and restricted.</p>
      </div>
    </div>
  );
} 