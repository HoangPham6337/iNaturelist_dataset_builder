from dataset_builder.core.config.schema import (
    Config,
    PathsConfig,
    GlobalConfig,
    WebCrawlConfig,
    TrainValSplitConfig,
)


def _ask(prompt, default=None, cast=str):
    raw = input(f"{prompt} [{default}]: ")
    return cast(raw.strip() if raw.strip() else default)


def _str_to_bool(x: str) -> bool:
    x = x.strip().lower()
    if x in {"true", "yes", "1"}:
        return True
    elif x in {"false", "no", "0"}:
        return False
    else:
        raise ValueError(f"Invalid boolean value: {x}")


def build_interactive_config() -> Config:
    """
    Launches an interactive command-line wizard to construct a `Config` object.

    This function walks the user through each section of the configuration—
    Global settings, Paths, Web Crawl parameters, and Train/Validation split—
    prompting for each value (with sensible defaults).  User responses are
    cast to the appropriate types (`bool`, `int`, `float`, or `List[str]`)
    before assembling the final `Config` dataclass.

    Returns:
        Config: A fully populated configuration object, with:
            - global_ (GlobalConfig): included_classes, verbose, overwrite
            - paths (PathsConfig): src_dataset, dst_dataset, web_crawl_output_json, output_dir
            - web_crawl (WebCrawlConfig): total_pages, base_url, delay_between_requests
            - train_val_split (TrainValSplitConfig): train_size, random_state, dominant_threshold
    """
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
