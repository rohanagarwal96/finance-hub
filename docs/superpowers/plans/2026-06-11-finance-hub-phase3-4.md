# Finance Hub — Implementation Plan (Phase 3 & 4)

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Build the complete Next.js 14 frontend (Phase 3) and deploy everything to Vercel + Render (Phase 4).

**Architecture:** Next.js App Router with TypeScript, shadcn/ui, NextAuth email auth, React Query for server state, Recharts for charts, axios for API calls, EventSource for SSE streaming.

**Tech Stack:** Next.js 14, TypeScript, Tailwind CSS, shadcn/ui, NextAuth.js, React Query, Recharts, axios, react-dropzone, framer-motion, lucide-react

---

## PHASE 3: Next.js Frontend

### Task 23: Initialize Next.js project and install dependencies

**Files:**
- Create: `finance-hub-frontend/` (entire Next.js project)

- [ ] **Step 1: Initialize Next.js 14 project**

```powershell
cd C:\Rohan\finance-hub
npx create-next-app@latest finance-hub-frontend --typescript --tailwind --eslint --app --src-dir=false --import-alias "@/*"
```
When prompted, accept all defaults.

- [ ] **Step 2: Install dependencies**

```powershell
cd finance-hub-frontend
npm install next-auth@4 @auth/supabase-adapter
npm install recharts
npm install @tanstack/react-query
npm install axios
npm install react-dropzone
npm install react-markdown
npm install framer-motion
npm install lucide-react
npm install @radix-ui/react-icons
npm install @supabase/supabase-js
```

- [ ] **Step 3: Initialize shadcn/ui**

```powershell
npx shadcn@latest init
```
When prompted: style=Default, base color=Slate, CSS variables=yes.

- [ ] **Step 4: Add all shadcn components**

```powershell
npx shadcn@latest add button card input textarea badge dialog dropdown-menu tabs progress toast skeleton separator scroll-area select switch label form
```

- [ ] **Step 5: Verify build compiles**

```powershell
npm run build
```
Expected: Build succeeds with no TypeScript errors.

- [ ] **Step 6: Commit**

```powershell
cd C:\Rohan\finance-hub
git add finance-hub-frontend/
git commit -m "feat: initialize Next.js 14 frontend with shadcn/ui"
```

---

### Task 24: Configure Tailwind theme and global styles

**Files:**
- Modify: `finance-hub-frontend/tailwind.config.ts`
- Modify: `finance-hub-frontend/app/globals.css`

- [ ] **Step 1: Update tailwind.config.ts**

Replace the contents of `finance-hub-frontend/tailwind.config.ts` with:

```typescript
import type { Config } from "tailwindcss";

const config: Config = {
  darkMode: ["class"],
  content: [
    "./pages/**/*.{ts,tsx}",
    "./components/**/*.{ts,tsx}",
    "./app/**/*.{ts,tsx}",
    "./src/**/*.{ts,tsx}",
  ],
  theme: {
    container: {
      center: true,
      padding: "2rem",
      screens: { "2xl": "1400px" },
    },
    extend: {
      colors: {
        background: "#0f172a",
        foreground: "#f8fafc",
        card: { DEFAULT: "#1e293b", foreground: "#f8fafc" },
        border: "#334155",
        input: "#1e293b",
        primary: { DEFAULT: "#3b82f6", foreground: "#ffffff" },
        secondary: { DEFAULT: "#1e293b", foreground: "#94a3b8" },
        muted: { DEFAULT: "#1e293b", foreground: "#64748b" },
        accent: { DEFAULT: "#3b82f6", foreground: "#ffffff" },
        positive: "#10b981",
        warning: "#f59e0b",
        danger: "#f43f5e",
        "mono-font": "JetBrains Mono, monospace",
      },
      fontFamily: {
        sans: ["Inter", "sans-serif"],
        mono: ["JetBrains Mono", "monospace"],
      },
      borderRadius: {
        lg: "var(--radius)",
        md: "calc(var(--radius) - 2px)",
        sm: "calc(var(--radius) - 4px)",
      },
      keyframes: {
        "accordion-down": {
          from: { height: "0" },
          to: { height: "var(--radix-accordion-content-height)" },
        },
        "accordion-up": {
          from: { height: "var(--radix-accordion-content-height)" },
          to: { height: "0" },
        },
      },
      animation: {
        "accordion-down": "accordion-down 0.2s ease-out",
        "accordion-up": "accordion-up 0.2s ease-out",
      },
    },
  },
  plugins: [require("tailwindcss-animate")],
};

export default config;
```

- [ ] **Step 2: Update globals.css**

Replace `finance-hub-frontend/app/globals.css` with:

```css
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&family=JetBrains+Mono:wght@400;500&display=swap');
@tailwind base;
@tailwind components;
@tailwind utilities;

@layer base {
  :root {
    --background: 222 47% 11%;
    --foreground: 210 40% 98%;
    --card: 217 33% 17%;
    --card-foreground: 210 40% 98%;
    --border: 215 25% 27%;
    --input: 217 33% 17%;
    --primary: 217 91% 60%;
    --primary-foreground: 0 0% 100%;
    --secondary: 217 33% 17%;
    --secondary-foreground: 215 16% 65%;
    --muted: 217 33% 17%;
    --muted-foreground: 215 16% 47%;
    --accent: 217 91% 60%;
    --accent-foreground: 0 0% 100%;
    --radius: 0.5rem;
  }

  * { @apply border-border; }
  body { @apply bg-background text-foreground font-sans; }
}

.font-mono { font-family: 'JetBrains Mono', monospace; }
.text-positive { color: #10b981; }
.text-warning { color: #f59e0b; }
.text-danger { color: #f43f5e; }
```

- [ ] **Step 3: Commit**

```powershell
cd C:\Rohan\finance-hub
git add finance-hub-frontend/tailwind.config.ts finance-hub-frontend/app/globals.css
git commit -m "feat: configure dark financial theme"
```

---

### Task 25: Create types/index.ts and lib files

**Files:**
- Create: `finance-hub-frontend/types/index.ts`
- Create: `finance-hub-frontend/lib/utils.ts`
- Create: `finance-hub-frontend/lib/api.ts`
- Create: `finance-hub-frontend/lib/auth.ts`

- [ ] **Step 1: Create types/index.ts**

```typescript
export interface Message {
  id: string;
  role: "user" | "assistant";
  content: string;
  created_at: string;
}

export interface Conversation {
  id: string;
  title: string;
  created_at: string;
}

export interface Document {
  id: string;
  filename: string;
  uploaded_at: string;
}

export interface Citation {
  page: number;
  section: string;
  text: string;
  score: number;
}

export interface KeyMetrics {
  pe_ratio: number | null;
  ev_ebitda: number | null;
  gross_margin: number | null;
  revenue_growth_yoy: number | null;
  market_cap: number | null;
  current_price: number | null;
}

export interface ResearchReport {
  ticker: string;
  company_name: string;
  overview: string;
  financial_performance: string;
  key_metrics: KeyMetrics;
  recent_news: string[];
  bull_case: string[];
  bear_case: string[];
  key_risks: string;
}

export interface StudyQuestion {
  question: string;
  options: string[] | null;
  correct_answer: string;
  explanation: string;
  topic: string;
  exam_type: string;
}

export interface StudyAttemptResult {
  correct: boolean;
  explanation: string;
}

export interface TopicPerformance {
  topic: string;
  correct: number;
  total: number;
  accuracy: number;
}

export interface Holding {
  ticker: string;
  shares: number;
  cost_basis: number;
}

export interface PositionAnalysis {
  ticker: string;
  shares: number;
  cost_basis: number;
  current_price: number;
  current_value: number;
  pnl_dollar: number;
  pnl_percent: number;
  sector: string | null;
  weight: number;
}

export interface PortfolioAnalysis {
  total_value: number;
  total_cost: number;
  total_pnl_dollar: number;
  total_pnl_percent: number;
  positions: PositionAnalysis[];
  sector_allocation: Record<string, number>;
  herfindahl_index: number;
  correlation_matrix: Record<string, Record<string, number>>;
  commentary: string;
}

export interface ArticleSentiment {
  title: string;
  url: string;
  published_at: string;
  sentiment: "bullish" | "neutral" | "bearish";
  confidence: number;
  summary: string | null;
}

export interface SentimentResult {
  query: string;
  overall_score: number;
  overall_label: "bullish" | "neutral" | "bearish";
  article_count: number;
  articles: ArticleSentiment[];
  cached: boolean;
}

export interface EarningsSummarySection {
  title: string;
  content: string;
}
```

- [ ] **Step 2: Create lib/utils.ts**

```typescript
import { type ClassValue, clsx } from "clsx";
import { twMerge } from "tailwind-merge";

export function cn(...inputs: ClassValue[]) {
  return twMerge(clsx(inputs));
}

export function formatCurrency(value: number | null | undefined): string {
  if (value == null) return "N/A";
  if (Math.abs(value) >= 1e12) return `$${(value / 1e12).toFixed(2)}T`;
  if (Math.abs(value) >= 1e9) return `$${(value / 1e9).toFixed(2)}B`;
  if (Math.abs(value) >= 1e6) return `$${(value / 1e6).toFixed(2)}M`;
  return `$${value.toFixed(2)}`;
}

export function formatPercent(value: number | null | undefined): string {
  if (value == null) return "N/A";
  return `${(value * 100).toFixed(2)}%`;
}

export function sentimentColor(label: string): string {
  if (label === "bullish") return "text-positive";
  if (label === "bearish") return "text-danger";
  return "text-warning";
}

export function pnlColor(value: number): string {
  return value >= 0 ? "text-positive" : "text-danger";
}
```

- [ ] **Step 3: Create lib/api.ts**

