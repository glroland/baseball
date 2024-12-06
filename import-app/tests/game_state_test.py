""" Game State Unit Tests

Unit tests for the game state object
"""
import logging
import pytest
from model.game_state import GameState
from model.play_record import PlayRecord
from model.advance_record import AdvanceRecord
from model.runner import Runner

logger = logging.getLogger(__name__)

@pytest.fixture
def new_game():
    game = GameState()
    batter = Runner("B")
    game._runners.append(batter)
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
    batter = Runner("B")
    game._runners.append(batter)
    runner1 = Runner("1")
    game._runners.append(runner1)
    runner2 = Runner("2")
    game._runners.append(runner2)
    runner3 = Runner("3")
    game._runners.append(runner3)
    assert game.is_on_first()
    assert game.is_on_second()
    assert game.is_on_third()
    assert game.get_outs() == 0
    assert game.get_score() == [0, 0]
    return game

@pytest.fixture
def sparse():
    game = GameState()
    batter = Runner("B")
    game._runners.append(batter)
    runner1 = Runner("1")
    game._runners.append(runner1)
    runner3 = Runner("3")
    game._runners.append(runner3)
    assert game.is_on_first()
    assert not game.is_on_second()
    assert game.is_on_third()
    assert game.get_outs() == 0
    assert game.get_score() == [0, 0]
    return game

@pytest.fixture
def runner_on_first():
    game = GameState()
    batter = Runner("B")
    game._runners.append(batter)
    runner1 = Runner("1")
    game._runners.append(runner1)
    assert game.is_on_first()
    assert not game.is_on_second()
    assert not game.is_on_third()
    assert game.get_outs() == 0
    assert game.get_score() == [0, 0]
    return game

def test_single_on_new(new_game):
    new_game.action_advance_runner("B", "1")
    assert new_game.is_on_first()
    assert not new_game.is_on_second()
    assert not new_game.is_on_third()
    assert len(new_game.get_runners()) == 1
    assert new_game.get_runners()[0] == "1"
    assert new_game.get_outs() == 0
    assert new_game.get_score() == [0, 0]

def test_double_on_new_int(new_game):
    new_game.action_advance_runner("B", 2)
    assert not new_game.is_on_first()
    assert new_game.is_on_second()
    assert not new_game.is_on_third()
    assert len(new_game.get_runners()) == 1
    assert new_game.get_runners()[0] == "2"
    assert new_game.get_outs() == 0
    assert new_game.get_score() == [0, 0]

def test_double_on_new_str(new_game):
    new_game.action_advance_runner("B", "2")
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
    new_bases_loaded.action_advance_runner("B", "1")
    assert new_bases_loaded.is_on_first()
    assert new_bases_loaded.is_on_second()
    assert new_bases_loaded.is_on_third()
    assert len(new_bases_loaded.get_runners()) == 3
    assert new_bases_loaded.get_runners() == ["1", "2", "3"]
    assert new_bases_loaded.get_outs() == 0
    assert new_bases_loaded.get_score() == [1, 0]

def test_batter_flyball_error_on_bases_loaded_home(new_bases_loaded):
    new_bases_loaded._top_of_inning_flag = False
    new_bases_loaded.action_advance_runner("B", "1")
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
    new_game._outs = 3
    assert new_game._top_of_inning_flag
    new_game.on_batting_team_change()
    assert new_game._outs == 0
    # data updates innings and batting team change
    #assert not new_game._top_of_inning_flag

def test_dont_advance_23_on_hit(new_game):
    runner2 = Runner("2")
    new_game._runners.append(runner2)
    runner3 = Runner("3")
    new_game._runners.append(runner3)
    new_game.action_advance_runner("B", "1")
    assert new_game.get_outs() == 0
    assert new_game.get_score() == [0, 0]
    assert new_game.is_on_first()
    assert new_game.is_on_second()
    assert new_game.is_on_third()

def test_dont_advance_3_on_hit(new_game):
    runner3 = Runner("3")
    new_game._runners.append(runner3)
    new_game.action_advance_runner("B", "1")
    assert new_game.get_outs() == 0
    assert new_game.get_score() == [0, 0]
    assert new_game.is_on_first()
    assert not new_game.is_on_second()
    assert new_game.is_on_third()

def test_advance_runner_on_1st_not_on_base(new_game):
    try:
        new_game.action_advance_runner("1", "2")
        pytest.fail()
    except ValueError:
        return

def test_advance_runner_on_1st(new_game):
    runner = Runner("1")
    new_game._runners.append(runner)
    new_game.action_advance_runner("1", "2")
    assert not new_game.is_on_first()
    assert new_game.is_on_second()
    assert not new_game.is_on_third()

def test_advance_runner_on_2nd_not_on_base(new_game):
    try:
        new_game.action_advance_runner(2, 3)
        pytest.fail()
    except ValueError:
        return

def test_advance_runner_on_2nd(new_game):
    runner = Runner("2")
    new_game._runners.append(runner)
    new_game.action_advance_runner(2, 3)
    assert not new_game.is_on_first()
    assert not new_game.is_on_second()
    assert new_game.is_on_third()

def test_advance_runner_on_3rd_not_on_base(new_game):
    try:
        new_game.action_advance_runner("3", "H")
        pytest.fail()
    except ValueError:
        return

def test_advance_runner_on_3rd(new_game):
    runner = Runner("3")
    new_game._runners.append(runner)
    new_game.action_advance_runner("3", "H")
    assert not new_game.is_on_first()
    assert not new_game.is_on_second()
    assert not new_game.is_on_third()
    assert new_game.get_score() == [1, 0]

