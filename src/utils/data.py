""" Generic Data Utility Functions

Utility functions to help simplify data manipulation.
"""
import logging
import re
import json
from pydantic import BaseModel

logger = logging.getLogger(__name__)

def fail(s : str, *argv):
    #if argv is None:
    #    logger.fatal(s)
    #else:
    #    logger.fatal(s, argv)
    logger.fatal(s)
    raise ValueError(s)

def to_json_string(i : BaseModel):
    return i.model_dump_json(indent=2)

def regex_split(regex, str):
    if str is None:
        return []
    return list(filter(None, re.split(regex, str)))

def split_leading_chars_from_numbers(str):
    if not re.match("[A-Z]", str[0]):
        msg = f"Input string is not compatible with REGEX!  {str}"
        logger.error(msg)
        raise ValueError(msg)

    result = regex_split("^([A-Z]+)([0-9]*)$", str)

    if len(result) != 2:
        msg = f"Rseulting split is not of the correct structure!  Len={len(result)} Result={result}"
        logger.error(msg)
        raise ValueError(msg)

    return result

def split_num_paren_chunks(str):
    return regex_split("([0-9]+\\([0-9]+\\)?)+", str)

def split_leading_num(str):
    return regex_split("^([0-9]+)(.*)", str)

def extract_groups(str):
    groups = []
    if str is not None and len(str) > 0:
        working = str
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
