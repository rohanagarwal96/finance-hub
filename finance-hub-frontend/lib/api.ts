import axios from "axios";
import type {
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
  timeout: 130000,
});

// Chat
export async function sendChatMessage(params: {
  conversation_id?: string;
  message: string;
}): Promise<{ conversation_id: string; content: string; message_id: string }> {
  if (params.conversation_id) {
    const { data } = await api.post(
      `/chat/conversations/${params.conversation_id}/messages`,
      { content: params.message }
    );
    return data;
  }
  const { data: conv } = await api.post("/chat/conversations");
  const { data } = await api.post(
    `/chat/conversations/${conv.conversation_id}/messages`,
    { content: params.message }
  );
  return { ...data, conversation_id: conv.conversation_id };
}

export async function getChatHistory(conversationId: string): Promise<Message[]> {
  const { data } = await api.get(`/chat/conversations/${conversationId}/messages`);
  return data;
}

export async function getConversations(): Promise<Conversation[]> {
  const { data } = await api.get("/chat/conversations");
  return data;
}

// Document Q&A
export async function uploadDocument(file: File): Promise<{
  document_id: string;
  filename: string;
  chunk_count: number;
}> {
  const form = new FormData();
  form.append("file", file);
  const { data } = await api.post("/documents/upload", form, {
    headers: { "Content-Type": "multipart/form-data" },
  });
  return data;
}

export async function queryDocument(params: {
  document_id: string;
  question: string;
}): Promise<{ answer: string; citations: Citation[] }> {
  const { data } = await api.post("/documents/query", params);
  return data;
}

export async function listDocuments(): Promise<Document[]> {
  const { data } = await api.get("/documents/");
  return data;
}

// Research
export async function getResearchReport(ticker: string, focus = "comprehensive"): Promise<ResearchReport> {
  const { data } = await api.post("/research/", { ticker, focus });
  return data;
}

// Study
export async function generateStudyQuestions(
  params: { examType: string; topic: string; mode: string },
  numQuestions = 5
): Promise<StudyQuestion[]> {
  const { data } = await api.post(
    `/study/generate?num_questions=${numQuestions}`,
    { exam_type: params.examType, topic: params.topic, mode: params.mode, user_id: "anonymous" }
  );
  return data;
}

export async function submitStudyAttempt(params: {
  examType: string;
  topic: string;
  question: string;
  user_answer: string;
  correct_answer: string;
}): Promise<StudyAttemptResult> {
  const { data } = await api.post("/study/attempt", {
    user_id: "anonymous",
    exam_type: params.examType,
    topic: params.topic,
    question: params.question,
    user_answer: params.user_answer,
    correct_answer: params.correct_answer,
  });
  return data;
}

export async function getStudyPerformance(documentId: string): Promise<{ topics: TopicPerformance[] }> {
  const { data } = await api.get(`/study/performance/${documentId}`);
  return data;
}

// Portfolio
export async function analyzePortfolio(params: {
  holdings: Holding[];
  risk_tolerance?: string;
}): Promise<PortfolioAnalysis> {
  const { data } = await api.post("/portfolio/analyze", params);
  return data;
}

// Sentiment
export async function getSentiment(ticker: string, days = 30): Promise<SentimentResult> {
  const { data } = await api.get(`/sentiment/${encodeURIComponent(ticker)}?days=${days}`);
  return data;
}
