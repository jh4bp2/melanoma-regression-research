# Melanoma Spontaneous Regression Research System

This project is a research tool for evidence-structured analysis of published melanoma spontaneous regression cases.

It does not provide medical advice or claim a causal mechanism for cancer regression.

흑색종 자연관해 증례를 동일한 구조로 정리하고, 반복되는 관찰·충돌하는
관찰·설명되지 않은 메커니즘을 원문 근거까지 추적하는 연구용 문헌 분석
시스템이다.

> Research use only. 이 시스템은 환자 진단, 치료 추천 또는 치료 효과 판정을
> 제공하지 않는다. **Association ≠ Causation.**

## Project Vision

이 프로젝트는 일반적인 논문 요약기가 아니라 Biological Anomaly Discovery
Engine의 첫 프로토타입이다. 20~50편의 흑색종 자연관해 문헌에서 환자별
timeline, 선행 사건, 생물학적 변화와 결과를 구조화하고, 사례 사이의 공통점과
반례를 evidence-first 방식으로 비교하는 것이 V1의 목표다.

모든 주장은 다음 provenance class 중 하나로 분리한다.

- `OBSERVED_FACT`: 논문에 직접 기술된 관찰
- `AUTHOR_INTERPRETATION`: 논문 저자가 제시한 해석
- `SYSTEM_INFERENCE`: 여러 근거를 비교해 시스템이 생성한 추론

`SYSTEM_INFERENCE`는 원문 사실처럼 저장하지 않는다. PHASE 1에서는 연결 근거
검증 기능이 아직 없으므로 `SUPPORTED` 상태로 생성하는 것을 스키마 수준에서
차단한다. 출처가 없는 주장은 Evidence가 아니라 `UNSUPPORTED` 상태로만
보존할 수 있다.

## Architecture

현재 구조는 FastAPI application/service/repository 경계를 단순하게 유지한다.
SQLAlchemy를 사용하므로 SQLite에서 PostgreSQL로 교체할 때 도메인 모델을
재작성하지 않아도 된다.

```text
Local PDF (data/papers)
        |
        v
Paper parser (PyMuPDF, page-preserving extraction)
        |
        v
Ingestion service (SHA-256 / DOI / PMID deduplication)
        |
        +--> data/processed/<sha256>.txt
        |
        v
SQLAlchemy models --> SQLite
        |
        v
FastAPI /api/v1
```

PHASE 2 extraction path:

```text
Page-preserving text
  -> section/page chunks (bounded context)
  -> metadata extraction
  -> case existence classification
  -> zero-or-more CaseCandidates
  -> normalized quote verification
  -> Case + field-level Evidence links
  -> per-case TimelineCandidates
  -> normalized quote verification
  -> Event + field-level Evidence links
  -> ExtractionRun audit
```

설계 경계:

- `app/api`: HTTP 입력, 오류 매핑, parent-child 무결성 검증
- `app/core`: 환경 설정
- `app/db`: engine, session, schema initialization
- `app/models`: 영속 모델과 제한 enum
- `app/schemas`: Pydantic 입력/출력 및 provenance validation
- `app/services`: PDF parsing과 ingestion use case
- `scripts`: 로컬 batch ingestion
- `tests`: PDF 추출, 중복 방지, path safety, evidence invariant 테스트

향후 LLM은 `app/llm`의 provider abstraction 뒤에 위치한다. 원문 파싱,
case/timeline 추출, evidence 추출, hypothesis 생성과 비판은 서로 다른
모듈과 JSON Schema로 분리한다.

## Data Model

PHASE 1은 핵심 provenance backbone만 구현한다.

- `Paper`: 서지 정보, 원본/추출 텍스트 경로, SHA-256, 페이지 수, 분석 상태
- `Case`: 논문에 포함된 환자 사례와 흑색종/자연관해 관련 필드
- `Event`: absolute date 또는 regression 기준 relative day, 날짜 정확도,
  사건 유형
- `Evidence`: claim, 원문 quote, page/section locator, provenance class,
  confidence, supporting/contradicting/neutral relation

무결성 규칙:

- `SUPPORTED` Evidence는 비어 있지 않은 `source_quote`와 `page` 또는
  `section`을 반드시 가진다.
- confidence는 0~1 범위만 허용한다.
- Evidence에 `case_id`가 있으면 해당 Case와 같은 Paper를 가리켜야 한다.
- exact/approximate Event는 absolute date 또는 relative day가 필요하다.
- PDF는 SHA-256을 우선으로, DOI/PMID를 보조로 중복 방지한다.
- 입력 경로는 `data/papers` 밖으로 이동할 수 없다.
- PDF 원본은 수정하거나 삭제하지 않는다.

생물학 변수에는 PHASE 2 schema부터 값과 별도로
`REPORTED` / `NO_CHANGE` / `NOT_REPORTED` 상태를 둔다.
`NOT_REPORTED`를 생물학적 변화가 없었다는 뜻으로 해석하지 않는다.

## PHASE 1 — Implemented

구현 내용:

