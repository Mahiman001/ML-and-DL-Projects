import joblib
import numpy as np
import pandas as pd
from pathlib import Path

# Locate the project root and saved model
PROJECT_ROOT = Path(__file__).resolve().parent.parent
MODEL_PATH = PROJECT_ROOT / "MODELS" / "personality_baseline.joblib"

# Load the trained pipeline once
model = joblib.load(MODEL_PATH)

# Expected questionnaire feature order

# Preserve the exact feature order used during model training
QUESTIONNAIRE_COLUMNS = list(model.feature_names_in_)

TRAITS = ["E", "A", "C", "O", "N"]


def predict_personality(answers: dict) -> dict:
    """Predict five OCEAN scores from 50 questionnaire answers."""

    if set(answers.keys()) != set(QUESTIONNAIRE_COLUMNS):
        raise ValueError("Exactly the 50 expected questionnaire fields are required.")

    values = [answers[col] for col in QUESTIONNAIRE_COLUMNS]

    if any(
        not isinstance(value, (int, float, np.integer, np.floating))
        or not np.isfinite(value)
        or not 1 <= value <= 5
        for value in values
    ):
        raise ValueError("Each answer must be a finite number between 1 and 5.")

    input_df = pd.DataFrame([answers], columns=QUESTIONNAIRE_COLUMNS)
    predictions = model.predict(input_df)[0]

    return {
        trait: round(float(score), 3)
        for trait, score in zip(TRAITS, predictions)
    }
    
def interpret_scores(scores: dict) -> dict:
    """Convert OCEAN scores into simple descriptive labels."""

    interpretations = {}

    for trait, score in scores.items():
        if score < 2:
            level = "Low"
        elif score < 4:
            level = "Moderate"
        else:
            level = "High"

        interpretations[trait] = {
            "score": score,
            "level": level,
        }

    return interpretations    