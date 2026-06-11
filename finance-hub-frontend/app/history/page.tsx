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

  useEffect(() => {
    if (!session) return;
    getConversations().then(setConversations).catch(() => {});
    listDocuments().then(setDocuments).catch(() => {});
  }, [session]);

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
                        <p className="text-sm truncate">{c.title || "Untitled conversation"}</p>
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
