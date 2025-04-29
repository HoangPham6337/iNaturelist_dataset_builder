import os
import re
from typing import Any, List

import yaml  #type: ignore

from dataclasses import dataclass, asdict

from dataset_builder.core.exceptions import ConfigError
from dataset_builder.core.utility import log
from dataset_builder.core.utility import _str_to_bool


def load_config(config_path: str) -> Any:
    """
    Loads a YAML configuration file and returns its contents.

    Args:
        config_path: The file pip install types-PyYAMLpath to the YAML configuration file to be loaded.

    Returns:
        output: The parsed contents of the YAML configuration file.

    Raises:
        FileNotFoundError: If the specified configuration file does not exist.
        yaml.YAMLError: If the YAML file is invalid or cannot be parsed.
    """
    with open(config_path, "r") as file:
        return yaml.safe_load(file)


def validate_config(config):
    """
    Validates the provided configuration dictionary.

    Checks for the presence and correctness of required sections like 'global',
    'paths', 'web_crawl', and 'train_val_split', ensuring that values are of
    the correct type and format. Creates missing directories and raises errors
    for any invalid or missing configurations.

    Args:
        config: The configuration dictionary to validate. Parse from `load_config()`

    Raises:
        ConfigError: If any required section or value in the config is missing or invalid.
    """
    # Validate global
    if "global" not in config:
        raise ConfigError("Missing 'global' section in config")
    if not isinstance(config["global"].get("verbose", None), bool):
        raise ConfigError("'verbose' should be a boolean value in 'global'")
    if not isinstance(config["global"].get("overwrite", None), bool):
        raise ConfigError("'overwrite' should be a boolean value in 'global'")
    if not isinstance(config["global"].get("included_classes", None), list):
        raise ConfigError("'included_classes' should be a list of strings in 'global'")

    verbose = config["global"]["verbose"]

    # Validate path
    if "paths" not in config:
        raise ConfigError("Missing 'paths' section in config")

    src_dataset_path = config["paths"].get("src_dataset", None)
    dst_dataset_path = config["paths"].get("dst_dataset", None)
    output_path = config["paths"].get("output_dir", None)
    web_crawl_output_path = config["paths"].get("web_crawl_output_json", None)

    if not all(
        [src_dataset_path, dst_dataset_path, output_path, web_crawl_output_path]
    ):
        raise ConfigError("Missing one or more required paths in 'paths' section.")

    for path in [dst_dataset_path, output_path]:
        if not os.path.isdir(path):
            log(f"Path {path} does not exist. It will be created.", True, "INFO")
            os.makedirs(path, exist_ok=True)

    # Validate web_crawl
    if "web_crawl" not in config:
        raise ConfigError("Missing 'web_crawl' section in config.")

    base_url = config["web_crawl"].get("base_url", None)
    total_pages = config["web_crawl"].get("total_pages", None)
    delay = config["web_crawl"].get("delay_between_requests", None)

    if not isinstance(base_url, str) or not re.match(r"^https?://", base_url):
        raise ConfigError(
            "'base_url' should be a valid URL starting with http:// or https://"
        )
    if not isinstance(total_pages, int) or total_pages <= 0:
        raise ConfigError("'total_pages' should be a positive integer")
    if not isinstance(delay, (int, float)) or delay <= 0:
        raise ConfigError("'delay_between_requests' should be a positive number")

    # Validate train_val_split
    if "train_val_split" not in config:
        raise ConfigError("Missing 'train_val_split' section in config")
    train_size = config["train_val_split"].get("train_size", None)
    randomness = config["train_val_split"].get("random_state", None)
    dominant_threshold = config["train_val_split"].get("dominant_threshold", None)

    if not isinstance(train_size, float) or not (0 < train_size and train_size < 1):
        raise ConfigError("'train_size' should be a float between 0 and 1")
    if not isinstance(dominant_threshold, float) or not (
        0 < dominant_threshold and dominant_threshold <= 1
    ):
        raise ConfigError(
            "'dominant_threshold' should be a float between 0 and 1 (inclusive)"
        )
    if not isinstance(randomness, int):
        raise ConfigError("'random_state' should be an integer")

    log("Configuration is valid!", verbose)


def _ask(prompt, default=None, cast=str):
    raw = input(f"{prompt} [{default}]: ")
    return cast(raw.strip() if raw.strip() else default)


@dataclass
class GlobalConfig:
    included_classes: List[str]
    verbose: bool
    overwrite: bool


@dataclass
class PathsConfig:
    src_dataset: str
    dst_dataset: str
    web_crawl_output_json: str
    output_dir: str


@dataclass
class WebCrawlConfig:
    total_pages: int
    base_url: str
    delay_between_requests: int


@dataclass
class TrainValSplitConfig:
    train_size: float
    random_state: int
    dominant_threshold: float


@dataclass
class Config:
    global_: GlobalConfig
    paths: PathsConfig
    web_crawl: WebCrawlConfig
    train_val_split: TrainValSplitConfig


def build_interactive_config() -> Config:
    print("=== GLOBAL CONFIG ===")
    included = _ask("Included classes (comma-separated)", "Aves,Insecta").split(",")
    verbose = _ask("Verbose mode?", "false", _str_to_bool)
    overwrite = _ask("Overwrite existing files?", "false", _str_to_bool)

    print("\n=== PATH CONFIG ===")
    src = _ask("Source dataset path", "./data/train_val_images")
    dst = _ask("Destination dataset path", "./data/haute_garonne")
    json_out = _ask("Web crawl output JSON", "./output/haute_garonne.json")
    outdir = _ask("Output directory", "./output")

    print("\n=== WEB CRAWL CONFIG ===")
    pages = _ask("Total pages", 104, int)
    base_url = _ask(
        "Base URL",
        "https://www.inaturalist.org/check_lists/32961-Haute-Garonne-Check-List?page=",
    )
    delay = _ask("Delay between requests (sec)", 1, int)

    print("\n=== TRAIN/VAL SPLIT CONFIG ===")
    train_size = _ask("Train size (e.g., 0.8)", 0.8, float)
    seed = _ask("Random seed", 42, int)
    threshold = _ask("Dominant threshold", 0.5, float)

    return Config(
        global_=GlobalConfig(included, verbose, overwrite),
        paths=PathsConfig(src, dst, json_out, outdir),
        web_crawl=WebCrawlConfig(pages, base_url, delay),
        train_val_split=TrainValSplitConfig(train_size, seed, threshold),
    )


def save_config(config: Config, filepath="config.yaml"):
    with open(filepath, "w") as f:
        yaml.safe_dump(asdict(config), f, sort_keys=False)
    print(f"\nConfiguration saved to {filepath}")