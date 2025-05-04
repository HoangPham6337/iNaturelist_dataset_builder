import pytest
from pathlib import Path
import shutil

from dataset_builder.builder.walker import CopyTask
from dataset_builder.builder.copier import copy_one_species_data, copy_all_species

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
    assert result is True

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
    assert result is False

    # missing directory is always logged as ERROR
    out = capsys.readouterr().out
    assert "[ERROR] Missing source directory:" in out

def test_copy_all_mixed(tmp_path: Path, capsys):
    # valid task
    valid_src = tmp_path / "src" / "Aves" / "sparrow"
    valid_src.mkdir(parents=True)
    (valid_src / "a.jpg").write_text("x")
    valid_task: CopyTask = ("Aves", "sparrow", valid_src, tmp_path / "dst" / "Aves" / "sparrow")

    # missing task
    missing_src = tmp_path / "src" / "Insecta" / "ant"
    missing_task: CopyTask = ("Insecta", "ant", missing_src, tmp_path / "dst" / "Insecta" / "ant")

    copied, total = copy_all_species(iter([valid_task, missing_task]), verbose=True)
    assert total == 2
    assert copied == 1

    out = capsys.readouterr().out
    assert "[INFO] Copied Aves/sparrow/a.jpg" in out
    assert "[ERROR] Missing source directory:" in out