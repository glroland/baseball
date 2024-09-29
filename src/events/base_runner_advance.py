""" Base Runner Advance Game Event

Base Runner Advance game event.
"""
import logging
from events.base_event import BaseEvent
from model.action_record import ActionRecord
from model.game_state import GameState

logger = logging.getLogger(__name__)

class BaseRunnerAdvanceEvent(BaseEvent):
    """ Base Runner Advance Event """

    def handle(self, game_state : GameState, action : ActionRecord):

        logging.warning("Base Runner Advance Event.  Assuming advancements contain details.")
