""" Game Play Event Pipeline

Data pipeline for events associated with a game play.
"""
from typing import List
import logging
from pipelines.base_pipeline import BasePipeline
from events.event_factory import EventFactory
from model.game import Game
from model.play_record import PlayRecord

logger = logging.getLogger(__name__)

class GamePlayEventPipeline(BasePipeline):
    """ Game Play Event Data Pipeline """

    game : Game = None

    record : List[str] = None
    inning : int = 0
    home_team_flag : bool = False

    player_code : str = None
    pitch_count : str = None
    pitches : str = None
    play : PlayRecord = None

    sub_player_tobe : str = None
    batting_order : int = None
    fielding_position : int = None
    players_team_home_flag : bool = None

    def __handle_sub(self):
        logger.info("Handling substituion...")
        self.game.new_substitution(player_to=self.no_play_sub_player,
                            player_from=self.player_code,
                            home_team_flag=self.players_team_home_flag,
                            batting_order=self.batting_order,
                            fielding_position=self.fielding_position)


    def execute_pipeline(self):
        """ Orchestrate the end to end ingestion process associated with this pipeline. """
        # handle substitutions
        if self.sub_player_tobe is not None and len(self.sub_player_tobe) > 0:
            self.__handle_sub()

        else:
            # Process all the game level info records first
            is_first = True
            m = self.modifiers
            a = self.advancements
            while len(self.staged_records) > 0:
                record = self.staged_records.pop(0)
                logger.fatal("Record -- %s", record)

                game_at_bat = self.game.new_at_bat(
                            inning = self.inning,
                            home_team_flag = self.home_team_flag == "1",
                            player_code = self.player_code,
                            count = self.pitch_count,
                            pitches = self.pitches,
                            basic_play = record,
                            modifiers = m,
                            advances = a)
                if is_first:
                      m = []
                      a = []
                      is_first = False

                EventFactory.create(game_at_bat)

                self.processed_records.append(record)
