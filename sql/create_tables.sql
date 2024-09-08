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

    constraint pk_roster primary key (season_year, player_code)
);
