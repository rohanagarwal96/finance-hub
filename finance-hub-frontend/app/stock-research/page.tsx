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
import { getResearchReport } from "@/lib/api";
import { formatCurrency } from "@/lib/utils";
import type { ResearchReport } from "@/types";
import { Search } from "lucide-react";

export default function StockResearchPage() {
  const [ticker, setTicker] = useState("");
  const [report, setReport] = useState<ResearchReport | null>(null);
  const [loading, setLoading] = useState(false);

  const handleSearch = async () => {
    if (!ticker.trim()) return;
    setLoading(true);
    setReport(null);
    try {
      const data = await getResearchReport(ticker.trim().toUpperCase());
      setReport(data);
    } catch {
      toast.error(`Could not find data for ${ticker}.`);
    } finally {
      setLoading(false);
    }
  };

  const financials = report?.financials as Record<string, unknown> | null;
  const marketData = report?.market_data as Record<string, unknown> | null;

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
                {marketData && (
                  <div className="text-right font-mono">
                    <p className="text-2xl font-bold">{formatCurrency(marketData.current_price as number)}</p>
                    <p className="text-sm text-muted-foreground">Market Cap: {formatCurrency(marketData.market_cap as number)}</p>
                  </div>
                )}
              </div>
              {financials && (
                <div className="grid grid-cols-2 md:grid-cols-4 gap-3">
                  {[
                    { label: "P/E Ratio", value: (financials.pe_ratio as number)?.toFixed(1) ?? "N/A" },
                    { label: "P/S Ratio", value: (financials.ps_ratio as number)?.toFixed(1) ?? "N/A" },
                    { label: "Operating Margin", value: financials.operating_margin != null ? `${((financials.operating_margin as number) * 100).toFixed(1)}%` : "N/A" },
                    { label: "Sector", value: (financials.sector as string) ?? "N/A" },
                    { label: "Industry", value: (financials.industry as string) ?? "N/A" },
                  ].map(({ label, value }) => (
                    <Card key={label} className="bg-card border-border">
                      <CardContent className="pt-4 pb-3">
                        <p className="text-xs text-muted-foreground">{label}</p>
                        <p className="font-mono font-semibold text-sm truncate">{value}</p>
                      </CardContent>
                    </Card>
                  ))}
                </div>
              )}
              <Card className="bg-card border-border">
                <CardHeader><CardTitle className="text-sm">Research Report</CardTitle></CardHeader>
                <CardContent>
                  <p className="text-sm leading-relaxed whitespace-pre-line">{report.report}</p>
                </CardContent>
              </Card>
            </div>
          )}
        </main>
      </div>
    </div>
  );
}
