""" Defensive Play Event

After a hit, the defense made a successful play on the ball/runner.
"""
import logging
import re
from events.base_event import BaseEvent
from events.constants import Modifiers
from model.action_record import ActionRecord
from model.game_state import GameState
from utils.data import fail

logger = logging.getLogger(__name__)

# pylint: disable=protected-access
class DefensivePlayEvent(BaseEvent):
    """ Defensive Play Event """

    # pylint: disable=too-many-branches,too-many-statements
    def handle(self, game_state : GameState, action : ActionRecord):
        """ Handle defensive play based on provided action list.exc_info=
        
        game_at_bat - game at bat
        play_list - list of offensive play components
        """
        fielded_by = action.action
        base_out = "B"
        if len(action.groups) > 0:
            base_out = action.groups[0]
        logger.info("Defensive Play.  Base=%s  Credit_to=%s", base_out, fielded_by)

        # Check for error or a specific runner
        is_out = True
        runner = None
        if len(action.groups) > 0:
            for group in action.groups:
                if re.match("^[0-9]+E[0-9]*$", group):
                    logger.info("Defensive error overriding out")
                    is_out = False
                elif group in ["B", "1", "2", "3"]:
                    runner = group
                else:
                    fail(f"Unknown group command!  {group}")

        logger.debug("Offensive Play - Runner Out -- %s", runner)

        # check for non-advancing reasons in modifier list
        non_advancing_out = False
        for modifier in action.modifiers:
            if len(modifier) >= 2:
                if modifier == Modifiers.FOUL:
                    non_advancing_out = True
                    logger.info("Batter out due to catch from foul ball.")
                elif modifier == Modifiers.SACRIFICE_FLY:
                    non_advancing_out = True
                    logger.info("Batter out due to catch from sacrifice fly.")
                elif (modifier[0] == Modifiers.FLY or modifier[0] == Modifiers.POP_FLY) and \
                    re.match("^[0-9]+$", modifier[1]):
                    non_advancing_out = True
                    logger.info("Batter out due to fly ball.")

        # TODO Need to chain defensive plays.  1 runner on base.  3(B)3(1)/LDP
        # mark the position as out
        if non_advancing_out:
            game_state.on_out()
        else:
            if base_out in ["B", 0]:
                game_state.action_advance_runner("B", "1", True)
            elif base_out in ["1", 1]:
                game_state.action_advance_runner("1", "2", True)
            elif base_out in ["2", 2]:
                game_state.action_advance_runner("2", "3", True)
            elif base_out in ["3", 3]:
                game_state.action_advance_runner("3", "H", True)
            else:
                fail(f"Illegal Base Out on Defensive Play!  {base_out}")

        # advance the runner
        #if runner is not None and runner in ["1", "2"]:
        #    game_state.action_advance_runner("B", "1", True)
        #    if runner == "1":
        #        game_state._second = False
        #    elif runner == "2":
        #        game_state._third = False
        #elif runner is not None and runner in ["3"]:
        #    game_state.action_advance_runner("B", "1", True)
        #    game_state._third = False
        #    game_state.on_out()
        #elif not non_advancing_out:
        #    game_state.action_advance_runner("B", "1", True)
        #else:
        #    game_state.on_out()

        # analyze modifier
        due_to = ""
        for modifier in action.modifiers:
            if modifier in [Modifiers.GROUNDER, Modifiers.GROUNDER_UNKNOWN]:
                due_to += "Due to Ground Ball"
            elif modifier == Modifiers.GROUNDER_DOUBLE_PLAY:
                due_to += "Due to Ground Ball - Double Play"
            elif modifier == Modifiers.GROUNDER_TRIPLE_PLAY:
                due_to += "Due to Ground Ball - Triple Play"
            elif modifier == Modifiers.LINED_INTO_DOUBLE_PLAY:
                due_to += "Due to Lined Into Double Play"
            elif modifier == Modifiers.DOUBLE_PLAY:
                due_to += "Due to Double Play"
            elif modifier == Modifiers.LINED_INTO_TRIPLE_PLAY:
                due_to += "Due to Lined Into Triple Play"
            elif modifier == Modifiers.TRIPLE_PLAY:
                due_to += "Due to Triple Play"
            elif modifier[0] == Modifiers.LINE_DRIVE:
                due_to += "Due to Line Drive"
            elif modifier == Modifiers.FORCE_OUT:
                due_to += "Due to Force Out"
            elif modifier == Modifiers.FOUL:
                due_to += "Due to Foul"
            elif modifier == Modifiers.FAN_INTERFERENCE:
                due_to += "Due to Fan Interference"
            elif modifier == Modifiers.FLY_BALL_DOUBLE_PLAY:
                due_to += "Due to Fly Ball Double Play"
            elif modifier[0] == Modifiers.FLY:
                due_to += "Due to Fly Ball"
            elif modifier == Modifiers.SACRIFICE_FLY:
                due_to += "Due to Sacrifice Fly"
            elif modifier == Modifiers.RUNNER_PASSED_ANOTHER_RUNNER:
                due_to += "Due to Runner Passing Another Runner"
            elif modifier[0] == Modifiers.POP_FLY:
                due_to += "Due to Pop Fly"
            elif modifier == Modifiers.SACRIFICE_HIT_BUNT:
                due_to += "Due to Sacrifice Hit / Bunt"
            elif modifier == Modifiers.GROUND_BALL_BUNT:
                due_to += "Due to Ground Ball Bunt"
            elif re.match("^" + Modifiers.BUNT_POPUP + "[0-9]$", modifier):
                due_to += "Due to Bunt Popup"
            else:
                msg = f"Unhandled Modifier!  {modifier}"
                logger.warning(msg)

        fielded_by = ""

        if is_out:
            logger.info("Runner out after hit.  Out credited to pos %s. %s", fielded_by, due_to)
        else:
            logger.info("Runner safe on base after defensive error by %s. %s", fielded_by, due_to)
