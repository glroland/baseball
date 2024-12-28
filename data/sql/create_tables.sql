create table temp_load
(
    col0 varchar(250),
    col1 varchar(250),
    col2 varchar(250),
    col3 varchar(250),
    col4 varchar(250),
    col5 varchar(250),
    col6 varchar(250),
    col7 varchar(250),
    col8 varchar(250),
    col9 varchar(250),
    col10 varchar(250),
    col11 varchar(250),
    col12 varchar(250),
    col13 varchar(250),
    col14 varchar(250),
    col15 varchar(250)
);

create table field_pos
(
    field_pos_cd varchar(2) not null,
    field_pos_num int,
    field_pos_desc varchar(100) not null,

    unique (field_pos_num),

    constraint pk_field_pos primary key (field_pos_cd)
);

insert into field_pos (field_pos_cd, field_pos_num, field_pos_desc) values ('P', 1, 'Pitcher');
insert into field_pos (field_pos_cd, field_pos_num, field_pos_desc) values ('C', 2, 'Catcher');
insert into field_pos (field_pos_cd, field_pos_num, field_pos_desc) values ('1B', 3, 'First Base');
insert into field_pos (field_pos_cd, field_pos_num, field_pos_desc) values ('2B', 4, 'Second Base');
insert into field_pos (field_pos_cd, field_pos_num, field_pos_desc) values ('3B', 5, 'Third Base');
insert into field_pos (field_pos_cd, field_pos_num, field_pos_desc) values ('SS', 6, 'Shortstop');
insert into field_pos (field_pos_cd, field_pos_num, field_pos_desc) values ('LF', 7, 'Left Field');
insert into field_pos (field_pos_cd, field_pos_num, field_pos_desc) values ('CF', 8, 'Center Field');
insert into field_pos (field_pos_cd, field_pos_num, field_pos_desc) values ('RF', 9, 'Right Field');
-- TODO - What is the X Player Code in the Retrosheet data file?
insert into field_pos (field_pos_cd, field_pos_num, field_pos_desc) values ('X', null, 'UNKNOWN (???)');
-- TODO - Not confident that 12 is PR
insert into field_pos (field_pos_cd, field_pos_num, field_pos_desc) values ('PR', 12, 'Pinch Runner');
insert into field_pos (field_pos_cd, field_pos_num, field_pos_desc) values ('IF', null, 'Infield');
-- TODO - Not confident that 10 is DH
insert into field_pos (field_pos_cd, field_pos_num, field_pos_desc) values ('DH', 10, 'Designated Hitter');
insert into field_pos (field_pos_cd, field_pos_num, field_pos_desc) values ('OF', null, 'Outfield');
-- TODO - What is the A Player Code in the Retrosheet data file?
insert into field_pos (field_pos_cd, field_pos_num, field_pos_desc) values ('A', null, 'UNKNOWN (ACE?)');
-- TODO - Not confident that 11 is PH
insert into field_pos (field_pos_cd, field_pos_num, field_pos_desc) values ('PH', 11, 'Pinch Hitter');
insert into field_pos (field_pos_cd, field_pos_num, field_pos_desc) values ('U', null, 'Unknown');

create table team
(
    season_year int not null,
    team_code char(3) not null,
    league varchar(2) not null,
    team_location varchar(100) not null,
    team_name varchar(100) not null,

    constraint pk_teams primary key (season_year, team_code)
);

create table roster
(
    season_year int not null,
    player_code varchar(20) not null,
    last_name varchar(100) not null,
    first_name varchar(100) not null,
    throw_hand char(1) not null,
    batting_hand char(1) not null,
    team_code char(3) not null,
    position varchar(2) not null,

    constraint pk_roster primary key (season_year, player_code, team_code, position),

    constraint field_pos
            foreign key (position) 
            references field_pos (field_pos_cd)
);

create table game
(
    game_id serial not null,
    retrosheet_id varchar(12) not null,
    game_date date not null,
    game_time time not null,
    game_number_that_day int not null,
    team_visiting varchar(3) not null,
    team_home varchar(3) not null,
    game_site varchar(25) not null,
    night_flag boolean not null,
    ump_home varchar(20) not null,
    ump_1b varchar(20) not null,
    ump_2b varchar(20) not null,
    ump_3b varchar(20) not null,
    official_scorer varchar(20),
    temperature int not null,
    wind_direction varchar(10) not null,
    wind_speed int not null,
    field_condition varchar(50),
    precipitation varchar(50),
    sky varchar(50) not null,
    game_length int not null,
    attendance int not null,
    used_dh_rule_flag boolean,
    score_visitor int not null,
    score_home int not null,

    wp varchar(20),
    lp varchar(20),
    save_code varchar(20),

    constraint pk_game 
            primary key (game_id),

    constraint unique_retrosheet_id
            unique (retrosheet_id)
);

