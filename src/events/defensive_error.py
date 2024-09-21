""" Error Event

Defensive error resulting in a runner progression game event.
"""
import logging
from events.base_event import BaseEvent
from events.constants import Modifiers

logger = logging.getLogger(__name__)

class DefensiveErrorEvent(BaseEvent):
    """ Defensive Error Event """

    def handle(self, game_at_bat, op_details):
        fb = ""
        if len(op_details) > 0:
            game_at_bat.fielded_by = op_details.pop(0)
            fb = f"by {game_at_bat.fielded_by}"
        cause = ""
        if len(game_at_bat.modifiers) > 0:
            cause = game_at_bat.modifiers.pop(0)
            if cause == Modifiers.THROW:
                cause = "Due to Throw By "
        logger.info("Offensive Error Getting Batter on Base.  %s %s", cause, fb)

        self.advance_runner(game_at_bat, "B", "1")
