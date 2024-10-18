""" Base Runner Advance Game Event

Base Runner Advance game event.
"""
import logging
from events.base_event import BaseEvent

logger = logging.getLogger(__name__)

class BaseRunnerAdvanceEvent(BaseEvent):
    """ Base Runner Advance Event """

    def handle(self):

        logging.warning("Base Runner Advance Event.  Assuming advancements contain details.")
