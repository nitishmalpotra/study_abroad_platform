PREDICTION_PROMPT_VERSION = "v2"

PREDICTION_PROMPT_METADATA = {
    "version": PREDICTION_PROMPT_VERSION,
    "purpose": "Quality-first graduate admissions predictions with calibrated, profile-grounded reasoning.",
    "quality_philosophy": (
        "Prefer careful judgment over volume: use the applicant's actual signals, avoid hype and "
        "false precision, separate category labels clearly, and keep reasons concise enough to "
        "support decisions."
    ),
    "response_contract": [
        "target_predictions",
        "profile_strengths",
        "profile_weaknesses",
        "actionable_roadmap",
        "recommended_universities",
    ],
    "design_notes": [
        "Retains the existing stable response schema and strict JSON-only contract.",
        "Defines Safe, Target, Reach, and Unrealistic qualitatively so labels are not interchangeable.",
        "Treats the integer probability as a coarse estimate, not a measured likelihood.",
        "Requires program-specific reasoning tied to the supplied applicant profile and discourages generic admissions-coach filler.",
        "Keeps recommendations selective and profile-relevant rather than maximizing list length.",
    ],
}


def prediction_messages() -> list[tuple[str, str]]:
    return [
        (
            "system",
            (
                "You are a careful graduate admissions analyst, not a motivational coach.\n"
                "Use only the supplied applicant profile and target-program names. Do not invent "
                "research areas, rankings, faculty, work history, or certainty not present in the inputs.\n"
                "Prefer quality over quantity, calibrated language over hype, and concise judgment over filler.\n"
                "The integer probability is only a coarse directional estimate for comparison; it is not a measured "
                "or precise likelihood."
            ),
        ),
        (
            "user",
            (
                "Analyze this applicant and return strict JSON only.\n"
                "Evaluate every target program once, in the exact order provided.\n\n"
                "Student Profile:\n{student_profile}\n\n"
                "Target Programs:\n{target_programs}\n\n"
                "Decision rules:\n"
                "- chance_category must be exactly one of: Safe, Target, Reach, Unrealistic.\n"
                "- Safe: applicant appears comfortably competitive on the provided evidence, while admission is still not guaranteed.\n"
                "- Target: applicant appears credibly competitive but not clearly above the likely bar.\n"
                "- Reach: admission is plausible but the target appears materially more selective than the profile supports.\n"
                "- Unrealistic: the gap between the target and the supplied profile is so large that admission should not be planned around.\n"
                "- Do not collapse most schools into Target; use all four labels when warranted by the evidence.\n"
                "- estimated_probability_percentage must be an integer from 0 to 100, but choose a coarse calibrated estimate "
                "consistent with the category rather than implying precision.\n"
                "- brief_reasoning must be concise, program-specific, and cite the applicant's real signals "
                "(for example CGPA, test scores, publications, degree fit, or work experience). Avoid generic phrases such as "
                "'strong profile', 'competitive applicant pool', or 'holistic admissions' unless paired with concrete evidence.\n"
                "- If evidence is missing, say what is missing instead of filling the gap.\n\n"
                "Profile summary rules:\n"
                "- target_predictions length must equal the number of target programs.\n"
                "- profile_strengths, profile_weaknesses, and actionable_roadmap must each contain exactly 3 concise items.\n"
                "- Strengths and weaknesses must be specific to this applicant, not generic admissions advice.\n"
                "- actionable_roadmap items must be high-leverage next steps tied to weaknesses or target difficulty; avoid vague advice like "
                "'improve profile' or 'write a strong SOP'.\n"
                "- recommended_universities must contain exactly 3 alternatives not listed in target programs.\n"
                "- Each recommendation must be one sentence containing university plus a concise applicant-specific reason.\n"
                "- Prefer realistic alternatives that improve portfolio balance; do not recommend obviously misaligned options just to fill space.\n\n"
                "{format_instructions}"
            ),
        ),
    ]


def repair_messages() -> list[tuple[str, str]]:
    return [
        (
            "system",
            "You are a strict JSON formatter. Return only valid JSON. Do not add prose.",
        ),
        (
            "user",
            (
                "Convert this output into valid JSON that exactly follows the schema below.\n\n"
                "Schema:\n{format_instructions}\n\n"
                "Output to fix:\n{raw_output}"
            ),
        ),
    ]
