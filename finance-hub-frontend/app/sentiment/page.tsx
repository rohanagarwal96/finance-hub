"use client";

import { useState } from "react";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Skeleton } from "@/components/ui/skeleton";
import { Navbar } from "@/components/layout/Navbar";
import { Sidebar } from "@/components/layout/Sidebar";
import { toast } from "sonner";
import { getSentiment } from "@/lib/api";
import type { SentimentResult } from "@/types";
import { Search } from "lucide-react";

const SENTIMENT_STYLE: Record<string, string> = {
  bullish: "bg-positive/10 border-positive/30 text-positive",
  neutral: "bg-warning/10 border-warning/30 text-warning",
  bearish: "bg-danger/10 border-danger/30 text-danger",
};

export default function SentimentPage() {
  const [ticker, setTicker] = useState("");
  const [result, setResult] = useState<SentimentResult | null>(null);
  const [loading, setLoading] = useState(false);

  const handleSearch = async () => {
    if (!ticker.trim()) return;
    setLoading(true);
    setResult(null);
    try {
      const data = await getSentiment(ticker.trim().toUpperCase());
      setResult(data);
    } catch {
      toast.error("No news found for that ticker.");
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="flex min-h-screen">
      <Sidebar />
      <div className="flex-1 flex flex-col">
        <Navbar />
        <main className="p-8 max-w-4xl space-y-6">
          <h1 className="text-2xl font-bold">News Sentiment Analyzer</h1>
          <div className="flex gap-2">
            <Input
              placeholder="Enter ticker (e.g. AAPL, TSLA)"
              value={ticker}
              onChange={e => setTicker(e.target.value.toUpperCase())}
              onKeyDown={e => e.key === "Enter" && handleSearch()}
              className="max-w-xs bg-input border-border font-mono"
            />
            <Button onClick={handleSearch} disabled={loading || !ticker.trim()}>
              <Search className="h-4 w-4 mr-2" />
              {loading ? "Analyzing..." : "Analyze"}
            </Button>
          </div>
          {loading && <div className="space-y-3"><Skeleton className="h-32 w-full" /><Skeleton className="h-64 w-full" /></div>}
          {result && (
            <>
              <div className={`p-6 rounded-lg border ${SENTIMENT_STYLE[result.overall_sentiment] ?? ""}`}>
                <div className="flex items-center justify-between">
                  <div>
                    <p className="text-sm text-muted-foreground mb-1">{result.ticker} — {result.article_count} articles over {result.days_analyzed} days</p>
                    <p className="text-4xl font-bold font-mono">{result.overall_sentiment.toUpperCase()}</p>
                    <p className="text-lg font-mono mt-1">{result.confidence}% confidence</p>
                  </div>
                  <div className="text-right text-sm text-muted-foreground">
                    <p className="text-positive">{result.bullish_count} bullish</p>
                    <p className="text-warning">{result.neutral_count} neutral</p>
                    <p className="text-danger">{result.bearish_count} bearish</p>
                  </div>
                </div>
                {result.summary && <p className="text-sm mt-4 text-muted-foreground">{result.summary}</p>}
                {result.key_themes.length > 0 && (
                  <div className="flex flex-wrap gap-2 mt-3">
                    {result.key_themes.map((theme, i) => (
                      <Badge key={i} variant="outline" className="text-xs">{theme}</Badge>
                    ))}
                  </div>
                )}
              </div>
              <Card className="bg-card border-border">
                <CardHeader><CardTitle className="text-sm">Recent Articles</CardTitle></CardHeader>
                <CardContent className="space-y-3">
                  {result.articles.map((article, i) => (
                    <div key={i} className="py-2 border-t border-border first:border-0">
                      <a href={article.url} target="_blank" rel="noopener noreferrer"
                        className="text-sm hover:text-primary transition-colors line-clamp-2">
                        {article.title}
                      </a>
                      <div className="flex items-center gap-2 mt-1">
                        <p className="text-xs text-muted-foreground">{article.published_at}</p>
                        <Badge variant="outline" className="text-xs">{article.source}</Badge>
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
