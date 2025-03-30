"use client";

import { useEffect, useState } from "react";
import Link from "next/link";

export function Header() {
  const [user, setUser] = useState<{ name?: string; email?: string } | null>(null);

  useEffect(() => {
    fetch("/api/auth/me")
      .then((res) => res.ok && res.json())
      .then((data) => {
        if (data?.user) setUser(data.user);
      });
  }, []);

  return (
    <header className="flex items-center justify-between px-6 py-4 border-b bg-background">
      <h2 className="text-lg font-medium">Dashboard</h2>

      <div className="flex items-center gap-4 text-sm">
        {user ? (
          <>
            <span className="text-muted-foreground">Signed in as {user.name || user.email}</span>
            <Link
              href="/api/auth/logout"
              className="text-primary underline underline-offset-2 hover:text-primary/80"
            >
              Logout
            </Link>
          </>
        ) : (
          <Link
            href="/login"
            className="text-muted-foreground hover:underline"
          >
            Sign In
          </Link>
        )}
      </div>
    </header>
  );
} 