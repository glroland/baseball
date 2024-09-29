""" Baseball Utility Functions

Helper methods for baseball related data.
"""
from utils.data import fail

def get_base_as_int(base):
    """ Gets the specified base as a number.
    
        base - base str
    """
    if base in ["B", 0]:
        return 0
    if base in ["1", 1]:
        return 1
    if base in ["2", 2]:
        return 2
    if base in ["3", 3]:
        return 3
    if base in ["H", 4]:
        return 4
    
    fail(f"get_base_as_int failing due to illegal parameter!  {base}")

def validate_base(base_str, first_allowed=True, home_allowed=True):
    """ Validates the provided string representation of the base
        to ensure it is valid for the circumstance.  Otherwise an exception
        is thrown.
        
        base_str - string representation of the base
        first_allowed - whether first base is a permissiable value
        home_allowed - whether home is a permissiable value
    """
    if base_str is None or len(base_str) != 1:
        fail("Invalid Base String!  Empty string or None.")
    if not isinstance(base_str, str):
        fail("Base String is not a string!")
    if base_str in ["1", 1]:
        if not first_allowed:
            fail("First base is not a permissible value for this play!")
        return True
    if base_str in ["2", 2]:
        return True
    if base_str == ["3", 3]:
        return True
    if base_str == ["H", 4]:
        if not home_allowed:
            fail("Home base is not a permissible value for this play!")
        return True
    fail(f"Unexpected value for Base!  <{base_str}>")
    return False
