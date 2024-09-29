""" Stolen Base Event

Stolen base game event.
"""
import logging
from events.base_event import BaseEvent
from utils.data import split_leading_chars_from_numbers
from utils.baseball import validate_base
from model.action_record import ActionRecord
from model.game_state import GameState

logger = logging.getLogger(__name__)

class StolenBaseEvent(BaseEvent):
    """ Stolen Base Event """

    def handle(self, game_state : GameState, action : ActionRecord):
        """ Check the advancement history to see if this runner progression was
            already handled.
            
            base_to - where the runner is running to 
        """
        # Extract the tailing numbers
        components = split_leading_chars_from_numbers(action.action)
        if len(components) != 2:
            self.fail(f"Illegal action for SB!  {action.action}  ComponentLen={len(components)}")
        base_to = components[1]
        validate_base(base_to, first_allowed=False)

        # determine if the advancement was already completed
        #if self.was_advancement_already_handled(base_to):
        #    logger.warning("Advancement already handled.  Skipping!")
        #elif base_to == "2":
        if base_to == "2":
            game_state.action_advance_runner("1", "2", False)
        elif base_to == "3":
            game_state.action_advance_runner("2", "3", False)
        elif base_to == "H":
            game_state.action_advance_runner("3", "H", False)

        #for advance in self.completed_advances:
        #    # get and validate base information from prior advances
        #    old_from = advance[0]
        #    self.validate_base(old_from)
        #    old_to = advance[2]
        #    self.validate_base(old_to)

        #    if base_to == "2":
        #        pass
        #    if base_to == "3":
        #        pass
        #    if base_to == "H":
        #        pass
        #return False
