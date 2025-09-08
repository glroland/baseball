""" CLI for importing retrosheet's play by play processed event files. """
import logging
import os
import sys
import csv
import click
from typing import List
from datetime import datetime
from play_by_play_type import PlayByPlay
import psycopg

logger = logging.getLogger(__name__)

NUM_COLUMNS = 161
MAX_LINES = -1
COMMIT_INTERVAL = 1000

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
    if column is None or len(column.strip()) == 0:
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


def save_record(db_cursor, play_by_play : PlayByPlay):
    """ Insert the record into the database.
    
        db_curosr - database cursor
        play_by_play - play by play
    """
    sql = f"""
            insert into game_play_by_play(
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
                %s
            )
        """

    data = (

        play_by_play.retrosheet_id,
        play_by_play.original_event_str,
        play_by_play.inning,
        play_by_play.is_top_of_inning,
        play_by_play.is_home_team,
        play_by_play.game_location,
        play_by_play.batting_team,
        play_by_play.pitching_team,
        play_by_play.batter,
        play_by_play.pitcher,
        play_by_play.batter_lineup_pos,
        play_by_play.batter_fielding_pos,
        play_by_play.batting_hand,
        play_by_play.pitching_hand,
        #play_by_play.pitch_count_str,
        play_by_play.pitch_count,
        play_by_play.pitch_sequence,
        #play_by_play.num_pitches_str,
        play_by_play.num_pitches,
        play_by_play.plate_appearance_flag,
        play_by_play.is_at_bat,
        play_by_play.is_single,
        play_by_play.is_double,
        play_by_play.is_triple,
        play_by_play.is_home_run,
        play_by_play.is_sacrifice_bunt,
        play_by_play.is_sacrifice_fly,
        play_by_play.is_hit_by_pitch,
        play_by_play.is_walk,
        play_by_play.is_intentional_walk,
        play_by_play.is_strikeout,
        play_by_play.is_catchers_interference,
        play_by_play.is_other_play_appearance,
        play_by_play.is_other_out,
        play_by_play.is_other_no_out,
        play_by_play.is_ball_in_play,
        play_by_play.is_bunt,
        play_by_play.is_ground_ball,
        play_by_play.is_fly_ball,
        play_by_play.is_line_drive,
        play_by_play.is_double_play_grounded,
        play_by_play.is_double_play_other,
        play_by_play.is_triple_play,
        play_by_play.is_wild_pitch,
        play_by_play.is_passed_ball,
        play_by_play.is_balk,
        play_by_play.is_other_advance,
        play_by_play.is_defensive_indifference,
        play_by_play.is_stole_2,
        play_by_play.is_stole_3,
        play_by_play.is_stole_home,
        play_by_play.is_caught_steeling_2,
        play_by_play.is_caught_steeling_3,
        play_by_play.is_caught_steeling_home,
        play_by_play.is_pickoff_at_1,
        play_by_play.is_pickoff_at_2,
        play_by_play.is_pickoff_at_3,
        play_by_play.is_strikeout_but_safe,
        play_by_play.errors_1,
        play_by_play.errors_2,
        play_by_play.errors_3,
        play_by_play.errors_4,
        play_by_play.errors_5,
        play_by_play.errors_6,
        play_by_play.errors_7,
        play_by_play.errors_8,
        play_by_play.errors_9,
        play_by_play.outs_pre,
        play_by_play.outs_post,
        play_by_play.base_runner_1_pre,
        play_by_play.base_runner_2_pre,
        play_by_play.base_runner_3_pre,
        play_by_play.base_runner_1_post,
        play_by_play.base_runner_2_post,
        play_by_play.base_runner_3_post,
        play_by_play.scorer_from_bat,
        play_by_play.scorer_from_1,
        play_by_play.scorer_from_2,
        play_by_play.scorer_from_3,
        play_by_play.pitcher_charged_run_batter,
        play_by_play.pitcher_charged_run_1,
        play_by_play.pitcher_charged_run_2,
        play_by_play.pitcher_charged_run_3,
        play_by_play.unearned_run_by_batter ,
        play_by_play.unearned_run_by_1,
        play_by_play.unearned_run_by_2,
        play_by_play.unearned_run_by_3,
        play_by_play.rbi_batter,
        play_by_play.rbi_1,
        play_by_play.rbi_2,
        play_by_play.rbi_3,
        play_by_play.num_runs_scored,
        play_by_play.num_rbi_credited,
        play_by_play.num_earned_runs,
        play_by_play.num_team_unearned_runs,
        play_by_play.batting_team_lineup_1,
        play_by_play.batting_team_lineup_2,
        play_by_play.batting_team_lineup_3,
        play_by_play.batting_team_lineup_4,
        play_by_play.batting_team_lineup_5,
        play_by_play.batting_team_lineup_6,
        play_by_play.batting_team_lineup_7,
        play_by_play.batting_team_lineup_8,
        play_by_play.batting_team_lineup_9,
        play_by_play.batting_team_field_pos_for_lineup_1,
        play_by_play.batting_team_field_pos_for_lineup_2,
        play_by_play.batting_team_field_pos_for_lineup_3,
        play_by_play.batting_team_field_pos_for_lineup_4,
        play_by_play.batting_team_field_pos_for_lineup_5,
        play_by_play.batting_team_field_pos_for_lineup_6,
        play_by_play.batting_team_field_pos_for_lineup_7,
        play_by_play.batting_team_field_pos_for_lineup_8,
        play_by_play.batting_team_field_pos_for_lineup_9,
        play_by_play.catcher,
        play_by_play.first_baseman,
        play_by_play.second_baseman,
        play_by_play.third_baseman,
        play_by_play.shortstop,
        play_by_play.left_fielder,
        play_by_play.center_fielder,
        play_by_play.right_fielder,
        play_by_play.putouts_unidentified,
        play_by_play.putouts_by_1,
        play_by_play.putouts_by_2,
        play_by_play.putouts_by_3,
        play_by_play.putouts_by_4,
        play_by_play.putouts_by_5,
        play_by_play.putouts_by_6,
        play_by_play.putouts_by_7,
        play_by_play.putouts_by_8,
        play_by_play.putouts_by_9,
        play_by_play.assists_by_1,
        play_by_play.assists_by_2,
        play_by_play.assists_by_3,
        play_by_play.assists_by_4,
        play_by_play.assists_by_5,
        play_by_play.assists_by_6,
        play_by_play.assists_by_7,
        play_by_play.assists_by_8,
        play_by_play.assists_by_9,
        play_by_play.fielding_seq_for_out,
        play_by_play.batout1,
        play_by_play.batout2,
        play_by_play.batout3,
        play_by_play.brout_b,
        play_by_play.brout1,
        play_by_play.brout2,
        play_by_play.brout3,
        play_by_play.firstf,
        play_by_play.loc,
        play_by_play.hittype,
        play_by_play.dpopp,
        play_by_play.pivot,
        play_by_play.play_number,
        play_by_play.umpire_home,
        play_by_play.umpire_1b,
        play_by_play.umpire_2b,
        play_by_play.umpire_3b,
        play_by_play.umpire_left_field,
        play_by_play.umpire_right_field,
        play_by_play.game_date,
        play_by_play.game_type,
        play_by_play.pbp,
    )

    # save the record
    db_cursor.execute(sql, data)


