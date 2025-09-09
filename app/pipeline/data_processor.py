import os
from pathlib import Path

import pandas as pd

# --- Paths ---
RAW_DATA_DIR = Path(__file__).resolve().parent.parent.parent / "data" / "raw"
PROCESSED_DIR = Path(__file__).resolve().parent.parent.parent / "data" / "processed"
PROCESSED_DIR.mkdir(parents=True, exist_ok=True)  # safe to keep


def _list_csvs(directory: Path) -> str:
    if not directory.exists():
        return "<dir missing>"
    csvs = sorted(p.name for p in directory.glob("*.csv"))
    return ", ".join(csvs) if csvs else "<no csv files>"


def load_csv(filename: str, subfolder: str = "") -> pd.DataFrame:
    base = RAW_DATA_DIR if not subfolder else (RAW_DATA_DIR / subfolder)
    path = base / filename
    if not path.exists():
        # Helpful diagnostics
        raise FileNotFoundError(
            f"Missing file: {path}\n"
            f"RAW_DATA_DIR: {RAW_DATA_DIR}\n"
            f"In '{base}': [{_list_csvs(base)}]"
        )
    return pd.read_csv(path)


def load_all_raw_data() -> dict:
    # Main job postings
    postings = load_csv("postings.csv")

    # Companies
    companies = load_csv("companies.csv", "companies")
    company_industries = load_csv("company_industries.csv", "companies")
    company_specialities = load_csv("company_specialities.csv", "companies")
    employee_counts = load_csv("employee_counts.csv", "companies")

    # Jobs
    benefits = load_csv("benefits.csv", "jobs")
    job_industries = load_csv("job_industries.csv", "jobs")
    job_skills = load_csv("job_skills.csv", "jobs")
    salaries = load_csv("salaries.csv", "jobs")

    # Mappings
    industries = load_csv("industries.csv", "mappings")
    skills = load_csv("skills.csv", "mappings")

    return {
        "postings": postings,
        "companies": companies,
        "company_industries": company_industries,
        "company_specialities": company_specialities,
        "employee_counts": employee_counts,
        "benefits": benefits,
        "job_industries": job_industries,
        "job_skills": job_skills,
        "salaries": salaries,
        "industries": industries,
        "skills": skills,
    }


if __name__ == "__main__":
    # Sanity prints so you can see what the script sees
    print("data_processor.py:", Path(__file__).resolve())
    print("RAW_DATA_DIR:", RAW_DATA_DIR)
    print("RAW contents:", _list_csvs(RAW_DATA_DIR))
    print("companies/:", _list_csvs(RAW_DATA_DIR / "companies"))
    print("jobs/:", _list_csvs(RAW_DATA_DIR / "jobs"))
    print("mappings/:", _list_csvs(RAW_DATA_DIR / "mappings"))

    data = load_all_raw_data()
    for name, df in data.items():
        print(f"{name:>22}: {df.shape}")
