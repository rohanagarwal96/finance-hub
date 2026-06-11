"use client";

import { useState } from "react";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select";
import { Badge } from "@/components/ui/badge";
import { Skeleton } from "@/components/ui/skeleton";
import { Navbar } from "@/components/layout/Navbar";
import { Sidebar } from "@/components/layout/Sidebar";
import { toast } from "sonner";
import { generateStudyQuestions, submitStudyAttempt } from "@/lib/api";
import type { StudyQuestion } from "@/types";

const EXAM_TYPES = ["CFA", "Series7", "FRM", "CPA"];
const TOPICS: Record<string, string[]> = {
  CFA: ["Equity Valuation", "Fixed Income", "Derivatives", "Portfolio Management", "Ethics"],
  Series7: ["Equity Securities", "Debt Securities", "Options", "Mutual Funds"],
  FRM: ["Market Risk", "Credit Risk", "Operational Risk", "Quantitative Analysis"],
  CPA: ["Financial Accounting", "Auditing", "Taxation", "Business Law"],
};

export default function StudyPage() {
  const [exam, setExam] = useState("CFA");
  const [topic, setTopic] = useState(TOPICS["CFA"][0]);
  const [questions, setQuestions] = useState<StudyQuestion[]>([]);
  const [currentIdx, setCurrentIdx] = useState(0);
  const [selectedAnswer, setSelectedAnswer] = useState<string | null>(null);
  const [result, setResult] = useState<{ correct: boolean; explanation: string } | null>(null);
  const [loading, setLoading] = useState(false);
  const [flipped, setFlipped] = useState(false);
  const [mode, setMode] = useState<"practice" | "flashcard">("practice");

  const currentQuestion = questions[currentIdx] ?? null;

  const handleGenerateQuestions = async () => {
    setLoading(true);
    setQuestions([]);
    setCurrentIdx(0);
    setSelectedAnswer(null);
    setResult(null);
    setFlipped(false);
    try {
      // Use a placeholder document ID — study generates generic questions
      const qs = await generateStudyQuestions("general", 5);
      setQuestions(qs);
    } catch {
      toast.error("Could not generate questions.");
    } finally {
      setLoading(false);
    }
  };

  const handleAnswer = async (answer: string) => {
    if (!currentQuestion || result) return;
    setSelectedAnswer(answer);
    try {
      const res = await submitStudyAttempt({
        question_id: "temp",
        user_answer: answer,
      });
      setResult(res);
    } catch {
      toast.error("Could not submit answer.");
    }
  };

  const handleNext = () => {
    setSelectedAnswer(null);
    setResult(null);
    setFlipped(false);
    if (currentIdx < questions.length - 1) {
      setCurrentIdx(prev => prev + 1);
    } else {
      toast.success("All questions completed!");
      setQuestions([]);
      setCurrentIdx(0);
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
                {EXAM_TYPES.map(e => <SelectItem key={e} value={e}>{e}</SelectItem>)}
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
            <Select value={mode} onValueChange={(v) => setMode(v as "practice" | "flashcard")}>
              <SelectTrigger className="w-40 bg-input border-border">
                <SelectValue placeholder="Mode" />
              </SelectTrigger>
              <SelectContent>
                <SelectItem value="practice">Practice Exam</SelectItem>
                <SelectItem value="flashcard">Flashcard</SelectItem>
              </SelectContent>
            </Select>
            <Button onClick={handleGenerateQuestions} disabled={loading}>
              {loading ? "Generating..." : "Get Questions"}
            </Button>
          </div>
          {loading && <Skeleton className="h-48 w-full" />}
          {currentQuestion && mode === "flashcard" && (
            <Card
              className="bg-card border-border cursor-pointer min-h-48 flex items-center justify-center"
              onClick={() => setFlipped(!flipped)}
            >
              <CardContent className="text-center p-8">
                {!flipped ? (
                  <>
                    <p className="text-xs text-muted-foreground mb-4">Click to reveal answer</p>
                    <p className="text-lg font-medium">{currentQuestion.question}</p>
                  </>
                ) : (
                  <>
                    <Badge className="mb-4 bg-positive">Answer</Badge>
                    <p className="text-lg font-medium">{currentQuestion.correct_answer}</p>
                    <p className="text-sm text-muted-foreground mt-4">{currentQuestion.explanation}</p>
                    <Button className="mt-4" size="sm" onClick={(e) => { e.stopPropagation(); handleNext(); }}>Next</Button>
                  </>
                )}
              </CardContent>
            </Card>
          )}
          {currentQuestion && mode === "practice" && (
            <Card className="bg-card border-border">
              <CardHeader>
                <Badge variant="outline" className="w-fit mb-2">{currentQuestion.exam_type} — {currentQuestion.topic}</Badge>
                <CardTitle className="text-base font-medium leading-relaxed">{currentQuestion.question}</CardTitle>
              </CardHeader>
              <CardContent className="space-y-2">
                {currentQuestion.options?.map((option, i) => {
                  const isSelected = selectedAnswer === option;
                  const isCorrect = result && option === currentQuestion.correct_answer;
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
                {!currentQuestion.options && (
                  <p className="text-sm text-muted-foreground">Answer: {currentQuestion.correct_answer}</p>
                )}
                {result && (
                  <div className={`mt-4 p-4 rounded-lg ${result.correct ? "bg-positive/10 border border-positive/30" : "bg-danger/10 border border-danger/30"}`}>
                    <p className={`font-semibold ${result.correct ? "text-positive" : "text-danger"}`}>
                      {result.correct ? "Correct!" : "Incorrect"}
                    </p>
                    <p className="text-sm mt-2 text-muted-foreground">{result.explanation}</p>
                    <Button className="mt-3" size="sm" onClick={handleNext}>Next Question</Button>
                  </div>
                )}
              </CardContent>
            </Card>
          )}
          {questions.length > 0 && (
            <p className="text-xs text-muted-foreground">Question {currentIdx + 1} of {questions.length}</p>
          )}
        </main>
      </div>
    </div>
  );
}
