import unittest
from unittest.mock import patch, MagicMock
import logging
import os
import sys

# Добавляем путь к корневому каталогу проекта
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from pytracelog.base import (
    PyTraceLog,
    LOGSTASH_HOST,
    LOGSTASH_PORT,
    OTEL_EXPORTER_JAEGER_AGENT_HOST,
)
from logstash_async.handler import AsynchronousLogstashHandler


class TestPyTraceLog(unittest.TestCase):

    @patch("pytracelog.base.basicConfig")
    def test_init_root_logger(self, mock_basic_config):
        PyTraceLog.init_root_logger(level=logging.INFO)
        self.assertEqual(len(logging.root.handlers), 2)
        mock_basic_config.assert_called_once()

    @patch("pytracelog.base.basicConfig")
    def test_init_root_logger_already_initialized(self, mock_basic_config):
        logging.root.handlers = [MagicMock()]
        PyTraceLog.init_root_logger(level=logging.INFO)
        self.assertEqual(len(logging.root.handlers), 1)
        mock_basic_config.assert_not_called()

    @patch("pytracelog.base.getLogRecordFactory")
    @patch("pytracelog.base.setLogRecordFactory")
    def test_extend_log_record(self, mock_set_factory, mock_get_factory):
        mock_get_factory.return_value = MagicMock()
        PyTraceLog.extend_log_record(test_attr="test_value")

        factory = logging.getLogRecordFactory()
        record = factory(
            name="test",
            level=logging.INFO,
            pathname=__file__,
            lineno=1,
            msg="test",
            args=(),
            exc_info=None,
        )

        self.assertEqual(record.test_attr, "test_value")
        mock_set_factory.assert_called_once()

    @patch.dict(os.environ, {LOGSTASH_HOST: "localhost", LOGSTASH_PORT: "5044"})
    @patch("pytracelog.base.AsynchronousLogstashHandler")
    @patch("pytracelog.base.basicConfig")
    def test_init_logstash_logger(self, mock_basic_config, mock_logstash_handler):
        PyTraceLog.init_logstash_logger(level=logging.INFO)
        self.assertEqual(len(logging.root.handlers), 1)
        mock_logstash_handler.assert_called_once()
        mock_basic_config.assert_called_once()

    @patch.dict(os.environ, {OTEL_EXPORTER_JAEGER_AGENT_HOST: "localhost"})
    @patch("pytracelog.base.JaegerExporter")
    @patch("pytracelog.base.TracerProvider")
    @patch("pytracelog.base.set_tracer_provider")
    @patch("pytracelog.base.LoggingInstrumentor")
    def test_init_tracer(
        self,
        mock_logging_instrumentor,
        mock_set_tracer_provider,
        mock_tracer_provider,
        mock_jaeger_exporter,
    ):
        PyTraceLog.init_tracer(service="test_service")
        mock_jaeger_exporter.assert_called_once()
        mock_tracer_provider.assert_called_once()
        mock_set_tracer_provider.assert_called_once()
        mock_logging_instrumentor().instrument.assert_called_once()

    @patch("pytracelog.base.basicConfig")
    def test_reset(self, mock_basic_config):
        PyTraceLog.init_root_logger(level=logging.INFO)
        PyTraceLog.reset()
        self.assertEqual(len(logging.root.handlers), 0)
        self.assertIsNone(PyTraceLog._old_factory)
        mock_basic_config.assert_called()


if __name__ == "__main__":
    unittest.main()
