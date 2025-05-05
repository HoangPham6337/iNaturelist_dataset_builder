import json
import os
import pytest
from unittest.mock import patch

from dataset_builder.visualization.visualizer import _visualize_class  # type: ignore

@pytest.fixture
def minimal_species_json(tmp_path):
    data = {
            "Aves": {
                "Corvus corax": 882,
                "Coccothraustes coccothraustes": 52,
                "Somateria mollissima": 145,
                "Myioborus miniatus": 49,
                "Crax rubra": 46,
                "Anas crecca": 456,
                "Thryothorus ludovicianus": 574,
                "Coragyps atratus": 831,
                "Turdus philomelos": 144,
                "Columbina inca": 560,
                "Chroicocephalus ridibundus": 295,
                "Scopus umbretta": 30,
                "Ocyphaps lophotes": 41,
                "Spizella atrogularis": 37,
                "Pheucticus melanocephalus": 370,
                "Phalacrocorax auritus": 1726,
                "Rallus crepitans": 43,
                "Euphonia elegantissima": 41,
                "Tyrannus dominicensis": 52,
                "Sitta canadensis": 325,
                "Chen rossii": 130,
            },
        }
    json_path = tmp_path / "mock_composition.json"
    with open(json_path, "w") as f:
        json.dump(data, f)
    return json_path

def test_visualize_class_creates_plots(tmp_path, minimal_species_json, capsys):
    export_dir = tmp_path / "export"
    dataset_name = "test_dataset"
    species_class = "Aves"

    with patch("matplotlib.pyplot.savefig") as mock_savefig, patch("matplotlib.pyplot.close"):
        _visualize_class(
            str(minimal_species_json),
            species_class,
            str(export_dir),
            dataset_name,
            verbose=False,
            overwrite=True,
        )

    expected_bar = os.path.join(export_dir, dataset_name, "composition", f"{dataset_name}_{species_class}_bar.png")
    expected_ppf = os.path.join(export_dir, dataset_name, "ppf", f"{dataset_name}_{species_class}_ppf.png")

    # These paths should have been passed to plt.savefig
    mock_savefig.assert_any_call(expected_bar, bbox_inches="tight")
    mock_savefig.assert_any_call(expected_ppf, bbox_inches="tight")
    assert "Processing" in capsys.readouterr().out