""" Base Runner Advance Game Event

Base Runner Advance game event.
"""
import logging
from events.base_event import BaseEvent

logger = logging.getLogger(__name__)

class BaseRunnerAdvanceEvent(BaseEvent):
    """ Base Runner Advance Event """

    def get_play_type_code(self) -> str:
        """ Get the play type code. """
        return "A"

    def handle(self):

        logging.warning("Base Runner Advance Event.  Assuming advancements contain details.")