@click.command()
@click.argument('db_connection_string')
@click.argument('play_by_play_file')
@click.option('--jump_to_line', default=0, help='Start saving data at a specific line number.')
def cli(db_connection_string: str, play_by_play_file: str, jump_to_line: int):
    """ CLI for importing retrosheet's play by play data file.
    
        db_connection_string - postgresql database connection string
        play_by_play_file - csv containing historical play by play data
        jump_to_line - (optional) skip inserts until this line position
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
    logger.info("Jump To Line: %s", jump_to_line)

    # connect to the database
    logger.info("Database Connection String: %s", db_connection_string)
    db_connection = psycopg.connect(db_connection_string)
    db_cursor = db_connection.cursor()

    # metrics
    total_line_count = 0
    lines_uncommitted = 0

    # load file and process line by line
    try:
        with open(play_by_play_file, 'r') as csv_file:
            csv_reader = csv.reader(csv_file)

            # Read the header row
            header = next(csv_reader)
            logger.info(f"CSV Header Row: {header}")

            for line in csv_reader:
                if line is not None and len(line) > 0:
                    # validate line
                    if len(line) != NUM_COLUMNS:
                        logger.fatal("Data file contains an invalid row.  Aborting load...  Length=%s Row=%s", len(line), line)
                        sys.exit(ErrorCodes.INVALID_DATA)

                    # update metrics
                    total_line_count += 1
                    lines_uncommitted += 1

                    # skip all precediting lines
                    if jump_to_line is None or total_line_count >= jump_to_line:
                        # process line
                        play_by_play = convert_line(line)

                        # save the record
                        save_record(db_cursor, play_by_play)

                        # abort if at max line count
                        if MAX_LINES > 0 and total_line_count >= MAX_LINES:
                            logger.warning("Stopping load after max rows reached, even though more data was still available.  Lines Loaded=%s", total_line_count)
                            break

                        # commit if buffer is reached
                        #logger.info("Line # %s ... Uncommitted Line # %s", total_line_count, lines_uncommitted)
                        if COMMIT_INTERVAL > 0 and lines_uncommitted >= COMMIT_INTERVAL:
                            # commit the transaction
                            logger.info("Commiting buffer size of %s lines.  Line Count=%s", lines_uncommitted, total_line_count)
                            db_connection.commit()
                            lines_uncommitted = 0
                else:
                    logger.debug("Skipping empty row")    
    except FileNotFoundError:
        logger.fatal(f"Error: The file '{play_by_play_file}' was not found.")
        sys.exit(ErrorCodes.FILE_NOT_FOUND)
#    except Exception as e:
#        logger.fatal(f"An error occurred while processing %s: {e}", play_by_play_file)
#        sys.exit(ErrorCodes.GENERIC_ERROR)

    # commit the transaction
    if lines_uncommitted > 0:
        logger.info("Commiting buffer size of %s lines.  Line Count=%s", lines_uncommitted, total_line_count)
        db_connection.commit()
        lines_uncommitted = 0

    # Successfully loaded data file
    logger.info("%s Successfully Imported!", play_by_play_file)
    sys.exit(ErrorCodes.SUCCESS)


if __name__ == '__main__':
    cli()
