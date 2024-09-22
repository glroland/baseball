""" Stolen Base Event

Stolen base game event.
"""
import logging
from events.base_event import BaseEvent
from utils.data import regex_split

logger = logging.getLogger(__name__)

class StolenBaseEvent(BaseEvent):
    """ Stolen Base Event """

    def was_advancement_already_handled(self, base_to):
        """ Check the advancement history to see if this runner progression was
            already handled.
            
            base_to - where the runner is running to 
        """
        self.validate_base(base_to, first_allowed=False)
        for advance in self.completed_advances:
            # get and validate base information from prior advances
            old_from = advance[0]
            self.validate_base(old_from)
            old_to = advance[2]
            self.validate_base(old_to)

            if base_to == "2":
                pass
            if base_to == "3":
                pass
            if base_to == "H":
                pass
        return False

    def handle(self, game_at_bat, op_details):
        details = op_details.pop(0)
        base_list = regex_split("^([23H]);SB([23H])$", details)

        logger.debug(f"Stolen Base List: {base_list}")
        while len(base_list) > 0:
            base = base_list.pop(0)

            if self.was_advancement_already_handled(base):
                logger.warning("Advancement already handled.  Skipping validations and base assignments!")
            elif base == "2":
                if not game_at_bat.runner_on_1b:
                    self.fail("Runner stealing 2nd but there was no runner on 1st")
                game_at_bat.runner_on_1b = False
                game_at_bat.runner_on_2b = True
            elif base == "3":
                if not game_at_bat.runner_on_2b:
                    self.fail("Runner stealing 3rd but there was no runner on 2nd")
                game_at_bat.runner_on_2b = False
                game_at_bat.runner_on_3b = True
            elif base == "H":
                if not game_at_bat.runner_on_3b:
                    self.fail("Runner stealing home but there was no runner on 3rd")
                game_at_bat.runner_on_3b = False
                game_at_bat.score()
            else:
                self.fail(f"Unknown Stolen Base # {base}")

            logging.info("Runner stole base:", base)
