from toontown.clashbattle.battle.attacks.base.AttackEnum import AttackEnum
from toontown.clashbattle.battle.attacks.server.AttackRepositoryAI import AttackRepository

from .SuitSingleAttackAI import SuitSingleAttackAI
from .SuitMultiAttackAI import SuitDoubleAttackAI, SuitTripleAttackAI
from .SuitGroupAttackAI import SuitGroupAttackAI
from .BasicSuitAttacksAI import *
from .EventSuitAttacksAI import *
from .LitigationSuitAttacksAI import *
from .MercSuitAttacksAI import *
from .MinibossSuitAttacksAI import *

AttackRepository.update({
    # region Generic suit attacks
    AttackEnum.AUDIT:                   SuitSingleAttackAI,
    AttackEnum.BITE:                    SuitSingleAttackAI,
    AttackEnum.BLUE_CHIP:               SuitSingleAttackAI,
    AttackEnum.BOUNCE_CHECK:            SuitSingleAttackAI,
    AttackEnum.BRAIN_STORM:             SuitSingleAttackAI,
    AttackEnum.BUZZ_WORD:               SuitSingleAttackAI,
    AttackEnum.CALCULATE:               SuitSingleAttackAI,
    AttackEnum.CANNED:                  SuitSingleAttackAI,
    AttackEnum.CHOMP:                   SuitSingleAttackAI,
    AttackEnum.CIGAR_SMOKE:             SuitSingleAttackAI,
    AttackEnum.CIGAR_SMOKE_HEAD_HONCHO: SuitSingleAttackAI,
    AttackEnum.CIGAR_SMOKE_FIRESTARTER: SuitSingleAttackAI,
    AttackEnum.CIGAR_SMOKE_PLUTOCRAT:   SuitSingleAttackAI,
    AttackEnum.CLIPON_TIE:              SuitSingleAttackAI,
    AttackEnum.CRUNCH:                  SuitSingleAttackAI,
    AttackEnum.DEMOTION:                SuitSingleAttackAI,
    AttackEnum.DOUBLE_TALK:             SuitSingleAttackAI,
    AttackEnum.DOWNSIZE:                SuitSingleAttackAI,
    AttackEnum.EVICTION_NOTICE:         SuitSingleAttackAI,
    AttackEnum.EVIL_EYE:                SuitSingleAttackAI,
    AttackEnum.FALLING_KNIFE:           SuitSingleAttackAI,
    AttackEnum.FILIBUSTER:              SuitSingleAttackAI,
    AttackEnum.FILL_WITH_LEAD:          SuitSingleAttackAI,
    AttackEnum.FINGER_WAG:              SuitSingleAttackAI,
    AttackEnum.FIRED:                   SuitSingleAttackAI,
    AttackEnum.FOUNTAIN_PEN:            SuitSingleAttackAI,
    AttackEnum.FREEZE_ASSETS:           SuitSingleAttackAI,
    AttackEnum.GLOWER_POWER:            SuitSingleAttackAI,
    AttackEnum.GUILT_TRIP:              SuitGroupAttackAI,
    AttackEnum.HALF_WINDSOR:            SuitSingleAttackAI,
    AttackEnum.HANG_UP:                 SuitSingleAttackAI,
    AttackEnum.HEAD_SHRINK:             SuitSingleAttackAI,
    AttackEnum.HOT_AIR:                 SuitSingleAttackAI,
    AttackEnum.JARGON:                  SuitSingleAttackAI,
    AttackEnum.LEGALESE:                SuitSingleAttackAI,
    AttackEnum.LIQUIDATE:               SuitSingleAttackAI,
    AttackEnum.MARKET_CRASH:            SuitSingleAttackAI,
    AttackEnum.MUMBO_JUMBO:             SuitSingleAttackAI,
    AttackEnum.PARADIGM_SHIFT:          SuitGroupAttackAI,
    AttackEnum.PECKING_ORDER:           SuitSingleAttackAI,
    AttackEnum.PENNY_PINCH:             SuitSingleAttackAI,
    AttackEnum.PICK_POCKET:             SuitSingleAttackAI,
    AttackEnum.PINK_SLIP:               SuitSingleAttackAI,
    AttackEnum.PLAY_HARDBALL:           SuitSingleAttackAI,
    AttackEnum.POUND_KEY:               SuitSingleAttackAI,
    AttackEnum.POWER_TIE:               SuitSingleAttackAI,
    AttackEnum.POWER_TRIP:              SuitGroupAttackAI,
    AttackEnum.QUAKE:                   SuitGroupAttackAI,
    AttackEnum.RAZZLE_DAZZLE:           SuitSingleAttackAI,
    AttackEnum.RED_TAPE:                SuitSingleAttackAI,
    AttackEnum.RE_ORG:                  SuitSingleAttackAI,
    AttackEnum.RE_ARRANGE:              SuitSingleAttackAI,
    AttackEnum.RESTRAINING_ORDER:       SuitSingleAttackAI,
    AttackEnum.ROLODEX:                 SuitSingleAttackAI,
    AttackEnum.ROLODEX_DOUBLE:          SuitDoubleAttackAI,
    AttackEnum.RUBBER_STAMP:            SuitSingleAttackAI,
    AttackEnum.RUB_OUT:                 SuitSingleAttackAI,
    AttackEnum.SACKED:                  SuitSingleAttackAI,
    AttackEnum.SCHMOOZE:                SuitSingleAttackAI,
    AttackEnum.SHAKE:                   SuitGroupAttackAI,
    AttackEnum.SHORT_SQUEEZE:           SuitSingleAttackAI,
    AttackEnum.SHRED:                   SuitSingleAttackAI,
    AttackEnum.SONG_AND_DANCE:          SuitGroupAttackAI,
    AttackEnum.SPIN:                    SuitSingleAttackAI,
    AttackEnum.SYNERGY:                 SuitGroupAttackAI,
    AttackEnum.TABULATE:                SuitSingleAttackAI,
    AttackEnum.TEE_OFF:                 SuitSingleAttackAI,
    AttackEnum.THROW_BOOK:              SuitSingleAttackAI,
    AttackEnum.TREMOR:                  SuitGroupAttackAI,
    AttackEnum.WATERCOOLER:             SuitSingleAttackAI,
    AttackEnum.WATERCOOLER_DOUBLE:      SuitDoubleAttackAI,
    AttackEnum.WATERCOOLER_GROUP:       SuitGroupAttackAI,
    AttackEnum.WITHDRAWAL:              SuitSingleAttackAI,
    AttackEnum.WRITE_OFF:               SuitSingleAttackAI,
    # endregion

    # region Events
    AttackEnum.FTF_SUPERVISOR_ABACUS_SYNERGY: SuitGroupAttackAI,
    AttackEnum.FTF_PRESIDENT_MULLIGAN:  SuitSingleAttackAI,
    AttackEnum.CON_DUCK_TION:  SuitDoubleAttackAI,
    # endregion
})
