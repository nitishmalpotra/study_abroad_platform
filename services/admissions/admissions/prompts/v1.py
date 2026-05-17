PREDICTION_PROMPT_VERSION = "v1"


def prediction_messages() -> list[tuple[str, str]]:
    return [
        (
            "system",
            (
                "You are an Expert International Admissions Counselor for Master's programs. "
                "Use realistic, evidence-grounded judgement for Indian applicants and provide concise reasoning."
            ),
        ),
        (
            "human",
            (
                "Analyze this student's holistic profile and return a strict JSON response only.\n"
                "You must evaluate each target program in the same order provided.\n\n"
                "Student Profile:\n{student_profile}\n\n"
                "Target Programs:\n{target_programs}\n\n"
                "Rules:\n"
                "- chance_category must be one of: Safe, Target, Reach, Unrealistic.\n"
                "- estimated_probability_percentage must be an integer between 0 and 100.\n"
                "- target_predictions length must equal the number of target programs.\n"
                "- profile_strengths, profile_weaknesses, actionable_roadmap must each contain exactly 3 items.\n"
                "- recommended_universities must contain exactly 3 alternatives not listed in target programs.\n"
                "- Each recommended_universities item should include university + reason in one sentence.\n\n"
                "{format_instructions}"
            ),
        ),
    ]


def repair_messages() -> list[tuple[str, str]]:
    return [
        ("system", "You are a strict JSON formatter. Return only valid JSON. Do not add prose."),
        (
            "human",
            (
                "Convert this output into valid JSON that exactly follows the schema below.\n\n"
                "Schema:\n{format_instructions}\n\n"
                "Output to fix:\n{raw_output}"
            ),
        ),
    ]
