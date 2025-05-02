import yaml
import pytest
from dataclasses import asdict

from dataset_builder.core.config import load_config, save_config  # type: ignore
from dataset_builder.core.config import Config, WebCrawlConfig, PathsConfig, GlobalConfig, TrainValSplitConfig  # type: ignore


def test_load_config_valid(tmp_path):
    data = {"foo": 1, "bar": ["a", "b"]}
    p = tmp_path / "config.yaml"
    p.write_text(yaml.safe_dump(data))
    loaded = load_config(str(p))
    assert loaded == data


def test_load_config_file_not_found():
    with pytest.raises(FileNotFoundError):
        load_config("no_such_file.yaml")


def test_load_config_invalid_yaml(tmp_path):
    p = tmp_path / "config.yaml"
    p.write_text("key: [1, 2")
    with pytest.raises(yaml.YAMLError):
        load_config(str(p))


def test_load_config_not_dict(tmp_path):
    p = tmp_path / "config.yaml"
    p.write_text(yaml.safe_dump([1, 2, 3]))
    with pytest.raises(ValueError, match="Expect YAML to be a dictionary"):
        load_config(str(p))


def test_save_config_dict(tmp_path):
    data = {"alpha": 42, "beta": ["x", "y"]}
    p = tmp_path / "out.yaml"
    save_config(data, str(p))
    reloaded = yaml.safe_load(p.read_text())
    assert reloaded == data


def test_save_config_dataclass(tmp_path):
    gc = GlobalConfig(["Aves"], verbose=True, overwrite=False)
    pc = PathsConfig("a", "b", "c.json", "d")
    wc = WebCrawlConfig(total_pages=2, base_url="https://x", delay_between_requests=3)
    tvs = TrainValSplitConfig(train_size=0.7, random_state=0, dominant_threshold=0.4)
    cfg = Config(global_=gc, paths=pc, web_crawl=wc, train_val_split=tvs)

    p = tmp_path / "out.yaml"
    save_config(cfg, str(p))

    reloaded = yaml.safe_load(p.read_text())
    assert reloaded == asdict(cfg)