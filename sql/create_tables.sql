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
    id varchar(12) not null,
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
            primary key (id)
);

create table game_data
(
    id varchar(12) not null,
    data_type varchar(2) not null,
    pitcher_player_code varchar(20) not null,
    quantity int not null,

    constraint pk_game_data 
            primary key (id, data_type, pitcher_player_code),

    constraint fk_game
            foreign key (id) 
            references game (id)
);

create table game_starter
(
    id varchar(12) not null,
    player_code varchar(20) not null,
    player_name varchar(200) not null,
    home_team_flag boolean not null,
    batting_order int not null,
    fielding_position int not null,

    unique (id, home_team_flag, batting_order),

    constraint pk_game_starter 
            primary key (id, player_code),

    constraint fk_game
            foreign key (id) 
            references game (id),

    constraint field_pos
            foreign key (fielding_position) 
            references field_pos (field_pos_num)
);

create table game_play
(
    id varchar(12) not null,
    play_index int not null,

    check (play_index >= 1),

    constraint pk_game_play
            primary key (id, play_index),

    constraint fk_game
            foreign key (id) 
            references game (id)
);

create table game_play_atbat
(
    id varchar(12) not null,
    play_index int not null,
    inning int not null,
    home_team_flag boolean not null,
    player_code varchar(20) not null,
    count varchar(2) not null,
    pitches varchar(100) not null,
    full_action_str varchar(100) not null,
    outs int not null,
    runner_1b varchar(20),
    runner_2b varchar(20),
    runner_3b varchar(20),
    score_home int not null,
    score_visitor int not null,

    constraint pk_game_play_atbat 
            primary key (id, play_index),

    constraint fk_game_play
            foreign key (id, play_index) 
            references game_play (id, play_index)
);

create table game_play_sub
(
    id varchar(12) not null,
    play_index int not null,
    player_from varchar(20) not null,
    player_to varchar(20) not null,
    players_team_home_flag boolean not null,
    batting_order int not null,
    fielding_position int not null,

    constraint pk_game_play_sub 
            primary key (id, play_index),

    constraint fk_game_play 
            foreign key (id, play_index) 
            references game_play (id, play_index),

    constraint field_pos
            foreign key (fielding_position) 
            references field_pos (field_pos_num)
);

create table pitch_type
(
    pitch_type_cd char(1) not null,
    pitch_type_desc varchar(150) not null,

    constraint pk_pitch_type
            primary key (pitch_type_cd)
);

insert into pitch_type (pitch_type_cd, pitch_type_desc) values ('+', 'following pickoff throw by the catcher');
insert into pitch_type (pitch_type_cd, pitch_type_desc) values ('*', 'indicates the following pitch was blocked by the catcher');
insert into pitch_type (pitch_type_cd, pitch_type_desc) values ('.', 'marker for play not involving the batter');
insert into pitch_type (pitch_type_cd, pitch_type_desc) values ('1', 'pickoff throw to first');
insert into pitch_type (pitch_type_cd, pitch_type_desc) values ('2', 'pickoff throw to second');
insert into pitch_type (pitch_type_cd, pitch_type_desc) values ('3', 'pickoff throw to third');
insert into pitch_type (pitch_type_cd, pitch_type_desc) values ('>', 'Indicates a runner going on the pitch');
insert into pitch_type (pitch_type_cd, pitch_type_desc) values ('A', 'automatic strike, usually for pitch timer violation');
insert into pitch_type (pitch_type_cd, pitch_type_desc) values ('B', 'ball');
insert into pitch_type (pitch_type_cd, pitch_type_desc) values ('C', 'called strike');
insert into pitch_type (pitch_type_cd, pitch_type_desc) values ('F', 'foul');
insert into pitch_type (pitch_type_cd, pitch_type_desc) values ('H', 'hit batter');
insert into pitch_type (pitch_type_cd, pitch_type_desc) values ('I', 'intentional ball');
insert into pitch_type (pitch_type_cd, pitch_type_desc) values ('K', 'strike (unknown type)');
insert into pitch_type (pitch_type_cd, pitch_type_desc) values ('L', 'foul bunt');
insert into pitch_type (pitch_type_cd, pitch_type_desc) values ('M', 'missed bunt attempt');
insert into pitch_type (pitch_type_cd, pitch_type_desc) values ('N', 'no pitch (on balks and interference calls)');
insert into pitch_type (pitch_type_cd, pitch_type_desc) values ('O', 'foul tip on bunt');
insert into pitch_type (pitch_type_cd, pitch_type_desc) values ('P', 'pitchout');
insert into pitch_type (pitch_type_cd, pitch_type_desc) values ('Q', 'swinging on pitchout');
insert into pitch_type (pitch_type_cd, pitch_type_desc) values ('R', 'foul ball on pitchout');
insert into pitch_type (pitch_type_cd, pitch_type_desc) values ('S', 'swinging strike');
insert into pitch_type (pitch_type_cd, pitch_type_desc) values ('T', 'foul tip');
insert into pitch_type (pitch_type_cd, pitch_type_desc) values ('U', 'unknown or missed pitch');
insert into pitch_type (pitch_type_cd, pitch_type_desc) values ('V', 'called ball because pitcher went to his mouth or automatic ball on intentional walk or pitch timer violation');
insert into pitch_type (pitch_type_cd, pitch_type_desc) values ('X', 'ball put into play by batter');
insert into pitch_type (pitch_type_cd, pitch_type_desc) values ('Y', 'ball put into play on pitchout');

create table game_play_atbat_pitch
(
    id varchar(12) not null,
    play_index int not null,
    pitch_index int not null,
    pitch_type_cd char(1) not null,

    check (pitch_index >= 1),

    constraint pk_game_play_atbat_pitch
            primary key (id, play_index, pitch_index),

    constraint fk_game_play_atbat
            foreign key (id, play_index) 
            references game_play_atbat (id, play_index),

    constraint fk_pitch_type
            foreign key (pitch_type_cd) 
            references pitch_type (pitch_type_cd)
);

create table game_play_atbat_field_event
(
    id varchar(12) not null,
    play_index int not null,
    
    constraint pk_game_play_atbat_field_event
            primary key (id, play_index),

    constraint fk_game_play_atbat
            foreign key (id, play_index) 
            references game_play_atbat (id, play_index)
);
