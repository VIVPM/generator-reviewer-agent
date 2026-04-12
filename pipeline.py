from generator import GeneratorAgent
from reviewer import ReviewerAgent


def run_pipeline(grade: int, topic: str) -> dict:
    """
    Runs Generator → Reviewer → (optional one-pass refinement).

    Returns a dict with all stages so the UI can display the full agent flow:
    {
      "draft": <generator output>,
      "review": <reviewer output>,
      "refined": <refined generator output> or None,
      "refined_review": <reviewer output on refined> or None
    }
    """
    generator = GeneratorAgent()
    reviewer = ReviewerAgent()

    draft = generator.run(grade, topic)
    review = reviewer.run(grade, topic, draft)

    refined = None
    refined_review = None
    if review.get("status") == "fail":
        refined = generator.run(grade, topic, feedback=review.get("feedback", []))
        refined_review = reviewer.run(grade, topic, refined)

    return {
        "draft": draft,
        "review": review,
        "refined": refined,
        "refined_review": refined_review,
    }
