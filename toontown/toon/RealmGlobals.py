import os
from enum import IntEnum


class Realm(IntEnum):
    Production = 0
    Staging = 1
    QA = 2
    Development = 3

    def isPublicRealm(self) -> bool:
        """
        Returns if the realm is a public facing realm (Production, Staging).

        :return: True if the realm is public facing, false if not.
        """
        return self.value in PRESET_PUBLIC

    def isPrivateRealm(self) -> bool:
        """
        Returns if the realm is an internal realm (QA, Dev).

        :return: True if the realm is an internal realm, false if not.
        """
        return self.value in PRESET_PRIVATE

    def isDevRealm(self) -> bool:
        """
        Returns if the realm is a development realm (Dev).

        :return: True if the realm is a development realm, false if not.
        """
        return self.value == Realm.Development

    def isBuiltRealm(self) -> bool:
        """
        Returns if the realm runs using a built client (QA, Production).

        :return: True if the realm uses a built client, false if not.
        """
        return self.value in PRESET_BUILT

    def isTestingRealm(self) -> bool:
        """
        Returns if the realm is used for testing.

        :return: True if the realmis used for testing, false if not.
        """
        return self.value in PRESET_TESTING


# Caching the current realm, since it doesn't change.
# Don't use this value directly, use the getCurrentRealm function to be consistent.
__currentRealm = {
    'production': Realm.Production,
    'staging': Realm.Staging,
    'qa': Realm.QA,
    'dev': Realm.Development
}.get(os.environ.get('REALM', 'production').lower(), Realm.Production)
print(f"REALM env var = {os.environ.get('REALM')!r}, resolved realm = {__currentRealm}")


def getCurrentRealm() -> Realm:
    """
    A helper function which gets the realm the process is set to.

    :return: The realm the game is running on.
    """
    return __currentRealm


"""
Presets
"""
PRESET_ALL = {Realm.Production, Realm.Staging, Realm.QA, Realm.Development}
PRESET_PRIVATE = {Realm.QA, Realm.Development, Realm.Staging}
PRESET_PUBLIC = {Realm.Production}
PRESET_BUILT = {Realm.Production, Realm.Staging, Realm.QA}
PRESET_TESTING = {Realm.Staging, Realm.QA}
