# Paper 1: run 8 vs run 10

> Association does not imply causation. This report compares extraction behavior, not clinical truth.

## Summary

- `status`: "partial" → "partial"
- `case_count`: 1 → 1
- `event_count`: 10 → 10
- `evidence_count`: 41 → 40
- `quote_rejected`: 1 → 0
- `retry_count`: 1 → 0
- `prompt_version`: "paper_metadata:v1,case_detection:v1,case_extraction:v1,timeline_extraction:v1" → "paper_metadata:v2,case_detection:v2,case_extraction:v2,timeline_extraction:v2"
- `evidence_type_counts`: {"AUTHOR_INTERPRETATION": 17, "OBSERVED_FACT": 24} → {"AUTHOR_INTERPRETATION": 2, "OBSERVED_FACT": 38}
- `reason_codes`: [] → ["PARTIAL_TEMPORAL_UNCERTAINTY"]

## Changed fields

### `case[1].follow_up_duration`
- Old value: "19 months that followed after initial diagnosis"
- New value: "19 months that followed after initial diagnosis"
- Old field status: "REPORTED"
- New field status: "REPORTED"
- Old evidence type: ["AUTHOR_INTERPRETATION"]
- New evidence type: ["OBSERVED_FACT"]
- Old quote verification: `VERIFIED`
- New quote verification: `VERIFIED`
- Reason: evidence type changed.

### `case[1].metastatic_sites`
- Old value: ["left lower lobe pulmonary nodule", "bilateral upper lung cavitary lesions", "left hilar nodal spread", "lung", "brain", "spinal cord"]
- New value: ["lungs (left lower lobe and bilateral upper lungs)", "left hilar node", "brain", "spinal cord"]
- Old field status: "REPORTED"
- New field status: "REPORTED"
- Old evidence type: ["AUTHOR_INTERPRETATION", "OBSERVED_FACT"]
- New evidence type: ["OBSERVED_FACT"]
- Old quote verification: `VERIFIED`
- New quote verification: `VERIFIED`
- Reason: value changed, evidence type changed.

### `case[1].outcome`
- Old value: "The biopsied lesion continued to decrease in size throughout the 19 months that followed after initial diagnosis; melanoma recurred with lung, brain, and spinal cord metastases and was resistant to ipilimumab."
- New value: "Melanoma recurred with lung, brain, and spinal cord metastases resistant to ipilimumab; the biopsied lesion continued to decrease in size."
- Old field status: "REPORTED"
- New field status: "REPORTED"
- Old evidence type: ["AUTHOR_INTERPRETATION"]
- New evidence type: ["OBSERVED_FACT"]
- Old quote verification: `VERIFIED`
- New quote verification: `VERIFIED`
- Reason: value changed, evidence type changed.

### `case[1].partial_or_complete`
- Old value: "partial"
- New value: "partial"
- Old field status: "REPORTED"
- New field status: "REPORTED"
- Old evidence type: ["AUTHOR_INTERPRETATION"]
- New evidence type: ["AUTHOR_INTERPRETATION", "OBSERVED_FACT"]
- Old quote verification: `VERIFIED`
- New quote verification: `VERIFIED`
- Reason: evidence type changed.

### `case[1].primary_site`
- Old value: "No primary lesion identified"
- New value: "No primary lesion identified on clinical examination"
- Old field status: "REPORTED"
- New field status: "REPORTED"
- Old evidence type: ["OBSERVED_FACT"]
- New evidence type: ["OBSERVED_FACT"]
- Old quote verification: `VERIFIED`
- New quote verification: `VERIFIED`
- Reason: value changed.

### `case[1].regression_confirmed_date`
- Old value: "43 days later"
- New value: "43 days after the baseline CT"
- Old field status: "REPORTED"
- New field status: "REPORTED"
- Old evidence type: ["AUTHOR_INTERPRETATION"]
- New evidence type: ["OBSERVED_FACT"]
- Old quote verification: `VERIFIED`
- New quote verification: `VERIFIED`
- Reason: value changed, evidence type changed.

### `case[1].treatment_before_regression`
- Old value: "CT-guided biopsy of the left lower lobe nodule"
- New value: "ipilimumab; timing relative to the initially documented regression is not explicitly stated"
- Old field status: "REPORTED"
- New field status: "UNCERTAIN"
- Old evidence type: ["OBSERVED_FACT"]
- New evidence type: []
- Old quote verification: `VERIFIED`
- New quote verification: `VERIFIED`
- Reason: value changed, field status changed, evidence type changed.

### `case[1].treatment_status`
- Old value: "Immune therapy with ipilimumab was given after initial diagnosis; timing relative to the observed regression is not explicitly reported."
- New value: "unknown"
- Old field status: "UNCERTAIN"
- New field status: "UNCERTAIN"
- Old evidence type: []
- New evidence type: []
- Old quote verification: `VERIFIED`
- New quote verification: `NOT_APPLICABLE`
- Reason: value changed, quote verification changed.


## Verification failures

### Old run 8
- Field: `event.description`
  - Status: `UNVERIFIED`
  - Quote: "Fig. 3 – Positron emission tomography–computed tomography images, 43 days later. ... (C) Bilateral upper lobe disease has increased (arrows). These show intensely increased ﬂudeoxyglucose uptake on positron emission tomography (D). Note left hilar nodal spread (arrowhead)."
  - Reason: Quote was not found in normalized paper text

### New run 10
- None.
