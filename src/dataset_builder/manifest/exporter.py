import os
import json
from typing import List, Tuple, Dict
from tqdm import tqdm  # type: ignore
from dataset_builder.core.utility import save_manifest_parquet, write_data_to_json


def _write_species_lists(
    base_output_path: str,
    image_list: List[Tuple[str, int]],
    species_dict: Dict[int, str],
):
    """
    Writes species-specific image lists to the specified output path.

    Groups the images by species, creates directories for each species, and saves 
    the list of image paths to a Parquet file for each species.

    Args:
        base_output_path (str): The base directory where species lists will be saved.
        image_list (List[Tuple[str, int]]): A list of image paths and their corresponding species IDs.
        species_dict (Dict[int, str]): A dictionary mapping species IDs to species names.
    """

    species_list_dir = os.path.join(base_output_path, "species_lists")
    os.makedirs(species_list_dir, exist_ok=True)

    species_group: Dict[str, List[Tuple[str, int]]] = {}
    for img_path, label in image_list:
        species = species_dict[label]
        if species not in species_group:
            species_group[species] = []
        species_group[species].append((img_path, label))


    for species, tuple_list in tqdm(species_group.items(), f"Writing species specific manifest to {species_list_dir}"):
        class_name = tuple_list[0][0].split(os.sep)[-3]
        species_dir = os.path.join(species_list_dir, class_name, species)
        os.makedirs(species_dir, exist_ok=True)
        file_name = os.path.join(species_dir, "images.parquet")

        # save_manifest_parquet(tuple_list, file_name)
        write_data_to_json(file_name, "Per-species data", tuple_list, False)

        # with open(os.path.join(species_dir, "images.txt"), "w") as file:
        #     file.write("\n".join(tuple_list))


def export_dataset_files(
    output_dir: str,
    image_list: List[Tuple[str, int]],
    train_data: List[Tuple[str, int]],
    val_data: List[Tuple[str, int]],
    species_dict: Dict[int, str],
    species_composition: Dict[str, int],
    per_species_list: bool = False,
):
    os.makedirs(output_dir, exist_ok=True)
    with open(os.path.join(output_dir, "dataset_species_labels.json"), "w", encoding="utf-8") as f:
        json.dump(species_dict, f, indent=4)

    save_manifest_parquet(image_list, os.path.join(output_dir, "dataset_manifest.parquet"))
    save_manifest_parquet(train_data, os.path.join(output_dir, "train.parquet"))
    save_manifest_parquet(val_data, os.path.join(output_dir, "val.parquet"))
    write_data_to_json(os.path.join(output_dir, "species_composition.json"), "species_composition", species_composition)

    if per_species_list:
        _write_species_lists(output_dir, image_list, species_dict)
