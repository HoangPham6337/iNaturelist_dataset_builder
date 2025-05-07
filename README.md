<br/>
<div align="center">

<h3 align="center">A modular dataset preparation toolkit for species-based classification pipelines.</h3>
<p align="center">
A flexible and fast dataset builder for iNaturalist-style species classification.
</p>
</div>

<a href='https://coveralls.io/github/HoangPham6337/iNaturelist_dataset_builder?branch=main'><img src='https://coveralls.io/repos/github/HoangPham6337/iNaturelist_dataset_builder/badge.svg?branch=main' alt='Coverage Status' /></a>

## About The Project
![Example Output](images/example.png)

`dataset_builder` is a modular toolkit designed to streamline the process of preparing image classification datasets, especially for biodiversity and species-based research projects.
It provides flexible CLI tools and Python APIs to help you:
- Organize images by species into training and validation folders.
- Apply filtering rules based on dominant species.
- Export dataset manifests in plain text or Parquet formats.
- Handle restricted dataset creation, cross-referencing, and species-level analysis.

This package is designed with iNaturelist 2017 dataset in mind. However, it should still helps you if you want to build a similar iNaturelist-style datasets or building your own species classifier.

The project follows the DRY principle and is designed with modularity and pipeline automation in mind.

You can use the CLI to quickly build datasets, or integrate it directly into your own ML pipeline.
### Built With

This package is written entirely in Python to ensure that it can run on multiple platform easily. I use the following packages to enable the high-level feature of the package.

- [Pandas](https://pandas.pydata.org/)
- [PyArrow](https://arrow.apache.org/docs/python/index.html)
- [tqdm](https://github.com/tqdm/tqdm)
- [scikit-learn](https://scikit-learn.org/stable/)
- [matplotlib](https://matplotlib.org/)
- [matplotlib-venn](https://python-graph-gallery.com/venn-diagram/)
- [BeautifulSoup4](https://www.crummy.com/software/BeautifulSoup/bs4/doc/)
## Getting Started

This project helps you build custom fine-tuning datasets from the INaturelist collection with minimal effort. It supports tasks such as filtering species, copying matched images, generating manifests, and preparing training/validation splits - all with configurable YAML pipelines.
Whether you are training a deep learning model or simply exploring biodiversity data, this toolkit gets your dataset in shape.
### Prerequisites

- `Python >= 3.11`
- Git
### Installation
```python
pip install dataset_builder_inat
```
For more details, check out the wiki [here](https://github.com/HoangPham6337/iNaturelist_dataset_builder/wiki/Ihttps://github.com/HoangPham6337/iNaturelist_dataset_buildernstallation)

## Usage

This package is designed to be used through its high-level Python APIs. The typical workflow is defined in a central Python script such as `main.py` (see below), which loads a config file and runs multiple dataset preparation stages.

**Step 1: Create a YAML config file (`config.yaml`)**
You can check out the details in the wiki [here](https://github.com/HoangPham6337/iNaturelist_dataset_builder/wiki/Configuration).

```yaml
global:
  included_classes: ["Aves", "Insecta"]
  verbose: false
  overwrite: false

paths:
  src_dataset: "iNaturelist_2017"
  dst_dataset: "haute_garonne"
  web_crawl_output_json: "./output/haute_garonne.json"
  output_dir: "./output"

web_crawl:
  total_pages: 104
  base_url: "https://www.inaturalist.org/check_lists/32961-Haute-Garonne-Check-List?page="
  delay_between_requests: 1

train_val_split:
  train_size: 0.8
  random_state: 42
  dominant_threshold: 0.9
```

**Step 2: Create the `main.py` or use the `dataset_orchestration.py` provided in release**

For more details, you can check out the wiki [here](https://github.com/HoangPham6337/iNaturelist_dataset_builder/wiki/Pipeline).

## Roadmap

- [x] Simplify `config.yaml` structure: group related options, add environmental variable support, introduce profiles (e.g., dev/prod).
- [x] Add advanced options to `train_val_split`: support stratified splitting, per-class balancing, and deterministic sampling for reproducibility.
- [x] Auto-generate `config.yaml` step-by-step from terminal prompts.
- [x] Built-in summary report: after pipeline finishes, output a Markdown or HTML report: species count, splits, coverage, etc. (show logs after each run)
- [x] Add support for export all manifests in Parquet format regardless of path format.
## Contributing

Contributions are welcome!

If you have suggestions for improvements or spot any issues, feel free to open an issue or submit a pull request.  
Please follow the existing project structure and naming conventions when contributing.

To get started:

1. Fork the repo
2. Clone your fork locally:  
   `git clone https://github.com/HoangPham6337/iNaturelist_dataset_builder`
3. Create a new branch:  
   `git checkout -b feature/your-feature-name`
4. Make your changes and commit
5. Push to your fork:  
   `git push origin feature/your-feature-name`
6. Open a Pull Request

For major changes, please open an issue first to discuss what you’d like to change.
## License

Distributed under the MIT License. See [MIT License](https://opensource.org/licenses/MIT) for more information.
## Contact

Pham Xuan Hoang – [LinkedIn](https://www.linkedin.com/in/xuan-hoang-pham/) – hoangphamat0407@gmail.com

