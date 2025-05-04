from dataclasses import dataclass
from typing import List


@dataclass
class GlobalConfig:
    """Pipeline global settings."""
    included_classes: List[str]
    verbose: bool
    overwrite: bool


@dataclass
class PathsConfig:
    """Filesystem paths for source, destination, and outputs."""
    src_dataset: str
    dst_dataset: str
    web_crawl_output_json: str
    output_dir: str


@dataclass
class WebCrawlConfig:
    """Parameters controlling the web crawl (URL, pages, delay)."""
    total_pages: int
    base_url: str
    delay_between_requests: float


@dataclass
class TrainValSplitConfig:
    """Settings for train/validation split (ratio, seed, threshold)."""
    train_size: float
    random_state: int
    dominant_threshold: float


@dataclass
class Config:
    """Aggregate configuration for all pipeline stages."""
    global_: GlobalConfig
    paths: PathsConfig
    web_crawl: WebCrawlConfig
    train_val_split: TrainValSplitConfig