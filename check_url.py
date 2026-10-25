from pathlib import Path

import joblib
import pandas as pd

from features import extract_features

MODEL_PATH = Path(__file__).parent / "models" / "phishing_model.joblib"
model = joblib.load(MODEL_PATH)
PHISHING_COLUMN = list(model.classes_).index(0)  # label 0 = phishing


def check(url: str) -> tuple[str, float]:
    """Return a verdict and the model's phishing probability for one link."""
    if "://" not in url:
        url = "https://" + url  # assume https when the user leaves it out
    features = pd.DataFrame([extract_features(url)])
    phishing_prob = model.predict_proba(features)[0][PHISHING_COLUMN]
    verdict = "PHISHING" if phishing_prob >= 0.5 else "legitimate"
    return verdict, phishing_prob


if __name__ == "__main__":
    print("Paste a link to check it (press Enter on an empty line to quit).")
    while True:
        url = input("\nLink: ").strip()
        if not url:
            break
        verdict, prob = check(url)
        print(f"{verdict}  (phishing probability: {prob:.0%})")