```typescript
import axios from "axios";
import type {
  ArticleSentiment,
  Citation,
  Conversation,
  Document,
  Holding,
  Message,
  PortfolioAnalysis,
  ResearchReport,
  SentimentResult,
  StudyAttemptResult,
  StudyQuestion,
  TopicPerformance,
} from "@/types";

const api = axios.create({
  baseURL: process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000",
  timeout: 130000, // 130s — HF Space can take up to 120s
});

// Chat
export async function sendChatMessage(params: {
  user_id: string;
  content: string;
  conversation_id?: string;
}) {
  const { data } = await api.post("/api/chat/message", params);
  return data as { conversation_id: string; message_id: string; role: string; content: string; created_at: string };
}

export async function getChatHistory(conversationId: string): Promise<Message[]> {
  const { data } = await api.get(`/api/chat/history/${conversationId}`);
  return data;
}

export async function getConversations(userId: string): Promise<Conversation[]> {
  const { data } = await api.get(`/api/chat/conversations/${userId}`);
  return data;
}

// Document Q&A
export async function uploadDocument(file: File, userId: string): Promise<{
  document_id: string;
  filename: string;
  chunk_count: number;
}> {
  const form = new FormData();
  form.append("file", file);
  form.append("user_id", userId);
  const { data } = await api.post("/api/document/upload", form, {
    headers: { "Content-Type": "multipart/form-data" },
  });
  return data;
}

export async function queryDocument(params: {
  document_id: string;
  user_id: string;
  question: string;
}): Promise<{ answer: string; citations: Citation[] }> {
  const { data } = await api.post("/api/document/query", params);
  return data;
}

export async function listDocuments(userId: string): Promise<Document[]> {
  const { data } = await api.get(`/api/document/list?user_id=${userId}`);
  return data;
}

// Research
export async function getResearchReport(ticker: string): Promise<ResearchReport> {
  const { data } = await api.get(`/api/research/${ticker}`);
  return data;
}

// Study
export async function getStudyQuestion(params: {
  user_id: string;
  exam_type: string;
  topic: string;
  mode: string;
}): Promise<StudyQuestion> {
  const { data } = await api.get("/api/study/question", { params });
  return data;
}

export async function submitStudyAttempt(params: {
  user_id: string;
  topic: string;
  exam_type: string;
  question: string;
  user_answer: string;
  correct_answer: string;
}): Promise<StudyAttemptResult> {
  const { data } = await api.post("/api/study/attempt", params);
  return data;
}

export async function getStudyPerformance(
  userId: string,
  examType?: string
): Promise<{ topics: TopicPerformance[] }> {
  const params = examType ? { exam_type: examType } : {};
  const { data } = await api.get(`/api/study/performance/${userId}`, { params });
  return data;
}

// Portfolio
export async function analyzePortfolio(params: {
  user_id: string;
  holdings: Holding[];
}): Promise<PortfolioAnalysis> {
  const { data } = await api.post("/api/portfolio/holdings", params);
  return data;
}

// Sentiment
export async function getSentiment(query: string): Promise<SentimentResult> {
  const { data } = await api.get(`/api/sentiment/${encodeURIComponent(query)}`);
  return data;
}
```

- [ ] **Step 4: Create lib/auth.ts**

```typescript
import { NextAuthOptions } from "next-auth";
import EmailProvider from "next-auth/providers/email";

export const authOptions: NextAuthOptions = {
  providers: [
    EmailProvider({
      server: {
        host: process.env.EMAIL_SERVER_HOST || "smtp.gmail.com",
        port: Number(process.env.EMAIL_SERVER_PORT) || 587,
        auth: {
          user: process.env.EMAIL_SERVER_USER || "",
          pass: process.env.EMAIL_SERVER_PASSWORD || "",
        },
      },
      from: process.env.EMAIL_FROM || "noreply@financehub.app",
    }),
    // Google OAuth — add GOOGLE_CLIENT_ID and GOOGLE_CLIENT_SECRET to .env.local to enable
    // GoogleProvider({
    //   clientId: process.env.GOOGLE_CLIENT_ID!,
    //   clientSecret: process.env.GOOGLE_CLIENT_SECRET!,
    // }),
  ],
  pages: {
    signIn: "/login",
  },
  callbacks: {
    async session({ session, token }) {
      if (session.user && token.sub) {
        (session.user as any).id = token.sub;
      }
      return session;
    },
    async jwt({ token, user }) {
      if (user) {
        token.sub = user.id;
      }
      return token;
    },
  },
  secret: process.env.NEXTAUTH_SECRET,
};
```

- [ ] **Step 5: Verify TypeScript compiles**

```powershell
cd C:\Rohan\finance-hub\finance-hub-frontend
npx tsc --noEmit
```
Expected: no errors.

- [ ] **Step 6: Commit**

```powershell
cd C:\Rohan\finance-hub
git add finance-hub-frontend/types/ finance-hub-frontend/lib/
git commit -m "feat: add TypeScript types, API client, and auth config"
```

---

### Task 26: Create NextAuth route and app/layout.tsx

**Files:**
- Create: `finance-hub-frontend/app/api/auth/[...nextauth]/route.ts`
- Modify: `finance-hub-frontend/app/layout.tsx`
- Create: `finance-hub-frontend/components/providers.tsx`

- [ ] **Step 1: Create NextAuth route**

Create `finance-hub-frontend/app/api/auth/[...nextauth]/route.ts`:

```typescript
import NextAuth from "next-auth";
import { authOptions } from "@/lib/auth";

const handler = NextAuth(authOptions);
export { handler as GET, handler as POST };
```

- [ ] **Step 2: Create providers.tsx**

Create `finance-hub-frontend/components/providers.tsx`:

```typescript
"use client";

import { SessionProvider } from "next-auth/react";
import { QueryClient, QueryClientProvider } from "@tanstack/react-query";
import { useState } from "react";

export function Providers({ children }: { children: React.ReactNode }) {
  const [queryClient] = useState(() => new QueryClient({
    defaultOptions: { queries: { staleTime: 60_000, retry: 1 } },
  }));

  return (
    <SessionProvider>
      <QueryClientProvider client={queryClient}>
        {children}
      </QueryClientProvider>
    </SessionProvider>
  );
}
```

- [ ] **Step 3: Update app/layout.tsx**

Replace `finance-hub-frontend/app/layout.tsx` with:

```typescript
import type { Metadata } from "next";
import { Inter } from "next/font/google";
import "./globals.css";
import { Providers } from "@/components/providers";
import { Toaster } from "@/components/ui/toaster";

const inter = Inter({ subsets: ["latin"] });

export const metadata: Metadata = {
  title: "Finance Hub — AI Financial Research Platform",
  description: "AI-powered financial research: document Q&A, earnings analysis, stock research, portfolio analytics, and more.",
};

export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    <html lang="en" className="dark">
      <body className={`${inter.className} bg-background text-foreground min-h-screen`}>
        <Providers>
          {children}
          <Toaster />
        </Providers>
      </body>
    </html>
  );
}
```

- [ ] **Step 4: Commit**

```powershell
cd C:\Rohan\finance-hub
git add finance-hub-frontend/app/api/ finance-hub-frontend/app/layout.tsx finance-hub-frontend/components/providers.tsx
git commit -m "feat: add NextAuth route and app layout with providers"
```

---

### Task 27: Create layout components (Navbar, Sidebar)

**Files:**
- Create: `finance-hub-frontend/components/layout/Navbar.tsx`
- Create: `finance-hub-frontend/components/layout/Sidebar.tsx`

- [ ] **Step 1: Create Navbar.tsx**

Create `finance-hub-frontend/components/layout/Navbar.tsx`:

```typescript
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
```

- [ ] **Step 2: Create Sidebar.tsx**

Create `finance-hub-frontend/components/layout/Sidebar.tsx`:

```typescript
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
```

- [ ] **Step 3: Commit**

```powershell
cd C:\Rohan\finance-hub
git add finance-hub-frontend/components/layout/
git commit -m "feat: add Navbar and Sidebar layout components"
```

---

### Task 28: Create landing page and login page

**Files:**
- Modify: `finance-hub-frontend/app/page.tsx`
- Create: `finance-hub-frontend/app/login/page.tsx`

- [ ] **Step 1: Replace app/page.tsx (landing)**

```typescript
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
  { icon: Search, title: "Stock Research", desc: "AI agent with live data tools generates bull/bear cases and key metrics instantly." },
  { icon: BookOpen, title: "Study Assistant", desc: "CFA, Series 7, FRM, and CPA prep with flashcards, practice exams, and weak-spot analysis." },
  { icon: PieChart, title: "Portfolio Analyzer", desc: "P&L, sector allocation, concentration risk, and AI narrative commentary." },
  { icon: Newspaper, title: "Sentiment Analyzer", desc: "30-day news sentiment timeline with bullish/bearish classification per article." },
  { icon: MessageSquare, title: "Financial Chat", desc: "Persistent AI chat with sliding context window and cross-module integration." },
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
          Seven AI modules backed by a fine-tuned financial language model. From earnings analysis to portfolio risk — all in one place.
        </p>
        <Link href="/login">
          <Button size="lg" className="text-base px-8">
            Start Researching Free
          </Button>
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
```

- [ ] **Step 2: Create app/login/page.tsx**

