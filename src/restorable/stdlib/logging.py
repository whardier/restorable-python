from __future__ import annotations

import logging
from logging import Logger
from typing import Callable, cast

logger = logging.getLogger(__name__)

_acquire_lock = cast(Callable, getattr(logging, "_acquireLock"))  # noqa: B009
_release_lock = cast(Callable, getattr(logging, "_releaseLock"))  # noqa: B009
_clear_cache = cast(Callable, getattr(logging.root.manager, "_clear_cache"))  # noqa: B009


class RestorableLogging:
    def __enter__(self) -> None:
        _acquire_lock()

        self.root_manager_logger_dict = logging.root.manager.loggerDict
        self.root_handlers = logging.root.handlers
        self.root_filters = logging.root.filters

        self.logging_levels = {
            name: logger.level for name, logger in logging.root.manager.loggerDict.items() if isinstance(logger, Logger)
        }

        logging.root.manager.loggerDict = self.root_manager_logger_dict.copy()
        logging.root.handlers = self.root_handlers.copy()
        logging.root.filters = self.root_filters.copy()

        _clear_cache()
        _release_lock()

    def __exit__(self, exc_type, exc_val, exc_tb):
        _acquire_lock()

        logging.root.manager.loggerDict = self.root_manager_logger_dict
        logging.root.handlers = self.root_handlers
        logging.root.filters = self.root_filters

        for name, level in self.logging_levels.items():
            logging.getLogger(name).setLevel(level)

        _release_lock()
