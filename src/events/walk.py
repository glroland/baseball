""" Walk Event

Runner walked game event.
"""
import logging
from events.base_event import BaseEvent

logger = logging.getLogger(__name__)

class WalkEvent(BaseEvent):
    """ Walk Event """

    def get_play_type_code(self) -> str:
        """ Get the play type code. """
        return "W"

    def handle(self):
        """ Walk the player
        """
        logger.info("Batter Walked")

        self.game_state.action_advance_runner("B", "1")
