from io import StringIO
import csv
from pipelines.event_file_pipeline import EventFilePipeline

GAME = """
id,ANA200004030
version,2
info,visteam,NYA
info,hometeam,ANA
info,site,ANA01
info,date,2000/04/03
info,number,0
info,starttime,7:35PM
info,daynight,night
info,usedh,true
info,umphome,mcclt901
info,ump1b,craft901
info,ump2b,schrp901
info,ump3b,cuzzp901
info,pitches,pitches
info,oscorer,munse701
info,temp,70
info,winddir,rtol
info,windspeed,5
info,fieldcond,unknown
info,precip,unknown
info,sky,sunny
info,timeofgame,182
info,attendance,42704
info,wp,herno001
info,lp,hillk001
info,save,rivem002
start,knobc001,"Chuck Knoblauch",0,1,4
start,jeted001,"Derek Jeter",0,2,6
start,oneip001,"Paul O'Neill",0,3,9
start,willb002,"Bernie Williams",0,4,10
start,martt002,"Tino Martinez",0,5,3
start,leder001,"Ricky Ledee",0,6,8
start,posaj001,"Jorge Posada",0,7,2
start,spens001,"Shane Spencer",0,8,7
start,bross001,"Scott Brosius",0,9,5
start,herno001,"Orlando Hernandez",0,0,1
start,erstd001,"Darin Erstad",1,1,7
start,kenna001,"Adam Kennedy",1,2,4
start,vaugm001,"Mo Vaughn",1,3,3
start,salmt001,"Tim Salmon",1,4,9
start,andeg001,"Garret Anderson",1,5,8
start,glaut001,"Troy Glaus",1,6,5
start,spies001,"Scott Spiezio",1,7,10
start,molib001,"Ben Molina",1,8,2
start,disag001,"Gary DiSarcina",1,9,6
start,hillk001,"Ken Hill",1,0,1
play,1,0,knobc001,21,FSBFBFFBS,K
play,1,0,knobc001,21,FSBFBFFBS,K
play,1,0,knobc001,21,FSBFBFFBS,K
play,1,1,vaugm001,32,FSBFBFFBS,K
play,1,1,vaugm001,32,FSBFBFFBS,K
play,1,1,vaugm001,32,FSBFBFFBS,K
play,2,0,knobc001,21,FSBFBFFBS,K
play,2,0,knobc001,21,FSBFBFFBS,K
play,2,0,knobc001,21,FSBFBFFBS,K
play,2,1,vaugm001,32,FSBFBFFBS,K
play,2,1,vaugm001,32,FSBFBFFBS,K
play,2,1,vaugm001,32,FSBFBFFBS,K
play,3,0,knobc001,21,FSBFBFFBS,K
play,3,0,knobc001,21,FSBFBFFBS,K
play,3,0,knobc001,21,FSBFBFFBS,K
play,3,1,vaugm001,32,FSBFBFFBS,K
play,3,1,vaugm001,32,FSBFBFFBS,K
play,3,1,vaugm001,32,FSBFBFFBS,K
play,4,0,knobc001,21,FSBFBFFBS,K
play,4,0,knobc001,21,FSBFBFFBS,K
play,4,0,knobc001,21,FSBFBFFBS,K
play,4,1,vaugm001,32,FSBFBFFBS,K
play,4,1,vaugm001,32,FSBFBFFBS,K
play,4,1,vaugm001,32,FSBFBFFBS,K
play,5,0,knobc001,21,FSBFBFFBS,K
play,5,0,knobc001,21,FSBFBFFBS,K
play,5,0,knobc001,21,FSBFBFFBS,K
play,5,1,vaugm001,32,FSBFBFFBS,K
play,5,1,vaugm001,32,FSBFBFFBS,K
play,5,1,vaugm001,32,FSBFBFFBS,K
play,6,0,knobc001,21,FSBFBFFBS,K
play,6,0,knobc001,21,FSBFBFFBS,K
play,6,0,knobc001,21,FSBFBFFBS,K
play,6,1,vaugm001,32,FSBFBFFBS,K
play,6,1,vaugm001,32,FSBFBFFBS,K
play,6,1,vaugm001,32,FSBFBFFBS,K
play,7,0,knobc001,21,FSBFBFFBS,K
play,7,0,knobc001,21,FSBFBFFBS,K
play,7,0,knobc001,21,FSBFBFFBS,K
play,7,1,vaugm001,32,FSBFBFFBS,K
play,7,1,vaugm001,32,FSBFBFFBS,K
play,7,1,vaugm001,32,FSBFBFFBS,K
play,8,0,knobc001,21,FSBFBFFBS,K
play,8,0,knobc001,21,FSBFBFFBS,K
play,8,0,knobc001,21,FSBFBFFBS,K
play,8,1,vaugm001,32,FSBFBFFBS,K
play,8,1,vaugm001,32,FSBFBFFBS,K
play,8,1,vaugm001,32,FSBFBFFBS,K
play,9,0,knobc001,21,FSBFBFFBS,K
play,9,0,knobc001,21,FSBFBFFBS,K
play,9,0,knobc001,21,FSBFBFFBS,K
play,9,1,vaugm001,32,FSBFBFFBS,K
play,9,1,vaugm001,32,FSBFBFFBS,K
play,9,1,vaugm001,32,FSBFBFFBS,K
data,er,herno001,1
data,er,nelsj001,0
data,er,rivem002,1
data,er,hillk001,2
data,er,merck001,1
data,er,petkm001,0
"""

def test_simple_all_strikeouts_game():
    event_file_pipeline = EventFilePipeline()

    reader = csv.reader(StringIO(GAME, newline=''), delimiter=',', quotechar='"')
    rows = list(reader)
    for row in rows:
        if len(row) > 0:
            event_file_pipeline.stage_record(row)
    event_file_pipeline.execute_pipeline()

    assert len(event_file_pipeline.game_pipelines) == 1
    game_pipeline = event_file_pipeline.game_pipelines[0]
    assert game_pipeline is not None
    assert game_pipeline.game is not None
    game = game_pipeline.game
    assert game.game_id == "ANA200004030"

    score_tuple = game.get_score()
    assert score_tuple is not None
    assert len(score_tuple) == 2
    assert score_tuple[0] == 0
    assert score_tuple[1] == 0
