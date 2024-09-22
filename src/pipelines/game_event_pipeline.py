""" Game Event Pipeline

Data pipeline for game events.
"""
import logging
from model.game import Game
from pipelines.base_pipeline import BasePipeline
from events.event_factory import EventFactory
from events.constants import EventCodes

logger = logging.getLogger(__name__)

class GameEventPipeline(BasePipeline):
    """ Game Event Data Pipeline """

    game : Game = None
    no_play_sub_player : str = None

    def execute_pipeline(self):
        """ Orchestrate the end to end ingestion process associated with this pipeline. """
        # Process all the game level info records first
        while len(self.staged_records) > 0:
            record = self.staged_records.pop(0)

            logger.warning("TEMP <ROW> -- %s", record)

            if record[0] == "play" and record[6] == EventCodes.NO_PLAY_SUB_COMING:
                self.no_play_sub_player = record[3]
            elif record[0] == "play":
                game_at_bat = self.game.new_at_bat(
                            inning = record[1],
                            home_team_flag = record[2] == "1",
                            player_code = record[3],
                            count = record[4],
                            pitches = record[5],
                            game_event = record[6])

                # Process batter event
                self.extract_batter_events(self.game.game_id, game_at_bat.game_event, game_at_bat)
                event = EventFactory.create(game_at_bat)
            elif record[0] == "sub":
                self.game.new_substitution(player_to=self.no_play_sub_player,
                                    player_from=record[1],
                                    home_team_flag=record[3] == "1",
                                    batting_order=record[4],
                                    fielding_position=record[5])
                # ignoring player name row[2]
                self.no_play_sub_player = None
            elif record[0] == "com":
                logger.debug("Comment: %s", record[1])
            else:
                logger.error("Unknown Row Type!  %s", record[0])
            
            self.processed_records.append(record)


    def extract_batter_events(self, game_id, batter_events, game_at_bat):
        """ Extract the batter event strings and apply onto the game at bat.
        
            game_id - game id
            batter_events - batter events
            atbat - at bat record
        """
        logger.debug("Extracting Batter Events!  ID=%s, Events=%s",
                        game_id, batter_events)

        # split batter events into chunks
        dot_index = batter_events.find(".")
        basic_play_w_mods = batter_events
        advance = None
        if dot_index != -1 and dot_index < len(batter_events):
            advance = batter_events[(dot_index+1):]
            basic_play_w_mods = batter_events[0:dot_index]
        l = basic_play_w_mods.split("/")
        basic_play = l.pop(0)
        modifiers = l

        # apply onto game at bat object
        game_at_bat.basic_play = basic_play
        game_at_bat.modifiers = modifiers
        game_at_bat.advance = advance
