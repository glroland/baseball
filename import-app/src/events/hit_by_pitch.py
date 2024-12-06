""" Hit By Ptich Event

Runner hit by pitch game event.
"""
import logging
from events.base_event import BaseEvent

logger = logging.getLogger(__name__)

class HitByPitchEvent(BaseEvent):
    """ Hit By Pitch Event """

    def get_play_type_code(self) -> str:
        """ Get the play type code. """
        return "X"

    def handle(self):
        """ Walk the player due to hit by pitch
        """
        logger.info("Batter Hit By Pitch")

        self.game_state.action_advance_runner("B", "1")
