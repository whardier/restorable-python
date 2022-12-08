from __future__ import annotations

import logging
from logging import Handler, Logger
from typing import Callable, cast

logger = logging.getLogger(__name__)

_acquire_lock = cast(Callable, getattr(logging, "_acquireLock"))  # noqa: B009
_release_lock = cast(Callable, getattr(logging, "_releaseLock"))  # noqa: B009
_clear_cache = cast(Callable, getattr(logging.root.manager, "_clear_cache"))  # noqa: B009


class RestorableLogging:
    def __enter__(self) -> None:
        _acquire_lock()

        self.logger_class = logging.getLoggerClass()
        self.log_record_factory = logging.getLogRecordFactory()

        self.default_formatter = getattr(logging, "_defaultFormatter")  # noqa: B009

        self.root_manager_logger_class = logging.root.manager.loggerClass
        self.root_manager_log_record_factory = logging.root.manager.logRecordFactory
        self.root_manager_logger_dict = logging.root.manager.loggerDict
        self.root_handlers = logging.root.handlers
        self.root_filters = logging.root.filters

        self.root_handler_attrs: dict[Handler, dict[str, object]] = {}

        self.logging_levels = {
            name: logger.level for name, logger in logging.root.manager.loggerDict.items() if isinstance(logger, Logger)
        }

        logging.root.manager.loggerDict = self.root_manager_logger_dict.copy()
        logging.root.handlers = self.root_handlers.copy()

        for handler in self.root_handlers:
            self.root_handler_attrs[handler] = {
                "level": getattr(handler, "level", None),
                "formatter": getattr(handler, "formatter", None),
                "filters": getattr(handler, "filters", None),
            }

        logging.root.filters = self.root_filters.copy()

        _clear_cache()
        _release_lock()

    def __exit__(self, exc_type, exc_val, exc_tb):
        _acquire_lock()

        logging.setLoggerClass(self.logger_class)
        logging.setLogRecordFactory(self.log_record_factory)

        setattr(logging, "_defaultFormatter", self.default_formatter)  # noqa: B010

        logging.root.manager.loggerClass = self.root_manager_logger_class
        logging.root.manager.logRecordFactory = self.root_manager_log_record_factory
        logging.root.manager.loggerDict = self.root_manager_logger_dict
        logging.root.handlers = self.root_handlers

        for root_handler in self.root_handler_attrs:
            _attrs = self.root_handler_attrs[root_handler]
            setattr(root_handler, "level", _attrs["level"])  # noqa: B010
            setattr(root_handler, "formatter", _attrs["formatter"])  # noqa: B010
            setattr(root_handler, "filters", _attrs["filters"])  # noqa: B010

        logging.root.filters = self.root_filters

        for name, level in self.logging_levels.items():
            logging.getLogger(name).setLevel(level)

        _release_lock()
