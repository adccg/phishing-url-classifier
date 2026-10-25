from pathlib import Path

import joblib
import pandas as pd
from sklearn.base import clone
from sklearn.ensemble import RandomForestClassifier
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import ConfusionMatrixDisplay, classification_report
from sklearn.model_selection import cross_val_score, train_test_split
from sklearn.pipeline import make_pipeline
from sklearn.preprocessing import StandardScaler

from features import extract_features

HERE = Path(__file__).parent
FIG_DIR = HERE / "figures"
MODEL_DIR = HERE / "models"

# Load and clean
df = pd.read_csv(HERE / "data" / "PhiUSIIL_Phishing_URL_Dataset.csv")
df = df.drop_duplicates(subset="URL")
y = df["label"]  # 1 = legitimate, 0 = phishing

# Feature set A: the dataset's own URL features
DATASET_FEATURES = [
    "URLLength", "DomainLength", "IsDomainIP", "TLDLength", "NoOfSubDomain",
    "NoOfLettersInURL", "LetterRatioInURL", "NoOfDegitsInURL", "DegitRatioInURL",
    "NoOfEqualsInURL", "NoOfQMarkInURL", "NoOfAmpersandInURL",
    "NoOfOtherSpecialCharsInURL", "SpacialCharRatioInURL", "IsHTTPS",
]
# Feature set B: our own domain-only features
OWN = "B: own domain-only features"
feature_sets = {
    "A: dataset URL features": df[DATASET_FEATURES],
    OWN: pd.DataFrame(df["URL"].apply(extract_features).tolist(), index=df.index),
}

# One split for both, so both are tested on exactly the same unseen websites
train_idx, test_idx = train_test_split(
    df.index, test_size=0.2, stratify=y, random_state=42
)

models = {
    "Logistic regression": make_pipeline(StandardScaler(), LogisticRegression(max_iter=1000)),
    "Random forest": RandomForestClassifier(
        n_estimators=100, min_samples_leaf=5, n_jobs=-1, random_state=42
    ),
}

# Compare models with cross-validation on the TRAINING data only
cv_scores = {}
for set_name, X in feature_sets.items():
    print(f"\n=== {set_name}: 5-fold cross-validation (training data) ===")
    for model_name, model in models.items():
        scores = cross_val_score(model, X.loc[train_idx], y.loc[train_idx], cv=5)
        cv_scores[(set_name, model_name)] = scores.mean()
        print(f"{model_name:20s} accuracy: {scores.mean():.4f} (± {scores.std():.4f})")

# Final check: best model per feature set, scored ONCE on the untouched test set
print("\n=== Final check on the untouched test set ===")
for set_name, X in feature_sets.items():
    best_name = max(models, key=lambda name: cv_scores[(set_name, name)])
    model = clone(models[best_name])
    model.fit(X.loc[train_idx], y.loc[train_idx])
    predictions = model.predict(X.loc[test_idx])

    print(f"\n{set_name} (best model: {best_name})")
    print(classification_report(
        y.loc[test_idx], predictions, target_names=["phishing", "legitimate"], digits=4
    ))

    if set_name == OWN:
        disp = ConfusionMatrixDisplay.from_predictions(
            y.loc[test_idx], predictions, display_labels=["phishing", "legitimate"]
        )
        disp.ax_.set_title("Model B on unseen test data")
        disp.figure_.savefig(FIG_DIR / "confusion_matrix.png", dpi=150, bbox_inches="tight")

        if hasattr(model, "feature_importances_"):
            importances = pd.Series(model.feature_importances_, index=X.columns)
            print("Feature importance (Model B):")
            print(importances.sort_values(ascending=False).round(3))

        MODEL_DIR.mkdir(exist_ok=True)
        joblib.dump(model, MODEL_DIR / "phishing_model.joblib", compress=3)
        print("\nModel B saved to:", MODEL_DIR / "phishing_model.joblib")