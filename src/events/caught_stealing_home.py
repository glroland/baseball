""" Caught Stealing Event

Runner caught stealing a base game event.
"""
import logging
from events.base_event import BaseEvent

logger = logging.getLogger(__name__)

class CaughtStealingHomeEvent(BaseEvent):
    """ Caught Stealing Home Event """

    def handle(self, game_at_bat, op_details):
        credit_to = ""
        if len(op_details) > 0:
            credit_to = op_details.pop(0)
        logger.info("Player Caught Stealing Home")
        game_at_bat.outs += 1
        if not game_at_bat.runner_on_3b:
            self.fail("Encountered caught stealing event but no runner on third. Credit to %s", credit_to)
        game_at_bat.runner_on_3b = False
