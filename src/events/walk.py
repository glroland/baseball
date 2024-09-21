""" Walk Event

Runner walked game event.
"""
import logging
from events.base_event import BaseEvent

logger = logging.getLogger(__name__)

class WalkEvent(BaseEvent):
    """ Walk Event """

    def handle(self, game_at_bat, op_details):
        """ Walk the player
        
            game_at_bat - game at bat
            op_details - offensive play details
        """
        logger.info("Batter Walked")
            
        self.advance_runner(game_at_bat, "B", "1")
