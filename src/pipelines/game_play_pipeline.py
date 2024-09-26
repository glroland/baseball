""" Game Play Pipeline

Data pipeline for game plays.
"""
import logging
import re
from typing import List, Dict
from model.game import Game
from pipelines.base_pipeline import BasePipeline
from pipelines.game_play_event_pipeline import GamePlayEventPipeline
from events.constants import EventCodes
from utils.data import extract_groups
from model.play_record import PlayRecord

logger = logging.getLogger(__name__)

class GamePlayPipeline(BasePipeline):
    """ Game Play Data Pipeline """

    game : Game = None
    no_play_sub_player : str = None
    events : List[GamePlayEventPipeline] = []
    uncertainty_flag : bool = False
    exceptional_play_flag : bool = False


    def __split_action_string(self, event):
        # trim uncertainty flag
        action_str = event.full_play_action
        if action_str[len(action_str)-1] == "#":
            self.uncertainty_flag = True
            action_str = action_str[0:len(action_str)-1]
            logger.warning("Uncertainty Flag set for play!  {self.event.full_play_action}")

        # manage exceptional plays
        if action_str.find("!") != -1:
            self.exceptional_play_flag = True
            action_str = action_str.replace("!", "")

        # splt advancements
        beginning = self.__split_advancements(event, action_str)
        logging.fatal("Beginning - %s", beginning)
        groups = extract_groups(beginning)
        tokens = groups[0].split("/")
        event.play = tokens.pop(0)
        logging.fatal("Play - %s", beginning)
        event.modifiers = tokens
        logging.fatal("Modifiers - %s", beginning)

        # break out plays (usually just 1 but that's a big usually)
        play = event.play
        while True:
            end_parens = play.find(")")
            if end_parens == -1:
                event.stage_record([play])
                break
            elif end_parens == len(play)-1:
                groups = extract_groups(play)
                first_part = play[0:play.find("(")]
                event.stage_record([first_part] + groups)
                break
            else:
                record = play[0:end_parens+1]
                play = play[end_parens+1:]
                groups = extract_groups(record)
                first_part = record[0:record.find("(")]
                event.stage_record([first_part] + groups)

    def __setup_child_pipelines(self):
        # Process all the game level info records first
        while len(self.staged_records) > 0:
            record = self.staged_records.pop(0)


            if len(record)> 6:
                play = PlayRecord.create(record[6])
                logger.fatal("PlayRecord - %s", str(play.__dict__))
            return


            logger.fatal("TEMP <ROW> -- %s", record)
            if record[0] == "play" and record[6] == EventCodes.NO_PLAY_SUB_COMING:
                self.no_play_sub_player = record[3]
            elif record[0] == "play":
                # create game play event record
                event = GamePlayEventPipeline()
                event.game = self.game
                event.record = record
                event.inning = int(record[1])
                event.home_team_flag = record[2] == "1"
                event.player_code = record[3]
                event.pitch_count = record[4]
                event.pitches = record[5]
                event.full_play_action = record[6]
                self.events.append(event)

                self.__split_action_string(event)

            elif record[0] == "sub":
                event = GamePlayEventPipeline()
                event.game = self.game
                event.record = record
                event.sub_player_tobe = self.no_play_sub_player
                event.player_code = record[1]
                event.batting_order = record[4]
                event.fielding_position = record[5]
                event.players_team_home_flag = record[3] == "1"
                self.events.append(event)
                self.no_play_sub_player = None
            elif record[0] == "com":
                logger.info("Comment: %s", record[1])
            elif record[0] == "radj":
                logger.fatal ("UNHANDLED radj")
                # TODO
            elif record[0] == "badj":
                logger.fatal ("UNHANDLED badj")
                # TODO
            elif record[0] == "presadj":
                logger.fatal ("UNHANDLED presadj")
                # TODO
            elif record[0] == "padj":
                logger.fatal ("UNHANDLED padj")
                # TODO
            elif record[0] == "ladj":
                logger.fatal ("UNHANDLED ladj")
                # TODO
            else:
                self.fail(f"Unknown Game Event Row Type! {record[0]}")

    def execute_pipeline(self):
        """ Orchestrate the end to end ingestion process associated with this pipeline. """
        self.__setup_child_pipelines()

        for event in self.events:
            event.execute_pipeline()
            self.processed_records.append(event.record)
