from google_play_scraper import reviews, Sort
import pandas as pd
from pathlib import Path


# Folder to save CSV
DATA_DIR = Path(__file__).resolve().parents[1] / "data"
DATA_DIR.mkdir(exist_ok=True)


# Google Play package names for each bank app (no query params such as &hl)
BANK_APPS = [
    {"bank": "CBE", "app_id": "com.combanketh.mobilebanking"},
    {"bank": "BOA", "app_id": "com.boa.boaMobileBanking"},
    {"bank": "Dashen", "app_id": "com.dashen.dashensuperapp"},
]


def scrape_bank_reviews(bank: str, app_id: str, n_reviews: int = 500) -> pd.DataFrame:
    print(f"Scraping {n_reviews} reviews for {bank}...")

    result, _ = reviews(
        app_id,
        lang="en",
        country="et",
        sort=Sort.NEWEST,
        count=n_reviews,
    )

    if not result:
        print(
            f"No reviews returned for {bank} (app_id={app_id}). "
            "Verify the package name and store locale."
        )
        return pd.DataFrame(columns=["review", "rating", "date", "bank", "source"])

    df = pd.DataFrame(result)

    # Keep only columns we need and rename them
    df_clean = pd.DataFrame({
        "review": df["content"],
        "rating": df["score"],
        "date": df["at"].dt.date,  # YYYY-MM-DD
    })

    df_clean["bank"] = bank
    df_clean["source"] = "Google Play"

    # Drop rows with missing review text
    df_clean = df_clean.dropna(subset=["review"])

    return df_clean


def main():
    all_dfs = []

    for app in BANK_APPS:
        df_bank = scrape_bank_reviews(app["bank"], app["app_id"], n_reviews=500)
        all_dfs.append(df_bank)

    full_df = pd.concat(all_dfs, ignore_index=True)

    # Remove duplicate reviews within same bank
    full_df = full_df.drop_duplicates(subset=["review", "bank"])

    out_path = DATA_DIR / "reviews_clean_raw.csv"
    full_df.to_csv(out_path, index=False)
    print(f"Saved {len(full_df)} reviews to {out_path}")


if __name__ == "__main__":
    main()
