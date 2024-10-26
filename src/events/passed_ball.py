""" Passed Ball Event

Passed ball game event.
"""
import logging
from events.base_event import BaseEvent

logger = logging.getLogger(__name__)

class PassedBallEvent(BaseEvent):
    """ Passed Ball Event """

    def get_play_type_code(self) -> str:
        """ Get the play type code. """
        return "O"

    def handle(self):
        logger.warning("Ignoring passed ball event")
