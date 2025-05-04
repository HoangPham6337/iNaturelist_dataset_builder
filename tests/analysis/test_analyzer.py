import pytest
from dataset_builder.analysis.analyzer import run_analyze_dataset  # type: ignore
from dataset_builder.core.utility import read_species_from_json, write_data_to_json  # type: ignore


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
def populated_dir(tmp_path) -> str:
    class_a = tmp_path / "class_a"
    class_a.mkdir()
    (class_a / "sp1").mkdir()
    (class_a / "sp2").mkdir()
    (class_a / "sp1" / "img1.jpg").write_text("dummy")
    (class_a / "sp1" / "img2.jpg").write_text("dummy")
    (class_a / "sp2" / "img3.jpg").write_text("dummy")
    return str(tmp_path)


def test_run_analyze_dataset_with_json(dummy_json_file, tmp_path):
    out_dir = tmp_path / "output"
    run_analyze_dataset(dummy_json_file, str(out_dir), "test", ["class_a"], verbose=False)
    assert (out_dir / "test_species.json").exists()


def test_run_analyze_dataset_with_dir(populated_dir, tmp_path):
    out_dir = tmp_path / "output"
    run_analyze_dataset(populated_dir, str(out_dir), "test", ["class_a"], verbose=True)
    species_out = read_species_from_json(out_dir / "test_species.json")
    composition = read_species_from_json(out_dir / "test_composition.json")
    assert "class_a" in species_out
    assert "class_a" in composition


def test_run_analyze_dataset_verbose(dummy_json_file, tmp_path, capsys):
    out_dir = tmp_path / "output"
    run_analyze_dataset(dummy_json_file, str(out_dir), "test", ["class_a"], verbose=True)
    output = capsys.readouterr().out
    assert "class_a: 3 species" in output


def test_run_analyze_all_ready_exist(dummy_json_file, tmp_path, capsys):
    out_dir = tmp_path / "output"
    run_analyze_dataset(dummy_json_file, str(out_dir), "test", ["class_a"], verbose=False)
    run_analyze_dataset(dummy_json_file, str(out_dir), "test", ["class_a"], verbose=False)
    output = capsys.readouterr().out
    assert "already exists, skipping analyzing dataset." in output
