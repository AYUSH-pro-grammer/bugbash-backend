
from fastapi import APIRouter
from pydantic import BaseModel
from fastapi.middleware.cors import CORSMiddleware
import uuid
import json

from ai import generate_response, generate_question, evaluate_answer, generate_mcq



sessions = {}


router = APIRouter(prefix="/meet", tags=["meet"])

class ChatRequest(BaseModel):
    message: str




@router.post("/create-session")
def create_session():
    session_id = str(uuid.uuid4())

    sessions[session_id] = {
        "messages": [],
        "topic": None,
        "level": None,
        "stage": "topic",

        "assessment_index": 0,
        "mcq_index": 0,
        "score": 0,
        "weakness": [],

        "current_question": None,
        "current_mcq": None,

        "final_quiz": False,
        "final_mcq_index": 0,
        "final_coding_index": 0,
        "final_score": 0,
    }

    return {
        "session_id": session_id,
        "initial_message": {
            "type": "explanation",
            "explanation": "Hi, I am your DSA tutor. What topic would you like to study?",
            "options": ["Arrays", "Linked List", "Trees", "Graphs"]
        }
    }


@router.post("/chat/{session_id}")
def chat(session_id: str, req: ChatRequest):
    if session_id not in sessions:
        return {"error": "Invalid session"}

    message = req.message.strip()
    session = sessions[session_id]

    if session["stage"] == "learning":
        if message.lower().strip() in ["end session", "finish session"]:
            session["stage"] = "end_prompt"

            return {
                "type": "explanation",
                "explanation": "Do you want to take a final quiz?",
                "options": ["Yes", "No"]
            }

    if session["stage"] == "topic":
        session["topic"] = message
        session["stage"] = "level"

        return {
            "type": "explanation",
            "explanation": f"Great choice. What is your level in {message}?",
            "options": ["Easy", "Intermediate", "Advanced"]
        }

    if session["stage"] == "level":
        session["level"] = message.lower()
        session["stage"] = "assessment"

        session["assessment_index"] = 0
        session["mcq_index"] = 0
        session["score"] = 0
        session["weakness"] = []

        coding_q = generate_question(session["topic"], session["level"])
        session["current_question"] = coding_q

        return {
            "type": "explanation",
            "explanation": f"Coding Question:\n{coding_q}",
            "playground": True
        }

    if session["stage"] == "assessment":

        if session["assessment_index"] == 0:
            feedback, score, weak = evaluate_answer(
                message,
                session["current_question"],
                session["topic"]
            )

            session["score"] += score
            session["assessment_index"] = 1

            if weak:
                session["weakness"].append(weak)

            mcq = generate_mcq(session["topic"], session["level"])
            session["current_mcq"] = mcq

            return {
                "type": "explanation",
                "feedback": feedback,
                "score": score,
                "explanation": mcq["question"],
                "options": mcq["options"],
                "correct_answer": mcq["answer"]
            }

        correct = session["current_mcq"]["answer"]
        explanation = session["current_mcq"].get("explanation", "")

        if message == "timeout":
            score = 0
            feedback = f"⏰ Time's up! Correct answer: {correct}. {explanation}"
        else:
            is_correct = message.strip().lower() == correct.strip().lower()
            score = 20 if is_correct else 0

            if is_correct:
                feedback = f"Correct ✅ {explanation}"
            else:
                feedback = f"Wrong ❌ Correct: {correct}. {explanation}"

        session["score"] += score
        session["mcq_index"] += 1

        if score == 0:
            session["weakness"].append("concept")

        if session["mcq_index"] < 5:
            mcq = generate_mcq(session["topic"], session["level"])
            session["current_mcq"] = mcq

            return {
                "type": "explanation",
                "feedback": feedback,
                "score": score,
                "explanation": mcq["question"],
                "options": mcq["options"],
                "correct_answer": mcq["answer"]
            }

        avg = session["score"] // 6
        session["stage"] = "learning"

        weak_text = (
            f"\nWeak areas: {', '.join(set(session['weakness']))}"
            if session["weakness"] else ""
        )

        return {
            "type": "explanation",
            "explanation": f"Assessment complete!\nScore: {avg}/100.\n{weak_text}\n\nYou can continue learning.\nType 'end session' anytime to take final quiz."
        }

    if session["stage"] == "end_prompt":

        if message.lower() == "yes":
            session["stage"] = "final_mcq"
            session["final_mcq_index"] = 0
            session["final_score"] = 0

            mcq = generate_mcq(session["topic"], session["level"])
            session["current_mcq"] = mcq

            return {
                "type": "explanation",
                "explanation": "Final Quiz (MCQ 1/7): " + mcq["question"],
                "options": mcq["options"],
                "correct_answer": mcq["answer"]
            }

        else:
            session["stage"] = "summary_prompt"
            return {
                "type": "explanation",
                "explanation": "Do you want a summary of this session?",
                "options": ["Yes", "No"]
            }

    if session["stage"] == "final_mcq":

        correct = session["current_mcq"]["answer"]
        explanation = session["current_mcq"].get("explanation", "")

        is_correct = message.strip().lower() == correct.strip().lower()
        score = 10 if is_correct else 0

        feedback = f"Correct ✅ {explanation}" if is_correct else f"Wrong ❌ Correct: {correct}. {explanation}"

        session["final_score"] += score
        session["final_mcq_index"] += 1

        if session["final_mcq_index"] < 7:
            mcq = generate_mcq(session["topic"], session["level"])
            session["current_mcq"] = mcq

            return {
                "type": "explanation",
                "feedback": feedback,
                "score": score,
                "explanation": f"MCQ {session['final_mcq_index']+1}/7: {mcq['question']}",
                "options": mcq["options"],
                "correct_answer": mcq["answer"]
            }

        session["stage"] = "final_coding"
        session["final_coding_index"] = 0

        coding_q = generate_question(session["topic"], session["level"])
        session["current_question"] = coding_q

        return {
            "type": "explanation",
            "feedback": feedback,
            "explanation": f"Now coding section (1/3):\n{coding_q}",
            "playground": True
        }

    if session["stage"] == "final_coding":

        feedback, score, _ = evaluate_answer(
            message,
            session["current_question"],
            session["topic"]
        )

        session["final_score"] += score // 10
        session["final_coding_index"] += 1

        if session["final_coding_index"] < 3:
            coding_q = generate_question(session["topic"], session["level"])
            session["current_question"] = coding_q

            return {
                "type": "explanation",
                "feedback": feedback,
                "explanation": f"Next coding ({session['final_coding_index']+1}/3):\n{coding_q}",
                "playground": True
            }

        session["stage"] = "summary_prompt"

        return {
            "type": "explanation",
            "explanation": f"Final Quiz Complete! Score: {session['final_score']}/100.\nDo you want a summary?",
            "options": ["Yes", "No"]
        }

    if session["stage"] == "summary_prompt":

        if message.lower() == "yes":
            return {
                "type": "explanation",
                "explanation": f"""
Summary:

Topic: {session['topic']}
Level: {session['level']}

Weak Areas: {', '.join(set(session['weakness'])) if session['weakness'] else 'None'}

You completed learning + assessment + final quiz.
Great progress 🚀
"""
            }

        return {
            "type": "explanation",
            "explanation": "Session completed successfully 🚀"
        }

    session["messages"].append({
        "role": "user",
        "content": message
    })

    try:
        response = generate_response(
            session["messages"],
            session["level"]
        )
    except Exception as e:
        return {"error": str(e)}

    session["messages"].append({
        "role": "assistant",
        "content": json.dumps(response)
    })

    return response




