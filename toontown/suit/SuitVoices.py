from toontown.suit import SuitDNA
from toontown.battle import SuitBattleGlobals
from toontown.nametag import NametagGlobals
from panda3d.core import TransparencyAttrib
from toontown.nametag import NametagGroup

SuitDialogArray = []
SkelSuitDialogArray = []
SkelecogDialogFemaleArray = []
PrethinkerDialogArray = []
PacesetterDialogArray = []
AmbassadorDialogArray = []
CLODialogArray = []
FirestarterDialogArray = []
LitigatorDialogArray = []
CaseManagerDialogArray = []
ScapegoatDialogArray = []
MajorPlayerDialogArray = []
DuckShufflerDialogArray = []
PlutocratDialogArray = []
WitchHunterDialogArray = []
RainmakerDialogArray = []
ChairmanDialogArray = []
OttomanDialogArray = []
CEODialogArray = []
ChainsawDialogArray = []
DOLADialogArray = []
DOPADialogArray = []
DOLDDialogArray = []
DOLDSkeleDialogArray = []
DOPRDialogArray = []
DerrickHandDialogArray = []
DerrickSkeleDialogArray = []
DerrickManDialogArray = []
HonchoDialogArray = []
MultislackerDialogArray = []
BellringerDialogArray = []
CountErfitDialogArray = []
CountErclaimDialogArray = []
FeatherbedderDialogArray = []
DeepDiverDialogArray =[]
GatekeeperDialogArray = []
MouthpieceDialogArray = []
ReddDialogArray = []
DeskJockeyDialogArray = []
ChainsawORDialogArray = []
SkelecogDialogArray = []
HighRollerDialogArray = []
StenographerDialogArray = []
FemaleDialogArray = []
TreekillerDialogArray = []
HonchoDialogFiles = ['COG_VO_grunt_honcho',
        'COG_VO_murmur_honcho',
        'COG_VO_statement_honcho',
        'COG_VO_question_honcho',
        'COG_VO_grunt_honcho']
PrethinkerDialogFiles = ['ttcc_ene_prethink_grunt',
        'ttcc_ene_prethink_murmur',
        'ttcc_ene_prethink_statement',
        'ttcc_ene_prethink_question',
        'ttcc_ene_prethink_grunt']
AmbassadorDialogFiles = ['ttcc_ene_ambass_grunt',
        'ttcc_ene_ambass_murmur',
        'ttcc_ene_ambass_statement',
        'ttcc_ene_ambass_question',
        'ttcc_ene_ambass_grunt']
PacesetterDialogFiles = ['ttcc_ene_psetter_grunt',
        'ttcc_ene_psetter_murmur',
        'ttcc_ene_psetter_statement',
        'ttcc_ene_psetter_question',
        'ttcc_ene_psetter_grunt']
HighRollerDialogFiles = ['ttcc_ene_hroller_grunt',
        'ttcc_ene_hroller_murmur',
        'ttcc_ene_hroller_statement',
        'ttcc_ene_hroller_question',
        'ttcc_ene_hroller_grunt']
CLODialogFiles = ['ttcc_ene_clo_grunt',
        'ttcc_ene_clo_murmur',
        'ttcc_ene_clo_statement',
        'ttcc_ene_clo_question',
        'ttcc_ene_clo_grunt']
FirestarterDialogFiles = ['ttcc_ene_fires_grunt',
        'ttcc_ene_fires_murmur',
        'ttcc_ene_fires_statement',
        'ttcc_ene_fires_question',
        'ttcc_ene_fires_grunt']
LitigatorDialogFiles = ['ttcc_ene_lgator_grunt',
        'ttcc_ene_lgator_murmur',
        'ttcc_ene_lgator_statement',
        'ttcc_ene_lgator_question',
        'ttcc_ene_lgator_grunt']
FemaleDialogFiles = ['COG_VO_grunt_f',
        'COG_VO_murmur_f',
        'COG_VO_statement_f',
        'COG_VO_question_1_f',
        'COG_VO_grunt_f']
CaseManagerDialogFiles = ['ttcc_ene_caseman_grunt',
        'ttcc_ene_caseman_murmur',
        'ttcc_ene_caseman_statement',
        'ttcc_ene_caseman_question',
        'ttcc_ene_caseman_grunt']
ScapegoatDialogFiles = ['ttcc_ene_sgoat_grunt',
        'ttcc_ene_sgoat_murmur',
        'ttcc_ene_sgoat_statement',
        'ttcc_ene_sgoat_question',
        'ttcc_ene_sgoat_grunt']
