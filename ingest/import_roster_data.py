""" Import Team Roster Data """
import logging
import os
import csv
from db_utils import connect_to_db

logger = logging.getLogger(__name__)

ROSTER_FILE_EXTENSION = ".ROS"

# pylint: disable=too-many-arguments
def insert_roster_record(sql_cursor,
                         year,
                         player_code,
                         last_name,
                         first_name,
                         throw_hand,
                         batting_hand,
                         team_code,
                         position):

    """ Insert Team Record into DB """
    logger.debug("Inserting Player Record.  Year=%s, Code=%s, LastName=%s, FirstName=%s, " +
                 "ThrowHand=%s, BatHand=%s, TeamCode=%s, Position=%s", +
                 year, player_code, last_name, first_name, throw_hand, batting_hand, team_code,
                 position)

    select_sql = "select count(*) " \
                 "from Rosters " \
                 "where season_year=%s and player_code = %s"

    insert_sql = "insert into Rosters (season_year, player_code, last_name, first_name, " \
                                      "throw_hand, batting_hand, team_code, position) " \
                 "values (%s, %s, %s, %s, %s, %s, %s, %s)"

    sql_cursor.execute(select_sql,
        (
            year,
            player_code
        )
    )
    count = sql_cursor.fetchone()

    if count[0] != 0:
        logger.debug("Record already exists, skipping insert.")
    else:
        logger.debug("Record missing - insertting.")
        sql_cursor.execute(insert_sql,
            (
                year,
                player_code,
                last_name,
                first_name,
                throw_hand,
                batting_hand,
                team_code,
                position
            )
        )


def import_roster_data_file(file, directory):
    """ Import the specified roster data file.
    
        data_file - roster file to import
    """
    data_file = directory + file
    logger.info("Importing Roster Data File: %s", data_file)

    year = int(file[3:6])

    sql_connection = connect_to_db()

    with sql_connection.cursor() as sql_cursor:
        with open(data_file, encoding="utf-8", newline='') as csvfile:
            csv_reader = csv.reader(csvfile, delimiter=',', quotechar='\"')
            for row in csv_reader:
                player_code = row[0]
                last_name = row[1]
                first_name = row[2]
                throw_hand = row[3]
                batting_hand = row[4]
                team_code = row[5]
                position = row[6]

                insert_roster_record(sql_cursor,
                                     year,
                                     player_code,
                                     last_name,
                                     first_name,
                                     throw_hand,
                                     batting_hand,
                                     team_code,
                                     position)

    sql_connection.commit()

    logger.debug("Deleting file after successful processing: %s", data_file)
    os.remove(data_file)


def import_all_roster_data_files(directory):
    """ Imports all roster data files stored in the specified directory.
    
        directory - directory to import roster files from
    """
    logger.info("Importing Roster Data Files from Directory: %s", directory)
    for file in os.listdir(directory):
        if file.endswith(ROSTER_FILE_EXTENSION):
            import_roster_data_file(file, directory)
    logger.debug("All files imported")
