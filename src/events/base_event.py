""" Core Game Event

Base logic for game events.
"""
import logging
import re
from pydantic import BaseModel
from events.constants import Parameters
from model.action_record import ActionRecord
from model.game_state import GameState
from utils.data import to_json_string, fail

logger = logging.getLogger(__name__)

class BaseEvent(BaseModel):
    """ Base class for all game events.  """

    def handle(self, game_state : GameState, action : ActionRecord):
        """ Each Game Event Class should implement this method."""
        raise NotImplementedError()

    def pre_handle(self, game_state : GameState, action : ActionRecord):
        """ Debugging Method """
        logger.debug ("Action=<%s>, Groups=<%s>, Modifiers=<%s>, GameStatus=<%s>",
                     action.action,
                     action.groups,
                     action.modifiers,
                     game_state.get_game_status_string())

    def post_handle(self, game_state : GameState, action : ActionRecord):
        """ Debugging Method """
        logger.info("Post Event Processing Game Status:  %s", game_state.get_game_status_string())


    def __str__(self) -> str:
        return to_json_string(self)
