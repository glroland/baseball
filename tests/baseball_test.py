""" Unit tests for Baseball Utilities functions

Baseball Utility Unit Tests
"""
import pytest
from utils.baseball import sort_defensive_play_actions_desc, sort_play_advances_desc
from model.play_record import PlayRecord
from model.advance_record import AdvanceRecord

@pytest.fixture
def advances_loaded():
    advance1 = AdvanceRecord()
    advance1.base_from = "B"
    advance1.base_to = "1"
    advance2 = AdvanceRecord()
    advance2.base_from = "1"
    advance2.base_to = "2"
    advance3 = AdvanceRecord()
    advance3.base_from = "2"
    advance3.base_to = "3"
    advance4 = AdvanceRecord()
    advance4.base_from = "3"
    advance4.base_to = "H"
    return [advance1, advance2, advance3, advance4]

def test_non_def_sort():
    play = PlayRecord.create("K")
    sort_defensive_play_actions_desc(play)
    assert len(play.actions) == 1
    assert play.actions[0].action == "K"

def test_non_def_w_modifier_sort():
    play = PlayRecord.create("S3/RBI")
    sort_defensive_play_actions_desc(play)
    assert len(play.actions) == 1
    assert play.actions[0].action == "S3"

def test_def_simple():
    play = PlayRecord.create("3")
    sort_defensive_play_actions_desc(play)
    assert len(play.actions) == 1
    assert play.actions[0].action == "3"

def test_def_simple_w_group():
    play = PlayRecord.create("2(B)")
    sort_defensive_play_actions_desc(play)
    assert len(play.actions) == 1
    assert play.actions[0].action == "2"
    assert len(play.actions[0].groups)  == 1
    assert play.actions[0].groups[0] == "B"

def test_def_multi_w_two_groups():
    play = PlayRecord.create("2(B)4(1)/LDP")
    assert len(play.actions) == 2
    assert play.actions[0].action == "2"
    assert len(play.actions[0].groups) == 1
    assert play.actions[0].groups[0] == "B"
    assert len(play.actions[0].modifiers) == 1
    assert play.actions[0].modifiers[0] == "LDP"
    assert play.actions[1].action == "4"
    assert len(play.actions[1].groups) == 1
    assert play.actions[1].groups[0] == "1"
    sort_defensive_play_actions_desc(play)
    assert len(play.actions) == 2
    assert play.actions[0].action == "4"
    assert len(play.actions[0].groups) == 1
    assert play.actions[0].groups[0] == "1"
    assert len(play.actions[1].modifiers) == 1      # modifier stays with original action
    assert play.actions[1].modifiers[0] == "LDP"    # modifier stays with original action
    assert play.actions[1].action == "2"
    assert len(play.actions[1].groups) == 1
    assert play.actions[1].groups[0] == "B"

def test_def_multi_w_two_groups_already_sorted():
    play = PlayRecord.create("3(1)1(B)")
    assert len(play.actions) == 2
    assert play.actions[0].action == "3"
    assert len(play.actions[0].groups) == 1
    assert play.actions[0].groups[0] == "1"
    assert len(play.actions[0].modifiers) == 0
    assert play.actions[1].action == "1"
    assert len(play.actions[1].groups) == 1
    assert play.actions[1].groups[0] == "B"
    sort_defensive_play_actions_desc(play)
    assert len(play.actions) == 2
    assert play.actions[0].action == "3"
    assert len(play.actions[0].groups) == 1
    assert play.actions[0].groups[0] == "1"
    assert len(play.actions[0].modifiers) == 0
    assert play.actions[1].action == "1"
    assert len(play.actions[1].groups) == 1
    assert play.actions[1].groups[0] == "B"

def test_advance_sort_loaded_all_safe(advances_loaded):
    results = sort_play_advances_desc(advances_loaded)
    assert len(results) == 4
    assert results[0].base_from == "3"
    assert results[0].base_to == "H"
    assert results[1].base_from == "2"
    assert results[1].base_to == "3"
    assert results[2].base_from == "1"
    assert results[2].base_to == "2"
    assert results[3].base_from == "B"
    assert results[3].base_to == "1"

def test_advance_sort_loaded_all_out(advances_loaded):
    advances_loaded[0].was_out = True
    advances_loaded[1].was_out = True
    advances_loaded[2].was_out = True
    advances_loaded[3].was_out = True
    results = sort_play_advances_desc(advances_loaded)
    assert len(results) == 4
    assert results[0].base_from == "3"
    assert results[0].base_to == "H"
    assert results[1].base_from == "2"
    assert results[1].base_to == "3"
    assert results[2].base_from == "1"
    assert results[2].base_to == "2"
    assert results[3].base_from == "B"
    assert results[3].base_to == "1"

def test_advance_sort_loaded_all_safe_and_out(advances_loaded):
    advances_loaded[0].was_out = True
    advances_loaded[1].was_out = False
    advances_loaded[2].was_out = True
    advances_loaded[3].was_out = False
    results = sort_play_advances_desc(advances_loaded)
    assert len(results) == 4
    assert results[0].base_from == "2"
    assert results[0].base_to == "3"
    assert results[1].base_from == "B"
    assert results[1].base_to == "1"
    assert results[2].base_from == "3"
    assert results[2].base_to == "H"
    assert results[3].base_from == "1"
    assert results[3].base_to == "2"
