""" Passed Ball Event

Passed ball game event.
"""
import logging
from events.base_event import BaseEvent
from model.action_record import ActionRecord
from model.game_at_bat import GameAtBat

logger = logging.getLogger(__name__)

class PassedBallEvent(BaseEvent):
    """ Passed Ball Event """

    def handle(self, game_at_bat : GameAtBat, action : ActionRecord):
        logger.warning("Ignoring passed ball event")
