from datetime import datetime
from pydantic import BaseModel, Field, ConfigDict
from typing import Optional

class PlayByPlay(BaseModel):
    model_config = ConfigDict(validate_assignment=True)

    retrosheet_id : Optional[str] = Field(None, max_length=12)
    original_event_str : Optional[str] = Field(None, max_length=125)
    inning : Optional[int] = None
    is_top_of_inning : Optional[bool] = None
    is_home_team : Optional[bool] = None
    game_location : Optional[str] = Field(None, max_length=5)
    batting_team : Optional[str] = Field(None, max_length=3)
    pitching_team : Optional[str] = Field(None, max_length=3)
    batter : Optional[str] = Field(None, max_length=8)
    pitcher : Optional[str] = Field(None, max_length=8)
    batter_lineup_pos : Optional[int] = None
    batter_fielding_pos : Optional[int] = None
    batting_hand : Optional[str] = Field(None, max_length=1)
    pitching_hand : Optional[str] = Field(None, max_length=1)
    pitch_count_str : str = None
    pitch_count : Optional[int] = None
    pitch_sequence : Optional[str] = Field(None, max_length=20)
    num_pitches_str : str = None
    num_pitches : Optional[int] = None
    plate_appearance_flag : Optional[bool] = None
    is_at_bat : Optional[bool] = None
    is_single : Optional[bool] = None
    is_double : Optional[bool] = None
    is_triple : Optional[bool] = None
    is_home_run : Optional[bool] = None
    is_sacrifice_bunt : Optional[bool] = None
    is_sacrifice_fly : Optional[bool] = None
    is_hit_by_pitch : Optional[bool] = None
    is_walk : Optional[bool] = None
    is_intentional_walk : Optional[bool] = None
    is_strikeout : Optional[bool] = None
    is_catchers_interference : Optional[bool] = None
    is_other_play_appearance : Optional[bool] = None
    is_other_out : Optional[bool] = None
    is_other_no_out : Optional[bool] = None
    is_ball_in_play : Optional[bool] = None
    is_bunt : Optional[bool] = None
    is_ground_ball : Optional[bool] = None
    is_fly_ball : Optional[bool] = None
    is_line_drive : Optional[bool] = None
    is_double_play_grounded : Optional[bool] = None
    is_double_play_other : Optional[bool] = None
    is_triple_play : Optional[bool] = None
    is_wild_pitch : Optional[bool] = None
    is_passed_ball : Optional[bool] = None
    is_balk : Optional[bool] = None
    is_other_advance : Optional[bool] = None
    is_defensive_indifference : Optional[bool] = None
    is_stole_2 : Optional[bool] = None
    is_stole_3 : Optional[bool] = None
    is_stole_home : Optional[bool] = None
    is_caught_steeling_2 : Optional[bool] = None
    is_caught_steeling_3 : Optional[bool] = None
    is_caught_steeling_home : Optional[bool] = None
    is_pickoff_at_1 : Optional[bool] = None
    is_pickoff_at_2 : Optional[bool] = None
    is_pickoff_at_3 : Optional[bool] = None
    is_strikeout_but_safe : Optional[bool] = None
    errors_1 : Optional[int] = None
    errors_2 : Optional[int] = None
    errors_3 : Optional[int] = None
    errors_4 : Optional[int] = None
    errors_5 : Optional[int] = None
    errors_6 : Optional[int] = None
    errors_7 : Optional[int] = None
    errors_8 : Optional[int] = None
    errors_9 : Optional[int] = None
    outs_pre : Optional[int] = None
    outs_post : Optional[int] = None
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
    num_runs_scored : Optional[int] = None
    num_rbi_credited : Optional[int] = None
    num_earned_runs : Optional[int] = None
    num_team_unearned_runs : Optional[int] = None
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
    putouts_unidentified : Optional[int] = None
    putouts_by_1 : Optional[int] = None
    putouts_by_2 : Optional[int] = None
    putouts_by_3 : Optional[int] = None
    putouts_by_4 : Optional[int] = None
    putouts_by_5 : Optional[int] = None
    putouts_by_6 : Optional[int] = None
    putouts_by_7 : Optional[int] = None
    putouts_by_8 : Optional[int] = None
    putouts_by_9 : Optional[int] = None
    assists_by_1 : Optional[int] = None
    assists_by_2 : Optional[int] = None
    assists_by_3 : Optional[int] = None
    assists_by_4 : Optional[int] = None
    assists_by_5 : Optional[int] = None
    assists_by_6 : Optional[int] = None
    assists_by_7 : Optional[int] = None
    assists_by_8 : Optional[int] = None
    assists_by_9 : Optional[int] = None
    fielding_seq_for_out : Optional[str] = Field(None, max_length=10)
    batout1 : Optional[int] = None
    batout2 : Optional[int] = None
    batout3 : Optional[int] = None
    brout_b : Optional[int] = None
    brout1 : Optional[int] = None
    brout2 : Optional[int] = None
    brout3 : Optional[int] = None
    firstf : Optional[int] = None
    loc : Optional[str] = Field(None, max_length=10)
    hittype : Optional[str] = Field(None, max_length=1)
    dpopp : Optional[int] = None
    pivot : Optional[str] = Field(None, max_length=8)
    play_number : Optional[int] = None
    umpire_home : Optional[str] = Field(None, max_length=8)
    umpire_1b : Optional[str] = Field(None, max_length=8)
    umpire_2b : Optional[str] = Field(None, max_length=8)
    umpire_3b : Optional[str] = Field(None, max_length=8)
    umpire_left_field : Optional[str] = Field(None, max_length=8)
    umpire_right_field : Optional[str] = Field(None, max_length=8)
    game_date : Optional[datetime] = None
    game_type : Optional[str] = Field(None, max_length=1)
    pbp : Optional[str] = Field(None, max_length=1)
