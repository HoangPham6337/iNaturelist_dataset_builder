import os
import re
from typing import get_origin, get_args, Dict, Any

from dataset_builder.core.exceptions import ConfigError
from dataset_builder.core.config.schema import GlobalConfig, PathsConfig, WebCrawlConfig, TrainValSplitConfig
from dataclasses import is_dataclass, fields


def validate_dict_against_dataclass(data: Dict, schema_class: type, path="root") -> None:
    """
    Recursively verify that `data` matches the fields and types of `schema_class`.

    Args:
        data (Dict): The raw section to check.
        schema_class (type): A dataclass type whose fields define the expected keys and types.
        path (str): Dot-separated path for error reporting.

    Raises:
        ConfigError: If `data` is not a dict, is missing a required key, or if a value has the wrong primitive type or unsupported type.
    """
    if not isinstance(data, dict):
        raise ConfigError(f"{path} should be a dict, got {type(data).__name__}")

    for field in fields(schema_class):
        key = field.name
        expected_type = field.type

        if key not in data:
            raise ConfigError(f"Missing key '{key}' in section '{path}'")

        value = data[key]
        origin = get_origin(expected_type)
        args = get_args(expected_type)

        if is_dataclass(expected_type) and isinstance(expected_type, type):
            validate_dict_against_dataclass(value, expected_type, f"{path}.{key}")

        elif origin is list and args == (str,):
            if not isinstance(value, list) or not all (isinstance(item, str) for item in value):
                raise ConfigError(f"{path}.{key} should be a list of strings")

        elif expected_type is bool:
            if not isinstance(value, bool):
                raise ConfigError(f"{path}.{key} should be a boolean")

        elif expected_type is int:
            if not isinstance(value, int):
                raise ConfigError(f"{path}.{key} should be an integer")

        elif expected_type is float:
            if not isinstance(value, float):
                raise ConfigError(f"{path}.{key} should be a float")

        elif expected_type is str:
            if not isinstance(value, str):
                raise ConfigError(f"{path}.{key} should be a string")

        else:
            raise ConfigError(f"Unsupported field type {expected_type} at {path}.{key}")


def validate_global_rules(config: Dict):
    """
    Enforce semantic rules on the 'global' section.

    Args:
        config (Dict): Full raw config dict.

    Raises:
        ConfigError: If 'included_classes' is empty.
    """
    global_cfg = config["global"]
    if len(global_cfg["included_classes"]) == 0:
        raise ConfigError("'included_classes' should contain at least one entry")


def validate_path_rules(config: Dict):
    """
    Ensure required filesystem paths exist.

    Args:
        config (Dict): Full raw config dict.

    Raises:
        ConfigError: If any of src_dataset, dst_dataset, or output_dir is missing or not a dir.
    """
    path_cfg = config["paths"]
    for path in [
        path_cfg["src_dataset"],
        path_cfg["dst_dataset"],
        path_cfg["output_dir"]
    ]:
        if not os.path.isdir(path):
            raise ConfigError(f"Path {path} does not exist. Please create it and try again")


def validate_web_crawl_rules(config: Dict):
    """
    Enforce semantic rules on the 'web_crawl' section.

    Args:
        config (Dict): Full raw config dict.

    Raises:
        ConfigError: For invalid URL scheme, non-positive total_pages or delay.
    """
    wc_config = config["web_crawl"]
    base_url = wc_config.get("base_url", None)
    total_pages = wc_config.get("total_pages", None)
    delay = wc_config.get("delay_between_requests", None)

    if not re.match(r"^https?://", base_url):
        raise ConfigError("'base_url' should be a valid URL starting with http:// or https://")
    if total_pages <= 0:
        raise ConfigError("'total_pages' should be a positive integer")
    if delay <= 0:
        raise ConfigError("'delay_between_requests' should be a positive number")


def validate_train_val_split_rules(config: Dict):
    """
    Enforce semantic rules on the 'train_val_split' section.

    Args:
        config (Dict): Full raw config dict.

    Raises:
        ConfigError: If train_size or dominant_threshold are out of (0,1] range, or if random_state is negative.
    """
    tvs_config = config["train_val_split"]
    train_size = tvs_config.get("train_size", None)
    randomness = tvs_config.get("random_state", None)
    dominant_threshold = tvs_config.get("dominant_threshold", None)

    if not (0 < train_size and train_size <= 1):
        raise ConfigError("'train_size' should be a float between 0 and 1 (inclusive)")
    if not (0 < dominant_threshold and dominant_threshold <= 1):
        raise ConfigError("'dominant_threshold' should be a float between 0 and 1 (inclusive)")
    if randomness < 0:
        raise ConfigError("'random_state' should be a positive integer")


def validate_all_group_exists(config: Dict):
    """
    Check that all required top-level sections are present.

    Args:
        config (Dict): Full raw config dict.

    Raises:
        ConfigError: If any of 'global', 'paths', 'web_crawl', or 'train_val_split' is missing.
    """
    groups = ["global", "paths", "web_crawl", "train_val_split"]
    for group in groups:
        if group not in config:
            raise ConfigError(f"Missing {group} section in config")


def is_config_dict(raw_config: Any):
    """
    Quick check that the loaded config is a dict.

    Args:
        raw_config (Any): The object returned by load_config().

    Returns:
        bool: True if it's a dict, False otherwise.
    """
    if not isinstance(raw_config, dict):
        return False
    return True


def validate_config(raw_config: Dict) -> None:
    """
    Full config validation pipeline:

      1. Ensure the config is a dict.
      2. Check for all required top-level sections.
      3. Validate each section's structure against its dataclass schema.
      4. Apply semantic rules on each section.

    Args:
        raw_config (Dict): The nested dict loaded from YAML.

    Raises:
        ConfigError: On any missing section, field, type mismatch, or rule violation.
    """
    if not is_config_dict(raw_config):
        raise ConfigError("Config is not a dictionary")
    # validate top structures
    validate_all_group_exists(raw_config)

    # validate internal structures
    validate_dict_against_dataclass(raw_config["global"], GlobalConfig, "global")
    validate_dict_against_dataclass(raw_config["paths"], PathsConfig, "paths")
    validate_dict_against_dataclass(raw_config["web_crawl"], WebCrawlConfig, "web_crawl")
    validate_dict_against_dataclass(raw_config["train_val_split"], TrainValSplitConfig, "train_val_split")

    # validate data for correct logic
    validate_global_rules(raw_config)
    validate_path_rules(raw_config)
    validate_web_crawl_rules(raw_config)
    validate_train_val_split_rules(raw_config)