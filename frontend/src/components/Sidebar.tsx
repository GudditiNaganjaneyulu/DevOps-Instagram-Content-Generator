"use client";
import Link from "next/link";
import { usePathname } from "next/navigation";
import { cn } from "@/lib/utils";
import {
  LayoutDashboard, Wand2, Images, TrendingUp,
  AlertTriangle, Settings, Shield,
} from "lucide-react";

const NAV = [
  { href: "/dashboard", icon: LayoutDashboard, label: "Dashboard" },
  { href: "/generate", icon: Wand2, label: "Generate" },
  { href: "/gallery", icon: Images, label: "Gallery" },
  { href: "/trends", icon: TrendingUp, label: "Trends" },
  { href: "/incidents", icon: AlertTriangle, label: "Incidents" },
  { href: "/settings", icon: Settings, label: "Settings" },
  { href: "/admin", icon: Shield, label: "Admin" },
];

export function Sidebar() {
  const pathname = usePathname();

  return (
    <aside className="w-60 shrink-0 border-r border-border bg-card h-screen sticky top-0 flex flex-col">
      <div className="p-5 border-b border-border">
        <h1 className="text-lg font-bold gradient-text">DevOps Emotions</h1>
        <p className="text-xs text-muted-foreground mt-0.5">AI Studio</p>
      </div>
      <nav className="flex-1 p-3 space-y-1">
        {NAV.map(({ href, icon: Icon, label }) => (
          <Link
            key={href}
            href={href}
            className={cn(
              "flex items-center gap-3 px-3 py-2.5 rounded-lg text-sm transition-colors",
              pathname === href
                ? "bg-purple-600/20 text-purple-400 font-medium"
                : "text-muted-foreground hover:text-foreground hover:bg-muted"
            )}
          >
            <Icon className="w-4 h-4" />
            {label}
          </Link>
        ))}
      </nav>
    </aside>
  );
}