- 프로젝트 디렉터리와 환경 설정
- SQLite initialization 및 SQLAlchemy 2.x models
- Paper / Case / Event / Evidence FastAPI endpoints
- PyMuPDF 기반 페이지 보존 텍스트 추출
- PDF metadata, DOI, PMID 추출
- SHA-256 / DOI / PMID 중복 방지
- directory traversal 차단
- evidence provenance를 Pydantic과 DB constraint 양쪽에서 검증
- 생성 PDF를 이용한 자동 테스트

PDF 파일의 `creationDate`는 논문의 출판 연도가 아니므로 `Paper.year`로
복사하지 않고 `raw_metadata`에만 보존한다. 서지 연도는 후속 metadata
resolver가 명시적 출처를 확인한 뒤 기록한다.

주요 생성 파일:

- `app/main.py`
- `app/models/entities.py`
- `app/schemas/records.py`
- `app/services/paper_parser.py`
- `app/services/paper_ingestion.py`
- `app/api/routes.py`
- `scripts/ingest_papers.py`
- `tests/test_ingestion.py`
- `tests/test_evidence_validation.py`

### Setup

PowerShell:

```powershell
py -3.11 -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
Copy-Item .env.example .env
```

### PDF ingestion

1. PDF를 `data/papers/`에 넣는다.
2. batch ingestion을 실행한다.

```powershell
python -m scripts.ingest_papers
```

추출 텍스트는 `data/processed/<sha256>.txt`에 `=== PAGE N ===` marker와
함께 저장된다. 텍스트 layer가 없는 스캔 PDF는 조용히 빈 문서로 처리하지
않고 명시적으로 실패한다. OCR은 후속 범위다.

PMC의 article-page PDF URL이 HTML download wrapper를 반환할 수 있으므로
parser는 `%PDF-` signature를 먼저 검사한다. PMC 연구 데이터는 가능한 경우
공식 AWS Open Data 객체(`pmc-oa-opendata`)에서 받으며 acquisition URL과
checksum은 `data/papers/manifest.json`에 기록한다.

### API

```powershell
uvicorn app.main:app --reload
```

- Swagger UI: `http://127.0.0.1:8000/docs`
- health: `GET /api/v1/health`
- papers: `GET /api/v1/papers`
- one-file ingestion: `POST /api/v1/papers/ingest`
- cases: `GET/POST /api/v1/cases`
- timeline: `GET /api/v1/cases/{case_id}/events`, `POST /api/v1/events`
- evidence: `GET/POST /api/v1/evidence`

### Tests

```powershell
pytest
```

현재 검증 결과: Python 3.14 환경에서 `6 passed`, FastAPI health endpoint
`200 OK`.

## PHASE 2 — Implemented

구현 내용:

- 공급자 독립 `LLMProvider.extract_structured()`와 OpenAI-compatible provider
- API key를 환경 변수로만 주입
- Pydantic JSON Schema validation, repair prompt, 제한된 retry
- `FakeLLMProvider` 기반 외부 호출 없는 회귀 테스트
- page/section-aware chunking과 최대 입력 길이 제한
- versioned metadata/detection/case/timeline prompt
- 0개 및 복수 Case 추출
- relative time 원문 보존과 계산 가능한 relative day 정렬값
- exact date에 ISO `YYYY-MM-DD` 검증
- Unicode NFKC, case-fold, whitespace normalization quote verification
- 검증된 Evidence만 Case/Event field에 연결
- hallucinated quote는 `UNVERIFIED` audit failure로 남기고 confirmed Evidence에서 제외
- `REPORTED`, `NOT_REPORTED`, `UNCERTAIN`, `CONFLICTING` field status
- BiologicalObservation schema/interface와 별도 `NO_CHANGE` 상태
- model/prompt/retry/error/result를 보존하는 `ExtractionRun`
- 기존 DB 행을 보존하는 nullable-column additive migration

새로운 핵심 파일:

- `app/schemas/extraction.py`
- `app/llm/base.py`
- `app/llm/provider.py`
- `app/llm/fake.py`
- `app/llm/prompts/*_v1.txt`
- `app/services/chunking.py`
- `app/services/case_extractor.py`
- `app/services/evidence_verifier.py`
- `app/services/timeline_extractor.py`
- `app/services/extraction_pipeline.py`
- `scripts/extract_cases.py`
- `tests/fixtures/melanoma_case.txt`
- `tests/fixtures/melanoma_case_expected.json`
- `tests/test_phase2_extraction.py`

### LLM configuration

`.env.example`을 `.env`로 복사한 후 secret을 로컬 환경에만 입력한다.

```dotenv
LLM_PROVIDER=openai
LLM_API_KEY=replace-locally
LLM_MODEL=your-structured-output-model
LLM_BASE_URL=https://api.openai.com/v1
LLM_MAX_RETRIES=2
LLM_TIMEOUT_SECONDS=300
```

`openai_compatible` provider name과 호환 endpoint도 사용할 수 있다. API key는
코드, audit log, model request body에 저장하지 않는다.

### End-to-end execution

```powershell
.\.venv\Scripts\Activate.ps1
python -m scripts.ingest_papers
python -m scripts.extract_cases
python -m scripts.extract_cases --paper-id 3
python -m scripts.export_audit --paper-id 3
uvicorn app.main:app --reload
```

