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

    _first : bool = False
    _second : bool = False
    _third : bool = False

    _inning : int = 0
    _top_of_inning_flag : bool = True

    _outs : int = 0
    _score_visitor : int = 0
    _score_home : int = 0

    def copy(self) -> object:
        # validate parameters
        if self is None:
            fail("Input object for game state is None!")

        # create new game state
        result = GameState()
        result._first = self._first
        result._second = self._second
        result._third = self._third
        result._inning = self._inning
        result._top_of_inning_flag = self._top_of_inning_flag
        result._outs = self._outs
        result._score_visitor = self._score_visitor
        result._score_home = self._score_home

        return result


    def action_batter_to_first_safe(self):
        """ Signal that the batter made it to _first. """
        logger.debug("action_batter_to_first_safe()")
        self.action_runner_advance_safe("B", "1")

    def action_batter_to__first_out(self):
        logger.debug("action_batter_to__first_out()")
        self.action_advancing_runner_out("B", "1")

    def action_batter_out_non_progressing(self):
        logger.debug("action_batter_out_non_progressing")
        self.on_out()

    def action_advance_runner_safe_or_out(self, base_from, base_to, is_out):
        # validate inputs before entering more complex logic
        if base_from not in ["B", 0, "1", 1, "2", 2, "3", 3]:
            fail(f"Invalid value for base_from! {base_from}")
        if base_to not in ["1", 1, "2", 2, "3", 3, "H", 4]:
            fail(f"Invalid value for base_to! {base_from}")
        if base_from in ["B", 0] and base_to not in ["1", 1, "2", 2, "3", 3, "H", 4]:
            fail(f"Illegal advancement from Batter's box!  To={base_to}")
        if base_from in ["1", 1] and base_to not in ["2", 2, "3", 3, "H", 4]:
            fail(f"Illegal advancement from First Base!  To={base_to}")
        if base_from in ["2", 2] and base_to not in ["3", 3, "H", 4]:
            fail(f"Illegal advancement from Second Base!  To={base_to}")
        if base_from in ["3", 3] and base_to not in ["H", 4]:
            fail(f"Illegal advancement from Third Base!  To={base_to}")

        # runner advances from batter's position
        if base_from in ["B", 0]:
            # to validation above, we can always assume an advancement at least to first
            if self._first:
                if self._second:
                    if self._third:
                        if not is_out:
                            self.on_score()
                    self._third = True
                self._second = True
            self._first = True
            if base_to in ["2", 2, "3", 3, "4", "H"]:
                self.action_runner_advance_safe("1", base_to)

        # runner advances from _first base
        if base_from in ["1", 1]:
            # ensure runner actually on base
            if not self._first:
                fail("Advancing runner from first but no runner on base!")

            self._first = False

            # to validation above, we can always assume an advancement at least to second
            if self._second:
                if self._third:
                    if not is_out:
                        self.on_score()
                self._third = True
            self._second = True
            if base_to in ["3", 3, "4", "H"]:
                self.action_runner_advance_safe("2", base_to)

        # runner advances from second base
        if base_from in ["2", 2]:
            # ensure runner actually on base
            if not self._second:
                fail("Advancing runner from second but no runner on base!")

            self._second = False

            # to validation above, we can always assume an advancement at least to third
            if self._third:
                if not is_out:
                    self.on_score()
            self._third = True
            if base_to in ["4", "H"]:
                self.action_runner_advance_safe("3", base_to)

        # runner advances from third base
        if base_from in ["3", 3]:
            # ensure runner actually on base
            if not self._third:
                fail("Advancing runner from third but no runner on base!")

            self._third = False
            if not is_out:
                self.on_score()

        # mark the runner out
        if is_out:
            if base_to in ["1", 1]:
                self._first = False
            elif base_to in ["2", 2]:
                self._second = False
            elif base_to in ["3", 3]:
                self._third = False
            self.on_out()


    def action_runner_advance_safe(self, base_from, base_to):
        logger.debug("action_runner_advance_safe()")
        self.action_advance_runner_safe_or_out(base_from, base_to, False)

    def action_advancing_runner_out(self, base_from, base_to):
        logger.debug("action_advancing_runner_out()")
        self.action_advance_runner_safe_or_out(base_from, base_to, True)

    def on_batting_team_change(self):
        # validate first
        if self._outs != 3:
            fail("Changing batting team but outs is incorrect! {self._outs}")

        # then clear
        self._outs = 0
        self._first = False
        self._second = False
        self._third = False
        if self._top_of_inning_flag:
            self._top_of_inning_flag = False
        else:
            self._top_of_inning_flag = True
            self._inning += 1


    def is_on_first(self):
        return self._first

    def is_on_second(self):
        return self._second

    def is_on_third(self):
        return self._third

    def on_out(self):
        logger.debug("on_out()")
        self._outs += 1
    
    def get_outs(self):
        return self._outs

    def on_score(self):
        logger.debug("on_score")
        if self._top_of_inning_flag:
            self._score_visitor += 1
        else:
            self._score_home += 1

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
        return [self._score_visitor, self._score_home]

    def get_score_str(self) -> str:
        return f"{self._score_visitor}-{self._score_home}"

    def get_inning_and_score_str(self) -> str:
        # create top or bottom of inning str
        top_or_bottom_str = "Bot"
        if self._top_of_inning_flag:
            top_or_bottom_str = "Top"

        return f"{self._inning}/{top_or_bottom_str} {self.get_score_str()}"

    def __str__(self) -> str:
        return to_json_string(self)
