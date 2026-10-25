from pathlib import Path

import matplotlib.pyplot as plt
import pandas as pd

HERE = Path(__file__).parent
DATA_PATH = HERE / "data" / "PhiUSIIL_Phishing_URL_Dataset.csv"
FIG_DIR = HERE / "figures"
FIG_DIR.mkdir(exist_ok=True)

df = pd.read_csv(DATA_PATH)

# 1. Clean the data
df = df.drop(columns=["FILENAME"])
df = df.drop_duplicates(subset="URL")
print("Rows after removing duplicates:", len(df))

# Readable names for the charts
df["type"] = df["label"].map({1: "legitimate", 0: "phishing"})

# Simple features that can be calculated from the link text alone
URL_FEATURES = [
    "URLLength", "DomainLength", "IsDomainIP", "TLDLength", "NoOfSubDomain",
    "NoOfLettersInURL", "LetterRatioInURL", "NoOfDegitsInURL", "DegitRatioInURL",
    "NoOfEqualsInURL", "NoOfQMarkInURL", "NoOfAmpersandInURL",
    "NoOfOtherSpecialCharsInURL", "SpacialCharRatioInURL", "IsHTTPS",
]

# 2. Average of each feature, phishing vs legitimate
print("\nAverage per type:")
print(df.groupby("type")[URL_FEATURES].mean().T.round(2))

# 3a. Chart: URL length distribution
fig, ax = plt.subplots(figsize=(8, 5))
for name, group in df.groupby("type"):
    ax.hist(group["URLLength"].clip(upper=150), bins=50, alpha=0.6, label=name)
ax.set_title("URL length: phishing vs legitimate")
ax.set_xlabel("URL length (characters, capped at 150)")
ax.set_ylabel("Number of URLs")
ax.legend()
fig.savefig(FIG_DIR / "url_length.png", dpi=150, bbox_inches="tight")

# 3b. Chart: share of URLs using HTTPS
https_share = df.groupby("type")["IsHTTPS"].mean() * 100
fig, ax = plt.subplots(figsize=(6, 4))
https_share.plot.bar(ax=ax, color=["tab:blue", "tab:orange"])
ax.set_title("Share of URLs using HTTPS")
ax.set_ylabel("Percent")
ax.set_xlabel("")
fig.savefig(FIG_DIR / "https_share.png", dpi=150, bbox_inches="tight")

# 4. The "bare homepage" check: does the URL have anything after the domain?
after_domain = (
    df["URL"].str.replace(r"^https?://", "", regex=True)
    .str.split("/", n=1).str[1].fillna("")
)
df["has_path"] = after_domain.str.len() > 0
print("\nPercent of URLs with something after the domain:")
print((df.groupby("type")["has_path"].mean() * 100).round(1))

print("\nCharts saved in:", FIG_DIR)