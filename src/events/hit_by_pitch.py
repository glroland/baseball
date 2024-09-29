""" Hit By Ptich Event

Runner hit by pitch game event.
"""
import logging
from events.base_event import BaseEvent
from model.action_record import ActionRecord
from model.game_state import GameState

logger = logging.getLogger(__name__)

class HitByPitchEvent(BaseEvent):
    """ Hit By Pitch Event """

    def handle(self, game_state : GameState, action : ActionRecord):
        """ Walk the player due to hit by pitch
        
            game_at_bat - game at bat
            op_details - offensive play details
        """
        logger.info("Batter Hit By Pitch")

        game_state.action_advance_runner("B", "1")
