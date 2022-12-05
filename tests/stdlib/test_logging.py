import logging

from restorable.stdlib.logging import RestorableLogging


def get_all_logging_levels():
    return {
        name: logger.level
        for name, logger in logging.root.manager.loggerDict.items()
        if isinstance(logger, logging.Logger)
    }


def get_all_logging_handlers():
    return {
        name: logger.handlers
        for name, logger in logging.root.manager.loggerDict.items()
        if isinstance(logger, logging.Logger)
    }


def test_logging_simple():
    logging.basicConfig(level=logging.DEBUG)

    foo = logging.getLogger("foo")
    foo.setLevel(logging.DEBUG)

    assert logging.getLogger("foo").level == logging.DEBUG
    assert logging.getLogger("bar").level == 0

    levels = get_all_logging_levels()
    handlers = get_all_logging_handlers()

    logger_dict = logging.root.manager.loggerDict.copy()

    with RestorableLogging():
        foo.setLevel(logging.WARNING)
        bar = logging.getLogger("bar")
        bar.setLevel(logging.INFO)
        bar.info("message")

    assert logging.root.manager.loggerDict == logger_dict
    assert levels == get_all_logging_levels()
    assert handlers == get_all_logging_handlers()
