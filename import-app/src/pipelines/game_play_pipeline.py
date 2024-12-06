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
from utils.data import fail

logger = logging.getLogger(__name__)

class GamePlayPipeline(BasePipeline):
    """ Game Play Data Pipeline """

    game : Game = None
    events : List[GamePlayEventPipeline] = []
    inning : int = 0
    home_team_flag : bool = None

    # pylint: disable=too-many-statements
    def __setup_child_pipelines(self):
        # Process all the game level info records first
        while len(self.staged_records) > 0:
            record = self.staged_records.pop(0)

            if record[0] == "play" and record[6] == EventCodes.NO_PLAY_SUB_COMING:
                self.game.no_play_sub_player = record[3]
                logger.debug("No Play - player preparing for substitution: %s", record[3])

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
                logger.info("Player Substitution. From=%s, To=%s, HomeTeamFlag=%s",
                             record[1],
                             event.sub_player_tobe,
                             event.players_team_home_flag)
                self.game.no_play_sub_player = None

            elif record[0] == "com":
                logger.warning("Comment: %s", record[1])

            elif record[0] == "radj":
                # start specified runner on speciifed base
                runner_id = record[1]
                base = record[2]
                logger.debug("Runner adjustment - Runner=%s Base=%s", runner_id, base)

                event = GamePlayEventPipeline()
                event.game = self.game
                event.record = record
                event.player_code = runner_id
                event.adjusted_base = base

                self.events.append(event)

            elif record[0] == "badj":
                # mark plate appearance where the batter bats from the side that is not expected
                batter_id = record[1]
                hand = record[2]
                logger.warning("Batter batting from an unexpected side!  Batter=%s Hand=%s",
                               batter_id, hand)

            elif record[0] == "presadj":
                # Pitcher responsibility adjustment
                pitcher_id = record[1]
                occupied_base = record[2]
                logger.warning("Pitcher Responsibility Adjustment!  Pitcher=%s Occupied_Base=%s",
                               pitcher_id, occupied_base)
                # TODO Investigate whether the charged runs impacts only stats or the game itself

            elif record[0] == "padj":
                # pitcher pitches to a batter with the hand opposite the one in the roster file
                pitcher_id = record[1]
                hand = record[2]
                logger.warning("Pitcher pitching from unexpected hand!  Pitcher=%s Hand=%s",
                               pitcher_id, hand)

            elif record[0] == "ladj":
                # indicates that the next batter is the one listed in the 4th spot in the order for
                # the visiting team although some other player was expected to bat next based on
                # the current lineup.
                batting_team = record[1]
                batting_order_position = record[2]
                logger.warning("Lineup Adjustment!  Team=%s Position=%s",
                               batting_team, batting_order_position)
                # TODO This needs to be handled to identify players accurately
                #fail(f"Unhandled game record event LADJ - BT={batting_team} " + \
                #     f"BOP={batting_order_position}")

            else:
                fail(f"Unknown Game Event Row Type! {record[0]}")

    def execute_pipeline(self):
        """ Orchestrate the end to end ingestion process associated with this pipeline. """
        self.__setup_child_pipelines()

        prev_game_state = None
        for event in self.events:
            details = ""
            if prev_game_state is not None:
                details = prev_game_state.get_game_status_string()
            logger.info(">>> Pre-Play Details.  %s  %s", event.record, details)

            event.execute_pipeline()
            self.processed_records.append(event.record)

            # build game tracking strings
            prev_game_state = event.game_play_model.game_state
            game_status = prev_game_state.get_game_status_string()
            logger.info("<<<  Post Play Details.  %s", game_status)
            prev_game_state = event.game_play_model.game_state
