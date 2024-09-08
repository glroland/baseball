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

create table teams
(
    season_year int not null,
    team_code char(3) not null,
    league varchar(2) not null,
    team_location varchar(100) not null,
    team_name varchar(100) not null,

    constraint pk_teams primary key (season_year, team_code)
);

create table rosters
(
    season_year int not null,
    player_code varchar(20) not null,
    last_name varchar(100) not null,
    first_name varchar(100) not null,
    throw_hand char(1) not null,
    batting_hand char(1) not null,
    team_code char(3) not null,
    position varchar(5) not null,

    constraint pk_roster primary key (season_year, player_code, team_code, position)
);

create table games
(
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
    official_scorer varchar(20) not null,
    pitch_count int not null,
    temperature int not null,
    wind_direction varchar(10) not null,
    wind_speed int not null,
    field_condition varchar(50),
    precipitation varchar(50),
    sky varchar(50) not null,
    game_length int not null,
    attendance int not null,

    usedh boolean,
    wp varchar(20),
    lp varchar(20),
    save_code varchar(20)
);
