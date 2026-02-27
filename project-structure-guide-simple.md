# 프로젝트 폴더 구조 한눈에 보기 (초보용)

이 문서는 팀원들이 “어느 폴더에 무엇을 넣어야 하는지” 바로 이해할 수 있도록 **아주 쉽게** 정리한 안내서입니다.  
프로젝트는 **FastAPI + (HTML 템플릿) + DB + (비동기 작업/Celery)** 형태로 구성합니다.

---

## 0) 한 줄 요약

- **web/**: 브라우저 요청을 받아서 **화면(HTML)을 보여주는 곳**
- **services/**: 기능 로직(검증/분석/점수/질문 생성 등) **일을 처리하는 곳**
- **worker/**: 오래 걸리는 작업(LLM/STT/분석)을 **백그라운드로 실행**하는 곳
- **templates/**: 화면 HTML 파일
- **static/**: CSS/JS 같은 정적 파일
- **constants/**: 문자열 하드코딩 방지(enum, 가중치)
- **utils/** : 공용 도구함수 폴더


---

## 1) 전체 흐름(그림처럼 이해하기)

사용자(브라우저)
→ **web**(요청 받기/화면 렌더링)
→ **services**(실제 기능 처리)
→ (오래 걸리면) **worker**(백그라운드 작업)

---


## 3) 폴더별로 “무슨 일을 하는지”

### app/main.py
서버 시작 파일입니다.
- FastAPI 앱 만들기
- web 라우터 붙이기
- static 폴더(정적 파일) 연결

### app/core/
“기본 설정” 폴더입니다.
- DB 연결 정보, 환경변수(.env) 읽기
- DB 세션 만들기(SessionLocal 등)

### app/web/
**화면(페이지) 담당** 폴더입니다. (요청/응답 처리)
- URL을 받고(예: `/resumes/new`)
- 서비스를 호출해서 데이터를 만들고
- templates의 HTML을 렌더링해서 보여줍니다.

#### app/web/pages/
**기능(서비스) 단위로 파이썬 파일을 나눕니다.**
- `resume_page.py` : 이력서 화면들(업로드/상세/피드백)
- `interview_page.py` : 면접 진행 화면들(질문/답변 제출)
- `result_page.py` : 결과 화면들(전사/분석 결과)

> 중요한 규칙: web/pages에는 “점수 계산, LLM 호출” 같은 복잡한 로직을 길게 쓰지 않습니다.  
> 그런 로직은 services로 보내고, web은 “서비스 호출 + 화면 출력”만 합니다.

### app/templates/
**HTML 화면 파일**이 있는 폴더입니다.
- `resume/upload.html` : 이력서 업로드 화면
- `resume/feedback.html` : 이력서 피드백 화면
- `interview/question_detail.html` : 질문/답변 화면
- `result/analysis_detail.html` : 분석 결과 화면

### app/static/
브라우저에서 쓰는 파일입니다.
- CSS(디자인)
- JS(버튼 클릭, 간단한 상태 폴링 등)
- 이미지

### app/models/
DB 테이블을 파이썬 클래스로 만든 것(ORM)입니다.
- 예: `Resume`, `Question`, `InterviewSession` 등

### app/services/
프로젝트의 “진짜 기능 로직”이 들어갑니다.
- 이력서 파일 저장/검증/텍스트 추출
- 질문 생성/필터/랜덤 5문항 선정
- STT(음성→텍스트)
- 답변 분석/점수 계산/약점 생성

### app/worker/
오래 걸리는 작업을 백그라운드로 돌리는 곳입니다.
- 예: 이력서 분석(LLM), STT, 답변 분석
- 웹 요청을 오래 잡아두지 않기 위해 사용합니다.

---

## 4) 예시 흐름 1개(이력서 업로드 → 피드백 보기)

1) 사용자가 `/resumes/new`에서 파일 업로드  
2) **web/pages/resume_page.py**가 파일을 받고, **services**를 호출  
3) services가 DB에 resume를 저장하고, worker 작업을 “예약”  
4) worker가 분석 끝내고 DB에 키워드/분류 결과 저장  
5) 사용자가 `/resumes/{id}/feedback`로 들어가면  
   - web이 services를 호출해서 결과를 가져와서  
   - `templates/resume/feedback.html`로 화면을 보여줍니다.

---

## 5) 초보 팀원용 규칙(진짜 중요)

- “화면 관련”이면 → **templates / web**
- “기능 로직”이면 → **services**
- “오래 걸리는 작업”이면 → **worker**

---

## 6) 역할 초간단 요약

- **templates/**: HTML(화면)
- **static/**: CSS/JS(디자인/동작)
- **web/**: 요청 받고 화면 보여주기
- **services/**: 기능 처리(검증/분석/점수/생성)
- **worker/**: 오래 걸리는 작업을 백그라운드로 실행



## 7) 담당 파트

resume_service.py (B)

이력서 업로드 및 분석

question_service.py (B)

세션 생성, 5문항 배정, 질문 조회

stt_service.py (A)

음성 답변 제출 처리(파일 저장, STT, 음성분석, transcript 저장)

analysis_service.py(B)

제출하기 처리(컨텍스트 분석, 음성분석 + 컨텍스트 분석 점수 평가)

feedback_service.py (C)

이력서 피드백 화면용 데이터 조립
