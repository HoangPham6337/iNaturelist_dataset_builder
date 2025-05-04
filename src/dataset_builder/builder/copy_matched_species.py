from pathlib import Path
from dataset_builder.builder.io import load_matched_species
from dataset_builder.builder.walker import build_copy_tasks
from dataset_builder.builder.copier import copy_all_species
from dataset_builder.core.exceptions import FailedOperation
from typing import List

def run_copy_matched_species(
    src_dataset: str,
    dst_dataset: str,
    matched_species_json: str,
    target_classes: List[str],
    verbose: bool = False
) -> None:
    matched_species = load_matched_species(matched_species_json)

    tasks = build_copy_tasks(matched_species, target_classes, Path(src_dataset), Path(dst_dataset))

    print(f"Copying data to {dst_dataset}")
    copied, total = copy_all_species(tasks, verbose)

    if copied != total:
        raise FailedOperation(f"Failed to copy all matched species: {copied}/{total} copied")