""" Wild Pitch Event

Wild pitch game event.
"""
import logging
from events.base_event import BaseEvent
from model.action_record import ActionRecord
from model.game_state import GameState

logger = logging.getLogger(__name__)

class WildPitchEvent(BaseEvent):
    """ Wild Pitch Event """

    def handle(self, game_state : GameState, action : ActionRecord):
        """ Wild pitch event
        
            game_at_bat - game at bat
            action - offensive play details
        """
        logger.info("Wild Pitch")

        #TODO - If the next record has the same batter as this one, the runner doesn't advance
        game_state.action_advance_runner("B", "1")
