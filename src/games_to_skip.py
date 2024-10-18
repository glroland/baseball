""" List of Games to Skip

These games should not be imported due to bad data.
"""
from typing import List

GAMES_TO_SKIP : List[str] = \
[
    # skipping these due to errors in the data
    "ANA200004080",
    "ANA200004100",

    # skipping these due to various data issues that need to be supported somehow
    "CIN201005170"      # 'S9/G.2-3;1X3(936);B-2(TH3)' when runners on 12-
]
