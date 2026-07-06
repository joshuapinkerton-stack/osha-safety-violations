# osha-safety-violations

Apify actor that scrapes OSHA enforcement data from public establishment search and inspection pages. Returns structured contact and penalty records.

## Buyer personas

**B2B** — compliance teams, safety consultants, insurance underwriters, EHS platforms, legal-tech companies.

**B2C** — freelance safety auditors, journalists, civic-tech projects, newsletter authors wanting enforcement summaries.

## Example input

```json
{
  "startUrls": [{"url": "https://www.osha.gov/enforcement/establishment-search-results?state=TX"}],
  "maxRequestsPerCrawl": 200,
  "establishmentLinkSelector": "a[href*='/establishment/']",
  "inspectionLinkSelector": "a[href*='/inspection/']"
}
```

## Output fields

Each result includes EIN, company name, site address, city, state, zip, inspection ID, date, inspection type, severity, violations found, and total penalties.
