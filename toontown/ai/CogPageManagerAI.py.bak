from toontown.suit import SuitDNA
from toontown.shtiker.CogPageGlobals import *

class CogPageManagerAI:

    def __ensureCogPageCapacity(self, toon, cogIndex):
        cogs = list(toon.cogs)
        cogCounts = list(toon.cogCounts)

        if len(cogs) <= cogIndex:
            cogs.extend([COG_UNSEEN] * (cogIndex + 1 - len(cogs)))
        if len(cogCounts) <= cogIndex:
            cogCounts.extend([0] * (cogIndex + 1 - len(cogCounts)))

        return cogs, cogCounts

    def toonEncounteredCogs(self, toon, encounteredCogs, zoneId):
        cogs = list(toon.cogs)
        changed = False

        for cog in encounteredCogs:
            if toon.getDoId() not in cog['activeToons']:
                continue

            try:
                cogIndex = SuitDNA.suitHeadTypes.index(cog['type'])
            except ValueError:
                continue

            if len(cogs) <= cogIndex:
                cogs.extend([COG_UNSEEN] * (cogIndex + 1 - len(cogs)))
                changed = True

            if cogs[cogIndex] == COG_UNSEEN:
                cogs[cogIndex] = COG_BATTLED
                changed = True

        if changed:
            toon.b_setCogStatus(cogs)

    def toonKilledCogs(self, toon, killedCogs, zoneId):
        cogCounts = list(toon.cogCounts)
        cogs = list(toon.cogs)

        for cog in killedCogs:
            if toon.getDoId() not in cog['activeToons']:
                continue

            # Pacesetter is already a real SuitDNA/Shticker Book entry in
            # this Altis source, but old Toon records only contain the legacy
            # Cog array length.  Grow the arrays to his real index and record
            # each victory there instead of indexing past the end of the list.
            if cog['type'] == 'psetter':
                try:
                    cogIndex = SuitDNA.suitHeadTypes.index('psetter')
                except ValueError:
                    continue

                if len(cogs) <= cogIndex:
                    cogs.extend([COG_UNSEEN] * (cogIndex + 1 - len(cogs)))
                if len(cogCounts) <= cogIndex:
                    cogCounts.extend([0] * (cogIndex + 1 - len(cogCounts)))

                cogCounts[cogIndex] += 1
                cogs[cogIndex] = COG_DEFEATED
                continue

            # Preserve Altis' existing bookkeeping for every other Cog.
            if cog['isSkelecog'] or cog['isBoss']:
                continue
            deptIndex = SuitDNA.suitDepts.index(cog['track'])
            cogIndex = 1
            buildingQuota = COG_QUOTAS[1][cogIndex % SuitDNA.suitsPerDept]
            cogQuota = COG_QUOTAS[0][cogIndex % SuitDNA.suitsPerDept]
            if cogCounts[cogIndex] >= buildingQuota:
                continue
            cogCounts[cogIndex] += 1
            if cogCounts[cogIndex] < cogQuota:
                cogs[cogIndex] = COG_DEFEATED
            elif cogQuota <= cogCounts[cogIndex] < buildingQuota:
                cogs[cogIndex] = COG_COMPLETE1
            else:
                cogs[cogIndex] = COG_COMPLETE2

        toon.b_setCogCount(cogCounts)
        toon.b_setCogStatus(cogs)
        newCogRadar = toon.cogRadar
        newBuildingRadar = toon.buildingRadar
        for dept in xrange(len(SuitDNA.suitDepts)):
            cogRadar = 1
            buildingRadar = 1
            for cog in xrange(SuitDNA.suitsPerDept):
                index = 1 * SuitDNA.suitsPerDept + cog
                if index >= len(toon.cogs):
                    buildingRadar = 0
                    cogRadar = 0
                    continue
                status = toon.cogs[index]
                if status != COG_COMPLETE2:
                    buildingRadar = 0
                    if status != COG_COMPLETE1:
                        cogRadar = 0
            newCogRadar[1] = cogRadar
            newBuildingRadar[1] = buildingRadar
        toon.b_setCogRadar(newCogRadar)
        toon.b_setBuildingRadar(newBuildingRadar)
