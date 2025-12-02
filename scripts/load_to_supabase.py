import os
from pathlib import Path

import pandas as pd
import psycopg2
from dotenv import load_dotenv

BASE_DIR = Path(__file__).resolve().parents[1]
DATA_DIR = BASE_DIR / "data"

# Load env once
load_dotenv(BASE_DIR / ".env")
DATABASE_URL = os.getenv("DATABASE_URL", "").strip()


def get_connection():
    if not DATABASE_URL:
        raise RuntimeError("DATABASE_URL is not set in .env")
    return psycopg2.connect(DATABASE_URL)


BANK_APP_NAMES = {
    "CBE": "Commercial Bank of Ethiopia Mobile",
    "BOA": "Bank of Abyssinia Mobile",
    "Dashen": "Dashen Bank Mobile",
}


def upsert_banks(conn, df: pd.DataFrame):
    banks = df["bank"].unique()

    with conn.cursor() as cur:
        for bank in banks:
            app_name = BANK_APP_NAMES.get(bank, bank)
            cur.execute(
                """
                INSERT INTO banks (bank_name, app_name)
                SELECT %s, %s
                WHERE NOT EXISTS (
                    SELECT 1 FROM banks WHERE bank_name = %s
                );
                """,
                (bank, app_name, bank),
            )
    conn.commit()


def load_reviews(conn, df: pd.DataFrame):
    with conn.cursor() as cur:
        for _, row in df.iterrows():
            bank_name = row["bank"]

            cur.execute("SELECT bank_id FROM banks WHERE bank_name = %s;", (bank_name,))
            result = cur.fetchone()
            if not result:
                print(f"Skipping review, bank not found: {bank_name}")
                continue
            bank_id = result[0]

            cur.execute(
                """
                INSERT INTO reviews (
                    bank_id,
                    review_text,
                    rating,
                    review_date,
                    sentiment_label,
                    sentiment_score,
                    source,
                    themes
                )
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s);
                """,
                (
                    bank_id,
                    row["review"],
                    int(row["rating"]),
                    row["date"],
                    row["sentiment_label"],
                    float(row["sentiment_score"]),
                    row["source"],
                    row.get("themes", None),
                ),
            )
    conn.commit()


def main():
    csv_path = DATA_DIR / "reviews_with_sentiment_and_themes.csv"
    print(f"Loading {csv_path} ...")
    df = pd.read_csv(csv_path)

    print("Total rows:", len(df))

    conn = get_connection()
    try:
        print("Upserting banks ...")
        upsert_banks(conn, df)

        print("Inserting reviews ...")
        load_reviews(conn, df)

        print("Done loading data into Supabase/Postgres.")
    finally:
        conn.close()


if __name__ == "__main__":
    main()
