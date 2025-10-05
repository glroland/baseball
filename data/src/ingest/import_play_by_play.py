""" CLI for importing retrosheet's play by play processed event files. """
import logging
import os
import sys
import csv
import click
import psycopg
from typing import List
from datetime import datetime
from ingest_types import PlayByPlay, Game

logger = logging.getLogger(__name__)

NUM_COLUMNS = 161
MAX_GAMES = -1
GAME_SAVE_INTERVAL = 1000

class ErrorCodes:
    SUCCESS = 0
    GENERIC_ERROR = 1
    FILE_NOT_FOUND = 2
    MISSING_FILE = 3
    INVALID_DATA = 4


class ColorOutputFormatter(logging.Formatter):
    """ Add colors to stdout logging output to simplify text.  Thank you to:
        https://stackoverflow.com/questions/384076/how-can-i-color-python-logging-output
    """

    grey = "\x1b[38;20m"
    yellow = "\x1b[33;20m"
    red = "\x1b[31;20m"
    bold_red = "\x1b[31;1m"
    reset = "\x1b[0m"
    format_str = '%(name)-13s: %(message)s'

    FORMATS = {
        logging.DEBUG: grey + format_str + reset,
        logging.INFO: grey + format_str + reset,
        logging.WARNING: yellow + format_str + reset,
        logging.ERROR: red + format_str + reset,
        logging.CRITICAL: bold_red + format_str + reset
    }

    def format(self, record):
        log_fmt = self.FORMATS.get(record.levelno)
        formatter = logging.Formatter(log_fmt)
        return formatter.format(record)


def get_char_value(column: str):
    """ Imports a character value from a string column.
        Gets that character by pulling the first character.

        column - string value for column
    """
    if column is None or len(column.strip()) == 0:
        return None
    return column[0]

def get_str_value(column: str):
    """ Imports a string value.
    
        column - string value for column
    """
    if column is None or len(column.strip()) == 0 or column == "(unknown)":
        return None
    return column

def get_date_value(column: str):
    """ Imports a string value.
    
        column - string value for column
    """
    if column is None or len(column.strip()) == 0:
        return None
    format_string = "%Y%m%d"
    datetime_object = datetime.strptime(column, format_string)
    date = datetime_object.date()
    return date

def get_int_value(column: str):
    """ Imports an integer value.
    
        column - string value for column
    """
    if column is None or len(column.strip()) == 0:
        return None
    return int(column)

def get_bool_value(column: str):
    """ Imports a boolean value.
    
        column - string value for column
    """
    if column is None or len(column.strip()) == 0:
        return None
    if column == "1":
        return True
    if column == "0":
        return False
    raise ValueError(f"Column Value is not suitable for a boolean:  Val={column}")


