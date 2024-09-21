""" Walk Event

Runner walked game event.
"""
import logging
from events.base_event import BaseEvent

logger = logging.getLogger(__name__)

class HitByPitchEvent(BaseEvent):
    """ Hit By Pitch Event """

    def handle(self, game_at_bat, op_details):
        """ Walk the player due to hit by pitch
        
            game_at_bat - game at bat
            op_details - offensive play details
        """
        logger.info("Batter Hit By Pitch")
            
        self.batter_progressed_runners(game_at_bat)