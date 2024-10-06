""" Catcher Interference Event

Catcher Interference game event.
"""
import logging
from events.base_event import BaseEvent
from model.action_record import ActionRecord
from model.game_state import GameState

logger = logging.getLogger(__name__)

class CatcherInterferenceEvent(BaseEvent):
    """ Catcher Interference Event """

    def handle(self, game_state : GameState, action : ActionRecord):
        """ Walk the player due to catcher interference
        
            game_at_bat - game at bat
            action - offensive play details
        """
        logger.info("Batter Walked due to Catcher Interference")

        game_state.action_advance_runner("B", "1")
