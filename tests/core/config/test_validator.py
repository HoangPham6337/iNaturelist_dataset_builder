import os

import pytest

from dataset_builder.core.config import validate_config, validate_dict_against_dataclass  # type: ignore
from dataset_builder.core.config import PathsConfig, GlobalConfig, WebCrawlConfig, TrainValSplitConfig
from dataset_builder.core.exceptions import ConfigError  # type: ignore
from typing import Dict, Any
from dataclasses import dataclass


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
            "delay_between_requests": 1.0
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
    ("delay_between_requests", -1.2),
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


@pytest.fixture
def valid_global() -> Dict[str, Any]:
    return {
        "included_classes": ["Aves", "Insecta"],
        "verbose": True,
        "overwrite": False,
    }

@pytest.fixture
def valid_paths(tmp_path) -> Dict[str, Any]:
    return {
        "src_dataset": str(tmp_path / "src"),
        "dst_dataset": str(tmp_path / "dst"),
        "web_crawl_output_json": "crawl.json",
        "output_dir": str(tmp_path / "out"),
    }

@pytest.fixture
def valid_web_crawl() -> Dict[str, Any]:
    return {
        "total_pages": 10,
        "base_url": "https://example.com",
        "delay_between_requests": 2.0,
    }

@pytest.fixture
def valid_train_val() -> Dict[str, Any]:
    return {
        "train_size": 0.8,
        "random_state": 42,
        "dominant_threshold": 0.5,
    }

# --- tests for non-dict input ---

def test_validate_not_dict_raises():
    with pytest.raises(ConfigError, match="root should be a dict, got list"):
        validate_dict_against_dataclass([], GlobalConfig, path="root")

# --- tests for GlobalConfig ---

def test_global_valid(valid_global):
    # Should not raise
    validate_dict_against_dataclass(valid_global, GlobalConfig, path="global")

@pytest.mark.parametrize("key", ["included_classes", "verbose", "overwrite"])
def test_global_missing_key(valid_global, key):
    d = valid_global.copy()
    del d[key]
    with pytest.raises(ConfigError, match=f"Missing key '{key}' in section 'global'"):
        validate_dict_against_dataclass(d, GlobalConfig, path="global")

def test_global_included_classes_not_list(valid_global):
    d = valid_global.copy()
    d["included_classes"] = "notalist"
    with pytest.raises(ConfigError, match="global.included_classes should be a list of strings"):
        validate_dict_against_dataclass(d, GlobalConfig, path="global")

def test_global_included_classes_element_not_str(valid_global):
    d = valid_global.copy()
    d["included_classes"] = ["Aves", 123]
    with pytest.raises(ConfigError, match="global.included_classes should be a list of strings"):
        validate_dict_against_dataclass(d, GlobalConfig, path="global")

def test_global_verbose_not_bool(valid_global):
    d = valid_global.copy()
    d["verbose"] = "yes"
    with pytest.raises(ConfigError, match="global.verbose should be a boolean"):
        validate_dict_against_dataclass(d, GlobalConfig, path="global")

# --- tests for PathsConfig ---

def test_paths_valid(valid_paths):
    validate_dict_against_dataclass(valid_paths, PathsConfig, path="paths")

@pytest.mark.parametrize("key,wrong,err", [
    ("src_dataset", 123, "paths.src_dataset should be a string"),
    ("dst_dataset", None, "paths.dst_dataset should be a string"),
    ("web_crawl_output_json", ["a"], "paths.web_crawl_output_json should be a string"),
    ("output_dir", 5.5, "paths.output_dir should be a string"),
])
def test_paths_wrong_type(valid_paths, key, wrong, err):
    d = valid_paths.copy()
    d[key] = wrong
    with pytest.raises(ConfigError, match=err):
        validate_dict_against_dataclass(d, PathsConfig, path="paths")

# --- tests for WebCrawlConfig ---

def test_web_crawl_valid(valid_web_crawl):
    validate_dict_against_dataclass(valid_web_crawl, WebCrawlConfig, path="web_crawl")

@pytest.mark.parametrize("key,wrong,err", [
    ("total_pages", 0.0, "web_crawl.total_pages should be an integer"),
    ("base_url", 123,      "web_crawl.base_url should be a string"),
    ("delay_between_requests", "1", "web_crawl.delay_between_requests should be a float"),
])
def test_web_crawl_wrong_type(valid_web_crawl, key, wrong, err):
    d = valid_web_crawl.copy()
    d[key] = wrong
    with pytest.raises(ConfigError, match=err):
        validate_dict_against_dataclass(d, WebCrawlConfig, path="web_crawl")

# --- tests for TrainValSplitConfig ---

def test_train_val_valid(valid_train_val):
    validate_dict_against_dataclass(valid_train_val, TrainValSplitConfig, path="train_val_split")

@pytest.mark.parametrize("key,wrong,err", [
    ("train_size", "0.8", "train_val_split.train_size should be a float"),
    ("random_state", -1.0, "train_val_split.random_state should be an integer"),
    ("dominant_threshold", None, "train_val_split.dominant_threshold should be a float"),
])
def test_train_val_wrong_type(valid_train_val, key, wrong, err):
    d = valid_train_val.copy()
    d[key] = wrong
    with pytest.raises(ConfigError, match=err):
        validate_dict_against_dataclass(d, TrainValSplitConfig, path="train_val_split")


@dataclass
class Inner:
    foo: int


@dataclass
class Outer:
    inner: Inner
    name: str


@dataclass
class Unsupported:
    data: Dict[str, int]


def test_recursive_valid():
    data = {"inner": {"foo": 42}, "name": "example"}
    validate_dict_against_dataclass(data, Outer, path="outer")


@pytest.mark.parametrize("bad_inner", [
    {},
    {"foo": "a_string"}
])
def test_recursive_invalid(bad_inner):
    data = {"inner": bad_inner, "name": "something"}
    with pytest.raises(ConfigError) as exc:
        validate_dict_against_dataclass(data, Outer, path="outer")
    msg = str(exc.value)
    assert "Missing key 'foo' in section 'outer.inner'" in msg or "outer.inner.foo should be an integer" in msg


def test_outer_missing_name():
    data = {"inner": {"foo": 1}}
    with pytest.raises(ConfigError, match="Missing key 'name' in section 'outer'"):
        validate_dict_against_dataclass(data, Outer, "outer")


def test_unsupported_field_type():
    payload = {"data": {"a": 1}}
    with pytest.raises(ConfigError, match="Unsupported field type"):
        validate_dict_against_dataclass(payload, Unsupported, "unsupported")