""" Defensive Indifference Game Event

Defensive indifference game event.
"""
import logging
from events.base_event import BaseEvent

logger = logging.getLogger(__name__)

class DefensiveIndifferenceEvent(BaseEvent):
    """ Defensive Indifference Event """

    def get_play_type_code(self) -> str:
        """ Get the play type code. """
        return "N"

    def handle(self):

        logging.info("Defensive Indifference.  Assuming advancements contain the details.")