MajorPlayerDialogFiles = ['ttcc_ene_mplayer_grunt',
        'ttcc_ene_mplayer_murmur',
        'ttcc_ene_mplayer_statement',
        'ttcc_ene_mplayer_question',
        'ttcc_ene_mplayer_grunt']
DuckShufflerDialogFiles = ['ttcc_ene_duckshfl_grunt',
        'ttcc_ene_duckshfl_murmur',
        'ttcc_ene_duckshfl_statement',
        'ttcc_ene_duckshfl_question',
        'ttcc_ene_duckshfl_grunt']
PlutocratDialogFiles = ['ttcc_ene_pcrat_grunt',
                                'ttcc_ene_pcrat_murmur',
                                'ttcc_ene_pcrat_statement',
                                'ttcc_ene_pcrat_question',
                                'ttcc_ene_pcrat_grunt']
WitchHunterDialogFiles = ['ttcc_ene_whunter_grunt',
                                'ttcc_ene_whunter_murmur',
                                'ttcc_ene_whunter_statement',
                                'ttcc_ene_whunter_question',
                                'ttcc_ene_whunter_grunt']
RainmakerDialogFiles = ['ttcc_ene_rainmake_grunt',
                                'ttcc_ene_rainmake_murmur',
                                'ttcc_ene_rainmake_statement',
                                'ttcc_ene_rainmake_question',
                                'ttcc_ene_rainmake_grunt']
StenographerDialogFiles = ['ttcc_ene_stenog_grunt',
                                'ttcc_ene_stenog_murmur',
                                'ttcc_ene_stenog_statement',
                                'ttcc_ene_stenog_question',
                                'ttcc_ene_stenog_grunt']
ChairmanDialogFiles = ['ttcc_ene_chairman_grunt',
                                'ttcc_ene_chairman_murmur',
                                'ttcc_ene_chairman_statement',
                                'ttcc_ene_chairman_question',
                                'ttcc_ene_chairman_grunt']
OttomanDialogFiles = ['ttcc_ene_ottoman_grunt',
                                'ttcc_ene_ottoman_murmur',
                                'ttcc_ene_ottoman_statement',
                                'ttcc_ene_ottoman_question',
                                'ttcc_ene_ottoman_grunt']
CEODialogFiles = ['ttcc_ene_CEO_grunt',
                                'ttcc_ene_CEO_murmur',
                                'ttcc_ene_CEO_statement',
                                'ttcc_ene_CEO_question',
                                'ttcc_ene_CEO_grunt']
ChainsawDialogFiles = ['ttcc_ene_chainsaw_grunt',
                                'ttcc_ene_chainsaw_murmur',
                                'ttcc_ene_chainsaw_statement',
                                'ttcc_ene_chainsaw_question',
                                'ttcc_ene_chainsaw_grunt']
DOLADialogFiles = ['ttcc_ene_dlao_grunt',
                                'ttcc_ene_dlao_murmur',
                                'ttcc_ene_dlao_statement',
                                'ttcc_ene_dlao_question',
                                'ttcc_ene_dlao_grunt']
DOPADialogFiles = ['ttcc_ene_dopa_grunt_skel',
                                'ttcc_ene_dopa_murmur_skel',
                                'ttcc_ene_dopa_statement_skel',
                                'ttcc_ene_dopa_question_skel',
                                'ttcc_ene_dopa_grunt_skel']
DOLDDialogFiles = ['ttcc_ene_dold_grunt',
                                'ttcc_ene_dold_murmur',
                                'ttcc_ene_dold_statement',
                                'ttcc_ene_dold_question',
                                'ttcc_ene_dold_grunt']
DOLDSkeleDialogFiles = ['ttcc_ene_dold_grunt_skel',
                                'ttcc_ene_dold_murmur_skel',
                                'ttcc_ene_dold_statement_skel',
                                'ttcc_ene_dold_question_skel',
                                'ttcc_ene_dold_grunt_skel']
TreekillerDialogFiles = ['ttcc_ene_treek_grunt',
                                'ttcc_ene_treek_murmur',
                                'ttcc_ene_treek_statement',
                                'ttcc_ene_treek_question',
                                'ttcc_ene_treek_grunt']
DOPRDialogFiles = ['ttcc_ene_DOPR_grunt_skel',
                                'ttcc_ene_DOPR_murmur_skel',
                                'ttcc_ene_DOPR_statement_skel',
                                'ttcc_ene_DOPR_question_skel',
                                'ttcc_ene_DOPR_grunt_skel']
