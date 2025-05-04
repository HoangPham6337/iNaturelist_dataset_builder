from pathlib import Path
from typing import List

from tqdm import tqdm

from dataset_builder.builder.copier import copy_all_species
from dataset_builder.builder.io import load_matched_species
from dataset_builder.builder.walker import build_copy_tasks
from dataset_builder.core.exceptions import FailedOperation


def run_copy_matched_species(
    src_dataset: str,
    dst_dataset: str,
    matched_species_json: str,
    target_classes: List[str],
    overwrite: bool = False,
    verbose: bool = False
) -> None:
    matched_species = load_matched_species(matched_species_json)

    total_tasks = sum(
        len(species_list)
        for species_class, species_list in matched_species.items()
        if species_class in target_classes
    )
    tasks = build_copy_tasks(matched_species, target_classes, Path(src_dataset), Path(dst_dataset))

    print(f"Copying data to {dst_dataset}")
    tasks_with_progress = tqdm(tasks, total=total_tasks, desc="Species", unit="species")
    copied, total = copy_all_species(tasks_with_progress, verbose)

    if not overwrite and copied != total:
        raise FailedOperation(f"Failed to copy all matched species: {copied}/{total} copied")