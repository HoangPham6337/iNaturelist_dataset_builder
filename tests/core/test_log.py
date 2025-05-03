import pytest
import os
from datetime import datetime as real_datetime
from dataset_builder.core import log as log_mod  # type: ignore
from dataset_builder.core.log import initialize_logger, log  # type: ignore


def test_initialize_logger_default(tmp_path, monkeypatch):
    class DummyDatetime:
        @classmethod
        def now(cls):
            return real_datetime(2025, 1, 2, 3, 4, 5)
    
    monkeypatch.setattr(log_mod, "datetime", DummyDatetime)
    
    # Run initialization
    initialize_logger(log_dir=str(tmp_path))
    expected_filename = "log_2025-01-02_03-04-05.txt"
    expected_path = os.path.join(str(tmp_path), expected_filename)

    assert log_mod.LOG_FILE_PATH == expected_path
    assert os.path.isdir(str(tmp_path))


def test_initialize_logger_with_filename(tmp_path):
    initialize_logger(log_dir=str(tmp_path), filename="mylog.txt")
    expected_path = os.path.join(str(tmp_path), "mylog.txt")
    assert log_mod.LOG_FILE_PATH == expected_path


def test_log_writes_and_prints(tmp_path, capsys):
    initialize_logger(log_dir=str(tmp_path), filename="testlog.txt")
    log("hello world", verbose=True, level="DEBUG")

    captured = capsys.readouterr()
    assert "[DEBUG] hello world\n" in captured.out

    content = (tmp_path / "testlog.txt").read_text(encoding="utf-8")
    assert "[DEBUG] hello world\n" == content


def test_log_without_verbose(tmp_path, capsys):
    initialize_logger(log_dir=str(tmp_path), filename="silent.txt")
    # Log without printing
    log("quiet message", verbose=False, level="INFO")

    captured = capsys.readouterr()
    assert captured.out == ""  # no console output

    # File still receives the log
    content = (tmp_path / "silent.txt").read_text(encoding="utf-8")
    assert "[INFO] quiet message\n" == content


def test_log_appends(tmp_path):
    initialize_logger(log_dir=str(tmp_path), filename="append.txt")
    log("first", verbose=False, level="INFO")
    log("second", verbose=False, level="INFO")

    lines = (tmp_path / "append.txt").read_text(encoding="utf-8").splitlines()
    assert lines == ["[INFO] first", "[INFO] second"]


def test_log_before_initialize(monkeypatch, capsys):
    # ensure LOG_FILE_PATH is None
    monkeypatch.setattr(log_mod, "LOG_FILE_PATH", None)
    # logging prints only
    log("no file", verbose=True, level="WARN")
    captured = capsys.readouterr()
    assert "[WARN] no file\n" in captured.out
