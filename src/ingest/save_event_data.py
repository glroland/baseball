""" Save Game Data Functions

Persists the game data hierarchy of classes to a SQL database.
"""
import logging
import psycopg
from model.game_at_bat import GameAtBat
from model.game_substitution import GameSubstitution

logger = logging.getLogger(__name__)

def save_game_base_record(sql_connection, game):
    """ Save the provided game base record to the database.
    
        sql_connection - sql connection to use for the tx
        game - game record to save 
    """
    logger.debug("Saving Base Game Record!  ID=%s", game.game_id)

    # Save Game
    sql = """
        insert into game
        (
            id,
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
            wp,
            lp,
            save_code
        )
        values 
        (
            %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s,
            %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s
        )
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
                game.info_attributes["oscorer"],
                game.info_attributes["temp"],
                game.info_attributes["winddir"],
                game.info_attributes["windspeed"],
                game.info_attributes["fieldcond"],
                game.info_attributes["precip"],
                game.info_attributes["sky"],
                game.info_attributes["timeofgame"],
                game.info_attributes["attendance"],
                game.info_attributes["usedh"],
                game.info_attributes["wp"],
                game.info_attributes["lp"],
                game.info_attributes["save"]
            ]
        )


def save_game_starter(sql_connection, game_id, starter):
    """ Save the Game Starters.
    
        sql_connection - sql connection to use for transaction
        game_id - associated game id
        data - game data record
    """
    logger.debug("Saving Game Starter!  ID=%s, Starter=%s", game_id, starter)

    # Save Game Starter
    sql = """
        insert into game_starter
        (
            id, player_code, player_name, home_team_flag, batting_order, fielding_position
        )
        values 
        (
            %s, %s, %s, %s, %s, %s
        )
           """
    with sql_connection.cursor() as sql_cursor:
        sql_cursor.execute(sql,
            [
                game_id,
                starter.player_code,
                starter.player_name,
                starter.home_team_flag,
                starter.batting_order,
                starter.fielding_position
            ]
        )


def save_game_data(sql_connection, game_id, data):
    """ Save the Game Data Entry.
    
        sql_connection - sql connection to use for transaction
        game_id - game id
        data - game data record
    """
    logger.debug("Saving Data Record!  ID=%s, Type=%s", game_id, data.data_type)

    # Save Data
    sql = """
        insert into game_data 
        (
            id, data_type, pitcher_player_code, quantity
        )
        values 
        (
            %s, %s, %s, %s
        )
           """
    with sql_connection.cursor() as sql_cursor:
        sql_cursor.execute(sql,
            [
                game_id,
                data.data_type,
                data.pitcher_player_code,
                data.quantity
            ]
        )


def save_game_play(sql_connection, game_id, index):
    """ Save the Game Play record.
    
        sql_connection - sql connection to use for transaction
        game_id - associated game id
        index - game play index
    """
    logger.debug("Saving Game Play!  ID=%s, Index=%s", game_id, index)

    # Save Game Play
    sql = """
        insert into game_play
        (
            id, play_index
        )
        values 
        (
            %s, %s
        )
           """
    with sql_connection.cursor() as sql_cursor:
        sql_cursor.execute(sql,
            [
                game_id,
                index
            ]
        )


# pylint: disable=too-many-arguments
def save_batter_event(sql_cursor, game_id, play_index):
    """ Save the provided batter event.
    
        sql_cursor - cursor to use for tx
        game_id - baseball game id
        play_index - game play index
        basic_play - core play details
        modifiers - list of modifiers attached to the basic play
        advance - runner advancement details
    """
    logger.debug("Saving Batter Fielding Events!  ID=%s, PlayIndex=%s", game_id, play_index)
    sql = """
            insert into game_play_atbat_field_event (id, play_index)
            values(%s, %s)
          """
    sql_cursor.execute(sql,
        [
            game_id,
            play_index
        ]
    )


def save_pitches(sql_cursor, game_id, play_index, pitches):
    """ Save the pitch strings.  
    
        sql_cursor - sql cursor to use for tx
        game_id - associated game id
        play_index - game play index
        pitches - pitches string
    """
    logger.debug("Saving At Bat Pitch Events!  ID=%s, PlayIndex=%s, Pitches=%s",
                     game_id, play_index, pitches)
    sql = """
            insert into game_play_atbat_pitch (id, play_index, pitch_index, pitch_type_cd)
            values(%s, %s, %s, %s)
          """

    pitch_index = 0
    for pitch_type_cd in pitches:
        pitch_index += 1
        logger.debug("Saving At Bat Pitch!  ID=%s, PlayIndex=%s, Pitches=%s, Pitch=%s",
                     game_id, play_index, pitches, pitch_type_cd)
        sql_cursor.execute(sql,
            [
                game_id,
                play_index,
                pitch_index,
                pitch_type_cd
            ]
        )


def save_game_play_atbat(sql_connection, game_id, index, atbat):
    """ Save the Game Play record.
    
        sql_connection - sql connection to use for transaction
        game_id - associated game id
        index - game play index
        atbat - at bat record
    """
    logger.debug("Saving At Bat!  ID=%s, Index=%s, AtBat=%s", game_id, index, atbat)

    # Save Game Play
    sql = """
        insert into game_play_atbat
        (
            id, play_index, inning, home_team_flag, player_code, count, pitches,
            basic_play, modifiers, advance, outs, runner_on_1b, runner_on_2b,
            runner_on_3b, score_home, score_visitor
        )
        values 
        (
            %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s
        )
           """
    with sql_connection.cursor() as sql_cursor:
        sql_cursor.execute(sql,
            [
                game_id,
                index,
                atbat.inning,
                atbat.home_team_flag,
                atbat.player_code,
                atbat.count,
                atbat.pitches,
                atbat.basic_play,
                atbat.modifiers,
                atbat.advance,
                atbat.outs,
                atbat.runner_on_1b,
                atbat.runner_on_2b,
                atbat.runner_on_3b,
                atbat.score_home,
                atbat.score_visitor
            ]
        )
        save_pitches(sql_cursor, game_id, index, atbat.pitches)
        save_batter_event(sql_cursor, game_id, index)


def save_game_play_sub(sql_connection, game_id, index, sub):
    """ Save the Game Play record.
    
        sql_connection - sql connection to use for transaction
        game_id - associated game id
        index - game play index
        sub - substitution record
    """
    logger.debug("Saving Substitution!  ID=%s, Index=%s, Sub=%s", game_id, index, sub)

    # Save Game Play
    sql = """
        insert into game_play_sub
        (
            id, play_index, player_code, player_name, home_team_flag, batting_order, fielding_position
        )
        values 
        (
            %s, %s, %s, %s, %s, %s, %s
        )
           """
    with sql_connection.cursor() as sql_cursor:
        sql_cursor.execute(sql,
            [
                game_id,
                index,
                sub.player_code,
                sub.player_name,
                sub.home_team_flag,
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
        save_game_base_record(sql_connection, game)
        for starter in game.starters:
            save_game_starter(sql_connection, game.game_id, starter)
        for data in game.data:
            save_game_data(sql_connection, game.game_id, data)
        game_play_index = 0
        for game_play in game.game_plays:
            game_play_index += 1
            save_game_play(sql_connection, game.game_id, game_play_index)
            if isinstance(game_play, GameAtBat):
                save_game_play_atbat(sql_connection, game.game_id, game_play_index, game_play)
            elif isinstance(game_play, GameSubstitution):
                save_game_play_sub(sql_connection, game.game_id, game_play_index, game_play)
            else:
                logger.error("Unknown game play type.  Type=%s", type(game_play))
                raise ValueError("Unknown game play record type.")
    except psycopg.Error as e:
        logger.error("Unable to save Record due to SQL error (%s):  Object=<%s>", e, str(game))
        raise e
