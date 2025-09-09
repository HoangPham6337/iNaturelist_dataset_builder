from typing import List, Tuple, Dict
from dataset_builder.manifest.data_preparer import get_dominant_species_if_needed, collect_images
from dataset_builder.manifest.composition import generate_species_composition, split_train_val
from dataset_builder.manifest.exporter import export_dataset_files


def run_manifest_generator(
    data_dir: str,
    output_dir: str,
    dataset_properties_path: str,
    train_size: float,
    random_state: int,
    target_classes: List[str],
    threshold: float,
    per_species_list: bool = False,
    export: bool = True,
    just_other: bool = False
) -> Tuple[List[Tuple[str, int]], List[Tuple[str, int]], List[Tuple[str, int]], Dict[int, str], Dict[str, int]]:
    """
    Builds a dataset manifest by collecting species images, identifying dominant species, 
    generating train/val splits, and optionally exporting all results.

    This function orchestrates the entire data preparation workflow for species-based datasets. 
    It loads class-wise image statistics, optionally filters by dominant species using a threshold, 
    collects image paths with labels, splits the data into training and validation sets, 
    and saves dataset metadata and manifests to disk.

    Args:
        data_dir (str): Root path of the dataset, organized by class and species folders.
        output_dir (str): Output path for saving manifest files and metadata.
        dataset_properties_path (str): Path to the JSON file with precomputed image counts.
        train_size (float): Fraction of data to use for training (0 < train_size < 1).
        random_state (int): Seed for reproducibility of the train/val split.
        target_classes (List[str]): List of species classes (e.g., "Aves", "Mammalia") to process.
        threshold (float): CDF threshold (e.g., 0.9). If < 1.0, low-count species are grouped into "Other".
        per_species_list (bool, optional): Whether to export per-species image manifests. Default is False.
        export (bool, optional): Whether to save dataset files to disk. Default is True.

    Returns:
        Tuple containing:
            - image_list: All image paths and their assigned labels.
            - train_data: Training set (subset of image_list).
            - val_data: Validation set (subset of image_list).
            - species_dict: Mapping from label ID to species name.
            - species_composition: Mapping from species name to image count.

    Notes:
        - If `threshold == 1.0`, all species are included with no 'Other' category.
        - Creates files like:
            - dataset_manifest.parquet
            - train.parquet / val.parquet
            - dataset_species_labels.json
            - species_composition.json
            - species_lists/ (optional per-species files)
    """
    dominant_species = get_dominant_species_if_needed(dataset_properties_path, threshold, target_classes)
    image_list, species_dict, _ = collect_images(data_dir, dominant_species, just_other)
    species_composition = generate_species_composition(image_list, species_dict)
    train_data, val_data = split_train_val(image_list, train_size, random_state)

    if export:
        export_dataset_files(output_dir, image_list, train_data, val_data, species_dict, species_composition, per_species_list)

    print(f"Total species ({'no Other' if threshold == 1.0 else 'with Other'}): {len(species_dict)}")
    print(f"Total Images: {len(image_list)} | Train: {len(train_data)} | Val: {len(val_data)}")

    return image_list, train_data, val_data, species_dict, species_composition
