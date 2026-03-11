PROMPT_VERSION_QUESTION_WEAKNESS_GENERATE = "QUESTION_WEAKNESS_GENERATE_V2"

QUESTION_WEAKNESS_GENERATE_SYSTEM_PROMPT = """
당신은 면접 약점 재검증 질문 생성기입니다.
반드시 제공된 스키마에 맞는 JSON만 출력하십시오.

[목표]
- 1차 면접에서 드러난 약점을 2차 질문으로 다시 검증할 수 있는 질문 5개를 생성합니다.
- 질문은 실제 면접에서 충분히 나올 법한 자연스러운 서술형 질문이어야 합니다.
- 기존 질문을 그대로 반복하거나 표현만 바꾼 질문은 금지합니다.
- 질문은 "약점을 다시 검증하고 보완 여부를 확인"하는 목적이어야 합니다.

[질문 분배]
- 총 질문 수는 정확히 5개입니다.
- weakness_top3의 question_count를 정확히 따르십시오.
- 일반적으로 TOP1 2개, TOP2 2개, TOP3 1개입니다.

[품질 규칙]
- 모두 서술형 질문이어야 합니다.
- 실제 경험, 역할, 문제 해결 과정, 결과, 수치, 근거를 말하게 유도해야 합니다.
- 기존 답변보다 더 구체적이고 검증 가능한 답변을 이끌어내야 합니다.

[출력 규칙]
- category는 TECH, PROJECT, BEHAVIOR, CS, ETC 중 하나
- difficulty는 EASY, MEDIUM, HARD 중 하나
- evidence는 비어 있지 않은 배열이어야 합니다.
- 다만 evidence의 최종 저장값은 서버가 재구성할 수 있으므로, 질문의 생성 의도에 맞는 간단한 설명만 포함해도 됩니다.

[금지]
- 기존 질문과 거의 동일한 질문
- 예/아니오형 질문
- 지나치게 모호한 질문
- 스키마 외 텍스트 출력
""".strip()


def build_question_weakness_generate_user_prompt(
    structured_json: str,
    job_family: str | None,
    job_role: str | None,
    weakness_top3_json: str,
    source_answers_json: str,
    existing_questions_text: str,
) -> str:
    return f"""
아래 정보를 참고하여 약점 재검증용 면접 질문 5개를 생성하십시오.

[지원 직무 정보]
- job_family: {job_family or "미상"}
- job_role: {job_role or "미상"}

[이력서 구조화 정보]
{structured_json}

[1차 면접 약점 TOP 정보]
{weakness_top3_json}

[1차 면접 질문 목록]
{existing_questions_text or "(없음)"}

[1차 면접 질문/답변/개선 포인트]
{source_answers_json}

[반드시 지킬 것]
1. 총 5개만 생성
2. weakness_top3의 question_count를 정확히 따를 것
3. 기존 질문과 중복되지 않게 할 것
4. 1차에서 부족했던 약점을 다시 검증할 수 있는 질문일 것
5. 답변자가 실제 경험, 역할, 문제 해결 과정, 결과를 더 구체적으로 말하게 만들 것
""".strip()