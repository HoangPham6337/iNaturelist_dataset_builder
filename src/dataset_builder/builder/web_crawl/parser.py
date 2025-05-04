from bs4 import BeautifulSoup, Tag
from typing import Optional
from dataset_builder.core.utility import SpeciesDict


def parse_species_page(html: str, verbose: bool = True) -> SpeciesDict:
    """
    Parse one page's HTML and return a SpeciesDict.
    """
    soup = BeautifulSoup(html, "html.parser")
    out: SpeciesDict = {}
    for section in soup.select("h2.title"):
        class_tag: Optional[Tag] = section.select_one(".othernames .sciname")
        if not class_tag:
            continue

        class_name: str = class_tag.text.strip()
        species_list = section.find_next_sibling("ul", class_="listed_taxa")

        if not isinstance(species_list, Tag):
            continue

        out.setdefault(class_name, [])
        for species in species_list.select("li.clear"):
            scientific_tag: Optional[Tag] = species.select_one(".sciname")

            if scientific_tag:
                scientific_name = scientific_tag.text.strip()
                out[class_name].append(scientific_name)
    if verbose:
        print(f"Extracted {sum(len(v) for v in out.values())} species across {len(out)} classes: {list(out.keys())}")
    return out