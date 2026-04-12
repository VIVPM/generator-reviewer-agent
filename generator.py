import os
import json
from pathlib import Path
from google import genai
from google.genai import types
from dotenv import load_dotenv

load_dotenv(dotenv_path=Path(__file__).resolve().parent / ".env")

SYSTEM_INSTRUCTION = """You are an educational content generator for school children.
Given a grade level and a topic, produce a short explanation and multiple-choice questions.

Rules:
- Language and vocabulary MUST match the given grade level.
- Concepts MUST be factually correct.
- Generate exactly 3 MCQs, each with exactly 4 options.
- The "answer" field must contain the exact text of the correct option (not a letter).
- Respond with ONLY valid JSON matching this schema:
{
  "explanation": "string",
  "mcqs": [
    {"question": "string", "options": ["string","string","string","string"], "answer": "string"}
  ]
}
"""


def _validate_content(content: dict) -> None:
    """Output guardrail: ensure generator JSON has the expected shape before returning."""
    if not isinstance(content, dict):
        raise ValueError("Generator output is not a JSON object.")
    explanation = content.get("explanation")
    if not isinstance(explanation, str) or not explanation.strip():
        raise ValueError("Generator output missing a non-empty 'explanation' string.")
    mcqs = content.get("mcqs")
    if not isinstance(mcqs, list) or not mcqs:
        raise ValueError("Generator output missing a non-empty 'mcqs' list.")
    for i, mcq in enumerate(mcqs, start=1):
        if not isinstance(mcq, dict):
            raise ValueError(f"MCQ {i} is not an object.")
        question = mcq.get("question")
        options = mcq.get("options")
        answer = mcq.get("answer")
        if not isinstance(question, str) or not question.strip():
            raise ValueError(f"MCQ {i} missing a non-empty 'question'.")
        if not isinstance(options, list) or len(options) != 4:
            raise ValueError(f"MCQ {i} must have exactly 4 options.")
        if not all(isinstance(o, str) and o.strip() for o in options):
            raise ValueError(f"MCQ {i} options must all be non-empty strings.")
        if not isinstance(answer, str) or answer not in options:
            raise ValueError(f"MCQ {i} 'answer' must exactly match one of the options.")


class GeneratorAgent:
    """Generator Agent: produces educational content as structured JSON."""

    def __init__(self, model: str = "gemini-2.5-flash", api_key: str | None = None):
        self.model = model
        self.client = genai.Client(api_key=api_key or os.getenv("GEMINI_API_KEY"))

    def run(self, grade: int, topic: str, feedback: list[str] | None = None) -> dict:
        user_prompt = f"Grade: {grade}\nTopic: {topic}"
        if feedback:
            bullets = "\n".join(f"- {item}" for item in feedback)
            user_prompt += (
                "\n\nA previous attempt was rejected by a reviewer for these reasons. "
                "Produce a new version that fixes every issue:\n" + bullets
            )

        response = self.client.models.generate_content(
            model=self.model,
            contents=user_prompt,
            config=types.GenerateContentConfig(
                system_instruction=SYSTEM_INSTRUCTION,
                response_mime_type="application/json",
                temperature=0.4,
            ),
        )
        content = json.loads(response.text)
        # _validate_content(content)
        return content