def convert_line(line: List[str]):
    """ Converts a single line into a strongly typed play by play.
    
        line - one play by play entry
    """
    col_index = 0

    play_by_play = PlayByPlay()

    play_by_play.retrosheet_id = get_str_value(line[col_index])
    col_index += 1
    play_by_play.original_event_str = get_str_value(line[col_index])
    col_index += 1
    play_by_play.inning = get_int_value(line[col_index])
    col_index += 1
    play_by_play.is_top_of_inning = line[col_index] == "0"
    col_index += 1
    play_by_play.is_home_team = get_bool_value(line[col_index])
    col_index += 1
    play_by_play.game_location = get_str_value(line[col_index])
    col_index += 1
    play_by_play.batting_team = get_str_value(line[col_index])
    col_index += 1
    play_by_play.pitching_team = get_str_value(line[col_index])
    col_index += 1
    play_by_play.batter = get_str_value(line[col_index])
    col_index += 1
    play_by_play.pitcher = get_str_value(line[col_index])
    col_index += 1
    play_by_play.batter_lineup_pos = get_int_value(line[col_index])
    col_index += 1
    play_by_play.batter_fielding_pos = get_int_value(line[col_index])
    col_index += 1
    play_by_play.batting_hand = get_str_value(line[col_index])
    col_index += 1
    play_by_play.pitching_hand = get_str_value(line[col_index])
    col_index += 1
    pitch_count_str = get_str_value(line[col_index])
    col_index += 1
    if pitch_count_str is not None and pitch_count_str != "??" and pitch_count_str != "00.":
        play_by_play.pitch_count = get_int_value(pitch_count_str)
    play_by_play.pitch_sequence = get_str_value(line[col_index])
    col_index += 1
    num_pitches_str = line[col_index]
    col_index += 1
    if num_pitches_str is not None and len(num_pitches_str.strip()) > 0:
        play_by_play.num_pitches = get_int_value(num_pitches_str)
    play_by_play.plate_appearance_flag = get_bool_value(line[col_index])
    col_index += 1
    play_by_play.is_at_bat = get_bool_value(line[col_index])
    col_index += 1
    play_by_play.is_single = get_bool_value(line[col_index])
    col_index += 1
    play_by_play.is_double = get_bool_value(line[col_index])
    col_index += 1
    play_by_play.is_triple = get_bool_value(line[col_index])
    col_index += 1
    play_by_play.is_home_run = get_bool_value(line[col_index])
    col_index += 1
    play_by_play.is_sacrifice_bunt = get_bool_value(line[col_index])
    col_index += 1
    play_by_play.is_sacrifice_fly = get_bool_value(line[col_index])
    col_index += 1
    play_by_play.is_hit_by_pitch = get_bool_value(line[col_index])
    col_index += 1
    play_by_play.is_walk = get_bool_value(line[col_index])
    col_index += 1
    play_by_play.is_intentional_walk = get_bool_value(line[col_index])
    col_index += 1
    play_by_play.is_strikeout = get_bool_value(line[col_index])
    col_index += 1
    play_by_play.is_catchers_interference = get_bool_value(line[col_index])
    col_index += 1
    play_by_play.is_other_play_appearance = get_bool_value(line[col_index])
    col_index += 1
    play_by_play.is_other_out = get_bool_value(line[col_index])
    col_index += 1
    play_by_play.is_other_no_out = get_bool_value(line[col_index])
    col_index += 1
    play_by_play.is_ball_in_play = get_bool_value(line[col_index])
    col_index += 1
    play_by_play.is_bunt = get_bool_value(line[col_index])
    col_index += 1
    play_by_play.is_ground_ball = get_bool_value(line[col_index])
    col_index += 1
    play_by_play.is_fly_ball = get_bool_value(line[col_index])
    col_index += 1
    play_by_play.is_line_drive = get_bool_value(line[col_index])
    col_index += 1
    play_by_play.is_double_play_grounded = get_bool_value(line[col_index])
    col_index += 1
    play_by_play.is_double_play_other = get_bool_value(line[col_index])
    col_index += 1
    play_by_play.is_triple_play = get_bool_value(line[col_index])
    col_index += 1
    play_by_play.is_wild_pitch = get_bool_value(line[col_index])
    col_index += 1
    play_by_play.is_passed_ball = get_bool_value(line[col_index])
    col_index += 1
    play_by_play.is_balk = get_bool_value(line[col_index])
    col_index += 1
    play_by_play.is_other_advance = get_bool_value(line[col_index])
    col_index += 1
    play_by_play.is_defensive_indifference = get_bool_value(line[col_index])
    col_index += 1
    play_by_play.is_stole_2 = get_bool_value(line[col_index])
    col_index += 1
    play_by_play.is_stole_3 = get_bool_value(line[col_index])
    col_index += 1
    play_by_play.is_stole_home = get_bool_value(line[col_index])
    col_index += 1
    play_by_play.is_caught_steeling_2 = get_bool_value(line[col_index])
    col_index += 1
    play_by_play.is_caught_steeling_3 = get_bool_value(line[col_index])
    col_index += 1
    play_by_play.is_caught_steeling_home = get_bool_value(line[col_index])
    col_index += 1
    play_by_play.is_pickoff_at_1 = get_bool_value(line[col_index])
    col_index += 1
    play_by_play.is_pickoff_at_2 = get_bool_value(line[col_index])
    col_index += 1
    play_by_play.is_pickoff_at_3 = get_bool_value(line[col_index])
    col_index += 1
    play_by_play.is_strikeout_but_safe = get_bool_value(line[col_index])
    col_index += 1
    play_by_play.errors_1 = get_int_value(line[col_index])
    col_index += 1
    play_by_play.errors_2 = get_int_value(line[col_index])
    col_index += 1
    play_by_play.errors_3 = get_int_value(line[col_index])
    col_index += 1
    play_by_play.errors_4 = get_int_value(line[col_index])
    col_index += 1
    play_by_play.errors_5 = get_int_value(line[col_index])
    col_index += 1
    play_by_play.errors_6 = get_int_value(line[col_index])
    col_index += 1
    play_by_play.errors_7 = get_int_value(line[col_index])
    col_index += 1
    play_by_play.errors_8 = get_int_value(line[col_index])
    col_index += 1
    play_by_play.errors_9 = get_int_value(line[col_index])
    col_index += 1
    play_by_play.outs_pre = get_int_value(line[col_index])
    col_index += 1
    play_by_play.outs_post = get_int_value(line[col_index])
    col_index += 1
    play_by_play.base_runner_1_pre = get_str_value(line[col_index])
    col_index += 1
    play_by_play.base_runner_2_pre = get_str_value(line[col_index])
    col_index += 1
    play_by_play.base_runner_3_pre = get_str_value(line[col_index])
    col_index += 1
    play_by_play.base_runner_1_post = get_str_value(line[col_index])
    col_index += 1
    play_by_play.base_runner_2_post = get_str_value(line[col_index])
    col_index += 1
    play_by_play.base_runner_3_post = get_str_value(line[col_index])
    col_index += 1
    play_by_play.scorer_from_bat = get_str_value(line[col_index])
    col_index += 1
    play_by_play.scorer_from_1 = get_str_value(line[col_index])
    col_index += 1
    play_by_play.scorer_from_2 = get_str_value(line[col_index])
    col_index += 1
    play_by_play.scorer_from_3 = get_str_value(line[col_index])
    col_index += 1
    play_by_play.pitcher_charged_run_batter = get_str_value(line[col_index])
    col_index += 1
    play_by_play.pitcher_charged_run_1 = get_str_value(line[col_index])
    col_index += 1
    play_by_play.pitcher_charged_run_2 = get_str_value(line[col_index])
    col_index += 1
    play_by_play.pitcher_charged_run_3 = get_str_value(line[col_index])
    col_index += 1
    play_by_play.unearned_run_by_batter = get_str_value(line[col_index])
    col_index += 1
    play_by_play.unearned_run_by_1 = get_str_value(line[col_index])
    col_index += 1
    play_by_play.unearned_run_by_2 = get_str_value(line[col_index])
    col_index += 1
    play_by_play.unearned_run_by_3 = get_str_value(line[col_index])
    col_index += 1
    play_by_play.rbi_batter = get_str_value(line[col_index])
    col_index += 1
    play_by_play.rbi_1 = get_str_value(line[col_index])
    col_index += 1
    play_by_play.rbi_2 = get_str_value(line[col_index])
    col_index += 1
    play_by_play.rbi_3 = get_str_value(line[col_index])
    col_index += 1
    play_by_play.num_runs_scored = get_int_value(line[col_index])
    col_index += 1
    play_by_play.num_rbi_credited = get_int_value(line[col_index])
    col_index += 1
    play_by_play.num_earned_runs = get_int_value(line[col_index])
    col_index += 1
    play_by_play.num_team_unearned_runs = get_int_value(line[col_index])
    col_index += 1
    play_by_play.batting_team_lineup_1 = get_str_value(line[col_index])
    col_index += 1
    play_by_play.batting_team_lineup_2 = get_str_value(line[col_index])
    col_index += 1
    play_by_play.batting_team_lineup_3 = get_str_value(line[col_index])
    col_index += 1
    play_by_play.batting_team_lineup_4 = get_str_value(line[col_index])
    col_index += 1
    play_by_play.batting_team_lineup_5 = get_str_value(line[col_index])
    col_index += 1
    play_by_play.batting_team_lineup_6 = get_str_value(line[col_index])
    col_index += 1
    play_by_play.batting_team_lineup_7 = get_str_value(line[col_index])
    col_index += 1
    play_by_play.batting_team_lineup_8 = get_str_value(line[col_index])
    col_index += 1
    play_by_play.batting_team_lineup_9 = get_str_value(line[col_index])
    col_index += 1
    play_by_play.batting_team_field_pos_for_lineup_1 = get_str_value(line[col_index])
    col_index += 1
    play_by_play.batting_team_field_pos_for_lineup_2 = get_str_value(line[col_index])
    col_index += 1
    play_by_play.batting_team_field_pos_for_lineup_3 = get_str_value(line[col_index])
    col_index += 1
    play_by_play.batting_team_field_pos_for_lineup_4 = get_str_value(line[col_index])
    col_index += 1
    play_by_play.batting_team_field_pos_for_lineup_5 = get_str_value(line[col_index])
    col_index += 1
    play_by_play.batting_team_field_pos_for_lineup_6 = get_str_value(line[col_index])
    col_index += 1
    play_by_play.batting_team_field_pos_for_lineup_7 = get_str_value(line[col_index])
    col_index += 1
    play_by_play.batting_team_field_pos_for_lineup_8 = get_str_value(line[col_index])
    col_index += 1
    play_by_play.batting_team_field_pos_for_lineup_9 = get_str_value(line[col_index])
    col_index += 1
    play_by_play.catcher = get_str_value(line[col_index])
    col_index += 1
    play_by_play.first_baseman = get_str_value(line[col_index])
    col_index += 1
    play_by_play.second_baseman = get_str_value(line[col_index])
    col_index += 1
    play_by_play.third_baseman = get_str_value(line[col_index])
    col_index += 1
    play_by_play.shortstop = get_str_value(line[col_index])
    col_index += 1
    play_by_play.left_fielder = get_str_value(line[col_index])
    col_index += 1
    play_by_play.center_fielder = get_str_value(line[col_index])
    col_index += 1
    play_by_play.right_fielder = get_str_value(line[col_index])
    col_index += 1
    play_by_play.putouts_unidentified = get_int_value(line[col_index])
    col_index += 1
    play_by_play.putouts_by_1 = get_int_value(line[col_index])
    col_index += 1
    play_by_play.putouts_by_2 = get_int_value(line[col_index])
    col_index += 1
    play_by_play.putouts_by_3 = get_int_value(line[col_index])
    col_index += 1
    play_by_play.putouts_by_4 = get_int_value(line[col_index])
    col_index += 1
    play_by_play.putouts_by_5 = get_int_value(line[col_index])
    col_index += 1
    play_by_play.putouts_by_6 = get_int_value(line[col_index])
    col_index += 1
    play_by_play.putouts_by_7 = get_int_value(line[col_index])
    col_index += 1
    play_by_play.putouts_by_8 = get_int_value(line[col_index])
    col_index += 1
    play_by_play.putouts_by_9 = get_int_value(line[col_index])
    col_index += 1
    play_by_play.assists_by_1 = get_int_value(line[col_index])
    col_index += 1
    play_by_play.assists_by_2 = get_int_value(line[col_index])
    col_index += 1
    play_by_play.assists_by_3 = get_int_value(line[col_index])
    col_index += 1
    play_by_play.assists_by_4 = get_int_value(line[col_index])
    col_index += 1
    play_by_play.assists_by_5 = get_int_value(line[col_index])
    col_index += 1
    play_by_play.assists_by_6 = get_int_value(line[col_index])
    col_index += 1
    play_by_play.assists_by_7 = get_int_value(line[col_index])
    col_index += 1
    play_by_play.assists_by_8 = get_int_value(line[col_index])
    col_index += 1
    play_by_play.assists_by_9 = get_int_value(line[col_index])
    col_index += 1
    play_by_play.fielding_seq_for_out = get_str_value(line[col_index])
    col_index += 1
    play_by_play.batout1 = get_int_value(line[col_index])
    col_index += 1
    play_by_play.batout2 = get_int_value(line[col_index])
    col_index += 1
    play_by_play.batout3 = get_int_value(line[col_index])
    col_index += 1
    play_by_play.brout_b = get_int_value(line[col_index])
    col_index += 1
    play_by_play.brout1 = get_int_value(line[col_index])
    col_index += 1
    play_by_play.brout2 = get_int_value(line[col_index])
    col_index += 1
    play_by_play.brout3 = get_int_value(line[col_index])
    col_index += 1
    play_by_play.firstf = get_int_value(line[col_index])
    col_index += 1
    play_by_play.loc = get_str_value(line[col_index])
    col_index += 1
    play_by_play.hittype = get_char_value(line[col_index])
    col_index += 1
    play_by_play.dpopp = get_int_value(line[col_index])
    col_index += 1
    play_by_play.pivot = get_str_value(line[col_index])
    col_index += 1
    play_by_play.play_number = get_int_value(line[col_index])
    col_index += 1
    play_by_play.umpire_home = get_str_value(line[col_index])
    col_index += 1
    play_by_play.umpire_1b = get_str_value(line[col_index])
    col_index += 1
    play_by_play.umpire_2b = get_str_value(line[col_index])
    col_index += 1
    play_by_play.umpire_3b = get_str_value(line[col_index])
    col_index += 1
    play_by_play.umpire_left_field = get_str_value(line[col_index])
    col_index += 1
    play_by_play.umpire_right_field = get_str_value(line[col_index])
    col_index += 1
    play_by_play.game_date = get_date_value(line[col_index])
    col_index += 1
    play_by_play.game_type = get_char_value(line[col_index])
    col_index += 1
    play_by_play.pbp = get_char_value(line[col_index])
    col_index += 1
    
    return play_by_play


