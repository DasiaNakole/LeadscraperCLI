# Lead Scraper

A portfolio-ready lead generation tool for scraping public business directory results and exporting prospect lists to CSV.

This is the kind of lightweight automation businesses actually pay for:

- local service lead lists
- niche B2B prospect research
- directory-to-CRM enrichment
- quick outbound list building for agencies and freelancers

## Why This Is Marketable

Small businesses, recruiters, agencies, and SDR teams all want the same thing: a faster path to qualified leads.

This project shows that you can:

- turn public web data into structured business leads
- enrich listings by visiting business websites for contact emails
- clean, dedupe, and export records into client-friendly CSVs
- build a maintainable scraping workflow instead of a one-off script

If you are selling on Contra, this positions well as:

- "Lead List Builder"
- "Custom Business Directory Scraper"
- "Prospect Research Automation"
- "CSV Lead Generation Tool"

## Features

- Scrapes directory-style business listings
- Extracts `business_name`, `phone`, `website`, and `directory_url`
- Visits company websites to find contact emails
- Deduplicates leads before export
- Supports pluggable sources
- Includes an offline HTML fixture mode for demos and screen recordings
- Exports clean CSV output
- Ships with tests

## Tech Stack

- Python 3.10+
- `requests`
- `beautifulsoup4`
- CSV export with the Python standard library

## Project Structure

- [/Users/dasiamitchell/Desktop/ContraWork/lead_scraper/scraper.py](/Users/dasiamitchell/Desktop/ContraWork/lead_scraper/scraper.py): core models, sources, enrichment, CSV export
- [/Users/dasiamitchell/Desktop/ContraWork/lead_scraper/cli.py](/Users/dasiamitchell/Desktop/ContraWork/lead_scraper/cli.py): command-line interface
- [/Users/dasiamitchell/Desktop/ContraWork/fixtures/yellowpages_sample.html](/Users/dasiamitchell/Desktop/ContraWork/fixtures/yellowpages_sample.html): offline demo fixture
- [/Users/dasiamitchell/Desktop/ContraWork/tests/test_lead_scraper.py](/Users/dasiamitchell/Desktop/ContraWork/tests/test_lead_scraper.py): unit tests
- [/Users/dasiamitchell/Desktop/ContraWork/sample_leads.csv](/Users/dasiamitchell/Desktop/ContraWork/sample_leads.csv): sample output

## Quick Start

Create a virtual environment:

```bash
cd /Users/dasiamitchell/Desktop/ContraWork
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

## Demo Run

This mode is perfect for a portfolio video, Loom walkthrough, or client demo because it does not depend on a live site being available:

```bash
.venv/bin/python -m lead_scraper.cli \
  --source html \
  --input-html fixtures/yellowpages_sample.html \
  --query "roofing contractors" \
  --location "Chicago, IL" \
  --skip-email-enrichment \
  --output demo_leads.csv
```

## Live Run

```bash
.venv/bin/python -m lead_scraper.cli \
  --source yellowpages \
  --query "roofing contractors" \
  --location "Austin, TX" \
  --pages 2 \
  --output leads.csv
```

## CSV Output

The CSV includes:

- `business_name`
- `email`
- `phone`
- `website`
- `directory_url`
- `source`
- `query`
- `location`

## CLI Options

```bash
.venv/bin/python -m lead_scraper.cli --help
```

Useful options:

- `--source yellowpages`
- `--source html --input-html fixtures/yellowpages_sample.html`
- `--skip-email-enrichment`
- `--pages 3`
- `--output leads.csv`

## Productization Ideas

To turn this into an even stronger client offer, the next upgrades would be:

- add more directory adapters
- add proxy and retry support
- add browser automation for challenge-protected sites
- export directly to Airtable, HubSpot, or Google Sheets
- add email validation and lead scoring
- wrap the CLI in a tiny web dashboard

## Real-World Note

Some directories actively block non-browser traffic. During live verification on March 17, 2026, Yellow Pages returned HTTP `403` to a direct request in this environment. That is common in production scraping work and is exactly why the architecture here is split into reusable source adapters instead of hardcoding one fragile script.

## Tests

Run:

```bash
.venv/bin/python -m unittest discover -s tests -p "test_*.py"
```

## Contra Positioning

A clean service listing could be:

**Custom Lead Scraper for Local Businesses and B2B Prospecting**

Deliverables:

- CSV lead list
- source notes
- custom search criteria by niche and location
- optional website email enrichment
- optional recurring runs
