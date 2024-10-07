""" Baseball game model

Representation of a baseball game and its field. 
"""
import logging
import re
from typing import List
from pydantic import BaseModel
from utils.data import to_json_string, fail, get_base_as_int
from utils.baseball import sort_play_advances_desc, base_after, is_action_str_defensive_error
from events.constants import Parameters
from model.advance_record import AdvanceRecord
from model.runner import Runner

logger = logging.getLogger(__name__)

#pylint: disable=too-many-instance-attributes,protected-access
class GameState(BaseModel):
    """ Baseball Game Model """

    _inning : int = 0
    _top_of_inning_flag : bool = True

    _outs : int = 0
    _score_visitor : int = 0
    _score_home : int = 0

    _completed_advancements : List[AdvanceRecord] = []

    _runners : List[Runner] = []

    def clone(self) -> object:
        """ Duplicate object. """
        # validate parameters
        if self is None:
            fail("Input object for game state is None!")

        # create new game state
        result = GameState()
        for runner in self._runners:
            if not runner.is_out and runner.current_base in ["1", 1, "2", 2, "3", 3]:
                runner_clone = runner.clone()
                result._runners.append(runner_clone)
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
        self.on_out("B")

    #pylint: disable=too-many-branches,too-many-statements,too-many-arguments
    def action_advance_runner(self, base_from, base_to, is_out=False, parameter = ""):
        """ Advance runners with full control over the details.
        
            base_from - where the runner is running from
            base_to - where the runner is going to
            is_out - whether or not the runner is out
            parameter - optional parameters
        """
        # have there already been advancements from B?
        if base_from in ["B", 0]:
            for completed_advancement in self._completed_advancements:
                if completed_advancement.base_from == base_from:
                    logger.warning("Batter already advanced.  Ignoring requested " + \
                                   f"advancement to {base_to}.  Completed=" + \
                                   f"Match={completed_advancement}")
                    return

        # get runner for the base
        runner = self.get_runner_on_base(base_from)
        if runner is None:
            fail("Illegal Advancement - Runner not on base! " + \
                 f"From={base_from} To={base_to}")

        # was this advancement already completed?
        advance_record = AdvanceRecord()
        advance_record.base_from = base_from
        advance_record.base_to = base_to
        advance_record.was_out = is_out
        logger.debug("Game State before check = %s", self.get_game_status_string())
        if advance_record.is_completed(self._completed_advancements):
            logger.warning("Advancement already completed!  From=%s To=%s WasOut=%s GameStr=%s",
                        base_from, base_to, is_out, self.get_game_status_string())
            #return
        else:
            logger.debug("Advancement NOT completed!  From=%s To=%s WasOut=%s GameStr=%s",
                        base_from, base_to, is_out, self.get_game_status_string())

        # log the advancement request
        self._completed_advancements.append(advance_record)

        # validate inputs before entering more complex logic
        base_from_int = get_base_as_int(base_from)
        base_to_int = get_base_as_int(base_to)
        if base_from_int not in [0, 1, 2, 3]:
            fail(f"Invalid value for base_from! {base_from_int}")
        if base_to_int not in [1, 2, 3, 4]:
            fail(f"Invalid value for base_to! {base_to_int}")
        if base_from_int >= base_to_int:
            fail(f"Illegal advancement!  From={base_from_int} To={base_to_int}")

        # which nearest base, if any, needs to advance?
        # -- first?
        if base_from_int == 0 \
            and base_to_int >= 1 \
            and self.is_on_first():
            self.action_advance_runner("1", base_after(base_to), is_out=False)

        # -- second?
        elif base_from_int <= 1 \
            and base_to_int >= 2 \
            and self.is_on_second():
            self.action_advance_runner("2", base_after(base_to), is_out=False)

        # -- third?
        elif base_from_int <= 2 \
            and base_to_int >= 3 \
            and self.is_on_third():
            self.action_advance_runner("3", base_after(base_to), is_out=False)

        # progress runner
        if base_to_int == 1:
            if self.is_on_first():
                fail(f"Runner on first did not progress?!?!? {self.get_game_status_string()}")
            runner.current_base = "1"
        elif base_to_int == 2:
            if self.is_on_second():
                fail(f"Runner on second did not progress?!?!? {self.get_game_status_string()}")
            runner.current_base = "2"
        elif base_to_int == 3:
            if self.is_on_third():
                fail(f"Runner on third did not progress?!?!? {self.get_game_status_string()}")
            runner.current_base = "3"
        elif base_to_int == 4:
            runner.current_base = "H"
            if not is_out:
                self.on_score()

        # mark the runner out
        if is_out:
            self.on_out(base_to)

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
        self._runners = []

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

    def get_runner_on_base(self, base):
        """ Find the runner on the specified base
        
            base - base to check
        """
        base_int = get_base_as_int(base)
        logger.debug("# of runners on base: %s", len(self._runners))
        for runner in self._runners:
            logger.debug("Runner: %s", runner)
            if not runner.is_out and get_base_as_int(runner.current_base) == base_int:
                return runner
        return None

    def is_on_first(self):
        """ Is the runner on first? """
        return self.get_runner_on_base("1") is not None

    def is_on_second(self):
        """ Is the runner on second? """
        return self.get_runner_on_base("2") is not None

    def is_on_third(self):
        """ Is the runner on third? """
        return self.get_runner_on_base("3") is not None

    def reverse_score_due_to_out(self, runner):
        """ Reverse the score due to the provided runner actually being out.
        
            runner - runner
        """
        logger.warning("Reversing score by runner: %s", runner)

        # Verify the runner made it home
        if runner.current_base not in ["H", 4]:
            fail("Cannot reverse score of runner who didn't score!  {runner}")

        # Runner Out
        runner.current_base = None
        runner.is_out = True
        self._outs += 1

        # Reverse Score
        if self._top_of_inning_flag:
            self._score_visitor -= 1
        else:
            self._score_home -= 1

    def on_out(self, base):
        """ Signal that there was an out.
        
            base - optional base (from - currently resides)
        """
        logger.debug("on_out()")
        self._outs += 1
        runner = self.get_runner_on_base(base)
        if runner is None:
            fail(f"No runner on the specified base for out!  Base={base} Runners={self._runners}")
        runner.is_out = True
        runner.current_base = None

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
        # sort advances before processing them
        advances = sort_play_advances_desc(advances)

        if advances is not None and len(advances) > 0:
            for advance in advances:
                base_from = advance.base_from
                was_out = advance.was_out
                base_to = advance.base_to

                # check for error
                defensive_error = False
                if len(advance.groups) > 0:
                    for group in advance.groups:
                        if is_action_str_defensive_error(group):
                            defensive_error = True
                            logger.debug("Error by defense on advance attempt! %s", group)

                # override the out?
                out_override = was_out
                if defensive_error and was_out:
                    logger.info("Overriding out due to error!")
                    out_override = False

                # check for situation where advancement is to itself
                if base_from == base_to and not out_override:
                    logger.info("Runner ran back to base.  Ignoring advancement...")
                    self._completed_advancements.append(advance)
                elif base_from == base_to and out_override:
                    logger.info("Runner ran back to base but was still out!")
                    self.on_out(base_from)
                    self._completed_advancements.append(advance)
                else:
                    # see if the advancement was already handled
                    if advance.is_completed(self._completed_advancements):
                        fail(f"Advancement Requested F={base_from} T={base_to} Out={was_out} " + \
                            f"overlaps with Completed Advancements! {self._completed_advancements}")

                    # advance the runner
                    try:
                        self.action_advance_runner(base_from, base_to, out_override)
                    except ValueError as e:
                        logger.error("Unable to advance!  Requested=%s  Completed=%s Error=%s",
                                        advance, self._completed_advancements, e)
                        raise e

    #pylint: disable=inconsistent-return-statements
    def get_runner_from_original_base(self, original_base):
        """ For a given base, find where the runner is currently after a varying 
            number of advances.
            
            original_base - original base
        """
        original_base_int = get_base_as_int(original_base)
        for runner in self._runners:
            if get_base_as_int(runner.original_base) == original_base_int:
                return runner
        fail(f"No runner exists for original base! Base={original_base} Runners={self._runners}")

    def __str__(self) -> str:
        """ Convert object to a JSON string """
        return to_json_string(self)
