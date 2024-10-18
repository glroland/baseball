""" Picked Off Event

Runner picked off game event.
"""
import logging
from events.base_event import BaseEvent
from events.constants import Parameters
from utils.data import split_leading_chars_from_numbers, fail
from utils.baseball import validate_base

logger = logging.getLogger(__name__)

class PickedOffEvent(BaseEvent):
    """ Picked Off Event """

    def handle(self):
        logger.info("Runner Picked Off - %s - %s", self.action.action,
                    self.game_state.get_game_status_string())

        # Extract the tailing numbers
        components = split_leading_chars_from_numbers(self.action.action)
        if len(components) != 2:
            fail(f"Illegal action for PO!  {self.action.action}  ComponentLen={len(components)}")
        base = components[1]
        validate_base(base)
        logger.debug("Picked Off Base To: %s", base)

        # see if there was an error during the pick off
        override_po_due_to_error = False
        credited_to = ""
        if len(self.action.groups) > 0:
            group = self.action.groups[0]
            if len(group) > 0 and group[0] == Parameters.ERROR:
                logger.debug("Overriding pick off due to error")
                override_po_due_to_error = True

        if override_po_due_to_error:
            logger.info("Fielding team attempted to pick off runner but errored out.  Runner safe.")
        else:
            logger.info("Runner Picked Off Base #%s by %s", base, credited_to)
            self.game_state.on_out(base)
            # TODO Empty 1st on B is potentially not error due to its ability to
            # occur when no one is yet on base.
