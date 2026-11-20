#!/usr/bin/env python3
"""Profile JHU CSSE daily reports over a reproducible date range.

Uses only the Python standard library. Downloaded source files are cached under
data/downloads/jhu_daily_reports; generated summaries are written under
data/profiling/. This script does not transform or publish Kafka messages.
"""
from __future__ import annotations

import argparse
import csv
import json
import sys
import time
from collections import Counter, defaultdict
from datetime import date, datetime, timedelta
from pathlib import Path
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen

REPOSITORY = "https://raw.githubusercontent.com/CSSEGISandData/COVID-19/master"
REPORT_PATH = "csse_covid_19_data/csse_covid_19_daily_reports"
METRICS = ("Confirmed", "Deaths", "Recovered", "Active")
MISSING_MARKERS = {"", "na", "n/a", "null", "none"}
COUNTRY_COLUMNS = ("Country_Region", "Country/Region")
PROVINCE_COLUMNS = ("Province_State", "Province/State")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Download and profile JHU CSSE daily COVID-19 reports."
    )
    parser.add_argument("--start", default="2021-01-22", help="First report date (YYYY-MM-DD).")
    parser.add_argument("--end", default="2021-06-30", help="Last report date, inclusive (YYYY-MM-DD).")
    parser.add_argument("--download-dir", default="data/downloads/jhu_daily_reports")
    parser.add_argument("--output-dir", default="data/profiling")
    parser.add_argument("--delay", type=float, default=0.15, help="Seconds between HTTP requests.")
    parser.add_argument("--retries", type=int, default=3)
    return parser.parse_args()


def parse_date(value: str) -> date:
    try:
        return datetime.strptime(value, "%Y-%m-%d").date()
    except ValueError as exc:
        raise argparse.ArgumentTypeError(f"Invalid date {value!r}; expected YYYY-MM-DD") from exc


def date_range(start: date, end: date):
    current = start
    while current <= end:
        yield current
        current += timedelta(days=1)


def report_filename(day: date) -> str:
    return day.strftime("%m-%d-%Y") + ".csv"


def fetch_report(day: date, download_dir: Path, retries: int, delay: float) -> tuple[Path | None, str | None]:
    filename = report_filename(day)
    destination = download_dir / filename
    if destination.exists() and destination.stat().st_size > 0:
        return destination, None

    url = f"{REPOSITORY}/{REPORT_PATH}/{filename}"
    last_error = None
    for attempt in range(1, retries + 1):
        try:
            request = Request(url, headers={"User-Agent": "covid-bigdata-course-project/1.0"})
            with urlopen(request, timeout=30) as response:
                payload = response.read()
            if not payload:
                raise ValueError("Downloaded an empty response")
            destination.write_bytes(payload)
            time.sleep(max(0.0, delay))
            return destination, None
        except (HTTPError, URLError, TimeoutError, ValueError, OSError) as exc:
            last_error = f"{type(exc).__name__}: {exc}"
            if attempt < retries:
                time.sleep(min(2 ** (attempt - 1), 5))
    return None, last_error or "Unknown download error"


def first_value(row: dict[str, str], names: tuple[str, ...]) -> str:
    for name in names:
        if name in row:
            return (row.get(name) or "").strip()
    return ""


def is_missing(value: str | None) -> bool:
    return value is None or value.strip().lower() in MISSING_MARKERS


def numeric_value(value: str | None) -> float | None:
    if is_missing(value):
        return None
    try:
        return float(value.replace(",", ""))
    except (AttributeError, ValueError):
        return None


def read_report(path: Path, report_day: date) -> tuple[list[dict[str, str]], list[str]]:
    with path.open("r", encoding="utf-8-sig", newline="") as handle:
        reader = csv.DictReader(handle)
        if not reader.fieldnames:
            raise ValueError(f"{path} has no CSV header")
        rows = []
        for raw in reader:
            country = first_value(raw, COUNTRY_COLUMNS)
            province = first_value(raw, PROVINCE_COLUMNS)
            admin2 = (raw.get("Admin2") or "").strip()
            combined = (raw.get("Combined_Key") or "").strip()
            rows.append({
                "report_date": report_day.isoformat(),
                "country": country,
                "province_state": province,
                "admin2": admin2,
                "combined_key": combined,
                **{metric.lower(): (raw.get(metric) or "").strip() for metric in METRICS},
            })
        return rows, list(reader.fieldnames)


