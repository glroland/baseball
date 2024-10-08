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
play,1,0,knobc001,21,CBBX,S7/7S
play,1,0,jeted001,00,C,CS2(26)
play,1,0,jeted001,22,CSBBX,63/G
play,1,0,oneip001,32,BBBCFB,W
play,1,0,willb002,21,CBBX,46(1)/FO
play,1,1,erstd001,21,BCBX,S7
play,1,1,kenna001,11,SBX,3(B)3(1)/LDP
play,1,1,vaugm001,32,FSBFBFFBS,K
play,2,0,martt002,31,BCBBX,43/G
play,2,0,leder001,31,BBBCX,53/G
play,2,0,posaj001,32,BBBCCFFB,W
play,2,0,spens001,22,BFBCFX,53/G
play,2,1,salmt001,00,X,HR/7
play,2,1,andeg001,00,X,7/L7
play,2,1,glaut001,31,BBFBX,S9
play,2,1,spies001,10,BS,CS2(26)
play,2,1,spies001,32,BSSBBB,W
play,2,1,molib001,12,CFBX,54(1)/FO
play,3,0,bross001,22,BCBCX,63/G
play,3,0,knobc001,11,BCX,3/FL
play,3,0,jeted001,32,CFBBBX,13/G
play,3,1,disag001,00,X,63/G
play,3,1,erstd001,02,CCX,7/F7
play,3,1,kenna001,22,CBBCFFX,D9
play,3,1,vaugm001,32,BBCFBS,K
play,4,0,oneip001,20,BBX,S9
play,4,0,willb002,10,BX,7/F7
play,4,0,martt002,02,CSB,CS2(26)
play,4,0,martt002,12,CSBS,K
play,4,1,salmt001,10,BX,63/G
play,4,1,andeg001,02,SFX,43/G
play,4,1,glaut001,11,BFX,9/F9
play,5,0,leder001,31,SBBBX,43/G
play,5,0,posaj001,12,FCBC,K/C
play,5,0,spens001,31,FBBBX,E3/TH
play,5,0,bross001,32,BBBCCB,W.1-2
play,5,0,knobc001,20,BBX,31/G
play,5,1,spies001,12,BCFX,S
play,5,1,molib001,10,BX,6/P6
play,5,1,disag001,20,BBX,S8.1-2
play,5,1,erstd001,21,BSBX,S7/7S.2-3;1-2
play,5,1,kenna001,11,BFX,5/P5
play,5,1,vaugm001,22,FBSBS,K
play,6,0,jeted001,12,SFBX,S
play,6,0,oneip001,10,BX,HR/8.1-H
play,6,0,willb002,22,BSBCX,63/G
play,6,0,martt002,00,,NP
sub,merck001,"Kent Mercker",1,0,1
play,6,0,martt002,01,CX,S9
play,6,0,leder001,22,BFCFBX,53/G.1-2
play,6,0,posaj001,31,BBCBX,9/F9
play,6,1,salmt001,22,CBBFS,K
play,6,1,andeg001,11,BFX,3/G
play,6,1,glaut001,30,BBBB,W
play,6,1,spies001,31,BBBCB,W.1-2
play,6,1,molib001,02,CFX,4/P4
play,7,0,spens001,20,BBX,HR/9
play,7,0,bross001,31,BBBCX,7/F7
play,7,0,knobc001,01,CX,4/FL
play,7,0,jeted001,00,X,8/F8D
play,7,1,disag001,01,CX,8/F8
play,7,1,erstd001,11,CBX,S8
play,7,1,kenna001,00,X,7/L7
play,7,1,vaugm001,32,BBCBSX,3/G
play,8,0,oneip001,10,BX,43/G
play,8,0,willb002,12,FBCS,K
play,8,0,martt002,10,BX,7/F7D
play,8,1,salmt001,00,,NP
sub,nelsj001,"Jeff Nelson",0,0,1
play,8,1,salmt001,10,BX,9/F9
play,8,1,andeg001,32,BCBFBFS,K
play,8,1,glaut001,31,BBBCB,W
play,8,1,spies001,11,CBX,7/F7D
play,9,0,leder001,00,,NP
sub,petkm001,"Mark Petkovsek",1,0,1
play,9,0,leder001,32,SCBBFBFX,31/G
play,9,0,posaj001,00,X,3/G
play,9,0,spens001,31,FBBBX,53/G
play,9,1,molib001,00,,NP
sub,leder001,"Ricky Ledee",0,6,7
play,9,1,molib001,00,,NP
sub,kellb002,"Roberto Kelly",0,8,8
play,9,1,molib001,00,,NP
sub,palmo001,"Orlando Palmeiro",1,8,11
play,9,1,palmo001,00,,NP
sub,rivem002,"Mariano Rivera",0,0,1
play,9,1,palmo001,12,BCFS,K
play,9,1,disag001,22,BBCFX,S9
play,9,1,erstd001,30,BBBB,W.1-2
play,9,1,kenna001,01,SX,9/F9
play,9,1,vaugm001,00,X,S8.2-H;1-2
play,9,1,salmt001,00,,NP
sub,cleme001,"Edgard Clemente",1,3,12
play,9,1,salmt001,02,SSX,9/F9
data,er,herno001,1
data,er,nelsj001,0
data,er,rivem002,1
data,er,hillk001,2
data,er,merck001,1
data,er,petkm001,0
"""

def test_valid_game():
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
    assert score_tuple[0] == 3
    assert score_tuple[1] == 2
