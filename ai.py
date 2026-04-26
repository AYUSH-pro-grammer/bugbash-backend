import os
import json
import re
from openai import OpenAI




client = OpenAI(
    base_url="https://api.groq.com/openai/v1",
    api_key="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"


)

def build_system_prompt(level: str):
    return f"""
You are a DSA tutor.

Student level: {level}

Teaching style:
- easy → simple language, step-by-step, examples
- intermediate → balanced explanation + intuition
- advanced → optimization, edge cases, complexity

Rules:
- Stay on topic
- Be clear and structured
- Do not hallucinate
- Return ONLY JSON

FORMAT:

{{
  "type": "explanation",
  "explanation": "...",
  "approach": "...",
  "code": "...",
  "complexity": "..."
}}

OR

{{
  "type": "questions",
  "content": ["Q1", "Q2", "Q3", "Q4", "Q5"]
}}
"""






def safe_json_parse(text: str):
    try:
        return json.loads(text)
    except:
        match = re.search(r"\{.*\}", text, re.DOTALL)
        if match:
            try:
                return json.loads(match.group())
            except:
                return None
    return None





def parse_response(text: str):
    data = safe_json_parse(text)

    if not data:
        return fallback_response(text)

    if data.get("type") == "questions":
        return {
            "type": "questions",
            "content": data.get("content", [])
        }

    return {
        "type": "explanation",
        "explanation": data.get("explanation", ""),
        "approach": data.get("approach", ""),
        "code": data.get("code", ""),
        "complexity": data.get("complexity", "")
    }





def fallback_response(text: str):
    return {
        "type": "explanation",
        "explanation": text,
        "approach": "",
        "code": "",
        "complexity": ""
    }


def generate_response(history: list, level: str):




    try:
        trimmed_history = history[-6:]

        messages = [
            {"role": "system", "content": build_system_prompt(level)}
        ]

        for msg in trimmed_history:
            if msg["role"] == "assistant":
                try:
                    parsed = json.loads(msg["content"])
                    messages.append({
                        "role": "assistant",
                        "content": json.dumps(parsed)
                    })



                except:
                    messages.append(msg)
            else:
                messages.append(msg)

        response = client.chat.completions.create(
            model="llama-3.1-8b-instant",
            messages=messages,
            temperature=0.2
        )

        return parse_response(response.choices[0].message.content)

    except Exception as e:
        return fallback_response(f"Error: {str(e)}")





def generate_question(topic: str, level: str):
    prompt = f"""
Generate ONE coding-style DSA question.

Topic: {topic}
Level: {level}

Rules:
- Short and clear
- Real interview-style
- No explanation
- Only question text
"""

    response = client.chat.completions.create(
        model="llama-3.1-8b-instant",
        messages=[{"role": "user", "content": prompt}],
        temperature=0.7
    )

    return response.choices[0].message.content.strip()






def generate_mcq(topic: str, level: str):
    prompt = f"""
You are a DSA tutor.

Generate ONE MCQ question.

Topic: {topic}
Level: {level}

Rules:
- 4 clear options
- only one correct answer
- realistic DSA concept

Return ONLY JSON:

{{
  "question": "...",
  "options": ["A", "B", "C", "D"],
  "answer": "one of the options exactly",
  "explanation": "why this is correct in 1-2 lines"
}}
"""

    response = client.chat.completions.create(
        model="llama-3.1-8b-instant",
        messages=[{"role": "user", "content": prompt}],
        temperature=0.7
    )

    data = safe_json_parse(response.choices[0].message.content)

    if not data:
        return {
            "question": "What is time complexity of linear search?",
            "options": ["O(1)", "O(n)", "O(log n)", "O(n^2)"],
            "answer": "O(n)",
            "explanation": "Linear search checks each element one by one."
        }

    return {
        "question": data.get("question", "Fallback question"),
        "options": data.get("options", []),
        "answer": data.get("answer", ""),
        "explanation": data.get("explanation", "")
    }







def evaluate_answer(answer: str, question: str, topic: str):
    prompt = f"""
You are a strict DSA evaluator.

Question:
{question}

User Answer:
{answer}

Evaluate:
- correctness
- clarity
- understanding

Return JSON ONLY:

{{
  "feedback": "short explanation",
  "score": number between 0-100,
  "weakness": "logic / concept / complexity / null"
}}
"""

    response = client.chat.completions.create(
        model="llama-3.1-8b-instant",
        messages=[{"role": "user", "content": prompt}],
        temperature=0
    )

    data = safe_json_parse(response.choices[0].message.content)

    if not data:
        return ("Decent attempt", 50, None)

    return (
        data.get("feedback", "Decent attempt"),
        int(data.get("score", 50)),
        data.get("weakness", None),
    )