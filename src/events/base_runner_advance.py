""" Base Runner Advance Game Event

Base Runner Advance game event.
"""
import logging
from events.base_event import BaseEvent

logger = logging.getLogger(__name__)

class BaseRunnerAdvanceEvent(BaseEvent):
    """ Base Runner Advance Event """

    def handle(self, game_at_bat, op_details):

        logging.info("Base Runner Advance Event.  Assuming that the advancement details contain the details")
