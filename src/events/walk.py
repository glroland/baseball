""" Walk Event

Runner walked game event.
"""
import logging
from events.base_event import BaseEvent
from model.action_record import ActionRecord
from model.game_state import GameState

logger = logging.getLogger(__name__)

class WalkEvent(BaseEvent):
    """ Walk Event """

    def handle(self, game_state : GameState, action : ActionRecord):
        """ Walk the player
        
            game_at_bat - game at bat
            action - offensive play details
        """
        logger.info("Batter Walked")

        game_state.action_advance_runner("B", "1")
