""" Core Game Event

Base logic for game events.
"""
import logging
import re
from typing import List
from pydantic import BaseModel
from events.constants import Parameters
from model.action_record import ActionRecord
from model.advance_record import AdvanceRecord
from model.game_at_bat import GameAtBat
from utils.data import to_json_string

logger = logging.getLogger(__name__)

class BaseEvent(BaseModel):
    """ Base class for all game events.  """

    def handle(self, game_at_bat : GameAtBat, action : ActionRecord):
        """ Each Game Event Class should implement this method."""
        raise NotImplementedError()

    def debug_check_key_attributes_in(self, game_at_bat, op_details):
        """ Debugging Method """
        logger.info ("BasicPlay=<%s>, Modifiers=<%s>, Advance=<%s>, op_details=<%s>",
                     game_at_bat.basic_play,
                     game_at_bat.modifiers,
                     game_at_bat.advance,
                     op_details)

    def debug_check_key_attributes_out(self, game_at_bat, op_details):
        """ Debugging Method """
        logger.info("Score=%s-%s, Outs=%s, 1B=%s, 2B=%s, 3B=%s", game_at_bat.score_visitor,
                    game_at_bat.score_home, game_at_bat.outs, game_at_bat.runner_on_1b,
                    game_at_bat.runner_on_2b, game_at_bat.runner_on_3b)
        if len(op_details) > 0:
            self.fail(f"UNHANDLED DETAILS!!!  {op_details}")

    def validate_base(self, base_str, first_allowed=True, home_allowed=True):
        """ Validates the provided string representation of the base
            to ensure it is valid for the circumstance.  Otherwise an exception
            is thrown.
            
            base_str - string representation of the base
            first_allowed - whether first base is a permissiable value
            home_allowed - whether home is a permissiable value
        """
        if base_str is None or len(base_str) != 1:
            self.fail("Invalid Base String!  Empty string or None.")
        if not isinstance(base_str, str):
            self.fail("Base String is not a string!")
        if base_str == "1":
            if not first_allowed:
                self.fail("First base is not a permissible value for this play!")
            return True
        if base_str == "2":
            return True
        if base_str == "3":
            return True
        if base_str == "H":
            if not home_allowed:
                self.fail("Home base is not a permissible value for this play!")
            return True
        self.fail(f"Unexpected value for Base!  <{base_str}>")
        return False

    def score(self, game_at_bat):
        """ Update the score based on the team at bat.
        
            game_at_bat - game at bat
        """
        if game_at_bat.home_team_flag is None:
            self.fail("Unknown Home Team Flag Type!  Its unexpectedly None!")

        inning_str = str(game_at_bat.inning) + "/"
        if game_at_bat.home_team_flag:
            game_at_bat.score_home += 1
            inning_str += "Bottom"
            logger.info("Home Team Scored! %s %s-%s", inning_str,
                        game_at_bat.score_visitor, game_at_bat.score_home)
        else:
            game_at_bat.score_visitor += 1
            inning_str += "Top"
            logger.info("Visiting Team Scored! %s %s-%s", inning_str,
                        game_at_bat.score_visitor, game_at_bat.score_home)

    def advance_runner(self, game_at_bat, base_from, base_to,
                       is_out = False, parameter = ""):
        """ Advance runner from the specified from to the to base.
        
            game_at_bat - game at bat
            base_from - starting base
            base_to - ending base
            is_out - advancement type character
        """
        current_base = base_from
        while True:
            # stop the progression once the runner reaches the target base
            if current_base in [base_to, "H"]:
                break

            # advance one base
            if current_base == "B":
                if game_at_bat.runner_on_1b:
                    logger.info("1st Base Runner Progressed")
                    if game_at_bat.runner_on_2b:
                        logger.info("2nd Base Runner Progressed")
                        if game_at_bat.runner_on_3b:
                            logger.info("3rd Base Runner Progressed")
                            self.score(game_at_bat)
                            game_at_bat.runner_on_3b = False
                        game_at_bat.runner_on_3b = True
                        game_at_bat.runner_on_2b = False
                    game_at_bat.runner_on_2b = True
                    game_at_bat.runner_on_1b = False
                game_at_bat.runner_on_1b = not is_out
                current_base = "1"

            elif current_base == "1":
                if not game_at_bat.runner_on_1b:
                    self.fail(f"Runner on 1st advancing to {base_to} but no runner is on base!")
                if game_at_bat.runner_on_2b:
                    logger.info("2nd Base Runner Progressed")
                    if game_at_bat.runner_on_3b:
                        logger.info("3rd Base Runner Progressed")
                        self.score(game_at_bat)
                        game_at_bat.runner_on_3b = False
                    game_at_bat.runner_on_3b = True
                    game_at_bat.runner_on_2b = False
                game_at_bat.runner_on_2b = not is_out
                game_at_bat.runner_on_1b = False
                current_base = "2"

            elif current_base == "2":
                if not game_at_bat.runner_on_2b:
                    self.fail(f"Runner on 2nd advancing to {base_to} but no runner is on base!")
                if game_at_bat.runner_on_3b:
                    logger.info("3rd Base Runner Progressed")
                    self.score(game_at_bat)
                    game_at_bat.runner_on_3b = False
                game_at_bat.runner_on_3b = not is_out
                game_at_bat.runner_on_2b = False
                current_base = "3"

            elif current_base == "3":
                if not game_at_bat.runner_on_3b:
                    self.fail(f"Runner on 3rd advancing to {base_to} but no runner is on base!")
                self.score(game_at_bat)
                game_at_bat.runner_on_3b = False
                current_base = "H"

            else:
                self.fail(f"Unknown value for current_base: {current_base}")

        if is_out:
            extra_text = ""
            if parameter is not None and len(parameter) > 0:
                if parameter == Parameters.UNEARNED_RUN:
                    extra_text = "Unearned Run"
                elif parameter == Parameters.RBI_CREDITED:
                    extra_text = "Credited with RBI"
                elif parameter in [Parameters.RBI_NOT_CREDITED_1, Parameters.RBI_NOT_CREDITED_2]:
                    extra_text = "RBI NOT Credited"
                elif re.match("^\\([0-9]+\\)#?$", parameter) is not None:
                    extra_text = f"{parameter} are credited with the out"
                else:
                    self.fail(f"Unknown advancement parameter = {parameter}")
            logger.info("Base Runner OUT while progressing from %s to %s.  %s",
                        base_from, base_to, extra_text)
            game_at_bat.outs += 1

        elif not is_out:
            logger.info("Base Runner advanced from %s to %s.", base_from, base_to)


    def handle_advances(self, game_at_bat, advances):
        """ Handle Base Advances.
    
            game_at_bat - game at bat
            advances - list of base advances
        """
        if advances is not None and len(advances) > 0:
            for advance in advances:
                base_from = advance.base_from
                was_out = advance.was_out
                base_to = advance.base_to

                self.advance_runner(game_at_bat, base_from, base_to, was_out)


    def fail(self, msg):
        """ Log and fail the application with the specified message.
        
            msg - message
        """
        logger.error(msg)
        raise ValueError(msg)


    def __str__(self) -> str:
        return to_json_string(self)
