from .logger import Logger


def create_logger(name: str) -> Logger:
    return Logger(name=name)
