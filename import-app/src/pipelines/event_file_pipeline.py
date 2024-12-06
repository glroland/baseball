""" Event File Pipeline

Data pipeline for event files.
"""
import logging
from typing import List
import psycopg
from pipelines.base_pipeline import BasePipeline
from pipelines.game_pipeline import GamePipeline
from utils.db import connect_to_db_with_conn_str
from utils.data import fail
from games_to_skip import GAMES_TO_SKIP

logger = logging.getLogger(__name__)

class EventFilePipeline(BasePipeline):
    """ Event File Data Pipeline """

    filename : str = None
    game_pipelines : List[GamePipeline] = []
    inflight : GamePipeline = None

    def optionally_redelegate_record(self, record : List[str]):
        """ If implemented by a subclass, this is its opportunity to re-delegate the record
            to another pipeline. 
            
            record - row to delegate, optionally
        """
        if record[0] == "id":
            self.inflight = None
            if record[1] in GAMES_TO_SKIP:
                logger.warning("Skipping Game!  Game_ID=%s", record[1])
            else:
                # Creating new Game Pipeline
                self.inflight = GamePipeline()
                self.inflight.set_game_id(record[1])
                self.game_pipelines.append(self.inflight)
                logger.debug("New Game Record in Data File.  Index # %s", len(self.game_pipelines))

        elif record[0] == "version":
            # ignore game version info
            # pylint: disable=unnecessary-pass
            pass
        else:
            # validate that a game is inflight to delegate to
            if self.inflight is not None:
                # delegate the event
                logger.debug("Redelegating record to game: %s", record)
                self.inflight.stage_record(record)
                return True

        return False

    def execute_pipeline(self):
        """ Orchestrate the end to end ingestion process associated with this pipeline. """
        logger.debug("Processing Event File Data Pipeline.  File: %s", self.filename)
        for game_pipeline in self.game_pipelines:
            # Find where the row is in the row index
            r = None
            for r in self.staged_records:
                if r[1] == game_pipeline.game.game_id:
                    break

            # Ensure that it was found
            if r is None:
                fail(f"Could not find record for game id: {game_pipeline.game.game_id}")

            # Execute Pipeline
            logger.debug("Executing Pipeline = %s", game_pipeline)
            logger.info("Starting New Game!  %s", game_pipeline.game.game_id)
            game_pipeline.execute_pipeline()
            logger.debug("Pipeline Executed")

            # Move Record from staged to processed
            self.processed_records.append(r)
            self.staged_records.remove(r)

        self.processing_complete()
        logger.info("Data Pipeline Successfully Processed: %s", type(self))


    def processing_complete(self):
        """ Formally acknowledges that the feed is loaded """
        # Validate that game pipeline is in flight
        if self.inflight is not None:
            self.inflight.processing_complete()
            self.inflight = None


    def save(self, db_conn_str):
        """ Save all the encompassing game records to the database.
        
            db_conn_str - database connection string
        """
        logger.info("Saving Games.  List is %s games long.", len(self.game_pipelines))

        # Validate parameters
        if db_conn_str is None:
            fail("Save failed due to invalid DB Connection String!  (none)")

        # Save all the game pipeline records
        sql_connection = connect_to_db_with_conn_str(db_conn_str)
        try:
            for game_pipeline in self.game_pipelines:
                game_pipeline.save(sql_connection)
        except psycopg.Error as e:
            sql_connection.rollback()
            logger.error("Unable to save games due to SQL error (%s)", e)
            raise e
        sql_connection.commit()
