""" Caught Stealing Event

Runner caught stealing a base game event.
"""
import logging
from events.base_event import BaseEvent
from utils.data import split_leading_chars_from_numbers
from model.action_record import ActionRecord
from model.game_state import GameState

logger = logging.getLogger(__name__)

class CaughtStealingEvent(BaseEvent):
    """ Caught Stealing Event """

    def handle(self, game_state : GameState, action : ActionRecord):
        base = ""
        if action.action == "CSH":
            base = "H"
        else:
            components = split_leading_chars_from_numbers(action.action)
            base = components[1]
        logger.error("Stolen Base.  Base=%s Action=%s", base, action)

        # Check to see if there are details being ignored
        credited_to = ""
        if len(action.groups) > 0:
            credited_to = f"Crediting to {action.groups[0]}"

        # Player Out
        logger.info("Player Caught Stealing to Base #%s %s", base, credited_to)

        #  Update and validate runner status
        if base == "2":
            game_state.action_advance_runner("1", "2", True)
        elif base == "3":
            game_state.action_advance_runner("2", "3", True)
        elif base == "H":
            game_state.action_advance_runner("3", "H", True)
