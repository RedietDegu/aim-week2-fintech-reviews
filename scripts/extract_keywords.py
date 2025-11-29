import pandas as pd
from pathlib import Path
from sklearn.feature_extraction.text import TfidfVectorizer

DATA_DIR = Path(__file__).resolve().parents[1] / "data"


def extract_keywords(texts, top_n=20):
    vectorizer = TfidfVectorizer(
        stop_words="english",
        max_df=0.8,
        min_df=2,
        ngram_range=(1, 2)
    )
    tfidf_matrix = vectorizer.fit_transform(texts)
    scores = tfidf_matrix.sum(axis=0).A1
    words = vectorizer.get_feature_names_out()

    sorted_idx = scores.argsort()[::-1]  # descending
    return [words[i] for i in sorted_idx[:top_n]]


def main():
    df = pd.read_csv(DATA_DIR / "reviews_with_sentiment.csv")

    banks = df["bank"].unique()
    output = []

    for bank in banks:
        bank_reviews = df[df["bank"] == bank]["review"].astype(str).tolist()
        keywords = extract_keywords(bank_reviews)

        print(f"\n--- Top Keywords for {bank} ---")
        for k in keywords:
            print(" -", k)

        output.append({
            "bank": bank,
            "keywords": ", ".join(keywords)
        })

    out_file = DATA_DIR / "bank_keywords.csv"
    pd.DataFrame(output).to_csv(out_file, index=False)

    print(f"\nSaved to {out_file}")


if __name__ == "__main__":
    main()
