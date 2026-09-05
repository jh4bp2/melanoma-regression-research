# Paper 2: run 7 vs run 11

> Association does not imply causation. This report compares extraction behavior, not clinical truth.

## Summary

- `status`: "partial" → "partial"
- `case_count`: 1 → 1
- `event_count`: 10 → 12
- `evidence_count`: 30 → 35
- `quote_rejected`: 4 → 0
- `retry_count`: 0 → 0
- `prompt_version`: "paper_metadata:v1,case_detection:v1,case_extraction:v1,timeline_extraction:v1" → "paper_metadata:v2,case_detection:v2,case_extraction:v2,timeline_extraction:v2"
- `evidence_type_counts`: {"AUTHOR_INTERPRETATION": 3, "OBSERVED_FACT": 27} → {"AUTHOR_INTERPRETATION": 2, "OBSERVED_FACT": 33}
- `reason_codes`: [] → ["PARTIAL_TEMPORAL_UNCERTAINTY"]

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

### `case[1].outcome`
- Old value: "Post-operative CT chest confirmed the left upper lobe nodule had been completely resected with no new pulmonary nodules."
- New value: "The left upper lobe nodule was completely resected with no new pulmonary nodules on postoperative CT chest."
- Old field status: "REPORTED"
- New field status: "REPORTED"
- Old evidence type: []
- New evidence type: ["OBSERVED_FACT"]
- Old quote verification: `UNVERIFIED`
- New quote verification: `VERIFIED`
- Reason: value changed, evidence type changed, quote verification changed.

### `case[1].partial_or_complete`
- Old value: "complete"
- New value: null
- Old field status: "REPORTED"
- New field status: "NOT_REPORTED"
- Old evidence type: ["OBSERVED_FACT"]
- New evidence type: []
- Old quote verification: `VERIFIED`
- New quote verification: `NOT_APPLICABLE`
- Reason: value changed, field status changed, evidence type changed, quote verification changed.

### `case[1].preceding_events`
- Old value: ["investigation of peripheral neuropathy", "Computed-tomography-guided biopsy"]
- New value: ["Computed-tomography-guided biopsy of the lung nodule demonstrated malignant melanoma.", "Serial PET/CT scans were performed at 3 and 6 months; at 6 months the nodule SUV had reduced to 0.9."]
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
- New value: null
- Old field status: "REPORTED"
- New field status: "UNCERTAIN"
- Old evidence type: ["OBSERVED_FACT"]
- New evidence type: []
- Old quote verification: `VERIFIED`
- New quote verification: `VERIFIED`
- Reason: value changed, field status changed, evidence type changed.

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

### New run 11
- None.
