# 데이터 사전

## 공통 입력 규칙

- 문헌에 명시되지 않은 값은 추론하지 않고 빈칸 또는 `NA`로 둔다. `unknown`은 문헌상 불명/평가 불가라고 명시됐거나 불리언 필드에서 상태가 확인되지 않을 때 사용한다.
- 불리언 필드는 `yes`, `no`, `unknown` 소문자만 허용한다.
- 날짜 간격과 기간은 0 이상의 수치로 입력한다. 달력 정보만 있으면 계산 방법과 불확실성을 `data_quality_notes`에 남긴다.
- 감염 의심과 세균 감염 확인을 구분한다. `infection_before_regression=yes`라도 병원체가 확인되지 않으면 `bacterial_infection`을 추정하지 않는다.
- 자연관해와 치료반응을 혼동하지 않도록 `prior_cancer_treatment`와 `treatment_stopped_before_regression`을 반드시 확인한다. 정보가 없으면 각각 빈칸과 `unknown`으로 둔다.
- `regression_start_days`는 분석에서 선택한 주요 사건 이후 암 감소가 처음 확인되기까지의 기간이다. 주요 사건이 여러 개면 기준 사건과 선택 근거를 `data_quality_notes`에 기록한다.
- 목록형 값은 세미콜론(`;`)으로 구분하고, 원문의 불확실성은 보존한다.

## `data/cases.csv`

| 컬럼 | 의미와 입력 규칙 |
|---|---|
| `case_id` | 사례 고유 ID. 필수이며 중복 불가. 직접식별정보를 포함하지 않는다. |
| `paper_id` | `papers.csv`의 논문 ID. 필수. |
| `publication_year` | 출판 연도(정수). |
| `patient_age` | 보고 시점의 나이(년). 기준 시점이 다르면 메모. |
| `patient_sex` | 원문에 보고된 성별/sex. 미보고 시 비워 둔다. |
| `cancer_type` | 원발 암종. 필수. |
| `histology` | 병리 조직형. |
| `stage` | 원문에 보고된 병기 체계와 값. |
| `metastatic_sites` | 확인된 전이 부위; 세미콜론 구분. |
| `prior_cancer_treatment` | 관해 전 모든 암 치료와 시점. 없음은 `none`, 미상은 빈칸/`NA`. |
| `treatment_stopped_before_regression` | 관해 확인 전 치료 중단 여부: `yes/no/unknown`. |
| `surgery_before_regression` | 관해 전 수술 여부: `yes/no/unknown`. |
| `surgery_type` | 수술명·부위·목적. 수술이 `no`이면 비워 둔다. |
| `days_surgery_to_regression` | 수술일부터 암 감소 최초 확인일까지의 일수(0 이상). |
| `infection_before_regression` | 관해 전 감염 보고 여부: `yes/no/unknown`. 의심만 있어도 원문 수준을 `infection_type`에 명시. |
| `infection_type` | 감염 부위, 임상 진단, 병원체 및 확인법. 감염이 `no`이면 비워 둔다. |
| `bacterial_infection` | 세균 감염 확인 여부: `yes/no/unknown`. 단순 가능성을 `yes`로 입력하지 않는다. |
| `sepsis` | 원문에서 패혈증으로 진단/기술됐는지: `yes/no/unknown`. |
| `fever` | 발열 보고 여부: `yes/no/unknown`. |
| `max_temperature_c` | 최고 체온(섭씨). 원문 수치만 입력. |
| `days_infection_to_regression` | 감염 시작/진단일부터 암 감소 최초 확인일까지의 일수(0 이상); 기준을 메모. |
| `biopsy_or_tissue_injury` | 관해 전 생검 또는 유의한 조직손상: `yes/no/unknown`. |
| `blood_transfusion` | 관해 전 수혈: `yes/no/unknown`. |
| `other_major_stressor` | 수술·감염 외 중대한 생물학적 사건과 시점. |
| `regression_type` | `complete`, `partial`, `mixed`, `stable`, `unclear` 중 해당 기술. 원문 정의를 메모. |
| `complete_remission` | 완전관해 여부: `yes/no/unknown`. `yes`이면 `regression_type=complete`. |
| `regression_start_days` | 선택한 주요 사건부터 암 감소 최초 확인일까지의 일수(0 이상). |
| `remission_duration_months` | 보고된 관해 지속 또는 무진행 추적 기간(개월, 0 이상). |
| `immune_findings` | 면역 관련 직접 측정 결과의 요약. |
| `cd8_tcell_findings` | CD8 T세포 수, 위치, 활성 또는 클론성 결과. |
| `nk_cell_findings` | NK 세포 수 또는 활성 결과. |
| `ifn_gamma_findings` | IFN-γ 농도/발현/시그니처 결과. |
| `mhc1_findings` | MHC class I 발현 또는 항원제시 결과. |
| `pd_l1_findings` | PD-L1 측정법, 값, 시점. |
| `metabolic_findings` | 일반 대사 관련 직접 측정 결과. |
| `methionine_findings` | methionine 측정 결과. |
| `sam_findings` | S-adenosylmethionine(SAM) 결과. |
| `sah_findings` | S-adenosylhomocysteine(SAH) 결과. |
| `lactate_findings` | lactate 결과와 검체/시점. |
| `glucose_findings` | glucose 결과와 검체/시점. |
| `glutamine_findings` | glutamine 결과와 검체/시점. |
| `alpha_ketoglutarate_findings` | alpha-ketoglutarate 결과. |
| `acetyl_coa_findings` | acetyl-CoA 결과. |
| `authors_proposed_mechanism` | 논문 저자가 제안한 기전. 데이터와 구분해 귀속한다. |
| `alternative_explanations` | 지연 치료효과, 오진 등 가능한 대안 설명. |
| `evidence_strength` | 사전 정의한 등급(권장: `low/moderate/high/unclear`)과 근거. 사례보고 자체의 한계를 반영. |
| `source_quote_or_note` | 짧은 직접 인용 또는 근거 요약과 페이지/표/그림 위치. |
| `data_quality_notes` | 결측, 모호성, 시점 계산, 진단 확인 및 추출자 판단 기록. |

