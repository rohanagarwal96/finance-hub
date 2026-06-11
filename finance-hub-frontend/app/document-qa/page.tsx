"use client";

import { useState, useCallback } from "react";
import { useDropzone } from "react-dropzone";
import { toast } from "sonner";
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
  const [docId, setDocId] = useState<string | null>(null);
  const [docName, setDocName] = useState<string>("");
  const [uploading, setUploading] = useState(false);
  const [question, setQuestion] = useState("");
  const [answer, setAnswer] = useState("");
  const [citations, setCitations] = useState<Citation[]>([]);
  const [querying, setQuerying] = useState(false);

  const onDrop = useCallback(async (files: File[]) => {
    const file = files[0];
    if (!file) return;
    if (file.size > 10 * 1024 * 1024) {
      toast.error("PDF must be under 10 MB.");
      return;
    }
    setUploading(true);
    try {
      const result = await uploadDocument(file);
      setDocId(result.document_id);
      setDocName(file.name);
      toast.success(`Uploaded — ${result.chunk_count} chunks indexed.`);
    } catch {
      toast.error("Could not process PDF.");
    } finally {
      setUploading(false);
    }
  }, []);

  const { getRootProps, getInputProps, isDragActive } = useDropzone({
    onDrop, accept: { "application/pdf": [".pdf"] }, maxFiles: 1,
  });

  const handleQuery = async () => {
    if (!docId || !question.trim()) return;
    setQuerying(true);
    setAnswer("");
    setCitations([]);
    try {
      const result = await queryDocument({ document_id: docId, question });
      setAnswer(result.answer);
      setCitations(result.citations);
    } catch {
      toast.error("Could not get answer. Try again.");
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