```typescript
"use client";

import { signIn } from "next-auth/react";
import { useState } from "react";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { BarChart2 } from "lucide-react";
import { useToast } from "@/components/ui/use-toast";

export default function LoginPage() {
  const [email, setEmail] = useState("");
  const [loading, setLoading] = useState(false);
  const [sent, setSent] = useState(false);
  const { toast } = useToast();

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!email) return;
    setLoading(true);
    try {
      await signIn("email", { email, redirect: false, callbackUrl: "/dashboard" });
      setSent(true);
    } catch {
      toast({ title: "Error", description: "Failed to send login email.", variant: "destructive" });
    } finally {
      setLoading(false);
    }
  };

  return (
    <main className="min-h-screen bg-background flex items-center justify-center">
      <Card className="w-full max-w-md bg-card border-border">
        <CardHeader className="text-center">
          <div className="flex items-center justify-center gap-2 mb-4">
            <BarChart2 className="h-8 w-8 text-primary" />
            <span className="text-2xl font-bold">Finance Hub</span>
          </div>
          <CardTitle>Sign In</CardTitle>
          <CardDescription>Enter your email to receive a sign-in link.</CardDescription>
        </CardHeader>
        <CardContent>
          {sent ? (
            <div className="text-center py-4">
              <p className="text-positive font-medium">Check your email!</p>
              <p className="text-muted-foreground text-sm mt-2">
                We sent a sign-in link to <strong>{email}</strong>.
              </p>
            </div>
          ) : (
            <form onSubmit={handleSubmit} className="space-y-4">
              <Input
                type="email"
                placeholder="you@example.com"
                value={email}
                onChange={(e) => setEmail(e.target.value)}
                required
                className="bg-input border-border"
              />
              <Button type="submit" className="w-full" disabled={loading}>
                {loading ? "Sending..." : "Send Sign-In Link"}
              </Button>
            </form>
          )}
        </CardContent>
      </Card>
    </main>
  );
}
```

- [ ] **Step 3: Commit**

```powershell
cd C:\Rohan\finance-hub
git add finance-hub-frontend/app/page.tsx finance-hub-frontend/app/login/
git commit -m "feat: add landing page and login page"
```

---

### Task 29: Create dashboard page

**Files:**
- Create: `finance-hub-frontend/app/dashboard/page.tsx`

- [ ] **Step 1: Create dashboard/page.tsx**

```typescript
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
```

- [ ] **Step 2: Commit**

```powershell
cd C:\Rohan\finance-hub
git add finance-hub-frontend/app/dashboard/
git commit -m "feat: add dashboard page"
```

---

### Task 30: Create Document Q&A page

**Files:**
- Create: `finance-hub-frontend/app/document-qa/page.tsx`

- [ ] **Step 1: Create document-qa/page.tsx**

```typescript
"use client";

import { useState, useCallback } from "react";
import { useSession } from "next-auth/react";
import { useDropzone } from "react-dropzone";
import { useToast } from "@/components/ui/use-toast";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Skeleton } from "@/components/ui/skeleton";
import { Navbar } from "@/components/layout/Navbar";
import { Sidebar } from "@/components/layout/Sidebar";
import { uploadDocument, queryDocument } from "@/lib/api";
import type { Citation } from "@/types";
import { FileText, Upload, Send } from "lucide-react";

export default function DocumentQAPage() {
  const { data: session } = useSession();
  const { toast } = useToast();
  const [docId, setDocId] = useState<string | null>(null);
  const [docName, setDocName] = useState<string>("");
  const [uploading, setUploading] = useState(false);
  const [question, setQuestion] = useState("");
  const [answer, setAnswer] = useState("");
  const [citations, setCitations] = useState<Citation[]>([]);
  const [querying, setQuerying] = useState(false);

  const onDrop = useCallback(async (files: File[]) => {
    const file = files[0];
    if (!file || !session?.user) return;

    if (file.size > 10 * 1024 * 1024) {
      toast({ title: "File too large", description: "PDF must be under 10 MB.", variant: "destructive" });
      return;
    }

    setUploading(true);
    try {
      const userId = (session.user as any).id || session.user.email || "anon";
      const result = await uploadDocument(file, userId);
      setDocId(result.document_id);
      setDocName(file.name);
      toast({ title: "Uploaded", description: `${result.chunk_count} chunks indexed.` });
    } catch {
      toast({ title: "Upload failed", description: "Could not process PDF.", variant: "destructive" });
    } finally {
      setUploading(false);
    }
  }, [session, toast]);

  const { getRootProps, getInputProps, isDragActive } = useDropzone({
    onDrop, accept: { "application/pdf": [".pdf"] }, maxFiles: 1,
  });

  const handleQuery = async () => {
    if (!docId || !question.trim() || !session?.user) return;
    setQuerying(true);
    setAnswer("");
    setCitations([]);
    try {
      const userId = (session.user as any).id || session.user.email || "anon";
      const result = await queryDocument({ document_id: docId, user_id: userId, question });
      setAnswer(result.answer);
      setCitations(result.citations);
    } catch {
      toast({ title: "Query failed", description: "Could not get answer. Try again.", variant: "destructive" });
    } finally {
      setQuerying(false);
    }
  };

  return (
    <div className="flex min-h-screen">
      <Sidebar />
      <div className="flex-1 flex flex-col">
        <Navbar />
        <main className="p-8 max-w-4xl">
          <h1 className="text-2xl font-bold mb-6">Document Q&A</h1>

          {!docId ? (
            <div
              {...getRootProps()}
              className={`border-2 border-dashed rounded-lg p-16 text-center cursor-pointer transition-colors ${
                isDragActive ? "border-primary bg-primary/10" : "border-border hover:border-primary"
              }`}
            >
              <input {...getInputProps()} />
              <Upload className="h-12 w-12 mx-auto mb-4 text-muted-foreground" />
              {uploading ? (
                <p className="text-muted-foreground">Uploading and indexing...</p>
              ) : (
                <>
                  <p className="font-medium">Drop a PDF here or click to upload</p>
                  <p className="text-sm text-muted-foreground mt-1">Max 10 MB — 10-K, annual reports, earnings releases</p>
                </>
              )}
            </div>
          ) : (
            <div className="space-y-6">
              <div className="flex items-center gap-2 text-sm text-muted-foreground">
                <FileText className="h-4 w-4" />
                <span>{docName}</span>
                <Button variant="ghost" size="sm" onClick={() => { setDocId(null); setDocName(""); setAnswer(""); setCitations([]); }}>
                  Change file
                </Button>
              </div>

              <div className="flex gap-2">
                <Input
                  placeholder="Ask a question about the document..."
                  value={question}
                  onChange={(e) => setQuestion(e.target.value)}
                  onKeyDown={(e) => e.key === "Enter" && handleQuery()}
                  className="bg-input border-border"
                />
                <Button onClick={handleQuery} disabled={querying || !question.trim()}>
                  <Send className="h-4 w-4" />
                </Button>
              </div>

              {querying && <Skeleton className="h-32 w-full" />}

              {answer && (
                <Card className="bg-card border-border">
                  <CardHeader><CardTitle className="text-sm">Answer</CardTitle></CardHeader>
                  <CardContent>
                    <p className="text-sm leading-relaxed">{answer}</p>
                    {citations.length > 0 && (
                      <div className="mt-4 space-y-2">
                        <p className="text-xs text-muted-foreground font-medium">Sources:</p>
                        {citations.map((c, i) => (
                          <div key={i} className="bg-secondary p-3 rounded text-xs">
                            <Badge variant="outline" className="mb-1">Page {c.page} — {c.section}</Badge>
                            <p className="text-muted-foreground">{c.text}</p>
                          </div>
                        ))}
                      </div>
                    )}
                  </CardContent>
                </Card>
              )}
            </div>
          )}
        </main>
      </div>
    </div>
  );
}
```

- [ ] **Step 2: Commit**

```powershell
cd C:\Rohan\finance-hub
git add finance-hub-frontend/app/document-qa/
git commit -m "feat: add Document Q&A page with PDF upload and citation display"
```

---

### Task 31: Create Earnings Summarizer page

**Files:**
- Create: `finance-hub-frontend/app/earnings-summarizer/page.tsx`

- [ ] **Step 1: Create earnings-summarizer/page.tsx**

```typescript
"use client";

import { useState, useRef } from "react";
import { Button } from "@/components/ui/button";
import { Textarea } from "@/components/ui/textarea";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Skeleton } from "@/components/ui/skeleton";
import { Badge } from "@/components/ui/badge";
import { Navbar } from "@/components/layout/Navbar";
import { Sidebar } from "@/components/layout/Sidebar";
import { useToast } from "@/components/ui/use-toast";
import type { EarningsSummarySection } from "@/types";

export default function EarningsSummarizerPage() {
  const [transcript, setTranscript] = useState("");
  const [sections, setSections] = useState<EarningsSummarySection[]>([]);
  const [status, setStatus] = useState("");
  const [running, setRunning] = useState(false);
  const { toast } = useToast();
  const esRef = useRef<EventSource | null>(null);

  const handleSummarize = async () => {
    if (!transcript.trim() || transcript.length < 100) {
      toast({ title: "Too short", description: "Transcript must be at least 100 characters.", variant: "destructive" });
      return;
    }

    setSections([]);
    setStatus("");
    setRunning(true);

    const apiUrl = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";

    // POST via fetch to get SSE
    const response = await fetch(`${apiUrl}/api/summarize/earnings`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ transcript }),
    });

    if (!response.ok || !response.body) {
      toast({ title: "Error", description: "Failed to start summarization.", variant: "destructive" });
      setRunning(false);
      return;
    }

    const reader = response.body.getReader();
    const decoder = new TextDecoder();

    while (true) {
      const { done, value } = await reader.read();
      if (done) break;

      const text = decoder.decode(value);
      const lines = text.split("\n").filter(l => l.startsWith("data: "));

      for (const line of lines) {
        try {
          const data = JSON.parse(line.slice(6));
          if (data.type === "status") setStatus(data.message);
          if (data.type === "section") {
            setSections(prev => [...prev, { title: data.title, content: data.content }]);
            setStatus("");
          }
          if (data.type === "done") setRunning(false);
        } catch {}
      }
    }

    setRunning(false);
  };

  return (
    <div className="flex min-h-screen">
      <Sidebar />
      <div className="flex-1 flex flex-col">
        <Navbar />
        <main className="p-8 max-w-4xl space-y-6">
          <h1 className="text-2xl font-bold">Earnings Call Summarizer</h1>

          <Textarea
            placeholder="Paste earnings call transcript here (minimum 100 characters)..."
            value={transcript}
            onChange={(e) => setTranscript(e.target.value)}
            className="h-48 bg-input border-border font-mono text-sm resize-none"
          />

          <Button onClick={handleSummarize} disabled={running || transcript.length < 100}>
            {running ? "Summarizing..." : "Summarize Transcript"}
          </Button>

          {status && (
            <p className="text-sm text-muted-foreground animate-pulse">{status}</p>
          )}

          {running && sections.length === 0 && (
            <div className="space-y-3">
              {[1, 2, 3].map(i => <Skeleton key={i} className="h-24 w-full" />)}
            </div>
          )}

          {sections.map((section) => (
            <Card key={section.title} className="bg-card border-border">
              <CardHeader className="pb-2">
                <CardTitle className="text-sm text-primary">{section.title}</CardTitle>
              </CardHeader>
              <CardContent>
                <p className="text-sm leading-relaxed">{section.content}</p>
              </CardContent>
            </Card>
          ))}
        </main>
      </div>
    </div>
  );
}
```

