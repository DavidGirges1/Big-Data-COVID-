# Fixtures and verification

Member 7 owns this folder. Start with [synthetic raw reports](fixtures/covid-raw.jsonl) and [expected daily output](fixtures/expected-daily.csv). Empty CSV result cells represent SQL null. The first day establishes the baseline. On day two, Region A adds 20 confirmed cases and Region B adds 12. Use separate publish batches to make the streaming updates observable. Add acceptance cases and the end-to-end verification steps here.
