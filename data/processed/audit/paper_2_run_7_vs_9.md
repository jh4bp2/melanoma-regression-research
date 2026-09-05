# Paper 2: run 7 vs run 9

> Association does not imply causation. This report compares extraction behavior, not clinical truth.

## Summary

- `status`: "partial" → "partial"
- `case_count`: 1 → 1
- `event_count`: 10 → 12
- `evidence_count`: 30 → 34
- `quote_rejected`: 4 → 2
- `retry_count`: 0 → 0
- `prompt_version`: "paper_metadata:v1,case_detection:v1,case_extraction:v1,timeline_extraction:v1" → "paper_metadata:v2,case_detection:v2,case_extraction:v2,timeline_extraction:v2"
- `evidence_type_counts`: {"AUTHOR_INTERPRETATION": 3, "OBSERVED_FACT": 27} → {"AUTHOR_INTERPRETATION": 1, "OBSERVED_FACT": 33}
- `reason_codes`: [] → ["PARTIAL_FIELD_WITHOUT_EVIDENCE", "PARTIAL_TEMPORAL_UNCERTAINTY", "PARTIAL_UNVERIFIED_QUOTE"]

## Changed fields

### `case[1].metastatic_sites`
- Old value: ["left upper lobe lingula segment of lung"]
- New value: ["left upper lobe lingula segment lung nodule"]
- Old field status: "REPORTED"
- New field status: "REPORTED"
- Old evidence type: ["OBSERVED_FACT"]
- New evidence type: ["OBSERVED_FACT"]
- Old quote verification: `VERIFIED`
- New quote verification: `VERIFIED`
- Reason: value changed.

### `case[1].preceding_events`
- Old value: ["investigation of peripheral neuropathy", "Computed-tomography-guided biopsy"]
- New value: ["Computed-tomography-guided biopsy demonstrated malignant melanoma.", "Serial PET/CT scans were performed at 3 and 6 months as part of the treatment planning workup."]
- Old field status: "REPORTED"
- New field status: "REPORTED"
- Old evidence type: ["OBSERVED_FACT"]
- New evidence type: ["OBSERVED_FACT"]
- Old quote verification: `VERIFIED`
- New quote verification: `VERIFIED`
- Reason: value changed.

### `case[1].regression_start_date`
- Old value: "at 6 months"
- New value: null
- Old field status: "REPORTED"
- New field status: "UNCERTAIN"
- Old evidence type: ["OBSERVED_FACT"]
- New evidence type: []
- Old quote verification: `VERIFIED`
- New quote verification: `VERIFIED`
- Reason: value changed, field status changed, evidence type changed.

### `case[1].treatment_status`
- Old value: "Video-assisted thoracoscopic surgery wedge resection of the left upper lobe lesion was performed 8 months after initial diagnosis."
- New value: "unknown"
- Old field status: "REPORTED"
- New field status: "UNCERTAIN"
- Old evidence type: ["OBSERVED_FACT"]
- New evidence type: []
- Old quote verification: `VERIFIED`
- New quote verification: `VERIFIED`
- Reason: value changed, field status changed, evidence type changed.

### `paper.abstract`
- Old value: "Spontaneous regression of metastatic melanoma is a rare event with only 76 cases\nhaving been reported since 1866. The precise mechanism of regression remains\nunknown. We present a case of a man with spontaneous regression of pulmonary\nmetastatic melanoma conﬁrmed on histopathology accompanied by reduction in\nﬂuorodeoxyglucose-activity on serial positron emission tomography/computed\ntomography scan."
- New value: "Spontaneous regression of metastatic melanoma is a rare event with only 76 cases\nhaving been reported since 1866. The precise mechanism of regression remains\nunknown. We present a case of a man with spontaneous regression of pulmonary\nmetastatic melanoma conﬁrmed on histopathology accompanied by reduction in\nﬂuorodeoxyglucose-activity on serial positron emission tomography/computed\ntomography scan."
- Old field status: "REPORTED"
- New field status: "REPORTED"
- Old evidence type: ["AUTHOR_INTERPRETATION"]
- New evidence type: ["OBSERVED_FACT"]
- Old quote verification: `VERIFIED`
- New quote verification: `VERIFIED`
- Reason: evidence type changed.

### `paper.title`
- Old value: "Spontaneous regression of pulmonary\nmetastatic melanoma"
- New value: "Spontaneous regression of pulmonary metastatic melanoma"
- Old field status: "REPORTED"
- New field status: "REPORTED"
- Old evidence type: ["OBSERVED_FACT"]
- New evidence type: ["OBSERVED_FACT"]
- Old quote verification: `VERIFIED`
- New quote verification: `VERIFIED`
- Reason: value changed.


## Verification failures

### Old run 7
- Field: `paper.case_existence`
  - Status: `UNVERIFIED`
  - Quote: "A healthy 83-year-old male, a lifelong non-smoker, was found to have an incidental 15 mm left upper lobe lingula segment lung nodule... Computed-tomography-guided biopsy demonstrated malignant melanoma, immunohistochemistry was positive for S-100 and Melan-A."
  - Reason: Quote was not found in normalized paper text
- Field: `paper.case_existence`
  - Status: `UNVERIFIED`
  - Quote: "Video-assisted thoracoscopic surgery wedge resection of the left upper lobe lesion was performed 8 months after initial diagnosis. Histopathology showed scattered completely infarcted and necrotic ghost outlines of cells seen within the nodule with no viable cells present."
  - Reason: Quote was not found in normalized paper text
- Field: `case.outcome`
  - Status: `UNVERIFIED`
  - Quote: "Post-operative CT chest confirmed the left upper lobe nodule had been completely resected with no new pulmonary nodules."
  - Reason: Quote was not found in normalized paper text
- Field: `event.description`
  - Status: `UNVERIFIED`
  - Quote: "Post-operative CT chest confirmed the left upper lobe nodule had been completely resected with no new pulmonary nodules."
  - Reason: Quote was not found in normalized paper text

### New run 9
- Field: `case.outcome`
  - Status: `UNVERIFIED`
  - Quote: "Post-operative CT chest confirmed the left upper lobe nodule had been completely resected with no new pulmonary nodules."
  - Reason: Quote was not found in normalized paper text
- Field: `event.description`
  - Status: `UNVERIFIED`
  - Quote: "Post-operative CT chest conﬁrmed the left upper lobe nodule had been completely resected with no new pulmonary nodules."
  - Reason: Quote was not found in normalized paper text
