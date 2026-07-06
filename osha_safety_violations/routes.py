from __future__ import annotations

from apify import Actor
from crawlee.crawlers import Router
from crawlee._types import BasicCrawlingContext


router = Router[BasicCrawlingContext]()


@router.default()
async def listing_handler(context: BasicCrawlingContext) -> None:
    Actor.log.info(f"Listing: {context.request.url}")

    try:
        await Actor.charge("safety_snapshot", {"url": context.request.url})
    except RuntimeError as exc:
        Actor.log.warning(f"Charge skipped (non-billing run): {exc}")

    link_selector = context.request.user_data.get(
        "establishment_link_selector",
        "a[href*='/establishment/']",
    )
    async for _ in context.request.enqueue_links(
        selector=link_selector,
        label="detail",
        user_data={"url_type": "detail"},
    ):
        pass

    async for _ in context.request.enqueue_links(
        selector="a[rel='next'], .pagination-next, .next a",
        label="listing",
        user_data={"url_type": "listing"},
    ):
        pass


@router.handler("detail")
async def detail_handler(context: BasicCrawlingContext) -> None:
    Actor.log.info(f"Detail page: {context.request.url}")
    dom = context.request.loaded_dom

    def _text(selector: str) -> str | None:
        if dom is None:
            return None
        try:
            el = dom.select_one(selector)
            return el.get_text(strip=True) if el else None
        except Exception:
            return None

    company_name = _text("h1")
    ein = _text("dd:contains('EIN')")
    address_full = _text("dd:contains('Address'):last-of-type") or ""
    city = _text(".city, dd:contains('City')")
    state = _text(".state, dd:contains('State')")
    zip_code = _text(".zip, dd:contains('Zip')")
    date = _text(".date, .inspection-date, td:contains('Date') + td")
    inspection_type = _text(".inspection-type, td:contains('Type') + td")
    severity = _text(".severity, .hazard-category")

    violations_found = 0
    total_penalties = 0.0
    if dom is not None:
        try:
            rows = dom.select(".violation-row, .citation-row")
            violations_found = len(rows)
            amounts = []
            for row in rows:
                penalty_el = row.select_one(".penalty, td:contains('Penalty') + td, td:contains('$')")
                if penalty_el:
                    text = penalty_el.get_text(strip=True).replace("$", "").replace(",", "")
                    try:
                        amounts.append(float(text))
                    except ValueError:
                        pass
            total_penalties = sum(amounts)
        except Exception:
            violations_found = 0
            total_penalties = 0.0

    record = {
        "ein": ein,
        "companyName": company_name,
        "siteAddress": address_full or None,
        "city": city,
        "state": state,
        "zip": zip_code,
        "inspectionId": context.request.url.rstrip("/").split("/")[-1],
        "date": date,
        "inspectionType": inspection_type,
        "severity": severity,
        "violationsFound": violations_found,
        "totalPenalties": total_penalties,
    }

    payload = {"url": context.request.url, "record": record}
    await Actor.push_data(payload)

    try:
        await Actor.charge("violation_record", payload)
    except RuntimeError as exc:
        Actor.log.warning(f"Charge skipped (non-billing run): {exc}")
