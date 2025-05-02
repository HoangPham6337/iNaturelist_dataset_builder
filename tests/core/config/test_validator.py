import os

import pytest

from dataset_builder.core.config import validate_config  # type: ignore
from dataset_builder.core.exceptions import ConfigError  # type: ignore


def make_valid_config(base_dir):
    return {
        "global": {
            "included_classes": ["Aves", "Insecta"],
            "verbose": True,
            "overwrite": False
        },
        "paths": {
            "src_dataset": os.path.join(base_dir, "src"),
            "dst_dataset": os.path.join(base_dir, "dst"),
            "output_dir": os.path.join(base_dir, "out"),
            "web_crawl_output_json": os.path.join(base_dir, "dummy.json")
        },
        "web_crawl": {
            "base_url": "https://example.com",
            "total_pages": 3,
            "delay_between_requests": 1
        },
        "train_val_split": {
            "train_size": 0.8,
            "random_state": 42,
            "dominant_threshold": 0.5
        }
    }


def create_dirs(base_dir: str):
    os.makedirs(os.path.join(base_dir, "src"))
    os.makedirs(os.path.join(base_dir, "dst"))
    os.makedirs(os.path.join(base_dir, "out"))


def test_valid_config_passes(tmp_path):
    create_dirs(tmp_path)
    config = make_valid_config(tmp_path)
    validate_config(config)


def test_malformed_config_raises():
    with pytest.raises(ConfigError, match="Config is not a dictionary"):
        validate_config(None)


@pytest.mark.parametrize("section", ["global", "paths", "web_crawl", "train_val_split"])
def test_empty_section_raises(section, tmp_path):
    create_dirs(tmp_path)
    cfg = make_valid_config(tmp_path)
    cfg[section] = "this is not a dictionary"
    with pytest.raises(ConfigError, match=f"{section} should be a dict, got str"):
        validate_config(cfg)


@pytest.mark.parametrize("section", ["global", "paths", "web_crawl", "train_val_split"])
def test_missing_section_raises(section, tmp_path):
    create_dirs(tmp_path)
    cfg = make_valid_config(tmp_path)
    cfg.pop(section)
    with pytest.raises(ConfigError, match=f"Missing {section} section"):
        validate_config(cfg)


@pytest.mark.parametrize("section, key", [
    ("global", "verbose"),
    ("paths", "output_dir"),
    ("web_crawl", "total_pages"),
    ("train_val_split", "dominant_threshold")
])
def test_missing_key_in_global(section, key, tmp_path):
    create_dirs(tmp_path)
    cfg = make_valid_config(tmp_path)
    del cfg[section][key]
    with pytest.raises(ConfigError, match=f"Missing key '{key}' in section '{section}'"):
        validate_config(cfg)


def test_empty_included_classes(tmp_path):
    create_dirs(tmp_path)
    cfg = make_valid_config(tmp_path)
    cfg["global"]["included_classes"] = []
    with pytest.raises(ConfigError, match="'included_classes' should contain at least one entry"):
        validate_config(cfg)


def test_wrong_type_included_classes(tmp_path):
    create_dirs(tmp_path)
    cfg = make_valid_config(tmp_path)
    cfg["global"]["included_classes"] = "Aves"
    with pytest.raises(ConfigError, match="global.included_classes should be a list"):
        validate_config(cfg)


def test_included_classes_with_wrong_element_types(tmp_path):
    create_dirs(tmp_path)
    cfg = make_valid_config(tmp_path)
    cfg["global"]["included_classes"] = ["Aves", 123]
    with pytest.raises(ConfigError, match="should be a list of string"):
        validate_config(cfg)


@pytest.mark.parametrize("missing_dir", ["dst", "src", "out"])
def test_nonexistant_path_raises(missing_dir, tmp_path):
    for d in ["src", "dst", "out"]:
        if d != missing_dir:
            os.makedirs(os.path.join(tmp_path, d))
    cfg = make_valid_config(tmp_path)
    expected = os.path.join(tmp_path, missing_dir)
    with pytest.raises(ConfigError, match=f"Path {expected} does not exist. Please create it and try again"):
        validate_config(cfg)


def test_invalid_url_format(tmp_path):
    create_dirs(tmp_path)
    cfg = make_valid_config(tmp_path)
    cfg["web_crawl"]["base_url"] = "ftp://thisisverywrong"
    with pytest.raises(ConfigError, match="'base_url' should be a valid URL starting with http:// or https://"):
        validate_config(cfg)


@pytest.mark.parametrize("field, value", [
    ("total_pages", 0),
    ("total_pages", -3),
    ("total_pages", 3.0),
    ("delay_between_requests", 0),
    ("delay_between_requests", -1),
    ("delay_between_requests", "9"),
])
def test_web_crawl_invalid_values(field, value, tmp_path):
    create_dirs(tmp_path)
    cfg = make_valid_config(tmp_path)
    cfg["web_crawl"][field] = value
    with pytest.raises(ConfigError, match=field):
        validate_config(cfg)


@pytest.mark.parametrize("field,value", [
    ("train_size", 0),
    ("train_size", 1.1),
    ("dominant_threshold", -0.1),
    ("dominant_threshold", 2.0),
    ("random_state", -1),
])
def test_train_val_split_invalid(field, value, tmp_path):
    create_dirs(tmp_path)
    cfg = make_valid_config(tmp_path)
    cfg["train_val_split"][field] = value
    with pytest.raises(ConfigError, match=field):
        validate_config(cfg)