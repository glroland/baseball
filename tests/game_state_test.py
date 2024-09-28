import pytest
from model.game_state import GameState

@pytest.fixture
def new_game():
    game = GameState()
    assert not game.is_on_first()
    assert not game.is_on_second()
    assert not game.is_on_third()
    assert game.get_outs() == 0
    assert game.get_score() == [0, 0]
    assert game.get_score_str() == "0-0"
    return game

@pytest.fixture
def new_bases_loaded():
    game = GameState()
    game.action_batter_to_first_safe()
    game.action_batter_to_first_safe()
    game.action_batter_to_first_safe()
    assert game.is_on_first()
    assert game.is_on_second()
    assert game.is_on_third()
    assert game.get_outs() == 0
    assert game.get_score() == [0, 0]
    return game

def test_single_on_new(new_game):
    new_game.action_batter_to_first_safe()
    assert new_game.is_on_first()
    assert not new_game.is_on_second()
    assert not new_game.is_on_third()
    assert len(new_game.get_runners()) == 1
    assert new_game.get_runners()[0] == "1"
    assert new_game.get_outs() == 0
    assert new_game.get_score() == [0, 0]

def test_double_on_new_int(new_game):
    new_game.action_batter_to_first_safe()
    new_game.action_runner_advance_safe(1, 2)
    assert not new_game.is_on_first()
    assert new_game.is_on_second()
    assert not new_game.is_on_third()
    assert len(new_game.get_runners()) == 1
    assert new_game.get_runners()[0] == "2"
    assert new_game.get_outs() == 0
    assert new_game.get_score() == [0, 0]

def test_double_on_new_str(new_game):
    new_game.action_batter_to_first_safe()
    new_game.action_runner_advance_safe("1", "2")
    assert not new_game.is_on_first()
    assert new_game.is_on_second()
    assert not new_game.is_on_third()
    assert len(new_game.get_runners()) == 1
    assert new_game.get_runners()[0] == "2"
    assert new_game.get_outs() == 0
    assert new_game.get_score() == [0, 0]

def test_batter_flyball_out_on_new(new_game):
    new_game.action_batter_out_non_progressing()
    assert not new_game.is_on_first()
    assert not new_game.is_on_second()
    assert not new_game.is_on_third()
    assert len(new_game.get_runners()) == 0
    assert new_game.get_outs() == 1
    assert new_game.get_score() == [0, 0]

def test_batter_flyball_out_on_bases_loaded(new_bases_loaded):
    new_bases_loaded.action_batter_out_non_progressing()
    assert new_bases_loaded.is_on_first()
    assert new_bases_loaded.is_on_second()
    assert new_bases_loaded.is_on_third()
    assert len(new_bases_loaded.get_runners()) == 3
    assert new_bases_loaded.get_runners() == ["1", "2", "3"]
    assert new_bases_loaded.get_outs() == 1
    assert new_bases_loaded.get_score() == [0, 0]

def test_batter_flyball_error_on_bases_loaded_visitor(new_bases_loaded):
    new_bases_loaded.action_batter_to_first_safe()
    assert new_bases_loaded.is_on_first()
    assert new_bases_loaded.is_on_second()
    assert new_bases_loaded.is_on_third()
    assert len(new_bases_loaded.get_runners()) == 3
    assert new_bases_loaded.get_runners() == ["1", "2", "3"]
    assert new_bases_loaded.get_outs() == 0
    assert new_bases_loaded.get_score() == [1, 0]

def test_batter_flyball_error_on_bases_loaded_home(new_bases_loaded):
    new_bases_loaded.top_of_inning_flag = False
    new_bases_loaded.action_batter_to_first_safe()
    assert new_bases_loaded.is_on_first()
    assert new_bases_loaded.is_on_second()
    assert new_bases_loaded.is_on_third()
    assert len(new_bases_loaded.get_runners()) == 3
    assert new_bases_loaded.get_runners() == ["1", "2", "3"]
    assert new_bases_loaded.get_outs() == 0
    assert new_bases_loaded.get_score() == [0, 1]

def test_switch_batting_teams_zero_outs(new_game):
    try:
        new_game.on_batting_team_change()
    except ValueError:
        return
    pytest.fail()

def test_switch_batting_teams_three_outs(new_game):
    new_game.outs = 3
    assert new_game.top_of_inning_flag
    new_game.on_batting_team_change()
    assert new_game.outs == 0
    assert not new_game.top_of_inning_flag

def test_dont_advance_23_on_hit(new_game):
    new_game.second = True
    new_game.third = True
    new_game.action_batter_to_first_safe()
    assert new_game.get_outs() == 0
    assert new_game.get_score() == [0, 0]
    assert new_game.first
    assert new_game.second
    assert new_game.third

def test_dont_advance_3_on_hit(new_game):
    new_game.third = True
    new_game.action_batter_to_first_safe()
    assert new_game.get_outs() == 0
    assert new_game.get_score() == [0, 0]
    assert new_game.first
    assert not new_game.second
    assert new_game.third
