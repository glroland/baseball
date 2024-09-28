""" Defensive Play Event

After a hit, the defense made a successful play on the ball/runner.
"""
import logging
import re
from events.base_event import BaseEvent
from events.constants import Modifiers
from utils.data import split_leading_num, split_leading_chars_from_numbers
from model.action_record import ActionRecord
from model.game_at_bat import GameAtBat

logger = logging.getLogger(__name__)

class DefensivePlayEvent(BaseEvent):
    """ Defensive Play Event """

    def handle(self, game_at_bat : GameAtBat, action : ActionRecord):
        """ Handle defensive play based on provided action list.exc_info=
        
        game_at_bat - game at bat
        play_list - list of offensive play components
        """
        logger.info("Defensive Play.  Play_List<%s>", action.action)

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
                    self.fail(f"Unknown group command!  {group}")

        logger.fatal("Offensive Play - Runner Out -- %s", runner)

        # check for non-advancing reasons in modifier list
        non_advancing_out = False
        for modifier in action.modifiers:
            if len(modifier) >= 2:
                if modifier == Modifiers.FOUL:
                    non_advancing_out = True
                    logger.info("Batter out due to catch from foul ball.")
                elif (modifier[0] == Modifiers.FLY or modifier[0] == Modifiers.POP_FLY) and \
                    re.match("^[0-9]+$", modifier[1]):
                    non_advancing_out = True
                    logger.info("Batter out due to fly ball.")

        # advance the runner
        if runner is not None and runner in ["1", "2"]:
            self.advance_runner(game_at_bat, "B", "1", False)
            game_at_bat.outs += 1
            if runner == "1":
                game_at_bat.runner_on_2b = False
            elif runner == "2":
                game_at_bat.runner_on_3b = False
        elif runner is not None and runner in ["3"]:
            self.advance_runner(game_at_bat, "B", "1", False)
            game_at_bat.runner_on_3b = False
            game_at_bat.outs += 1
        elif not non_advancing_out:
            self.advance_runner(game_at_bat, "B", "1", is_out)
        else:
            game_at_bat.outs += 1
        
        # analyze modifier
        due_to = ""
        for modifier in action.modifiers:
            if modifier == Modifiers.GROUNDER or modifier == Modifiers.GROUNDER_UNKNOWN:
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

        if is_out:
            logger.info ("Runner out after hit.  Out credited to pos %s. %s", game_at_bat.fielded_by, due_to)
        else:
            logger.info("Runner safe on base after defensive error by %s. %s", game_at_bat.fielded_by, due_to)

