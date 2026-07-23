from dataclasses import dataclass
from datetime import datetime
from decimal import Decimal

from pydantic import BaseModel

from utils.logger import create_logger


class TestCreateLogger:
    def test_normal(self, read_logs):
        logger = create_logger("mod_a")
        logger.info("hello")

        logs = read_logs()
        assert len(logs) == 1
        log = logs[0]

        assert log["message"] == "hello"
        assert log["identifier"] == "mod_a"
        assert log["service"] == "test-service"
        assert log["level"] == "INFO"
        assert "timestamp" in log
        assert "T" in log["timestamp"]

    def test_identifier_differs_per_logger(self, read_logs):
        logger_a = create_logger("a")
        logger_b = create_logger("b")

        logger_a.info("from_a")
        logger_b.info("from_b")

        logs = read_logs()
        assert len(logs) == 2
        assert logs[0]["identifier"] == "a"
        assert logs[0]["message"] == "from_a"
        assert logs[1]["identifier"] == "b"
        assert logs[1]["message"] == "from_b"

    def test_service_shared_context(self, read_logs):
        logger_a = create_logger("mod_a")
        logger_b = create_logger("mod_b")
        logger_c = create_logger("mod_c")

        logger_a.info("msg_a")
        logger_b.info("msg_b")
        logger_c.info("msg_c")

        logs = read_logs()
        assert len(logs) == 3
        for log in logs:
            assert log["service"] == "test-service"
        assert logs[0]["identifier"] == "mod_a"
        assert logs[1]["identifier"] == "mod_b"
        assert logs[2]["identifier"] == "mod_c"

    def test_all_levels(self, read_logs):
        logger = create_logger("test_logger")

        logger.debug("debug msg")
        logger.info("info msg")
        logger.warning("warning msg")
        logger.error("error msg")
        logger.critical("critical msg")
        try:
            raise ValueError("test exception")
        except ValueError:
            logger.exception("exception msg")

        logs = read_logs()
        assert len(logs) == 6
        assert logs[0]["level"] == "DEBUG"
        assert logs[1]["level"] == "INFO"
        assert logs[2]["level"] == "WARNING"
        assert logs[3]["level"] == "ERROR"
        assert logs[4]["level"] == "CRITICAL"
        assert logs[5]["level"] == "ERROR"

        for log in logs:
            assert log["identifier"] == "test_logger"

    def test_extra_passthrough(self, read_logs):
        logger = create_logger("logger")

        logger.info("msg with extra", extra={"custom_key": "custom_value"})
        logger.info("msg with kwargs", another_key="another_value")

        logs = read_logs()
        assert len(logs) == 2

        assert logs[0]["custom_key"] == "custom_value"
        assert logs[1]["another_key"] == "another_value"

    def test_custom_default_serialization(self, read_logs):
        logger = create_logger("logger")

        now = datetime(2024, 4, 11, 15, 7, 17, 544914)
        data_dict = {
            "dt": now,
            "b": b"bytes_data",
            "decimal_int": Decimal("123"),
            "decimal_float": Decimal("123.45"),
        }
        logger.info("complex", data=data_dict)

        logs = read_logs()
        assert len(logs) == 1
        log = logs[0]
        assert "data" in log

        data = log["data"]
        assert data["dt"]["value"] == now.isoformat()
        assert data["b"]["type"] == "bytes (base64 encoded, gzip compressed)"
        assert isinstance(data["b"]["value"], str)
        assert data["decimal_int"] == 123
        assert data["decimal_float"] == 123.45

    def test_with_pydantic_model(self, read_logs):
        class SampleModel(BaseModel):
            name: str
            value: int

        logger = create_logger("logger")
        model = SampleModel(name="test", value=42)
        logger.info("pydantic", data={"model": model})

        logs = read_logs()
        assert len(logs) == 1
        assert "data" in logs[0]

    def test_with_dataclass(self, read_logs):
        @dataclass
        class SampleDataclass:
            name: str
            value: int

        logger = create_logger("logger")
        dc = SampleDataclass(name="test", value=42)
        logger.info("dataclass", data={"dc": dc})

        logs = read_logs()
        assert len(logs) == 1
        assert "data" in logs[0]
