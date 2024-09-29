""" Passed Ball Event

Passed ball game event.
"""
import logging
from events.base_event import BaseEvent
from model.action_record import ActionRecord
from model.game_state import GameState

logger = logging.getLogger(__name__)

class PassedBallEvent(BaseEvent):
    """ Passed Ball Event """

    def handle(self, game_state : GameState, action : ActionRecord):
        logger.warning("Ignoring passed ball event")
