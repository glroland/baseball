""" Walk Event

Runner walked game event.
"""
import logging
from events.base_event import BaseEvent

logger = logging.getLogger(__name__)

class WalkEvent(BaseEvent):
    """ Walk Event """

    def handle(self):
        """ Walk the player
        """
        logger.info("Batter Walked")

        self.game_state.action_advance_runner("B", "1")
