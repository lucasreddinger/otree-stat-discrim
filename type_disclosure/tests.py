#-*- coding: utf-8 -*-
from __future__ import division

import random

from otree.common import Currency as c, currency_range

from . import pages
from ._builtin import Bot
from .models import Constants


class PlayerBot(Bot):
    """Bot that plays one round"""

    def play_round(self):
        self.submit(pages.MyPage)
        self.submit(pages.Results)

    def validate_play(self):
        pass