- [ ] **Step 2: Commit**

```powershell
cd C:\Rohan\finance-hub
git add finance-hub-frontend/app/earnings-summarizer/
git commit -m "feat: add Earnings Summarizer page with SSE streaming"
```

---

### Task 32: Create Stock Research page

**Files:**
- Create: `finance-hub-frontend/app/stock-research/page.tsx`

- [ ] **Step 1: Create stock-research/page.tsx**

```typescript
"use client";

import { useState } from "react";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Skeleton } from "@/components/ui/skeleton";
import { Navbar } from "@/components/layout/Navbar";
import { Sidebar } from "@/components/layout/Sidebar";
import { useToast } from "@/components/ui/use-toast";
import { getResearchReport } from "@/lib/api";
import { formatCurrency, formatPercent } from "@/lib/utils";
import type { ResearchReport } from "@/types";
import { TrendingUp, TrendingDown, Search } from "lucide-react";
import { useRouter } from "next/navigation";

export default function StockResearchPage() {
  const [ticker, setTicker] = useState("");
  const [report, setReport] = useState<ResearchReport | null>(null);
  const [loading, setLoading] = useState(false);
  const { toast } = useToast();
  const router = useRouter();

  const handleSearch = async () => {
    if (!ticker.trim()) return;
    setLoading(true);
    setReport(null);
    try {
      const data = await getResearchReport(ticker.trim().toUpperCase());
      setReport(data);
    } catch {
      toast({ title: "Not found", description: `Could not find data for ${ticker}.`, variant: "destructive" });
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="flex min-h-screen">
      <Sidebar />
      <div className="flex-1 flex flex-col">
        <Navbar />
        <main className="p-8 max-w-5xl space-y-6">
          <h1 className="text-2xl font-bold">Stock Research Copilot</h1>

          <div className="flex gap-2">
            <Input
              placeholder="Enter ticker (e.g. AAPL, MSFT, NVDA)"
              value={ticker}
              onChange={(e) => setTicker(e.target.value.toUpperCase())}
              onKeyDown={(e) => e.key === "Enter" && handleSearch()}
              className="max-w-xs bg-input border-border font-mono"
            />
            <Button onClick={handleSearch} disabled={loading || !ticker.trim()}>
              <Search className="h-4 w-4 mr-2" />
              {loading ? "Researching..." : "Research"}
            </Button>
          </div>

          {loading && (
            <div className="space-y-4">
              {[1, 2, 3, 4].map(i => <Skeleton key={i} className="h-32 w-full" />)}
            </div>
          )}

          {report && (
            <div className="space-y-4">
              <div className="flex items-center justify-between">
                <div>
                  <h2 className="text-xl font-bold">{report.company_name}</h2>
                  <Badge variant="outline" className="font-mono">{report.ticker}</Badge>
                </div>
                <div className="text-right font-mono">
                  <p className="text-2xl font-bold">{formatCurrency(report.key_metrics.current_price)}</p>
                  <p className="text-sm text-muted-foreground">Market Cap: {formatCurrency(report.key_metrics.market_cap)}</p>
                </div>
              </div>

              <div className="grid grid-cols-2 md:grid-cols-4 gap-3">
                {[
                  { label: "P/E Ratio", value: report.key_metrics.pe_ratio?.toFixed(1) ?? "N/A" },
                  { label: "EV/EBITDA", value: report.key_metrics.ev_ebitda?.toFixed(1) ?? "N/A" },
                  { label: "Gross Margin", value: formatPercent(report.key_metrics.gross_margin) },
                  { label: "Rev Growth YoY", value: formatPercent(report.key_metrics.revenue_growth_yoy) },
                ].map(({ label, value }) => (
                  <Card key={label} className="bg-card border-border">
                    <CardContent className="pt-4 pb-3">
                      <p className="text-xs text-muted-foreground">{label}</p>
                      <p className="font-mono font-semibold">{value}</p>
                    </CardContent>
                  </Card>
                ))}
              </div>

              <Card className="bg-card border-border">
                <CardHeader><CardTitle className="text-sm">Company Overview</CardTitle></CardHeader>
                <CardContent><p className="text-sm leading-relaxed">{report.overview}</p></CardContent>
              </Card>

              <Card className="bg-card border-border">
                <CardHeader><CardTitle className="text-sm">Financial Performance</CardTitle></CardHeader>
                <CardContent><p className="text-sm leading-relaxed">{report.financial_performance}</p></CardContent>
              </Card>

              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                <Card className="bg-card border-[#10b981]/30">
                  <CardHeader>
                    <CardTitle className="text-sm flex items-center gap-2 text-positive">
                      <TrendingUp className="h-4 w-4" /> Bull Case
                    </CardTitle>
                  </CardHeader>
                  <CardContent>
                    <ul className="space-y-2">
                      {report.bull_case.map((point, i) => (
                        <li key={i} className="text-sm flex gap-2">
                          <span className="text-positive font-bold">{i + 1}.</span>
                          {point}
                        </li>
                      ))}
                    </ul>
                  </CardContent>
                </Card>
                <Card className="bg-card border-[#f43f5e]/30">
                  <CardHeader>
                    <CardTitle className="text-sm flex items-center gap-2 text-danger">
                      <TrendingDown className="h-4 w-4" /> Bear Case
                    </CardTitle>
                  </CardHeader>
                  <CardContent>
                    <ul className="space-y-2">
                      {report.bear_case.map((point, i) => (
                        <li key={i} className="text-sm flex gap-2">
                          <span className="text-danger font-bold">{i + 1}.</span>
                          {point}
                        </li>
                      ))}
                    </ul>
                  </CardContent>
                </Card>
              </div>

              <Card className="bg-card border-border">
                <CardHeader><CardTitle className="text-sm">Key Risks</CardTitle></CardHeader>
                <CardContent><p className="text-sm leading-relaxed">{report.key_risks}</p></CardContent>
              </Card>

              {report.recent_news.length > 0 && (
                <Card className="bg-card border-border">
                  <CardHeader><CardTitle className="text-sm">Recent Headlines</CardTitle></CardHeader>
                  <CardContent>
                    <ul className="space-y-1">
                      {report.recent_news.map((headline, i) => (
                        <li key={i} className="text-sm text-muted-foreground">• {headline}</li>
                      ))}
                    </ul>
                  </CardContent>
                </Card>
              )}

              <Button
                variant="outline"
                onClick={() => router.push(`/chat?context=${encodeURIComponent(`Research on ${report.company_name} (${report.ticker}): ${report.overview}`)}`)}
              >
                Ask follow-up questions in Chat →
              </Button>
            </div>
          )}
        </main>
      </div>
    </div>
  );
}
```

- [ ] **Step 2: Commit**

```powershell
cd C:\Rohan\finance-hub
git add finance-hub-frontend/app/stock-research/
git commit -m "feat: add Stock Research page with bull/bear case display"
```

---

### Task 33: Create Study Assistant page

**Files:**
- Create: `finance-hub-frontend/app/study/page.tsx`

- [ ] **Step 1: Create study/page.tsx**

