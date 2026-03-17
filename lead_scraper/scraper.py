from __future__ import annotations

import csv
import re
import time
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Iterable, Protocol
from urllib.parse import quote_plus, urljoin, urlparse

import requests
from bs4 import BeautifulSoup, Tag


EMAIL_PATTERN = re.compile(r"([A-Z0-9._%+-]+@[A-Z0-9.-]+\.[A-Z]{2,})", re.IGNORECASE)
CONTACT_PATHS = ("", "/contact", "/contact-us", "/about", "/about-us")
DEFAULT_HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
        "AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0 Safari/537.36"
    )
}


@dataclass
class SearchRequest:
    query: str
    location: str
    pages: int = 1


@dataclass
class BusinessLead:
    business_name: str
    email: str
    phone: str
    website: str
    directory_url: str
    source: str
    query: str
    location: str


class LeadSource(Protocol):
    name: str

    def fetch_leads(self, request: SearchRequest) -> list[BusinessLead]:
        ...


def clean_text(value: str | None) -> str:
    if not value:
        return ""
    return " ".join(value.split()).strip()


def normalize_website(url: str | None) -> str:
    if not url:
        return ""

    parsed = urlparse(url)
    if parsed.scheme:
        return url
    return f"https://{url.lstrip('/')}"


def extract_first_email_from_html(html: str) -> str:
    matches = EMAIL_PATTERN.findall(html)
    return matches[0] if matches else ""


def export_to_csv(leads: Iterable[BusinessLead], output_path: str) -> None:
    fieldnames = [
        "business_name",
        "email",
        "phone",
        "website",
        "directory_url",
        "source",
        "query",
        "location",
    ]
    with open(output_path, "w", newline="", encoding="utf-8") as csv_file:
        writer = csv.DictWriter(csv_file, fieldnames=fieldnames)
        writer.writeheader()
        for lead in leads:
            writer.writerow(asdict(lead))


class LeadEnricher:
    def __init__(self, delay_seconds: float = 1.0, timeout: int = 15) -> None:
        self.delay_seconds = delay_seconds
        self.timeout = timeout
        self.session = requests.Session()
        self.session.headers.update(DEFAULT_HEADERS)

    def enrich(self, leads: Iterable[BusinessLead], include_email: bool = True) -> list[BusinessLead]:
        enriched: list[BusinessLead] = []
        for lead in leads:
            email = lead.email
            if include_email and not email and lead.website:
                email = self.find_email_on_website(lead.website)

            enriched.append(
                BusinessLead(
                    business_name=lead.business_name,
                    email=email,
                    phone=lead.phone,
                    website=lead.website,
                    directory_url=lead.directory_url,
                    source=lead.source,
                    query=lead.query,
                    location=lead.location,
                )
            )
        return dedupe_leads(enriched)

    def find_email_on_website(self, website: str) -> str:
        normalized = normalize_website(website)
        if not normalized:
            return ""

        parsed = urlparse(normalized)
        base = f"{parsed.scheme}://{parsed.netloc}"

        for path in CONTACT_PATHS:
            url = base if not path else urljoin(base, path)
            try:
                response = self.session.get(url, timeout=self.timeout)
                response.raise_for_status()
            except requests.RequestException:
                continue

            email = extract_first_email_from_html(response.text)
            if email:
                return email

            time.sleep(min(self.delay_seconds, 0.5))

        return ""


def dedupe_leads(leads: Iterable[BusinessLead]) -> list[BusinessLead]:
    deduped: list[BusinessLead] = []
    seen_keys: set[str] = set()

    for lead in leads:
        key = lead.website or lead.directory_url or f"{lead.business_name}:{lead.phone}"
        if key in seen_keys:
            continue
        seen_keys.add(key)
        deduped.append(lead)

    return deduped


