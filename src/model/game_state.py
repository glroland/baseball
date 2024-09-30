""" Baseball game model

Representation of a baseball game and its field. 
"""
import logging
import re
from typing import List
from pydantic import BaseModel
from utils.data import to_json_string, fail
from events.constants import Parameters
from model.advance_record import AdvanceRecord

logger = logging.getLogger(__name__)

#pylint: disable=too-many-instance-attributes,protected-access
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

    _completed_advancements : List[AdvanceRecord] = []

    def clone(self) -> object:
        """ Duplicate object. """
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

    def action_batter_out_non_progressing(self):
        """ Signal that the batter is out and should not progresseed runners.
            i.e. fly balls.
        """
        logger.debug("action_batter_out_non_progressing")
        self.on_out()

    #pylint: disable=too-many-branches,too-many-statements,too-many-arguments
    def action_advance_runner(self, base_from, base_to, is_out=False,
                              parameter = "", is_recursive=False):
        """ Advance runners with full control over the details.
        
            base_from - where the runner is running from
            base_to - where the runner is going to
            is_out - whether or not the runner is out
            parameter - optional parameters
            is_recursive - flag indicating whether the invocation is self induced
        """
        # have there already been advancements from B?
        if base_from == "B":
            for completed_advancement in self._completed_advancements:
                if completed_advancement.base_from == base_from:
                    fail("Redundant advances from batter during a single play! " + \
                         f"Match={completed_advancement}")

        # log the advancement request
        if not is_recursive:
            advance_record = AdvanceRecord()
            advance_record.base_from = base_from
            advance_record.base_to = base_to
            advance_record.was_out = is_out
            self._completed_advancements.append(advance_record)

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
                self.action_advance_runner("1", base_to, is_recursive=True)

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
                self.action_advance_runner("2", base_to, is_recursive=True)

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
                # TODO on these recursive calls, what happens when its an advanced out?
                # seems like you'd call the last one out with all the others safe?
                self.action_advance_runner("3", base_to, is_recursive=True)

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

            # log extra info about event
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

        elif not is_out:
            logger.info("Base Runner advanced from %s to %s.", base_from, base_to)


    def on_batting_team_change(self):
        """ Notify that the inning or batting team is changing and validate that
            the data reflects a valid condition for this to happen.
        """
        # validate first
        if self._outs != 3:
            fail(f"Changing batting team but outs is incorrect! {self._outs}")

        # then clear
        self._outs = 0
        self._first = False
        self._second = False
        self._third = False

        # data sets the innings for us
        #if self._top_of_inning_flag:
        #    self._top_of_inning_flag = False
        #else:
        #    self._top_of_inning_flag = True
        #    self._inning += 1

    def validate_against_prev(self, prev):
        """ Validate the game state object. 
        
            prev - previous game state
        """
        # determine if there is a change in batting team
        change_in_batting_team = False
        if self._inning != prev._inning or self._top_of_inning_flag != prev._top_of_inning_flag:
            logger.debug("Change in batting team recognized in validation.")
            change_in_batting_team = True

        # validate outs
        if change_in_batting_team and self._outs not in [0, 1, 3]:
            msg = f"Incorrect number of outs after batting team change! #={self._outs}"
            logger.error(msg)
            raise ValueError(msg)
        if self._outs > 3:
            msg = f"Too many outs! #={self._outs}"
            logger.error(msg)
            raise ValueError(msg)

        # validate innings
        if self._inning < 1:
            msg = f"Inning value is less than 1! #={self._inning}"
            logger.error(msg)
            raise ValueError(msg)

    def is_on_first(self):
        """ Is the runner on first? """
        return self._first

    def is_on_second(self):
        """ Is the runner on second? """
        return self._second

    def is_on_third(self):
        """ Is the runner on third? """
        return self._third

    def on_out(self):
        """ Signal that there was an out. """
        logger.debug("on_out()")
        self._outs += 1

    def get_outs(self):
        """ Get the number of outs this batting segment. """
        return self._outs

    def on_score(self):
        """ Signal that a runner just scored. """
        logger.debug("on_score")
        if self._top_of_inning_flag:
            self._score_visitor += 1
        else:
            self._score_home += 1

    def get_runners(self) -> List[str]:
        """ Returns a list of runners on base. """
        runners = []
        if self.is_on_first():
            runners.append ("1")
        if self.is_on_second():
            runners.append ("2")
        if self.is_on_third():
            runners.append ("3")
        return runners

    def get_runners_str(self) -> str:
        """ Gets a string for logging purposes that indicates what runners on what
            bases.
        """
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
        """ Gets the game score as a tuple """
        return [self._score_visitor, self._score_home]

    def get_score_str(self) -> str:
        """ Gest a string containing the score. """
        return f"{self._score_visitor}-{self._score_home}"

    def get_game_status_string(self) -> str:
        """ Gets the inning and score in a short string suitable for logging. """
        # create top or bottom of inning str
        top_or_bottom_str = "Bot"
        if self._top_of_inning_flag:
            top_or_bottom_str = "Top"

        return f"{self._inning}/{top_or_bottom_str}  Runners={self.get_runners_str()}  " +\
               f"Outs={self.get_outs()}  {self.get_score_str()}"

    def handle_advances(self, advances):
        """ Handle Base Advances.
    
            advances - list of base advances
        """
        if advances is not None and len(advances) > 0:
            for advance in advances:
                base_from = advance.base_from
                was_out = advance.was_out
                base_to = advance.base_to

                # see if the advancement was already handled
                if advance.is_completed(self._completed_advancements):
                    logger.warning("Advancement Requested F=%s T=%s Out=%s overlaps with " + \
                                   "Completed Advancements! %s", base_from, base_to, was_out,
                                   self._completed_advancements)

                else:
                    # advance the runner
                    try:
                        self.action_advance_runner(base_from, base_to, was_out)
                    except ValueError as e:
                        logger.error("Unable to advance!  Requested=%s  Completed=%s Error=%s",
                                     advance, self._completed_advancements, e)
                        raise e

    def __str__(self) -> str:
        """ Convert object to a JSON string """
        return to_json_string(self)
