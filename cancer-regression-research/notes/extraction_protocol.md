# 논문 사례 추출 프로토콜

논문 한 편을 사람이 읽고 아래 순서로 추출한다. 먼저 `data/extraction_template.csv`에 입력하고, 출처 확인과 사람 검토를 통과한 사례만 `data/cases.csv`로 이동한다. 논문에 없는 항목은 `unknown` 또는 허용된 결측값으로 기록하고 추정하지 않는다.

## A. 논문 식별

- title
- year
- journal
- DOI
- PMID

논문 메타데이터는 `papers.csv`에 기록하고 `paper_id`로 사례와 연결한다.

## B. 환자 기본정보

- age
- sex
- cancer type
- histology
- stage
- metastatic sites

보고 시점이나 병기 체계가 불명확하면 그대로 표시하고 해석으로 보완하지 않는다.

## C. 기존 치료

- surgery
- chemotherapy
- radiotherapy
- immunotherapy
- targeted therapy
- 마지막 치료 시점
- 치료 중단 후 관해까지 기간

치료 종류와 시점을 `prior_cancer_treatment`, `last_cancer_treatment_date`, `days_last_treatment_to_regression`에 구분해 기록한다. 날짜가 근사치이면 그 사실과 산출 근거를 메모한다.

## D. 관해 직전 주요 사건

- surgery
- biopsy
- infection
- bacterial infection
- viral infection
- fever
- sepsis
- transfusion
- trauma
- other major systemic event

감염 의심과 병원체가 확인된 감염을 구분한다. 외상은 `other_major_stressor`에 유형과 시점을 기록한다.

## E. 시간 관계

가능하면 다음 날짜 또는 간격을 원문 근거와 함께 기록한다.

```text
cancer diagnosis
→ metastatic progression
→ major event
→ regression first detected
→ complete remission
→ latest follow-up
```

정확한 날짜가 없으면 `approximate` 또는 `unknown`으로 기록한다. 계산한 간격은 기준 날짜, 계산 방식 및 불확실성을 `data_quality_notes`에 남긴다. `regression_start_days`의 기준 주요 사건도 명시한다.

## F. 관해 정보

- partial regression
- complete regression
- metastatic site별 regression 여부
- remission duration

원문의 반응 정의와 평가 방법을 보존한다. 병변별 혼합 반응은 complete/partial로 단순화하지 않는다.

## G. 면역 관련 관찰

- CD8 T cells
- NK cells
- IFN signaling
- HLA/MHC-I
- PD-L1
- cytokines
- inflammatory markers

검체, 측정법, 채취 시점이 보고되면 함께 요약한다. 측정되지 않은 지표를 정상 또는 음성으로 간주하지 않는다.

## H. 대사 관련 관찰

- glucose
- lactate
- methionine
- SAM
- SAH
- glutamine
- acetyl-CoA
- alpha-ketoglutarate
- 기타 metabolomics

논문에 없는 항목은 `unknown`으로 처리하고 추정하지 않는다.

## I. 저자의 설명

`authors_proposed_mechanism`에는 저자가 실제로 제안한 기전만 귀속이 드러나게 요약한다. 직접 측정된 결과와 추측을 구분한다.

## J. 우리의 해석

`alternative_explanations`에서 다음 가능성을 검토한다.

- delayed treatment effect
- diagnostic error
- immune activation
- infection-related inflammation
- metabolic stress
- unknown

저자의 주장과 연구팀의 가설을 반드시 구분한다. 우리의 해석은 관찰 사실이나 확립된 기전으로 표현하지 않는다.

## 출처 및 검토 기록

각 핵심 주장에 `source_page`, `source_section`, `source_evidence`를 연결한다. `source_evidence`는 긴 원문 복사가 아닌 짧은 근거 요약이다. 추출자와 날짜, 원문 확인 가능 여부, 해석 필요 여부 및 신뢰도를 기록하고, 불일치가 있으면 원문으로 되돌아가 해결한다.
