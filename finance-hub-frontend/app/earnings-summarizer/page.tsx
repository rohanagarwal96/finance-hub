"use client";

import { useState } from "react";
import { Button } from "@/components/ui/button";
import { Textarea } from "@/components/ui/textarea";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Skeleton } from "@/components/ui/skeleton";
import { Navbar } from "@/components/layout/Navbar";
import { Sidebar } from "@/components/layout/Sidebar";
import { toast } from "sonner";

interface SummarySection {
  title: string;
  content: string;
}

export default function EarningsSummarizerPage() {
  const [transcript, setTranscript] = useState("");
  const [sections, setSections] = useState<SummarySection[]>([]);
  const [status, setStatus] = useState("");
  const [running, setRunning] = useState(false);

  const handleSummarize = async () => {
    if (!transcript.trim() || transcript.length < 100) {
      toast.error("Transcript must be at least 100 characters.");
      return;
    }
    setSections([]);
    setStatus("");
    setRunning(true);

    const apiUrl = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";
    try {
      const response = await fetch(`${apiUrl}/summarizer/`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ transcript }),
      });
      if (!response.ok) throw new Error("Request failed");
      const data = await response.json();
      setSections([
        { title: "Summary", content: data.summary || data.report || JSON.stringify(data) },
      ]);
    } catch {
      toast.error("Failed to summarize.");
    } finally {
      setRunning(false);
    }
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
          {status && <p className="text-sm text-muted-foreground animate-pulse">{status}</p>}
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
                <p className="text-sm leading-relaxed whitespace-pre-line">{section.content}</p>
              </CardContent>
            </Card>
          ))}
        </main>
      </div>
    </div>
  );
}
