# Team assignments

Each member owns the files and folders listed here. Coordinate with the owner when a change crosses a boundary. Some files, including `compose.yaml`, `.env.example`, `docs/INTEGRATION.md` and `docs/DEMO.md`, are deliverables the named owner will add.

| Member | GitHub handle | Issue | Accountable paths | Reviewer |
| --- | --- | --- | --- | --- |
| 1. Team lead | [@DavidGirges1](https://github.com/DavidGirges1) | [#1](https://github.com/DavidGirges1/Big-Data-COVID-/issues/1) | `README.md`, `TEAM.md`, `docs/DATA_CONTRACT.md`, `docs/INTEGRATION.md`, `.github/pull_request_template.md`, `.gitignore` | Member 7 |
| 2. Data source and producer | To confirm | [#2](https://github.com/DavidGirges1/Big-Data-COVID-/issues/2) | `producer/`, `data/` | Member 4 |
| 3. Local infrastructure and Kafka | To confirm | [#3](https://github.com/DavidGirges1/Big-Data-COVID-/issues/3) | `compose.yaml`, `.env.example`, `infra/`, `docs/GETTING_STARTED.md` | Member 4 |
| 4. NiFi ETL | To confirm | [#4](https://github.com/DavidGirges1/Big-Data-COVID-/issues/4) | `nifi/` | Member 5 |
| 5. Spark Structured Streaming | To confirm | [#5](https://github.com/DavidGirges1/Big-Data-COVID-/issues/5) | `spark/` except `spark/sinks/` | Member 6 |
| 6. Database and Spark sink | To confirm | [#6](https://github.com/DavidGirges1/Big-Data-COVID-/issues/6) | `database/`, `spark/sinks/` | Member 5 |
| 7. Verification and demo | To confirm | [#7](https://github.com/DavidGirges1/Big-Data-COVID-/issues/7) | `tests/`, `docs/DEMO.md` | Member 1 |

The lead records each handle, invites teammates who need write access from **Settings → Collaborators**, and sets the issue assignees. Teammates accept the invitation before pushing their branch.

## First integration milestone

1. Members 1 and 2 agree on dataset requirements, and Members 2, 4, 5 and 6 confirm their input and output contracts.
2. Member 3 shares local broker connection details. Members 2, 4, 5 and 6 verify their components against the same fixtures while Member 7 prepares expected results.
3. The full team runs the four-report fixture and checks the results in PostgreSQL. Each person explains their component and the handoff in the demo.
