from .config import FALLBACK_RECOMMENDATIONS
from .schemas import AdmissionPrediction, ProgramPrediction
from .utils import sanitize_text


def _program_tokens(value: str) -> set[str]:
    return {
        token
        for token in sanitize_text(value)
        .lower()
        .replace("(", " ")
        .replace(")", " ")
        .split()
        if token not in {"at", "in"}
    }


def align_predictions_to_targets(
    prediction: AdmissionPrediction, target_programs: list[str]
) -> AdmissionPrediction:
    mapped_predictions = {
        sanitize_text(item.program_name).lower(): item
        for item in prediction.target_predictions
    }
    aligned_predictions: list[ProgramPrediction] = []

    for target in target_programs:
        target_key = sanitize_text(target).lower()
        matched_prediction = mapped_predictions.get(target_key)
        if matched_prediction is None:
            for candidate in prediction.target_predictions:
                candidate_name = sanitize_text(candidate.program_name).lower()
                if (
                    target_key in candidate_name
                    or candidate_name in target_key
                    or _program_tokens(target_key) == _program_tokens(candidate_name)
                ):
                    matched_prediction = candidate
                    break

        if matched_prediction is None:
            matched_prediction = ProgramPrediction(
                program_name=target,
                chance_category="Reach",
                estimated_probability_percentage=20,
                brief_reasoning=(
                    "Model output omitted this target program, so a conservative placeholder estimate is shown."
                ),
            )
        else:
            matched_prediction = ProgramPrediction(
                program_name=target,
                chance_category=matched_prediction.chance_category,
                estimated_probability_percentage=matched_prediction.estimated_probability_percentage,
                brief_reasoning=matched_prediction.brief_reasoning,
            )
        aligned_predictions.append(matched_prediction)

    return AdmissionPrediction(
        target_predictions=aligned_predictions,
        profile_strengths=prediction.profile_strengths,
        profile_weaknesses=prediction.profile_weaknesses,
        actionable_roadmap=prediction.actionable_roadmap,
        recommended_universities=prediction.recommended_universities,
    )


def enforce_alternative_recommendations(
    prediction: AdmissionPrediction, target_programs: list[str]
) -> AdmissionPrediction:
    targets_lower = {sanitize_text(item).lower() for item in target_programs}
    curated: list[str] = []
    seen: set[str] = set()

    for recommendation in prediction.recommended_universities:
        clean = sanitize_text(recommendation, max_length=220)
        if not clean:
            continue
        lowered = clean.lower()
        key = lowered.split(":", 1)[0]
        if any(target in lowered for target in targets_lower):
            continue
        if key in seen:
            continue
        curated.append(clean)
        seen.add(key)

    for fallback in FALLBACK_RECOMMENDATIONS:
        if len(curated) >= 3:
            break
        lowered = fallback.lower()
        key = lowered.split(":", 1)[0]
        if key in seen or any(target in lowered for target in targets_lower):
            continue
        curated.append(fallback)
        seen.add(key)

    return AdmissionPrediction(
        target_predictions=prediction.target_predictions,
        profile_strengths=prediction.profile_strengths,
        profile_weaknesses=prediction.profile_weaknesses,
        actionable_roadmap=prediction.actionable_roadmap,
        recommended_universities=curated[:3],
    )
