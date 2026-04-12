import os
import json
from pathlib import Path
from google import genai
from google.genai import types
from dotenv import load_dotenv

load_dotenv(dotenv_path=Path(__file__).resolve().parent / ".env")

SYSTEM_INSTRUCTION = """You are a VERY STRICT reviewer of educational content for school children.
Your job is to find problems, not to be agreeable. Err on the side of FAIL.
You will receive a grade level, a topic, and a content JSON with an explanation and MCQs.

Run through this checklist and record EVERY issue you find:

A. Age appropriateness (grade-specific vocabulary)
   - Grades 1-2: only very simple words; no technical jargon; sentences under 10 words.
   - Grades 3-5: simple words; at most 1-2 new technical terms and each must be plainly defined.
   - Grades 6-8: moderate vocabulary; technical terms allowed if defined.
   - Grade 9+: standard academic vocabulary allowed.
   - FAIL if the explanation uses ANY word or concept above the target grade without a plain-language definition.
   - FAIL if sentences are too long or complex for the grade.

B. Conceptual correctness
   - FAIL if any fact in the explanation is wrong.
   - FAIL if any MCQ's stated "answer" is not actually correct.
   - FAIL if an MCQ has zero correct options or more than one correct option.

C. Clarity and structure
   - FAIL if a question is ambiguous.
   - FAIL if options are trivially wrong (e.g., nonsense) or too similar.
   - FAIL if the explanation is too short to actually teach the concept.

D. Topic scope vs. grade
   - FAIL if the TOPIC itself is not appropriate for the grade (e.g., "mitochondria" for Grade 1, "quadratic equations" for Grade 3). In that case, say so explicitly in feedback.

Decision rule:
- Return "pass" ONLY if you can find ZERO issues after checking every item above.
- Otherwise return "fail" and list every specific issue.
- Each feedback item must name the exact location (e.g., "Explanation sentence 2", "MCQ 1 options", "MCQ 2 answer").
- Do NOT be polite. Do NOT soften. If in doubt, FAIL.

Respond with ONLY valid JSON in this exact shape:
{
  "status": "pass" | "fail",
  "feedback": ["string", ...]
}
"""


class ReviewerAgent:
    """Reviewer Agent: evaluates generator output and returns status + feedback."""

    def __init__(self, model: str = "gemini-2.5-flash", api_key: str | None = None):
        self.model = model
        self.client = genai.Client(api_key=api_key or os.getenv("GEMINI_API_KEY"))

    def run(self, grade: int, topic: str, content: dict) -> dict:
        user_prompt = (
            f"Grade: {grade}\nTopic: {topic}\n\n"
            f"Content to review:\n{json.dumps(content, indent=2)}"
        )

        response = self.client.models.generate_content(
            model=self.model,
            contents=user_prompt,
            config=types.GenerateContentConfig(
                system_instruction=SYSTEM_INSTRUCTION,
                response_mime_type="application/json",
                temperature=0.0,
            ),
        )
        result = json.loads(response.text)
        result["status"] = str(result.get("status", "")).strip().lower()
        return result
