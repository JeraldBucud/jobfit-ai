from __future__ import annotations

import os
from pathlib import Path
from typing import Dict, Iterable, List

import numpy as np
import pandas as pd

# Reuse paths + loaders from data_processor.py
from app.pipeline.data_processor import (
    PROCESSED_DIR,
    RAW_DATA_DIR,
    load_all_raw_data,
)


# ----------------------------
# Helpers
# ----------------------------
def _lc(df: pd.DataFrame) -> pd.DataFrame:
    """Lowercase/strip column names."""
    df = df.copy()
    df.columns = [c.strip().lower() for c in df.columns]
    return df


def _coalesce(
    df: pd.DataFrame, candidates: Iterable[str], new_name: str
) -> pd.DataFrame:
    """
    If any column in 'candidates' exists, create/rename it to 'new_name'.
    Leaves existing 'new_name' as-is.
    """
    df = df.copy()
    if new_name in df.columns:
        return df
    for c in candidates:
        if c in df.columns:
            df[new_name] = df[c]
            return df
    # If nothing matched, create empty
    df[new_name] = np.nan
    return df


def _ensure_int(df: pd.DataFrame, cols: Iterable[str]) -> pd.DataFrame:
    df = df.copy()
    for c in cols:
        if c in df.columns:
            df[c] = pd.to_numeric(df[c], errors="coerce").astype("Int64")
    return df


def _ensure_str(df: pd.DataFrame, cols: Iterable[str]) -> pd.DataFrame:
    df = df.copy()
    for c in cols:
        if c in df.columns:
            df[c] = df[c].astype("string")
    return df


def _agg_comma(values: Iterable[str]) -> str:
    uniq = sorted({v for v in values if isinstance(v, str) and v.strip()})
    return ", ".join(uniq)


# ----------------------------
# Load and normalize raw tables
# ----------------------------
def _load_normalized() -> Dict[str, pd.DataFrame]:
    t = {k: _lc(v) for k, v in load_all_raw_data().items()}

    # postings: job_id, company_id, title, description, location
    p = t["postings"]
    p = _coalesce(p, ["job_id", "id"], "job_id")
    p = _coalesce(p, ["company_id", "employer_id"], "company_id")
    p = _coalesce(p, ["title", "job_title"], "title")
    p = _coalesce(p, ["description", "job_description", "desc"], "description")
    # location can be a single field or multiple pieces
    if "location" not in p.columns:
        # try to build from city/country/region/state if present
        parts = [
            c
            for c in ["city", "state", "region", "country", "location_text"]
            if c in p.columns
        ]
        if parts:
            p["location"] = (
                p[parts]
                .astype("string")
                .fillna("")
                .apply(
                    lambda r: ", ".join([x for x in r.tolist() if x and x.strip()]),
                    axis=1,
                )
            )
        else:
            p["location"] = pd.NA
    p = _ensure_int(p, ["job_id", "company_id"])
    p = _ensure_str(p, ["title", "description", "location"])
    t["postings"] = p

    # companies: company_id, company (name), maybe location
    c = t["companies"]
    c = _coalesce(c, ["company_id", "id"], "company_id")
    c = _coalesce(c, ["company", "name"], "company")
    if "location" not in c.columns:
        parts = [
            x
            for x in ["hq_city", "hq_state", "hq_country", "location"]
            if x in c.columns
        ]
        if parts:
            c["location"] = (
                c[parts]
                .astype("string")
                .fillna("")
                .apply(
                    lambda r: ", ".join([x for x in r.tolist() if x and x.strip()]),
                    axis=1,
                )
            )
        else:
            c["location"] = pd.NA
    c = _ensure_int(c, ["company_id"])
    c = _ensure_str(c, ["company", "location"])
    t["companies"] = c

    # job_skills: job_id, skill_id
    js = t["job_skills"]
    js = _coalesce(js, ["job_id"], "job_id")
    js = _coalesce(js, ["skill_id", "skills_id", "id_skill"], "skill_id")
    js = _ensure_int(js, ["job_id", "skill_id"])
    t["job_skills"] = js

    # skills: skill_id, skill (name)
    sk = t["skills"]
    sk = _coalesce(sk, ["skill_id", "id"], "skill_id")
    sk = _coalesce(sk, ["skill", "name", "skill_name"], "skill")
    sk = _ensure_int(sk, ["skill_id"])
    sk = _ensure_str(sk, ["skill"])
    t["skills"] = sk

    # job_industries: job_id, industry_id
    ji = t["job_industries"]
    ji = _coalesce(ji, ["job_id"], "job_id")
    ji = _coalesce(ji, ["industry_id", "id_industry"], "industry_id")
    ji = _ensure_int(ji, ["job_id", "industry_id"])
    t["job_industries"] = ji

    # industries: industry_id, industry (name)
    ind = t["industries"]
    ind = _coalesce(ind, ["industry_id", "id"], "industry_id")
    ind = _coalesce(ind, ["industry", "name", "industry_name"], "industry")
    ind = _ensure_int(ind, ["industry_id"])
    ind = _ensure_str(ind, ["industry"])
    t["industries"] = ind

    # salaries: by job_id
    sal = t["salaries"]
    sal = _coalesce(sal, ["job_id"], "job_id")
    # try to build a readable salary text
    possible_amt = [
        c
        for c in [
            "salary",
            "amount",
            "pay",
            "annual_salary",
            "min_salary",
            "max_salary",
        ]
        if c in sal.columns
    ]
    if possible_amt:

        def _fmt(row):
            vals = []
            if "min_salary" in sal.columns and not pd.isna(row.get("min_salary")):
                vals.append(str(row["min_salary"]))
            if "max_salary" in sal.columns and not pd.isna(row.get("max_salary")):
                vals.append(str(row["max_salary"]))
            if vals:
                s = "-".join(vals)
            elif "salary" in sal.columns and not pd.isna(row.get("salary")):
                s = str(row["salary"])
            elif "amount" in sal.columns and not pd.isna(row.get("amount")):
                s = str(row["amount"])
            else:
                s = pd.NA
            cur = row.get("currency") if "currency" in sal.columns else None
            return f"{s} {cur}".strip() if cur and s is not pd.NA else s

        sal["salary"] = sal.apply(_fmt, axis=1)
    else:
        sal["salary"] = pd.NA
    sal = sal[["job_id", "salary"]].copy()
    sal = _ensure_int(sal, ["job_id"])
    sal = _ensure_str(sal, ["salary"])
    t["salaries"] = sal

    return t


