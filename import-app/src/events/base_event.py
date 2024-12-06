""" Core Game Event

Base logic for game events.
"""
import logging
from pydantic import BaseModel
from model.action_record import ActionRecord
from model.game_state import GameState
from model.play_record import PlayRecord
from utils.data import to_json_string

logger = logging.getLogger(__name__)

class BaseEvent(BaseModel):
    """ Base class for all game events.  """

    game_state : GameState = None
    action : ActionRecord = None
    play_record : PlayRecord = None

    def get_play_type_code(self) -> str:
        """ Return the play type code. """
        return None

    def handle(self):
        """ Each Game Event Class should implement this method."""
        raise NotImplementedError()

    def pre_handle(self):
        """ Debugging Method """
        logger.debug ("Action=<%s>, Groups=<%s>, Modifiers=<%s>, GameStatus=<%s>",
                     self.action.action,
                     self.action.groups,
                     self.action.modifiers,
                     self.game_state.get_game_status_string())

    # pylint: disable=unused-argument
    def post_handle(self):
        """ Debugging Method """
        logger.debug("Post Event Processing Game Status:  %s",
                     self.game_state.get_game_status_string())

    def __str__(self) -> str:
        return to_json_string(self)
