import pytest
from dataset_builder.core.config.interactive_builder import (  # type: ignore
    _str_to_bool, build_interactive_config
)
from dataset_builder.core.config.schema import (  # type: ignore
    Config, GlobalConfig, PathsConfig, WebCrawlConfig, TrainValSplitConfig
)

def test_str_to_bool_accepts_true_values():
    for val in ("true", "True", "YES", "1"):
        assert _str_to_bool(val) is True

def test_str_to_bool_accepts_false_values():
    for val in ("false", "False", "no", "0"):
        assert _str_to_bool(val) is False

def test_str_to_bool_rejects_invalid():
    with pytest.raises(ValueError):
        _str_to_bool("notabool")

def test_build_interactive_config_defaults(monkeypatch):
    """
    If the user just presses Enter at every prompt (i.e. returns ""),
    build_interactive_config() should pick up all the default values.
    """
    # monkeypatch input() so it always returns "" -> default is used
    monkeypatch.setattr("builtins.input", lambda prompt: "")

    cfg = build_interactive_config()

    # check types
    assert isinstance(cfg, Config)
    assert isinstance(cfg.global_, GlobalConfig)
    assert isinstance(cfg.paths, PathsConfig)
    assert isinstance(cfg.web_crawl, WebCrawlConfig)
    assert isinstance(cfg.train_val_split, TrainValSplitConfig)

    assert cfg.global_.included_classes == ["Aves", "Insecta"]
    assert cfg.global_.verbose is False
    assert cfg.global_.overwrite is False

    assert cfg.paths.src_dataset == "./data/train_val_images"
    assert cfg.paths.dst_dataset == "./data/haute_garonne"
    assert cfg.paths.web_crawl_output_json == "./output/haute_garonne.json"
    assert cfg.paths.output_dir == "./output"

    assert cfg.web_crawl.total_pages == 104
    assert cfg.web_crawl.base_url.startswith("https://")
    assert cfg.web_crawl.delay_between_requests == 1

    assert cfg.train_val_split.train_size == 0.8
    assert cfg.train_val_split.random_state == 42
    assert cfg.train_val_split.dominant_threshold == 0.5


def test_build_interactive_config_custom(monkeypatch):
    """
    Feed a custom sequence of answers and verify they are parsed correctly.
    """
    answers = iter([
        # global
        "Fish,Mammal",  # included_classes
        "yes",          # verbose
        "1",            # overwrite

        # paths
        "/in/src",      # src
        "/out/dst",     # dst
        "crawl.json",   # json_out
        "/final/out",   # outdir

        # web crawl
        "7",            # total_pages
        "http://foo",   # base_url
        "3",            # delay

        # train/val split
        "0.75",         # train_size
        "123",          # random_state
        "0.2",          # threshold
    ])
    monkeypatch.setattr("builtins.input", lambda prompt: next(answers))

    cfg = build_interactive_config()

    # global
    assert cfg.global_.included_classes == ["Fish", "Mammal"]
    assert cfg.global_.verbose is True
    assert cfg.global_.overwrite is True

    # paths
    assert cfg.paths.src_dataset == "/in/src"
    assert cfg.paths.dst_dataset == "/out/dst"
    assert cfg.paths.web_crawl_output_json == "crawl.json"
    assert cfg.paths.output_dir == "/final/out"

    # web crawl
    assert cfg.web_crawl.total_pages == 7
    assert cfg.web_crawl.base_url == "http://foo"
    assert cfg.web_crawl.delay_between_requests == 3

    # train/val split
    assert cfg.train_val_split.train_size == pytest.approx(0.75)
    assert cfg.train_val_split.random_state == 123
    assert cfg.train_val_split.dominant_threshold == pytest.approx(0.2)
