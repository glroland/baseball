""" Homerun Event

Runner hit a home run game event.
"""
import logging
from events.base_event import BaseEvent

logger = logging.getLogger(__name__)

class HomerunEvent(BaseEvent):
    """ Homerun Event """

    def get_play_type_code(self) -> str:
        """ Get the play type code. """
        return "H"

    def handle(self):
        logger.info("Out of Park Home Run hit by batter")

        self.game_state.action_advance_runner("B", "H")
