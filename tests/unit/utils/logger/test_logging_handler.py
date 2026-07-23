import pytest

from utils.logger import create_logger, logging_handler


class TestLoggingHandler:
    def test_normal_success(self, read_logs, dummy_context):
        logger = create_logger("handler")

        @logging_handler(logger)
        def handler(event, context):
            return {"status": "ok"}

        event = {"test": "data"}
        result = handler(event, dummy_context)

        assert result == {"status": "ok"}
        logs = read_logs()
        assert len(logs) >= 2

        event_log = logs[0]
        assert "event and environment variables" in event_log["message"]
        assert "event" in event_log["data"]
        assert "env" in event_log["data"]
        assert event_log["data"]["event"] == event
        assert isinstance(event_log["data"]["env"], dict)
        assert event_log["identifier"] == "handler"

        return_log = logs[-1]
        assert "handler return" in return_log["message"]
        assert return_log["data"]["Return"] == {"status": "ok"}
        assert return_log["identifier"] == "handler"

    def test_env_excludes_sensitive_keys(self, read_logs, dummy_context, monkeypatch):
        monkeypatch.setenv("AWS_ACCESS_KEY_ID", "AKIATEST")
        monkeypatch.setenv("AWS_SECRET_ACCESS_KEY", "secret_value")
        monkeypatch.setenv("AWS_SESSION_TOKEN", "session_token")
        monkeypatch.setenv("AWS_XRAY_DAEMON_ADDRESS", "127.0.0.1:2000")

        logger = create_logger("handler")

        @logging_handler(logger)
        def handler(event, context):
            return "ok"

        handler({}, dummy_context)

        logs = read_logs()
        event_log = logs[0]
        env = event_log["data"]["env"]

        excluded_keys = [
            "AWS_ACCESS_KEY_ID",
            "AWS_SECRET_ACCESS_KEY",
            "AWS_SESSION_TOKEN",
            "AWS_XRAY_DAEMON_ADDRESS",
        ]
        for key in excluded_keys:
            assert key not in env

    def test_with_return_false(self, read_logs, dummy_context):
        logger = create_logger("handler")

        @logging_handler(logger, with_return=False)
        def handler(event, context):
            return "result"

        handler({}, dummy_context)

        logs = read_logs()
        for log in logs:
            assert "handler return" not in log["message"]

    def test_exception(self, read_logs, dummy_context):
        logger = create_logger("handler")

        @logging_handler(logger)
        def handler(event, context):
            raise ValueError("handler error")

        with pytest.raises(ValueError, match="handler error"):
            handler({}, dummy_context)

        logs = read_logs()
        assert len(logs) >= 2

        error_log = logs[-1]
        assert error_log["level"] == "ERROR"
        assert "Error" in error_log["data"]
        assert "ValueError" in error_log["data"]["Error"]["Type"]
        assert "handler error" in error_log["data"]["Error"]["Message"]

    def test_lambda_context_shared(self, read_logs, dummy_context):
        logger = create_logger("handler")

        @logging_handler(logger)
        def handler(event, context):
            logger.info("inside handler")
            return "ok"

        handler({}, dummy_context)

        logs = read_logs()
        assert len(logs) >= 3

        for log in logs:
            assert log["identifier"] == "handler"
            assert "function_name" in log
            assert log["function_name"] == dummy_context.function_name

        inside_log = next(
            (log for log in logs if log["message"] == "inside handler"), None
        )
        assert inside_log is not None
