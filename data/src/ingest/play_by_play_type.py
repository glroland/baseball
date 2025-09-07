from datetime import datetime
from pydantic import BaseModel, Field, ConfigDict
from typing import Optional

class PlayByPlay(BaseModel):
    model_config = ConfigDict(validate_assignment=True)

    retrosheet_id : Optional[str] = Field(None, max_length=12)
    original_event_str : Optional[str] = Field(None, max_length=50)
    inning : int = None
    is_top_of_inning : bool = None
    is_home_team : bool = None
    game_location : Optional[str] = Field(None, max_length=5)
    batting_team : Optional[str] = Field(None, max_length=3)
    pitching_team : Optional[str] = Field(None, max_length=3)
    batter : Optional[str] = Field(None, max_length=8)
    pitcher : Optional[str] = Field(None, max_length=8)
    batter_lineup_pos : int = None
    batter_fielding_pos : int = None
    batting_hand : Optional[str] = Field(None, max_length=1)
    pitching_hand : Optional[str] = Field(None, max_length=1)
    pitch_count_str : str = None
    pitch_count : int = None
    pitch_sequence : Optional[str] = Field(None, max_length=20)
    num_pitches_str : str = None
    num_pitches : int = None
    plate_appearance_flag : bool = None
    is_at_bat : bool = None
    is_single : bool = None
    is_double : bool = None
    is_triple : bool = None
    is_home_run : bool = None
    is_sacrifice_bunt : bool = None
    is_sacrifice_fly : bool = None
    is_hit_by_pitch : bool = None
    is_walk : bool = None
    is_intentional_walk : bool = None
    is_strikeout : bool = None
    is_catchers_interference : bool = None
    is_other_play_appearance : bool = None
    is_other_out : bool = None
    is_other_no_out : bool = None
    is_ball_in_play : bool = None
    is_bunt : bool = None
    is_ground_ball : bool = None
    is_fly_ball : bool = None
    is_line_drive : bool = None
    is_double_play_grounded : bool = None
    is_double_play_other : bool = None
    is_triple_play : bool = None
    is_wild_pitch : bool = None
    is_passed_ball : bool = None
    is_balk : bool = None
    is_other_advance : bool = None
    is_defensive_indifference : bool = None
    is_stole_2 : bool = None
    is_stole_3 : bool = None
    is_stole_home : bool = None
    is_caught_steeling_2 : bool = None
    is_caught_steeling_3 : bool = None
    is_caught_steeling_home : bool = None
    is_pickoff_at_1 : bool = None
    is_pickoff_at_2 : bool = None
    is_pickoff_at_3 : bool = None
    is_strikeout_but_safe : bool = None
    errors_1 : int = None
    errors_2 : int = None
    errors_3 : int = None
    errors_4 : int = None
    errors_5 : int = None
    errors_6 : int = None
    errors_7 : int = None
    errors_8 : int = None
    errors_9 : int = None
    outs_pre : int = None
    outs_post : int = None
    base_runner_1_pre : Optional[str] = Field(None, max_length=8)
    base_runner_2_pre : Optional[str] = Field(None, max_length=8)
    base_runner_3_pre : Optional[str] = Field(None, max_length=8)
    base_runner_1_post : Optional[str] = Field(None, max_length=8)
    base_runner_2_post : Optional[str] = Field(None, max_length=8)
    base_runner_3_post : Optional[str] = Field(None, max_length=8)
    scorer_from_bat : Optional[str] = Field(None, max_length=8)
    scorer_from_1 : Optional[str] = Field(None, max_length=8)
    scorer_from_2 : Optional[str] = Field(None, max_length=8)
    scorer_from_3 : Optional[str] = Field(None, max_length=8)
    pitcher_charged_run_batter : Optional[str] = Field(None, max_length=8)
    pitcher_charged_run_1 : Optional[str] = Field(None, max_length=8)
    pitcher_charged_run_2 : Optional[str] = Field(None, max_length=8)
    pitcher_charged_run_3 : Optional[str] = Field(None, max_length=8)
    unearned_run_by_batter : Optional[str] = Field(None, max_length=8)
    unearned_run_by_1 : Optional[str] = Field(None, max_length=8)
    unearned_run_by_2 : Optional[str] = Field(None, max_length=8)
    unearned_run_by_3 : Optional[str] = Field(None, max_length=8)
    rbi_batter : Optional[str] = Field(None, max_length=8)
    rbi_1 : Optional[str] = Field(None, max_length=8)
    rbi_2 : Optional[str] = Field(None, max_length=8)
    rbi_3 : Optional[str] = Field(None, max_length=8)
    num_runs_scored : int = None
    num_rbi_credited : int = None
    num_earned_runs : int = None
    num_team_unearned_runs : int = None
    batting_team_lineup_1 : Optional[str] = Field(None, max_length=8)
    batting_team_lineup_2 : Optional[str] = Field(None, max_length=8)
    batting_team_lineup_3 : Optional[str] = Field(None, max_length=8)
    batting_team_lineup_4 : Optional[str] = Field(None, max_length=8)
    batting_team_lineup_5 : Optional[str] = Field(None, max_length=8)
    batting_team_lineup_6 : Optional[str] = Field(None, max_length=8)
    batting_team_lineup_7 : Optional[str] = Field(None, max_length=8)
    batting_team_lineup_8 : Optional[str] = Field(None, max_length=8)
    batting_team_lineup_9 : Optional[str] = Field(None, max_length=8)
    batting_team_field_pos_for_lineup_1 : Optional[str] = Field(None, max_length=8)
    batting_team_field_pos_for_lineup_2 : Optional[str] = Field(None, max_length=8)
    batting_team_field_pos_for_lineup_3 : Optional[str] = Field(None, max_length=8)
    batting_team_field_pos_for_lineup_4 : Optional[str] = Field(None, max_length=8)
    batting_team_field_pos_for_lineup_5 : Optional[str] = Field(None, max_length=8)
    batting_team_field_pos_for_lineup_6 : Optional[str] = Field(None, max_length=8)
    batting_team_field_pos_for_lineup_7 : Optional[str] = Field(None, max_length=8)
    batting_team_field_pos_for_lineup_8 : Optional[str] = Field(None, max_length=8)
    batting_team_field_pos_for_lineup_9 : Optional[str] = Field(None, max_length=8)
    catcher : Optional[str] = Field(None, max_length=8)
    first_baseman : Optional[str] = Field(None, max_length=8)
    second_baseman : Optional[str] = Field(None, max_length=8)
    third_baseman : Optional[str] = Field(None, max_length=8)
    shortstop : Optional[str] = Field(None, max_length=8)
    left_fielder : Optional[str] = Field(None, max_length=8)
    center_fielder : Optional[str] = Field(None, max_length=8)
    right_fielder : Optional[str] = Field(None, max_length=8)
    putouts_unidentified : int = None
    putouts_by_1 : int = None
    putouts_by_2 : int = None
    putouts_by_3 : int = None
    putouts_by_4 : int = None
    putouts_by_5 : int = None
    putouts_by_6 : int = None
    putouts_by_7 : int = None
    putouts_by_8 : int = None
    putouts_by_9 : int = None
    assists_by_1 : int = None
    assists_by_2 : int = None
    assists_by_3 : int = None
    assists_by_4 : int = None
    assists_by_5 : int = None
    assists_by_6 : int = None
    assists_by_7 : int = None
    assists_by_8 : int = None
    assists_by_9 : int = None
    fielding_seq_for_out : Optional[str] = Field(None, max_length=10)
    batout1 : int = None
    batout2 : int = None
    batout3 : int = None
    brout_b : int = None
    brout1 : int = None
    brout2 : int = None
    brout3 : int = None
    firstf : int = None
    loc : Optional[str] = Field(None, max_length=10)
    hittype : Optional[str] = Field(None, max_length=1)
    dpopp : int = None
    pivot : Optional[str] = Field(None, max_length=8)
    play_number : int = None
    umpire_home : Optional[str] = Field(None, max_length=8)
    umpire_1b : Optional[str] = Field(None, max_length=8)
    umpire_2b : Optional[str] = Field(None, max_length=8)
    umpire_3b : Optional[str] = Field(None, max_length=8)
    umpire_left_field : Optional[str] = Field(None, max_length=8)
    umpire_right_field : Optional[str] = Field(None, max_length=8)
    game_date : datetime = None
    game_type : Optional[str] = Field(None, max_length=1)
    pbp : Optional[str] = Field(None, max_length=1)