DerrickHandDialogFiles = ['ttcc_ene_derrhand_grunt',
                                'ttcc_ene_derrhand_murmur',
                                'ttcc_ene_derrhand_statement',
                                'ttcc_ene_derrhand_question',
                                'ttcc_ene_derrhand_grunt']
DerrickSkeleDialogFiles = ['ttcc_ene_derrhand_grunt_skel',
                                'ttcc_ene_derrhand_murmur_skel',
                                'ttcc_ene_derrhand_statement_skel',
                                'ttcc_ene_derrhand_question_skel',
                                'ttcc_ene_derrhand_grunt_skel']
DerrickManDialogFiles = ['ttcc_ene_derrman_grunt',
                                'ttcc_ene_derrman_murmur',
                                'ttcc_ene_derrman_statement',
                                'ttcc_ene_derrman_question',
                                'ttcc_ene_derrman_grunt']
MultislackerDialogFiles = ['ttcc_ene_mslacker_grunt',
                                'ttcc_ene_mslacker_murmur',
                                'ttcc_ene_mslacker_statement',
                                'ttcc_ene_mslacker_question',
                                'ttcc_ene_mslacker_grunt']
BellringerDialogFiles = ['ttcc_ene_bellring_grunt',
                                'ttcc_ene_bellring_murmur',
                                'ttcc_ene_bellring_statement',
                                'ttcc_ene_bellring_question',
                                'ttcc_ene_bellring_grunt']
CountErclaimDialogFiles = ['ttcc_ene_erclaim_grunt',
                                'ttcc_ene_erclaim_murmur',
                                'ttcc_ene_erclaim_statement',
                                'ttcc_ene_erclaim_question',
                                'ttcc_ene_erclaim_grunt']
CountErfitDialogFiles = ['ttcc_ene_erfit_grunt',
                                'ttcc_ene_erfit_murmur',
                                'ttcc_ene_erfit_statement',
                                'ttcc_ene_erfit_question',
                                'ttcc_ene_erfit_grunt']
FeatherbedderDialogFiles = ['ttcc_ene_fbed_grunt',
                                'ttcc_ene_fbed_murmur',
                                'ttcc_ene_fbed_statement',
                                'ttcc_ene_fbed_question',
                                'ttcc_ene_fbed_grunt']
DeepDiverDialogFiles = ['ttcc_ene_ddiver_grunt',
                                'ttcc_ene_ddiver_murmur',
                                'ttcc_ene_ddiver_statement',
                                'ttcc_ene_ddiver_question',
                                'ttcc_ene_ddiver_grunt']
GatekeeperDialogFiles = ['ttcc_ene_gatekeep_grunt',
                                'ttcc_ene_gatekeep_murmur',
                                'ttcc_ene_gatekeep_statement',
                                'ttcc_ene_gatekeep_question',
                                'ttcc_ene_gatekeep_grunt']
ChainsawORDialogFiles = ['ttcc_ene_chainsaw_grunt_or',
                                'ttcc_ene_chainsaw_murmur_or',
                                'ttcc_ene_chainsaw_statement_or',
                                'ttcc_ene_chainsaw_question_or',
                                'ttcc_ene_chainsaw_grunt_or']
ReddDialogFiles = ['REDD_grunt',
                                    'REDD_murmur',
                                    'REDD_VO_statement',
                                    'REDD_VO_question',
                                    'REDD_grunt']
SkelecogDialogFiles = ['COG_VO_grunt_skel',
        'COG_VO_murmur_skel',
        'COG_VO_statement_skel',
        'COG_VO_question_skel',
        'COG_VO_grunt_skel']
SkelSuitDialogFiles  = ['COG_VO_grunt_skel',
        'COG_VO_murmur_skel',
        'COG_VO_statement_skel',
        'COG_VO_question_skel',
        'COG_VO_grunt_skel']
DeskJockeyDialogFiles = ['ttcc_ene_djockey_grunt',
        'ttcc_ene_djockey_murmur',
        'ttcc_ene_djockey_statement',
        'ttcc_ene_djockey_question',
        'ttcc_ene_djockey_grunt']
MouthpieceDialogFiles = ['ttcc_ene_mouthp_grunt',
        'ttcc_ene_mouthp_murmur',
        'ttcc_ene_mouthp_statement',
        'ttcc_ene_mouthp_question',
        'ttcc_ene_mouthp_grunt']
