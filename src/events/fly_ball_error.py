""" Fly Ball Error Event

Fly Ball Error game event.
"""
import logging
from events.base_event import BaseEvent
from model.action_record import ActionRecord
from model.game_state import GameState

logger = logging.getLogger(__name__)

class FlyBallErrorEvent(BaseEvent):
    """ Fly Ball Error Event """

    def handle(self, game_state : GameState, action : ActionRecord):
        """ Fielding team made an error on a fly ball.  Putting the batter on base.
        
            game_at_bat - game at bat
            op_details - offensive play details
        """
        logger.info("Fielding error on a fly ball.  Putting batter on base.")

        game_state.action_advance_runner("B", "1")
