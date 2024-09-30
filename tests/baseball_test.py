""" Unit tests for Baseball Utilities functions

Baseball Utility Unit Tests
"""
from utils.baseball import sort_defensive_play_actions_desc
from model.play_record import PlayRecord

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
