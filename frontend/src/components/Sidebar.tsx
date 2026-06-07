"use client";
import { useState, useEffect } from "react";
import Link from "next/link";
import { usePathname } from "next/navigation";
import { cn } from "@/lib/utils";
import {
  LayoutDashboard, Wand2, Images, TrendingUp,
  AlertTriangle, Settings, Shield, Menu, X,
} from "lucide-react";

const NAV = [
  { href: "/dashboard", icon: LayoutDashboard, label: "Dashboard" },
  { href: "/generate",  icon: Wand2,           label: "Generate"  },
  { href: "/gallery",   icon: Images,           label: "Gallery"   },
  { href: "/trends",    icon: TrendingUp,       label: "Trends"    },
  { href: "/incidents", icon: AlertTriangle,    label: "Incidents" },
  { href: "/settings",  icon: Settings,         label: "Settings"  },
  { href: "/admin",     icon: Shield,           label: "Admin"     },
];

function NavLinks({ pathname, onNavigate }: { pathname: string; onNavigate?: () => void }) {
  return (
    <nav className="flex-1 p-3 space-y-1">
      {NAV.map(({ href, icon: Icon, label }) => (
        <Link
          key={href}
          href={href}
          onClick={onNavigate}
          className={cn(
            "flex items-center gap-3 px-3 py-2.5 rounded-lg text-sm transition-colors",
            pathname === href
              ? "bg-purple-600/20 text-purple-400 font-medium"
              : "text-muted-foreground hover:text-foreground hover:bg-muted"
          )}
        >
          <Icon className="w-4 h-4 shrink-0" />
          {label}
        </Link>
      ))}
    </nav>
  );
}

function Brand() {
  return (
    <div className="p-5 border-b border-border">
      <h1 className="text-lg font-bold gradient-text">DevOps Emotions</h1>
      <p className="text-xs text-muted-foreground mt-0.5">AI Studio</p>
    </div>
  );
}

export function Sidebar() {
  const pathname = usePathname();
  const [open, setOpen] = useState(false);

  // Close drawer on route change
  useEffect(() => { setOpen(false); }, [pathname]);

  // Prevent body scroll when drawer is open
  useEffect(() => {
    document.body.style.overflow = open ? "hidden" : "";
    return () => { document.body.style.overflow = ""; };
  }, [open]);

  return (
    <>
      {/* ── Mobile hamburger button ── */}
      <button
        onClick={() => setOpen(true)}
        className="md:hidden fixed top-4 left-4 z-40 p-2 rounded-lg bg-card border border-border shadow-lg"
        aria-label="Open menu"
      >
        <Menu className="w-5 h-5" />
      </button>

      {/* ── Mobile overlay ── */}
      {open && (
        <div
          className="md:hidden fixed inset-0 z-40 bg-black/60 backdrop-blur-sm"
          onClick={() => setOpen(false)}
        />
      )}

      {/* ── Mobile slide-in drawer ── */}
      <aside
        className={cn(
          "md:hidden fixed top-0 left-0 z-50 h-full w-64 bg-card border-r border-border flex flex-col",
          "transition-transform duration-200 ease-in-out",
          open ? "translate-x-0" : "-translate-x-full"
        )}
      >
        <div className="flex items-center justify-between p-5 border-b border-border">
          <div>
            <h1 className="text-lg font-bold gradient-text">DevOps Emotions</h1>
            <p className="text-xs text-muted-foreground mt-0.5">AI Studio</p>
          </div>
          <button onClick={() => setOpen(false)} aria-label="Close menu">
            <X className="w-5 h-5 text-muted-foreground" />
          </button>
        </div>
        <NavLinks pathname={pathname} onNavigate={() => setOpen(false)} />
      </aside>

      {/* ── Desktop sidebar (always visible ≥ md) ── */}
      <aside className="hidden md:flex w-60 shrink-0 border-r border-border bg-card h-screen sticky top-0 flex-col">
        <Brand />
        <NavLinks pathname={pathname} />
      </aside>
    </>
  );
}
