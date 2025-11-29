import pandas as pd
from pathlib import Path

DATA_DIR = Path(__file__).resolve().parents[1] / "data"


def main():
    in_path = DATA_DIR / "reviews_clean_raw.csv"
    print(f"Loading {in_path} ...")
    df = pd.read_csv(in_path)

    print("Original rows:", len(df))

    # Drop empty reviews
    df = df.dropna(subset=["review"])

    # Remove very short reviews (e.g. "Good", "Ok")
    df = df[df["review"].str.len() > 5]

    # Standardize date to YYYY-MM-DD
    df["date"] = pd.to_datetime(df["date"]).dt.date

    # Optional: sort by bank + date
    df = df.sort_values(by=["bank", "date"]).reset_index(drop=True)

    # Save final cleaned dataset
    out_path = DATA_DIR / "reviews_clean_final.csv"
    df.to_csv(out_path, index=False)

    print("Cleaned rows:", len(df))
    print(f"Saved cleaned reviews to {out_path}")


if __name__ == "__main__":
    main()
