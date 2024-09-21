""" Defensive Play Event

After a hit, the defense made a successful play on the ball/runner.
"""
import logging
from events.base_event import BaseEvent
from events.constants import Modifiers
from utils.data import split_leading_num

logger = logging.getLogger(__name__)

class DefensivePlayEvent(BaseEvent):
    """ Defensive Play Event """

    def handle(self, game_at_bat, play_list):
        """ Handle defensive play based on provided action list.exc_info=
        
        game_at_bat - game at bat
        play_list - list of offensive play components
        """
        logger.debug("Defensive Play.  Play_List<%s>", play_list)

        # First fielding event after hit
        logger.fatal("PLAY LIST??? %s", play_list)
        while len(play_list) > 0:
            play = play_list.pop(0)
            logger.fatal("PLAY??? %s", play)
            db_event_list = split_leading_num(play)
            fielders = db_event_list.pop(0)
            game_at_bat.fielded_by = fielders[len(fielders) - 1]
            game_at_bat.outs += 1
            due_to = ""
            if len(game_at_bat.modifiers) > 0:
                modifier = game_at_bat.modifiers.pop(0)
                if modifier == Modifiers.GROUNDER or modifier == Modifiers.GROUNDER_UNKNOWN:
                    due_to = "Due to Ground Ball"
                elif modifier == Modifiers.GROUNDER_DOUBLE_PLAY:
                    due_to = "Due to Ground Ball - Double Play"
                elif modifier == Modifiers.GROUNDER_TRIPLE_PLAY:
                    due_to = "Due to Ground Ball - Triple Play"
                elif modifier == Modifiers.LINED_INTO_DOUBLE_PLAY:
                    due_to = "Due to Lined Into Double Play"
                elif modifier == Modifiers.LINED_INTO_TRIPLE_PLAY:
                    due_to = "Due to Lined Into Triple Play"
                elif modifier[0] == Modifiers.LINE_DRIVE:
                    due_to = "Due to Line Drive"
                elif modifier == Modifiers.FORCE_OUT:
                    due_to = "Due to Force Out"
                elif modifier == Modifiers.FOUL:
                    due_to = "Due to Foul"
                elif modifier == Modifiers.FAN_INTERFERENCE:
                    due_to = "Due to Fan Interference"
                elif modifier == Modifiers.FLY_BALL_DOUBLE_PLAY:
                    due_to = "Due to Fly Ball Double Play"
                elif modifier[0] == Modifiers.FLY:
                    due_to = "Due to Fly Ball"
                elif modifier == Modifiers.SACRIFICE_FLY:
                    due_to = "Due to Sacrifice Fly"
                elif modifier == Modifiers.RUNNER_PASSED_ANOTHER_RUNNER:
                    due_to = "Due to Runner Passing Another Runner"
                elif modifier[0] == Modifiers.POP_FLY:
                    due_to = "Due to Pop Fly"
                elif modifier == Modifiers.SACRIFICE_HIT_BUNT:
                    due_to = "Due to Sacrifice Hit / Bunt"
                else:
                    msg = f"Unhandled Modifier!  {modifier}"
                    logger.error(msg)
                    raise ValueError(msg)

            logger.info ("Runner out after hit.  Out credited to pos %s. %s", game_at_bat.fielded_by, due_to)
            if len(db_event_list) > 0:
                logger.debug(f"Unhandled Fielded By Metadata.  {db_event_list}")

        self.handle_advances(game_at_bat)

