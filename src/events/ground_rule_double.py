""" Ground Rule Double Event

Runner hit a ground rule double game event.
"""
import logging
from events.base_event import BaseEvent

logger = logging.getLogger(__name__)

class GroundRuleDoubleEvent(BaseEvent):
    """ Ground Rule Double Event """

    def handle(self):
        logger.info("Ground Rule Double.")

        self.game_state.action_advance_runner("B", "2")
