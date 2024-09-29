""" Defensive Indifference Game Event

Defensive indifference game event.
"""
import logging
from events.base_event import BaseEvent
from model.action_record import ActionRecord
from model.game_state import GameState

logger = logging.getLogger(__name__)

class DefensiveIndifferenceEvent(BaseEvent):
    """ Defensive Indifference Event """

    def handle(self, game_state : GameState, action : ActionRecord):

        logging.info("Defensive Indifference.  Assuming advancements contain the details.")
