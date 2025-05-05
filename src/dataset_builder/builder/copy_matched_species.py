from pathlib import Path
from typing import List

from tqdm import tqdm  # type: ignore

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
    """
    Copies matched species data from the source dataset to the destination directory.

    This function loads a JSON file containing matched species grouped by class,
    filters the species by the specified target classes, and copies their data
    (images) from `src_dataset` to `dst_dataset`.

    For each species, it uses a `CopyTask` and tracks the number of species successfully
    copied, skipped (already exist), or missing (source directory does not exist).
    If any species are missing and `overwrite` is False, the function raises a `FailedOperation`.

    Args:
        src_dataset (str): Path to the source dataset directory.
        dst_dataset (str): Path to the destination dataset directory.
        matched_species_json (str): Path to a JSON file containing matched species information.
        target_classes (List[str]): List of species classes to filter and copy.
        overwrite (bool, optional): Whether to ignore missing species and proceed anyway. Defaults to False.
        verbose (bool, optional): Whether to print detailed logs during copy. Defaults to False.

    Raises:
        FailedOperation: If some species are missing in the source dataset and `overwrite` is False.
    """
    matched_species = load_matched_species(matched_species_json)

    total_tasks = sum(
        len(species_list)
        for species_class, species_list in matched_species.items()
        if species_class in target_classes
    )
    tasks = build_copy_tasks(matched_species, target_classes, Path(src_dataset), Path(dst_dataset))

    print(f"Copying data to {dst_dataset}")
    tasks_with_progress = tqdm(tasks, total=total_tasks, desc="Species", unit="species")
    copied, skipped, missing = copy_all_species(tasks_with_progress, verbose)
    if missing > 0 and not overwrite:
        raise FailedOperation(f"Missing images in {missing} of {total_tasks} species")
    elif copied == 0 and skipped > 0:
        print(f"All {skipped} species already up-to-date; nothing to do")