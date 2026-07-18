import json
import logging
from typing import override


class JsonFormatter(logging.Formatter):
    @override
    def format(self, record: logging.LogRecord) -> str:
        data = {
            "time": self.formatTime(record),
            "level": record.levelname,
            "logger": record.name,
            "message": record.getMessage(),
        }
        if record.exc_info:
            data["exc"] = self.formatException(record.exc_info)

        return json.dumps(data, ensure_ascii=False)


def setup_logging(level: int = logging.INFO) -> None:
    handler = logging.StreamHandler()
    handler.setFormatter(JsonFormatter())
    logging.basicConfig(level=level, handlers=[handler])

    module_logger = logging.getLogger(__name__)
    root = logging.getLogger()
    for lg in root.manager.loggerDict.values():
        if isinstance(lg, logging.Logger) and lg is not root and lg.handlers:
            module_logger.debug(f"Clearing handlers for logger: {lg.name}")
            lg.handlers.clear()
            # logger.propagate = True  # TODO: in case of some loggers not propagating
