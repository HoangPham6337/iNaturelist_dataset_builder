import os
import json
import tempfile
import matplotlib
matplotlib.use("Agg")  # Use non-interactive backend for testing
from unittest.mock import patch

from dataset_builder.visualization.visualizer import (  # type: ignore
    venn_diagram,
    _class_composition_bar_chart,
    _visualizing_ppf,
)


def create_dummy_species_file(filepath: str, data: dict):
    with open(filepath, "w", encoding="utf-8") as f:
        json.dump(data, f)


def test_venn_diagram_generation():
    with tempfile.TemporaryDirectory() as tmp:
        d1 = {
            "class_a": {"sp1": 10, "sp2": 5},
            "class_b": {"sp3": 3}
        }
        d2 = {
            "class_a": {"sp2": 6, "sp3": 2},
            "class_b": {"sp4": 1}
        }

        path1 = os.path.join(tmp, "src.json")
        path2 = os.path.join(tmp, "dst.json")
        out = os.path.join(tmp, "venn.png")
        create_dummy_species_file(path1, d1)
        create_dummy_species_file(path2, d2)

        venn_diagram(path1, path2, "src", "dst", "test", target_classes=["class_a"], save_path=out)
        assert os.path.exists(out)


def test_venn_diagram_show_plot_mode():
    with tempfile.TemporaryDirectory() as tmp:
        d1 = {
            "class_a": {"sp1": 10, "sp2": 5},
            "class_b": {"sp3": 3}
        }
        d2 = {
            "class_a": {"sp2": 6, "sp3": 2},
            "class_b": {"sp4": 1}
        }

        path1 = os.path.join(tmp, "src.json")
        path2 = os.path.join(tmp, "dst.json")
        create_dummy_species_file(path1, d1)
        create_dummy_species_file(path2, d2)

        with patch("matplotlib.pyplot.show") as mock_show:
            venn_diagram(path1, path2, "src", "dst", "test", target_classes=["class_a"])
            mock_show.assert_called_once()


def test_venn_diagram_generation_already_exist(capsys):
    with tempfile.TemporaryDirectory() as tmp:
        d1 = {
            "class_a": {"sp1": 10, "sp2": 5},
            "class_b": {"sp3": 3}
        }
        d2 = {
            "class_a": {"sp2": 6, "sp3": 2},
            "class_b": {"sp4": 1}
        }

        path1 = os.path.join(tmp, "src.json")
        path2 = os.path.join(tmp, "dst.json")
        out = os.path.join(tmp, "venn.png")
        with open(out, "w") as tmp_file:
            tmp_file.write("tada")
        create_dummy_species_file(path1, d1)
        create_dummy_species_file(path2, d2)

        venn_diagram(path1, path2, "src", "dst", "test", target_classes=["class_a"], save_path=out)
        assert "already exists, skipping creating" in  capsys.readouterr().out


def test_class_composition_bar_chart():
    with tempfile.TemporaryDirectory() as tmp:
        d = {
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
                "Passer domesticus": 2274,
                "Chordeiles acutipennis": 43,
                "Sayornis phoebe": 926,
                "Troglodytes troglodytes": 71,
                "Sporophila torqueola": 325,
                "Himantopus himantopus": 99,
                "Tringa incana": 118,
                "Buteo regalis": 97,
                "Apus apus": 29,
                "Megascops asio": 147,
                "Eremophila alpestris": 275,
                "Contopus sordidulus": 170,
                "Alectoris chukar": 55,
                "Catherpes mexicanus": 134,
                "Bubo virginianus": 603,
                "Poecile rufescens": 323,
                "Onychognathus morio": 18,
                "Piranga bidentata": 30,
                "Calidris pusilla": 128,
                "Calidris mauri": 210,
                "Accipiter nisus": 69,
                "Pipilo maculatus": 698,
                "Gavia stellata": 138,
            },
        }
        path = os.path.join(tmp, "properties.json")
        out = os.path.join(tmp, "bar.png")
        create_dummy_species_file(path, d)

        _class_composition_bar_chart(path, "Aves", save_path=out)
        assert os.path.exists(out)


