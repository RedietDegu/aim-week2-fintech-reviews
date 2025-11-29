import pandas as pd
from pathlib import Path

DATA_DIR = Path(__file__).resolve().parents[1] / "data"

# You can tweak these lists later if you see more patterns
THEMES = {
    "Login & Access Issues": [
        "login", "log in", "sign in", "otp", "verification", "verify",
        "password", "pin", "account locked"
    ],
    "Performance & Speed": [
        "slow", "loading", "load", "lag", "delay", "takes time",
        "not responding", "hang", "freeze"
    ],
    "Transactions & Payments": [
        "transfer", "transaction", "payment", "send money", "deposit",
        "withdraw", "airtime", "bill", "failed", "declined"
    ],
    "Stability & Bugs": [
        "crash", "force close", "bug", "error", "not working",
        "stopped", "doesn work", "doesn't work", "fail", "issue"
    ],
    "UI & Ease of Use": [
        "ui", "interface", "user friendly", "easy to use",
        "design", "layout", "navigation"
    ],
    "Features & Updates": [
        "fingerprint", "face id", "feature", "update", "new version",
        "notification", "alert", "dark mode"
    ]
}


def detect_themes(review: str) -> str:
    if not isinstance(review, str):
        return "Other"

    text = review.lower()
    found = []

    for theme, keywords in THEMES.items():
        if any(k in text for k in keywords):
            found.append(theme)

    return ", ".join(found) if found else "Other"


def main():
    df_path = DATA_DIR / "reviews_with_sentiment.csv"
    print(f"Loading {df_path} ...")
    df = pd.read_csv(df_path)

    print("Tagging themes...")
    df["themes"] = df["review"].astype(str).apply(detect_themes)

    out_path = DATA_DIR / "reviews_with_sentiment_and_themes.csv"
    df.to_csv(out_path, index=False)

    print(f"Saved tagged reviews to {out_path}")
    print(df[["bank", "rating", "sentiment_label", "themes"]].head(10))


if __name__ == "__main__":
    main()
