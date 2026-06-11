"use client";

import { useState } from "react";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Skeleton } from "@/components/ui/skeleton";
import { Navbar } from "@/components/layout/Navbar";
import { Sidebar } from "@/components/layout/Sidebar";
import { toast } from "sonner";
import { analyzePortfolio } from "@/lib/api";
import { formatCurrency, pnlColor } from "@/lib/utils";
import type { Holding, PortfolioAnalysis } from "@/types";
import { BarChart, Bar, XAxis, YAxis, Tooltip, ResponsiveContainer } from "recharts";
import { PlusCircle, Trash2 } from "lucide-react";

export default function PortfolioPage() {
  const [holdings, setHoldings] = useState<Holding[]>([]);
  const [newTicker, setNewTicker] = useState("");
  const [newShares, setNewShares] = useState("");
  const [newCost, setNewCost] = useState("");
  const [analysis, setAnalysis] = useState<PortfolioAnalysis | null>(null);
  const [loading, setLoading] = useState(false);

  const addHolding = () => {
    if (!newTicker || !newShares || !newCost) return;
    setHoldings(prev => [...prev, {
      ticker: newTicker.toUpperCase(),
      shares: parseFloat(newShares),
      avg_cost: parseFloat(newCost),
    }]);
    setNewTicker(""); setNewShares(""); setNewCost("");
  };

  const removeHolding = (i: number) => setHoldings(prev => prev.filter((_, idx) => idx !== i));

  const handleAnalyze = async () => {
    if (holdings.length === 0) return;
    setLoading(true);
    setAnalysis(null);
    try {
      const data = await analyzePortfolio({ holdings });
      setAnalysis(data);
    } catch {
      toast.error("Could not analyze portfolio.");
    } finally {
      setLoading(false);
    }
  };

  const pnlChartData = analysis?.positions.map(p => ({
    ticker: p.ticker,
    pnl: p.gain_loss_pct,
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
                <table className="w-full text-sm mb-4">
                  <thead><tr className="text-muted-foreground text-xs"><th className="text-left">Ticker</th><th className="text-right">Shares</th><th className="text-right">Avg Cost</th><th></th></tr></thead>
                  <tbody>
                    {holdings.map((h, i) => (
                      <tr key={i} className="border-t border-border">
                        <td className="py-1 font-mono font-semibold">{h.ticker}</td>
                        <td className="py-1 text-right font-mono">{h.shares}</td>
                        <td className="py-1 text-right font-mono">${h.avg_cost.toFixed(2)}</td>
                        <td className="py-1 text-right"><Button variant="ghost" size="sm" onClick={() => removeHolding(i)}><Trash2 className="h-3 w-3" /></Button></td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              )}
              <Button onClick={handleAnalyze} disabled={loading || holdings.length === 0}>
                {loading ? "Analyzing..." : "Analyze Portfolio"}
              </Button>
            </CardContent>
          </Card>
          {loading && <Skeleton className="h-64 w-full" />}
          {analysis && (
            <>
              <div className="grid grid-cols-2 md:grid-cols-4 gap-3">
                {[
                  { label: "Total Value", value: formatCurrency(analysis.summary.total_value) },
                  { label: "Total Cost", value: formatCurrency(analysis.summary.total_cost) },
                  { label: "Total P&L", value: formatCurrency(analysis.summary.total_gain_loss), color: pnlColor(analysis.summary.total_gain_loss) },
                  { label: "Return", value: `${analysis.summary.total_return_pct.toFixed(2)}%`, color: pnlColor(analysis.summary.total_return_pct) },
                ].map(({ label, value, color }) => (
                  <Card key={label} className="bg-card border-border">
                    <CardContent className="pt-4"><p className="text-xs text-muted-foreground">{label}</p><p className={`font-mono font-bold text-lg ${color ?? ""}`}>{value}</p></CardContent>
                  </Card>
                ))}
              </div>
              <Card className="bg-card border-border">
                <CardHeader><CardTitle className="text-sm">P&L by Position (%)</CardTitle></CardHeader>
                <CardContent>
                  <ResponsiveContainer width="100%" height={200}>
                    <BarChart data={pnlChartData}>
                      <XAxis dataKey="ticker" tick={{ fontSize: 11, fill: "#94a3b8" }} />
                      <YAxis tick={{ fontSize: 11, fill: "#94a3b8" }} />
                      <Tooltip formatter={(v: number) => [`${v.toFixed(2)}%`, "P&L"]} />
                      <Bar dataKey="pnl" fill="#3b82f6" radius={[4, 4, 0, 0]} />
                    </BarChart>
                  </ResponsiveContainer>
                </CardContent>
              </Card>
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