## `data/papers.csv`

| 컬럼 | 의미와 입력 규칙 |
|---|---|
| `paper_id` | 논문 고유 ID. 필수이며 `cases.csv`와 연결. |
| `title` | 논문 제목. |
| `authors` | 저자 목록; 일관된 형식 사용. |
| `year` | 출판 연도(정수). |
| `journal` | 학술지명. |
| `doi` | DOI(가능하면 `10.`으로 시작하는 정규화된 값). |
| `pmid` | PubMed ID. |
| `url` | 공개 원문 또는 서지 레코드 URL. |
| `cancer_type` | 논문이 다루는 암종; 복수면 세미콜론 구분. |
| `case_report_or_review` | 문헌 유형(예: `case_report`, `case_series`, `review`). |
| `number_of_cases` | 논문에 포함된 관련 사례 수(0 이상의 정수). |
| `notes` | 포함 기준, 중복 보고, 접근성 및 기타 메모. |

## 2단계 추가 필드

| 컬럼 | 의미와 입력 규칙 |
|---|---|
| `last_cancer_treatment_date` | 마지막 암 치료일. 정확하지 않으면 `approximate`임을 품질 메모에 남기며 날짜를 추정하지 않는다. |
| `days_last_treatment_to_regression` | 마지막 치료일부터 관해 최초 확인일까지의 일수(0 이상). 계산 근거를 기록한다. |
| `viral_infection` | 바이러스 감염 확인 여부: `yes/no/unknown`. 임상적 의심만으로 `yes`를 입력하지 않는다. |
| `source_page` | 핵심 사례 정보가 위치한 페이지. 페이지 체계를 명시한다. |
| `source_section` | 근거가 위치한 절, 표 또는 그림. |
| `source_evidence` | 긴 원문 복사가 아닌 짧은 근거 요약. 관찰과 해석을 구분한다. |
| `extraction_confidence` | 검토 완료 사례의 추출 신뢰도: `high`, `medium`, `low`. |
| `reviewer` | 중간 추출을 수행한 검토자 코드 또는 이름. |
| `extraction_date` | 추출일(권장 형식 `YYYY-MM-DD`). |
| `exact_text_available` | 원문 직접 확인 가능 여부: `yes/no/unknown`. |
| `interpretation_required` | 해석 또는 계산 필요 여부: `yes/no/unknown`. |
| `confidence_level` | 중간 추출 레코드의 신뢰도: `high`, `medium`, `low`. 검토 후 `extraction_confidence`로 확정한다. |

`data/extraction_template.csv`는 검토 메타데이터를 포함하는 중간 작업 파일이다. 출처 확인과 사람 검토를 거친 행만 `cases.csv`로 이동한다.
