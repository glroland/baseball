""" Homerun Event

Runner hit a home run game event.
"""
import logging
from events.base_event import BaseEvent

logger = logging.getLogger(__name__)

class HomerunEvent(BaseEvent):
    """ Homerun Event """

    def handle(self, game_at_bat, op_details):
        logger.info("Out of Park Home Run hit by batter")
        if len(game_at_bat.modifiers) > 0:
            game_at_bat.hit_to_location = game_at_bat.modifiers.pop(0)
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
