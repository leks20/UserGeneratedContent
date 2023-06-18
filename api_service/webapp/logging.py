import logging

import logstash

from conf.config import settings


class RequestIdFilter(logging.Filter):
    def __init__(self):
        super().__init__()
        self._request_id = ''

    def filter(self, record):
        record.request_id = self._request_id
        return True


logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)
handler = logstash.LogstashHandler(
    settings.logstash_handler_host,
    settings.logstash_handler_port,
    settings.logstash_handler_version,
)
filter_instance = RequestIdFilter()
handler.addFilter(filter_instance)
logger.addHandler(handler)
