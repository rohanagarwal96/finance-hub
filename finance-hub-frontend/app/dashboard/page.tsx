import { redirect } from "next/navigation";
import { getServerSession } from "next-auth";
import { authOptions } from "@/lib/auth";
import Link from "next/link";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Navbar } from "@/components/layout/Navbar";
import { Sidebar } from "@/components/layout/Sidebar";
import {
  FileText, TrendingUp, Search, BookOpen,
  PieChart, Newspaper, MessageSquare,
} from "lucide-react";

const MODULES = [
  { href: "/document-qa", title: "Document Q&A", desc: "Upload PDFs and ask questions with citations.", icon: FileText, color: "text-blue-400" },
  { href: "/earnings-summarizer", title: "Earnings Summarizer", desc: "Structured earnings call analysis in real time.", icon: TrendingUp, color: "text-emerald-400" },
  { href: "/stock-research", title: "Stock Research", desc: "AI-generated research reports with live data.", icon: Search, color: "text-violet-400" },
  { href: "/study", title: "Study Assistant", desc: "CFA, Series 7, FRM, CPA exam prep.", icon: BookOpen, color: "text-amber-400" },
  { href: "/portfolio", title: "Portfolio Analyzer", desc: "P&L, allocation, and concentration analysis.", icon: PieChart, color: "text-rose-400" },
  { href: "/sentiment", title: "Sentiment Analyzer", desc: "30-day news sentiment for any company.", icon: Newspaper, color: "text-cyan-400" },
  { href: "/chat", title: "Financial Chat", desc: "Persistent AI chat with financial expertise.", icon: MessageSquare, color: "text-indigo-400" },
];

export default async function DashboardPage() {
  const session = await getServerSession(authOptions);
  if (!session) redirect("/login");

  return (
    <div className="flex min-h-screen">
      <Sidebar />
      <div className="flex-1 flex flex-col">
        <Navbar />
        <main className="p-8">
          <h1 className="text-2xl font-bold mb-2">Dashboard</h1>
          <p className="text-muted-foreground mb-8">Welcome back, {session.user?.email}</p>
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
            {MODULES.map(({ href, title, desc, icon: Icon, color }) => (
              <Card key={href} className="bg-card border-border hover:border-primary transition-colors">
                <CardHeader>
                  <Icon className={`h-8 w-8 ${color} mb-2`} />
                  <CardTitle className="text-base">{title}</CardTitle>
                  <CardDescription className="text-sm">{desc}</CardDescription>
                </CardHeader>
                <CardContent>
                  <Link href={href}>
                    <Button className="w-full" variant="outline">Open</Button>
                  </Link>
                </CardContent>
              </Card>
            ))}
          </div>
        </main>
      </div>
    </div>
  );
}
