"use client";

import Link from "next/link";
import { usePathname } from "next/navigation";
import { cn } from "@/lib/utils";
import {
  FileText, TrendingUp, Search, BookOpen,
  PieChart, Newspaper, MessageSquare, History, LayoutDashboard,
} from "lucide-react";

const NAV_ITEMS = [
  { href: "/dashboard", label: "Dashboard", icon: LayoutDashboard },
  { href: "/document-qa", label: "Document Q&A", icon: FileText },
  { href: "/earnings-summarizer", label: "Earnings", icon: TrendingUp },
  { href: "/stock-research", label: "Research", icon: Search },
  { href: "/study", label: "Study", icon: BookOpen },
  { href: "/portfolio", label: "Portfolio", icon: PieChart },
  { href: "/sentiment", label: "Sentiment", icon: Newspaper },
  { href: "/chat", label: "Chat", icon: MessageSquare },
  { href: "/history", label: "History", icon: History },
];

export function Sidebar() {
  const pathname = usePathname();
  return (
    <aside className="w-56 border-r border-border bg-card min-h-screen p-4 flex flex-col gap-1">
      {NAV_ITEMS.map(({ href, label, icon: Icon }) => (
        <Link
          key={href}
          href={href}
          className={cn(
            "flex items-center gap-3 px-3 py-2 rounded-md text-sm transition-colors",
            pathname === href
              ? "bg-primary text-primary-foreground"
              : "text-muted-foreground hover:bg-secondary hover:text-foreground"
          )}
        >
          <Icon className="h-4 w-4" />
          {label}
        </Link>
      ))}
    </aside>
  );
}
