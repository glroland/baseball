""" Stolen Base Event

Stolen base game event.
"""
import logging
from events.base_event import BaseEvent

logger = logging.getLogger(__name__)

class StolenBaseEvent(BaseEvent):
    """ Stolen Base Event """

    def handle(self, game_at_bat, op_details):
        base = op_details.pop(0)
        if base == "2":
            if not game_at_bat.runner_on_1b:
                self.fail("Runner stealing 2nd but there was no runner on 1st")
            game_at_bat.runner_on_1b = False
            game_at_bat.runner_on_2b = True
        elif base == "3":
            if not game_at_bat.runner_on_2b:
                self.fail("Runner stealing 3rd but there was no runner on 2nd")
            game_at_bat.runner_on_2b = False
            game_at_bat.runner_on_3b = True
        elif base == "H":
            if not game_at_bat.runner_on_3b:
                self.fail("Runner stealing home but there was no runner on 3rd")
            game_at_bat.runner_on_3b = False
            game_at_bat.score()
        else:
            self.fail(f"Unknown Stolen Base # {base}")

        logging.info("Runner stole base:", base)
