import re

from ut_calculation_builder.Utilities.logger import logger


class CommonUtils:
    def __init__(self):
        pass

    def get_pattern_string(self, project_n_type):
        try:
            if project_n_type:
                pattern_string = "l1_\\d+(?:[a-z]*(?:\\d+)*_\\d+dollar)*tag_\\d+|l1_\\d+dollartag_\\d+|tag_\\d+"
            else:
                pattern_string = "site_\\d+(?:[a-z]*_\\d+dollar)*tag_\\d+|site_\\d+dollartag_\\d+|tag_\\d+"
            return re.compile(pattern_string)
        except Exception as e:
            logger.exception(e)


