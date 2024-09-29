""" Homerun Event

Runner hit a home run game event.
"""
import logging
from events.base_event import BaseEvent
from model.action_record import ActionRecord
from model.game_state import GameState

logger = logging.getLogger(__name__)

class HomerunEvent(BaseEvent):
    """ Homerun Event """

    def handle(self, game_state : GameState, action : ActionRecord):
        logger.info("Out of Park Home Run hit by batter")

        game_state.action_advance_runner("B", "H")
