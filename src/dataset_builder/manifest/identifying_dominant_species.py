from collections import defaultdict
from typing import Dict, List, Optional

import numpy as np

from dataset_builder.core.utility import _prepare_data_cdf_ppf, SpeciesDict
from dataset_builder.core.log import log
from dataset_builder.core.exceptions import PipelineError


def _validate_dominant_species_rules(threshold: float):
    if threshold < 0 or threshold > 1:
        raise PipelineError("Threshold must be between 0 and 1")


def analyze_single_class(
    properties_json_path: str,
    species_class: str,
    threshold: float,
) -> List[str]:
    """
    Analyzes a single species class to identify dominant species based on cumulative image distribution.

    The function reads image count data from a precomputed properties file, computes the cumulative
    distribution function (CDF) of image counts, and selects the minimal set of species that collectively
    reach or exceed the specified threshold of total images.

    Args:
        properties_json_path (str): Path to the JSON file containing image statistics per species per class.
        species_class (str): The name of the class to analyze (e.g., "Aves").
        threshold (float): The cumulative percentage threshold (e.g., 0.8 for 80%).

    Returns:
        List[str]: A list of dominant species names that contribute to the threshold image coverage.

    Raises:
        PipelineError: If data preparation fails, total images is zero, or threshold is too low
                       to include any species.

    Notes:
        - If no species meet the criteria or data is missing, an empty list is returned.
        - If the threshold is below the first species's cdf, a PipelineError is raised.
    """
    result = _prepare_data_cdf_ppf(properties_json_path, species_class)
    if result is None:
        raise PipelineError(f"ERROR: Data preparation failed for {species_class}")

    species_names, sorted_image_counts = result

    if not species_names or not sorted_image_counts:
        log(f"No data available for {species_class}", True, "WARNING")
        return []

    total_images = sum(sorted_image_counts)
    if total_images == 0:
        log(f"No data available for {species_class}", True, "WARNING")
        return []

    cumulative_images = np.cumsum(sorted_image_counts)
    cdf_values = cumulative_images / total_images
    sorted_images = np.array(sorted_image_counts)

    filtered_index = np.argmax(cdf_values >= threshold)
    thresholded_image_count = sorted_images[filtered_index]

    if filtered_index == 0 and cdf_values[0] > threshold:
        raise PipelineError(
            f"Threshold {threshold:.2f} is too low to select any meaningful dominant species in class '{species_class}\nMinimum: {cdf_values[0]}'"
        )

    dominant_species = [
        species
        for species, count in zip(species_names, sorted_image_counts)
        if count >= thresholded_image_count
    ]
    return dominant_species


def identifying_dominant_species(properties_json_path: str, threshold: float, classes_to_analyze: List[str]) -> Optional[Dict[str, List[str]]]:
    """
    Identifies dominant species in the given classes based on a specified image count threshold.

    The function calculates the cumulative distribution of image counts for each species class,
    and identifies species whose image counts exceed the threshold defined by the given percentile.

    Args:
        properties_json_path: Path to the JSON file containing species image data.
        threshold: The cumulative percentage threshold (e.g., 0.5 for 50%).
        classes_to_analyze: List of species classes to analyze.

    Returns:
        SpeciesDict: A dictionary where keys are species class names, and values are lists of dominant species names.
        Returns None if the data preparation fails for any class.
    """
    _validate_dominant_species_rules(threshold)

    species_data: SpeciesDict = defaultdict(list)
    for species_class in classes_to_analyze:
        dominant_species = analyze_single_class(properties_json_path, species_class, threshold)
        species_data[species_class] = dominant_species
    return species_data
