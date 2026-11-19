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
- Require `event_id`, `region_id`, a valid ISO calendar date in `YYYY-MM-DD` format, and a nonnegative integer `confirmed_total`. Other count fields accept nonnegative integers or JSON `null` when unavailable. Keep reported zero as zero.
- The rejected record contains the original raw payload and a rejection reason. Avoid copying malformed input into a clean event.
- Preserve `active_reported` as provided. If the team elects to calculate estimated active cases, use comparable same-date totals for confirmed, recovered and deaths and expose the estimate separately. Record source coverage and limitations.

## Result rows

Use one PostgreSQL result row per `(region_id, report_date)`. The Spark and database owners agree on the final column types and checkpoint behavior before connecting the sink.

- Preserve reported totals and calculate `new_confirmed` and `new_deaths` by subtracting the prior calendar day's total for the same region. A missing prior day or required count produces a null delta.
- A lower cumulative total can reflect a reporting correction. Keep the signed delta, flag the corresponding metric as corrected (for example `confirmed_correction`), and leave negative confirmed changes out of the ranking.
- `hotspot_rank` is per report date, descending by nonnegative `new_confirmed` and then ascending by `region_id` for ties. Rows without an eligible delta have a null rank. It measures reported case volume.
- The fixture ships in date order, but regions can arrive separately. Later arrivals for the same date can change a previously emitted rank, so use updates keyed by region and date. Before using a real dataset, agree on and document how late or revised reports are handled. Ensure replays of an identical report leave results unchanged.

See [expected fixture rows](../tests/fixtures/expected-daily.csv).
