import pandas as pd
from pathlib import Path
from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer

DATA_DIR = Path(__file__).resolve().parents[1] / "data"


def label_from_score(score: float) -> str:
    """Convert VADER compound score to POS / NEG / NEU label."""
    if score >= 0.05:
        return "positive"
    if score <= -0.05:
        return "negative"
    return "neutral"


def apply_rating_override(row: pd.Series) -> str:
    """
    Use the explicit star rating as a sanity-check override.
    Very low star ratings shouldn't end up labelled positive even if VADER is confused
    by wording such as "better but doesn't work".
    """
    label = row["sentiment_label"]
    score = row["sentiment_score"]
    rating = row.get("rating", None)

    if pd.isna(rating):
        return label

    # Force clearly negative sentiment for 1-2 star reviews unless VADER already agrees.
    if rating <= 2 and score > -0.05:
        return "negative"

    # Force clearly positive sentiment for 4-5 star reviews unless VADER already agrees.
    if rating >= 4 and score < 0.05:
        return "positive"

    # Default: keep VADER label (3-star ratings often represent mixed views).
    return label


def main():
    in_path = DATA_DIR / "reviews_clean_final.csv"
    print(f"Loading {in_path} ...")
    df = pd.read_csv(in_path)

    print("Rows:", len(df))

    sia = SentimentIntensityAnalyzer()

    # Compute sentiment scores for each review
    scores = df["review"].astype(str).apply(sia.polarity_scores)
    scores_df = pd.DataFrame(list(scores))

    # Add compound score + label to original df
    df["sentiment_score"] = scores_df["compound"]
    df["sentiment_label"] = df["sentiment_score"].apply(label_from_score)

    # Adjust VADER labels using the actual star rating as a secondary signal.
    df["sentiment_label"] = df.apply(apply_rating_override, axis=1)

    out_path = DATA_DIR / "reviews_with_sentiment.csv"
    df.to_csv(out_path, index=False)

    print("Sentiment columns added.")
    print(f"Saved file to {out_path}")


if __name__ == "__main__":
    main()
