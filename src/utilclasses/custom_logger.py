# Copyright (C) 2021 Josef Natanael
# 
# This file is part of BoyBot LINE bot.
# 
# BoyBot LINE bot is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
# 
# BoyBot LINE bot is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
# 
# You should have received a copy of the GNU General Public License
# along with BoyBot LINE bot.  If not, see <http://www.gnu.org/licenses/>.
# 
# This copyright notice and this permission notice shall be included in 
# all copies or substantial portions of the Software.

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
