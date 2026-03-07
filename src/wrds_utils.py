# ============================================================
# src/wrds_utils.py
# Reusable WRDS connection and validation utilities
# ============================================================
# Purpose : Centralize all WRDS connection logic so notebooks
#           stay clean and readable.
# Usage   : from src.wrds_utils import connect_wrds, validate_df
# ============================================================

import os
import wrds
import pandas as pd
from dotenv import load_dotenv

# Load credentials from .env file
load_dotenv()


def connect_wrds() -> wrds.Connection:
    """
    Establish a WRDS connection using credentials from .env file.

    Returns
    -------
    wrds.Connection
        An active WRDS connection object.

    Raises
    ------
    EnvironmentError
        If WRDS_USERNAME is not set in .env
    """
    username = os.getenv("WRDS_USERNAME")
    if not username:
        raise EnvironmentError(
            "WRDS_USERNAME not found. "
            "Make sure you have a .env file with WRDS_USERNAME=your_username. "
            "See .env.example for the template."
        )
    print(f"Connecting to WRDS as: {username}")
    conn = wrds.Connection(wrds_username=username)
    print("Connection established.")
    return conn


def validate_df(df: pd.DataFrame, name: str) -> None:
    """
    Run standard validation checks on a pulled DataFrame and
    print a structured report. Does not modify the DataFrame.

    Checks performed
    ----------------
    1. Shape (rows x columns)
    2. Column names and dtypes
    3. Missingness per column (count + %)
    4. Date coverage (if a date column exists)
    5. Duplicate rows

    Parameters
    ----------
    df   : pd.DataFrame  — the DataFrame to validate
    name : str           — label for the report header
    """
    separator = "=" * 60
    print(f"\n{separator}")
    print(f"VALIDATION REPORT: {name}")
    print(separator)

    # 1. Shape
    print(f"\n[1] Shape: {df.shape[0]:,} rows x {df.shape[1]} columns")

    # 2. Columns and dtypes
    print(f"\n[2] Columns and dtypes:")
    for col, dtype in df.dtypes.items():
        print(f"    {col:<35} {str(dtype)}")

    # 3. Missingness
    print(f"\n[3] Missingness:")
    missing = df.isnull().sum()
    missing_pct = (missing / len(df) * 100).round(2)
    for col in df.columns:
        if missing[col] > 0:
            print(f"    {col:<35} {missing[col]:>8,} missing  ({missing_pct[col]}%)")
    if missing.sum() == 0:
        print("    No missing values detected.")

    # 4. Date coverage
    date_cols = [c for c in df.columns if "date" in c.lower()]
    if date_cols:
        print(f"\n[4] Date coverage:")
        for col in date_cols:
            try:
                parsed = pd.to_datetime(df[col], errors="coerce")
                print(f"    {col}: {parsed.min()} → {parsed.max()}")
            except Exception:
                print(f"    {col}: could not parse as date")
    else:
        print(f"\n[4] Date coverage: no date columns detected")

    # 5. Duplicates
    n_dupes = df.duplicated().sum()
    print(f"\n[5] Duplicate rows: {n_dupes:,}")

    print(f"\n{separator}\n")
