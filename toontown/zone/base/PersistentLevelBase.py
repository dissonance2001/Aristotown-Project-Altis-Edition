"""PersistentLevelBase module: contains the PersistentLevelBase class"""
from toontown.level.editor import EditorGlobals


class PersistentLevelBase:
    if EditorGlobals.wantLevelEditor():
        def getEntityTypeReg(self):
            """
            :return: an EntityTypeRegistry with information about the entity types that persistent levels use
            """
            from toontown.zone.entities import PersistentLevelEntityTypes
            from toontown.level import EntityTypeRegistry
            typeReg = EntityTypeRegistry.EntityTypeRegistry(PersistentLevelEntityTypes)
            return typeReg
