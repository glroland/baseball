""" Caught Stealing Event

Runner caught stealing a base game event.
"""
import logging
from events.base_event import BaseEvent
from events.constants import EventCodes
from utils.data import split_leading_chars_from_numbers, get_base_as_int, fail

logger = logging.getLogger(__name__)

class CaughtStealingEvent(BaseEvent):
    """ Caught Stealing Event """

    def get_play_type_code(self) -> str:
        """ Get the play type code. """
        return "B"

    def handle(self):
        base = ""
        if self.action.action in [EventCodes.CAUGHT_STEALING_HOME,
                                  EventCodes.PICKED_OFF_CAUGHT_STEALING_HOME]:
            base = "H"
        else:
            components = split_leading_chars_from_numbers(self.action.action)
            base = components[1]
        logger.debug("Stolen Base.  Base=%s Action=%s", base, self.action)

        # Check to see if there are details being ignored
        error_flag = False
        credited_to = ""
        if len(self.action.groups) > 0:
            if self.action.groups[0].find("E") != -1:
                error_flag = True
                credited_to = f"Error by {self.action.groups[0]}"
            else:
                credited_to = f"Crediting to {self.action.groups[0]}"

        # determine source base
        base_int = get_base_as_int(base)
        original_base_int = base_int - 1
        runner = self.game_state.get_runner_from_original_base(original_base_int)
        if runner is None:
            fail("No runner for original base!  {original_base_int}")

        # progress runner due to error
        if error_flag:
            logger.info("Player almost caught stealing but safe due to error. B#%s %s",
                        base, credited_to)
            self.game_state.action_advance_runner(runner.original_base, base, False)
        else:
            # mark the player out
            logger.info("Player Caught Stealing to Base #%s %s", base, credited_to)
            if not runner.is_out and runner.current_base == "H":
                #TODO Reverse Score logic
                fail("Runner was advanced home but was out earlier.  Need to reverse score.")
            self.game_state.on_out(runner.current_base)
