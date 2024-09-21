""" Fielders Choice Event

Fielding issue leading to walk game event.
"""
import logging
from events.base_event import BaseEvent
from events.constants import Modifiers

logger = logging.getLogger(__name__)

class FieldersChoiceEvent(BaseEvent):
    """ Fielders Choice Event """

    def handle(self, game_at_bat, op_details):
        """ Walk the player
        
            game_at_bat - game at bat
            op_details - offensive play details
        """
        # Identify due to
        fielder = ""
        if len(op_details) > 0:
            fielder = op_details.pop(0)

        # Check Modifiers
        due_to = ""
        if len(game_at_bat.modifiers) > 0:
            modifier = game_at_bat.modifiers.pop(0)
            if modifier == Modifiers.DOUBLE_PLAY:
                due_to = "Double Play"

        logger.info(f"Batter Walked due to Fielders Choice (Fielder = {fielder}).  {due_to} ")

        self.batter_progressed_runners(game_at_bat)
