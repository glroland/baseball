""" Import Team Data File """
import os
import logging
import csv
from db_utils import connect_to_db

logger = logging.getLogger(__name__)

TEAM_FILE_PREFIX = "TEAM"

# pylint: disable=too-many-arguments
def insert_team_record(sql_cursor, year, team_code, league, team_location, team_name):
    """ Insert Team Record into DB """
    logger.debug("Inserting Team Record.  Year=%s, Code=%s, League=%s, Location=%s, Name=%s",
                 year, team_code, league, team_location, team_name)

    select_sql = "select count(*) " \
                 "from Teams " \
                 "where season_year=%s and team_code = %s"

    insert_sql = "insert into Teams (season_year, team_code, league, team_location, team_name)" \
                 "values (%s, %s, %s, %s, %s)"

    sql_cursor.execute(select_sql,
        (
            year,
            team_code
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
                team_code,
                league,
                team_location,
                team_name
            )
        )


def import_team_data_file(file, directory):
    """ Import the specified team data file.
    
        data_file - team file to import
    """
    data_file = directory + file
    logger.info("Importing Team Data File: %s", data_file)
    year = int(file.replace(TEAM_FILE_PREFIX, ""))

    sql_connection = connect_to_db()

    with sql_connection.cursor() as sql_cursor:
        with open(data_file, encoding="utf-8", newline='') as csvfile:
            csv_reader = csv.reader(csvfile, delimiter=',', quotechar='\"')
            for row in csv_reader:
                team_code = row[0]
                league = row[1]
                team_location = row[2]
                team_name = row[3]

                insert_team_record(sql_cursor, year, team_code, league, team_location, team_name)

    sql_connection.commit()

    logger.debug("Deleting file after successful processing: %s", data_file)
    os.remove(data_file)


def import_all_team_data_files(directory):
    """ Imports all team data files stored in the specified directory.
    
        directory - directory to import team files from
    """
    logger.info("Importing Team Data Files from Directory: %s", directory)
    for file in os.listdir(directory):
        if file.startswith(TEAM_FILE_PREFIX):
            import_team_data_file(file, directory)
    logger.debug("All files imported")