def save_game(db_cursor, game):
    """ Save the provided game base record to the database.
    
        db_cursor - sql cursor to use for the tx
        game - game record to save 
    """
    logger.debug("Saving Game!  ID=%s", game.retrosheet_id)

    # calculate game score
    score_visitor = 0
    score_home = 0
    last_play = None
    for play in game.game_plays:
        last_play = play

        if play.is_home_team:
            score_home += play.num_runs_scored
        else:
            score_visitor += play.num_runs_scored

    # Save Game
    sql = """
        insert into game
        (
            retrosheet_id,
            game_date,
            game_time,
            team_visiting,
            team_home,
            game_site,
            ump_home,
            ump_1b,
            ump_2b,
            ump_3b,
            score_visitor,
            score_home,
            innings_played,
            game_type
        )
        values 
        (
            %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s
        )
        returning game_id
           """
    db_cursor.execute(sql,
        [
            game.retrosheet_id,
            game.game_date,
            game.game_time,
            game.team_visiting,
            game.team_home,
            game.game_location,
            game.umpire_home,
            game.umpire_1b,
            game.umpire_2b,
            game.umpire_3b,
            score_visitor,
            score_home,
            last_play.inning,
            game.game_type
        ]
    )
    game_id_in_db = db_cursor.fetchone()[0]
    return game_id_in_db


