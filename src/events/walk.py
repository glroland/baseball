""" Walk Event

Runner walked game event.
"""
import logging
from events.base_event import BaseEvent
from events.constants import EventCodes
from events.stolen_base import StolenBaseEvent
from events.caught_stealing import CaughtStealingEvent

logger = logging.getLogger(__name__)

class WalkEvent(BaseEvent):
    """ Walk Event """

    def handle(self, game_at_bat, op_details):
        """ Walk the player
        
            game_at_bat - game at bat
            op_details - offensive play details
        """
        logger.info("Batter Walked")
            
        self.advance_runner(game_at_bat, "B", "1")

        # handle extra play events
        op_detail = None
        while len(op_details) > 0:
            op_detail = op_details.pop(0)
            if op_detail[0] != "+":
                self.fail("Expected W+ but received something otherwise.")
    
            # handle extra play
            added_play = op_detail[1:]
            if added_play[0:2] == EventCodes.STOLEN_BASE:
                base = added_play[2:]
                added_event = StolenBaseEvent()
                added_event.handle(game_at_bat, [base])
            elif added_play[0:2] == EventCodes.CAUGHT_STEALING:
                base = added_play[2:]
                added_event = CaughtStealingEvent()
                added_event.handle(game_at_bat, [base])
            else:
                self.fail(f"Unknown/Unhandled added play type: {added_play}")
