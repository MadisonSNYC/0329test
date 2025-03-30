import { Sidebar } from "../../components/sidebar";
import { Header } from "../../components/Header";

export default function SettingsLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <div className="flex min-h-screen bg-background text-foreground">
      <Sidebar />
      <div className="flex flex-col flex-1">
        <Header />
        <main>{children}</main>
      </div>
    </div>
  );
} 