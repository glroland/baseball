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
