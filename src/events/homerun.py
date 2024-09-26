""" Homerun Event

Runner hit a home run game event.
"""
import logging
from events.base_event import BaseEvent
from model.action_record import ActionRecord
from model.game_at_bat import GameAtBat

logger = logging.getLogger(__name__)

class HomerunEvent(BaseEvent):
    """ Homerun Event """

    def handle(self, game_at_bat : GameAtBat, action : ActionRecord):
        logger.info("Out of Park Home Run hit by batter")

        if game_at_bat.runner_on_3b:
            game_at_bat.runner_on_3b = False
            self.score(game_at_bat)
        if game_at_bat.runner_on_2b:
            game_at_bat.runner_on_2b = False
            self.score(game_at_bat)
        if game_at_bat.runner_on_1b:
            game_at_bat.runner_on_1b = False
            self.score(game_at_bat)
        self.score(game_at_bat)
