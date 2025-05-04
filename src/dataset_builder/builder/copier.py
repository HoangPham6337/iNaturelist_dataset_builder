import shutil
from typing import Tuple, Iterator
from enum import Enum
from dataset_builder.builder.walker import CopyTask
from dataset_builder.core.utility import log


class CopyStatus(Enum):
    COPIED = 1
    SKIPPED = 2
    MISSING = 3


def copy_one_species_data(task: CopyTask, verbose: bool = False) -> CopyStatus:
    """
    Copy all files under `src_dir` to `dst_dir` for one species.
    Returns `True` if `src_dir` existed and copied at least one file,
    `False` if `src_dir` was missing
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
    Runs `copy_one` over all tasks, returns `copied_count`, `total_tasks`.
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