def save_game_plays(db_cursor, game_id : int, plays : list[PlayByPlay]):
    """ Save the list of game plays to the database
    
        db_cursor - database cursor
        game_id - game id
        play_by_play - play by play
    """
    sql = f"""
            insert into game_play (
                game_id,
                retrosheet_id,
                original_event_str,
                inning,
                is_top_of_inning,
                is_home_team,
                game_location,
                batting_team,
                pitching_team,
                batter,
                pitcher,
                batter_lineup_pos,
                batter_fielding_pos,
                batting_hand,
                pitching_hand,
                pitch_count,
                pitch_sequence,
                num_pitches,
                plate_appearance_flag,
                is_at_bat,
                is_single,
                is_double,
                is_triple,
                is_home_run,
                is_sacrifice_bunt,
                is_sacrifice_fly,
                is_hit_by_pitch,
                is_walk,
                is_intentional_walk,
                is_strikeout,
                is_catchers_interference,
                is_other_play_appearance,
                is_other_out,
                is_other_no_out,
                is_ball_in_play,
                is_bunt,
                is_ground_ball,
                is_fly_ball,
                is_line_drive,
                is_double_play_grounded,
                is_double_play_other,
                is_triple_play,
                is_wild_pitch,
                is_passed_ball,
                is_balk,
                is_other_advance,
                is_defensive_indifference,
                is_stole_2,
                is_stole_3,
                is_stole_home,
                is_caught_steeling_2,
                is_caught_steeling_3,
                is_caught_steeling_home,
                is_pickoff_at_1,
                is_pickoff_at_2,
                is_pickoff_at_3,
                is_strikeout_but_safe,
                errors_1,
                errors_2,
                errors_3,
                errors_4,
                errors_5,
                errors_6,
                errors_7,
                errors_8,
                errors_9,
                outs_pre,
                outs_post,
                base_runner_1_pre,
                base_runner_2_pre,
                base_runner_3_pre,
                base_runner_1_post,
                base_runner_2_post,
                base_runner_3_post,
                scorer_from_bat,
                scorer_from_1,
                scorer_from_2,
                scorer_from_3,
                pitcher_charged_run_batter,
                pitcher_charged_run_1,
                pitcher_charged_run_2,
                pitcher_charged_run_3,
                unearned_run_by_batter,
                unearned_run_by_1,
                unearned_run_by_2,
                unearned_run_by_3,
                rbi_batter,
                rbi_1,
                rbi_2,
                rbi_3,
                num_runs_scored,
                num_rbi_credited,
                num_earned_runs,
                num_team_unearned_runs,
                batting_team_lineup_1,
                batting_team_lineup_2,
                batting_team_lineup_3,
                batting_team_lineup_4,
                batting_team_lineup_5,
                batting_team_lineup_6,
                batting_team_lineup_7,
                batting_team_lineup_8,
                batting_team_lineup_9,
                batting_team_field_pos_for_lineup_1,
                batting_team_field_pos_for_lineup_2,
                batting_team_field_pos_for_lineup_3,
                batting_team_field_pos_for_lineup_4,
                batting_team_field_pos_for_lineup_5,
                batting_team_field_pos_for_lineup_6,
                batting_team_field_pos_for_lineup_7,
                batting_team_field_pos_for_lineup_8,
                batting_team_field_pos_for_lineup_9,
                catcher,
                first_baseman,
                second_baseman,
                third_baseman,
                shortstop,
                left_fielder,
                center_fielder,
                right_fielder,
                putouts_unidentified,
                putouts_by_1,
                putouts_by_2,
                putouts_by_3,
                putouts_by_4,
                putouts_by_5,
                putouts_by_6,
                putouts_by_7,
                putouts_by_8,
                putouts_by_9,
                assists_by_1,
                assists_by_2,
                assists_by_3,
                assists_by_4,
                assists_by_5,
                assists_by_6,
                assists_by_7,
                assists_by_8,
                assists_by_9,
                fielding_seq_for_out,
                batout1,
                batout2,
                batout3,
                brout_b,
                brout1,
                brout2,
                brout3,
                firstf,
                loc,
                hittype,
                dpopp,
                pivot,
                play_number,
                umpire_home,
                umpire_1b,
                umpire_2b,
                umpire_3b,
                umpire_left_field,
                umpire_right_field,
                game_date,
                game_type,
                pbp
            )
            values (
                %s, %s, %s, %s, %s, %s, %s, %s, %s, %s,
                %s, %s, %s, %s, %s, %s, %s, %s, %s, %s,
                %s, %s, %s, %s, %s, %s, %s, %s, %s, %s,
                %s, %s, %s, %s, %s, %s, %s, %s, %s, %s,
                %s, %s, %s, %s, %s, %s, %s, %s, %s, %s,
                %s, %s, %s, %s, %s, %s, %s, %s, %s, %s,
                %s, %s, %s, %s, %s, %s, %s, %s, %s, %s,
                %s, %s, %s, %s, %s, %s, %s, %s, %s, %s,
                %s, %s, %s, %s, %s, %s, %s, %s, %s, %s,
                %s, %s, %s, %s, %s, %s, %s, %s, %s, %s,
                %s, %s, %s, %s, %s, %s, %s, %s, %s, %s,
                %s, %s, %s, %s, %s, %s, %s, %s, %s, %s,
                %s, %s, %s, %s, %s, %s, %s, %s, %s, %s,
                %s, %s, %s, %s, %s, %s, %s, %s, %s, %s,
                %s, %s, %s, %s, %s, %s, %s, %s, %s, %s,
                %s, %s, %s, %s, %s, %s, %s, %s, %s, %s,
                %s, %s
            )
        """

    data = []
    for play in plays:
        row = (

            game_id,
            play.retrosheet_id,
            play.original_event_str,
            play.inning,
            play.is_top_of_inning,
            play.is_home_team,
            play.game_location,
            play.batting_team,
            play.pitching_team,
            play.batter,
            play.pitcher,
            play.batter_lineup_pos,
            play.batter_fielding_pos,
            play.batting_hand,
            play.pitching_hand,
            play.pitch_count,
            play.pitch_sequence,
            play.num_pitches,
            play.plate_appearance_flag,
            play.is_at_bat,
            play.is_single,
            play.is_double,
            play.is_triple,
            play.is_home_run,
            play.is_sacrifice_bunt,
            play.is_sacrifice_fly,
            play.is_hit_by_pitch,
            play.is_walk,
            play.is_intentional_walk,
            play.is_strikeout,
            play.is_catchers_interference,
            play.is_other_play_appearance,
            play.is_other_out,
            play.is_other_no_out,
            play.is_ball_in_play,
            play.is_bunt,
            play.is_ground_ball,
            play.is_fly_ball,
            play.is_line_drive,
            play.is_double_play_grounded,
            play.is_double_play_other,
            play.is_triple_play,
            play.is_wild_pitch,
            play.is_passed_ball,
            play.is_balk,
            play.is_other_advance,
            play.is_defensive_indifference,
            play.is_stole_2,
            play.is_stole_3,
            play.is_stole_home,
            play.is_caught_steeling_2,
            play.is_caught_steeling_3,
            play.is_caught_steeling_home,
            play.is_pickoff_at_1,
            play.is_pickoff_at_2,
            play.is_pickoff_at_3,
            play.is_strikeout_but_safe,
            play.errors_1,
            play.errors_2,
            play.errors_3,
            play.errors_4,
            play.errors_5,
            play.errors_6,
            play.errors_7,
            play.errors_8,
            play.errors_9,
            play.outs_pre,
            play.outs_post,
            play.base_runner_1_pre,
            play.base_runner_2_pre,
            play.base_runner_3_pre,
            play.base_runner_1_post,
            play.base_runner_2_post,
            play.base_runner_3_post,
            play.scorer_from_bat,
            play.scorer_from_1,
            play.scorer_from_2,
            play.scorer_from_3,
            play.pitcher_charged_run_batter,
            play.pitcher_charged_run_1,
            play.pitcher_charged_run_2,
            play.pitcher_charged_run_3,
            play.unearned_run_by_batter ,
            play.unearned_run_by_1,
            play.unearned_run_by_2,
            play.unearned_run_by_3,
            play.rbi_batter,
            play.rbi_1,
            play.rbi_2,
            play.rbi_3,
            play.num_runs_scored,
            play.num_rbi_credited,
            play.num_earned_runs,
            play.num_team_unearned_runs,
            play.batting_team_lineup_1,
            play.batting_team_lineup_2,
            play.batting_team_lineup_3,
            play.batting_team_lineup_4,
            play.batting_team_lineup_5,
            play.batting_team_lineup_6,
            play.batting_team_lineup_7,
            play.batting_team_lineup_8,
            play.batting_team_lineup_9,
            play.batting_team_field_pos_for_lineup_1,
            play.batting_team_field_pos_for_lineup_2,
            play.batting_team_field_pos_for_lineup_3,
            play.batting_team_field_pos_for_lineup_4,
            play.batting_team_field_pos_for_lineup_5,
            play.batting_team_field_pos_for_lineup_6,
            play.batting_team_field_pos_for_lineup_7,
            play.batting_team_field_pos_for_lineup_8,
            play.batting_team_field_pos_for_lineup_9,
            play.catcher,
            play.first_baseman,
            play.second_baseman,
            play.third_baseman,
            play.shortstop,
            play.left_fielder,
            play.center_fielder,
            play.right_fielder,
            play.putouts_unidentified,
            play.putouts_by_1,
            play.putouts_by_2,
            play.putouts_by_3,
            play.putouts_by_4,
            play.putouts_by_5,
            play.putouts_by_6,
            play.putouts_by_7,
            play.putouts_by_8,
            play.putouts_by_9,
            play.assists_by_1,
            play.assists_by_2,
            play.assists_by_3,
            play.assists_by_4,
            play.assists_by_5,
            play.assists_by_6,
            play.assists_by_7,
            play.assists_by_8,
            play.assists_by_9,
            play.fielding_seq_for_out,
            play.batout1,
            play.batout2,
            play.batout3,
            play.brout_b,
            play.brout1,
            play.brout2,
            play.brout3,
            play.firstf,
            play.loc,
            play.hittype,
            play.dpopp,
            play.pivot,
            play.play_number,
            play.umpire_home,
            play.umpire_1b,
            play.umpire_2b,
            play.umpire_3b,
            play.umpire_left_field,
            play.umpire_right_field,
            play.game_date,
            play.game_type,
            play.pbp,
        )

        data.append(row)

    # save the records
    db_cursor.executemany(sql, data)


