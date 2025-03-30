"use client";

import { useState } from "react";
import RequireAuth from "../../components/require-auth";

export default function SettingsPage() {
  const [darkMode, setDarkMode] = useState(true);
  const [notifications, setNotifications] = useState(true);

  return (
    <RequireAuth>
      <div className="p-6 space-y-6">
        <h1 className="text-2xl font-semibold">⚙️ Settings</h1>

        <div className="space-y-4 max-w-md">
          {/* Theme toggle */}
          <div className="flex justify-between items-center border p-4 rounded-lg bg-muted/30">
            <div>
              <h2 className="font-medium">Dark Mode</h2>
              <p className="text-sm text-muted-foreground">Toggle site appearance</p>
            </div>
            <button
              onClick={() => {
                setDarkMode(!darkMode);
                document.documentElement.classList.toggle("dark");
              }}
              className="px-3 py-1 text-sm rounded-md bg-primary text-white"
            >
              {darkMode ? "On" : "Off"}
            </button>
          </div>

          {/* Notifications */}
          <div className="flex justify-between items-center border p-4 rounded-lg bg-muted/30">
            <div>
              <h2 className="font-medium">Notifications</h2>
              <p className="text-sm text-muted-foreground">Trade confirmations & AI alerts</p>
            </div>
            <button
              onClick={() => setNotifications(!notifications)}
              className="px-3 py-1 text-sm rounded-md bg-primary text-white"
            >
              {notifications ? "Enabled" : "Disabled"}
            </button>
          </div>

          {/* Placeholder for future preferences */}
          <div className="border p-4 rounded-lg bg-muted/20 text-sm text-muted-foreground italic">
            More preferences coming soon — AI risk levels, daily trade limits, and more.
          </div>
        </div>
      </div>
    </RequireAuth>
  );
} 