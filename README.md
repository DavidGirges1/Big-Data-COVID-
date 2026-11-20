# Real-time COVID-19 Data Processing and Analysis

Big Data course project 2. We use Kafka, Apache NiFi, Spark Structured Streaming, and PostgreSQL to turn incoming COVID-19 reports into daily trends and hotspot rankings.

**Start here:** [Install the tools](docs/GETTING_STARTED.md) · [Find your assignment](#team-roles) · [Read the data contract](docs/DATA_CONTRACT.md) · [Run the integration checklist](docs/INTEGRATION.md)

## What we are building

The producer sends reports to Kafka (`covid.raw`). NiFi validates and standardizes them and writes to Kafka (`covid.clean`). Spark reads the clean stream and calculates metrics. PostgreSQL stores the results for SQL queries. NiFi sends invalid records to `covid.invalid` for investigation.

Our first milestone is four sample reports (two regions, two dates) traveling through every stage. Then we connect the selected data source. Historical replay is pending course approval, and the production data source is pending the dataset owner's recommendation and team lead's sign-off. The checkout provides the collaboration structure and sample contract. The linked issues track implementation of the services.

## Team roles

| Member | Role | GitHub issue |
| --- | --- | --- |
| David E. Fam | Team lead | [#1](https://github.com/DavidGirges1/Big-Data-COVID-/issues/1) |
| Menna | Data source and producer | [#2](https://github.com/DavidGirges1/Big-Data-COVID-/issues/2) |
| Abdullah Mahmoud | Local infrastructure and Kafka | [#3](https://github.com/DavidGirges1/Big-Data-COVID-/issues/3) |
| Asmaa | NiFi ETL | [#4](https://github.com/DavidGirges1/Big-Data-COVID-/issues/4) |
| Ahmed Hameed ([@Ahmed-Hameed930](https://github.com/Ahmed-Hameed930)) | Spark Structured Streaming | [#5](https://github.com/DavidGirges1/Big-Data-COVID-/issues/5) |
| Heba | Database and Spark sink | [#6](https://github.com/DavidGirges1/Big-Data-COVID-/issues/6) |
| M7 -George | Verification and demo | [#7](https://github.com/DavidGirges1/Big-Data-COVID-/issues/7) |

See [TEAM.md](TEAM.md) for folder ownership and reviewers.

## Repository layout

| Path | What goes here |
| --- | --- |
| [`docs/`](docs/) | Tools, data contract, integration and demo notes |
| [`producer/`](producer/) and [`data/`](data/) | Kafka publisher, source selection and fetch instructions |
| [`infra/`](infra/) | Local services and Kafka setup notes |
| [`nifi/`](nifi/) | NiFi flow export and instructions |
| [`spark/`](spark/) | Spark Structured Streaming job and database sink |
| [`database/`](database/) | PostgreSQL schema and verification queries |
| [`tests/`](tests/) | Sample reports, expected outputs and verification |

## Start your first task

1. Install Git and follow the [tools guide](docs/GETTING_STARTED.md). Sign in to GitHub using the account the team leader invited, and accept the repository invitation for push access.
2. Open your issue from the [team roles table](#team-roles). Read the files you own, the handoff, and the definition of done. If you are blocked, comment on your issue with what you tried and the exact error or decision you need.
3. Open Command Prompt on Windows or Terminal on macOS/Linux in the parent folder where you want the project. A *clone* is your local copy of the repository.

   ```bash
   git clone https://github.com/DavidGirges1/Big-Data-COVID-.git
   cd Big-Data-COVID-
   git status
   ```

4. Create your own *branch*, a workspace where you can change files while the team keeps a shared copy on `main`. Use your issue number and a short description. Example for issue 4:

   ```bash
   git switch main
   git pull --ff-only origin main
   git switch -c task/4-nifi-etl
   ```

   Use the same branch for your later edits. Run `git status` to check where you are. Coordinate with the owner before changing files assigned to another member.

5. After editing, review the changes, stage the files you intend to share, save a *commit*, and *push* the branch to GitHub. This example assumes you changed `nifi/README.md`. Replace that path and the branch name with your own.

   ```bash
   git status
   git diff
   git add nifi/README.md
   git diff --staged
   git commit -m "Document the NiFi ETL setup"
   git push -u origin task/4-nifi-etl
   ```

6. On GitHub, click **Compare & pull request**, or go to **Pull requests → New pull request**. Choose `main` as the base and your branch as the compare branch. A *pull request* (PR) asks the team to review and merge your changes. Include `Closes #4` using your issue number, add the commands or evidence needed to verify your work, and request the reviewer named in your issue. The lead merges after review. Use `git push` for later commits on the same branch.
