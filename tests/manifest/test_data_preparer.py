import pytest
from dataset_builder.manifest.data_preparer import collect_images_by_dominance  # type: ignore


@pytest.fixture
def setup_test_dirs(tmp_path):
    base = tmp_path / "dataset" / "class_a"
    base.mkdir(parents=True)

    # Create species folders
    dominant = base / "sp1"
    nondominant = base / "sp2"
    nondir_file = base / "README.txt"  # not a dir

    dominant.mkdir()
    nondominant.mkdir()
    nondir_file.write_text("I am not a directory")

    # Add dummy images
    for sp in [dominant, nondominant]:
        for i in range(2):
            (sp / f"img_{i}.jpg").write_text("")

    return str(base)


def test_collect_without_dominant_species(setup_test_dirs):
    image_list = []
    species_to_id, species_dict = {}, {}
    current_id = 0

    collect_images_by_dominance(
        dataset_path=setup_test_dirs,
        class_name="class_a",
        dominant_species=None,
        species_to_id=species_to_id,
        species_dict=species_dict,
        image_list=image_list,
        current_id=current_id,
    )

    # Should ignore README.txt and include both sp1, sp2
    assert len(image_list) == 4
    assert len(species_to_id) == 2
    assert len(species_dict) == 2


def test_collect_with_dominant_species(setup_test_dirs):
    image_list = []
    species_to_id, species_dict = {}, {}
    current_id = 0

    dominant_species = {"class_a": ["sp1"]}

    collect_images_by_dominance(
        dataset_path=setup_test_dirs,
        class_name="class_a",
        dominant_species=dominant_species,
        species_to_id=species_to_id,
        species_dict=species_dict,
        image_list=image_list,
        current_id=current_id,
    )

    # 2 from dominant sp1 + 2 from sp2 (as "Other")
    assert len(image_list) == 4
    assert "Other" in species_dict.values()
    assert species_dict[1] == "Other"  # assumes sp1 gets ID 0, other gets 1


def test_collect_all_non_dominant(setup_test_dirs):
    image_list = []
    species_to_id, species_dict = {}, {}
    current_id = 0

    dominant_species = {"class_a": []}

    collect_images_by_dominance(
        dataset_path=setup_test_dirs,
        class_name="class_a",
        dominant_species=dominant_species,
        species_to_id=species_to_id,
        species_dict=species_dict,
        image_list=image_list,
        current_id=current_id,
    )

    assert len(image_list) == 4  # both sp1 and sp2 fall into "Other"
    assert list(species_dict.values()) == ["Other"]