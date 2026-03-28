"""Framework-specific error types.

These are intentionally small and explicit so callers can distinguish
validation, runtime adapter, judge parsing, and timeout failures.
"""


class ScenarioValidationError(ValueError):
    """Raised when scenario files violate schema/validation rules."""


class AdapterExecutionError(RuntimeError):
    """Raised when adapter interaction fails during execution."""


class JudgeParsingError(RuntimeError):
    """Raised when judge output cannot be normalized into contract models."""


class ScenarioTimeoutError(TimeoutError):
    """Raised when a scenario exceeds configured timeout."""
