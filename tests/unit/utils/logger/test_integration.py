import pytest

from utils.logger import create_logger, logging_function, logging_handler


class TestLoggerIntegration:
    def test_normal_flow(self, read_logs, dummy_context):
        logger_handler = create_logger("handlers.sample")
        logger_service = create_logger("services.sample")

        @logging_function(logger_service)
        def do_work(x, y):
            return x + y

        @logging_handler(logger_handler)
        def handler(event, context):
            result = do_work(10, 20)
            return {"result": result}

        result = handler({"input": "data"}, dummy_context)

        assert result == {"result": 30}
        logs = read_logs()

        assert len(logs) >= 4

        event_log = logs[0]
        assert "event and environment variables" in event_log["message"]
        assert event_log["identifier"] == "handlers.sample"
        assert "function_name" in event_log

        start_function_log = logs[1]
        assert "start function" in start_function_log["message"]
        assert start_function_log["identifier"] == "services.sample"
        assert "function_name" in start_function_log

        success_function_log = logs[2]
        assert "succeeded function" in success_function_log["message"]
        assert success_function_log["identifier"] == "services.sample"
        assert success_function_log["data"]["Return"] == 30
        assert "function_name" in success_function_log

        handler_return_log = logs[3]
        assert "handler return" in handler_return_log["message"]
        assert handler_return_log["identifier"] == "handlers.sample"
        assert handler_return_log["data"]["Return"] == {"result": 30}
        assert "function_name" in handler_return_log

        for log in logs:
            assert log["service"] == "test-service"
            assert log["function_name"] == dummy_context.function_name

    def test_exception_flow(self, read_logs, dummy_context):
        logger_handler = create_logger("handlers.sample")
        logger_service = create_logger("services.sample")

        @logging_function(logger_service)
        def do_work():
            raise RuntimeError("work failed")

        @logging_handler(logger_handler)
        def handler(event, context):
            do_work()
            return "ok"

        with pytest.raises(RuntimeError, match="work failed"):
            handler({}, dummy_context)

        logs = read_logs()
        assert len(logs) >= 3

        event_log = logs[0]
        assert event_log["identifier"] == "handlers.sample"

        failure_log = next(
            (log for log in logs if "failed function" in log.get("message", "")),
            None,
        )
        assert failure_log is not None
        assert failure_log["identifier"] == "services.sample"
        assert "RuntimeError" in failure_log["data"]["Error"]["type"]
        assert "function_name" in failure_log

        handler_error_log = logs[-1]
        assert handler_error_log["level"] == "ERROR"
        assert handler_error_log["identifier"] == "handlers.sample"
        assert "function_name" in handler_error_log

    def test_multiple_service_layers(self, read_logs, dummy_context):
        logger_handler = create_logger("handlers.api")
        logger_service_a = create_logger("services.a")
        logger_service_b = create_logger("services.b")

        @logging_function(logger_service_b)
        def low_level_work(x):
            return x * 2

        @logging_function(logger_service_a)
        def high_level_work(x):
            return low_level_work(x) + 1

        @logging_handler(logger_handler)
        def handler(event, context):
            result = high_level_work(5)
            return {"result": result}

        result = handler({}, dummy_context)

        assert result == {"result": 11}
        logs = read_logs()

        identifiers = [log["identifier"] for log in logs]
        assert identifiers[0] == "handlers.api"
        assert "services.a" in identifiers
        assert "services.b" in identifiers

        for log in logs:
            assert log["service"] == "test-service"
            assert "function_name" in log
