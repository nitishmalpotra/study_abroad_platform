from pydantic import BaseModel, ConfigDict


FALLBACK_RECOMMENDATIONS = [
    "Northeastern University (MS CS): Strong co-op ecosystem and industry-aligned curriculum.",
    "Arizona State University (MS CS): Broad intake capacity with solid applied research opportunities.",
    "University at Buffalo, SUNY (MS CS): Balanced selectivity with a good ROI for international students.",
]


class AppSettings(BaseModel):
    model_config = ConfigDict(extra="forbid")


def load_settings() -> AppSettings:
    return AppSettings()
