
from fastapi import FastAPI
from pydantic import BaseModel, Field, ConfigDict, field_validator

from src.predict import (
    predict_personality,
    QUESTIONNAIRE_COLUMNS,
    interpret_scores,
)
app = FastAPI(
    title="Big Five Personality API",
    description="Predicts OCEAN personality trait scores from 50 questionnaire answers.",
    version="1.0.0",
)


class PersonalityRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")

    answers: dict[str, float]

    @field_validator("answers")
    @classmethod
    def validate_answers(cls, answers):
        expected = set(QUESTIONNAIRE_COLUMNS)
        received = set(answers.keys())

        missing = expected - received
        extra = received - expected

        if missing or extra:
            raise ValueError(
                f"Expected exactly 50 questionnaire fields. "
                f"Missing: {sorted(missing)}; unexpected: {sorted(extra)}"
            )

        for question, value in answers.items():
            if not 1 <= value <= 5:
                raise ValueError(
                    f"{question} must be between 1 and 5."
                )

        return answers


@app.get("/")
def home():
    return {"message": "Big Five Personality API is running"}


@app.post("/predict")
def predict(request: PersonalityRequest):
    scores = predict_personality(request.answers)
    interpretations = interpret_scores(scores)

    return {
        "personality_scores": scores,
        "interpretations": interpretations,
    }

