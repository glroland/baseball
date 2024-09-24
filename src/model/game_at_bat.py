""" Baseball Data Structures

Baseball data structures used throughout the application. 
"""
import logging
from typing import List
from model.game_play import GamePlay

logger = logging.getLogger(__name__)

# pylint: disable=too-few-public-methods
# pylint: disable=too-many-instance-attributes
class GameAtBat(GamePlay):
    """ At Bat Record for a Game """
    player_code : str = None
    count : int = None
    pitches : int = None
    basic_play : str = None
    modifiers : List[str] = None
    advances : List[str] = None
    hit_to_location : int = None
    fielded_by : str = None

    def __str__(self) -> str:
        return f"""{{ "play_type": "AtBat", "inning": "{self.inning}", """ \
               f""""home_team_flag": {str(self.home_team_flag).lower()}, "player_code": """ \
               f""""{self.player_code}", "count": {self.count}, "pitches": """ \
               f""""{self.pitches}", "game_event": "{self.game_event}", """ \
               f""""basic_play": {self.basic_play}, "modifiers": {self.modifiers}, """ \
               f""""advances": {self.advances}, "outs": {self.outs}, """ \
               f""""runner_on_1b": {self.runner_on_1b}, "runner_on_2b": {self.runner_on_2b}, """ \
               f""""runner_on_3b": {self.runner_on_3b}, "score_home": {self.score_home}, """ \
               f""""score_visitor": {self.score_visitor} }}"""
