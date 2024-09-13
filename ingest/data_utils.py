""" Generic Data Utility Functions

Utility functions to help simplify data manipulation.
"""
import logging

logger = logging.getLogger(__name__)

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
