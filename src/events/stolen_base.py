""" Stolen Base Event

Stolen base game event.
"""
import logging
from events.base_event import BaseEvent
from utils.data import fail
from utils.baseball import validate_base
from model.advance_record import AdvanceRecord

logger = logging.getLogger(__name__)

class StolenBaseEvent(BaseEvent):
    """ Stolen Base Event """

    def advance_if_not_already_handled(self, game_state, base_from, base_to):
        """ Advance the runner, if this event has not already been handled
            through an explicit advance
            
            game_state - game state
            base_from - starting base
            base_to - ending base
        """
        # was the advancement already handled?
        advance = AdvanceRecord()
        advance.base_from = base_from
        advance.base_to = base_to
        advance.was_out = False
        if advance.is_completed(game_state._completed_advancements):
            logger.debug("Stolen Base event already handled.")
            return

        # advance the runner
        game_state.action_advance_runner(base_from, base_to, False)

    def handle(self):
        logger.info("Stealing Base - %s - %s", self.action.action,
                    self.game_state.get_game_status_string())

        # Extract the tailing numbers
        base_to = self.action.action[2:]
        validate_base(base_to, first_allowed=False)

        # determine if the advancement was already completed
        if base_to in ["2", 2]:
            self.advance_if_not_already_handled(self.game_state, "1", "2")
        elif base_to in ["3", 3]:
            self.advance_if_not_already_handled(self.game_state, "2", "3")
        elif base_to in ["H", 4]:
            self.advance_if_not_already_handled(self.game_state, "3", "H")