def test_class_composition_bar_chart_show_plot_mode():
    with tempfile.TemporaryDirectory() as tmp:
        d = {
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
                "Passer domesticus": 2274,
                "Chordeiles acutipennis": 43,
                "Sayornis phoebe": 926,
                "Troglodytes troglodytes": 71,
                "Sporophila torqueola": 325,
                "Himantopus himantopus": 99,
                "Tringa incana": 118,
                "Buteo regalis": 97,
                "Apus apus": 29,
                "Megascops asio": 147,
                "Eremophila alpestris": 275,
                "Contopus sordidulus": 170,
                "Alectoris chukar": 55,
                "Catherpes mexicanus": 134,
                "Bubo virginianus": 603,
                "Poecile rufescens": 323,
                "Onychognathus morio": 18,
                "Piranga bidentata": 30,
                "Calidris pusilla": 128,
                "Calidris mauri": 210,
                "Accipiter nisus": 69,
                "Pipilo maculatus": 698,
                "Gavia stellata": 138,
            },
        }
        path = os.path.join(tmp, "properties.json")
        create_dummy_species_file(path, d)

        with patch("matplotlib.pyplot.show") as mock_show:
            _class_composition_bar_chart(path, "Aves")
            mock_show.assert_called_once()


def test_class_composition_bar_chart_no_species(capsys):
    with tempfile.TemporaryDirectory() as tmp:
        d = {
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
        path = os.path.join(tmp, "properties.json")
        out = os.path.join(tmp, "bar.png")
        create_dummy_species_file(path, d)

        _class_composition_bar_chart(path, "Insecta", save_path=out)
        assert "Class 'Insecta' not found" in capsys.readouterr().out


def test_class_composition_bar_chart_already_exists(capsys):
    with tempfile.TemporaryDirectory() as tmp:
        d = {
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
        path = os.path.join(tmp, "properties.json")
        out = os.path.join(tmp, "bar.png")
        create_dummy_species_file(path, d)
        out = os.path.join(tmp, "venn.png")
        with open(out, "w") as tmp_file:
            tmp_file.write("tada")

        _class_composition_bar_chart(path, "Aves", save_path=out, verbose=True)
        assert "already exists, skipping" in capsys.readouterr().out



def test_visualizing_ppf():
    with tempfile.TemporaryDirectory() as tmp:
        d = {
            "Mammalia": {
                "lion": 120,
                "tiger": 80,
                "bear": 20
            }
        }
        path = os.path.join(tmp, "properties.json")
        out = os.path.join(tmp, "ppf.png")
        create_dummy_species_file(path, d)

        _visualizing_ppf(path, "Mammalia", save_path=out, verbose=True)
        assert os.path.exists(out)


def test_visualizing_ppf_show_plot():
    with tempfile.TemporaryDirectory() as tmp:
        d = {
            "Mammalia": {
                "lion": 120,
                "tiger": 80,
                "bear": 20
            }
        }
        path = os.path.join(tmp, "properties.json")
        create_dummy_species_file(path, d)

        with patch("matplotlib.pyplot.show") as mock_show:
            _visualizing_ppf(path, "Mammalia", verbose=True)
            mock_show.assert_called_once()

def test_visualizing_ppf_already_exists(capsys):
    with tempfile.TemporaryDirectory() as tmp:
        d = {}
        path = os.path.join(tmp, "properties.json")
        out = os.path.join(tmp, "ppf.png")
        with open(out, "w") as tmp_file:
            tmp_file.write("tada")
        create_dummy_species_file(path, d)

        _visualizing_ppf(path, "Mammalia", save_path=out, verbose=True)
        assert "already exists, skipping" in capsys.readouterr().out


def test_visualizing_ppf_no_data(capsys):
    with tempfile.TemporaryDirectory() as tmp:
        d = {}
        path = os.path.join(tmp, "properties.json")
        out = os.path.join(tmp, "ppf.png")
        create_dummy_species_file(path, d)

        _visualizing_ppf(path, "Mammalia", save_path=out, verbose=True)
        assert "No data found for" in capsys.readouterr().out