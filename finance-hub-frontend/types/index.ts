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
  report: string;
  market_data: Record<string, unknown>;
  financials: Record<string, unknown>;
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
  avg_cost: number;
}

export interface PositionAnalysis {
  ticker: string;
  shares: number;
  avg_cost: number;
  current_price: number;
  market_value: number;
  gain_loss: number;
  gain_loss_pct: number;
  weight_pct: number;
}

export interface PortfolioAnalysis {
  positions: PositionAnalysis[];
  summary: {
    total_value: number;
    total_cost: number;
    total_gain_loss: number;
    total_return_pct: number;
    top_winner: string;
    top_loser: string;
    position_count: number;
  };
  risk_tolerance: string;
  commentary: string;
}

export interface SentimentResult {
  ticker: string;
  days_analyzed: number;
  article_count: number;
  overall_sentiment: "bullish" | "neutral" | "bearish";
  confidence: number;
  bullish_count: number;
  bearish_count: number;
  neutral_count: number;
  key_themes: string[];
  summary: string;
  articles: Array<{
    title: string;
    url: string;
    published_at: string;
    source: string;
    summary: string;
  }>;
}