def main() -> int:
    args = parse_args()
    start, end = parse_date(args.start), parse_date(args.end)
    if end < start:
        print("ERROR: --end must be on or after --start.", file=sys.stderr)
        return 2
    if args.retries < 1:
        print("ERROR: --retries must be at least 1.", file=sys.stderr)
        return 2

    download_dir = Path(args.download_dir)
    output_dir = Path(args.output_dir)
    download_dir.mkdir(parents=True, exist_ok=True)
    output_dir.mkdir(parents=True, exist_ok=True)

    expected_dates = [day for day in date_range(start, end)]
    available_dates: list[str] = []
    failed_dates: dict[str, str] = {}
    daily_rows: list[dict[str, str]] = []
    daily_summary: list[dict[str, object]] = []
    country_history: dict[str, list[tuple[str, float | None, float | None]]] = defaultdict(list)
    headers_by_date: dict[str, list[str]] = {}

    for index, day in enumerate(expected_dates, start=1):
        path, error = fetch_report(day, download_dir, args.retries, args.delay)
        day_text = day.isoformat()
        if path is None:
            failed_dates[day_text] = error or "Download failed"
            print(f"[{index}/{len(expected_dates)}] MISSING {day_text}: {failed_dates[day_text]}", file=sys.stderr)
            continue
        try:
            rows, headers = read_report(path, day)
        except (OSError, UnicodeError, csv.Error, ValueError) as exc:
            failed_dates[day_text] = f"Could not parse {path.name}: {exc}"
            print(f"[{index}/{len(expected_dates)}] INVALID {day_text}: {exc}", file=sys.stderr)
            continue

        available_dates.append(day_text)
        headers_by_date[day_text] = headers
        daily_rows.extend(rows)
        metric_missing = {
            metric.lower(): sum(is_missing(row[metric.lower()]) for row in rows)
            for metric in METRICS
        }
        country_rows = [
            row for row in rows
            if row["country"] and not row["province_state"] and not row["admin2"]
        ]
        country_names = sorted({row["country"] for row in country_rows})
        daily_summary.append({
            "date": day_text,
            "rows": len(rows),
            "country_level_rows": len(country_rows),
            "distinct_country_names_at_country_level": len(country_names),
            "missing": metric_missing,
        })
        for row in country_rows:
            country_history[row["country"]].append((
                day_text,
                numeric_value(row["confirmed"]),
                numeric_value(row["deaths"]),
            ))
        print(f"[{index}/{len(expected_dates)}] OK {day_text}: {len(rows)} rows")

    if not daily_rows:
        print("ERROR: No valid daily reports were downloaded or found in the cache.", file=sys.stderr)
        return 1

    total_missing = {
        metric.lower(): sum(is_missing(row[metric.lower()]) for row in daily_rows)
        for metric in METRICS
    }
    total_cells = len(daily_rows)
    negative_counts = {
        metric.lower(): sum(
            (numeric_value(row[metric.lower()]) is not None)
            and numeric_value(row[metric.lower()]) < 0
            for row in daily_rows
        )
        for metric in METRICS
    }
    country_only_names = sorted({
        row["country"] for row in daily_rows
        if row["country"] and not row["province_state"] and not row["admin2"]
    })
    province_only_names = sorted({
        row["country"] for row in daily_rows
        if row["country"] and (row["province_state"] or row["admin2"])
        and not any(
            other["country"] == row["country"]
            and not other["province_state"] and not other["admin2"]
            for other in daily_rows
        )
    })

    duplicate_geo_date = Counter(
        (row["country"], row["province_state"], row["admin2"], row["report_date"])
        for row in daily_rows
    )
    duplicate_count = sum(count - 1 for count in duplicate_geo_date.values() if count > 1)

    cumulative_checks = {}
    for country, points in sorted(country_history.items()):
        points.sort(key=lambda item: item[0])
        confirmed_decreases = 0
        deaths_decreases = 0
        comparable_pairs = 0
        for previous, current in zip(points, points[1:]):
            if previous[1] is not None and current[1] is not None:
                comparable_pairs += 1
                confirmed_decreases += current[1] < previous[1]
            if previous[2] is not None and current[2] is not None:
                deaths_decreases += current[2] < previous[2]
        cumulative_checks[country] = {
            "country_level_reports": len(points),
            "adjacent_report_pairs_with_confirmed_values": comparable_pairs,
            "confirmed_decreases_between_adjacent_available_reports": confirmed_decreases,
            "deaths_decreases_between_adjacent_available_reports": deaths_decreases,
        }

    summary = {
        "source": "Johns Hopkins CSSE COVID-19 Daily Reports",
        "source_repository": "https://github.com/CSSEGISandData/COVID-19",
        "source_report_directory": f"{REPOSITORY}/{REPORT_PATH}/",
        "requested_period": {"start": start.isoformat(), "end": end.isoformat()},
        "expected_report_days": len(expected_dates),
        "available_report_days": len(available_dates),
        "missing_or_invalid_report_days": failed_dates,
        "total_rows_across_reports": total_cells,
        "distinct_country_names_with_country_level_rows": len(country_only_names),
        "country_names_with_country_level_rows": country_only_names,
        "countries_seen_only_at_subnational_level_in_available_reports": province_only_names,
        "missing_values": {
            metric: {
                "count": count,
                "percentage_of_all_rows": round(100 * count / total_cells, 4),
            }
            for metric, count in total_missing.items()
        },
        "negative_numeric_values": negative_counts,
        "duplicate_geography_date_rows": duplicate_count,
        "daily_report_summary": daily_summary,
        "country_level_cumulative_trend_checks": cumulative_checks,
        "interpretation_notes": [
            "This script reports missingness as empty/NA/null text in the downloaded CSVs; it does not impute values.",
            "Country-level rows are identified by blank Province_State and Admin2. Some countries may only have subnational rows.",
            "Adjacent-report decreases are flagged for review; they can represent corrections and are not automatically treated as invalid.",
            "The trend check is evidence about cumulative semantics, not proof that every source field is a cumulative measure.",
            "The script does not calculate Active, aggregate provinces, or publish Kafka messages.",
        ],
        "headers_by_date": headers_by_date,
    }

    summary_path = output_dir / "jhu_profile_summary.json"
    daily_path = output_dir / "jhu_daily_coverage.csv"
    summary_path.write_text(json.dumps(summary, indent=2, ensure_ascii=False), encoding="utf-8")
    with daily_path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(
            handle,
            fieldnames=[
                "date", "rows", "country_level_rows",
                "distinct_country_names_at_country_level",
                "missing_confirmed", "missing_deaths",
                "missing_recovered", "missing_active",
            ],
        )
        writer.writeheader()
        for item in daily_summary:
            writer.writerow({
                "date": item["date"],
                "rows": item["rows"],
                "country_level_rows": item["country_level_rows"],
                "distinct_country_names_at_country_level": item["distinct_country_names_at_country_level"],
                **{f"missing_{metric}": item["missing"][metric] for metric in ("confirmed", "deaths", "recovered", "active")},
            })

    print("\nPROFILE COMPLETE")
    print(f"Available reports: {len(available_dates)}/{len(expected_dates)}")
    print(f"Rows: {total_cells}")
    print(f"Missing values: {json.dumps(total_missing)}")
    print(f"Summary: {summary_path}")
    print(f"Daily coverage: {daily_path}")
    if failed_dates:
        print(f"WARNING: {len(failed_dates)} dates could not be profiled; see summary JSON.", file=sys.stderr)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
