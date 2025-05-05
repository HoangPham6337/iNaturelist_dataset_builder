import pytest
from unittest.mock import patch

from dataset_builder.manifest.identifying_dominant_species import _identifying_dominant_species  # type: ignore
from dataset_builder.core.exceptions import PipelineError  # type: ignore


@pytest.fixture
def mock_species_data():
    # species names and sorted image counts
    # [0.52631579 0.78947368 0.94736842 1.0]
    return (["sp1", "sp2", "sp3", "sp4"], [100, 50, 30, 10])


def test_threshold_60_percent(mock_species_data):
    with patch("dataset_builder.manifest.identifying_dominant_species._prepare_data_cdf_ppf", return_value=mock_species_data):
        result = _identifying_dominant_species("some/path.json", 0.6, ["class_a"])
    print(result["class_a"])
    
    assert result["class_a"] == ["sp1", "sp2"]


def test_threshold_90_percent(mock_species_data):
    with patch("dataset_builder.manifest.identifying_dominant_species._prepare_data_cdf_ppf", return_value=mock_species_data):
        result = _identifying_dominant_species("some/path.json", 0.90, ["class_a"])
    
    assert result["class_a"] == ["sp1", "sp2", "sp3"]


def test_zero_threshold(mock_species_data):
    with patch("dataset_builder.manifest.identifying_dominant_species._prepare_data_cdf_ppf", return_value=mock_species_data):
        with pytest.raises(PipelineError, match="is too low to select any meaningful"):
            _identifying_dominant_species("some/path.json", 0.0, ["class_a"])


def test_full_threshold(mock_species_data):
    with patch("dataset_builder.manifest.identifying_dominant_species._prepare_data_cdf_ppf", return_value=mock_species_data):
        result = _identifying_dominant_species("some/path.json", 1.0, ["class_a"])

    assert set(result["class_a"]) == {"sp1", "sp2", "sp3", "sp4"}


def test_empty_result_logs_warning(capsys):
    with patch("dataset_builder.manifest.identifying_dominant_species._prepare_data_cdf_ppf", return_value=([], [])):
        result = _identifying_dominant_species("some/path.json", 0.5, ["class_a"])
    
    assert result["class_a"] == []  # returns empty list
    assert "No data available for class_a" in capsys.readouterr().out


def test_prepare_data_failure_raises():
    with patch("dataset_builder.manifest.identifying_dominant_species._prepare_data_cdf_ppf", return_value=None):
        with pytest.raises(PipelineError, match="Data preparation failed for class_a"):
            _identifying_dominant_species("some/path.json", 0.5, ["class_a"])


def test_multiple_classes_mixed_behavior(mock_species_data):
    def prepare_data_side_effect(path, cls):
        return mock_species_data if cls == "class_good" else None

    with patch("dataset_builder.manifest.identifying_dominant_species._prepare_data_cdf_ppf", side_effect=prepare_data_side_effect):
        with pytest.raises(PipelineError):
            _identifying_dominant_species("some/path.json", 0.5, ["class_good", "class_bad"])


def test_negative_threshold_raises(mock_species_data):
    with patch("dataset_builder.manifest.identifying_dominant_species._prepare_data_cdf_ppf", return_value=mock_species_data):
        with pytest.raises(PipelineError, match="Threshold must be between 0 and 1"):
            _identifying_dominant_species("dummy.json", -0.1, ["class_a"])


def test_threshold_above_1_raises(mock_species_data):
    with patch("dataset_builder.manifest.identifying_dominant_species._prepare_data_cdf_ppf", return_value=mock_species_data):
        with pytest.raises(PipelineError, match="Threshold must be between 0 and 1"):
            _identifying_dominant_species("dummy.json", 1.5, ["class_a"])


def test_zero_total_images_triggers_warning(capsys):
    with patch("dataset_builder.manifest.identifying_dominant_species._prepare_data_cdf_ppf", return_value=(["sp1", "sp2"], [0, 0])):
        result = _identifying_dominant_species("dummy.json", 0.5, ["class_a"])
    
    assert result["class_a"] == []
    assert "No data available for class_a" in capsys.readouterr().out