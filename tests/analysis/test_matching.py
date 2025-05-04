from typing import Dict, List

import pytest

from dataset_builder.analysis.matching import (  # type: ignore
    _aggregate_all_species,
    _match_and_diff_sets,
    cross_reference_set,
)


@pytest.fixture
def dummy_species_dict() -> Dict[str, List[str]]:
    return {"class_a": ["sp1", "sp2"], "class_b": ["sp3"]}

def test_aggregate_all_species(dummy_species_dict):
    species = _aggregate_all_species(dummy_species_dict, ["class_a", "class_b"])
    assert species == {"sp1", "sp2", "sp3"}


def test_aggregate_all_species_without_specified(dummy_species_dict):
    species = _aggregate_all_species(dummy_species_dict)
    assert species == {"sp1", "sp2", "sp3"}


def test_aggregate_some_species(dummy_species_dict):
    species = _aggregate_all_species(dummy_species_dict, ["class_a"])
    assert species == {"sp1", "sp2"}


def test_aggregate_unknown_species(dummy_species_dict):
    species = _aggregate_all_species(dummy_species_dict, ["class_a", "class_c"])
    assert species == {"sp1", "sp2"}


def test_find_set_matches_differences():
    set1 = {"a", "b", "c"}
    set2 = {"b", "c", "d"}
    match, non_match = _match_and_diff_sets(set1, set2)
    assert match == {"b", "c"}
    assert non_match == {"a", "d"}


def test_cross_reference_set_full_match():
    d1 = {"class_a": ["sp1", "sp2"], "class_b": ["sp3"]}
    d2 = {"class_a": ["sp1", "sp2"], "class_b": ["sp3"]}
    matched, total, _ = cross_reference_set(d1, d2, ["class_a", "class_b"])
    assert total == 3
    assert matched == {"class_a": ["sp1", "sp2"], "class_b": ["sp3"]}


def test_cross_reference_set_partial_match():
    d1 = {"class_a": ["sp1", "sp2"], "class_b": ["sp3"]}
    d2 = {"class_a": ["sp2"], "class_b": ["spX"]}
    matched, total, _ = cross_reference_set(d1, d2, ["class_a", "class_b"])
    assert matched == {"class_a": ["sp2"], "class_b": []}
    assert total == 1


def test_cross_reference_set_unknown_class():
    d1 = {"class_a": ["sp1", "sp2"], "class_b": ["sp3"]}
    d2 = {"class_a": ["sp2"], "class_b": ["spX"]}
    # Just simply skip over them
    matched, total, _ = cross_reference_set(d1, d2, ["class_a", "class_b", "class_c"])
    assert matched == {"class_a": ["sp2"], "class_b": []}
    assert total == 1