""" Baseball game model

Representation of a baseball game and its field. 
"""
import logging
from typing import List
from pydantic import BaseModel
from utils.data import to_json_string, fail

logger = logging.getLogger(__name__)

class GameState(BaseModel):
    """ Baseball Game Model """

    first : bool = False
    second : bool = False
    third : bool = False

    inning : int = 0
    top_of_inning_flag : bool = True

    outs : int = 0
    score_visitor : int = 0
    score_home : int = 0

    def copy(self) -> object:
        # validate parameters
        if self is None:
            fail("Input object for game state is None!")

        # create new game state
        result = GameState()
        result.first = self.first
        result.second = self.second
        result.third = self.third
        result.inning = self.inning
        result.top_of_inning_flag = self.top_of_inning_flag
        result.outs = self.outs
        result.score_visitor = self.score_visitor
        result.score_home = self.score_home

        return result


    def action_batter_to_first_safe(self):
        """ Signal that the batter made it to first. """
        logger.debug("action_batter_to_first_safe()")
        self.action_runner_advance_safe("B", "1")

    def action_batter_to_first_out(self):
        logger.debug("action_batter_to_first_out()")
        self.action_advancing_runner_out("B", "1")

    def action_batter_out_non_progressing(self):
        logger.debug("action_batter_out_non_progressing")
        self.on_out()

    def action_advance_runner_safe_or_out(self, base_from, base_to, is_out):
        # validate inputs before entering more complex logic
        if base_from not in ["B", 0, "1", 1, "2", 2, "3", 3]:
            fail("Invalid value for base_from! %s", base_from)
        if base_to not in ["1", 1, "2", 2, "3", 3, "H", 4]:
            fail("Invalid value for base_to! %s", base_from)
        if base_from in ["B", 0] and base_to not in ["1", 1, "2", 2, "3", 3, "H", 4]:
            fail("Illegal advancement from Batter's box!  To=%s", base_to)
        if base_from in ["1", 1] and base_to not in ["2", 2, "3", 3, "H", 4]:
            fail("Illegal advancement from First Base!  To=%s", base_to)
        if base_from in ["2", 2] and base_to not in ["3", 3, "H", 4]:
            fail("Illegal advancement from Second Base!  To=%s", base_to)
        if base_from in ["3", 3] and base_to not in ["H", 4]:
            fail("Illegal advancement from Third Base!  To=%s", base_to)

        # runner advances from batter's position
        if base_from in ["B", 0]:
            # to validation above, we can always assume an advancement at least to first
            if self.first:
                if self.second:
                    if self.third:
                        if not is_out:
                            self.on_score()
                    self.third = True
                self.second = True
            self.first = True
            if base_to in ["2", 2, "3", 3, "4", "H"]:
                self.action_runner_advance_safe("1", base_to)

        # runner advances from first base
        if base_from in ["1", 1]:
            self.first = False

            # to validation above, we can always assume an advancement at least to second
            if self.second:
                if self.third:
                    if not is_out:
                        self.on_score()
                self.third = True
            self.second = True
            if base_to in ["3", 3, "4", "H"]:
                self.action_runner_advance_safe("2", base_to)

        # runner advances from second base
        if base_from in ["2", 2]:
            self.second = False

            # to validation above, we can always assume an advancement at least to third
            if self.third:
                if not is_out:
                    self.on_score()
            self.third = True
            if base_to in ["3", 3, "4", "H"]:
                self.action_runner_advance_safe("2", base_to)

        # runner advances from third base
        if base_from in ["3", 3]:
            self.third = False
            if not is_out:
                self.on_score()

        # mark the runner out
        if is_out:
            if base_to in ["1", 1]:
                self.first = False
            elif base_to in ["2", 2]:
                self.second = False
            elif base_to in ["3", 3]:
                self.third = False
            self.on_out()


    def action_runner_advance_safe(self, base_from, base_to):
        logger.debug("action_runner_advance_safe()")
        self.action_advance_runner_safe_or_out(base_from, base_to, False)

    def action_advancing_runner_out(self, base_from, base_to):
        logger.debug("action_advancing_runner_out()")
        self.action_advance_runner_safe_or_out(base_from, base_to, True)

    def on_batting_team_change(self):
        # validate first
        if self.outs != 3:
            fail("Changing batting team but outs is incorrect! %s", self.outs)

        # then clear
        self.outs = 0
        self.first = False
        self.second = False
        self.third = False
        if self.top_of_inning_flag:
            self.top_of_inning_flag = False
        else:
            self.top_of_inning_flag = True
            self.inning += 1


    def is_on_first(self):
        return self.first

    def is_on_second(self):
        return self.second

    def is_on_third(self):
        return self.third

    def on_out(self):
        logger.debug("on_out()")
        self.outs += 1
    
    def get_outs(self):
        return self.outs

    def on_score(self):
        logger.debug("on_score")
        if self.top_of_inning_flag:
            self.score_visitor += 1
        else:
            self.score_home += 1

    def get_runners(self) -> List[str]:
        runners = []
        if self.is_on_first():
            runners.append ("1")
        if self.is_on_second():
            runners.append ("2")
        if self.is_on_third():
            runners.append ("3")
        return runners

    def get_runners_str(self) -> str:
        runners = ""
        if self.is_on_first():
            runners += "1"
        else:
            runners += "-"
        if self.is_on_second():
            runners += "2"
        else:
            runners += "-"
        if self.is_on_third():
            runners += "3"
        else:
            runners += "-"
        return runners

    def get_score(self) -> List[int]:
        return [self.score_visitor, self.score_home]

    def get_score_str(self) -> str:
        return f"{self.score_visitor}-{self.score_home}"

    def get_inning_and_score_str(self) -> str:
        # create top or bottom of inning str
        top_or_bottom_str = "Bot"
        if self.top_of_inning_flag:
            top_or_bottom_str = "Top"

        return f"{self.inning}/{top_or_bottom_str} {self.get_score_str()}"

    def __str__(self) -> str:
        return to_json_string(self)
