from uuid import UUID

import pytest
from freezegun import freeze_time

from utils.logger import create_logger, logging_function


class TestLoggingFunction:
    def test_normal_success(self, read_logs):
        logger = create_logger("service")

        @logging_function(logger)
        def fn(x, y):
            return x + y

        result = fn(10, 20)

        assert result == 30
        logs = read_logs()
        assert len(logs) >= 2

        start_log = logs[0]
        assert "start function" in start_log["message"]
        assert "fn" in start_log["message"]
        assert start_log["data"]["FunctionName"] == "fn"
        assert "CallID" in start_log["data"]
        assert start_log["data"]["Args"] == [10, 20]
        assert start_log["data"]["KwArgs"] == {}
        assert start_log["identifier"] == "service"

        success_log = logs[1]
        assert "succeeded function" in success_log["message"]
        assert "fn" in success_log["message"]
        assert success_log["data"]["CallID"] == start_log["data"]["CallID"]
        assert success_log["data"]["Return"] == 30
        assert "Duration" in success_log["data"]
        assert "TotalSeconds" in success_log["data"]["Duration"]
        assert "str" in success_log["data"]["Duration"]
        assert success_log["identifier"] == "service"

    def test_with_kwargs(self, read_logs):
        logger = create_logger("service")

        @logging_function(logger)
        def fn(x, y=100):
            return x + y

        result = fn(10, y=20)
        assert result == 30

        logs = read_logs()
        start_log = logs[0]
        assert start_log["data"]["Args"] == [10]
        assert start_log["data"]["KwArgs"] == {"y": 20}

    def test_write_false_skips_entry_logs(self, read_logs):
        logger = create_logger("service")

        @logging_function(logger, write=False)
        def fn(x):
            return x * 2

        result = fn(5)
        assert result == 10

        logs = read_logs()
        assert len(logs) == 0

    def test_with_return_false(self, read_logs):
        logger = create_logger("service")

        @logging_function(logger, with_return=False)
        def fn():
            return 42

        fn()

        logs = read_logs()
        assert len(logs) == 2
        success_log = logs[1]
        assert "Return" not in success_log["data"]

    def test_with_args_false(self, read_logs):
        logger = create_logger("service")

        @logging_function(logger, with_args=False)
        def fn(x, y):
            return x + y

        fn(1, 2)

        logs = read_logs()
        assert len(logs) == 2
        start_log = logs[0]
        success_log = logs[1]

        assert "Args" not in start_log["data"]
        assert "KwArgs" not in start_log["data"]
        assert "Args" not in success_log["data"]
        assert "KwArgs" not in success_log["data"]

    def test_failure(self, read_logs):
        logger = create_logger("service")

        @logging_function(logger)
        def fn():
            raise ValueError("test error")

        with pytest.raises(ValueError, match="test error"):
            fn()

        logs = read_logs()
        assert len(logs) >= 2

        start_log = logs[0]
        assert "start function" in start_log["message"]

        failure_log = logs[1]
        assert "failed function" in failure_log["message"]
        assert "ValueError" in failure_log["data"]["Error"]["type"]
        assert "test error" in failure_log["data"]["Error"]["message"]
        assert failure_log["identifier"] == "service"

    def test_failure_with_write_false_still_logs(self, read_logs):
        logger = create_logger("service")

        @logging_function(logger, write=False)
        def fn():
            raise RuntimeError("error")

        with pytest.raises(RuntimeError):
            fn()

        logs = read_logs()
        assert len(logs) == 1
        assert "failed function" in logs[0]["message"]

    @freeze_time("2024-04-11 15:07:17.544914")
    def test_uuid_and_time_frozen(self, read_logs, monkeypatch):
        import sys

        lf_module = sys.modules["utils.logger.logging_function"]
        logger = create_logger("service")

        fixed_uuid = UUID("12345678-1234-5678-1234-567812345678")
        monkeypatch.setattr(lf_module, "uuid7", lambda: fixed_uuid)

        @logging_function(logger)
        def fn():
            return "result"

        fn()

        logs = read_logs()
        start_log = logs[0]
        success_log = logs[1]

        assert start_log["data"]["CallID"] == str(fixed_uuid)
        assert success_log["data"]["CallID"] == str(fixed_uuid)
        assert success_log["data"]["Duration"]["TotalSeconds"] == 0.0
