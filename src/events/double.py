""" Double Event

Runner hit a double game event.
"""
import logging
from events.base_event import BaseEvent
from model.action_record import ActionRecord
from model.game_state import GameState

logger = logging.getLogger(__name__)

class DoubleEvent(BaseEvent):
    """ Double Event """

    def handle(self, game_state : GameState, action : ActionRecord):
        logger.info("Player Hit Double")

        game_state.action_advance_runner("B", "2")
