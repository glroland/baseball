""" Strikeout Event

Runner striked out game event.
"""
import logging
from events.base_event import BaseEvent
from events.constants import Modifiers, EventCodes
from events.stolen_base import StolenBaseEvent

logger = logging.getLogger(__name__)

class StrikeoutEvent(BaseEvent):
    """ Strikeout Event """

    def handle(self, game_at_bat, op_details):
        # attempt to grab play modifiers
        called = ""
        if len(game_at_bat.modifiers) > 0:
            called = game_at_bat.modifiers.pop(0)
            if called == Modifiers.CALLED_THIRD_STRIKE:
                called = "CALLED THIRD STRIKE"
            else:
                raise ValueError(f"Unknown modifier on strikeout! {called}")

        # game play result
        game_at_bat.outs += 1

        # handle extra play events
        op_detail = None
        while len(op_details) > 0:
            op_detail = op_details.pop(0)
            if op_detail[0] != "+":
                self.fail("Expected K+ but received something otherwise.")
    
            # handle extra play
            added_play = op_detail[1:]
            if added_play[0:2] == EventCodes.STOLEN_BASE:
                base = added_play[2:]
                added_event = StolenBaseEvent()
                added_event.handle(game_at_bat, [base])
            else:
                self.fail(f"Unknown/Unhandled added play type: {added_play}")

        # log detail
        logger.info("Player Striked Out.  %s", called)
