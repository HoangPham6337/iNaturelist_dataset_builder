import shutil
from typing import Tuple, Iterator
from enum import Enum
from dataset_builder.builder.walker import CopyTask
from dataset_builder.core.log import log


class CopyStatus(Enum):
    COPIED = 1
    SKIPPED = 2
    MISSING = 3


def copy_one_species_data(task: CopyTask, verbose: bool = False) -> CopyStatus:
    """
    Copies all image files of a single species from the source to the destination directory.

    This function takes a `CopyTask`, which contains the species class, species name,
    source directory, and destination directory. It attempts to copy all files from
    the source to the destination. It skips any file that already exists in the destination.

    Args:
        task (CopyTask): A tuple containing:
            - species_class (str): The class name (e.g., "Aves").
            - species (str): The species name.
            - src_dir (Path): Path to the source directory.
            - dst_dir (Path): Path to the destination directory.
        verbose (bool, optional): Whether to print detailed log messages. Defaults to False.

    Returns:
        CopyStatus: 
            - `CopyStatus.COPIED` if at least one file was copied.
            - `CopyStatus.SKIPPED` if all files were already present.
            - `CopyStatus.MISSING` if the source directory does not exist.
    """
    species_class, species, src_dir, dst_dir = task
    if not src_dir.exists():
        log(f"Missing source directory: {src_dir}", True, "ERROR")
        return CopyStatus.MISSING
    
    dst_dir.mkdir(parents=True, exist_ok=True)
    did_copied = False

    for image_file in src_dir.iterdir():
        if image_file.is_file():
            target = dst_dir / image_file.name
            if not target.exists():
                shutil.copy2(image_file, target)
                log(f"Copied {species_class}/{species}/{image_file.name}", verbose)
                did_copied = True
            else:
                log(f"Skipping existing {species_class}/{species}/{image_file.name}", verbose)
    return CopyStatus.COPIED if did_copied else CopyStatus.SKIPPED


def copy_all_species(
    tasks: Iterator[CopyTask],
    verbose: bool = False
) -> Tuple[int, int, int]:
    """
    Executes copy operations for multiple species based on the provided tasks.

    This function iterates through an iterable of `CopyTask` items and uses
    `copy_one_species_data()` to copy files for each species. It tracks and returns
    the number of species that were copied, skipped (already exist), or failed 
    due to missing source directories.

    Args:
        tasks (Iterator[CopyTask]): An iterable of `CopyTask` tuples, each representing
            a species to copy.
        verbose (bool, optional): Whether to print detailed logs. Defaults to False.

    Returns:
        Tuple[int, int, int]: A tuple of three integers:
            - copied (int): Number of species successfully copied.
            - skipped (int): Number of species skipped (files already existed).
            - missing (int): Number of species whose source directories were missing.
    """
    copied = 0
    skipped = 0
    missing = 0
    for task in tasks:
        status = copy_one_species_data(task, verbose)
        if status is CopyStatus.COPIED:
            copied += 1
        elif status is CopyStatus.SKIPPED:
            skipped += 1
        else:
            missing += 1
    return copied, skipped, missing