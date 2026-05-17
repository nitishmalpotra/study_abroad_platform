# SOP prompt evaluation fixtures

`v2` is a quality-first prompt revision. Its philosophy is to prefer judgment over volume: feedback should be concise, evidence-based, admissions-relevant, candid about weaknesses, and explicit when evidence is missing rather than padded with generic praise.

The fixtures in `fixtures.json` are sanitized synthetic cases, not user submissions. They cover:

- `strong`: specific academic fit, concrete university fit, and coherent goals
- `average`: credible but thinner evidence and some generic phrasing
- `weak_generic`: broadly aspirational text with little admissions value
- `invalid_non_sop`: text that should be rejected before grading

Automated checks validate the stable schema contract, exact criterion order, concise golden outputs, and coarse qualitative tendencies such as `strong > average > weak_generic` and invalid inputs being rejected. They catch obvious regressions, not nuanced admissions judgment drift.

Human review is still needed for:

- calibration of score severity against real applicant essays
- whether feedback is genuinely useful rather than merely schema-valid
- factual restraint when a university is named but the essay is vague
- whether DeepSeek follows the prompt consistently across paraphrases and edge cases

Few-shot examples were intentionally omitted in `v2`: the main failure mode was insufficient rubric discipline, not lack of format imitation, and extra exemplars would add prompt mass while risking style overfitting.