```typescript
"use client";

import { useState } from "react";
import { useSession } from "next-auth/react";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select";
import { Badge } from "@/components/ui/badge";
import { Skeleton } from "@/components/ui/skeleton";
import { Navbar } from "@/components/layout/Navbar";
import { Sidebar } from "@/components/layout/Sidebar";
import { useToast } from "@/components/ui/use-toast";
import { getStudyQuestion, submitStudyAttempt } from "@/lib/api";
import type { StudyQuestion } from "@/types";

const EXAMS = ["CFA", "Series7", "FRM", "CPA"];
const TOPICS: Record<string, string[]> = {
  CFA: ["Equity Valuation", "Fixed Income", "Derivatives", "Portfolio Management", "Ethics", "Economics"],
  Series7: ["Equity Securities", "Debt Securities", "Options", "Mutual Funds", "Regulations"],
  FRM: ["Market Risk", "Credit Risk", "Operational Risk", "Quantitative Analysis"],
  CPA: ["Financial Accounting", "Auditing", "Taxation", "Business Law"],
};
const MODES = [
  { value: "flashcard", label: "Flashcard" },
  { value: "practice", label: "Practice Exam" },
  { value: "weakspot", label: "Weak Spot Analysis" },
];

export default function StudyPage() {
  const { data: session } = useSession();
  const { toast } = useToast();
  const [exam, setExam] = useState("CFA");
  const [topic, setTopic] = useState(TOPICS["CFA"][0]);
  const [mode, setMode] = useState("practice");
  const [question, setQuestion] = useState<StudyQuestion | null>(null);
  const [selectedAnswer, setSelectedAnswer] = useState<string | null>(null);
  const [result, setResult] = useState<{ correct: boolean; explanation: string } | null>(null);
  const [loading, setLoading] = useState(false);
  const [flipped, setFlipped] = useState(false);

  const userId = (session?.user as any)?.id || session?.user?.email || "anon";

  const handleGetQuestion = async () => {
    setLoading(true);
    setQuestion(null);
    setSelectedAnswer(null);
    setResult(null);
    setFlipped(false);
    try {
      const q = await getStudyQuestion({ user_id: userId, exam_type: exam, topic, mode });
      setQuestion(q);
    } catch {
      toast({ title: "Error", description: "Could not generate question.", variant: "destructive" });
    } finally {
      setLoading(false);
    }
  };

  const handleAnswer = async (answer: string) => {
    if (!question || result) return;
    setSelectedAnswer(answer);
    try {
      const res = await submitStudyAttempt({
        user_id: userId,
        topic: question.topic,
        exam_type: question.exam_type,
        question: question.question,
        user_answer: answer,
        correct_answer: question.correct_answer,
      });
      setResult(res);
    } catch {
      toast({ title: "Error", description: "Could not submit answer.", variant: "destructive" });
    }
  };

  return (
    <div className="flex min-h-screen">
      <Sidebar />
      <div className="flex-1 flex flex-col">
        <Navbar />
        <main className="p-8 max-w-3xl space-y-6">
          <h1 className="text-2xl font-bold">Study Assistant</h1>

          <div className="flex flex-wrap gap-4">
            <Select value={exam} onValueChange={(v) => { setExam(v); setTopic(TOPICS[v][0]); }}>
              <SelectTrigger className="w-36 bg-input border-border">
                <SelectValue placeholder="Exam" />
              </SelectTrigger>
              <SelectContent>
                {EXAMS.map(e => <SelectItem key={e} value={e}>{e}</SelectItem>)}
              </SelectContent>
            </Select>

            <Select value={topic} onValueChange={setTopic}>
              <SelectTrigger className="w-52 bg-input border-border">
                <SelectValue placeholder="Topic" />
              </SelectTrigger>
              <SelectContent>
                {(TOPICS[exam] || []).map(t => <SelectItem key={t} value={t}>{t}</SelectItem>)}
              </SelectContent>
            </Select>

            <Select value={mode} onValueChange={setMode}>
              <SelectTrigger className="w-48 bg-input border-border">
                <SelectValue placeholder="Mode" />
              </SelectTrigger>
              <SelectContent>
                {MODES.map(m => <SelectItem key={m.value} value={m.value}>{m.label}</SelectItem>)}
              </SelectContent>
            </Select>

            <Button onClick={handleGetQuestion} disabled={loading}>
              {loading ? "Generating..." : "Get Question"}
            </Button>
          </div>

          {loading && <Skeleton className="h-48 w-full" />}

          {question && mode === "flashcard" && (
            <Card
              className="bg-card border-border cursor-pointer min-h-48 flex items-center justify-center"
              onClick={() => setFlipped(!flipped)}
            >
              <CardContent className="text-center p-8">
                {!flipped ? (
                  <>
                    <p className="text-xs text-muted-foreground mb-4">Click to reveal answer</p>
                    <p className="text-lg font-medium">{question.question}</p>
                  </>
                ) : (
                  <>
                    <Badge className="mb-4 bg-positive">Answer</Badge>
                    <p className="text-lg font-medium">{question.correct_answer}</p>
                    <p className="text-sm text-muted-foreground mt-4">{question.explanation}</p>
                  </>
                )}
              </CardContent>
            </Card>
          )}

          {question && mode !== "flashcard" && (
            <Card className="bg-card border-border">
              <CardHeader>
                <Badge variant="outline" className="w-fit mb-2">{question.exam_type} — {question.topic}</Badge>
                <CardTitle className="text-base font-medium leading-relaxed">{question.question}</CardTitle>
              </CardHeader>
              <CardContent className="space-y-2">
                {question.options?.map((option, i) => {
                  const isSelected = selectedAnswer === option;
                  const isCorrect = result && option === question.correct_answer;
                  const isWrong = result && isSelected && !result.correct;
                  return (
                    <Button
                      key={i}
                      variant="outline"
                      className={`w-full justify-start text-left h-auto py-3 ${
                        isCorrect ? "border-positive text-positive" :
                        isWrong ? "border-danger text-danger" :
                        isSelected ? "border-primary" : "border-border"
                      }`}
                      onClick={() => handleAnswer(option)}
                      disabled={!!result}
                    >
                      {option}
                    </Button>
                  );
                })}

                {result && (
                  <div className={`mt-4 p-4 rounded-lg ${result.correct ? "bg-positive/10 border border-positive/30" : "bg-danger/10 border border-danger/30"}`}>
                    <p className={`font-semibold ${result.correct ? "text-positive" : "text-danger"}`}>
                      {result.correct ? "✓ Correct!" : "✗ Incorrect"}
                    </p>
                    <p className="text-sm mt-2 text-muted-foreground">{result.explanation}</p>
                    <Button className="mt-3" size="sm" onClick={handleGetQuestion}>Next Question</Button>
                  </div>
                )}
              </CardContent>
            </Card>
          )}
        </main>
      </div>
    </div>
  );
}
```

- [ ] **Step 2: Commit**

```powershell
cd C:\Rohan\finance-hub
git add finance-hub-frontend/app/study/
git commit -m "feat: add Study Assistant page with flashcard and MCQ modes"
```

---

### Task 34: Create Portfolio Analyzer page

**Files:**
- Create: `finance-hub-frontend/app/portfolio/page.tsx`

- [ ] **Step 1: Create portfolio/page.tsx**

```typescript
"use client";

import { useState } from "react";
import { useSession } from "next-auth/react";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Skeleton } from "@/components/ui/skeleton";
import { Navbar } from "@/components/layout/Navbar";
import { Sidebar } from "@/components/layout/Sidebar";
import { useToast } from "@/components/ui/use-toast";
import { analyzePortfolio } from "@/lib/api";
import { formatCurrency, pnlColor } from "@/lib/utils";
import type { Holding, PortfolioAnalysis } from "@/types";
import { PieChart, Pie, Cell, BarChart, Bar, XAxis, YAxis, Tooltip, ResponsiveContainer, Legend } from "recharts";
import { PlusCircle, Trash2 } from "lucide-react";

const CHART_COLORS = ["#3b82f6", "#10b981", "#f59e0b", "#f43f5e", "#8b5cf6", "#06b6d4", "#ec4899"];

export default function PortfolioPage() {
  const { data: session } = useSession();
  const { toast } = useToast();
  const [holdings, setHoldings] = useState<Holding[]>([]);
  const [newTicker, setNewTicker] = useState("");
  const [newShares, setNewShares] = useState("");
  const [newCost, setNewCost] = useState("");
  const [analysis, setAnalysis] = useState<PortfolioAnalysis | null>(null);
  const [loading, setLoading] = useState(false);

  const userId = (session?.user as any)?.id || session?.user?.email || "anon";

  const addHolding = () => {
    if (!newTicker || !newShares || !newCost) return;
    setHoldings(prev => [...prev, {
      ticker: newTicker.toUpperCase(),
      shares: parseFloat(newShares),
      cost_basis: parseFloat(newCost),
    }]);
    setNewTicker(""); setNewShares(""); setNewCost("");
  };

  const removeHolding = (i: number) => setHoldings(prev => prev.filter((_, idx) => idx !== i));

  const handleAnalyze = async () => {
    if (holdings.length === 0) return;
    setLoading(true);
    setAnalysis(null);
    try {
      const data = await analyzePortfolio({ user_id: userId, holdings });
      setAnalysis(data);
    } catch {
      toast({ title: "Error", description: "Could not analyze portfolio.", variant: "destructive" });
    } finally {
      setLoading(false);
    }
  };

  const sectorData = analysis
    ? Object.entries(analysis.sector_allocation).map(([name, value]) => ({ name, value: Math.round(value * 100) }))
    : [];

  const pnlData = analysis?.positions.map(p => ({
    ticker: p.ticker,
    pnl: p.pnl_percent,
  })) ?? [];

  return (
    <div className="flex min-h-screen">
      <Sidebar />
      <div className="flex-1 flex flex-col">
        <Navbar />
        <main className="p-8 max-w-5xl space-y-6">
          <h1 className="text-2xl font-bold">Portfolio Analyzer</h1>

          <Card className="bg-card border-border">
            <CardHeader><CardTitle className="text-sm">Add Holdings</CardTitle></CardHeader>
            <CardContent>
              <div className="flex gap-2 mb-4">
                <Input placeholder="Ticker" value={newTicker} onChange={e => setNewTicker(e.target.value)} className="w-24 bg-input border-border font-mono" />
                <Input placeholder="Shares" type="number" value={newShares} onChange={e => setNewShares(e.target.value)} className="w-28 bg-input border-border" />
                <Input placeholder="Cost/share" type="number" value={newCost} onChange={e => setNewCost(e.target.value)} className="w-32 bg-input border-border" />
                <Button onClick={addHolding} size="sm" variant="outline"><PlusCircle className="h-4 w-4" /></Button>
              </div>
              {holdings.length > 0 && (
                <table className="w-full text-sm">
                  <thead><tr className="text-muted-foreground text-xs"><th className="text-left">Ticker</th><th className="text-right">Shares</th><th className="text-right">Cost Basis</th><th></th></tr></thead>
                  <tbody>
                    {holdings.map((h, i) => (
                      <tr key={i} className="border-t border-border">
                        <td className="py-1 font-mono font-semibold">{h.ticker}</td>
                        <td className="py-1 text-right font-mono">{h.shares}</td>
                        <td className="py-1 text-right font-mono">${h.cost_basis.toFixed(2)}</td>
                        <td className="py-1 text-right"><Button variant="ghost" size="sm" onClick={() => removeHolding(i)}><Trash2 className="h-3 w-3" /></Button></td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              )}
              <Button className="mt-4" onClick={handleAnalyze} disabled={loading || holdings.length === 0}>
                {loading ? "Analyzing..." : "Analyze Portfolio"}
              </Button>
            </CardContent>
          </Card>

          {loading && <Skeleton className="h-64 w-full" />}

          {analysis && (
            <>
              <div className="grid grid-cols-2 md:grid-cols-4 gap-3">
                {[
                  { label: "Total Value", value: formatCurrency(analysis.total_value) },
                  { label: "Total Cost", value: formatCurrency(analysis.total_cost) },
                  { label: "Total P&L", value: formatCurrency(analysis.total_pnl_dollar), color: pnlColor(analysis.total_pnl_dollar) },
                  { label: "Return", value: `${analysis.total_pnl_percent.toFixed(2)}%`, color: pnlColor(analysis.total_pnl_percent) },
                ].map(({ label, value, color }) => (
                  <Card key={label} className="bg-card border-border">
                    <CardContent className="pt-4"><p className="text-xs text-muted-foreground">{label}</p><p className={`font-mono font-bold text-lg ${color ?? ""}`}>{value}</p></CardContent>
                  </Card>
                ))}
              </div>

              <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                <Card className="bg-card border-border">
                  <CardHeader><CardTitle className="text-sm">Sector Allocation</CardTitle></CardHeader>
                  <CardContent>
                    <ResponsiveContainer width="100%" height={200}>
                      <PieChart>
                        <Pie data={sectorData} dataKey="value" nameKey="name" cx="50%" cy="50%" outerRadius={80} label={({ name, value }) => `${name} ${value}%`}>
                          {sectorData.map((_, i) => <Cell key={i} fill={CHART_COLORS[i % CHART_COLORS.length]} />)}
                        </Pie>
                        <Tooltip />
                      </PieChart>
                    </ResponsiveContainer>
                  </CardContent>
                </Card>

                <Card className="bg-card border-border">
                  <CardHeader><CardTitle className="text-sm">P&L by Position (%)</CardTitle></CardHeader>
                  <CardContent>
                    <ResponsiveContainer width="100%" height={200}>
                      <BarChart data={pnlData}>
                        <XAxis dataKey="ticker" tick={{ fontSize: 11, fill: "#94a3b8" }} />
                        <YAxis tick={{ fontSize: 11, fill: "#94a3b8" }} />
                        <Tooltip formatter={(v: number) => [`${v.toFixed(2)}%`, "P&L"]} />
                        <Bar dataKey="pnl" fill="#3b82f6" radius={[4, 4, 0, 0]} />
                      </BarChart>
                    </ResponsiveContainer>
                  </CardContent>
                </Card>
              </div>

              <Card className="bg-card border-border">
                <CardHeader><CardTitle className="text-sm">AI Commentary</CardTitle></CardHeader>
                <CardContent><p className="text-sm leading-relaxed whitespace-pre-line">{analysis.commentary}</p></CardContent>
              </Card>
            </>
          )}
        </main>
      </div>
    </div>
  );
}
```

