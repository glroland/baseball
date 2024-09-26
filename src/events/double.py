""" Double Event

Runner hit a double game event.
"""
import logging
from events.base_event import BaseEvent
from model.action_record import ActionRecord
from model.game_at_bat import GameAtBat

logger = logging.getLogger(__name__)

class DoubleEvent(BaseEvent):
    """ Double Event """

    def handle(self, game_at_bat : GameAtBat, action : ActionRecord):
        logger.info("Player Hit Double")

        self.advance_runner(game_at_bat, "B", "2")
