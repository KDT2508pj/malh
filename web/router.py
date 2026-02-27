from fastapi import APIRouter, Request
from fastapi.templating import Jinja2Templates
from pathlib import Path

# templates 폴더 경로 설정 (malh/templates)
BASE_DIR = Path(__file__).resolve().parent.parent
templates = Jinja2Templates(directory=str(BASE_DIR / "templates"))

web_router = APIRouter()

@web_router.get("/")
async def index(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})

# Auth
@web_router.get("/auth/login")
async def login(request: Request):
    return templates.TemplateResponse("auth/login.html", {"request": request, "resume_id": 1})

@web_router.get("/auth/agree")
async def agree(request: Request):
    return templates.TemplateResponse("auth/agree.html", {"request": request, "resume_id": 1})

@web_router.get("/auth/signup")
async def signup(request: Request):
    return templates.TemplateResponse("auth/signup.html", {"request": request, "resume_id": 1})

# Resume
@web_router.get("/resumes")
async def resume_list(request: Request):
    return templates.TemplateResponse("resume/list.html", {"request": request, "resume_id": 1})

@web_router.get("/resumes/wait")
async def resume_wait(request: Request):
    return templates.TemplateResponse("resume/wait.html", {"request": request, "resume_id": 1})

@web_router.get("/resumes/{resume_id}")
async def resume_detail(request: Request, resume_id: int):
    return templates.TemplateResponse("resume/detail.html", {"request": request, "resume_id": resume_id})

@web_router.get("/resumes/{resume_id}/feedback")
async def resume_feedback(request: Request, resume_id: int):
    return templates.TemplateResponse("resume/feedback.html", {"request": request, "resume_id": resume_id, "session_id": 1})

# Interview
@web_router.get("/interviews/wait")
async def interview_wait(request: Request):
    return templates.TemplateResponse("interview/wait.html", {"request": request, "resume_id": 1})

@web_router.get("/interviews/{session_id}")
async def interview_questions(request: Request, session_id: int):
    return templates.TemplateResponse("interview/questions.html", {"request": request, "session_id": session_id, "resume_id": 1})

@web_router.get("/interviews/{session_id}/questions/{question_id}")
async def interview_question_detail(request: Request, session_id: int, question_id: int):
    return templates.TemplateResponse("interview/question_detail.html", {"request": request, "session_id": session_id, "question_id": question_id, "resume_id": 1})

# Result
@web_router.get("/interviews/{session_id}/results")
async def result_index(request: Request, session_id: int):
    return templates.TemplateResponse("result/index.html", {"request": request, "session_id": session_id, "resume_id": 1, "sel_id": 1})

@web_router.get("/interviews/{session_id}/results/{sel_id}/analysis")
async def result_analysis(request: Request, session_id: int, sel_id: int):
    return templates.TemplateResponse("result/analysis.html", {"request": request, "session_id": session_id, "sel_id": sel_id, "resume_id": 1})

@web_router.get("/interviews/{session_id}/results/{sel_id}/stt")
async def result_analysis_stt(request: Request, session_id: int, sel_id: int):
    return templates.TemplateResponse("result/analysis_stt.html", {"request": request, "session_id": session_id, "sel_id": sel_id, "resume_id": 1})

@web_router.get("/interviews/{session_id}/results/{sel_id}/text")
async def result_transcript(request: Request, session_id: int, sel_id: int):
    return templates.TemplateResponse("result/transcript.html", {"request": request, "session_id": session_id, "sel_id": sel_id, "resume_id": 1})

# Weakness
@web_router.get("/interviews/{session_id}/weakness")
async def weakness_questions(request: Request, session_id: int):
    return templates.TemplateResponse("weakness/questions.html", {"request": request, "session_id": session_id, "resume_id": 1})

@web_router.get("/interviews/{session_id}/weakness/wait")
async def weakness_wait(request: Request, session_id: int):
    return templates.TemplateResponse("weakness/wait.html", {"request": request, "session_id": session_id, "resume_id": 1})

@web_router.get("/interviews/{session_id}/weakness/{question_id}")
async def weakness_detail(request: Request, session_id: int, question_id: int):
    return templates.TemplateResponse("weakness/question_detail.html", {"request": request, "session_id": session_id, "question_id": question_id, "resume_id": 1})

# Account
@web_router.get("/account/password")
async def account_password(request: Request):
    return templates.TemplateResponse("account/password.html", {"request": request, "resume_id": 1})

@web_router.get("/account/withdraw")
async def account_withdraw(request: Request):
    return templates.TemplateResponse("account/withdraw.html", {"request": request, "resume_id": 1})
