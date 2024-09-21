""" Defensive Indifference Game Event

Defensive indifference game event.
"""
import logging
from events.base_event import BaseEvent

logger = logging.getLogger(__name__)

class DefensiveIndifferenceEvent(BaseEvent):
    """ Defensive Indifference Event """

    def handle(self, game_at_bat, op_details):

        logging.info("Defensive Indifference.  Assuming that the advancement details contain the details")
