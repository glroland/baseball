""" Walk Event

Runner walked game event.
"""
import logging
from events.base_event import BaseEvent
from model.action_record import ActionRecord
from model.game_at_bat import GameAtBat

logger = logging.getLogger(__name__)

class WalkEvent(BaseEvent):
    """ Walk Event """

    def handle(self, game_at_bat : GameAtBat, action : ActionRecord):
        """ Walk the player
        
            game_at_bat - game at bat
            action - offensive play details
        """
        logger.info("Batter Walked")

        self.advance_runner(game_at_bat, "B", "1")
