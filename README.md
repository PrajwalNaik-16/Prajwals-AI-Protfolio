# HireMe AI

HireMe is a resume-backed candidate introduction. Recruiters can explore a simple portfolio page, choose a suggested question, or chat with an AI assistant that answers from the candidate's resume.

## Run locally

1. Install the project dependencies (the project uses `uv`).
2. Create a `.env` file in the project root with `GROQ_API_KEY=your_key`.
3. Start the FastAPI app from the project root:

   ```powershell
   .\.venv\Scripts\python.exe -m uvicorn backend.main:app --reload
   ```

4. Open http://127.0.0.1:8000 in a browser.

The resume is loaded from `backend/My_Resume.pdf`. The chat endpoint is `POST /chat` and accepts a `question` plus optional conversation `history`.

## Product direction

The first version is designed to make a recruiter stay long enough to understand the person behind the resume: a guided introduction, suggested questions, and a chat that keeps conversational context. Strong next steps include:

- Replace the generic candidate identity with a consented public name, photo, short bio, and a clear contact action.
- Add project case studies with screenshots, links, the candidate's contribution, and outcomes.
- Add a skills map that connects each skill to resume evidence and a project or role.
- Offer recruiter-friendly paths such as “Explore projects,” “Check role fit,” and “Ask about collaboration.”
- Let the candidate review the extracted resume profile before publishing, and show which resume facts support an answer.
- Add privacy controls for contact details, analytics consent, and a way to request an updated resume.
- Make the page easy to share with a custom URL and add basic accessibility and mobile polish as the profile grows.

## Current limitation

The resume is parsed each time a question is asked, which adds latency and uses an LLM call. A next backend improvement is to parse once at startup (or when the resume changes) and reuse the structured profile.
