# pylint: disable = too-many-arguments
import logging

import pytest

from hambone.logger import logger


@pytest.fixture()
def log_level_env_var(monkeypatch, request):
    monkeypatch.delenv("LOGLEVEL", False)
    monkeypatch.setenv("LOGLEVEL", request.param)
    monkeypatch.setattr(
        logger, "log_level", getattr(logging, request.param, logging.INFO)
    )
    monkeypatch.setattr(
        logger.create_logger,
        "__defaults__",
        (getattr(logging, request.param, logging.INFO),),
    )


# --------------------- create_logger ------------------------------


@pytest.mark.parametrize(
    ("log_level_env_var", "logger_name", "expected_level"),
    (
        ("DEBUG", "debug_test", 10),
        ("INFO", "info_test", 20),
        ("CRITICAL", "crit_test", 50),
        ("ERROR", "error_test", 40),
        ("WARNING", "warning_test", 30),
    ),
    indirect=["log_level_env_var"],
    ids=("debug", "info", "critical", "error", "warning"),
)
@pytest.mark.usefixtures("log_level_env_var")
def test_create_logger_returns_a_named_logger_with_log_level_set_by_environment_variable(
    logger_name: str, expected_level: int
) -> None:
    lgr = logger.create_logger(logger_name)
    assert (
        lgr.getEffectiveLevel() == expected_level
    ), f"expected {expected_level} got {lgr.getEffectiveLevel()}"


@pytest.mark.parametrize(
    ("log_level_env_var", "logger_name", "expected_level"),
    (("NOTSET", "notset_test", 30),),
    indirect=["log_level_env_var"],
    ids=("notset",),
)
@pytest.mark.usefixtures("log_level_env_var")
def test_create_logger_returns_a_named_logger_with_log_level_set_by_parents_log_level_when_log_level_is_not_set(
    logger_name: str, expected_level: int
) -> None:
    lgr = logger.create_logger(logger_name)
    assert (
        lgr.parent.getEffectiveLevel() == expected_level
    ), f"expected {expected_level} got {lgr.parent.getEffectiveLevel()}"


@pytest.mark.parametrize(
    ("log_level_env_var", "logger_name", "expected_level"),
    (
        ("DBEUG", "debug_test", 10),
        ("INFO", "info_test", 20),
        ("CRITICAL", "crit_test", 50),
        ("ERROR", "error_test", 40),
        ("WARNING", "warning_test", 30),
    ),
    indirect=["log_level_env_var"],
    ids=("debug", "info", "critical", "error", "warning"),
)
@pytest.mark.usefixtures("log_level_env_var")
def test_create_logger_returns_a_named_logger_with_log_level_set_log_level_param(
    logger_name: str, expected_level: int
) -> None:
    lgr = logger.create_logger(logger_name, expected_level)
    assert lgr.getEffectiveLevel() == expected_level


# --------------------- error_to_dict ------------------------------


@pytest.mark.parametrize("error", [BaseException("test")])
def test_error_to_dict(monkeypatch, error):
    with monkeypatch.context() as m:
        m.setattr(
            "traceback.TracebackException.from_exception", lambda x: "testing trace"
        )
        assert logger.error_to_dict(error) == {
            "errorMsg": str(error),
            "stacktrace": "testing trace",
        }
