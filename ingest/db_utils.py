""" SQL Utilities"""
import logging
import os
# import pyodbc
import psycopg

logger = logging.getLogger(__name__)

ENV_BASEBALL_DB_CONN_STRING = "BASEBALL_DB_CONN_STRING"
DEFAULT_DB_CONN_STRING = "postgresql://baseball_app:baseball123@tools/baseball_db"


def connect_to_db():
    """ Connects to the baseball database """
    logger.debug("Connecting to database.")

    connection_string = DEFAULT_DB_CONN_STRING
    if ENV_BASEBALL_DB_CONN_STRING in os.environ:
        connection_string = os.environ[ENV_BASEBALL_DB_CONN_STRING]

    #return pyodbc.connect(connection_string)
    return psycopg.connect(connection_string)
