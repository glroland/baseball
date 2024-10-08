""" Game Play Event Pipeline

Data pipeline for events associated with a game play.
"""
from typing import List
import logging
from pipelines.base_pipeline import BasePipeline
from model.game import Game
from model.play_record import PlayRecord
from model.game_play import GamePlay
from utils.data import fail

logger = logging.getLogger(__name__)

class GamePlayEventPipeline(BasePipeline):
    """ Game Play Event Data Pipeline """

    game : Game = None

    record : List[str] = None
    inning : int = 0
    home_team_flag : bool = False
    game_play_model : GamePlay = None

    player_code : str = None
    pitch_count : str = None
    pitches : str = None
    play : PlayRecord = None

    sub_player_tobe : str = None
    batting_order : int = None
    fielding_position : int = None
    players_team_home_flag : bool = None

    adjusted_base : str = None

    def __handle_sub(self):
        logger.info("Handling substituion...")
        self.game_play_model = self.game.new_substitution(player_to=self.game.no_play_sub_player,
                            player_from=self.player_code,
                            home_team_flag=self.players_team_home_flag,
                            batting_order=self.batting_order,
                            fielding_position=self.fielding_position)


    def __handle_new_play(self):
        # validate at bat metadata
        if self.play is None:
            fail("Play is empty, meaning the NP record wasn't picked up prior to the sub " + \
                      f"record! Game={self.game.game_id} " + \
                      f"SubFrom={self.player_code} " + \
                      f"SubToBe={self.sub_player_tobe} " + \
                      f"HomeTeamFlag={self.players_team_home_flag} " + \
                      f"FieldingPosition={self.fielding_position} " + \
                      f"BattingOrder={self.batting_order}")

        # create at bat model
        self.game_play_model = self.game.new_at_bat(
                    inning = self.inning,
                    home_team_flag = self.home_team_flag,
                    player_code = self.player_code,
                    count = self.pitch_count,
                    pitches = self.pitches,
                    play = self.play)


    def __handle_runner_adjustment(self):
        """ Runner Adjustment Event"""
        logger.info("Adjusting Runner!  Player=%s to Base=%s", self.player_code, self.adjusted_base)
        self.game_play_model = self.game.new_runner_adjustment(
                    self.player_code,
                    self.adjusted_base)


    def execute_pipeline(self):
        """ Orchestrate the end to end ingestion process associated with this pipeline. """
        # validate pipeline first
        if len(self.processed_records) > 0:
            fail("Pipeline not designed for use of staged records!  " + \
                      f"Count={len(self.processed_records)}")

        # handle substitutions
        if self.sub_player_tobe is not None and len(self.sub_player_tobe) > 0:
            self.__handle_sub()

        # handle runner adjustment
        elif self.player_code is not None and self.adjusted_base is not None:
            self.__handle_runner_adjustment()

        else:
            # action play
            self.__handle_new_play()
            logger.debug("Post Play Game Status = %s",
                         self.game_play_model.game_state.get_game_status_string())
