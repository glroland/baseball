""" Game Play Pipeline

Data pipeline for game plays.
"""
import logging
from typing import List
from pipelines.base_pipeline import BasePipeline
from pipelines.game_play_event_pipeline import GamePlayEventPipeline
from model.game import Game
from model.play_record import PlayRecord
from events.constants import EventCodes

logger = logging.getLogger(__name__)

class GamePlayPipeline(BasePipeline):
    """ Game Play Data Pipeline """

    game : Game = None
    events : List[GamePlayEventPipeline] = []
    inning : int = 0
    home_team_flag : bool = None

    def __setup_child_pipelines(self):
        # Process all the game level info records first
        while len(self.staged_records) > 0:
            record = self.staged_records.pop(0)

            if record[0] == "play" and record[6] == EventCodes.NO_PLAY_SUB_COMING:
                self.game.no_play_sub_player = record[3]
                logger.info("No Play - player preparing for substitution: %s", record[3])

            elif record[0] == "play":
                # parse action record
                play = PlayRecord.create(record[6])

                # create game play event record
                event = GamePlayEventPipeline()
                event.game = self.game
                event.record = record
                event.inning = int(record[1])
                self.inning = event.inning
                event.home_team_flag = record[2] == "1"
                self.home_team_flag = event.home_team_flag
                event.player_code = record[3]
                event.pitch_count = record[4]
                event.pitches = record[5]
                event.play = play
                self.events.append(event)

            elif record[0] == "sub":
                event = GamePlayEventPipeline()
                event.game = self.game
                event.record = record
                event.sub_player_tobe = self.game.no_play_sub_player
                event.player_code = record[1]
                event.batting_order = record[4]
                event.fielding_position = record[5]
                event.players_team_home_flag = record[3] == "1"
                self.events.append(event)
                logger.debug("Player Substitution. From=%s, To=%s, HomeTeamFlag=%s",
                             record[1],
                             event.sub_player_tobe,
                             event.players_team_home_flag)
                self.game.no_play_sub_player = None

            elif record[0] == "com":
                logger.info("Comment: %s", record[1])

            elif record[0] == "radj":
                # TODO
                self.fail(f"Unhandled game record event - {record[0]}")

            elif record[0] == "badj":
                # TODO
                self.fail(f"Unhandled game record event - {record[0]}")

            elif record[0] == "presadj":
                # TODO
                self.fail(f"Unhandled game record event - {record[0]}")

            elif record[0] == "padj":
                # TODO
                self.fail(f"Unhandled game record event - {record[0]}")

            elif record[0] == "ladj":
                # TODO
                self.fail(f"Unhandled game record event - {record[0]}")

            else:
                self.fail(f"Unknown Game Event Row Type! {record[0]}")

    def execute_pipeline(self):
        """ Orchestrate the end to end ingestion process associated with this pipeline. """
        self.__setup_child_pipelines()

        for event in self.events:
            logger.error("---- PLAY   %s", event.record)

            event.execute_pipeline()
            self.processed_records.append(event.record)

            # build game tracking strings
            game_status = event.game_play_model.game_state.get_game_status_string()
            logger.error(">>>> POST PLAY DETAILS.  %s",
                        game_status)
