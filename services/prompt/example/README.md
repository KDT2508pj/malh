# resume_keyword_extraction Prompt Pack

이 폴더는 **이력서 텍스트(resume_text)** 를 입력으로 받아, 면접 서비스 파이프라인에서 사용할 **구조화 JSON** 을 생성하기 위한 프롬프트 버전들을 보관한다.

- **Prompt ID**: `resume_keyword_extraction`
- **버전 규칙**: SemVer (`vMAJOR.MINOR.PATCH.md`)
- **권장 운영 원칙**
  1. 런타임/DB에 `prompt_id`, `prompt_version`을 반드시 기록하여 결과 재현성을 확보한다.
  2. 배포 시점에 사용할 버전을 명시적으로 고정한다(“latest” 자동 추종 금지).
  3. 변경 내용은 `CHANGELOG.md`에 반드시 남긴다.

## 폴더 구조

```
resume_keyword_extraction/
  README.md
  v1.0.0.md
  v1.1.0.md
  v2.0.0.md
  CHANGELOG.md
```

## 버전 선택 가이드

- `v1.x` : 기존 파서/DB가 **root 스키마를 그대로** 기대하는 경우(호환 유지).
- `v2.0.0` : 스키마가 변경되므로(예: `meta`, `data` 루트 도입) **파서/저장 로직 업데이트가 필요**하다.

## SemVer 기준(팀 합의용)

- **MAJOR**: 출력 JSON의 구조/필수 필드/타입이 바뀌어 파서 또는 DB 저장이 깨질 수 있는 변경
- **MINOR**: 기존 구조는 유지하면서 “필드 추가” 등 하위 호환 가능한 변경
- **PATCH**: 문구 튜닝/규칙 보강 등 출력 스키마에 영향을 주지 않는 변경

## 런타임 통합(예시)

- 모델 호출 시 프롬프트 파일을 읽어 시스템/유저 메시지로 구성한다.
- 결과 저장 시 다음을 함께 저장한다.

```
prompt_id = "resume_keyword_extraction"
prompt_version = "1.1.0"  # 예: 선택한 버전
```

> 주의: 이 폴더의 프롬프트들은 **JSON만 출력**하도록 강제한다. 모델이 마크다운/설명을 섞어 내보내면 파서에서 실패하도록 설계하는 것을 권장한다.

추신)이 문서에 맞춰서 작성안하셔도 됩니다
나중에 발표나 면접시 ~버전 관리를 했습니다 증거 남기는 용도입니다
본인이 필요하다 생각하시면 작성하시면 됩니다
