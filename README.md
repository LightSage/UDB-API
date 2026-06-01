# UDB-API

An API that wraps the [Universal DB](https://db.universal-team.net/) json file, built with FastAPI! 💪

You can find the public API at https://udb-api.lightsage.dev/ with documentation located at https://udb-api.lightsage.dev/docs/


### General self-hosting tips

- You'll want to run the fetch script with cron or whatever system you prefer. `python3 fetch/main.py`

#### Performance

- Install `uvloop` if you're on a UNIX-based system
