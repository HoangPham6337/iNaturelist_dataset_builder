import dataclasses
from typing import List

from dataset_builder.core.config.schema import (  # type: ignore
    GlobalConfig,
    PathsConfig,
    WebCrawlConfig,
    TrainValSplitConfig,
    Config
)


def test_global_config_schema():
    # field names and order
    names = [f.name for f in dataclasses.fields(GlobalConfig)]
    assert names == ["included_classes", "verbose", "overwrite"]

    # type annotations
    ann = GlobalConfig.__annotations__
    assert ann["included_classes"] == List[str]
    assert ann["verbose"] is bool
    assert ann["overwrite"] is bool

    # instantiation
    gc = GlobalConfig(["Aves", "Insecta"], verbose=False, overwrite=True)
    assert gc.included_classes == ["Aves", "Insecta"]
    assert gc.verbose is False
    assert gc.overwrite is True

    # asdict output
    assert dataclasses.asdict(gc) == {
        "included_classes": ["Aves", "Insecta"],
        "verbose": False,
        "overwrite": True
    }


def test_path_config_schema():
    # field names and order
    names = [f.name for f in dataclasses.fields(PathsConfig)]
    assert names == ["src_dataset", "dst_dataset", "web_crawl_output_json", "output_dir"]

    # type annotations
    ann = PathsConfig.__annotations__
    for key in names:
        assert ann[key] is str

    # instantiation
    pc = PathsConfig("a", "b", "c.json", "d")
    assert pc.src_dataset == "a"
    assert pc.dst_dataset == "b"
    assert pc.web_crawl_output_json == "c.json"
    assert pc.output_dir == "d"

    # asdict output
    assert dataclasses.asdict(pc) == {
        "src_dataset": "a",
        "dst_dataset": "b",
        "web_crawl_output_json": "c.json",
        "output_dir": "d"
    }


def test_web_crawl_config_schema():
    # field names and order
    names = [f.name for f in dataclasses.fields(WebCrawlConfig)]
    assert names == ["total_pages", "base_url", "delay_between_requests"]

    # type annotations
    ann = WebCrawlConfig.__annotations__
    assert ann["total_pages"] is int
    assert ann["base_url"] is str
    assert ann["delay_between_requests"] is float

    # instantiation
    wc = WebCrawlConfig(1000, "https://test.com", 1)
    assert wc.total_pages == 1000
    assert wc.base_url == "https://test.com"
    assert wc.delay_between_requests == 1

    # asdict output
    assert dataclasses.asdict(wc) == {
        "total_pages": 1000,
        "base_url": "https://test.com",
        "delay_between_requests": 1
    }


def test_train_val_split_config_schema():
    # field names and order
    names = [f.name for f in dataclasses.fields(TrainValSplitConfig)]
    assert names == ["train_size", "random_state", "dominant_threshold"]

    # type annotations
    ann = TrainValSplitConfig.__annotations__
    assert ann["train_size"] is float
    assert ann["random_state"] is int
    assert ann["dominant_threshold"] is float

    # instantiation
    tvsc = TrainValSplitConfig(0.8, 32, 0.5)
    assert tvsc.train_size == 0.8
    assert tvsc.random_state == 32
    assert tvsc.dominant_threshold == 0.5

    # asdict output
    assert dataclasses.asdict(tvsc) == {
        "train_size": 0.8,
        "random_state": 32,
        "dominant_threshold": 0.5
    }


def test_config_aggregates_config():
    gc = GlobalConfig(["Aves"], True, False)
    pc = PathsConfig("a", "b", "c.json", "d")
    wc = WebCrawlConfig(100, "https://test.com", 1)
    tvsc = TrainValSplitConfig(0.8, 30, 0.5)

    cfg = Config(gc, pc, wc, tvsc)

    # check correct types
    assert isinstance(cfg.global_, GlobalConfig)
    assert isinstance(cfg.paths, PathsConfig)
    assert isinstance(cfg.web_crawl, WebCrawlConfig)
    assert isinstance(cfg.train_val_split, TrainValSplitConfig)

    expected = {
        "global_": {
            "included_classes": ["Aves"],
            "verbose": True,
            "overwrite": False
        },
        "paths": {
            "src_dataset": "a",
            "dst_dataset": "b",
            "web_crawl_output_json": "c.json",
            "output_dir": "d"
        },
        "web_crawl": {
            "total_pages": 100,
            "base_url": "https://test.com",
            "delay_between_requests": 1
        },
        "train_val_split": {
            "train_size": 0.8,
            "random_state": 30,
            "dominant_threshold": 0.5
        }
    }
    assert dataclasses.asdict(cfg) == expected