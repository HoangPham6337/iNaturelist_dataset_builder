import pytest

from dataset_builder.core.exceptions import FailedOperation, ConfigError, AnalysisError, PipelineError


def test_exception_subclassing():
    assert issubclass(FailedOperation, PipelineError)
    assert issubclass(ConfigError, PipelineError)
    assert issubclass(AnalysisError, PipelineError)
    assert issubclass(PipelineError, Exception)


@pytest.mark.parametrize("exc_cls", [FailedOperation, ConfigError, AnalysisError])
def test_exception_str_and_instance(exc_cls):
    msg = "something went wrong"
    exc = exc_cls(msg)
    assert str(exc) == msg
    assert isinstance(exc, exc_cls)
    assert isinstance(exc, PipelineError)


def test_pipeline_error_without_message_is_empty_string():
    pe = PipelineError()
    assert str(pe) == ""
    assert isinstance(pe, Exception)


def test_raising_and_catching():
    with pytest.raises(ConfigError) as cm:
        raise ConfigError("bad config")
    assert str(cm.value) == "bad config"