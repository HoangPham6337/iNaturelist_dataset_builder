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
) -> Tuple[List[Tuple[str, int]], List[Tuple[str, int]], List[Tuple[str, int]], Dict[int, str], Dict[str, int]]:
    dominant_species = get_dominant_species_if_needed(dataset_properties_path, threshold, target_classes)
    image_list, species_dict, _ = collect_images(data_dir, dominant_species)
    species_composition = generate_species_composition(image_list, species_dict)
    train_data, val_data = split_train_val(image_list, train_size, random_state)

    if export:
        export_dataset_files(output_dir, image_list, train_data, val_data, species_dict, species_composition, per_species_list)

    print(f"Total species ({'no Other' if threshold == 1.0 else 'with Other'}): {len(species_dict)}")
    print(f"Total Images: {len(image_list)} | Train: {len(train_data)} | Val: {len(val_data)}")

    return image_list, train_data, val_data, species_dict, species_composition
