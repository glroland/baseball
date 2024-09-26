""" Error Event

Defensive error resulting in a runner progression game event.
"""
import logging
from events.base_event import BaseEvent
from events.constants import Modifiers
from model.action_record import ActionRecord
from model.game_at_bat import GameAtBat

logger = logging.getLogger(__name__)

class DefensiveErrorEvent(BaseEvent):
    """ Defensive Error Event """

    def handle(self, game_at_bat : GameAtBat, action : ActionRecord):
        fb = ""
        if len(op_details) > 0:
            game_at_bat.fielded_by = op_details.pop(0)
            fb = f"by {game_at_bat.fielded_by}"
        cause = ""
        while len(game_at_bat.modifiers) > 0:
            cause = game_at_bat.modifiers.pop(0)
            if cause == Modifiers.THROW:
                cause += "Due to Bad Throw"
            elif cause == Modifiers.SACRIFICE_HIT_BUNT:
                cause += "Due to Sacrifice Hit / Bunt"
        logger.info("Offensive Error by %s resulting in batter on base.  %s", cause, fb)

        self.advance_runner(game_at_bat, "B", "1")
