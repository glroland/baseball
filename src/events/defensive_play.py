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
        dp_event = play_list.pop(0)
        db_event_list = split_leading_num(dp_event)
        fielders = db_event_list.pop(0)
        game_at_bat.fielded_by = fielders[len(fielders) - 1]
        game_at_bat.outs += 1
        due_to = ""
        if len(game_at_bat.modifiers) > 0:
            modifier = game_at_bat.modifiers.pop(0)
            if modifier == Modifiers.GROUNDER:
                due_to = "Due to Ground Ball"
        logger.info ("Batter out after hit.  Out credited to pos %s %s", game_at_bat.fielded_by, due_to)
        if len(db_event_list) > 0:
            msg = f"Unhandled Fielded By Metadata.  {db_event_list}"
            logger.warning(msg)
            raise ValueError(msg)

        self.handle_advances(game_at_bat)

