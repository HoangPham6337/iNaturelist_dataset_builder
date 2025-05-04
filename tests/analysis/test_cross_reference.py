import pytest
from dataset_builder.core.utility import write_data_to_json, read_species_from_json  # type: ignore
from dataset_builder.analysis.cross_reference import run_cross_reference  # type: ignore
from dataset_builder.core.exceptions import FailedOperation  # type: ignore


@pytest.fixture
def dummy_json_file(tmp_path) -> str:
    path = tmp_path / "species.json"
    data = {
        "class_a": ["sp1", "sp2", "sp3"],
        "class_b": ["sp4", "sp5"],
    }
    write_data_to_json(path, "Species list", data)
    return str(path)


def test_run_cross_reference_success(tmp_path, dummy_json_file):
    # Create second matching JSON file
    second_json = tmp_path / "second.json"
    write_data_to_json(second_json, "Species list", {
        "class_a": ["sp1", "sp3"],
        "class_b": ["sp5", "sp6"],
    })

    output_file = tmp_path / "results.json"
    result, total = run_cross_reference(
        str(output_file), dummy_json_file, str(second_json),
        "dataset1", "dataset2", ["class_a", "class_b"], verbose=True
    )

    assert isinstance(result, dict)
    assert total == 3  # sp1, sp3, sp5 matched
    assert output_file.exists()

    loaded = read_species_from_json(output_file)
    assert loaded == result


def test_run_cross_reference_invalid_file(tmp_path):
    out_file = tmp_path / "result.json"
    with pytest.raises(FailedOperation):
        run_cross_reference(str(out_file), "invalid1.json", "invalid2.json", "d1", "d2", ["class_a"])


def test_run_cross_reference_empty_json(tmp_path):
    f1 = tmp_path / "file1.json"
    f2 = tmp_path / "file2.json"
    write_data_to_json(f1, "Species list", {})
    write_data_to_json(f2, "Species list", {})

    out = tmp_path / "output.json"
    with pytest.raises(FailedOperation):
        run_cross_reference(str(out), str(f1), str(f2), "a", "b", ["class_a"])


def test_run_cross_reference_overwrite_false_reads_existing(tmp_path, dummy_json_file):
    # Create second JSON
    second_json = tmp_path / "second.json"
    write_data_to_json(second_json, "Species list", {
        "class_a": ["sp1"],
        "class_b": ["sp5"],
    })

    # First call: generate and write result
    output_file = tmp_path / "out.json"
    original, total1 = run_cross_reference(
        str(output_file), dummy_json_file, str(second_json),
        "first", "second", ["class_a", "class_b"], overwrite=True
    )

    # Modify file to test that overwrite=False reuses file
    write_data_to_json(output_file, "Modified", {"class_x": ["dummy"]})

    reused, total2 = run_cross_reference(
        str(output_file), dummy_json_file, str(second_json),
        "first", "second", ["class_a", "class_b"], overwrite=False
    )

    assert reused == {"class_x": ["dummy"]}
    assert total2 == 1