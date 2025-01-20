-- Create Indices
create index game_date_ix on game (game_date)
create index game_play_game_id_ix on game_play (game_id)
create index game_play_atbat_pitcher_ix on game_play_atbat (pitcher)
create index game_play_atbat_play_id_ix on game_play_atbat (game_play_id)
create index game_play_atbat_pitch_play_id_ix on game_play_atbat_pitch (game_play_id)


-- Populate Pitch Count
update game_play
set pitch_count = sq.pitch_count
from (
	select game.game_id,
		   game_play.play_index,
	       game_play_atbat.pitcher,
		   game_play.game_play_id game_play_id,
		   (
				select count(*)
	         	from game_play_atbat_pitch pc_pitch, 
					 game_play_atbat pc_atbat, 
				 	 game_play pc_gameplay, 
					 pitch_type pc_pitch_type
	         	where pc_pitch.game_play_id = pc_atbat.game_play_id
				  and pc_pitch.game_play_id = pc_gameplay.game_play_id
				  and pc_gameplay.game_id = game.game_id
	         	  and pc_atbat.pitcher = game_play_atbat.pitcher
	         	  and pc_pitch_type.pitch_type_cd = pc_pitch.pitch_type_cd
	         	  and pc_pitch_type.ball_or_strike is not null
	         	  and pc_gameplay.play_index < game_play.play_index
		   ) pitch_count
	from game, game_play, game_play_atbat
	where game.game_id = game_play.game_id
	  and game_play.game_play_id = game_play_atbat.game_play_id
	order by game.game_id, game_play.play_index
	 ) sq
where game_play.game_play_id = sq.game_play_id;
