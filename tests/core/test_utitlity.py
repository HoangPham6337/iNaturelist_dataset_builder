import os
import json
import shutil
import pandas as pd
import pytest
from pathlib import Path
from typing import Tuple, List

from dataset_builder.core.utility import (  # type: ignore
    banner,
    _is_json_file,
    _is_a_valid_species_dict,
    save_manifest_parquet,
    load_manifest_parquet,
    write_data_to_json,
    read_species_from_json,
    _prepare_data_cdf_ppf,
    cleanup,
)


# test for banner()
def test_banner_output(capsys):
    banner("hello world")
    out, _ = capsys.readouterr()
    lines = out.splitlines()
    assert len(lines) == 3
    assert lines[0] == "#" * 60
    assert lines[1] == "HELLO WORLD"
    assert lines[2] == "#" * 60


def test_banner_return_value_is_none(capsys):
    result = banner("anything")
    assert result is None
    # verify it printed something
    out, _ = capsys.readouterr()
    assert out  # non-empty


def test_banner_empty_title(capsys):
    banner("")
    out, _ = capsys.readouterr()
    lines = out.splitlines()
    assert lines[0] == "#" * 60
    assert lines[1] == ""   # empty line for title
    assert lines[2] == "#" * 60
    # exactly three lines
    assert len(lines) == 3


def test_banner_special_characters(capsys):
    title = "!@#$%^&*()_+-=[]{}|;':,./<>?"
    banner(title)
    out, _ = capsys.readouterr()
    lines = out.splitlines()
    assert lines[1] == title.upper()
    assert lines[0] == "#" * 60
    assert lines[2] == "#" * 60


def test_banner_unicode_characters(capsys):
    title = "héllo wörld"
    banner(title)
    out, _ = capsys.readouterr()
    lines = out.splitlines()
    assert lines[1] == "HÉLLO WÖRLD"
    assert len(lines) == 3


def test_banner_multiline_title(capsys):
    title = "first line\nsecond line"
    banner(title)
    out, _ = capsys.readouterr()
    lines = out.splitlines()
    assert lines[0] == "#" * 60
    # The two title lines
    assert lines[1] == "FIRST LINE"
    assert lines[2] == "SECOND LINE"
    # Footer
    assert lines[3] == "#" * 60
    # Exactly 4 lines
    assert len(lines) == 4


# test for _is_json_file()
def test_is_json_file(tmp_path):
    valid = tmp_path / "data.JSON"
    invalid_ext = tmp_path / "data.txt"
    nonexist = tmp_path / "no.json"
    valid.write_text("{}")
    invalid_ext.write_text("{}")
    assert _is_json_file(str(valid)) is True
    assert _is_json_file(str(invalid_ext)) is False
    assert _is_json_file(str(nonexist)) is False


@pytest.mark.parametrize("filename, should_be_json", [
    (".json", True),                
    ("archive.json.zip", False),
    ("my.backup.JSON", True),
    ("CONFIG.Json", True),
    ("data.json/", False),
])
def test_is_json_file_various(tmp_path: Path, filename: str, should_be_json: bool):
    path = tmp_path / filename
    # if it ends with a slash we treat it as a directory; otherwise create a file
    if not filename.endswith("/"):
        path.write_text("{}")
    else:
        os.makedirs(str(path), exist_ok=True)

    result = _is_json_file(str(path))
    assert result is should_be_json

def test_is_json_file_directory_named_json(tmp_path: Path):
    dirpath = tmp_path / "foo.json"
    dirpath.mkdir()
    assert _is_json_file(str(dirpath)) is False

