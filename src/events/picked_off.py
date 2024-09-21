""" Picked Off Event

Runner picked off game event.
"""
import logging
import re
from events.base_event import BaseEvent
from utils.data import split_leading_num

logger = logging.getLogger(__name__)

class PickedOffEvent(BaseEvent):
    """ Picked Off Event """

    def handle(self, game_at_bat, op_details):
        details = op_details.pop()
        details_list = split_leading_num(details)
        logger.debug("Picked Off Base Details: %s", details_list)
        base = int(details_list.pop(0))

        # see if there was an error during the pick off
        override_po_due_to_error = False
        credited_to = ""
        if len(details_list) > 0:
            d = details_list.pop(0)    
            if re.match("^\(E[0-9]\)$", d):
                override_po_due_to_error = True
            elif re.match("^\([0-9]+\)$", d):
                credited_to = d
            else:
                self.fail(f"Unknown picked off detail: {d}")

        logger.warning("Picked Off Details Being Ignored!: %s", details_list)

        if override_po_due_to_error:
            logger.info("Fielding team attempted to pick off runner but errored out.  Runner safe.")
        else:
            logger.info("Runner Picked Off Base #%s by %s", base, credited_to)
            game_at_bat.outs += 1
            if base == 1:
                # Not error checking this one because it can happen with a batter going to base
                #if not game_at_bat.runner_on_1b:
                #    self.fail("Encountered runner picked off event but no runner on first.")
                game_at_bat.runner_on_1b = False
            elif base == 2:
                if not game_at_bat.runner_on_2b:
                    self.fail("Encountered runner picked off event but no runner on second.")
                game_at_bat.runner_on_2b = False
            elif base == 3:
                if not game_at_bat.runner_on_3b:
                    self.fail("Encountered runner picked off event but no runner on third.")
                game_at_bat.runner_on_3b = False
            else:
                self.fail(f"Unknown base encountered when processing runner picked off event: {base}")
