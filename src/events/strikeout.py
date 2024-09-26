""" Strikeout Event

Runner striked out game event.
"""
import logging
from events.base_event import BaseEvent
from events.constants import Modifiers, EventCodes
from events.stolen_base import StolenBaseEvent
from events.caught_stealing import CaughtStealingEvent
from model.action_record import ActionRecord
from model.game_at_bat import GameAtBat

logger = logging.getLogger(__name__)

class StrikeoutEvent(BaseEvent):
    """ Strikeout Event """

    DROPPED_THIRD_STRIKE_PUTOUT : str = "23"  # K23

    def handle(self, game_at_bat : GameAtBat, action : ActionRecord):
        # attempt to grab play modifiers
        called = ""
        while len(game_at_bat.modifiers) > 0:
            called = game_at_bat.modifiers.pop(0)
            if called == Modifiers.CALLED_THIRD_STRIKE:
                called += "CALLED THIRD STRIKE "
            elif called == Modifiers.DOUBLE_PLAY:
                called += "DOUBLE PLAY "
            else:
                raise ValueError(f"Unknown modifier on strikeout! {called}")

        # game play result
        game_at_bat.outs += 1

        # handle extra play events
        op_detail = None
        was_dropped_third_strike_putout = False
        while len(op_details) > 0:
            op_detail = op_details.pop(0)
            if op_detail == self.DROPPED_THIRD_STRIKE_PUTOUT:
                was_dropped_third_strike_putout = True
            elif op_detail[0] != "+":
                self.fail("Expected K+ but received something otherwise.")
    
            # handle extra play
            added_play = op_detail[1:]
            if was_dropped_third_strike_putout:
                pass
            elif added_play[0:2] == EventCodes.STOLEN_BASE:
                base = added_play[2:]
                added_event = StolenBaseEvent()
                added_event.handle(game_at_bat, [base])
            elif added_play[0:2] == EventCodes.CAUGHT_STEALING:
                base = added_play[2:]
                added_event = CaughtStealingEvent()
                added_event.handle(game_at_bat, [base])
            elif added_play[0:2] == EventCodes.WILD_PITCH:
                logger.warning("Ignoring Wild Pitch adder to Strikeout Event!")
            else:
                self.fail(f"Unknown/Unhandled added play type: {added_play}")

        # log detail
        if was_dropped_third_strike_putout:
            logger.info("Third Strike Dropped but Player still out due to putout.  %s", called)
        else:
            logger.info("Player Striked Out.  %s", called)
