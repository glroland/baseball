""" Import Team Roster Data """
import logging
import os
from bulk_load_db import bulk_import_csv_file, fail

logger = logging.getLogger(__name__)

ROSTER_FILE_EXTENSION = ".ROS"

def roster_load_transformer(sql_connection, sql_columns_mapping):
    """ Transforms the load table before being loaded into the actual roster.
    
        sql_connection - sql connection
        sql_columns_mapping - mapping of fields to column numbers
    """
    # validate parameters
    if sql_connection is None:
        fail("SQL Connection not provided.")
    if sql_columns_mapping is None or len(sql_columns_mapping) == 0:
        fail("SQL Columns Mapping is empty!")

    # build column name
    col_number = sql_columns_mapping.index("position")
    if col_number < 0:
        fail("position field does not exist in columsn mapping! " +
             f"{sql_columns_mapping}")
    col_name = "col" + str(col_number)

    # update load table - null positions become "U"
    logger.warning("Updating NULL position values in load table to 'U'")
    sql = f"update temp_load set {col_name} = 'U' where {col_name} is NULL"
    with sql_connection.cursor() as sql_cursor:
        sql_cursor.execute(sql)
    sql_connection.commit()


def import_roster_data_file(file, directory):
    """ Import the specified roster data file.
    
        data_file - roster file to import
    """
    data_file = directory + file
    logger.info("Importing Roster Data File: %s", data_file)

    year = int(file[3:7])
    logger.debug("Data File <%s> is mapping to Year <%s>", file, year)

    sql_table = "roster"
    sql_columns_mapping = ["player_code",
                           "last_name",
                           "first_name",
                           "throw_hand",
                           "batting_hand",
                           "team_code",
                           "position"]

    bulk_import_csv_file(data_file, sql_table, sql_columns_mapping,
                         "season_year", year, roster_load_transformer)

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
