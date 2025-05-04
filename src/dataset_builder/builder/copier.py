import shutil
from typing import Tuple, Iterator
from dataset_builder.builder.walker import CopyTask
from dataset_builder.core.utility import log


def copy_one_species_data(task: CopyTask, verbose: bool = False) -> bool:
    """
    Copy all files under `src_dir` to `dst_dir` for one species.
    Returns `True` if `src_dir` existed and copied at least one file,
    `False` if `src_dir` was missing
    """
    species_class, species, src_dir, dst_dir = task
    if not src_dir.exists():
        log(f"Missing source directory: {src_dir}", True, "ERROR")
        return False
    
    dst_dir.mkdir(parents=True, exist_ok=True)
    copied_any = False

    for image_file in src_dir.iterdir():
        if image_file.is_file():
            target = dst_dir / image_file.name
            if not target.exists():
                shutil.copy2(image_file, target)
                log(f"Copied {species_class}/{species}/{image_file.name}", verbose)
                copied_any = True
            else:
                log(f"Skipping existing {species_class}/{species}/{image_file.name}", verbose)
    return copied_any


def copy_all_species(
    tasks: Iterator[CopyTask],
    verbose: bool = False
) -> Tuple[int, int]:
    """
    Runs `copy_one` over all tasks, returns `copied_count`, `total_tasks`.
    """
    total = 0
    copied = 0
    for task in tasks:
        total += 1
        if copy_one_species_data(task, verbose):
            copied += 1
    return copied, total