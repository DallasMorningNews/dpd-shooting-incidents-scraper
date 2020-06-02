# DPD Shooting, Cutting and Dead Body incident bot

### Purpose
Checks DPD's Open Data Portal of active calls every five minutes and alerts the `#feed-dpd-incident-alerts` slack channel for when there are calls involving shootings, cuttings or dead bodies

### What's here
- `scraper.py`: Set of functions to complete the scrape.
- `service.py`: File run on AWS Lambda. Runs the daily update and uploads the resulting data file back to AWS S3.
- `zappa_settings.json`: Zappa configuration file containing project name, description runtime environment, and most importantly, schedule for the scraper to run.

------

## Developing locally

Download the repository and run `$ pipenv install --development`.

Copy the `.env-example` file and rename it `.env`. Add your own `AWS_ACCESS_KEY` and `AWS_SECRET_ACCESS_KEY`. For messaging to slack, you'll also need our `SLACK_TOKEN`.

------
## Editing the scraper

This project uses zappa to upload and schedule the scraper to our AWS Lambda. After making changes to the scraper, run `pipenv run zappa update` to push those changes to Lambda. Scheduling is handled via the `zappa-settings.json` file. The `events` key is an array of events objects. The `service.handler` opject has an `expression` key that can either take a schedule in cron format or a rate (`rate(12 hours)`).

------

## Running the scraper locally

To run the scraper locally, run the following command in the command line:

`$ pipenv run python service.py`
