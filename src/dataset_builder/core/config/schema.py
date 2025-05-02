from dataclasses import dataclass
from typing import List


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