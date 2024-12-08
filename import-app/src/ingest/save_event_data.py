""" Save Game Data Functions

Persists the game data hierarchy of classes to a SQL database.
"""
import logging
import psycopg
from model.game_at_bat import GameAtBat
from model.game_substitution import GameSubstitution
from utils.data import get_optional_value

logger = logging.getLogger(__name__)

def save_game_base_record(sql_connection, game):
    """ Save the provided game base record to the database.
    
        sql_connection - sql connection to use for the tx
        game - game record to save 
    """
    logger.debug("Saving Base Game Record!  ID=%s", game.game_id)

    # get game score
    score_visitor, score_home = game.get_score()

    # Save Game
    sql = """
        insert into game
        (
            retrosheet_id,
            game_date,
            game_time,
            game_number_that_day,
            team_visiting,
            team_home,
            game_site,
            night_flag,
            ump_home,
            ump_1b,
            ump_2b,
            ump_3b,
            official_scorer,
            temperature,
            wind_direction,
            wind_speed,
            field_condition,
            precipitation,
            sky,
            game_length,
            attendance,
            used_dh_rule_flag,
            score_visitor,
            score_home,
            wp,
            lp,
            save_code
        )
        values 
        (
            %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s,
            %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s
        )
        returning game_id
           """
    with sql_connection.cursor() as sql_cursor:
        sql_cursor.execute(sql,
            [
                game.game_id,
                game.info_attributes["date"],
                game.info_attributes["starttime"],
                game.info_attributes["number"],
                game.info_attributes["visteam"],
                game.info_attributes["hometeam"],
                game.info_attributes["site"],
                game.info_attributes["daynight"] == "night",
                game.info_attributes["umphome"],
                game.info_attributes["ump1b"],
                game.info_attributes["ump2b"],
                game.info_attributes["ump3b"],
                get_optional_value(game.info_attributes, "oscorer"),
                game.info_attributes["temp"],
                game.info_attributes["winddir"],
                game.info_attributes["windspeed"],
                game.info_attributes["fieldcond"],
                game.info_attributes["precip"],
                game.info_attributes["sky"],
                game.info_attributes["timeofgame"],
                game.info_attributes["attendance"],
                game.info_attributes["usedh"],
                score_visitor,
                score_home,
                game.info_attributes["wp"],
                game.info_attributes["lp"],
                game.info_attributes["save"]
            ]
        )
        game_id_in_db = sql_cursor.fetchone()[0]
        return game_id_in_db

def save_game_starter(sql_connection, game_id_in_db, starter):
    """ Save the Game Starters.
    
        sql_connection - sql connection to use for transaction
        game_id_in_db - associated game id
        data - game data record
    """
    logger.debug("Saving Game Starter!  ID=%s, Starter=%s", game_id_in_db, starter)

    # Save Game Starter
    sql = """
        insert into game_starter
        (
            game_id, player_code, player_name, home_team_flag, batting_order, fielding_position
        )
        values 
        (
            %s, %s, %s, %s, %s, %s
        )
           """
    with sql_connection.cursor() as sql_cursor:
        sql_cursor.execute(sql,
            [
                game_id_in_db,
                starter.player_code,
                starter.player_name,
                starter.home_team_flag,
                starter.batting_order,
                starter.fielding_position
            ]
        )


def save_game_data(sql_connection, game_id_in_db, data):
    """ Save the Game Data Entry.
    
        sql_connection - sql connection to use for transaction
        game_id_in_db - game id
        data - game data record
    """
    logger.debug("Saving Data Record!  ID=%s, Type=%s", game_id_in_db, data.data_type)

    # Save Data
    sql = """
        insert into game_data 
        (
            game_id, data_type, pitcher_player_code, quantity
        )
        values 
        (
            %s, %s, %s, %s
        )
           """
    with sql_connection.cursor() as sql_cursor:
        sql_cursor.execute(sql,
            [
                game_id_in_db,
                data.data_type,
                data.pitcher_player_code,
                data.quantity
            ]
        )


def save_game_play(sql_connection, game_id_in_db, index):
    """ Save the Game Play record.
    
        sql_connection - sql connection to use for transaction
        game_id_in_db - associated game id
        index - game play index
    """
    logger.debug("Saving Game Play!  ID=%s, Index=%s", game_id_in_db, index)

    # Save Game Play
    sql = """
        insert into game_play
        (
            game_id, play_index
        )
        values 
        (
            %s, %s
        )
           """
    with sql_connection.cursor() as sql_cursor:
        sql_cursor.execute(sql,
            [
                game_id_in_db,
                index
            ]
        )


# pylint: disable=too-many-arguments
def save_batter_event(sql_cursor, game_id_in_db, play_index):
    """ Save the provided batter event.
    
        sql_cursor - cursor to use for tx
        game_id_in_db - baseball game id
        play_index - game play index
        basic_play - core play details
        modifiers - list of modifiers attached to the basic play
        advance - runner advancement details
    """
    logger.debug("Saving Batter Fielding Events!  ID=%s, PlayIndex=%s", game_id_in_db, play_index)
    sql = """
            insert into game_play_atbat_field_event (game_id, play_index)
            values(%s, %s)
          """
    sql_cursor.execute(sql,
        [
            game_id_in_db,
            play_index
        ]
    )


