""" Catcher Interference Event

Catcher Interference game event.
"""
import logging
from events.base_event import BaseEvent

logger = logging.getLogger(__name__)

class CatcherInterferenceEvent(BaseEvent):
    """ Catcher Interference Event """

    def get_play_type_code(self) -> str:
        """ Get the play type code. """
        return "I"

    def handle(self):
        """ Walk the player due to catcher interference
        
            game_at_bat - game at bat
            action - offensive play details
        """
        logger.info("Batter Walked due to Catcher Interference")

        self.game_state.action_advance_runner("B", "1")
