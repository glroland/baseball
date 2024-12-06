""" Baseball Data Structures

Baseball data structures used throughout the application. 
"""
from pydantic import BaseModel
from model.game_state import GameState
from utils.data import to_json_string

# pylint: disable=too-few-public-methods
class GamePlay(BaseModel):
    """ Base Class of Game Play Types """
    game_state : GameState = None

    def __str__(self) -> str:
        """ Create JSON string representation of the object. """
        return to_json_string(self)
