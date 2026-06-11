"""Study Assistant — question generation + attempt tracking + performance."""
from __future__ import annotations

import json
import uuid
from typing import Annotated, Optional

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession

from models.database import get_db
from models.schemas import (
    StudyAttemptRequest,
    StudyAttemptResponse,
    StudyPerformanceResponse,
    StudyQuestion,
    StudyQuestionRequest,
    TopicPerformance,
)
from services.groq_service import groq_complete

router = APIRouter(prefix="/study", tags=["study"])


@router.post("/generate", response_model=list[StudyQuestion])
async def generate_questions(
    request: StudyQuestionRequest,
    num_questions: int = 5,
    db: Annotated[AsyncSession, Depends(get_db)] = None,
) -> list[StudyQuestion]:
    """Generate study questions for a given exam type and topic."""
    mode_instruction = {
        "flashcard": "Generate open-ended flashcard questions with concise answers.",
        "practice": "Generate multiple-choice questions with 4 options (A-D).",
        "weakspot": "Generate harder questions targeting common misconceptions and edge cases.",
    }.get(request.mode, "Generate practice questions.")

    prompt = (
        f"You are an expert tutor for {request.exam_type} exam preparation.\n"
        f"{mode_instruction}\n"
        f"Topic: {request.topic}\n"
        f"Generate {num_questions} questions.\n\n"
        "Return a JSON array with this structure:\n"
        '[\n'
        '  {\n'
        '    "question": "...",\n'
        '    "options": ["A) ...", "B) ...", "C) ...", "D) ..."] or null for flashcards,\n'
        '    "correct_answer": "...",\n'
        '    "explanation": "...",\n'
        '    "topic": "...",\n'
        f'    "exam_type": "{request.exam_type}"\n'
        '  }\n'
        ']\n\n'
        "Return ONLY the JSON array."
    )

    raw = await groq_complete(prompt, max_tokens=1200)

    try:
        start = raw.find("[")
        end = raw.rfind("]") + 1
        questions_data = json.loads(raw[start:end]) if start != -1 else []
    except Exception:
        questions_data = []

    questions = []
    for q in questions_data[:num_questions]:
        questions.append(
            StudyQuestion(
                question=q.get("question", ""),
                options=q.get("options"),
                correct_answer=q.get("correct_answer", ""),
                explanation=q.get("explanation", ""),
                topic=q.get("topic", request.topic),
                exam_type=q.get("exam_type", request.exam_type),
            )
        )

    return questions


@router.post("/attempt", response_model=StudyAttemptResponse)
async def submit_attempt(
    request: StudyAttemptRequest,
    db: Annotated[AsyncSession, Depends(get_db)] = None,
) -> StudyAttemptResponse:
    """Submit a study attempt and get AI feedback."""
    prompt = (
        f"Question: {request.question}\n"
        f"Correct Answer: {request.correct_answer}\n"
        f"Student Answer: {request.user_answer}\n\n"
        "Evaluate the student's answer. Return JSON:\n"
        '{"is_correct": true/false, "explanation": "..."}\n\n'
        "Be encouraging but honest. Return ONLY the JSON."
    )

    raw = await groq_complete(prompt, max_tokens=400)

    try:
        start = raw.find("{")
        end = raw.rfind("}") + 1
        eval_data = json.loads(raw[start:end]) if start != -1 else {}
    except Exception:
        eval_data = {}

    is_correct = eval_data.get("is_correct", False)
    explanation = eval_data.get("explanation", request.correct_answer)

    # Persist the attempt if db is provided
    if db is not None:
        attempt_id = str(uuid.uuid4())
        try:
            await db.execute(
                text(
                    "INSERT INTO study_attempts "
                    "(id, user_id, exam_type, topic, question, user_answer, correct_answer, is_correct, created_at) "
                    "VALUES (:id, :user_id, :exam_type, :topic, :question, :user_answer, :correct_answer, :is_correct, NOW())"
                ),
                {
                    "id": attempt_id,
                    "user_id": request.user_id,
                    "exam_type": request.exam_type,
                    "topic": request.topic,
                    "question": request.question,
                    "user_answer": request.user_answer,
                    "correct_answer": request.correct_answer,
                    "is_correct": is_correct,
                },
            )
            await db.commit()
        except Exception:
            # DB persistence is best-effort; don't fail the response
            await db.rollback()

    return StudyAttemptResponse(
        correct=is_correct,
        explanation=explanation,
    )


@router.get("/performance/{user_id}", response_model=StudyPerformanceResponse)
async def get_performance(
    user_id: str,
    exam_type: Optional[str] = None,
    db: Annotated[AsyncSession, Depends(get_db)] = None,
) -> StudyPerformanceResponse:
    """Return study performance metrics for a user, optionally filtered by exam type."""
    if db is None:
        return StudyPerformanceResponse(user_id=user_id, exam_type=exam_type, topics=[])

    if exam_type:
        result = await db.execute(
            text(
                "SELECT topic, "
                "COUNT(*) AS total, "
                "SUM(CASE WHEN is_correct THEN 1 ELSE 0 END) AS correct "
                "FROM study_attempts "
                "WHERE user_id = :user_id AND exam_type = :exam_type "
                "GROUP BY topic"
            ),
            {"user_id": user_id, "exam_type": exam_type},
        )
    else:
        result = await db.execute(
            text(
                "SELECT topic, "
                "COUNT(*) AS total, "
                "SUM(CASE WHEN is_correct THEN 1 ELSE 0 END) AS correct "
                "FROM study_attempts "
                "WHERE user_id = :user_id "
                "GROUP BY topic"
            ),
            {"user_id": user_id},
        )

    rows = result.fetchall()

    topic_perf = [
        TopicPerformance(
            topic=row.topic,
            correct=int(row.correct or 0),
            total=int(row.total or 0),
            accuracy=float(row.correct or 0) / float(row.total) * 100.0 if row.total else 0.0,
        )
        for row in rows
    ]

    return StudyPerformanceResponse(
        user_id=user_id,
        exam_type=exam_type,
        topics=topic_perf,
    )
