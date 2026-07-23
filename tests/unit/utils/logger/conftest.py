import json
import logging

import pytest


@pytest.fixture(autouse=True)
def reset_powertools_logger_state():
    """各テスト前後で Powertools Logger の Python logging 状態をリセットする。

    Powertools Logger は初回 `__init__` 時に `sys.stdout` を StreamHandler に保存し、
    `logger.init = True` でキャッシュする。pytest は各テストで capfd/capsys 用に
    `sys.stdout` を差し替えるため、リセットしないと最初のテストで bind した
    古い capture stream に書き込み続けて捕捉できない。
    """
    logger_name = "test-service"

    def _reset() -> None:
        py_logger = logging.getLogger(logger_name)
        py_logger.handlers = []
        py_logger.filters = []
        for attr in ("init", "powertools_handler"):
            if hasattr(py_logger, attr):
                delattr(py_logger, attr)

    _reset()
    yield
    _reset()


@pytest.fixture
def read_logs(capfd):
    """capfd から stdout を読み、各行を JSON 解析したリストを返す関数を提供する fixture。"""

    def _read():
        output = capfd.readouterr().out
        if not output.strip():
            return []
        return [json.loads(line) for line in output.strip().split("\n") if line]

    return _read
