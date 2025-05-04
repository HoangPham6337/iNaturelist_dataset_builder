import pytest
import json
from pathlib import Path
from dataset_builder.core.exceptions import FailedOperation  # type: ignore
from dataset_builder.builder.io import load_matched_species  # type: ignore


def test_load_matched_species_file_not_found(tmp_path: Path):
    missing = tmp_path / "no.json"
    with pytest.raises(FailedOperation, match="Matched species JSON not found"):
        load_matched_species(str(missing))


def test_load_matched_species_invalid_json(tmp_path: Path):
    path = tmp_path / "invalid.json"
    path.write_text('{"not-json": "should be a list"}')
    with pytest.raises(FailedOperation, match="Invalid matched species JSON format"):
        load_matched_species(str(path))


def test_load_matched_species_invalid_structure(tmp_path: Path):
    path = tmp_path / "struct.json"
    # structure with non-list or non-str in list
    bad = {"Aves": [1, 2], 3: ["a"]}
    path.write_text(json.dumps(bad))
    with pytest.raises(FailedOperation, match="Invalid matched species JSON format"):
        load_matched_species(str(path))


def test_load_matched_species_valid(tmp_path: Path):
    data = {"Aves": ["sparrow"], "Insecta": ["ant"]}
    path = tmp_path / "good.json"
    path.write_text(json.dumps(data))
    result = load_matched_species(str(path))
    assert result == data