import os
from pathlib import Path
import streamlit as st
from dotenv import load_dotenv

load_dotenv(dotenv_path=Path(__file__).resolve().parent / ".env")

st.set_page_config(page_title="Eklavya AI Content Pipeline", layout="centered")
st.title("Eklavya — Agent-Based Content Generator")
st.caption("Generator Agent → Reviewer Agent → (one-pass refinement if needed)")

if not os.getenv("GEMINI_API_KEY"):
    st.error(
        "GEMINI_API_KEY is not set. Create a `.env` file in the project root "
        "with `GEMINI_API_KEY=<your_key>` and restart the app."
    )
    st.stop()

from pipeline import run_pipeline

with st.container():
    st.header("Inputs")
    grade = st.number_input("Grade", min_value=1, max_value=12, value=4, step=1)
    topic = st.text_input("Topic", value="Types of angles")
    run = st.button("Generate", type="primary", use_container_width=True)


def render_content(content: dict):
    st.markdown("**Explanation**")
    st.write(content.get("explanation", ""))
    st.markdown("**MCQs**")
    for i, mcq in enumerate(content.get("mcqs", []), start=1):
        with st.container(border=True):
            st.markdown(f"**Q{i}. {mcq.get('question','')}**")
            for opt in mcq.get("options", []):
                st.write(f"- {opt}")
            st.success(f"Answer: {mcq.get('answer','')}")


if run:
    if not topic.strip():
        st.error("Please enter a topic.")
        st.stop()

    with st.spinner("Running agent pipeline..."):
        try:
            result = run_pipeline(int(grade), topic.strip())
        except Exception as e:
            st.error(f"Pipeline failed: {e}")
            st.stop()

    draft = result["draft"]
    review = result["review"]
    refined = result["refined"]
    refined_review = result["refined_review"]

    st.subheader("1. Generator Output (Draft)")
    render_content(draft)
    with st.expander("Raw JSON"):
        st.json(draft)

    st.subheader("2. Reviewer Feedback")
    status = review.get("status", "unknown")
    if status == "pass":
        st.success("Status: PASS — no issues found.")
    else:
        st.error("Status: FAIL")
        for item in review.get("feedback", []):
            st.write(f"- {item}")
    with st.expander("Raw JSON"):
        st.json(review)

    st.subheader("3. Refined Output")
    if refined is None:
        st.info("No refinement needed — draft passed review.")
    else:
        st.write("Generator was re-run once with reviewer feedback embedded.")
        render_content(refined)
        with st.expander("Raw JSON"):
            st.json(refined)

        st.subheader("4. Review of Refined Output")
        r_status = refined_review.get("status", "unknown")
        if r_status == "pass":
            st.success("Status: PASS — refinement fixed all issues.")
        else:
            st.error("Status: FAIL — issues remain after refinement (retry cap reached).")
            for item in refined_review.get("feedback", []):
                st.write(f"- {item}")
        with st.expander("Raw JSON"):
            st.json(refined_review)
else:
    st.info("Enter a grade and topic in the sidebar, then click **Generate**.")
