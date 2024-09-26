""" Baseball Data Structures

Baseball data structures used throughout the application. 
"""
from pydantic import BaseModel
from utils.data import to_json_string

# pylint: disable=too-few-public-methods
class GamePlay(BaseModel):
    """ Base Class of Game Play Types """
    inning : int = None
    home_team_flag : bool = False
    outs : int = 0
    runner_on_1b : bool = False
    runner_on_2b : bool = False
    runner_on_3b : bool = False
    score_home : int = 0
    score_visitor : int = 0

    def __str__(self) -> str:
        return to_json_string(self)
