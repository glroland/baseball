""" Stolen Base Event

Stolen base game event.
"""
import logging
from events.base_event import BaseEvent
from utils.data import regex_split, split_leading_chars_from_numbers
from model.action_record import ActionRecord
from model.game_at_bat import GameAtBat

logger = logging.getLogger(__name__)

class StolenBaseEvent(BaseEvent):
    """ Stolen Base Event """

    def handle(self, game_at_bat : GameAtBat, action : ActionRecord):
        """ Check the advancement history to see if this runner progression was
            already handled.
            
            base_to - where the runner is running to 
        """
        # Extract the tailing numbers
        components = split_leading_chars_from_numbers(action.action)
        if len(components) != 2:
            self.fail(f"Illegal action for SB!  {action.action}  ComponentLen={len(components)}")
        base_to = components[1]
        self.validate_base(base_to, first_allowed=False)
    
        # determine if the advancement was already completed
        #if self.was_advancement_already_handled(base_to):
        #    logger.warning("Advancement already handled.  Skipping validations and base assignments!")
        #elif base_to == "2":
        if base_to == "2":
            if not game_at_bat.runner_on_1b:
                self.fail("Runner stealing 2nd but there was no runner on 1st")
            game_at_bat.runner_on_1b = False
            game_at_bat.runner_on_2b = True
        elif base_to == "3":
            if not game_at_bat.runner_on_2b:
                self.fail("Runner stealing 3rd but there was no runner on 2nd")
            game_at_bat.runner_on_2b = False
            game_at_bat.runner_on_3b = True
        elif base_to == "H":
            if not game_at_bat.runner_on_3b:
                self.fail("Runner stealing home but there was no runner on 3rd")
            game_at_bat.runner_on_3b = False
            game_at_bat.score()

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
