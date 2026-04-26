import os
import google.generativeai as genai


preprompt = """
You are a backend content generator.

Return ONLY valid JSON. No explanations. No markdown.

Schema:
{
  "questions": [
    {
      "title": "string",
      "description": "string",
      "difficulty": "easy | medium | hard",
      "testcases": [
        {
          "input": "string",
          "output": "string"
        }
      ]
    }
  ],
  "assignment": {
    "title": "string",
    "description": "string"
  }
}

Task:
Generate 3 coding questions about arrays and hashing.

Rules:
- Each question must have at least 2 testcases
- Output must be strictly valid JSON
- Do NOT include extra text
"""


def ask(topic: str):
    try:
        # ✅ configure once per call (safe for serverless)
        genai.configure(api_key=os.getenv("GOOGLE_API_KEY"))

        model = genai.GenerativeModel("gemini-1.5-flash")

        response = model.generate_content(
            f"{preprompt}\nTopic: {topic}"
        )

        text = response.text.strip()

        # 🔥 clean possible markdown wrapping
        if text.startswith("```"):
            text = text.split("```")[1]

        return text

    except Exception as e:
        raise Exception(f"AI generation failed: {str(e)}")