import Link from "next/link";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import {
  FileText, TrendingUp, Search, BookOpen,
  PieChart, Newspaper, MessageSquare, BarChart2,
} from "lucide-react";

const FEATURES = [
  { icon: FileText, title: "Document Q&A", desc: "Upload 10-K, annual reports, or earnings releases and ask questions with citations." },
  { icon: TrendingUp, title: "Earnings Summarizer", desc: "Paste any earnings transcript and get a structured summary streamed in real-time." },
  { icon: Search, title: "Stock Research", desc: "AI agent with live data tools generates research reports instantly." },
  { icon: BookOpen, title: "Study Assistant", desc: "CFA, Series 7, FRM, and CPA prep with flashcards and practice exams." },
  { icon: PieChart, title: "Portfolio Analyzer", desc: "P&L, concentration risk, and AI narrative commentary." },
  { icon: Newspaper, title: "Sentiment Analyzer", desc: "30-day news sentiment with bullish/bearish classification." },
  { icon: MessageSquare, title: "Financial Chat", desc: "Persistent AI chat with sliding context window." },
];

export default function LandingPage() {
  return (
    <main className="min-h-screen bg-background">
      <nav className="border-b border-border px-8 py-4 flex items-center justify-between">
        <div className="flex items-center gap-2 font-bold text-xl text-primary">
          <BarChart2 className="h-6 w-6" />
          Finance Hub
        </div>
        <Link href="/login">
          <Button>Get Started</Button>
        </Link>
      </nav>
      <section className="px-8 py-24 text-center max-w-4xl mx-auto">
        <h1 className="text-5xl font-bold mb-6 bg-gradient-to-r from-primary to-emerald-400 bg-clip-text text-transparent">
          Your AI-Powered Financial Research Platform
        </h1>
        <p className="text-xl text-muted-foreground mb-10 max-w-2xl mx-auto">
          Seven AI modules backed by a fine-tuned financial language model.
        </p>
        <Link href="/login">
          <Button size="lg" className="text-base px-8">Start Researching Free</Button>
        </Link>
      </section>
      <section className="px-8 pb-24 max-w-6xl mx-auto">
        <h2 className="text-2xl font-semibold text-center mb-12">7 AI-Powered Modules</h2>
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
          {FEATURES.map(({ icon: Icon, title, desc }) => (
            <Card key={title} className="bg-card border-border hover:border-primary transition-colors">
              <CardHeader className="pb-3">
                <Icon className="h-8 w-8 text-primary mb-2" />
                <CardTitle className="text-base">{title}</CardTitle>
              </CardHeader>
              <CardContent>
                <CardDescription className="text-sm leading-relaxed">{desc}</CardDescription>
              </CardContent>
            </Card>
          ))}
        </div>
      </section>
    </main>
  );
}
