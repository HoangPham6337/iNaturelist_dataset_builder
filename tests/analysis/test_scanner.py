import pytest
from dataset_builder.analysis.scanner import (  # type: ignore
    scan_species_list,
    filter_species_from_json,
    scan_image_counts,
)
from dataset_builder.core.utility import write_data_to_json  # type: ignore


@pytest.fixture
def dummy_json_file(tmp_path) -> str:
    path = tmp_path / "species.json"
    data = {
        "class_a": ["sp1", "sp2", "sp3"],
        "class_b": ["sp4", "sp5"],
    }
    write_data_to_json(path, "Species list", data)
    return str(path)


@pytest.fixture
def dummy_invalid_json_file(tmp_path) -> str:
    path = tmp_path / "species.json"
    data = {
        "class_a": ["sp1", "sp2", "sp3"],
        "class_b": 4,  # should be a list here
    }
    write_data_to_json(path, "Species list", data)
    return str(path)


@pytest.fixture
def populated_dir(tmp_path) -> str:
    class_a = tmp_path / "class_a"
    class_a.mkdir()
    (class_a / "sp1").mkdir()
    (class_a / "sp2").mkdir()
    (class_a / "sp1" / "img1.jpg").write_text("dummy")
    (class_a / "sp1" / "img2.jpg").write_text("dummy")
    (class_a / "sp2" / "img3.jpg").write_text("dummy")
    return str(tmp_path)


@pytest.fixture
def populated_dir_invalid(tmp_path) -> str:
    invalid = tmp_path / "species_lists"
    invalid.mkdir()
    class_a = tmp_path / "class_a"
    class_a.mkdir()
    (class_a / "sp1").mkdir()
    (class_a / "sp2").mkdir()
    (class_a / "sp1" / "img1.jpg").write_text("dummy")
    (class_a / "sp1" / "img2.jpg").write_text("dummy")
    (class_a / "sp2" / "img3.jpg").write_text("dummy")
    return str(tmp_path)


def test_scan_species_list(populated_dir):
    species_dict, total = scan_species_list(populated_dir)
    assert "class_a" in species_dict
    assert set(species_dict["class_a"]) == {"sp1", "sp2"}
    assert total == 2


def test_scan_species_list_invalid_folder(populated_dir_invalid):
    # Since there is an invalid folder, skip it
    species_dict, total = scan_species_list(populated_dir_invalid)
    assert set(species_dict["class_a"]) == {"sp1", "sp2"}
    assert total == 2

def test_scan_image_counts(populated_dir):
    counts = scan_image_counts(populated_dir)
    assert counts["class_a"]["sp1"] == 2
    assert counts["class_a"]["sp2"] == 1


def test_scan_image_counts_invalid_folder(populated_dir_invalid):
    # Since there is an invalid folder, skip it 
    counts = scan_image_counts(populated_dir_invalid)
    assert counts["class_a"]["sp1"] == 2
    assert counts["class_a"]["sp2"] == 1


def test_filter_species_from_json_valid(dummy_json_file):
    result = filter_species_from_json(dummy_json_file, ["class_a"])
    assert result == {"class_a": ["sp1", "sp2", "sp3"]}


def test_filter_species_from_json_invalid(dummy_invalid_json_file):
    with pytest.raises(ValueError, match="Invalid JSON structure"):
        filter_species_from_json(dummy_invalid_json_file, ["class_a"])


def test_filter_species_from_json_missing_file():
    with pytest.raises(FileNotFoundError):
        filter_species_from_json("missing.json", ["class_a"])


def test_filter_species_from_json_no_matching_class(dummy_json_file):
    with pytest.raises(ValueError):
        filter_species_from_json(dummy_json_file, ["class_x"])