def save_pitches(sql_cursor, game_id_in_db, play_index, pitches):
    """ Save the pitch strings.  
    
        sql_cursor - sql cursor to use for tx
        game_id_in_db - associated game id
        play_index - game play index
        pitches - pitches string
    """
    logger.debug("Saving At Bat Pitch Events!  ID=%s, PlayIndex=%s, Pitches=%s",
                     game_id_in_db, play_index, pitches)
    sql = """
            insert into game_play_atbat_pitch (game_id, play_index, pitch_index, pitch_type_cd)
            values(%s, %s, %s, %s)
          """

    pitch_index = 0
    for pitch_type_cd in pitches:
        pitch_index += 1
        logger.debug("Saving At Bat Pitch!  ID=%s, PlayIndex=%s, Pitches=%s, Pitch=%s",
                     game_id_in_db, play_index, pitches, pitch_type_cd)
        sql_cursor.execute(sql,
            [
                game_id_in_db,
                play_index,
                pitch_index,
                pitch_type_cd
            ]
        )

# pylint: disable=protected-access
def save_game_play_atbat(sql_connection, game_id_in_db, index, atbat):
    """ Save the Game Play record.
    
        sql_connection - sql connection to use for transaction
        game_id_in_db - associated game id
        index - game play index
        atbat - at bat record
    """
    logger.debug("Saving At Bat!  ID=%s, Index=%s, AtBat=%s", game_id_in_db, index, atbat)

    # retrieve runners
    runner_1b = None
    r = atbat.game_state.get_runner_on_base("1")
    if r is not None and not r.is_out:
        runner_1b = r.player_code
    runner_2b = None
    r = atbat.game_state.get_runner_on_base("2")
    if r is not None and not r.is_out:
        runner_2b = r.player_code
    runner_3b = None
    r = atbat.game_state.get_runner_on_base("3")
    if r is not None and not r.is_out:
        runner_3b = r.player_code

    # Save Game Play
    sql = """
        insert into game_play_atbat
        (
            game_id, play_index, inning, home_team_flag, player_code, count,
            outs, runner_1b, runner_2b, runner_3b, score_home, score_visitor,
            pitcher, primary_play_type_cd
        )
        values 
        (
            %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s
        )
           """
    with sql_connection.cursor() as sql_cursor:
        sql_cursor.execute(sql,
            [
                game_id_in_db,
                index,
                atbat.game_state._inning,
                atbat.game_state._top_of_inning_flag,
                atbat.player_code,
                atbat.count,
                atbat.game_state._outs,
                runner_1b,
                runner_2b,
                runner_3b,
                atbat.game_state._score_home,
                atbat.game_state._score_visitor,
                atbat.pitcher,
                atbat.primary_play_type_cd
            ]
        )
        save_pitches(sql_cursor, game_id_in_db, index, atbat.pitches)
        save_batter_event(sql_cursor, game_id_in_db, index)


def save_game_play_sub(sql_connection, game_id_in_db, index, sub):
    """ Save the Game Play record.
    
        sql_connection - sql connection to use for transaction
        game_id_in_db - associated game id
        index - game play index
        sub - substitution record
    """
    logger.debug("Saving Substitution!  ID=%s, Index=%s, Sub=%s", game_id_in_db, index, sub)

    # TODO Fix issue causing empty player to values
    player_to = sub.player_to
    if player_to is None:
        player_to = "UNKNOWN"

    # Save Game Play
    sql = """
        insert into game_play_sub
        (
            game_id,
            play_index,
            player_from,
            player_to,
            players_team_home_flag,
            batting_order, 
            fielding_position
        )
        values 
        (
            %s, %s, %s, %s, %s, %s, %s
        )
           """
    with sql_connection.cursor() as sql_cursor:
        sql_cursor.execute(sql,
            [
                game_id_in_db,
                index,
                sub.player_from,
                player_to, #TODO sub.player_to,
                sub.players_team_home_flag,
                sub.batting_order,
                sub.fielding_position
            ]
        )


def save_game(sql_connection, game):
    """ Save the provided game chunk to the database.
    
        sql_connection - sql connection to use for tx
        game - game to save 
    """
    logger.info("Saving Game Record!  ID=%s", game.game_id)
    try:
        game_id_in_db = save_game_base_record(sql_connection, game)
        logger.info("Game ID in Database: %s", game_id_in_db)
        for starter in game.starters:
            save_game_starter(sql_connection, game_id_in_db, starter)
        for data in game.data:
            save_game_data(sql_connection, game_id_in_db, data)
        game_play_index = 0
        for game_play in game.game_plays:
            game_play_index += 1
            save_game_play(sql_connection, game_id_in_db, game_play_index)
            if isinstance(game_play, GameAtBat):
                save_game_play_atbat(sql_connection, game_id_in_db, game_play_index, game_play)
            elif isinstance(game_play, GameSubstitution):
                save_game_play_sub(sql_connection, game_id_in_db, game_play_index, game_play)
            else:
                logger.error("Unknown game play type.  Type=%s", type(game_play))
                raise ValueError("Unknown game play record type.")
    except psycopg.Error as e:
        logger.error("Unable to save Record due to SQL error (%s):  Object=<%s>", e, str(game))
        raise e
