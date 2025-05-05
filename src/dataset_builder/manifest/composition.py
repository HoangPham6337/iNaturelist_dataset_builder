from typing import List, Dict, Tuple
from sklearn.model_selection import train_test_split  # type: ignore
from dataset_builder.core.log import log


def generate_species_composition(
    image_list: List[Tuple[str, int]], 
    species_dict: Dict[int, str]
) -> Dict[str, int]:
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

