import unittest
from unittest.mock import MagicMock
from logging import LogRecord, ERROR
from pytracelog.logging.handlers import StdoutHandler, StderrHandler, TracerHandler


class TestHandlers(unittest.TestCase):
    def test_stdout_handler(self):
        handler = StdoutHandler()
        self.assertTrue(
            handler.filter(
                LogRecord(
                    name="",
                    level=ERROR - 1,
                    pathname="",
                    lineno=0,
                    msg="",
                    args=(),
                    exc_info=None,
                )
            )
        )
        self.assertFalse(
            handler.filter(
                LogRecord(
                    name="",
                    level=ERROR,
                    pathname="",
                    lineno=0,
                    msg="",
                    args=(),
                    exc_info=None,
                )
            )
        )

    def test_stderr_handler(self):
        handler = StderrHandler()
        self.assertFalse(
            handler.filter(
                LogRecord(
                    name="",
                    level=ERROR - 1,
                    pathname="",
                    lineno=0,
                    msg="",
                    args=(),
                    exc_info=None,
                )
            )
        )
        self.assertTrue(
            handler.filter(
                LogRecord(
                    name="",
                    level=ERROR,
                    pathname="",
                    lineno=0,
                    msg="",
                    args=(),
                    exc_info=None,
                )
            )
        )

    def test_tracer_handler(self):
        record = LogRecord(
            name="",
            level=ERROR,
            pathname="",
            lineno=0,
            msg="test message",
            args=(),
            exc_info=None,
        )
        handler = TracerHandler()
        span_mock = MagicMock()
        handler.emit(record)
        span_mock.add_event.assert_called_with(
            name="test message", attributes={"message": "test message"}
        )


if __name__ == "__main__":
    unittest.main()
