""" Fielders Choice Event

Fielding issue leading to walk game event.
"""
import logging
from events.base_event import BaseEvent
from events.constants import Modifiers
from model.action_record import ActionRecord
from model.game_at_bat import GameAtBat

logger = logging.getLogger(__name__)

class FieldersChoiceEvent(BaseEvent):
    """ Fielders Choice Event """

    def handle(self, game_at_bat : GameAtBat, action : ActionRecord):
        """ Walk the player
        
            game_at_bat - game at bat
            details - offensive play details
        """
        # Identify due to
        fielder = ""
        if len(details) > 0:
            fielder = details.pop(0)

        # Check Modifiers
        due_to = ""
        if len(game_at_bat.modifiers) > 0:
            modifier = game_at_bat.modifiers.pop(0)
            if modifier == Modifiers.DOUBLE_PLAY:
                due_to = "Double Play"

        logger.info("Batter Walked due to Fielders Choice (Fielder = %s). %s ", fielder, due_to)

        self.advance_runner(game_at_bat, "B", "1")