- [ ] **Step 2: Commit**

```powershell
cd C:\Rohan\finance-hub
git add finance-hub-frontend/app/portfolio/
git commit -m "feat: add Portfolio Analyzer page with Recharts visualizations"
```

---

### Task 35: Create Sentiment Analyzer page

**Files:**
- Create: `finance-hub-frontend/app/sentiment/page.tsx`

- [ ] **Step 1: Create sentiment/page.tsx**

```typescript
"use client";

import { useState } from "react";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Skeleton } from "@/components/ui/skeleton";
import { Navbar } from "@/components/layout/Navbar";
import { Sidebar } from "@/components/layout/Sidebar";
import { useToast } from "@/components/ui/use-toast";
import { getSentiment } from "@/lib/api";
import { sentimentColor } from "@/lib/utils";
import type { SentimentResult } from "@/types";
import { Search } from "lucide-react";

const SENTIMENT_BG: Record<string, string> = {
  bullish: "bg-positive/10 border-positive/30 text-positive",
  neutral: "bg-warning/10 border-warning/30 text-warning",
  bearish: "bg-danger/10 border-danger/30 text-danger",
};

export default function SentimentPage() {
  const [query, setQuery] = useState("");
  const [result, setResult] = useState<SentimentResult | null>(null);
  const [loading, setLoading] = useState(false);
  const { toast } = useToast();

  const handleSearch = async () => {
    if (!query.trim()) return;
    setLoading(true);
    setResult(null);
    try {
      const data = await getSentiment(query.trim());
      setResult(data);
    } catch {
      toast({ title: "Not found", description: "No news found for that query.", variant: "destructive" });
    } finally {
      setLoading(false);
    }
  };

  const overallScore = result ? Math.round(result.overall_score * 100) : 0;

  return (
    <div className="flex min-h-screen">
      <Sidebar />
      <div className="flex-1 flex flex-col">
        <Navbar />
        <main className="p-8 max-w-4xl space-y-6">
          <h1 className="text-2xl font-bold">News Sentiment Analyzer</h1>

          <div className="flex gap-2">
            <Input
              placeholder="Enter company name or topic (e.g. Apple, interest rates)"
              value={query}
              onChange={e => setQuery(e.target.value)}
              onKeyDown={e => e.key === "Enter" && handleSearch()}
              className="bg-input border-border"
            />
            <Button onClick={handleSearch} disabled={loading || !query.trim()}>
              <Search className="h-4 w-4 mr-2" />
              {loading ? "Analyzing..." : "Analyze"}
            </Button>
          </div>

          {loading && (
            <div className="space-y-3">
              <Skeleton className="h-32 w-full" />
              <Skeleton className="h-64 w-full" />
            </div>
          )}

          {result && (
            <>
              <div className={`p-6 rounded-lg border ${SENTIMENT_BG[result.overall_label]}`}>
                <div className="flex items-center justify-between">
                  <div>
                    <p className="text-sm text-muted-foreground mb-1">Overall Sentiment — {result.article_count} articles</p>
                    <p className="text-4xl font-bold font-mono">{result.overall_label.toUpperCase()}</p>
                    <p className="text-lg font-mono mt-1">{overallScore > 0 ? "+" : ""}{overallScore}</p>
                  </div>
                  {result.cached && <Badge variant="outline" className="text-xs">Cached</Badge>}
                </div>
              </div>

              <Card className="bg-card border-border">
                <CardHeader><CardTitle className="text-sm">Article Sentiment Breakdown</CardTitle></CardHeader>
                <CardContent className="space-y-2">
                  {result.articles.map((article, i) => (
                    <div key={i} className="flex items-start justify-between gap-4 py-2 border-t border-border first:border-0">
                      <div className="flex-1 min-w-0">
                        <a href={article.url} target="_blank" rel="noopener noreferrer"
                          className="text-sm hover:text-primary transition-colors line-clamp-2">
                          {article.title}
                        </a>
                        <p className="text-xs text-muted-foreground mt-0.5">{article.published_at}</p>
                      </div>
                      <div className="shrink-0 text-right">
                        <Badge className={`text-xs ${
                          article.sentiment === "bullish" ? "bg-positive/20 text-positive" :
                          article.sentiment === "bearish" ? "bg-danger/20 text-danger" :
                          "bg-warning/20 text-warning"
                        }`}>
                          {article.sentiment}
                        </Badge>
                        <p className="text-xs text-muted-foreground mt-0.5 font-mono">
                          {Math.round(article.confidence * 100)}%
                        </p>
                      </div>
                    </div>
                  ))}
                </CardContent>
              </Card>
            </>
          )}
        </main>
      </div>
    </div>
  );
}
```

- [ ] **Step 2: Commit**

```powershell
cd C:\Rohan\finance-hub
git add finance-hub-frontend/app/sentiment/
git commit -m "feat: add Sentiment Analyzer page"
```

---

### Task 36: Create Chat page and History page

**Files:**
- Create: `finance-hub-frontend/app/chat/page.tsx`
- Create: `finance-hub-frontend/app/history/page.tsx`

- [ ] **Step 1: Create chat/page.tsx**

Note: `useSearchParams()` requires a `Suspense` boundary in Next.js 14 App Router. The page is split into a shell (`ChatPage`) and a client component (`ChatInner`) wrapped in `Suspense`.