# ----------------------------
# Build processed dataset
# ----------------------------
def build_processed_dataset(
    outfile_csv: Path | None = None, outfile_parquet: Path | None = None
) -> pd.DataFrame:
    t = _load_normalized()

    postings = t["postings"]
    companies = t["companies"]
    job_skills = t["job_skills"]
    skills = t["skills"]
    job_industries = t["job_industries"]
    industries = t["industries"]
    salaries = t["salaries"]

    # SKILLS per job_id
    js_join = job_skills.merge(skills, on="skill_id", how="left")
    skills_agg = (
        js_join.groupby("job_id")["skill"]
        .apply(_agg_comma)
        .reset_index()
        .rename(columns={"skill": "skills"})
    )

    # INDUSTRY per job_id (if multiple, comma-join)
    ji_join = job_industries.merge(industries, on="industry_id", how="left")
    industry_agg = (
        ji_join.groupby("job_id")["industry"]
        .apply(_agg_comma)
        .reset_index()
        .rename(columns={"industry": "industry"})
    )

    # COMPANY fields
    base = postings.merge(
        companies[["company_id", "company", "location"]].rename(
            columns={"location": "company_location"}
        ),
        on="company_id",
        how="left",
    )

    # Prefer posting location, else fallback to company location
    if "location" not in base.columns:
        base["location"] = base["company_location"]
    else:
        base["location"] = base["location"].fillna(base["company_location"])

    # JOIN skills, industry, salaries
    base = base.merge(skills_agg, on="job_id", how="left")
    base = base.merge(industry_agg, on="job_id", how="left")
    base = base.merge(salaries, on="job_id", how="left")

    # Select final schema
    final = base[
        [
            "job_id",
            "title",
            "company",
            "location",
            "description",
            "skills",
            "industry",
            "salary",
        ]
    ].copy()

    # Fill empties with empty strings for text columns
    for col in [
        "title",
        "company",
        "location",
        "description",
        "skills",
        "industry",
        "salary",
    ]:
        if col in final.columns:
            final[col] = final[col].fillna("")

    # Output
    if outfile_csv is None:
        outfile_csv = PROCESSED_DIR / "jobs_processed.csv"
    if outfile_parquet is None:
        outfile_parquet = PROCESSED_DIR / "jobs_processed.parquet"

    PROCESSED_DIR.mkdir(parents=True, exist_ok=True)
    final.to_csv(outfile_csv, index=False, encoding="utf-8")
    try:
        final.to_parquet(outfile_parquet, index=False)
    except Exception:
        # Parquet optional; skip if pyarrow/fastparquet not installed
        pass

    return final


# ----------------------------
# CLI
# ----------------------------
if __name__ == "__main__":
    print("RAW_DATA_DIR:", RAW_DATA_DIR)
    print("PROCESSED_DIR:", PROCESSED_DIR)
    df = build_processed_dataset()
    print("Processed rows:", len(df))
    print("Wrote:", PROCESSED_DIR / "jobs_processed.csv")
