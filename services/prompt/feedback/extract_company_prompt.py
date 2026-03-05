PROMPT_VERSION_EXTRACT_COMPANY = "FEEDBACK_EXTRACT_COMPANY_V1"

EXTRACT_COMPANY_SYSTEM_PROMPT = """
당신은 기업의 채용 공고나 회사 소개 페이지 텍스트에서 회사의 비전, 핵심 가치, 인재상을 추출하는 분석기입니다.
반드시 제공된 스키마에 맞는 JSON만 출력하십시오.
불필요한 미사여구는 빼고, 핵심 키워드와 문장만 정제하십시오.
"""

def build_extract_company_user_prompt(crawled_text: str) -> str:
    return f"""
아래 기업 웹페이지 크롤링 텍스트를 읽고 회사의 비전, 핵심 가치, 인재상을 추출하십시오.

[목표 데이터]
- vision: 회사가 추구하는 최종 목표나 비전 (1~2문장으로 요약)
- core_values: 회사의 핵심 가치 키워드 및 짧은 설명 (문자열 리스트)
- ideal_candidates: 회사가 원하는 인재상 키워드 및 요구 태도 (문자열 리스트)
※ 텍스트에 해당 내용이 명확하지 않다면 빈 리스트([])나 빈 문자열("")로 반환하십시오.

[기업 웹페이지 크롤링 텍스트]
{crawled_text}
"""