```typescript
"use client";

import { Suspense, useState, useEffect, useRef } from "react";
import { useSession } from "next-auth/react";
import { useSearchParams } from "next/navigation";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { ScrollArea } from "@/components/ui/scroll-area";
import { Skeleton } from "@/components/ui/skeleton";
import { Navbar } from "@/components/layout/Navbar";
import { Sidebar } from "@/components/layout/Sidebar";
import { useToast } from "@/components/ui/use-toast";
import { sendChatMessage, getConversations, getChatHistory } from "@/lib/api";
import type { Conversation, Message } from "@/types";
import { Send, PlusCircle } from "lucide-react";

function ChatInner() {
  const { data: session } = useSession();
  const searchParams = useSearchParams();
  const { toast } = useToast();
  const [conversations, setConversations] = useState<Conversation[]>([]);
  const [activeConvId, setActiveConvId] = useState<string | null>(null);
  const [messages, setMessages] = useState<Message[]>([]);
  const [input, setInput] = useState("");
  const [sending, setSending] = useState(false);
  const bottomRef = useRef<HTMLDivElement>(null);

  const userId = (session?.user as any)?.id || session?.user?.email || "anon";

  // Pre-fill from stock research context
  useEffect(() => {
    const context = searchParams.get("context");
    if (context) setInput(context.slice(0, 500));
  }, [searchParams]);

  useEffect(() => {
    if (!session) return;
    getConversations(userId).then(setConversations).catch(() => {});
  }, [session, userId]);

  useEffect(() => {
    bottomRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [messages]);

  const loadConversation = async (convId: string) => {
    setActiveConvId(convId);
    try {
      const history = await getChatHistory(convId);
      setMessages(history);
    } catch {
      toast({ title: "Error", description: "Could not load conversation.", variant: "destructive" });
    }
  };

  const handleSend = async () => {
    if (!input.trim() || sending) return;
    const content = input.trim();
    setInput("");
    setSending(true);

    const userMsg: Message = { id: "temp", role: "user", content, created_at: new Date().toISOString() };
    setMessages(prev => [...prev, userMsg]);

    try {
      const resp = await sendChatMessage({ user_id: userId, content, conversation_id: activeConvId ?? undefined });
      if (!activeConvId) {
        setActiveConvId(resp.conversation_id);
        getConversations(userId).then(setConversations).catch(() => {});
      }
      const aiMsg: Message = { id: resp.message_id, role: "assistant", content: resp.content, created_at: resp.created_at };
      setMessages(prev => [...prev.filter(m => m.id !== "temp"), userMsg, aiMsg]);
    } catch {
      setMessages(prev => prev.filter(m => m.id !== "temp"));
      toast({ title: "Error", description: "Message failed. Try again.", variant: "destructive" });
    } finally {
      setSending(false);
    }
  };

  return (
    <div className="flex flex-1 overflow-hidden">
          {/* Conversation list */}
          <aside className="w-56 border-r border-border bg-card flex flex-col">
            <div className="p-3 border-b border-border">
              <Button size="sm" variant="outline" className="w-full" onClick={() => { setActiveConvId(null); setMessages([]); }}>
                <PlusCircle className="h-4 w-4 mr-2" /> New Chat
              </Button>
            </div>
            <ScrollArea className="flex-1">
              {conversations.map(c => (
                <button
                  key={c.id}
                  onClick={() => loadConversation(c.id)}
                  className={`w-full text-left px-3 py-2 text-sm border-b border-border hover:bg-secondary transition-colors ${activeConvId === c.id ? "bg-secondary text-foreground" : "text-muted-foreground"}`}
                >
                  <p className="truncate">{c.title}</p>
                  <p className="text-xs text-muted-foreground mt-0.5">{new Date(c.created_at).toLocaleDateString()}</p>
                </button>
              ))}
            </ScrollArea>
          </aside>

          {/* Chat area */}
          <div className="flex-1 flex flex-col">
            <ScrollArea className="flex-1 p-6">
              {messages.length === 0 && (
                <p className="text-center text-muted-foreground mt-16">Start a conversation about finance, markets, or anything financial.</p>
              )}
              <div className="space-y-4 max-w-3xl mx-auto">
                {messages.map((m, i) => (
                  <div key={i} className={`flex ${m.role === "user" ? "justify-end" : "justify-start"}`}>
                    <div className={`max-w-[75%] rounded-lg px-4 py-3 text-sm leading-relaxed ${
                      m.role === "user" ? "bg-primary text-primary-foreground" : "bg-card border border-border"
                    }`}>
                      {m.content}
                    </div>
                  </div>
                ))}
                {sending && (
                  <div className="flex justify-start">
                    <div className="bg-card border border-border rounded-lg px-4 py-3">
                      <Skeleton className="h-4 w-32" />
                    </div>
                  </div>
                )}
                <div ref={bottomRef} />
              </div>
            </ScrollArea>

            <div className="border-t border-border p-4">
              <div className="flex gap-2 max-w-3xl mx-auto">
                <Input
                  placeholder="Ask anything about finance, markets, or investments..."
                  value={input}
                  onChange={e => setInput(e.target.value)}
                  onKeyDown={e => e.key === "Enter" && !e.shiftKey && handleSend()}
                  className="bg-input border-border"
                />
                <Button onClick={handleSend} disabled={sending || !input.trim()}>
                  <Send className="h-4 w-4" />
                </Button>
              </div>
            </div>
          </div>
    </div>
  );
}

export default function ChatPage() {
  return (
    <div className="flex min-h-screen">
      <Sidebar />
      <div className="flex-1 flex flex-col">
        <Navbar />
        <Suspense fallback={<div className="flex-1 flex items-center justify-center text-muted-foreground">Loading...</div>}>
          <ChatInner />
        </Suspense>
      </div>
    </div>
  );
}
```

- [ ] **Step 2: Create history/page.tsx**

```typescript
"use client";

import { useEffect, useState } from "react";
import { useSession } from "next-auth/react";
import { Card, CardContent } from "@/components/ui/card";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";
import { Navbar } from "@/components/layout/Navbar";
import { Sidebar } from "@/components/layout/Sidebar";
import { getConversations, listDocuments } from "@/lib/api";
import type { Conversation, Document } from "@/types";
import Link from "next/link";
import { MessageSquare, FileText } from "lucide-react";

export default function HistoryPage() {
  const { data: session } = useSession();
  const [conversations, setConversations] = useState<Conversation[]>([]);
  const [documents, setDocuments] = useState<Document[]>([]);

  const userId = (session?.user as any)?.id || session?.user?.email || "anon";

  useEffect(() => {
    if (!session) return;
    getConversations(userId).then(setConversations).catch(() => {});
    listDocuments(userId).then(setDocuments).catch(() => {});
  }, [session, userId]);

  return (
    <div className="flex min-h-screen">
      <Sidebar />
      <div className="flex-1 flex flex-col">
        <Navbar />
        <main className="p-8 max-w-3xl">
          <h1 className="text-2xl font-bold mb-6">History</h1>
          <Tabs defaultValue="conversations">
            <TabsList className="mb-4">
              <TabsTrigger value="conversations">Conversations</TabsTrigger>
              <TabsTrigger value="documents">Documents</TabsTrigger>
            </TabsList>

            <TabsContent value="conversations" className="space-y-2">
              {conversations.length === 0 && <p className="text-muted-foreground text-sm">No conversations yet.</p>}
              {conversations.map(c => (
                <Link key={c.id} href={`/chat?conv=${c.id}`}>
                  <Card className="bg-card border-border hover:border-primary transition-colors cursor-pointer">
                    <CardContent className="flex items-center gap-3 py-3">
                      <MessageSquare className="h-4 w-4 text-muted-foreground shrink-0" />
                      <div className="min-w-0">
                        <p className="text-sm truncate">{c.title}</p>
                        <p className="text-xs text-muted-foreground">{new Date(c.created_at).toLocaleDateString()}</p>
                      </div>
                    </CardContent>
                  </Card>
                </Link>
              ))}
            </TabsContent>

            <TabsContent value="documents" className="space-y-2">
              {documents.length === 0 && <p className="text-muted-foreground text-sm">No documents uploaded yet.</p>}
              {documents.map(d => (
                <Card key={d.id} className="bg-card border-border">
                  <CardContent className="flex items-center gap-3 py-3">
                    <FileText className="h-4 w-4 text-muted-foreground shrink-0" />
                    <div className="min-w-0">
                      <p className="text-sm truncate">{d.filename}</p>
                      <p className="text-xs text-muted-foreground">{new Date(d.uploaded_at).toLocaleDateString()}</p>
                    </div>
                  </CardContent>
                </Card>
              ))}
            </TabsContent>
          </Tabs>
        </main>
      </div>
    </div>
  );
}
```

- [ ] **Step 3: Commit**

```powershell
cd C:\Rohan\finance-hub
git add finance-hub-frontend/app/chat/ finance-hub-frontend/app/history/
git commit -m "feat: add Chat and History pages"
```

---

### Task 37: Create next.config.ts and verify full build

**Files:**
- Modify: `finance-hub-frontend/next.config.ts`

- [ ] **Step 1: Update next.config.ts**

Replace `finance-hub-frontend/next.config.ts` with:

```typescript
import type { NextConfig } from "next";

const nextConfig: NextConfig = {
  async rewrites() {
    return [
      {
        source: "/api/backend/:path*",
        destination: `${process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000"}/:path*`,
      },
    ];
  },
  images: {
    domains: [],
  },
};

export default nextConfig;
```

- [ ] **Step 2: Run full build to verify no TypeScript errors**

```powershell
cd C:\Rohan\finance-hub\finance-hub-frontend
npm run build
```
Expected: `Build succeeded` — no TypeScript compilation errors.

If errors appear, fix them before committing. Common fixes:
- Missing `"use client"` directive on pages using hooks
- Import path issues (use `@/` prefix)
- Unused variables (prefix with `_` or remove)

- [ ] **Step 3: Test locally**

```powershell
npm run dev
```
Open http://localhost:3000 — verify landing page loads with the dark theme.

- [ ] **Step 4: Commit and push**

```powershell
cd C:\Rohan\finance-hub
git add finance-hub-frontend/next.config.ts
git add finance-hub-frontend/
git commit -m "feat: complete Next.js frontend — all pages and components"
git push origin main
```

> ✅ **Phase 3 complete.** Tell the user: "Phase 3 (Next.js frontend) is complete. The frontend runs at http://localhost:3000. Please verify the landing page and dashboard load correctly, then I'll proceed to Phase 4 (deployment)."

---

## PHASE 4: Deployment

### Task 38: Configure Render deployment

**Files:**
- Verify: `finance-hub-backend/render.yaml` (already created in Task 22)

- [ ] **Step 1: Confirm render.yaml exists with correct content**

The file `finance-hub-backend/render.yaml` should contain:
```yaml
services:
  - type: web
    name: finance-hub-api
    runtime: python
    rootDir: finance-hub-backend
    buildCommand: pip install -r requirements.txt
    startCommand: uvicorn main:app --host 0.0.0.0 --port $PORT
    envVars:
      - key: PYTHON_VERSION
        value: 3.11.0
```

- [ ] **Step 2: Add all backend env vars to Render dashboard**

In the Render dashboard for the `finance-hub-api` service, add these Environment Variables:

| Key | Value (from .env file) |
|-----|----------------------|
| `DATABASE_URL` | value from .env |
| `PINECONE_API_KEY` | value from .env |
| `PINECONE_INDEX_NAME` | `finance-hub` |
| `PINECONE_ENVIRONMENT` | `us-east-1` |
| `UPSTASH_REDIS_REST_URL` | value from .env |
| `UPSTASH_REDIS_REST_TOKEN` | value from .env |
| `HUGGINGFACE_API_TOKEN` | value from .env |
| `HUGGINGFACE_MODEL_ID` | `rohan1324/phi3-mini-finance-qlora` |
| `HUGGINGFACE_SPACE_URL` | `https://rohan1324-finance-hub-api.hf.space` |
| `GROQ_API_KEY` | value from .env |
| `GNEWS_API_KEY` | value from .env |
| `SUPABASE_SERVICE_ROLE_KEY` | value from .env |

