""" Baseball App CLI """
import logging
import sys
import os
import click
from utils.db import truncate_table, connect_to_db
from ingest.import_event_data import import_event_file, import_all_event_data_files

@click.command()
@click.argument('event_file_or_dir')
@click.option('--limit', '-l', default=-1,
              help='max games to import')
@click.option('--truncate', '-t', default=True, is_flag=True,
              help='whether or not to truncate all the game tables before import')
@click.option('--debug', '-d', 'log_file', default=None,
              help='enable debug level logging or keep as info')
def cli(event_file_or_dir, limit, truncate, log_file):
    """ CLI utility for importing Retrosheet event files into the game
        history database.  This tool assumes that team and roster data
        has already been imported.
    """
    # Default to not set
    logging.getLogger().setLevel(logging.NOTSET)

    # Log info and higher to the console
    console = logging.StreamHandler(sys.stdout)
    console.setLevel(logging.INFO)
    console.setFormatter(logging.Formatter('%(name)-13s: %(message)s'))
    logging.getLogger().addHandler(console)

    # Log debug and higher to a file
    if log_file is not None:
        file_handler = logging.FileHandler(log_file, 'w+')
        file_handler.setLevel(logging.DEBUG)
        formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
        file_handler.setFormatter(formatter)
        logging.getLogger().addHandler(file_handler)

    # (Optional) Truncate all game event data in the database
    if truncate:
        truncate_table(connect_to_db(), "game", True)

    if os.path.isfile(event_file_or_dir):
        # Import event file
        import_event_file(event_file_or_dir, limit)
    elif os.path.isdir(event_file_or_dir):
        # Import all files in directory
        import_all_event_data_files(event_file_or_dir)

if __name__ == '__main__':
    cli(None, None, None, None)
