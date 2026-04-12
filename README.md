# Eklavya - Agent-Based Educational Content Generator

A multi-agent pipeline that generates and reviews grade-appropriate educational content using Google's Gemini AI. A **Generator Agent** creates explanations and MCQs, a **Reviewer Agent** evaluates quality, and a one-pass refinement loop fixes any issues found.

## Architecture

```
User Input (Grade + Topic)
        |
        v
  Generator Agent  ──>  Reviewer Agent
        |                     |
        |              pass?  |
        |             /    \  |
        |           yes     no
        |            |       |
        |         Done    Feedback
        |                    |
        v                    v
  Generator Agent  ──>  Reviewer Agent  ──>  Final Output
  (with feedback)        (second pass)
```

**Generator Agent** — Produces a short explanation and 3 MCQs (4 options each) as structured JSON, tailored to the student's grade level. Uses Gemini 2.5 Flash with `temperature=0.4`.

**Reviewer Agent** — Strictly evaluates content against a checklist covering age-appropriateness, factual correctness, clarity, and topic-grade fit. Uses Gemini 2.5 Flash with `temperature=0.0`. Returns `pass` or `fail` with specific feedback.

**Pipeline** — Orchestrates Generator -> Reviewer -> optional one-pass refinement. If the draft fails review, the generator re-runs with the reviewer's feedback embedded in the prompt. The retry cap is one refinement pass.

## Tech Stack

- **LLM**: Google Gemini 2.5 Flash (via `google-genai` SDK)
- **UI**: Streamlit
- **Language**: Python

## Setup

### 1. Clone the repository

```bash
git clone <repo-url>
cd generator-reviewer-agent
```

### 2. Create a virtual environment

```bash
python -m venv .venv
source .venv/bin/activate        # Linux/macOS
.venv\Scripts\activate           # Windows
```

### 3. Install dependencies

```bash
pip install -r requirements.txt
```

### 4. Set up environment variables

```bash
cp .env.example .env
```

Open `.env` and replace `your_gemini_api_key_here` with your actual [Gemini API key](https://aistudio.google.com/apikey).

### 5. Run the app

```bash
streamlit run app.py
```

## Usage

1. Enter a **Grade** (1-12) and a **Topic** in the UI.
2. Click **Generate**.
3. The app displays the full agent pipeline output:
   - Draft content from the Generator
   - Reviewer feedback (pass/fail with specific issues)
   - Refined output (if the draft failed review)
   - Second review result (if refinement occurred)

## Example Inputs

| Grade | Topic | Expected Behavior |
|-------|-------|-------------------|
| 4 | Types of angles | Pass on first try |
| 3 | Photosynthesis | Fail -> Refine -> Pass |
| 1 | Mitochondria | Fail -> Refine -> Still Fail (topic too advanced) |
| 9 | Mitochondria | Pass on first try |
| 5 | The solar system | Pass on first try |
| 4 | The water cycle | Fail -> Refine -> Pass |

> Results are probabilistic -- the LLM may behave differently across runs.

## Project Structure

```
generator-reviewer-agent/
├── app.py             # Streamlit UI
├── generator.py       # Generator Agent (content creation)
├── reviewer.py        # Reviewer Agent (content evaluation)
├── pipeline.py        # Orchestration pipeline
├── requirements.txt   # Python dependencies
├── .env.example       # Environment variable template
├── examples.txt       # Detailed example inputs and expected behavior
└── .gitignore
```

## License

This project was built as part of an AI Developer Assessment.
