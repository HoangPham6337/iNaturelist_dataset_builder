import json
import re
import requests
import pytest

import dataset_builder.builder.web_crawl.web_crawler as wc  # type: ignore
from dataset_builder.core.exceptions import FailedOperation  # type: ignore
from dataset_builder.builder.web_crawl.scraper import parse_species_page


# --- Helpers ---
class DummyResponse:
    def __init__(self, text: str, status_code: int = 200):
        self.text = text
        self.status_code = status_code

    def raise_for_status(self):
        if not (200 <= self.status_code < 300):
            raise requests.RequestException(f"Status code {self.status_code}")

# --- Integration tests for run_web_crawl ---

def test_run_web_crawl_end_to_end(tmp_path, monkeypatch):
    """
    Ensure that run_web_crawl fetches multiple pages, parses them, aggregates species,
    and writes the combined JSON file.
    """
    # Stub requests.get to return a different HTML per page number
    def fake_get(url, *args, **kwargs):
        page_num = int(re.search(r'page=(\d+)', url).group(1))
        html = f"""
        <h2 class="title">
          <div class="othernames"><span class="sciname">Class{page_num}</span></div>
        </h2>
        <ul class="listed_taxa">
          <li class="clear"><span class="sciname">Spec{page_num}A</span></li>
          <li class="clear"><span class="sciname">Spec{page_num}B</span></li>
        </ul>
        """
        return DummyResponse(html)
    monkeypatch.setattr(requests, "get", fake_get)

    out_file = tmp_path / "out.json"
    wc.run_web_crawl(
        base_url="http://fake?page=",
        output_path=str(out_file),
        total_pages=2,
        delay=0.5,
        overwrite=True,
        verbose=False
    )

    # Verify file written
    assert out_file.exists()
    data = json.loads(out_file.read_text())
    # Should aggregate exactly the two pages
    assert data == {
        "Class1": ["Spec1A", "Spec1B"],
        "Class2": ["Spec2A", "Spec2B"]
    }

def test_skip_on_existing_file(tmp_path, monkeypatch, capsys):
    """
    If the output JSON already exists and overwrite=False,
    run_web_crawl should skip and print a skip message.
    """
    out_file = tmp_path / "out.json"
    # Pre-create the JSON
    out_file.write_text('{"X":[]}')

    wc.run_web_crawl(
        base_url="unused",
        output_path=str(out_file),
        total_pages=1,
        delay=0,
        overwrite=False,
        verbose=False
    )

    captured = capsys.readouterr().out
    assert f"{out_file} already exists, skipping web crawl." in captured


def test_unexpected_error_raises(tmp_path, monkeypatch):
    """
    If an unexpected exception occurs during scraping, it should be wrapped
    in FailedOperation.
    """
    def _fake_validate_web_crawl_rules(*args, **kwargs):
        raise RuntimeError("boom")
    monkeypatch.setattr(wc, "_validate_web_crawl_rules", _fake_validate_web_crawl_rules)

    out_file = tmp_path / "out.json"
    with pytest.raises(FailedOperation, match="Unexpected error during web crawl: boom"):
        wc.run_web_crawl(
            base_url="https://unused.com",
            output_path=str(out_file),
            total_pages=1,
            delay=0.5,
            overwrite=True,
            verbose=False
        )


def test_request_exception_raise(tmp_path):
    out_file = tmp_path / "out.json"
    with pytest.raises(FailedOperation, match="HTTP error fetching"):
        wc.run_web_crawl(
            base_url="https://unused.com",
            output_path=str(out_file),
            total_pages=1,
            delay=0.5,
            overwrite=True,
            verbose=False
        )


@pytest.mark.parametrize("base_url, total_pages, delay, msg", [
    ("unused.com", 1, 0.1, "'base_url' should be a valid URL"),
    ("https://unused.com", -1, 0.1, "'total_pages' should be a positive integer"),
    ("https://unused.com", 1, -0.1, "'delay_between_requests' should be a positive number")
])
def test_validate_web_crawl_rules(tmp_path, base_url, total_pages, delay, msg):
    out_file = tmp_path / "out.json"
    with pytest.raises(FailedOperation, match=msg):
        wc.run_web_crawl(
            base_url=base_url,
            output_path=str(out_file),
            total_pages=total_pages,
            delay=delay,
            overwrite=True,
            verbose=False
        )


def test_continue_when_class_tag_missing():
    html = """
    <html><body>
        <h2 class="title"><div class="othernames"><span class="wrongtag">Aves</span></div></h2>
        <ul class="listed_taxa"><li class="clear"><span class="sciname">Sparrow</span></li></ul>
    </body></html>
    """
    result = parse_species_page(html, verbose=False)
    assert result == {}


def test_continue_when_species_list_missing():
    html = """
    <html><body>
        <h2 class="title"><div class="othernames"><span class="sciname">Aves</span></div></h2>
        <div class="not_ul_class"></div>
    </body></html>
    """
    result = parse_species_page(html, verbose=False)
    assert result == {}


def test_verbose_prints_summary(capsys):
    html = """
    <html><body>
        <h2 class="title"><div class="othernames"><span class="sciname">Aves</span></div></h2>
        <ul class="listed_taxa">
            <li class="clear"><span class="sciname">Sparrow</span></li>
            <li class="clear"><span class="sciname">Hawk</span></li>
        </ul>
    </body></html>
    """
    result = parse_species_page(html, verbose=True)
    captured = capsys.readouterr().out
    assert "Extracted 2 species across 1 classes: ['Aves']" in captured
    assert result == {"Aves": ["Sparrow", "Hawk"]}