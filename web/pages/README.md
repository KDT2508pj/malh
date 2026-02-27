1) pages(web/pages)에는 뭘 넣나?

pages는 화면을 위한 요청/응답 처리만 넣습니다.

✅ pages에 넣는 것

URL 라우팅 (GET /resumes/new, POST /resumes)

폼/파일 입력 받기 (Form, UploadFile)

로그인 여부 체크(간단)

서비스 함수 호출

템플릿 렌더링 (TemplateResponse)

리다이렉트 (RedirectResponse)

“화면용 메시지” 처리(성공/실패 안내 문구)

❌ pages에 넣지 말아야 할 것(길어지면 서비스로)

텍스트 추출 알고리즘

점수 계산(가중치, 합산, 규칙)

LLM 호출/프롬프트 처리

STT 처리

DB 쿼리 복잡한 것(반복되면 분리)

한 줄: pages = 화면 담당(입력 받고, 결과 보여주기)

2) services에는 뭘 넣나?

services는 **실제 기능 로직(일 처리)**를 넣습니다.

✅ services에 넣는 것

이력서 업로드 처리 흐름
(파일 저장 → sha256 → 텍스트 추출 → 규칙 검증 → 분석 트리거)

질문 생성/꼬리질문 생성 로직

STT 처리(음성 저장, STT 실행, transcript 저장)

음성 점수 계산(말하기 점수)

텍스트 분석 점수 계산(맥락/구체성/근거/정합성)

최종 점수 합산(음성+텍스트)

(선택) worker 작업 등록(Celery delay)

한 줄: services = 기능 담당(검증/분석/점수/생성/저장)

3) 예시로 한 번에 감 잡기 (이력서 업로드)
pages가 하는 일

/resumes/new 화면 보여줌

/resumes로 파일 업로드 받음

resume_service.upload_resume(...) 호출

성공이면 /resumes/{id}로 redirect

services가 하는 일

파일 저장

sha256 중복 체크

텍스트 추출

규칙 검증

DB 저장/상태 업데이트

(필요 시) LLM 분석 작업 트리거