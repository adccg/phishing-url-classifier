import pandas as pd

from pathlib import Path

DATA_PATH = Path(__file__).parent / "data" / "PhiUSIIL_Phishing_URL_Dataset.csv"
df = pd.read_csv(DATA_PATH)

print("Rows and columns:", df.shape)
print("\nColumn names:\n", list(df.columns))
print("\nLabel counts (1 = legitimate, 0 = phishing):\n", df["label"].value_counts())
print("\nDuplicate URLs:", df["URL"].duplicated().sum())
print("\nFirst 5 rows:\n", df[["URL", "URLLength", "IsHTTPS", "label"]].head())