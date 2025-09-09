import os
from typing import List, Optional, Dict, Set, Tuple
from dataset_builder.core.utility import SpeciesDict
from dataset_builder.core.log import log
from dataset_builder.manifest.identifying_dominant_species import identifying_dominant_species


def get_dominant_species_if_needed(
    dataset_properties_path: str,
    threshold: float,
    target_classes: List[str]
) -> Optional[SpeciesDict]:
    if threshold == 1.0:
        log("Selecting the entire dataset, no 'Other' label.", True)
        return None
    return identifying_dominant_species(dataset_properties_path, threshold, target_classes)


def collect_images_by_dominance(
    dataset_path: str,
    class_name: str,
    dominant_species: Optional[Dict[str, List[str]]],
    species_to_id: Dict[str, int],
    species_dict: Dict[int, str],
    image_list: List[Tuple[str, int]],
    current_id: int,
    just_other: bool = False
) -> int:
    """
    Collects image paths for dominant and non-dominant species from the dataset.

    First, it processes dominant species, assigning unique species IDs. Then, it 
    processes non-dominant species, assigning them to the "Other" category.

    Args:
        dataset_path: The path to the dataset containing species folders.
        class_name: The species class to process.
        dominant_species: A dictionary of dominant species by class.
        species_to_id: A mapping of species names to unique IDs.
        species_dict: A mapping of species IDs to species names.
        image_list: The list to accumulate image paths and their corresponding species IDs.
        current_id: The current species ID to assign.

    Returns:
        int: The updated species ID after processing the species.

    Raises:
        FailedOperation: If no dominant species are found for the given class.
    """
    dominant_set: Optional[Set[str]] = set(dominant_species.get(class_name, [])) if dominant_species else None

    if dominant_set is None:
        for species in sorted(os.listdir(dataset_path)):
            species_path = os.path.join(dataset_path, species)
            if not os.path.isdir(species_path):
                continue
            label = species_to_id.setdefault(species, current_id)
            if label == current_id:
                species_dict[current_id] = species
                current_id += 1
            for img_file in os.listdir(species_path):
                img_path = os.path.join(species_path, img_file)
                image_list.append((img_path, label))
    elif just_other and dominant_set:
        print("Generating for just 'Other'")
        for species in sorted(os.listdir(dataset_path)):
            if species in dominant_set:
                continue
            species_path = os.path.join(dataset_path, species)
            if not os.path.isdir(species_path):
                continue
            label = species_to_id.setdefault(species, current_id)
            if label == current_id:
                species_dict[current_id] = species
                current_id += 1
            for img_file in os.listdir(species_path):
                img_path = os.path.join(species_path, img_file)
                image_list.append((img_path, label))       
    else:

        # First pass: dominant species
        for species in sorted(os.listdir(dataset_path)):
            species_path = os.path.join(dataset_path, species)
            if not os.path.isdir(species_path):
                continue
            if species in dominant_set:
                label = species_to_id.setdefault(species, current_id)
                if label == current_id:
                    species_dict[current_id] = species
                    current_id += 1
                for img_file in os.listdir(species_path):
                    img_path = os.path.join(species_path, img_file)
                    image_list.append((img_path, label))

        # Second pass: non-dominant species → "Other"
        other_label = sum(len(species_list) for species_list in dominant_species.values())  # type: ignore
        for species in os.listdir(dataset_path):
            species_path = os.path.join(dataset_path, species)
            if not os.path.isdir(species_path):
                continue
            if species not in dominant_set:
                for img_file in os.listdir(species_path):
                    img_path = os.path.join(species_path, img_file)
                    image_list.append((img_path, other_label))

        if "Other" not in species_dict.values():
            species_dict[other_label] = "Other"

    return current_id


def collect_images(
    data_dir: str,
    dominant_species: Optional[SpeciesDict],
    just_other: bool = False
) -> Tuple[List[Tuple[str, int]], Dict[int, str], Dict[str, int]]:
    """
    Collects all image paths and assigns labels to species in a dataset directory.

    Iterates through species class subfolders in `data_dir`, optionally using a 
    dominant species list to determine whether to include all species or map 
    non-dominant ones to a shared "Other" class.

    Args:
        data_dir (str): Root directory containing class folders with species subdirectories.
        dominant_species (Optional[SpeciesDict]): Mapping from class names to lists of dominant species.
            If None, all species are considered. If provided, only dominant species are individually labeled;
            others are grouped under an "Other" label.

    Returns:
        Tuple containing:
            - image_list (List[Tuple[str, int]]): List of (image_path, species_label) pairs.
            - species_dict (Dict[int, str]): Mapping from label ID to species name.
            - species_to_id (Dict[str, int]): Mapping from species name to label ID.
    """
    species_to_id: Dict[str, int] = {}
    species_dict: Dict[int, str] = {}
    image_list: List[Tuple[str, int]] = []
    current_id = 0

    for class_name in os.listdir(data_dir):
        class_path = os.path.join(data_dir, class_name)
        if os.path.isdir(class_path) or class_name == "species_lists":
            current_id = collect_images_by_dominance(
                class_path,
                class_name,
                dominant_species,
                species_to_id,
                species_dict,
                image_list,
                current_id,
                just_other
            )
    species_dict = dict(sorted(species_dict.items()))

    return image_list, species_dict, species_to_id