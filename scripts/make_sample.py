"""Pull a 50,000-loan sample (issued 2016-2018) out of the full LendingClub file.

The full file has over two million rows and about 150 columns, far more than Excel can
open. This script keeps the columns the dashboard needs, keeps loans issued 2016-2018,
and draws a reproducible random sample of 50,000.

Run from the project folder:
    python3 scripts/make_sample.py
"""
from pathlib import Path
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / "data" / "accepted_2007_to_2018Q4.csv"
TARGET = ROOT / "data" / "loans_2016_2018_sample.csv"
SAMPLE_SIZE = 50_000
SEED = 42

COLUMNS = [
    "id", "issue_d", "loan_status", "grade", "sub_grade", "purpose", "term",
    "loan_amnt", "funded_amnt", "int_rate", "installment",
    "annual_inc", "dti", "fico_range_low", "fico_range_high",
    "emp_length", "home_ownership", "verification_status", "addr_state",
    "total_pymnt", "total_rec_prncp", "total_rec_int", "recoveries", "out_prncp",
]


def main():
    if not SOURCE.exists():
        raise SystemExit(f"Cannot find {SOURCE}. Put the Kaggle file in the data folder first.")

    print("Reading the full file (this takes a minute or two)...")
    df = pd.read_csv(SOURCE, usecols=lambda c: c in COLUMNS, low_memory=False)
    missing = [c for c in COLUMNS if c not in df.columns]
    if missing:
        print("Note - these columns were not in the file and are skipped:", missing)
    print(f"  rows in full file: {len(df):,}")

    # the file ends with a few summary lines that are not loans
    df = df.dropna(subset=["issue_d", "loan_status", "loan_amnt"])

    df["issue_date"] = pd.to_datetime(df["issue_d"], format="%b-%Y")
    df = df[df["issue_date"].dt.year.between(2016, 2018)]
    print(f"  loans issued 2016-2018: {len(df):,}")

    sample = df.sample(n=SAMPLE_SIZE, random_state=SEED).sort_values(["issue_date", "id"])

    # tidy a few columns so Excel reads them cleanly
    sample["issue_date"] = sample["issue_date"].dt.strftime("%Y-%m-%d")
    sample["term_months"] = sample["term"].astype(str).str.extract(r"(\d+)").astype(int)
    sample = sample.drop(columns=["issue_d", "term"])
    first = ["id", "issue_date", "loan_status", "grade", "sub_grade", "purpose", "term_months"]
    sample = sample[first + [c for c in sample.columns if c not in first]]

    sample.to_csv(TARGET, index=False)
    print(f"\nWrote {len(sample):,} loans to {TARGET.relative_to(ROOT)}")
    print("\nLoans per year:")
    print(sample["issue_date"].str[:4].value_counts().sort_index().to_string())
    print("\nLoan status:")
    print(sample["loan_status"].value_counts().to_string())
    print("\nGrade:")
    print(sample["grade"].value_counts().sort_index().to_string())


if __name__ == "__main__":
    main()
