""" Baseball Data Structures

Baseball data structures used throughout the application. 
"""
import logging
from model.game_play import GamePlay

logger = logging.getLogger(__name__)

# pylint: disable=too-few-public-methods
# pylint: disable=too-many-instance-attributes
class GameAtBat(GamePlay):
    """ At Bat Record for a Game """

    def __init__(self):
        self.inning = None
        self.home_team_flag = None
        self.player_code = None
        self.count = None
        self.pitches = None
        self.game_event = None
        self.basic_play = None
        self.modifiers = None
        self.advance = None
        self.outs = 0
        self.runner_on_1b = False
        self.runner_on_2b = False
        self.runner_on_3b = False
        self.score_home = 0
        self.score_visitor = 0
        self.hit_to_location = None
        self.fielded_by = None

    def __str__(self) -> str:
        return f"""{{ "play_type": "AtBat", "inning": "{self.inning}", """ \
               f""""home_team_flag": {str(self.home_team_flag).lower()}, "player_code": """ \
               f""""{self.player_code}", "count": {self.count}, "pitches": """ \
               f""""{self.pitches}", "game_event": "{self.game_event}", """ \
               f""""basic_play": {self.basic_play}, "modifiers": {self.modifiers}, """ \
               f""""advance": {self.advance}, "outs": {self.outs}, """ \
               f""""runner_on_1b": {self.runner_on_1b}, "runner_on_2b": {self.runner_on_2b}, """ \
               f""""runner_on_3b": {self.runner_on_3b}, "score_home": {self.score_home}, """ \
               f""""score_visitor": {self.score_visitor} }}"""
