from typing import List, Dict, Tuple
from sklearn.model_selection import train_test_split  # type: ignore
from dataset_builder.core.log import log


def generate_species_composition(
    image_list: List[Tuple[str, int]], 
    species_dict: Dict[int, str]
) -> Dict[str, int]:
    """
    Computes the number of images per species from a labeled image list.

    This function takes a list of (image_path, species_id) tuples and a dictionary
    mapping species IDs to species names, and returns a dictionary indicating how 
    many images belong to each species.

    Args:
        image_list (List[Tuple[str, int]]): A list of tuples where each entry contains
            an image path and its associated species ID.
        species_dict (Dict[int, str]): A mapping from integer species ID to species name.

    Returns:
        Dict[str, int]: A dictionary mapping species names to the number of images belonging to them.
    """
    species_composition: Dict[str, int] = {}
    for species_label, species_name in species_dict.items():
        current_species = [1 for label in image_list if label[1] == species_label]
        total_species = sum(current_species)
        species_composition[species_name] = total_species
    return species_composition


def split_train_val(
    image_list: List[Tuple[str, int]],
    train_size: float,
    random_state: int,
) -> Tuple[List[Tuple[str, int]], List[Tuple[str, int]]]:
    """
    Splits the dataset into training and validation sets, stratified by species label.

    Attempts to perform a stratified split to preserve label distribution in both splits.
    If stratification fails due to insufficient class samples, a fallback non-stratified split is used.

    Args:
        image_list (List[Tuple[str, int]]): A list of (image_path, label) tuples.
        train_size (float): Proportion of the dataset to allocate to training (e.g., 0.8).
        random_state (int): Random seed for reproducibility.

    Returns:
        Tuple[List[Tuple[str, int]], List[Tuple[str, int]]]: Two lists representing the training and validation splits.

    Notes:
        If some labels have fewer than 2 samples, stratification will fail and a warning will be logged.
    """
    try:
        train, val = train_test_split(
        image_list,
        train_size=train_size,
        random_state=random_state,
        stratify=[label for _, label in image_list],
        )
    except ValueError as e:
        log(str(e), True, "WARNING")
        log("Fallback to splitting without stratify, some species can be missing.", True)
        train, val = train_test_split(
        image_list,
        train_size=train_size,
        random_state=random_state,
        )
    return train, val

