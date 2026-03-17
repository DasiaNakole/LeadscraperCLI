import csv
import os
import tempfile
import unittest

from lead_scraper.scraper import (
    BusinessLead,
    HtmlFixtureSource,
    LeadEnricher,
    LeadScraperService,
    SearchRequest,
    YellowPagesSource,
    dedupe_leads,
    export_to_csv,
    extract_first_email_from_html,
)


SAMPLE_RESULTS_HTML = """
<html>
  <body>
    <div class="result">
      <a class="business-name" href="/chicago-il/mip/acme-roofing-123">Acme Roofing</a>
      <div class="phones">(312) 555-0101</div>
      <a class="track-visit-website" href="https://acmeroofing.example.com">Website</a>
    </div>
    <div class="result">
      <a class="business-name" href="/chicago-il/mip/lakefront-plumbing-456">Lakefront Plumbing</a>
      <div class="phones">(773) 555-0199</div>
      <a class="track-visit-website" href="/adredir?url=https%3A%2F%2Flakefrontplumbing.example.com">Website</a>
    </div>
  </body>
</html>
"""


class StubEnricher(LeadEnricher):
    def enrich(self, leads, include_email=True):  # type: ignore[override]
        results = []
        for lead in leads:
            results.append(
                BusinessLead(
                    business_name=lead.business_name,
                    email="owner@example.com" if include_email else "",
                    phone=lead.phone,
                    website=lead.website,
                    directory_url=lead.directory_url,
                    source=lead.source,
                    query=lead.query,
                    location=lead.location,
                )
            )
        return results


class LeadScraperTests(unittest.TestCase):
    def test_parse_search_results_extracts_business_rows(self) -> None:
        source = YellowPagesSource(delay_seconds=0)
        leads = source.parse_search_results(
            SAMPLE_RESULTS_HTML,
            "https://www.yellowpages.com",
            query="roofers",
            location="Chicago, IL",
        )

        self.assertEqual(len(leads), 2)
        self.assertEqual(leads[0].business_name, "Acme Roofing")
        self.assertEqual(leads[0].phone, "(312) 555-0101")
        self.assertEqual(leads[0].website, "https://acmeroofing.example.com")
        self.assertTrue(leads[0].directory_url.endswith("/chicago-il/mip/acme-roofing-123"))
        self.assertEqual(leads[0].source, "yellowpages")
        self.assertEqual(leads[0].query, "roofers")

    def test_extract_first_email_from_html_finds_email(self) -> None:
        html = "<p>Email us at hello@example.com for a quote.</p>"
        self.assertEqual(extract_first_email_from_html(html), "hello@example.com")

    def test_export_to_csv_writes_expected_headers(self) -> None:
        leads = [
            BusinessLead(
                business_name="Acme Roofing",
                email="hello@acme.com",
                phone="(312) 555-0101",
                website="https://acme.example.com",
                directory_url="https://yellowpages.example.com/acme",
                source="yellowpages",
                query="roofers",
                location="Chicago, IL",
            )
        ]

        with tempfile.TemporaryDirectory() as tmpdir:
            output_path = os.path.join(tmpdir, "leads.csv")
            export_to_csv(leads, output_path)

            with open(output_path, newline="", encoding="utf-8") as csv_file:
                rows = list(csv.DictReader(csv_file))

        self.assertEqual(len(rows), 1)
        self.assertEqual(rows[0]["business_name"], "Acme Roofing")
        self.assertEqual(rows[0]["email"], "hello@acme.com")
        self.assertEqual(rows[0]["source"], "yellowpages")

    def test_dedupe_leads_prefers_unique_websites(self) -> None:
        leads = [
            BusinessLead("A", "", "1", "https://a.com", "dir-1", "yellowpages", "roofers", "Chicago, IL"),
            BusinessLead("A", "", "1", "https://a.com", "dir-2", "yellowpages", "roofers", "Chicago, IL"),
            BusinessLead("B", "", "2", "", "dir-3", "yellowpages", "roofers", "Chicago, IL"),
        ]

        deduped = dedupe_leads(leads)
        self.assertEqual(len(deduped), 2)

    def test_service_can_run_with_html_fixture_source(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            html_path = os.path.join(tmpdir, "results.html")
            with open(html_path, "w", encoding="utf-8") as html_file:
                html_file.write(SAMPLE_RESULTS_HTML)

            service = LeadScraperService(
                source=HtmlFixtureSource(html_path),
                enricher=StubEnricher(delay_seconds=0),
            )
            leads = service.run(
                SearchRequest(query="roofers", location="Chicago, IL"),
                include_email=True,
            )

        self.assertEqual(len(leads), 2)
        self.assertEqual(leads[0].email, "owner@example.com")


if __name__ == "__main__":
    unittest.main()
