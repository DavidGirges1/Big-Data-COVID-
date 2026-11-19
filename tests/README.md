# Fixtures and verification

Member 7 owns pipeline verification. Use these synthetic reports to test without downloading the course dataset. Each input line is a Kafka message value. An empty expected CSV cell means SQL NULL. A numeric zero is a real count.

| Scenario | Raw values | Expected PostgreSQL rows |
| --- | --- | --- |
| Baseline | [Four reports](fixtures/covid-raw.jsonl) | [Four rows](fixtures/expected-daily.csv) |
| Edge cases | [Nine deliveries](fixtures/covid-edge-raw.jsonl) | [Eight rows](fixtures/expected-edge-daily.csv) |
| Invalid reports | [Three raw payloads](fixtures/covid-invalid.txt) | Three rejects on `covid.invalid`, zero clean records for these inputs |

Run the fixture-only check with Python 3.9+ and no dependencies:

```bash
python tests/check_fixtures.py
```

Use a fresh demo run for each scenario as described in the [integration runbook](../docs/INTEGRATION.md). For the edge case, wait for SQL to reflect line 4 before proceeding. B starts at rank 1. Line 5 repeats the same event and should leave the rows unchanged. After line 6, A takes rank 1 and B moves to rank 2. Line 7 gives C the same delta as B, so C ranks third by the region-ID tiebreaker. Line 8 is a downward correction for A. Line 9 gives B a Jan 4 report without a Jan 3 baseline.

Send invalid payloads directly to Kafka, one line per message as plain text. A producer that parses JSON locally may reject malformed text before NiFi sees it. Assert each message preserves its original raw text and carries a non-empty rejection reason.
