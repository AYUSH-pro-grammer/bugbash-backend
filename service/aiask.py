import requests 
from google import genai



preprompt = '''
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
'''
def ask(question):
    client = genai.Client(api_key="AIzaSyBWz0c0jWKM2DdtOtgcZw1cio2mty6lsYA")

    response = client.models.generate_content(
        model="gemini-3-flash-preview",
        contents=f"{preprompt}, of topic {question}",
    )


    return (response.text)



