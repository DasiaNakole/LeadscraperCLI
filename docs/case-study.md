# Portfolio Case Study

## Title

Built a Custom Lead Scraper for Business Prospecting

## Summary

I built a Python-based lead scraping tool that collects public business listing data and exports it into a clean CSV for prospecting workflows.

The tool was designed as a reusable starting point for lead generation projects, especially for local business research, outbound list building, and niche B2B targeting.

## Problem

Many teams still build lead lists manually by searching directories, opening listings one by one, and copying details into spreadsheets.

That process is slow, repetitive, and difficult to scale.

## Solution

I created a command-line scraping workflow that:

- pulls structured business listings from directory-style pages
- extracts business name, phone, website, and listing URL
- visits business websites to look for contact emails
- deduplicates results
- exports the final dataset to CSV

I also structured the project so that different source adapters can be added later instead of locking the code to one brittle website.

## Tech Used

- Python
- Requests
- BeautifulSoup
- CSV export
- modular scraper architecture

## Outcome

The final result is a reusable lead-generation workflow that can be adapted for different niches, locations, and public sources.

It demonstrates both technical implementation and business usefulness, which makes it a strong portfolio piece for freelance automation and research work.

## Why It Matters

This project is a good example of the kind of work businesses actually hire for:

- lead generation
- market research
- repetitive workflow automation
- data cleanup and export

## Demo Angle

For demos and sales calls, the project includes a fixture-driven mode so the scraper can be shown working reliably even if a live source blocks bot traffic that day.

