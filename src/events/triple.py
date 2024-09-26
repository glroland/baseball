""" Triple Event

Runner hit a triple game event.
"""
import logging
from events.base_event import BaseEvent
from model.action_record import ActionRecord
from model.game_at_bat import GameAtBat

logger = logging.getLogger(__name__)

class TripleEvent(BaseEvent):
    """ Triple Event """

    def handle(self, game_at_bat : GameAtBat, action : ActionRecord):
        logger.info("Player Hit Triple.")

        self.advance_runner(game_at_bat, "B", "3")
