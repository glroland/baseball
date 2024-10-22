""" Game Pipeline

Data pipeline for games.
"""
import logging
from typing import List
from pipelines.base_pipeline import BasePipeline
from pipelines.game_play_pipeline import GamePlayPipeline
from model.game import Game
from model.starter import Starter
from model.data import Data
from utils.data import fail
from ingest.save_event_data import save_game

logger = logging.getLogger(__name__)

class GamePipeline(BasePipeline):
    """ Game Data Pipeline """

    game : Game = None
    game_events_pipelines : List[GamePlayPipeline] = []

    def set_game_id(self, game_id):
        """ Set the game id
        
            game_id - game id
        """
        self.game = Game()
        self.game.game_id = game_id

    # pylint: disable=inconsistent-return-statements
    def optionally_redelegate_record(self, record : List[str]):
        """ If implemented by a subclass, this is its opportunity to re-delegate the record
            to another pipeline. 
            
            record - row to delegate, optionally
        """
        # handle known record types
        if record[0] in [ "info", "start", "data" ]:
            return False
        if record[0] in [ "play", "sub", "com", "radj", "badj", "presadj", "padj", "padj", "ladj" ]:
            game_event_pipeline = GamePlayPipeline()
            game_event_pipeline.game = self.game
            game_event_pipeline.stage_record(record)
            self.game_events_pipelines.append(game_event_pipeline)
            return True

        # fail on unexpected record types
        fail(f"Unknown Game Row Type!  {record[0]}")


    def execute_pipeline(self):
        """ Orchestrate the end to end ingestion process associated with this pipeline. """
        # Process all the game level info records first
        while len(self.staged_records) > 0:
            record = self.staged_records.pop(0)

            if record[0] == "info":
                self.game.info_attributes[record[1]] = record[2]
            elif record[0] == "start":
                starter = Starter()
                starter.player_code = record[1]
                starter.player_name = record[2]
                starter.home_team_flag = record[3] == "1"
                starter.batting_order = int(record[4])
                starter.fielding_position = int(record[5])
                self.game.starters.append(starter)
            elif record[0] == "data":
                data = Data()
                data.data_type = record[1]
                data.pitcher_player_code = record[2]
                data.quantity = int(record[3])
                self.game.data.append(data)
            else:
                fail(f"Unknown Row Type!  {record[0]}")

            self.processed_records.append(record)

        # Process all the game events, in order
        logger.info("New Game (%s)> Processing Events Pipeline.  Size=%s",
                    self.game.game_id, len(self.game_events_pipelines))
        for game_events_pipeline in self.game_events_pipelines:
            game_events_pipeline.execute_pipeline()

    def save(self, sql_connection):
        """ Save this game record to the database 
        
            sql_connection - sql connection to use for tx
        """
        logger.info("Saving Game #%s", self.game.game_id)
        save_game(sql_connection, self.game)
        logger.debug("Game saved!  %s", self.game.game_id)

    def processing_complete(self):
        """ Formally acknowledges that the feed is loaded """
        # Validate prior game
        if self.game is not None:
            logging.debug("Game processing complete!")
            self.game.on_game_end()
