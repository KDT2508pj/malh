# Changelog - resume_keyword_extraction

## [2.0.0] - 2026-02-26
### Added
- root에 `meta`, `data` 구조 도입(재현성/추적성 강화)
- 각 필드에 `confidence`, `evidence_quotes` 제공 가능
- schema_version = 2

### Changed (BREAKING)
- v1의 루트 스키마(`position`, `career`, ...)에서 v2는 `data.position`, `data.career`, ...로 이동
- 파서/DB 저장 로직 수정 필요

---

## [1.1.0] - 2026-02-26
### Added
- 정규화 규칙 강화(중복 제거, 표기 통일 예시)
- 기간 표기 규칙 명시(월 단위 불명확 시 빈 값)
- Quality Checklist 섹션

### Changed
- "추측 금지"를 보다 명시적으로 강화

### Compatibility
- v1.x 스키마 호환 (schema_version: 1)

---

## [1.0.0] - 2026-02-26
### Added
- 초기 버전(JSON 스키마 및 기본 규칙)
