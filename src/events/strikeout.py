""" Strikeout Event

Runner striked out game event.
"""
import logging
from events.base_event import BaseEvent
from events.constants import EventCodes
from model.action_record import ActionRecord
from model.game_state import GameState
from utils.data import fail

logger = logging.getLogger(__name__)

class StrikeoutEvent(BaseEvent):
    """ Strikeout Event """

    DROPPED_THIRD_STRIKE_PUTOUT : str = "K23"

    def handle(self, game_state : GameState, action : ActionRecord):
        due_to = ""
        runner_saved = False

        # Check for dropped putout
        if action.action == self.DROPPED_THIRD_STRIKE_PUTOUT:
            #runner_saved = True
            due_to += "Dropped third stike putout. "

        # Unknown strikeout action
        elif len(action.action) > 1:
            fail(f"Unknown action type: {action.action}")

        # review chained actions
        chained_action = action.chain_to
        while chained_action is not None:
            if chained_action.action == EventCodes.WILD_PITCH:
                due_to += "Wild Pitch, saving runner. "
                runner_saved = True
                chained_action.handled_flag = True

            elif chained_action.action == EventCodes.PASSED_BALL:
                due_to += "Passed Ball, saving runner. "
                runner_saved = True
                chained_action.handled_flag = True

            chained_action = chained_action.chain_to

        called = ""
        #while len(game_at_bat.modifiers) > 0:
        #    called = game_at_bat.modifiers.pop(0)
        #    if called == Modifiers.CALLED_THIRD_STRIKE:
        #        called += "CALLED THIRD STRIKE "
        #    elif called == Modifiers.DOUBLE_PLAY:
        #        called += "DOUBLE PLAY "
        #    else:
        #        raise ValueError(f"Unknown modifier on strikeout! {called}")

        # did the batter already out from an advancement?
        batter_already_out = False
        for advance in game_state._completed_advancements:
            if advance.base_from == "B" and advance.was_out:
                batter_already_out = True

        # game play result
        if runner_saved:
            game_state.action_advance_runner("B", "1", False)
        elif batter_already_out:
            logger.info("Batter already out from advancement.  Skipping strikeout...")
        else:
            game_state.on_out("B")

        # handle extra play events
        #op_detail = None
        #while len(op_details) > 0:
        #    op_detail = op_details.pop(0)
        #    if op_detail == self.DROPPED_THIRD_STRIKE_PUTOUT:
        #        was_dropped_third_strike_putout = True
        #    elif op_detail[0] != "+":
        #        self.fail("Expected K+ but received something otherwise.")

        #    # handle extra play
        #    added_play = op_detail[1:]
        #    if was_dropped_third_strike_putout:
        #        pass
        #    elif added_play[0:2] == EventCodes.STOLEN_BASE:
        #        base = added_play[2:]
        #        added_event = StolenBaseEvent()
        #        added_event.handle(game_at_bat, [base])
        #    elif added_play[0:2] == EventCodes.CAUGHT_STEALING:
        #        base = added_play[2:]
        #        added_event = CaughtStealingEvent()
        #        added_event.handle(game_at_bat, [base])
        #    elif added_play[0:2] == EventCodes.WILD_PITCH:
        #        logger.warning("Ignoring Wild Pitch adder to Strikeout Event!")
        #    else:
        #        self.fail(f"Unknown/Unhandled added play type: {added_play}")

        # log detail
        if runner_saved:
            logger.info("Runner saved from strikeout.  %s  %s", called, due_to)
        else:
            logger.info("Player Striked Out.  %s  %s", called, due_to)
