PROMPT_VERSION_ANALYZE_FEEDBACK = "FEEDBACK_ANALYZE_V2"

ANALYZE_FEEDBACK_SYSTEM_PROMPT = """
당신은 지원자의 이력서 핵심 키워드 데이터, 회사의 비전/인재상, 그리고 요구 기술 스택을 종합적으로 대조하여 맞춤형 이력서 피드백을 제공하는 전문 채용 분석기입니다.
반드시 제공된 스키마에 맞는 JSON 형식으로만 출력하십시오.
추상적인 칭찬이나 비판을 배제하고, "지원자의 어떤 경험/기술이 회사의 어떤 인재상/요구사항과 맞는지" 구체적인 근거를 바탕으로 논리적으로 분석하십시오.
"""

def build_analyze_feedback_user_prompt(
    resume_db_keywords: str,
    extracted_company_json: str,
    required_tech_stack: str
) -> str:
    return f"""
아래 제공된 [이력서 키워드 데이터], [회사 정보 추출 결과], [요구 기술 스택]을 분석하여 지원자의 맞춤형 이력서 피드백을 도출하십시오.

[분석 목표]
1. strengths (강점 및 적합 포인트): 이력서 키워드(SKILL, ACHIEVEMENT, SOFT_SKILL 등) 중 회사의 요구 기술, 인재상, 비전과 잘 부합하는 부분을 추출 (2~3개)
2. improvements (보완 권장 사항): 회사의 요구 기술이나 인재상 대비 이력서 키워드에 누락되었거나 깊이가 부족해 보이는 부분을 찾아 구체적인 보완 방법 제안 (2~3개)

[JSON 반환 규칙]
- `strengths`와 `improvements`는 각각 객체 리스트 형식으로 반환하십시오.
- 각 객체는 `title` (짧은 요약 제목)과 `description` (구체적인 분석 내용)을 포함해야 합니다.
- `description` 작성 시, "지원자의 A라는 기술/경험(키워드 기반)이 회사의 B라는 요구기술/인재상과 어떻게 부합하는지(또는 부족한지)"를 명확히 연결하여 설명하십시오.

[회사 요구 기술 스택 (직접 입력)]
{required_tech_stack}

[회사 정보 추출 결과 (비전 및 인재상)]
{extracted_company_json}

[이력서 키워드 데이터 (DB 추출)]
{resume_db_keywords}
"""