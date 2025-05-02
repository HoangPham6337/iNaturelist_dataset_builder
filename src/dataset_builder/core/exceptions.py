class PipelineError(Exception):
    """Base class for all pipeline-related exceptions."""

    pass


class FailedOperation(PipelineError):
    """External or recoverable failure (e.g., network, disk)."""

    def __init__(self, message: str):
        super().__init__(message)


class ConfigError(PipelineError):
    """Bad or missing configuration."""

    def __init__(self, message: str):
        super().__init__(message)


class AnalysisError(PipelineError):
    """Failure during dataset analysis or statistics."""

    def __init__(self, message: str):
        super().__init__(message)
