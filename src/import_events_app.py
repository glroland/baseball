""" Baseball App CLI """
import logging
import click
from utils.db import truncate_table, connect_to_db
from ingest.import_event_data import import_event_file

@click.command()
@click.option('--limit', '-l', default=-1, help='max games to import')
@click.option('--truncate', '-t', default=True, is_flag=True, help='whether or not to truncate all the game tables before import')
@click.option('--debug', '-d', default=False, is_flag=True, help='enable debug level logging or keep as info')
@click.argument('event_file')
def cli(limit, truncate, debug, event_file):
    log_level = logging.INFO
    if debug:
        log_level = logging.DEBUG
    logging.basicConfig(level=log_level,
    handlers=[
        # no need - logging.FileHandler("baseball-ingest.log"),
        logging.StreamHandler()
    ])

    if truncate:
        truncate_table(connect_to_db(), "game", True)
    import_event_file(event_file, limit)


if __name__ == '__main__':
    cli()
