""" Picked Off Event

Runner picked off game event.
"""
import logging
import re
from events.base_event import BaseEvent
from utils.data import split_leading_chars_from_numbers, fail
from utils.baseball import validate_base
from model.action_record import ActionRecord
from model.game_state import GameState

logger = logging.getLogger(__name__)

class PickedOffEvent(BaseEvent):
    """ Picked Off Event """

    def handle(self, game_state : GameState, action : ActionRecord):
        logger.info("Runner Picked Off - %s - %s", action.action, game_state.get_game_status_string())

        # Extract the tailing numbers
        components = split_leading_chars_from_numbers(action.action)
        if len(components) != 2:
            fail(f"Illegal action for PO!  {action.action}  ComponentLen={len(components)}")
        base = components[1]
        validate_base(base, first_allowed=False)
        logger.debug("Picked Off Base To: %s", base)





        # see if there was an error during the pick off
        override_po_due_to_error = False
        credited_to = ""
        #if len(details_list) > 0:
        #    d = details_list.pop(0)
        #    if re.match("^\\(E[0-9]\\)$", d):
        #        override_po_due_to_error = True
        #    elif re.match("^\\([0-9]+\\)$", d):
        #        credited_to = d
        #    else:
        #        self.fail(f"Unknown picked off detail: {d}")



        if override_po_due_to_error:
            logger.info("Fielding team attempted to pick off runner but errored out.  Runner safe.")
        else:
            logger.info("Runner Picked Off Base #%s by %s", base, credited_to)
            game_state.on_out()
            if base in ["1", 1]:
                # TODO Not error checking this one because it can happen with a batter going to base
                if not game_state.is_on_first():
                    fail("Encountered runner picked off event but no runner on first.")
                game_state._first = False
            elif base in ["2", 2]:
                if not game_state.is_on_second():
                    fail("Encountered runner picked off event but no runner on second.")
                game_state._second = False
            elif base in ["3", 3]:
                if not game_state.is_on_third():
                    fail("Encountered runner picked off event but no runner on third.")
                game_state._third = False
            else:
                fail(f"Unknown base encountered with runner picked off event: {base}")
