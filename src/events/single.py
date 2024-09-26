""" Single Event

Runner hit a single game event.
"""
import logging
from events.base_event import BaseEvent
from model.action_record import ActionRecord
from model.game_at_bat import GameAtBat

logger = logging.getLogger(__name__)

class SingleEvent(BaseEvent):
    """ Single Event """

    def handle(self, game_at_bat : GameAtBat, action : ActionRecord):

        #if len(op_details) > 0:
        #    game_at_bat.fielded_by = op_details.pop(0)
        #if len(game_at_bat.modifiers) > 0:
        #    game_at_bat.hit_to_location = game_at_bat.modifiers.pop(0)
        #if len(game_at_bat.modifiers) > 1:
        #    self.fail( f"Too many modifiers!  {game_at_bat.modifiers}")
        #logger.info("Player Hit Single to %s.  Fielded By %s.",
        #            game_at_bat.hit_to_location, game_at_bat.fielded_by)
        logger.info ("Batter hit single.")

        self.advance_runner(game_at_bat, "B", "1")
