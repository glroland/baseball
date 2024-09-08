""" SQL Utilities"""
import logging
import os
import subprocess
# import pyodbc
import psycopg

logger = logging.getLogger(__name__)

ENV_BASEBALL_DB_CONN_STRING = "BASEBALL_DB_CONN_STRING"
DEFAULT_DB_CONN_STRING = "postgresql://baseball_app:baseball123@tools/baseball_db"


def connect_to_db_with_conn_str(connection_string):
    """ Connects to the baseball database """
    logger.debug("Connecting to database.")

    #return pyodbc.connect(connection_string)
    return psycopg.connect(connection_string)


def connect_to_db():
    """ Connects to the baseball database """
    logger.debug("Connecting to database.")

    connection_string = DEFAULT_DB_CONN_STRING
    if ENV_BASEBALL_DB_CONN_STRING in os.environ:
        connection_string = os.environ[ENV_BASEBALL_DB_CONN_STRING]

    return connect_to_db_with_conn_str(connection_string)


def truncate_load_table(sql_connection):
    """ Truncates the temperary load table.
    
        sql_cursor - SQL Cursor
    """
    logger.debug("Truncating Load Table")
    with sql_connection.cursor() as sql_cursor:
        sql_cursor.execute("truncate temp_load")
    sql_connection.commit()


def raw_file_import(connection_string, data_file, columns_str):
    """ Performs the raw file import into the temp load table.
    
    """
    logger.debug("Doing bulk data load of CSV file into temp table.  File<%s>", data_file)
    
    # Execute bulk load command
    copy_sql = f"\copy temp_load ( {columns_str} ) from '{data_file}' delimiter ',' csv"
    subprocess.run(["psql", connection_string, "-c", copy_sql], check=True)
    logger.debug("Imported data file. %s", data_file)


def migrate_load_to_table(sql_connection, table_name, sql_columns_str, preval, temp_columns_str):
    """ Perform an in-database migration of data from the loading table
        to the destination table.

        sql_cursor - cursor to use
        table_name - name of destination table
        sql_columns_mapping - array of columns correlating to each load column
    """
    sql = f"insert into {table_name} ( {sql_columns_str} ) select {preval}, {temp_columns_str} from temp_load"
    logger.debug("Copying data from load to prod.  SQL<%s>", sql)
    with sql_connection.cursor() as sql_cursor:
        sql_cursor.execute(sql)
    sql_connection.commit()


def bulk_import_csv_file(data_file, table_name, sql_columns_mapping, file_identifier_col, file_identifier):
    """ Bulk imports the provided CSV file into the specified table and columns.
    
        data_file - csv file
        table_name - name of table
        columns_str - typical column list separated by comman
        """
    logger.info("Bulk Importing Data File <%s> into Table <%s>", data_file, table_name)

    # Connect to database
    connection_string = ENV_BASEBALL_DB_CONN_STRING
    if ENV_BASEBALL_DB_CONN_STRING in os.environ:
        connection_string = os.environ[ENV_BASEBALL_DB_CONN_STRING]
    sql_connection = connect_to_db_with_conn_str(connection_string)

    # Truncate load table
    truncate_load_table(sql_connection)

    # Create columns list string
    load_columns_str = ""
    sql_columns_str = ""
    for i in range(len(sql_columns_mapping)):
        if i > 0:
            load_columns_str = load_columns_str + ", "
            sql_columns_str = sql_columns_str + ", "
        load_columns_str = load_columns_str + "col" + str(i)
        sql_columns_str = sql_columns_str + sql_columns_mapping[i]

    # Load the datafile
    raw_file_import(connection_string, data_file, load_columns_str)

    # Migrate the temp table to the destination
    migrate_load_to_table(sql_connection, 
                          table_name,
                          file_identifier_col + ", " + sql_columns_str, 
                          file_identifier, 
                          load_columns_str)

    logger.debug ("Completed Bulk Import of File: %s", data_file)
