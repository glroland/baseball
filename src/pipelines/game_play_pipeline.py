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

logger = logging.getLogger(__name__)

class GamePlayPipeline(BasePipeline):
    """ Game Play Data Pipeline """

    game : Game = None
    no_play_sub_player : str = None
    events : List[GamePlayEventPipeline] = []
    uncertainty_flag : bool = False
    exceptional_play_flag : bool = False

    def __split_advancements(self, event, action_str):
        # splt advancements
        if action_str.count(".") > 1:
            self.fail("Unexpected - too Many dots encountered with advancement!  " + \
                        f"{action_str.count('.')} Action={event.full_play_action}")
        advancements = action_str.split(".")
        if action_str.count(".") != (len(advancements) - 1):
            self.fail("Split Operation for advancements failed due to count mispatch.")
        beginning = advancements[0]
        advancements = advancements[1:]
        if len(advancements) > 0:
            event.advancements = advancements[0].split(";")

            # validate advancements
            for a in event.advancements:
                if not re.match("^[B123][X-][123H](\\(.+\\))*$", a):
                    self.fail(f"Invalid Advancement: {a}")

                # extract advancement parameters
                advancement_parameters = extract_groups(a)
                if len(advancement_parameters) > 0:
                    for group in advancement_parameters:
                        # all numbers test
                        if re.match("^[0-9]+$", group):
                            logger.debug("Advancement Parameter - all numbers - %s", group)
                        elif re.match("^[0-9]+X$", group):
                            logger.debug("Advancement Parameter - number X - %s", group)
                        elif re.match("^[0-9]+H$", group):
                            logger.debug("Advancement Parameter - number H - %s", group)
                        elif re.match("^[0-9]+/TH[123H]?$", group):
                            logger.debug("Advancement Parameter - numbers plus throw - %s", group)
                        elif re.match("^[0-9]+/BINT$", group):
                            logger.debug("Advancement Parameter - numbers plus BINT - %s", group)
                        elif re.match("^[0-9]+/RINT$", group):
                            logger.debug("Advancement Parameter - numbers plus RINT - %s", group)
                        elif re.match("^[0-9]+/AP$", group):
                            logger.debug("Advancement Parameter - numbers plus AP - %s", group)
                        elif re.match("^[0-9]*E[0-9]/TH[123H]?$", group):
                            logger.debug("Advancement Parameter - error due to throw - %s", group)
                        elif re.match("^[0-9]*E[0-9]/OBS?$", group):
                            logger.debug("Advancement Parameter - error due to OBS - %s", group)
                        elif re.match("^[0-9]*E[0-9]$", group):
                            logger.debug("Advancement Parameter - error - %s", group)
                        elif group == "ER":
                            logger.debug("Advancement Parameter - Earned Run")
                        elif group == "UR":
                            logger.debug("Advancement Parameter - Unearned Run")
                        elif group == "TUR":
                            logger.debug("Advancement Parameter - Team Unearned Run")
                        elif group == "NR":
                            logger.debug("Advancement Parameter - RBI Not Credited")
                        elif group == "PB":
                            logger.debug("Advancement Parameter - Passed Ball")
                        elif group == "RBI":
                            logger.debug("Advancement Parameter - RBI")
                        elif group == "WP":
                            logger.debug("Advancement Parameter - WP")
                        elif re.match("^TH[123H]?$", group):
                            logger.debug("Advancement Parameter - Throw")
                        else:
                            self.fail(f"Illegal Advancement Parameter - {group}")
        
        return beginning


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

        # extract the modifiers
        slash_pos = beginning.find("/")
        if slash_pos == -1:
            event.play = beginning
        else:
            event.play = beginning[0:slash_pos]
            modifiers = beginning[slash_pos+1:]
            event.modifiers = modifiers.split("/")

        logger.fatal("Play = %s", event.play)

        # break out plays (usually just 1 but that's a big usually)
        play = event.play
        while True:
            end_parens = play.find(")")
            if end_parens == -1:
                event.stage_record([play])
                logger.fatal("1 %s", event.staged_records)
                break
            elif end_parens == len(play)-1:
                groups = extract_groups(play)
                first_part = play[0:play.find("(")]
                event.stage_record([first_part] + groups)
                logger.fatal("2 %s", event.staged_records)
                break
            else:
                record = play[0:end_parens+1]
                play = play[end_parens+1:]
                groups = extract_groups(record)
                first_part = record[0:record.find("(")]
                logger.fatal("3A %s", first_part)
                logger.fatal("3B %s", groups)
                event.stage_record([first_part] + groups)
                logger.fatal("3 %s", event.staged_records)


    def __setup_child_pipelines(self):
        # Process all the game level info records first
        while len(self.staged_records) > 0:
            record = self.staged_records.pop(0)

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