SkelecogDialogFemaleFiles = ['COG_VO_grunt_skel_f',
        'COG_VO_murmur_skel_f',
        'COG_VO_statement_skel_f',
        'COG_VO_question_skel_f',
        'COG_VO_grunt_skel_f']
SuitDialogFiles = ['COG_VO_grunt',
        'COG_VO_murmur',
        'COG_VO_statement',
        'COG_VO_question',
        'COG_VO_grunt']

def unloadDialog(level=0):
    arrays = (
        SuitDialogArray,
        PrethinkerDialogArray,
        PacesetterDialogArray,
        AmbassadorDialogArray,
        CLODialogArray,
        FirestarterDialogArray,
        LitigatorDialogArray,
        CaseManagerDialogArray,
        ScapegoatDialogArray,
        MajorPlayerDialogArray,
        DuckShufflerDialogArray,
        PlutocratDialogArray,
        WitchHunterDialogArray,
        RainmakerDialogArray,
        ChairmanDialogArray,
        OttomanDialogArray,
        CEODialogArray,
        ChainsawDialogArray,
        DOLADialogArray,
        DOPADialogArray,
        DOLDDialogArray,
        DOLDSkeleDialogArray,
        DOPRDialogArray,
        DerrickHandDialogArray,
        DerrickSkeleDialogArray,
        DerrickManDialogArray,
        HonchoDialogArray,
        MultislackerDialogArray,
        BellringerDialogArray,
        CountErfitDialogArray,
        CountErclaimDialogArray,
        FeatherbedderDialogArray,
        DeepDiverDialogArray,
        GatekeeperDialogArray,
        MouthpieceDialogArray,
        ReddDialogArray,
        DeskJockeyDialogArray,
        ChainsawORDialogArray,
        SkelecogDialogArray,
        SkelecogDialogFemaleArray,
        SkelSuitDialogArray,
        HighRollerDialogArray,
        StenographerDialogArray,
        FemaleDialogArray,
        TreekillerDialogArray
    )

    for array in arrays:
        del array[:]

def loadSkelDialog():
    return loadDialogArray(
        SkelSuitDialogArray,
        SkelSuitDialogFiles,
        'phase_5/audio/sfx/'
    )


def unloadSkelDialog():
    del SkelSuitDialogArray[:]

def loadDialog(level=0):
    return loadDialogArray(
        SuitDialogArray,
        SuitDialogFiles
    )

def loadDialogArray(dialogArray, files,
                    loadPath='phase_3.5/audio/dial/'):

    if dialogArray:
        return dialogArray

    for filename in files:
        sound = base.loader.loadSfx(
            loadPath + filename + '.ogg'
        )

        if sound:
            dialogArray.append(sound)

    return dialogArray


