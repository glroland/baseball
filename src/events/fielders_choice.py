""" Fielders Choice Event

Fielding issue leading to walk game event.
"""
import logging
from events.base_event import BaseEvent
from events.constants import Modifiers

logger = logging.getLogger(__name__)

class FieldersChoiceEvent(BaseEvent):
    """ Fielders Choice Event """

    def get_play_type_code(self) -> str:
        """ Get the play type code. """
        return "C"

    def handle(self):
        # Identify due to
        fielder = ""
        #if len(details) > 0:
        #    fielder = details.pop(0)

        # Check Modifiers
        due_to = ""
        if len(self.action.modifiers) > 0:
            modifier = self.action.modifiers[0]
            if modifier == Modifiers.DOUBLE_PLAY:
                due_to = "Double Play"

        logger.info("Batter Walked due to Fielders Choice (Fielder = %s). %s ", fielder, due_to)

        self.game_state.action_advance_runner("B", "1")