create table game_data
(
    game_id int not null,
    data_type varchar(2) not null,
    pitcher_player_code varchar(20) not null,
    quantity int not null,

    constraint pk_game_data 
            primary key (game_id, data_type, pitcher_player_code),

    constraint fk_game
            foreign key (game_id) 
            references game (game_id)
);

create table game_starter
(
    game_id int not null,
    player_code varchar(20) not null,
    player_name varchar(200) not null,
    home_team_flag boolean not null,
    batting_order int not null,
    fielding_position int not null,

    unique (game_id, home_team_flag, batting_order),

    constraint pk_game_starter 
            primary key (game_id, player_code, fielding_position),

    constraint fk_game
            foreign key (game_id) 
            references game (game_id),

    constraint field_pos
            foreign key (fielding_position) 
            references field_pos (field_pos_num)
);

create table game_play
(
    game_play_id serial not null,
    game_id int not null,
    play_index int not null,

    check (play_index >= 1),

    constraint pk_game_play
            primary key (game_play_id),

    constraint uq_game_play
            unique (game_id, play_index),

    constraint fk_game
            foreign key (game_id) 
            references game (game_id)
);

create table play_type
(
    play_type_cd char(1) not null,
    play_type_desc varchar(200) not null,

    constraint pk_play_type
            primary key (play_type_cd)
);

insert into play_type (play_type_cd, play_type_desc) values ('K', 'Strikeout');
insert into play_type (play_type_cd, play_type_desc) values ('L', 'Wild Pitch');
insert into play_type (play_type_cd, play_type_desc) values ('W', 'Walk');
insert into play_type (play_type_cd, play_type_desc) values ('3', 'Triple');
insert into play_type (play_type_cd, play_type_desc) values ('2', 'Double');
insert into play_type (play_type_cd, play_type_desc) values ('1', 'Single');
insert into play_type (play_type_cd, play_type_desc) values ('0', 'Stolen Base');
insert into play_type (play_type_cd, play_type_desc) values ('H', 'Homerun');
insert into play_type (play_type_cd, play_type_desc) values ('E', 'Defensive Error');
insert into play_type (play_type_cd, play_type_desc) values ('D', 'Defensive Play');
insert into play_type (play_type_cd, play_type_desc) values ('P', 'Picked Off');
insert into play_type (play_type_cd, play_type_desc) values ('A', 'Base Runner Advance');
insert into play_type (play_type_cd, play_type_desc) values ('C', 'Fielders Choice');
insert into play_type (play_type_cd, play_type_desc) values ('X', 'Hit By Pitch');
insert into play_type (play_type_cd, play_type_desc) values ('I', 'Catcher Interference');
insert into play_type (play_type_cd, play_type_desc) values ('N', 'Defensive Indifference');
insert into play_type (play_type_cd, play_type_desc) values ('G', 'Ground Rule Double');
insert into play_type (play_type_cd, play_type_desc) values ('F', 'Fly Ball Error');
insert into play_type (play_type_cd, play_type_desc) values ('O', 'Passed Ball');
insert into play_type (play_type_cd, play_type_desc) values ('B', 'Caught Stealing');

create table game_play_atbat
(
    game_play_id int not null,
    inning int not null,
    home_team_flag boolean not null,
    player_code varchar(20) not null,
    pitcher varchar(20),
    count varchar(2) not null,
    primary_play_type_cd char(1),
    outs int not null,
    runner_1b varchar(20),
    runner_2b varchar(20),
    runner_3b varchar(20),
    score_home int not null,
    score_visitor int not null,

    constraint pk_game_play_atbat 
            primary key (game_play_id),

    constraint fk_game_play
            foreign key (game_play_id) 
            references game_play (game_play_id),

    constraint fk_play_type
            foreign key (primary_play_type_cd) 
            references play_type (play_type_cd)
);

create table game_play_sub
(
    game_play_id int not null,
    player_from varchar(20) not null,
    player_to varchar(20) not null,
    players_team_home_flag boolean not null,
    batting_order int not null,
    fielding_position int not null,

    constraint pk_game_play_sub 
            primary key (game_play_id),

    constraint fk_game_play 
            foreign key (game_play_id) 
            references game_play (game_play_id),

    constraint field_pos
            foreign key (fielding_position) 
            references field_pos (field_pos_num)
);

create table pitch_type
(
    pitch_type_cd char(1) not null,
    pitch_type_desc varchar(150) not null,
    ball_or_strike char(1),

    constraint pk_pitch_type
            primary key (pitch_type_cd)
);

