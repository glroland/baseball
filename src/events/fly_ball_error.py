""" Fly Ball Error Event

Fly Ball Error game event.
"""
import logging
from events.base_event import BaseEvent

logger = logging.getLogger(__name__)

class FlyBallErrorEvent(BaseEvent):
    """ Fly Ball Error Event """

    def handle(self, game_at_bat, op_details):
        """ Fielding team made an error on a fly ball.  Putting the batter on base.
        
            game_at_bat - game at bat
            op_details - offensive play details
        """
        details = op_details.pop()
        logger.info("Fielding error on a fly ball by {details}.  Putting batter on base.")

        self.advance_runner(game_at_bat, "B", "1")
