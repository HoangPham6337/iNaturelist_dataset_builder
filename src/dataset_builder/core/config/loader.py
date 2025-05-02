from typing import Any, Dict, Union
import yaml  # type: ignore

from dataclasses import asdict
from .schema import Config
from dataset_builder.core.utility import log


def load_config(config_path: str) -> Dict[str, Any]:
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
    with open(config_path, "r", encoding="utf-8") as file:
        data = yaml.safe_load(file)
    
    if not isinstance(data, dict):
        raise ValueError(f"Expect YAML to be a dictionary, got {type(data)} instead")
    
    return data


def save_config(config: Union[Dict, Config], filepath="config.yaml"):
    """
    Write a Config or dict to a YAML file.

    Args:
        config (Union[Dict, Config]):  
            Configuration to save; can be a Config instance or a plain dict.
        filepath (str, optional):  
            Destination file path. Defaults to "config.yaml".

    Raises:
        OSError: If the file can’t be written.
    """
    with open(filepath, "w") as f:
        if isinstance(config, Config):
            yaml.safe_dump(asdict(config), f, sort_keys=False)
        else:
            yaml.safe_dump(config, f, sort_keys=False)
    log(f"Configuration saved to {filepath}")