insert into pitch_type (pitch_type_cd, pitch_type_desc, ball_or_strike) values ('+', 'following pickoff throw by the catcher', NULL);
insert into pitch_type (pitch_type_cd, pitch_type_desc, ball_or_strike) values ('*', 'indicates the following pitch was blocked by the catcher', NULL);
insert into pitch_type (pitch_type_cd, pitch_type_desc, ball_or_strike) values ('.', 'marker for play not involving the batter', NULL);
insert into pitch_type (pitch_type_cd, pitch_type_desc, ball_or_strike) values ('1', 'pickoff throw to first', NULL);
insert into pitch_type (pitch_type_cd, pitch_type_desc, ball_or_strike) values ('2', 'pickoff throw to second', NULL);
insert into pitch_type (pitch_type_cd, pitch_type_desc, ball_or_strike) values ('3', 'pickoff throw to third', NULL);
insert into pitch_type (pitch_type_cd, pitch_type_desc, ball_or_strike) values ('>', 'Indicates a runner going on the pitch', NULL);
insert into pitch_type (pitch_type_cd, pitch_type_desc, ball_or_strike) values ('A', 'automatic strike, usually for pitch timer violation', 'S');
insert into pitch_type (pitch_type_cd, pitch_type_desc, ball_or_strike) values ('B', 'ball', 'B');
insert into pitch_type (pitch_type_cd, pitch_type_desc, ball_or_strike) values ('C', 'called strike', 'S');
insert into pitch_type (pitch_type_cd, pitch_type_desc, ball_or_strike) values ('F', 'foul', 'S');
insert into pitch_type (pitch_type_cd, pitch_type_desc, ball_or_strike) values ('H', 'hit batter', 'B');
insert into pitch_type (pitch_type_cd, pitch_type_desc, ball_or_strike) values ('I', 'intentional ball', 'B');
insert into pitch_type (pitch_type_cd, pitch_type_desc, ball_or_strike) values ('K', 'strike (unknown type)', 'S');
insert into pitch_type (pitch_type_cd, pitch_type_desc, ball_or_strike) values ('L', 'foul bunt', 'S');
insert into pitch_type (pitch_type_cd, pitch_type_desc, ball_or_strike) values ('M', 'missed bunt attempt', 'S');
insert into pitch_type (pitch_type_cd, pitch_type_desc, ball_or_strike) values ('N', 'no pitch (on balks and interference calls)', NULL);
insert into pitch_type (pitch_type_cd, pitch_type_desc, ball_or_strike) values ('O', 'foul tip on bunt', 'S');
insert into pitch_type (pitch_type_cd, pitch_type_desc, ball_or_strike) values ('P', 'pitchout', 'B');
insert into pitch_type (pitch_type_cd, pitch_type_desc, ball_or_strike) values ('Q', 'swinging on pitchout', 'S');
insert into pitch_type (pitch_type_cd, pitch_type_desc, ball_or_strike) values ('R', 'foul ball on pitchout', 'S');
insert into pitch_type (pitch_type_cd, pitch_type_desc, ball_or_strike) values ('S', 'swinging strike', 'S');
insert into pitch_type (pitch_type_cd, pitch_type_desc, ball_or_strike) values ('T', 'foul tip', 'S');
insert into pitch_type (pitch_type_cd, pitch_type_desc, ball_or_strike) values ('U', 'unknown or missed pitch', 'B');
insert into pitch_type (pitch_type_cd, pitch_type_desc, ball_or_strike) values ('V', 'called ball because pitcher went to his mouth or automatic ball on intentional walk or pitch timer violation', 'B');
insert into pitch_type (pitch_type_cd, pitch_type_desc, ball_or_strike) values ('X', 'ball put into play by batter', 'S');
insert into pitch_type (pitch_type_cd, pitch_type_desc, ball_or_strike) values ('Y', 'ball put into play on pitchout', 'S');

create table game_play_atbat_pitch
(
    game_play_pitch_id serial not null,
    game_play_id int not null,
    pitch_index int not null,
    pitch_type_cd char(1) not null,

    check (pitch_index >= 1),

    constraint pk_game_play_atbat_pitch
            primary key (game_play_pitch_id),

    constraint uq_game_play_atbat_pitch
            unique (game_play_id, pitch_index),

    constraint fk_game_play_atbat
            foreign key (game_play_id) 
            references game_play_atbat (game_play_id),

    constraint fk_pitch_type
            foreign key (pitch_type_cd) 
            references pitch_type (pitch_type_cd)
);

create table game_play_atbat_field_event
(
    game_play_id int not null,
    
    constraint pk_game_play_atbat_field_event
            primary key (game_play_id),

    constraint fk_game_play_atbat
            foreign key (game_play_id) 
            references game_play_atbat (game_play_id)
);
