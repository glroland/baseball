""" Fly Ball Error Event

Fly Ball Error game event.
"""
import logging
from events.base_event import BaseEvent

logger = logging.getLogger(__name__)

class FlyBallErrorEvent(BaseEvent):
    """ Fly Ball Error Event """

    def handle(self):
        """ Fielding team made an error on a fly ball.  Putting the batter on base.
        """
        logger.info("Fielding error on a fly ball.  Putting batter on base.")

        self.game_state.action_advance_runner("B", "1")
