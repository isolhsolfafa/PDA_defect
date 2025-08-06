import logging
import os
from config import log_config


def setup_logger(name: str = __name__) -> logging.Logger:
    """로거 설정 및 초기화"""
    # 로그 디렉토리 생성
    log_dir = os.path.dirname(log_config.log_file)
    if log_dir and not os.path.exists(log_dir):
        os.makedirs(log_dir)

    # 로거 생성
    logger = logging.getLogger(name)
    logger.setLevel(getattr(logging, log_config.log_level))

    # 기존 핸들러 제거 (중복 방지)
    for handler in logger.handlers[:]:
        logger.removeHandler(handler)

    # 콘솔 핸들러
    console_handler = logging.StreamHandler()
    console_handler.setLevel(getattr(logging, log_config.log_level))
    console_formatter = logging.Formatter(log_config.log_format)
    console_handler.setFormatter(console_formatter)

    # 파일 핸들러
    file_handler = logging.FileHandler(log_config.log_file, encoding="utf-8")
    file_handler.setLevel(getattr(logging, log_config.log_level))
    file_formatter = logging.Formatter(log_config.log_format)
    file_handler.setFormatter(file_formatter)

    # 핸들러 추가
    logger.addHandler(console_handler)
    logger.addHandler(file_handler)

    return logger


def flush_log(logger: logging.Logger):
    """로그 파일 플러시"""
    for handler in logger.handlers:
        if hasattr(handler, "flush"):
            handler.flush()
        if hasattr(handler, "stream") and hasattr(handler.stream, "fileno"):
            try:
                os.fsync(handler.stream.fileno())
            except (OSError, AttributeError):
                pass  # 일부 핸들러는 fileno()를 지원하지 않을 수 있음
