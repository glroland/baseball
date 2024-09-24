""" Passed Ball Event

Passed ball game event.
"""
import logging
from events.base_event import BaseEvent

logger = logging.getLogger(__name__)

class PassedBallEvent(BaseEvent):
    """ Passed Ball Event """

    def handle(self, game_at_bat, details):
        logger.warning("Ignoring passed ball event")