def save_games(db_connection, games_uncommitted):
    """ Save all uncommitted games.
    
        db_connection - database connection
        games_uncommitted - list of uncommitted games
    """
    logger.info("Saving games....  # Queued=%s", len(games_uncommitted))

    # create cursor
    with db_connection.cursor() as db_cursor:

        # save all games
        for game in games_uncommitted:
            # save game and get game id
            game_id = save_game(db_cursor, game)


    # commit the transaction
    db_connection.commit()

    # clear uncommitted games list
    games_uncommitted.clear()


@click.command()
@click.argument('db_connection_string')
@click.argument('play_by_play_file')
@click.option('--save_after_game', default=None, help='Start saving data after the game with the retrosheet id.')
def cli(db_connection_string: str, play_by_play_file: str, save_after_game: str):
    """ CLI for importing retrosheet's play by play data file.
    
        db_connection_string - postgresql database connection string
        play_by_play_file - csv containing historical play by play data
        save_after_game - (optional) skip inserts until after the provided game is reached
    """
    # Default to not set
    logging.getLogger().setLevel(logging.NOTSET)

    # Log info and higher to the console
    console = logging.StreamHandler(sys.stdout)
    console.setLevel(logging.INFO)
    console.setFormatter(ColorOutputFormatter())
    logging.getLogger().addHandler(console)
    
    # ensure data file exists
    logger.info("Data File: %s", play_by_play_file)
    if not os.path.exists(play_by_play_file) or not os.path.isfile(play_by_play_file):
        logger.error("%s must exist and be a data file!  ", play_by_play_file)
        sys.exit(ErrorCodes.MISSING_FILE)

    # log the jump to argument
    waiting_for_first_game = False
    if save_after_game is None:
        logger.info("Save After Game is empty, immediately saving all records.")
    else:
        logger.info("Save After Game: %s", save_after_game)
        waiting_for_first_game = True

    # connect to the database
    logger.info("Database Connection String: %s", db_connection_string)
    db_connection = psycopg.connect(db_connection_string)

    # metrics
    total_line_count = 0
    total_game_count = 0

    # game info
    queued_games = []

    # load file and process line by line
    try:
        with open(play_by_play_file, 'r') as csv_file:
            csv_reader = csv.reader(csv_file)

            # Read the header row
            header = next(csv_reader)
            logger.info(f"CSV Header Row: {header}")

            # running queue of plays for the current game
            current_game = None

            for line in csv_reader:
                if line is not None and len(line) > 0:
                    # validate line
                    if len(line) != NUM_COLUMNS:
                        logger.fatal("Data file contains an invalid row.  Aborting load...  Length=%s Row=%s", len(line), line)
                        sys.exit(ErrorCodes.INVALID_DATA)

                    # update metrics
                    total_line_count += 1

                    # get retrosheet game id for current row
                    line_retrosheet_id = line[0]

                    # see if we are waiting for the specified game and if so, have we reached it
                    if waiting_for_first_game and line_retrosheet_id == save_after_game:
                        logger.info("Was waiting for first game and that game has been reached.  Saving subsequent games.")
                        waiting_for_first_game = False

                    # skip all precediting lines
                    if save_after_game is None or \
                        (not waiting_for_first_game and line_retrosheet_id != save_after_game):

                        # process line
                        play_by_play = convert_line(line)

                        # create new game when needed
                        if current_game is None or play_by_play.retrosheet_id != current_game.retrosheet_id:
                            # save if buffer is reached
                            if GAME_SAVE_INTERVAL > 0 and len(queued_games) >= GAME_SAVE_INTERVAL:
                                # commit the transaction
                                logger.info("Commiting buffer size of %s games.  Total Line Count=%s", len(queued_games), total_line_count)
                                save_games(db_connection, queued_games)

                            # abort if at max game count
                            if MAX_GAMES > 0 and total_game_count >= MAX_GAMES:
                                logger.warning("Stopping load after max games reached, even though more data was still available.  Games Loaded=%s", total_game_count)
                                break

                            # determine home vs away team
                            team_home = None
                            team_visiting = None
                            if play_by_play.is_home_team:
                                team_home = play_by_play.batting_team
                                team_visiting = play_by_play.pitching_team
                            else:
                                team_home = play_by_play.pitching_team
                                team_visiting = play_by_play.batting_team

                            # create new game
                            current_game = Game()
                            current_game.retrosheet_id = play_by_play.retrosheet_id
                            current_game.game_date = play_by_play.game_date.date()
                            current_game.game_time = play_by_play.game_date.time()
                            current_game.team_visiting = team_visiting
                            current_game.team_home = team_home
                            current_game.game_location = play_by_play.game_location
                            current_game.umpire_home = play_by_play.umpire_home
                            current_game.umpire_1b = play_by_play.umpire_1b
                            current_game.umpire_2b = play_by_play.umpire_2b
                            current_game.umpire_3b = play_by_play.umpire_3b
                            current_game.score_visitor = 0
                            current_game.score_home = 0
                            current_game.innings_played = 1
                            current_game.game_type = play_by_play.game_type

                            queued_games.append(current_game)
                            total_game_count += 1

                        # append play to game
                        current_game.game_plays.append(play_by_play)
                else:
                    logger.debug("Skipping empty row")    
    except FileNotFoundError:
        logger.fatal(f"Error: The file '{play_by_play_file}' was not found.")
        sys.exit(ErrorCodes.FILE_NOT_FOUND)

    # save any remaining games
    save_games(db_connection, queued_games)

    # Successfully loaded data file
    logger.info("%s Successfully Imported!", play_by_play_file)
    sys.exit(ErrorCodes.SUCCESS)


if __name__ == '__main__':
    cli()