def getDialogueArray(suit):
    if suit.style.name == 'derrman' and not suit.isSkeleton:
        return loadDialogArray(DerrickManDialogArray, DerrickManDialogFiles)
    elif suit.style.name in ['fmaker', 'choreo', 'cinema'] and not suit.isSkeleton:
        return loadDialogArray(HonchoDialogArray, HonchoDialogFiles)
    elif suit.style.name == 'derrhand' and not suit.isSkeleton:
        return loadDialogArray(DerrickHandDialogArray, DerrickHandDialogFiles)
    elif suit.style.name == 'derrhand' and suit.isSkeleton:
        return loadDialogArray(DerrickSkeleDialogArray, DerrickSkeleDialogFiles)
    elif suit.style.name == 'fires' and not suit.isSkeleton:
        return loadDialogArray(FirestarterDialogArray, FirestarterDialogFiles)
    elif suit.style.name == 'fbed' and not suit.isSkeleton:
        return loadDialogArray(FeatherbedderDialogArray, FeatherbedderDialogFiles)
    elif suit.style.name == 'mplayer' and not suit.isSkeleton:
        return loadDialogArray(MajorPlayerDialogArray, MajorPlayerDialogFiles)
    elif suit.style.name == 'director' and not suit.isSkeleton:
        return loadDialogArray(MajorPlayerDialogArray, MajorPlayerDialogFiles)
    elif suit.style.name == 'chainsaw' and not suit.isSkeleton:
        return loadDialogArray(ChainsawDialogArray, ChainsawDialogFiles)
    elif suit.style.name == 'chainsaw2' and not suit.isSkeleton:
        return loadDialogArray(ChainsawORDialogArray, ChainsawORDialogFiles)
    elif suit.style.name == 'phouse' and not suit.isSkeleton:
        return loadDialogArray(DerrickSkeleDialogArray, DerrickSkeleDialogFiles)
    elif suit.style.name == 'bkeeper' and not suit.isSkeleton:
        return loadDialogArray(CaseManagerDialogArray, CaseManagerDialogFiles)
    elif suit.style.name == 'wtapper' and not suit.isSkeleton:
        return loadDialogArray(StenographerDialogArray, StenographerDialogFiles)
    elif suit.style.name == 'djockey' and not suit.isSkeleton:
        return loadDialogArray(DeskJockeyDialogArray, DeskJockeyDialogFiles)
    elif suit.style.name == 'ptjockey' and not suit.isSkeleton:
        return loadDialogArray(DeskJockeyDialogArray, DeskJockeyDialogFiles)
    elif suit.style.name == 'rkeeper' and not suit.isSkeleton:
        return loadDialogArray(StenographerDialogArray, StenographerDialogFiles)
    elif suit.style.name == 'liquid' and not suit.isSkeleton:
        return loadDialogArray(BellringerDialogArray, BellringerDialogFiles)
    elif suit.style.name == 'cdirector':
        return loadDialogArray(ChainsawORDialogArray, ChainsawORDialogFiles)
    elif suit.style.name == 'cbutcher' and not suit.isSkeleton:
        return loadDialogArray(StenographerDialogArray, StenographerDialogFiles)
    elif suit.style.name == 'ambass':
        return loadDialogArray(AmbassadorDialogArray, AmbassadorDialogFiles)
    elif suit.style.name == 'mouthp' and not suit.isSkeleton:
        return loadDialogArray(MouthpieceDialogArray, MouthpieceDialogFiles)
    elif suit.style.name == 'whunter' and not suit.isSkeleton:
        return loadDialogArray(WitchHunterDialogArray, WitchHunterDialogFiles)
    elif suit.style.name == 'erfit' and not suit.isSkeleton:
        return loadDialogArray(CountErfitDialogArray, CountErfitDialogFiles)
    elif suit.style.name == 'erclaim' and not suit.isSkeleton:
        return loadDialogArray(CountErclaimDialogArray, CountErclaimDialogFiles)
    elif suit.style.name == 'rainmake' and not suit.isSkeleton:
        return loadDialogArray(RainmakerDialogArray, RainmakerDialogFiles)
    elif suit.style.name == 'redd' and not suit.isSkeleton:
        return loadDialogArray(ReddDialogArray, ReddDialogFiles)
    elif suit.style.name == 'sgoat' and not suit.isSkeleton:
        return loadDialogArray(ScapegoatDialogArray, ScapegoatDialogFiles)
    elif suit.style.name == 'caseman' and not suit.isSkeleton:
        return loadDialogArray(CaseManagerDialogArray, CaseManagerDialogFiles)
    elif suit.style.name == 'stenog' and not suit.isSkeleton:
        return loadDialogArray(StenographerDialogArray, StenographerDialogFiles)
    elif suit.style.name == 'lgator' and not suit.isSkeleton:
        return loadDialogArray(LitigatorDialogArray, LitigatorDialogFiles)
    elif suit.style.name == 'treasure' and not suit.isSkeleton:
        return loadDialogArray(LitigatorDialogArray, LitigatorDialogFiles)
    elif suit.style.name == 'liquidr' and not suit.isSkeleton:
        return loadDialogArray(GatekeeperDialogArray, GatekeeperDialogFiles)
    elif suit.style.name == 'bookkeep' and not suit.isSkeleton:
        return loadDialogArray(ChairmanDialogArray, ChairmanDialogFiles)
    elif suit.style.name == 'arbit' and not suit.isSkeleton:
        return loadDialogArray(CLODialogArray, CLODialogFiles)
    elif suit.style.name == 'duckshfl' and not suit.isSkeleton:
        return loadDialogArray(DuckShufflerDialogArray, DuckShufflerDialogFiles)
    elif suit.style.name == 'treek' and not suit.isSkeleton:
        return loadDialogArray(TreekillerDialogArray, TreekillerDialogFiles)
    elif suit.style.name == 'pcrat' and not suit.isSkeleton:
        return loadDialogArray(PlutocratDialogArray, PlutocratDialogFiles)
    elif suit.style.name == 'payman' and not suit.isSkeleton:
        return loadDialogArray(PlutocratDialogArray, PlutocratDialogFiles)
    elif suit.style.name == 'hroller' and not suit.isSkeleton:
        return loadDialogArray(HighRollerDialogArray, HighRollerDialogFiles)
    elif suit.style.name == 'hrollers' and not suit.isSkeleton:
        return loadDialogArray(HighRollerDialogArray, HighRollerDialogFiles)
    elif suit.style.name == 'hroller2' and not suit.isSkeleton:
        return loadDialogArray(HighRollerDialogArray, HighRollerDialogFiles)
    elif suit.style.name == 'dopr':
        return loadDialogArray(DOPRDialogArray, DOPRDialogFiles)
    elif suit.style.name == 'dopa':
        return loadDialogArray(DOPADialogArray, DOPADialogFiles)
    elif suit.style.name == 'bellring' and not suit.isSkeleton:
        return loadDialogArray(BellringerDialogArray, BellringerDialogFiles)
    elif suit.style.name == 'prethink' and not suit.isSkeleton:
        return loadDialogArray(PrethinkerDialogArray, PrethinkerDialogFiles)
    elif suit.style.name == 'mslacker' and not suit.isSkeleton:
        return loadDialogArray(MultislackerDialogArray, MultislackerDialogFiles)
    elif suit.style.name == 'videog' and not suit.isSkeleton:
        return loadDialogArray(PacesetterDialogArray, PacesetterDialogFiles)
    elif suit.style.name == 'bcaster' and not suit.isSkeleton:
        return loadDialogArray(PacesetterDialogArray, PacesetterDialogFiles)
    elif suit.style.name == 'radiog':
        return loadDialogArray(DOPADialogArray, DOPADialogFiles)
    elif suit.style.name == 'racket' and not suit.isSkeleton:
        return loadDialogArray(FeatherbedderDialogArray, FeatherbedderDialogFiles)
    elif suit.style.name == 'ubuster':
        return loadDialogArray(DOPRDialogArray, DOPRDialogFiles)
    elif suit.style.name == 'safesupervis' and not suit.isSkeleton:
        return loadDialogArray(FirestarterDialogArray, FirestarterDialogFiles)
    elif suit.style.name == 'psetter' and not suit.isSkeleton:
        return loadDialogArray(PacesetterDialogArray, PacesetterDialogFiles)
    elif suit.style.name == 'ddiver' and not suit.isSkeleton:
        return loadDialogArray(DeepDiverDialogArray, DeepDiverDialogFiles)
    elif suit.style.name == 'gatekeep' and not suit.isSkeleton:
        return loadDialogArray(GatekeeperDialogArray, GatekeeperDialogFiles)
    elif suit.style.name == 'dola' and not suit.isSkeleton:
        return loadDialogArray(DOLADialogArray, DOLADialogFiles)
    elif suit.style.name == 'dold' and not suit.isSkeleton:
        return loadDialogArray(DOLDDialogArray, DOLDDialogFiles)
    elif suit.style.name == 'hustle' and not suit.isSkeleton:
        return loadDialogArray(DOLADialogArray, DOLADialogFiles)
    elif suit.style.name == 'dold' and suit.isSkeleton:
        return loadDialogArray(DOLDSkeleDialogArray, DOLDSkeleDialogFiles)
    elif suit.style.name == 'dking' and not suit.isSkeleton:
        return loadDialogArray(ReddDialogArray, ReddDialogFiles)
    elif suit.style.name == 'ottoman' and not suit.isSkeleton:
        return loadDialogArray(OttomanDialogArray, OttomanDialogFiles)
    elif suit.style.name == 'crystal' and not suit.isSkeleton:
        return loadDialogArray(StenographerDialogArray, StenographerDialogFiles)
    elif suit.style.name == 'chairman' and not suit.isSkeleton:
        return loadDialogArray(ChairmanDialogArray, ChairmanDialogFiles)
    elif suit.isSkelecogDialogue:
        return loadDialogArray(SkelecogDialogArray, SkelecogDialogFiles)
    elif suit.isFemaleSkelecog and suit.isSkeleton:
        return loadDialogArray(SkelecogDialogFemaleArray, SkelecogDialogFemaleFiles)
    elif suit.isFemale and not suit.isSkeleton:
        return loadDialogArray(FemaleDialogArray, FemaleDialogFiles)
    elif suit.isSkeleton:
        return loadDialogArray(SkelecogDialogArray, SkelecogDialogFiles)
    else:
        return loadDialogArray(SuitDialogArray, SuitDialogFiles)