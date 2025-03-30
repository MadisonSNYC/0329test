"use client";

import { useEffect, useState } from "react";
import { useRouter } from "next/navigation";

export default function RequireAuth({ children }: { children: React.ReactNode }) {
  const [loading, setLoading] = useState(true);
  const router = useRouter();

  useEffect(() => {
    fetch("/api/auth/me").then(res => {
      if (res.ok) {
        setLoading(false); // logged in
      } else {
        router.push("/login");
      }
    });
  }, []);

  if (loading) return <div className="p-6 text-sm text-muted-foreground">Checking login…</div>;

  return <>{children}</>;
} 