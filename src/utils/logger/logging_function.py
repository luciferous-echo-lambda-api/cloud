from datetime import datetime
from functools import wraps
from typing import Callable
from uuid import uuid7
from zoneinfo import ZoneInfo

from .logger import Logger

jst = ZoneInfo("Asia/Tokyo")


def logging_function(
    logger: Logger,
    *,
    write: bool = True,
    with_return: bool = True,
    with_args: bool = True,
) -> Callable:
    def decorator(func: Callable) -> Callable:
        @wraps(func)
        def process(*args, **kwargs):
            name_function = func.__name__
            id_call = str(uuid7())
            dt_start = datetime.now(tz=jst)
            try:
                data_start = {"FunctionName": name_function, "CallID": id_call}
                if with_args:
                    data_start["Args"] = args
                    data_start["KwArgs"] = kwargs
                if write:
                    logger.debug(
                        f'start function "{name_function}" ({id_call})', data=data_start
                    )

                result = func(*args, **kwargs)

                dt_end = datetime.now(tz=jst)
                delta = dt_end - dt_start
                data_end = {
                    "FunctionName": name_function,
                    "CallID": id_call,
                    "Duration": {
                        "str": str(delta),
                        "TotalSeconds": delta.total_seconds(),
                    },
                }
                if with_args:
                    data_end["Args"] = args
                    data_end["KwArgs"] = kwargs
                if with_return:
                    data_end["Return"] = result
                if write:
                    logger.debug(
                        f'succeeded function "{name_function}" ({id_call})',
                        data=data_end,
                    )

                return result
            except Exception as e:
                dt_end = datetime.now(tz=jst)
                delta = dt_end - dt_start

                logger.debug(
                    f'failed function "{name_function}" ({id_call})',
                    exc_info=True,
                    data={
                        "FunctionName": name_function,
                        "CallID": id_call,
                        "Duration": {
                            "str": str(delta),
                            "TotalSeconds": delta.total_seconds(),
                        },
                        "Args": args,
                        "KwArgs": kwargs,
                        "Error": {"type": str(type(e)), "message": str(e)},
                    },
                )
                raise

        return process

    return decorator