추출 API:

- `POST /api/v1/papers/{paper_id}/extract`
- `GET /api/v1/papers/{paper_id}/extraction-status`
- `GET /api/v1/papers/{paper_id}/cases`
- `GET /api/v1/cases/{case_id}`
- `GET /api/v1/cases/{case_id}/timeline`

Case 응답은 구조화 값과 field-level Evidence를 함께 반환한다.

```json
{
  "case": {
    "id": 1,
    "paper_id": 3,
    "patient_identifier": "67-year-old man",
    "age": 67,
    "field_statuses": {
      "age": {"status": "REPORTED", "raw_value": 67},
      "melanoma_subtype": {"status": "NOT_REPORTED", "raw_value": null}
    }
  },
  "evidence": [
    {
      "field_name": "age",
      "evidence": {
        "id": 12,
        "paper_id": 3,
        "case_id": 1,
        "evidence_type": "OBSERVED_FACT",
        "claim": "case.age: 67",
        "source_quote": "A 67-year-old man...",
        "page": 2,
        "section": "Case Presentation",
        "confidence": 0.96,
        "support_type": "neutral",
        "status": "SUPPORTED"
      }
    }
  ]
}
```

Timeline의 상대 시간은 calendar date로 변환하지 않는다.

```json
{
  "event": {
    "event_type": "biopsy",
    "event_date": null,
    "relative_time": "Two weeks before regression",
    "relative_day": -14,
    "date_precision": "relative",
    "relation_to_regression": "BEFORE",
    "temporal_order_confidence": 0.95
  },
  "evidence": [
    {
      "field_name": "relative_time",
      "evidence": {
        "source_quote": "Two weeks before regression, a biopsy was performed.",
        "page": 2,
        "status": "SUPPORTED"
      }
    }
  ]
}
```

### PHASE 2 verification

```powershell
pytest
python -m app.db.init_db
```

현재 검증 결과: Python 3.14에서 `17 passed`, linter error 0,
PHASE 2 OpenAPI endpoint 5개 확인, 기존 SQLite에 additive migration 확인.

## PHASE 2.1 — Extraction Quality Hardening

- `treatment_status`를 제한 enum으로 변경하고 timed procedure와 분리
- biopsy/surgery-only 값을 `treatment_before_regression`에서 schema reject
- section 기반 강제 분류를 제거하고 claim 의미 기반 Evidence classifier 적용
- Discussion의 관찰 재서술과 speculative mechanism을 별도 분류
- ellipsis가 포함된 non-contiguous quote를 명시적으로 거절
- `ExtractionRun.reason_codes`에 partial 원인을 machine-readable하게 저장
- PHASE 2 prompt v1을 보존하고 강화 prompt를 v2로 추가
- run별 audit JSON과 old/new Markdown diff 지원

```powershell
python -m scripts.export_audit --paper-id 2 --run-id 11
python -m scripts.compare_audit_runs --paper-id 2 --old-run 7 --new-run 11
```

실제 재검증:

- Ong: run 7 → run 11, quote rejection 4 → 0
- Behnia: run 8 → run 10, quote rejection 1 → 0
- Behnia Evidence 분류: AUTHOR_INTERPRETATION 17 → 2
- 전체 테스트: `21 passed`

### Known limitations

- OCR은 아직 지원하지 않는다.
- 실제 공급자 구현은 OpenAI-compatible structured-output API 한 종류다.
- extraction endpoint는 현재 동기 실행이다.
- 긴 논문은 우선순위 section에서 최대 24,000자만 한 요청에 사용한다.
  선택 범위 밖의 사례가 있을 수 있으므로 audit status와 원문 검토가 필요하다.
- 재분석 시 Case는 paper/identifier로 갱신되며 Event는 run별로 추가된다.
- BiologicalObservation은 schema와 service interface만 있고 자동 추출은
  후속 단계다.
- quote verification은 text layer 기준이다. 표, 이미지, OCR 좌표 검증은 없다.

## Development Roadmap

### PHASE 3 — Evidence linking

- BiologicalObservation 자동 추출
- 표와 OCR source locator
- event 재분석 deduplication
- 비동기 extraction worker

### PHASE 4 — Streamlit Case Browser

- Papers, Cases, Case Detail
- Claim → Evidence → Paper → Quote drill-down
- provenance class별 일관된 시각 구분

### PHASE 5 — Case comparison

- 2개 이상 사례 정렬 비교
- partial/complete, recurrence, infection, surgery, immune-reporting cohort
- missingness를 관찰 부재와 분리

### PHASE 6 — Pattern discovery

- time-window event query
- co-occurrence 탐색
- 반례 우선 표시
- 모든 결과에 `Association ≠ Causation` 경고

### PHASE 7 — Hypothesis Generator + Critic

- Generator와 Critic을 독립 실행
- supporting / contradicting / unknown evidence 분리
- evidence 없는 가설은 confirmed 상태 금지

### PHASE 8 — Evidence Graph

- node/edge 양쪽 provenance
- edge별 source, evidence type, confidence
- 클릭 가능한 원문 quote 추적
