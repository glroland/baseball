""" Double Event

Runner hit a double game event.
"""
import logging
from events.base_event import BaseEvent

logger = logging.getLogger(__name__)

class DoubleEvent(BaseEvent):
    """ Double Event """

    def get_play_type_code(self) -> str:
        """ Get the play type code. """
        return "2"

    def handle(self):
        logger.info("Player Hit Double")

        self.game_state.action_advance_runner("B", "2")
