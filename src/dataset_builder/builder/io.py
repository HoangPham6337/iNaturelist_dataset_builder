import os
from dataset_builder.core.utility import SpeciesDict, read_species_from_json, _is_a_valid_species_dict
from dataset_builder.core.exceptions import FailedOperation


def load_matched_species(path: str) -> SpeciesDict:
    """Load and validate the matched_species JSON."""
    if not os.path.isfile(path):
        raise FailedOperation(f"Matched species JSON not found: {path}")
    data: SpeciesDict = read_species_from_json(path)
    if not _is_a_valid_species_dict(data):
        msg_1 = "Invalid matched species JSON format,"
        msg_2 = "The object must be a dictionary where keys are strings (non-null) (species classes)"
        msg_3 = "and values are lists of species names (non-null strings)."
        raise FailedOperation(f"{msg_1} {msg_2} {msg_3}")
    return data