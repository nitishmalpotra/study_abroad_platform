# Admissions prompt evaluation fixtures

`v2` is a quality-first prompt revision for graduate-admissions prediction. It keeps the existing schema stable while pushing the model toward calibrated, profile-grounded judgment: clear category separation, coarse rather than over-precise probabilities, concise reasoning, and selective recommendations tied to the actual applicant.

The sanitized synthetic fixtures in `fixtures.json` cover:

- `strong`: clearly competitive profile across balanced targets
- `borderline`: credible but uneven profile where category boundaries matter
- `weak`: limited evidence and meaningful gaps against ambitious targets
- `unrealistic_target`: targets far above the supplied profile, where the model must say so plainly

Automated checks validate the stable schema, prompt metadata/versioning, required fixture coverage, concise golden outputs, category calibration tendencies, and whether golden reasoning is grounded in concrete applicant signals instead of generic admissions-coach language.

Human live-model review is still required for:

- whether DeepSeek preserves category calibration across paraphrases and edge cases
- whether probabilities remain usefully coarse rather than spuriously exact
- whether university recommendations are genuinely sensible for changing market realities
- whether reasons stay practically useful when target names are ambiguous or incomplete

Suggested future eval expansion:

1. Add fixtures only when they introduce a distinct failure mode, such as missing test scores, degree mismatch, or highly specialized programs.
2. Keep deterministic schema and golden-output checks as the first regression layer.
3. Periodically run live-provider spot checks on all fixtures plus paraphrases, then record qualitative drift separately from deterministic test results.
4. Revisit probability-band expectations only after reviewing a larger set of real model outputs; do not tune around a single anecdote.

Raw user submissions must not be committed as fixtures.
