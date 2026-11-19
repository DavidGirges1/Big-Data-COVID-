"""Check synthetic fixture expectations without running the pipeline."""

import csv
from datetime import date, timedelta
import json
from pathlib import Path

FIXTURES = Path(__file__).with_name("fixtures")
COUNT_FIELDS = {
    "confirmed": "confirmed_total",
    "deaths": "deaths_total",
    "recovered": "recovered_total",
    "active": "active_reported",
}


def parse_report(payload):
    raw = json.loads(payload)
    day = date.fromisoformat(raw["date"])
    if day.isoformat() != raw["date"] or not raw["event_id"] or not raw["region"]:
        raise ValueError("Expected an ISO report date, event ID, and region")
    counts = {}
    for source, target in COUNT_FIELDS.items():
        value = raw.get(source)
        if value in ("", None) and source != "confirmed":
            counts[target] = None
            continue
        if not isinstance(value, str) or not value.isascii() or not value.isdecimal():
            raise ValueError(f"Invalid count: {source}")
        count = int(value)
        if count >= 2**63:
            raise ValueError(f"Count outside signed 64-bit range: {source}")
        counts[target] = count
    return raw["event_id"], raw["region"], day, counts


def expected_rows(payloads):
    reports = {}
    seen = {}
    for payload in payloads:
        event_id, region, day, counts = parse_report(payload)
        report = (region, day, counts)
        if event_id in seen:
            if seen[event_id] != report:
                raise ValueError(f"Inconsistent reuse of event ID: {event_id}")
            continue
        if (region, day) in reports:
            raise ValueError(f"Fixture contains a revision for {region} on {day}")
        seen[event_id] = report
        reports[region, day] = counts

    rows = []
    candidates = {}
    for (region, day), counts in sorted(reports.items(), key=lambda pair: (pair[0][1], pair[0][0])):
        previous = reports.get((region, day - timedelta(days=1)), {})
        row = dict(region_id=region, report_date=day.isoformat(), **counts)
        row["hotspot_rank"] = None
        for metric in ("confirmed", "deaths"):
            current = counts[f"{metric}_total"]
            baseline = previous.get(f"{metric}_total")
            delta = None if current is None or baseline is None else current - baseline
            row[f"new_{metric}"] = delta
            row[f"{metric}_correction"] = str(delta is not None and delta < 0).lower()
        if row["new_confirmed"] is not None and row["new_confirmed"] >= 0:
            candidates.setdefault(day, []).append(row)
        rows.append(row)

    for group in candidates.values():
        ranked = sorted(group, key=lambda row: (-row["new_confirmed"], row["region_id"]))
        for rank, row in enumerate(ranked, start=1):
            row["hotspot_rank"] = rank
    return [{key: "" if value is None else str(value) for key, value in row.items()} for row in rows]


def check_pair(raw_file, expected_file):
    payloads = (FIXTURES / raw_file).read_text(encoding="utf-8").splitlines()
    with (FIXTURES / expected_file).open(encoding="utf-8", newline="") as stream:
        expected = list(csv.DictReader(stream))
    actual = expected_rows(payloads)
    if actual != expected:
        raise SystemExit(f"{expected_file} mismatch\nExpected: {expected}\nComputed: {actual}")
    print(f"{raw_file}: {len(payloads)} deliveries, {len(actual)} result rows match")


def main():
    check_pair("covid-raw.jsonl", "expected-daily.csv")
    check_pair("covid-edge-raw.jsonl", "expected-edge-daily.csv")
    edge = (FIXTURES / "covid-edge-raw.jsonl").read_text(encoding="utf-8").splitlines()
    early = expected_rows(edge[:4])
    if early != expected_rows(edge[:5]) or early[-1]["hotspot_rank"] != "1":
        raise SystemExit("Duplicate delivery changed B's initial rank")
    next_day_two = [row for row in expected_rows(edge[:6]) if row["report_date"] == "2021-01-02"]
    if [(row["region_id"], row["hotspot_rank"]) for row in next_day_two] != [("A", "1"), ("B", "2")]:
        raise SystemExit("A's arrival did not move B to rank 2")
    print("Rank updates: duplicate delivery unchanged, later region updates B to rank 2")
    invalid = (FIXTURES / "covid-invalid.txt").read_text(encoding="utf-8").splitlines()
    if len(invalid) != 3:
        raise SystemExit("Expected 3 invalid payloads")
    for line_number, payload in enumerate(invalid, start=1):
        try:
            parse_report(payload)
        except (ValueError, KeyError, TypeError):
            continue
        raise SystemExit(f"Invalid payload {line_number} was accepted")
    print(f"covid-invalid.txt: {len(invalid)} invalid payloads rejected")


if __name__ == "__main__":
    main()
