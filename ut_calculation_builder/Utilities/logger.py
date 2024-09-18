import logging.handlers
import sys
from logging import StreamHandler

class LoggingConstants:
    LOG_NAME = "ut_pod_adx_timescale"
    LOG_LEVEL = "INFO"

logger = logging.getLogger(LoggingConstants.LOG_NAME)

formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s  - %(filename)s - %(module)s: %(funcName)s: '
                              '%(lineno)d - %(message)s')

console_handler = StreamHandler(sys.stdout)
console_handler.setFormatter(formatter)
