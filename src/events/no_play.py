""" Caught Stealing Event

Runner caught stealing a base game event.
"""
import logging
from events.base_event import BaseEvent

logger = logging.getLogger(__name__)

class NoPlayEvent(BaseEvent):
    """ No Play, Sub Incoming Event """

    def handle(self, game_at_bat, op_details):
        logger.info("No Play, Sub Incoming for Player %s", game_at_bat.player_code)
