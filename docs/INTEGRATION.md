# Integration runbook

## Course scope and current milestone

The course requires a producer → Kafka → NiFi → Kafka → Spark Streaming → database pipeline. We use PostgreSQL. The first milestone uses synthetic reports and daily deltas with a hotspot ranking by reported new-case count. Confirmed, death, recovered, and active counts have a place in the schema. Their actual coverage depends on the selected source. Forecasting is outside the first milestone.

Before the final demo, record instructor guidance on historical replay, forecasting, and required field coverage here. Member 2 proposes the source in [data/README.md](../data/README.md) after checking actual rows. The team lead approves it after verifying the intended date range, geographic coverage, and missing-field limitations. The synthetic fixture can be used now.

## Start the pipeline

Use local, per-teammate services and work from the repo root. Review the [data contract](DATA_CONTRACT.md) and [tools setup](GETTING_STARTED.md).

| Order | Component | Action and observable result |
| --- | --- | --- |
| 1 | Infrastructure · #3 | After Compose is merged, copy `.env.example` to `.env`, then run `docker compose config --quiet`, `docker compose up -d`, and `docker compose ps`. Verify the broker and the three topics via [infra/](../infra/). |
| 2 | PostgreSQL · #6 | Apply the schema from [database/](../database/) and verify that `covid_daily_metrics` is queryable and empty for this run. |
| 3 | NiFi · #4 | Import and start the flow using [nifi/](../nifi/). Check its Kafka broker address and verify all required processors are running. |
| 4 | Spark · #5 and #6 | Start the streaming job using [spark/](../spark/) with its clean topic, dedicated checkpoint and PostgreSQL settings. Check that it is listening before publishing. |
| 5 | Producer · #2 | Use [producer/](../producer/) to publish the baseline fixture in two date batches. Confirm the first date reaches SQL before sending the second, then inspect the output below. |

Component owners will add their exact import, submit, publish and connection commands at those links. In the meantime, `python tests/check_fixtures.py` checks the fixture and its expected data independently.

## Verify the integration

```sql
SELECT region_id, report_date, new_confirmed, new_deaths, hotspot_rank
FROM covid_daily_metrics
WHERE report_date = DATE '2021-01-02'
ORDER BY hotspot_rank;
```

| Region | Report date | New confirmed | New deaths | Hotspot rank |
| --- | --- | ---: | ---: | ---: |
| A | 2021-01-02 | 20 | 1 | 1 |
| B | 2021-01-02 | 12 | 0 | 2 |

Day 1 has NULL daily deltas and ranks. Member 7 verifies the [baseline, edge and invalid scenarios](../tests/README.md) from a fresh checkout and attaches the commands, topic evidence, SQL output and retry observations to #7. The lead signs off in #1 after that run.

## Repeat without affecting other runs

Use your own Compose project name and isolated local volumes, or have the infrastructure owner provide a separate test environment when using shared services. Check host ports for conflicts before running two stacks. For a fresh scenario use an empty database, fresh Kafka topics, a clean NiFi consumer state, and a new Spark checkpoint in the isolated environment. For a restart test, keep the same state and checkpoint. Verify the intended project name before stopping it. Keep existing volumes for other runs intact.
