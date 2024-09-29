""" Unit Tests for Advance Record

Automated testing for the advancement record.
"""
import pytest
from model.advance_record import AdvanceRecord

@pytest.fixture
def empty():
    return []

@pytest.fixture
def sparse1():
    first_to_second = AdvanceRecord()
    first_to_second.base_from = "1"
    first_to_second.base_to = "2"
    first_to_second.was_out = False

    third_to_home = AdvanceRecord()
    third_to_home.base_from = "3"
    third_to_home.base_to = "H"
    third_to_home.was_out = False

    return [first_to_second, third_to_home]

@pytest.fixture
def sparse2():
    first_to_second = AdvanceRecord()
    first_to_second.base_from = "1"
    first_to_second.base_to = "2"
    first_to_second.was_out = False

    second_to_home = AdvanceRecord()
    second_to_home.base_from = "2"
    second_to_home.base_to = "H"
    second_to_home.was_out = False

    return [first_to_second, second_to_home]

@pytest.fixture
def sparse3():
    first_to_second = AdvanceRecord()
    first_to_second.base_from = "1"
    first_to_second.base_to = "2"
    first_to_second.was_out = False

    third_to_home = AdvanceRecord()
    third_to_home.base_from = "B"
    third_to_home.base_to = "1"
    third_to_home.was_out = False

    return [first_to_second, third_to_home]

@pytest.fixture
def busy():
    batter_to_second = AdvanceRecord()
    batter_to_second.base_from = "B"
    batter_to_second.base_to = "1"
    batter_to_second.was_out = False

    first_to_second = AdvanceRecord()
    first_to_second.base_from = "1"
    first_to_second.base_to = "2"
    first_to_second.was_out = False

    second_to_third = AdvanceRecord()
    second_to_third.base_from = "2"
    second_to_third.base_to = "3"
    second_to_third.was_out = False

    third_to_home = AdvanceRecord()
    third_to_home.base_from = "3"
    third_to_home.base_to = "H"
    third_to_home.was_out = False

    return [batter_to_second, first_to_second, second_to_third, third_to_home]

def test_is_overlapping_empty_base_hit(empty):
    # record to compare
    advance = AdvanceRecord()
    advance.base_from = "B"
    advance.base_to = "1"
    advance.was_out = False

    assert not advance.is_completed(empty)

def test_is_overlapping_empty_steal(empty):
    # record to compare
    advance = AdvanceRecord()
    advance.base_from = "2"
    advance.base_to = "3"
    advance.was_out = False

    assert not advance.is_completed(empty)

def test_is_overlapping_empty_run(empty):
    # record to compare
    advance = AdvanceRecord()
    advance.base_from = "3"
    advance.base_to = "H"
    advance.was_out = False

    assert not advance.is_completed(empty)

def test_is_overlapping_empty_out(empty):
    # record to compare
    advance = AdvanceRecord()
    advance.base_from = "B"
    advance.base_to = "1"
    advance.was_out = True

    assert not advance.is_completed(empty)

def test_is_overlapping_double_sparse3(sparse3):
    # record to compare
    advance = AdvanceRecord()
    advance.base_from = "B"
    advance.base_to = "2"
    advance.was_out = False

    assert advance.is_completed(sparse3)

def test_is_overlapping_single_sparse1(sparse1):
    # record to compare
    advance = AdvanceRecord()
    advance.base_from = "B"
    advance.base_to = "1"
    advance.was_out = False

    assert not advance.is_completed(sparse1)

def test_is_overlapping_single_busy(busy):
    # record to compare
    advance = AdvanceRecord()
    advance.base_from = "B"
    advance.base_to = "1"
    advance.was_out = False

    assert advance.is_completed(busy)

def test_is_overlapping_triple_busy(busy):
    # record to compare
    advance = AdvanceRecord()
    advance.base_from = "B"
    advance.base_to = "3"
    advance.was_out = False

    assert advance.is_completed(busy)

def test_is_overlapping_triple_busy(sparse2):
    # record to compare
    advance = AdvanceRecord()
    advance.base_from = "B"
    advance.base_to = "3"
    advance.was_out = False

    assert not advance.is_completed(sparse2)