def test_advance_runner_from_3rd_to_2nd(new_game):
    try:
        new_game.action_advance_runner("3", "2")
        pytest.fail()
    except ValueError:
        return

def test_advance_runner_from_3rd_to_1nd(new_game):
    try:
        new_game.action_advance_runner("3", "1")
        pytest.fail()
    except ValueError:
        return

def test_advance_runner_from_2nd_to_1nd(new_game):
    try:
        new_game.action_advance_runner("2", "1")
        pytest.fail()
    except ValueError:
        return

def test_home_run_new_game(new_game):
    new_game.action_advance_runner("B", "H")
    assert not new_game.is_on_first()
    assert not new_game.is_on_second()
    assert not new_game.is_on_third()
    assert len(new_game.get_runners()) == 0
    assert new_game.get_outs() == 0
    assert new_game.get_score() == [1, 0]

def test_home_run_100(new_game):
    runner = Runner("1")
    new_game._runners.append(runner)
    new_game.action_advance_runner("B", "H")
    assert not new_game.is_on_first()
    assert not new_game.is_on_second()
    assert not new_game.is_on_third()
    assert len(new_game.get_runners()) == 0
    assert new_game.get_outs() == 0
    assert new_game.get_score() == [2, 0]

def test_home_run_101(new_game):
    runner1 = Runner("1")
    new_game._runners.append(runner1)
    runner3 = Runner("3")
    new_game._runners.append(runner3)
    new_game.action_advance_runner("B", "H")
    assert not new_game.is_on_first()
    assert not new_game.is_on_second()
    assert not new_game.is_on_third()
    assert len(new_game.get_runners()) == 0
    assert new_game.get_outs() == 0
    assert new_game.get_score() == [3, 0]

def test_home_run_grand_slam(new_game):
    runner1 = Runner("1")
    new_game._runners.append(runner1)
    runner2 = Runner("2")
    new_game._runners.append(runner2)
    runner3 = Runner("3")
    new_game._runners.append(runner3)
    new_game.action_advance_runner("B", "H")
    assert not new_game.is_on_first()
    assert not new_game.is_on_second()
    assert not new_game.is_on_third()
    assert len(new_game.get_runners()) == 0
    assert new_game.get_outs() == 0
    assert new_game.get_score() == [4, 0]

def test_batter_out_sparse(sparse):
    sparse.action_advance_runner("B", "1", True)
    assert not sparse.is_on_first()
    assert sparse.is_on_second()
    assert sparse.is_on_third()
    assert len(sparse.get_runners()) == 2
    assert sparse.get_runners() == ["2", "3"]
    assert sparse.get_outs() == 1
    assert sparse.get_score() == [0, 0]

def test_complex_multi_w_runner_on_first(runner_on_first):
    play = PlayRecord.create("E5/TH.1-3;B-2")
    assert runner_on_first.is_on_first()
    assert not runner_on_first.is_on_second()
    assert not runner_on_first.is_on_third()
    assert runner_on_first.get_outs() == 0
    assert runner_on_first.get_score() == [0, 0]
    runner_on_first.handle_advances(play.advances)
    #runner_on_first.advance_runner("B", "1")
    logging.info("Game Status - %s", runner_on_first.get_game_status_string())
    assert not runner_on_first.is_on_first()
    assert runner_on_first.is_on_second()
    assert runner_on_first.is_on_third()
    assert runner_on_first.get_outs() == 0
    assert runner_on_first.get_score() == [0, 0]
    std_batter = AdvanceRecord()
    std_batter.base_from = "B"
    std_batter.base_to = "1"
    std_batter.was_out = False
    assert std_batter.is_completed(runner_on_first._completed_advancements)

def test_get_current_base_from_original_runner_single(new_game):
    runner = new_game.get_runner_from_original_base("B")
    new_game.action_advance_runner("B", "1")
    assert runner is not None
    assert runner.current_base == "1"

def test_get_current_base_from_original_runner_no_runners(new_game):
    try:
        new_game.get_runner_from_original_base("1")
        pytest.fail()
    except ValueError:
        pass

def test_get_current_base_from_original_runner_double(new_game):
    new_game.action_advance_runner("B", "2")
    runner = new_game.get_runner_from_original_base("B")
    assert runner is not None
    assert runner.current_base == "2"

def test_get_current_base_from_original_runner_triple(new_game):
    new_game.action_advance_runner("B", "3")
    runner = new_game.get_runner_from_original_base("B")
    assert runner is not None
    assert runner.current_base == "3"

def test_get_current_base_from_original_runner_grandslam(new_bases_loaded):
    new_bases_loaded.action_advance_runner("B", "H")
    runner = new_bases_loaded.get_runner_from_original_base("B")
    assert runner is not None
    assert runner.current_base == "H"
    runner = new_bases_loaded.get_runner_from_original_base("1")
    assert runner is not None
    assert runner.current_base == "H"
    runner = new_bases_loaded.get_runner_from_original_base("2")
    assert runner is not None
    assert runner.current_base == "H"
    runner = new_bases_loaded.get_runner_from_original_base("3")
    assert runner is not None
    assert runner.current_base == "H"

def test_get_current_base_from_original_runner_bases_loaded_double(new_bases_loaded):
    new_bases_loaded.action_advance_runner("B", "2")
    runner = new_bases_loaded.get_runner_from_original_base("B")
    assert runner is not None
    assert runner.current_base == "2"
    runner = new_bases_loaded.get_runner_from_original_base("1")
    assert runner is not None
    assert runner.current_base == "3"
    runner = new_bases_loaded.get_runner_from_original_base("2")
    assert runner is not None
    assert runner.current_base == "H"
    runner = new_bases_loaded.get_runner_from_original_base("3")
    assert runner is not None
    assert runner.current_base == "H"
