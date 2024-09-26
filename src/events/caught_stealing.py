""" Caught Stealing Event

Runner caught stealing a base game event.
"""
import logging
from events.base_event import BaseEvent
from utils.data import split_leading_chars_from_numbers
from model.action_record import ActionRecord
from model.game_at_bat import GameAtBat

logger = logging.getLogger(__name__)

class CaughtStealingEvent(BaseEvent):
    """ Caught Stealing Event """

    def handle(self, game_at_bat : GameAtBat, action : ActionRecord):
        components = split_leading_chars_from_numbers(action.action)
        base = components[1]
        logger.error("Stolen Base.  Base=%s Details=%s", base, action)

        # Check to see if there are details being ignored
        credited_to = ""
        if len(action.groups) > 0:
            credited_to = f"Crediting to {action.groups[0]}"

        # Player Out
        game_at_bat.outs += 1
        logger.info("Player Caught Stealing to Base #%s %s", base, credited_to)

        #  Update and validate runner status
        if base == "2":
            if not game_at_bat.runner_on_1b:
                self.fail("Encountered caught stealing event but no runner on first.")
            game_at_bat.runner_on_1b = False
        elif base == "3":
            if not game_at_bat.runner_on_2b:
                self.fail("Encountered caught stealing event but no runner on second.")
            game_at_bat.runner_on_2b = False
        elif base == "H":
            if not game_at_bat.runner_on_3b:
                self.fail("Encountered caught stealing event but no runner on third.")
            game_at_bat.runner_on_3b = False
