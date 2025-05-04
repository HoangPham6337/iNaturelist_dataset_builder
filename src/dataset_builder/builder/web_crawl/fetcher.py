import requests
from requests import Response
from dataset_builder.core.exceptions import FailedOperation


def fetch_page(url: str) -> str:
    """
    Return HTML text or raise FailedOperation.
    """
    try:
        r: Response = requests.get(url)
        r.raise_for_status()
        return r.text
    except requests.RequestException as e:
        raise FailedOperation(f"HTTP error fetching {url}: {e}")