def test_is_json_file_relative_paths(tmp_path: Path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    (Path("rel.JSON")).write_text("{}")
    assert _is_json_file("rel.JSON") is True


# _is_a_valid_species_dict()
def test_is_species_dict_valid():
    d = {"Aves": ["sparrow", "falcon"], "Insecta": []}
    assert _is_a_valid_species_dict(d) is True


@pytest.mark.parametrize("obj, expected", [
    ({}, True),                                # empty dict is valid
    ({"Aves": []}, True),                      # empty list value
    ({"Aves": ["sparrow"]}, True),             # single-species list
    ({"A": [], "B": ["x", "y"]}, True),        # multiple keys
    ({"": []}, False),                         # empty-string key
    ({"A": ["", " "]}, False),                 # list of strings (even empty)
    ({"A": ["a", 1]}, False),                  # non-string element in list
    ({"A": None}, False),                      # value is None
    ({"A": "notalist"}, False),                # value not a list
    ({"A": [["nested"]]}, False),              # nested list instead of str
    ({1: ["a"]}, False),                       # non-str key
    ([], False),                               # list instead of dict
    (None, False),                             # None
    ("string", False),                         # string
    (42, False),                               # integer
    ({"A": [b"bytes"]}, False),                # bytes instead of str
])
def test_is_species_dict_various(obj, expected):
    assert _is_a_valid_species_dict(obj) is expected


# save_manifest_parquet & load_manifest_parquet
def test_parquet_roundtrip(tmp_path):
    manifest: List[Tuple[str,int]] = [
        ("/path/img1.jpg", 0),
        ("/path/img2.jpg", 1),
        ("/path/img3.jpg", 0),
    ]
    out = tmp_path / "m.parquet"
    save_manifest_parquet(manifest, str(out))
    loaded = load_manifest_parquet(str(out))
    assert loaded == manifest


def test_save_and_load_empty_manifest(tmp_path):
    manifest = []
    out = tmp_path / "empty.parquet"
    save_manifest_parquet(manifest, str(out))
    loaded = load_manifest_parquet(str(out))
    assert loaded == manifest


def test_save_and_load_preserves_order_and_values(tmp_path):
    manifest = [
        ("img1.jpg", 0),
        ("img2.jpg", 1),
        ("img3.jpg", 0),
        ("img4.jpg", 2),
    ]
    out = tmp_path / "data.parquet"
    save_manifest_parquet(manifest, str(out))
    df = pd.read_parquet(str(out))
    assert list(df.columns) == ["image_path", "label_id"]
    assert df.shape[0] == len(manifest)
    loaded = load_manifest_parquet(str(out))
    assert loaded == manifest


def test_load_manifest_raises_on_missing_file(tmp_path: Path):
    missing = tmp_path / "no_such_file.parquet"
    with pytest.raises(FileNotFoundError):
        load_manifest_parquet(str(missing))


def test_save_manifest_raises_when_directory_missing(tmp_path: Path):
    manifest = [("img.jpg", 5)]
    nested = tmp_path / "nonexistent_dir" / "out.parquet"
    with pytest.raises(Exception):
        save_manifest_parquet(manifest, str(nested))


# write_data_to_json + read_species_from_json
def test_write_and_read_json(tmp_path, capsys):
    data = {"A": [1,2], "B": []}
    # write under nested dir
    out = tmp_path / "sub" / "f.json"
    write_data_to_json(str(out), "TestDump", data, verbose=True)

    # Captures the log print
    outp, _ = capsys.readouterr()
    assert "TestDump" in outp and str(out) in outp

    text = out.read_text(encoding="utf-8")
    loaded = json.loads(text)
    assert loaded == data

    result = read_species_from_json(str(out))
    cap, _ = capsys.readouterr()
    assert "Successfully loaded species data" in cap
    assert result == data

def test_read_species_from_json_errors(tmp_path, capsys):
    missing = tmp_path / "x.json"
    result = read_species_from_json(str(missing))
    assert result == {}
    # invalid JSON
    bad = tmp_path / "bad.json"
    bad.write_text("{not valid}")
    result2 = read_species_from_json(str(bad))
    assert result2 == {}
    out, _ = capsys.readouterr()
    assert "Invalid JSON format" in out or "Error reading" in out


# _prepare_data_cdf_ppf
def test_prepare_data_cdf_ppf_file_not_found(tmp_path, capsys):
    missing = tmp_path / "no.json"
    res = _prepare_data_cdf_ppf(str(missing), "Aves")
    assert res is None
    out, _ = capsys.readouterr()
    assert f"File not found: {missing}" in out

def test_prepare_data_cdf_ppf_invalid_json(tmp_path, capsys):
    f = tmp_path / "bad.json"
    f.write_text("{oops")
    res = _prepare_data_cdf_ppf(str(f), "Aves")
    assert res is None
    out, _ = capsys.readouterr()
    assert "Not a valid JSON file" in out

def test_prepare_data_cdf_ppf_missing_class(tmp_path, capsys):
    f = tmp_path / "data.json"
    # JSON without key
    json.dump({"Insecta": {"ant": 5}}, open(f, "w"))
    res = _prepare_data_cdf_ppf(str(f), "Aves")
    assert res is None
    out, _ = capsys.readouterr()
    assert "ERROR: Class 'Aves' not found" in out

def test_prepare_data_cdf_ppf_valid(tmp_path):
    f = tmp_path / "data.json"
    # two species with counts
    species_data = {"Aves": {"sparrow": 2, "hawk": 5, "crow": 3}}
    f.write_text(json.dumps(species_data))
    names, counts = _prepare_data_cdf_ppf(str(f), "Aves")
    # sorted descending: hawk(5), crow(3), sparrow(2)
    assert names == ["hawk", "crow", "sparrow"]
    assert counts == [5, 3, 2]


# cleanup()

def test_cleanup_calls_rmtree(monkeypatch):
    calls = []
    # stub out rmtree
    monkeypatch.setattr(shutil, "rmtree", lambda path: calls.append(path))
    # pass two keyword args
    cleanup(one="/tmp/x", two="/tmp/y")
    # because code iterates keys, not values:
    assert calls == ["one", "two"]