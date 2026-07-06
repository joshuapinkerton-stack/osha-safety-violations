import asyncio
from apify import Actor
from crawlee.crawlers import CheerioCrawler
from crawlee._types import BasicCrawlingContext

from osha_safety_violations.routes import router


async def main() -> None:
    async with Actor:
        actor_input = await Actor.get_input() or {}

        max_requests = int(actor_input.get("maxRequestsPerCrawl", 200))
        user_agent = actor_input.get(
            "userAgent",
            "Apify-osha-safety-violations/1.0 (+https://github.com/joshuapinkerton-stack/osha-safety-violations)",
        )

        crawler = CheerioCrawler(
            max_requests_per_crawl=max_requests,
            max_request_retries=4,
            request_handler=router,
            additional_http_error_status_codes=[429],
        )

        start_urls = actor_input.get("startUrls") or []
        if start_urls:
            initial_requests = [
                {
                    "url": item.get("url"),
                    "user_data": {"url_type": "listing"},
                }
                for item in start_urls
                if item.get("url")
            ]
        else:
            Actor.log.info("No startUrls provided; running with empty crawl.")
            initial_requests = []

        await crawler.run(initial_requests)
