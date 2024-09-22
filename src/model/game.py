""" Baseball Data Structures

Baseball data structures used throughout the application. 
"""
import logging
from datetime import datetime, timedelta
from typing import List, Dict
from pydantic import BaseModel
from pybaseball import statcast
from model.game_play import GamePlay
from model.game_at_bat import GameAtBat
from model.game_substitution import GameSubstitution
from model.starter import Starter
from model.data import Data
from model.game_play import GamePlay

logger = logging.getLogger(__name__)

# pylint: disable=too-few-public-methods
class Game(BaseModel):
    """ Data Structure for a game chunk that is incrementally assembled as 
    the file is parsed.
    """

    game_id : str = None
    info_attributes : Dict[str, str] = {}
    starters : List[Starter] = []
    game_plays : List[GamePlay] = []
    data : List[Data] = []

    def get_last_at_bat(self):
        """ Locate and return the last at bat record.  """
        if len(self.game_plays) > 0:
            i = len(self.game_plays) - 1
            last_play = None
            while i >= 0:
                if isinstance(self.game_plays[i], GamePlay):
                    last_play = self.game_plays[len(self.game_plays) - 1]
                    return last_play
                i -= 1
        return None

    def propogate_game_stats(self, current_play, force_overwrite_team_flag = False):
        """ Copies the running outs, runs, players on base, etc from the last batting
            event to the current one.
            
            current_play - current play object to receive attribute values
        """
        last_at_bat = self.get_last_at_bat()
        if last_at_bat is not None:
            current_play.outs = last_at_bat.outs
            current_play.runner_on_1b = last_at_bat.runner_on_1b
            current_play.runner_on_2b = last_at_bat.runner_on_2b
            current_play.runner_on_3b = last_at_bat.runner_on_3b
            current_play.score_home = last_at_bat.score_home
            current_play.score_visitor = last_at_bat.score_visitor

            if force_overwrite_team_flag:
                current_play.home_team_flag = last_at_bat.home_team_flag

            if last_at_bat.home_team_flag != current_play.home_team_flag:
                # validate outs
                if last_at_bat.outs != 3:
                    msg = "Outs out of alignment at top/bottom of inning. " + \
                          f"Outs={last_at_bat.outs} " + \
                          f"LastHTFlag={last_at_bat.home_team_flag} " + \
                          f"ThisHTFlag={current_play.home_team_flag} " + \
                          f"LastInning={last_at_bat.inning} " + \
                          f"ThisInning={current_play.inning}"
                    logger.error(msg)
                    raise ValueError(msg)

                current_play.outs = 0
                current_play.runner_on_1b = False
                current_play.runner_on_2b = False
                current_play.runner_on_3b = False

        return last_at_bat

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
        game_at_bat.inning = inning
        game_at_bat.home_team_flag = home_team_flag
        game_at_bat.player_code = player_code
        game_at_bat.count = count
        game_at_bat.pitches = pitches
        game_at_bat.game_event = game_event
        last_at_bat = self.propogate_game_stats(game_at_bat)
        self.game_plays.append(game_at_bat)

        # log status of inning change
        if last_at_bat is None or last_at_bat.inning != game_at_bat.inning:
            logger.info("Inning %s / Top - Visiting Team at Bat", inning)
        elif last_at_bat is not None and last_at_bat.home_team_flag != game_at_bat.home_team_flag:
            logger.info("Inning %s / Bottom - Home Team at Bat", inning)

        return game_at_bat

    def new_substitution(self,
                   player_to,
                   player_from,
                   home_team_flag,
                   batting_order,
                   fielding_position):
        """ Generate a new at bat record, prepopulated with the latest game
            details for incrementing.

            inning - inning
            home_team_flag - true for home, false for visitor
            player_code - player code
            count - count
            pitches - pitches string
            game_event - game event string
        """
        game_subst = GameSubstitution()
        game_subst.player_to = player_to
        game_subst.player_from = player_from
        game_subst.players_team_home_flag = home_team_flag
        game_subst.batting_order = batting_order
        game_subst.fielding_position = fielding_position
        self.propogate_game_stats(game_subst, force_overwrite_team_flag=True)
        self.game_plays.append(game_subst)

        logger.info("Player <%s> substituted with <%s>", game_subst.player_from,
                    game_subst.player_to)
        return game_subst

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

    def score(self):
        """ Get the current score of the game.
        
        Returns a tuple where visitor is first, home is second.
        """
        last_at_bat = self.get_last_at_bat()
        if last_at_bat is None:
            return [0, 0]
        v = last_at_bat.score_visitor
        if v is None:
            v = 0
        h = last_at_bat.score_home
        if h is None:
            h = 0
        return [v, h]

    def game_end(self):
        """ Validate that the results of the game matches  the play by play data.
        
            game - game record
        """
        score_tuple = self.score()
        logger.info("Game Ended!  ID=%s Score=%s-%s",
                    self.game_id,
                    score_tuple[0],
                    score_tuple[1])


    def validate(self):
        """ Validates the scores and other calculated attributes based on official
            game data from a third party service.
        """
        score_tuple = self.score()

        # validate final score
        date_str = self.info_attributes["date"]
        date = datetime.strptime(date_str, '%Y/%m/%d')
        home_team = self.info_attributes["hometeam"]
        #visiting_team = self.info_attributes["visteam"]
        start_dt = date - timedelta(days=1)
        stats_all = statcast(start_dt=datetime.strftime(start_dt, '%Y-%m-%d'),
                             end_dt=datetime.strftime(date, '%Y-%m-%d'),
                             team=home_team)
        #logger.fatal(stats_all.head())
        game_stats = stats_all.dropna(subset=['home_score', 'away_score'])
        if len(game_stats) != 1:
            msg = "Incorrect number of scores in gamestats dataset!  " + \
                  f"Expected 1 but actuals = {len(game_stats)}"
            logger.fatal(msg)
            raise ValueError(msg)
        home_score = int(game_stats["home_score"])
        away_score = int(game_stats["away_score"])
        if home_score != score_tuple[1] or away_score != score_tuple[0]:
            msg = f"Score Mismatch!  Actual={away_score}-{home_score}.  " + \
                  f"Calculated={score_tuple[0]}-{score_tuple[1]}"
            logger.fatal(msg)
            raise ValueError(msg)
