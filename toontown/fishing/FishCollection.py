from toontown.fishing import FishBase
from toontown.fishing import FishGlobals


class FishCollection:
    """
    FishCollection
    """

    def __init__(self):
        self.fishList = []

    def __len__(self):
        """
        For convenience
        """
        return len(self.fishList)

    def getFish(self):
        """
        Return the current fish list

        :return: fishList
        """
        return self.fishList

    def makeFromNetLists(self, genusList, speciesList, weightList):
        """
        Fill in the fish collection based on lists passed in like they are
        in the toon.dc file
        """
        self.fishList = []
        for genus, species, weight in zip(genusList, speciesList, weightList):
            self.fishList.append(FishBase.FishBase(genus, species, weight))

    def getNetLists(self):
        """
        Return lists formatted for toon.dc style setting and getting
        We store parallel lists of genus, species, and weight in the db

        :return: [genusList, speciesList, weightList]
        """
        genusList = []
        speciesList = []
        weightList = []
        for fish in self.fishList:
            genusList.append(fish.getGenus())
            speciesList.append(fish.getSpecies())
            weightList.append(fish.getWeight())

        return [genusList, speciesList, weightList]

    def hasFish(self, genus, species):
        """
        Return fish if we have the fish specified by this genus and species
        Return None if we do not

        :return: fish | None
        """
        for fish in self.fishList:
            if fish.getGenus() == genus and fish.getSpecies() == species:
                return fish
        return None

    def hasGenus(self, genus):
        """
        Return 1 if we have a fish specified by this genus
        Return 0 if we do not

        :return: 1 | 0
        """
        for fish in self.fishList:
            if fish.getGenus() == genus:
                return 1
        return 0

    def __collect(self, newFish, updateCollection):
        """
        This function exists to share code between collectFish and getCollectResult.
        See their documentation for more details

        :param updateCollection: 1 | 0
        :return: 0 [COLLECT_NO_UPDATE] | 1 [COLLECT_NEW_ENTRY] | 2 [COLLECT_NEW_RECORD]
        """
        # Look for this fish type in our list
        for fish in self.fishList:
            if fish.getGenus() == newFish.getGenus() and fish.getSpecies() == newFish.getSpecies():
                # We already have this fish let's check the weight for a record
                if fish.getWeight() < newFish.getWeight():
                    # new record! set the new weight on the fish in our collection
                    if updateCollection:
                        fish.setWeight(newFish.getWeight())
                    return FishGlobals.COLLECT_NEW_RECORD
                else:
                    # Nope, nothing to update here
                    return FishGlobals.COLLECT_NO_UPDATE
        if updateCollection:
            self.fishList.append(newFish)
        return FishGlobals.COLLECT_NEW_ENTRY

    def collectFish(self, newFish):
        """
        Record this catch in our collection. Has several possible return values:

        - If this fish was not previously in our collection, return COLLECT_NEW_ENTRY
        - If this fish was already found, and we set a new weight record, return COLLECT_NEW_RECORD
        - Otherwise, we already had this fish, nothing to update, return COLLECT_NO_UPDATE

        :param newFish:
        :return: __collect(newFish, updateCollection=1) --> int (enum)
        """
        return self.__collect(newFish, updateCollection = 1)

    def getCollectResult(self, newFish):
        """
        NOTE: This DOES NOT record the fish in our collection.

        - If this fish was not previously in our collection, return COLLECT_NEW_ENTRY
        - If this fish was already found, and we set a new weight record, return COLLECT_NEW_RECORD
        - Otherwise, we already had this fish, nothing to update, return COLLECT_NO_UPDATE

        :return: __collect(newFish, updateCollection=0) --> int (enum)
        """
        return self.__collect(newFish, updateCollection = 0)

    def __str__(self):
        numFish = len(self.fishList)
        txt = 'Fish Collection (%s fish):' % numFish
        for fish in self.fishList:
            txt += '\n' + str(fish)
        return txt
