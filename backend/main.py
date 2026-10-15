from fastapi import FastAPI, HTTPException
from fastapi.responses import FileResponse
from pathlib import Path
from pypdf import PdfReader
import os
import json
from fastapi.staticfiles import StaticFiles
from dotenv import load_dotenv
from groq import Groq
from pydantic import BaseModel, Field

load_dotenv()
my_api_key=os.getenv("GROQ_API_KEY")

if not my_api_key:
    raise ValueError("API key kaha hai bhai")

client=Groq(api_key=my_api_key)
model = "openai/gpt-oss-120b"

app= FastAPI(title="HireMe AI")
WEB_DIR = Path(__file__).parent / "web"
RESUME_PATH = Path(__file__).parent / "My_Resume.pdf"
app.mount("/static", StaticFiles(directory=WEB_DIR), name="static")

#parse resume
class Experience(BaseModel):
    company: str | None = None
    role: str | None = None
    duration: str | None = None
    description: str | None = None
    skills_used: list[str] = Field(default_factory=list)

class Resume(BaseModel):
    name: str | None = None
    email: str | None = None
    phone: str | None = None

    total_experience_years: float | None = None

    skills: list[str] = Field(default_factory=list)
    experiences: list[Experience] = Field(default_factory=list)
    education: list[str] = Field(default_factory=list)
    projects: list[str] = Field(default_factory=list)
    certifications: list[str] = Field(default_factory=list)
resume_schema = Resume.model_json_schema()

class ChatTurn(BaseModel):
    role: str
    content: str

class ChatRequest(BaseModel):
    question: str
    history: list[ChatTurn] = Field(default_factory=list)

def ask_candidate(question: str, resume: Resume, history: list[ChatTurn] | None = None):

    system_prompt = f"""
You are an AI assistant representing a job candidate.

Below is everything you know about the candidate.

{resume.model_dump_json(indent=2)}

Rules:

1. Answer only using this information.

2. Never hallucinate.

3. If information is unavailable,
say

"I don't have enough information to answer that."

4. Be professional.

5. Answer as if HR is interviewing this candidate.
"""

    messages = [{"role": "system", "content": system_prompt}]
    if history:
        messages.extend(
            {"role": turn.role, "content": turn.content}
            for turn in history[-12:]
            if turn.role in {"user", "assistant"}
        )
    messages.append({"role": "user", "content": question})

    response = client.chat.completions.create(

        model=model,

        messages=messages

    )

    return response.choices[0].message.content

def parse_resume(resume_text):
    system_prompt = f"""
    You are an expert resume parser.

    Extract information from the resume based on its meaning,
    not only based on exact section headings.

    Different resumes may use different headings.

    For example:
    - Experience
    - Professional Experience
    - Work History
    - Employment
    - Internships

    These may all contain relevant experience.

    Skills may also appear in the skills section, work experience,
    internships or projects.

    Return ONLY valid JSON matching this schema:

    {resume_schema}

    Important rules:

    1. Do not invent information.
    2. If a value is not available, return null.
    3. If a list has no information, return an empty list.
    4. Include internships inside experiences.
    5. Extract skills mentioned across the entire resume.
    """
    user_prompt = f"""
    Parse the following resume:

    {resume_text}
    """
    message_system={
        "role" : "system",
        "content" : system_prompt
    }
    message_user={
        "role" : "user",
        "content" : user_prompt
    }
    messages=[message_system, message_user]
    response_format={
        "type": "json_object"
    }
    response=client.chat.completions.create(model=model, messages=messages, response_format=response_format)
    raw_output = response.choices[0].message.content
    data = json.loads(raw_output)
    resume = Resume(**data)
    return resume

#pdf extraction
def read_pdf(file_path):
    reader = PdfReader(file_path)
    text = ""
    for page in reader.pages:
        page_text = page.extract_text()
        if page_text:
            text += page_text + "\n"
    return text

@app.get("/")
def home():
    return FileResponse(WEB_DIR / "index.html")

@app.post("/chat")
def chat(request:ChatRequest):
    if not request.question.strip():
        raise HTTPException(status_code=422, detail="Please enter a question.")
    try:
        resume_text = read_pdf(RESUME_PATH)
        resume = parse_resume(resume_text)
        answer = ask_candidate(request.question, resume, request.history)
    except Exception as exc:
        raise HTTPException(status_code=500, detail="The assistant couldn't respond right now. Please try again.") from exc
    return {
        "answer" : answer
    }
