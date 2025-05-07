import os
import tempfile
import json
from pathlib import Path
from unittest.mock import patch

import pytest
from dataset_builder.visualization.visualizer import visualize_ppf_multiple_species_class  # type: ignore
from dataset_builder.core.exceptions import PipelineError  # type: ignore


@pytest.fixture
def dummy_properties_file():
    with tempfile.TemporaryDirectory() as tmpdir:
        path = Path(tmpdir) / "data.json"
        with open(path, "w", encoding="utf-8") as f:
            json.dump({
                "Aves": {"sp1": 100, "sp2": 50, "sp3": 30},
                "Mammalia": {"sp2": 30, "sp4": 70}
            }, f)
        yield str(path)


def test_saves_plot_to_file(dummy_properties_file):
    with tempfile.TemporaryDirectory() as tmpdir:
        save_path = os.path.join(tmpdir, "plot.png")
        with patch("dataset_builder.visualization.visualizer._prepare_data_cdf_ppf") as mock_prepare:
            mock_prepare.side_effect = [
                (["sp1", "sp2", "sp3"], [100, 50, 30]),
                (["sp2", "sp4"], [30, 70])
            ]
            visualize_ppf_multiple_species_class(
                dummy_properties_file, ["Aves", "Mammalia"], save_path=save_path
            )
        assert os.path.isfile(save_path)


def test_skips_if_plot_exists(dummy_properties_file):
    with tempfile.TemporaryDirectory() as tmpdir:
        save_path = os.path.join(tmpdir, "already_there.png")
        Path(save_path).touch()
        with patch("dataset_builder.visualization.visualizer._prepare_data_cdf_ppf") as mock_prepare:
            visualize_ppf_multiple_species_class(
                dummy_properties_file, ["Aves"], save_path=save_path, overwrite=False
            )
            mock_prepare.assert_not_called()


def test_handles_missing_data(dummy_properties_file, capsys):
    with pytest.raises(PipelineError, match="no data to visualize"):
        with patch("dataset_builder.visualization.visualizer._prepare_data_cdf_ppf", return_value=None):
            visualize_ppf_multiple_species_class(
                dummy_properties_file, ["NonexistentClass"]
            )
    out = capsys.readouterr().out
    assert "No data found for" in out


def test_show_plot_mode(dummy_properties_file):
    with patch("dataset_builder.visualization.visualizer._prepare_data_cdf_ppf") as mock_prepare:
        mock_prepare.side_effect = [
            (["sp1", "sp2", "sp3"], [100, 50, 30]),
            (["sp2", "sp4"], [30, 70])
        ]
        with patch("matplotlib.pyplot.show") as mock_show:
            visualize_ppf_multiple_species_class(
                dummy_properties_file, ["Aves", "Mammalia"], save_path=None
            )
            mock_show.assert_called_once()