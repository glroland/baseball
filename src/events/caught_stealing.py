""" Caught Stealing Event

Runner caught stealing a base game event.
"""
import logging
import re
from events.base_event import BaseEvent
from utils.data import split_leading_num

logger = logging.getLogger(__name__)

class CaughtStealingEvent(BaseEvent):
    """ Caught Stealing Event """

    def handle(self, game_at_bat, details):
        d = details.pop(0)
        details_list = split_leading_num(d)
        logger.debug("Stolen Base Details: %s", details_list)
        base = int(details_list.pop(0))

        # Check to see if there are details being ignored
        credited_to = ""
        while len(details) > 0:
            d = details.pop(0)
            if re.match("^\\([0-9]+\\)", d):
                credited_to = f"Crediting to {d}"
            else:
                self.fail(f"Stolen Base Details Being Ignored!: {details_list}")

        # Player Out
        game_at_bat.outs += 1
        logger.info("Player Caught Stealing to Base #%s %s", base, credited_to)

        #  Update and validate runner status
        if base == 2:
            if not game_at_bat.runner_on_1b:
                self.fail("Encountered caught stealing event but no runner on first.")
            game_at_bat.runner_on_1b = False
        elif base == 3:
            if not game_at_bat.runner_on_2b:
                self.fail("Encountered caught stealing event but no runner on second.")
            game_at_bat.runner_on_2b = False
        elif base == 4:
            if not game_at_bat.runner_on_3b:
                self.fail("Encountered caught stealing event but no runner on third.")
            game_at_bat.runner_on_3b = False
