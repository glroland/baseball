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
from model.runner_adjustment import RunnerAdjustment
from model.game_state import GameState
from model.starter import Starter
from model.runner import Runner
from model.data import Data
from events.event_factory import EventFactory
from utils.data import to_json_string

logger = logging.getLogger(__name__)

# pylint: disable=too-few-public-methods,protected-access
class Game(BaseModel):
    """ Data Structure for a game chunk that is incrementally assembled as 
    the file is parsed.
    """

    game_id : str = None
    info_attributes : Dict[str, str] = {}
    starters : List[Starter] = []
    game_plays : List[GamePlay] = []
    data : List[Data] = []
    no_play_sub_player : str = None

    def get_last_at_bat(self) -> GameAtBat:
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

    # pylint: disable=too-many-arguments
    def new_at_bat(self,
                   inning,
                   home_team_flag,
                   player_code,
                   count,
                   pitches,
                   play):
        """ Generate a new at bat record, prepopulated with the latest game
            details for incrementing.

            inning - inning
            home_team_flag - true for home, false for visitor
            player_code - player code
            count - count
            pitches - pitches string
            play - play record
        """
        game_at_bat = GameAtBat()

        # propagate prior game state
        last_at_bat = self.get_last_at_bat()
        if last_at_bat is None:
            game_at_bat.game_state = GameState()
            logger.debug("No previous game state")
        else:
            logger.debug("Previous Game State = %s",
                         last_at_bat.game_state.get_game_status_string())

            game_at_bat.game_state = last_at_bat.game_state.clone()
            game_at_bat.game_state._inning = inning
            game_at_bat.game_state._top_of_inning_flag = home_team_flag is False

            if game_at_bat.game_state._top_of_inning_flag  != \
                last_at_bat.game_state._top_of_inning_flag:
                game_at_bat.game_state.on_batting_team_change()

        # add batter to game state
        batter = Runner("B")
        batter.player_code = player_code
        game_at_bat.game_state._runners.append(batter)

        # update values with incoming data values
        game_at_bat.player_code = player_code
        game_at_bat.count = count
        game_at_bat.pitches = pitches
        game_at_bat.play = play
        self.game_plays.append(game_at_bat)

        # log status of inning change
        if last_at_bat is None or last_at_bat.game_state._inning != game_at_bat.game_state._inning:
            logger.info("Inning %s / Top - Visiting Team at Bat", inning)
        elif last_at_bat is not None and \
            last_at_bat.game_state._top_of_inning_flag != \
            game_at_bat.game_state._top_of_inning_flag:
            logger.info("Inning %s / Bottom - Home Team at Bat", inning)

        # process each action under the play record
        EventFactory.create(game_at_bat)

        # validate the game after each at bat
        #self.validate()

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

        last_at_bat = self.get_last_at_bat()
        if last_at_bat is None:
            game_subst.game_state = GameState()
        else:
            game_subst.game_state = last_at_bat.game_state.clone()

        game_subst.player_to = player_to
        game_subst.player_from = player_from
        game_subst.players_team_home_flag = home_team_flag
        game_subst.batting_order = batting_order
        game_subst.fielding_position = fielding_position
        self.game_plays.append(game_subst)

        logger.info("Player <%s> substituted with <%s>", game_subst.player_from,
                    game_subst.player_to)
        return game_subst


    def new_runner_adjustment(self, runner_id, base):
        """ Implement a manual runner adjustment.

            runner_id - runner
            base - adjusted base
        """
        runner_adj = RunnerAdjustment()

        last_at_bat = self.get_last_at_bat()
        if last_at_bat is None:
            runner_adj.game_state = GameState()
        else:
            runner_adj.game_state = last_at_bat.game_state.clone()

        runner_adj.runner_code = runner_id
        runner_adj.adjusted_base = base
        self.game_plays.append(runner_adj)

        if runner_adj.game_state._top_of_inning_flag:
            runner_adj.game_state._top_of_inning_flag = False
        else:
            runner_adj.game_state._top_of_inning_flag = True
            runner_adj.game_state._inning += 1
        logger.info ("New Inning due to runner adjustment")

        logger.info("Runner <%s> manually adjusted to base <%s>", runner_adj.runner_code,
                    runner_adj.adjusted_base)

        runner = Runner("B")
        runner.player_code = runner_id
        runner_adj.game_state._runners.append(runner)

        runner_adj.game_state.action_advance_runner("B", base)

        return runner_adj


    def get_score(self):
        """ Get the current score of the game.
        
        Returns a tuple where visitor is first, home is second.
        """
        last_at_bat = self.get_last_at_bat()
        return last_at_bat.game_state.get_score()

    def on_game_end(self):
        """ Validate that the results of the game matches  the play by play data.
        
            game - game record
        """
        last_at_bat = self.get_last_at_bat()
        score_tuple = last_at_bat.game_state.get_score()
        logger.info("Game Ended!  ID=%s Score=%s-%s",
                    self.game_id,
                    score_tuple[0],
                    score_tuple[1])

    def is_valid(self):
        """ Validate the game and the state of its at bat objects. """
        # get 2 most recent at bats
        current_atbat = None
        prev_atbat = None
        i = len(self.game_plays) - 1
        while i >= 0:
            atbat = self.game_plays[i]
            if isinstance(atbat, GamePlay):
                if current_atbat is None:
                    current_atbat = atbat
                elif prev_atbat is None:
                    prev_atbat = atbat
                else:
                    break
            i -= 1

        # validate current at bat based on previous at bat
        if current_atbat is not None and prev_atbat is not None:
            current_atbat.game_state.validate_against_prev(prev_atbat.game_state)

    def validate_externally(self):
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

    def __str__(self) -> str:
        return to_json_string(self)
