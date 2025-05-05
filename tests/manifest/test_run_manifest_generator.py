import os
import json
import pytest
import tempfile
from typing import List, Tuple
from dataset_builder.core.exceptions import PipelineError  # type: ignore
from dataset_builder.manifest.manifest_builder import run_manifest_generator  # type: ignore


def _create_dummy_dataset_structure(base_dir: str) -> Tuple[str, List[str]]:
    """
    Create a simple dataset:
    class_a/
        sp1/
            img1.jpg
        sp2/
            img2.jpg
            img3.jpg
    class_b/
        sp3/
            img4.jpg
    """
    structure = {
        "class_a": {
            "sp1": ["img1.jpg", "img2.jpg", "img_3.jpg"],
            "sp2": ["img4.jpg", "img5.jpg"]
        },
        "class_b": {
            "sp3": ["img6.jpg", "img7.jpg", "img8.jpg", "img9.jpg"]
        }
    }

    for class_name, species_dict in structure.items():
        for species, images in species_dict.items():
            species_dir = os.path.join(base_dir, class_name, species)
            os.makedirs(species_dir, exist_ok=True)
            for img in images:
                open(os.path.join(species_dir, img), "a").close()  # create empty image file

    return base_dir, list(structure.keys())


def _create_dummy_dataset_properties(path: str):
    # Matching what _identifying_dominant_species expects
    data = {
        "class_a": ["sp1", "sp2"],
        "class_b": ["sp3"]
    }
    with open(path, "w") as f:
        json.dump(data, f)


def test_run_manifest_generator_basic_flow():
    with tempfile.TemporaryDirectory() as tmp_dir:
        data_dir = os.path.join(tmp_dir, "dataset")
        output_dir = os.path.join(tmp_dir, "output")
        os.makedirs(data_dir, exist_ok=True)

        _create_dummy_dataset_structure(data_dir)
        props_path = os.path.join(tmp_dir, "props.json")
        _create_dummy_dataset_properties(props_path)

        result = run_manifest_generator(
            data_dir=data_dir,
            output_dir=output_dir,
            dataset_properties_path=props_path,
            train_size=0.67,
            random_state=42,
            target_classes=["class_a", "class_b"],
            threshold=1.0,
            per_species_list=True,
            export=True,
        )

        image_list, train_data, val_data, species_dict, species_composition = result

        # Assertions
        assert len(image_list) == 9
        assert len(train_data) + len(val_data) == 9
        assert os.path.exists(os.path.join(output_dir, "dataset_manifest.parquet"))
        assert os.path.exists(os.path.join(output_dir, "train.parquet"))
        assert os.path.exists(os.path.join(output_dir, "val.parquet"))
        assert os.path.exists(os.path.join(output_dir, "species_composition.json"))
        assert os.path.exists(os.path.join(output_dir, "dataset_species_labels.json"))

        # Per-species lists created
        species_list_dir = os.path.join(output_dir, "species_lists")
        assert os.path.isdir(species_list_dir)
        species_folders = [f for root, dirs, files in os.walk(species_list_dir) for f in dirs]
        assert set(species_folders) >= {"sp1", "sp2", "sp3"}

        # check species_dict contents
        # assumes deterministic ordering (sorted by label index)
        expected_species_names = {"sp1", "sp2", "sp3"}
        actual_species_names = set(species_dict.values())
        assert expected_species_names == actual_species_names

        # check species_composition counts
        # sp1: 1 image, sp2: 2 images, sp3: 1 image
        expected_counts = {
            "sp1": 3,
            "sp2": 2,
            "sp3": 4
        }
        assert species_composition == expected_counts


