'''
https://pypi.python.org/pypi/JSON-log-formatter
'''


import logging
from datetime import datetime

import json

BUILTIN_ATTRS = {
    'args',
    'asctime',
    'created',
    'exc_info',
    'exc_text',
    'filename',
    'funcName',
    'levelname',
    'levelno',
    'lineno',
    'module',
    'msecs',
    'message',
    'msg',
    'name',
    'pathname',
    'process',
    'processName',
    'relativeCreated',
    'stack_info',
    'thread',
    'threadName',
}


class JSONFormatter(logging.Formatter):
    """JSON log formatter.

    Usage example::

        import logging

        import json_log_formatter

        json_handler = logging.FileHandler(filename='/var/log/my-log.json')
        json_handler.setFormatter(json_log_formatter.JSONFormatter())

        logger = logging.getLogger('my_json')
        logger.addHandler(json_handler)

        logger.info('Sign up', extra={'referral_code': '52d6ce'})

    The log file will contain the following log record (inline)::

        {
            "message": "Sign up",
            "time": "2015-09-01T06:06:26.524448",
            "referral_code": "52d6ce"
        }

    """
    json_lib = json

    def format(self, record):
        message = record.getMessage()
        extra = self.extra_from_record(record)
        vals = [record.__dict__[item] for item in self._fmt]
        extra.update(dict(zip(self._fmt, vals)))
        json_record = self.json_record(message, extra, record)
        self.mutate_json_record(json_record)
        return self.json_lib.dumps(json_record)

    def extra_from_record(self, record):
        """Returns `extra` dict you passed to logger.

        The `extra` keyword argument is used to populate the `__dict__` of
        the `LogRecord`.

        """
        return {
            attr_name: record.__dict__[attr_name]
            for attr_name in record.__dict__
            if attr_name not in BUILTIN_ATTRS
        }

    def json_record(self, message, extra, record):
        """Prepares a JSON payload which will be logged.

        Override this method to change JSON log format.

        :param message: Log message, e.g., `logger.info(msg='Sign up')`.
        :param extra: Dictionary that was passed as `extra` param
            `logger.info('Sign up', extra={'referral_code': '52d6ce'})`.
        :param record: `LogRecord` we got from `JSONFormatter.format()`.
        :return: Dictionary which will be passed to JSON lib.

        """
        extra['message'] = message
        if 'time' not in extra:
            extra['time'] = datetime.utcnow()
        return extra

    def mutate_json_record(self, json_record):
        """Override it to convert fields of `json_record` to needed types.

        Default implementation converts `datetime` to string in ISO8601 format.

        """
        for attr_name in json_record:
            attr = json_record[attr_name]
            if isinstance(attr, datetime):
                json_record[attr_name] = attr.isoformat()
