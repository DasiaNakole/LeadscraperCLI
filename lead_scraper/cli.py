from __future__ import annotations

import argparse
import sys

from lead_scraper.scraper import (
    HtmlFixtureSource,
    LeadEnricher,
    LeadScraperService,
    SearchRequest,
    YellowPagesSource,
    export_to_csv,
)


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Scrape public business directory results and export leads to CSV."
    )
    parser.add_argument("--query", required=True, help="Search query, e.g. 'plumbers'")
    parser.add_argument("--location", required=True, help="Location, e.g. 'Chicago, IL'")
    parser.add_argument("--pages", type=int, default=1, help="Number of result pages to scrape")
    parser.add_argument("--output", default="leads.csv", help="CSV file path")
    parser.add_argument("--delay", type=float, default=1.0, help="Delay in seconds between requests")
    parser.add_argument(
        "--source",
        choices=["yellowpages", "html"],
        default="yellowpages",
        help="Lead source adapter to use",
    )
    parser.add_argument(
        "--input-html",
        help="Local HTML file to parse when --source html is selected",
    )
    parser.add_argument(
        "--skip-email-enrichment",
        action="store_true",
        help="Skip visiting business websites to look for emails",
    )
    return parser


def build_service(args: argparse.Namespace) -> LeadScraperService:
    if args.source == "html":
        if not args.input_html:
            raise ValueError("--input-html is required when --source html is selected")
        source = HtmlFixtureSource(args.input_html)
    else:
        source = YellowPagesSource(delay_seconds=args.delay)

    enricher = LeadEnricher(delay_seconds=args.delay)
    return LeadScraperService(source=source, enricher=enricher)


def main() -> int:
    parser = build_parser()
    args = parser.parse_args()

    if args.pages < 1:
        parser.error("--pages must be at least 1")

    request = SearchRequest(query=args.query, location=args.location, pages=args.pages)

    try:
        service = build_service(args)
        leads = service.run(request, include_email=not args.skip_email_enrichment)
        export_to_csv(leads, args.output)
    except Exception as exc:  # pragma: no cover - CLI safety net
        print(f"Error: {exc}", file=sys.stderr)
        return 1

    print(f"Saved {len(leads)} leads to {args.output} using source '{args.source}'")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