def test_run_manifest_with_other_label():
    with tempfile.TemporaryDirectory() as tmp_dir:
        data_dir = os.path.join(tmp_dir, "dataset")
        output_dir = os.path.join(tmp_dir, "output")
        os.makedirs(data_dir, exist_ok=True)

        # Setup: 1 dominant, 1 non-dominant per class
        structure = {
            "class_a": {
                "sp1": [f"{i}.jpg" for i in range(0, 10)],
                "sp2": [f"{i}.jpg" for i in range(10, 15)]
            },
            "class_b": {
                "sp3": [f"{i}.jpg" for i in range(15, 25)],
                "sp4": [f"{i}.jpg" for i in range(25, 30)]
            }
        }
        for class_name, species_map in structure.items():
            for species, images in species_map.items():
                path = os.path.join(data_dir, class_name, species)
                os.makedirs(path)
                for name in images:
                    open(os.path.join(path, name), "a").close()

        # Properties file that allows selecting dominant species
        props_path = os.path.join(tmp_dir, "props.json")
        structure_dump = {
            "class_a": {"sp1": 10, "sp2": 5},
            "class_b": {"sp3": 10, "sp4": 5}
        }
        json.dump(structure_dump, open(props_path, "w"))

        result = run_manifest_generator(
            data_dir=data_dir,
            output_dir=output_dir,
            dataset_properties_path=props_path,
            train_size=0.7,
            random_state=0,
            target_classes=["class_a", "class_b"],
            threshold=0.84,
            per_species_list=True,
            export=True,
        )

        image_list, train_data, val_data, species_dict, species_composition = result

        # Validation
        assert len(image_list) == 30
        assert "Other" in species_dict.values()
        assert any(s.endswith("species_lists") for s in os.listdir(output_dir))
        assert os.path.exists(os.path.join(output_dir, "dataset_manifest.parquet"))


def test_run_manifest_stratify_fallback():
    with tempfile.TemporaryDirectory() as tmp_dir:
        data_dir = os.path.join(tmp_dir, "dataset")
        output_dir = os.path.join(tmp_dir, "output")
        os.makedirs(data_dir, exist_ok=True)

        structure = {
            "class_a": {
                "sp1": [f"{i}.jpg" for i in range(0, 10)],
                "sp2": [f"{i}.jpg" for i in range(10, 15)]
            },
            "class_b": {
                "sp3": [f"{i}.jpg" for i in range(15, 25)],
                "sp4": ["25.jpg"]
            }
        }
        for class_name, species_map in structure.items():
            for species, images in species_map.items():
                path = os.path.join(data_dir, class_name, species)
                os.makedirs(path)
                for name in images:
                    open(os.path.join(path, name), "a").close()

        props_path = os.path.join(tmp_dir, "props.json")
        structure_dump = {
            "class_a": {"sp1": 10, "sp2": 5},
            "class_b": {"sp3": 5, "sp4": 1}
        }
        json.dump(structure_dump, open(props_path, "w"))

        result = run_manifest_generator(
            data_dir=data_dir,
            output_dir=output_dir,
            dataset_properties_path=props_path,
            train_size=0.7,
            random_state=0,
            target_classes=["class_a", "class_b"],
            threshold=0.84,
            per_species_list=True,
            export=True,
        )

        image_list, train_data, val_data, species_dict, species_composition = result

        # Validation
        assert len(image_list) == 26
        assert len(image_list) == len(train_data) + len(val_data)
        assert "Other" in species_dict.values()
        assert any(s.endswith("species_lists") for s in os.listdir(output_dir))
        assert os.path.exists(os.path.join(output_dir, "dataset_manifest.parquet"))


def test_all_species_go_to_other():
    with tempfile.TemporaryDirectory() as tmp_dir:
        data_dir = os.path.join(tmp_dir, "dataset")
        output_dir = os.path.join(tmp_dir, "output")
        os.makedirs(data_dir)

        structure = {"class_a": {"sp1": ["1.jpg"], "sp2": ["2.jpg"]}}
        for cls, species_map in structure.items():
            for sp, imgs in species_map.items():
                sp_dir = os.path.join(data_dir, cls, sp)
                os.makedirs(sp_dir)
                for img in imgs:
                    open(os.path.join(sp_dir, img), "a").close()

        props_path = os.path.join(tmp_dir, "props.json")
        structure_dump = {"class_a": {"sp1": 1, "sp2": 1}}
        json.dump(structure_dump, open(props_path, "w"))

        with pytest.raises(PipelineError, match="is too low to select any meaningful"):
            run_manifest_generator(
                data_dir=data_dir,
                output_dir=output_dir,
                dataset_properties_path=props_path,
                train_size=0.5,
                random_state=1,
                target_classes=["class_a"],
                threshold=0.1,
            )