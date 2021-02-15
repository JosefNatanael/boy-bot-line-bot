import logging


logger = logging.getLogger(__name__)

NOTICE_LEVEL_NUM = 25
logging.addLevelName(NOTICE_LEVEL_NUM, "NOTICE")


def notice(self, message, *args, **kws):
    if self.isEnabledFor(NOTICE_LEVEL_NUM):
        self._log(NOTICE_LEVEL_NUM, message, args, **kws)


logging.Logger.notice = notice

_handler = logging.StreamHandler()
_handler.setLevel(NOTICE_LEVEL_NUM)

_format = logging.Formatter('%(levelname)s: %(message)s')
_handler.setFormatter(_format)


logger.addHandler(_handler)
logger.setLevel(NOTICE_LEVEL_NUM)
