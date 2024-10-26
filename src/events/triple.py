""" Triple Event

Runner hit a triple game event.
"""
import logging
from events.base_event import BaseEvent

logger = logging.getLogger(__name__)

class TripleEvent(BaseEvent):
    """ Triple Event """

    def get_play_type_code(self) -> str:
        """ Get the play type code. """
        return "3"

    def handle(self):
        logger.info("Player Hit Triple.")

        self.game_state.action_advance_runner("B", "3")
