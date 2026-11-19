# COVID-19 report contract

This is the initial interface for the fixture. The team lead and component owners can revise it after selecting the data source. Each record describes one region's reported totals for one calendar date. `report_date` is the source's report date. Kafka arrival time is useful for debugging ingestion.

| Topic | Producer | Consumer |
| --- | --- | --- |
| `covid.raw` | Dataset publisher | NiFi |
| `covid.clean` | NiFi | Spark |
| `covid.invalid` | NiFi | Verification or manual inspection |

## Raw and clean events

Raw sample from [covid-raw.jsonl](../tests/fixtures/covid-raw.jsonl):

```json
{"event_id":"fixture-a-2021-01-02","region":"A","date":"2021-01-02","confirmed":"120","deaths":"6","recovered":"70","active":""}
```

Expected clean event:

```json
{"event_id":"fixture-a-2021-01-02","region_id":"A","report_date":"2021-01-02","confirmed_total":120,"deaths_total":6,"recovered_total":70,"active_reported":null}
```

- The Kafka message key is the region identifier. Use one geography level and stable identifiers. Use a stable `event_id` for repeat delivery of the same report and a distinct ID for a revised report.
- Raw demo counts arrive as decimal strings. Map missing or blank optional counts to JSON null. Require `event_id`, `region_id`, a valid ISO calendar date in `YYYY-MM-DD` format, and a nonnegative signed 64-bit integer `confirmed_total`. Other count fields accept nonnegative signed 64-bit integers or JSON `null` when unavailable. Keep reported zero as zero.
- The rejected record contains the original raw payload and a rejection reason. Avoid copying malformed input into a clean event.
- Preserve `active_reported` as provided. If the team elects to calculate estimated active cases, use comparable same-date totals for confirmed, recovered and deaths and expose the estimate separately. Record source coverage and limitations.

## Result rows

Spark hands the following columns to the PostgreSQL sink. Use table `covid_daily_metrics` with primary key `(region_id, report_date)`. The sink upserts rows by that key so retries and rank changes replace an existing row.

| Column | PostgreSQL type | Nullable |
| --- | --- | --- |
| `region_id` | TEXT | No |
| `report_date` | DATE | No |
| `confirmed_total` | BIGINT | No |
| `deaths_total`, `recovered_total`, `active_reported` | BIGINT | Yes |
| `new_confirmed`, `new_deaths` | BIGINT | Yes |
| `hotspot_rank` | INTEGER | Yes |
| `confirmed_correction`, `deaths_correction` | BOOLEAN | No |

- Compute each daily delta from the prior **calendar day** for the same region. A missing date or missing required count yields a null delta. Set a correction flag to true only for a negative delta.
- Rank each date by nonnegative `new_confirmed`, highest first, with `region_id` ascending as the deterministic tiebreaker. Leave the rank null when the delta is missing or negative. This ranking measures reported case counts.
- The kickoff fixtures are ordered by report date. Different regions can arrive separately on the same date. Emit an update for each existing rank that changes. Repeated deliveries of the same event ID leave results unchanged.
- After selecting the source, agree how to handle older dates arriving out of order and distinct revisions for a region and date. A cumulative drop on a subsequent date in the fixture is a correction to the count trend.

See the [fixture inputs and expected rows](../tests/README.md) and [integration runbook](INTEGRATION.md).
