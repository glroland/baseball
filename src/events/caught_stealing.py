""" Caught Stealing Event

Runner caught stealing a base game event.
"""
import logging
from events.base_event import BaseEvent
from utils.data import split_leading_num

logger = logging.getLogger(__name__)

class CaughtStealingEvent(BaseEvent):
    """ Caught Stealing Event """

    def handle(self, game_at_bat, op_details):
        details = op_details.pop()
        details_list = split_leading_num(details)
        logger.debug("Stolen Base Details: %s", details_list)
        base = int(details_list.pop(0))
        logger.warning("Stolen Base Details Being Ignored!: %s", details_list)
        logger.info("Player Caught Stealing to Base #%s", base)
        game_at_bat.outs += 1
        if base == 2:
            game_at_bat.runner_on_1b = False
        elif base == 3:
            game_at_bat.runner_on_2b = False
        elif base == 4:
            game_at_bat.runner_on_3b = False

