""" Double Event

Runner hit a double game event.
"""
import logging
from events.base_event import BaseEvent

logger = logging.getLogger(__name__)

class DoubleEvent(BaseEvent):
    """ Double Event """

    def handle(self, game_at_bat, details):
        if len(details) > 0:
            game_at_bat.fielded_by = details.pop(0)
        if len(game_at_bat.modifiers) > 0:
            game_at_bat.hit_to_location = game_at_bat.modifiers.pop(0)
        if len(game_at_bat.modifiers) > 1:
            self.fail( f"Too many modifiers!  {game_at_bat.modifiers}")
        logger.info("Player Hit Double to %s.  Fielded By %s.",
                    game_at_bat.hit_to_location, game_at_bat.fielded_by)

        self.advance_runner(game_at_bat, "B", "2")
