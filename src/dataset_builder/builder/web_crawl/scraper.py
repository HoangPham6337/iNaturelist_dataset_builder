import time
from typing import Iterator
from dataset_builder.core.utility import SpeciesDict
from dataset_builder.builder.web_crawl.fetcher import fetch_page
from dataset_builder.builder.web_crawl.parser import parse_species_page


def scrape_pages(
    base_url: str,
    total_pages: int,
    delay: float = 1.0,
    verbose: bool = False
) -> Iterator[SpeciesDict]:
    """
    Yields the parsed species dict for each page number.
    """
    for page_num in range(1, total_pages + 1):
        html = fetch_page(f"{base_url}{page_num}&view=plain")
        yield parse_species_page(html, verbose)
        time.sleep(delay)