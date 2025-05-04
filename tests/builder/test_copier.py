import pytest
from pathlib import Path
import shutil

from dataset_builder.builder.walker import CopyTask  # type: ignore
from dataset_builder.builder.copier import copy_one_species_data, copy_all_species, CopyStatus  # type: ignore

# Helpers
def make_sample_src(tmp_path: Path):
    # creates src/Aves/sparrow with two files
    src = tmp_path / "Aves" / "sparrow"
    src.mkdir(parents=True)
    for fname in ["a.jpg", "b.png"]:
        (src / fname).write_text(f"data-{fname}")
    return src

def test_copy_one_success(tmp_path: Path, capsys):
    src_dir = make_sample_src(tmp_path)
    dst_dir = tmp_path / "out" / "Aves" / "sparrow"
    task: CopyTask = ("Aves", "sparrow", src_dir, dst_dir)

    result = copy_one_species_data(task, verbose=True)
    assert result is CopyStatus.COPIED

    # files should be copied
    for fname in ["a.jpg", "b.png"]:
        file_path = dst_dir / fname
        assert file_path.exists()
        assert file_path.read_text() == f"data-{fname}"

    # check console logs
    out = capsys.readouterr().out
    assert "[INFO] Copied Aves/sparrow/a.jpg" in out
    assert "[INFO] Copied Aves/sparrow/b.png" in out

def test_copy_one_missing_src(tmp_path: Path, capsys):
    # src_dir does not exist
    src_dir = tmp_path / "Aves" / "sparrow"
    dst_dir = tmp_path / "out" / "Aves" / "sparrow"
    task: CopyTask = ("Aves", "sparrow", src_dir, dst_dir)

    result = copy_one_species_data(task, verbose=False)
    assert result is CopyStatus.MISSING

    # missing directory is always logged as ERROR
    out = capsys.readouterr().out
    assert "[ERROR] Missing source directory:" in out

def test_copy_all_mixed(tmp_path: Path, capsys):
    # --- prepare source files ---
    valid_src = tmp_path / "src" / "Aves" / "sparrow"
    valid_src.mkdir(parents=True)
    (valid_src / "a.jpg").write_text("data-a")

    # --- skip source files ---
    skip_src = tmp_path / "src" / "Aves" / "peacock"
    skip_dst = tmp_path / "dst" / "Aves" / "peacock"
    skip_src.mkdir(parents=True)
    skip_dst.mkdir(parents=True)
    (skip_src / "a.jpg").write_text("data-a")
    (skip_dst / "a.jpg").write_text("data-a")

    # --- pre-create one dest file so it gets skipped ---
    existing_dst = tmp_path / "dst" / "Aves" / "sparrow" / "b.jpg"
    existing_dst.parent.mkdir(parents=True)
    existing_dst.write_text("old-data")

    # define tasks
    valid_task: CopyTask = (
        "Aves",
        "sparrow",
        valid_src,
        tmp_path / "dst" / "Aves" / "sparrow"
    )
    skip_task: CopyTask = (
        "Aves",
        "peacock",
        skip_src,
        tmp_path / "dst" / "Aves" / "peacock"
    )
    missing_task: CopyTask = (
        "Insecta",
        "ant",
        tmp_path / "src" / "Insecta" / "ant",    # doesn’t exist
        tmp_path / "dst" / "Insecta" / "ant"
    )

    # run
    copied, skipped, missing = copy_all_species(
        iter([valid_task, skip_task, missing_task]),
        verbose=True
    )

    # expectations:
    #  - a.jpg gets copied   → copied == 1
    #  - b.jpg already there → skipped == 1
    #  - "ant" folder missing → missing == 1
    assert copied  == 1
    assert skipped == 1
    assert missing == 1

    out = capsys.readouterr().out
    assert "[INFO] Copied Aves/sparrow/a.jpg" in out
    assert "[INFO] Skipping existing Aves/peacock/a.jpg" in out
    assert "[ERROR] Missing source directory:" in out