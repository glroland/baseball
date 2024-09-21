""" Fielders Choice Event

Fielding issue leading to walk game event.
"""
import logging
from events.base_event import BaseEvent

logger = logging.getLogger(__name__)

class FieldersChoiceEvent(BaseEvent):
    """ Fielders Choice Event """

    def handle(self, game_at_bat, op_details):
        """ Walk the player
        
            game_at_bat - game at bat
            op_details - offensive play details
        """
        due_to = ""
        if len(op_details) > 0:
            due_to = op_details.pop(0)
        logger.info("Batter Walked due to Fielders Choice - {due_to}")

        self.batter_progressed_runners(game_at_bat)
