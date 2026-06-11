"use client";

import Link from "next/link";
import { useSession, signOut } from "next-auth/react";
import { Button } from "@/components/ui/button";
import { BarChart2 } from "lucide-react";

export function Navbar() {
  const { data: session } = useSession();
  return (
    <nav className="border-b border-border bg-card px-6 py-3 flex items-center justify-between">
      <Link href="/dashboard" className="flex items-center gap-2 font-bold text-lg text-primary">
        <BarChart2 className="h-5 w-5" />
        Finance Hub
      </Link>
      <div className="flex items-center gap-3">
        {session ? (
          <>
            <span className="text-sm text-muted-foreground">{session.user?.email}</span>
            <Button variant="outline" size="sm" onClick={() => signOut({ callbackUrl: "/" })}>
              Sign Out
            </Button>
          </>
        ) : (
          <Link href="/login">
            <Button size="sm">Sign In</Button>
          </Link>
        )}
      </div>
    </nav>
  );
}
