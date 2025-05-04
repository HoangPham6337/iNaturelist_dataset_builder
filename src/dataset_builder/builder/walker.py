from pathlib import Path
from dataset_builder.core.utility import SpeciesDict
from typing import Iterator, Tuple, List


CopyTask = Tuple[str, str, Path, Path]


def build_copy_tasks(
    matched_species: SpeciesDict,
    target_classes: List[str],
    src_root: Path,
    dst_root: Path,
) -> Iterator[CopyTask]:
    """
    Yields one task per (class_name, species_name) pair in target_classes.
    """
    for species_class, species_list in matched_species.items():
        if species_class in target_classes:
            for species in species_list:
                yield (
                    species_class,
                    species,
                    src_root / species_class / species,
                    dst_root / species_class / species,
                )
