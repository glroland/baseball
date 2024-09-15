""" Baseball Data Structures

Baseball data structures used throughout the application. 
"""
import logging

logger = logging.getLogger(__name__)

# pylint: disable=too-few-public-methods
class Starter:
    """ Starter Entry Fields """

    def __init__(self):
        self.player_code = None
        self.player_name = None
        self.home_team_flag = None
        self.batting_order = None
        self.fielding_position = None

    def __str__(self) -> str:
        return f"""{{ "player_code": "{self.player_code}", "player_name": """ \
               f""""{self.player_name}", "home_team_flag": {str(self.home_team_flag).lower()}, """ \
               f""""batting_order": {self.batting_order}, "fielding_position": """ \
               f"""{self.fielding_position} }}"""

# pylint: disable=too-few-public-methods
class GamePlay:
    """ Base Class of Game Play Types """
    # pylint: disable=unnecessary-pass
    pass

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


# pylint: disable=too-few-public-methods
class GameSubstitution(GamePlay):
    """ Player Substitution Event """

    def __init__(self):
        self.player_code = None
        self.player_name = None
        self.home_team_flag = None
        self.batting_order = None
        self.fielding_position = None

    def __str__(self) -> str:
        return f"""{{ "play_type": "Substitution", "player_code": "{self.player_code}", """ \
               f""""player_name": "{self.player_name}", "home_team_flag": """ \
               f"""{str(self.home_team_flag).lower()}, "batting_order": {self.batting_order}, """ \
               f""""fielding_position": {self.fielding_position} }}"""


# pylint: disable=too-few-public-methods
class Data:
    """ Represents the end of game data records, such as earned runs. """

    def __init__(self):
        self.data_type = None
        self.pitcher_player_code = None
        self.quantity = None

    def __str__(self) -> str:
        return f"""{{ "data_type": "{self.data_type}", "pitcher_player_code": """ + \
               f""""{self.pitcher_player_code}", "quantity": {self.quantity} }}"""


# pylint: disable=too-few-public-methods
class Game:
    """ Data Structure for a game chunk that is incrementally assembled as 
    the file is parsed.
    """

    def __init__(self):
        self.game_id = None
        self.info_attributes = {}
        self.starters = []
        self.game_plays = []
        self.data = []

    def get_last_at_bat(self):
        if len(self.game_plays) > 0:
            i = len(self.game_plays) - 1
            last_play = None
            while i >= 0:
                if isinstance(self.game_plays[i], GamePlay):
                    last_play = self.game_plays[len(self.game_plays) - 1]
                    return last_play
                i -= 1
        return None

    def new_at_bat(self,
                   inning,
                   home_team_flag,
                   player_code,
                   count,
                   pitches,
                   game_event):
        """ Generate a new at bat record, prepopulated with the latest game
            details for incrementing.

            inning - inning
            home_team_flag - true for home, false for visitor
            player_code - player code
            count - count
            pitches - pitches string
            game_event - game event string
        """
        game_at_bat = GameAtBat()
        last_at_bat = self.get_last_at_bat()
        if last_at_bat != None:
            game_at_bat.outs = last_at_bat.outs
            game_at_bat.runner_on_1b = last_at_bat.runner_on_1b
            game_at_bat.runner_on_2b = last_at_bat.runner_on_2b
            game_at_bat.runner_on_3b = last_at_bat.runner_on_3b
            game_at_bat.score_home = last_at_bat.score_home
            game_at_bat.score_visitor = last_at_bat.score_visitor

            if last_at_bat.home_team_flag != home_team_flag:
                # validate outs
                if last_at_bat.outs != 3:
                    msg = f"Outs out of alignment at top/bottom of inning.  {last_at_bat.outs}"
                    logger.error(msg)
                    raise ValueError(msg)

                game_at_bat.outs = 0

        game_at_bat.inning = inning
        game_at_bat.home_team_flag = home_team_flag
        game_at_bat.player_code = player_code
        game_at_bat.count = count
        game_at_bat.pitches = pitches
        game_at_bat.game_event = game_event

        self.game_plays.append(game_at_bat)
        return game_at_bat

    def __str__(self) -> str:
        response = f"""{{ "id": "{self.game_id}", "info_attributes": {self.info_attributes}, """
        response += """"starters": [ """
        c = 0
        for starter in self.starters:
            if c > 0:
                response += ", "
            response += str(starter)
            c += 1
        response += " ], "
        response += """"game_plays": [ """
        c = 0
        for play in self.game_plays:
            if c > 0:
                response += ", "
            response += str(play)
            c += 1
        response += " ], "
        response += """"data": [ """
        c = 0
        for d in self.data:
            if c > 0:
                response += ", "
            response += str(d)
            c += 1
        response += " ] "
        response += "}"
        return response
