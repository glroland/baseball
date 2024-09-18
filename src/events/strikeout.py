""" Strikeout Event

Runner striked out game event.
"""
import logging
from events.base_event import BaseEvent
from events.constants import Modifiers

logger = logging.getLogger(__name__)

class StrikeoutEvent(BaseEvent):
    """ Strikeout Event """

    def handle(self, game_at_bat, op_details):
        called = ""
        if len(game_at_bat.modifiers) > 0:
            called = game_at_bat.modifiers.pop(0)
            if called == Modifiers.CALLED_THIRD_STRIKE:
                called = "CALLED THIRD STRIKE"
            else:
                raise ValueError(f"Unknown modifier on strikeout! {called}")
        logger.info("Player Striked Out.  %s", called)
        game_at_bat.outs += 1
