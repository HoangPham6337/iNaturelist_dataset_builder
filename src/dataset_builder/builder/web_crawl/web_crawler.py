import re
from tqdm import tqdm  # type: ignore
from pathlib import Path
from collections import defaultdict
from typing import Dict, List

from dataset_builder.core.exceptions import FailedOperation
from dataset_builder.core.utility import write_data_to_json
from dataset_builder.builder.web_crawl.scraper import scrape_pages


def _validate_web_crawl_rules(base_url: str, total_pages: int, delay: float):
    """
    Enforce semantic rules on the 'web_crawl' section.

    Args:
        config (Dict): Full raw config dict.

    Raises:
        ConfigError: For invalid URL scheme, non-positive total_pages or delay.
    """

    if not re.match(r"^https?://", base_url):
        raise FailedOperation(
            "'base_url' should be a valid URL starting with http:// or https://"
        )
    if total_pages <= 0:
        raise FailedOperation("'total_pages' should be a positive integer")
    if delay <= 0:
        raise FailedOperation("'delay_between_requests' should be a positive number")


def run_web_crawl(
    base_url: str,
    output_path: str,
    delay: float = 1.0,
    total_pages: int = 1,
    overwrite: bool = False,
    verbose: bool = True,
):
    """
        Crawls iNaturelist site to scrape species data and saves the results to a JSON file.

    This function scrapes species data from multiple pages of a website,
    aggregates the data by taxonomic class, and saves it as a JSON file.
    If the output file already exists and `overwrite` is False, the crawl
    process will be skipped. Otherwise, the function will fetch the data
    and store it at the specified location.

    Args:
        base_url: The base URL of the website from which to scrape species data.
        output_path: The file path where the scraped species data will be saved as JSON.
        delay: The delay (in seconds) between requests to avoid overwhelming the server. Defaults to 1.
        total_pages : The number of pages to crawl. Defaults to 1.
        overwrite: Flag to indicate whether to overwrite the existing output file. Defaults to False.
        verbose: Whether to print detailed information during the web crawl process. Defaults to False.

    Raises:
        FailedOperation: If an unexpected error occurs during the web crawling process.
    """
    path = Path(output_path)
    if path.exists() and not overwrite:
        print(f"{str(path)} already exists, skipping web crawl.")
        return

    all_species: Dict[str, List[str]] = defaultdict(list)
    try:
        _validate_web_crawl_rules(base_url, total_pages, delay)
        pages = scrape_pages(base_url, total_pages, delay, verbose)
        page_iter = tqdm(
            pages,
            total=total_pages,
            desc="Scraping pages",
            unit="page",
            disable=verbose,
        )
        for page_data in page_iter:
            for species_class, species_list in page_data.items():
                all_species[species_class].extend(species_list)
        write_data_to_json(str(path), "Web crawl results", all_species)
    except Exception as e:
            raise FailedOperation(f"Unexpected error during web crawl: {e}")