from groq import Groq
import os

client = Groq(api_key="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")



@router.post("/analyze-code")
def analyze_code(data: dict):

    code = data.get("code", "")
    question_id = data.get("question_id")

    prompt = f"""


You are a smart DSA tutor.

Analyze the student's code and give helpful guidance.

Rules:
- DO NOT give full solution
- DO NOT write final code
- Give 2-4 hints max
- Detect:
    • brute force
    • wrong logic
    • missing edge cases
    • inefficiency
- Keep hints short and actionable

Student code:
{code}
"""

    try:
        response = client.chat.completions.create(
            model="mixtral-8x7b-32768",  # ✅ FIXED
            messages=[{"role": "user", "content": prompt}],
        )

        text = response.choices[0].message.content

        hints = [
            line.strip("-• ")
            for line in text.split("\n")
            if line.strip()
        ]

        return {"hints": hints[:4]}

    except Exception as e:
        return {"hints": [f"Error: {str(e)}"]}
    

@router.post("/analyze-lines")

def analyze_lines(data: dict):
    code = data.get("code", "")

    prompt = f"""
Analyze the following code.

Return ONLY valid JSON array like:
[
  {{"line": 3, "issue": "wrong condition"}},
  {{"line": 7, "issue": "inefficient loop"}}
]

Code:
{code}
"""

    try:
        response = client.chat.completions.create(
    model="mixtral-8x7b-32768",  # ✅ FIXED
    messages=[{"role": "user", "content": prompt}],
)

        raw = response.choices[0].message.content.strip()

        return json.loads(raw)

    except Exception as e:
        return []