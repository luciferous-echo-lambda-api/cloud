import logging
from base64 import b64encode
from dataclasses import asdict, is_dataclass
from datetime import datetime
from decimal import Decimal
from gzip import compress
from logging import DEBUG
from typing import TYPE_CHECKING

from aws_lambda_powertools import Logger as PowertoolsLogger
from aws_lambda_powertools.utilities.data_classes.common import DictWrapper
from pydantic import BaseModel

if TYPE_CHECKING:
    from collections.abc import Mapping


def custom_default(obj):
    if isinstance(obj, tuple) or isinstance(obj, set):
        return {"type": str(type(obj)), "items": list(obj)}
    if isinstance(obj, datetime):
        return {"type": str(type(obj)), "value": obj.isoformat()}
    if isinstance(obj, bytes):
        compressed = compress(obj, compresslevel=7)
        encoded = b64encode(compressed).decode()
        return {"type": "bytes (base64 encoded, gzip compressed)", "value": encoded}
    if isinstance(obj, Decimal):
        return num if (num := int(obj)) == obj else float(str(obj))
    if isinstance(obj, DictWrapper):
        return {"type": str(type(obj)), "value": obj.raw_event}
    if isinstance(obj, BaseModel):
        return {"type": str(type(obj)), "value": obj.model_dump()}
    if is_dataclass(obj):
        if isinstance(obj, type):
            return {"type": str(obj)}
        else:
            return asdict(obj)
    try:
        return {"type": str(type(obj)), "value": str(obj)}
    except Exception as e:
        return {
            "type": str(type(obj)),
            "failed to str": {"error": str(type(e)), "message": str(e)},
        }


class Logger:
    _powertools_logger: PowertoolsLogger
    _name: str

    def __init__(self, name: str):
        self._name = name
        self._powertools_logger = PowertoolsLogger(
            level=DEBUG, use_rfc3339=True, json_default=custom_default
        )

    def debug(
        self,
        msg: object,
        *args: object,
        exc_info: logging._ExcInfoType = None,
        stack_info: bool = False,
        stacklevel: int = 2,
        extra: Mapping[str, object] | None = None,
        **kwargs: object,
    ) -> None:
        self._powertools_logger.debug(
            msg=msg,
            *args,
            exc_info=exc_info,
            stack_info=stack_info,
            stacklevel=stacklevel,
            extra=extra,
            identifier=self._name,
            **kwargs,
        )

    def info(
        self,
        msg: object,
        *args: object,
        exc_info: logging._ExcInfoType = None,
        stack_info: bool = False,
        stacklevel: int = 2,
        extra: Mapping[str, object] | None = None,
        **kwargs: object,
    ) -> None:
        self._powertools_logger.info(
            msg=msg,
            *args,
            exc_info=exc_info,
            stack_info=stack_info,
            stacklevel=stacklevel,
            extra=extra,
            identifier=self._name,
            **kwargs,
        )

    def warning(
        self,
        msg: object,
        *args: object,
        exc_info: logging._ExcInfoType = None,
        stack_info: bool = False,
        stacklevel: int = 2,
        extra: Mapping[str, object] | None = None,
        **kwargs: object,
    ) -> None:
        self._powertools_logger.warning(
            msg=msg,
            *args,
            exc_info=exc_info,
            stack_info=stack_info,
            stacklevel=stacklevel,
            extra=extra,
            identifier=self._name,
            **kwargs,
        )

    def error(
        self,
        msg: object,
        *args: object,
        exc_info: logging._ExcInfoType = None,
        stack_info: bool = False,
        stacklevel: int = 2,
        extra: Mapping[str, object] | None = None,
        **kwargs: object,
    ) -> None:
        self._powertools_logger.error(
            msg=msg,
            *args,
            exc_info=exc_info,
            stack_info=stack_info,
            stacklevel=stacklevel,
            extra=extra,
            identifier=self._name,
            **kwargs,
        )

    def critical(
        self,
        msg: object,
        *args: object,
        exc_info: logging._ExcInfoType = None,
        stack_info: bool = False,
        stacklevel: int = 2,
        extra: Mapping[str, object] | None = None,
        **kwargs: object,
    ) -> None:
        self._powertools_logger.critical(
            msg=msg,
            *args,
            exc_info=exc_info,
            stack_info=stack_info,
            stacklevel=stacklevel,
            extra=extra,
            identifier=self._name,
            **kwargs,
        )

    def exception(
        self,
        msg: object,
        *args: object,
        exc_info: logging._ExcInfoType = True,
        stack_info: bool = False,
        stacklevel: int = 2,
        extra: Mapping[str, object] | None = None,
        **kwargs: object,
    ) -> None:
        self._powertools_logger.exception(
            msg=msg,
            *args,
            exc_info=exc_info,
            stack_info=stack_info,
            stacklevel=stacklevel,
            extra=extra,
            identifier=self._name,
            **kwargs,
        )
