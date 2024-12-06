""" Data Tests

Tests for data Utilities
"""
import pytest
from utils.data import fail

def test_fail_msg_only():
    try:
        fail("test")
    except ValueError:
        return
    pytest.fail()