class YellowPagesSource:
    name = "yellowpages"

    def __init__(self, delay_seconds: float = 1.0, timeout: int = 15) -> None:
        self.delay_seconds = delay_seconds
        self.timeout = timeout
        self.session = requests.Session()
        self.session.headers.update(DEFAULT_HEADERS)

    def fetch_leads(self, request: SearchRequest) -> list[BusinessLead]:
        leads: list[BusinessLead] = []

        for page in range(1, request.pages + 1):
            search_url = self.build_search_url(query=request.query, location=request.location, page=page)
            response = self.session.get(search_url, timeout=self.timeout)
            response.raise_for_status()
            leads.extend(
                self.parse_search_results(
                    html=response.text,
                    base_url=response.url,
                    query=request.query,
                    location=request.location,
                )
            )
            time.sleep(self.delay_seconds)

        return dedupe_leads(leads)

    @staticmethod
    def build_search_url(query: str, location: str, page: int) -> str:
        return (
            "https://www.yellowpages.com/search?"
            f"search_terms={quote_plus(query)}&geo_location_terms={quote_plus(location)}&page={page}"
        )

    def parse_search_results(
        self,
        html: str,
        base_url: str,
        query: str,
        location: str,
    ) -> list[BusinessLead]:
        soup = BeautifulSoup(html, "html.parser")
        cards = soup.select(".result, .organic, .result-row")
        leads: list[BusinessLead] = []

        for card in cards:
            name = clean_text(self._first_text(card, ["a.business-name", ".business-name", "h2 a"]))
            phone = clean_text(self._first_text(card, [".phones", ".phone", "[itemprop='telephone']"]))
            website = self._website_from_card(card, base_url)
            directory_url = self._directory_url_from_card(card, base_url)

            if not name:
                continue

            leads.append(
                BusinessLead(
                    business_name=name,
                    email="",
                    phone=phone,
                    website=website,
                    directory_url=directory_url,
                    source=self.name,
                    query=query,
                    location=location,
                )
            )

        return leads

    @staticmethod
    def _first_text(card: Tag, selectors: list[str]) -> str:
        for selector in selectors:
            node = card.select_one(selector)
            if node and node.get_text(strip=True):
                return node.get_text(" ", strip=True)
        return ""

    @staticmethod
    def _directory_url_from_card(card: Tag, base_url: str) -> str:
        business_link = card.select_one("a.business-name, h2 a, a.track-visit-website")
        if not business_link:
            return base_url
        href = business_link.get("href", "").strip()
        return urljoin(base_url, href) if href else base_url

    @staticmethod
    def _website_from_card(card: Tag, base_url: str) -> str:
        website_link = card.select_one("a.track-visit-website, a.website-link, .links a")
        if not website_link:
            return ""

        href = website_link.get("href", "").strip()
        if not href:
            return ""

        if "adredir?" in href and "url=" in href:
            match = re.search(r"[?&]url=([^&]+)", href)
            if match:
                return requests.utils.unquote(match.group(1))

        absolute = urljoin(base_url, href)
        return normalize_website(absolute if absolute.startswith("http") else href)


class HtmlFixtureSource:
    name = "html"

    def __init__(self, html_path: str) -> None:
        self.html_path = Path(html_path)
        self.parser = YellowPagesSource(delay_seconds=0)

    def fetch_leads(self, request: SearchRequest) -> list[BusinessLead]:
        html = self.html_path.read_text(encoding="utf-8")
        base_url = "https://www.yellowpages.com"
        return self.parser.parse_search_results(
            html=html,
            base_url=base_url,
            query=request.query,
            location=request.location,
        )


class LeadScraperService:
    def __init__(self, source: LeadSource, enricher: LeadEnricher | None = None) -> None:
        self.source = source
        self.enricher = enricher or LeadEnricher()

    def run(self, request: SearchRequest, include_email: bool = True) -> list[BusinessLead]:
        leads = self.source.fetch_leads(request)
        return self.enricher.enrich(leads, include_email=include_email)
