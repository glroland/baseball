""" Wild Pitch Event

Wild pitch game event.
"""
import logging
from events.base_event import BaseEvent

logger = logging.getLogger(__name__)

class WildPitchEvent(BaseEvent):
    """ Wild Pitch Event """

    def handle(self):
        """ Wild pitch event
        
            game_at_bat - game at bat
            action - offensive play details
        """
        logger.info("Wild Pitch Event.  Assuming to be coupled with batter action or advancement.")
