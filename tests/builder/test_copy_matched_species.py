import json
from pathlib import Path

import pytest

from dataset_builder.core.exceptions import FailedOperation  # type: ignore
from dataset_builder.builder.copy_matched_species import run_copy_matched_species  # type: ignore


def make_src(tmp_path: Path, structure: dict) -> Path:
    """
    Create a fake source directory tree under tmp_path/src based on:
        { class_name: { species_name: [filenames...] } }
    """
    src = tmp_path / "src"
    for cls, species_dict in structure.items():
        for sp, files in species_dict.items():
            d = src / cls / sp
            d.mkdir(parents=True, exist_ok=True)
            for fn in files:
                (d / fn).write_text(f"dummy {fn}")
    return src

def make_matched_json(tmp_path: Path, data: dict) -> Path:
    """
    Write the matched-species JSON file.
    """
    p = tmp_path / "matched.json"
    p.write_text(json.dumps(data))
    return p

def test_missing_json_file(tmp_path: Path):
    src = tmp_path / "src"
    src.mkdir()
    dst = tmp_path / "dst"
    dst.mkdir()
    missing = tmp_path / "nomatch.json"
    with pytest.raises(FailedOperation, match="JSON not found"):
        run_copy_matched_species(str(src), str(dst), str(missing), ["Aves"], verbose=True)

def test_invalid_json_format(tmp_path: Path, capsys):
    # write invalid JSON so read_species_from_json returns {}
    mj = tmp_path / "matched.json"
    mj.write_text('{"not a dict"}')
    src = tmp_path / "src"
    src.mkdir()
    dst = tmp_path / "dst"
    dst.mkdir()

    run_copy_matched_species(str(src), str(dst), str(mj), ["Aves"], verbose=True)
    output = capsys.readouterr()
    assert "Invalid JSON format" in str(output)


def test_invalid_species_dict_json(tmp_path: Path, capsys):
    # write invalid JSON so read_species_from_json returns {}
    mj = tmp_path / "matched.json"
    mj.write_text('{"not a dict": "this should be a list"}')
    src = tmp_path / "src"
    src.mkdir()
    dst = tmp_path / "dst"
    dst.mkdir()

    with pytest.raises(FailedOperation, match="Invalid matched species JSON format"):
        run_copy_matched_species(str(src), str(dst), str(mj), ["Aves"], verbose=True)

def test_copy_success_all_species(tmp_path: Path):
    # two species under Aves
    structure = {"Aves": {"sparrow": ["a.jpg"], "hawk": ["b.jpg"]}}
    src = make_src(tmp_path, structure)
    dst = tmp_path / "dst"
    dst.mkdir()
    mj = make_matched_json(tmp_path, {"Aves": ["sparrow", "hawk"]})

    # should complete without error
    run_copy_matched_species(str(src), str(dst), str(mj), ["Aves"], verbose=True)

    # both species directories and files must exist in dst
    for sp, fn in [("sparrow", "a.jpg"), ("hawk", "b.jpg")]:
        out_file = dst / "Aves" / sp / fn
        assert out_file.exists()
        assert out_file.read_text() == f"dummy {fn}"

def test_partial_copy_raises_and_logs_missing(tmp_path: Path, capsys):
    # only sparrow exists, hawk is missing
    structure = {"Aves": {"sparrow": ["a.jpg"]}}
    src = make_src(tmp_path, structure)
    dst = tmp_path / "dst"
    dst.mkdir()
    mj = make_matched_json(tmp_path, {"Aves": ["sparrow", "hawk"]})

    # expect failure because 1/2 copied
    with pytest.raises(FailedOperation, match="Failed to copy all matched species: 1/2 copied"):
        run_copy_matched_species(str(src), str(dst), str(mj), ["Aves"], verbose=False)

    # it should have logged a missing‐directory error for hawk
    captured = capsys.readouterr()
    assert "Missing source directory" in captured.out

def test_skip_non_target_class(tmp_path: Path):
    # src has Aves/sparrow and Insecta/ant
    structure = {"Aves": {"sparrow": ["a.jpg"]}, "Insecta": {"ant": ["c.jpg"]}}
    src = make_src(tmp_path, structure)
    dst = tmp_path / "dst"
    dst.mkdir()
    # matched includes both, but target_classes only Aves
    mj = make_matched_json(tmp_path, {"Aves": ["sparrow"], "Insecta": ["ant"]})

    # should copy only sparrow and ignore 'ant'
    run_copy_matched_species(str(src), str(dst), str(mj), ["Aves"], verbose=True)

    assert (dst / "Aves" / "sparrow" / "a.jpg").exists()
    assert not (dst / "Insecta").exists()

def test_overwrite_existing_files(tmp_path: Path, capsys):
    # setup src, dst already contains a file for sparrow
    structure = {"Aves": {"sparrow": ["a.jpg"]}}
    src = make_src(tmp_path, structure)
    dst = tmp_path / "dst" / "Aves" / "sparrow"
    dst.mkdir(parents=True)
    existing = dst / "a.jpg"
    existing.write_text("old")

    mj = make_matched_json(tmp_path, {"Aves": ["sparrow"]})

    with pytest.raises(FailedOperation, match="Failed to copy all matched species"):
        run_copy_matched_species(str(src), str(tmp_path/"dst"), str(mj), ["Aves"], verbose=True)
    out = capsys.readouterr().out
    # it should have logged a skip notice (File exists - skipping)
    assert "Skipping existing" in out

    # original file should remain unchanged
    assert existing.read_text() == "old"

