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
import { toast } from "sonner";
import { sendChatMessage, getConversations, getChatHistory } from "@/lib/api";
import type { Conversation, Message } from "@/types";
import { Send, PlusCircle } from "lucide-react";

function ChatInner() {
  const { data: session } = useSession();
  const searchParams = useSearchParams();
  const [conversations, setConversations] = useState<Conversation[]>([]);
  const [activeConvId, setActiveConvId] = useState<string | null>(null);
  const [messages, setMessages] = useState<Message[]>([]);
  const [input, setInput] = useState("");
  const [sending, setSending] = useState(false);
  const bottomRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    const context = searchParams.get("context");
    if (context) setInput(context.slice(0, 500));
  }, [searchParams]);

  useEffect(() => {
    if (!session) return;
    getConversations().then(setConversations).catch(() => {});
  }, [session]);

  useEffect(() => {
    bottomRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [messages]);

  const loadConversation = async (convId: string) => {
    setActiveConvId(convId);
    try {
      const history = await getChatHistory(convId);
      setMessages(history);
    } catch {
      toast.error("Could not load conversation.");
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
      const resp = await sendChatMessage({ conversation_id: activeConvId ?? undefined, message: content });
      if (!activeConvId) {
        setActiveConvId(resp.conversation_id);
        getConversations().then(setConversations).catch(() => {});
      }
      const aiMsg: Message = {
        id: resp.message_id,
        role: "assistant",
        content: resp.reply,
        created_at: new Date().toISOString(),
      };
      setMessages(prev => [...prev.filter(m => m.id !== "temp"), userMsg, aiMsg]);
    } catch {
      setMessages(prev => prev.filter(m => m.id !== "temp"));
      toast.error("Message failed. Try again.");
    } finally {
      setSending(false);
    }
  };

  return (
    <div className="flex flex-1 overflow-hidden">
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
              <p className="truncate">{c.title || "Untitled"}</p>
              <p className="text-xs text-muted-foreground mt-0.5">{new Date(c.created_at).toLocaleDateString()}</p>
            </button>
          ))}
        </ScrollArea>
      </aside>
      <div className="flex-1 flex flex-col">
        <ScrollArea className="flex-1 p-6">
          {messages.length === 0 && (
            <p className="text-center text-muted-foreground mt-16">Start a conversation about finance, markets, or investments.</p>
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
