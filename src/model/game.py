""" Baseball Data Structures

Baseball data structures used throughout the application. 
"""
import logging
from model.game_play import GamePlay
from model.game_at_bat import GameAtBat
from model.game_substitution import GameSubstitution

logger = logging.getLogger(__name__)

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
                    msg = f"Outs out of alignment at top/bottom of inning.  Outs={last_at_bat.outs} " +\
                          f"LastHTFlag={last_at_bat.home_team_flag} ThisHTFlag={current_play.home_team_flag} " +\
                          f"LastInning={last_at_bat.inning} ThisInning={current_play.inning}"
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
            logger.info(f"Inning {inning} / Top - Visiting Team at Bat")
        elif last_at_bat is not None and last_at_bat.home_team_flag != game_at_bat.home_team_flag:
            logger.info(f"Inning {inning} / Bottom - Home Team at Bat")

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
