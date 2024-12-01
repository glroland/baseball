""" Generic Data Utility Functions

Utility functions to help simplify data manipulation.
"""
import os
import logging
import re
from pydantic import BaseModel

logger = logging.getLogger(__name__)

def get_env_value(env_key : str, default : str = None):
    """ Gets the value of the specified environment variable.
    
        env_key - environment variable name
        default - default value if that is not set
    """
    # validate paratmers
    if env_key is None or len(env_key) == 0:
        fail("get_env() - called without valid env_key!")

    # get configured value
    value = default
    if env_key in os.environ:
        value = os.environ[env_key]
    else:
        logger.warning("Config Key not set!  Using default...  Key=%s", env_key)

    logger.debug("Configuration Value.  Key=%s  Value=%s", env_key, value)
    return value

def fail(s : str):
    """ Log and fail process.
    
        s - string to log
    """
    logger.fatal(s)
    raise ValueError(s)

def to_json_string(i : BaseModel):
    """ Create a JSON string for the provided pydantic model.
    
        i - model
    """
    return i.model_dump_json(indent=2)

def regex_split(regex, s):
    """ Split string via a regular expression.
    
        s - string
    """
    if s is None:
        return []
    return list(filter(None, re.split(regex, s)))

def split_leading_chars_from_numbers(s):
    """ Split leading characters from numbers and return an array.
    
        s - string
    """
    if not re.match("[A-Z]", s[0]):
        msg = f"Input string is not compatible with REGEX!  {s}"
        logger.error(msg)
        raise ValueError(msg)

    result = regex_split("^([A-Z]+)([0-9]*)$", s)

    if len(result) != 2:
        msg = f"Rseulting split is not of the correct structure!  Len={len(result)} Result={result}"
        logger.error(msg)
        raise ValueError(msg)

    return result

def split_num_paren_chunks(s):
    """ Split groups of characters associated via characters.
    
        s - string
    """
    return regex_split("([0-9]+\\([0-9]+\\)?)+", s)

def split_leading_num(s):
    """ Split the leading number from a string.
    
        s - string
    """
    return regex_split("^([0-9]+)(.*)", s)

def extract_groups(s):
    """ Extracts groups of characters from a string.
    
        s - string
    """
    groups = []
    if s is not None and len(s) > 0:
        working = s
        while working.count("(") > 0:
            s = working.find("(") + 1
            e = working.find(")")
            groups.append(working[s:e])

            working = working[e+1:]

    return groups

def split_string(s, token_list):
    """ Splits a string into a list of strings using the list of tokens.
    
    s - string to chunk
    token_list - list of tokens to match
    """
    logger.debug("split_string invoked.  String<%s> Tokens<%s>", s, token_list)

    # find all the tokens
    indices = []
    for token in token_list:
        token_index = s.find(token)
        #logger.info("Str=<%s> Token=<%s> Index=<%s>", s, token, token_index)
        indices.append(token_index)

    # find the minimum index
    min_index = -1
    for index in indices:
        if index >= 0:
            if min_index == -1:
                min_index = index
            elif index < min_index:
                min_index = index
    #logger.info("Str=<%s> Min=<%s>", s, min_index)

    # Done
    if min_index == -1 or min_index >= (len(s)-1):
        return [ s ]

    # Split
    return [ s[0:min_index] ] + split_string(s[(min_index+1):], token_list)

# pylint: disable=inconsistent-return-statements
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

def get_optional_value(map, key):
    """ Gets the value of the key in the set or none, if not present.
    
        key - key name
    """
    # validate arguments
    if map is None:
        fail("Input map value is None!")
    if key is None:
        fail("Input key for map is None!")

    # handle non-existent key
    if key not in map:
        logger.debug("Key not present in map!  Key=%s", key)
        return None

    return map[key]