- [ ] **Step 3: Trigger Render deploy**

Push to GitHub (already done in Task 37). Render will auto-deploy from main branch.

```powershell
git push origin main
```

Wait for Render build to complete (5-10 minutes). The Render URL will be something like `https://finance-hub-api-xxxx.onrender.com`.

- [ ] **Step 4: Verify Render /health endpoint**

```powershell
curl https://finance-hub-api-xxxx.onrender.com/health
```
Expected: `{"status":"ok"}`

Note the Render URL for the next step.

---

### Task 39: Configure Vercel deployment

**Files:** (no code changes — Vercel dashboard configuration)

- [ ] **Step 1: Set Vercel root directory**

In Vercel dashboard → project settings → General → Root Directory: set to `finance-hub-frontend`.

- [ ] **Step 2: Add all frontend env vars to Vercel dashboard**

In Vercel dashboard → project settings → Environment Variables:

| Key | Value |
|-----|-------|
| `NEXTAUTH_URL` | Your Vercel production URL (e.g. `https://finance-hub.vercel.app`) |
| `NEXTAUTH_SECRET` | value from .env.local |
| `NEXT_PUBLIC_API_URL` | Your Render URL (from Task 38 Step 4) |
| `NEXT_PUBLIC_SUPABASE_URL` | value from .env.local |
| `NEXT_PUBLIC_SUPABASE_ANON_KEY` | value from .env.local |

- [ ] **Step 3: Trigger Vercel deploy**

```powershell
git push origin main
```
Vercel auto-deploys on push to main.

- [ ] **Step 4: Verify Vercel landing page**

Open the Vercel production URL. Verify the landing page loads with dark theme.

---

### Task 40: Update HF Space CORS with production URLs

**Files:**
- Modify: `C:\Rohan\finance-hub-api\app.py`

- [ ] **Step 1: Update CORS origins in app.py**

In `C:\Rohan\finance-hub-api\app.py`, replace the `allow_origins` list with the actual production URLs:

```python
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "https://YOUR-ACTUAL-VERCEL-URL.vercel.app",   # replace with real Vercel URL
        "https://YOUR-ACTUAL-RENDER-URL.onrender.com", # replace with real Render URL
        "http://localhost:3000",
        "http://localhost:8000",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
```

- [ ] **Step 2: Push to HuggingFace**

```powershell
cd C:\Rohan\finance-hub-api
git add app.py
git commit -m "fix: update CORS with production URLs"
git push
```

Wait for HF Space to rebuild (~5-10 minutes).

---

### Task 41: End-to-end production verification

- [ ] **Step 1: Test Document Q&A**

Visit `/document-qa` on your Vercel URL. Upload a small PDF (any PDF under 1MB). Ask "What is this document about?". Verify an answer with citations appears.

- [ ] **Step 2: Test Earnings Summarizer**

Visit `/earnings-summarizer`. Paste this sample text (repeat to get >100 chars):
```
Good afternoon, everyone. Thank you for joining our Q3 earnings call. Revenue grew 15% year over year to $2.1 billion. Gross margin expanded to 68%, up from 65% in the prior year. We are raising our full-year guidance to $8.2 billion in revenue. Key risks include macroeconomic uncertainty and supply chain constraints. Our analyst questions focused on AI investment and international expansion.
```
Click Summarize. Verify 6 sections stream in.

- [ ] **Step 3: Test Stock Research**

Visit `/stock-research`. Search for `AAPL`. Verify a report with bull/bear case renders.

- [ ] **Step 4: Test Study Assistant**

Visit `/study`. Select CFA, Equity Valuation, Practice Exam. Click Get Question. Submit an answer. Verify result and explanation appear.

- [ ] **Step 5: Test Portfolio**

Visit `/portfolio`. Add: AAPL, 10 shares, $150 cost. Click Analyze. Verify P&L, charts, and AI commentary appear.

- [ ] **Step 6: Test Sentiment**

Visit `/sentiment`. Search `Apple`. Verify sentiment score and article list appear.

- [ ] **Step 7: Test Chat**

Visit `/chat`. Send "What is the P/E ratio and why does it matter?". Verify a response comes back and appears in the conversation list.

- [ ] **Step 8: Final push**

```powershell
cd C:\Rohan\finance-hub
git push origin main
```

> ✅ **Phase 4 complete.** Tell the user: "All 4 phases are complete. Finance Hub is live. Provide the user with: Vercel URL, Render URL, and the HF Space URL."

---

## PHASE 5: Final README

### Task 42: Write comprehensive README.md

**Files:**
- Modify: `C:\Rohan\finance-hub\README.md`

- [ ] **Step 1: Replace README.md with full documentation**

Replace `C:\Rohan\finance-hub\README.md` with:

```markdown
# Finance Hub — AI-Powered Financial Research Platform

> A full-stack AI financial research platform with 7 specialized modules, backed by a fine-tuned Phi-3 Mini language model and Groq Llama 3.1 70B.

**Live Demo:** [finance-hub.vercel.app](https://finance-hub.vercel.app)  
**API:** [finance-hub-api.onrender.com](https://finance-hub-api.onrender.com)  
**Model Server:** [rohan1324-finance-hub-api.hf.space](https://rohan1324-finance-hub-api.hf.space)

---

## Features

| Module | Description | Model |
|--------|-------------|-------|
| Document Q&A | Upload PDFs, ask questions with page-level citations | Phi-3 Mini (fine-tuned) |
| Earnings Summarizer | Structured earnings call analysis with SSE streaming | Phi-3 Mini (fine-tuned) |
| Stock Research | AI agent with live market data tools | Groq Llama 3.1 70B |
| Study Assistant | CFA/Series 7/FRM/CPA prep with flashcards and MCQs | Phi-3 Mini (fine-tuned) |
| Portfolio Analyzer | P&L, allocation, concentration risk + AI commentary | Groq Llama 3.1 70B |
| Sentiment Analyzer | 30-day news sentiment classification with caching | Phi-3 Mini (fine-tuned) |
| Financial Chat | Persistent chat with sliding context window | Phi-3 Mini (fine-tuned) |

---

## Tech Stack

| Layer | Technology |
|-------|-----------|
| Frontend | Next.js 14, TypeScript, Tailwind CSS, shadcn/ui |
| Backend | FastAPI, Python 3.11, asyncpg, SQLAlchemy |
| Database | Supabase PostgreSQL |
| Vector Store | Pinecone (384-dim, cosine) |
| Cache | Upstash Redis |
| Model Server | HuggingFace Spaces (Phi-3 Mini + LoRA) |
| Fast LLM | Groq (Llama 3.1 70B) |
| Auth | NextAuth.js (email magic link) |
| Hosting | Vercel (frontend), Render (backend) |

---

## Architecture

```
Browser → Next.js (Vercel)
              │
              ├── /api/auth    ← NextAuth.js
              │
              └── FastAPI (Render)
                      │
                      ├── HuggingFace Space  (Phi-3 Mini fine-tuned)
                      ├── Groq API           (Llama 3.1 70B)
                      ├── Pinecone           (vector search)
                      ├── Supabase           (PostgreSQL)
                      ├── Upstash Redis      (caching)
                      ├── yfinance           (stock data)
                      ├── SEC EDGAR API      (filings)
                      └── GNews + Reuters    (news)
```

---

## Local Development

### Prerequisites
- Python 3.11+
- Node.js 18+
- Git

### Backend

```bash
cd finance-hub-backend
pip install -r requirements.txt
uvicorn main:app --reload --port 8000
```

### Frontend

```bash
cd finance-hub-frontend
npm install
npm run dev
```

Open http://localhost:3000

---

## Environment Variables

### Backend (`.env`)

| Variable | Description |
|----------|-------------|
| `DATABASE_URL` | Supabase PostgreSQL connection string |
| `PINECONE_API_KEY` | Pinecone API key |
| `PINECONE_INDEX_NAME` | Pinecone index name (`finance-hub`) |
| `HUGGINGFACE_SPACE_URL` | HF Space URL for model inference |
| `GROQ_API_KEY` | Groq API key |
| `GNEWS_API_KEY` | GNews API key |
| `UPSTASH_REDIS_REST_URL` | Upstash Redis REST URL |
| `UPSTASH_REDIS_REST_TOKEN` | Upstash Redis REST token |
| `SUPABASE_SERVICE_ROLE_KEY` | Supabase service role key |

### Frontend (`.env.local`)

| Variable | Description |
|----------|-------------|
| `NEXTAUTH_URL` | Your app URL |
| `NEXTAUTH_SECRET` | Random secret (`openssl rand -base64 32`) |
| `NEXT_PUBLIC_API_URL` | Backend API URL |
| `NEXT_PUBLIC_SUPABASE_URL` | Supabase project URL |
| `NEXT_PUBLIC_SUPABASE_ANON_KEY` | Supabase anon key |

---

## Known Limitations

- HF Space CPU inference takes 30-60s per request — free tier constraint
- Render free tier spins down after 15 min inactivity (~30s cold start)
- Portfolio correlation matrix uses placeholder values (requires historical price data for real correlations)
- Email auth requires SMTP configuration; magic links won't work without email server setup
- Google OAuth requires additional Google Cloud Console setup

## Future Improvements

- Add historical price correlation using yfinance `.history()` for real correlation matrices
- Add Google OAuth once Google Cloud OAuth consent screen is configured
- Add WebSocket support for real-time portfolio price updates
- Add PDF annotation overlay showing highlighted cited passages
- Add export to PDF for research reports
```

- [ ] **Step 2: Commit and push**

```powershell
cd C:\Rohan\finance-hub
git add README.md
git commit -m "docs: add comprehensive README with architecture, setup, and API docs"
git push origin main
```

> 🎉 **All 5 phases complete.** Finance Hub is fully built and deployed.
