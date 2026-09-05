# 전이성 암 자연관해 사례 탐색 연구

## 연구 목적

공개 문헌의 전이성 암 자연관해 사례를 구조화하고, 관해 전 수술·감염·고열·패혈증·조직손상 같은 사건과 관해 사이의 패턴을 탐색한다. 현재 파일럿 단계의 목적은 실제 논문 5건을 사람이 추출해 보며 스키마가 현실적인지 평가하는 것이다. 치료법, 효과 또는 인과관계를 주장하지 않는다.

## 프로젝트 구조

```text
cancer-regression-research/
├─ data/
│  ├─ cases.csv                 # 검토가 끝난 사례
│  ├─ papers.csv                # 논문 메타데이터
│  └─ extraction_template.csv   # 검토 전 중간 추출
├─ notes/                       # 기준, 프로토콜, 가설, 사전, 기전, 반례
├─ scripts/                     # 검증, 완전성 보고, 탐색 분석, 타임라인
├─ outputs/figures/
├─ requirements.txt
└─ README.md
```

## 데이터 입력 원칙

- 공개 원문에서 확인한 사실만 입력하며, 없는 정보는 빈칸, `NA` 또는 `unknown`으로 둔다.
- 불리언 값은 `yes`, `no`, `unknown` 소문자로 통일한다.
- 감염 의심과 확인된 세균·바이러스 감염을 구분한다.
- 이전 치료와 마지막 치료 시점을 기록해 자연관해와 치료의 지연 반응을 구분할 수 있게 한다.
- `regression_start_days`는 기록된 주요 사건 이후 암 감소가 최초 확인되기까지의 기간이다.
- 각 핵심 주장에 페이지·절·짧은 근거 요약을 연결한다. 긴 논문 원문은 CSV에 복사하지 않는다.
- 저자의 설명, 직접 관찰 및 연구팀의 대안 해석을 구분한다.

CSV 파일에는 실제 또는 가상 환자 행이 미리 포함되어 있지 않다. 자세한 규칙은 `notes/data_dictionary.md`, 선별은 `notes/inclusion_criteria.md`, 추출은 `notes/extraction_protocol.md`를 따른다.

## 파일럿 workflow

```text
논문 발견
→ inclusion/exclusion 평가
→ extraction_template.csv 입력
→ 출처/페이지 확인
→ validate_data.py
→ 사람이 검토
→ cases.csv 이동
→ pilot_report.py
→ 스키마 수정
→ 본격적인 사례 수집
```

`extraction_template.csv`의 행은 자동으로 확정 사례가 되지 않는다. 검증 오류는 수정해야 하며 warning은 입력을 차단하지 않지만 원문 확인 또는 결측 사유 기록이 필요하다. 검토가 끝난 사례만 `cases.csv`로 이동한다.

## 설치 및 실행

Python 3.9 이상을 권장한다.

```bash
python -m pip install -r requirements.txt
python scripts/validate_data.py
python scripts/pilot_report.py
python scripts/analyze_cases.py
python scripts/timeline_analysis.py
```

다른 CSV는 첫 번째 위치 인자로 지정할 수 있다.

```bash
python scripts/validate_data.py data/cases.csv
python scripts/pilot_report.py data/cases.csv
python scripts/analyze_cases.py data/cases.csv
python scripts/timeline_analysis.py data/cases.csv --output-dir outputs/figures
```

헤더만 있는 빈 데이터에서도 모든 스크립트는 오류 없이 종료한다.

## 현재 단계의 한계와 주의

사례보고는 표본이 작고 선택·출판·보고 편향이 크며 사건 시점과 바이오마커가 불완전하다. 진단 오류, 치료의 지연 효과, 동시 중재와 시간 의존 교란을 배제하기 어렵다. 파일럿 보고서는 스키마 적합성과 추출 완전성만 평가하며 관해 원인이나 통계적 결론을 제시하지 않는다. 이 프로젝트는 임상 치료 권고가 아니다.

## 확장 방향

파일럿 후 스키마를 고정하고 공개 문헌의 사례와 반례를 체계적으로 수집할 수 있다. 이후 사전 정의한 가설을 TCGA 종양 분자자료 또는 GEO 감염·면역·종양 전사체 자료에서 별도로 검토할 수 있다. 사례 수준 관찰과 집단 오믹스 분석은 서로 다른 근거 층위로 유지한다.
